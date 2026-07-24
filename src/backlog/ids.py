"""
Task ID allocation — PROJECTPREFIX-#### format (Decision Sign-Off item 3).

IDs are permanently retired once allocated: a dedicated counter file
(id_counter.json) tracks the next number to hand out, independent of
scanning active/archive contents. This guarantees no reuse even in an edge
case where scanning-based allocation could otherwise collide (e.g. a future
bug that removes a task instead of archiving it) — the counter never moves
backward, only forward.
"""
import json

from src.backlog import schema
from src.backlog.store import project_dir


def _counter_path(project_name: str):
    return project_dir(project_name) / "id_counter.json"


def _read_counter(project_name: str) -> int:
    path = _counter_path(project_name)
    if not path.exists():
        return 0
    try:
        return json.loads(path.read_text(encoding="utf-8"))["next"]
    except (OSError, json.JSONDecodeError, KeyError):
        # Corrupt counter is a structural concern, not silently reset to 0 —
        # caller should treat this the same as any other integrity failure.
        raise ValueError(f"corrupt id counter for {project_name!r} at {path}")


def _write_counter(project_name: str, next_value: int) -> None:
    path = _counter_path(project_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    from src.utils.atomic import atomic_write_json
    atomic_write_json(str(path), {"next": next_value})


def allocate_task_id(project_name: str) -> str:
    """Return the next unique task_id for this project and permanently
    advance the counter — never reused, even if the task is later archived
    or (in principle) removed."""
    if project_name not in schema.PROJECT_PREFIXES:
        raise ValueError(f"unknown project {project_name!r} — not in schema.PROJECT_PREFIXES")
    prefix = schema.PROJECT_PREFIXES[project_name]
    current = _read_counter(project_name)
    next_value = current + 1
    _write_counter(project_name, next_value)
    return f"{prefix}-{next_value:04d}"
