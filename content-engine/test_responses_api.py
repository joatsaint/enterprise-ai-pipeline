#!/usr/bin/env python3
"""
test_responses_api.py — content-engine/

Two-image quality test using the OpenAI Responses API with the
image_generation tool. This is the same internal path ChatGPT uses:
gpt-4o interprets and enhances the prompt, then calls the image generator.
Contrast: images.generate() sends the prompt directly with no enhancement.

Generates slides 1 and 2 from ART6 and saves as:
  images/01_hook_RESPONSES.png
  images/02_problem_RESPONSES.png

Compare side-by-side against the existing 01_hook.png / 02_problem.png.
"""

import base64
import io
import json
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE      = Path(__file__).resolve().parent
ROOT      = HERE.parent
BRAND_DIR = ROOT / "docs" / "ChatGPT - LinkedIn Content Creation Prompts and Playbook"
PENDING   = HERE / "pending"
MASTER_STYLE_FILE = BRAND_DIR / "ChatGPT Prompt Image Generation for Claude Code.txt"

FONT_CANDIDATES = [
    "C:\\Windows\\Fonts\\impact.ttf",
    "C:\\Windows\\Fonts\\arialbd.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
]

TARGET_W, TARGET_H, BORDER = 1080, 1350, 36
FONT_SIZE_BASE = 52

SLUG = "ART6-from-no-to-safe-enough-yes"


def load_dotenv_env():
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text("utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        if key.strip() not in os.environ:
            os.environ[key.strip()] = val.strip()


def load_master_style() -> str:
    with open(str(MASTER_STYLE_FILE), "r", encoding="utf-8", errors="replace") as fh:
        return fh.read().strip()


def load_production_sheet() -> list[dict]:
    """Pull the already-generated storyboard from the production sheet JSON-adjacent data.
    We re-read carousel_production_sheet.md and extract slide 1 and 2 scene data,
    OR re-call Gemini if the sheet is missing."""
    sheet = PENDING / SLUG / "carousel_production_sheet.md"
    if not sheet.exists():
        sys.exit("[error] Run generate_carousel_images.py --prompts-only first to build the storyboard.")
    # The storyboard JSON is regenerated fresh — cheaper than parsing the md
    return None  # signals caller to regenerate


def post_process_image(img_bytes: bytes, overlay_text: str,
                       placement: str = "lower third") -> bytes:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return img_bytes

    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    inner_w = TARGET_W - BORDER * 2
    inner_h = TARGET_H - BORDER * 2
    scale = max(inner_w / img.width, inner_h / img.height)
    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    left = (img.width - inner_w) // 2
    top  = (img.height - inner_h) // 2
    img = img.crop((left, top, left + inner_w, top + inner_h))

    canvas = Image.new("RGB", (TARGET_W, TARGET_H), (255, 255, 255))
    canvas.paste(img, (BORDER, BORDER))

    if not overlay_text:
        out = io.BytesIO()
        canvas.save(out, format="PNG")
        return out.getvalue()

    canvas_rgba = canvas.convert("RGBA")
    zone_h = TARGET_H // 3
    zone_top = TARGET_H - zone_h if placement != "top third" else BORDER

    gradient = Image.new("RGBA", (TARGET_W, zone_h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gradient)
    for y in range(zone_h):
        alpha = int(200 * (y / zone_h)) if placement != "top third" else int(200 * (1 - y / zone_h))
        gd.line([(0, y), (TARGET_W, y)], fill=(0, 0, 0, alpha))
    canvas_rgba.paste(gradient, (0, zone_top), gradient)
    canvas = canvas_rgba.convert("RGB")

    font_size = int(TARGET_W * FONT_SIZE_BASE / 1080)
    font = None
    try:
        from PIL import ImageFont
        for fp in FONT_CANDIDATES:
            if Path(fp).exists():
                try:
                    font = ImageFont.truetype(fp, font_size)
                    break
                except Exception:
                    pass
        if font is None:
            font = ImageFont.load_default()
    except Exception:
        pass

    draw = ImageDraw.Draw(canvas)
    words = overlay_text.upper().split()
    lines, current = [], []
    max_w = inner_w - BORDER * 2
    for word in words:
        test = " ".join(current + [word])
        bw = font.getbbox(test)[2] if (font and hasattr(font, "getbbox")) else len(test) * font_size * 0.6
        if bw <= max_w:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))

    lh = font_size + 10
    ty = zone_top + (zone_h - len(lines) * lh) // 2
    for line in lines:
        tw = font.getbbox(line)[2] if (font and hasattr(font, "getbbox")) else len(line) * font_size * 0.6
        tx = (TARGET_W - tw) // 2
        draw.text((tx + 2, ty + 2), line, font=font, fill=(0, 0, 0))
        draw.text((tx, ty), line, font=font, fill=(255, 255, 255))
        ty += lh

    out = io.BytesIO()
    canvas.save(out, format="PNG")
    return out.getvalue()


def generate_via_responses_api(client, prompt: str) -> bytes | None:
    """
    Use the Responses API with the image_generation tool.
    gpt-4o acts as orchestrator — it interprets and enhances the prompt
    before calling the image generator. This mirrors the ChatGPT internal path.
    """
    try:
        response = client.responses.create(
            model="gpt-4o",
            input=prompt,
            tools=[{
                "type": "image_generation",
                "quality": "high",
                "size": "1024x1536",
            }],
        )
        for item in response.output:
            if item.type == "image_generation_call":
                return base64.b64decode(item.result)
        print("  [warn] No image_generation_call in response output")
        return None
    except Exception as e:
        print(f"  [error] Responses API failed: {e}")
        return None


def main():
    load_dotenv_env()

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        sys.exit("[error] OPENAI_API_KEY not found in .env")

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        sys.exit("[error] GEMINI_API_KEY not found in .env")

    import openai as openai_lib
    from google import genai

    client      = openai_lib.OpenAI(api_key=openai_key)
    gemini      = genai.Client(api_key=gemini_key)
    master_style = load_master_style()
    images_dir  = PENDING / SLUG / "images"
    images_dir.mkdir(exist_ok=True)

    # Regenerate storyboard for slides 1-2
    carousel_text = (PENDING / SLUG / "carousel.md").read_text("utf-8")

    storyboard_prompt = f"""\
You are the visual director for Randy Skiles' LinkedIn brand. Generate a storyboard
for the first TWO slides of this carousel only. Output a JSON array of exactly 2 objects.

For each slide, output these keys:
  slide_number, scene_archetype, scene_description (5-7 rich sentences — every prop,
  every texture, every environmental detail), operator_action, overlay_text (3-8 words),
  stapler_placement, optional_easter_eggs, text_placement, negative_space_note

Make the scene descriptions EXTREMELY DETAILED and PHOTOREALISTIC. Include specific props:
what is on the desk, what the screens show, the exact state of the room, weather outside,
specific labels on mugs or sticky notes, the Operator's exact posture and expression.
The description should read like a cinematographer's shot list.

Archetypes available: Hurricane Motel Command Center, Enterprise War Room,
Jenga Dependency Collapse, Empty Bob Chair, Permission Gate, Approval Console,
Shadow AI Server Rack, Castle Moat / Trust Fortress.

Output ONLY valid JSON array. No fences. No explanation.

CAROUSEL COPY:
{carousel_text[:3000]}"""

    print("[storyboard] Generating detailed 2-slide storyboard...", end=" ", flush=True)
    r = gemini.models.generate_content(model="gemini-2.5-flash", contents=storyboard_prompt)
    raw = r.text.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    slides = json.loads(raw.strip())
    print(f"done ({len(slides)} slides)")

    for i, slide in enumerate(slides[:2], 1):
        num     = slide.get("slide_number", i)
        overlay = slide.get("overlay_text", "")
        placement = slide.get("text_placement", "lower third")

        # Build rich prompt: master style + highly detailed scene
        scene_desc  = slide.get("scene_description", "")
        op_action   = slide.get("operator_action", "")
        stapler     = slide.get("stapler_placement", "")
        easter_eggs = slide.get("optional_easter_eggs", [])
        neg_space   = slide.get("negative_space_note", "lower third")

        prompt_parts = [
            master_style,
            "\n\n--- SCENE DIRECTION ---",
            f"Scene archetype: {slide.get('scene_archetype', '')}",
            f"\nDetailed scene (every prop, texture, and environmental detail matters):\n{scene_desc}",
            f"\nThe Operator's action: {op_action}",
        ]
        if stapler:
            prompt_parts.append(f"\nHide the red Swingline stapler: {stapler}")
        if easter_eggs:
            prompt_parts.append(f"\nInclude naturally: {', '.join(easter_eggs)}")
        prompt_parts.append(
            f"\nLeave clean dark negative space in the {neg_space} — "
            f"no faces, hands, or props in that zone. "
            f"DO NOT render any text, headline, or caption in the image. "
            f"Text is added in post-processing."
        )
        prompt_parts.append("\nFormat: 1024 x 1536 px vertical. Maximum photorealistic detail.")
        full_prompt = "\n".join(prompt_parts)

        out_path = images_dir / f"{num:02d}_slide{num}_RESPONSES.png"
        print(f"\n[{i}/2] Slide {num} via Responses API...", end=" ", flush=True)

        raw_bytes = generate_via_responses_api(client, full_prompt)

        if raw_bytes:
            final = post_process_image(raw_bytes, overlay, placement)
            out_path.write_bytes(final)
            print(f"saved -> {out_path.name} ({len(final)//1024}KB)")
        else:
            print(f"failed")

    print("\n[done] Check images/ folder:")
    print(f"  Compare 01_hook.png vs 01_slide1_RESPONSES.png")
    print(f"  Compare 02_problem.png vs 02_slide2_RESPONSES.png")
    print(f"  Folder: {images_dir}")


if __name__ == "__main__":
    main()
