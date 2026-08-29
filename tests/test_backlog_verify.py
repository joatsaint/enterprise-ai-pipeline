"""
Tests for src/backlog/verify.py — the Verification Engine.

Covers the single most important distinction in the whole system (Decision
Sign-Off item 1): structural failures refuse (integrity_status="fail"),
staleness alone only warns (integrity_status="stale_warning") and still
allows an answer. Also covers AT-18 (referential integrity), AT-23
(unrecognized schema version).
"""
import json
from datetime import datetime, timedelta, timezone

import pytest

from src.backlog import ids, schema, store, verify


@pytest.fixture(autouse=True)
def isolated_backlog_root(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "BACKLOG_ROOT", tmp_path)


PROJECT = "youtube-downloader"


def _bootstrap_with_one_task(priority="high", status="open"):
    store.bootstrap_project(PROJECT)
    tid = ids.allocate_task_id(PROJECT)
    task = schema.new_task_object(
        task_id=tid, title="Test", priority=priority,
        priority_rationale="test", source="unit-test",
    )
    task["status"] = status
    task["confirmed_by_user"] = True
    backlog = store.load_backlog(PROJECT)
    backlog["tasks"].append(task)
    store.save_backlog(PROJECT, backlog)
    return tid


def test_clean_backlog_passes():
    _bootstrap_with_one_task(priority="critical")
    record = verify.run_verification(PROJECT)
    assert record["integrity_status"] == "pass"
    assert record["load_success"] is True
    assert record["open_task_count"] == 1
    assert record["critical_task_count"] == 1
    assert record["failure_reason"] is None


def test_missing_backlog_fails_structurally():
    record = verify.run_verification(PROJECT)
    assert record["integrity_status"] == "fail"
    assert "file not found" in record["failure_reason"]


def test_empty_backlog_is_valid_not_unavailable():
    # Phase 1's core proof: an empty backlog and an unavailable backlog are
    # NOT the same state, and must never be reported as if they were.
    store.bootstrap_project(PROJECT)  # zero tasks, nothing added
    empty_record = verify.run_verification(PROJECT)
    missing_record = verify.run_verification("swarmops-core")  # never bootstrapped

    assert empty_record["integrity_status"] == "pass"
    assert empty_record["load_success"] is True
    assert empty_record["open_task_count"] == 0
    assert empty_record["failure_reason"] is None

    assert missing_record["integrity_status"] == "fail"
    assert missing_record["load_success"] is False
    assert missing_record["failure_reason"] is not None

    # The two must never be confusable by anything downstream reading the record.
    assert empty_record["integrity_status"] != missing_record["integrity_status"]


def test_unknown_project_fails_structurally():
    record = verify.run_verification("not-a-real-project")
    assert record["integrity_status"] == "fail"
    assert "unknown project" in record["failure_reason"]


def test_corrupt_json_fails_structurally():
    _bootstrap_with_one_task()
    store.backlog_path(PROJECT).write_text("{not valid json", encoding="utf-8")
    record = verify.run_verification(PROJECT)
    assert record["integrity_status"] == "fail"
    assert "JSON parse error" in record["failure_reason"]


def test_unrecognized_schema_version_fails_structurally():
    # AT-23
    _bootstrap_with_one_task()
    backlog = store.load_backlog(PROJECT)
    backlog["schema_version"] = "99.9"
    store.save_backlog(PROJECT, backlog)
    record = verify.run_verification(PROJECT)
    assert record["integrity_status"] == "fail"
    assert "unrecognized schema_version" in record["failure_reason"]


def test_duplicate_task_id_fails_structurally():
    _bootstrap_with_one_task()
    backlog = store.load_backlog(PROJECT)
    backlog["tasks"].append(dict(backlog["tasks"][0]))  # exact duplicate id
    store.save_backlog(PROJECT, backlog)
    record = verify.run_verification(PROJECT)
    assert record["integrity_status"] == "fail"
    assert "duplicate task_id" in record["failure_reason"]


def test_dangling_dependency_fails_structurally():
    # AT-18 — the specific test Decision Sign-Off item 4 required.
    _bootstrap_with_one_task()
    backlog = store.load_backlog(PROJECT)
    backlog["tasks"][0]["dependencies"] = ["YTD-9999"]  # does not exist
    store.save_backlog(PROJECT, backlog)
    record = verify.run_verification(PROJECT)
    assert record["integrity_status"] == "fail"
    assert "dangling reference" in record["failure_reason"]


def test_mismatched_project_name_fails_structurally():
    _bootstrap_with_one_task()
    backlog = store.load_backlog(PROJECT)
    backlog["project_name"] = "swarmops-core"
    store.save_backlog(PROJECT, backlog)
    record = verify.run_verification(PROJECT)
    assert record["integrity_status"] == "fail"
    assert "self-declares project_name" in record["failure_reason"]


def test_stale_backlog_warns_but_still_answers():
    # AT-19 — the single most important test in this file: staleness must
    # NOT refuse the way structural failures do.
    _bootstrap_with_one_task(priority="critical")
    backlog = store.load_backlog(PROJECT)
    old_ts = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    backlog["last_updated"] = old_ts
    store.save_backlog(PROJECT, backlog)

    record = verify.run_verification(PROJECT, staleness_days=14)
    assert record["integrity_status"] == "stale_warning"
    assert record["staleness_flag"] is True
    assert record["failure_reason"] is None  # not a failure
    # Real data must still be usable — this is what "still answers" means.
    assert record["open_task_count"] == 1
    assert record["critical_task_count"] == 1


def test_fresh_backlog_has_no_staleness_flag():
    _bootstrap_with_one_task()
    record = verify.run_verification(PROJECT, staleness_days=14)
    assert record["staleness_flag"] is False
    assert record["integrity_status"] == "pass"


def test_orphaned_tmp_file_detected_but_non_blocking():
    _bootstrap_with_one_task()
    orphan = store.project_dir(PROJECT) / ".tmp_leftover.swap"
    orphan.write_text("partial write", encoding="utf-8")

    record = verify.run_verification(PROJECT)
    assert record["integrity_status"] == "pass"  # non-blocking
    assert record["orphaned_tmp_files"] == [".tmp_leftover.swap"]
    assert ".tmp_leftover.swap" in verify.render_verification(record)


def test_render_verification_distinguishes_all_three_states():
    pass_record = verify.run_verification(PROJECT)  # missing file -> fail actually
    # Build one of each explicitly for the render check:
    fail_text = verify.render_verification({
        "integrity_status": "fail", "project_name": PROJECT, "failure_reason": "x",
    })
    stale_text = verify.render_verification({
        "integrity_status": "stale_warning", "project_name": PROJECT,
        "staleness_reason": "x", "open_task_count": 1, "critical_task_count": 0,
    })
    pass_text = verify.render_verification({
        "integrity_status": "pass", "project_name": PROJECT,
        "open_task_count": 1, "critical_task_count": 0, "last_updated_timestamp": "x",
    })
    assert "FAILED" in fail_text and "unavailable" in fail_text
    assert "STALE" in stale_text and "may continue" in stale_text
    assert "PASS" in pass_text
