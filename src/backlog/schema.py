"""
Data model for the Canonical Project Backlog System.

Plain dicts, not classes — matches this project's existing JSON-file
conventions (dashboard_state.json, channels.json) rather than introducing a
new object-modeling pattern. Validation functions return a list of error
strings (empty list = valid) so callers can report every problem found in
one pass, not just the first one — important for FR6.2 (report the cause).

Schema version bumps must add an entry to UPGRADE_FUNCTIONS (FR11.2) — never
silently change field meaning under the same version number.
"""
from datetime import datetime, timezone

# Phase 3 bump (2026-07-24): added origin_type + capture_key to the Task
# Object for capture-workflow traceability and idempotent-write detection
# (Randy's Phase 3 Additional Requirements 2-3). Per FR11.2 this is a real,
# explicit migration (see UPGRADE_FUNCTIONS below), never a silent format
# drift under the same version number — real production 1.0 files exist on
# disk (zero tasks, so trivially safe) and are upgraded transparently the
# next time they're loaded (store.py load_* functions).
SCHEMA_VERSION = "1.1"

STATUS_VALUES = {"open", "blocked", "in_progress", "done", "rejected"}
PRIORITY_VALUES = {"critical", "high", "medium", "low"}
FINAL_STATUS_VALUES = {"done", "rejected", "archived_historical"}

# Phase 3 — origin_type values (Additional Requirement 3). "source" continues
# to serve as the origin_reference (a locator string) — kept as one field
# rather than duplicating it under a new name, since it already existed and
# already meant exactly this.
ORIGIN_TYPES = {"conversation", "migration", "manual"}

# FR1.2 / Decision Sign-Off item 3 — confirmed project prefixes.
PROJECT_PREFIXES = {
    "youtube-downloader": "YTD",
    "swarmops-core": "SWA",
    "voice-line": "JAR",
}

TASK_REQUIRED_FIELDS = {
    "task_id", "title", "status", "priority", "created_at", "updated_at",
    "source", "priority_rationale", "priority_overridden_by_user",
    "dependencies", "blocks", "tags", "confirmed_by_user",
    "origin_type", "capture_key",
}

ARCHIVED_TASK_REQUIRED_FIELDS = TASK_REQUIRED_FIELDS | {
    "completion_date", "completion_history", "final_status",
}

PROJECT_STATE_REQUIRED_FIELDS = {
    "schema_version", "project_name", "current_objective",
    "current_sprint_focus", "active_blockers", "last_verified", "backlog_ref",
}

BACKLOG_REQUIRED_FIELDS = {"schema_version", "project_name", "last_updated", "tasks"}

ARCHIVE_REQUIRED_FIELDS = {"schema_version", "project_name", "last_updated", "tasks"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_task_object(
    task_id: str,
    title: str,
    priority: str,
    priority_rationale: str,
    source: str,
    origin_type: str = "conversation",
    capture_key: str | None = None,
    description: str = "",
    due_date: str | None = None,
    dependencies: list | None = None,
    blocks: list | None = None,
    tags: list | None = None,
    notes: str = "",
) -> dict:
    """Construct a valid, unconfirmed (FR2.3) Task Object with sane defaults.

    origin_type/capture_key added Phase 3 (Additional Requirements 2-3):
    capture_key is the deterministic idempotency key (src/backlog/capture.py
    computes it) used to detect a replayed confirmation before ever writing
    a duplicate task; origin_type classifies where the item came from,
    `source` remains the free-text locator (origin_reference)."""
    now = utc_now_iso()
    return {
        "task_id": task_id,
        "title": title,
        "description": description,
        "status": "open",
        "priority": priority,
        "due_date": due_date,
        "created_at": now,
        "updated_at": now,
        "source": source,
        "origin_type": origin_type,
        "capture_key": capture_key,
        "priority_rationale": priority_rationale,
        "priority_overridden_by_user": False,
        "dependencies": dependencies or [],
        "blocks": blocks or [],
        "tags": tags or [],
        "confirmed_by_user": False,  # FR2.3 — set True only on explicit confirmation
        "notes": notes,
    }


def validate_task(task: dict) -> list[str]:
    """Return a list of validation errors for a single Task Object. Empty = valid."""
    errors = []
    if not isinstance(task, dict):
        return [f"task is not an object: {task!r}"]

    missing = TASK_REQUIRED_FIELDS - task.keys()
    if missing:
        errors.append(f"task {task.get('task_id', '?')}: missing required fields {sorted(missing)}")

    if "status" in task and task["status"] not in STATUS_VALUES:
        errors.append(f"task {task.get('task_id', '?')}: invalid status {task['status']!r}")

    if "priority" in task and task["priority"] not in PRIORITY_VALUES:
        errors.append(f"task {task.get('task_id', '?')}: invalid priority {task['priority']!r}")

    for field in ("dependencies", "blocks", "tags"):
        if field in task and not isinstance(task[field], list):
            errors.append(f"task {task.get('task_id', '?')}: {field} must be a list")

    if "confirmed_by_user" in task and not isinstance(task["confirmed_by_user"], bool):
        errors.append(f"task {task.get('task_id', '?')}: confirmed_by_user must be a boolean")

    if "origin_type" in task and task["origin_type"] not in ORIGIN_TYPES:
        errors.append(f"task {task.get('task_id', '?')}: invalid origin_type {task['origin_type']!r}")

    if "capture_key" in task and task["capture_key"] is not None and not isinstance(task["capture_key"], str):
        errors.append(f"task {task.get('task_id', '?')}: capture_key must be a string or null")

    return errors


def validate_archived_task(task: dict) -> list[str]:
    errors = validate_task(task)
    missing = ARCHIVED_TASK_REQUIRED_FIELDS - task.keys()
    if missing:
        errors.append(f"archived task {task.get('task_id', '?')}: missing required fields {sorted(missing)}")
    if task.get("final_status") not in FINAL_STATUS_VALUES:
        errors.append(f"archived task {task.get('task_id', '?')}: invalid final_status {task.get('final_status')!r}")
    return errors


def validate_project_state(state: dict) -> list[str]:
    errors = []
    if not isinstance(state, dict):
        return ["project_state is not an object"]
    missing = PROJECT_STATE_REQUIRED_FIELDS - state.keys()
    if missing:
        errors.append(f"project_state: missing required fields {sorted(missing)}")
    return errors


def validate_backlog(backlog: dict) -> list[str]:
    """Structural validation only (FR5.3a) — referential integrity and
    uniqueness are cross-file checks, done in verify.py, not here."""
    errors = []
    if not isinstance(backlog, dict):
        return ["backlog is not an object"]
    missing = BACKLOG_REQUIRED_FIELDS - backlog.keys()
    if missing:
        errors.append(f"backlog: missing required fields {sorted(missing)}")
    if "tasks" in backlog:
        if not isinstance(backlog["tasks"], list):
            errors.append("backlog: 'tasks' must be a list")
        else:
            for task in backlog["tasks"]:
                errors.extend(validate_task(task))
    return errors


def validate_archive(archive: dict) -> list[str]:
    errors = []
    if not isinstance(archive, dict):
        return ["archive is not an object"]
    missing = ARCHIVE_REQUIRED_FIELDS - archive.keys()
    if missing:
        errors.append(f"archive: missing required fields {sorted(missing)}")
    if "tasks" in archive:
        if not isinstance(archive["tasks"], list):
            errors.append("archive: 'tasks' must be a list")
        else:
            for task in archive["tasks"]:
                errors.extend(validate_archived_task(task))
    return errors


def is_supported_schema_version(version: str) -> bool:
    """FR11.2 — unrecognized version is a structural failure, not best-effort parse."""
    return version == SCHEMA_VERSION


def _upgrade_task_1_0_to_1_1(task: dict) -> dict:
    upgraded = dict(task)
    upgraded.setdefault("origin_type", "conversation")
    upgraded.setdefault("capture_key", None)
    return upgraded


def _upgrade_1_0_to_1_1(doc: dict) -> dict:
    upgraded = dict(doc)
    upgraded["schema_version"] = "1.1"
    if isinstance(upgraded.get("tasks"), list):
        upgraded["tasks"] = [_upgrade_task_1_0_to_1_1(t) for t in upgraded["tasks"]]
    return upgraded


# FR11.2 — real migration functions, keyed by the version being upgraded FROM,
# never a silent format change under the same version number.
UPGRADE_FUNCTIONS = {
    "1.0": _upgrade_1_0_to_1_1,
}


def upgrade_document(doc: dict) -> tuple[dict, bool]:
    """Chain through UPGRADE_FUNCTIONS until the doc reaches SCHEMA_VERSION or
    hits a version with no registered upgrade path (left alone — verify.py's
    is_supported_schema_version check will correctly flag anything that isn't
    SCHEMA_VERSION as a structural failure, AT-23). Returns (doc, was_upgraded)
    so callers (store.py) know whether to persist the upgraded form back."""
    upgraded = False
    version = doc.get("schema_version")
    while version in UPGRADE_FUNCTIONS:
        doc = UPGRADE_FUNCTIONS[version](doc)
        upgraded = True
        version = doc.get("schema_version")
    return doc, upgraded
