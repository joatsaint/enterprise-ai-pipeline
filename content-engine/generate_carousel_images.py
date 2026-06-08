#!/usr/bin/env python3
"""
generate_carousel_images.py  — content-engine/

Two-pass pipeline:
  Pass 1 — Gemini 2.5 Flash builds a visual storyboard (scene archetypes,
            operator actions, emotional jobs) using the full brand bible.
  Pass 2 — gpt-image-1 generates clean cinematic scenes with NO embedded text.
            Pillow adds the white border, lower-third gradient, and typography
            deterministically so text is always crisp and consistent.

Usage
-----
  python generate_carousel_images.py ART6-from-no-to-safe-enough-yes
  python generate_carousel_images.py ART6-from-no-to-safe-enough-yes --prompts-only
  python generate_carousel_images.py ART6-from-no-to-safe-enough-yes --hero
"""

import argparse
import base64
import io
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE      = Path(__file__).resolve().parent
ROOT      = HERE.parent
BRAND_DIR = ROOT / "docs" / "ChatGPT - LinkedIn Content Creation Prompts and Playbook"
PENDING   = HERE / "pending"

MASTER_STYLE_FILE = BRAND_DIR / "ChatGPT Prompt Image Generation for Claude Code.txt"

# Windows system fonts — Impact is the canonical brand condensed face
FONT_CANDIDATES = [
    "C:\\Windows\\Fonts\\impact.ttf",
    "C:\\Windows\\Fonts\\arialbd.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
]

SLIDE_NAMES = {
    1: "hook", 2: "problem", 3: "mistake", 4: "operator",
    5: "turn",  6: "reveal", 7: "recognition", 8: "lesson_cta",
}

# LinkedIn carousel final dimensions
CAROUSEL_W, CAROUSEL_H = 1080, 1350
BORDER_PX = 36        # white documentary border
FONT_SIZE_BASE = 52   # baseline — scales with image width


# ---------------------------------------------------------------------------
# Brand loading
# ---------------------------------------------------------------------------

def load_master_style() -> str:
    if not MASTER_STYLE_FILE.exists():
        sys.exit(f"[error] Master style file not found: {MASTER_STYLE_FILE}")
    try:
        with open(str(MASTER_STYLE_FILE), "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read()
        print(f"  [style] Loaded: {MASTER_STYLE_FILE.name}")
        return content.strip()
    except OSError as e:
        sys.exit(f"[error] Could not read master style file: {e}")


def load_brand_context() -> str:
    parts = []
    if not BRAND_DIR.exists():
        return ""
    for f in sorted(BRAND_DIR.glob("*.md")):
        kw = ["master_linkedin_image_system", "sysadmin_ai_visual_brand_bible"]
        if not any(k in f.name.lower() for k in kw):
            continue
        try:
            with open(str(f), "r", encoding="utf-8", errors="replace") as fh:
                parts.append(fh.read())
            print(f"  [brand] Loaded: {f.name}")
        except OSError as e:
            print(f"  [warn] Could not read {f.name}: {e}")
    return "\n\n---\n\n".join(parts)


def load_carousel(slug: str) -> tuple[Path, str]:
    article_dir = PENDING / slug
    if not article_dir.exists():
        sys.exit(f"[error] Article folder not found: {article_dir}")
    carousel_file = article_dir / "carousel.md"
    if not carousel_file.exists():
        sys.exit(f"[error] carousel.md not found in {slug}/")
    text = carousel_file.read_text("utf-8").strip()
    if "(content here)" in text or not text.replace("## CAROUSEL", "").strip():
        sys.exit(f"[error] carousel.md for {slug} is empty — add slide copy first.")
    return article_dir, text


# ---------------------------------------------------------------------------
# Storyboard (Gemini — scene selection + operator action only)
# ---------------------------------------------------------------------------

STORYBOARD_SYSTEM = """\
You are the visual director for Randy Skiles' LinkedIn brand system.

Your job: for each carousel slide, choose the strongest visual scene and output
the slide-specific details used to build the image prompt. You do NOT write style
rules, lighting, color grades, or character descriptions — those come from the
master style block automatically.

CRITICAL: Images will be generated WITHOUT embedded text. A separate post-processing
step adds the text overlay. Your job is to design a scene that works WITHOUT any text
on it — the visual metaphor must stand alone.

The most important question for every slide:
"What is The Operator DOING that proves experience matters?"
He must always have a clear operational role: gatekeeper, reviewer, approver,
diagnostician, stabilizer, translator, or controller.

BRAND CONTEXT (for scene selection guidance):
{brand_context}

SCENE ARCHETYPES — choose the best fit for each slide:
1. Hurricane Motel Command Center — Operator runs enterprise IT from a cheap motel during a storm
2. Enterprise War Room — Conference room with dashboards, outage alerts, Operator calm amid chaos
3. Jenga Dependency Collapse — Jenga tower of labeled enterprise dependencies collapsing (DNS, Active Directory, Change Control, Bob, Print Server, Backups, Service Account)
4. Empty Bob Chair — AI command room frozen because Bob's institutional knowledge is absent
5. Permission Gate — AI workflow waiting behind locked enterprise security checkpoint (PII, PROD, HR DATA, FINANCE, IDENTITY); Operator with clipboard and access badge
6. Approval Console — Operator reviewing AI workflow screen with APPROVE / HOLD / ESCALATE / ROLLBACK / HUMAN REVIEW REQUIRED buttons
7. Shadow AI Server Rack — Dark server room, open racks, unauthorized systems labeled Shadow AI / Data Leak / Hallucination / Prompt Injection
8. Castle Moat / Trust Fortress — Secure grounded business fortress representing trust, accountability, expertise

APPROVED STAPLER LOCATIONS (choose one, write as a complete natural-language sentence):
- half-hidden behind a coffee mug on the checkpoint desk
- partly covered by printed approval forms on the far edge of the conference table
- tucked beside a mechanical keyboard on the desk
- nestled under the edge of an old runbook binder on the shelf
- partly buried under fallen Jenga blocks near the corner
- reflected faintly in server rack glass near floor level
- tucked inside a cable bag on the floor beside the desk
- on Bob's empty desk chair, half under a stack of printouts

OPTIONAL EASTER EGGS (use 0-2, only if they fit naturally):
orange towel, rubber duck, old pager, floppy disk, CRT monitor, Cisco console cable,
pizza box, Dr Pepper-style soda can, sticky note reading "Rollback Plan?",
sticky note reading "Ask Bob", sticky note reading "Temporary since 2014",
whiteboard reading "The Full Monty", coffee mug reading "Systems Don't Sleep",
coffee mug reading "Caffeine / Sarcasm / Uptime"

Output a JSON array — one object per slide — with EXACTLY these keys:
  slide_number         (int)
  slide_title          (string, 2-5 words)
  emotional_job        (string: one word — curiosity, recognition, stress, validation, hope, etc.)
  viewer_takeaway      (string: one sentence — what the viewer thinks after seeing this image)
  scene_archetype      (string: name from list above, or "custom")
  scene_description    (string: 4-6 sentences — who, what, where, story tension, what catches the eye)
  operator_action      (string: one sentence — exactly what The Operator is doing that proves experience matters)
  overlay_text         (string: 3-8 words, high-impact, drawn directly from slide copy — this will be added by code, NOT by the image generator)
  stapler_placement    (string: complete natural-language sentence from approved list)
  optional_easter_eggs (array of 0-2 strings)
  text_placement       (string: "lower third", "left side", or "top third")
  negative_space_note  (string: where in the image to leave clean dark area for the text overlay)

Output ONLY the JSON array. No markdown fences. No explanation. Start with [ end with ]."""


def generate_storyboard(client, brand_context: str, carousel_text: str) -> list[dict]:
    prompt = STORYBOARD_SYSTEM.format(brand_context=brand_context)
    full_input = f"{prompt}\n\nCARROUSEL SLIDE COPY:\n{carousel_text}"

    print("[storyboard] Calling Gemini 2.5 Flash...", end=" ", flush=True)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_input,
    )
    print("done")

    raw = response.text.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    raw = raw.strip()

    try:
        slides = json.loads(raw)
        if not isinstance(slides, list):
            raise ValueError("Expected a JSON array")
        return slides
    except (json.JSONDecodeError, ValueError) as e:
        print(f"\n[error] Could not parse storyboard JSON: {e}")
        print(f"[debug] First 600 chars of response:\n{raw[:600]}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Prompt assembly — master style + scene details, NO text rendering
# ---------------------------------------------------------------------------

def build_image_prompt(master_style: str, scene: dict, portrait: bool = True) -> str:
    """
    Full production prompt = master style block + slide-specific scene direction.
    Text overlay is NEVER asked of the image generator — handled by post_process_image.
    """
    parts = [master_style]

    archetype      = scene.get("scene_archetype", "")
    scene_desc     = scene.get("scene_description", "")
    operator_action = scene.get("operator_action", "")
    stapler        = scene.get("stapler_placement", "")
    easter_eggs    = scene.get("optional_easter_eggs", [])
    negative_space = scene.get("negative_space_note", "")
    viewer_takeaway = scene.get("viewer_takeaway", "")
    emotional_job  = scene.get("emotional_job", "")

    parts.append("\n\n--- SCENE DIRECTION FOR THIS SLIDE ---")

    if emotional_job:
        parts.append(f"Emotional job: {emotional_job}.")
    if viewer_takeaway:
        parts.append(f"Viewer takeaway: {viewer_takeaway}")

    if archetype and archetype.lower() != "custom":
        parts.append(f"\nUse the '{archetype}' scene archetype as the visual foundation.")

    if scene_desc:
        parts.append(f"\nScene: {scene_desc}")

    if operator_action:
        parts.append(f"\nThe Operator's action: {operator_action}")

    if stapler:
        parts.append(
            f"\nHide the red stapler: {stapler} — one stapler only, never centered, "
            f"never spotlit, visible only on careful inspection."
        )

    if easter_eggs:
        parts.append(f"\nInclude these details naturally if they fit: {', '.join(easter_eggs)}")

    # Critical: NO text in the generated image
    if negative_space:
        parts.append(
            f"\nLeave clean negative space — a dark uncluttered zone — in the {negative_space}. "
            f"Text will be added in post-processing. Do NOT render any headline, overlay, "
            f"or caption text in the generated image."
        )
    else:
        parts.append(
            "\nLeave clean negative space in the lower third of the image — a dark, "
            "uncluttered zone free of faces, hands, or key props. "
            "Text will be added in post-processing. Do NOT render any headline, overlay, "
            "or caption text in the generated image."
        )

    size = "1024 x 1536 px vertical portrait" if portrait else "1536 x 1024 px landscape"
    parts.append(f"\nFormat: {size}. No embedded text. Strong cinematic composition.")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Post-processing — border + gradient + typography via Pillow
# ---------------------------------------------------------------------------

def _load_font(size: int):
    try:
        from PIL import ImageFont
        for fp in FONT_CANDIDATES:
            if Path(fp).exists():
                try:
                    return ImageFont.truetype(fp, size)
                except Exception:
                    continue
        return ImageFont.load_default()
    except ImportError:
        return None


def post_process_image(
    img_bytes: bytes,
    overlay_text: str,
    placement: str = "lower third",
    target_w: int = CAROUSEL_W,
    target_h: int = CAROUSEL_H,
    border: int = BORDER_PX,
) -> bytes:
    """
    Add white border + dark gradient + bold text overlay.
    Resize/crop to final LinkedIn carousel dimensions.
    Returns PNG bytes.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("[warn] Pillow not installed — skipping post-processing (pip install pillow)")
        return img_bytes

    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    # --- Resize to fill target dimensions (cover, not stretch) ---
    inner_w = target_w - border * 2
    inner_h = target_h - border * 2
    scale = max(inner_w / img.width, inner_h / img.height)
    new_w = int(img.width * scale)
    new_h = int(img.height * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    # Center crop
    left = (new_w - inner_w) // 2
    top  = (new_h - inner_h) // 2
    img = img.crop((left, top, left + inner_w, top + inner_h))

    # --- Add white border ---
    canvas = Image.new("RGB", (target_w, target_h), (255, 255, 255))
    canvas.paste(img, (border, border))

    if not overlay_text:
        out = io.BytesIO()
        canvas.save(out, format="PNG")
        return out.getvalue()

    # --- Dark gradient in text zone ---
    canvas_rgba = canvas.convert("RGBA")

    # Determine text zone position
    zone_height = target_h // 3
    if placement == "top third":
        zone_top = border
    elif placement == "left side":
        zone_top = border + (inner_h // 4)
        zone_height = inner_h // 2
    else:  # lower third (default)
        zone_top = target_h - zone_height

    gradient = Image.new("RGBA", (target_w, zone_height), (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(gradient)
    for y in range(zone_height):
        if placement == "top third":
            alpha = int(200 * (1 - y / zone_height))
        else:
            alpha = int(200 * (y / zone_height))
        grad_draw.line([(0, y), (target_w, y)], fill=(0, 0, 0, alpha))

    canvas_rgba.paste(gradient, (0, zone_top), gradient)
    canvas = canvas_rgba.convert("RGB")

    # --- Typography ---
    font_size = int(target_w * FONT_SIZE_BASE / 1080)
    font = _load_font(font_size)

    draw = ImageDraw.Draw(canvas)

    # Word-wrap
    words = overlay_text.upper().split()
    lines = []
    current: list[str] = []
    max_line_w = inner_w - border * 2
    for word in words:
        test = " ".join(current + [word])
        if font and hasattr(font, "getbbox"):
            bbox = font.getbbox(test)
            line_w = bbox[2] - bbox[0]
        else:
            line_w = len(test) * font_size * 0.6
        if line_w <= max_line_w:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))

    line_h = font_size + 10
    total_text_h = len(lines) * line_h
    text_start_y = zone_top + (zone_height - total_text_h) // 2
    text_start_y = max(text_start_y, zone_top + 12)

    for line in lines:
        if font and hasattr(font, "getbbox"):
            bbox = font.getbbox(line)
            text_w = bbox[2] - bbox[0]
        else:
            text_w = len(line) * font_size * 0.6
        text_x = (target_w - text_w) // 2

        # Drop shadow
        draw.text((text_x + 2, text_start_y + 2), line, font=font, fill=(0, 0, 0))
        # White text
        draw.text((text_x, text_start_y), line, font=font, fill=(255, 255, 255))
        text_start_y += line_h

    out = io.BytesIO()
    canvas.save(out, format="PNG")
    return out.getvalue()


# ---------------------------------------------------------------------------
# Production sheet
# ---------------------------------------------------------------------------

def save_production_sheet(article_dir: Path, slides: list[dict], built_prompts: list[str], slug: str):
    lines = [
        f"# Carousel Production Sheet — {slug}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Slides: {len(slides)}",
        "",
    ]
    for s, prompt in zip(slides, built_prompts):
        n = s.get("slide_number", "?")
        lines += [
            "---",
            f"## Slide {n} — {s.get('slide_title', '')}",
            f"**Emotional job:** {s.get('emotional_job', '')}",
            f"**Viewer takeaway:** {s.get('viewer_takeaway', '')}",
            f"**Archetype:** {s.get('scene_archetype', '')}",
            f"**Operator action:** {s.get('operator_action', '')}",
            f"**Overlay text:** _{s.get('overlay_text', '')}_",
            f"**Text placement:** {s.get('text_placement', '')}",
            f"**Stapler:** {s.get('stapler_placement', '')}",
            f"**Easter eggs:** {', '.join(s.get('optional_easter_eggs', [])) or 'none'}",
            "",
            "**Scene:**",
            s.get("scene_description", ""),
            "",
            "**Full Image Prompt (sent to gpt-image-1):**",
            "",
            prompt,
            "",
        ]
    out = article_dir / "carousel_production_sheet.md"
    out.write_text("\n".join(lines), "utf-8")
    print(f"[ok] Production sheet -> {out.name}")


# ---------------------------------------------------------------------------
# Image generation
# ---------------------------------------------------------------------------

def generate_image(openai_client, prompt: str, size: str = "1024x1536") -> bytes | None:
    """
    Use the Responses API with gpt-4o as orchestrator + image_generation tool.
    gpt-4o interprets and enhances the prompt before calling the image generator —
    the same internal path ChatGPT uses, producing the rich photorealistic quality.
    """
    try:
        response = openai_client.responses.create(
            model="gpt-4o",
            input=prompt,
            tools=[{
                "type": "image_generation",
                "quality": "high",
                "size": size,
            }],
        )
        for item in response.output:
            if item.type == "image_generation_call":
                return base64.b64decode(item.result)
        print("failed — no image_generation_call in response")
        return None
    except Exception as e:
        print(f"failed — {e}")
        return None


def generate_hero_image(gemini_client, openai_client, article_dir: Path,
                        master_style: str, brand_context: str, carousel_text: str):
    print("\n[hero] Generating article hero image (landscape)...")

    hero_request = (
        f"{STORYBOARD_SYSTEM.format(brand_context=brand_context)}\n\n"
        "Generate ONE hero image scene for this article. Output a single JSON object "
        "(not an array) with keys: scene_archetype, scene_description, operator_action, "
        "overlay_text, stapler_placement, optional_easter_eggs, text_placement, "
        "negative_space_note, emotional_job, viewer_takeaway.\n\n"
        f"CAROUSEL COPY FOR CONTEXT:\n{carousel_text}"
    )

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=hero_request,
    )
    raw = response.text.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    try:
        hero_scene = json.loads(raw.strip())
    except Exception:
        print("[warn] Could not parse hero scene JSON — using minimal scene")
        hero_scene = {"scene_description": raw}

    prompt = build_image_prompt(master_style, hero_scene, portrait=False)
    overlay = hero_scene.get("overlay_text", "")
    placement = hero_scene.get("text_placement", "lower third")

    print(f"  Calling gpt-image-1 (1536x1024)...", end=" ", flush=True)
    raw_bytes = generate_image(openai_client, prompt, size="1536x1024")

    if raw_bytes:
        # Post-process to 1376x768 hero format
        final_bytes = post_process_image(
            raw_bytes, overlay, placement,
            target_w=1376, target_h=768, border=28,
        )
        out = article_dir / "images" / "00_hero.png"
        out.write_bytes(final_bytes)
        print(f"saved -> {out.name} ({len(final_bytes)//1024}KB)")
    else:
        print("failed")


# ---------------------------------------------------------------------------
# PDF compilation
# ---------------------------------------------------------------------------

def compile_carousel_pdf(images_dir: Path, article_dir: Path, slug: str) -> "Path | None":
    try:
        from PIL import Image
    except ImportError:
        print("[warn] Pillow not available — skipping PDF compilation")
        return None

    png_files = sorted(
        [f for f in images_dir.glob("*.png") if not f.name.startswith("00_")],
        key=lambda f: f.name,
    )

    if not png_files:
        print("[warn] No slide images found for PDF compilation")
        return None

    images = []
    for f in png_files:
        try:
            images.append(Image.open(f).convert("RGB"))
        except Exception as e:
            print(f"[warn] Could not open {f.name} for PDF: {e}")

    if not images:
        return None

    pdf_path = article_dir / f"{slug}_carousel.pdf"
    try:
        images[0].save(
            str(pdf_path),
            format="PDF",
            save_all=True,
            append_images=images[1:],
        )
        return pdf_path
    except Exception as e:
        print(f"[error] PDF compilation failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(slug: str, prompts_only: bool, hero: bool):
    load_dotenv_env()

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        sys.exit("[error] GEMINI_API_KEY not found in .env")

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key and not prompts_only:
        sys.exit("[error] OPENAI_API_KEY not found in .env — required for image generation")

    from google import genai
    import openai as openai_lib

    gemini_client = genai.Client(api_key=gemini_key)
    openai_client = openai_lib.OpenAI(api_key=openai_key) if openai_key else None

    article_dir, carousel_text = load_carousel(slug)
    images_dir = article_dir / "images"

    print(f"\n[carousel] Article: {slug}")
    print(f"[carousel] Loading brand assets...")
    master_style = load_master_style()
    brand_context = load_brand_context()

    slide_count = sum(1 for line in carousel_text.splitlines() if line.strip().startswith("Slide "))
    print(f"[carousel] Detected {slide_count} slides in carousel.md")

    slides = generate_storyboard(gemini_client, brand_context, carousel_text)
    print(f"[carousel] Storyboard: {len(slides)} slides")

    built_prompts = [build_image_prompt(master_style, s) for s in slides]
    save_production_sheet(article_dir, slides, built_prompts, slug)

    if prompts_only:
        print("\n[carousel] --prompts-only: skipping image generation.")
        print(f"[carousel] Review {article_dir / 'carousel_production_sheet.md'}")
        print("[carousel] Re-run without --prompts-only when ready.")
        return

    # Verify Pillow is available before burning image credits
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print("[warn] Pillow not installed — images will be saved without post-processing")
        print("[warn] Run: pip install pillow")

    images_dir.mkdir(exist_ok=True)

    print(f"\n[carousel] Generating {len(slides)} carousel images via gpt-image-1...")
    print(f"[carousel] Post-processing to {CAROUSEL_W}x{CAROUSEL_H} with border + text overlay")
    generated = 0

    for i, (slide, prompt) in enumerate(zip(slides, built_prompts), 1):
        num = slide.get("slide_number", i)
        name = SLIDE_NAMES.get(num, f"slide_{num}")
        filename = f"{num:02d}_{name}.png"
        out_path = images_dir / filename

        overlay   = slide.get("overlay_text", "")
        placement = slide.get("text_placement", "lower third")

        print(f"  [{num:02d}/{len(slides)}] {filename} — \"{overlay}\"...", end=" ", flush=True)
        raw_bytes = generate_image(openai_client, prompt, size="1024x1536")

        if raw_bytes:
            final_bytes = post_process_image(raw_bytes, overlay, placement)
            out_path.write_bytes(final_bytes)
            print(f"saved ({len(final_bytes)//1024}KB)")
            generated += 1
        else:
            print("failed")

        if i < len(slides):
            time.sleep(1)

    if hero:
        generate_hero_image(gemini_client, openai_client, article_dir,
                            master_style, brand_context, carousel_text)

    pdf_path = None
    if generated > 0:
        print(f"\n[pdf] Compiling {generated} slides into carousel PDF...")
        pdf_path = compile_carousel_pdf(images_dir, article_dir, slug)
        if pdf_path:
            print(f"[pdf] Ready -> {pdf_path.name}")
        else:
            print("[pdf] PDF compilation failed — see warnings above")

    print(f"\n{'━'*40}")
    print(f" Carousel Complete — {slug}")
    print(f"{'━'*40}")
    print(f" ✓ Images generated:  {generated}/{len(slides)}")
    print(f" ✓ Final size:        {CAROUSEL_W}x{CAROUSEL_H} with {BORDER_PX}px white border")
    print(f" ✓ Images folder:     content-engine/pending/{slug}/images/")
    print(f" ✓ Production sheet:  carousel_production_sheet.md")
    if pdf_path:
        print(f" ✓ Carousel PDF:      {pdf_path.name}  ← upload this to LinkedIn as a Document post")
    else:
        print(f" ✗ PDF:               not compiled — upload images manually as PDF")
    if generated < len(slides):
        print(f" ✗ Failed:            {len(slides) - generated} (check prompts in production sheet)")
    print(f"{'━'*40}\n")


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


def main():
    parser = argparse.ArgumentParser(
        description="Generate LinkedIn carousel images — Gemini storyboard + gpt-image-1 + Pillow post-processing"
    )
    parser.add_argument("slug", help="Article folder name under content-engine/pending/")
    parser.add_argument("--prompts-only", action="store_true",
                        help="Build storyboard and prompts only — skip image generation")
    parser.add_argument("--hero", action="store_true",
                        help="Also generate a landscape article hero image (00_hero.png)")
    args = parser.parse_args()
    run(args.slug, prompts_only=args.prompts_only, hero=args.hero)


if __name__ == "__main__":
    main()
