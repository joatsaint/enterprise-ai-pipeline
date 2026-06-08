#!/usr/bin/env python3
"""
schedule_weekly_posts.py — content-engine/

Reads all post.md files from a weekly-posts week folder, schedules each
post's text to LinkedIn via Buffer at the time encoded in the folder name,
and prints the local image path so you can attach it manually in Buffer.

Buffer requires a publicly hosted image URL — local files can't be attached
via API. Each post takes ~30 seconds to attach manually in Buffer's web UI.

Usage
-----
  python schedule_weekly_posts.py week-of-2026-06-08
  python schedule_weekly_posts.py week-of-2026-06-08 --dry-run
"""

import argparse
import os
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE    = Path(__file__).resolve().parent
ROOT    = HERE.parent
PENDING = HERE / "pending" / "weekly-posts"

CDT_OFFSET = timedelta(hours=-5)  # Mar–Oct
CST_OFFSET = timedelta(hours=-6)  # Nov–Feb


def parse_schedule_from_folder(folder_name: str):
    """
    Parse date and time from folder name like:
      Monday_2026-06-08_8AM-CST
      Tuesday_2026-06-09_9AM-CST
    Returns a UTC-aware datetime.
    """
    # Extract date (YYYY-MM-DD) and time (e.g. 8AM, 9PM)
    m = re.search(r"(\d{4}-\d{2}-\d{2})_(\d+)(AM|PM)-C[SD]T", folder_name)
    if not m:
        raise ValueError(f"Cannot parse schedule from folder name: {folder_name}")
    date_str, hour_str, ampm = m.group(1), m.group(2), m.group(3)
    hour = int(hour_str)
    if ampm == "PM" and hour != 12:
        hour += 12
    elif ampm == "AM" and hour == 12:
        hour = 0
    local_dt = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=hour, minute=0)
    offset = CDT_OFFSET if 3 <= local_dt.month <= 10 else CST_OFFSET
    local_aware = local_dt.replace(tzinfo=timezone(offset))
    return local_aware.astimezone(timezone.utc)


def extract_post_text(post_md: Path) -> str:
    """Extract the post body from between the POST TEXT and FIRST COMMENT sections."""
    text = post_md.read_text("utf-8", errors="replace")
    m = re.search(
        r"## POST TEXT \(copy-paste ready\)\s*\n+(.*?)\n+---\s*\n+## FIRST COMMENT",
        text,
        re.DOTALL,
    )
    if not m:
        raise ValueError(f"Could not find POST TEXT section in {post_md}")
    return m.group(1).strip()


def extract_first_comment(post_md: Path) -> str:
    """Extract the first comment text (hashtags line)."""
    text = post_md.read_text("utf-8", errors="replace")
    m = re.search(
        r"## FIRST COMMENT \(post immediately after publishing\)\s*\n+(.*?)\n+---",
        text,
        re.DOTALL,
    )
    if not m:
        return ""
    return m.group(1).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("week", help="Week folder name, e.g. week-of-2026-06-08")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be scheduled without calling Buffer")
    args = parser.parse_args()

    week_dir = PENDING / args.week
    if not week_dir.exists():
        sys.exit(f"[error] Week folder not found: {week_dir}")

    day_dirs = sorted(week_dir.iterdir())
    if not day_dirs:
        sys.exit(f"[error] No day folders found in {week_dir}")

    if not args.dry_run:
        # Load env from project root
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
        token = os.getenv("BUFFER_ACCESS_TOKEN")
        channel_id = os.getenv("BUFFER_LINKEDIN_CHANNEL_ID")
        if not token or not channel_id:
            sys.exit("[error] BUFFER_ACCESS_TOKEN or BUFFER_LINKEDIN_CHANNEL_ID not set in .env")
        sys.path.insert(0, str(ROOT))
        from src.publisher.buffer_publisher import schedule_post

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Scheduling {args.week}\n")
    print("=" * 60)

    results = []

    for day_dir in day_dirs:
        post_md = day_dir / "post.md"
        if not post_md.exists():
            print(f"  [skip] {day_dir.name} — no post.md\n")
            continue

        # Parse schedule
        try:
            due_utc = parse_schedule_from_folder(day_dir.name)
        except ValueError as e:
            print(f"  [skip] {day_dir.name} — {e}\n")
            continue

        # Extract content
        try:
            post_text = extract_post_text(post_md)
            first_comment = extract_first_comment(post_md)
        except ValueError as e:
            print(f"  [skip] {day_dir.name} — {e}\n")
            continue

        image_path = day_dir / "image.png"
        local_time = due_utc.astimezone(timezone(timedelta(hours=-5)))

        print(f"  {day_dir.name}")
        print(f"  Publish: {local_time.strftime('%a %b %d %Y @ %I:%M %p CDT')}")
        print(f"  Words:   {len(post_text.split())}")
        print(f"  Preview: {post_text[:80].replace(chr(10), ' ')}...")

        if args.dry_run:
            print(f"  Image:   {image_path}")
            print(f"  Comment: {first_comment}")
            print()
            continue

        # Schedule to Buffer
        try:
            result = schedule_post(post_text, due_utc)
            buffer_id = result.get("id", "unknown")
            print(f"  [OK] Buffer ID: {buffer_id}")
            results.append({
                "day": day_dir.name,
                "buffer_id": buffer_id,
                "image_path": str(image_path),
                "first_comment": first_comment,
                "publish_time": local_time.strftime("%a %b %d @ %I:%M %p CDT"),
            })
        except Exception as e:
            print(f"  [FAIL] Buffer error: {e}")

        print(f"  Image to attach manually: {image_path.name}")
        print()

        if day_dirs.index(day_dir) < len(day_dirs) - 1:
            time.sleep(2)

    print("=" * 60)

    if not args.dry_run and results:
        print(f"\n[DONE] {len(results)}/5 posts scheduled in Buffer\n")
        print("NEXT STEP — attach images in Buffer (30 sec each):")
        print("  buffer.com/app → Publishing → Queue → edit each post\n")
        for r in results:
            print(f"  {r['publish_time']}")
            print(f"    Buffer ID : {r['buffer_id']}")
            print(f"    Image     : {r['image_path']}")
            print(f"    1st Comment: {r['first_comment']}")
            print()
    elif args.dry_run:
        print("\n[DRY RUN COMPLETE] Remove --dry-run to schedule for real.\n")


if __name__ == "__main__":
    main()
