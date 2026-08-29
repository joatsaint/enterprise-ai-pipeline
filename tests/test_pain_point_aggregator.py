"""
Pain Point Cross-Run Aggregator (Pass 3) test suite.
Run: pytest tests/test_pain_point_aggregator.py -v
"""
import json
import os
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest


SAMPLE_REPORT = """# Pain Point Analysis: Ai And Claude Code
**Generated:** 2026-04-12 07:00
**Videos Analyzed:** 10
**Comment Files Included:** 8
**Group:** ai-and-claude-code

---

## Top Questions (Most Asked)

1. How do I get started with Claude Code? — mentioned in 8 video(s)
2. What's the difference between Sonnet and Opus? — mentioned in 3 video(s)

## Top Pain Points (Most Expressed)

1. AI is going to replace my job — mentioned in 12 video(s)
2. Too many tools, no clear starting point — mentioned in 5 video(s)

## Top Desired Outcomes (What They Want)

1. Land an AI-adjacent job within a year — mentioned in 6 video(s)

---

## PDF Product Opportunities

Based on the above, the highest-priority PDF topics are:

1. **How do I get started with Claude Code?**
   Estimated demand: HIGH
"""


def _write_report(folder, filename, content=SAMPLE_REPORT):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# ---------------------------------------------------------------------------
# Test 1 — parse_report extracts all three sections correctly
# ---------------------------------------------------------------------------

def test_parse_report_extracts_sections():
    from src.analyzer.pain_point_aggregator import parse_report

    with tempfile.TemporaryDirectory() as tmpdir:
        path = _write_report(tmpdir, "pain_points_2026-04-12_ai-and-claude-code.md")
        parsed = parse_report(path)

    assert parsed["date"] == "2026-04-12"
    assert parsed["group"] == "ai-and-claude-code"

    questions = [i for i in parsed["items"] if i["type"] == "question"]
    pain_points = [i for i in parsed["items"] if i["type"] == "pain_point"]
    outcomes = [i for i in parsed["items"] if i["type"] == "desired_outcome"]

    assert len(questions) == 2
    assert len(pain_points) == 2
    assert len(outcomes) == 1
    assert pain_points[0]["text"] == "AI is going to replace my job"
    assert pain_points[0]["count"] == 12


# ---------------------------------------------------------------------------
# Test 2 — list_report_files excludes AGGREGATE output files
# ---------------------------------------------------------------------------

def test_list_report_files_excludes_aggregate():
    from src.analyzer.pain_point_aggregator import list_report_files

    with tempfile.TemporaryDirectory() as tmpdir:
        _write_report(tmpdir, "pain_points_2026-04-12_ai-and-claude-code.md")
        _write_report(tmpdir, "pain_points_AGGREGATE_2026-07-24.md", content="# Aggregate\n")
        files = list_report_files(tmpdir)

    assert len(files) == 1
    assert "AGGREGATE" not in files[0]


# ---------------------------------------------------------------------------
# Test 3 — decay_score: recent last_seen outranks older last_seen despite
# a lower raw mention count (this is the whole point of the feature)
# ---------------------------------------------------------------------------

def test_decay_score_recent_beats_stale():
    from src.analyzer.pain_point_aggregator import decay_score

    as_of = "2026-07-24"
    recent_score = decay_score(total_mentions=8, last_seen="2026-07-20", as_of=as_of)
    stale_score = decay_score(total_mentions=20, last_seen="2026-05-01", as_of=as_of)

    assert recent_score > stale_score


def test_decay_score_zero_days_no_decay():
    from src.analyzer.pain_point_aggregator import decay_score

    score = decay_score(total_mentions=10, last_seen="2026-07-24", as_of="2026-07-24")
    assert score == pytest.approx(10.0)


def test_decay_score_one_half_life_halves_score():
    from src.analyzer.pain_point_aggregator import decay_score, DECAY_HALF_LIFE_DAYS
    from datetime import timedelta

    last_seen = datetime(2026, 7, 1)
    as_of = last_seen + timedelta(days=DECAY_HALF_LIFE_DAYS)
    score = decay_score(
        total_mentions=10,
        last_seen=last_seen.strftime("%Y-%m-%d"),
        as_of=as_of.strftime("%Y-%m-%d"),
    )
    assert score == pytest.approx(5.0, abs=0.01)


# ---------------------------------------------------------------------------
# Test 4 — clustering merges a reworded item into an existing theme
# ---------------------------------------------------------------------------

def test_cluster_batch_merges_into_existing_theme():
    from src.analyzer.pain_point_aggregator import _cluster_batch

    history = {
        "themes": [{
            "theme_id": "pp_0001",
            "type": "pain_point",
            "canonical_text": "AI will replace my job",
            "category": "career",
            "first_seen": "2026-04-01",
            "last_seen": "2026-04-01",
            "total_mentions": 10,
        }],
        "processed_files": [],
    }

    new_items = [{"type": "pain_point", "text": "Worried AI takes my career", "count": 5,
                  "date": "2026-07-20", "group": "ai-and-claude-code"}]

    fake_response = [[0, "pp_0001", None, None]]
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(fake_response))]
    mock_response.usage.input_tokens = 50
    mock_response.usage.output_tokens = 20
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            _cluster_batch(mock_client, "claude-haiku-4-5-20251001", history, new_items)
        finally:
            os.chdir(orig_dir)

    assert len(history["themes"]) == 1  # merged, not duplicated
    theme = history["themes"][0]
    assert theme["total_mentions"] == 15
    assert theme["last_seen"] == "2026-07-20"


# ---------------------------------------------------------------------------
# Test 5 — clustering creates a new theme when nothing matches
# ---------------------------------------------------------------------------

def test_cluster_batch_creates_new_theme():
    from src.analyzer.pain_point_aggregator import _cluster_batch

    history = {"themes": [], "processed_files": []}
    new_items = [{"type": "question", "text": "How do I use Claude Code?", "count": 4,
                  "date": "2026-07-20", "group": "ai-and-claude-code"}]

    fake_response = [[0, None, "Getting started with Claude Code", "tools"]]
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(fake_response))]
    mock_response.usage.input_tokens = 30
    mock_response.usage.output_tokens = 15
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            _cluster_batch(mock_client, "claude-haiku-4-5-20251001", history, new_items)
        finally:
            os.chdir(orig_dir)

    assert len(history["themes"]) == 1
    assert history["themes"][0]["canonical_text"] == "Getting started with Claude Code"
    assert history["themes"][0]["total_mentions"] == 4


# ---------------------------------------------------------------------------
# Test 6 — pruning only deletes files already folded into history, and
# only once they're older than the retention window
# ---------------------------------------------------------------------------

def test_prune_only_deletes_old_processed_files():
    from src.analyzer.pain_point_aggregator import _prune_old_reports

    with tempfile.TemporaryDirectory() as tmpdir:
        old_processed = _write_report(tmpdir, "pain_points_2026-01-01_ai-and-claude-code.md")
        old_unprocessed = _write_report(tmpdir, "pain_points_2026-01-02_ai-and-claude-code.md")
        recent_processed = _write_report(tmpdir, "pain_points_2026-07-20_ai-and-claude-code.md")

        history = {
            "themes": [],
            "processed_files": [
                "pain_points_2026-01-01_ai-and-claude-code.md",
                "pain_points_2026-07-20_ai-and-claude-code.md",
            ],
        }

        deleted = _prune_old_reports(history, as_of="2026-07-24", reports_dir=tmpdir)

        assert deleted == ["pain_points_2026-01-01_ai-and-claude-code.md"]
        assert not os.path.exists(old_processed)
        assert os.path.exists(old_unprocessed)      # never processed -> never deleted
        assert os.path.exists(recent_processed)      # processed but within retention -> kept


# ---------------------------------------------------------------------------
# Test 7 — dry-run writes nothing to disk
# ---------------------------------------------------------------------------

def test_run_aggregator_dry_run_writes_nothing():
    from src.analyzer.pain_point_aggregator import run_aggregator

    fake_response = [
        [0, None, "Getting started", "tools"],
        [1, None, "Model choice confusion", "tools"],
        [2, None, "Job replacement fear", "career"],
        [3, None, "Tool overload", "tools"],
        [4, None, "Land an AI job", "career"],
    ]
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(fake_response))]
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 50
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            reports_dir = os.path.join(tmpdir, "knowledge_base", "reports")
            _write_report(reports_dir, "pain_points_2026-04-12_ai-and-claude-code.md")

            with patch("src.analyzer.pain_point_aggregator.anthropic.Anthropic", return_value=mock_client):
                run_aggregator(
                    dry_run=True,
                    reports_dir=reports_dir,
                    history_path=os.path.join(tmpdir, "knowledge_base", "pain_point_history.json"),
                )

            assert not os.path.exists(os.path.join(tmpdir, "knowledge_base", "pain_point_history.json"))
            assert not any("AGGREGATE" in f for f in os.listdir(reports_dir))
        finally:
            os.chdir(orig_dir)


# ---------------------------------------------------------------------------
# Test 8 — a real run writes history, an aggregate report, and skips
# already-processed files on a second run (idempotent)
# ---------------------------------------------------------------------------

def test_run_aggregator_writes_history_and_report_once():
    from src.analyzer.pain_point_aggregator import run_aggregator

    fake_response = [
        [0, None, "Getting started", "tools"],
        [1, None, "Model choice confusion", "tools"],
        [2, None, "Job replacement fear", "career"],
        [3, None, "Tool overload", "tools"],
        [4, None, "Land an AI job", "career"],
    ]
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(fake_response))]
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 50
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            reports_dir = os.path.join(tmpdir, "knowledge_base", "reports")
            history_path = os.path.join(tmpdir, "knowledge_base", "pain_point_history.json")
            _write_report(reports_dir, "pain_points_2026-04-12_ai-and-claude-code.md")

            with patch("src.analyzer.pain_point_aggregator.anthropic.Anthropic", return_value=mock_client):
                run_aggregator(reports_dir=reports_dir, history_path=history_path)

            assert os.path.exists(history_path)
            with open(history_path) as f:
                history = json.load(f)
            assert len(history["themes"]) == 5
            assert "pain_points_2026-04-12_ai-and-claude-code.md" in history["processed_files"]

            aggregate_files = [f for f in os.listdir(reports_dir) if "AGGREGATE" in f]
            assert len(aggregate_files) == 1

            calls_before_second_run = mock_client.messages.create.call_count
            with patch("src.analyzer.pain_point_aggregator.anthropic.Anthropic", return_value=mock_client):
                run_aggregator(reports_dir=reports_dir, history_path=history_path)
            # No new reports -> no new clustering call
            assert mock_client.messages.create.call_count == calls_before_second_run
        finally:
            os.chdir(orig_dir)
