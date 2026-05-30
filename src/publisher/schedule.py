"""
CLI runner for the schedule-post command.

Reads a post body from docs/CONTENT_DRAFTS.md, schedules it to LinkedIn
via Buffer's GraphQL API, and updates the post's status line.

Times are treated as US Central (CDT = UTC-5, CST = UTC-6).
Buffer publishes at the UTC equivalent.
"""
import sys
from datetime import datetime, timezone, timedelta

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CDT_OFFSET = timedelta(hours=-5)  # May–Nov
CST_OFFSET = timedelta(hours=-6)  # Nov–Mar


def _parse_local(date_str):
    """
    Parse 'YYYY-MM-DD HH:MM' as US Central time and return a UTC datetime.
    Assumes CDT (UTC-5) — adjust CST_OFFSET in winter.
    """
    local = datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M")
    local_tz = timezone(CDT_OFFSET)
    local_aware = local.replace(tzinfo=local_tz)
    return local_aware.astimezone(timezone.utc)


def run_schedule_post(post_number, date_str, dry_run=False):
    """
    Schedule POST N to LinkedIn via Buffer at the given date/time (Central time).

    Args:
        post_number: Integer post number from CONTENT_DRAFTS.md.
        date_str:    'YYYY-MM-DD HH:MM' in US Central time.
        dry_run:     If True, print what would be sent without calling Buffer.
    """
    from src.publisher.content_parser import get_post_body, get_post_status, mark_scheduled
    from src.publisher.buffer_publisher import schedule_post

    # Load and validate post content
    try:
        body = get_post_body(post_number)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    current_status = get_post_status(post_number)
    print(f"\nPOST {post_number}")
    print(f"Current status: {current_status}")
    print(f"Scheduled for:  {date_str} CDT")
    print(f"\nPost preview ({len(body)} chars):")
    print("─" * 50)
    print(body[:300] + ("..." if len(body) > 300 else ""))
    print("─" * 50)

    if dry_run:
        print("\n[DRY RUN] No post created. Remove --dry-run to schedule for real.")
        return

    # Convert to UTC
    try:
        due_at_utc = _parse_local(date_str)
    except ValueError:
        print(f"[ERROR] Invalid date format '{date_str}'. Use: YYYY-MM-DD HH:MM")
        return

    # Schedule via Buffer
    print("\nScheduling to LinkedIn via Buffer...")
    try:
        result = schedule_post(body, due_at_utc)
    except Exception as e:
        print(f"[ERROR] Buffer API failed: {e}")
        return

    buffer_id = result["id"]
    print(f"[OK] Scheduled — Buffer post ID: {buffer_id}")
    print(f"     Status: {result['status']} | Publishes: {result['dueAt']}")

    # Update CONTENT_DRAFTS.md
    scheduled_label = f"{date_str} CDT"
    mark_scheduled(post_number, buffer_id, scheduled_label)

    print(f"\n[DONE] POST {post_number} is queued in Buffer and marked in CONTENT_DRAFTS.md")
