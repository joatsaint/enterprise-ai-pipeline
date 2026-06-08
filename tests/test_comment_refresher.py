"""
Comment Refresher test suite (src/downloader/comment_refresher.py)

Covers:
1. find_stale_comment_videos selects only entries older than the cutoff
   that already have an existing _comments.md file
2. refresh_old_comments overwrites the existing comments file in place
   (same filename) with a fresh "Fetched" date
3. refresh_old_comments stops early and reports when the API quota is exhausted
4. refresh_old_comments respects the --limit cap
5. refresh_old_comments skips entries with no existing comments file and
   logs failures to error_log.json without crashing the run

All YouTube API calls are mocked — zero live spend, matches the project's
existing mocked-test convention (see test_phase2.py).
"""
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest


def _iso(days_ago):
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


def _make_entry(video_id, days_ago, transcript_path, title="Sample Video", channel="sample-channel"):
    return {
        "video_id": video_id,
        "title": title,
        "channel": channel,
        "final_category": "ai-and-claude-code",
        "suggested_category": "ai-and-claude-code",
        "timestamp": _iso(days_ago),
        "file_path": transcript_path,
    }


def _setup(tmp_path, monkeypatch, entries):
    from src.downloader import comment_refresher

    download_log = tmp_path / "logs" / "download_log.json"
    error_log = tmp_path / "logs" / "error_log.json"
    download_log.parent.mkdir(parents=True, exist_ok=True)
    download_log.write_text(json.dumps({"downloads": entries}), encoding="utf-8")

    monkeypatch.setattr(comment_refresher, "DOWNLOAD_LOG", str(download_log))
    monkeypatch.setattr(comment_refresher, "ERROR_LOG", str(error_log))
    return comment_refresher, download_log, error_log


# ---------------------------------------------------------------------------
# find_stale_comment_videos
# ---------------------------------------------------------------------------

def test_find_stale_videos_filters_by_age_and_existing_comments_file(tmp_path, monkeypatch):
    transcript_old = tmp_path / "transcripts" / "old_video.md"
    transcript_old.parent.mkdir(parents=True, exist_ok=True)
    transcript_old.write_text("# old", encoding="utf-8")
    (tmp_path / "transcripts" / "old_video_comments.md").write_text("# comments", encoding="utf-8")

    transcript_recent = tmp_path / "transcripts" / "recent_video.md"
    transcript_recent.write_text("# recent", encoding="utf-8")
    (tmp_path / "transcripts" / "recent_video_comments.md").write_text("# comments", encoding="utf-8")

    transcript_no_comments = tmp_path / "transcripts" / "no_comments_video.md"
    transcript_no_comments.write_text("# no comments file", encoding="utf-8")

    entries = [
        _make_entry("old1234567a", 10, str(transcript_old)),
        _make_entry("rec1234567a", 1, str(transcript_recent)),
        _make_entry("noc1234567a", 30, str(transcript_no_comments)),
    ]

    refresher, _, _ = _setup(tmp_path, monkeypatch, entries)

    candidates = refresher.find_stale_comment_videos(days=7)

    ids = [c["video_id"] for c in candidates]
    assert ids == ["old1234567a"]


def test_find_stale_videos_skips_recently_refreshed_and_advances_backlog(tmp_path, monkeypatch):
    """
    Two old-by-download-date videos: one whose comments were refreshed
    yesterday (within the cooldown window) and one whose comments were last
    fetched long ago. Repeat runs should skip the recently-refreshed one and
    surface the truly-overdue one — otherwise --limit batches loop forever
    on the same group instead of advancing through the backlog.
    """
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat()
    long_ago = (datetime.now(timezone.utc) - timedelta(days=60)).date().isoformat()

    transcript_fresh = tmp_path / "transcripts" / "fresh_video.md"
    transcript_fresh.parent.mkdir(parents=True, exist_ok=True)
    transcript_fresh.write_text("# fresh", encoding="utf-8")
    (tmp_path / "transcripts" / "fresh_video_comments.md").write_text(
        f"# Comments: Fresh\n\n**Fetched:** {yesterday}\n\ncontent", encoding="utf-8"
    )

    transcript_overdue = tmp_path / "transcripts" / "overdue_video.md"
    transcript_overdue.write_text("# overdue", encoding="utf-8")
    (tmp_path / "transcripts" / "overdue_video_comments.md").write_text(
        f"# Comments: Overdue\n\n**Fetched:** {long_ago}\n\ncontent", encoding="utf-8"
    )

    entries = [
        _make_entry("fresh1234567", 10, str(transcript_fresh)),
        _make_entry("over1234567a", 10, str(transcript_overdue)),
    ]

    refresher, _, _ = _setup(tmp_path, monkeypatch, entries)

    candidates = refresher.find_stale_comment_videos(days=7)

    ids = [c["video_id"] for c in candidates]
    assert ids == ["over1234567a"]


# ---------------------------------------------------------------------------
# refresh_old_comments
# ---------------------------------------------------------------------------

FRESH_COMMENTS = [
    {"author": "Alice", "text": "This is the new top comment.", "like_count": 99, "published_at": "2026-06-01"},
    {"author": "Bob", "text": "Totally agree, AI changed my workflow.", "like_count": 50, "published_at": "2026-06-02"},
]


def test_refresh_overwrites_existing_file_in_place_with_fresh_fetched_date(tmp_path, monkeypatch):
    transcript = tmp_path / "transcripts" / "ai-and-claude-code" / "2026-05-01_my-video.md"
    transcript.parent.mkdir(parents=True, exist_ok=True)
    transcript.write_text("# transcript", encoding="utf-8")
    comments_path = tmp_path / "transcripts" / "ai-and-claude-code" / "2026-05-01_my-video_comments.md"
    comments_path.write_text("# Comments: Old\n\n**Fetched:** 2026-05-01\n\nstale content", encoding="utf-8")

    entries = [_make_entry("vid1234567a", 10, str(transcript), title="My Video")]
    refresher, _, _ = _setup(tmp_path, monkeypatch, entries)

    with patch("src.downloader.comment_refresher.fetch_comments", return_value=(FRESH_COMMENTS, "ok")) as mock_fetch:
        summary = refresher.refresh_old_comments(days=7)

    mock_fetch.assert_called_once_with("vid1234567a")
    assert summary == {"checked": 1, "refreshed": 1, "skipped": 0, "failed": 0, "quota_stopped": False}

    # Same filename — overwritten in place, no duplicate created
    siblings = list(comments_path.parent.glob("*_comments.md"))
    assert siblings == [comments_path]

    content = comments_path.read_text(encoding="utf-8")
    assert "This is the new top comment." in content
    assert "stale content" not in content
    assert "**Comments Fetched:** 2" in content
    today_iso = datetime.now(timezone.utc).date().isoformat()
    assert f"**Fetched:** {today_iso}" in content


def test_refresh_stops_early_on_quota_exhausted(tmp_path, monkeypatch):
    transcripts = []
    entries = []
    for i in range(3):
        t = tmp_path / "transcripts" / f"video{i}.md"
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text("# t", encoding="utf-8")
        (tmp_path / "transcripts" / f"video{i}_comments.md").write_text("# c", encoding="utf-8")
        transcripts.append(t)
        entries.append(_make_entry(f"vid{i}1234567", 10 + i, str(t)))

    refresher, _, _ = _setup(tmp_path, monkeypatch, entries)

    with patch("src.downloader.comment_refresher.fetch_comments",
               side_effect=[(FRESH_COMMENTS, "ok"), ([], "quota_exhausted")]) as mock_fetch:
        summary = refresher.refresh_old_comments(days=7)

    assert mock_fetch.call_count == 2
    assert summary["refreshed"] == 1
    assert summary["quota_stopped"] is True


def test_refresh_respects_limit(tmp_path, monkeypatch):
    entries = []
    for i in range(5):
        t = tmp_path / "transcripts" / f"video{i}.md"
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text("# t", encoding="utf-8")
        (tmp_path / "transcripts" / f"video{i}_comments.md").write_text("# c", encoding="utf-8")
        entries.append(_make_entry(f"vid{i}1234567", 10 + i, str(t)))

    refresher, _, _ = _setup(tmp_path, monkeypatch, entries)

    with patch("src.downloader.comment_refresher.fetch_comments", return_value=(FRESH_COMMENTS, "ok")) as mock_fetch:
        summary = refresher.refresh_old_comments(days=7, limit=2)

    assert mock_fetch.call_count == 2
    assert summary["checked"] == 2
    assert summary["refreshed"] == 2


def test_refresh_logs_failure_and_continues(tmp_path, monkeypatch):
    t = tmp_path / "transcripts" / "video0.md"
    t.parent.mkdir(parents=True, exist_ok=True)
    t.write_text("# t", encoding="utf-8")
    (tmp_path / "transcripts" / "video0_comments.md").write_text("# c", encoding="utf-8")
    entries = [_make_entry("vid01234567a", 10, str(t))]

    refresher, _, error_log = _setup(tmp_path, monkeypatch, entries)

    with patch("src.downloader.comment_refresher.fetch_comments", return_value=(FRESH_COMMENTS, "ok")), \
         patch("src.downloader.comment_refresher.save_comments_markdown", side_effect=OSError("disk full")):
        summary = refresher.refresh_old_comments(days=7)

    assert summary["failed"] == 1
    assert summary["refreshed"] == 0

    logged = json.loads(error_log.read_text(encoding="utf-8"))
    assert len(logged["errors"]) == 1
    assert logged["errors"][0]["video_id"] == "vid01234567a"
    assert logged["errors"][0]["reason"] == "comment_refresh_failed"


def test_refresh_with_no_candidates_exits_cleanly(tmp_path, monkeypatch):
    t = tmp_path / "transcripts" / "video0.md"
    t.parent.mkdir(parents=True, exist_ok=True)
    t.write_text("# t", encoding="utf-8")
    entries = [_make_entry("vid01234567a", 1, str(t))]  # too recent

    refresher, _, _ = _setup(tmp_path, monkeypatch, entries)

    with patch("src.downloader.comment_refresher.fetch_comments") as mock_fetch:
        summary = refresher.refresh_old_comments(days=7)

    mock_fetch.assert_not_called()
    assert summary == {"checked": 0, "refreshed": 0, "skipped": 0, "failed": 0, "quota_stopped": False}
