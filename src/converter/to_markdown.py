import os
import re
from datetime import date as _date


DISPLAY_TO_FOLDER = {
    "AI & Claude Code": "ai-and-claude-code",
    "Bitcoin and Economic News": "bitcoin-and-economic-news",
    "Uncategorized": "uncategorized",
}


def slugify(title, max_len=60):
    """Create a filesystem-safe slug from a title."""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    slug = slug[:max_len].rstrip('-')
    return slug


def build_filename(title, downloaded_date=None):
    """Return filename in YYYY-MM-DD_[slug].md format."""
    if downloaded_date is None:
        downloaded_date = _date.today().isoformat()
    slug = slugify(title)
    return f"{downloaded_date}_{slug}.md"


def convert_to_markdown(cleaned_text, metadata, category_display, url, downloaded_date=None):
    """
    Write cleaned transcript to a categorized .md file.

    Args:
        cleaned_text: The cleaned transcript string.
        metadata: Dict with keys title, channel, published, word_count_after.
        category_display: Human-readable category string.
        url: Original YouTube URL.
        downloaded_date: ISO date string (YYYY-MM-DD). Defaults to today.

    Returns:
        Absolute file path of the written file.
    """
    if downloaded_date is None:
        downloaded_date = _date.today().isoformat()

    title = metadata.get("title", "Unknown Title")
    channel = metadata.get("channel", "Unknown")
    published = metadata.get("published") or "Unknown"
    word_count = metadata.get("word_count_after", len(cleaned_text.split()))

    folder = DISPLAY_TO_FOLDER.get(category_display, "uncategorized")
    output_dir = os.path.join("transcripts", folder)
    os.makedirs(output_dir, exist_ok=True)

    filename = build_filename(title, downloaded_date)
    file_path = os.path.join(output_dir, filename)

    content = (
        f"# {title}\n\n"
        f"**Channel:** {channel}\n"
        f"**Category:** {category_display}\n"
        f"**Published:** {published}\n"
        f"**URL:** {url}\n"
        f"**Downloaded:** {downloaded_date}\n"
        f"**Word Count:** {word_count}\n\n"
        f"---\n\n"
        f"## Transcript\n\n"
        f"{cleaned_text}\n"
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path
