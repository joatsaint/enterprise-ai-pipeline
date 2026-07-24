"""Tests for src/backlog/schema.py — data model + validation."""
from src.backlog import schema


def test_new_task_object_is_unconfirmed_by_default():
    t = schema.new_task_object(
        task_id="YTD-0001", title="Test task", priority="high",
        priority_rationale="test", source="unit-test",
    )
    assert t["confirmed_by_user"] is False
    assert t["status"] == "open"
    assert schema.validate_task(t) == []


def test_validate_task_catches_missing_fields():
    errors = schema.validate_task({"task_id": "YTD-0001"})
    assert errors
    assert "missing required fields" in errors[0]


def test_validate_task_catches_bad_status_and_priority():
    t = schema.new_task_object(
        task_id="YTD-0001", title="x", priority="high",
        priority_rationale="x", source="x",
    )
    t["status"] = "not_a_real_status"
    t["priority"] = "not_a_real_priority"
    errors = schema.validate_task(t)
    assert any("invalid status" in e for e in errors)
    assert any("invalid priority" in e for e in errors)


def test_validate_backlog_requires_tasks_list():
    errors = schema.validate_backlog({"schema_version": "1.0", "project_name": "x", "last_updated": "x"})
    assert any("missing required fields" in e for e in errors)


def test_is_supported_schema_version():
    assert schema.is_supported_schema_version(schema.SCHEMA_VERSION) is True
    assert schema.is_supported_schema_version("99.9") is False
