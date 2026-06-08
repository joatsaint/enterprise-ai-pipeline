"""
Trend Finder orchestrator — sequences source_scanner -> relevance_scorer ->
post_drafter and writes the day's draft to content-engine/pending/ for
Randy's review.

Pipeline (one run = one draft, per the locked-in "1 draft per day" scope):
  1. gather_candidates()  -> raw candidates from Reddit, RSS, knowledge base
  2. score_topics()       -> ranked by fit to the ICP
  3. draft_post()         -> full post draft + rationale, in voice, for the
                             single top-ranked topic
  4. write_draft()        -> content-engine/pending/<slug>/ (text-post.md + _README.md)
  5. _append_log()        -> append a run record to logs/trend_finder_log.json

This module never publishes anything — it only ever proposes. Every draft
lands in the same review -> approve -> schedule -> publish queue every other
piece of content in this project goes through (see linkedin_atomizer.py).
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from src.trend_finder.source_scanner import gather_candidates
from src.trend_finder.relevance_scorer import score_topics
from src.trend_finder.post_drafter import draft_post


ROOT = Path(__file__).resolve().parent.parent.parent
PENDING_DIR = ROOT / "content-engine" / "pending"
TREND_LOG = ROOT / "logs" / "trend_finder_log.json"
VOICE_PATH = ROOT / "knowledge" / "me" / "voice.md"


def _read_optional(path):
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _slugify(title, date_str):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60].rstrip("-")
    return f"TREND_{date_str}_{slug or 'untitled'}"


def _append_log(record):
    TREND_LOG.parent.mkdir(parents=True, exist_ok=True)
    if TREND_LOG.exists():
        try:
            data = json.loads(TREND_LOG.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {"runs": []}
    else:
        data = {"runs": []}
    data.setdefault("runs", []).append(record)
    TREND_LOG.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_draft(slug, topic, draft):
    """Write the draft + a review README into content-engine/pending/<slug>/."""
    out_dir = PENDING_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "text-post.md").write_text(
        f"## Text Post\n\n{draft['post_text']}\n", encoding="utf-8"
    )

    source = topic.get("source", "unknown")
    source_line = f"`{source}`" + (f" — {topic['url']}" if topic.get("url") else "")

    readme = (
        f"# {slug}\n\n"
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  \n"
        f"**Topic:** {topic.get('title', '')}  \n"
        f"**Relevance score:** {topic.get('score', 0):.2f}  \n"
        f"**Source:** {source_line}  \n\n"
        f"## Why this topic fits the audience\n\n{topic.get('why_it_fits', '')}\n\n"
        f"## Drafting rationale\n\n{draft.get('rationale', '')}\n\n"
        f"## Review checklist\n\n"
        f"- [ ] Voice check — sounds like Randy, not generic AI\n"
        f"- [ ] Facts check — claims in the post are accurate\n"
        f"- [ ] Edited and approved before scheduling to Buffer\n"
    )
    (out_dir / "_README.md").write_text(readme, encoding="utf-8")

    return ["text-post.md", "_README.md"]


def run(dry_run=False):
    """
    Run the trend-finder pipeline once: gather -> score -> draft -> write.

    In --dry-run mode, candidates are gathered and scored (no Anthropic spend
    beyond the Haiku scoring call) but no post is drafted and nothing is
    written to pending/ — used to sanity-check source health and topic fit.

    Returns a summary dict (also appended to logs/trend_finder_log.json).
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "date": date_str,
        "status": "no_candidates",
        "topic": None,
        "score": None,
        "tokens_used": 0,
        "output_dir": None,
    }

    print("[1/3] Gathering candidate topics (Reddit, RSS, knowledge base)...")
    candidates = gather_candidates()
    print(f"      {len(candidates)} candidate(s) found.")
    if not candidates:
        print("[DONE] No candidates found — nothing to score or draft.")
        _append_log(summary)
        return summary

    print("[2/3] Scoring candidates against the ICP...")
    ranked, score_tokens = score_topics(candidates)
    summary["tokens_used"] += score_tokens
    if not ranked:
        summary["status"] = "scoring_failed"
        print("[DONE] Scoring failed or returned nothing — nothing to draft.")
        _append_log(summary)
        return summary

    top_topic = ranked[0]
    summary["topic"] = top_topic.get("title")
    summary["score"] = top_topic.get("score")
    print(f"      Top topic: \"{top_topic.get('title')}\" (score {top_topic.get('score'):.2f})")

    if dry_run:
        summary["status"] = "dry_run"
        print("[DRY RUN] Skipping post drafting and pending/ write.")
        _append_log(summary)
        return summary

    print("[3/3] Drafting post in voice...")
    voice_profile = _read_optional(VOICE_PATH)
    draft, draft_tokens = draft_post(top_topic, voice_profile=voice_profile)
    summary["tokens_used"] += draft_tokens

    if not draft:
        summary["status"] = "draft_failed"
        print("[DONE] Drafting failed — nothing written to pending/.")
        _append_log(summary)
        return summary

    slug = _slugify(top_topic.get("title", "untitled"), date_str)
    written = _write_draft(slug, top_topic, draft)
    summary["status"] = "drafted"
    summary["output_dir"] = f"content-engine/pending/{slug}"

    print(f"[DONE] Draft written -> content-engine/pending/{slug}/ ({', '.join(written)})")
    print("       Review, edit, and approve before scheduling to Buffer.")

    _append_log(summary)
    return summary
