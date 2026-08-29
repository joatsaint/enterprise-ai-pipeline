"""
Pain Point Cross-Run Aggregator — Pass 3.

pain_point_extractor.py writes one standalone report per group per run
(knowledge_base/reports/pain_points_YYYY-MM-DD_[group].md). Nothing rolls
those individual snapshots up into one current view, so the same recurring
theme gets independently rediscovered dozens of times across dozens of
files with no cross-run ranking.

This module:
  1. Parses any report not yet folded into the running theme history
     (knowledge_base/pain_point_history.json).
  2. Uses one Claude call per batch to cluster each new item against the
     existing canonical themes (same idea, different wording -> merge;
     genuinely new -> new theme), updating each theme's last_seen date
     and total_mentions.
  3. Scores every theme by recency-decay off ITS OWN last_seen date (not
     the file date) — a theme mentioned yesterday outranks one with a
     higher raw count that hasn't come up in 6 weeks.
  4. Writes a single ranked top-10 report:
     knowledge_base/reports/pain_points_AGGREGATE_YYYY-MM-DD.md
  5. Deletes individual report files older than RETENTION_DAYS — safe,
     because step 2 already folded their signal into history.json before
     any deletion happens.

CLI (via main.py):
    python -m src.main aggregate-pain-points
    python -m src.main aggregate-pain-points --dry-run   # no writes, no deletes
"""
import glob
import json
import math
import os
import re
from datetime import datetime, timezone

import anthropic

from src.utils.ai import create
from src.utils.atomic import atomic_write_json

REPORTS_DIR = "knowledge_base/reports"
HISTORY_PATH = "knowledge_base/pain_point_history.json"
ANALYZER_LOG = "logs/analyzer_log.json"

RETENTION_DAYS = 90
DECAY_HALF_LIFE_DAYS = 14
BATCH_SIZE = 4  # report files per clustering call — each file yields ~25-30 items,
                # and every item needs a JSON match entry back, so this stays small
                # enough that the response fits well inside CLUSTER_MAX_TOKENS.
CLUSTER_MAX_TOKENS = 8000
TOP_N = 10

_FILENAME_RE = re.compile(r"^pain_points_(\d{4}-\d{2}-\d{2})_(.+)\.md$")
_ITEM_RE = re.compile(r"^\d+\.\s+(.+?)\s+—\s+mentioned in (\d+) video\(s\)\s*$")

_SECTION_TYPE = {
    "## Top Questions (Most Asked)": "question",
    "## Top Pain Points (Most Expressed)": "pain_point",
    "## Top Desired Outcomes (What They Want)": "desired_outcome",
}

_TYPE_LABEL = {
    "question": "Top Questions",
    "pain_point": "Top Pain Points",
    "desired_outcome": "Top Desired Outcomes",
}


# ---------------------------------------------------------------------------
# Report parsing
# ---------------------------------------------------------------------------

def list_report_files(reports_dir=REPORTS_DIR):
    """All individual (non-aggregate) pain_points_*.md report files."""
    files = []
    for path in glob.glob(os.path.join(reports_dir, "pain_points_*.md")):
        filename = os.path.basename(path)
        if "AGGREGATE" in filename:
            continue
        if _FILENAME_RE.match(filename):
            files.append(path)
    return sorted(files)


def parse_report(path):
    """
    Parse one pain_points_YYYY-MM-DD_[group].md file into structured items.

    Returns dict: {"date": str, "group": str, "items": [
        {"type": "question"|"pain_point"|"desired_outcome", "text": str, "count": int}
    ]} or None if the filename/content doesn't match the expected format.
    """
    filename = os.path.basename(path)
    m = _FILENAME_RE.match(filename)
    if not m:
        return None
    date, group = m.group(1), m.group(2)

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except OSError:
        return None

    items = []
    current_type = None
    for line in lines:
        stripped = line.strip()
        if stripped in _SECTION_TYPE:
            current_type = _SECTION_TYPE[stripped]
            continue
        if stripped.startswith("## "):
            current_type = None  # left the sections we care about (e.g. PDF Opportunities)
            continue
        if current_type is None:
            continue
        item_match = _ITEM_RE.match(stripped)
        if item_match:
            items.append({
                "type": current_type,
                "text": item_match.group(1).strip(),
                "count": int(item_match.group(2)),
            })

    return {"date": date, "group": group, "items": items}


# ---------------------------------------------------------------------------
# History persistence
# ---------------------------------------------------------------------------

def _load_history(path=HISTORY_PATH):
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data.setdefault("themes", [])
            data.setdefault("processed_files", [])
            return data
        except (json.JSONDecodeError, OSError):
            pass
    return {"themes": [], "processed_files": []}


def _save_history(history, path=HISTORY_PATH):
    history["last_run"] = datetime.now(timezone.utc).isoformat()
    atomic_write_json(path, history)


def _next_theme_id(history):
    existing = {t["theme_id"] for t in history["themes"]}
    n = len(history["themes"]) + 1
    while f"pp_{n:04d}" in existing:
        n += 1
    return f"pp_{n:04d}"


# ---------------------------------------------------------------------------
# Clustering (LLM merge)
# ---------------------------------------------------------------------------

def _cluster_batch(client, model, history, new_items):
    """
    One LLM call: for each new item, match it to an existing theme (by id)
    or flag it as a new canonical theme. Mutates `history["themes"]` in
    place. `new_items` is a list of dicts with type/text/count/date/group.
    """
    if not new_items:
        return

    existing_themes = [
        {"theme_id": t["theme_id"], "type": t["type"], "text": t["canonical_text"]}
        for t in history["themes"]
    ]

    prompt = f"""You maintain a canonical list of recurring pain points, questions, and
desired outcomes extracted from YouTube audience research. For each NEW item
below, decide whether it expresses the SAME underlying theme as an EXISTING
one (just worded differently) or is genuinely new.

EXISTING THEMES:
{json.dumps(existing_themes, ensure_ascii=False)}

NEW ITEMS (match within the same "type" only):
{json.dumps([{"index": i, **item} for i, item in enumerate(new_items)], ensure_ascii=False)}

Return ONLY valid JSON: a flat array with exactly one entry per new item, in
the same order, using this COMPACT 4-element array form (not objects — this
keeps the response short):
[index, theme_id_or_null, new_canonical_text_or_null, new_category_or_null]

Example:
[[0, "pp_0003", null, null], [1, null, "short canonical phrasing", "career"]]

Use theme_id (existing) when it's the same theme as an existing one. Use
new_canonical_text + new_category (theme_id null) when it's genuinely new.
No prose, no markdown fences, no explanation — the array only."""

    client_ = client or anthropic.Anthropic()
    text, _usage = create(
        client_,
        task="pain_point_aggregator_cluster",
        model=model,
        max_tokens=CLUSTER_MAX_TOKENS,
        system="You cluster research themes. Return ONLY a valid JSON array. No prose.",
        messages=[{"role": "user", "content": prompt}],
    )
    clean = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    clean = re.sub(r"```\s*$", "", clean.strip())
    matches = json.loads(clean)

    by_id = {t["theme_id"]: t for t in history["themes"]}

    for match in matches:
        if not isinstance(match, list) or len(match) != 4:
            continue
        idx, theme_id, new_text, new_category = match
        if idx is None or idx >= len(new_items):
            continue
        item = new_items[idx]

        if theme_id and theme_id in by_id:
            theme = by_id[theme_id]
            theme["total_mentions"] += item["count"]
            if item["date"] > theme["last_seen"]:
                theme["last_seen"] = item["date"]
            if item["date"] < theme["first_seen"]:
                theme["first_seen"] = item["date"]
        else:
            new_id = _next_theme_id(history)
            theme = {
                "theme_id": new_id,
                "type": item["type"],
                "canonical_text": new_text or item["text"],
                "category": new_category or "uncategorized",
                "first_seen": item["date"],
                "last_seen": item["date"],
                "total_mentions": item["count"],
            }
            history["themes"].append(theme)
            by_id[new_id] = theme


# ---------------------------------------------------------------------------
# Scoring + report rendering
# ---------------------------------------------------------------------------

def decay_score(total_mentions, last_seen, as_of, half_life_days=DECAY_HALF_LIFE_DAYS):
    """Recency-weighted score: raw mentions decayed by an exponential
    half-life measured from the theme's own last_seen date, not the file date."""
    last_seen_dt = datetime.strptime(last_seen, "%Y-%m-%d")
    as_of_dt = datetime.strptime(as_of, "%Y-%m-%d")
    days_since = max((as_of_dt - last_seen_dt).days, 0)
    decay = math.pow(0.5, days_since / half_life_days)
    return total_mentions * decay


def _render_aggregate_report(history, as_of, files_processed_count):
    scored = []
    for t in history["themes"]:
        scored.append({**t, "score": decay_score(t["total_mentions"], t["last_seen"], as_of)})

    lines = [
        "# Pain Point Analysis: Cross-Run Aggregate",
        f"**Generated:** {as_of}",
        f"**Themes Tracked:** {len(history['themes'])}",
        f"**Source Reports Folded In This Run:** {files_processed_count}",
        f"**Decay Half-Life:** {DECAY_HALF_LIFE_DAYS} days (recency measured from each theme's own last-mentioned date)",
        "",
        "---",
        "",
    ]

    for item_type in ("question", "pain_point", "desired_outcome"):
        ranked = sorted(
            (t for t in scored if t["type"] == item_type),
            key=lambda t: t["score"],
            reverse=True,
        )[:TOP_N]
        lines.append(f"## {_TYPE_LABEL[item_type]}")
        lines.append("")
        for i, t in enumerate(ranked, 1):
            lines.append(
                f"{i}. {t['canonical_text']} — {t['total_mentions']} total mention(s), "
                f"last seen {t['last_seen']} (score {t['score']:.1f}, category: {t['category']})"
            )
        lines.append("")

    lines += [
        "---",
        "*Generated by pain_point_aggregator.py — Pass 3 cross-run merge of pain_point_extractor.py reports*",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Retention (safe delete)
# ---------------------------------------------------------------------------

def _prune_old_reports(history, as_of, reports_dir=REPORTS_DIR, retention_days=RETENTION_DAYS):
    """
    Delete individual report files older than retention_days — only files
    already recorded in history["processed_files"], i.e. already folded
    into pain_point_history.json. Never deletes an unprocessed file.
    """
    as_of_dt = datetime.strptime(as_of, "%Y-%m-%d")
    processed = set(history["processed_files"])
    deleted = []

    for path in list_report_files(reports_dir):
        filename = os.path.basename(path)
        if filename not in processed:
            continue
        m = _FILENAME_RE.match(filename)
        if not m:
            continue
        file_date = datetime.strptime(m.group(1), "%Y-%m-%d")
        if (as_of_dt - file_date).days > retention_days:
            try:
                os.remove(path)
                deleted.append(filename)
            except OSError:
                pass

    return deleted


# ---------------------------------------------------------------------------
# Log
# ---------------------------------------------------------------------------

def _append_analyzer_log(files_processed, files_deleted, themes_total, output_file):
    os.makedirs("logs", exist_ok=True)
    log = {"runs": []}
    if os.path.exists(ANALYZER_LOG):
        try:
            with open(ANALYZER_LOG, "r", encoding="utf-8") as f:
                log = json.load(f)
        except Exception:
            pass

    log["runs"].append({
        "run_id": datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S"),
        "pass": "aggregate",
        "files_processed": files_processed,
        "files_deleted": files_deleted,
        "themes_total": themes_total,
        "output_file": output_file,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    with open(ANALYZER_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_aggregator(dry_run=False, reports_dir=REPORTS_DIR, history_path=HISTORY_PATH):
    """
    Run Pass 3: fold unprocessed reports into the theme history, write the
    ranked aggregate report, and prune reports older than RETENTION_DAYS.

    dry_run=True: parses and scores as normal but writes nothing to disk
    (no history update, no aggregate report, no deletions) — preview only.
    """
    model = os.getenv("ANALYZER_MODEL", "claude-haiku-4-5-20251001")
    as_of = datetime.now().strftime("%Y-%m-%d")

    history = _load_history(history_path)
    processed_set = set(history["processed_files"])

    all_files = list_report_files(reports_dir)
    new_files = [p for p in all_files if os.path.basename(p) not in processed_set]

    if not new_files:
        print("[aggregate] No new reports since last run.")
        return _render_aggregate_report(history, as_of, 0) if history["themes"] else None

    client = anthropic.Anthropic()
    newly_processed = []

    for batch_start in range(0, len(new_files), BATCH_SIZE):
        batch = new_files[batch_start:batch_start + BATCH_SIZE]
        batch_items = []
        for path in batch:
            parsed = parse_report(path)
            if not parsed:
                continue
            for item in parsed["items"]:
                batch_items.append({**item, "date": parsed["date"], "group": parsed["group"]})
            newly_processed.append(os.path.basename(path))

        try:
            _cluster_batch(client, model, history, batch_items)
        except Exception as e:
            print(f"[WARN] Aggregator clustering failed for batch starting at {batch_start}: {e}")

    report_text = _render_aggregate_report(history, as_of, len(newly_processed))

    if dry_run:
        print(f"[aggregate] DRY RUN — {len(newly_processed)} report(s) would be folded in, "
              f"{len(history['themes'])} themes total. Nothing written.")
        return report_text

    history["processed_files"] = sorted(set(history["processed_files"]) | set(newly_processed))
    _save_history(history, history_path)

    os.makedirs(reports_dir, exist_ok=True)
    output_path = os.path.join(reports_dir, f"pain_points_AGGREGATE_{as_of}.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    deleted = _prune_old_reports(history, as_of, reports_dir)

    _append_analyzer_log(len(newly_processed), len(deleted), len(history["themes"]), output_path)

    print(f"[aggregate] Folded {len(newly_processed)} report(s) into history "
          f"({len(history['themes'])} themes total).")
    print(f"[aggregate] Wrote {output_path}")
    if deleted:
        print(f"[aggregate] Pruned {len(deleted)} report(s) older than {RETENTION_DAYS} days "
              f"(already folded into pain_point_history.json).")

    return report_text
