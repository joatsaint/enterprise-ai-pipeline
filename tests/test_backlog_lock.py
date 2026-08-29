"""Tests for src/backlog/lock.py — 30-minute stale threshold, no auto-delete
(Decision Sign-Off item 5, AT-20/AT-21)."""
import json
import time

import pytest

from src.backlog import lock, store


@pytest.fixture(autouse=True)
def isolated_backlog_root(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "BACKLOG_ROOT", tmp_path)


def test_acquire_and_release_roundtrip():
    lock.acquire("youtube-downloader")
    assert lock.check_lock("youtube-downloader")["stale"] is False
    lock.release("youtube-downloader")
    assert lock.check_lock("youtube-downloader") is None


def test_second_acquire_within_threshold_is_refused_not_queued():
    lock.acquire("youtube-downloader")
    with pytest.raises(lock.LockHeldError, match="another process may be writing"):
        lock.acquire("youtube-downloader")


def test_stale_lock_is_reported_not_silently_acquired():
    lock.acquire("youtube-downloader")
    # Backdate the lock past the 30-minute threshold.
    p = lock.lock_path("youtube-downloader")
    data = json.loads(p.read_text(encoding="utf-8"))
    data["acquired_at"] = time.time() - (lock.STALE_THRESHOLD_SECONDS + 60)
    p.write_text(json.dumps(data), encoding="utf-8")

    status = lock.check_lock("youtube-downloader")
    assert status["stale"] is True

    with pytest.raises(lock.StaleLockError, match="stale lock"):
        lock.acquire("youtube-downloader")


def test_force_clear_requires_explicit_confirmation():
    lock.acquire("youtube-downloader")
    with pytest.raises(ValueError, match="requires explicit user_confirmed=True"):
        lock.force_clear("youtube-downloader", user_confirmed=False)
    # Lock must still be present — the refused call did not remove it.
    assert lock.check_lock("youtube-downloader") is not None

    lock.force_clear("youtube-downloader", user_confirmed=True)
    assert lock.check_lock("youtube-downloader") is None


def test_context_manager_releases_on_exit():
    with lock.locked("youtube-downloader"):
        assert lock.check_lock("youtube-downloader") is not None
    assert lock.check_lock("youtube-downloader") is None
