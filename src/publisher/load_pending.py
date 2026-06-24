"""
Loader for Buffer-eligible posts that live in content-engine/pending/{slug}/
(the current folder-per-piece structure), as opposed to the legacy single-file
docs/...CONTENT_DRAFTS.md format that content_parser.py reads.

Each entry in PENDING_ITEMS points at a specific file + the line range that is
the actual post body (frontmatter, headers, and "first comment" sections are
excluded — those are pasted manually after publish, never scheduled via the API).
"""
import sys
import re
from datetime import datetime, timezone, timedelta

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CDT_OFFSET = timedelta(hours=-5)
CST_OFFSET = timedelta(hours=-6)

PENDING_ITEMS = {
    "mon-career-2": {
        "file": "content-engine/pending/career-positioning-series/02_the-skill-that-makes-you-indispensable.md",
        "body_between": ("# Post body", "# First comment"),
        "label": "Mon 6/22 — Career post #2 (observability)",
    },
    "wed-art8-text": {
        "file": "content-engine/pending/ART8_The_Hardest_Worker_On_My_Team_Got_Cut_First/text-post.md",
        "body_between": ("## TEXT FEED POST", None),
        "label": "Wed 6/24 12:15 — ART8 text teaser",
        "image_file": "content-engine/pending/ART8_The_Hardest_Worker_On_My_Team_Got_Cut_First/images/00_hero_vertical.png",
    },
    "fri-art8-image": {
        "file": "content-engine/pending/ART8_The_Hardest_Worker_On_My_Team_Got_Cut_First/image-post.md",
        "body_between": ("## IMAGE POST", None),
        "label": "Fri 6/26 — ART8 image post (pull quote)",
        "strip_line_prefix": "Static image text:",
        "image_file": "content-engine/pending/ART8_The_Hardest_Worker_On_My_Team_Got_Cut_First/images/image_post_busy_vs_safe.png",
    },
    "wed-art9-text": {
        "file": "content-engine/pending/ART9_The_Next_Y2K_2038/text-post.md",
        "body_between": ("## TEXT FEED POST", None),
        "label": "Wed 7/08 12:15 — ART9 text teaser",
    },
    "thu-art9-image": {
        "file": "content-engine/pending/ART9_The_Next_Y2K_2038/image-post.md",
        "body_between": ("## IMAGE POST", None),
        "label": "Thu 7/09 11:30 — ART9 image post (pull quote)",
        "strip_line_prefix": "Static image text:",
        "image_file": "content-engine/pending/ART9_The_Next_Y2K_2038/images/image_post_pull_quote.png",
    },
    "fri-art9-carousel": {
        "file": "content-engine/pending/ART9_The_Next_Y2K_2038/carousel.md",
        "body_between": ("## CAROUSEL CAPTION", "## SLIDES"),
        "label": "Fri 7/10 08:30 — ART9 carousel (10 slides, PDF)",
        "document_file": "content-engine/pending/ART9_The_Next_Y2K_2038/ART9_The_Next_Y2K_2038_carousel.pdf",
        "thumbnail_file": "content-engine/pending/ART9_The_Next_Y2K_2038/images/01_hook.png",
        "document_title": "What Would You Say You Do Here? In 2038 We're Gonna Find Out!",
    },
}


def _extract_body(path, start_marker, end_marker):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    start = content.index(start_marker) + len(start_marker)
    end = content.index(end_marker, start) if end_marker else len(content)
    body = content[start:end].strip()
    body = re.sub(r"^---\s*$", "", body, flags=re.MULTILINE).strip()
    return body


def get_pending_body(item_key):
    item = PENDING_ITEMS[item_key]
    start, end = item["body_between"]
    body = _extract_body(item["file"], start, end)
    prefix = item.get("strip_line_prefix")
    if prefix:
        lines = [ln for ln in body.splitlines() if not ln.strip().startswith(prefix)]
        body = "\n".join(lines).strip()
    return body


def _parse_local(date_str):
    local = datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M")
    offset = CDT_OFFSET if 3 <= local.month <= 10 else CST_OFFSET
    local_aware = local.replace(tzinfo=timezone(offset))
    return local_aware.astimezone(timezone.utc)


def run_load_pending(item_key, date_str, dry_run=False):
    from src.publisher.buffer_publisher import schedule_post
    from src.publisher.wordpress_uploader import upload_media

    if item_key not in PENDING_ITEMS:
        print(f"[ERROR] Unknown item '{item_key}'. Known items: {', '.join(PENDING_ITEMS)}")
        return

    item = PENDING_ITEMS[item_key]
    body = get_pending_body(item_key)

    print(f"\n{item['label']}")
    print(f"Source: {item['file']}")
    print(f"Scheduled for: {date_str} CDT")
    print(f"\nPost preview ({len(body)} chars):")
    print("-" * 50)
    print(body)
    print("-" * 50)

    if item.get("image_file"):
        print(f"\n[NOTE] This post has an image ({item['image_file']}).")
        print("        Will upload to rskiles.com (WordPress media library) for a public URL, then attach to the Buffer post.")
    if item.get("document_file"):
        print(f"\n[NOTE] This post has a document ({item['document_file']}) + thumbnail ({item.get('thumbnail_file')}).")
        print("        Will upload both to rskiles.com, then attach as a Document asset to the Buffer post.")

    if dry_run:
        print("\n[DRY RUN] No post created, no files uploaded. Remove --dry-run to schedule for real.")
        return

    due_at_utc = _parse_local(date_str)
    assets = None

    try:
        if item.get("image_file"):
            print(f"\nUploading {item['image_file']} to WordPress...")
            media = upload_media(item["image_file"], title=item["label"])
            print(f"[OK] Uploaded — {media['url']}")
            assets = [{"image": {"url": media["url"]}}]
        elif item.get("document_file"):
            print(f"\nUploading {item['document_file']} to WordPress...")
            doc_media = upload_media(item["document_file"], title=item["label"])
            print(f"[OK] Uploaded — {doc_media['url']}")
            print(f"Uploading thumbnail {item['thumbnail_file']} to WordPress...")
            thumb_media = upload_media(item["thumbnail_file"], title=f"{item['label']} (thumbnail)")
            print(f"[OK] Uploaded — {thumb_media['url']}")
            assets = [{
                "document": {
                    "url": doc_media["url"],
                    "title": item.get("document_title", item["label"]),
                    "thumbnailUrl": thumb_media["url"],
                }
            }]
    except Exception as e:
        print(f"[ERROR] Media upload failed: {e}")
        return

    print("\nScheduling to LinkedIn via Buffer...")
    try:
        result = schedule_post(body, due_at_utc, assets=assets)
    except Exception as e:
        print(f"[ERROR] Buffer API failed: {e}")
        return

    print(f"[OK] Scheduled — Buffer post ID: {result.get('id')}")
    print(f"     Status: {result.get('status')} | Publishes: {result.get('dueAt')}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--item", required=True, choices=list(PENDING_ITEMS))
    parser.add_argument("--date", required=True, help="YYYY-MM-DD HH:MM (Central time)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_load_pending(args.item, args.date, args.dry_run)
