"""
Phase 4 test suite — digest.py

Covers the six testing requirements from the spec:
1. No new transcripts → clean exit, no file written
2. New transcripts → correct digest file with proper format
3. Idempotency → running twice (--force) overwrites, not appends
4. --group filter → only specified group summarized
5. Scheduled mode → no terminal output, error goes to error_log.json
6. Stale index warning → warning printed but digest proceeds
"""
import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------

FAKE_SUMMARY_RESPONSE = (
    "Summary: AI is rapidly transforming IT career paths.\n"
    "Top questions: How do I start learning AI without a CS degree?"
)
FAKE_SYNTHESIS_RESPONSE = (
    "1. Create a guide on AI career transitions for IT professionals.\n"
    "2. Address the certification question directly — it comes up constantly."
)


def _write_index(stale=False):
    os.makedirs("knowledge_base", exist_ok=True)
    data = {
        "built_at": "2026-04-29 07:00:00",
        "total_transcripts": 0,
        "groups": {},
    }
    with open("knowledge_base/index.json", "w", encoding="utf-8") as fh:
        json.dump(data, fh)
    if stale:
        old_ts = (datetime.now(timezone.utc) - timedelta(hours=25)).timestamp()
        os.utime("knowledge_base/index.json", (old_ts, old_ts))


def _write_download_log(downloads):
    os.makedirs("logs", exist_ok=True)
    with open("logs/download_log.json", "w", encoding="utf-8") as fh:
        json.dump({"downloads": downloads, "last_updated": None}, fh)


def _write_digest_log(runs):
    os.makedirs("logs", exist_ok=True)
    with open("logs/digest_log.json", "w", encoding="utf-8") as fh:
        json.dump({"runs": runs}, fh)


def _make_transcript_file(folder, filename, title="Test Video", channel="Test Channel"):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(
            f"# {title}\n\n"
            f"**Channel:** {channel}\n"
            f"**Published:** 2026-04-29\n"
            f"**URL:** https://youtube.com/watch?v=abc123\n"
            f"**Downloaded:** 2026-04-29\n"
            f"**Word Count:** 500\n\n"
            f"---\n\nTranscript content about AI careers and tools.\n"
        )
    return path


def _fresh_download(file_path, title="Test Video", channel="Test Channel",
                    group="ai-and-claude-code"):
    return {
        "video_id": "abc123",
        "title": title,
        "channel": channel,
        "url": "https://youtube.com/watch?v=abc123",
        "final_category": group,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "file_path": file_path,
        "comments_file": None,
        "comments_status": "none",
    }


def _claude_mocks():
    """Return patch context managers for the two Claude helper functions."""
    return (
        patch(
            "src.knowledge_base.digest._summarize_transcript",
            return_value=(FAKE_SUMMARY_RESPONSE, 150),
        ),
        patch(
            "src.knowledge_base.digest._synthesize_action_items",
            return_value=(FAKE_SYNTHESIS_RESPONSE, 200),
        ),
    )


# ---------------------------------------------------------------------------
# Test 1 — No new transcripts → clean exit, no digest file written
# ---------------------------------------------------------------------------

def test_digest_no_new_transcripts_exits_cleanly():
    from src.knowledge_base.digest import run_digest

    with tempfile.TemporaryDirectory() as tmpdir:
        orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            _write_index()
            # Old download (before the last digest run)
            file_path = _make_transcript_file(
                "transcripts/ai-and-claude-code", "2026-04-01_old.md"
            )
            _write_download_log([{
                **_fresh_download(file_path),
                "timestamp": "2026-04-01T06:00:00+00:00",
            }])
            # Last digest ran AFTER the download — so nothing is "new"
            _write_digest_log([{
                "timestamp": "2026-04-28 07:00:00",
                "date_digested": "2026-04-28",
                "new_transcripts": 1,
                "groups_covered": ["ai-and-claude-code"],
                "output_file": "knowledge_base/digests/2026-04-28_digest.md",
                "tokens_consumed": 1000,
                "model": "claude-haiku-4-5-20251001",
            }])

            run_digest()

            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            assert not os.path.isfile(
                f"knowledge_base/digests/{today}_digest.md"
            ), "No digest file should be written when there is nothing new"

            # digest_log should record the empty run
            with open("logs/digest_log.json", encoding="utf-8") as fh:
                log = json.load(fh)
            assert len(log["runs"]) == 2
            assert log["runs"][-1]["new_transcripts"] == 0
            assert log["runs"][-1]["output_file"] is None
        finally:
            os.chdir(orig)


# ---------------------------------------------------------------------------
# Test 2 — New transcripts → correct digest file with proper format
# ---------------------------------------------------------------------------

def test_digest_new_transcripts_produces_correct_format():
    from src.knowledge_base.digest import run_digest

    with tempfile.TemporaryDirectory() as tmpdir:
        orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            _write_index()
            file_path = _make_transcript_file(
                "transcripts/ai-and-claude-code",
                "2026-04-29_ai-careers.md",
                title="AI Career Guide",
                channel="Tech Channel",
            )
            _write_download_log([_fresh_download(
                file_path, title="AI Career Guide", channel="Tech Channel"
            )])

            p_summarize, p_synthesize = _claude_mocks()
            with p_summarize, p_synthesize:
                run_digest()

            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            digest_path = f"knowledge_base/digests/{today}_digest.md"
            assert os.path.isfile(digest_path), "Digest file should be created"

            with open(digest_path, encoding="utf-8") as fh:
                content = fh.read()

            assert f"# Daily Digest — {today}" in content
            assert "## Summary" in content
            assert "## ai-and-claude-code" in content
            assert "### Tech Channel" in content
            assert "AI Career Guide" in content
            assert "## What to Act On" in content
            assert FAKE_SYNTHESIS_RESPONSE in content
        finally:
            os.chdir(orig)


# ---------------------------------------------------------------------------
# Test 3 — Idempotency: running twice (--force) overwrites, never appends
# ---------------------------------------------------------------------------

def test_digest_force_overwrites_not_appends():
    from src.knowledge_base.digest import run_digest

    with tempfile.TemporaryDirectory() as tmpdir:
        orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            _write_index()
            file_path = _make_transcript_file(
                "transcripts/ai-and-claude-code",
                "2026-04-29_video.md",
            )
            _write_download_log([_fresh_download(file_path)])

            p_summarize, p_synthesize = _claude_mocks()
            with p_summarize, p_synthesize:
                run_digest(force=True)
                run_digest(force=True)

            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            digest_path = f"knowledge_base/digests/{today}_digest.md"

            # Only one digest file for today
            assert os.path.isfile(digest_path)
            digest_files = [
                f for f in os.listdir("knowledge_base/digests")
                if f.endswith("_digest.md")
            ]
            assert len(digest_files) == 1, "Only one digest file should exist"

            # Two entries in digest_log (one per run)
            with open("logs/digest_log.json", encoding="utf-8") as fh:
                log = json.load(fh)
            assert len(log["runs"]) == 2

            # File content is not doubled
            with open(digest_path, encoding="utf-8") as fh:
                content = fh.read()
            assert content.count("# Daily Digest") == 1
        finally:
            os.chdir(orig)


# ---------------------------------------------------------------------------
# Test 4 — --group filter: only the specified group is summarized
# ---------------------------------------------------------------------------

def test_digest_group_filter_limits_summary():
    from src.knowledge_base.digest import run_digest

    with tempfile.TemporaryDirectory() as tmpdir:
        orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            _write_index()
            ai_file = _make_transcript_file(
                "transcripts/ai-and-claude-code",
                "2026-04-29_ai.md",
                title="AI Skills Video",
                channel="AI Channel",
            )
            btc_file = _make_transcript_file(
                "transcripts/bitcoin-and-economic-news",
                "2026-04-29_btc.md",
                title="Bitcoin Analysis",
                channel="BTC Channel",
            )
            _write_download_log([
                _fresh_download(ai_file, title="AI Skills Video",
                                channel="AI Channel", group="ai-and-claude-code"),
                _fresh_download(btc_file, title="Bitcoin Analysis",
                                channel="BTC Channel", group="bitcoin-and-economic-news"),
            ])

            p_summarize, p_synthesize = _claude_mocks()
            with p_summarize, p_synthesize:
                run_digest(group_filter="ai-and-claude-code")

            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            with open(f"knowledge_base/digests/{today}_digest.md", encoding="utf-8") as fh:
                content = fh.read()

            assert "## ai-and-claude-code" in content
            assert "AI Skills Video" in content
            assert "## bitcoin-and-economic-news" not in content
            assert "Bitcoin Analysis" not in content
        finally:
            os.chdir(orig)


# ---------------------------------------------------------------------------
# Test 5 — Scheduled mode: no terminal output, API error goes to error_log.json
# ---------------------------------------------------------------------------

def test_digest_scheduled_mode_silent_on_error(capsys):
    from src.knowledge_base.digest import run_digest

    with tempfile.TemporaryDirectory() as tmpdir:
        orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            _write_index()
            file_path = _make_transcript_file(
                "transcripts/ai-and-claude-code",
                "2026-04-29_video.md",
            )
            _write_download_log([_fresh_download(file_path)])

            # Summarize raises; synthesis succeeds — tests error logging
            with patch(
                "src.knowledge_base.digest._summarize_transcript",
                side_effect=Exception("API unavailable"),
            ), patch(
                "src.knowledge_base.digest._synthesize_action_items",
                return_value=(FAKE_SYNTHESIS_RESPONSE, 200),
            ):
                run_digest(scheduled=True)

            captured = capsys.readouterr()
            assert captured.out == "", "scheduled mode must produce no terminal output"

            assert os.path.isfile("logs/error_log.json")
            with open("logs/error_log.json", encoding="utf-8") as fh:
                log = json.load(fh)
            assert any("API unavailable" in e["error"] for e in log["errors"])
        finally:
            os.chdir(orig)


# ---------------------------------------------------------------------------
# Test 6 — Stale index warning: warning is printed but digest proceeds
# ---------------------------------------------------------------------------

def test_digest_stale_index_warns_but_proceeds(capsys):
    from src.knowledge_base.digest import run_digest

    with tempfile.TemporaryDirectory() as tmpdir:
        orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            _write_index(stale=True)
            file_path = _make_transcript_file(
                "transcripts/ai-and-claude-code",
                "2026-04-29_video.md",
            )
            _write_download_log([_fresh_download(file_path)])

            p_summarize, p_synthesize = _claude_mocks()
            with p_summarize, p_synthesize:
                run_digest()

            captured = capsys.readouterr()
            assert "WARNING" in captured.out, "Stale index warning should be printed"
            assert "hours old" in captured.out

            # Digest still proceeds despite stale index
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            assert os.path.isfile(f"knowledge_base/digests/{today}_digest.md"), \
                "Digest file should still be written despite stale index"
        finally:
            os.chdir(orig)
