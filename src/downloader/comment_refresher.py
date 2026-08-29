"""
Comment Refresher — re-fetches comments for videos downloaded more than N
days ago, since comment counts and content keep growing after upload.

Why this matters (see CLAUDE.md "Comment Fetching Rules"):
comments are the highest-signal pain-point data source — "what the audience
actually struggles with, asks, and argues about." A video downloaded a week
ago may have had only a handful of comments at fetch time; by now it could
have hundreds, with the real audience questions and frustrations surfaced.
Re-checking older videos keeps that signal current for the pain point
extractor without re-touching the canonical transcript.

Refreshes the existing _comments.md file IN PLACE (overwrite, same filename).
Comments are an explicitly secondary, recency-sensitive data source — not
the canonical transcript that CLAUDE.md's "treat /transcripts/ as read-only"
rule protects. Re-running this is always safe: same cutoff, same files,
freshest data wins.
"""
import os
import re
import json
from datetime import datetime, timezone, timedelta

from src.downloader.comment_fetcher import fetch_comments, save_comments_markdown

DOWNLOAD_LOG = "logs/download_log.json"
ERROR_LOG = "logs/error_log.json"

_FETCHED_RE = re.compile(r"\*\*Fetched:\*\*\s*(\d{4}-\d{2}-\d{2})")


def _load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _log_error(video_id, reason, message):
    errors = _load_json(ERROR_LOG, {"errors": []})
    errors.setdefault("errors", []).append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "video_id": video_id,
        "reason": reason,
        "message": message,
    })
    _write_json(ERROR_LOG, errors)


def _existing_comments_path(entry):
    """Derive the _comments.md path that sits alongside the transcript file."""
    file_path = entry.get("file_path", "")
    if not file_path.endswith(".md"):
        return None
    return file_path[:-len(".md")] + "_comments.md"


def _last_fetched_date(comments_path):
    """
    Parse the '**Fetched:** YYYY-MM-DD' header line out of an existing
    _comments.md file. Returns a date, or None if no parseable Fetched
    line is found — treated as "never refreshed", always eligible.
    """
    try:
        with open(comments_path, "r", encoding="utf-8") as f:
            for _ in range(10):
                line = f.readline()
                if not line:
                    break
                m = _FETCHED_RE.search(line)
                if m:
                    try:
                        return datetime.strptime(m.group(1), "%Y-%m-%d").date()
                    except ValueError:
                        return None
    except OSError:
        return None
    return None


def find_stale_comment_videos(days=7, log=None):
    """
    Return download_log entries whose download timestamp is older than
    `days` days, that already have a _comments.md file on disk, and whose
    comments haven't already been refreshed within the last `days` days —
    otherwise repeat runs would loop on the same group instead of advancing
    through the backlog. Most-overdue (oldest fetch date, or never refreshed)
    candidates are returned first.
    """
    if log is None:
        log = _load_json(DOWNLOAD_LOG, {"downloads": []})

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_date = cutoff.date()
    candidates = []

    for entry in log.get("downloads", []):
        ts = entry.get("timestamp")
        if not ts:
            continue
        try:
            downloaded_at = datetime.fromisoformat(ts)
        except ValueError:
            continue
        if downloaded_at > cutoff:
            continue

        comments_path = _existing_comments_path(entry)
        if not comments_path or not os.path.exists(comments_path):
            continue

        last_fetched = _last_fetched_date(comments_path)
        if last_fetched is not None and last_fetched > cutoff_date:
            continue

        candidates.append((last_fetched, entry))

    candidates.sort(key=lambda pair: (pair[0] is not None, pair[0] or datetime.min.date()))
    return [entry for _, entry in candidates]


def refresh_old_comments(days=7, limit=None):
    """
    Re-fetch comments for every downloaded video older than `days` days that
    already has a comments file, and overwrite that file with the refreshed
    set. Stops early and reports if the YouTube API quota is exhausted.

    Args:
        days: age threshold in days (default 7, per the daily research cadence)
        limit: optional cap on how many videos to refresh this run — useful
            for a first real run to sanity-check quota usage before going wide

    Returns: summary dict {checked, refreshed, skipped, failed, quota_stopped}
    """
    candidates = find_stale_comment_videos(days=days)
    if limit is not None:
        candidates = candidates[:limit]

    summary = {"checked": 0, "refreshed": 0, "skipped": 0, "failed": 0, "quota_stopped": False}

    print(f"[SCAN] {len(candidates)} video(s) older than {days} day(s) with existing comment files.")
    if not candidates:
        print("[DONE] Nothing to refresh.")
        return summary

    today_iso = datetime.now(timezone.utc).date().isoformat()

    for i, entry in enumerate(candidates):
        video_id = entry.get("video_id")
        title = entry.get("title", "")
        channel = entry.get("channel", "")
        category = entry.get("final_category") or entry.get("suggested_category") or ""
        comments_path = _existing_comments_path(entry)
        downloaded_date = (entry.get("timestamp") or "")[:10] or None

        summary["checked"] += 1
        print(f"[{i + 1}/{len(candidates)}] Refreshing comments: {title[:70]}")

        comments, status = fetch_comments(video_id)

        if status == "quota_exhausted":
            summary["quota_stopped"] = True
            print("[STOP] YouTube API quota exhausted — stopping comment refresh for this session.")
            break

        if status != "ok":
            summary["skipped"] += 1
            print(f"          skipped (status: {status})")
            continue

        try:
            save_comments_markdown(
                video_id, title, channel, comments, category,
                downloaded_date=downloaded_date,
                file_path=comments_path,
                fetched_date=today_iso,
            )
            summary["refreshed"] += 1
            print(f"          refreshed -> {len(comments)} comment(s)")
        except Exception as e:
            summary["failed"] += 1
            _log_error(video_id, "comment_refresh_failed", str(e))
            print(f"[WARN] Failed to write refreshed comments for {video_id}: {e}")

    print(
        "[DONE] Comment refresh complete — "
        f"checked: {summary['checked']}, refreshed: {summary['refreshed']}, "
        f"skipped: {summary['skipped']}, failed: {summary['failed']}"
        + (" (stopped early — quota exhausted)" if summary["quota_stopped"] else "")
    )
    return summary
