"""
YouTube comment fetcher using the YouTube Data API v3.

Session-level quota flag: once a 403/quotaExceeded is received, all
subsequent fetch_comments() calls in the same session return [] immediately
without hitting the API again. Transcript downloads continue uninterrupted.
"""
import os
import re
from datetime import date


# ---------------------------------------------------------------------------
# Load .env into os.environ at module import time
# ---------------------------------------------------------------------------

def _load_env():
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
# Session-level quota flag
# ---------------------------------------------------------------------------

_quota_exhausted = False


def reset_quota_flag():
    """Reset the session quota flag. Exposed for use in tests."""
    global _quota_exhausted
    _quota_exhausted = False


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_api_key():
    """Load YOUTUBE_API_KEY from os.environ (populated from .env at import time)."""
    return os.environ.get("YOUTUBE_API_KEY", "").strip()


def _make_api_request(video_id, api_key):
    """
    Execute the YouTube Data API commentThreads.list call via direct HTTP.
    Uses requests instead of googleapiclient to avoid the discovery schema
    prefetch that can fail in certain network environments.
    Isolated into its own function so tests can patch it cleanly.
    """
    import requests

    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "order": "relevance",
        "maxResults": 100,
        "textFormat": "plainText",
        "key": api_key,
    }
    resp = requests.get(url, params=params, timeout=10)

    # Attach status to the response so error handling can inspect it
    if not resp.ok:
        err = Exception(f"HTTP {resp.status_code}: {resp.text[:300]}")
        err.resp = type("R", (), {"status": resp.status_code})()
        err.content = resp.content
        raise err

    return resp.json()


def _slugify(title, max_len=60):
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    return slug[:max_len].rstrip('-')


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_comments(video_id):
    """
    Fetch top 100 comments (sorted by relevance) for a video.

    Returns: (comments_list, status_str)
        comments_list: list of {author, text, like_count, published_at}
        status_str: "ok" | "disabled" | "quota_exhausted" | "no_api_key" |
                    "comments_unavailable" | "failed"

    Never raises — any failure returns ([], status).
    """
    global _quota_exhausted

    if _quota_exhausted:
        return [], "quota_exhausted"

    api_key = _load_api_key()
    if not api_key:
        return [], "no_api_key"

    try:
        response = _make_api_request(video_id, api_key)
    except Exception as e:
        # Decode error details
        resp_status = getattr(getattr(e, 'resp', None), 'status', 0)
        raw_content = getattr(e, 'content', b'')
        if isinstance(raw_content, bytes):
            content_str = raw_content.decode('utf-8', errors='replace')
        else:
            content_str = str(raw_content)

        if resp_status == 403:
            if "quotaExceeded" in content_str or "dailyLimitExceeded" in content_str:
                _quota_exhausted = True
                print("[WARN] YouTube API quota exhausted for today. Skipping remaining comment fetches.")
                return [], "quota_exhausted"
            # Generic 403 — treat conservatively as quota exhausted
            _quota_exhausted = True
            print("[WARN] YouTube API quota exhausted for today.")
            return [], "quota_exhausted"

        if resp_status == 400:
            if "commentsDisabled" in content_str:
                return [], "comments_disabled"

        if resp_status == 404:
            return [], "comments_unavailable"

        # Fallback: check error string
        err_lower = str(e).lower()
        if "disabled" in err_lower or "commentsdisabled" in err_lower:
            return [], "comments_disabled"

        return [], "failed"

    comments = []
    for item in response.get("items", []):
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        comments.append({
            "author": snippet.get("authorDisplayName", "Unknown"),
            "text": snippet.get("textDisplay", ""),
            "like_count": snippet.get("likeCount", 0),
            "published_at": snippet.get("publishedAt", "")[:10],
        })
    return comments, "ok"


def save_comments_markdown(video_id, title, channel, comments, category_folder,
                           downloaded_date=None, file_path=None, fetched_date=None):
    """
    Save comments list to a _comments.md file in the category folder.

    Args:
        downloaded_date: date used to derive the standard filename
            (transcripts/<category>/<date>_<slug>_comments.md). Ignored if
            file_path is given.
        file_path: write directly to this path instead of deriving one —
            used to refresh an existing comments file in place (see
            comment_refresher.py) without creating a duplicate under a
            slightly different slug.
        fetched_date: date shown in the "Fetched:" header line. Defaults to
            downloaded_date — pass a fresh date when refreshing so the file
            reflects when the comments were actually re-pulled.

    Returns: file path (str)
    """
    if downloaded_date is None:
        downloaded_date = date.today().isoformat()
    if fetched_date is None:
        fetched_date = downloaded_date

    if file_path is None:
        slug = _slugify(title)
        filename = f"{downloaded_date}_{slug}_comments.md"
        output_dir = os.path.join("transcripts", category_folder)
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)

    lines = [
        f"# Comments: {title}",
        "",
        f"**Channel:** {channel}",
        f"**Video URL:** https://www.youtube.com/watch?v={video_id}",
        f"**Comments Fetched:** {len(comments)}",
        f"**Fetched:** {fetched_date}",
        "",
        "---",
        "",
        "## Top Comments (by relevance)",
        "",
    ]

    for comment in comments:
        lines.append(comment["text"])
        lines.append(
            f"— {comment['author']} | {comment['like_count']} likes | {comment['published_at']}"
        )
        lines.append("")
        lines.append("---")
        lines.append("")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return file_path
