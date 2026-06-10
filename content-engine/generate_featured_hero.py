#!/usr/bin/env python3
"""
generate_featured_hero.py — content-engine/

One-off landscape hero image generator for the standalone FEATURED article
("From Burned OUT! to Fired UP!"), which lives outside the pending/{slug}/
carousel pipeline. Reuses gpt-image-1 generation + font loading from
generate_carousel_images.py.

Usage:
  python generate_featured_hero.py
"""

import io
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from generate_carousel_images import generate_image, load_dotenv_env, FONT_CANDIDATES

OUT_DIR = HERE / "pending" / "FEATURED-burned-out-to-fired-up" / "images"

TITLE_LINES = ["FROM BURNED OUT!", "TO FIRED UP!"]
SUBTITLE = "Randy & Claude Code's Excellent Agentic Adventure"

PROMPT = """\
A late-night home IT office, cinematic documentary photography style. Multiple
monitors glow with cool electric-blue light, displaying active dashboards,
scrolling terminal logs, and automation pipelines clearly running on their own
— no one at the desk. A handwritten sticky note stuck to the edge of one
monitor reads "Don't touch — it's working." The office chair sits empty,
pushed back at an angle, as if someone just stood up and walked away. In the
soft-focus background, a GenX man in his 50s — flannel shirt, reading glasses
pushed up on his head — walks toward a sunlit window with a coffee mug in
hand, relaxed, not looking back at the screens. Cool electric-blue monitor
glow contrasts with warm golden morning light from the window. Realistic,
editorial photography quality, cinematic lighting, subtle humor in the
contrast between the busy screens and the calm departing figure. Leave a
clean, dark, uncluttered zone across the lower third of the frame — floor and
shadow area, free of key details and free of any text — for a text overlay to
be added separately in post-processing. Landscape orientation, 1536x1024.
"""


def _load_font(size: int):
    from PIL import ImageFont
    for fp in FONT_CANDIDATES:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def post_process(img_bytes: bytes) -> bytes:
    from PIL import Image, ImageDraw

    target_w, target_h, border = 1376, 768, 28
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    inner_w = target_w - border * 2
    inner_h = target_h - border * 2
    scale = max(inner_w / img.width, inner_h / img.height)
    new_w, new_h = int(img.width * scale), int(img.height * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    left = (new_w - inner_w) // 2
    top = (new_h - inner_h) // 2
    img = img.crop((left, top, left + inner_w, top + inner_h))

    canvas = Image.new("RGB", (target_w, target_h), (255, 255, 255))
    canvas.paste(img, (border, border))

    # Dark gradient across the lower third for the text overlay
    canvas_rgba = canvas.convert("RGBA")
    zone_height = target_h // 3
    zone_top = target_h - zone_height
    gradient = Image.new("RGBA", (target_w, zone_height), (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(gradient)
    for y in range(zone_height):
        alpha = int(190 * (y / zone_height))
        grad_draw.line([(0, y), (target_w, y)], fill=(0, 0, 0, alpha))
    canvas_rgba.paste(gradient, (0, zone_top), gradient)
    canvas = canvas_rgba.convert("RGB")

    draw = ImageDraw.Draw(canvas)
    title_font = _load_font(76)
    subtitle_font = _load_font(36)

    title_line_h = 88
    subtitle_h = 44
    total_h = len(TITLE_LINES) * title_line_h + subtitle_h + 12
    y = zone_top + (zone_height - total_h) // 2

    for line in TITLE_LINES:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        w = bbox[2] - bbox[0]
        x = (target_w - w) // 2
        draw.text((x + 2, y + 2), line, font=title_font, fill=(0, 0, 0))
        draw.text((x, y), line, font=title_font, fill=(255, 255, 255))
        y += title_line_h

    y += 12
    bbox = draw.textbbox((0, 0), SUBTITLE, font=subtitle_font)
    w = bbox[2] - bbox[0]
    x = (target_w - w) // 2
    draw.text((x + 1, y + 1), SUBTITLE, font=subtitle_font, fill=(0, 0, 0))
    draw.text((x, y), SUBTITLE, font=subtitle_font, fill=(0, 150, 240))

    out = io.BytesIO()
    canvas.save(out, format="PNG")
    return out.getvalue()


def main():
    load_dotenv_env()
    import os
    import openai as openai_lib

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        sys.exit("[error] OPENAI_API_KEY not found in .env")

    client = openai_lib.OpenAI(api_key=openai_key)

    print("[hero] Generating FEATURED article hero image (1536x1024)...", end=" ", flush=True)
    raw_bytes = generate_image(client, PROMPT, size="1536x1024")
    if not raw_bytes:
        sys.exit("\n[error] Image generation failed")
    print("done")

    final_bytes = post_process(raw_bytes)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "00_hero.png"
    out_path.write_bytes(final_bytes)
    print(f"[ok] Saved -> {out_path}")
    print(f"[ok] Final size: 1376x768 with 28px white border, text overlay applied")


if __name__ == "__main__":
    main()
