"""
Benchmark-channel comparison tracker (see content-engine/research/
benchmark_channels.csv for the input list Randy provided). Pulls real
current stats per channel via YouTube Data API v3 (forHandle lookup,
free tier) and writes a report.

Run manually: python -m src.benchmark_channel_stats
"""
from __future__ import annotations

import csv
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

INPUT_CSV = Path(__file__).resolve().parents[1] / "content-engine" / "research" / "benchmark_channels.csv"
OUTPUT_CSV = Path(__file__).resolve().parents[1] / "content-engine" / "research" / "benchmark_channels_report.csv"
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def fetch_channel(handle: str) -> dict | None:
    resp = requests.get(
        "https://www.googleapis.com/youtube/v3/channels",
        params={
            "part": "snippet,statistics",
            "forHandle": handle,
            "key": YOUTUBE_API_KEY,
        },
        timeout=15,
    )
    resp.raise_for_status()
    items = resp.json().get("items", [])
    if not items:
        return None
    item = items[0]
    return {
        "handle": handle,
        "title": item["snippet"]["title"],
        "published_at": item["snippet"]["publishedAt"][:10],
        "subscriber_count": item["statistics"].get("subscriberCount", ""),
        "video_count": item["statistics"].get("videoCount", ""),
        "view_count": item["statistics"].get("viewCount", ""),
    }


def main():
    if not YOUTUBE_API_KEY:
        print("YOUTUBE_API_KEY not set in .env -- nothing to do.")
        return

    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        input_rows = list(csv.DictReader(f))

    results = []
    for row in input_rows:
        handle = row["handle"].strip()
        data = fetch_channel(handle)
        if data is None:
            print(f"  [skip] @{handle}: not found")
            continue
        data["why_watching"] = row.get("why_watching", "")
        results.append(data)
        print(f"  [ok] @{handle}: {data['subscriber_count']} subs, {data['video_count']} videos")

    if not results:
        print("No channels resolved -- nothing written.")
        return

    fieldnames = ["handle", "title", "published_at", "subscriber_count", "video_count", "view_count", "why_watching"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nWrote {len(results)} channel(s) to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
