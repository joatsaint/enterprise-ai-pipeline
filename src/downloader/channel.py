"""
Channel batch downloader.

Uses yt-dlp to enumerate a channel's video list, then runs the full
orchestrator pipeline on each video. Supports incremental (default) and
force-full modes with mandatory randomized rate limiting.

Environment variables (read from .env):
  MAX_VIDEOS_DEFAULT         Max videos per channel run (default 20)
  MIN_VIDEO_DURATION_SECONDS Minimum video duration to include (default 300s / 5 min)
"""
import json
import os
import random
import subprocess
import sys
import time


# ---------------------------------------------------------------------------
# Video list retrieval
# ---------------------------------------------------------------------------

def get_video_entries_from_channel(channel_url, limit=50):
    """
    Use yt-dlp to get up to `limit` video entries from a channel's video tab.
    Returns list of entry dicts (each has 'id' and optionally 'duration').
    Raises RuntimeError on yt-dlp failure.
    """
    result = subprocess.run(
        [
            sys.executable, "-m", "yt_dlp",
            "--flat-playlist",
            "--dump-single-json",
            "--playlist-end", str(limit),
            channel_url,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"yt-dlp failed (exit {result.returncode}): {result.stderr.strip()}"
        )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"yt-dlp returned invalid JSON: {e}")

    entries = [e for e in (data.get("entries") or []) if e and e.get("id")]
    print(f"[INFO] yt-dlp retrieved {len(entries)} video(s) from channel.")
    return entries


def get_video_ids_from_channel(channel_url, limit=50):
    """Compatibility wrapper — returns list of video_id strings."""
    entries = get_video_entries_from_channel(channel_url, limit)
    return [e["id"] for e in entries]


# ---------------------------------------------------------------------------
# Channel runner
# ---------------------------------------------------------------------------

def run_channel(channel_name_or_url, force_full=False, pre_suggestion=None):
    """
    Download transcripts and comments for videos in a channel.

    Args:
        channel_name_or_url: Channel name (from channels.json) or direct URL.
        force_full: If True, download all videos regardless of download log.
        pre_suggestion: Optional category folder to pre-fill the classifier.
                        If None, looks up the channel's group in channels.json.
    """
    from src.orchestrator import run as orchestrator_run, _read_json, DOWNLOAD_LOG, _ensure_dirs
    from src.channels.registry import find_channel

    _ensure_dirs()

    # ----------------------------------------------------------------
    # Cloud environment warning
    # ----------------------------------------------------------------
    if "CLAUDE" in os.environ or not sys.stdin.isatty():
        print(
            "[WARNING] Possible cloud environment detected. YouTube may block "
            "transcript requests from cloud IPs. If downloads fail with IP "
            "block errors, run this command from your local terminal instead."
        )

    # ----------------------------------------------------------------
    # Load limits from environment
    # ----------------------------------------------------------------
    max_videos_default = int(os.getenv("MAX_VIDEOS_DEFAULT", "20"))
    min_duration = int(os.getenv("MIN_VIDEO_DURATION_SECONDS", "300"))

    # ----------------------------------------------------------------
    # Resolve channel info
    # ----------------------------------------------------------------
    channel_info = find_channel(channel_name_or_url)
    if channel_info:
        channel_url = channel_info["url"]
        resolved_suggestion = pre_suggestion or channel_info.get("group")
        max_videos = channel_info.get("max_videos", max_videos_default)
        print(f"[INFO] Channel: {channel_info['name']} ({channel_url})")
    else:
        channel_url = channel_name_or_url
        resolved_suggestion = pre_suggestion
        max_videos = max_videos_default
        print(f"[INFO] Channel URL: {channel_url}")

    # Validate channel URL format
    if not channel_url.startswith("http"):
        print(f"[ERROR] Not a valid URL: '{channel_url}'. Register the channel with add-channel first.")
        return

    # ----------------------------------------------------------------
    # Get video entries (fetch enough to apply limits after filtering)
    # ----------------------------------------------------------------
    fetch_limit = max(max_videos * 3, 50)  # fetch extra to survive duration filter
    try:
        entries = get_video_entries_from_channel(channel_url, limit=fetch_limit)
    except RuntimeError as e:
        print(f"[ERROR] Failed to get video list: {e}")
        return

    if not entries:
        print("[INFO] No videos found for this channel.")
        return

    # ----------------------------------------------------------------
    # Apply video count limit (most recent first — yt-dlp default order)
    # ----------------------------------------------------------------
    entries = entries[:max_videos]
    print(f"[INFO] Limiting to {max_videos} most recent video(s) (channel setting).")

    # ----------------------------------------------------------------
    # Apply minimum duration filter
    # ----------------------------------------------------------------
    before_count = len(entries)
    entries = [e for e in entries if (e.get("duration") or 0) >= min_duration]
    filtered_count = before_count - len(entries)
    if filtered_count > 0:
        print(f"[INFO] Skipped {filtered_count} video(s) under {min_duration // 60} minutes.")

    if not entries:
        print("[INFO] No videos remain after duration filter.")
        return

    video_ids = [e["id"] for e in entries]

    # ----------------------------------------------------------------
    # Filter for incremental mode
    # ----------------------------------------------------------------
    if not force_full:
        try:
            log = _read_json(DOWNLOAD_LOG)
            downloaded_ids = {d["video_id"] for d in log.get("downloads", [])}
        except Exception:
            downloaded_ids = set()

        original_count = len(video_ids)
        video_ids = [vid for vid in video_ids if vid not in downloaded_ids]
        skipped_count = original_count - len(video_ids)
        if skipped_count:
            print(f"[INFO] Skipping {skipped_count} already-downloaded video(s).")

    if not video_ids:
        print("[INFO] Nothing new to download. Run with --force-full to re-download all.")
        return

    # ----------------------------------------------------------------
    # Hard cap: prompt user before exceeding 200 downloads
    # ----------------------------------------------------------------
    if len(video_ids) > 200:
        try:
            resp = input(
                f"[WARN] {len(video_ids)} videos to download. "
                "This exceeds the 200-video session limit. Continue? (y/N): "
            ).strip().lower()
        except (EOFError, KeyboardInterrupt):
            resp = "n"
        if resp != "y":
            print("[INFO] Aborted by user.")
            return

    delay_low, delay_high = (4, 7) if force_full else (2, 5)
    mode_label = "--force-full" if force_full else "incremental"
    print(
        f"[INFO] Downloading {len(video_ids)} video(s) "
        f"[{mode_label}] with {delay_low}-{delay_high}s randomized delay."
    )

    for i, video_id in enumerate(video_ids):
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"\n[{i + 1}/{len(video_ids)}] {url}")

        try:
            orchestrator_run(url, pre_suggestion=resolved_suggestion)
        except Exception as e:
            print(f"[ERROR] Unexpected error processing {video_id}: {e}")

        # Randomized rate-limit pause — skip after last video
        if i < len(video_ids) - 1:
            delay = random.uniform(delay_low, delay_high)
            print(f"[RATE] Pausing {delay:.1f}s...")
            time.sleep(delay)

    print(f"\n[DONE] Channel batch complete: {len(video_ids)} video(s) processed.")


# ---------------------------------------------------------------------------
# Group runner
# ---------------------------------------------------------------------------

def run_group(group_name, force_full=False):
    """Download all active channels in a group."""
    from src.channels.registry import channels_in_group

    members = channels_in_group(group_name)
    if not members:
        print(f"[INFO] No active channels found in group '{group_name}'.")
        return

    print(f"[INFO] Running {len(members)} channel(s) in group '{group_name}'...")
    for ch in members:
        print(f"\n[GROUP] Channel: {ch['name']}")
        run_channel(ch["name"], force_full=force_full)
