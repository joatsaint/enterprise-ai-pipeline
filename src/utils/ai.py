"""
AI call wrapper — disk response cache + cost ledger in one place.

Two Tier-1 pipeline wins (see content-engine/pipeline_backlog.md):
  - Caching: identical requests (same model/system/messages) return a stored
    response instead of re-calling the API. Re-runs over static input cost $0.
  - Cost ledger: every call records {task, model, tokens, cost, cached} to
    logs/ai_cost_ledger.json, so `src.main report` can show weekly spend.

Use `create(client, task=..., model=..., max_tokens=..., system=..., messages=...)`
in place of `client.messages.create(...)`. Returns (text, usage) where usage is
{input_tokens, output_tokens, cost, cached}.

Pricing is approximate (USD per 1M tokens) — good enough for a spend estimate.
"""
import hashlib
import json
import os
from datetime import datetime, timezone

from src.utils.atomic import atomic_write_json

CACHE_DIR = os.path.join(".cache", "ai")
LEDGER = os.path.join("logs", "ai_cost_ledger.json")

# Approximate prices per 1M tokens (input, output). Matched by substring of model id.
PRICES = {
    "haiku": (1.0, 5.0),
    "sonnet": (3.0, 15.0),
    "opus": (15.0, 75.0),
}


def estimate_cost(model, input_tokens, output_tokens):
    key = next((k for k in PRICES if k in (model or "").lower()), "haiku")
    pin, pout = PRICES[key]
    return round(input_tokens / 1_000_000 * pin + output_tokens / 1_000_000 * pout, 6)


def _cache_key(model, max_tokens, system, messages):
    payload = json.dumps(
        {"model": model, "max_tokens": max_tokens, "system": system, "messages": messages},
        sort_keys=True, ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _cache_path(key):
    return os.path.join(CACHE_DIR, key + ".json")


def _cache_get(key):
    try:
        with open(_cache_path(key), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _cache_put(key, value):
    atomic_write_json(_cache_path(key), value)


def _load_ledger(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
            if isinstance(d, dict) and isinstance(d.get("entries"), list):
                return d
    except Exception:
        pass
    return {"entries": []}


def record_usage(task, model, input_tokens, output_tokens, cached=False, ledger_path=None):
    """Append one usage entry to the cost ledger (atomic). Cached calls cost $0."""
    ledger_path = ledger_path or LEDGER
    cost = 0.0 if cached else estimate_cost(model, input_tokens, output_tokens)
    ledger = _load_ledger(ledger_path)
    ledger["entries"].append({
        "ts": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": cost,
        "cached": bool(cached),
    })
    atomic_write_json(ledger_path, ledger)
    return cost


def create(client, *, task, model, max_tokens, system, messages, use_cache=True):
    """
    Drop-in for client.messages.create that caches responses and ledgers cost.

    Returns (text, usage) where usage = {input_tokens, output_tokens, cost, cached}.
    """
    if use_cache:
        key = _cache_key(model, max_tokens, system, messages)
        hit = _cache_get(key)
        if hit is not None:
            it, ot = hit.get("input_tokens", 0), hit.get("output_tokens", 0)
            record_usage(task, model, it, ot, cached=True)
            return hit["text"], {"input_tokens": it, "output_tokens": ot, "cost": 0.0, "cached": True}

    resp = client.messages.create(model=model, max_tokens=max_tokens, system=system, messages=messages)
    text = resp.content[0].text
    it = resp.usage.input_tokens
    ot = resp.usage.output_tokens
    if use_cache:
        _cache_put(key, {"text": text, "input_tokens": it, "output_tokens": ot})
    cost = record_usage(task, model, it, ot, cached=False)
    return text, {"input_tokens": it, "output_tokens": ot, "cost": cost, "cached": False}
