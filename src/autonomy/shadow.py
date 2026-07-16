"""
Autonomy L1 — shadow verdict logging.

The first rung of the progressive-autonomy ladder. For every asset that reaches
the human review gate, the system PREDICTS a verdict (ship / fix / kill) by
scoring it against Randy's kill-rubric + voice profile, logs that prediction,
and later records Randy's ACTUAL call beside it. No publishing behaviour changes
— L1 only observes, so it is safe and fully reversible.

After a few weeks, agreement_report() shows — per content type — how often the
AI matched Randy and, critically, the FALSE-APPROVE count (AI said "ship" where
Randy would have said "kill"). That scorecard is what earns a content type its
way to higher autonomy levels later. Nothing is auto-approved at L1.

Log: logs/shadow_log.jsonl — one JSON object per line,
gitignored. Two record kinds, joined by (slug, content_type):
  {"phase": "prediction", "ai_verdict": ..., "ai_confidence": ..., ...}
  {"phase": "actual",     "actual_verdict": ..., "note": ...}

CLI:
  python -m src.main shadow-score  <slug> [content_type]
  python -m src.main shadow-verdict <slug> ship|fix|kill [--type T] [--note "..."]
  python -m src.main shadow-report
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from src.utils.ai import create as ai_create

ROOT = Path(__file__).resolve().parent.parent.parent
RUBRIC_PATH = ROOT / "knowledge" / "me" / "kill_rubric.md"
VOICE_PATH = ROOT / "knowledge" / "me" / "voice.md"
LOG_PATH = ROOT / "logs" / "shadow_log.jsonl"
PENDING_DIR = ROOT / "content-engine" / "content"

VERDICTS = ("ship", "fix", "kill")
_DEFAULT_MODEL = "claude-haiku-4-5-20251001"


# ---------------------------------------------------------------------------
# Small IO helpers
# ---------------------------------------------------------------------------

def _read(path):
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _append_log(record, log_path=None):
    path = Path(log_path) if log_path else LOG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_log(log_path=None):
    """Read the shadow log into a list of dicts (skips blank/corrupt lines)."""
    path = Path(log_path) if log_path else LOG_PATH
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def _load_asset_text(slug):
    """Best-effort: return (content_type, text) for a pending asset folder.

    Prefers the article body ("<slug>.md"), then the loop draft ("text-post.md"),
    then the first non-README markdown file. content_type is inferred from which.
    """
    folder = PENDING_DIR / slug
    if not folder.is_dir():
        return None, None
    article = folder / f"{slug}.md"
    if article.exists():
        return "article", article.read_text(encoding="utf-8")
    text_post = folder / "text-post.md"
    if text_post.exists():
        return "text-post", text_post.read_text(encoding="utf-8")
    for md in sorted(folder.glob("*.md")):
        if md.name == "_README.md":
            continue
        return md.stem, md.read_text(encoding="utf-8")
    return None, None


# ---------------------------------------------------------------------------
# Prediction (the one AI call)
# ---------------------------------------------------------------------------

_SYSTEM = (
    "You are Randy Skiles' content gatekeeper. Using his kill-rubric and voice "
    "profile, predict whether Randy would SHIP, FIX, or KILL the asset. Be strict: "
    "any hard-kill rule = kill; a fixable problem = fix; only a clean, on-voice, "
    "hook-passing asset = ship. Return ONLY valid JSON, no prose."
)


def predict_verdict(asset_text, content_type, *, client=None, model=None,
                    rubric=None, voice=None):
    """Score one asset against the rubric. Returns a prediction dict.

    On success: {"verdict","confidence","reasons","rubric_flags","model","tokens","ok":True}
    On failure: {"ok": False, "error": "..."}  (never raises)
    """
    model = model or os.getenv("SHADOW_MODEL") or os.getenv("ANALYZER_MODEL") or _DEFAULT_MODEL
    rubric = rubric if rubric is not None else _read(RUBRIC_PATH)
    voice = voice if voice is not None else _read(VOICE_PATH)

    prompt = (
        f"KILL-RUBRIC (Randy's vetting criteria):\n{rubric}\n\n"
        f"VOICE PROFILE (abridged context):\n{voice[:4000]}\n\n"
        f"CONTENT TYPE: {content_type}\n\n"
        f"ASSET TO VET:\n{asset_text}\n\n"
        "Return JSON exactly:\n"
        '{"verdict":"ship|fix|kill","confidence":0.0-1.0,'
        '"reasons":["short reason", ...],'
        '"rubric_flags":["rule name it hit", ...]}'
    )

    try:
        client = client or _make_client()
        text, usage = ai_create(
            client,
            task="shadow_verdict",
            model=model,
            max_tokens=700,
            system=_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:  # noqa: BLE001 — never break the pipeline over vetting
        return {"ok": False, "error": str(e)}

    parsed = _parse_json(text)
    if parsed is None:
        return {"ok": False, "error": "could not parse model JSON"}

    verdict = str(parsed.get("verdict", "")).strip().lower()
    if verdict not in VERDICTS:
        return {"ok": False, "error": f"invalid verdict: {verdict!r}"}

    return {
        "ok": True,
        "verdict": verdict,
        "confidence": _clamp(parsed.get("confidence")),
        "reasons": list(parsed.get("reasons") or []),
        "rubric_flags": list(parsed.get("rubric_flags") or []),
        "model": model,
        "tokens": int(usage.get("input_tokens", 0)) + int(usage.get("output_tokens", 0)),
    }


def _make_client():
    import anthropic
    return anthropic.Anthropic()


def _parse_json(text):
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _clamp(v):
    try:
        return max(0.0, min(1.0, float(v)))
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Logging predictions + actuals
# ---------------------------------------------------------------------------

def log_prediction(slug, content_type, prediction, log_path=None):
    """Append a prediction record (only when the prediction succeeded)."""
    if not prediction.get("ok"):
        return False
    _append_log({
        "ts": datetime.now(timezone.utc).isoformat(),
        "phase": "prediction",
        "slug": slug,
        "content_type": content_type,
        "ai_verdict": prediction["verdict"],
        "ai_confidence": prediction.get("confidence"),
        "ai_reasons": prediction.get("reasons", []),
        "rubric_flags": prediction.get("rubric_flags", []),
        "model": prediction.get("model"),
        "tokens": prediction.get("tokens", 0),
    }, log_path=log_path)
    return True


def score_and_log(slug, content_type, asset_text, *, client=None, log_path=None):
    """Predict a verdict for an asset and log it. Non-fatal — returns the prediction."""
    prediction = predict_verdict(asset_text, content_type, client=client)
    if prediction.get("ok"):
        log_prediction(slug, content_type, prediction, log_path=log_path)
    return prediction


def record_actual(slug, actual_verdict, *, content_type=None, note="", log_path=None):
    """Record Randy's real call. content_type defaults to the latest prediction's."""
    verdict = str(actual_verdict).strip().lower()
    if verdict not in VERDICTS:
        raise ValueError(f"verdict must be one of {VERDICTS}, got {actual_verdict!r}")
    if content_type is None:
        content_type = _latest_prediction_type(slug, log_path=log_path) or "unknown"
    _append_log({
        "ts": datetime.now(timezone.utc).isoformat(),
        "phase": "actual",
        "slug": slug,
        "content_type": content_type,
        "actual_verdict": verdict,
        "note": note,
    }, log_path=log_path)
    return content_type


def _latest_prediction_type(slug, log_path=None):
    ctype = None
    for rec in load_log(log_path=log_path):
        if rec.get("phase") == "prediction" and rec.get("slug") == slug:
            ctype = rec.get("content_type")
    return ctype


# ---------------------------------------------------------------------------
# Agreement scorecard
# ---------------------------------------------------------------------------

def agreement_report(log_path=None):
    """Pair the latest prediction + latest actual per (slug, content_type) and
    roll up per content type. Pure over the log file — easy to test.

    Returns {
      "by_type": {ctype: {"paired","agree","false_approve","ship_ok","pending"}},
      "totals": {...same keys...},
      "unscored_actuals": int,
    }
    """
    latest_pred, latest_actual = {}, {}
    for rec in load_log(log_path=log_path):
        key = (rec.get("slug"), rec.get("content_type"))
        if rec.get("phase") == "prediction":
            latest_pred[key] = rec.get("ai_verdict")
        elif rec.get("phase") == "actual":
            latest_actual[key] = rec.get("actual_verdict")

    by_type, unscored = {}, 0
    for key, pred in latest_pred.items():
        ctype = key[1] or "unknown"
        bucket = by_type.setdefault(ctype, _empty_bucket())
        actual = latest_actual.get(key)
        if actual is None:
            bucket["pending"] += 1
            continue
        bucket["paired"] += 1
        if pred == actual:
            bucket["agree"] += 1
        if pred == "ship" and actual == "kill":
            bucket["false_approve"] += 1
        if pred == "ship" and actual == "ship":
            bucket["ship_ok"] += 1

    # actuals recorded with no matching prediction (shouldn't normally happen)
    for key in latest_actual:
        if key not in latest_pred:
            unscored += 1

    totals = _empty_bucket()
    for b in by_type.values():
        for k in totals:
            totals[k] += b[k]

    return {"by_type": by_type, "totals": totals, "unscored_actuals": unscored}


def _empty_bucket():
    return {"paired": 0, "agree": 0, "false_approve": 0, "ship_ok": 0, "pending": 0}


def format_report(report):
    """Render the agreement report as printable lines."""
    lines = ["━" * 54, " Shadow Verdict Scorecard (autonomy L1)", "━" * 54]
    by_type = report.get("by_type", {})
    if not by_type:
        lines.append(" No predictions logged yet.")
        lines.append("━" * 54)
        return lines
    for ctype in sorted(by_type):
        b = by_type[ctype]
        rate = f"{(b['agree'] / b['paired'] * 100):.0f}%" if b["paired"] else "—"
        lines.append(
            f" {ctype:<16} paired {b['paired']:>3} · agree {rate:>4} · "
            f"false-approve {b['false_approve']} · pending {b['pending']}"
        )
    t = report["totals"]
    rate = f"{(t['agree'] / t['paired'] * 100):.0f}%" if t["paired"] else "—"
    lines.append("-" * 54)
    lines.append(
        f" TOTAL            paired {t['paired']:>3} · agree {rate:>4} · "
        f"false-approve {t['false_approve']} · pending {t['pending']}"
    )
    if report.get("unscored_actuals"):
        lines.append(f" (note: {report['unscored_actuals']} actual(s) had no prediction)")
    lines.append(" Promotion to autonomy L3 needs high agreement + 0 false-approves per type.")
    lines.append("━" * 54)
    return lines


# ---------------------------------------------------------------------------
# CLI runners
# ---------------------------------------------------------------------------

def run_shadow_score(slug, content_type=None):
    ctype = content_type
    if ctype:
        text = None
        folder = PENDING_DIR / slug
        candidate = folder / f"{ctype}.md"
        text = candidate.read_text(encoding="utf-8") if candidate.exists() else None
        if text is None:
            ctype_auto, text = _load_asset_text(slug)
            ctype = ctype or ctype_auto
    else:
        ctype, text = _load_asset_text(slug)
    if not text:
        print(f"[shadow] No readable asset found in content-engine/content/{slug}/")
        return
    print(f"[shadow] Scoring {slug} ({ctype}) against the kill-rubric...")
    pred = score_and_log(slug, ctype, text)
    if not pred.get("ok"):
        print(f"[shadow] Prediction failed: {pred.get('error')}")
        return
    print(f"  AI verdict : {pred['verdict'].upper()}  (confidence {pred.get('confidence')})")
    if pred.get("rubric_flags"):
        print(f"  Rubric hits: {', '.join(pred['rubric_flags'])}")
    for r in pred.get("reasons", []):
        print(f"   - {r}")
    print(f"  Logged. Record your real call: "
          f'python -m src.main shadow-verdict {slug} ship|fix|kill')


def run_shadow_verdict(slug, verdict, note="", content_type=None):
    try:
        ctype = record_actual(slug, verdict, content_type=content_type, note=note)
    except ValueError as e:
        print(f"[shadow] {e}")
        return
    print(f"[shadow] Recorded your verdict for {slug} ({ctype}): {verdict.upper()}")


def run_shadow_report():
    print("\n".join(format_report(agreement_report())))
