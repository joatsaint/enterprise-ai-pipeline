"""
Trend Finder test suite — Phase 1 (relevance_scorer.py + post_drafter.py) and
Phase 2 (source_scanner.py + orchestrator.py)

Covers:
1. score_topics ranks candidates by relevance and attaches rationale
2. score_topics returns ([], 0) on empty input — no API call made
3. score_topics handles a malformed/failed API response gracefully
4. draft_post produces {post_text, rationale} from a top-ranked topic
5. draft_post returns (None, tokens) when the response is missing a POST section
6. draft_post returns (None, 0) when given no topic — no API call made
7. source_scanner gathers candidates from Reddit, RSS, and the knowledge base
8. orchestrator sequences gather -> score -> draft -> write to pending/

All Claude API calls and HTTP requests are mocked — zero live spend, zero
live network calls, matches the project's existing mocked-test convention
(see test_phase3.py / test_phase4.py).
"""
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fake_response(text, input_tokens=100, output_tokens=50):
    resp = MagicMock()
    resp.content = [MagicMock(text=text)]
    resp.usage.input_tokens = input_tokens
    resp.usage.output_tokens = output_tokens
    return resp


CANDIDATES = [
    {"title": "AI agents are replacing tier-1 helpdesk tickets",
     "summary": "Reddit thread: sysadmins discuss AI triaging support tickets.",
     "source": "reddit:r/sysadmin", "url": "https://reddit.com/r/sysadmin/abc"},
    {"title": "New phone case colors trending on TikTok",
     "summary": "Consumer gadget accessory roundup.",
     "source": "rss:gadget-news", "url": "https://example.com/phone-cases"},
    {"title": "Claude Code now reads enterprise ticketing systems",
     "summary": "Knowledge base theme: recurring questions about AI + ITSM integration.",
     "source": "knowledge_base", "url": None},
]


# ---------------------------------------------------------------------------
# relevance_scorer.score_topics
# ---------------------------------------------------------------------------

def test_score_topics_ranks_by_relevance_with_rationale():
    from src.trend_finder.relevance_scorer import score_topics

    fake_json = json.dumps({
        "ranked": [
            {"index": 2, "score": 0.93, "why_it_fits": "Directly addresses AI replacing IT job functions."},
            {"index": 0, "score": 0.88, "why_it_fits": "Sysadmins fear automation eating their tier-1 work."},
            {"index": 1, "score": 0.05, "why_it_fits": "Consumer gadget content, not relevant to IT careers."},
        ]
    })

    with patch("src.trend_finder.relevance_scorer.anthropic.Anthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages.create.return_value = _fake_response(fake_json)

        ranked, tokens = score_topics(CANDIDATES)

    assert tokens == 150
    assert len(ranked) == 3
    # Sorted highest score first
    assert ranked[0]["title"] == "Claude Code now reads enterprise ticketing systems"
    assert ranked[0]["score"] == 0.93
    assert "AI replacing IT job functions" in ranked[0]["why_it_fits"]
    assert ranked[-1]["title"] == "New phone case colors trending on TikTok"
    assert ranked[-1]["score"] == 0.05
    # Original candidate fields preserved
    assert ranked[0]["source"] == "knowledge_base"


def test_score_topics_empty_input_makes_no_api_call():
    from src.trend_finder.relevance_scorer import score_topics

    with patch("src.trend_finder.relevance_scorer.anthropic.Anthropic") as MockClient:
        ranked, tokens = score_topics([])

    assert ranked == []
    assert tokens == 0
    MockClient.assert_not_called()


def test_score_topics_handles_api_failure_gracefully(capsys):
    from src.trend_finder.relevance_scorer import score_topics

    with patch("src.trend_finder.relevance_scorer.anthropic.Anthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages.create.side_effect = RuntimeError("rate limited")

        ranked, tokens = score_topics(CANDIDATES)

    assert ranked == []
    assert tokens == 0
    captured = capsys.readouterr()
    assert "Relevance scoring failed" in captured.out


# ---------------------------------------------------------------------------
# post_drafter.draft_post
# ---------------------------------------------------------------------------

TOP_TOPIC = {
    "title": "AI agents are replacing tier-1 helpdesk tickets",
    "summary": "Reddit thread: sysadmins discuss AI triaging support tickets.",
    "source": "reddit:r/sysadmin",
    "why_it_fits": "Sysadmins fear automation eating their tier-1 work.",
}


def test_draft_post_returns_post_text_and_rationale():
    from src.trend_finder.post_drafter import draft_post

    fake_text = (
        "POST:\n"
        "I watched a sysadmin forum light up this week over AI triaging tickets. "
        "Here's the thing nobody's saying out loud...\n\n"
        "RATIONALE:\n"
        "This is the exact fear your audience is feeling right now — naming it "
        "directly builds trust instead of dodging it."
    )

    with patch("src.trend_finder.post_drafter.anthropic.Anthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages.create.return_value = _fake_response(fake_text, 200, 120)

        result, tokens = draft_post(TOP_TOPIC, voice_profile="Be conversational.")

    assert tokens == 320
    assert result is not None
    assert result["post_text"].startswith("I watched a sysadmin forum")
    assert "RATIONALE" not in result["post_text"]
    assert "exact fear your audience is feeling" in result["rationale"]


def test_draft_post_missing_post_section_returns_none():
    from src.trend_finder.post_drafter import draft_post

    fake_text = "RATIONALE:\nNo post section was generated, just a rationale."

    with patch("src.trend_finder.post_drafter.anthropic.Anthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages.create.return_value = _fake_response(fake_text, 50, 20)

        result, tokens = draft_post(TOP_TOPIC)

    assert result is None
    assert tokens == 70


def test_draft_post_no_topic_makes_no_api_call():
    from src.trend_finder.post_drafter import draft_post

    with patch("src.trend_finder.post_drafter.anthropic.Anthropic") as MockClient:
        result, tokens = draft_post(None)

    assert result is None
    assert tokens == 0
    MockClient.assert_not_called()


# ---------------------------------------------------------------------------
# source_scanner — all HTTP calls mocked, zero live network/scraping in tests
# ---------------------------------------------------------------------------

def _fake_http_response(status_code=200, json_data=None, content=b"", headers=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = headers or {}
    resp.content = content
    if json_data is not None:
        resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    return resp


REDDIT_PAGE = {
    "data": {
        "children": [
            {"data": {
                "title": "AI is replacing tier-1 helpdesk roles, sysadmins say",
                "selftext": "Long thread about automation anxiety.",
                "permalink": "/r/sysadmin/comments/abc/ai_helpdesk/",
            }},
            {"data": {"title": "", "selftext": "no title, should be skipped", "permalink": "/r/sysadmin/x"}},
        ]
    }
}

RSS_XML = b"""<?xml version="1.0"?>
<rss><channel>
<item>
  <title>New AI agent tooling for IT pros</title>
  <description>A roundup of automation tools sysadmins are trying.</description>
  <link>https://example.com/ai-agent-tooling</link>
</item>
</channel></rss>"""


def test_scan_reddit_returns_candidates_and_skips_blank_titles():
    from src.trend_finder import source_scanner

    with patch("src.trend_finder.source_scanner.requests.get") as mock_get, \
         patch("src.trend_finder.source_scanner.time.sleep"):
        mock_get.return_value = _fake_http_response(200, json_data=REDDIT_PAGE)

        candidates = source_scanner.scan_reddit()

    assert mock_get.call_count == len(source_scanner.SUBREDDITS)
    titles = [c["title"] for c in candidates]
    assert "AI is replacing tier-1 helpdesk roles, sysadmins say" in titles
    assert "" not in titles
    first = next(c for c in candidates if c["title"].startswith("AI is replacing"))
    assert first["source"] == "reddit:r/sysadmin"
    assert first["url"] == "https://reddit.com/r/sysadmin/comments/abc/ai_helpdesk/"


def test_scan_reddit_handles_fetch_failure_gracefully(capsys):
    from src.trend_finder import source_scanner

    with patch("src.trend_finder.source_scanner.requests.get") as mock_get, \
         patch("src.trend_finder.source_scanner.time.sleep"):
        mock_get.side_effect = RuntimeError("connection reset")

        candidates = source_scanner.scan_reddit()

    assert candidates == []
    captured = capsys.readouterr()
    assert "Reddit fetch failed" in captured.out


def test_scan_rss_parses_items_and_skips_not_modified(capsys):
    from src.trend_finder import source_scanner

    responses = [
        _fake_http_response(200, content=RSS_XML, headers={"Last-Modified": "Mon, 01 Jun 2026 00:00:00 GMT"}),
        _fake_http_response(304),
        _fake_http_response(200, content=RSS_XML, headers={}),
        _fake_http_response(200, content=RSS_XML, headers={}),
    ]

    with patch("src.trend_finder.source_scanner.requests.get", side_effect=responses) as mock_get, \
         patch("src.trend_finder.source_scanner._load_last_fetch_times", return_value={}), \
         patch("src.trend_finder.source_scanner._save_last_fetch_times") as mock_save, \
         patch("src.trend_finder.source_scanner.time.sleep"):
        candidates = source_scanner.scan_rss()

    assert mock_get.call_count == len(source_scanner.RSS_FEEDS)
    assert mock_save.called
    titles = [c["title"] for c in candidates]
    assert titles.count("New AI agent tooling for IT pros") == 3  # one feed returned 304, contributed nothing
    assert all(c["source"].startswith("rss:") for c in candidates)


def test_scan_rss_handles_fetch_failure_gracefully(capsys):
    from src.trend_finder import source_scanner

    with patch("src.trend_finder.source_scanner.requests.get") as mock_get, \
         patch("src.trend_finder.source_scanner._load_last_fetch_times", return_value={}), \
         patch("src.trend_finder.source_scanner._save_last_fetch_times"), \
         patch("src.trend_finder.source_scanner.time.sleep"):
        mock_get.side_effect = RuntimeError("DNS failure")

        candidates = source_scanner.scan_rss()

    assert candidates == []
    captured = capsys.readouterr()
    assert "RSS fetch failed" in captured.out


def test_scan_knowledge_base_makes_no_network_calls():
    from src.trend_finder import source_scanner

    fake_index = {
        "groups": {
            "claude-code": {
                "channels": {
                    "some-channel": {
                        "transcripts": [
                            {"title": "How sysadmins are using Claude Code daily"},
                            {"title": "Automating ticket triage with agents"},
                        ]
                    }
                }
            }
        }
    }

    with patch("src.knowledge_base.indexer.load_index", return_value=fake_index), \
         patch("src.trend_finder.source_scanner.requests.get") as mock_get:
        candidates = source_scanner.scan_knowledge_base()

    mock_get.assert_not_called()
    assert len(candidates) == 2
    assert candidates[0]["source"] == "knowledge_base"
    assert candidates[0]["url"] is None
    assert "How sysadmins are using Claude Code daily" in [c["title"] for c in candidates]


def test_gather_candidates_combines_all_sources():
    from src.trend_finder import source_scanner

    with patch("src.trend_finder.source_scanner.scan_reddit", return_value=[{"title": "r"}]) as mock_reddit, \
         patch("src.trend_finder.source_scanner.scan_spiceworks", return_value=[{"title": "s"}]) as mock_spice, \
         patch("src.trend_finder.source_scanner.scan_rss", return_value=[{"title": "f"}]) as mock_rss, \
         patch("src.trend_finder.source_scanner.scan_knowledge_base", return_value=[{"title": "k"}]) as mock_kb:
        candidates = source_scanner.gather_candidates()

    mock_reddit.assert_called_once()
    mock_spice.assert_called_once()
    mock_rss.assert_called_once()
    mock_kb.assert_called_once()
    assert [c["title"] for c in candidates] == ["r", "s", "f", "k"]


# ---------------------------------------------------------------------------
# orchestrator — sequencing + writing to content-engine/pending/
# ---------------------------------------------------------------------------

TOP_RANKED = [
    {"title": "AI agents are replacing tier-1 helpdesk tickets",
     "summary": "Reddit thread: sysadmins discuss AI triaging support tickets.",
     "source": "reddit:r/sysadmin", "url": "https://reddit.com/r/sysadmin/abc",
     "score": 0.93, "why_it_fits": "Sysadmins fear automation eating their tier-1 work."},
]

DRAFT_RESULT = {
    "post_text": "I watched a sysadmin forum light up this week over AI triaging tickets...",
    "rationale": "This names the exact fear your audience feels right now.",
}


def _patch_pending(tmp_path, monkeypatch):
    from src.trend_finder import orchestrator
    monkeypatch.setattr(orchestrator, "PENDING_DIR", tmp_path / "pending")
    monkeypatch.setattr(orchestrator, "TREND_LOG", tmp_path / "logs" / "trend_finder_log.json")
    monkeypatch.setattr(orchestrator, "VOICE_PATH", tmp_path / "voice.md")
    return orchestrator


def test_run_writes_draft_to_pending_and_logs_run(tmp_path, monkeypatch):
    orchestrator = _patch_pending(tmp_path, monkeypatch)

    with patch.object(orchestrator, "gather_candidates", return_value=[{"title": "x"}]) as mock_gather, \
         patch.object(orchestrator, "score_topics", return_value=(TOP_RANKED, 150)) as mock_score, \
         patch.object(orchestrator, "draft_post", return_value=(DRAFT_RESULT, 320)) as mock_draft:
        summary = orchestrator.run()

    mock_gather.assert_called_once()
    mock_score.assert_called_once()
    mock_draft.assert_called_once()

    assert summary["status"] == "drafted"
    assert summary["topic"] == TOP_RANKED[0]["title"]
    assert summary["score"] == 0.93
    assert summary["tokens_used"] == 470
    assert summary["output_dir"] is not None

    out_dir = tmp_path / "pending" / Path(summary["output_dir"]).name
    assert (out_dir / "text-post.md").exists()
    assert DRAFT_RESULT["post_text"] in (out_dir / "text-post.md").read_text(encoding="utf-8")
    readme = (out_dir / "_README.md").read_text(encoding="utf-8")
    assert "0.93" in readme
    assert "Sysadmins fear automation" in readme

    log_data = json.loads((tmp_path / "logs" / "trend_finder_log.json").read_text(encoding="utf-8"))
    assert len(log_data["runs"]) == 1
    assert log_data["runs"][0]["status"] == "drafted"


def test_run_dry_run_skips_drafting_and_writes_nothing(tmp_path, monkeypatch):
    orchestrator = _patch_pending(tmp_path, monkeypatch)

    with patch.object(orchestrator, "gather_candidates", return_value=[{"title": "x"}]), \
         patch.object(orchestrator, "score_topics", return_value=(TOP_RANKED, 150)), \
         patch.object(orchestrator, "draft_post") as mock_draft:
        summary = orchestrator.run(dry_run=True)

    mock_draft.assert_not_called()
    assert summary["status"] == "dry_run"
    assert summary["output_dir"] is None
    assert not (tmp_path / "pending").exists()


def test_run_no_candidates_short_circuits(tmp_path, monkeypatch):
    orchestrator = _patch_pending(tmp_path, monkeypatch)

    with patch.object(orchestrator, "gather_candidates", return_value=[]), \
         patch.object(orchestrator, "score_topics") as mock_score, \
         patch.object(orchestrator, "draft_post") as mock_draft:
        summary = orchestrator.run()

    mock_score.assert_not_called()
    mock_draft.assert_not_called()
    assert summary["status"] == "no_candidates"
    assert not (tmp_path / "pending").exists()


def test_run_scoring_failure_handled_gracefully(tmp_path, monkeypatch):
    orchestrator = _patch_pending(tmp_path, monkeypatch)

    with patch.object(orchestrator, "gather_candidates", return_value=[{"title": "x"}]), \
         patch.object(orchestrator, "score_topics", return_value=([], 0)), \
         patch.object(orchestrator, "draft_post") as mock_draft:
        summary = orchestrator.run()

    mock_draft.assert_not_called()
    assert summary["status"] == "scoring_failed"
    assert not (tmp_path / "pending").exists()


def test_run_draft_failure_handled_gracefully(tmp_path, monkeypatch):
    orchestrator = _patch_pending(tmp_path, monkeypatch)

    with patch.object(orchestrator, "gather_candidates", return_value=[{"title": "x"}]), \
         patch.object(orchestrator, "score_topics", return_value=(TOP_RANKED, 150)), \
         patch.object(orchestrator, "draft_post", return_value=(None, 70)) as mock_draft:
        summary = orchestrator.run()

    mock_draft.assert_called_once()
    assert summary["status"] == "draft_failed"
    assert summary["output_dir"] is None
    assert not (tmp_path / "pending").exists()
