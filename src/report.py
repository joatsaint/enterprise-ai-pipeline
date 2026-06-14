"""
AI cost report — weekly spend from the cost ledger (logs/ai_cost_ledger.json),
folding in the legacy analyzer_log so it shows real numbers even before every
caller is wired to the ledger. Read-only, zero tokens.

  python -m src.main report            # last 7 days
  python -m src.main report --days 30
"""
import json
import os
from collections import defaultdict
from datetime import datetime, timezone, timedelta

from src.utils.ai import estimate_cost

LEDGER = os.path.join("logs", "ai_cost_ledger.json")
ANALYZER_LOG = os.path.join("logs", "analyzer_log.json")


def _load(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _parse_ts(ts):
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except Exception:
        return None


def _entries():
    """Unified list of cost events from the ledger + legacy analyzer_log."""
    out = []
    led = _load(LEDGER)
    if isinstance(led, dict):
        for e in led.get("entries", []):
            it, ot = e.get("input_tokens", 0), e.get("output_tokens", 0)
            cached = bool(e.get("cached"))
            out.append({
                "ts": e.get("ts"), "task": e.get("task", "?"), "model": e.get("model", "?"),
                "tokens": it + ot, "cost": e.get("cost", 0.0), "cached": cached,
                "saved": estimate_cost(e.get("model", ""), it, ot) if cached else 0.0,
            })
    an = _load(ANALYZER_LOG)
    if isinstance(an, dict):
        for r in an.get("runs", []):
            out.append({
                "ts": r.get("timestamp"),
                "task": "analyzer:" + str(r.get("kind") or r.get("group") or ""),
                "model": "haiku", "tokens": r.get("tokens_used", 0),
                "cost": r.get("estimated_cost_usd", 0.0), "cached": False, "saved": 0.0,
            })
    return out


def build_report(now=None, days=7):
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    entries = _entries()

    window = [e for e in entries if (_parse_ts(e["ts"]) or now) >= cutoff]
    calls = len(window)
    cached = sum(1 for e in window if e["cached"])
    tokens = sum(e["tokens"] for e in window)
    spend = round(sum(e["cost"] for e in window), 6)
    saved = round(sum(e["saved"] for e in window), 6)

    by_task = defaultdict(lambda: [0, 0.0])  # task -> [calls, cost]
    for e in window:
        by_task[e["task"]][0] += 1
        by_task[e["task"]][1] += e["cost"]

    lines = ["━" * 54, f" AI Cost Report — last {days} days", "━" * 54]
    lines.append(f" Calls:  {calls}  ({cached} cached)")
    lines.append(f" Tokens: {tokens:,}")
    lines.append(f" Spend:  ${spend:.4f}" + (f"   (saved ${saved:.4f} via cache)" if saved else ""))
    if by_task:
        lines.append(" By task:")
        for task, (c, cost) in sorted(by_task.items(), key=lambda kv: kv[1][1], reverse=True):
            lines.append(f"   {task:<28} ${cost:.4f}  ({c} call{'s' if c != 1 else ''})")
    all_time_cost = round(sum(e["cost"] for e in entries), 6)
    lines.append(f" All-time spend: ${all_time_cost:.4f} across {len(entries)} events")
    lines.append("━" * 54)
    return lines


def run_report(days=7):
    print("\n".join(build_report(days=days)))
