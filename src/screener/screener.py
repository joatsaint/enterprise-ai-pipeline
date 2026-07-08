"""
Research Intake Router (RIR) — Local document screener via Ollama.

Accepts a file path, runs llama3.2:3b locally, produces a Research Card
scored against Randy's four active projects. Zero API cost, no rate limits.

Usage:
  python -m src.main screen path/to/doc.md
  python -m src.main screen path/to/doc.md --model llama3.2:3b
  python -m src.main screen path/to/doc.md --escalate-only

Output: knowledge_base/research_cards/YYYY-MM-DD_slug.md
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2:3b"
MAX_CHARS = 24000  # ~6000 words — well within 128K context, keeps response fast
RESEARCH_CARDS_DIR = Path("knowledge_base/research_cards")

SCREENER_PROMPT = """You are a research intake screener for an IT professional named Randy Skiles.
Randy has four active projects. Your job is to read a document and produce a structured Research Card.

RANDY'S FOUR PROJECTS:

1. SYSADMIN AI / LINKEDIN CONTENT
   Gen-X IT professionals (20+ years experience) facing AI disruption fears.
   Topics: career resilience, enterprise AI adoption, sysadmin relevance, AI governance for IT ops.
   Score high if: addresses IT career fears, AI tools for sysadmins, enterprise AI implementation,
   Zero Trust, Active Directory, governance, hiring, credential relevance, burnout recovery.

2. TRANSCRIPT INTELLIGENCE PLATFORM
   A Python pipeline that downloads YouTube transcripts, indexes them, and extracts
   audience pain points to feed a content business. Tools: yt-dlp, Claude API, knowledge base.
   Score high if: improves transcript processing, content extraction, AI research automation,
   knowledge base design, or pipeline architecture.

3. SWARMOPS GOVERNANCE
   A local AI orchestration layer treating AI agents like restricted Junior SysAdmins.
   Scoped access, kill switch, audit log, human approval gate. Runs on Ollama + local models.
   Score high if: AI governance, agentic safety, audit trails, human-in-the-loop design,
   local LLM deployment, orchestration patterns, enterprise AI risk management.

4. FUTURE CONSULTING / SAAS
   Randy's long-term plan to productize his 25-year IT expertise + AI skills.
   Score high if: monetization of IT expertise, SaaS for IT teams, consulting frameworks,
   enterprise AI ROI, pricing strategy, go-to-market for technical products.

SCORING RULES:
- Score each project 0-10. Be honest — most documents will score 3-6 on most projects.
- Reserve 8-10 for documents that are directly actionable for that project RIGHT NOW.
- Score 0-2 for documents with no meaningful connection.

LEARNING VALUE OPTIONS (pick exactly one):
- Ignore: No useful information, Randy's time is better spent elsewhere.
- Review Later: Mildly interesting, not urgent.
- Worth Reading: Genuinely useful, Randy should read within 2 weeks.
- High Priority: Randy should read this before his next work session on the relevant project.

RECOMMENDED ACTION OPTIONS (pick exactly one):
- Archive: File it away, don't act on it.
- Save for Future: Relevant to a future project not yet active.
- Content Research: Use as source material for LinkedIn posts or articles.
- Project Integration: Directly integrate into one of the four active projects.
- Immediate Review: Randy needs to see this today.

CONFIDENCE: Your confidence in this assessment (0-100). Drop below 70 if the document
is technical in a domain you're uncertain about, or if the content is ambiguous.

OUTPUT FORMAT — respond with ONLY this exact structure, no preamble:

## Executive Summary
[3-5 sentences. What is this document? What does it cover? Who wrote it or where is it from?
What are the 2-3 most important things Randy would want to know?]

## Content Opportunities
[List exactly 10 specific content opportunities. Each should be a concrete LinkedIn post,
article angle, or content idea that could come directly from this document. Be specific —
"Post: The 3 reasons enterprise AI fails at the permission layer" not "AI content."]
1.
2.
3.
4.
5.
6.
7.
8.
9.
10.

## Project Fit
| Project | Score | Why |
|---------|-------|-----|
| Sysadmin AI / LinkedIn | X | [one sentence] |
| Transcript Intelligence | X | [one sentence] |
| SwarmOps Governance | X | [one sentence] |
| Future Consulting / SaaS | X | [one sentence] |

## Learning Value
[Ignore / Review Later / Worth Reading / High Priority] — [one sentence rationale]

## Recommended Action
[Archive / Save for Future / Content Research / Project Integration / Immediate Review] — [one sentence rationale]

## Confidence
[0-100]%

## Escalation
[Write "NONE" if all project scores are below 8 AND confidence is 70 or above.
Otherwise write "ESCALATE → Claude: " followed by the reason.]
"""


def _read_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in (".md", ".txt", ".csv", ".rst"):
        return path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".pdf":
        try:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except ImportError:
            print("pdfplumber not installed — reading PDF as raw bytes (may be garbled).")
            return path.read_bytes().decode("utf-8", errors="replace")
    # fallback for unknown types
    return path.read_text(encoding="utf-8", errors="replace")


def _truncate(text: str, max_chars: int = MAX_CHARS) -> tuple[str, bool]:
    if len(text) <= max_chars:
        return text, False
    return text[:max_chars] + "\n\n[Document truncated at screening limit]", True


def _call_ollama(document_text: str, model: str) -> str:
    prompt = (
        f"{SCREENER_PROMPT}\n\n"
        f"---\nDOCUMENT TO SCREEN:\n---\n{document_text}\n---"
    )
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 2048},
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except requests.ConnectionError:
        print("ERROR: Cannot reach Ollama at http://localhost:11434")
        print("       Is the Ollama server running?")
        sys.exit(1)
    except requests.Timeout:
        print("ERROR: Ollama timed out after 120 seconds. Try a smaller document.")
        sys.exit(1)


def _parse_escalation(card_text: str) -> tuple[bool, str]:
    """Parse project scores and confidence from card; compute escalation in Python."""
    reasons = []

    # Extract project fit scores from the markdown table
    for match in re.finditer(r"\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|", card_text):
        project, score_str = match.group(1).strip(), match.group(2)
        if project.lower() == "project":
            continue  # header row
        score = int(score_str)
        if score >= 8:
            reasons.append(f"Project fit ≥ 8: {project} ({score})")

    # Extract confidence
    conf_match = re.search(r"## Confidence\s*\n(\d+)%", card_text)
    if conf_match:
        confidence = int(conf_match.group(1))
        if confidence < 70:
            reasons.append(f"Low confidence ({confidence}%)")

    if reasons:
        return True, "; ".join(reasons)
    return False, ""


def _save_card(source_path: Path, card_text: str, truncated: bool, model: str) -> Path:
    RESEARCH_CARDS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = re.sub(r"[^\w\-]", "_", source_path.stem)[:60]
    out_path = RESEARCH_CARDS_DIR / f"{date_str}_{slug}.md"

    header = (
        f"# Research Card — {source_path.name} — {date_str}\n\n"
        f"**Source:** `{source_path}`  \n"
        f"**Screened by:** {model} (local Ollama)  \n"
        f"**Screened at:** {datetime.now().strftime('%H:%M')}  \n"
    )
    if truncated:
        header += f"**Note:** Document truncated to {MAX_CHARS:,} chars for screening.  \n"
    header += "\n---\n\n"

    out_path.write_text(header + card_text, encoding="utf-8")
    return out_path


def run_screen(file_path: str, model: str = DEFAULT_MODEL, escalate_only: bool = False):
    path = Path(file_path)
    if not path.exists():
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)

    print(f"\n{'━' * 52}")
    print(f" Research Intake Router")
    print(f" File:  {path.name}")
    print(f" Model: {model} (local)")
    print(f"{'━' * 52}")
    print("⚙  Screening document...\n")

    raw = _read_file(path)
    doc, truncated = _truncate(raw)
    if truncated:
        print(f"   (Document truncated to {MAX_CHARS:,} chars)\n")

    card = _call_ollama(doc, model)
    escalate, escalate_reason = _parse_escalation(card)

    # Append computed escalation section so it's always present in the saved card
    escalation_line = (
        f"ESCALATE → Claude: {escalate_reason}" if escalate else "NONE"
    )
    card_with_escalation = card.rstrip() + f"\n\n## Escalation\n{escalation_line}\n"

    if escalate_only and not escalate:
        print("No escalation triggered. Screener says: handle without Claude.")
        print("Use without --escalate-only to see the full Research Card.\n")
        return

    print(card_with_escalation)

    out_path = _save_card(path, card_with_escalation, truncated, model)
    print(f"\n{'━' * 52}")
    print(f" Saved → {out_path}")
    if escalate:
        print(f" ⚠  ESCALATION FLAGGED — {escalate_reason}")
        print("    Pass this card to Claude for final review")
    else:
        print(" ✓  No escalation — Research Card is the final output")
    print(f"{'━' * 52}\n")
