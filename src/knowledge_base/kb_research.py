"""
Free, local research-brief generator for article creation.

Fills a real gap found 2026-08-04: create-next-article's own SKILL.md
documents a mandatory "Step 0b — KB Research" gate that calls a
`kb-research` skill which never actually existed anywhere in this project
-- every article created through that pipeline has been silently skipping
a step its own spec calls mandatory. This module (and the kb-research
SKILL.md that wraps it) is the real fix.

Deliberately zero API cost. Reuses query.py's own keyword-scoring/ranking
logic (load_index, _extract_keywords, _score_file) -- the same free,
local step query.py already runs before it ever calls Claude. This module
stops right there and never reaches query.py's paid _call_claude() step.
That matches this project's own established discipline: cheap
deterministic checks first, escalate to a paid AI call only when the
cheap check can't answer it (see Agentic Reliability Loop Cap in
CLAUDE.md). If a deeper, AI-synthesized answer is ever wanted on top of
this brief, that's a separate, explicit call to `python -m src.main ask`
-- flag the cost and ask first, same as every other on-demand API command
in this project.

CLI:
    python -m src.knowledge_base.kb_research "topic or war story angle"
    python -m src.knowledge_base.kb_research "topic" --group ai-and-claude-code
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from src.knowledge_base.query import _extract_keywords, _score_file, load_index

ICP_PAIN_MAP_PATH = Path("knowledge/me/icp_pain_map.md")
CALLBACK_BANK_PATH = Path("output/callback_bank.md")
CONTENT_INVENTORY_PATH = Path("content-engine/content/_ideas/_CONTENT_INVENTORY.md")
ARTICLES_DIR = Path("content-engine/content/articles")


def _relevant_transcripts(topic: str, group: str | None, top_n: int) -> list[dict]:
    """Free, local keyword-ranked transcript search -- the same scoring
    query.py uses before it ever calls Claude. No API cost."""
    index = load_index()
    keywords = _extract_keywords(topic)
    if not keywords:
        return []

    candidates = []
    for group_name, group_data in index.get("groups", {}).items():
        if group and group_name != group:
            continue
        for channel_data in group_data.get("channels", {}).values():
            for entry in channel_data.get("transcripts", []):
                candidates.append(entry)

    scored = [
        (score, entry)
        for entry in candidates
        if (score := _score_file(entry, keywords)) > 0
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "title": entry.get("title", ""),
            "channel": entry.get("channel", ""),
            "date": entry.get("date", ""),
            "score": score,
        }
        for score, entry in scored[:top_n]
    ]


def _repetition_check(topic: str) -> list[str]:
    """Flag existing published/drafted articles whose title shares real
    keyword overlap with the new topic. Soft signal, not a hard block --
    surfaced so a human (or the drafting step) can judge whether it's a
    genuine duplicate or just an adjacent angle."""
    keywords = set(_extract_keywords(topic))
    if not keywords:
        return []

    hits = []
    if CONTENT_INVENTORY_PATH.is_file():
        for line in CONTENT_INVENTORY_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
            line_keywords = set(_extract_keywords(line))
            overlap = keywords & line_keywords
            if len(overlap) >= 2:
                hits.append(line.strip())

    if ARTICLES_DIR.is_dir():
        for folder in ARTICLES_DIR.iterdir():
            if not folder.is_dir():
                continue
            title_guess = re.sub(r"^ART\d+_", "", folder.name).replace("_", " ")
            title_keywords = set(_extract_keywords(title_guess))
            overlap = keywords & title_keywords
            if len(overlap) >= 2:
                hits.append(f"{folder.name} (folder title overlap: {', '.join(sorted(overlap))})")

    return hits


def _p_number_candidates(topic: str) -> list[str]:
    """Return the full CORE PAINS list from icp_pain_map.md, flagging
    which ones share keyword overlap with the topic. Does not auto-assign
    a P# -- that's a real judgment call for whoever drafts the article,
    this just surfaces the checkable list instead of making them go find
    the file themselves."""
    if not ICP_PAIN_MAP_PATH.is_file():
        return ["icp_pain_map.md not found -- P# alignment cannot be checked"]

    text = ICP_PAIN_MAP_PATH.read_text(encoding="utf-8", errors="replace")
    pain_lines = re.findall(r"- \*\*(P\d[^*]*)\*\*(.*)", text)
    keywords = set(_extract_keywords(topic))

    results = []
    for bold_part, rest in pain_lines:
        line = f"{bold_part}{rest}"
        line_keywords = set(_extract_keywords(line))
        overlap = keywords & line_keywords
        marker = " <- keyword overlap" if overlap else ""
        results.append(f"{line.strip()}{marker}")
    return results


def _matching_callbacks(topic: str) -> list[str]:
    """Scan callback_bank.md for entries whose reference phrase or
    adaptation line shares keyword overlap with the topic. Soft-match --
    a human still picks, per this project's own callback rules (2-4 max,
    one per section, never forced)."""
    if not CALLBACK_BANK_PATH.is_file():
        return []

    keywords = set(_extract_keywords(topic))
    if not keywords:
        return []

    text = CALLBACK_BANK_PATH.read_text(encoding="utf-8", errors="replace")
    entries = re.findall(r"- \*\*(\w+\d+)\*\* — (.+?)(?=\n- \*\*|\n\n|\Z)", text, re.DOTALL)

    matches = []
    for entry_id, entry_text in entries:
        entry_keywords = set(_extract_keywords(entry_text))
        overlap = keywords & entry_keywords
        if overlap:
            first_line = entry_text.strip().splitlines()[0]
            matches.append(f"{entry_id} — {first_line} (overlap: {', '.join(sorted(overlap))})")
    return matches


def research_brief(topic: str, group: str | None = None, top_n: int = 8) -> dict:
    """Build the full free research brief. Zero API cost."""
    return {
        "topic": topic,
        "group_filter": group,
        "relevant_transcripts": _relevant_transcripts(topic, group, top_n),
        "repetition_flags": _repetition_check(topic),
        "p_number_candidates": _p_number_candidates(topic),
        "matching_callbacks": _matching_callbacks(topic),
    }


def print_brief(brief: dict) -> None:
    print(f"\nKB RESEARCH BRIEF — \"{brief['topic']}\"")
    if brief["group_filter"]:
        print(f"(scoped to group: {brief['group_filter']})")
    print("(free, local, zero API cost — keyword-ranked, not AI-synthesized)\n")

    print(f"RELEVANT TRANSCRIPTS ({len(brief['relevant_transcripts'])} found):")
    if brief["relevant_transcripts"]:
        for t in brief["relevant_transcripts"]:
            print(f"  [{t['score']:>3}] {t['title']} — {t['channel']} ({t['date']})")
    else:
        print("  None found — try broader keywords or check the topic wording.")

    print(f"\nREPETITION CHECK ({len(brief['repetition_flags'])} possible overlaps):")
    if brief["repetition_flags"]:
        for r in brief["repetition_flags"]:
            print(f"  ⚠ {r}")
    else:
        print("  No overlapping existing articles found.")

    print("\nP# ALIGNMENT CANDIDATES (from icp_pain_map.md):")
    for p in brief["p_number_candidates"]:
        print(f"  {p}")

    print(f"\nMATCHING CALLBACKS ({len(brief['matching_callbacks'])} candidates):")
    if brief["matching_callbacks"]:
        for c in brief["matching_callbacks"]:
            print(f"  {c}")
    else:
        print("  No keyword-matched callbacks — that's fine, don't force one.")

    print(
        "\nThis brief is free and local. A deeper AI-synthesized answer is "
        "available via `python -m src.main ask \"...\"` but costs real API "
        "credits — flag it and get a go-ahead before running that, same as "
        "every other on-demand API command in this project.\n"
    )


def main():
    parser = argparse.ArgumentParser(description="Free, local KB research brief for article creation.")
    parser.add_argument("topic", help="Article topic, war story angle, or working title")
    parser.add_argument("--group", default=None, help="Restrict transcript search to one group")
    parser.add_argument("--top", type=int, default=8, help="Max transcripts to surface (default 8)")
    args = parser.parse_args()

    brief = research_brief(args.topic, group=args.group, top_n=args.top)
    print_brief(brief)


if __name__ == "__main__":
    main()
