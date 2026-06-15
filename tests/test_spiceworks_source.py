"""
Tests for the Spiceworks (Discourse) source in src/trend_finder/source_scanner.py.

1. _fetch_spiceworks_tag maps Discourse topic JSON -> candidate dicts (with
   engagement in the summary + a built topic URL), skipping empty titles
2. _fetch_spiceworks_tag returns [] on fetch failure
3. scan_spiceworks aggregates across the configured tags (no real sleeping/network)
"""
from unittest.mock import patch, MagicMock

from src.trend_finder import source_scanner as ss


def _fake_resp(payload):
    r = MagicMock()
    r.json.return_value = payload
    r.status_code = 200
    return r


def test_fetch_spiceworks_tag_builds_candidates():
    payload = {"topic_list": {"topics": [
        {"id": 123, "slug": "how-to-automate", "title": "How to automate X?",
         "posts_count": 5, "views": 270},
        {"id": 124, "slug": "ai-build", "title": "What is everyone building with AI?",
         "posts_count": 22, "views": 751},
        {"id": 125, "slug": "blank", "title": "   ", "posts_count": 1, "views": 1},  # skipped
    ]}}
    with patch.object(ss, "_get_direct_first", return_value=_fake_resp(payload)):
        cands = ss._fetch_spiceworks_tag("process-automation")

    assert len(cands) == 2
    c = cands[0]
    assert c["title"] == "How to automate X?"
    assert c["source"] == "spiceworks:process-automation"
    assert c["url"] == "https://community.spiceworks.com/t/how-to-automate/123"
    assert "270 views" in c["summary"]


def test_fetch_spiceworks_tag_handles_failure():
    with patch.object(ss, "_get_direct_first", side_effect=Exception("boom")):
        assert ss._fetch_spiceworks_tag("anything") == []


def test_scan_spiceworks_aggregates(monkeypatch):
    monkeypatch.setattr(ss, "SPICEWORKS_TAGS", ["a", "b"])
    monkeypatch.setattr(ss.time, "sleep", lambda *a, **k: None)  # no real pause

    def fake_fetch(slug, limit=10):
        return [{"title": f"t-{slug}", "summary": "", "source": f"spiceworks:{slug}", "url": None}]

    monkeypatch.setattr(ss, "_fetch_spiceworks_tag", fake_fetch)
    out = ss.scan_spiceworks()
    assert {c["source"] for c in out} == {"spiceworks:a", "spiceworks:b"}
