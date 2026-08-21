"""
Real YouTube Analytics pull for the self-improvement channel spec's
actual core question: "is there real evidence people watch more than one
video in a sitting?" Requires OAuth (run src/youtube_oauth_setup.py
first) -- the public API key alone cannot answer this.

The real signal: insightTrafficSourceType broken down by views.
"RELATED_VIDEO" traffic (a viewer clicked from one of this channel's own
videos into another, via suggested/end-screen) is the closest real proxy
YouTube's API exposes for session/binge behavior. High RELATED_VIDEO %
= real evidence people watch more than one video per sitting.
YT_SEARCH/EXT_URL/etc. = people arriving fresh each time, no binge signal.

Run: python -m src.self_improvement_channel_analytics
"""
from __future__ import annotations

import json
import os
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv()

TOKEN_PATH = Path(__file__).resolve().parents[1] / ".youtube_oauth_token.json"
CHANNEL_ID = "UCZGHA3qfrHjkDQwSTxzz1CQ"  # Meditate with Me


def get_credentials() -> Credentials:
    if not TOKEN_PATH.exists():
        raise SystemExit(
            "No saved OAuth token found. Run `python -m src.youtube_oauth_setup` "
            "first (one-time, interactive browser login)."
        )
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    return creds


def main():
    creds = get_credentials()
    analytics = build("youtubeAnalytics", "v2", credentials=creds)

    end = date.today().isoformat()
    start = (date.today() - timedelta(days=365)).isoformat()

    print(f"Pulling Analytics for channel {CHANNEL_ID}, {start} to {end}\n")

    # 1. THE real question: traffic source breakdown (session/binge proxy)
    traffic = analytics.reports().query(
        ids=f"channel=={CHANNEL_ID}",
        startDate=start,
        endDate=end,
        metrics="views",
        dimensions="insightTrafficSourceType",
        sort="-views",
    ).execute()

    print("=== Traffic Source Breakdown (the real session/binge signal) ===")
    total_views = sum(row[1] for row in traffic.get("rows", []))
    related_video_views = 0
    for row in traffic.get("rows", []):
        source, views = row[0], row[1]
        pct = (views / total_views * 100) if total_views else 0
        flag = "  <-- session/binge signal" if source == "RELATED_VIDEO" else ""
        print(f"  {source:30s} {views:>8}  ({pct:.1f}%){flag}")
        if source == "RELATED_VIDEO":
            related_video_views = views

    related_pct = (related_video_views / total_views * 100) if total_views else 0
    print(f"\n  RELATED_VIDEO share: {related_pct:.1f}% of all views")
    print("  (This is views arriving from another of the channel's own videos --")
    print("   the real evidence of session/binge behavior, or the lack of it.)")

    # 2. Per-video retention (top 20 by views, same window)
    video_stats = analytics.reports().query(
        ids=f"channel=={CHANNEL_ID}",
        startDate=start,
        endDate=end,
        metrics="views,averageViewDuration,averageViewPercentage",
        dimensions="video",
        sort="-views",
        maxResults=20,
    ).execute()

    print("\n=== Top 20 videos (last 365 days) - views / avg view duration / avg view % ===")
    for row in video_stats.get("rows", []):
        video_id, views, avg_duration, avg_pct = row
        print(f"  {video_id}  views={views:>6}  avg_dur={avg_duration:>5}s  avg_%={avg_pct:.1f}%")

    out_path = Path(__file__).resolve().parents[1] / "content-engine" / "research" / "self_improvement_channel_analytics.json"
    out_path.write_text(json.dumps({
        "window": {"start": start, "end": end},
        "traffic_source": traffic.get("rows", []),
        "related_video_share_pct": round(related_pct, 1),
        "top_videos": video_stats.get("rows", []),
    }, indent=2), encoding="utf-8")
    print(f"\nFull data written to {out_path}")


if __name__ == "__main__":
    main()
