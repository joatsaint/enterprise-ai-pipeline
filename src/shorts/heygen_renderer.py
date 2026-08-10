"""
Submits a script to the HeyGen v2 API with transparent (or green-screen) background,
polls until complete, downloads the avatar file, and extracts audio as WAV for Whisper.

Background modes (SHORTS_BG_MODE env var):
    transparent  — HeyGen renders alpha channel, outputs WebM (default)
    greenscreen  — HeyGen renders solid #00FF00, outputs MP4; FFmpeg chromakeys it later
    none         — no background param (original solid default)

Env vars:
    HEYGEN_API_KEY
    SHORTS_AVATAR_ID    (required — your own HeyGen avatar ID)
    SHORTS_VOICE_ID     (required — your own HeyGen voice ID)
    SHORTS_BRAND_KIT_ID (required — your own HeyGen brand kit ID)
    SHORTS_BG_MODE      (default: transparent)

Returns:
    {
        "video_id":   str,
        "mp4_path":   str,   # downloaded avatar file (.webm or .mp4)
        "audio_path": str,   # extracted mono WAV for Whisper
        "duration_s": float,
        "bg_mode":    str,   # actual mode used
    }

---

remove_background() — real, tested workaround for the Digital Twin avatar
type, which silently ignores the `background` API param entirely (unlike
the older photo-avatar type). Uses rembg (U2Net) for real neural
background segmentation, then composites onto a solid color (green by
default) so the output slots straight into the existing CapCut chromakey
workflow, no matter what background HeyGen actually returned.

Real, benchmarked cost, not a guess (2026-08-09, this machine, GTX 1660
Ti): CUDA execution provider did NOT actually engage despite
onnxruntime-gpu being installed (likely missing system CUDA/cuDNN
runtime, separate from the pip package) — falls back to CPU. Reusing one
warm rembg session across all frames (vs. creating a fresh session per
frame) is the real lever: ~7.7s/frame cold -> ~0.7s/frame warm, a ~10x
difference on its own. At 25fps, a ~114s avatar video is ~2,841 frames ->
roughly 33 minutes end to end. That's real time, not a background task to
silently trigger on every render — call this explicitly per video when
the wait is worth it, not wired into render()'s default flow.

Resumable by design (frame-level idempotency, same pattern as render()
above): if interrupted, rerun and it skips every frame already processed.
Never leaves a partial final video — the assembled mp4 is only written
once every frame succeeds, via the same atomic temp-then-rename pattern
used in download() above.
"""
import os
import time
import json
import shutil
import subprocess
from pathlib import Path

import requests

HEYGEN_BASE = "https://api.heygen.com"
POLL_INTERVAL = 12
POLL_MAX = 60

DEFAULT_BG_MODE      = "transparent"

GREENSCREEN_COLOR = "#00FF00"


def _api_key() -> str:
    key = os.environ.get("HEYGEN_API_KEY", "")
    if not key:
        raise EnvironmentError(
            "HEYGEN_API_KEY not set. Add it to .env:\n"
            "  HEYGEN_API_KEY=your_key_here\n"
            "Get it at: app.heygen.com > Settings > API"
        )
    return key


def _avatar_config() -> tuple[str, str, str]:
    avatar_id = os.environ.get("SHORTS_AVATAR_ID", "")
    voice_id = os.environ.get("SHORTS_VOICE_ID", "")
    brand_kit_id = os.environ.get("SHORTS_BRAND_KIT_ID", "")
    missing = [
        name
        for name, val in (
            ("SHORTS_AVATAR_ID", avatar_id),
            ("SHORTS_VOICE_ID", voice_id),
            ("SHORTS_BRAND_KIT_ID", brand_kit_id),
        )
        if not val
    ]
    if missing:
        raise EnvironmentError(
            f"{', '.join(missing)} not set. These are your own HeyGen avatar/voice/"
            "brand-kit IDs (each account's are different). Add them to .env — "
            "find yours at app.heygen.com after creating a photo avatar and voice clone."
        )
    return avatar_id, voice_id, brand_kit_id


def _headers() -> dict:
    return {
        "X-Api-Key": _api_key(),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _background_payload(bg_mode: str) -> dict | None:
    if bg_mode == "transparent":
        return {"type": "transparent"}
    if bg_mode == "greenscreen":
        return {"type": "color", "value": GREENSCREEN_COLOR}
    return None   # "none" — let HeyGen use its default


def submit(script: str, title: str = "Randy Shorts", bg_mode: str = DEFAULT_BG_MODE) -> str:
    """Submit the script to HeyGen. Returns video_id."""
    avatar_id, voice_id, brand_kit_id = _avatar_config()

    payload: dict = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal",
                },
                "voice": {
                    "type": "text",
                    "input_text": script,
                    "voice_id": voice_id,
                    "speed": 1.0,
                },
            }
        ],
        "dimension": {"width": 1080, "height": 1920},
        "title": title[:80],
        "brand_kit_id": brand_kit_id,
        "caption": False,
    }

    bg = _background_payload(bg_mode)
    if bg:
        payload["background"] = bg

    print(f"[heygen] Submitting — bg_mode={bg_mode}, {len(script)} chars")

    for attempt in range(1, 3):
        try:
            resp = requests.post(
                f"{HEYGEN_BASE}/v2/video/generate",
                headers=_headers(),
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            video_id = (
                data.get("data", {}).get("video_id")
                or data.get("video_id")
            )
            if not video_id:
                raise ValueError(f"No video_id in response: {data}")
            print(f"[heygen] Submitted — video_id: {video_id}")
            return video_id
        except Exception as exc:
            if attempt == 1:
                print(f"[heygen] Submit failed ({exc}), retrying in 5s...")
                time.sleep(5)
            else:
                raise RuntimeError(f"HeyGen submit failed: {exc}") from exc

    raise RuntimeError("unreachable")


def poll(video_id: str) -> tuple[str, str]:
    """
    Poll until ready. Returns (download_url, file_format).
    file_format is "webm" or "mp4" based on the URL.
    """
    print(f"[heygen] Polling {video_id}...", flush=True)
    for attempt in range(POLL_MAX):
        try:
            resp = requests.get(
                f"{HEYGEN_BASE}/v1/video_status.get",
                headers=_headers(),
                params={"video_id": video_id},
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json().get("data", {})
            status = data.get("status", "")
            print(f"[heygen] [{attempt + 1}/{POLL_MAX}] status={status}", end="\r", flush=True)

            if status == "completed":
                url = data.get("video_url") or data.get("url")
                if not url:
                    raise ValueError(f"status=completed but no video_url: {data}")
                fmt = "webm" if ".webm" in url.lower() else "mp4"
                print(f"\n[heygen] Done — format={fmt}")
                return url, fmt

            if status in ("failed", "error"):
                raise RuntimeError(f"HeyGen video failed: {data}")

            time.sleep(POLL_INTERVAL)

        except RuntimeError:
            raise
        except Exception as exc:
            print(f"\n[heygen] Poll error: {exc}. Retrying...")
            time.sleep(POLL_INTERVAL)

    raise TimeoutError(f"HeyGen video {video_id} did not complete in time.")


def download(url: str, dest: Path) -> Path:
    """Download the HeyGen avatar file."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"[heygen] Downloading to {dest.name}...")
    for attempt in range(1, 3):
        try:
            with requests.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                tmp = dest.with_suffix(".tmp")
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(chunk_size=65536):
                        f.write(chunk)
                tmp.rename(dest)
            print(f"[heygen] Saved: {dest}")
            return dest
        except Exception as exc:
            if attempt == 1:
                print(f"[heygen] Download failed ({exc}), retrying...")
                time.sleep(5)
            else:
                dest.unlink(missing_ok=True)
                raise RuntimeError(f"HeyGen download failed: {exc}") from exc
    raise RuntimeError("unreachable")


def extract_audio(avatar_path: Path, audio_path: Path) -> Path:
    """Extract mono 16kHz WAV from the avatar video for Whisper."""
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-i", str(avatar_path),
        "-vn", "-ac", "1", "-ar", "16000",
        "-acodec", "pcm_s16le", str(audio_path),
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg audio extract failed:\n{result.stderr.decode(errors='replace')}"
        )
    print(f"[heygen] Audio extracted: {audio_path.name}")
    return audio_path


def get_credits_remaining() -> int | None:
    """Returns current premium credits remaining, or None on failure."""
    try:
        resp = requests.get(
            f"{HEYGEN_BASE}/v1/user/remaining_quota",
            headers=_headers(),
            timeout=10,
        )
        if resp.ok:
            data = resp.json().get("data", {})
            # v1 endpoint returns remaining_quota directly
            return data.get("remaining_quota")
    except Exception:
        pass
    # Fallback: try the /v2/user/me endpoint
    try:
        resp = requests.get(f"{HEYGEN_BASE}/v2/user/me", headers=_headers(), timeout=10)
        if resp.ok:
            sub = resp.json().get("data", {}).get("subscription", {})
            return sub.get("credits", {}).get("premium_credits", {}).get("remaining")
    except Exception:
        pass
    return None


def get_duration(avatar_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", str(avatar_path),
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        return 0.0
    try:
        return float(json.loads(result.stdout)["format"]["duration"])
    except Exception:
        return 0.0


def render(script: str, slug: str, out_dir: Path) -> dict:
    """
    Full pipeline: submit → poll → download → extract audio.
    Idempotent — skips steps whose output files already exist.
    """
    bg_mode = os.environ.get("SHORTS_BG_MODE", DEFAULT_BG_MODE)

    # Avatar file is .webm for transparent mode, .mp4 otherwise
    avatar_ext  = "webm" if bg_mode == "transparent" else "mp4"
    avatar_path = out_dir / f"heygen_raw.{avatar_ext}"
    audio_path  = out_dir / "audio.wav"
    meta_path   = out_dir / "heygen_meta.json"

    credits_before = get_credits_remaining()
    if credits_before is not None:
        print(f"[heygen] Credits before render: {credits_before}")

    video_id = None
    actual_bg = bg_mode

    # Resume from an existing submission if we crashed mid-poll
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text())
            video_id  = meta.get("video_id")
            actual_bg = meta.get("bg_mode", bg_mode)
            # Reconcile avatar path if bg_mode changed on resume
            saved_ext = "webm" if actual_bg == "transparent" else "mp4"
            avatar_path = out_dir / f"heygen_raw.{saved_ext}"
            print(f"[heygen] Resuming from existing video_id: {video_id}")
        except Exception:
            pass

    if not avatar_path.exists():
        if not video_id:
            video_id = submit(script, title=slug, bg_mode=bg_mode)
            meta_path.write_text(
                json.dumps({"video_id": video_id, "bg_mode": bg_mode}),
                encoding="utf-8",
            )
            actual_bg = bg_mode

        url, detected_fmt = poll(video_id)

        # HeyGen may return MP4 even when transparent was requested (plan limitation)
        if detected_fmt != avatar_ext:
            print(f"[heygen] WARN: requested {avatar_ext} but got {detected_fmt}. Adjusting.")
            avatar_path = out_dir / f"heygen_raw.{detected_fmt}"
            actual_bg = "greenscreen" if bg_mode == "transparent" and detected_fmt == "mp4" else actual_bg
            # Update meta so stitcher knows the actual format
            meta_path.write_text(
                json.dumps({"video_id": video_id, "bg_mode": actual_bg, "format": detected_fmt}),
                encoding="utf-8",
            )

        download(url, avatar_path)
    else:
        print(f"[heygen] Avatar already exists, skipping render: {avatar_path.name}")
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text())
                actual_bg = meta.get("bg_mode", bg_mode)
                video_id  = meta.get("video_id", "unknown")
            except Exception:
                pass

    if not audio_path.exists():
        extract_audio(avatar_path, audio_path)
    else:
        print(f"[heygen] Audio already exists, skipping: {audio_path.name}")

    duration = get_duration(avatar_path)

    credits_after = get_credits_remaining()
    credits_used = None
    if credits_before is not None and credits_after is not None:
        credits_used = credits_before - credits_after
        print(f"[heygen] Credits after render: {credits_after} (used: {credits_used})")

    return {
        "video_id":      video_id or "unknown",
        "avatar_path":   str(avatar_path),
        "audio_path":    str(audio_path),
        "duration_s":    duration,
        "bg_mode":       actual_bg,
        "credits_before": credits_before,
        "credits_after":  credits_after,
        "credits_used":   credits_used,
    }


REMBG_MODEL = "u2net"
REMBG_GREEN = "#00FF00"


def _get_rembg_session():
    """One warm session, reused across every frame — the real ~10x lever
    (see module docstring). Imported lazily so `rembg` stays an optional
    dependency for callers that never touch background removal."""
    from rembg import new_session
    return new_session(REMBG_MODEL, providers=["CUDAExecutionProvider", "CPUExecutionProvider"])


def remove_background(
    avatar_path: Path,
    out_path: Path,
    bg_color: str = REMBG_GREEN,
    fps: int = 25,
) -> Path:
    """
    Real neural background removal for HeyGen avatar footage, via rembg —
    a working substitute for the Digital Twin avatar type's `background`
    API param, which HeyGen silently ignores. Composites onto solid
    bg_color (green by default) so the output drops straight into the
    existing CapCut chromakey step.

    ~33 minutes for a ~114s clip on this machine (CPU fallback — see module
    docstring). Call explicitly per video; never triggered automatically by
    render() above.

    Resumable: frame-level idempotency via a per-video temp frames dir.
    Interrupting and rerunning skips every frame already processed.
    Never leaves a partial final video — the assembled mp4 only gets
    written (atomically) once every frame succeeds.
    """
    from rembg import remove
    from PIL import Image

    avatar_path = Path(avatar_path)
    out_path = Path(out_path)
    if not avatar_path.exists():
        raise FileNotFoundError(f"remove_background: source not found: {avatar_path}")

    frames_dir = out_path.parent / f".{out_path.stem}_bgremove_frames"
    raw_dir = frames_dir / "raw"
    done_dir = frames_dir / "done"
    raw_dir.mkdir(parents=True, exist_ok=True)
    done_dir.mkdir(parents=True, exist_ok=True)

    # Extract frames only if not already extracted (resumability: don't
    # re-extract on a rerun, ffmpeg's -n leaves existing frames untouched).
    existing_raw = sorted(raw_dir.glob("*.png"))
    if not existing_raw:
        print(f"[bg_remove] Extracting frames from {avatar_path.name}...")
        cmd = [
            "ffmpeg", "-y", "-i", str(avatar_path),
            "-vf", f"fps={fps}",
            str(raw_dir / "%06d.png"),
        ]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"bg_remove: frame extraction failed:\n{result.stderr.decode(errors='replace')}"
            )
        existing_raw = sorted(raw_dir.glob("*.png"))
    total = len(existing_raw)
    if total == 0:
        raise RuntimeError(f"bg_remove: no frames extracted from {avatar_path}")

    print(f"[bg_remove] {total} frames — processing (resumable, skips completed frames)...")
    session = _get_rembg_session()
    bg_rgb = tuple(int(bg_color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))

    t0 = time.time()
    processed_this_run = 0
    for i, raw_frame in enumerate(existing_raw, start=1):
        done_frame = done_dir / raw_frame.name
        if done_frame.exists():
            continue  # already processed on a prior run — skip
        img = Image.open(raw_frame)
        cutout = remove(img, session=session)  # RGBA, subject isolated
        composited = Image.new("RGBA", cutout.size, bg_rgb + (255,))
        composited.alpha_composite(cutout)
        composited.convert("RGB").save(done_frame)
        processed_this_run += 1
        if processed_this_run % 25 == 0:
            elapsed = time.time() - t0
            rate = elapsed / processed_this_run
            remaining = (total - i) * rate
            print(
                f"[bg_remove] {i}/{total} "
                f"({rate:.2f}s/frame, ~{remaining/60:.1f}m remaining)",
                end="\r", flush=True,
            )
    print(f"\n[bg_remove] All {total} frames done.")

    # Reassemble: processed frames + original audio track, atomic write.
    print("[bg_remove] Reassembling video with original audio...")
    tmp_out = out_path.with_suffix(".tmp.mp4")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps), "-i", str(done_dir / "%06d.png"),
        "-i", str(avatar_path),
        "-map", "0:v:0", "-map", "1:a:0?",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
        "-c:a", "aac", "-shortest",
        str(tmp_out),
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        tmp_out.unlink(missing_ok=True)
        raise RuntimeError(
            f"bg_remove: reassembly failed:\n{result.stderr.decode(errors='replace')}"
        )
    tmp_out.rename(out_path)  # atomic on same filesystem

    # Only clean up the working frames dir after a fully successful run —
    # if anything above raised, the partial frames stay for a resumed rerun.
    shutil.rmtree(frames_dir, ignore_errors=True)

    print(f"[bg_remove] Done: {out_path} ({time.time()-t0:.0f}s total)")
    return out_path


# Named FFmpeg filter-chain presets for talking-head footage polish — an
# optional, fast (pure FFmpeg, no ML, near-instant) CapCut-replacement
# step. Real-tested 2026-08-09 against actual walk-and-talk footage:
# subtle skin-texture smoothing + slightly sharper eyes + a touch warmer
# tone, no waxy/over-processed look, beard/hair texture mostly untouched
# since smartblur is edge-aware. Source: OpenMontage's face_enhance.py
# tool (github.com/calesthio/OpenMontage), cherry-picked as filter recipes
# only — not the whole framework.
FACE_ENHANCE_PRESETS = {
    "soft_skin": "smartblur=lr=1.0:ls=-0.5:lt=-3.0:cr=0.5:cs=-0.5:ct=-3.0",
    "sharpen": "unsharp=5:5:1.0:5:5:0.0",
    "sharpen_light": "unsharp=3:3:0.5:3:3:0.0",
    "brighten": "curves=all='0/0 0.25/0.35 0.5/0.55 0.75/0.8 1/1'",
    "contrast_boost": "curves=all='0/0 0.25/0.20 0.5/0.5 0.75/0.80 1/1'",
    "warm": "colorbalance=rs=0.05:gs=0.0:bs=-0.05:rm=0.05:gm=0.0:bm=-0.03",
    "cool": "colorbalance=rs=-0.03:gs=0.0:bs=0.05:rm=-0.02:gm=0.0:bm=0.03",
    "denoise": "hqdn3d=4:3:6:4",
    "talking_head_standard": (
        "smartblur=lr=1.0:ls=-0.5:lt=-3.0:cr=0.5:cs=-0.5:ct=-3.0,"
        "unsharp=5:5:0.6:5:5:0.0,"
        "colorbalance=rs=0.06:gs=0.01:bs=-0.04:rm=0.04:gm=0.01:bm=-0.03"
    ),
}


def face_enhance(
    video_path: Path,
    out_path: Path,
    preset: str = "talking_head_standard",
) -> Path:
    """
    Apply a named FFmpeg polish filter chain (see FACE_ENHANCE_PRESETS) to
    talking-head footage. Fast — pure FFmpeg, no model download, no per-
    frame ML inference (unlike remove_background above). Safe to run on
    every video; a real, subtle improvement, not a beauty-filter overhaul.
    """
    video_path = Path(video_path)
    out_path = Path(out_path)
    if not video_path.exists():
        raise FileNotFoundError(f"face_enhance: source not found: {video_path}")
    if preset not in FACE_ENHANCE_PRESETS:
        raise ValueError(
            f"face_enhance: unknown preset {preset!r} — choose from {sorted(FACE_ENHANCE_PRESETS)}"
        )

    tmp_out = out_path.with_suffix(".tmp.mp4")
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vf", FACE_ENHANCE_PRESETS[preset],
        "-c:a", "copy",
        str(tmp_out),
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        tmp_out.unlink(missing_ok=True)
        raise RuntimeError(
            f"face_enhance: FFmpeg failed:\n{result.stderr.decode(errors='replace')}"
        )
    tmp_out.rename(out_path)  # atomic on same filesystem
    print(f"[face_enhance] Done ({preset}): {out_path}")
    return out_path
