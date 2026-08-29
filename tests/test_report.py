"""
Tests for src/report.py — AI cost report.

1. build_report sums spend + counts within the window, folds the analyzer_log,
   and reports cache savings
2. entries outside the window are excluded from the window totals but counted
   all-time
"""
import json
from datetime import datetime, timezone

from src import report


NOW = datetime(2026, 6, 14, 12, 0, tzinfo=timezone.utc)


def _write(path, obj):
    path.write_text(json.dumps(obj), encoding="utf-8")


def test_build_report_window_and_savings(tmp_path, monkeypatch):
    ledger = {"entries": [
        {"ts": "2026-06-13T10:00:00+00:00", "task": "buildroom_catalog", "model": "claude-haiku-4-5",
         "input_tokens": 1_000_000, "output_tokens": 0, "cost": 1.0, "cached": False},
        {"ts": "2026-06-13T11:00:00+00:00", "task": "buildroom_catalog", "model": "claude-haiku-4-5",
         "input_tokens": 1_000_000, "output_tokens": 0, "cost": 0.0, "cached": True},   # saved ~$1
        {"ts": "2026-05-01T10:00:00+00:00", "task": "old", "model": "claude-haiku-4-5",
         "input_tokens": 500_000, "output_tokens": 0, "cost": 0.5, "cached": False},     # outside 7d
    ]}
    analyzer = {"runs": [
        {"timestamp": "2026-06-14T09:00:00+00:00", "kind": "pain_points",
         "tokens_used": 200_000, "estimated_cost_usd": 0.20},
    ]}
    led_path = tmp_path / "ledger.json"
    an_path = tmp_path / "analyzer.json"
    _write(led_path, ledger)
    _write(an_path, analyzer)
    monkeypatch.setattr(report, "LEDGER", str(led_path))
    monkeypatch.setattr(report, "ANALYZER_LOG", str(an_path))

    text = "\n".join(report.build_report(now=NOW, days=7))

    # window = 2 ledger (within 7d) + 1 analyzer = 3 calls, 1 cached
    assert "Calls:  3  (1 cached)" in text
    # spend = 1.0 (ledger) + 0.20 (analyzer) = 1.20
    assert "$1.2000" in text
    # cache saved ~$1.00
    assert "saved $1.0000 via cache" in text
    # all-time includes the out-of-window $0.5 -> 1.0 + 0.5 + 0.2 = 1.70
    assert "All-time spend: $1.7000" in text


def test_build_report_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(report, "LEDGER", str(tmp_path / "none.json"))
    monkeypatch.setattr(report, "ANALYZER_LOG", str(tmp_path / "none2.json"))
    text = "\n".join(report.build_report(now=NOW, days=7))
    assert "Calls:  0" in text
    assert "$0.0000" in text
