#!/usr/bin/env python3
"""
health_check.py — Pre-flight validator for the YouTube Transcript Downloader.

Run before every scheduled pipeline execution. Catches broken environments
before they produce silent failures inside an unattended Task Scheduler job.

Usage:
    python health_check.py

Exit codes:
    0 = HEALTHY — all required checks passed
    1 = DEGRADED — one or more required checks failed

Pass/fail notification is handled by the calling .bat file.
"""

import importlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Load .env if python-dotenv is available (graceful fallback if not)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PROJECT_ROOT = Path(__file__).parent
REQUIRED_PYTHON = (3, 10)
MIN_DISK_GB = 2.0

_results = []  # list of (icon, name, detail)


def _ok(name, detail=""):
    _results.append(("[OK]", name, detail))
    print(f"  [OK]   {name}" + (f" -- {detail}" if detail else ""))


def _warn(name, detail=""):
    _results.append(("[!!]", name, detail))
    print(f"  [!!]   {name}" + (f" -- {detail}" if detail else ""))


def _fail(name, detail=""):
    _results.append(("[FAIL]", name, detail))
    print(f"  [FAIL] {name}" + (f" -- {detail}" if detail else ""))


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_python_version():
    v = sys.version_info
    if (v.major, v.minor) >= REQUIRED_PYTHON:
        _ok("Python version", f"{v.major}.{v.minor}.{v.micro}")
    else:
        _fail(
            "Python version",
            f"{v.major}.{v.minor}.{v.micro} — need >= {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}"
        )


def check_packages():
    packages = {
        "youtube_transcript_api": "youtube-transcript-api",
        "requests":               "requests",
        "anthropic":              "anthropic",
        "yt_dlp":                 "yt-dlp",
        "googleapiclient":        "google-api-python-client",
        "slugify":                "python-slugify",
    }
    for module, pip_name in packages.items():
        try:
            importlib.import_module(module)
            _ok(f"Package: {pip_name}")
        except ImportError:
            _fail(f"Package: {pip_name}", "not installed — run: pip install -r requirements.txt")


def check_yt_dlp_cli():
    # Try direct executable first, fall back to python -m yt_dlp (more reliable on Windows)
    for cmd in (["yt-dlp", "--version"], [sys.executable, "-m", "yt_dlp", "--version"]):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                _ok("yt-dlp CLI", result.stdout.strip())
                return
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            _fail("yt-dlp CLI", "timed out after 10s")
            return
    _fail("yt-dlp CLI", "not callable as yt-dlp or python -m yt_dlp")


def check_env_vars():
    required = {
        "ANTHROPIC_API_KEY": ("your_key_here",),
        "YOUTUBE_API_KEY":   ("your_youtube_data_api_v3_key_here", "required_for_stage_2_and_above"),
    }
    optional = {
        "WEBSHARE_PROXY_USERNAME": "proxy fallback disabled — YouTube IP blocks will not be handled",
        "WEBSHARE_PROXY_PASSWORD": "proxy fallback disabled",
    }

    for var, placeholders in required.items():
        val = os.getenv(var, "")
        if val and val not in placeholders:
            _ok(f"Env: {var}", "set")
        else:
            _fail(f"Env: {var}", "missing or still a placeholder in .env")

    all_proxy = all(os.getenv(v) for v in optional)
    if all_proxy:
        _ok("Env: proxy credentials", "WEBSHARE_PROXY_USERNAME + PASSWORD set")
    else:
        _warn("Env: proxy credentials", "not set — YouTube IP blocks will not be handled")


def check_channels_json():
    path = PROJECT_ROOT / "channels.json"
    if not path.exists():
        _fail("channels.json", "file not found — pipeline has nothing to download")
        return
    try:
        with open(path) as f:
            data = json.load(f)
        channels = data.get("channels", [])
        active = [c for c in channels if c.get("active", True)]
        if not active:
            _warn("channels.json", "exists but no channels are marked active")
        else:
            _ok("channels.json", f"{len(active)} active channel(s) defined")
    except json.JSONDecodeError as e:
        _fail("channels.json", f"invalid JSON — {e}")


def check_transcripts_dir():
    path = PROJECT_ROOT / "transcripts"
    if not path.exists():
        # Not a hard fail — orchestrator creates it on first run
        _warn("transcripts/ directory", "does not exist yet — will be created on first run")
        return
    # Write probe confirms the NAS mount is live and writable
    probe = path / ".health_probe"
    try:
        probe.write_text("ok")
        probe.unlink()
        _ok("transcripts/ directory", "reachable and writable")
    except OSError as e:
        _fail("transcripts/ directory", f"not writable — {e} (is the NAS mounted?)")


def check_logs_dir():
    path = PROJECT_ROOT / "logs"
    try:
        path.mkdir(exist_ok=True)
        probe = path / ".health_probe"
        probe.write_text("ok")
        probe.unlink()
        _ok("logs/ directory", "writable")
    except OSError as e:
        _fail("logs/ directory", f"not writable — {e}")


def check_disk_space():
    usage = shutil.disk_usage(PROJECT_ROOT)
    free_gb = usage.free / (1024 ** 3)
    if free_gb >= MIN_DISK_GB:
        _ok("Disk space", f"{free_gb:.1f} GB free")
    else:
        _warn("Disk space", f"only {free_gb:.1f} GB free — threshold is {MIN_DISK_GB} GB")


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _write_log(status):
    log_path = PROJECT_ROOT / "logs" / "health_check_log.json"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "status":    status,
        "checks":    [{"status": s, "name": n, "detail": d} for s, n, d in _results],
    }
    existing = []
    if log_path.exists():
        try:
            with open(log_path) as f:
                existing = json.load(f)
        except Exception:
            existing = []
    existing.append(entry)
    with open(log_path, "w") as f:
        json.dump(existing[-52:], f, indent=2)  # keep last 52 runs (one year weekly)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    print("\n" + "=" * 58)
    print(f"  Health Check — {ts}")
    print("=" * 58 + "\n")

    check_python_version()
    check_packages()
    check_yt_dlp_cli()
    print()
    check_env_vars()
    print()
    check_channels_json()
    check_transcripts_dir()
    check_logs_dir()
    check_disk_space()

    failed  = [r for r in _results if r[0] == "[FAIL]"]
    warned  = [r for r in _results if r[0] == "[!!]"]
    passed  = [r for r in _results if r[0] == "[OK]"]
    status  = "HEALTHY" if not failed else "DEGRADED"

    print("\n" + "=" * 58)
    print(f"  {status} -- {len(passed)} passed | {len(warned)} warnings | {len(failed)} failed")
    print("=" * 58 + "\n")

    _write_log(status)

    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
