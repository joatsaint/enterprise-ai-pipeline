"""
Phase 2 test suite.
Run: pytest tests/ -v
"""
import io
import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock, call

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class FakeSnippet:
    def __init__(self, text):
        self.text = text


class FakeHttpError(Exception):
    """Stands in for googleapiclient.errors.HttpError in tests."""
    def __init__(self, status, content=""):
        self.resp = type("R", (), {"status": status})()
        self.content = content.encode() if isinstance(content, str) else content
        super().__init__(f"HttpError {status}: {content}")


# ---------------------------------------------------------------------------
# Test 1 — comment_fetcher returns empty list when comments are disabled
# ---------------------------------------------------------------------------

def test_comment_fetcher_comments_disabled():
    from src.downloader import comment_fetcher
    comment_fetcher.reset_quota_flag()

    disabled_body = json.dumps({
        "error": {"code": 400, "errors": [{"reason": "commentsDisabled"}]}
    })

    with patch(
        "src.downloader.comment_fetcher._make_api_request",
        side_effect=FakeHttpError(400, disabled_body),
    ), patch("src.downloader.comment_fetcher._load_api_key", return_value="fake_key"):
        comments, status = comment_fetcher.fetch_comments("test1234567")

    assert comments == []
    assert status == "comments_disabled"


# ---------------------------------------------------------------------------
# Test 2 — comment_fetcher sets session quota flag on 403 quotaExceeded
# ---------------------------------------------------------------------------

def test_comment_fetcher_quota_flag_set_on_403():
    from src.downloader import comment_fetcher
    comment_fetcher.reset_quota_flag()

    quota_body = json.dumps({
        "error": {"code": 403, "errors": [{"reason": "quotaExceeded"}]}
    })

    with patch(
        "src.downloader.comment_fetcher._make_api_request",
        side_effect=FakeHttpError(403, quota_body),
    ), patch("src.downloader.comment_fetcher._load_api_key", return_value="fake_key"):
        comments, status = comment_fetcher.fetch_comments("test1234567")

    assert comments == []
    assert status == "quota_exhausted"
    assert comment_fetcher._quota_exhausted is True

    # Subsequent call must short-circuit without hitting API
    with patch(
        "src.downloader.comment_fetcher._make_api_request"
    ) as mock_api:
        comment_fetcher.fetch_comments("another_vid1")
        mock_api.assert_not_called()

    # Clean up for other tests
    comment_fetcher.reset_quota_flag()


# ---------------------------------------------------------------------------
# Test 3 — comment_fetcher output file has all required header fields
# ---------------------------------------------------------------------------

def test_comment_file_has_all_headers():
    from src.downloader.comment_fetcher import save_comments_markdown

    comments = [
        {"author": "Alice", "text": "Great video!", "like_count": 42, "published_at": "2024-01-01"},
        {"author": "Bob", "text": "Very helpful.", "like_count": 10, "published_at": "2024-01-02"},
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            path = save_comments_markdown(
                "dQw4w9WgXcQ",
                "Test Video Title",
                "Test Channel",
                comments,
                "bitcoin-and-economic-news",
                "2024-04-12",
            )
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        finally:
            os.chdir(orig_dir)

    assert "# Comments: Test Video Title" in content
    assert "**Channel:** Test Channel" in content
    assert "**Video URL:** https://www.youtube.com/watch?v=dQw4w9WgXcQ" in content
    assert "**Comments Fetched:** 2" in content
    assert "**Fetched:** 2024-04-12" in content
    assert "## Top Comments (by relevance)" in content
    assert "Great video!" in content
    assert "— Alice | 42 likes | 2024-01-01" in content


# ---------------------------------------------------------------------------
# Test 4 — channel.py skips videos already in download_log.json (incremental)
# ---------------------------------------------------------------------------

def test_channel_skips_already_downloaded():
    from src.downloader import channel as channel_mod

    existing_id = "existing11a"
    new_id = "newvideo11b"
    # Entries need duration >= MIN_VIDEO_DURATION_SECONDS (300) to survive filter
    fake_entries = [
        {"id": existing_id, "duration": 600},
        {"id": new_id, "duration": 600},
    ]

    fake_log = {
        "downloads": [{"video_id": existing_id}],
        "last_updated": None,
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            os.makedirs("logs")
            log_path = os.path.join("logs", "download_log.json")
            with open(log_path, "w") as f:
                json.dump(fake_log, f)

            with (
                patch(
                    "src.downloader.channel.get_video_entries_from_channel",
                    return_value=fake_entries,
                ),
                patch("src.orchestrator.run") as mock_run,
                patch("src.channels.registry.find_channel", return_value=None),
            ):
                channel_mod.run_channel(
                    "https://www.youtube.com/@testchannel",
                    force_full=False,
                )

            called_urls = [c.args[0] for c in mock_run.call_args_list]
        finally:
            os.chdir(orig_dir)

    assert len(called_urls) == 1
    assert new_id in called_urls[0]
    assert existing_id not in called_urls[0]


# ---------------------------------------------------------------------------
# Test 5 — channel.py downloads ALL videos with --force-full
# ---------------------------------------------------------------------------

def test_channel_force_full_downloads_all():
    from src.downloader import channel as channel_mod

    existing_id = "existing11a"
    new_id = "newvideo11b"
    fake_entries = [
        {"id": existing_id, "duration": 600},
        {"id": new_id, "duration": 600},
    ]

    fake_log = {
        "downloads": [{"video_id": existing_id}],
        "last_updated": None,
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            os.makedirs("logs")
            log_path = os.path.join("logs", "download_log.json")
            with open(log_path, "w") as f:
                json.dump(fake_log, f)

            with (
                patch(
                    "src.downloader.channel.get_video_entries_from_channel",
                    return_value=fake_entries,
                ),
                patch("src.orchestrator.run") as mock_run,
                patch("src.channels.registry.find_channel", return_value=None),
                patch("src.downloader.channel.time.sleep"),
                patch("src.downloader.channel.random.uniform", return_value=0.0),
            ):
                channel_mod.run_channel(
                    "https://www.youtube.com/@testchannel",
                    force_full=True,
                )

            call_count = mock_run.call_count
        finally:
            os.chdir(orig_dir)

    assert call_count == 2


# ---------------------------------------------------------------------------
# Test 6 — channel.py uses randomized (not fixed) pause between requests
# ---------------------------------------------------------------------------

def test_channel_uses_randomized_pause():
    from src.downloader import channel as channel_mod

    fake_entries = [
        {"id": "video1111a1", "duration": 600},
        {"id": "video2222b2", "duration": 600},
    ]
    captured_uniform_args = []

    def fake_uniform(lo, hi):
        captured_uniform_args.append((lo, hi))
        return 0.001  # near-zero so test is fast

    fake_log = {"downloads": [], "last_updated": None}

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            os.makedirs("logs")
            with open("logs/download_log.json", "w") as f:
                json.dump(fake_log, f)

            with (
                patch(
                    "src.downloader.channel.get_video_entries_from_channel",
                    return_value=fake_entries,
                ),
                patch("src.orchestrator.run"),
                patch("src.channels.registry.find_channel", return_value=None),
                patch("src.downloader.channel.random.uniform", side_effect=fake_uniform),
                patch("src.downloader.channel.time.sleep"),
            ):
                channel_mod.run_channel(
                    "https://www.youtube.com/@testchannel",
                    force_full=False,
                )
        finally:
            os.chdir(orig_dir)

    # Exactly one pause between two videos
    assert len(captured_uniform_args) == 1
    lo, hi = captured_uniform_args[0]
    # Incremental mode → (2, 5)
    assert lo == 2
    assert hi == 5


# ---------------------------------------------------------------------------
# Test 7 — orchestrator state includes comments_fetched and comments_status
# ---------------------------------------------------------------------------

def test_orchestrator_state_has_comment_fields():
    from src.orchestrator import run

    fake_snippets = [FakeSnippet("Bitcoin and crypto markets analysis.")]

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            with (
                patch("src.orchestrator.fetch_transcript", return_value=fake_snippets),
                patch("src.orchestrator.get_video_metadata", return_value={
                    "title": "Bitcoin Test",
                    "channel": "Test Channel",
                    "published": "2024-01-01",
                }),
                patch("src.orchestrator.fetch_comments", return_value=([], "no_api_key")),
                patch("src.classifier.category._timed_input", return_value=None),
            ):
                state = run("https://youtu.be/dQw4w9WgXcQ")
        finally:
            os.chdir(orig_dir)

    assert "comments_fetched" in state
    assert "comments_status" in state
    assert isinstance(state["comments_fetched"], int)
    assert isinstance(state["comments_status"], str)


# ---------------------------------------------------------------------------
# Test 8 — run summary includes comments line in output
# ---------------------------------------------------------------------------

def test_run_summary_includes_comments_line():
    from src.orchestrator import run

    fake_snippets = [FakeSnippet("AI and Claude Code tutorial content.")]
    output_lines = []

    original_print = print

    def capturing_print(*args, **kwargs):
        text = " ".join(str(a) for a in args)
        output_lines.append(text)
        original_print(*args, **kwargs)

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            with (
                patch("src.orchestrator.fetch_transcript", return_value=fake_snippets),
                patch("src.orchestrator.get_video_metadata", return_value={
                    "title": "Claude Code Tutorial",
                    "channel": "AI Channel",
                    "published": "2024-01-01",
                }),
                patch("src.orchestrator.fetch_comments", return_value=([], "no_api_key")),
                patch("src.classifier.category._timed_input", return_value=None),
                patch("builtins.print", side_effect=capturing_print),
            ):
                run("https://youtu.be/dQw4w9WgXcQ")
        finally:
            os.chdir(orig_dir)

    all_output = "\n".join(output_lines)
    assert "[COMMENTS]" in all_output


# ---------------------------------------------------------------------------
# Test 9 — add-channel writes correct entry to channels.json
# ---------------------------------------------------------------------------

def test_add_channel_writes_to_registry():
    from src.channels.registry import add_channel, load_channels

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            # Pre-create a minimal channels.json
            initial = {
                "channels": [],
                "groups": ["ai-and-claude-code", "bitcoin-and-economic-news"],
                "display_names": {},
                "notes": "",
            }
            with open("channels.json", "w") as f:
                json.dump(initial, f)

            inputs = iter([
                "My Test Channel",              # name
                "https://www.youtube.com/@test",  # url
                "1",                            # group → ai-and-claude-code
                "y",                            # active
                "",                             # max_videos → blank = use default
            ])
            with patch("builtins.input", side_effect=lambda _: next(inputs)):
                add_channel()

            data = load_channels()
        finally:
            os.chdir(orig_dir)

    assert len(data["channels"]) == 1
    ch = data["channels"][0]
    assert ch["name"] == "My Test Channel"
    assert ch["url"] == "https://www.youtube.com/@test"
    assert ch["group"] == "ai-and-claude-code"
    assert ch["active"] is True


# ---------------------------------------------------------------------------
# Test 10 — list-channels outputs registered channels
# ---------------------------------------------------------------------------

def test_list_channels_shows_registered_channels():
    from src.channels.registry import list_channels

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            data = {
                "channels": [
                    {
                        "name": "Bitcoin Macro Channel",
                        "url": "https://www.youtube.com/@btcmacro",
                        "group": "bitcoin-and-economic-news",
                        "active": True,
                        "notes": "",
                    }
                ],
                "groups": ["bitcoin-and-economic-news"],
                "display_names": {},
                "notes": "",
            }
            with open("channels.json", "w") as f:
                json.dump(data, f)

            captured = []
            original_print = print

            def capture(*args, **kwargs):
                captured.append(" ".join(str(a) for a in args))
                original_print(*args, **kwargs)

            with patch("builtins.print", side_effect=capture):
                list_channels()
        finally:
            os.chdir(orig_dir)

    output = "\n".join(captured)
    assert "Bitcoin Macro Channel" in output
