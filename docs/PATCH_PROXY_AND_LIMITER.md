# PATCH_PROXY_AND_LIMITER.md
## Paste this into Claude Code inside the youtube-downloader project folder

---

This is a targeted patch — not a full scaffold. Read CLAUDE.md before starting.
Do not modify any file not listed below. Do not run tests unless instructed.
Verify Python 3.10+ before starting.

---

## Context

YouTube blocks bulk transcript requests from repeated IPs. The fix is rotating
residential proxies via Webshare, which is natively supported by the
youtube-transcript-api library. This patch adds proxy support plus two
channel download controls: a video count limiter and a minimum duration filter.

---

## Files to modify

1. src/downloader/transcript_fetcher.py
2. src/downloader/channel.py
3. src/channels/registry.py
4. .env.example

---

## Change 1 — transcript_fetcher.py: Add Webshare proxy support

At the top of transcript_fetcher.py, update the YouTubeTranscriptApi
initialization to read proxy credentials from environment variables.

```python
import os
from youtube_transcript_api import YouTubeTranscriptApi

def get_ytt_api():
    """
    Returns a YouTubeTranscriptApi instance.
    Uses Webshare rotating residential proxies if credentials are set in .env.
    Falls back to direct connection if no proxy credentials found.
    """
    proxy_username = os.getenv("WEBSHARE_PROXY_USERNAME", "").strip()
    proxy_password = os.getenv("WEBSHARE_PROXY_PASSWORD", "").strip()

    if proxy_username and proxy_password:
        from youtube_transcript_api.proxies import WebshareProxyConfig
        print("[PROXY] Using Webshare rotating residential proxies.")
        return YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=proxy_username,
                proxy_password=proxy_password,
            )
        )
    else:
        print("[PROXY] No proxy configured — using direct connection.")
        return YouTubeTranscriptApi()
```

Replace all existing direct instantiations of YouTubeTranscriptApi() in this
file with get_ytt_api(). The proxy print line should only appear once per
session — add a module-level flag to suppress it after the first call.

---

## Change 2 — channel.py: Add video count limiter and duration filter

### 2a. Read limits from environment and channel registry

At the top of run_channel() or equivalent batch function, load:

```python
import os

MAX_VIDEOS_DEFAULT = int(os.getenv("MAX_VIDEOS_DEFAULT", "20"))
MIN_DURATION_SECONDS = int(os.getenv("MIN_VIDEO_DURATION_SECONDS", "300"))
```

### 2b. Apply per-channel override

After loading the channel entry from channels.json, check for a per-channel
max_videos override:

```python
max_videos = channel_entry.get("max_videos", MAX_VIDEOS_DEFAULT)
```

### 2c. Apply the video count limit

After yt-dlp retrieves the video list, slice to max_videos most recent:

```python
# yt-dlp returns newest first by default
video_entries = video_entries[:max_videos]
```

Log this clearly:
```
[INFO] Limiting to {max_videos} most recent videos (channel setting).
```

### 2d. Apply the minimum duration filter

After slicing, filter out videos shorter than MIN_DURATION_SECONDS.
yt-dlp returns duration in seconds in the flat-playlist JSON.

```python
before_count = len(video_entries)
video_entries = [
    v for v in video_entries
    if v.get("duration", 0) >= MIN_DURATION_SECONDS
]
filtered_count = before_count - len(video_entries)
if filtered_count > 0:
    print(f"[INFO] Skipped {filtered_count} video(s) under "
          f"{MIN_DURATION_SECONDS // 60} minutes.")
```

### 2e. Add cloud environment warning

At the start of any channel batch download function, add:

```python
import sys
if "CLAUDE" in os.environ or not sys.stdin.isatty():
    print("[WARNING] Possible cloud environment detected. YouTube may block "
          "transcript requests from cloud IPs. If downloads fail with IP "
          "block errors, run this command from your local terminal instead.")
```

---

## Change 3 — registry.py: Support max_videos field in channels.json

Ensure add_channel() prompts for an optional max_videos override:

```
Max videos to download (leave blank to use default from .env): 
```

If blank — do not write max_videos to the channel entry (uses .env default).
If a number is entered — write it as an integer: `"max_videos": 30`

Update list_channels() to display max_videos if set:
```
[1] AI News & Strategy Daily | Nate B Jones
    URL: https://www.youtube.com/@NateBJones/videos
    Group: ai-and-claude-code
    Max videos: 20 (default)   ← or "30 (custom)" if set
    Active: yes
```

---

## Change 4 — .env.example: Add new variables

Add these lines to .env.example with placeholder values:

```
# Webshare rotating residential proxy (get credentials at dashboard.webshare.io)
WEBSHARE_PROXY_USERNAME=your_webshare_proxy_username
WEBSHARE_PROXY_PASSWORD=your_webshare_proxy_password

# Channel download limits
MAX_VIDEOS_DEFAULT=20
MIN_VIDEO_DURATION_SECONDS=300
```

---

## Do NOT change

- orchestrator.py
- classifier/category.py
- converter/to_markdown.py
- comment_fetcher.py
- main.py (unless a function signature requires updating)
- Any test file

---

## After making changes

Run one quick smoke test — do not run the full test suite:

```
python -m pytest tests/ -k "test_channel" -v
```

If no channel-specific tests exist, run:
```
python -m pytest tests/ -v
```

All 27 existing tests must still pass.

Then run a live single-video download to confirm proxy is active:

```
python download.py https://youtu.be/ZX_DEbZDUTI
```

Confirm output shows either:
- `[PROXY] Using Webshare rotating residential proxies.`
- `[PROXY] No proxy configured — using direct connection.`

Report which one appeared and whether the download succeeded.

---

## Final checklist

- [ ] get_ytt_api() reads WEBSHARE_PROXY_USERNAME and WEBSHARE_PROXY_PASSWORD from .env
- [ ] Falls back to direct connection gracefully if no proxy credentials found
- [ ] Proxy status printed once per session only
- [ ] MAX_VIDEOS_DEFAULT read from .env (default 20)
- [ ] MIN_VIDEO_DURATION_SECONDS read from .env (default 300)
- [ ] Per-channel max_videos override supported in channels.json
- [ ] Videos sliced to max_videos most recent before processing
- [ ] Videos under minimum duration filtered and count logged
- [ ] add-channel prompts for optional max_videos
- [ ] list-channels displays max_videos status
- [ ] Cloud environment warning fires when appropriate
- [ ] .env.example updated with new variables
- [ ] All 27 existing tests still pass
- [ ] Live single-video download confirms proxy status in output

Report checklist status when done.
EOF
