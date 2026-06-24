"""
Manual links — the "LinkedIn saved posts/manual links" source from the Daily
Audience Radar spec. LinkedIn has no public API for reading posts/threads, so
this is the deliberate manual-entry source: Randy pastes a URL (one per line,
optional " | note" after it) into content-engine/radar_manual_links.md when he
spots a conversation worth joining, and the radar treats each as a candidate
on its next run — then clears the file so links aren't re-scored every day.
"""
import os
import re

from src.utils.atomic import atomic_write_text

LINKS_PATH = os.path.join("content-engine", "radar_manual_links.md")

_TEMPLATE = """# Radar Manual Links

Paste one LinkedIn (or any) URL per line below the divider — optionally
" | a short note" after it. Picked up by the next `audience-radar` run, then
this file is cleared automatically so links aren't re-scored.

---
"""


def _ensure_file():
    if not os.path.exists(LINKS_PATH):
        atomic_write_text(LINKS_PATH, _TEMPLATE)


def read_manual_links():
    """
    Returns a list of candidate dicts from any URLs pasted in
    content-engine/radar_manual_links.md, in source_scanner candidate shape.
    """
    _ensure_file()
    with open(LINKS_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    if "---" in text:
        _, _, body = text.partition("---")
    else:
        body = text

    candidates = []
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^(\S+)\s*(?:\|\s*(.*))?$", line)
        if not m:
            continue
        url, note = m.group(1), (m.group(2) or "").strip()
        if not url.startswith("http"):
            continue
        candidates.append({
            "title": note or "(manual link — no note)",
            "summary": note,
            "source": "manual:linkedin",
            "url": url,
        })
    return candidates


def clear_manual_links():
    """Reset the manual links file to the empty template after a run consumes it."""
    atomic_write_text(LINKS_PATH, _TEMPLATE)
