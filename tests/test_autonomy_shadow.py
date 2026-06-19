"""Tests for the autonomy L1 shadow-verdict logging (no real API calls)."""
import json

import pytest

from src.autonomy import shadow


# --- small helpers -------------------------------------------------------

def test_clamp_bounds():
    assert shadow._clamp(1.5) == 1.0
    assert shadow._clamp(-0.2) == 0.0
    assert shadow._clamp("0.4") == 0.4
    assert shadow._clamp("nope") is None


def test_parse_json_strips_fences():
    assert shadow._parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert shadow._parse_json('{"b": 2}') == {"b": 2}
    assert shadow._parse_json("not json") is None


# --- log round-trip ------------------------------------------------------

def test_log_prediction_and_load(tmp_path):
    log = tmp_path / "shadow_log.jsonl"
    pred = {"ok": True, "verdict": "fix", "confidence": 0.7,
            "reasons": ["weak title"], "rubric_flags": ["title test"],
            "model": "haiku", "tokens": 42}
    assert shadow.log_prediction("SLUG_A", "text-post", pred, log_path=log) is True

    records = shadow.load_log(log_path=log)
    assert len(records) == 1
    assert records[0]["phase"] == "prediction"
    assert records[0]["ai_verdict"] == "fix"
    assert records[0]["slug"] == "SLUG_A"


def test_log_prediction_skips_failed():
    # a failed prediction is never logged
    assert shadow.log_prediction("X", "text-post", {"ok": False}, log_path="unused") is False


def test_record_actual_invalid_verdict(tmp_path):
    with pytest.raises(ValueError):
        shadow.record_actual("SLUG", "maybe", log_path=tmp_path / "l.jsonl")


def test_record_actual_infers_content_type(tmp_path):
    log = tmp_path / "l.jsonl"
    shadow.log_prediction("SLUG_B", "carousel",
                          {"ok": True, "verdict": "ship"}, log_path=log)
    ctype = shadow.record_actual("SLUG_B", "ship", log_path=log)
    assert ctype == "carousel"
    actuals = [r for r in shadow.load_log(log_path=log) if r["phase"] == "actual"]
    assert actuals[0]["content_type"] == "carousel"
    assert actuals[0]["actual_verdict"] == "ship"


# --- scorecard -----------------------------------------------------------

def _pred(slug, ctype, verdict):
    return {"phase": "prediction", "slug": slug, "content_type": ctype, "ai_verdict": verdict}


def _actual(slug, ctype, verdict):
    return {"phase": "actual", "slug": slug, "content_type": ctype, "actual_verdict": verdict}


def test_agreement_report_counts(tmp_path):
    log = tmp_path / "l.jsonl"
    rows = [
        _pred("a", "text-post", "ship"), _actual("a", "text-post", "ship"),   # agree + ship_ok
        _pred("b", "text-post", "ship"), _actual("b", "text-post", "kill"),   # false approve
        _pred("c", "text-post", "fix"),                                       # pending (no actual)
        _pred("d", "carousel", "kill"), _actual("d", "carousel", "kill"),     # agree
    ]
    with open(log, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    report = shadow.agreement_report(log_path=log)
    tp = report["by_type"]["text-post"]
    assert tp["paired"] == 2
    assert tp["agree"] == 1
    assert tp["false_approve"] == 1
    assert tp["ship_ok"] == 1
    assert tp["pending"] == 1

    car = report["by_type"]["carousel"]
    assert car["paired"] == 1 and car["agree"] == 1 and car["false_approve"] == 0

    totals = report["totals"]
    assert totals["paired"] == 3
    assert totals["agree"] == 2
    assert totals["false_approve"] == 1


def test_agreement_report_uses_latest(tmp_path):
    # a later prediction/actual overrides an earlier one for the same key
    log = tmp_path / "l.jsonl"
    rows = [
        _pred("a", "text-post", "kill"),
        _pred("a", "text-post", "ship"),   # latest prediction wins
        _actual("a", "text-post", "ship"),
    ]
    with open(log, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    report = shadow.agreement_report(log_path=log)
    assert report["totals"]["agree"] == 1
    assert report["totals"]["false_approve"] == 0


def test_format_report_empty():
    lines = shadow.format_report({"by_type": {}, "totals": shadow._empty_bucket()})
    assert any("No predictions logged yet" in ln for ln in lines)


# --- prediction (AI call mocked) -----------------------------------------

def test_predict_verdict_success(monkeypatch):
    def fake_create(client, *, task, model, max_tokens, system, messages):
        assert task == "shadow_verdict"
        payload = '{"verdict": "fix", "confidence": 0.8, "reasons": ["r1"], "rubric_flags": ["title test"]}'
        return payload, {"input_tokens": 100, "output_tokens": 20}

    monkeypatch.setattr(shadow, "ai_create", fake_create)
    pred = shadow.predict_verdict("some asset", "text-post",
                                  client=object(), rubric="rubric", voice="voice")
    assert pred["ok"] is True
    assert pred["verdict"] == "fix"
    assert pred["confidence"] == 0.8
    assert pred["tokens"] == 120
    assert "title test" in pred["rubric_flags"]


def test_predict_verdict_invalid_verdict(monkeypatch):
    monkeypatch.setattr(shadow, "ai_create",
                        lambda *a, **k: ('{"verdict": "perhaps"}', {"input_tokens": 1, "output_tokens": 1}))
    pred = shadow.predict_verdict("x", "text-post", client=object(), rubric="", voice="")
    assert pred["ok"] is False
    assert "invalid verdict" in pred["error"]


def test_predict_verdict_non_fatal_on_exception(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("no api key")
    monkeypatch.setattr(shadow, "ai_create", boom)
    pred = shadow.predict_verdict("x", "text-post", client=object(), rubric="", voice="")
    assert pred["ok"] is False
    assert "no api key" in pred["error"]
