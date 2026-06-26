"""
Renders the full 9:16 (1080×1920) background graphics layer.

Variant A — Text-driven (Remotion):
    Animated section cards in the top 50% of the frame. Avatar composites over bottom.
    Requires: node + npx in PATH, npm install done in remotion/shorts/.

Variant B — Image-driven (gpt-image-1 + FFmpeg):
    One IT-themed image per section, full 9:16, timed by Whisper timestamps.
    Requires: OPENAI_API_KEY in .env.

Both produce full 9:16 MP4s (1080×1920):
    top_a.mp4   (variant A — Remotion text cards)
    top_b.mp4   (variant B — image slideshow, skipped if no OPENAI_API_KEY)
"""
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
REMOTION_DIR = ROOT / "remotion" / "shorts"
FPS = 30

BG_COLOR       = "#0C0C0E"
ACCENT_GREEN   = "#39ff14"
ACCENT_ORANGE  = "#FF6700"
TEXT_WHITE     = "#f8f9fa"

SECTION_STYLES = {
    "hook":        {"color": ACCENT_GREEN,  "size": "large"},
    "problem":     {"color": TEXT_WHITE,    "size": "medium"},
    "insight":     {"color": ACCENT_ORANGE, "size": "medium"},
    "implication": {"color": TEXT_WHITE,    "size": "medium"},
    "cta":         {"color": ACCENT_GREEN,  "size": "small"},
}

IMAGE_PROMPTS = {
    "hook":        "Dark server room, dramatic cinematic lighting, enterprise IT equipment, no text, no people",
    "problem":     "Close-up of a terminal screen with a red warning alert, dark background, enterprise IT, no text",
    "insight":     "Wide shot of a network operations center, blue-green glow, monitors, dark moody atmosphere, no text",
    "implication": "Hands on a mechanical keyboard, green terminal text reflected in glasses, focused, dark, no text",
    "cta":         "Digital clock on black background, green LED display, enterprise aesthetic, no text",
}


# ---------------------------------------------------------------------------
# Variant A — Remotion (full 9:16)
# ---------------------------------------------------------------------------

def _write_remotion_data(whisper: dict, sections: list, text_hook: str, out_dir: Path) -> Path:
    section_frames = whisper.get("section_frames", {})
    duration_s     = whisper.get("duration_s", 60.0)
    total_frames   = int(duration_s * FPS) + 1

    composed = []
    for i, sec in enumerate(sections):
        label = sec["label"]
        start = section_frames.get(label, i * (total_frames // len(sections)))
        if i + 1 < len(sections):
            next_label = sections[i + 1]["label"]
            end = section_frames.get(next_label, start + (total_frames // len(sections)))
        else:
            end = total_frames

        style = SECTION_STYLES.get(label, {"color": TEXT_WHITE, "size": "medium"})
        composed.append({
            "label":      label,
            "text":       sec["text"],
            "startFrame": start,
            "endFrame":   end,
            "color":      style["color"],
            "size":       style["size"],
        })

    data = {
        "fps":              FPS,
        "durationInFrames": total_frames,
        "width":            1080,
        "height":           1920,
        "bgColor":          BG_COLOR,
        "textHook":         text_hook,
        "textHookEndFrame": min(int(FPS * 10), total_frames),
        "sections":         composed,
    }

    data_path = REMOTION_DIR / "public" / "data.json"
    data_path.parent.mkdir(exist_ok=True)
    data_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Also save a copy in out_dir for reference
    (out_dir / "remotion_data.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data_path


def render_variant_a(whisper: dict, sections: list, text_hook: str, out_dir: Path) -> Path | None:
    out_path = out_dir / "top_a.mp4"
    if out_path.exists():
        print("[remotion] top_a.mp4 already exists, skipping")
        return out_path

    if not REMOTION_DIR.exists():
        print(f"[remotion] WARN: project not found at {REMOTION_DIR}")
        print("[remotion] Run `npm install` in remotion/shorts/ first.")
        return None

    npx = shutil.which("npx") or "npx"

    data_path = _write_remotion_data(whisper, sections, text_hook, out_dir)
    duration_s   = whisper.get("duration_s", 60.0)
    if not duration_s:
        duration_s = 60.0
    total_frames = int(duration_s * FPS) + 1

    cmd = [
        npx, "remotion", "render",
        "TextCard",
        str(out_path),
        "--frames", f"0-{total_frames - 1}",
        "--config", str(REMOTION_DIR / "remotion.config.ts"),
        "--log", "error",
    ]

    print(f"[remotion] Rendering variant A — {total_frames} frames ({duration_s:.1f}s)...")
    result = subprocess.run(cmd, cwd=str(REMOTION_DIR), capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[remotion] Render failed:\n{result.stderr[-2000:]}")
        return None

    print(f"[remotion] top_a.mp4 ready: {out_path.name}")
    return out_path


# ---------------------------------------------------------------------------
# Variant B — gpt-image-1 + FFmpeg (full 9:16)
# ---------------------------------------------------------------------------

def _generate_image(prompt: str, out_path: Path) -> bool:
    if out_path.exists():
        return True
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai_key:
        return False
    try:
        import openai
        import base64
        client = openai.OpenAI(api_key=openai_key)
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            quality="low",
            n=1,
        )
        img_data = base64.b64decode(response.data[0].b64_json)
        out_path.write_bytes(img_data)
        return True
    except Exception as exc:
        print(f"[image_gen] Failed: {exc}")
        return False


def _images_to_video(image_paths: list, durations: list, out_path: Path) -> bool:
    concat_path = out_path.parent / "_concat_b.txt"
    with open(concat_path, "w") as f:
        for img, dur in zip(image_paths, durations):
            f.write(f"file '{img.as_posix()}'\n")
            f.write(f"duration {dur:.3f}\n")
        if image_paths:
            f.write(f"file '{image_paths[-1].as_posix()}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_path),
        # Scale to 9:16 full frame
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True)
    concat_path.unlink(missing_ok=True)
    if result.returncode != 0:
        print(f"[image_stitch] FFmpeg failed:\n{result.stderr.decode(errors='replace')[-800:]}")
        return False
    return True


def render_variant_b(whisper: dict, sections: list, out_dir: Path) -> Path | None:
    out_path = out_dir / "top_b.mp4"
    if out_path.exists():
        print("[image_gen] top_b.mp4 already exists, skipping")
        return out_path

    if not os.environ.get("OPENAI_API_KEY"):
        print("[image_gen] OPENAI_API_KEY not set — skipping variant B")
        return None

    section_frames = whisper.get("section_frames", {})
    duration_s     = whisper.get("duration_s", 60.0)

    img_dir = out_dir / "_images_b"
    img_dir.mkdir(exist_ok=True)
    image_paths = []
    durations   = []

    for i, sec in enumerate(sections):
        label    = sec["label"]
        prompt   = IMAGE_PROMPTS.get(label, IMAGE_PROMPTS["hook"])
        img_path = img_dir / f"{i:02d}_{label}.png"

        print(f"[image_gen] Generating {label} image...")
        if not _generate_image(prompt, img_path):
            return None
        image_paths.append(img_path)

        start_s = section_frames.get(label, i * duration_s / len(sections)) / FPS
        if i + 1 < len(sections):
            next_label = sections[i + 1]["label"]
            end_s = section_frames.get(next_label, (i + 1) * duration_s / len(sections)) / FPS
        else:
            end_s = duration_s
        durations.append(max(end_s - start_s, 1.0))
        time.sleep(1)

    print("[image_gen] Stitching images into top_b.mp4...")
    if not _images_to_video(image_paths, durations, out_path):
        return None

    print(f"[image_gen] top_b.mp4 ready")
    return out_path


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render(whisper: dict, sections: list, text_hook: str, out_dir: Path, variant: str = "both") -> dict:
    """
    Render full 9:16 background graphics.
    variant: "a" | "b" | "both"
    Returns {"top_a": path_or_None, "top_b": path_or_None}
    """
    results = {}
    if variant in ("a", "both"):
        results["top_a"] = render_variant_a(whisper, sections, text_hook, out_dir)
    if variant in ("b", "both"):
        results["top_b"] = render_variant_b(whisper, sections, out_dir)
    return results
