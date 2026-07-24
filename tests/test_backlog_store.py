"""Tests for src/backlog/store.py — bootstrap + atomic read/write, isolated
from the real data/backlog/ directory via monkeypatching BACKLOG_ROOT."""
import pytest

from src.backlog import schema, store


@pytest.fixture(autouse=True)
def isolated_backlog_root(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "BACKLOG_ROOT", tmp_path)


def test_bootstrap_rejects_unknown_project():
    with pytest.raises(ValueError, match="unknown project"):
        store.bootstrap_project("not-a-real-project")


def test_bootstrap_creates_valid_empty_files():
    store.bootstrap_project("youtube-downloader")
    state = store.load_project_state("youtube-downloader")
    backlog = store.load_backlog("youtube-downloader")
    archive = store.load_archive("youtube-downloader")

    assert state["project_name"] == "youtube-downloader"
    assert backlog["tasks"] == []
    assert archive["tasks"] == []
    assert state["schema_version"] == schema.SCHEMA_VERSION


def test_bootstrap_is_idempotent_never_overwrites():
    store.bootstrap_project("youtube-downloader")
    backlog = store.load_backlog("youtube-downloader")
    backlog["tasks"].append({"task_id": "YTD-0001"})
    store.save_backlog("youtube-downloader", backlog)

    store.bootstrap_project("youtube-downloader")  # re-run, should not wipe data
    reloaded = store.load_backlog("youtube-downloader")
    assert reloaded["tasks"] == [{"task_id": "YTD-0001"}]


def test_load_missing_file_raises_backlog_load_error():
    with pytest.raises(store.BacklogLoadError, match="file not found"):
        store.load_backlog("youtube-downloader")


def test_load_corrupt_json_raises_backlog_load_error():
    store.bootstrap_project("youtube-downloader")
    store.backlog_path("youtube-downloader").write_text("{not valid json", encoding="utf-8")
    with pytest.raises(store.BacklogLoadError, match="JSON parse error"):
        store.load_backlog("youtube-downloader")
