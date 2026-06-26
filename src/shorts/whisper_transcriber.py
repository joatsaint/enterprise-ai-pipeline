"""
Transcribes the HeyGen avatar audio with Whisper (word-level timestamps).

Requires: pip install openai-whisper

Returns a timestamps dict:
{
    "duration_s": float,
    "segments": [
        {
            "start": float,   # seconds
            "end":   float,
            "text":  str,
            "words": [{"word": str, "start": float, "end": float}]
        }
    ],
    "section_frames": {      # start frame (at 30fps) for each script section
        "hook":        int,
        "problem":     int,
        "insight":     int,
        "implication": int,
        "cta":         int,
    }
}
"""
import json
from pathlib import Path

WHISPER_MODEL = "base"
FPS = 30


def _match_section_frames(whisper_result: dict, sections: list) -> dict:
    """
    For each script section, find the word-level start time in the Whisper output
    and convert to frame number.

    Strategy: scan all words for the first token of each section's text, then
    return that word's start time × FPS.
    """
    all_words = []
    for seg in whisper_result.get("segments", []):
        for w in seg.get("words", []):
            all_words.append(w)

    def _first_token(text: str) -> str:
        return text.strip().split()[0].lower().strip(".,!?;:")

    frames = {}
    search_from = 0
    for section in sections:
        label = section["label"]
        token = _first_token(section["text"])
        matched = False
        for i, w in enumerate(all_words[search_from:], start=search_from):
            word_clean = w["word"].strip().lower().strip(".,!?;:")
            if word_clean == token or word_clean.startswith(token[:4]):
                frames[label] = int(w["start"] * FPS)
                search_from = i + 1
                matched = True
                break
        if not matched:
            # Fall back: evenly distribute remaining sections
            prev_frame = frames.get(sections[sections.index(next(s for s in sections if s["label"] == label)) - 1]["label"], 0) if label != sections[0]["label"] else 0
            frames[label] = prev_frame

    return frames


def transcribe(audio_path: Path, sections: list, out_path: Path) -> dict:
    """
    Transcribe audio_path with Whisper (word timestamps).
    Writes result to out_path as JSON.
    Returns parsed timestamps dict.
    """
    if out_path.exists():
        print(f"[whisper] Transcript already exists, loading: {out_path.name}")
        data = json.loads(out_path.read_text(encoding="utf-8"))
        return data

    print(f"[whisper] Transcribing {audio_path.name} (model={WHISPER_MODEL})...")
    try:
        import whisper  # type: ignore
    except ImportError:
        raise ImportError(
            "openai-whisper is not installed.\n"
            "Run: pip install openai-whisper\n"
            "Also needs ffmpeg on PATH."
        )

    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(str(audio_path), word_timestamps=True, language="en")

    # Whisper doesn't always populate top-level "duration" — derive from last segment
    duration = result.get("duration") or 0.0
    if not duration and result.get("segments"):
        duration = result["segments"][-1]["end"]
    segments = []
    for seg in result.get("segments", []):
        words = [
            {"word": w["word"], "start": round(w["start"], 3), "end": round(w["end"], 3)}
            for w in seg.get("words", [])
        ]
        segments.append({
            "start": round(seg["start"], 3),
            "end":   round(seg["end"], 3),
            "text":  seg["text"].strip(),
            "words": words,
        })

    section_frames = _match_section_frames({"segments": segments}, sections)

    data = {
        "duration_s":     round(duration, 3),
        "segments":       segments,
        "section_frames": section_frames,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[whisper] Saved timestamps: {out_path.name}")
    return data
