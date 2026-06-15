"""
md_to_linkedin_html.py — Convert a Markdown article to clean, paste-ready HTML.

Why: pasting raw Markdown into LinkedIn shows literal #/** and collapses spacing.
Pasting RENDERED (formatted) text keeps paragraphs, headers, bold, and lists with
zero manual cleanup. This produces that rendered HTML and opens it in your browser.

Usage:
    python content-engine/md_to_linkedin_html.py "docs/SOME_ARTICLE.md"
    python content-engine/md_to_linkedin_html.py "docs/SOME_ARTICLE.md" --no-open

Then in the browser: Ctrl+A, Ctrl+C, and paste into the LinkedIn Article editor.

Stdlib only — no external packages. Handles: # ## ### headings, paragraphs,
**bold** / *italic* / `inline code`, [links](url), - and * bullet lists,
1. numbered lists, > blockquotes, --- horizontal rules, and ``` fenced code blocks.
"""

import html
import re
import sys
import webbrowser
from pathlib import Path

CSS = """
body { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
       max-width: 720px; margin: 40px auto; padding: 0 20px; line-height: 1.6;
       color: #1d2226; font-size: 18px; }
h1 { font-size: 2em; line-height: 1.2; margin: 0.6em 0 0.4em; }
h2 { font-size: 1.4em; margin: 1.4em 0 0.4em; }
h3 { font-size: 1.15em; margin: 1.2em 0 0.3em; }
p { margin: 0.8em 0; }
ul, ol { margin: 0.8em 0; padding-left: 1.5em; }
li { margin: 0.3em 0; }
blockquote { border-left: 4px solid #0a66c2; margin: 1em 0; padding: 0.2em 1em;
             color: #44484c; background: #f3f6f8; }
hr { border: none; border-top: 1px solid #d0d5da; margin: 2em 0; }
code { background: #f0f2f4; padding: 2px 6px; border-radius: 4px;
       font-family: Consolas, Monaco, monospace; font-size: 0.9em; }
pre { background: #1d2226; color: #e8eef2; padding: 14px 16px; border-radius: 6px;
      overflow-x: auto; }
pre code { background: none; color: inherit; padding: 0; }
a { color: #0a66c2; }
.banner { background: #fff8e1; border: 1px solid #ffe082; border-radius: 6px;
          padding: 10px 14px; font-size: 14px; color: #6d4c00; margin-bottom: 24px; }
"""

BANNER = ("Select all (Ctrl+A), copy (Ctrl+C), and paste into the LinkedIn "
          "<b>Article</b> editor. Formatting carries over. "
          "Note: LinkedIn strips code-block styling and images on paste — "
          "re-add the cover/hero image in LinkedIn, and use a quote block + emoji "
          "for any commands.")


def _inline(text: str) -> str:
    """Inline formatting on an already escaped string."""
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def convert(md: str) -> str:
    lines = md.split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # fenced code block
        if stripped.startswith("```"):
            buf, i = [], i + 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            i += 1
            continue

        # horizontal rule
        if re.fullmatch(r"-{3,}|\*{3,}", stripped):
            out.append("<hr>")
            i += 1
            continue

        # headings
        m = re.match(r"(#{1,6})\s+(.*)", stripped)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(html.escape(m.group(2)))}</h{level}>")
            i += 1
            continue

        # blockquote
        if stripped.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(_inline(html.escape(lines[i].strip()[1:].strip())))
                i += 1
            out.append("<blockquote>" + "<br>".join(buf) + "</blockquote>")
            continue

        # unordered list
        if re.match(r"[-*]\s+", stripped):
            buf = []
            while i < len(lines) and re.match(r"[-*]\s+", lines[i].strip()):
                item = re.sub(r"^[-*]\s+", "", lines[i].strip())
                buf.append(f"<li>{_inline(html.escape(item))}</li>")
                i += 1
            out.append("<ul>" + "".join(buf) + "</ul>")
            continue

        # ordered list
        if re.match(r"\d+\.\s+", stripped):
            buf = []
            while i < len(lines) and re.match(r"\d+\.\s+", lines[i].strip()):
                item = re.sub(r"^\d+\.\s+", "", lines[i].strip())
                buf.append(f"<li>{_inline(html.escape(item))}</li>")
                i += 1
            out.append("<ol>" + "".join(buf) + "</ol>")
            continue

        # blank line
        if stripped == "":
            i += 1
            continue

        # paragraph (gather consecutive non-blank, non-structural lines)
        buf = []
        while i < len(lines) and lines[i].strip() != "" and not re.match(
            r"(#{1,6}\s|[-*]\s|\d+\.\s|>|```|-{3,}$|\*{3,}$)", lines[i].strip()
        ):
            buf.append(_inline(html.escape(lines[i].strip())))
            i += 1
        out.append("<p>" + "<br>".join(buf) + "</p>")

    body = "\n".join(out)
    return (f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<style>{CSS}</style></head><body>"
            f"<div class='banner'>{BANNER}</div>{body}</body></html>")


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--no-open"]
    if not args:
        print("Usage: python md_to_linkedin_html.py <path-to-markdown.md> [--no-open]")
        sys.exit(1)
    src = Path(args[0])
    if not src.exists():
        print(f"File not found: {src}")
        sys.exit(1)
    out_path = src.with_suffix(".linkedin.html")
    out_path.write_text(convert(src.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"Wrote: {out_path}")
    if "--no-open" not in sys.argv:
        webbrowser.open(out_path.resolve().as_uri())
        print("Opened in browser. Ctrl+A, Ctrl+C, then paste into LinkedIn.")


if __name__ == "__main__":
    main()
