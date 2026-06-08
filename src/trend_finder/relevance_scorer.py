"""
Relevance Scorer — scores candidate trending topics against Randy's ICP.

ICP: experienced IT/sysadmin professionals (Gen X, ~25 years in the field)
who are worried about AI displacing their careers and want to know how to
use AI to advance rather than be replaced by it.

Single Claude call per batch — takes a list of candidate topics (gathered
from Reddit, RSS, and the existing transcript knowledge base) and returns
them ranked by relevance, each with a one-line "why this fits" rationale.

This module never decides what to post — it only ranks. The orchestrator
hands the top-ranked topic to post_drafter.py for human review.
"""
import json
import os

import anthropic


_ICP_DESCRIPTION = (
    "Experienced IT/sysadmin professionals — Gen X, ~25 years in enterprise IT — "
    "who are worried AI will displace their careers and want straight answers on "
    "how to use AI to advance rather than be replaced by it. They are peers, not "
    "students: skeptical of hype, allergic to corporate-speak, and respond to "
    "real war stories over theory."
)


def _load_env():
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

_load_env()


def score_topics(candidates, model=None):
    """
    Score and rank candidate topics against the ICP.

    Args:
        candidates: list of dicts, each with at least:
            {"title": str, "summary": str, "source": str, "url": str}
        model: Claude model override (defaults to TREND_SCORER_MODEL env or Haiku)

    Returns:
        (ranked, tokens_used)
        ranked: list of dicts — each candidate plus "score" (0.0-1.0 float)
                and "why_it_fits" (one-sentence rationale), sorted by score desc.
        tokens_used: int total input+output tokens consumed (0 on failure)

    Returns ([], 0) if candidates is empty or the API call fails.
    """
    if not candidates:
        return [], 0

    model = model or os.getenv("TREND_SCORER_MODEL", "claude-haiku-4-5-20251001")
    client = anthropic.Anthropic()

    content = f"""You are scoring candidate content topics for relevance to a specific audience.

AUDIENCE (ICP):
{_ICP_DESCRIPTION}

For each candidate topic below, assign a relevance score from 0.0 (irrelevant)
to 1.0 (perfect fit) and a one-sentence reason why it does or doesn't fit.
A high score means: this audience would stop scrolling, feel seen, and want
to discuss it. Topics about generic tech news, consumer gadgets, or anything
unrelated to IT careers / enterprise AI adoption / job security should score low.

Return ONLY the top 10 highest-scoring candidates (fewer is fine if fewer
are genuinely relevant) as valid JSON with exactly this structure, sorted
by score highest first:
{{
  "ranked": [
    {{"index": 0, "score": 0.92, "why_it_fits": "one sentence reason"}},
    {{"index": 2, "score": 0.61, "why_it_fits": "one sentence reason"}}
  ]
}}

CANDIDATES:
{json.dumps([{"index": i, "title": c.get("title", ""), "summary": c.get("summary", "")} for i, c in enumerate(candidates)], indent=2)}"""

    try:
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            system="You are an audience-relevance analyst. Score topics for fit. Return ONLY valid JSON. No prose.",
            messages=[{"role": "user", "content": content}],
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        parsed = json.loads(text)
        tokens = response.usage.input_tokens + response.usage.output_tokens
    except Exception as e:
        print(f"[WARN] Relevance scoring failed: {e}")
        return [], 0

    ranked = []
    for entry in parsed.get("ranked", []):
        idx = entry.get("index")
        if idx is None or idx < 0 or idx >= len(candidates):
            continue
        scored = dict(candidates[idx])
        scored["score"] = float(entry.get("score", 0.0))
        scored["why_it_fits"] = entry.get("why_it_fits", "")
        ranked.append(scored)

    ranked.sort(key=lambda c: c["score"], reverse=True)
    return ranked, tokens
