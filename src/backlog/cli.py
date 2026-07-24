"""
Minimum integration surface for Phase 0.5 — Live Integration Validation.

This is deliberately NOT the real Phase 2 hook system (event-based triggers +
Planning Intent Classification). It's the smallest possible callable proof
that the library works end-to-end outside of pytest, invocable the same way
a real hook eventually will invoke it: run a command, get a result, get an
exit code that distinguishes "safe to proceed" from "must refuse."

Exit codes (meaningful to a caller deciding whether to answer a planning
question):
  0 = pass or stale_warning — proceed (with the warning attached if stale)
  1 = fail — refuse, planning/prioritization unavailable

Usage:
  python -m src.backlog.cli verify <project_name>
  python -m src.backlog.cli bootstrap <project_name>
  python -m src.backlog.cli check-intent <project_name>   (prompt text on stdin)

`check-intent` is the real Phase 2 entry point called by the
UserPromptSubmit hook (.claude/hooks/backlog-planning-check.ps1) — see
docs/Canonical Backlog System/PHASE_2_DESIGN.md Section 6. It classifies the
piped-in prompt text (intent.classify), runs verification only when the
classification requires it, and always appends one line to
logs/backlog_hook_runs.jsonl regardless of outcome (Section 3's "how we know
the hook fired" requirement) — the log write happens unconditionally, even
on non_planning, so an absence of log entries is itself diagnostic of the
hook not running at all, not just of nothing needing verification.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.backlog import intent, store, verify

_LOG_PATH = Path(__file__).resolve().parents[2] / "logs" / "backlog_hook_runs.jsonl"


def _log_run(project_name: str, classification: str, verification_ran: bool, outcome: str) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_name": project_name,
        "classification": classification,
        "verification_ran": verification_ran,
        "outcome": outcome,
    }
    try:
        _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        # Logging must never be the thing that breaks the hook's real job.
        pass


def cmd_verify(project_name: str) -> int:
    record = verify.run_verification(project_name)
    print(verify.render_verification(record))
    return 1 if record["integrity_status"] == "fail" else 0


def cmd_bootstrap(project_name: str) -> int:
    store.bootstrap_project(project_name)
    print(f"Bootstrapped {project_name!r} at {store.project_dir(project_name)}")
    return 0


def cmd_check_intent(project_name: str) -> int:
    prompt_text = sys.stdin.read()
    classification = intent.classify(prompt_text)

    if not intent.requires_verification(prompt_text):
        _log_run(project_name, classification, verification_ran=False, outcome="skipped")
        return 0

    record = verify.run_verification(project_name)
    print(verify.render_verification(record))
    _log_run(project_name, classification, verification_ran=True, outcome=record["integrity_status"])
    return 1 if record["integrity_status"] == "fail" else 0


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) < 2:
        print(
            "usage: python -m src.backlog.cli <verify|bootstrap|check-intent> <project_name>",
            file=sys.stderr,
        )
        return 2
    command, project_name = argv[0], argv[1]
    if command == "verify":
        return cmd_verify(project_name)
    if command == "bootstrap":
        return cmd_bootstrap(project_name)
    if command == "check-intent":
        return cmd_check_intent(project_name)
    print(f"unknown command {command!r}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
