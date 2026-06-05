"""
Daily pipeline runner for the YouTube Transcript Knowledge Base.

Full pipeline (runs in order):
  1. Incremental download for all active channel groups
  2. Rebuild knowledge base index
  3. Generate daily digest
  4. Run pain point analysis on all groups

Usage:
  python run_daily.py              # interactive — prints to terminal
  python run_daily.py --scheduled  # silent — output to logs/daily_run_output.log

Called by Windows Task Scheduler via digest_task.xml.
"""
import json
import os
import sys
from datetime import datetime, timezone


LOG_DIR = "logs"
RUN_LOG_PATH = os.path.join(LOG_DIR, "daily_run_log.json")
OUTPUT_LOG_PATH = os.path.join(LOG_DIR, "daily_run_output.log")
ERROR_LOG_PATH = os.path.join(LOG_DIR, "error_log.json")

GROUPS = [
    "ai-and-claude-code",
    "career-and-job-search",
    "developer-technical",
    "bitcoin-and-economic-news",
    "enterprise-strategy",
    "ai-marketing",
]


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _log(msg, fh=None):
    print(msg)
    if fh:
        fh.write(msg + "\n")
        fh.flush()


def _append_error_log(step, message):
    os.makedirs(LOG_DIR, exist_ok=True)
    log = {"errors": []}
    if os.path.isfile(ERROR_LOG_PATH):
        try:
            with open(ERROR_LOG_PATH, "r", encoding="utf-8") as f:
                log = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    log.setdefault("errors", []).append({
        "timestamp": _now(),
        "module": f"daily_pipeline/{step}",
        "error": message,
    })
    with open(ERROR_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def _append_run_log(entry):
    os.makedirs(LOG_DIR, exist_ok=True)
    log = {"runs": []}
    if os.path.isfile(RUN_LOG_PATH):
        try:
            with open(RUN_LOG_PATH, "r", encoding="utf-8") as f:
                log = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    log.setdefault("runs", []).append(entry)
    with open(RUN_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def run_pipeline(scheduled=False):
    os.makedirs(LOG_DIR, exist_ok=True)
    started_at = _now()
    results = {}

    # In scheduled mode, mirror all output to a rolling log file
    log_fh = None
    if scheduled:
        log_fh = open(OUTPUT_LOG_PATH, "a", encoding="utf-8")
        # Redirect stdout so module-level prints also land in the log file
        sys.stdout = log_fh

    try:
        _log(f"\n{'='*50}", log_fh)
        _log(f" Daily Pipeline — {started_at}", log_fh)
        _log(f"{'='*50}", log_fh)

        # ------------------------------------------------------------------
        # Step 1 — Incremental download for all active groups
        # ------------------------------------------------------------------
        from src.downloader.channel import run_group

        for group in GROUPS:
            _log(f"\n[1] Downloading new transcripts — group: {group}", log_fh)
            try:
                run_group(group, force_full=False)
                results[f"download_{group}"] = "ok"
            except Exception as exc:
                msg = f"Download failed for group '{group}': {exc}"
                _log(f"    ERROR: {msg}", log_fh)
                _append_error_log(f"download/{group}", msg)
                results[f"download_{group}"] = f"error: {exc}"

        # ------------------------------------------------------------------
        # Step 2 — Rebuild knowledge base index
        # ------------------------------------------------------------------
        _log("\n[2] Rebuilding knowledge base index...", log_fh)
        try:
            from src.knowledge_base.indexer import build_index
            build_index()
            results["index"] = "ok"
        except Exception as exc:
            msg = f"Indexer failed: {exc}"
            _log(f"    ERROR: {msg}", log_fh)
            _append_error_log("indexer", msg)
            results["index"] = f"error: {exc}"

        # ------------------------------------------------------------------
        # Step 3 — Generate daily digest
        # ------------------------------------------------------------------
        _log("\n[3] Generating daily digest...", log_fh)
        try:
            from src.knowledge_base.digest import run_digest
            run_digest(scheduled=scheduled)
            results["digest"] = "ok"
        except Exception as exc:
            msg = f"Digest failed: {exc}"
            _log(f"    ERROR: {msg}", log_fh)
            _append_error_log("digest", msg)
            results["digest"] = f"error: {exc}"

        # ------------------------------------------------------------------
        # Step 4 — Pain point analysis on all groups
        # ------------------------------------------------------------------
        _log("\n[4] Running pain point analysis...", log_fh)
        try:
            from src.analyzer.pain_point_extractor import run_extractor
            run_extractor(group=None)
            results["analysis"] = "ok"
        except Exception as exc:
            msg = f"Pain point analysis failed: {exc}"
            _log(f"    ERROR: {msg}", log_fh)
            _append_error_log("analysis", msg)
            results["analysis"] = f"error: {exc}"

        # ------------------------------------------------------------------
        # Summary
        # ------------------------------------------------------------------
        completed_at = _now()
        ok_count = sum(1 for v in results.values() if v == "ok")
        err_count = sum(1 for v in results.values() if str(v).startswith("error"))

        _log(f"\n{'='*50}", log_fh)
        _log(f" Pipeline complete — {completed_at}", log_fh)
        _log(f" Steps OK:     {ok_count}", log_fh)
        _log(f" Steps failed: {err_count}", log_fh)
        if err_count:
            _log(f" See logs/error_log.json for details.", log_fh)
        _log(f"{'='*50}\n", log_fh)

        _append_run_log({
            "started_at": started_at,
            "completed_at": completed_at,
            "steps": results,
            "ok": ok_count,
            "errors": err_count,
        })

    finally:
        if log_fh:
            sys.stdout = sys.__stdout__
            log_fh.close()


if __name__ == "__main__":
    scheduled = "--scheduled" in sys.argv
    run_pipeline(scheduled=scheduled)
