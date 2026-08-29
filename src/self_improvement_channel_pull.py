"""
Public-stats pull for the self-improvement channel analytics spec (see
Google Drive brain-dropping "CLAUDE CODE SPEC Self Improvement Channel
Analytics Pull", 2026-08-13). Channel: youtube.com/@meditatewithme4897.

Real, honest scope limit: this pulls only what the public YouTube Data
API v3 exposes (views, likes, comments per video) using the existing
YOUTUBE_API_KEY. It does NOT and CANNOT pull retention %, average view
duration, session/binge behavior, or traffic source -- those require the
YouTube Analytics API with OAuth as the channel owner, a separate,
bigger auth build not done here. This script answers "what are the real
top/bottom performers by public engagement" only -- the spec's most
important question (do viewers watch more than one video) is NOT
answered by this script.

Run manually: python -m src.self_improvement_channel_pull
"""
from __future__ import annotations

import csv
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ID = "UCZGHA3qfrHjkDQwSTxzz1CQ"
UPLOADS_PLAYLIST = "UUZGHA3qfrHjkDQwSTxzz1CQ"
OUTPUT_CSV = Path(__file__).resolve().parents[1] / "content-engine" / "research" / "self_improvement_channel_report.csv"
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def get_all_video_ids() -> list[str]:
    ids = []
    page_token = None
    while True:
        params = {
            "part": "contentDetails",
            "playlistId": UPLOADS_PLAYLIST,
            "maxResults": 50,
            "key": YOUTUBE_API_KEY,
        }
        if page_token:
            params["pageToken"] = page_token
        resp = requests.get("https://www.googleapis.com/youtube/v3/playlistItems", params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        ids.extend(item["contentDetails"]["videoId"] for item in data.get("items", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return ids


def get_stats(video_ids: list[str]) -> list[dict]:
    results = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={"part": "snippet,statistics,contentDetails", "id": ",".join(batch), "key": YOUTUBE_API_KEY},
            timeout=15,
        )
        resp.raise_for_status()
        for item in resp.json().get("items", []):
            results.append({
                "video_id": item["id"],
                "title": item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"][:10],
                "duration": item["contentDetails"]["duration"],
                "views": int(item["statistics"].get("viewCount", 0)),
                "likes": int(item["statistics"].get("likeCount", 0)),
                "comments": int(item["statistics"].get("commentCount", 0)),
            })
    return results


def main():
    if not YOUTUBE_API_KEY:
        print("YOUTUBE_API_KEY not set in .env -- nothing to do.")
        return

    print("Pulling all video IDs from uploads playlist...")
    video_ids = get_all_video_ids()
    print(f"Found {len(video_ids)} videos. Pulling stats...")
    stats = get_stats(video_ids)
    stats.sort(key=lambda v: v["views"], reverse=True)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["video_id", "title", "published_at", "duration", "views", "likes", "comments"])
        writer.writeheader()
        writer.writerows(stats)

    print(f"\nWrote {len(stats)} videos to {OUTPUT_CSV}")
    print("\nTop 5 by views:")
    for v in stats[:5]:
        print(f"  {v['views']:>8}  {v['title']}")
    print("\nBottom 5 by views:")
    for v in stats[-5:]:
        print(f"  {v['views']:>8}  {v['title']}")


if __name__ == "__main__":
    main()
