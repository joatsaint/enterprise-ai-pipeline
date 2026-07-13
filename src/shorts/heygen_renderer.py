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
"""
import os
import time
import json
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
