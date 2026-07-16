"""
ICP Hangouts Finder — mine Spiceworks threads for the external places your ICP
sends each other (LinkedIn, YouTube channels, subreddits, Discords, blogs, tools),
with a click-weighted popularity signal, so you verify where to show up instead
of guessing.

How: Discourse records outbound links per post (post.link_counts = url, clicks,
internal). We read what the community actually recommends. This is a one-time /
occasional RESEARCH crawl — NOT the daily trend scan — so it fetches one topic at
a time, paced + direct-first, and caches each topic so re-runs are free.

  python -m src.main spiceworks-hangouts [--per-tag N]   # default 12 topics/tag

Out: content-engine/research/icp_research/spiceworks_hangouts.md  (gitignored)
"""
import collections
import json
import os
import random
import re
import time
from datetime import datetime
from urllib.parse import urlparse

from src.trend_finder.source_scanner import (
    _get_direct_first,
    USER_AGENT,
    SPICEWORKS_BASE,
    SPICEWORKS_TAGS,
    SPICEWORKS_PAUSE,
)
from src.utils.atomic import atomic_write_json, atomic_write_text

CACHE_DIR = os.path.join(".cache", "spiceworks_topics")
OUT_DIR = os.path.join("content-engine", "research", "icp_research")
OUT_PATH = os.path.join(OUT_DIR, "spiceworks_hangouts.md")

# domain substring -> human platform label (ordered: first match wins)
PLATFORMS = [
    ("linkedin.", "LinkedIn"),
    ("youtube.", "YouTube"), ("youtu.be", "YouTube"),
    ("reddit.", "Reddit"),
    ("discord.", "Discord"),
    ("github.", "GitHub"), ("gitlab.", "GitLab"),
    ("stackoverflow.", "Stack Overflow"), ("stackexchange.", "Stack Exchange"),
    ("serverfault.", "ServerFault"), ("superuser.", "SuperUser"),
    ("learn.microsoft.", "Microsoft Learn/Docs"), ("docs.microsoft.", "Microsoft Learn/Docs"),
    ("medium.", "Medium"), ("substack.", "Substack"), ("dev.to", "dev.to"),
    ("twitter.", "X/Twitter"), ("x.com", "X/Twitter"),
    ("facebook.", "Facebook"), ("news.ycombinator", "Hacker News"),
]


def _domain(url):
    try:
        d = urlparse(url).netloc.lower()
        return d[4:] if d.startswith("www.") else d
    except Exception:
        return ""


def classify(url):
    """Return (platform_label_or_None, domain, specific) — specific is a channel/
    subreddit/invite handle when we can extract one."""
    dom = _domain(url)
    label = next((lab for sub, lab in PLATFORMS if sub in dom), None)
    specific = None
    if label == "YouTube":
        m = re.search(r"@[\w.-]+", url) or re.search(r"/(?:channel|c|user)/[\w-]+", url)
        specific = m.group(0) if m else None
    elif label == "Reddit":
        m = re.search(r"/r/([\w-]+)", url)
        specific = "r/" + m.group(1) if m else None
    elif label == "Discord":
        m = re.search(r"discord\.gg/[\w-]+|/invite/[\w-]+", url)
        specific = m.group(0) if m else None
    return label, dom, specific


# --------------------------------------------------------------------------
# Fetch (paced, direct-first, cached)
# --------------------------------------------------------------------------
def _topic_ids(tag, limit):
    url = f"{SPICEWORKS_BASE}/tag/{tag}.json"
    data = _get_direct_first(url, headers={"User-Agent": USER_AGENT}).json()
    topics = (data.get("topic_list", {}) or {}).get("topics", [])
    return [t["id"] for t in topics[:limit] if t.get("id")]


def _topic_links(topic_id):
    """Return [{url, clicks}] of external links in a topic. Cached; only a cache
    MISS does a (paced) network fetch."""
    cpath = os.path.join(CACHE_DIR, f"{topic_id}.json")
    if os.path.exists(cpath):
        try:
            with open(cpath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    url = f"{SPICEWORKS_BASE}/t/{topic_id}.json"
    try:
        data = _get_direct_first(url, headers={"User-Agent": USER_AGENT}).json()
    except Exception as e:
        print(f"[WARN] topic {topic_id} fetch failed: {e}")
        return []

    links = []
    for post in (data.get("post_stream", {}) or {}).get("posts", []):
        for lc in (post.get("link_counts") or []):
            if lc.get("internal"):
                continue
            u = lc.get("url")
            if u:
                links.append({"url": u, "clicks": lc.get("clicks", 0) or 0})

    atomic_write_json(cpath, links)
    time.sleep(random.uniform(*SPICEWORKS_PAUSE))  # pace real fetches only
    return links


# --------------------------------------------------------------------------
# Aggregate
# --------------------------------------------------------------------------
def aggregate(link_rows):
    """Pure: given an iterable of {url, clicks}, return ranked hangout buckets."""
    plat_mentions, plat_clicks = collections.Counter(), collections.Counter()
    yt, subs, disc = collections.Counter(), collections.Counter(), collections.Counter()
    other_mentions, other_clicks = collections.Counter(), collections.Counter()

    for row in link_rows:
        url, clicks = row.get("url", ""), row.get("clicks", 0) or 0
        label, dom, specific = classify(url)
        # Drop blanks, internal Spiceworks links, and malformed "domains" that are
        # really link text (spaces / percent-encoding / no dot).
        if not dom or "." not in dom or "%" in dom or " " in dom or "spiceworks" in dom:
            continue
        if label:
            plat_mentions[label] += 1
            plat_clicks[label] += clicks
            if label == "YouTube" and specific:
                yt[specific] += 1
            elif label == "Reddit" and specific:
                subs[specific] += 1
            elif label == "Discord" and specific:
                disc[specific] += 1
        else:
            other_mentions[dom] += 1
            other_clicks[dom] += clicks

    return {
        "platforms": [(p, plat_mentions[p], plat_clicks[p])
                      for p in sorted(plat_mentions, key=lambda p: (plat_clicks[p], plat_mentions[p]), reverse=True)],
        "youtube": yt.most_common(15),
        "subreddits": subs.most_common(15),
        "discords": disc.most_common(15),
        "other": [(d, other_mentions[d], other_clicks[d])
                  for d in sorted(other_mentions, key=lambda d: (other_clicks[d], other_mentions[d]), reverse=True)][:25],
    }


def render_report(agg, topics_scanned, per_tag, tags):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# ICP Verified Hangouts — from Spiceworks",
        f"_Generated {now}. Mined {topics_scanned} threads ({per_tag}/tag) across: "
        f"{', '.join(tags)}._",
        "",
        "Where your ICP sends each other when solving problems, click-weighted. "
        "Focus your presence on the top platforms; research the named channels/subreddits.",
        "",
        "## Platforms (by clicks, then mentions)",
        "",
    ]
    for label, m, c in agg["platforms"]:
        lines.append(f"- **{label}** — {m} mentions / {c} clicks")
    if not agg["platforms"]:
        lines.append("- (none found — try a larger --per-tag)")

    lines += ["", "## YouTube channels recommended", ""]
    lines += [f"- {h} — {n}" for h, n in agg["youtube"]] or ["- (none surfaced yet)"]

    lines += ["", "## Subreddits recommended", ""]
    lines += [f"- {s} — {n}" for s, n in agg["subreddits"]] or ["- (none surfaced yet)"]

    lines += ["", "## Discord / invite links", ""]
    lines += [f"- {d} — {n}" for d, n in agg["discords"]] or ["- (none surfaced yet)"]

    lines += ["", "## Other domains shared (long tail — blogs, tools, vendors)", ""]
    for d, m, c in agg["other"]:
        lines.append(f"- {d} — {m} mentions / {c} clicks")

    return "\n".join(lines)


def run_hangouts(per_tag=12, tags=None):
    tags = tags or SPICEWORKS_TAGS
    print(f"[HANGOUTS] Mining {per_tag} topics/tag across {len(tags)} tags "
          f"(paced, direct-first, cached)...")
    all_links = []
    topics_scanned = 0
    for tag in tags:
        try:
            ids = _topic_ids(tag, per_tag)
        except Exception as e:
            print(f"[WARN] tag '{tag}' failed: {e}")
            continue
        print(f"[HANGOUTS] #{tag}: {len(ids)} topics")
        for tid in ids:
            all_links.extend(_topic_links(tid))
            topics_scanned += 1

    agg = aggregate(all_links)
    report = render_report(agg, topics_scanned, per_tag, tags)
    atomic_write_text(OUT_PATH, report)
    print(f"[HANGOUTS] {len(all_links)} external links from {topics_scanned} topics.")
    print(f"[HANGOUTS] Report: {OUT_PATH}")
    top = agg["platforms"][:5]
    if top:
        print("[HANGOUTS] Top platforms: " + ", ".join(f"{p} ({c} clicks)" for p, m, c in top))
    return agg
