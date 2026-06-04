#!/usr/bin/env python3
"""
generate_carousel_images.py  — content-engine/

Reads carousel.md for a given article, generates a per-slide visual
storyboard + image prompts using the full brand bible, then calls
Imagen 3 via the Gemini API to produce the images.

Usage
-----
  python generate_carousel_images.py ART6-from-no-to-safe-enough-yes
  python generate_carousel_images.py ART6-from-no-to-safe-enough-yes --prompts-only
  python generate_carousel_images.py ART6-from-no-to-safe-enough-yes --hero
"""

import argparse
import base64
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Ensure the terminal handles Unicode on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE      = Path(__file__).resolve().parent
ROOT      = HERE.parent
BRAND_DIR = ROOT / "docs" / "ChatGPT - LinkedIn Content Creation Prompts and Playbook"
PENDING   = HERE / "pending"

# Load by pattern — avoids fragile exact-name matching
BRAND_KEYWORDS = ["master_linkedin_image_system", "sysadmin_ai_visual_brand_bible"]

SLIDE_NAMES = {
    1: "hook", 2: "problem", 3: "mistake", 4: "operator",
    5: "turn",  6: "reveal", 7: "recognition", 8: "lesson_cta",
}


# ---------------------------------------------------------------------------
# Brand / article loading
# ---------------------------------------------------------------------------

def load_brand_context() -> str:
    parts = []
    if not BRAND_DIR.exists():
        sys.exit(f"[error] Brand directory not found: {BRAND_DIR}")
    for f in sorted(BRAND_DIR.glob("*.md")):
        if not any(kw in f.name.lower() for kw in BRAND_KEYWORDS):
            continue
        try:
            with open(str(f), "r", encoding="utf-8", errors="replace") as fh:
                parts.append(fh.read())
            print(f"  [brand] Loaded: {f.name}")
        except OSError as e:
            print(f"  [warn] Could not read {f.name}: {e}")
    if not parts:
        print(f"[warn] No brand files matched — generating with limited context")
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


def load_article(article_dir: Path) -> str:
    for candidate in ["linkedin-article.md", "article.md"]:
        f = article_dir / candidate
        if f.exists():
            return f.read_text("utf-8")
    return ""


# ---------------------------------------------------------------------------
# Storyboard generation (Gemini text)
# ---------------------------------------------------------------------------

STORYBOARD_SYSTEM = """\
You are the visual director for Randy Skiles' LinkedIn brand system. You have
full knowledge of the brand bible provided below. Your job is to produce a
complete image-generation storyboard for a LinkedIn carousel.

BRAND BIBLE:
{brand_context}

TASK:
Given the carousel slide copy, output a JSON array — one object per slide.

Each object must have these exact keys:
  slide_number       (int)
  slide_title        (string, 2-5 words)
  emotional_objective (string, one word or short phrase)
  image_style        (string: exactly "Cinematic Editorial Realism" or "Documentary Photograph Principle")
  overlay_text       (string: short text overlay, 3-10 words — copy from the slide or sharpen it)
  stapler_placement  (string: where the red stapler is hidden)
  full_image_prompt  (string: complete Imagen-ready prompt — see rules below)

Rules for full_image_prompt:
- The image generator is gpt-image-1 (OpenAI) which renders text ACCURATELY in images.
  Include all text that should appear in the image directly in the prompt.
- Open with: "Create a high-impact LinkedIn carousel image, vertical portrait format,
  1024 x 1536 px, with a clean 1-inch white border around the entire image."
- State the image style (Cinematic Editorial Realism OR Documentary Photograph Principle).
- Include The Operator: "the recurring Operator character — a Gen-X enterprise IT veteran,
  male, early-to-mid 50s, salt-and-pepper hair, slightly tired eyes, calm expression,
  practical business-casual clothing, headset often present, coffee nearby, never panicking,
  always the calmest person in the scene."
- Include the specific scene description for this slide.
- Include the stapler: "Hide a red Swingline-style stapler [placement] — never centered,
  never highlighted, visible only on close inspection."
- Include lighting: "Cinematic lighting: warm monitor glow, cool blue-gray ambient."
- Include text to render: "Render the following text in the lower third of the image in
  large bold clean sans-serif white typography with a subtle dark gradient behind it for
  readability: '[overlay_text]'"
- NEVER include: generic AI robots, glowing brains, holograms, neon cyberpunk,
  Silicon Valley stock-photo polish, Canva-style over-design.

Use the metaphor library from the brand bible to select the strongest visual for each slide.
Use Documentary Photograph Principle for war-story / real-incident slides.
Use Cinematic Editorial Realism for concept / metaphor / governance slides.

Output ONLY the JSON array. No markdown fences. No explanation. Start with [ end with ]."""


def generate_storyboard(client, brand_context: str, carousel_text: str) -> list[dict]:
    from google import genai  # noqa: F401 (already imported at call site)

    prompt = STORYBOARD_SYSTEM.format(brand_context=brand_context)
    full_input = f"{prompt}\n\nCARROUSEL SLIDE COPY:\n{carousel_text}"

    print("[storyboard] Calling Gemini 2.5 Flash...", end=" ", flush=True)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_input,
    )
    print("done")

    raw = response.text.strip()
    # Strip markdown code fences if the model wraps the JSON anyway
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
# Production sheet
# ---------------------------------------------------------------------------

def save_production_sheet(article_dir: Path, slides: list[dict], slug: str):
    lines = [
        f"# Carousel Production Sheet — {slug}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Slides: {len(slides)}",
        "",
    ]
    for s in slides:
        n = s.get("slide_number", "?")
        lines += [
            f"---",
            f"## Slide {n} — {s.get('slide_title', '')}",
            f"**Emotion:** {s.get('emotional_objective', '')}",
            f"**Style:** {s.get('image_style', '')}",
            f"**Overlay:** _{s.get('overlay_text', '')}_",
            f"**Stapler:** {s.get('stapler_placement', '')}",
            "",
            "**Image Prompt:**",
            "",
            s.get("full_image_prompt", ""),
            "",
        ]
    out = article_dir / "carousel_production_sheet.md"
    out.write_text("\n".join(lines), "utf-8")
    print(f"[ok] Production sheet -> {out.name}")


# ---------------------------------------------------------------------------
# Image generation (gpt-image-1 via OpenAI)
# ---------------------------------------------------------------------------

def generate_image(openai_client, prompt: str, size: str = "1024x1536") -> bytes | None:
    import openai

    try:
        response = openai_client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size,
            quality="high",
            n=1,
        )
        img_data = response.data[0].b64_json
        if img_data:
            return base64.b64decode(img_data)
        return None
    except Exception as e:
        print(f"failed — {e}")
        return None


def generate_hero_image(gemini_client, openai_client, article_dir: Path, brand_context: str, carousel_text: str):
    """Generate a single landscape article hero image (1536x1024)."""
    print("\n[hero] Generating article hero image (landscape)...")

    prompt_request = (
        f"{STORYBOARD_SYSTEM.format(brand_context=brand_context)}\n\n"
        "Generate ONE hero image prompt for this article. Output a single JSON object "
        "(not an array) with keys: overlay_text, full_image_prompt.\n\n"
        "The full_image_prompt must specify: landscape format, 1536 x 1024 px, "
        "clean 1-inch white border, Cinematic Editorial Realism style. "
        "Text will be rendered accurately by gpt-image-1 — include the headline text "
        "to render directly in the prompt.\n\n"
        f"CAROUSEL COPY FOR CONTEXT:\n{carousel_text}"
    )

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_request,
    )
    raw = response.text.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    try:
        hero_data = json.loads(raw.strip())
        prompt = hero_data.get("full_image_prompt", "")
    except Exception:
        print("[warn] Could not parse hero prompt JSON — using raw response")
        prompt = raw

    print(f"  Calling gpt-image-1 (1536x1024)...", end=" ", flush=True)
    img_bytes = generate_image(openai_client, prompt, size="1536x1024")

    if img_bytes:
        out = article_dir / "images" / "00_hero.png"
        out.write_bytes(img_bytes)
        print(f"saved -> {out.name} ({len(img_bytes)//1024}KB)")
    else:
        print("failed")


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
    print(f"[carousel] Loading brand context...")
    brand_context = load_brand_context()

    slide_count = sum(1 for line in carousel_text.splitlines() if line.strip().startswith("Slide "))
    print(f"[carousel] Detected {slide_count} slides in carousel.md")

    slides = generate_storyboard(gemini_client, brand_context, carousel_text)
    print(f"[carousel] Storyboard: {len(slides)} slides")
    save_production_sheet(article_dir, slides, slug)

    if prompts_only:
        print("\n[carousel] --prompts-only: skipping image generation.")
        print(f"[carousel] Review {article_dir / 'carousel_production_sheet.md'}")
        print("[carousel] Re-run without --prompts-only when ready.")
        return

    images_dir.mkdir(exist_ok=True)

    print(f"\n[carousel] Generating {len(slides)} carousel images via gpt-image-1...")
    generated = 0
    for i, slide in enumerate(slides, 1):
        num = slide.get("slide_number", i)
        name = SLIDE_NAMES.get(num, f"slide_{num}")
        filename = f"{num:02d}_{name}.png"
        out_path = images_dir / filename
        prompt = slide.get("full_image_prompt", "")

        if not prompt:
            print(f"  [{num:02d}] No prompt — skipping")
            continue

        overlay = slide.get("overlay_text", "")
        print(f"  [{num:02d}/{len(slides)}] {filename} — \"{overlay}\"...", end=" ", flush=True)
        img_bytes = generate_image(openai_client, prompt, size="1024x1536")

        if img_bytes:
            out_path.write_bytes(img_bytes)
            print(f"saved ({len(img_bytes)//1024}KB)")
            generated += 1
        else:
            print("failed")

        if i < len(slides):
            time.sleep(1)

    if hero:
        generate_hero_image(gemini_client, openai_client, article_dir, brand_context, carousel_text)

    print(f"\n{'━'*40}")
    print(f" Carousel Complete — {slug}")
    print(f"{'━'*40}")
    print(f" ✓ Images generated:  {generated}/{len(slides)}")
    print(f" ✓ Images folder:     content-engine/pending/{slug}/images/")
    print(f" ✓ Production sheet:  carousel_production_sheet.md")
    if generated < len(slides):
        failed = len(slides) - generated
        print(f" ✗ Failed:            {failed} (check prompts in production sheet)")
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
        description="Generate LinkedIn carousel images via Gemini/Imagen 3"
    )
    parser.add_argument(
        "slug",
        help="Article folder name under content-engine/pending/ (e.g. ART6-from-no-to-safe-enough-yes)",
    )
    parser.add_argument(
        "--prompts-only",
        action="store_true",
        help="Generate storyboard and image prompts only — skip Imagen calls",
    )
    parser.add_argument(
        "--hero",
        action="store_true",
        help="Also generate a 16:9 article hero image (saved as 00_hero.png)",
    )
    args = parser.parse_args()
    run(args.slug, prompts_only=args.prompts_only, hero=args.hero)


if __name__ == "__main__":
    main()
