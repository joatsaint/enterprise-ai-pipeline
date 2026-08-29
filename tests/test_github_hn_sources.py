"""
Tests for the GitHub and Hacker News sources in src/trend_finder/source_scanner.py.

1. _fetch_github_term maps GitHub Search API JSON -> candidate dicts, skips
   repos with no name, and quotes the search term (exact-phrase match --
   unquoted was confirmed empirically to dilute results with generic-word
   noise, see the comment in source_scanner.py)
2. _fetch_github_term returns [] on fetch failure, and [] (not a raise) when
   the search rate limit is hit (403 + X-RateLimit-Remaining: 0)
3. scan_github aggregates across BUILD_SIGNAL_TERMS (no real sleeping/network)
4. _fetch_hn_term maps Algolia HN Search API JSON -> candidate dicts, skips
   hits with no title, and falls back to the HN item URL when a story has no
   external url
5. _fetch_hn_term returns [] on fetch failure
6. scan_hackernews aggregates across BUILD_SIGNAL_TERMS (no real sleeping/network)
"""
from unittest.mock import patch, MagicMock

from src.trend_finder import source_scanner as ss


def _fake_resp(json_data, status_code=200, headers=None):
    r = MagicMock()
    r.status_code = status_code
    r.headers = headers or {}
    r.json.return_value = json_data
    r.raise_for_status = MagicMock()
    return r


# ---------------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------------

def test_fetch_github_term_builds_candidates_and_quotes_term():
    payload = {"items": [
        {"full_name": "someone/jarvis-clone", "description": "A local Jarvis-style assistant",
         "stargazers_count": 12, "created_at": "2026-07-01T00:00:00Z",
         "html_url": "https://github.com/someone/jarvis-clone"},
        {"full_name": "", "description": "no name, should be skipped",
         "stargazers_count": 0, "created_at": "2026-07-01T00:00:00Z", "html_url": None},
    ]}
    with patch.object(ss.requests, "get", return_value=_fake_resp(payload)) as mock_get:
        cands = ss._fetch_github_term("Jarvis build")

    assert len(cands) == 1
    c = cands[0]
    assert c["title"] == "someone/jarvis-clone"
    assert c["source"] == "github:Jarvis build"
    assert c["url"] == "https://github.com/someone/jarvis-clone"
    assert "12 stars" in c["summary"]
    assert "2026-07-01" in c["summary"]

    # The search term must be quoted for exact-phrase matching, not passed raw.
    called_params = mock_get.call_args.kwargs["params"]
    assert '"Jarvis build"' in called_params["q"]


def test_fetch_github_term_handles_failure():
    with patch.object(ss.requests, "get", side_effect=Exception("boom")):
        assert ss._fetch_github_term("anything") == []


def test_fetch_github_term_handles_rate_limit_without_raising():
    resp = _fake_resp({}, status_code=403, headers={"X-RateLimit-Remaining": "0"})
    with patch.object(ss.requests, "get", return_value=resp):
        assert ss._fetch_github_term("anything") == []


def test_scan_github_aggregates(monkeypatch):
    monkeypatch.setattr(ss, "BUILD_SIGNAL_TERMS", ["term-a", "term-b"])
    monkeypatch.setattr(ss.time, "sleep", lambda *a, **k: None)

    def fake_fetch(term, limit=10):
        return [{"title": f"repo-for-{term}", "summary": "", "source": f"github:{term}", "url": None}]

    monkeypatch.setattr(ss, "_fetch_github_term", fake_fetch)
    out = ss.scan_github()
    assert {c["source"] for c in out} == {"github:term-a", "github:term-b"}


# ---------------------------------------------------------------------------
# Hacker News
# ---------------------------------------------------------------------------

def test_fetch_hn_term_builds_candidates():
    payload = {"hits": [
        {"title": "Show HN: build your own Jarvis on Claude Code", "points": 240,
         "num_comments": 88, "objectID": "12345", "url": "https://example.com/jarvis-post"},
        {"title": "", "points": 1, "num_comments": 0, "objectID": "999", "url": None},  # skipped
    ]}
    with patch.object(ss.requests, "get", return_value=_fake_resp(payload)):
        cands = ss._fetch_hn_term("Jarvis build")

    assert len(cands) == 1
    c = cands[0]
    assert c["title"] == "Show HN: build your own Jarvis on Claude Code"
    assert c["source"] == "hackernews:Jarvis build"
    assert c["url"] == "https://example.com/jarvis-post"
    assert "240 points" in c["summary"]


def test_fetch_hn_term_falls_back_to_hn_url_when_no_external_url():
    payload = {"hits": [
        {"title": "Ask HN: anyone else building a local AI OS?", "points": 50,
         "num_comments": 10, "objectID": "54321", "url": None},
    ]}
    with patch.object(ss.requests, "get", return_value=_fake_resp(payload)):
        cands = ss._fetch_hn_term("AI operating system")

    assert cands[0]["url"] == "https://news.ycombinator.com/item?id=54321"


def test_fetch_hn_term_handles_failure():
    with patch.object(ss.requests, "get", side_effect=Exception("boom")):
        assert ss._fetch_hn_term("anything") == []


def test_scan_hackernews_aggregates(monkeypatch):
    monkeypatch.setattr(ss, "BUILD_SIGNAL_TERMS", ["term-a", "term-b"])
    monkeypatch.setattr(ss.time, "sleep", lambda *a, **k: None)

    def fake_fetch(term, limit=10):
        return [{"title": f"story-for-{term}", "summary": "", "source": f"hackernews:{term}", "url": None}]

    monkeypatch.setattr(ss, "_fetch_hn_term", fake_fetch)
    out = ss.scan_hackernews()
    assert {c["source"] for c in out} == {"hackernews:term-a", "hackernews:term-b"}
