"""
Source Scanner — gathers candidate trending topics from a small, curated set
of sources for relevance_scorer.py to rank.

Sources (curated registry — same philosophy as channels.json: an intentional
list, not an open crawl):
  - A handful of subreddits via Reddit's public Atom RSS feeds (their *.json
    endpoints are OAuth-gated/403 now; the /top/.rss feed is still open)
  - A handful of RSS feeds from sysadmin/AI-industry blogs
  - A handful of Spiceworks (Discourse) tags via the public /tag/<slug>.json
    endpoint — direct connection first, proxy only as a fallback on 403/429
    (a stable IP + low frequency looks like a normal reader; rotating IPs can
    read as more bot-like to detection — so we don't proxy by default here)
  - GitHub — public Search API (unauthenticated, 10 req/min), searched against
    a curated term list, biased toward RECENTLY CREATED repos (not just
    recently updated) since the goal is catching new "weekend project" builds,
    not established repos getting routine commits
  - Hacker News — Algolia's public HN Search API (free, no key), same curated
    term list, restricted to the "story" tag
  - The existing transcript knowledge base (recurring themes, zero new calls)

GitHub + Hacker News both search the same BUILD_SIGNAL_TERMS list — this is
the "what are smart people obsessively building for free" signal: the same
handful of ideas turning up independently across many different repos/posts
is the thing worth noticing, not any single high-view post.

Anti-throttling design (mirrors CLAUDE.md's existing rate-limiting rules):
  - Routes through the project's existing Webshare rotating residential proxy
    if WEBSHARE_PROXY_USERNAME/PASSWORD are set in .env — same fallback-to-
    direct-connection pattern as transcript_fetcher.get_ytt_api()
  - Randomized pauses between requests (random.uniform — never uniform timing,
    per CLAUDE.md's "uniform timing is a bot signature" rule)
  - Descriptive User-Agent on Reddit requests (Reddit blocks/throttles default
    python-requests user agents)
  - Conditional GET on RSS feeds (If-Modified-Since) so unchanged feeds return
    304 and we don't re-fetch the same content every run
  - One run per day, capped request count per source — this is "check once
    each morning," not continuous scraping
  - On HTTP 429: pause 60s, retry once, then log and move on — never hammer
    a rate-limited endpoint (matches CLAUDE.md's API rate-limit rule)
"""
import os
import random
import re
import time
from email.utils import format_datetime
from datetime import datetime, timedelta, timezone

import requests
import defusedxml.ElementTree as ET


SUBREDDITS = [
    "sysadmin",
    "ITCareerQuestions",
    "cscareerquestions",
    "artificial",
    "iiiiiiitttttttttttt",
]

RSS_FEEDS = [
    {"name": "4sysops", "url": "https://4sysops.com/feed/"},
    {"name": "Adam the Automator", "url": "https://adamtheautomator.com/feed/"},
    {"name": "Ivanti Blog", "url": "https://www.ivanti.com/blog/feed"},
    {"name": "MarkTechPost", "url": "https://www.marktechpost.com/feed/"},
]

# Spiceworks Community (Discourse) tag slugs — curated 2026-06-14 from the full
# tag list, ranked by ICP fit + activity. Add/remove tags here.
SPICEWORKS_TAGS = [
    "artificial-intelligence",
    "process-automation",
    "powershell",
    "it-jobs-careers",
    "general-it-security",
]
SPICEWORKS_BASE = "https://community.spiceworks.com"

# "Weekend project" convergence terms — curated 2026-07-17 from Randy's own
# signal-hunting brief. Search these, not generic category terms ("AI
# assistant"), because the goal is spotting the same specific thing being
# independently rebuilt by many people, not general topic volume.
BUILD_SIGNAL_TERMS = [
    "Jarvis build",
    "AI operating system",
    "voice assistant local AI",
    "desktop AI",
    "Claude Code projects",
    "MCP server projects",
    "agentic workflows",
]

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"
GITHUB_LOOKBACK_DAYS = 45  # bias toward NEW repos, not old ones getting updated

HN_ALGOLIA_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
HN_LOOKBACK_DAYS = 45

USER_AGENT = "randy-trend-scanner/1.0 (personal research tool; contact via project owner)"

REDDIT_PAUSE = (2.0, 5.0)     # randomized seconds between Reddit requests
RSS_PAUSE = (1.0, 3.0)        # randomized seconds between RSS requests
SPICEWORKS_PAUSE = (2.0, 5.0)  # randomized seconds between Spiceworks requests
GITHUB_PAUSE = (6.0, 8.0)     # GitHub search API caps at 10 req/min unauthenticated
HN_PAUSE = (1.0, 2.0)         # Algolia HN search has a generous, informal rate limit
RATE_LIMIT_PAUSE = 60         # seconds to wait on HTTP 429 before one retry

_LAST_FETCH_LOG = "logs/trend_source_last_fetch.json"


# ---------------------------------------------------------------------------
# Env / proxy
# ---------------------------------------------------------------------------

def _load_env():
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

_load_env()


_proxy_status_printed = False


def _get_proxies():
    """
    Returns a requests-compatible proxies dict using the project's existing
    Webshare rotating residential proxy credentials, or None for a direct
    connection. Mirrors transcript_fetcher.get_ytt_api()'s fallback pattern —
    one proxy setup serving multiple consumers.
    """
    global _proxy_status_printed

    username = os.getenv("WEBSHARE_PROXY_USERNAME", "").strip()
    password = os.getenv("WEBSHARE_PROXY_PASSWORD", "").strip()

    if username and password:
        if not _proxy_status_printed:
            print("[PROXY] Trend scanner using Webshare rotating residential proxies.")
            _proxy_status_printed = True
        proxy_url = f"http://{username}:{password}@p.webshare.io:80"
        return {"http": proxy_url, "https": proxy_url}

    if not _proxy_status_printed:
        print("[PROXY] Trend scanner: no proxy configured — using direct connection.")
        _proxy_status_printed = True
    return None


# ---------------------------------------------------------------------------
# HTTP helper with 429 handling (retry-once, per CLAUDE.md rate-limit rule)
# ---------------------------------------------------------------------------

def _get(url, headers=None, timeout=15):
    """
    GET with one retry-after-pause on HTTP 429. Returns the Response, or
    raises on persistent failure / non-429 errors (caller handles + logs).
    """
    proxies = _get_proxies()
    resp = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)

    if resp.status_code == 429:
        print(f"[RATE] 429 from {url} — pausing {RATE_LIMIT_PAUSE}s before one retry...")
        time.sleep(RATE_LIMIT_PAUSE)
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)

    resp.raise_for_status()
    return resp


def _get_direct_first(url, headers=None, timeout=15):
    """
    GET a public endpoint DIRECTLY (no proxy) first. Only on a 403/429 does it
    pause and retry once through the proxy. This is the Spiceworks ban-resistance
    stance: a stable IP making a low-frequency, honest request looks like a
    normal feed reader; rotating residential IPs can read as more evasive. Direct
    is the polite default; the proxy is the fallback if the IP ever gets limited.
    """
    resp = requests.get(url, headers=headers, proxies=None, timeout=timeout)
    if resp.status_code in (403, 429):
        print(f"[RATE] {resp.status_code} from {url} (direct) — pausing "
              f"{RATE_LIMIT_PAUSE}s, retrying once via proxy...")
        time.sleep(RATE_LIMIT_PAUSE)
        resp = requests.get(url, headers=headers, proxies=_get_proxies(), timeout=timeout)
    resp.raise_for_status()
    return resp


# ---------------------------------------------------------------------------
# Reddit — public read-only JSON endpoints
# ---------------------------------------------------------------------------

# Reddit 403s its public *.json endpoints (OAuth-gated since ~2024) but still
# serves Atom RSS at /r/<sub>/top/.rss — our read-only, no-key access path. A
# browser User-Agent is required (Reddit blocks bot-like UAs even on RSS).
REDDIT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
_ATOM = "{http://www.w3.org/2005/Atom}"


def _fetch_subreddit(name, limit=10):
    """
    Fetch top posts from a subreddit via its public Atom RSS feed (read-only,
    no login/API key). Reddit's *.json endpoints return 403 now; the /top/.rss
    feed is still open. Returns a list of candidate dicts, or [] on failure.
    """
    url = f"https://www.reddit.com/r/{name}/top/.rss?t=day&limit={limit}"
    headers = {"User-Agent": REDDIT_UA}

    try:
        resp = _get_direct_first(url, headers=headers)
        root = ET.fromstring(resp.content)
    except Exception as e:
        print(f"[WARN] Reddit fetch failed for r/{name}: {e}")
        return []

    candidates = []
    for entry in root.iter(f"{_ATOM}entry"):
        title_el = entry.find(f"{_ATOM}title")
        title = (title_el.text or "").strip() if title_el is not None else ""
        if not title:
            continue
        link_el = entry.find(f"{_ATOM}link")
        link = link_el.get("href") if link_el is not None else None
        content_el = entry.find(f"{_ATOM}content")
        summary = ""
        if content_el is not None and content_el.text:
            summary = re.sub(r"<[^>]+>", " ", content_el.text)        # strip HTML
            summary = re.sub(r"\s+", " ", summary).strip()[:500]
        candidates.append({
            "title": title,
            "summary": summary,
            "source": f"reddit:r/{name}",
            "url": link,
        })
        if len(candidates) >= limit:
            break
    return candidates


def scan_reddit():
    """
    Scan all curated subreddits for candidate topics, with a randomized
    pause between each request. Returns a flat list of candidate dicts.
    """
    all_candidates = []
    for i, name in enumerate(SUBREDDITS):
        print(f"[SCAN] r/{name} ...", end=" ", flush=True)
        found = _fetch_subreddit(name)
        all_candidates.extend(found)
        print(f"{len(found)} candidate(s)")

        if i < len(SUBREDDITS) - 1:
            delay = random.uniform(*REDDIT_PAUSE)
            time.sleep(delay)

    return all_candidates


# ---------------------------------------------------------------------------
# Spiceworks (Discourse) — public /tag/<slug>.json, direct-first/proxy-fallback
# ---------------------------------------------------------------------------

def _fetch_spiceworks_tag(slug, limit=10):
    """
    Fetch recent topics for one Spiceworks tag via the public Discourse JSON
    endpoint (no login/API key). Carries engagement metrics (posts, views) into
    the summary so relevance_scorer sees the same signal it uses elsewhere.
    Returns a list of candidate dicts, or [] on failure.
    """
    url = f"{SPICEWORKS_BASE}/tag/{slug}.json"
    headers = {"User-Agent": USER_AGENT}

    try:
        resp = _get_direct_first(url, headers=headers)
        data = resp.json()
    except Exception as e:
        print(f"[WARN] Spiceworks fetch failed for tag '{slug}': {e}")
        return []

    candidates = []
    for topic in (data.get("topic_list", {}) or {}).get("topics", [])[:limit]:
        title = (topic.get("title") or "").strip()
        if not title:
            continue
        tid = topic.get("id")
        tslug = topic.get("slug")
        topic_url = f"{SPICEWORKS_BASE}/t/{tslug}/{tid}" if tid and tslug else None
        posts = topic.get("posts_count")
        views = topic.get("views")
        candidates.append({
            "title": title,
            "summary": f"Spiceworks discussion tagged #{slug} — {posts} posts, {views} views.",
            "source": f"spiceworks:{slug}",
            "url": topic_url,
        })
    return candidates


def scan_spiceworks():
    """
    Scan the curated Spiceworks tags for candidate topics, with a randomized
    pause between each request. Returns a flat list of candidate dicts.
    """
    all_candidates = []
    for i, slug in enumerate(SPICEWORKS_TAGS):
        print(f"[SCAN] spiceworks #{slug} ...", end=" ", flush=True)
        found = _fetch_spiceworks_tag(slug)
        all_candidates.extend(found)
        print(f"{len(found)} candidate(s)")

        if i < len(SPICEWORKS_TAGS) - 1:
            time.sleep(random.uniform(*SPICEWORKS_PAUSE))

    return all_candidates


# ---------------------------------------------------------------------------
# RSS — curated feed list, conditional GET to avoid re-fetching unchanged feeds
# ---------------------------------------------------------------------------

def _load_last_fetch_times():
    if not os.path.exists(_LAST_FETCH_LOG):
        return {}
    try:
        import json
        with open(_LAST_FETCH_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_last_fetch_times(times):
    import json
    os.makedirs("logs", exist_ok=True)
    with open(_LAST_FETCH_LOG, "w", encoding="utf-8") as f:
        json.dump(times, f, indent=2)


def _fetch_rss_feed(feed, last_fetch_iso=None):
    """
    Fetch one RSS feed with conditional GET (If-Modified-Since). Returns
    (candidates, new_last_modified_header_or_None). A 304 response yields
    ([], None) — nothing changed, nothing to re-process.
    """
    headers = {"User-Agent": USER_AGENT}
    if last_fetch_iso:
        try:
            dt = datetime.fromisoformat(last_fetch_iso)
            headers["If-Modified-Since"] = format_datetime(dt, usegmt=True)
        except ValueError:
            pass

    try:
        proxies = _get_proxies()
        resp = requests.get(feed["url"], headers=headers, proxies=proxies, timeout=15)
        if resp.status_code == 304:
            return [], None
        if resp.status_code == 429:
            print(f"[RATE] 429 from {feed['name']} — pausing {RATE_LIMIT_PAUSE}s before one retry...")
            time.sleep(RATE_LIMIT_PAUSE)
            resp = requests.get(feed["url"], headers=headers, proxies=proxies, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"[WARN] RSS fetch failed for {feed['name']}: {e}")
        return [], None

    candidates = []
    try:
        root = ET.fromstring(resp.content)
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            if not title:
                continue
            description = (item.findtext("description") or "")[:500].strip()
            link = (item.findtext("link") or "").strip() or None
            candidates.append({
                "title": title,
                "summary": description,
                "source": f"rss:{feed['name']}",
                "url": link,
            })
    except ET.ParseError as e:
        print(f"[WARN] RSS parse failed for {feed['name']}: {e}")
        return [], None

    new_last_modified = resp.headers.get("Last-Modified")
    return candidates[:10], new_last_modified


def scan_rss():
    """
    Scan all curated RSS feeds for candidate topics, with conditional GET
    and a randomized pause between each request. Returns a flat list of
    candidate dicts (feeds returning 304 contribute nothing — by design).
    """
    last_fetch = _load_last_fetch_times()
    all_candidates = []

    for i, feed in enumerate(RSS_FEEDS):
        print(f"[SCAN] {feed['name']} ...", end=" ", flush=True)
        found, new_last_modified = _fetch_rss_feed(feed, last_fetch.get(feed["name"]))
        all_candidates.extend(found)

        if new_last_modified:
            last_fetch[feed["name"]] = datetime.now(timezone.utc).isoformat()
        print(f"{len(found)} candidate(s)" + (" (not modified)" if not found and feed["name"] in last_fetch else ""))

        if i < len(RSS_FEEDS) - 1:
            delay = random.uniform(*RSS_PAUSE)
            time.sleep(delay)

    _save_last_fetch_times(last_fetch)
    return all_candidates


# ---------------------------------------------------------------------------
# GitHub — public Search API, unauthenticated, biased toward recently-created
# repos (catching new weekend-project builds, not established repos updating)
# ---------------------------------------------------------------------------

def _github_headers():
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json",
    }
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _fetch_github_term(term, limit=10):
    """
    Search GitHub repositories for one term, restricted to repos created in
    the last GITHUB_LOOKBACK_DAYS days, sorted by star count. Returns a list
    of candidate dicts, or [] on failure.
    """
    # Quoted exact-phrase match -- unquoted, GitHub's search treats a multi-word
    # term as an AND of individual words, so "Jarvis build" also matches any
    # repo containing the generic word "build" anywhere (confirmed empirically:
    # unquoted returned 3,013 total matches, mostly irrelevant noise like
    # "Awesome-Agent-Engineering"; quoted returned 35, all genuinely on-topic
    # Jarvis-style builds). Precision on the exact phrase is the whole point of
    # this scanner -- catching the SAME specific idea recurring, not general
    # keyword volume.
    since = (datetime.now(timezone.utc) - timedelta(days=GITHUB_LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    query = f'"{term}" in:name,description,readme created:>{since}'
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": limit}

    try:
        resp = requests.get(
            GITHUB_SEARCH_URL,
            params=params,
            headers=_github_headers(),
            proxies=_get_proxies(),
            timeout=15,
        )
        if resp.status_code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0":
            print(f"[RATE] GitHub search rate limit hit for '{term}' — skipping this term.")
            return []
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[WARN] GitHub search failed for '{term}': {e}")
        return []

    candidates = []
    for repo in data.get("items", [])[:limit]:
        name = repo.get("full_name") or repo.get("name") or ""
        if not name:
            continue
        description = (repo.get("description") or "").strip()
        stars = repo.get("stargazers_count", 0)
        created = (repo.get("created_at") or "")[:10]
        candidates.append({
            "title": name,
            "summary": f"GitHub repo (matched \"{term}\", {stars} stars, created {created}): {description}"[:500],
            "source": f"github:{term}",
            "url": repo.get("html_url"),
        })
    return candidates


def scan_github():
    """
    Search GitHub for each curated BUILD_SIGNAL_TERMS entry, restricted to
    recently-created repos, with a randomized pause between each request
    (GitHub's unauthenticated search API caps at 10 req/min). Returns a flat
    list of candidate dicts.
    """
    all_candidates = []
    for i, term in enumerate(BUILD_SIGNAL_TERMS):
        print(f"[SCAN] github \"{term}\" ...", end=" ", flush=True)
        found = _fetch_github_term(term)
        all_candidates.extend(found)
        print(f"{len(found)} candidate(s)")

        if i < len(BUILD_SIGNAL_TERMS) - 1:
            time.sleep(random.uniform(*GITHUB_PAUSE))

    return all_candidates


# ---------------------------------------------------------------------------
# Hacker News — Algolia public Search API, free, no key
# ---------------------------------------------------------------------------

def _fetch_hn_term(term, limit=10):
    """
    Search Hacker News stories for one term via Algolia's public API,
    restricted to stories posted in the last HN_LOOKBACK_DAYS days. Returns
    a list of candidate dicts, or [] on failure.
    """
    since_ts = int((datetime.now(timezone.utc) - timedelta(days=HN_LOOKBACK_DAYS)).timestamp())
    params = {
        "query": term,
        "tags": "story",
        "numericFilters": f"created_at_i>{since_ts}",
        "hitsPerPage": limit,
    }

    try:
        resp = requests.get(
            HN_ALGOLIA_SEARCH_URL,
            params=params,
            headers={"User-Agent": USER_AGENT},
            proxies=_get_proxies(),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[WARN] Hacker News search failed for '{term}': {e}")
        return []

    candidates = []
    for hit in data.get("hits", [])[:limit]:
        title = (hit.get("title") or "").strip()
        if not title:
            continue
        points = hit.get("points", 0)
        num_comments = hit.get("num_comments", 0)
        object_id = hit.get("objectID")
        hn_url = f"https://news.ycombinator.com/item?id={object_id}" if object_id else None
        candidates.append({
            "title": title,
            "summary": f"Hacker News story (matched \"{term}\", {points} points, {num_comments} comments).",
            "source": f"hackernews:{term}",
            "url": hit.get("url") or hn_url,
        })
    return candidates


def scan_hackernews():
    """
    Search Hacker News for each curated BUILD_SIGNAL_TERMS entry via the
    Algolia API, with a randomized pause between each request. Returns a
    flat list of candidate dicts.
    """
    all_candidates = []
    for i, term in enumerate(BUILD_SIGNAL_TERMS):
        print(f"[SCAN] hackernews \"{term}\" ...", end=" ", flush=True)
        found = _fetch_hn_term(term)
        all_candidates.extend(found)
        print(f"{len(found)} candidate(s)")

        if i < len(BUILD_SIGNAL_TERMS) - 1:
            time.sleep(random.uniform(*HN_PAUSE))

    return all_candidates


# ---------------------------------------------------------------------------
# Knowledge base — recurring themes, zero new outbound calls
# ---------------------------------------------------------------------------

def scan_knowledge_base(limit=5):
    """
    Surface recurring themes from the existing transcript knowledge base as
    candidate topics. Makes no outbound network calls — reads index.json only.
    """
    try:
        from src.knowledge_base.indexer import load_index
        index = load_index()
    except Exception as e:
        print(f"[WARN] Knowledge base scan failed: {e}")
        return []

    candidates = []
    for group_name, group_data in index.get("groups", {}).items():
        for channel_name, channel_data in group_data.get("channels", {}).items():
            for entry in channel_data.get("transcripts", [])[:limit]:
                candidates.append({
                    "title": entry.get("title", ""),
                    "summary": f"Recurring theme from your knowledge base ({group_name} / {channel_name}).",
                    "source": "knowledge_base",
                    "url": None,
                })
    return candidates[:limit * 2]


# ---------------------------------------------------------------------------
# Combined scan
# ---------------------------------------------------------------------------

def gather_candidates():
    """
    Run all scans and return one combined list of candidate dicts, ready to
    hand to relevance_scorer.score_topics().
    """
    candidates = []
    candidates.extend(scan_reddit())
    candidates.extend(scan_spiceworks())
    candidates.extend(scan_rss())
    candidates.extend(scan_github())
    candidates.extend(scan_hackernews())
    candidates.extend(scan_knowledge_base())
    return candidates
