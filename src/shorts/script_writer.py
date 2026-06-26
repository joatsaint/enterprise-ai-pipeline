"""
Writes a 5-part YouTube Shorts script from a sysadmin pain point.

5-part structure (~160 words total, ~74 sec at 130 wpm):
  1. Hook       ~15 words — grabs attention, names the irony/tension
  2. Problem    ~35 words — the specific pain, named clearly
  3. Insight    ~45 words — "here's what nobody is talking about"
  4. Implication ~45 words — "what it means for you" (actionable)
  5. CTA        ~20 words — one specific action

Also generates a TEXT HOOK (screen overlay, different from spoken hook):
  - Paradox / social-proof-gap / confession pattern
  - Appears in the top third during first 10 seconds
  - Creates separate intrigue — never repeats the spoken hook

Returns: {
    script:    str,              # full spoken script, pure text
    text_hook: str,              # screen-overlay text hook (different from spoken)
    slug:      str,              # url-safe identifier
    sections:  [                 # per-section character offsets into `script`
        {"label": str, "start": int, "end": int, "text": str}
    ]
}
"""
import os
import re
import json
from pathlib import Path

import anthropic

from src.utils.ai import create, record_usage

ROOT = Path(__file__).resolve().parent.parent.parent
VOICE_PATH = ROOT / "knowledge" / "me" / "voice.md"
PAIN_MAP_PATH = ROOT / "knowledge" / "me" / "icp_pain_map.md"

MODEL = os.environ.get("SHORTS_MODEL", "claude-sonnet-4-6")


def _read_optional(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:60].strip("-")


_SYSTEM = """\
You write YouTube Shorts scripts for Randy Skiles, a 25-year enterprise IT veteran
(firewalls, zero trust, hospitals, credit unions, AI governance).
His audience: sysadmins, IT admins, network engineers, helpdesk leads — 10-25 years in.
Their core fear: AI will make their career irrelevant.
His thesis: judgment, context, and institutional knowledge are what AI can't replace.

Voice rules:
- Dry, direct, no hype
- Talks like he's been in the war, not watching it from a distance
- One practical thought at a time
- Never says "in today's digital landscape" or "as IT professionals"
- Contrarian when the crowd is wrong
- Ends on a practical action, not a inspirational close
"""

_USER_TEMPLATE = """\
Write a YouTube Shorts script and screen text hook for this sysadmin pain point:

PAIN POINT: {title}
CONTEXT: {pain_summary}

OUTPUT must be valid JSON (nothing else) with exactly these fields:

{{
  "spoken_hook":   "~15 words. Grabs attention immediately. Names irony or tension. No question mark.",
  "problem":       "~35 words. The specific pain, concrete, named. No corporate speak.",
  "insight":       "~45 words. What nobody is talking about — the real reason this matters. Contrarian ok.",
  "implication":   "~45 words. What it means for the viewer RIGHT NOW. One concrete thing they can do or understand.",
  "cta":           "~20 words. One specific action. Link in bio, save this, comment below — pick one.",
  "text_hook":     "6-10 words MAX. Appears on screen while spoken hook plays. DIFFERENT from spoken hook. Use paradox pattern (e.g., 'The tool keeping you safe is ending your career') or confession ('I was wrong about this for 20 years'). No question mark.",
  "slug":          "3-5 word url-safe slug for this short (e.g., 'ai-job-security-myth')"
}}

Target: ~160 words total spoken. ~74 seconds at natural speaking pace.
Do NOT include section labels, directions, or markdown in the spoken text.
The text_hook creates SEPARATE intrigue from the spoken hook — a viewer reads it while hearing something different.
"""


def write(pain_point: dict) -> dict:
    """
    Generate script + text hook from a pain_point dict.
    Returns the parsed script dict.
    """
    voice = _read_optional(VOICE_PATH)
    pain_map = _read_optional(PAIN_MAP_PATH)

    system = _SYSTEM
    if voice:
        system += f"\n\nRANDY'S VOICE PROFILE:\n{voice[:2000]}"
    if pain_map:
        system += f"\n\nICP PAIN MAP:\n{pain_map[:1500]}"

    user = _USER_TEMPLATE.format(
        title=pain_point["title"],
        pain_summary=pain_point["pain_summary"],
    )

    client = anthropic.Anthropic()
    text, usage = create(
        client,
        task="shorts_script_writer",
        model=MODEL,
        max_tokens=1200,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    # Parse JSON — strip any accidental markdown fences
    clean = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    clean = re.sub(r"```\s*$", "", clean.strip())
    data = json.loads(clean)

    spoken_hook = data["spoken_hook"].strip()
    problem = data["problem"].strip()
    insight = data["insight"].strip()
    implication = data["implication"].strip()
    cta = data["cta"].strip()
    text_hook = data["text_hook"].strip()
    slug = _slugify(data.get("slug", pain_point["title"]))

    # Build full spoken script as a single plain-text string
    script = " ".join([spoken_hook, problem, insight, implication, cta])

    # Build section markers (character offsets into `script`)
    sections = []
    cursor = 0
    for label, text_part in [
        ("hook", spoken_hook),
        ("problem", problem),
        ("insight", insight),
        ("implication", implication),
        ("cta", cta),
    ]:
        # find position in script (with the joining space)
        pos = script.find(text_part, cursor)
        if pos == -1:
            pos = cursor
        end = pos + len(text_part)
        sections.append({"label": label, "start": pos, "end": end, "text": text_part})
        cursor = end + 1

    word_count = len(script.split())
    print(f"[script_writer] {word_count} words → ~{word_count // 130 * 60 + (word_count % 130) * 60 // 130}s")
    print(f"[script_writer] text_hook: {text_hook}")

    return {
        "script": script,
        "text_hook": text_hook,
        "slug": slug,
        "sections": sections,
        "word_count": word_count,
        "tokens": usage,
    }
