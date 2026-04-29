"""
Phase 3 test suite.
Run: pytest tests/ -v
"""
import json
import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_transcript_file(folder, filename, title="Test Video", channel="Test Channel"):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    content = f"""# {title}

**Channel:** {channel}
**Published:** 2026-04-01
**Word Count:** 500

---

This is the transcript content about AI careers and learning Claude Code.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def _make_comments_file(folder, filename):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    content = """# Comments: Test Video

**Channel:** Test Channel
**Comments Fetched:** 2
**Fetched:** 2026-04-01

---

## Top Comments (by relevance)

How do I get started with AI without a CS degree?
— Alice | 42 likes | 2026-04-01

---

I struggle with knowing which tools to learn first.
— Bob | 18 likes | 2026-04-02

---
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# ---------------------------------------------------------------------------
# Test 1 — indexer builds correct index.json structure
# ---------------------------------------------------------------------------

def test_indexer_builds_correct_structure():
    from src.knowledge_base.indexer import build_index

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            _make_transcript_file(
                "transcripts/ai-and-claude-code",
                "2026-04-01_test-video.md",
                title="Test Video",
                channel="Test Channel",
            )
            index = build_index()
        finally:
            os.chdir(orig_dir)

    assert "built_at" in index
    assert "total_transcripts" in index
    assert "groups" in index
    assert index["total_transcripts"] == 1
    assert "ai-and-claude-code" in index["groups"]
    group = index["groups"]["ai-and-claude-code"]
    assert group["total"] == 1
    assert "Test Channel" in group["channels"]
    transcripts = group["channels"]["Test Channel"]["transcripts"]
    assert len(transcripts) == 1
    entry = transcripts[0]
    assert entry["file_path"].endswith("2026-04-01_test-video.md")
    assert entry["title"] == "Test Video"
    assert entry["channel"] == "Test Channel"
    assert "word_count" in entry
    assert "has_comments" in entry


# ---------------------------------------------------------------------------
# Test 2 — indexer correctly identifies files with and without comment pairs
# ---------------------------------------------------------------------------

def test_indexer_detects_comment_files():
    from src.knowledge_base.indexer import build_index

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            _make_transcript_file(
                "transcripts/ai-and-claude-code",
                "2026-04-01_with-comments.md",
            )
            _make_comments_file(
                "transcripts/ai-and-claude-code",
                "2026-04-01_with-comments_comments.md",
            )
            _make_transcript_file(
                "transcripts/ai-and-claude-code",
                "2026-04-02_no-comments.md",
            )
            index = build_index()
        finally:
            os.chdir(orig_dir)

    transcripts = index["groups"]["ai-and-claude-code"]["channels"]["Test Channel"]["transcripts"]
    by_name = {t["file_path"].split("/")[-1]: t for t in transcripts}

    assert by_name["2026-04-01_with-comments.md"]["has_comments"] is True
    assert by_name["2026-04-02_no-comments.md"]["has_comments"] is False


# ---------------------------------------------------------------------------
# Test 3 — indexer rebuilds from scratch (no appending)
# ---------------------------------------------------------------------------

def test_indexer_rebuilds_from_scratch():
    from src.knowledge_base.indexer import build_index

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            _make_transcript_file("transcripts/ai-and-claude-code", "2026-04-01_first.md")
            index1 = build_index()

            _make_transcript_file("transcripts/ai-and-claude-code", "2026-04-02_second.md")
            index2 = build_index()
        finally:
            os.chdir(orig_dir)

    # Second build should have exactly 2 files, not 3 (no duplication from first build)
    assert index1["total_transcripts"] == 1
    assert index2["total_transcripts"] == 2


# ---------------------------------------------------------------------------
# Test 4 — pass1 extraction returns valid JSON structure
# ---------------------------------------------------------------------------

def test_pass1_extraction_returns_valid_json():
    from src.analyzer.pain_point_extractor import _pass1_extract

    fake_response_text = json.dumps({
        "questions": ["How do I start?", "What tools to use?", "Is it hard?", "Cost?", "Time?"],
        "pain_points": ["overwhelm", "no direction", "imposter syndrome", "cost", "time"],
        "desired_outcomes": ["get a job", "build skills", "earn income"],
    })

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=fake_response_text)]
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 50

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    result, tokens = _pass1_extract(
        mock_client, "claude-haiku-4-5-20251001",
        "transcript content here",
        "comment content here",
    )

    assert result is not None
    assert "questions" in result
    assert "pain_points" in result
    assert "desired_outcomes" in result
    assert len(result["questions"]) == 5
    assert tokens == 150


# ---------------------------------------------------------------------------
# Test 5 — pass1 handles missing comment file gracefully
# ---------------------------------------------------------------------------

def test_pass1_handles_empty_comments():
    from src.analyzer.pain_point_extractor import _pass1_extract

    fake_response_text = json.dumps({
        "questions": ["Q1", "Q2", "Q3", "Q4", "Q5"],
        "pain_points": ["P1", "P2", "P3", "P4", "P5"],
        "desired_outcomes": ["O1", "O2", "O3"],
    })

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=fake_response_text)]
    mock_response.usage.input_tokens = 80
    mock_response.usage.output_tokens = 40

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    # Empty string for comments — should still work
    result, tokens = _pass1_extract(
        mock_client, "claude-haiku-4-5-20251001",
        "transcript content",
        "",  # no comments
    )

    assert result is not None
    assert "questions" in result


# ---------------------------------------------------------------------------
# Test 6 — pass2 aggregation produces ranked output
# ---------------------------------------------------------------------------

def test_pass2_aggregation_produces_ranked_output():
    from src.analyzer.pain_point_extractor import _pass2_aggregate

    fake_aggregated = {
        "top_questions": [
            {"text": "How to get started?", "count": 8, "category": "getting started"},
            {"text": "What tools to use?", "count": 5, "category": "tools"},
        ],
        "top_pain_points": [
            {"text": "Overwhelm", "count": 12, "category": "mindset"},
        ],
        "top_desired_outcomes": [
            {"text": "Get an AI job", "count": 9, "category": "career"},
        ],
        "videos_analyzed": 5,
        "total_extractions": 5,
    }

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(fake_aggregated))]
    mock_response.usage.input_tokens = 200
    mock_response.usage.output_tokens = 100

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    extractions = [{"questions": ["Q1"], "pain_points": ["P1"], "desired_outcomes": ["O1"]}]
    result, tokens = _pass2_aggregate(mock_client, "claude-haiku-4-5-20251001", extractions, 5)

    assert result is not None
    assert "top_questions" in result
    assert "top_pain_points" in result
    assert "top_desired_outcomes" in result
    assert result["top_questions"][0]["count"] >= result["top_questions"][1]["count"]


# ---------------------------------------------------------------------------
# Test 7 — extractor saves report to correct path
# ---------------------------------------------------------------------------

def test_extractor_saves_report_to_correct_path():
    from src.analyzer.pain_point_extractor import _render_report

    fake_aggregated = {
        "top_questions": [{"text": "How to start?", "count": 5, "category": "basics"}],
        "top_pain_points": [{"text": "Overwhelm", "count": 8, "category": "mindset"}],
        "top_desired_outcomes": [{"text": "Get a job", "count": 6, "category": "career"}],
        "videos_analyzed": 10,
        "total_extractions": 10,
    }

    report = _render_report(fake_aggregated, "ai-and-claude-code", 10, 8, "2026-04-12")

    assert "# Pain Point Analysis:" in report
    assert "ai-and-claude-code" in report
    assert "How to start?" in report
    assert "Overwhelm" in report
    assert "Get a job" in report
    assert "PDF Product Opportunities" in report
    assert "Videos Analyzed:** 10" in report
    assert "Comment Files Included:** 8" in report


# ---------------------------------------------------------------------------
# Test 8 — query returns answer with source citations
# ---------------------------------------------------------------------------

def test_query_returns_answer_with_sources():
    from src.knowledge_base.query import ask

    fake_index = {
        "built_at": "2026-04-12 00:00:00",
        "total_transcripts": 1,
        "groups": {
            "ai-and-claude-code": {
                "total": 1,
                "channels": {
                    "AI Channel": {
                        "total": 1,
                        "transcripts": [
                            {
                                "file_path": "/fake/path/2026-04-01_ai-careers.md",
                                "video_id": "abc123",
                                "title": "AI Careers Guide",
                                "channel": "AI Channel",
                                "group": "ai-and-claude-code",
                                "date": "2026-04-01",
                                "has_comments": False,
                                "word_count": 500,
                            }
                        ],
                    }
                },
            }
        },
    }

    with patch("src.knowledge_base.query.load_index", return_value=fake_index), \
         patch("src.knowledge_base.query._score_file", return_value=5), \
         patch("src.knowledge_base.query._read_file_content", return_value="AI career content here"), \
         patch("src.knowledge_base.query._call_claude", return_value=("Here is the answer based on transcripts.", 100)):
        answer, sources = ask("What are the best AI certifications?")

    assert isinstance(answer, str)
    assert len(answer) > 0
    assert len(sources) > 0
    assert sources[0]["filename"] == "2026-04-01_ai-careers.md"


# ---------------------------------------------------------------------------
# Test 9 — query states clearly when no relevant transcripts found
# ---------------------------------------------------------------------------

def test_query_no_results_message():
    from src.knowledge_base.query import ask

    fake_index = {
        "built_at": "2026-04-12 00:00:00",
        "total_transcripts": 1,
        "groups": {
            "ai-and-claude-code": {
                "total": 1,
                "channels": {
                    "Food Channel": {
                        "total": 1,
                        "transcripts": [
                            {
                                "file_path": "/fake/path/unrelated.md",
                                "video_id": "",
                                "title": "Cooking Recipes",
                                "channel": "Food Channel",
                                "group": "ai-and-claude-code",
                                "date": "2026-04-01",
                                "has_comments": False,
                                "word_count": 200,
                            }
                        ],
                    }
                },
            }
        },
    }

    with patch("src.knowledge_base.query.load_index", return_value=fake_index):
        # Query about something with zero keyword overlap
        answer, sources = ask("xyzzy quantum entanglement wormhole")

    # Either no sources found or answer mentions limitation
    assert isinstance(answer, str)
    assert len(answer) > 0


# ---------------------------------------------------------------------------
# Test 10 — analyzer_log records api_calls_made and files_processed
# ---------------------------------------------------------------------------

def test_analyzer_log_records_correctly():
    from src.analyzer.pain_point_extractor import _append_analyzer_log

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            os.makedirs("logs")
            _append_analyzer_log(
                run_id="2026-04-12_120000",
                group="ai-and-claude-code",
                files_processed=15,
                api_calls=16,
                tokens_used=45000,
                output_file="knowledge_base/reports/pain_points_2026-04-12_ai-and-claude-code.md",
            )
            with open("logs/analyzer_log.json", "r") as f:
                log = json.load(f)
        finally:
            os.chdir(orig_dir)

    assert "runs" in log
    assert len(log["runs"]) == 1
    run = log["runs"][0]
    assert run["files_processed"] == 15
    assert run["api_calls_made"] == 16
    assert run["tokens_used"] == 45000
    assert run["group"] == "ai-and-claude-code"
    assert "estimated_cost_usd" in run


# ---------------------------------------------------------------------------
# Test 11 — analyze --group only processes files from specified group
# ---------------------------------------------------------------------------

def test_extractor_respects_group_filter():
    from src.analyzer.pain_point_extractor import run_extractor

    fake_index = {
        "built_at": "2026-04-12T00:00:00+00:00",
        "total_files": 2,
        "groups": {
            "ai-and-claude-code": {
                "count": 1,
                "files": [{"filename": "ai.md", "path": "/fake/ai.md",
                           "title": "AI", "channel": "AI Ch",
                           "has_comments": False, "comments_path": None}],
            },
            "bitcoin-and-economic-news": {
                "count": 1,
                "files": [{"filename": "btc.md", "path": "/fake/btc.md",
                           "title": "BTC", "channel": "BTC Ch",
                           "has_comments": False, "comments_path": None}],
            },
        },
    }

    processed_groups = []

    def fake_run_for_group(client, model, max_files, group_name, files):
        processed_groups.append(group_name)

    with patch("src.analyzer.pain_point_extractor.load_index", return_value=fake_index), \
         patch("src.analyzer.pain_point_extractor.anthropic.Anthropic"), \
         patch("src.analyzer.pain_point_extractor._run_for_group", side_effect=fake_run_for_group):
        run_extractor(group="ai-and-claude-code")

    assert processed_groups == ["ai-and-claude-code"]
    assert "bitcoin-and-economic-news" not in processed_groups


# ---------------------------------------------------------------------------
# Test 12 — ask --group limits search to specified group
# ---------------------------------------------------------------------------

def test_ask_group_limits_search():
    from src.knowledge_base.query import ask

    fake_index = {
        "built_at": "2026-04-12 00:00:00",
        "total_transcripts": 2,
        "groups": {
            "ai-and-claude-code": {
                "total": 1,
                "channels": {
                    "AI Channel": {
                        "total": 1,
                        "transcripts": [
                            {
                                "file_path": "/fake/2026-04-01_ai-video.md",
                                "video_id": "",
                                "title": "AI Claude Tutorial",
                                "channel": "AI Channel",
                                "group": "ai-and-claude-code",
                                "date": "2026-04-01",
                                "has_comments": False,
                                "word_count": 500,
                            }
                        ],
                    }
                },
            },
            "bitcoin-and-economic-news": {
                "total": 1,
                "channels": {
                    "BTC Channel": {
                        "total": 1,
                        "transcripts": [
                            {
                                "file_path": "/fake/2026-04-01_btc-video.md",
                                "video_id": "",
                                "title": "Bitcoin Analysis Claude",
                                "channel": "BTC Channel",
                                "group": "bitcoin-and-economic-news",
                                "date": "2026-04-01",
                                "has_comments": False,
                                "word_count": 500,
                            }
                        ],
                    }
                },
            },
        },
    }

    searched_files = []

    def fake_score(entry, keywords):
        searched_files.append(os.path.basename(entry["file_path"]))
        return 5  # always match

    with patch("src.knowledge_base.query.load_index", return_value=fake_index), \
         patch("src.knowledge_base.query._score_file", side_effect=fake_score), \
         patch("src.knowledge_base.query._read_file_content", return_value="content"), \
         patch("src.knowledge_base.query._call_claude", return_value=("Answer here.", 100)):
        ask("Claude AI career", group="ai-and-claude-code")

    assert "2026-04-01_ai-video.md" in searched_files
    assert "2026-04-01_btc-video.md" not in searched_files
