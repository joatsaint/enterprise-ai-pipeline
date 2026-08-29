#!/usr/bin/env python3
"""
generate_pack_pdf.py — render a markdown lead-magnet (e.g. a prompt pack) into a
clean, READABLE, copy-paste-able PDF with SELECTABLE TEXT (reportlab).

Image-based PDFs (Remotion stills) are great for swipe carousels but useless for a
prompt pack — people can't copy the prompts out of an image. This makes a real
text PDF: code blocks are selectable monospace boxes.

Usage:
    python generate_pack_pdf.py "path/to/file.md" ["path/to/out.pdf"]

Supports: # title, ### subtitle, ## heading, ``` code blocks, > notes, --- rules,
*italic lines*, and normal paragraphs.
"""
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Preformatted,
                                Table, TableStyle, HRFlowable)

ACCENT = colors.HexColor("#1f6f3f")   # firewall green, print-safe
DARK = colors.HexColor("#161b22")
MUTED = colors.HexColor("#57606a")
CODE_BG = colors.HexColor("#f6f8fa")
CODE_BORDER = colors.HexColor("#d0d7de")


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_styles():
    ss = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("t", parent=ss["Title"], fontSize=26, leading=30, textColor=DARK, spaceAfter=4),
        "subtitle": ParagraphStyle("st", parent=ss["Normal"], fontSize=13, leading=17, textColor=ACCENT, spaceAfter=14, fontName="Helvetica-Bold"),
        "h2": ParagraphStyle("h2", parent=ss["Heading2"], fontSize=15, leading=19, textColor=DARK, spaceBefore=18, spaceAfter=4),
        "italic": ParagraphStyle("it", parent=ss["Normal"], fontSize=10.5, leading=14, textColor=MUTED, fontName="Helvetica-Oblique", spaceAfter=8),
        "body": ParagraphStyle("b", parent=ss["Normal"], fontSize=10.5, leading=15, textColor=DARK, spaceAfter=8),
        "quote": ParagraphStyle("q", parent=ss["Normal"], fontSize=9.5, leading=13, textColor=MUTED, leftIndent=10, fontName="Helvetica-Oblique", spaceAfter=8),
        "code": ParagraphStyle("c", parent=ss["Code"], fontName="Courier", fontSize=8.6, leading=11.4, textColor=DARK),
    }


def code_box(lines, st, width):
    pre = Preformatted("\n".join(esc(l) for l in lines), st["code"])
    tbl = Table([[pre]], colWidths=[width])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("BOX", (0, 0), (-1, -1), 0.75, CODE_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return tbl


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python generate_pack_pdf.py file.md [out.pdf]")
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else src.rsplit(".", 1)[0] + ".pdf"
    st = build_styles()
    md = open(src, encoding="utf-8").read().split("\n")

    doc = SimpleDocTemplate(out, pagesize=letter, leftMargin=0.85 * inch,
                            rightMargin=0.85 * inch, topMargin=0.8 * inch, bottomMargin=0.7 * inch)
    avail = doc.width
    story = []
    in_code, code_lines = False, []

    for line in md:
        if line.strip().startswith("```"):
            if in_code:
                story.append(code_box(code_lines, st, avail))
                story.append(Spacer(1, 8))
                code_lines, in_code = [], False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue

        s = line.strip()
        if not s:
            continue
        if s.startswith("### "):
            story.append(Paragraph(esc(s[4:]), st["subtitle"]))
        elif s.startswith("## "):
            story.append(Paragraph(esc(s[3:]), st["h2"]))
        elif s.startswith("# "):
            story.append(Paragraph(esc(s[2:]), st["title"]))
        elif s.startswith(">"):
            story.append(Paragraph(esc(s.lstrip("> ").strip()), st["quote"]))
        elif s.startswith("---"):
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.5, color=CODE_BORDER))
            story.append(Spacer(1, 4))
        elif s.startswith("*") and s.endswith("*"):
            story.append(Paragraph(esc(s.strip("*")), st["italic"]))
        else:
            # light **bold** handling
            t = esc(s)
            while "**" in t:
                t = t.replace("**", "<b>", 1).replace("**", "</b>", 1)
            story.append(Paragraph(t, st["body"]))

    if in_code and code_lines:
        story.append(code_box(code_lines, st, avail))

    doc.build(story)
    import os
    print(f"wrote {out}  ({os.path.getsize(out)//1024} KB, {len(story)} flowables)")


if __name__ == "__main__":
    main()
