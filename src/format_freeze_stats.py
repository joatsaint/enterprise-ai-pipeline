"""
Weekly stats refresh for the format-freeze test (see
memory/project_format_freeze_test_2026-08-13.md). Reads every row in
content-engine/research/format_freeze_tracking.csv that has a real
video_id, pulls current view/like/comment counts from the YouTube Data
API v3 (free tier, no OAuth needed for public stats), and updates the
views_7d/views_30d/likes/comments columns in place based on days since
publish. Does not touch rows a human hasn't filled in yet (blank
video_id is skipped, not an error).

Run manually: python -m src.format_freeze_stats
Scheduled: see format_freeze_stats_task.xml (weekly, same pattern as
digest_task.xml).
"""
from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

CSV_PATH = Path(__file__).resolve().parents[1] / "content-engine" / "research" / "format_freeze_tracking.csv"
DASHBOARD_JS_PATH = Path(__file__).resolve().parents[1] / "bitcoin-dashboard" / "data" / "format_freeze_report.js"
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def write_dashboard_data(rows: list[dict]) -> None:
    """Write bitcoin-dashboard/data/format_freeze_report.js so the
    dashboard tile has something to render the moment real rows exist --
    no separate "remember to build the dashboard" step later."""
    DASHBOARD_JS_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = [r for r in rows if r.get("video_id", "").strip()]
    js = "window.FORMAT_FREEZE_DATA = " + json.dumps(payload, indent=2) + ";\n"
    DASHBOARD_JS_PATH.write_text(js, encoding="utf-8")


def fetch_stats(video_id: str) -> dict | None:
    resp = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={"part": "statistics", "id": video_id, "key": YOUTUBE_API_KEY},
        timeout=15,
    )
    resp.raise_for_status()
    items = resp.json().get("items", [])
    if not items:
        return None
    return items[0]["statistics"]


def days_since(date_str: str) -> int:
    published = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - published).days


def main():
    if not YOUTUBE_API_KEY:
        print("YOUTUBE_API_KEY not set in .env -- nothing to do.")
        return

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    updated = 0
    for row in rows:
        video_id = row.get("video_id", "").strip()
        if not video_id:
            continue
        stats = fetch_stats(video_id)
        if stats is None:
            print(f"  [skip] {video_id}: not found or private")
            continue
        age_days = days_since(row["date_published"]) if row.get("date_published") else None
        views = stats.get("viewCount", "")
        if age_days is not None and age_days <= 8 and not row.get("views_7d"):
            row["views_7d"] = views
        if age_days is not None and age_days >= 28 and not row.get("views_30d"):
            row["views_30d"] = views
        row["likes"] = stats.get("likeCount", row.get("likes", ""))
        row["comments"] = stats.get("commentCount", row.get("comments", ""))
        updated += 1

    if not rows:
        print("Tracking sheet is empty -- nothing to update.")
        write_dashboard_data([])
        return

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    write_dashboard_data(rows)
    print(f"Updated {updated} row(s) in {CSV_PATH}, wrote {DASHBOARD_JS_PATH}")


if __name__ == "__main__":
    main()
