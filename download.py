import os
import re
import sys
from urllib.parse import urlparse, parse_qs

import requests
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled


def extract_video_id(url):
    parsed = urlparse(url)
    if parsed.hostname in ("youtu.be",):
        return parsed.path.lstrip("/").split("/")[0]
    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        if parsed.path == "/watch":
            qs = parse_qs(parsed.query)
            if "v" in qs:
                return qs["v"][0]
        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/shorts/")[1].split("/")[0]
        if parsed.path.startswith("/live/"):
            return parsed.path.split("/live/")[1].split("/")[0]
    raise ValueError(f"Could not extract video ID from URL: {url}")


def get_video_title(video_id):
    try:
        resp = requests.get(
            f"https://www.youtube.com/watch?v={video_id}",
            headers={"Accept-Language": "en-US,en;q=0.9"},
            timeout=10,
        )
        match = re.search(r'"title":"([^"]+)"', resp.text)
        if match:
            return match.group(1)
    except Exception:
        pass
    return video_id


def sanitize_filename(title, video_id):
    safe = re.sub(r"[^\w\s-]", "", title)
    safe = re.sub(r"\s+", "_", safe.strip())
    safe = safe[:60].rstrip("_")
    return f"{safe}_{video_id}"


def clean_text(snippets):
    raw = " ".join(s.text for s in snippets)
    raw = re.sub(r"\b\d{1,2}:\d{2}\b", "", raw)
    raw = re.sub(r"\s{2,}", " ", raw).strip()
    return raw


BUDGET = 50_000


def apply_token_budget(text):
    if len(text) <= BUDGET:
        return text
    print(f"[WARNING] Transcript truncated via Context Sandwich (>{BUDGET} chars)")
    n = len(text)
    head = text[:int(n * 0.2)]
    tail = text[int(n * 0.8):]
    return head + "\n\n[...CONTEXT SANDWICH APPLIED — middle omitted...]\n\n" + tail


def main():
    if len(sys.argv) < 2:
        print("Usage: python download.py <YouTube URL>")
        sys.exit(1)

    url = sys.argv[1]

    try:
        video_id = extract_video_id(url)
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    api = YouTubeTranscriptApi()

    try:
        fetched = api.fetch(video_id, languages=["en"])
    except NoTranscriptFound:
        print(f"[ERROR] No English transcript found for video: {video_id}")
        sys.exit(1)
    except TranscriptsDisabled:
        print(f"[ERROR] Transcripts are disabled for video: {video_id}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to fetch transcript: {e}")
        sys.exit(1)

    title = get_video_title(video_id)
    filename = sanitize_filename(title, video_id) + ".txt"

    text = clean_text(fetched.snippets)
    text = apply_token_budget(text)

    os.makedirs("transcripts", exist_ok=True)
    filepath = os.path.join("transcripts", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        print(f"[OK] Saved: {filepath} ({os.path.getsize(filepath):,} bytes)")
    else:
        print(f"[ERROR] File missing or empty after write: {filepath}")
        sys.exit(1)


if __name__ == "__main__":
    main()
