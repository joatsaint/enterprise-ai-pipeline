"""
Read/write layer for the Canonical Project Backlog System.

Reuses src/utils/atomic.py directly for every write — no new write mechanism
invented (Architecture Decision, Section 3). Data lives under data/backlog/
<project_name>/, local-only, gitignored (FR9.1/FR9.2) — see .gitignore.

Windows MAX_PATH note, real bug found and fixed during Phase 0.5 live
integration testing (not caught by unit tests, since pytest's tmp_path
fixture never produces paths long enough to trigger it): pathlib's
`.exists()`/`.read_text()`/`.iterdir()` silently fail on Windows once the
resolved path exceeds ~260 characters, EVEN THOUGH `.resolve()` itself
correctly expands 8.3 short names first. The extended-path `\\\\?\\` prefix
fixes this — but it must be applied to every filesystem-touching call, not
just writes. `_lp()` below is the single choke point every function in this
module routes through, specifically so this class of bug can't reappear by
a future function forgetting to apply it individually.
"""
import json
import os
from pathlib import Path

from src.utils.atomic import atomic_write_json
from src.backlog import schema

# BACKLOG_DATA_ROOT env var override exists so Phase 0.5's live integration
# demo (and any future manual CLI use) can point at a sandbox directory
# without ever touching real project data — see
# docs/Canonical Backlog System/PHASE_0.5_RESULTS.md.
_default_root = Path(__file__).resolve().parents[2] / "data" / "backlog"
BACKLOG_ROOT = Path(os.environ["BACKLOG_DATA_ROOT"]) if os.environ.get("BACKLOG_DATA_ROOT") else _default_root


def _lp(path: Path) -> Path:
    """Return a Path safe to call .exists()/.read_text()/.iterdir()/.mkdir()
    on regardless of length, by resolving (which expands 8.3 short names
    like JOATSA~1) and applying the Windows extended-path prefix. The single
    choke point for the MAX_PATH class of bug — every function below routes
    through this rather than touching Path objects directly."""
    resolved = str(path.resolve())
    if os.name == "nt" and not resolved.startswith("\\\\?\\"):
        resolved = "\\\\?\\" + resolved
    return Path(resolved)


def project_dir(project_name: str) -> Path:
    return BACKLOG_ROOT / project_name


def project_state_path(project_name: str) -> Path:
    return project_dir(project_name) / "project_state.json"


def backlog_path(project_name: str) -> Path:
    return project_dir(project_name) / "canonical_backlog.json"


def archive_path(project_name: str) -> Path:
    return project_dir(project_name) / "canonical_backlog_archive.json"


class BacklogLoadError(Exception):
    """Raised when a canonical file is missing, unreadable, or fails to parse.
    Callers (verify.py) catch this and translate it into a structural failure
    report — never swallowed silently (FR6.2)."""


def _load_json_file(path: Path) -> dict:
    safe = _lp(path)
    if not safe.exists():
        raise BacklogLoadError(f"file not found: {path}")
    try:
        text = safe.read_text(encoding="utf-8")
    except OSError as e:
        raise BacklogLoadError(f"file not readable: {path} ({e})") from e
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise BacklogLoadError(f"JSON parse error in {path}: {e}") from e


def load_project_state(project_name: str) -> dict:
    doc = _load_json_file(project_state_path(project_name))
    doc, upgraded = schema.upgrade_document(doc)
    if upgraded:
        save_project_state(project_name, doc)
    return doc


def load_backlog(project_name: str) -> dict:
    doc = _load_json_file(backlog_path(project_name))
    doc, upgraded = schema.upgrade_document(doc)
    if upgraded:
        save_backlog(project_name, doc)
    return doc


def load_archive(project_name: str) -> dict:
    doc = _load_json_file(archive_path(project_name))
    doc, upgraded = schema.upgrade_document(doc)
    if upgraded:
        save_archive(project_name, doc)
    return doc


def save_project_state(project_name: str, state: dict) -> None:
    atomic_write_json(str(_lp(project_state_path(project_name))), state)


def save_backlog(project_name: str, backlog: dict) -> None:
    atomic_write_json(str(_lp(backlog_path(project_name))), backlog)


def save_archive(project_name: str, archive: dict) -> None:
    atomic_write_json(str(_lp(archive_path(project_name))), archive)


def path_exists(path: Path) -> bool:
    """Long-path-safe existence check, exposed for callers outside this
    module (verify.py's orphaned-.tmp-file scan, lock.py) that need the same
    MAX_PATH protection without duplicating _lp()."""
    return _lp(path).exists()


def iter_project_dir(project_name: str):
    """Long-path-safe directory listing."""
    pdir = _lp(project_dir(project_name))
    if not pdir.exists():
        return []
    return list(pdir.iterdir())


def bootstrap_project(project_name: str) -> None:
    """Create empty, correctly-schemed files for a new project (Phase 1).
    Idempotent: does nothing if files already exist — never overwrites real data."""
    if project_name not in schema.PROJECT_PREFIXES:
        raise ValueError(
            f"unknown project {project_name!r} — add it to schema.PROJECT_PREFIXES "
            "first (this is a deliberate guard against silently creating a backlog "
            "for a typo'd or unconfigured project name)"
        )

    _lp(project_dir(project_name)).mkdir(parents=True, exist_ok=True)
    now = schema.utc_now_iso()

    if not path_exists(project_state_path(project_name)):
        save_project_state(project_name, {
            "schema_version": schema.SCHEMA_VERSION,
            "project_name": project_name,
            "current_objective": "",
            "current_sprint_focus": "",
            "active_blockers": [],
            "last_verified": now,
            "backlog_ref": str(backlog_path(project_name)),
        })

    if not path_exists(backlog_path(project_name)):
        save_backlog(project_name, {
            "schema_version": schema.SCHEMA_VERSION,
            "project_name": project_name,
            "last_updated": now,
            "tasks": [],
        })

    if not path_exists(archive_path(project_name)):
        save_archive(project_name, {
            "schema_version": schema.SCHEMA_VERSION,
            "project_name": project_name,
            "last_updated": now,
            "tasks": [],
        })
