"""
Capture workflow — Phase 3. New backlog items only (FR2.1-FR2.4); changes to
existing items (FR2.5) are Phase 4, deliberately not touched here.

Detect -> Propose -> User Confirms -> Persist -> Verify -> Receipt

Detection is automatic (the caller — Claude, in conversation — decides a
candidate is worth proposing). Persistence is NEVER automatic: propose_task()
only builds and returns a plain-dict Candidate; nothing is written anywhere
until the caller separately calls confirm_and_persist() with a candidate the
user has explicitly approved (verbatim or edited). Rejection needs no
function at all — a candidate the user doesn't confirm is simply discarded
by the caller, matching FR2.3/AT-9 ("not confirmed -> does not appear in the
backlog") exactly: there is no code path that can write a Task Object without
this function being called on a Candidate the user approved.

Idempotency (Additional Requirement 2, AT-25): every Candidate carries a
deterministic `capture_key` — a hash of (project_name, origin_type,
origin_reference, title). Replaying the same confirmed capture — whether
from a session restart, a crash, session restore, hook replay, or Claude
re-sending the same confirmation — always produces the same capture_key.
confirm_and_persist() checks active + archived tasks for a matching key
BEFORE allocating a new task_id or writing anything; a match returns the
existing task's Receipt (marked already_existed=True) instead of creating a
duplicate. This is a structural guarantee, not a "try to remember if we
already did this" behavioral rule — the check runs against the actual
persisted data every time, so it survives every replay vector listed above.
"""
import hashlib
from typing import Optional

from src.backlog import ids, lock, schema, store, verify


def _capture_key(project_name: str, origin_type: str, origin_reference: str, title: str) -> str:
    raw = f"{project_name}|{origin_type}|{origin_reference}|{title}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def propose_task(
    project_name: str,
    title: str,
    priority: str,
    priority_rationale: str,
    origin_reference: str,
    origin_type: str = "conversation",
    description: str = "",
    due_date: Optional[str] = None,
    dependencies: Optional[list] = None,
    blocks: Optional[list] = None,
    tags: Optional[list] = None,
    notes: str = "",
) -> dict:
    """Build a Candidate for the user to review. Writes nothing. The returned
    dict is plain data — the caller may edit any field before passing it to
    confirm_and_persist(); editing does not require a separate function."""
    if origin_type not in schema.ORIGIN_TYPES:
        raise ValueError(f"origin_type must be one of {sorted(schema.ORIGIN_TYPES)}, got {origin_type!r}")
    if priority not in schema.PRIORITY_VALUES:
        raise ValueError(f"priority must be one of {sorted(schema.PRIORITY_VALUES)}, got {priority!r}")

    return {
        "project_name": project_name,
        "title": title,
        "priority": priority,
        "priority_rationale": priority_rationale,
        "origin_type": origin_type,
        "origin_reference": origin_reference,
        "description": description,
        "due_date": due_date,
        "dependencies": dependencies or [],
        "blocks": blocks or [],
        "tags": tags or [],
        "notes": notes,
        "capture_key": _capture_key(project_name, origin_type, origin_reference, title),
    }


def _find_existing(project_name: str, capture_key: str) -> tuple[Optional[dict], bool]:
    """Return (task, is_archived) for a task matching capture_key, or
    (None, False) if no match. Checks active tasks first, then archive —
    a replayed confirmation must be caught regardless of whether the
    original task has since been completed/archived (Phase 5 territory,
    but the idempotency check must not regress once that exists)."""
    backlog = store.load_backlog(project_name)
    for task in backlog.get("tasks", []):
        if task.get("capture_key") == capture_key:
            return task, False

    archive = store.load_archive(project_name)
    for task in archive.get("tasks", []):
        if task.get("capture_key") == capture_key:
            return task, True

    return None, False


def _receipt(project_name: str, task: Optional[dict], verification_status: str,
             already_existed: bool, failure_reason: Optional[str] = None) -> dict:
    return {
        "project": project_name,
        "task_id": task["task_id"] if task else None,
        "title": task["title"] if task else None,
        "status": task["status"] if task else None,
        "priority": task["priority"] if task else None,
        "timestamp": schema.utc_now_iso(),
        "verification_status": verification_status,
        "already_existed": already_existed,
        "failure_reason": failure_reason,
    }


def confirm_and_persist(project_name: str, candidate: dict) -> dict:
    """The only function in this module that writes anything. Requires a
    Candidate the user has explicitly confirmed (verbatim or edited) — there
    is no automatic-confirmation path, per FR2.3/N6.

    Sequence, matching Additional Requirement 1 exactly:
      idempotency check -> persist -> verify -> receipt.
    A write is never reported successful without a post-write verification
    pass; verification failure is surfaced in the receipt, never swallowed.
    """
    capture_key = candidate.get("capture_key") or _capture_key(
        project_name, candidate["origin_type"], candidate["origin_reference"], candidate["title"]
    )

    # Idempotency check FIRST — before acquiring a lock or allocating an ID.
    # A replayed confirmation must never even attempt a second write.
    existing, is_archived = _find_existing(project_name, capture_key)
    if existing is not None:
        record = verify.run_verification(project_name)
        status = "FAIL" if record["integrity_status"] == "fail" else "PASS"
        return _receipt(project_name, existing, status, already_existed=True,
                         failure_reason=record["failure_reason"] if status == "FAIL" else None)

    # Acquire the write lock — real protection against a concurrent writer,
    # not just a Phase 6 placeholder; lock.py already exists and is safe to
    # use now (Phase 6 is about testing/extending lock behavior itself, not
    # a prerequisite for consuming it).
    try:
        lock.acquire(project_name)
    except (lock.LockHeldError, lock.StaleLockError) as e:
        return _receipt(project_name, None, "FAIL", already_existed=False,
                         failure_reason=f"could not acquire write lock: {e}")

    try:
        task_id = ids.allocate_task_id(project_name)
        task = schema.new_task_object(
            task_id=task_id,
            title=candidate["title"],
            priority=candidate["priority"],
            priority_rationale=candidate["priority_rationale"],
            source=candidate["origin_reference"],
            origin_type=candidate["origin_type"],
            capture_key=capture_key,
            description=candidate.get("description", ""),
            due_date=candidate.get("due_date"),
            dependencies=candidate.get("dependencies"),
            blocks=candidate.get("blocks"),
            tags=candidate.get("tags"),
            notes=candidate.get("notes", ""),
        )
        task["confirmed_by_user"] = True  # explicit confirmation happened to reach this call

        backlog = store.load_backlog(project_name)
        backlog["tasks"].append(task)
        backlog["last_updated"] = schema.utc_now_iso()
        store.save_backlog(project_name, backlog)
    finally:
        lock.release(project_name)

    # Verify — never claim success without it (Additional Requirement 1 + 5).
    record = verify.run_verification(project_name)
    if record["integrity_status"] == "fail":
        # Do not silently continue. The task IS on disk (preserving recovery
        # information per Requirement 5) but is reported as a failure, not a
        # false success — the caller must surface this, not paper over it.
        return _receipt(project_name, task, "FAIL", already_existed=False,
                         failure_reason=record["failure_reason"])

    return _receipt(project_name, task, "PASS", already_existed=False)
