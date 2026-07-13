"""
Reads a master timeline.json (from timeline_builder.py) and drafts the overlay
storyboard — the SwarmOps approval-gate artifact Randy reviews and signs off on
before any Remotion rendering happens (per long-form-video-production/SKILL.md
Stage 4: "Get Randy's sign-off on the storyboard before rendering anything.").

This replaces the manual "generate SRT, hand to Claude, Claude reads timestamps
out loud, back-and-forth" round trip — timing comes straight from timeline.json,
no relay needed. What still needs a human/Claude judgment pass: the actual visual
description for each overlay block (left as a TODO placeholder), since that's a
creative call the timeline alone can't make.

Output: <out_dir>/overlays/storyboard.md — same "[start] - [end]: visual
description" format the skill file already uses, just pre-filled with real
timing instead of hand-transcribed timestamps.
"""
from pathlib import Path

from src.utils.atomic import atomic_write_text


def _format_ts(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}:{s:05.2f}"


def build_storyboard(timeline: dict, out_dir: Path) -> Path:
    """
    timeline: the dict returned by timeline_builder.build_timeline()
    Writes <out_dir>/overlays/storyboard.md and returns its path.
    """
    overlays_dir = out_dir / "overlays"
    overlays_dir.mkdir(parents=True, exist_ok=True)
    out_path = overlays_dir / "storyboard.md"

    if out_path.exists():
        print(f"[storyboard] storyboard.md already exists, not overwriting: {out_path.name}")
        return out_path

    lines = [
        "# Overlay Storyboard — DRAFT, needs review before rendering",
        "",
        f"Total duration: {_format_ts(timeline['total_duration_s'])} "
        f"({timeline['total_duration_s']:.1f}s) across {len(timeline['steps'])} steps.",
        "",
        "Timing below comes directly from timeline.json — no manual transcription.",
        "Visual description for each block is a TODO — fill in before rendering, then",
        "get Randy's sign-off per Stage 4 of the long-form-video-production skill.",
        "",
        "---",
        "",
    ]

    for step in timeline["steps"]:
        label = step["label"]
        lines.append(f"## Step {step['index'] + 1}: {label}")
        lines.append("")

        still = step.get("still")
        if still:
            lines.append(
                f"**[{_format_ts(still['start_s'])} - {_format_ts(still['end_s'])}] "
                f"Still frame** (end-of-segment screenshot, holds on-screen text)"
            )
            lines.append("> TODO: visual description / overlay content for this block")
            lines.append("")

        broll = step.get("broll")
        if broll:
            lines.append(
                f"**[{_format_ts(broll['start_s'])} - {_format_ts(broll['end_s'])}] "
                f"B-roll** (sped-up activity footage)"
            )
            lines.append("> TODO: visual description / overlay content for this block")
            lines.append("")

        avatar = step.get("avatar")
        if avatar:
            lines.append(
                f"**[{_format_ts(avatar['start_s'])} - {_format_ts(avatar['end_s'])}] "
                f"Avatar speaking** (audio: {Path(avatar['path']).name})"
            )
            lines.append("")

        lines.append("---")
        lines.append("")

    atomic_write_text(out_path, "\n".join(lines))
    print(f"[storyboard] Draft storyboard written: overlays/{out_path.name}")
    print(f"[storyboard] {len(timeline['steps'])} steps — review and fill in visual "
          f"descriptions before rendering.")
    return out_path
