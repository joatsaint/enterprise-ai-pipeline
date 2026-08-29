import json

import pytest

from src.backlog import cli, store


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "BACKLOG_ROOT", tmp_path)
    monkeypatch.setattr(cli, "_LOG_PATH", tmp_path / "backlog_hook_runs.jsonl")
    store.bootstrap_project("youtube-downloader")
    return tmp_path


def _run_check_intent(monkeypatch, capsys, prompt_text):
    monkeypatch.setattr("sys.stdin", type("S", (), {"read": staticmethod(lambda: prompt_text)})())
    exit_code = cli.cmd_check_intent("youtube-downloader")
    captured = capsys.readouterr()
    return exit_code, captured.out


def test_non_planning_message_skips_verification_no_output(sandbox, monkeypatch, capsys):
    exit_code, out = _run_check_intent(monkeypatch, capsys, "rewrite this paragraph for me")
    assert exit_code == 0
    assert out == ""

    log_lines = cli._LOG_PATH.read_text(encoding="utf-8").strip().splitlines()
    assert len(log_lines) == 1
    entry = json.loads(log_lines[0])
    assert entry["classification"] == "non_planning"
    assert entry["verification_ran"] is False


def test_planning_message_triggers_verification_and_prints_block(sandbox, monkeypatch, capsys):
    exit_code, out = _run_check_intent(monkeypatch, capsys, "what should I work on next?")
    assert exit_code == 0  # empty backlog is a valid pass, not a failure
    assert "Backlog Verification" in out

    entry = json.loads(cli._LOG_PATH.read_text(encoding="utf-8").strip().splitlines()[0])
    assert entry["classification"] == "planning"
    assert entry["verification_ran"] is True
    assert entry["outcome"] == "pass"


def test_uncertain_message_also_triggers_verification(sandbox, monkeypatch, capsys):
    exit_code, out = _run_check_intent(monkeypatch, capsys, "hey, random thought")
    assert exit_code == 0
    assert "Backlog Verification" in out
    entry = json.loads(cli._LOG_PATH.read_text(encoding="utf-8").strip().splitlines()[0])
    assert entry["classification"] == "uncertain"
    assert entry["verification_ran"] is True


def test_every_invocation_logs_even_on_skip(sandbox, monkeypatch, capsys):
    for text in ["translate this", "what's blocking me?", "asdkfj laksjdf"]:
        _run_check_intent(monkeypatch, capsys, text)
    log_lines = cli._LOG_PATH.read_text(encoding="utf-8").strip().splitlines()
    assert len(log_lines) == 3


def test_log_write_failure_never_crashes_the_command(sandbox, monkeypatch, capsys, tmp_path):
    # Point the log at a path that can't be created (parent is a file, not a dir)
    blocker = tmp_path / "not_a_dir"
    blocker.write_text("x")
    monkeypatch.setattr(cli, "_LOG_PATH", blocker / "backlog_hook_runs.jsonl")
    exit_code, out = _run_check_intent(monkeypatch, capsys, "what's next?")
    assert exit_code == 0
    assert "Backlog Verification" in out
