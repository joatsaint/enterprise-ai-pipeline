#!/usr/bin/env python3
"""
generate_post_images.py — content-engine/

Generates casual square images for daily LinkedIn posts.
Reads IMAGE PROMPT sections from post.md files and calls the
OpenAI Responses API (gpt-4o + image_generation tool).

Usage
-----
  python generate_post_images.py week-of-2026-06-08
  python generate_post_images.py week-of-2026-06-08 --dry-run
"""

import argparse
import base64
import re
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE    = Path(__file__).resolve().parent
PENDING = HERE / "pending" / "weekly-posts"


def extract_image_prompt(post_md: Path) -> str | None:
    text = post_md.read_text("utf-8", errors="replace")
    match = re.search(
        r"## IMAGE PROMPT.*?\n+(.*?)(?:\n---|\Z)",
        text,
        re.DOTALL,
    )
    if not match:
        return None
    return match.group(1).strip()


def generate_image(client, prompt: str) -> bytes | None:
    try:
        response = client.responses.create(
            model="gpt-4o",
            input=prompt,
            tools=[{
                "type": "image_generation",
                "quality": "high",
                "size": "1024x1024",
            }],
        )
        for item in response.output:
            if item.type == "image_generation_call":
                return base64.b64decode(item.result)
        print("  [warn] No image_generation_call in response")
        return None
    except Exception as e:
        print(f"  [error] {e}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("week", help="Week folder name, e.g. week-of-2026-06-08")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print prompts only, do not call API")
    args = parser.parse_args()

    week_dir = PENDING / args.week
    if not week_dir.exists():
        sys.exit(f"[error] Week folder not found: {week_dir}")

    post_dirs = sorted(week_dir.iterdir())
    if not post_dirs:
        sys.exit(f"[error] No day folders found in {week_dir}")

    if args.dry_run:
        print(f"\n[dry-run] Week: {args.week}\n")
        for day_dir in post_dirs:
            post_md = day_dir / "post.md"
            if not post_md.exists():
                print(f"  [skip] {day_dir.name} — no post.md")
                continue
            prompt = extract_image_prompt(post_md)
            if not prompt:
                print(f"  [skip] {day_dir.name} — no IMAGE PROMPT section found")
                continue
            print(f"  [{day_dir.name}]\n  {prompt[:120]}...\n")
        return

    from dotenv import load_dotenv
    load_dotenv(HERE.parent / ".env")
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.exit("[error] OPENAI_API_KEY not set in .env")

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    total = sum(1 for d in post_dirs if (d / "post.md").exists())
    done = 0

    print(f"\n[start] Generating {total} images for {args.week}\n")

    for day_dir in post_dirs:
        post_md = day_dir / "post.md"
        if not post_md.exists():
            print(f"  [skip] {day_dir.name} — no post.md")
            continue

        out_path = day_dir / "image.png"
        if out_path.exists():
            print(f"  [skip] {day_dir.name} — image.png already exists")
            done += 1
            continue

        prompt = extract_image_prompt(post_md)
        if not prompt:
            print(f"  [skip] {day_dir.name} — IMAGE PROMPT section not found")
            continue

        print(f"  [gen]  {day_dir.name}...", end=" ", flush=True)
        img_bytes = generate_image(client, prompt)

        if img_bytes:
            out_path.write_bytes(img_bytes)
            size_kb = len(img_bytes) // 1024
            print(f"saved ({size_kb}KB) -> image.png")
            done += 1
        else:
            print("failed — skipping")

        if done < total:
            time.sleep(3)

    print(f"\n[done] {done}/{total} images generated in {week_dir}\n")


if __name__ == "__main__":
    main()
