"""
Knowledge base indexer.

Scans the transcripts/ folder and builds knowledge_base/index.json —
a lightweight flat JSON index of all transcript files and their comment pairs.

Always rebuilds from scratch. Index is derived data; transcripts are the source of truth.
"""
import json
import os
import re
from datetime import datetime, timezone


INDEX_PATH = "knowledge_base/index.json"
TRANSCRIPTS_ROOT = "transcripts"


def _parse_markdown_headers(path):
    """Extract title, channel, published date from a transcript .md file."""
    title = ""
    channel = ""
    published = ""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# ") and not title:
                    title = line[2:].strip()
                elif line.startswith("**Channel:**"):
                    channel = line.replace("**Channel:**", "").strip()
                elif line.startswith("**Published:**"):
                    published = line.replace("**Published:**", "").strip()
                if title and channel and published:
                    break
    except Exception:
        pass
    return title, channel, published


def _word_count(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return len(f.read().split())
    except Exception:
        return 0


def build_index():
    """
    Scan transcripts/ and write knowledge_base/index.json.
    Returns the index dict.
    """
    os.makedirs("knowledge_base", exist_ok=True)

    index = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "total_files": 0,
        "groups": {},
    }

    if not os.path.isdir(TRANSCRIPTS_ROOT):
        print("[INDEX] No transcripts/ folder found — nothing to index.")
        _write_index(index)
        return index

    total = 0
    for group_name in sorted(os.listdir(TRANSCRIPTS_ROOT)):
        group_path = os.path.join(TRANSCRIPTS_ROOT, group_name)
        if not os.path.isdir(group_path):
            continue

        files = []
        md_files = sorted([
            f for f in os.listdir(group_path)
            if f.endswith(".md") and not f.endswith("_comments.md")
        ])

        for filename in md_files:
            filepath = os.path.join(group_path, filename)
            title, channel, published = _parse_markdown_headers(filepath)
            wc = _word_count(filepath)

            # Check for companion comments file
            base = filename[:-3]  # strip .md
            comments_filename = base + "_comments.md"
            comments_path = os.path.join(group_path, comments_filename)
            has_comments = os.path.isfile(comments_path)

            entry = {
                "filename": filename,
                "path": filepath.replace("\\", "/"),
                "title": title,
                "channel": channel,
                "published": published,
                "word_count": wc,
                "has_comments": has_comments,
                "comments_path": comments_path.replace("\\", "/") if has_comments else None,
            }
            files.append(entry)
            total += 1

        index["groups"][group_name] = {
            "count": len(files),
            "files": files,
        }

    index["total_files"] = total
    _write_index(index)
    print(f"[INDEX] Built index: {total} file(s) across {len(index['groups'])} group(s).")
    return index


def _write_index(index):
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def load_index():
    """Load and return the existing index, or build it if missing."""
    if not os.path.exists(INDEX_PATH):
        return build_index()
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
