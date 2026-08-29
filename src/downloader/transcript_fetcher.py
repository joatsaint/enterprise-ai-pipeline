import os
import re
import requests
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled


# ---------------------------------------------------------------------------
# Proxy-aware API factory
# ---------------------------------------------------------------------------

_proxy_status_printed = False


def get_ytt_api():
    """
    Returns a YouTubeTranscriptApi instance.
    Uses Webshare rotating residential proxies if credentials are set in .env.
    Falls back to direct connection if no proxy credentials found.
    Proxy status is printed once per session only.
    """
    global _proxy_status_printed

    proxy_username = os.getenv("WEBSHARE_PROXY_USERNAME", "").strip()
    proxy_password = os.getenv("WEBSHARE_PROXY_PASSWORD", "").strip()

    if proxy_username and proxy_password:
        if not _proxy_status_printed:
            print("[PROXY] Using Webshare rotating residential proxies.")
            _proxy_status_printed = True
        from youtube_transcript_api.proxies import WebshareProxyConfig
        return YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=proxy_username,
                proxy_password=proxy_password,
            )
        )
    else:
        if not _proxy_status_printed:
            print("[PROXY] No proxy configured — using direct connection.")
            _proxy_status_printed = True
        return YouTubeTranscriptApi()


def _load_env():
    """Load .env file into os.environ if present."""
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


_load_env()


# ---------------------------------------------------------------------------
# URL utilities
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

def get_video_metadata(video_id):
    """Fetch title, channel name, and published date from YouTube page."""
    metadata = {"title": video_id, "channel": "Unknown", "published": None}
    try:
        resp = requests.get(
            f"https://www.youtube.com/watch?v={video_id}",
            headers={"Accept-Language": "en-US,en;q=0.9"},
            timeout=10,
        )
        title_match = re.search(r'"title":"([^"]+)"', resp.text)
        if title_match:
            metadata["title"] = title_match.group(1)

        channel_match = re.search(r'"ownerChannelName":"([^"]+)"', resp.text)
        if channel_match:
            metadata["channel"] = channel_match.group(1)

        date_match = re.search(r'"publishDate":"([^"]+)"', resp.text)
        if date_match:
            metadata["published"] = date_match.group(1)[:10]
    except Exception:
        pass
    return metadata


# ---------------------------------------------------------------------------
# Transcript cleaning
# ---------------------------------------------------------------------------

def clean_transcript(snippets):
    """
    Clean transcript text applying all token optimization steps in order:
    1. Remove timestamps
    2. Strip filler words
    3. Remove auto-caption tags
    4. Collapse excess whitespace
    5. Remove duplicate consecutive sentences

    Returns: (cleaned_text, word_count_before, word_count_after)
    """
    raw = " ".join(s.text for s in snippets)
    word_count_before = len(raw.split())

    # Step 1 — Remove timestamp patterns: [00:01:23], 0:01, 00:01:23
    raw = re.sub(r'\[?\d{1,2}:\d{2}(?::\d{2})?\]?', '', raw)

    # Step 2 — Strip filler words
    raw = re.sub(r'\bum+\b', '', raw, flags=re.IGNORECASE)
    raw = re.sub(r'\buh+\b', '', raw, flags=re.IGNORECASE)
    raw = re.sub(r',\s*like\s*,', ',', raw, flags=re.IGNORECASE)
    raw = re.sub(r',\s*you know\s*,', ',', raw, flags=re.IGNORECASE)
    raw = re.sub(r'\b(like|you know)\s*,', ',', raw, flags=re.IGNORECASE)

    # Step 3 — Remove auto-caption tags
    raw = re.sub(
        r'\[(?:Music|Applause|Laughter|Music playing|Applauding|Cheering)\]',
        '',
        raw,
        flags=re.IGNORECASE,
    )

    # Step 4 — Collapse excess whitespace
    raw = re.sub(r' {2,}', ' ', raw)
    raw = re.sub(r'\n{3,}', '\n\n', raw)
    raw = raw.strip()

    # Step 5 — Remove duplicate consecutive sentences
    sentences = re.split(r'(?<=[.!?])\s+', raw)
    deduped = []
    prev = None
    for s in sentences:
        s = s.strip()
        if s and s != prev:
            deduped.append(s)
        prev = s
    raw = ' '.join(deduped).strip()

    word_count_after = len(raw.split())
    if word_count_before > 0:
        reduction = round((1 - word_count_after / word_count_before) * 100, 1)
    else:
        reduction = 0.0

    print(f"Reduced from {word_count_before} words to {word_count_after} words ({reduction}% reduction)")

    return raw, word_count_before, word_count_after


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------

def fetch_transcript(video_id):
    """Fetch raw transcript snippets via proxy-aware API. Raises on failure."""
    api = get_ytt_api()
    return api.fetch(video_id, languages=["en"])
