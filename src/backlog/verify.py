"""
Verification Engine — the enforced gate in front of every planning answer.

Severity model (Decision Sign-Off, item 1 — the single most important
distinction in this whole system): structural checks are a hard failure with
no answer given; the staleness check is a warning that still allows an
answer, explicitly flagged. These must never be conflated.

Structural checks (any failure -> integrity_status="fail", refuse to answer):
  1. Correct project identified (declared project_name matches expected)
  2. project_state / backlog / archive files exist
  3. Files are readable
  4. Files parse as valid JSON
  5. schema_version present and recognized on every file
  6. Required fields present and correctly typed (schema.validate_*)
  7. task_ids unique across active + archive
  8. Referential integrity — every dependencies/blocks reference resolves

Freshness check (failure -> integrity_status="stale_warning", still answers):
  9. last_updated within the configured staleness threshold

This module never decides *what* to recommend — it only decides whether the
data is trustworthy enough to recommend anything from at all.
"""
from datetime import datetime, timezone

from src.backlog import schema
from src.backlog.store import (
    BacklogLoadError,
    iter_project_dir,
    load_archive,
    load_backlog,
    load_project_state,
)

DEFAULT_STALENESS_DAYS = 14


def _parse_iso(ts: str) -> datetime:
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def run_verification(project_name: str, staleness_days: int = DEFAULT_STALENESS_DAYS) -> dict:
    """Run every check and return a Verification Record dict matching the
    schema in ARCHITECTURE_DESIGN.md Section 4. Never raises — a failure to
    load or parse is captured *as* a failed verification result, not an
    uncaught exception, so callers always get a reportable record (FR6.2)."""

    record = {
        "timestamp": schema.utc_now_iso(),
        "project_name": project_name,
        "backlog_source": None,
        "load_success": False,
        "parse_success": False,
        "required_fields_present": False,
        "unique_ids_verified": False,
        "open_task_count": 0,
        "critical_task_count": 0,
        "last_updated_timestamp": None,
        "staleness_flag": False,
        "staleness_reason": None,
        "orphaned_tmp_files": [],
        "integrity_status": "fail",
        "failure_reason": None,
    }

    # Check 1 — correct project identified, up front. An unknown project name
    # is a structural failure, not a guess at which backlog to load.
    if project_name not in schema.PROJECT_PREFIXES:
        record["failure_reason"] = f"unknown project {project_name!r} — not a configured project"
        return record

    from src.backlog.store import backlog_path
    record["backlog_source"] = str(backlog_path(project_name))

    # Checks 2-4 — exists, readable, parses. load_* raises BacklogLoadError
    # for any of these; caught here and reported, never left uncaught.
    try:
        project_state = load_project_state(project_name)
        backlog = load_backlog(project_name)
        archive = load_archive(project_name)
    except BacklogLoadError as e:
        record["failure_reason"] = str(e)
        return record

    record["load_success"] = True
    record["parse_success"] = True

    # Check 1b — the file's own self-declared project_name must match.
    for label, doc in (("project_state", project_state), ("backlog", backlog), ("archive", archive)):
        if doc.get("project_name") != project_name:
            record["failure_reason"] = (
                f"{label} self-declares project_name={doc.get('project_name')!r}, "
                f"expected {project_name!r} — possible misconfiguration or wrong file pointer"
            )
            return record

    # Check 5 — schema_version present and recognized, every file.
    for label, doc in (("project_state", project_state), ("backlog", backlog), ("archive", archive)):
        version = doc.get("schema_version")
        if version is None or not schema.is_supported_schema_version(version):
            record["failure_reason"] = f"{label}: unrecognized schema_version {version!r}"
            return record

    # Check 6 — required fields present and correctly typed.
    errors = []
    errors.extend(schema.validate_project_state(project_state))
    errors.extend(schema.validate_backlog(backlog))
    errors.extend(schema.validate_archive(archive))
    if errors:
        record["failure_reason"] = "; ".join(errors)
        return record
    record["required_fields_present"] = True

    active_tasks = backlog.get("tasks", [])
    archived_tasks = archive.get("tasks", [])

    # Check 7 — unique task_ids across active + archive.
    all_ids = [t["task_id"] for t in active_tasks] + [t["task_id"] for t in archived_tasks]
    seen = set()
    duplicates = set()
    for tid in all_ids:
        if tid in seen:
            duplicates.add(tid)
        seen.add(tid)
    if duplicates:
        record["failure_reason"] = f"duplicate task_id(s): {sorted(duplicates)}"
        return record
    record["unique_ids_verified"] = True

    # Check 8 — referential integrity (Decision Sign-Off item 4, AT-18).
    # Structural, not soft, per the ruling.
    known_ids = set(all_ids)
    dangling = []
    for t in active_tasks:
        for ref in t.get("dependencies", []) + t.get("blocks", []):
            if ref not in known_ids:
                dangling.append((t["task_id"], ref))
    if dangling:
        record["failure_reason"] = (
            f"dangling reference(s): {dangling} — a task references a dependency/"
            "blocker task_id that does not exist in active or archived tasks"
        )
        return record

    # All structural checks passed.
    record["open_task_count"] = sum(1 for t in active_tasks if t["status"] != "done")
    record["critical_task_count"] = sum(
        1 for t in active_tasks if t["status"] != "done" and t["priority"] == "critical"
    )
    record["last_updated_timestamp"] = backlog.get("last_updated")

    # Check 9 — staleness. A WARNING, never a refusal (Decision Sign-Off item 1).
    if record["last_updated_timestamp"]:
        age_days = (datetime.now(timezone.utc) - _parse_iso(record["last_updated_timestamp"])).days
        if age_days > staleness_days:
            record["staleness_flag"] = True
            record["staleness_reason"] = (
                f"last updated {age_days} days ago, exceeds the {staleness_days}-day threshold"
            )

    # Orphaned .tmp artifacts — Architecture Section 7 / Failure Mode #17 /
    # Phase 0.5 "interrupted write recovery" requirement. The atomic-write
    # pattern guarantees the real file itself is never torn, but a leftover
    # temp file is a real signal a previous write was interrupted and worth
    # surfacing for audit — non-blocking, since the loaded data is already
    # confirmed valid at this point.
    record["orphaned_tmp_files"] = sorted(
        p.name for p in iter_project_dir(project_name) if p.name.startswith(".tmp_")
    )

    record["integrity_status"] = "stale_warning" if record["staleness_flag"] else "pass"
    record["failure_reason"] = None
    return record


def render_verification(record: dict) -> str:
    """Human-readable rendering matching the formats in ARCHITECTURE_DESIGN.md
    Section 6. Kept terse on PASS (avoid alert fatigue, failure mode #19),
    detailed on failure/warning."""
    if record["integrity_status"] == "fail":
        return (
            f"❌ Backlog Verification FAILED — {record['project_name']}\n"
            f"Failure: {record['failure_reason']}\n"
            "Planning/prioritization functions unavailable until resolved.\n"
            "All other work may continue normally."
        )
    if record["integrity_status"] == "stale_warning":
        return (
            f"⚠️ Backlog Verification Warning — {record['project_name']}\n"
            "Status: STALE\n"
            f"Reason: {record['staleness_reason']}\n"
            "Structural checks: all OK — this is a freshness warning, not a load failure.\n"
            f"Open tasks: {record['open_task_count']} | Critical: {record['critical_task_count']}\n"
            "Planning may continue, but recommendations should be treated as possibly outdated."
        )
    text = (
        f"✅ Backlog Verification — {record['project_name']}\n"
        "Loaded / Parsed / Fields / Unique IDs / References / Schema: all OK\n"
        f"Open tasks: {record['open_task_count']} | Critical: {record['critical_task_count']}\n"
        f"Last updated: {record['last_updated_timestamp']}\n"
        "Integrity status: PASS"
    )
    if record.get("orphaned_tmp_files"):
        text += (
            f"\n⚠️ Note: {len(record['orphaned_tmp_files'])} orphaned .tmp file(s) found "
            f"({record['orphaned_tmp_files']}) — signals a previous write may have been "
            "interrupted. The loaded data above is confirmed valid regardless; this is "
            "flagged for audit, not a failure."
        )
    return text
