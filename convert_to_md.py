#!/usr/bin/env python3
"""
convert_to_md.py — bulk-convert PDFs / text / Office docs to clean Markdown for
easy Claude ingestion (e.g. triaging a folder of collected lead magnets).

Uses Microsoft's `markitdown` (built for document -> Markdown for LLMs).

Setup (one time):
    pip install "markitdown[all]"

Usage:
    python convert_to_md.py "C:\\path\\to\\lead-magnets"
    python convert_to_md.py "C:\\path\\to\\lead-magnets" --out "C:\\path\\to\\out"

Behavior:
- Walks the source folder recursively for .pdf .txt .md .docx .pptx .html .htm .rtf .csv
- Writes one .md per file into <src>/_md (or --out), mirroring nothing (flat, by stem)
- Idempotent: skips a file whose .md already exists (use --force to redo)
- Flags EMPTY outputs — almost always a scanned/image-only PDF that needs OCR
  (markitdown extracts TEXT; it does not OCR images unless configured)
"""
import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

EXTS = {".pdf", ".txt", ".md", ".docx", ".pptx", ".html", ".htm", ".rtf", ".csv", ".json"}


def main():
    ap = argparse.ArgumentParser(description="Bulk-convert documents to Markdown via markitdown")
    ap.add_argument("src", help="Source folder containing the files to convert")
    ap.add_argument("--out", default=None, help="Output folder (default: <src>/_md)")
    ap.add_argument("--force", action="store_true", help="Re-convert even if the .md already exists")
    args = ap.parse_args()

    try:
        from markitdown import MarkItDown
    except ImportError:
        sys.exit('[error] markitdown not installed. Run:  pip install "markitdown[all]"')

    src = Path(args.src).expanduser().resolve()
    if not src.is_dir():
        sys.exit(f"[error] Source folder not found: {src}")
    out = Path(args.out).resolve() if args.out else (src / "_md")
    out.mkdir(parents=True, exist_ok=True)

    md = MarkItDown()
    files = [f for f in src.rglob("*") if f.is_file() and f.suffix.lower() in EXTS and out not in f.parents]
    print(f"Found {len(files)} convertible file(s). Output -> {out}\n")

    ok = empty = failed = skipped = 0
    empties = []
    for f in sorted(files):
        target = out / (f.stem + ".md")
        if target.exists() and not args.force:
            skipped += 1
            continue
        try:
            text = (md.convert(str(f)).text_content or "").strip()
            target.write_text(text, encoding="utf-8")
            if len(text) < 20:  # essentially nothing extracted
                empty += 1
                empties.append(f.name)
                print(f"  [EMPTY] {f.name}  (likely scanned/image PDF -> needs OCR)")
            else:
                ok += 1
                print(f"  [OK]    {f.name}  ({len(text):,} chars)")
        except Exception as e:
            failed += 1
            print(f"  [FAIL]  {f.name}  -> {e}")

    print("\n" + "-" * 50)
    print(f"Converted: {ok}   Empty/needs-OCR: {empty}   Failed: {failed}   Skipped(existing): {skipped}")
    if empties:
        print("\nThese came out empty (scanned/image PDFs — separate OCR pass needed):")
        for n in empties:
            print(f"  - {n}")
    print(f"\nMarkdown is in: {out}")


if __name__ == "__main__":
    main()
