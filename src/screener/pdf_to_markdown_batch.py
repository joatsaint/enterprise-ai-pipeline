"""
Batch PDF -> plain-text markdown converter, local only, zero API cost.

Extracts the text layer from every .pdf in a folder via pdfplumber (same
technique src/screener/screener.py uses) and writes a sibling .md file next
to each source PDF. Image-only PDFs will come back empty/near-empty -- there
is no OCR step here, this is text-layer extraction only.

Idempotent: skips any PDF that already has a matching .md file, so it's safe
to re-run after dropping new PDFs into the folder.

Usage:
    python -m src.screener.pdf_to_markdown_batch "docs/AI Free PDFs from AI Youtubers"
"""
from __future__ import annotations

import sys
from pathlib import Path

import pdfplumber


def convert_folder(folder: Path) -> None:
    pdfs = sorted(folder.glob("*.pdf"))
    if not pdfs:
        print(f"No .pdf files found in {folder}")
        return

    converted, skipped, failed = 0, 0, 0

    for pdf_path in pdfs:
        md_path = pdf_path.with_suffix(".md")
        if md_path.exists():
            print(f"skip (already converted): {pdf_path.name}")
            skipped += 1
            continue

        try:
            with pdfplumber.open(pdf_path) as pdf:
                pages_text = [page.extract_text() or "" for page in pdf.pages]
            text = "\n\n".join(pages_text).strip()

            if not text:
                note = (
                    f"# {pdf_path.stem}\n\n"
                    f"_No extractable text found -- this PDF is likely image-only "
                    f"(scanned pages or design graphics), not selectable text._\n"
                )
                md_path.write_text(note, encoding="utf-8")
                print(f"empty (image-only, no text layer): {pdf_path.name}")
            else:
                header = f"# {pdf_path.stem}\n\n"
                md_path.write_text(header + text, encoding="utf-8")
                print(f"converted: {pdf_path.name} ({len(text):,} chars)")
            converted += 1
        except Exception as e:
            print(f"FAILED: {pdf_path.name} -- {e}")
            failed += 1

    print(
        f"\nDone. Converted: {converted}  Skipped (already done): {skipped}  Failed: {failed}"
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.screener.pdf_to_markdown_batch <folder>")
        sys.exit(1)
    convert_folder(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
