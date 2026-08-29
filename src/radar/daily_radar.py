"""
Daily Audience Radar v1 orchestrator — implements
docs/Daily Audience Radar for Commenting/Build Daily Audience Radar v1.txt
using the project's existing tools instead of Google Sheets + Make.com:

  source_scanner.scan_reddit() + scan_spiceworks()  -> "Source Collector"
  manual_links.read_manual_links()                  -> "LinkedIn saved/manual links" source
  comment_scorer.score_candidates()                 -> "AI Scorer" (5-dim + Priority Score)
  comment_generator.generate_comments()              -> "Comment Generator"
  this module's state file                          -> "Randy Approval Gate" (local, no Sheet)

Pipeline: gather -> score -> generate comments -> write today's radar (.md)
+ persist state (JSON, keyed by date) so approve/edit/skip/posted survives
across runs and the .md can be re-rendered on any status change.

Hard rule (unchanged from CLAUDE.md / the comment skill): nothing posts
automatically. Randy approves in the .md, then posts manually on-platform.
YouTube comments are explicitly out of scope for v1 per the source doc
("YouTube comments later").
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from src.trend_finder.source_scanner import scan_reddit, scan_spiceworks
from src.radar.manual_links import read_manual_links, clear_manual_links
from src.radar.comment_scorer import score_candidates
from src.radar.comment_generator import generate_comments
from src.utils.atomic import atomic_write_text, atomic_write_json

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "content-engine" / "research" / "daily_radar"
STATE_PATH = OUT_DIR / "radar_state.json"
RADAR_LOG = ROOT / "logs" / "daily_radar_log.json"

VOICE_PATH = ROOT / "knowledge" / "me" / "voice.md"
PAIN_MAP_PATH = ROOT / "knowledge" / "me" / "icp_pain_map.md"
STORY_BANK_PATH = ROOT / "knowledge" / "me" / "operator-story-bank.md"

STATUS_CHOICES = ["not_reviewed", "approve", "edit", "skip", "posted", "needs_reply"]


def _read_optional(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


# ---------------------------------------------------------------------------
# State: {"<date>": {"items": [item-dict, ...]}}  — each item carries its own
# "status"/"note" so re-rendering the day's markdown is a pure function of state.
# ---------------------------------------------------------------------------

def _load_state():
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_state(state):
    atomic_write_json(STATE_PATH, state)


def _append_log(record):
    RADAR_LOG.parent.mkdir(parents=True, exist_ok=True)
    if RADAR_LOG.exists():
        try:
            data = json.loads(RADAR_LOG.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {"runs": []}
    else:
        data = {"runs": []}
    data.setdefault("runs", []).append(record)
    RADAR_LOG.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _render_markdown(date_str, items):
    lines = [
        f"# Daily Audience Radar — {date_str}",
        "",
        "AI drafts. You approve, edit, skip, or mark posted/needs-reply below "
        "(via `python -m src.main radar-status <rank> approve|edit|skip|posted|needs_reply`). "
        "Nothing posts automatically.",
        "",
        "| Rank | Platform | Title | Why This Matters | Status |",
        "|---|---|---|---|---|",
    ]
    for i, item in enumerate(items, start=1):
        platform = item.get("source", "")
        title = (item.get("title") or "").replace("|", "/")[:80]
        why = (item.get("why_it_matters") or "").replace("|", "/")[:100]
        status = item.get("status", "not_reviewed")
        lines.append(f"| {i} | {platform} | {title} | {why} | {status} |")

    lines += ["", "---", ""]
    for i, item in enumerate(items, start=1):
        status = item.get("status", "not_reviewed")
        note = item.get("note", "")
        lines += [
            f"## {i}. {item.get('title', '(untitled)')}",
            "",
            f"**Platform/source:** {item.get('source', '')}  ",
            f"**URL:** {item.get('url') or '(none — manual entry, add a URL when found)'}  ",
            f"**Priority score:** {item.get('priority_score', 0)} "
            f"(fit {item.get('audience_fit', 0)} / pain {item.get('pain_level', 0)} / "
            f"opportunity {item.get('comment_opportunity', 0)} / freshness {item.get('freshness', 0)} / "
            f"sales risk {item.get('sales_risk', 0)})  ",
            f"**Why this matters:** {item.get('why_it_matters', '')}  ",
            f"**Status:** {status}" + (f"  \n**Note:** {note}" if note else ""),
            "",
            "**Suggested comment:**",
            "",
            "> " + (item.get("suggested_comment") or "_(generation failed — skip or write manually)_").replace("\n", "\n> "),
            "",
        ]

    return "\n".join(lines)


def _write_day(date_str, items):
    markdown = _render_markdown(date_str, items)
    out_path = OUT_DIR / f"{date_str}_radar.md"
    atomic_write_text(out_path, markdown)
    return out_path


def run(dry_run=False, top_n=10):
    """
    Run the Daily Audience Radar pipeline once: gather -> score -> draft
    comments -> write content-engine/research/daily_radar/<date>_radar.md.

    --dry-run gathers and scores only (no comment-drafting spend, nothing
    written) — same convention as trending --dry-run.
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "date": date_str,
        "status": "no_candidates",
        "candidates_found": 0,
        "top_n": 0,
        "tokens_used": 0,
        "output_file": None,
    }

    print("[1/4] Gathering candidates (Reddit, Spiceworks, manual links)...")
    candidates = []
    candidates.extend(scan_reddit())
    candidates.extend(scan_spiceworks())
    manual = read_manual_links()
    candidates.extend(manual)
    print(f"      {len(candidates)} candidate(s) found "
          f"({len(manual)} from manual links).")
    summary["candidates_found"] = len(candidates)

    if not candidates:
        print("[DONE] No candidates found — nothing to score.")
        _append_log(summary)
        return summary

    print("[2/4] Scoring candidates (audience fit, pain, opportunity, freshness, sales risk)...")
    ranked, score_tokens = score_candidates(candidates, top_n=top_n)
    summary["tokens_used"] += score_tokens
    if not ranked:
        summary["status"] = "scoring_failed"
        print("[DONE] Scoring failed or returned nothing.")
        _append_log(summary)
        return summary
    summary["top_n"] = len(ranked)
    print(f"      Top {len(ranked)} candidates selected.")

    if dry_run:
        summary["status"] = "dry_run"
        print("[DRY RUN] Skipping comment drafting and file write.")
        _append_log(summary)
        return summary

    print("[3/4] Drafting comments in voice...")
    voice_profile = _read_optional(VOICE_PATH)
    pain_map = _read_optional(PAIN_MAP_PATH)
    story_bank = _read_optional(STORY_BANK_PATH)
    items, draft_tokens = generate_comments(ranked, voice_profile=voice_profile,
                                             pain_map=pain_map, story_bank=story_bank)
    summary["tokens_used"] += draft_tokens
    for item in items:
        item.setdefault("status", "not_reviewed")
        item.setdefault("note", "")

    print("[4/4] Writing today's radar...")
    out_path = _write_day(date_str, items)

    state = _load_state()
    state[date_str] = {"items": items}
    _save_state(state)

    if manual:
        clear_manual_links()

    summary["status"] = "drafted"
    summary["output_file"] = str(out_path.relative_to(ROOT))
    print(f"[DONE] Radar written -> {summary['output_file']}")
    print("       Review each suggested comment, set status with "
          "`python -m src.main radar-status <rank> approve|edit|skip|posted|needs_reply`, "
          "then post manually.")

    _append_log(summary)
    return summary


def set_status(rank, status, note="", date_str=None):
    """
    Record Randy's approval-gate decision for the item at `rank` (1-based, as
    shown in that day's radar table) and re-render that day's markdown.
    """
    if status not in STATUS_CHOICES:
        raise ValueError(f"status must be one of {STATUS_CHOICES}, got '{status}'")

    date_str = date_str or datetime.now().strftime("%Y-%m-%d")
    state = _load_state()
    day = state.get(date_str)
    if not day or not day.get("items"):
        raise FileNotFoundError(f"No radar state found for {date_str} — run `audience-radar` first.")

    items = day["items"]
    rank = int(rank)
    if rank < 1 or rank > len(items):
        raise ValueError(f"Rank {rank} out of range — {date_str} has {len(items)} item(s).")

    item = items[rank - 1]
    item["status"] = status
    item["note"] = note
    item["updated"] = datetime.now(timezone.utc).isoformat()

    state[date_str] = {"items": items}
    _save_state(state)
    out_path = _write_day(date_str, items)

    print(f"[OK] {date_str} #{rank} \"{item.get('title', '')}\" -> {status}"
          + (f" ({note})" if note else ""))
    print(f"     Re-rendered: {out_path.relative_to(ROOT)}")
    return item
