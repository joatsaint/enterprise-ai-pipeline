#!/usr/bin/env python3
"""
performance_brief.py  .  content-engine/

Reads dashboard_state.json and writes performance_brief.md —
a summary of which topics and hook types are driving the most engagement.

The brief is injected into linkedin_atomizer.py via --brief flag
to inform the next article's topic and hook selection.

Usage
-----
  python performance_brief.py
  python performance_brief.py --out custom_brief.md
"""

import json, argparse
from pathlib import Path
from datetime import datetime

HERE       = Path(__file__).parent
STATE_FILE = HERE / "dashboard_state.json"
OUT_FILE   = HERE / "performance_brief.md"


def eng_score(eng: dict) -> float | None:
    if not eng:
        return None
    c = eng.get("comments")   or 0
    r = eng.get("reactions")  or 0
    i = eng.get("impressions") or 0
    if not c and not r and not i:
        return None
    return c * 3 + r + round(i / 100)


def load_articles() -> list[dict]:
    if not STATE_FILE.exists():
        return []
    try:
        raw = json.loads(STATE_FILE.read_text("utf-8"))
        return list(raw.get("articles", {}).values())
    except Exception:
        return []


def aggregate(articles: list[dict], field: str) -> list[dict]:
    buckets: dict[str, dict] = {}
    for a in articles:
        key = a.get(field)
        if not key:
            continue
        scores = [
            eng_score(e)
            for e in (a.get("engagement") or {}).values()
            if eng_score(e) is not None
        ]
        if not scores:
            continue
        avg = sum(scores) / len(scores)
        if key not in buckets:
            buckets[key] = {"total": 0.0, "count": 0}
        buckets[key]["total"] += avg
        buckets[key]["count"] += 1

    return sorted(
        [{"name": k, "avg": round(v["total"] / v["count"]), "posts": v["count"]}
         for k, v in buckets.items()],
        key=lambda x: x["avg"], reverse=True,
    )


def build_brief(articles: list[dict]) -> str:
    by_topic = aggregate(articles, "topic")
    by_hook  = aggregate(articles, "hook_type")

    scored = [a for a in articles
              if any(eng_score(e) is not None
                     for e in (a.get("engagement") or {}).values())]

    lines = [
        f"# Performance Brief",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Articles with engagement data: {len(scored)} of {len(articles)}",
        "",
    ]

    if not scored:
        lines += [
            "## No engagement data yet",
            "",
            "Enter impressions, comments, and reactions in the dashboard",
            "after publishing each piece to start building this brief.",
        ]
        return "\n".join(lines)

    # Topics
    lines += ["## Topic Performance (avg engagement score)"]
    if by_topic:
        for i, t in enumerate(by_topic):
            marker = " <-- TOP" if i == 0 else (" <-- AVOID" if i == len(by_topic) - 1 and len(by_topic) > 2 else "")
            lines.append(f"- {t['name']}: {t['avg']} ({t['posts']} posts){marker}")
    else:
        lines.append("- No tagged topic data yet")
    lines.append("")

    # Hook types
    lines += ["## Hook Type Performance (avg engagement score)"]
    if by_hook:
        for i, h in enumerate(by_hook):
            marker = " <-- TOP" if i == 0 else (" <-- AVOID" if i == len(by_hook) - 1 and len(by_hook) > 2 else "")
            lines.append(f"- {h['name']}: {h['avg']} ({h['posts']} posts){marker}")
    else:
        lines.append("- No tagged hook data yet")
    lines.append("")

    # Recommendation
    lines += ["## Recommendation for Next Article"]
    if by_topic and by_hook:
        top_t = by_topic[0]["name"]
        top_h = by_hook[0]["name"]
        low_t = by_topic[-1]["name"] if len(by_topic) > 1 else None
        lines.append(f"- Write about: **{top_t}** (highest avg score: {by_topic[0]['avg']})")
        lines.append(f"- Use hook type: **{top_h}** (highest avg score: {by_hook[0]['avg']})")
        if low_t:
            lines.append(f"- Rest this topic for now: {low_t} (lowest score: {by_topic[-1]['avg']})")
    else:
        lines.append("- More data needed for a reliable recommendation.")
    lines.append("")

    # Raw article scores
    lines += ["## Article Scores (published pieces)"]
    for a in sorted(scored,
                    key=lambda x: max(
                        (eng_score(e) or 0 for e in (x.get("engagement") or {}).values()),
                        default=0),
                    reverse=True):
        scores = [eng_score(e) for e in (a.get("engagement") or {}).values()
                  if eng_score(e) is not None]
        if not scores:
            continue
        best  = max(scores)
        title = a.get("title") or a.get("slug", "")
        num   = a.get("art_num") or ""
        tag   = f"{a.get('topic','?')} / {a.get('hook_type','?')}"
        lines.append(f"- {num} {title[:60]} [{tag}] best: {best}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate performance brief from dashboard state")
    parser.add_argument("--out", default=str(OUT_FILE), help="Output file path")
    args = parser.parse_args()

    articles = load_articles()
    brief    = build_brief(articles)

    out = Path(args.out)
    out.write_text(brief, encoding="utf-8")
    print(f"[done] Brief written -> {out}")
    print()
    print(brief)


if __name__ == "__main__":
    main()
