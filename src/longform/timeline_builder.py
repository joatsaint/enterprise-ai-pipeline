"""
Builds the master timeline for a long-form build video WITHOUT a CapCut rough cut.

Randy's manual process (per-step, ~several hours the first time):
  1. Record raw screen-capture segments (pause/resume at each natural stopping point —
     segments are already discrete, no scene-detection needed).
  2. Generate an AI avatar clip explaining what happened in that step.
  3. Assemble avatar + segments into a CapCut rough cut, export captions (SRT) from
     the assembled timeline, hand the SRT to Claude so it knows exact timing for
     Remotion overlays.

This module replaces step 3's manual assembly-then-export round trip. We already know
every duration involved (avatar length via HeyGen's own returned duration_s), so the
full master timeline can be computed directly — no CapCut needed until final compositing.

Per-segment structure (revised with Randy 2026-07-13, dropping the earlier still+B-roll
split): each segment's background is a SINGLE STILL IMAGE — the last frame of the raw
segment (the "step complete, here's what happened and why" on-screen moment) — held for
the segment's ENTIRE avatar-speaking duration, not just a few seconds. Two real reasons
for this, not just simplicity:
  1. HeyGen avatar segments stay short and independently redoable — a bad take only
     costs re-rendering one short segment, not a long continuous generation.
  2. A still image has no length constraint of its own, so there's no footage-to-speech
     duration-matching problem to solve at all — it just holds for however long is
     needed. B-roll speed-matching (the earlier design) is no longer needed.
  Remotion graphics still provide on-screen visual separation/activity between segments,
  layered on top of the still in the compositing step.

Output: <out_dir>/timeline.json (master timeline, same idea as whisper.json/
section_frames but spanning the whole video) + the actual still clip files, ready for
the Remotion overlay-storyboard step and the compositor.
"""
import json
import subprocess
from pathlib import Path

from src.utils.atomic import atomic_write_json


def _ffprobe_duration(path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError(f"ffprobe failed on {path.name}: {r.stderr.strip()[-400:]}")
    return float(r.stdout.strip())


def _extract_still_clip(segment: Path, hold_s: float, out_path: Path) -> bool:
    """Grab the LAST frame of segment and hold it as a hold_s-second video clip.

    Two-step: extract the frame as a PNG, then build a static-image video from
    it. A single-command `loop` filter after `-vframes 1` doesn't work — the
    output frame cap is applied before the loop filter can extend duration.
    """
    if out_path.exists():
        return True
    frame_png = out_path.with_suffix(".png")
    extract_cmd = [
        "ffmpeg", "-y",
        "-sseof", "-1",              # seek to 1s before end
        "-i", str(segment),
        "-vframes", "1",
        str(frame_png),
    ]
    r = subprocess.run(extract_cmd, capture_output=True)
    if r.returncode != 0:
        print(f"[timeline] still-frame grab failed for {segment.name}:\n"
              f"{r.stderr.decode(errors='replace')[-600:]}")
        return False

    hold_cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(frame_png),
        "-t", str(hold_s),
        "-r", "30",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        str(out_path),
    ]
    r = subprocess.run(hold_cmd, capture_output=True)
    frame_png.unlink(missing_ok=True)
    if r.returncode != 0:
        print(f"[timeline] still-frame hold failed for {segment.name}:\n"
              f"{r.stderr.decode(errors='replace')[-600:]}")
        return False
    return True


def build_segment(
    raw_segment: Path,
    avatar_duration_s: float,
    out_dir: Path,
    index: int,
) -> dict:
    """
    Build the still-frame background for one step's segment — the raw
    segment's last frame, held for the entire avatar-speaking duration.
    Returns a dict describing what was built.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    still_path = out_dir / f"segment_{index:02d}_still.mp4"

    ok = _extract_still_clip(raw_segment, avatar_duration_s, still_path)
    return {
        "index": index,
        "raw_segment": str(raw_segment),
        "still_path": str(still_path) if ok else None,
        "still_duration_s": round(avatar_duration_s, 3) if ok else 0.0,
    }


def build_timeline(steps: list[dict], out_dir: Path) -> dict:
    """
    steps: ordered list of
        {"label": str, "raw_segment": Path, "avatar_path": Path, "avatar_duration_s": float}
    Computes cumulative start/end timestamps for every segment (still + avatar, running
    concurrently) across the whole video and writes timeline.json.
    """
    out_path = out_dir / "timeline.json"
    if out_path.exists():
        print(f"[timeline] timeline.json already exists, loading: {out_path.name}")
        return json.loads(out_path.read_text(encoding="utf-8"))

    pieces_dir = out_dir / "pieces"
    cursor = 0.0
    entries = []

    for i, step in enumerate(steps):
        seg_result = build_segment(
            raw_segment=Path(step["raw_segment"]),
            avatar_duration_s=step["avatar_duration_s"],
            out_dir=pieces_dir,
            index=i,
        )

        start = cursor
        end = start + seg_result["still_duration_s"]
        entry = {
            "label": step["label"],
            "index": i,
            "still": {
                "path": seg_result["still_path"],
                "start_s": round(start, 3),
                "end_s": round(end, 3),
            },
            "avatar": {
                "path": str(step["avatar_path"]),
                "start_s": round(start, 3),
                "end_s": round(end, 3),
            },
        }
        entries.append(entry)
        cursor = end

    timeline = {
        "total_duration_s": round(cursor, 3),
        "steps": entries,
    }

    atomic_write_json(out_path, timeline)
    print(f"[timeline] Built master timeline: {len(entries)} steps, "
          f"{timeline['total_duration_s']:.1f}s total -> {out_path.name}")
    return timeline
