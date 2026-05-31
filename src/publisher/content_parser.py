"""
Parser for docs/CONTENT_DRAFTS.md.
Extracts post body text by post number and updates status lines after scheduling.
"""
import re

DRAFTS_PATH = "docs/CONTENT_DRAFTS.md"

# Matches from "### POST N —" up to the next post, section, or end of file
_SECTION_RE = r"(### POST {n}(?!\d) —[^\n]*\n(?:.*\n)*?)(?=### POST \d+|## PUBLISHED|## WEDNESDAY|\Z)"
_STATUS_RE = r"(\*\*Status:\*\* )([^\n]+)"
_BODY_RE = r"\*\*POST BODY[^\n]*\n```\n(.*?)```"


def _load():
    with open(DRAFTS_PATH, "r", encoding="utf-8") as f:
        return f.read()


def _save(content):
    import os as _os
    tmp = DRAFTS_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)
    _os.replace(tmp, DRAFTS_PATH)


def _get_section(content, post_number):
    match = re.search(_SECTION_RE.format(n=post_number), content, re.DOTALL)
    if not match:
        raise ValueError(f"POST {post_number} not found in {DRAFTS_PATH}")
    return match.group(1), match.start()


def get_post_body(post_number):
    """
    Return the post body text for POST N (content inside the 'POST BODY' code block).
    Raises ValueError if not found.
    """
    content = _load()
    section, _ = _get_section(content, post_number)
    match = re.search(_BODY_RE, section, re.DOTALL)
    if not match:
        raise ValueError(f"POST BODY code block not found for POST {post_number}")
    return match.group(1).strip()


def get_post_status(post_number):
    """Return the current status text for POST N."""
    content = _load()
    section, _ = _get_section(content, post_number)
    match = re.search(_STATUS_RE, section)
    return match.group(2).strip() if match else "Unknown"


def mark_scheduled(post_number, buffer_post_id, scheduled_label):
    """
    Replace the Status line for POST N with a SCHEDULED IN BUFFER entry.

    Args:
        post_number:    Integer post number.
        buffer_post_id: Post ID returned by Buffer API.
        scheduled_label: Human-readable date/time string for the status line.
    """
    content = _load()
    section, section_start = _get_section(content, post_number)

    status_match = re.search(_STATUS_RE, section)
    if not status_match:
        print(f"[WARN] No Status line found for POST {post_number} — skipping update")
        return

    new_status = (
        f"**Status:** ✅ SCHEDULED IN BUFFER — {scheduled_label} "
        f"| Buffer ID: {buffer_post_id}"
    )
    new_section = section[:status_match.start()] + new_status + section[status_match.end():]
    new_content = content[:section_start] + new_section + content[section_start + len(section):]
    _save(new_content)
    print(f"[OK] POST {post_number} status updated in {DRAFTS_PATH}")
