"""
Final composite: background graphics (1080×1920) + avatar (1080×1920, transparent or
green-screen) → 1080×1920 short with burned captions and text hook overlay.

Avatar is scaled to 1080×960 and composited into the bottom half (y=960).

Background removal modes (driven by heygen_renderer's bg_mode):
    transparent  — avatar is WebM with alpha channel; FFmpeg overlay handles it natively
    greenscreen  — avatar is MP4 with #00FF00 background; FFmpeg chromakey removes it
    none         — no compositing; falls back to vstack (split-screen, old behaviour)
"""
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

FPS = 30
AVATAR_HEIGHT = 960           # avatar occupies bottom 960px of the 1920px frame
AVATAR_Y      = 960           # y position of avatar overlay in the full frame
CAPTION_Y_IN_FRAME = 1400     # absolute y in 1920px frame (centered in avatar zone)
CAPTION_FONTSIZE   = 52
HOOK_Y_IN_FRAME    = 280      # absolute y in 1920px frame (top third)
HOOK_FONTSIZE      = 58
GREENSCREEN_HEX    = "0x00FF00"

# Windows system font used for all drawtext — bypasses fontconfig requirement
FONT_FILE = r"C\:/Windows/Fonts/arial.ttf"


def _escape_ffmpeg(text: str) -> str:
    return (
        text.replace("\\", "")
            .replace("'", "")
            .replace('"', "")
            .replace(":", "\\:")
            .replace("%", "\\%")
    )


def _build_caption_entries(whisper: dict, max_words: int = 2) -> list:
    """Split Whisper word timestamps into timed caption chunks."""
    entries = []
    for seg in whisper.get("segments", []):
        words = seg.get("words", [])
        if not words:
            entries.append({"start": seg["start"], "end": seg["end"], "text": seg["text"].strip()})
            continue
        chunk = []
        for w in words:
            chunk.append(w)
            if len(chunk) == max_words:
                entries.append({
                    "start": chunk[0]["start"],
                    "end":   chunk[-1]["end"],
                    "text":  " ".join(c["word"].strip() for c in chunk),
                })
                chunk = []
        if chunk:
            entries.append({
                "start": chunk[0]["start"],
                "end":   chunk[-1]["end"],
                "text":  " ".join(c["word"].strip() for c in chunk),
            })
    return entries


def _build_drawtext_captions(entries: list, y: int, fontsize: int) -> str:
    """
    Build a chain of drawtext filters for timed captions.
    Avoids libass/fontconfig entirely — works on any FFmpeg install.
    """
    parts = []
    for e in entries:
        # Strip/escape chars that break FFmpeg's filter string parser
        text = (
            e["text"].upper().strip()
            .replace("\\", "")
            .replace("'", "")      # apostrophes break single-quoted filter values
            .replace('"', "")
            .replace(":", "\\:")
            .replace("%", "\\%")
        )
        t0 = f"{e['start']:.3f}"
        t1 = f"{e['end']:.3f}"
        parts.append(
            f"drawtext=fontfile='{FONT_FILE}':text='{text}'"
            f":x=(w-text_w)/2:y={y}"
            f":fontsize={fontsize}:fontcolor=white"
            f":shadowcolor=black@0.9:shadowx=3:shadowy=3"
            f":enable='between(t,{t0},{t1})'"
        )
    return ",".join(parts)


def _composite_transparent(graphics: Path, avatar: Path, out: Path) -> bool:
    """Overlay transparent-background avatar (WebM) onto graphics using alpha."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(graphics),                   # [0] background graphics (1080×1920)
        "-i", str(avatar),                     # [1] avatar with alpha (1080×1920)
        "-filter_complex",
        f"[1:v]scale=1080:{AVATAR_HEIGHT}[ava];"    # scale to bottom-half height
        f"[0:v][ava]overlay=x=0:y={AVATAR_Y}:shortest=1[vout]",
        "-map", "[vout]",
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print(f"[stitch] transparent composite failed:\n{r.stderr.decode(errors='replace')[-800:]}")
        return False
    return True


def _composite_greenscreen(graphics: Path, avatar: Path, out: Path) -> bool:
    """Chromakey green background from avatar MP4, then overlay onto graphics."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(graphics),
        "-i", str(avatar),
        "-filter_complex",
        f"[1:v]scale=1080:{AVATAR_HEIGHT}[ava_scaled];"
        f"[ava_scaled]chromakey=color={GREENSCREEN_HEX}:similarity=0.15:blend=0.05[ava_keyed];"
        f"[0:v][ava_keyed]overlay=x=0:y={AVATAR_Y}:shortest=1[vout]",
        "-map", "[vout]",
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print(f"[stitch] greenscreen composite failed:\n{r.stderr.decode(errors='replace')[-800:]}")
        return False
    return True


def _composite_vstack(graphics: Path, avatar: Path, out: Path) -> bool:
    """Fallback: crop avatar to 1080×960 and vstack with a 1080×960 crop of graphics."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(graphics),
        "-i", str(avatar),
        "-filter_complex",
        f"[0:v]crop=1080:{AVATAR_HEIGHT}:0:0[top];"         # top 960px of graphics
        f"[1:v]scale=1080:{AVATAR_HEIGHT}[bot];"             # avatar scaled to 960px
        f"[top][bot]vstack=inputs=2[vout]",
        "-map", "[vout]",
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print(f"[stitch] vstack fallback failed:\n{r.stderr.decode(errors='replace')[-800:]}")
        return False
    return True


def stitch(
    top_mp4: Path,
    avatar_path: Path,
    whisper: dict,
    text_hook: str,
    out_path: Path,
    bg_mode: str = "transparent",
) -> bool:
    """
    Composite graphics + avatar, then burn captions and text hook overlay.
    Returns True on success.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        composited = tmp / "composited.mp4"

        print(f"[stitch] Compositing — mode={bg_mode}")
        if bg_mode == "transparent":
            ok = _composite_transparent(top_mp4, avatar_path, composited)
        elif bg_mode == "greenscreen":
            ok = _composite_greenscreen(top_mp4, avatar_path, composited)
        else:
            ok = _composite_vstack(top_mp4, avatar_path, composited)

        if not ok:
            return False

        # Build pure-drawtext filter chain (no libass/fontconfig dependency)
        duration_s = whisper.get("duration_s", 60.0) or 60.0
        hook_end   = min(10.0, duration_s)
        hook_esc   = _escape_ffmpeg(text_hook.upper())

        entries = _build_caption_entries(whisper)
        caption_vf = _build_drawtext_captions(entries, CAPTION_Y_IN_FRAME, CAPTION_FONTSIZE)

        hook_vf = (
            f"drawtext=fontfile='{FONT_FILE}':text='{hook_esc}'"
            f":x=(w-text_w)/2:y={HOOK_Y_IN_FRAME}"
            f":fontsize={HOOK_FONTSIZE}:fontcolor=white"
            f":shadowcolor=black@0.85:shadowx=3:shadowy=3"
            f":enable='between(t,0,{hook_end:.1f})'"
        )

        vf = f"{caption_vf},{hook_vf}"

        # Write to temp dir (no spaces/special chars in path) then copy to final dest
        tmp_final = tmp / "final.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-i", str(composited),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "copy",
            str(tmp_final),
        ]
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode != 0:
            print(f"[stitch] caption burn failed:\n{r.stderr.decode(errors='replace')[-1200:]}")
            return False

        shutil.copy2(tmp_final, out_path)

    print(f"[stitch] Final short: {out_path.name}")
    return True


def run(
    out_dir: Path,
    avatar_path: Path,
    whisper: dict,
    text_hook: str,
    bg_mode: str = "transparent",
    top_a: Path | None = None,
    top_b: Path | None = None,
) -> dict:
    """
    Stitch all available variants.
    Returns {"final_a": path_or_None, "final_b": path_or_None}
    """
    results = {}

    for key, top in [("final_a", top_a), ("final_b", top_b)]:
        if not (top and top.exists()):
            results[key] = None
            continue
        dest = out_dir / f"{key}.mp4"
        if dest.exists():
            print(f"[stitch] {key}.mp4 already exists, skipping")
            results[key] = dest
        else:
            ok = stitch(top, avatar_path, whisper, text_hook, dest, bg_mode=bg_mode)
            results[key] = dest if ok else None

    return results
