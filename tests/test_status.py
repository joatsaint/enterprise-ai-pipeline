"""
Tests for src/status.py — pipeline status summary.

1. summarize_articles rolls up stage counts, piece progress, and overdue items
2. build_report runs against an empty directory without error
"""
from src import status


def _piece(done):
    base = {"written": False, "reviewed": False, "approved": False,
            "scheduled": False, "published": False, "launch_window": False}
    return {k: True for k in base} if done else base


def test_summarize_articles_counts_and_overdue():
    state = {"articles": {
        "a": {"stage": "published", "publish_date": "2026-06-01",
              "pieces": {"p1": _piece(True), "p2": _piece(True)}},
        "b": {"stage": "scheduled", "publish_date": "2026-06-20",
              "pieces": {"p1": _piece(False)}},
        "c": {"stage": "pending", "publish_date": "2026-06-05",   # past + not published -> overdue
              "pieces": {"p1": _piece(True), "p2": _piece(False)}},
        "d": {"stage": "approved", "pieces": {}},
    }}
    s = status.summarize_articles(state, today="2026-06-14")
    assert s["total"] == 4
    assert s["by_stage"] == {"pending": 1, "approved": 1, "scheduled": 1, "published": 1}
    assert s["pieces_done"] == 3      # a:2 + c:1
    assert s["pieces_total"] == 5     # a:2 + b:1 + c:2 + d:0
    assert s["overdue"] == [("c", "2026-06-05")]


def test_summarize_articles_empty():
    s = status.summarize_articles({}, today="2026-06-14")
    assert s["total"] == 0
    assert s["pieces_total"] == 0
    assert s["overdue"] == []


def test_build_report_empty_dir(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    text = "\n".join(status.build_report(today="2026-06-14"))
    assert "Pipeline Status — 2026-06-14" in text
    assert "no dashboard_state.json" in text
