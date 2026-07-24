"""Tests for src/backlog/capture.py — Phase 3 capture workflow, isolated from
the real data/backlog/ directory via monkeypatching BACKLOG_ROOT."""
import json

import pytest

from src.backlog import capture, lock, schema, store, verify


@pytest.fixture(autouse=True)
def isolated_backlog_root(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "BACKLOG_ROOT", tmp_path)
    store.bootstrap_project("youtube-downloader")


def _propose(**overrides):
    defaults = dict(
        project_name="youtube-downloader",
        title="Build the thing",
        priority="high",
        priority_rationale="blocks the release",
        origin_reference="session 53bfd19f, message about the thing",
    )
    defaults.update(overrides)
    return capture.propose_task(**defaults)


# --- propose_task: detection/proposal never writes anything (AT-9) ---------

def test_propose_task_writes_nothing():
    _propose()
    backlog = store.load_backlog("youtube-downloader")
    assert backlog["tasks"] == []


def test_propose_task_rejects_invalid_priority():
    with pytest.raises(ValueError, match="priority must be one of"):
        _propose(priority="urgent!!")


def test_propose_task_rejects_invalid_origin_type():
    with pytest.raises(ValueError, match="origin_type must be one of"):
        _propose(origin_type="telepathy")


def test_candidate_is_plain_editable_data():
    candidate = _propose()
    candidate["title"] = "Build the better thing"  # user edit before confirming
    receipt = capture.confirm_and_persist("youtube-downloader", candidate)
    assert receipt["title"] == "Build the better thing"


# --- confirm_and_persist: the full detect->propose->confirm->persist->verify->receipt chain ---

def test_confirm_and_persist_full_chain_and_receipt_shape():
    candidate = _propose()
    receipt = capture.confirm_and_persist("youtube-downloader", candidate)

    assert receipt["project"] == "youtube-downloader"
    assert receipt["task_id"].startswith("YTD-")
    assert receipt["title"] == "Build the thing"
    assert receipt["status"] == "open"
    assert receipt["priority"] == "high"
    assert receipt["timestamp"]
    assert receipt["verification_status"] == "PASS"
    assert receipt["already_existed"] is False
    assert receipt["failure_reason"] is None

    backlog = store.load_backlog("youtube-downloader")
    assert len(backlog["tasks"]) == 1
    task = backlog["tasks"][0]
    assert task["confirmed_by_user"] is True
    assert task["origin_type"] == "conversation"
    assert task["source"] == "session 53bfd19f, message about the thing"
    assert task["capture_key"]


def test_rejection_is_just_not_confirming():
    _propose()  # detected and proposed
    # ... user rejects. No call to confirm_and_persist. Nothing to undo.
    backlog = store.load_backlog("youtube-downloader")
    assert backlog["tasks"] == []


# --- AT-25: idempotent capture ---------------------------------------------

def test_at25_replayed_confirmation_creates_exactly_one_task():
    candidate = _propose()
    receipt1 = capture.confirm_and_persist("youtube-downloader", candidate)

    # Replay: same candidate, confirmed again (simulates restart/crash/
    # session-restore/hook-replay/repeated confirmation — all indistinguishable
    # from capture.py's point of view, since it never trusts in-memory state).
    receipt2 = capture.confirm_and_persist("youtube-downloader", candidate)

    backlog = store.load_backlog("youtube-downloader")
    assert len(backlog["tasks"]) == 1
    assert receipt2["task_id"] == receipt1["task_id"]
    assert receipt2["already_existed"] is True
    assert receipt2["verification_status"] == "PASS"


def test_at25_replay_from_a_freshly_reconstructed_candidate_still_deduplicates():
    # Simulates a crash: the original candidate dict is gone, but the same
    # propose_task() inputs are reconstructed from scratch (e.g. re-derived
    # from the same conversation on session restore).
    receipt1 = capture.confirm_and_persist("youtube-downloader", _propose())
    receipt2 = capture.confirm_and_persist("youtube-downloader", _propose())

    backlog = store.load_backlog("youtube-downloader")
    assert len(backlog["tasks"]) == 1
    assert receipt1["task_id"] == receipt2["task_id"]
    assert receipt2["already_existed"] is True


def test_different_origin_reference_creates_a_distinct_task():
    receipt1 = capture.confirm_and_persist("youtube-downloader", _propose())
    receipt2 = capture.confirm_and_persist(
        "youtube-downloader", _propose(origin_reference="a completely different conversation moment")
    )
    assert receipt1["task_id"] != receipt2["task_id"]
    backlog = store.load_backlog("youtube-downloader")
    assert len(backlog["tasks"]) == 2


# --- Failure handling: lock contention -------------------------------------

def test_lock_held_returns_fail_receipt_not_an_exception():
    lock.acquire("youtube-downloader")  # simulate another writer mid-write
    try:
        receipt = capture.confirm_and_persist("youtube-downloader", _propose())
    finally:
        lock.release("youtube-downloader")

    assert receipt["verification_status"] == "FAIL"
    assert receipt["task_id"] is None
    assert "lock" in receipt["failure_reason"]

    # Never claims success, and nothing was written.
    backlog = store.load_backlog("youtube-downloader")
    assert backlog["tasks"] == []


# --- Failure handling: verification fails after a real write ---------------

def test_verification_failure_after_write_is_reported_not_hidden(monkeypatch):
    # Force run_verification to report a structural failure, simulating some
    # other corruption discovered at the post-write check.
    def fake_verify(project_name, staleness_days=14):
        return {"integrity_status": "fail", "failure_reason": "simulated structural corruption"}

    monkeypatch.setattr(capture.verify, "run_verification", fake_verify)
    candidate = _propose()
    receipt = capture.confirm_and_persist("youtube-downloader", candidate)

    assert receipt["verification_status"] == "FAIL"
    assert receipt["failure_reason"] == "simulated structural corruption"
    # The task itself is still real and on disk (Requirement 5 — preserve
    # recovery information), the receipt just refuses to claim success.
    assert receipt["task_id"] is not None


# --- Schema upgrade transparency (Phase 3 side effect) ---------------------

def test_real_1_0_file_upgrades_transparently_on_load(tmp_path):
    # Simulate a real pre-Phase-3 production file still declaring 1.0.
    old_backlog = {
        "schema_version": "1.0",
        "project_name": "youtube-downloader",
        "last_updated": schema.utc_now_iso(),
        "tasks": [],
    }
    store.save_backlog("youtube-downloader", old_backlog)
    # Bypass upgrade-on-load to write the raw 1.0 doc directly to disk.
    path = store.backlog_path("youtube-downloader")
    path.write_text(json.dumps(old_backlog), encoding="utf-8")

    loaded = store.load_backlog("youtube-downloader")
    assert loaded["schema_version"] == schema.SCHEMA_VERSION

    # Confirm the upgrade was actually persisted, not just returned in-memory.
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk["schema_version"] == schema.SCHEMA_VERSION


def test_verification_still_passes_after_transparent_upgrade():
    path = store.backlog_path("youtube-downloader")
    old_backlog = json.loads(path.read_text(encoding="utf-8"))
    old_backlog["schema_version"] = "1.0"
    path.write_text(json.dumps(old_backlog), encoding="utf-8")

    record = verify.run_verification("youtube-downloader")
    assert record["integrity_status"] == "pass"
