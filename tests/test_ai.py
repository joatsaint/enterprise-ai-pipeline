"""
Tests for src/utils/ai.py — AI call wrapper (cache + cost ledger).

1. estimate_cost picks the right per-model price
2. _cache_key is deterministic and order-independent for messages content
3. create(): first call hits the API + ledgers cost; identical second call
   returns from cache (no API call), cost 0, cached True; ledger records both
"""
import json
from unittest.mock import MagicMock

import pytest

from src.utils import ai


def test_estimate_cost():
    # haiku: $1/M in, $5/M out
    assert ai.estimate_cost("claude-haiku-4-5", 1_000_000, 0) == 1.0
    assert ai.estimate_cost("claude-haiku-4-5", 0, 1_000_000) == 5.0
    # sonnet pricier; unknown model falls back to haiku
    assert ai.estimate_cost("claude-sonnet-4-6", 1_000_000, 0) == 3.0
    assert ai.estimate_cost("mystery-model", 1_000_000, 0) == 1.0


def test_cache_key_deterministic():
    a = ai._cache_key("m", 100, "sys", [{"role": "user", "content": "hi"}])
    b = ai._cache_key("m", 100, "sys", [{"role": "user", "content": "hi"}])
    c = ai._cache_key("m", 100, "sys", [{"role": "user", "content": "bye"}])
    assert a == b
    assert a != c


def _fake_client(text='{"ok": 1}', it=100, ot=20):
    resp = MagicMock()
    resp.content = [MagicMock(text=text)]
    resp.usage.input_tokens = it
    resp.usage.output_tokens = ot
    client = MagicMock()
    client.messages.create.return_value = resp
    return client


def test_create_caches_and_ledgers(tmp_path, monkeypatch):
    monkeypatch.setattr(ai, "CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(ai, "LEDGER", str(tmp_path / "ledger.json"))
    client = _fake_client()

    kwargs = dict(task="t", model="claude-haiku-4-5", max_tokens=600,
                  system="sys", messages=[{"role": "user", "content": "hello"}])

    text1, u1 = ai.create(client, **kwargs)
    assert text1 == '{"ok": 1}'
    assert u1["cached"] is False
    assert u1["cost"] > 0
    assert client.messages.create.call_count == 1

    # identical call -> cache hit, no new API call, cost 0
    text2, u2 = ai.create(client, **kwargs)
    assert text2 == text1
    assert u2["cached"] is True
    assert u2["cost"] == 0.0
    assert client.messages.create.call_count == 1  # unchanged

    # ledger recorded both events (one real, one cached)
    ledger = json.loads((tmp_path / "ledger.json").read_text(encoding="utf-8"))
    assert len(ledger["entries"]) == 2
    assert [e["cached"] for e in ledger["entries"]] == [False, True]
