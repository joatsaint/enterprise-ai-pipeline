#!/usr/bin/env python3
"""
backup_transcripts.py — mirror the transcripts/ research asset to a backup location
(e.g. a NAS) using a NON-DESTRUCTIVE robocopy /E (copy + update, never delete).

transcripts/ is the irreplaceable source of truth (knowledge_base/index.json is
regenerable). This makes a second copy somewhere off this PC.

Destination resolution (first that's set wins):
  1. --dest "Z:\\path\\to\\backup"
  2. BACKUP_DEST in .env / environment

Source defaults to transcripts/ (override with TRANSCRIPT_OUTPUT in .env or --src).

Usage
-----
  python backup_transcripts.py --dest "Z:\\Claude Code Backups\\youtube-transcripts"
  python backup_transcripts.py --dry-run --dest "Z:\\..."   # list what would copy
  python backup_transcripts.py                               # uses BACKUP_DEST from .env
"""
import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent
LOG_FILE = ROOT / "logs" / "backup_log.txt"


def _load_env():
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text("utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main():
    _load_env()
    ap = argparse.ArgumentParser(description="Back up transcripts/ to a NAS/backup path (robocopy /E)")
    ap.add_argument("--dest", default=os.getenv("BACKUP_DEST"),
                    help="Backup destination folder (or set BACKUP_DEST in .env)")
    ap.add_argument("--src", default=os.getenv("TRANSCRIPT_OUTPUT", "transcripts"),
                    help="Source folder (default: transcripts/)")
    ap.add_argument("--dry-run", action="store_true", help="List what would copy; copy nothing")
    args = ap.parse_args()

    if not args.dest:
        sys.exit("[error] No destination. Pass --dest or set BACKUP_DEST in .env")

    src = (ROOT / args.src).resolve()
    if not src.exists():
        sys.exit(f"[error] Source not found: {src}")
    dest = Path(args.dest)

    # Reachability check for the destination root (e.g. is the NAS mounted?)
    dest_root = dest.anchor or str(dest)
    if not os.path.exists(dest_root):
        sys.exit(f"[error] Destination drive/root not reachable: {dest_root} "
                 f"(is the NAS mounted?)")

    print(f"Source: {src}")
    print(f"Dest:   {dest}")
    print(f"Mode:   {'DRY RUN' if args.dry_run else 'COPY/UPDATE (/E, non-destructive)'}")

    # robocopy: /E copy subdirs incl. empty; updates newer/changed; never deletes (no /MIR).
    # /R:2 /W:5 limited retries; /NP no per-file %; /NDL no dir list; /TEE console+log.
    LOG_FILE.parent.mkdir(exist_ok=True)
    cmd = ["robocopy", str(src), str(dest), "/E", "/R:2", "/W:5",
           "/NP", "/NDL", "/TEE", f"/LOG+:{LOG_FILE}"]
    if args.dry_run:
        cmd.append("/L")  # list only

    with open(LOG_FILE, "a", encoding="utf-8") as fh:
        fh.write(f"\n===== backup run {datetime.now():%Y-%m-%d %H:%M:%S} "
                 f"({'dry-run' if args.dry_run else 'live'}) =====\n")

    print("\nRunning robocopy...\n" + "-" * 50)
    result = subprocess.run(cmd)
    rc = result.returncode
    print("-" * 50)

    # robocopy exit codes: 0-7 = success (bit flags); 8+ = at least one failure.
    if rc >= 8:
        print(f"[FAIL] robocopy reported errors (exit {rc}). See {LOG_FILE.name}.")
        sys.exit(rc)
    msg = {0: "no changes — backup already current",
           1: "new files copied",
           2: "extra files/dirs detected (none removed)",
           3: "files copied + extras detected"}.get(rc, f"completed (code {rc})")
    print(f"[OK] Backup {msg}. Log: logs/{LOG_FILE.name}")


if __name__ == "__main__":
    main()
