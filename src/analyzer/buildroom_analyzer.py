"""
Build Room Analyzer — Phase B strategic teardown of Duncan Rogoff's Build Room.

Goal (strategic, NOT a build-along guide):
  Decompose the automated content pipeline Duncan teaches, inventory the tools /
  paid services / automations behind it, then feed that inventory into a synthesis
  pass that designs a cheaper, more token-efficient, more fully-automated version
  starting from THIS project's current state.

This module covers Step 1 only — the cheap, checkpointed Haiku catalog pass over
every lesson's written text (`*_lesson.md`). It deliberately ignores the 3rd-party
video transcripts (setup mechanics, ~650K tokens of re-embedded tutorials); the
strategy lives in Duncan's own lesson prose, which names every tool and automation.

  Pass: one Haiku call per *_lesson.md  → structured JSON, checkpointed/resumable
  Out:  courses/buildroom/_phaseB/catalog.json   (per-lesson)
        courses/buildroom/_phaseB/inventory.md   (aggregated, human-readable)
  Log:  logs/analyzer_log.json (shared)

The architecture decomposition and the June-2026 replacement research are done by
Claude directly against the methodology courses + this catalog — not by this script.
"""
import glob
import json
import os
import time
from datetime import datetime, timezone

import anthropic

from src.utils import ai

COURSE_ROOT = os.path.join("courses", "buildroom")
PHASEB_DIR = os.path.join(COURSE_ROOT, "_phaseB")
CATALOG_PATH = os.path.join(PHASEB_DIR, "catalog.json")
INVENTORY_PATH = os.path.join(PHASEB_DIR, "inventory.md")
ANALYZER_LOG = "logs/analyzer_log.json"


def _load_env():
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

_load_env()


def _read_file(path, max_chars=8000):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(max_chars)
    except Exception:
        return ""


def _load_catalog():
    if os.path.exists(CATALOG_PATH):
        try:
            with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_catalog(catalog):
    os.makedirs(PHASEB_DIR, exist_ok=True)
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)


def _lesson_files():
    """All *_lesson.md under courses/buildroom, sorted for stable order."""
    pattern = os.path.join(COURSE_ROOT, "**", "*_lesson.md")
    return sorted(glob.glob(pattern, recursive=True))


def _extract_one(client, model, course, title, body):
    """One Haiku call → structured strategic catalog entry. Returns (dict|None, tokens)."""
    content = f"""You are a content-automation strategist reverse-engineering a paid
course on building an automated personal-brand content pipeline. Analyze ONE lesson
and return ONLY JSON (no prose, no markdown fences) with exactly this structure:

{{
  "pipeline_stage": "one of: research | extract | recreate | execute | distribute | repeat | scale | monetize | tooling | mindset | onboarding | other",
  "tools": ["named tools/apps/platforms mentioned, e.g. n8n, Claude Code, Blotato, TrendJacker"],
  "paid_services": ["only the tools that are paid/subscription, e.g. Blotato, Apify"],
  "automations": ["concrete automations or workflows described, short noun phrases"],
  "technique_summary": "ONE sentence: the strategic point of this lesson",
  "outdated_risk": "low | medium | high — plus 3-6 words why (e.g. 'high: model/tool moves fast')",
  "replaceable_by": "ONE short phrase: a free or already-owned tool that could replace the paid/manual part, or '' if none obvious"
}}

COURSE: {course}
LESSON TITLE: {title}

LESSON TEXT:
{body}"""
    try:
        text, usage = ai.create(
            client,
            task="buildroom_catalog",
            model=model,
            max_tokens=600,
            system="Return ONLY valid minified JSON. No prose. No markdown.",
            messages=[{"role": "user", "content": content}],
        )
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        tokens = usage["input_tokens"] + usage["output_tokens"]
        return json.loads(text), tokens
    except Exception as e:
        print(f"[WARN] extract failed: {e}")
        return None, 0


def _course_and_title(path):
    """Derive a readable course + lesson title from the path and file header."""
    rel = os.path.relpath(path, COURSE_ROOT)
    parts = rel.split(os.sep)
    course = parts[0] if parts else "?"
    # Strip leading "NN_" and prettify
    course = course.split("_", 1)[-1].replace("-", " ").title()
    title = os.path.basename(path).replace("_lesson.md", "")
    title = title.split("_", 1)[-1].replace("-", " ")
    return course, title


def run_catalog(limit=None, force=False):
    """
    Checkpointed Haiku catalog pass over every lesson's written text.

    Args:
        limit: process at most N new lessons this run (for smoke tests). None = all.
        force: re-extract even lessons already in the checkpoint.
    """
    model = os.getenv("ANALYZER_MODEL", "claude-haiku-4-5-20251001")

    if not os.path.isdir(COURSE_ROOT):
        print(f"[BUILDROOM] No corpus at {COURSE_ROOT}. Run the skool-archive first.")
        return

    client = anthropic.Anthropic()
    catalog = _load_catalog()
    files = _lesson_files()
    print(f"[BUILDROOM] {len(files)} lesson files; {len(catalog)} already in catalog.")

    todo = [p for p in files if force or os.path.relpath(p, COURSE_ROOT) not in catalog]
    if limit:
        todo = todo[:limit]
    if not todo:
        print("[BUILDROOM] Catalog already complete. Use force=True to rebuild.")
        _write_inventory(catalog)
        return

    print(f"[BUILDROOM] Extracting {len(todo)} lesson(s) with {model} ...")
    api_calls = 0
    total_tokens = 0

    for i, path in enumerate(todo, 1):
        rel = os.path.relpath(path, COURSE_ROOT)
        course, title = _course_and_title(path)
        body = _read_file(path)
        if not body.strip():
            catalog[rel] = {"skipped": "empty"}
            continue

        print(f"  [{i}/{len(todo)}] {title[:60]} ...", end=" ", flush=True)
        result, tokens = _extract_one(client, model, course, title, body)
        api_calls += 1
        total_tokens += tokens

        if result:
            result["course"] = course
            result["lesson_title"] = title
            result["rel_path"] = rel
            catalog[rel] = result
            print("ok")
        else:
            print("skipped")

        # Checkpoint every 10 so a crash never loses much.
        if i % 10 == 0:
            _save_catalog(catalog)

        if i < len(todo):
            time.sleep(0.3)

    _save_catalog(catalog)
    _write_inventory(catalog)
    _append_log("buildroom_catalog", len([k for k in catalog if "skipped" not in catalog[k]]),
                api_calls, total_tokens, INVENTORY_PATH)
    print(f"\n[BUILDROOM] Catalog saved: {CATALOG_PATH}")
    print(f"[BUILDROOM] Inventory written: {INVENTORY_PATH}")
    print(f"[BUILDROOM] API calls: {api_calls} | Tokens: {total_tokens:,}")


def _write_inventory(catalog):
    """Aggregate the per-lesson catalog into a compact human/LLM-readable inventory."""
    from collections import Counter, defaultdict

    entries = [v for v in catalog.values() if isinstance(v, dict) and "skipped" not in v]
    tool_counts = Counter()
    paid_counts = Counter()
    stage_counts = Counter()
    automations_by_stage = defaultdict(list)
    replaceable = []

    for e in entries:
        for t in e.get("tools", []) or []:
            tool_counts[t.strip()] += 1
        for p in e.get("paid_services", []) or []:
            paid_counts[p.strip()] += 1
        stage = (e.get("pipeline_stage") or "other").strip()
        stage_counts[stage] += 1
        for a in e.get("automations", []) or []:
            automations_by_stage[stage].append(a.strip())
        rb = (e.get("replaceable_by") or "").strip()
        if rb:
            replaceable.append((e.get("lesson_title", "?"),
                                ", ".join(e.get("paid_services") or []) or "manual", rb))

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Build Room — Tool & Automation Inventory (Phase B, Step 1)",
        f"_Generated {now} from {len(entries)} lesson texts._",
        "",
        "Auto-extracted by `buildroom_analyzer.py` (Haiku). Source material for the",
        "strategic teardown in `ANALYSIS_feature-feasibility.md`.",
        "",
        "## Tools mentioned (by lesson frequency)",
        "",
    ]
    for tool, n in tool_counts.most_common():
        paid = " **[PAID]**" if tool in paid_counts else ""
        lines.append(f"- {tool} — {n}{paid}")

    lines += ["", "## Paid services (the replacement targets)", ""]
    for tool, n in paid_counts.most_common():
        lines.append(f"- {tool} — referenced in {n} lesson(s)")

    lines += ["", "## Pipeline stages (lesson coverage)", ""]
    for stage, n in stage_counts.most_common():
        lines.append(f"- **{stage}** — {n} lesson(s)")

    lines += ["", "## Automations by stage", ""]
    for stage in stage_counts:
        autos = sorted(set(automations_by_stage[stage]))
        if not autos:
            continue
        lines.append(f"### {stage}")
        for a in autos:
            lines.append(f"- {a}")
        lines.append("")

    lines += ["## Replacement candidates (paid/manual → free/owned)", ""]
    for title, paid, rb in replaceable:
        lines.append(f"- *{title}* — {paid} → {rb}")

    os.makedirs(PHASEB_DIR, exist_ok=True)
    with open(INVENTORY_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _append_log(run_kind, items, api_calls, tokens_used, output_file):
    os.makedirs("logs", exist_ok=True)
    log = {"runs": []}
    if os.path.exists(ANALYZER_LOG):
        try:
            with open(ANALYZER_LOG, "r", encoding="utf-8") as f:
                log = json.load(f)
        except Exception:
            pass
    estimated_cost = round(tokens_used / 1_000_000 * 1.0, 6)
    log["runs"].append({
        "run_id": datetime.now().strftime("%Y-%m-%d_%H%M%S"),
        "kind": run_kind,
        "items_processed": items,
        "api_calls_made": api_calls,
        "tokens_used": tokens_used,
        "estimated_cost_usd": estimated_cost,
        "output_file": output_file,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    with open(ANALYZER_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
