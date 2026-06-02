#!/usr/bin/env python3
"""
linkedin_atomizer.py  ·  content-engine/

One article in → seven LinkedIn content files written to pending/<slug>/
for review before scheduling.

Usage
-----
  # article from file (slug = filename stem)
  python linkedin_atomizer.py --file ART3-motel.md --date 2026-06-02

  # article pasted at prompt (slug = publish date)
  python linkedin_atomizer.py --date 2026-06-09

Output
------
  content-engine/pending/<slug>/
      text-post.md
      image-post.md
      carousel.md
      newsletter.md
      first-comments.md
      poll.md
      buffer-schedule.md
      _README.md
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import anthropic

# ── paths (always relative to this script — works regardless of CWD) ─────────
HERE         = Path(__file__).parent
RULES_DIR    = HERE / "rules"
PENDING_DIR  = HERE / "pending"
ARTICLES_DIR = HERE / "articles"

# ── section header → output filename ─────────────────────────────────────────
SECTION_MAP = {
    "TEXT FEED POST":  "text-post.md",
    "IMAGE POST":      "image-post.md",
    "CAROUSEL":        "carousel.md",
    "NEWSLETTER":      "newsletter.md",
    "FIRST COMMENTS":  "first-comments.md",
    "POLL":            "poll.md",
    "BUFFER SCHEDULE": "buffer-schedule.md",
}

REVIEW_CHECKLIST = """\
## Review Checklist

- [ ] Text feed post: hook in first line, no link in body, CTA is `Comment "GUIDE"`
- [ ] Image post: copy fits the visual, stat/quote is accurate, no link in body
- [ ] Carousel: ≤ 10 slides, one idea per slide, CTA on final slide
- [ ] Newsletter: subject line ≤ 50 chars, Kit URL placeholder present
- [ ] First comments: A–D options drafted, pick one before scheduling
- [ ] Poll: question is curiosity-driven, not leading
- [ ] Buffer schedule: date/time matches publish calendar, all slots filled
"""


# ── helpers ───────────────────────────────────────────────────────────────────

def _load_env() -> None:
    """Load .env from the project root (parent of content-engine/)."""
    env_path = HERE.parent / ".env"
    if not env_path.exists():
        return
    import os
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


def _read_optional(path: Path) -> str:
    """Return file contents, or empty string with a warning if missing."""
    if path.exists():
        return path.read_text(encoding="utf-8")
    print(f"[warn] {path.relative_to(HERE)} not found — skipping", file=sys.stderr)
    return ""


def _derive_slug(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).stem
    return args.date  # e.g. 2026-06-09


def _read_article(args: argparse.Namespace) -> str:
    if args.file:
        candidate = Path(args.file)
        if not candidate.is_absolute():
            candidate = ARTICLES_DIR / candidate.name
        if not candidate.exists():
            sys.exit(f"[error] Article not found: {candidate}")
        return candidate.read_text(encoding="utf-8")
    print("Paste article text, then Ctrl-Z + Enter (Windows) or Ctrl-D (Unix):\n")
    return sys.stdin.read()


def _find_section(sections: dict[str, str], header: str) -> str | None:
    """Locate a section by exact match, then case-insensitive, then starts-with."""
    if header in sections:
        return sections[header]
    upper = header.upper()
    for k, v in sections.items():
        if k.upper() == upper:
            return v
    for k, v in sections.items():
        if k.upper().startswith(upper):
            return v
    return None


# ── prompt ────────────────────────────────────────────────────────────────────

def _build_prompt(
    article: str,
    rules: str,
    voice: str,
    randy_voice: str,
    publish_date: str,
) -> str:
    preamble_parts = ["You are producing LinkedIn content for Randy Skiles.\n"]
    if voice:
        preamble_parts.append(f"VOICE AND STYLE:\n{voice}\n")
    if randy_voice:
        preamble_parts.append(f"RANDY VOICE PROFILE:\n{randy_voice}\n")
    if rules:
        preamble_parts.append(f"LINKEDIN CONTENT RULES:\n{rules}\n")
    preamble = "\n".join(preamble_parts)

    headers = "\n".join(f"## {h}" for h in SECTION_MAP)

    return f"""{preamble}
ARTICLE (publish date: {publish_date}):
---
{article}
---

Produce all seven sections below. Each section MUST begin with its exact header
on its own line (e.g. "## TEXT FEED POST"). Do not merge sections. Do not add
extra headers. Write every section even if the article is short.

{headers}

Rules for each section:

## TEXT FEED POST
Standalone LinkedIn feed post drawn from the article. Hook in the very first line
(no label, no "Hook:"). No links anywhere in the body. End with exactly:
Comment "GUIDE" and I'll DM you the free breakdown.

## IMAGE POST
Short post to accompany a single static image — a stat, bold claim, or pull quote
from the article. No link in the body. CTA: comment GUIDE.

## CAROUSEL
Slide-by-slide copy. Label each slide Slide 1, Slide 2, etc. Maximum 10 slides.
Each slide: one headline + 1–2 supporting lines. Final slide: CTA to comment GUIDE.

## NEWSLETTER
Email to the Kit subscriber list.
First line: Subject: [subject line, 50 chars max]
Then the email body in Randy's voice. End with a CTA that includes [Kit landing page URL].

## FIRST COMMENTS
Four comment options labeled A, B, C, D for the first comment on the feed post.
Comments add context — they do not repeat the post copy.
At least one option includes [Kit landing page URL].

## POLL
LinkedIn poll. Write the question + exactly 4 answer options.
Curiosity-driven — do not lead the reader toward a "correct" answer.

## BUFFER SCHEDULE
Week-of posting schedule starting {publish_date}.
Format each line: Day DD Mon — Platform — Content type — HH:MM CDT
Include the LinkedIn Article publish slot and every supporting asset for the week.
"""


# ── split and save ────────────────────────────────────────────────────────────

def _split_sections(text: str) -> dict[str, str]:
    """Split Claude's response at '## HEADER' lines into {{header: body}} pairs."""
    sections: dict[str, str] = {}
    current_header: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            if current_header is not None:
                sections[current_header] = "".join(current_lines).strip()
            current_header = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_header is not None:
        sections[current_header] = "".join(current_lines).strip()

    return sections


def _save_output(slug: str, publish_date: str, sections: dict[str, str]) -> list[str]:
    """Write each section to its own file in pending/<slug>/. Return filenames written."""
    out_dir = PENDING_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []

    for header, filename in SECTION_MAP.items():
        body = _find_section(sections, header)
        if body is None:
            print(
                f"[warn] '{header}' not found in response — {filename} not written",
                file=sys.stderr,
            )
            continue
        (out_dir / filename).write_text(f"## {header}\n\n{body}\n", encoding="utf-8")
        written.append(filename)

    file_list = "\n".join(f"- `{f}`" for f in written)
    readme = (
        f"# {slug}\n\n"
        f"**Slug:** `{slug}`  \n"
        f"**Publish date:** {publish_date}  \n"
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  \n\n"
        f"{REVIEW_CHECKLIST}\n"
        f"## Files in this folder\n\n"
        f"{file_list}\n"
    )
    (out_dir / "_README.md").write_text(readme, encoding="utf-8")
    written.append("_README.md")

    return written


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    _load_env()

    parser = argparse.ArgumentParser(
        description="LinkedIn content atomizer — one article → seven files in pending/<slug>/",
    )
    parser.add_argument(
        "--file",
        help="Article .md filename (looked up in content-engine/articles/)",
    )
    parser.add_argument(
        "--date",
        required=True,
        help="Publish date YYYY-MM-DD (used in schedule block; slug if no --file)",
    )
    args = parser.parse_args()

    slug    = _derive_slug(args)
    article = _read_article(args)

    rules       = _read_optional(RULES_DIR / "LINKEDIN_CONTENT_SKILL.md")
    voice       = _read_optional(RULES_DIR / "voice.md")
    randy_voice = _read_optional(RULES_DIR / "RANDY_VOICE_SKILL.md")

    prompt = _build_prompt(article, rules, voice, randy_voice, args.date)

    print(f"[info] Calling Claude API — slug: {slug}")
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )
    response_text = message.content[0].text

    sections = _split_sections(response_text)
    written  = _save_output(slug, args.date, sections)

    print(f"[done] {len(written)} files → pending/{slug}/")
    for f in written:
        print(f"       {f}")


if __name__ == "__main__":
    main()
