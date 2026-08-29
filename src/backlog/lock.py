"""
Write-lock mechanism for the Canonical Project Backlog System.

Decision Sign-Off (2026-07-23), item 5: 30-minute staleness threshold.
A lock younger than 30 minutes refuses a second writer outright. A lock
older than 30 minutes is reported as stale but is NEVER auto-removed —
automatic lock deletion creates real corruption risk if the original writer
is still genuinely active (e.g. mid-migration). Removal requires an explicit,
separate confirmation call from the caller.

This is the minimum viable protection permitted for the current
single-operator implementation (FR10.5) — a real compare-and-swap version
check is the future multi-agent upgrade path (Architecture Section 9), not
built here.
"""
import json
import os
import time
from pathlib import Path

from src.backlog.store import _lp, project_dir

STALE_THRESHOLD_SECONDS = 30 * 60  # Decision Sign-Off item 5


class LockHeldError(Exception):
    """Raised when a fresh (non-stale) lock already exists — refuse, don't wait/race."""


class StaleLockError(Exception):
    """Raised when a stale lock exists — caller must explicitly confirm removal."""


def lock_path(project_name: str) -> Path:
    return project_dir(project_name) / "canonical_backlog.json.lock"


def _read_lock(path: Path) -> dict | None:
    safe = _lp(path)
    if not safe.exists():
        return None
    try:
        return json.loads(safe.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        # A corrupt lock file is itself treated as stale — safer to report it
        # for explicit confirmation than to trust or silently ignore it.
        return {"acquired_at": 0, "pid": None, "corrupt": True}


def check_lock(project_name: str) -> dict | None:
    """Return None if no lock or lock is safely absent. Otherwise return
    {"stale": bool, "age_seconds": float, "pid": ...} describing it."""
    path = lock_path(project_name)
    data = _read_lock(path)
    if data is None:
        return None
    age = time.time() - data.get("acquired_at", 0)
    return {"stale": age > STALE_THRESHOLD_SECONDS, "age_seconds": age, "pid": data.get("pid")}


def acquire(project_name: str) -> None:
    """Raise LockHeldError if a fresh lock exists; raise StaleLockError if a
    stale one exists (caller must call force_clear explicitly first). Only
    creates the lock file if neither case applies."""
    status = check_lock(project_name)
    if status is not None:
        if status["stale"]:
            raise StaleLockError(
                f"stale lock for {project_name!r}, age={status['age_seconds']:.0f}s "
                f"(threshold={STALE_THRESHOLD_SECONDS}s) — call force_clear() after "
                "explicit user confirmation, do not auto-remove"
            )
        raise LockHeldError(
            f"active lock for {project_name!r}, age={status['age_seconds']:.0f}s — "
            "another process may be writing"
        )

    path = _lp(lock_path(project_name))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"acquired_at": time.time(), "pid": os.getpid()}),
        encoding="utf-8",
    )


def release(project_name: str) -> None:
    path = _lp(lock_path(project_name))
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def force_clear(project_name: str, user_confirmed: bool) -> None:
    """Remove a stale lock. Requires an explicit True from the caller,
    representing the user's confirmation — never called automatically."""
    if not user_confirmed:
        raise ValueError(
            "force_clear requires explicit user_confirmed=True — a stale lock "
            "is never auto-removed (Decision Sign-Off item 5)"
        )
    release(project_name)


class locked:
    """Context manager: with locked(project_name): ... Raises LockHeldError /
    StaleLockError on entry if it can't safely acquire; always releases on exit."""

    def __init__(self, project_name: str):
        self.project_name = project_name

    def __enter__(self):
        acquire(self.project_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        release(self.project_name)
        return False
