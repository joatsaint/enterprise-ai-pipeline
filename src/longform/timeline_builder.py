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
every duration involved (raw segment length via ffprobe, avatar length via HeyGen's
own returned duration_s / Whisper), so the full master timeline can be computed
directly — no CapCut needed until final compositing.

Per-segment structure (confirmed with Randy 2026-07-13):
  [still frame, held ~STILL_HOLD_S]  →  [sped-up B-roll, fills remaining avatar duration]
  ...both playing under/behind the avatar's spoken explanation, split-screen.

  - The still frame is the LAST frame of the raw segment (the "step complete, here's
    what happened and why" on-screen moment) — gives the audience a few seconds to
    read it before motion starts.
  - The B-roll is an earlier portion of the SAME raw segment, sped up (setpts) to
    exactly fill the remaining avatar duration. Randy's own build videos run ~5x raw
    footage to final length (20 min raw -> 4 min final), so there is always enough
    raw material — freeze-frame (extend the still) is a fallback for the rare case
    where a segment is too short, not the expected path.

Output: <out_dir>/timeline.json (master timeline, same idea as whisper.json/
section_frames but spanning the whole video) + the actual still/B-roll clip files,
ready for the Remotion overlay-storyboard step and, eventually, final compositing.
"""
import json
import subprocess
from pathlib import Path

from src.utils.atomic import atomic_write_json

STILL_HOLD_S = 3.0   # default seconds to hold the end-frame still before B-roll starts


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


def _extract_sped_up_broll(segment: Path, raw_duration: float, target_duration: float, out_path: Path) -> bool:
    """
    Take the segment (excluding the last ~1s reserved for the still frame) and speed
    it up (setpts) to exactly fill target_duration.
    """
    if out_path.exists():
        return True
    available = max(raw_duration - 1.0, 0.5)   # leave the last second for the still grab
    speed_factor = available / target_duration if target_duration > 0 else 1.0
    setpts_factor = 1.0 / speed_factor
    cmd = [
        "ffmpeg", "-y",
        "-i", str(segment),
        "-t", str(available),
        "-vf", f"setpts={setpts_factor:.6f}*PTS",
        "-t", str(target_duration),   # hard-cap output — setpts + fps quantization can overshoot
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-an",
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print(f"[timeline] B-roll speed-up failed for {segment.name}:\n"
              f"{r.stderr.decode(errors='replace')[-600:]}")
        return False
    return True


def build_segment(
    raw_segment: Path,
    avatar_duration_s: float,
    out_dir: Path,
    index: int,
    still_hold_s: float = STILL_HOLD_S,
) -> dict:
    """
    Build the still + B-roll pieces for one step's segment.
    Returns a dict describing what was built and each piece's duration.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_duration = _ffprobe_duration(raw_segment)

    still_path = out_dir / f"segment_{index:02d}_still.mp4"
    broll_path = out_dir / f"segment_{index:02d}_broll.mp4"

    remaining = avatar_duration_s - still_hold_s

    if remaining <= 0.5 or raw_duration <= 1.5:
        # Fallback: not enough avatar time or raw footage for real B-roll —
        # extend the still frame to cover the whole avatar duration instead.
        print(f"[timeline] segment {index}: using freeze-frame fallback "
              f"(avatar={avatar_duration_s:.1f}s, raw={raw_duration:.1f}s)")
        ok = _extract_still_clip(raw_segment, avatar_duration_s, still_path)
        return {
            "index": index,
            "raw_segment": str(raw_segment),
            "raw_duration_s": round(raw_duration, 3),
            "still_path": str(still_path) if ok else None,
            "still_duration_s": round(avatar_duration_s, 3) if ok else 0.0,
            "broll_path": None,
            "broll_duration_s": 0.0,
            "fallback_freeze_frame": True,
        }

    still_ok = _extract_still_clip(raw_segment, still_hold_s, still_path)
    broll_ok = _extract_sped_up_broll(raw_segment, raw_duration, remaining, broll_path)

    return {
        "index": index,
        "raw_segment": str(raw_segment),
        "raw_duration_s": round(raw_duration, 3),
        "still_path": str(still_path) if still_ok else None,
        "still_duration_s": round(still_hold_s, 3) if still_ok else 0.0,
        "broll_path": str(broll_path) if broll_ok else None,
        "broll_duration_s": round(remaining, 3) if broll_ok else 0.0,
        "fallback_freeze_frame": False,
    }


def build_timeline(
    steps: list[dict],
    out_dir: Path,
    still_hold_s: float = STILL_HOLD_S,
) -> dict:
    """
    steps: ordered list of
        {"label": str, "raw_segment": Path, "avatar_path": Path, "avatar_duration_s": float}
    Computes cumulative start/end timestamps for every piece (still, B-roll, avatar)
    across the whole video and writes timeline.json.
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
            still_hold_s=still_hold_s,
        )

        still_start = cursor
        still_end = still_start + seg_result["still_duration_s"]
        entry = {
            "label": step["label"],
            "index": i,
            "still": {
                "path": seg_result["still_path"],
                "start_s": round(still_start, 3),
                "end_s": round(still_end, 3),
            },
        }
        cursor = still_end

        if not seg_result["fallback_freeze_frame"] and seg_result["broll_path"]:
            broll_start = cursor
            broll_end = broll_start + seg_result["broll_duration_s"]
            entry["broll"] = {
                "path": seg_result["broll_path"],
                "start_s": round(broll_start, 3),
                "end_s": round(broll_end, 3),
            }
            cursor = broll_end

        entry["avatar"] = {
            "path": str(step["avatar_path"]),
            "start_s": round(still_start, 3),   # avatar audio runs concurrent with still+broll
            "end_s": round(still_start + step["avatar_duration_s"], 3),
        }

        entries.append(entry)
        cursor = max(cursor, entry["avatar"]["end_s"])

    timeline = {
        "total_duration_s": round(cursor, 3),
        "still_hold_s": still_hold_s,
        "steps": entries,
    }

    atomic_write_json(out_path, timeline)
    print(f"[timeline] Built master timeline: {len(entries)} steps, "
          f"{timeline['total_duration_s']:.1f}s total -> {out_path.name}")
    return timeline
