"""
Project isolation tests (Phase 1, item 5) — FR10.2/FR1.5/AT-16 partially
demonstrated here at the storage/verification layer. Full cross-project
onboarding is still Phase 8; this only proves the isolation guarantee holds
for the two-project structure that already exists.
"""
import pytest

from src.backlog import ids, schema, store, verify


@pytest.fixture(autouse=True)
def isolated_backlog_root(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "BACKLOG_ROOT", tmp_path)


def test_bootstrapping_one_project_does_not_create_the_other():
    store.bootstrap_project("youtube-downloader")
    assert not store.path_exists(store.project_state_path("swarmops-core"))


def test_modifying_one_project_does_not_affect_the_other():
    store.bootstrap_project("youtube-downloader")
    store.bootstrap_project("swarmops-core")

    tid = ids.allocate_task_id("youtube-downloader")
    task = schema.new_task_object(
        task_id=tid, title="YTD-only task", priority="high",
        priority_rationale="test", source="isolation-test",
    )
    task["confirmed_by_user"] = True
    ytd_backlog = store.load_backlog("youtube-downloader")
    ytd_backlog["tasks"].append(task)
    store.save_backlog("youtube-downloader", ytd_backlog)

    swa_backlog = store.load_backlog("swarmops-core")
    assert swa_backlog["tasks"] == []  # completely unaffected

    ytd_record = verify.run_verification("youtube-downloader")
    swa_record = verify.run_verification("swarmops-core")
    assert ytd_record["open_task_count"] == 1
    assert swa_record["open_task_count"] == 0


def test_corrupting_one_project_does_not_fail_the_other():
    store.bootstrap_project("youtube-downloader")
    store.bootstrap_project("swarmops-core")

    store.backlog_path("youtube-downloader").write_text("{not valid json", encoding="utf-8")

    ytd_record = verify.run_verification("youtube-downloader")
    swa_record = verify.run_verification("swarmops-core")
    assert ytd_record["integrity_status"] == "fail"
    assert swa_record["integrity_status"] == "pass"  # unaffected by sibling's corruption


def test_task_ids_are_never_cross_project_ambiguous():
    store.bootstrap_project("youtube-downloader")
    store.bootstrap_project("swarmops-core")
    ytd_id = ids.allocate_task_id("youtube-downloader")
    swa_id = ids.allocate_task_id("swarmops-core")
    assert ytd_id.startswith("YTD-")
    assert swa_id.startswith("SWA-")
    assert ytd_id != swa_id


def test_paths_resolve_to_separate_directories():
    ytd_dir = store.project_dir("youtube-downloader")
    swa_dir = store.project_dir("swarmops-core")
    assert ytd_dir != swa_dir
    assert ytd_dir.name == "youtube-downloader"
    assert swa_dir.name == "swarmops-core"
