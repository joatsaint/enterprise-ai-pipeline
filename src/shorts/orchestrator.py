"""
YouTube Shorts pipeline orchestrator.

Steps (all idempotent — safe to re-run from any point):
  1. Select pain point (radar state or --pain-point override)
  2. Write script (Claude Sonnet → 5-part + text hook)
  3. Render avatar (HeyGen v2 API → 1080×1920 MP4 + WAV audio)
  4. Transcribe (Whisper → word timestamps)
  5. Render top-half graphics (Remotion A + gpt-image-1 B)
  6. Stitch finals (FFmpeg → captioned 1080×1920 shorts)

Output folder: content-engine/content/_video/shorts/{slug}/
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from src.shorts import pain_point_selector, script_writer, heygen_renderer
from src.shorts import whisper_transcriber, top_half_renderer, ffmpeg_stitcher
from src.utils.atomic import atomic_write_json

ROOT = Path(__file__).resolve().parent.parent.parent
SHORTS_BASE = ROOT / "content-engine" / "content" / "_video" / "shorts"
ERROR_LOG = ROOT / "logs" / "error_log.json"


def _log_error(step: str, slug: str, exc: Exception):
    ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
    try:
        if ERROR_LOG.exists():
            data = json.loads(ERROR_LOG.read_text(encoding="utf-8"))
        else:
            data = {"errors": []}
        data.setdefault("errors", []).append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "pipeline": "shorts",
            "step": step,
            "slug": slug,
            "error": str(exc),
        })
        atomic_write_json(ERROR_LOG, data)
    except Exception:
        pass


def _save_state(out_dir: Path, state: dict):
    atomic_write_json(out_dir / "metadata.json", state)


def _load_state(out_dir: Path) -> dict:
    p = out_dir / "metadata.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_script(out_dir: Path, script_data: dict, pain_point: dict):
    text = "\n\n".join([
        f"# YouTube Short Script",
        f"**Slug:** {script_data['slug']}",
        f"**Pain point:** {pain_point['title']}",
        f"**Source:** {pain_point.get('source', 'unknown')}",
        f"**Word count:** {script_data['word_count']}",
        "",
        f"## Text Hook (screen overlay — top third, first 10 sec)",
        f"> {script_data['text_hook']}",
        "",
        "## Spoken Script",
        script_data["script"],
        "",
        "## Sections",
    ] + [
        f"**{s['label'].upper()}** ({s['start']}–{s['end']} chars)\n{s['text']}"
        for s in script_data["sections"]
    ])
    (out_dir / "script.md").write_text(text, encoding="utf-8")


def run(
    manual_pain_point: str | None = None,
    variant: str = "both",
    dry_run: bool = False,
) -> dict:
    """
    Run the full shorts pipeline.

    manual_pain_point: override pain point selector with this string
    variant: "a" | "b" | "both"
    dry_run: run through step 2 only (no API calls after script write)
    """
    started = time.time()
    print("=" * 56)
    print(" YouTube Shorts Pipeline")
    print("=" * 56)

    # ── Step 1: Select pain point ────────────────────────────
    print("[1/6] Selecting pain point...")
    try:
        pain_point = pain_point_selector.select(manual_override=manual_pain_point)
        print(f"      Pain point: {pain_point['title'][:80]}")
        print(f"      Source: {pain_point['source']} | Score: {pain_point['priority_score']}")
    except Exception as exc:
        print(f"[FAIL] Pain point selection failed: {exc}")
        return {"status": "failed", "step": "pain_point_selector", "error": str(exc)}

    # ── Step 2: Write script ─────────────────────────────────
    print("[2/6] Writing script...")
    try:
        script_data = script_writer.write(pain_point)
        slug = script_data["slug"]
        out_dir = SHORTS_BASE / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        _save_script(out_dir, script_data, pain_point)
        state = _load_state(out_dir)
        state.update({
            "slug": slug,
            "pain_point": pain_point,
            "script": script_data["script"],
            "text_hook": script_data["text_hook"],
            "sections": script_data["sections"],
            "word_count": script_data["word_count"],
            "created": datetime.now(timezone.utc).isoformat(),
        })
        _save_state(out_dir, state)
        print(f"      Slug: {slug} | {script_data['word_count']} words")
        print(f"      Text hook: {script_data['text_hook']}")
    except Exception as exc:
        _log_error("script_writer", "unknown", exc)
        print(f"[FAIL] Script writing failed: {exc}")
        return {"status": "failed", "step": "script_writer", "error": str(exc)}

    if dry_run:
        print(f"\n[DRY RUN] Stopping after script. Output: {out_dir.relative_to(ROOT)}")
        return {"status": "dry_run", "slug": slug, "out_dir": str(out_dir)}

    # ── Step 3: Render HeyGen avatar ─────────────────────────
    print("[3/6] Rendering HeyGen avatar (this takes 5–15 min)...")
    try:
        heygen_result = heygen_renderer.render(
            script=script_data["script"],
            slug=slug,
            out_dir=out_dir,
        )
        state.update({"heygen": heygen_result})
        _save_state(out_dir, state)
        print(f"      Duration: {heygen_result['duration_s']:.1f}s | bg_mode: {heygen_result['bg_mode']}")
    except Exception as exc:
        _log_error("heygen_renderer", slug, exc)
        print(f"[FAIL] HeyGen render failed: {exc}")
        return {"status": "failed", "step": "heygen_renderer", "slug": slug, "error": str(exc)}

    # ── Step 4: Transcribe with Whisper ──────────────────────
    print("[4/6] Transcribing with Whisper (word timestamps)...")
    try:
        whisper_data = whisper_transcriber.transcribe(
            audio_path=Path(heygen_result["audio_path"]),  # type: ignore[arg-type]
            sections=script_data["sections"],
            out_path=out_dir / "whisper.json",
        )
        state.update({"whisper_duration_s": whisper_data["duration_s"]})
        _save_state(out_dir, state)
        n_words = sum(len(s.get("words", [])) for s in whisper_data["segments"])
        print(f"      {n_words} words timestamped across {len(whisper_data['segments'])} segments")
    except Exception as exc:
        _log_error("whisper_transcriber", slug, exc)
        print(f"[FAIL] Whisper transcription failed: {exc}")
        return {"status": "failed", "step": "whisper_transcriber", "slug": slug, "error": str(exc)}

    # ── Step 5: Render top-half graphics ─────────────────────
    print(f"[5/6] Rendering top-half graphics (variant={variant})...")
    top_results = {}
    try:
        top_results = top_half_renderer.render(
            whisper=whisper_data,
            sections=script_data["sections"],
            text_hook=script_data["text_hook"],
            out_dir=out_dir,
            variant=variant,
        )
        state.update({"top_half": {k: str(v) if v else None for k, v in top_results.items()}})
        _save_state(out_dir, state)
        for k, v in top_results.items():
            print(f"      {k}: {'OK' if v else 'skipped'}")
    except Exception as exc:
        _log_error("top_half_renderer", slug, exc)
        print(f"[WARN] Top-half render failed: {exc}. Continuing without graphics.")

    # ── Step 6: Stitch finals ────────────────────────────────
    print("[6/6] Stitching final shorts...")
    avatar_path = Path(heygen_result["avatar_path"])
    bg_mode     = heygen_result.get("bg_mode", "transparent")
    final_results = {}
    try:
        final_results = ffmpeg_stitcher.run(
            out_dir=out_dir,
            avatar_path=avatar_path,
            whisper=whisper_data,
            text_hook=script_data["text_hook"],
            bg_mode=bg_mode,
            top_a=top_results.get("top_a"),
            top_b=top_results.get("top_b"),
        )
        state.update({"finals": {k: str(v) if v else None for k, v in final_results.items()}})
        state["status"] = "complete"
        _save_state(out_dir, state)
        for k, v in final_results.items():
            print(f"      {k}: {'OK' if v else 'skipped'}")
    except Exception as exc:
        _log_error("ffmpeg_stitcher", slug, exc)
        print(f"[FAIL] Stitch failed: {exc}")
        state["status"] = "stitch_failed"
        _save_state(out_dir, state)

    elapsed = time.time() - started
    print()
    print("━" * 56)
    print(f" Shorts Pipeline Complete — {elapsed:.0f}s")
    print("━" * 56)
    print(f" Slug:       {slug}")
    print(f" Output:     {out_dir.relative_to(ROOT)}")
    for k, v in final_results.items():
        status = str(v.relative_to(ROOT)) if v else "not generated"
        print(f" {k}:    {status}")
    print("━" * 56)
    print(f" Review script.md, then pick final_a.mp4 or final_b.mp4 to post.")

    return {
        "status": "complete",
        "slug": slug,
        "out_dir": str(out_dir),
        "finals": {k: str(v) if v else None for k, v in final_results.items()},
    }
