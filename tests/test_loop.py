"""
Tests for src/loop.py — unified content loop.

1. A successful draft run prints the human-gate message + the status readout,
   passes dry_run through, and returns the orchestrator summary
2. A dry run prints the dry-run message and writes nothing
3. A no-candidates run reports the status without claiming a draft
"""
from unittest.mock import patch

from src import loop


def test_run_loop_drafted(capsys):
    summary = {"status": "drafted", "output_dir": "content-engine/content/TREND_x",
               "topic": "T", "score": 0.8}
    with patch.object(loop, "run_trending", return_value=summary) as m, \
         patch.object(loop, "build_report", return_value=["STATUS-LINE"]):
        out = loop.run_loop(dry_run=False)
    m.assert_called_once_with(dry_run=False)
    text = capsys.readouterr().out
    assert "Draft staged for review" in text
    assert "approval-gated" in text
    assert "STATUS-LINE" in text
    assert out == summary


def test_run_loop_dry_run(capsys):
    summary = {"status": "dry_run", "topic": "T", "score": 0.8}
    with patch.object(loop, "run_trending", return_value=summary) as m, \
         patch.object(loop, "build_report", return_value=[]):
        loop.run_loop(dry_run=True)
    m.assert_called_once_with(dry_run=True)
    assert "Dry run complete" in capsys.readouterr().out


def test_run_loop_no_candidates(capsys):
    summary = {"status": "no_candidates"}
    with patch.object(loop, "run_trending", return_value=summary), \
         patch.object(loop, "build_report", return_value=[]):
        loop.run_loop(dry_run=False)
    assert "No draft produced" in capsys.readouterr().out
