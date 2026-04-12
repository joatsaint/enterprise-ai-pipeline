import json
import os
import re
import sys
import time
from datetime import datetime, date, timezone
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import NoTranscriptFound, TranscriptsDisabled

from src.downloader.transcript_fetcher import (
    get_video_metadata,
    fetch_transcript,
    clean_transcript,
)
from src.downloader.comment_fetcher import fetch_comments, save_comments_markdown
from src.classifier.category import classify, suggest_category
from src.converter.to_markdown import convert_to_markdown


DOWNLOAD_LOG = "logs/download_log.json"
ERROR_LOG = "logs/error_log.json"
RUN_SUMMARY = "logs/run_summary.json"


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

def _ensure_dirs():
    os.makedirs("logs", exist_ok=True)
    os.makedirs("transcripts/ai-and-claude-code", exist_ok=True)
    os.makedirs("transcripts/bitcoin-and-economic-news", exist_ok=True)
    os.makedirs("transcripts/uncategorized", exist_ok=True)

    if not os.path.exists(DOWNLOAD_LOG):
        _write_json(DOWNLOAD_LOG, {
            "downloads": [],
            "last_updated": None,
            "notes": "Tracks downloaded video IDs, categories, and override history.",
        })
    if not os.path.exists(ERROR_LOG):
        _write_json(ERROR_LOG, {"errors": []})
    if not os.path.exists(RUN_SUMMARY):
        _write_json(RUN_SUMMARY, {})


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def _read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _append_error(video_id, url, error_msg):
    try:
        log = _read_json(ERROR_LOG)
    except Exception:
        log = {"errors": []}
    log["errors"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "video_id": video_id,
        "url": url,
        "error": error_msg,
    })
    _write_json(ERROR_LOG, log)


# ---------------------------------------------------------------------------
# Step 1 — Input validation
# ---------------------------------------------------------------------------

def validate_input(url):
    """
    Validate URL format. Returns video_id (str) or raises ValueError
    with a plain-English message.
    """
    if "list=" in url:
        raise ValueError(
            "That looks like a playlist URL. Please provide a single video URL."
        )

    parsed = urlparse(url)
    path = parsed.path or ""

    if any(seg in path for seg in ("/@", "/channel/", "/c/", "/user/")):
        raise ValueError(
            "That's a channel URL. Use --channel flag for channel downloads."
        )
    if "/shorts/" in path:
        raise ValueError(
            "Shorts often lack transcripts. Try a long-form video URL."
        )

    video_id = None
    if parsed.hostname in ("youtu.be",):
        video_id = path.lstrip("/").split("/")[0]
    elif parsed.hostname in ("www.youtube.com", "youtube.com"):
        if path == "/watch":
            qs = parse_qs(parsed.query)
            if "v" not in qs:
                raise ValueError("No video ID found in URL.")
            video_id = qs["v"][0]
        elif path.startswith("/live/"):
            video_id = path.split("/live/")[1].split("/")[0]
        else:
            raise ValueError(f"Unrecognized YouTube URL format: {url}")
    else:
        raise ValueError(f"Not a YouTube URL: {url}")

    if not video_id or not re.match(r'^[A-Za-z0-9_-]{11}$', video_id):
        raise ValueError(
            f"Invalid video ID extracted: '{video_id}'. Expected 11 characters."
        )

    return video_id


# ---------------------------------------------------------------------------
# Step 2 — Duplicate check
# ---------------------------------------------------------------------------

def check_duplicate(video_id, log):
    return any(d["video_id"] == video_id for d in log.get("downloads", []))


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run(url, pre_suggestion=None):
    """
    Execute the full single-URL download pipeline.

    Args:
        url: YouTube video URL.
        pre_suggestion: Optional category folder name pre-filled by channel.py
                        when the channel has a registered group.

    Returns the state dict.
    """
    _ensure_dirs()

    start_time = time.time()
    stats = {
        "downloaded": 0,
        "skipped": 0,
        "failed": 0,
        "retried": 0,
        "tokens_saved": 0,
        "comments_ok": 0,
        "comments_disabled": 0,
        "comments_failed": 0,
    }

    state = {
        "video_id": None,
        "url": url,
        "title": None,
        "channel": None,
        "status": "pending",
        "failure_reason": None,
        "retry_count": 0,
        "category": None,
        "file_path": None,
        "tokens_before": 0,
        "tokens_after": 0,
        "comments_fetched": 0,
        "comments_file": None,
        "comments_status": "pending",
    }

    interrupted = False

    try:
        # ----------------------------------------------------------------
        # Step 1 — Validate input
        # ----------------------------------------------------------------
        try:
            video_id = validate_input(url)
        except ValueError as e:
            print(f"[ERROR] {e}")
            state["status"] = "failed"
            state["failure_reason"] = str(e)
            _append_error("unknown", url, str(e))
            stats["failed"] += 1
            _print_summary(stats, start_time)
            return state

        state["video_id"] = video_id

        # ----------------------------------------------------------------
        # Step 2 — Check duplicate
        # ----------------------------------------------------------------
        log = _read_json(DOWNLOAD_LOG)
        if check_duplicate(video_id, log):
            print(f"[SKIP] Already downloaded: {video_id}")
            state["status"] = "skipped"
            stats["skipped"] += 1
            _print_summary(stats, start_time)
            return state

        # ----------------------------------------------------------------
        # Step 3 — Fetch transcript (retry once on generic failure)
        # ----------------------------------------------------------------
        snippets = None
        for attempt in range(2):
            try:
                snippets = fetch_transcript(video_id)
                break
            except NoTranscriptFound:
                msg = f"No English transcript found for video: {video_id}"
                print(f"[ERROR] {msg} — logged as no_captions")
                state["status"] = "failed"
                state["failure_reason"] = "no_captions"
                _append_error(video_id, url, "no_captions")
                stats["failed"] += 1
                _print_summary(stats, start_time)
                return state
            except TranscriptsDisabled:
                msg = f"Transcripts are disabled for video: {video_id}"
                print(f"[ERROR] {msg} — logged as transcripts_disabled")
                state["status"] = "failed"
                state["failure_reason"] = "no_captions"
                _append_error(video_id, url, "transcripts_disabled")
                stats["failed"] += 1
                _print_summary(stats, start_time)
                return state
            except Exception as e:
                if attempt == 0:
                    print(f"[WARN] Transcript fetch failed, retrying in 5s... ({e})")
                    stats["retried"] += 1
                    state["retry_count"] += 1
                    time.sleep(5)
                else:
                    print(f"[ERROR] Failed to fetch transcript: {e}")
                    state["status"] = "failed"
                    state["failure_reason"] = str(e)
                    _append_error(video_id, url, str(e))
                    stats["failed"] += 1
                    _print_summary(stats, start_time)
                    return state

        # ----------------------------------------------------------------
        # Step 4 — Fetch comments (non-blocking — never fails the pipeline)
        # ----------------------------------------------------------------
        comments, comments_status = fetch_comments(video_id)
        state["comments_fetched"] = len(comments)
        state["comments_status"] = comments_status

        if comments_status == "ok":
            print(f"[COMMENTS] Fetched {len(comments)} comment(s).")
            stats["comments_ok"] += 1
        elif comments_status in ("disabled", "comments_disabled"):
            print("[COMMENTS] Comments disabled for this video.")
            state["comments_status"] = "comments_disabled"
            stats["comments_disabled"] += 1
        elif comments_status == "quota_exhausted":
            stats["comments_disabled"] += 1  # counts as skipped, not failed
        elif comments_status == "no_api_key":
            print("[COMMENTS] No YOUTUBE_API_KEY set — skipping comments.")
            stats["comments_disabled"] += 1
        else:
            print(f"[COMMENTS] Could not fetch comments ({comments_status}).")
            stats["comments_failed"] += 1

        # ----------------------------------------------------------------
        # Step 5 — Get metadata + clean transcript
        # ----------------------------------------------------------------
        metadata = get_video_metadata(video_id)
        state["title"] = metadata["title"]
        state["channel"] = metadata["channel"]

        cleaned_text, words_before, words_after = clean_transcript(snippets)
        state["tokens_before"] = words_before
        state["tokens_after"] = words_after
        metadata["word_count_after"] = words_after
        stats["tokens_saved"] += max(0, words_before - words_after)

        # ----------------------------------------------------------------
        # Step 6 — Classify category
        # ----------------------------------------------------------------
        folder, display, was_overridden = classify(
            state["title"], state["channel"], video_id,
            pre_suggestion=pre_suggestion,
        )
        state["category"] = folder

        # ----------------------------------------------------------------
        # Step 7 — Convert transcript to Markdown (retry once on failure)
        # ----------------------------------------------------------------
        today = date.today().isoformat()
        file_path = None
        for attempt in range(2):
            try:
                file_path = convert_to_markdown(
                    cleaned_text, metadata, display, url, today
                )
                break
            except Exception as e:
                if attempt == 0:
                    print(f"[WARN] Markdown write failed, retrying in 5s... ({e})")
                    stats["retried"] += 1
                    state["retry_count"] += 1
                    time.sleep(5)
                else:
                    print(f"[ERROR] Failed to write transcript file: {e}")
                    if file_path and os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"[CLEANUP] Removed partial file: {file_path}")
                    state["status"] = "failed"
                    state["failure_reason"] = str(e)
                    _append_error(video_id, url, str(e))
                    stats["failed"] += 1
                    _print_summary(stats, start_time)
                    return state

        state["file_path"] = file_path

        # Idempotency: verify file is real
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            print(f"[ERROR] File missing or empty after write: {file_path}")
            state["status"] = "failed"
            stats["failed"] += 1
            _print_summary(stats, start_time)
            return state

        print(f"[OK] Saved: {file_path} ({os.path.getsize(file_path):,} bytes)")
        state["status"] = "success"
        stats["downloaded"] += 1

        # ----------------------------------------------------------------
        # Step 8 — Save comments Markdown (only if comments were fetched)
        # ----------------------------------------------------------------
        if comments:
            try:
                comments_file = save_comments_markdown(
                    video_id,
                    state["title"],
                    state["channel"],
                    comments,
                    folder,
                    today,
                )
                state["comments_file"] = comments_file
                print(f"[OK] Comments: {comments_file} ({os.path.getsize(comments_file):,} bytes)")
            except Exception as e:
                print(f"[WARN] Failed to save comments file: {e}")
                state["comments_status"] = "failed"

        # ----------------------------------------------------------------
        # Step 9 — Log download
        # ----------------------------------------------------------------
        log["downloads"].append({
            "video_id": video_id,
            "title": state["title"],
            "channel": state["channel"],
            "url": url,
            "suggested_category": suggest_category(state["title"], state["channel"]),
            "final_category": folder,
            "was_overridden": was_overridden,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "file_path": file_path,
            "comments_file": state["comments_file"],
            "comments_status": state["comments_status"],
        })
        log["last_updated"] = datetime.now(timezone.utc).isoformat()
        _write_json(DOWNLOAD_LOG, log)

        # ----------------------------------------------------------------
        # Step 10 — Update run summary
        # ----------------------------------------------------------------
        _write_run_summary(state, stats, start_time, "success")

    except KeyboardInterrupt:
        interrupted = True
        print("\n[INTERRUPTED] Finishing current operation...")
        state["status"] = "interrupted"
        _write_run_summary(state, stats, start_time, "interrupted")

    _print_summary(stats, start_time, interrupted=interrupted)
    return state


# ---------------------------------------------------------------------------
# Observability
# ---------------------------------------------------------------------------

def _write_run_summary(state, stats, start_time, status):
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "stats": stats,
        "duration_seconds": round(time.time() - start_time, 1),
        "last_video": {
            "video_id": state.get("video_id"),
            "title": state.get("title"),
            "status": state.get("status"),
            "comments_status": state.get("comments_status"),
        },
    }
    _write_json(RUN_SUMMARY, summary)


def _print_summary(stats, start_time, interrupted=False):
    duration = round(time.time() - start_time, 1)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    label = "Interrupted" if interrupted else "Run Complete"
    bar = "-" * 36
    disabled = stats.get("comments_disabled", 0)
    failed_c = stats.get("comments_failed", 0)
    ok_c = stats.get("comments_ok", 0)
    lines = [
        "",
        bar,
        f" {label} -- {now}",
        bar,
        f" [OK]       Downloaded:   {stats['downloaded']}",
        f" [SKIP]     Skipped:      {stats['skipped']} (duplicates)",
        f" [FAIL]     Failed:       {stats['failed']} (see error_log.json)",
        f" [RETRY]    Retried:      {stats['retried']}",
        f" [SAVED]    Tokens saved: {stats['tokens_saved']} words cleaned",
        f" [COMMENTS] Comments:     {ok_c} files ({disabled} disabled, {failed_c} failed)",
        f" [TIME]     Duration:     {duration}s",
        bar,
    ]
    output = "\n".join(lines)
    try:
        print(output)
    except UnicodeEncodeError:
        print(output.encode("ascii", errors="replace").decode("ascii"))
