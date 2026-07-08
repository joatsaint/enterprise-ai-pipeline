"""
Project Wrap — turns a completed project milestone into 5 content + client acquisition assets.

For every milestone shipped, generates:
  1. linkedin-article.md    — pain point → story → solution → lesson (800-1200 words)
  2. case-study.md          — problem / solution / outcome / risks / benefits (managers/buyers)
  3. technical-breakdown.md — architecture / decisions / lessons (technical audience)
  4. youtube-topic.md       — title, hook, demo flow, CTA outline
  5. service-offering.md    — what Randy offers, who it's for, what they get

Outputs land in content-engine/pending/{project}-{milestone}/

Usage:
  python -m src.main project-wrap <project> <milestone> [--context path] [--context path]
  python -m src.main project-wrap swarmops "Milestone 2 - AD Triage" \\
      --context "docs/MONTE Project - SwarmOps Core .../MONTE-Project-Instructions from Claude Code.txt"
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

import anthropic

from src.utils.ai import create

PENDING_DIR = Path("content-engine/pending")
MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 2048

RANDY_CONTEXT = """
ABOUT RANDY SKILES:
- 25 years in enterprise IT (sysadmin, infrastructure, IT operations)
- Gen-X IT professional — lived through every major wave: Y2K, virtualisation, cloud, now AI
- Operator mindset: practical, war-story-driven, skeptical of hype, values what actually works
- ICP audience: Gen-X IT professionals (20+ years) facing AI disruption fears
- Voice: peer-to-peer, not guru-to-student. Credibility through lived experience, not credentials.
- Core message: IT professionals are not being replaced — they're being redeployed. The 25-year operator
  who knows what AI is NOT allowed to do is the most valuable hire in the room.
- Lead with operational pain. Never lead with AI. Never lead with tools.
- LinkedIn content rules: one audience (IT pros), one message per piece, war story validates the point.
"""

OUTPUTS = {
    "linkedin-article": {
        "audience": "Gen-X IT professionals on LinkedIn",
        "length": "800–1200 words",
        "structure": "Pain point hook → war story that validates the pain → what I built and why → "
                     "lesson for the reader → CTA (link to GitHub repo)",
        "rules": "Lead with reader pain, not with the tool. The story earns the solution. "
                 "End with one concrete thing the reader can do or think differently about. "
                 "No bullet-point listicles. Narrative flow throughout. Randy's voice.",
    },
    "case-study": {
        "audience": "IT managers, department heads, potential consulting clients",
        "length": "400–600 words",
        "structure": "The Problem (operational pain, not technical) → The Solution (what was built) → "
                     "The Outcome (what changed) → Risks Mitigated → Business Benefits",
        "rules": "Written for a buyer/manager, not a technologist. No code. No jargon. "
                 "Lead with the business problem. Quantify where possible. "
                 "End with a line about what this type of solution could do for their team.",
    },
    "technical-breakdown": {
        "audience": "Technical peers — sysadmins, infrastructure engineers, developers",
        "length": "400–600 words",
        "structure": "What was built (one paragraph) → Architecture decisions and why → "
                     "What I'd do differently → Key lessons for anyone building something similar",
        "rules": "Be specific about tech choices. Acknowledge tradeoffs honestly. "
                 "Write peer-to-peer. This is the kind of thing you'd share in a Slack channel "
                 "or a team retro. No marketing language.",
    },
    "youtube-topic": {
        "audience": "Potential clients and IT professionals on YouTube",
        "length": "200–300 words",
        "structure": "Proposed title (3 options) → Hook (first 15 seconds — what problem are we showing?) → "
                     "Demo flow (what the viewer sees, step by step) → Payoff / results reveal → "
                     "CTA (GitHub, LinkedIn, or lead magnet)",
        "rules": "This is an outline, not a script. The demo should be visual — show the tool running, "
                 "not slides. The hook must name a problem the viewer has RIGHT NOW. "
                 "The payoff is the before/after, not a product pitch.",
    },
    "service-offering": {
        "audience": "Potential consulting clients, hiring managers, IT directors",
        "length": "300–500 words",
        "structure": "Who this is for → The problem I solve → What you get → "
                     "How it works (engagement model) → Why Randy (credibility) → Next step",
        "rules": "Lead with the client's problem. Never 'I help people with AI.' "
                 "Be specific about the operational pain this addresses. "
                 "Placeholder for pricing — write [PRICE TBD]. "
                 "The 'next step' should be a discovery call or GitHub review, not a purchase.",
    },
}


def _read_context_files(paths: list[str]) -> str:
    chunks = []
    for p in paths:
        path = Path(p)
        if not path.exists():
            print(f"   [warn] Context file not found, skipping: {p}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        # Truncate large files
        if len(text) > 8000:
            text = text[:8000] + "\n\n[truncated]"
        chunks.append(f"--- {path.name} ---\n{text}")
    return "\n\n".join(chunks)


def _slug(text: str) -> str:
    return re.sub(r"[^\w\-]", "-", text.lower()).strip("-")[:60]


def _generate_output(client, project: str, milestone: str, context: str,
                     output_key: str, output_spec: dict) -> str:
    spec = output_spec
    system = (
        f"{RANDY_CONTEXT}\n\n"
        f"You are writing content for Randy Skiles about his project: {project}.\n"
        f"Milestone completed: {milestone}.\n\n"
        f"PROJECT CONTEXT:\n{context if context else 'No additional context provided.'}"
    )
    user = (
        f"Write the {output_key.replace('-', ' ').title()} for this project milestone.\n\n"
        f"AUDIENCE: {spec['audience']}\n"
        f"LENGTH: {spec['length']}\n"
        f"STRUCTURE: {spec['structure']}\n"
        f"RULES: {spec['rules']}\n\n"
        f"Write the full piece now. No preamble, no meta-commentary. Start writing."
    )
    text, usage = create(
        client,
        task=f"project-wrap/{output_key}",
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": user}],
        use_cache=False,
    )
    return text


def run_project_wrap(project: str, milestone: str, context_paths: list[str]):
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    context = _read_context_files(context_paths)
    slug = f"{_slug(project)}-{_slug(milestone)}"
    out_dir = PENDING_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")

    print(f"\n{'━' * 56}")
    print(f" Project Wrap — {project}")
    print(f" Milestone: {milestone}")
    print(f" Output: content-engine/pending/{slug}/")
    print(f"{'━' * 56}\n")

    generated = {}
    total_cost = 0.0

    for key, spec in OUTPUTS.items():
        print(f"  Generating {key}...", end=" ", flush=True)
        text = _generate_output(client, project, milestone, context, key, spec)
        generated[key] = text

        out_path = out_dir / f"{key}.md"
        header = (
            f"# {key.replace('-', ' ').title()} — {project} / {milestone}\n\n"
            f"**Generated:** {date_str}  \n"
            f"**Status:** draft — needs Randy review  \n\n---\n\n"
        )
        out_path.write_text(header + text, encoding="utf-8")
        print("done")

    # Write README
    readme = (
        f"# {project} — {milestone}\n\n"
        f"**Generated:** {date_str}  \n"
        f"**Pipeline:** project-wrap  \n\n"
        f"## Contents\n\n"
        f"| File | Purpose | Status |\n"
        f"|------|---------|--------|\n"
        f"| `linkedin-article.md` | LinkedIn long-form article | Draft |\n"
        f"| `case-study.md` | Business case study (managers/buyers) | Draft |\n"
        f"| `technical-breakdown.md` | Technical breakdown (peers) | Draft |\n"
        f"| `youtube-topic.md` | YouTube video outline | Draft |\n"
        f"| `service-offering.md` | Consulting service offering | Draft |\n\n"
        f"## Next Steps\n\n"
        f"1. Review each file — edit voice/facts as needed\n"
        f"2. `linkedin-article.md` → schedule via content pipeline\n"
        f"3. `case-study.md` → publish to rskiles.com as a portfolio piece\n"
        f"4. `youtube-topic.md` → film demo when ready\n"
        f"5. `service-offering.md` → add to website services page\n"
    )
    (out_dir / "_README.md").write_text(readme, encoding="utf-8")

    print(f"\n{'━' * 56}")
    print(f" ✓ 5 assets generated → content-engine/pending/{slug}/")
    print(f"{'━' * 56}\n")
