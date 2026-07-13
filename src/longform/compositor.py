"""
Composites one step's still + B-roll (left side) with the HeyGen avatar
(right side) into a single 1920x1080 landscape clip, then concatenates all
steps into the base video for the whole build.

Layout confirmed with Randy 2026-07-13 (matches his first manual build):
    - Avatar: full-height vertical (9:16-ish) clip, right side of frame
    - Footage (still -> sped-up B-roll): fills the remaining left width
    - Avatar uses greenscreen (#00FF00) chromakey — canonical for long-form
      per reference_heygen_avatar_voice.md (CapCut PC doesn't reliably
      support WebM alpha transparency; green screen + Remove BG is reliable)

This produces the BASE video only — Remotion overlays (from storyboard.md,
once the TODO visual descriptions are filled in) get composited on top of
this in a later pass, same as the existing Shorts pipeline layers graphics
under the avatar.
"""
import json
import subprocess
import tempfile
from pathlib import Path

FRAME_W = 1920
FRAME_H = 1080
GREENSCREEN_HEX = "0x00FF00"
CANVAS_BG_COLOR = "0x0C0C0E"   # matches top_half_renderer.py's BG_COLOR — avatar-zone backdrop


def _ffprobe_dims(path: Path) -> tuple[int, int]:
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=s=x:p=0",
        str(path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError(f"ffprobe dims failed on {path.name}: {r.stderr.strip()[-300:]}")
    w, h = r.stdout.strip().split("x")
    return int(w), int(h)


def _concat_footage(still_path: Path | None, broll_path: Path | None, out_path: Path) -> bool:
    """Concatenate still + B-roll (skip whichever is missing) into one footage clip."""
    pieces = [p for p in (still_path, broll_path) if p]
    if not pieces:
        return False
    if len(pieces) == 1:
        cmd = ["ffmpeg", "-y", "-i", str(pieces[0]), "-c", "copy", str(out_path)]
    else:
        concat_list = out_path.parent / f"{out_path.stem}_concat.txt"
        concat_list.write_text(
            "\n".join(f"file '{p.resolve().as_posix()}'" for p in pieces),
            encoding="utf-8",
        )
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy",
            str(out_path),
        ]
    r = subprocess.run(cmd, capture_output=True)
    if len(pieces) > 1:
        (out_path.parent / f"{out_path.stem}_concat.txt").unlink(missing_ok=True)
    if r.returncode != 0:
        print(f"[compositor] footage concat failed:\n{r.stderr.decode(errors='replace')[-600:]}")
        return False
    return True


def composite_step(
    footage_path: Path,
    avatar_path: Path,
    out_path: Path,
    bg_mode: str = "greenscreen",
) -> tuple[bool, int]:
    """
    Avatar (full-height, right side, chromakeyed) overlaid onto a canvas built
    from footage (left) + a solid backdrop (right, behind the avatar).

    hstack alone can't composite chromakey's transparent regions — it just
    places pixel grids side by side with no compositing, so "removed" green
    stays visible. Build an opaque canvas first (footage + solid backdrop
    hstacked), then `overlay` the chromakeyed avatar on top of that — overlay
    is what actually respects the alpha chromakey produces.

    Returns (success, footage_w) — footage_w is needed by the overlay-
    compositing step later so it knows the exact left-zone width to target.
    """
    avatar_w, avatar_h = _ffprobe_dims(avatar_path)
    # Scale avatar to full frame height, preserving its aspect ratio
    scaled_avatar_w = int(avatar_w * (FRAME_H / avatar_h))
    footage_w = max(FRAME_W - scaled_avatar_w, 1)

    if out_path.exists():
        return True, footage_w

    if bg_mode == "greenscreen":
        avatar_filter = (
            f"[1:v]scale={scaled_avatar_w}:{FRAME_H},"
            f"chromakey=color={GREENSCREEN_HEX}:similarity=0.15:blend=0.05[ava]"
        )
    else:
        avatar_filter = f"[1:v]scale={scaled_avatar_w}:{FRAME_H}[ava]"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(footage_path),
        "-i", str(avatar_path),
        "-f", "lavfi", "-i", f"color=c={CANVAS_BG_COLOR}:size={scaled_avatar_w}x{FRAME_H}",
        "-filter_complex",
        f"[0:v]scale={footage_w}:{FRAME_H}:force_original_aspect_ratio=increase,"
        f"crop={footage_w}:{FRAME_H}[foot];"
        f"[foot][2:v]hstack=inputs=2[canvas];"
        f"{avatar_filter};"
        f"[canvas][ava]overlay=x={footage_w}:y=0:shortest=1[vout]",
        "-map", "[vout]",
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print(f"[compositor] step composite failed:\n{r.stderr.decode(errors='replace')[-800:]}")
        return False, footage_w
    return True, footage_w


def composite_timeline(timeline: dict, out_dir: Path, bg_mode: str = "greenscreen") -> Path | None:
    """
    Builds the full base video (all steps composited + concatenated) from
    a timeline.json dict. Returns the output path, or None on failure.

    Also writes layout.json (footage_w, frame dims) alongside base_video.mp4
    so the later overlay-compositing step knows the exact footage-zone width
    without re-deriving it from the avatar clip.
    """
    composited_dir = out_dir / "pieces" / "composited"
    composited_dir.mkdir(parents=True, exist_ok=True)
    final_out = out_dir / "base_video.mp4"
    layout_path = out_dir / "layout.json"

    if final_out.exists():
        print(f"[compositor] base_video.mp4 already exists, skipping")
        return final_out

    step_clips = []
    footage_w = None
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for step in timeline["steps"]:
            idx = step["index"]
            still = Path(step["still"]["path"]) if step.get("still") and step["still"].get("path") else None
            broll = Path(step["broll"]["path"]) if step.get("broll") and step["broll"].get("path") else None
            avatar = Path(step["avatar"]["path"])

            footage_path = tmp / f"footage_{idx:02d}.mp4"
            if not _concat_footage(still, broll, footage_path):
                print(f"[compositor] step {idx}: no footage available, aborting")
                return None

            step_out = composited_dir / f"step_{idx:02d}.mp4"
            ok, step_footage_w = composite_step(footage_path, avatar, step_out, bg_mode=bg_mode)
            if not ok:
                print(f"[compositor] step {idx}: composite failed, aborting")
                return None
            if footage_w is None:
                footage_w = step_footage_w
            step_clips.append(step_out)

        concat_list = tmp / "final_concat.txt"
        concat_list.write_text(
            "\n".join(f"file '{p.resolve().as_posix()}'" for p in step_clips),
            encoding="utf-8",
        )
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy",
            str(final_out),
        ]
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode != 0:
            print(f"[compositor] final concat failed:\n{r.stderr.decode(errors='replace')[-600:]}")
            return None

    layout_path.write_text(
        json.dumps({"frame_w": FRAME_W, "frame_h": FRAME_H, "footage_w": footage_w}, indent=2),
        encoding="utf-8",
    )
    print(f"[compositor] Base video built: {final_out.name} ({len(step_clips)} steps)")
    return final_out


def composite_overlay(
    base_video_path: Path,
    overlay_video_path: Path,
    out_path: Path,
    footage_w: int | None = None,
    bg_mode: str = "greenscreen",
) -> bool:
    """
    Layers a rendered Remotion overlay video onto the FOOTAGE ZONE ONLY of an
    already-composited base_video.mp4 (avatar + footage side by side), leaving
    the avatar untouched — matches Randy's confirmed design: graphics play on
    top of the footage side, never over the avatar.

    Overlay video is expected to be rendered at exactly footage_w x FRAME_H
    (not full-frame) on a pure #00FF00 background per the existing Remotion
    convention (long-form-video-production skill, Stage 4) — chromakeyed here
    the same way the avatar is, then placed at x=0, y=0.

    footage_w: if not given, read from layout.json next to base_video_path
    (written by composite_timeline).
    """
    if out_path.exists():
        return True

    if footage_w is None:
        layout_path = base_video_path.parent / "layout.json"
        if not layout_path.exists():
            print(f"[compositor] footage_w not given and no layout.json found next to {base_video_path.name}")
            return False
        footage_w = json.loads(layout_path.read_text(encoding="utf-8"))["footage_w"]

    if bg_mode == "greenscreen":
        overlay_filter = (
            f"[1:v]scale={footage_w}:{FRAME_H},"
            f"chromakey=color={GREENSCREEN_HEX}:similarity=0.15:blend=0.05[ovl]"
        )
    else:
        overlay_filter = f"[1:v]scale={footage_w}:{FRAME_H}[ovl]"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(base_video_path),
        "-i", str(overlay_video_path),
        "-filter_complex",
        f"{overlay_filter};"
        f"[0:v][ovl]overlay=x=0:y=0:shortest=1[vout]",
        "-map", "[vout]",
        "-map", "0:a",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print(f"[compositor] overlay composite failed:\n{r.stderr.decode(errors='replace')[-800:]}")
        return False
    print(f"[compositor] Overlay composited: {out_path.name}")
    return True
