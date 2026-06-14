"""
Pipeline status — one read-only, at-a-glance summary of the whole content + funnel
pipeline. Zero tokens, zero network: it only reads existing JSON/state files and
gracefully skips anything missing.

  python -m src.main status
"""
import json
import os
from datetime import date

DASHBOARD_STATE = os.path.join("content-engine", "dashboard_state.json")
PENDING_DIR = os.path.join("content-engine", "pending")
KIT_LOG = "logs/kit_sync_log.json"
INDEX = "knowledge_base/index.json"
RUN_SUMMARY = "logs/run_summary.json"
TREND_LOG = "logs/trend_finder_log.json"
ANALYZER_LOG = "logs/analyzer_log.json"

STAGES = ["pending", "approved", "scheduled", "published"]


def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def summarize_articles(state, today=None):
    """Pure: roll up the dashboard_state into stage counts, piece progress, overdue."""
    today = today or date.today().isoformat()
    articles = (state or {}).get("articles", {})
    by_stage = {s: 0 for s in STAGES}
    pieces_done = pieces_total = 0
    overdue = []
    for slug, a in articles.items():
        if not isinstance(a, dict):
            continue
        stage = a.get("stage") or "pending"
        if stage in by_stage:
            by_stage[stage] += 1
        for piece in (a.get("pieces") or {}).values():
            if not isinstance(piece, dict):
                continue
            pieces_total += 1
            bools = [v for v in piece.values() if isinstance(v, bool)]
            if bools and all(bools):
                pieces_done += 1
        pd = a.get("publish_date")
        if pd and pd < today and stage != "published":
            overdue.append((slug, pd))
    overdue.sort(key=lambda x: x[1])
    return {
        "total": len(articles),
        "by_stage": by_stage,
        "pieces_done": pieces_done,
        "pieces_total": pieces_total,
        "overdue": overdue,
    }


def _last_run(log):
    if isinstance(log, dict) and isinstance(log.get("runs"), list) and log["runs"]:
        return log["runs"][-1]
    return None


def _fmt_ts(ts):
    return str(ts)[:16].replace("T", " ") if ts else "—"


def build_report(today=None):
    """Build the status report lines (testable; reads files, no printing)."""
    today = today or date.today().isoformat()
    lines = ["━" * 54, f" Pipeline Status — {today}", "━" * 54]

    state = _load_json(DASHBOARD_STATE)
    if state:
        s = summarize_articles(state, today)
        bs = s["by_stage"]
        lines.append(
            f" Content: {s['total']} articles  (published {bs['published']} · "
            f"scheduled {bs['scheduled']} · approved {bs['approved']} · pending {bs['pending']})"
        )
        lines.append(f"   Pieces complete: {s['pieces_done']}/{s['pieces_total']}")
        if s["overdue"]:
            shown = ", ".join(f"{slug} ({d})" for slug, d in s["overdue"][:5])
            lines.append(f"   ⚠ Overdue ({len(s['overdue'])}): {shown}")
    else:
        lines.append(" Content: (no dashboard_state.json yet)")

    if os.path.isdir(PENDING_DIR):
        folders = sorted(
            n for n in os.listdir(PENDING_DIR)
            if os.path.isdir(os.path.join(PENDING_DIR, n))
        )
        lines.append(f" Review queue (pending/): {len(folders)}")
        for n in folders[:8]:
            lines.append(f"   - {n}")

    kit = _last_run(_load_json(KIT_LOG))
    if kit:
        tc = kit.get("tier_counts", {}) or {}
        lines.append(
            f" Warm list (last sync {_fmt_ts(kit.get('timestamp'))}): "
            f"{kit.get('cohort_size', '?')} cohort — "
            f"customer {tc.get('customer', 0)}, hot {tc.get('hot', 0)}, "
            f"warm {tc.get('warm', 0)}, lead {tc.get('lead', 0)}"
        )

    idx = _load_json(INDEX)
    if idx:
        groups = idx.get("groups", {}) or {}
        channels = sum(len(g.get("channels", {})) for g in groups.values() if isinstance(g, dict))
        lines.append(
            f" Knowledge base: {idx.get('total_transcripts', '?')} transcripts · "
            f"{channels} channels · {len(groups)} groups"
        )

    rs = _load_json(RUN_SUMMARY)
    if isinstance(rs, dict) and rs.get("timestamp"):
        lines.append(f" Last pipeline run: {_fmt_ts(rs.get('timestamp'))} ({rs.get('status', '?')})")

    trend = _last_run(_load_json(TREND_LOG))
    if trend:
        lines.append(
            f" Last trend draft: {_fmt_ts(trend.get('timestamp'))} — "
            f"{str(trend.get('topic', '?'))[:48]} (score {trend.get('score', '?')})"
        )

    an = _last_run(_load_json(ANALYZER_LOG))
    if an:
        cost = an.get("estimated_cost_usd")
        lines.append(f" Last analysis: {_fmt_ts(an.get('timestamp'))}"
                     + (f" — ${cost}" if cost is not None else ""))

    lines.append("━" * 54)
    return lines


def run_status():
    print("\n".join(build_report()))
