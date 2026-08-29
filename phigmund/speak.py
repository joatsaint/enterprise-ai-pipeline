"""
Phigmund Voice System — five-mode TTS via OpenAI

Modes:
  standard  — KIT from Knight Rider. Calm, synthesized, authoritative.  (voice: onyx)
  snarky    — Douglas Adams / Marvin. Mildly resigned.                  (voice: echo)
  coaching  — Warm senior colleague.                                     (voice: nova)
  alert     — HAL. Clipped. No humor.                                   (voice: alloy)
  grail     — French Taunter / theatrical British. Holy Grail mode.     (voice: fable)

Usage:
  python speak.py "Your text here"
  python speak.py "Your text here" --mode grail
  python speak.py --event swarm_init --mode grail
  python speak.py --list-events
  echo "Text from pipe" | python speak.py

Auto-tag routing: if text begins with [GRAIL], [ALERT], [SNARK], [COACH] —
the tag is stripped and the matching mode is used automatically.

Playback: WAV via winsound (Windows built-in, no extra install needed).
"""

import os
import sys
import json
import tempfile
import winsound
import argparse
import urllib.request
import urllib.error
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================
VOICE_MAP = {
    "standard": "onyx",
    "snarky":   "echo",
    "coaching": "nova",
    "alert":    "alloy",
    "grail":    "fable",
}

TAG_TO_MODE = {
    "[GRAIL]":  "grail",
    "[ALERT]":  "alert",
    "[SNARK]":  "snarky",
    "[COACH]":  "coaching",
    "[STANDARD]": "standard",
}

DEFAULT_MODE = "standard"
TTS_MODEL = "tts-1"   # tts-1 is fast; tts-1-hd for higher quality at 2x cost

# ============================================================
# ENV — load OPENAI_API_KEY from .env
# ============================================================
def load_api_key() -> str:
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print(f"[ERROR] .env not found at {env_path}")
        sys.exit(1)
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("OPENAI_API_KEY="):
                key = line.split("=", 1)[1].strip()
                if key and key != "your_key_here":
                    return key
    print("[ERROR] OPENAI_API_KEY not set in .env")
    sys.exit(1)


# ============================================================
# AUTO-TAG DETECTION
# ============================================================
def detect_mode_from_tag(text: str) -> tuple[str, str]:
    """
    If text starts with a known tag like [GRAIL], strip it and return
    (cleaned_text, detected_mode). Otherwise return (text, None).
    """
    for tag, mode in TAG_TO_MODE.items():
        if text.startswith(tag):
            return text[len(tag):].strip(), mode
    return text, None


# ============================================================
# TTS — OpenAI REST call, no SDK required
# ============================================================
def synthesize(text: str, voice: str, api_key: str) -> bytes:
    """Call OpenAI TTS and return raw WAV bytes."""
    url = "https://api.openai.com/v1/audio/speech"
    payload = {
        "model": TTS_MODEL,
        "input": text,
        "voice": voice,
        "response_format": "wav",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[ERROR] OpenAI TTS HTTP {e.code}: {body[:200]}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"[ERROR] Cannot reach OpenAI API: {e}")
        sys.exit(1)


# ============================================================
# PLAYBACK — winsound (Windows built-in, synchronous)
# ============================================================
def play_wav(wav_bytes: bytes) -> None:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(wav_bytes)
        tmp_path = tmp.name
    try:
        winsound.PlaySound(tmp_path, winsound.SND_FILENAME)
    finally:
        os.unlink(tmp_path)


# ============================================================
# MODE-SWITCH ACKNOWLEDGMENT LINES
# ============================================================
MODE_SWITCH_LINES = {
    "snarky":   "Switching to Snark. I have been saving this for a special occasion.",
    "coaching": "Switching to Coaching mode. I will attempt to be encouraging. No promises.",
    "alert":    "Alert mode. Humor suspended.",
    "grail":    "Engaging Holy Grail protocol. You have been warned.",
    "standard": "Returning to standard operations. The dignity of this institution is restored.",
}


# ============================================================
# MAIN
# ============================================================
def speak(text: str, mode: str, api_key: str, announce_mode: bool = False) -> None:
    voice = VOICE_MAP[mode]

    if announce_mode:
        ack = MODE_SWITCH_LINES.get(mode)
        if ack:
            print(f"[Phigmund/{mode}] {ack}")
            wav = synthesize(ack, voice, api_key)
            play_wav(wav)

    print(f"[Phigmund/{mode}] {text}")
    wav = synthesize(text, voice, api_key)
    play_wav(wav)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phigmund voice system — speak text via OpenAI TTS"
    )
    parser.add_argument("text", nargs="?", help="Text to speak (or pipe via stdin)")
    parser.add_argument("--mode", choices=list(VOICE_MAP.keys()), default=None,
                        help="Voice mode (default: standard, or auto-detected from [TAG])")
    parser.add_argument("--event", metavar="EVENT_TYPE",
                        help="Speak a Phigmund library line for this event type")
    parser.add_argument("--list-events", action="store_true",
                        help="List all available event types")
    parser.add_argument("--announce-mode", action="store_true",
                        help="Speak a mode-switch acknowledgment line first")
    args = parser.parse_args()

    if args.list_events:
        sys.path.insert(0, str(Path(__file__).parent))
        from phigmund_lines import list_event_types
        types = list_event_types()
        print("\nAvailable event types:")
        for m, events in types.items():
            print(f"  --mode {m}:  {', '.join(events)}")
        return

    # Build the text to speak
    if args.event:
        sys.path.insert(0, str(Path(__file__).parent))
        from phigmund_lines import get_line
        mode_for_event = args.mode or ("grail" if args.event in [
            "bypass_gate", "empty_output", "zero_confidence",
            "swarm_init", "warning", "approval_required"
        ] else "standard")
        text = get_line(args.event, mode=mode_for_event)
        mode = mode_for_event

    elif args.text:
        text = args.text
        text, detected = detect_mode_from_tag(text)
        mode = args.mode or detected or DEFAULT_MODE

    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
        text, detected = detect_mode_from_tag(text)
        mode = args.mode or detected or DEFAULT_MODE

    else:
        parser.print_help()
        sys.exit(1)

    if not text:
        print("[ERROR] No text to speak.")
        sys.exit(1)

    api_key = load_api_key()
    speak(text, mode, api_key, announce_mode=args.announce_mode)


if __name__ == "__main__":
    main()
