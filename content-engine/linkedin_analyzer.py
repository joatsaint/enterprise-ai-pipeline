"""
LinkedIn Competitor Analyzer
Parses OCR-converted LinkedIn post activity markdown files,
extracts post data, and runs Claude analysis to produce
competitor intelligence reports.

Usage:
  python linkedin_analyzer.py                    # analyze all creators
  python linkedin_analyzer.py --creator duncan   # one creator only
  python linkedin_analyzer.py --no-claude        # parse only, skip Claude API
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DOCS_BASE = Path(__file__).parent.parent / "docs" / "LinkedIn Content Creators Pages to Study"


def _find_file(folder: Path, glob_pattern: str) -> Path | None:
    """Find a file matching glob_pattern in folder, handling emoji filenames safely."""
    try:
        matches = list(folder.glob(glob_pattern))
        return matches[0] if matches else None
    except Exception:
        return None


def _sabrina_md_path() -> Path:
    """Locate Sabrina's MD file dynamically (filename contains emoji)."""
    found = _find_file(DOCS_BASE, "Post Activity _ Sabrina*LinkedIn.md")
    if found:
        return found
    # Fallback: scan directory
    import os
    for name in os.listdir(str(DOCS_BASE)):
        if "Sabrina" in name and name.endswith(".md"):
            return DOCS_BASE / name
    return DOCS_BASE / "Post Activity _ Sabrina Ramonov _ LinkedIn.md"


CREATORS = {
    "duncan": {
        "name": "Duncan Rogoff",
        "md_file": DOCS_BASE / "Post_Activity _ Duncan Rogoff _ LinkedIn" / "1ffc70b820e54662b32a4733bfcb48f8_md_full.md",
        "profile": "Founder @ The Build Room. Ex-Apple, PlayStation, Nissan. 15,605 followers.",
        "niche": "Claude Code / AI content creation systems",
    },
    "sandra": {
        "name": "Sandra Pellumbi",
        "md_file": DOCS_BASE / "Post Activity _ Sandra Pellumbi _ LinkedIn" / "5164096769a448f5873ae89245bb4710_md_full.md",
        "profile": "Co-Founder & CEO. AI-trained EAs + operational infrastructure for founders.",
        "niche": "AI operations / founder productivity",
    },
    "sabrina": {
        "name": "Sabrina Ramonov",
        "md_file": _sabrina_md_path(),
        "profile": "#1 AI Educator, 2.5M+ followers, 33M+ monthly views. Founder & CEO of Blotato (AI Content Engine). Forbes 30 Under 30.",
        "niche": "AI for entrepreneurs / AI content engines / agent-native business",
    },
}

OUTPUT_DIR = Path(__file__).parent / "linkedin-intelligence"


# ── Post parsing ──────────────────────────────────────────────────────────────

def clean_text(raw: str) -> str:
    """Strip OCR artifacts, image tags, LaTeX, and nav noise from post text."""
    text = raw
    # Remove markdown image tags
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    # Remove standalone "Image" tokens (Sabrina's format uses Image instead of ![](…))
    text = re.sub(r"\bImage\b", "", text)
    # Remove LaTeX math blocks
    text = re.sub(r"\$\$.*?\$\$", "", text, flags=re.DOTALL)
    text = re.sub(r"\$.*?\$", "", text)
    # Convert arrow artifacts to →
    text = re.sub(r"\$\\rightarrow\$", "→", text)
    text = re.sub(r"\\rightarrow", "→", text)
    # Remove underline markup
    text = re.sub(r"\\underline\{([^}]+)\}", r"\1", text)
    # Remove bullet/circle number OCR artifacts (①②③④⑤)
    text = re.sub(r"[①②③④⑤⑥⑦⑧⑨⑩]", "", text)
    # Remove media player UI noise (Sabrina's video posts)
    text = re.sub(r"Media player modal window.*?$", "", text, flags=re.DOTALL | re.MULTILINE)
    text = re.sub(r"Stream Type LIVE.*?$", "", text, flags=re.DOTALL | re.MULTILINE)
    text = re.sub(r"Playback speed.*?$", "", text, flags=re.DOTALL | re.MULTILINE)
    text = re.sub(r"Remaining time.*?$", "", text, flags=re.MULTILINE)
    text = re.sub(r"00:00\s*\n", "", text)
    text = re.sub(r"Loaded:\s*[\d.]+%", "", text)
    # Remove engagement UI lines (■19 comments■11 reposts Like▼Comment Repost Send)
    text = re.sub(r"[■▼]?\d+\s*(?:comments?|reposts?|likes?)[■▼\s]*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bLike[▼]?\s*Comment\s*Repost\s*Send\b", "", text)
    # Strip nav/UI fragments
    ui_noise = [
        r"Activate to view larger image,?",
        r"No alternative text description for this image",
        r"has finished loading",
        r"Visit my website(?: my website)?",
        r"Follow Message",
        r"All activity",
        r"Posts Comments Videos Images More",
        r"Loaded \d+ Posts posts",
        r"\d+\s*new notifications",
        r"For Busines",
        r"Adverti",
        r"My Network",
        r"Messaging",
        r"Play\s*Play",
        r"Media is loading",
        r"Close\s*\nin\s*",
    ]
    for pattern in ui_noise:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    # Remove lines that are just image hash paths or navigation remnants
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        line = line.strip()
        if len(line) < 3:
            continue
        if re.match(r"^[•●.·\s◦○▪▸]+$", line):
            continue
        # Skip lines that look like pure URL artifacts
        if re.match(r"^https?://\S+$", line) and len(line) < 60:
            continue
        cleaned.append(line)
    result = "\n".join(cleaned)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def extract_engagement(raw: str) -> dict:
    """Extract comment and repost counts from raw post text where available."""
    comments = None
    reposts = None
    m = re.search(r"■(\d+)\s*comments?", raw, re.IGNORECASE)
    if m:
        comments = int(m.group(1))
    m = re.search(r"■(\d+)\s*reposts?", raw, re.IGNORECASE)
    if m:
        reposts = int(m.group(1))
    return {"comments": comments, "reposts": reposts}


def classify_post_type(raw: str) -> str:
    """Detect post type from raw OCR text."""
    if re.search(r"reposted this", raw, re.IGNORECASE):
        return "repost"
    if re.search(r"Activate to view larger image", raw, re.IGNORECASE):
        return "carousel"
    if re.search(r"Media is loading|Stream Type LIVE|Playback speed", raw, re.IGNORECASE):
        return "video"
    return "text"


def extract_dm_keyword(text: str) -> str | None:
    """Extract DM funnel keyword from 'Comment [WORD]' patterns."""
    patterns = [
        r'[Cc]omment\s+["“”‘’]?([A-Z]{2,})["“”‘’]?',
        r'[Cc]omment\s*"([A-Z]{2,})"',
        r'[Cc]omment\s*“([A-Z]{2,})”',
    ]
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            return m.group(1)
    return None


def extract_hashtags(text: str) -> list[str]:
    return re.findall(r"#\w+", text)


def extract_hook(text: str) -> str:
    """Return the first meaningful non-empty line as the hook."""
    for line in text.splitlines():
        line = line.strip()
        if len(line) > 20 and not line.startswith("→") and not line.startswith("#"):
            return line[:200]
    return text[:200] if text else ""


def parse_md_file(md_path: Path) -> list[dict]:
    """Parse an _md_full.md OCR file into a list of post dicts."""
    with open(str(md_path), "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Split on "Feed post number N" markers (handles ". Feed", "• Feed", "Feed" variants)
    parts = re.split(r"[•.\s]*\bFeed post number\s+(\d+)\b", content)

    posts = []
    # parts: [preamble, num, text, num, text, ...]
    i = 1
    while i < len(parts) - 1:
        post_num = int(parts[i])
        raw_text = parts[i + 1]
        i += 2

        post_type = classify_post_type(raw_text)
        engagement = extract_engagement(raw_text)
        clean = clean_text(raw_text)
        dm_keyword = extract_dm_keyword(clean)
        hashtags = extract_hashtags(clean)
        hook = extract_hook(clean)

        # Skip if essentially empty after cleaning
        if len(clean) < 50:
            continue

        posts.append({
            "post_num": post_num,
            "type": post_type,
            "hook": hook,
            "dm_keyword": dm_keyword,
            "hashtags": hashtags,
            "word_count": len(clean.split()),
            "comments": engagement["comments"],
            "reposts": engagement["reposts"],
            "text": clean,
        })

    return posts


# ── Stats computation ─────────────────────────────────────────────────────────

def compute_stats(posts: list[dict]) -> dict:
    total = len(posts)
    type_counts = {}
    dm_keywords = []
    all_hashtags = []
    hook_lengths = []

    for p in posts:
        type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1
        if p["dm_keyword"]:
            dm_keywords.append(p["dm_keyword"])
        all_hashtags.extend(p["hashtags"])
        hook_lengths.append(len(p["hook"]))

    hashtag_freq = {}
    for h in all_hashtags:
        hashtag_freq[h] = hashtag_freq.get(h, 0) + 1
    top_hashtags = sorted(hashtag_freq.items(), key=lambda x: -x[1])[:20]

    dm_freq = {}
    for k in dm_keywords:
        dm_freq[k] = dm_freq.get(k, 0) + 1
    top_dm = sorted(dm_freq.items(), key=lambda x: -x[1])[:15]

    return {
        "total_posts": total,
        "type_breakdown": type_counts,
        "dm_funnel_rate": f"{len(dm_keywords) / total * 100:.1f}%" if total else "0%",
        "top_dm_keywords": top_dm,
        "top_hashtags": top_hashtags,
        "avg_hook_length": int(sum(hook_lengths) / len(hook_lengths)) if hook_lengths else 0,
        "posts_with_hashtags": sum(1 for p in posts if p["hashtags"]),
    }


# ── Claude analysis ───────────────────────────────────────────────────────────

def call_claude(prompt: str, model: str = "claude-haiku-4-5-20251001") -> str:
    try:
        import anthropic
    except ImportError:
        return "[anthropic not installed — skipping Claude analysis]"

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break

    if not api_key:
        return "[ANTHROPIC_API_KEY not found — skipping Claude analysis]"

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def build_analysis_prompt(creator: dict, posts: list[dict], stats: dict) -> str:
    post_sample = posts[:80]
    posts_text = ""
    for p in post_sample:
        posts_text += f"\n---\nPost #{p['post_num']} [{p['type'].upper()}] | DM: {p['dm_keyword'] or 'none'} | Words: {p['word_count']}\n"
        posts_text += f"HOOK: {p['hook']}\n"
        posts_text += p["text"][:600] + ("..." if len(p["text"]) > 600 else "")
        posts_text += "\n"

    return f"""You are a LinkedIn content strategy analyst. Analyze this creator's posting behavior to extract patterns that a competitor can learn from.

CREATOR: {creator['name']}
PROFILE: {creator['profile']}
NICHE: {creator['niche']}

STATS:
- Total posts analyzed: {stats['total_posts']}
- Post type breakdown: {stats['type_breakdown']}
- DM funnel rate: {stats['dm_funnel_rate']} of posts use a DM CTA
- Top DM keywords: {[k for k,_ in stats['top_dm_keywords'][:10]]}
- Posts using hashtags: {stats['posts_with_hashtags']} of {stats['total_posts']}
- Top hashtags: {[h for h,_ in stats['top_hashtags'][:10]]}
- Average hook length: {stats['avg_hook_length']} chars

POSTS (sample of up to 80):
{posts_text}

Produce a structured intelligence report with these sections:

## Content Strategy Patterns
What content types dominate? What formats work best? How do they structure posts?

## Hook Formula Analysis
What patterns make their hooks work? Give 5 specific hook templates extracted from the data.

## DM Funnel Mechanics
How do they use comment-to-DM? What keywords do they use and why? What is the CTA structure?

## Topic Clusters
What are the 5-7 core topic buckets this creator returns to? What is their content "universe"?

## Posting Cadence Signals
What can you infer about their posting frequency and timing from the data?

## What Randy Can Steal
5 specific, actionable tactics Randy (sysadmin AI authority, targeting IT pros 40-50s) can directly adapt — not generic advice, specific patterns from THIS creator's posts.

## What NOT to Copy
Tactics that work for this creator but would feel off for Randy's audience or brand.

Be specific. Quote hooks and phrases from the posts where they illustrate a pattern."""


def build_synthesis_prompt(creator_reports: dict) -> str:
    reports_text = ""
    for slug, report in creator_reports.items():
        reports_text += f"\n\n=== {slug.upper()} ANALYSIS ===\n{report[:2500]}"

    creator_names = ", ".join(c.title() for c in creator_reports.keys())

    return f"""You are a LinkedIn content strategist. You've just read analysis reports for {len(creator_reports)} high-performing LinkedIn creators: {creator_names}. Now synthesize the cross-creator patterns.

{reports_text}

RANDY'S CONTEXT:
- Target: IT/sysadmin professionals, 40-50s, skeptical of AI hype, enterprise environments
- Goal: Become a LinkedIn authority → build trust → sell a field manual on AI for sysadmins
- Current: Building audience, 0→authority journey
- Voice: Blunt, experienced, peer-to-peer, no BS

Produce a CROSS-CREATOR SYNTHESIS with:

## Universal Patterns (All Creators Use)
Tactics that appear across ALL creators — these are bedrock fundamentals, not format flukes.

## What Sabrina Does Differently
Sabrina has 2.5M followers and very different tactics. What does she do that Duncan and Sandra don't? What can Randy learn from the contrast?

## The DM Funnel Blueprint
How creators architect CTAs and funnels. Duncan uses keyword comment-to-DM. Sabrina uses community links. Sandra uses waitlists. Give Randy a fill-in-the-blank template that fits his audience.

## Hook Formulas That Dominate
The 3-5 hook structures that appear across multiple creators with the highest signal.

## Content Cadence Model
What posting rhythm can Randy infer from all three creators' volumes and types?

## Randy's 30-Day LinkedIn Playbook
A concrete 4-week content plan Randy can execute NOW based on what's working across all three creators — adapted for the sysadmin AI niche. Include:
- Post types per week (text vs carousel vs video vs repost)
- 3 specific post ideas per week with hooks written for sysadmin audience
- CTA/funnel suggestion for his audience
- Which hashtags to use or avoid"""


# ── Report writing ────────────────────────────────────────────────────────────

def write_creator_report(slug: str, creator: dict, posts: list[dict], stats: dict, analysis: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"{slug}-analysis.md"

    dm_table = "\n".join(
        f"| {k} | {c} |" for k, c in stats["top_dm_keywords"]
    )
    hashtag_table = "\n".join(
        f"| {h} | {c} |" for h, c in stats["top_hashtags"]
    )

    sample_hooks = [p["hook"] for p in posts[:20] if p["hook"]][:10]
    hooks_text = "\n".join(f"- {h}" for h in sample_hooks)

    content = f"""# LinkedIn Analysis: {creator['name']}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Source:** OCR-parsed post activity feed

---

## Profile
{creator['profile']}
**Niche:** {creator['niche']}

---

## Stats at a Glance

| Metric | Value |
|--------|-------|
| Total posts analyzed | {stats['total_posts']} |
| Text posts | {stats['type_breakdown'].get('text', 0)} |
| Carousel posts | {stats['type_breakdown'].get('carousel', 0)} |
| Reposts | {stats['type_breakdown'].get('repost', 0)} |
| DM funnel rate | {stats['dm_funnel_rate']} |
| Posts with hashtags | {stats['posts_with_hashtags']} |
| Avg hook length | {stats['avg_hook_length']} chars |

---

## Top DM Keywords

| Keyword | Occurrences |
|---------|-------------|
{dm_table}

---

## Top Hashtags

| Hashtag | Count |
|---------|-------|
{hashtag_table}

---

## Sample Hooks (First 10)

{hooks_text}

---

## Claude Analysis

{analysis}

---

## Raw Post Index

| # | Type | DM Keyword | Comments | Reposts | Words | Hook |
|---|------|-----------|----------|---------|-------|------|
"""
    for p in posts[:50]:
        hook_short = p["hook"][:60].replace("|", "—")
        comments = p.get("comments") or "—"
        reposts = p.get("reposts") or "—"
        content += f"| {p['post_num']} | {p['type']} | {p['dm_keyword'] or '—'} | {comments} | {reposts} | {p['word_count']} | {hook_short} |\n"

    if len(posts) > 50:
        content += f"\n*...and {len(posts) - 50} more posts*\n"

    with open(str(out_path), "w", encoding="utf-8") as f:
        f.write(content)

    return out_path


def write_synthesis_report(synthesis: str, creator_names: list[str] | None = None) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "cross-creator-synthesis.md"
    names_str = ", ".join(creator_names) if creator_names else "Duncan Rogoff, Sandra Pellumbi, Sabrina Ramonov"

    content = f"""# Cross-Creator LinkedIn Synthesis
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Creators analyzed:** {names_str}

---

{synthesis}
"""
    with open(str(out_path), "w", encoding="utf-8") as f:
        f.write(content)

    return out_path


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="LinkedIn competitor analyzer")
    parser.add_argument("--creator", choices=list(CREATORS.keys()), help="Analyze one creator only")
    parser.add_argument("--no-claude", action="store_true", help="Skip Claude API calls")
    args = parser.parse_args()

    targets = {args.creator: CREATORS[args.creator]} if args.creator else CREATORS

    print("━" * 48)
    print(" LinkedIn Competitor Analyzer")
    print("━" * 48)

    creator_analyses = {}

    for slug, creator in targets.items():
        md_path = creator["md_file"]
        print(f"\n[{slug}] Parsing {md_path.name}...")

        if not md_path.exists():
            print(f"  [warn] File not found: {md_path}")
            continue

        posts = parse_md_file(md_path)
        stats = compute_stats(posts)

        print(f"  [ok] {stats['total_posts']} posts parsed")
        print(f"       Types: {stats['type_breakdown']}")
        print(f"       DM funnel rate: {stats['dm_funnel_rate']}")
        print(f"       Top DM keywords: {[k for k, _ in stats['top_dm_keywords'][:5]]}")

        analysis = ""
        if not args.no_claude:
            print(f"  [claude] Analyzing {slug}...")
            prompt = build_analysis_prompt(creator, posts, stats)
            analysis = call_claude(prompt)
            print(f"  [ok] Analysis complete ({len(analysis)} chars)")
        else:
            analysis = "*Claude analysis skipped (--no-claude flag)*"

        out_path = write_creator_report(slug, creator, posts, stats, analysis)
        print(f"  [saved] {out_path}")

        creator_analyses[slug] = analysis

    analyzed_names = [CREATORS[s]["name"] for s in creator_analyses]

    if not args.no_claude and len(creator_analyses) > 1:
        print(f"\n[synthesis] Running cross-creator synthesis ({len(creator_analyses)} creators)...")
        synthesis_prompt = build_synthesis_prompt(creator_analyses)
        synthesis = call_claude(synthesis_prompt, model="claude-haiku-4-5-20251001")
        out_path = write_synthesis_report(synthesis, analyzed_names)
        print(f"  [saved] {out_path}")
    elif len(creator_analyses) > 1:
        synthesis = "*Synthesis skipped (--no-claude flag)*"
        out_path = write_synthesis_report(synthesis, analyzed_names)
        print(f"\n[synthesis] Skipped — {out_path}")

    print("\n" + "━" * 48)
    print(f" Done — reports in content-engine/linkedin-intelligence/")
    print("━" * 48)


if __name__ == "__main__":
    main()
