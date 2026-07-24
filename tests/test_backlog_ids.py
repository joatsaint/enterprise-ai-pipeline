"""Tests for src/backlog/ids.py — sequential, unique, never-reused task IDs
(Decision Sign-Off item 3)."""
import pytest

from src.backlog import ids, store


@pytest.fixture(autouse=True)
def isolated_backlog_root(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "BACKLOG_ROOT", tmp_path)


def test_allocate_uses_correct_prefix():
    assert ids.allocate_task_id("youtube-downloader") == "YTD-0001"
    assert ids.allocate_task_id("swarmops-core") == "SWA-0001"


def test_allocate_is_sequential_and_never_reused():
    first = ids.allocate_task_id("youtube-downloader")
    second = ids.allocate_task_id("youtube-downloader")
    third = ids.allocate_task_id("youtube-downloader")
    assert [first, second, third] == ["YTD-0001", "YTD-0002", "YTD-0003"]


def test_allocate_rejects_unknown_project():
    with pytest.raises(ValueError, match="unknown project"):
        ids.allocate_task_id("not-a-real-project")


def test_projects_have_independent_counters():
    ids.allocate_task_id("youtube-downloader")
    ids.allocate_task_id("youtube-downloader")
    assert ids.allocate_task_id("swarmops-core") == "SWA-0001"
