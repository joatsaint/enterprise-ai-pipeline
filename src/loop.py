"""
Unified content loop — one command that runs the owned pipeline through to the
human approval gate, then stops. It never publishes (publishing approved content
stays a separate, deliberate Buffer action).

  python -m src.main loop            # research -> score -> draft -> pending/ (gate)
  python -m src.main loop --dry-run  # research + score only; write nothing

This is the single sequential orchestrator from the pipeline redesign. Stages
(each writes state — nothing lives only in chat memory):

  1. Research + draft   src.trend_finder.orchestrator.run  -> a draft in pending/
  2. Human gate         the draft waits in content-engine/pending/ for review
  3. Status readout     prints the updated review queue so you see what's waiting

QA, multi-format atomize, and publish-approved stages slot in here later — for
now the loop unifies the research→draft→gate cycle behind one command.
"""
from src.trend_finder.orchestrator import run as run_trending
from src.status import build_report


def run_loop(dry_run=False):
    print("=" * 54)
    print(" Content Loop — research -> draft -> review gate")
    print("=" * 54)

    summary = run_trending(dry_run=dry_run)

    status = summary.get("status")
    print()
    print("-" * 54)
    if dry_run:
        print(" Dry run complete — nothing written. (top topic scored above.)")
    elif status == "drafted":
        print(f" ✓ Draft staged for review: {summary.get('output_dir')}")
        print(" → Human gate: review / edit / approve in the dashboard before scheduling.")
        print("   Nothing published — publishing is a separate, approval-gated step.")
    else:
        print(f" No draft produced this run (status: {status}).")
    print("-" * 54)

    # Show the updated pipeline state so the operator sees the review queue.
    print()
    print("\n".join(build_report()))
    return summary
