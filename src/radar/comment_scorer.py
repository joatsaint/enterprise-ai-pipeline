"""
Comment Opportunity Scorer — scores candidate threads/posts for "is this a
conversation worth Randy joining today," per the Daily Audience Radar v1 spec
(docs/Daily Audience Radar for Commenting/Build Daily Audience Radar v1.txt).

Five dimensions per candidate (1-5 each), one Claude call per batch:
  Audience Fit, Pain Level, Comment Opportunity, Freshness, Sales Risk

Priority Score = Fit + Pain + Opportunity + Freshness - Sales Risk

This module never decides what to post — it only ranks and returns the top N
for comment_generator.py to draft against. Mirrors trend_finder/relevance_scorer.py's
shape (single batched call, JSON-only response) but scores for "comment on this"
instead of "write my own post about this."
"""
import json
import os

import anthropic


_ICP_DESCRIPTION = (
    "Randy Skiles — a 25-year enterprise IT/sysadmin operator (Gen X) writing for "
    "Gen-X sysadmins and infrastructure pros worried AI will displace their careers. "
    "They are peers, not students: skeptical of hype, allergic to corporate-speak, "
    "moved by real war stories over theory."
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


_PROMPT_TEMPLATE = """You are scoring audience-building opportunities for Randy Skiles, a 25-year
enterprise IT operator writing for Gen-X sysadmins worried about AI and career relevance.

AUDIENCE:
%(icp)s

For each candidate thread/post below, score 1-5 on each dimension:
- audience_fit: would Randy's exact ICP be reading this thread?
- pain_level: how much real pain/anxiety/frustration is visible in the post (career, AI, job security, burnout)?
- comment_opportunity: is there an actual opening for an operator-judgment comment, or is the thread already
  fully answered / closed / dead?
- freshness: how recent/active does this look (high = posted recently and still getting replies)?
- sales_risk: how much would commenting here read as self-promotion, off-topic, or out of place (5 = high risk, avoid)?

Then write:
- why_it_matters: one sentence — why this is worth Randy's time today
- one_liner: one sentence describing the actual hook/angle a comment could take (not the comment itself)

Do not sell. Do not suggest links or hashtags. Return ONLY the top %(top_n)s candidates, sorted by
priority score (fit + pain + opportunity + freshness - sales_risk) descending, as valid JSON matching
this shape (one object per ranked candidate):

{"ranked": [{"index": 0, "audience_fit": 5, "pain_level": 4, "comment_opportunity": 5,
"freshness": 4, "sales_risk": 1, "why_it_matters": "...", "one_liner": "..."}]}

CANDIDATES:
%(listing)s"""


def _build_prompt(candidates, top_n):
    listing = json.dumps(
        [{"index": i, "title": c.get("title", ""), "summary": c.get("summary", ""),
          "source": c.get("source", "")} for i, c in enumerate(candidates)],
        indent=2,
    )
    return _PROMPT_TEMPLATE % {"icp": _ICP_DESCRIPTION, "top_n": top_n, "listing": listing}


def score_candidates(candidates, top_n=10, model=None):
    """
    Score candidates on the 5 Daily-Radar dimensions and return the top N.

    Returns:
        (ranked, tokens_used)
        ranked: list of dicts — original candidate fields plus audience_fit,
                 pain_level, comment_opportunity, freshness, sales_risk,
                 priority_score, why_it_matters, one_liner — sorted desc by
                 priority_score.
        tokens_used: int (0 on failure/empty input)
    """
    if not candidates:
        return [], 0

    model = model or os.getenv("RADAR_SCORER_MODEL", "claude-haiku-4-5-20251001")
    client = anthropic.Anthropic()

    prompt = _build_prompt(candidates, top_n)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=3072,
            system="You are an audience-engagement analyst scoring comment opportunities. Return ONLY valid JSON. No prose.",
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        parsed = json.loads(text)
        tokens = response.usage.input_tokens + response.usage.output_tokens
    except Exception as e:
        print(f"[WARN] Comment-opportunity scoring failed: {e}")
        return [], 0

    ranked = []
    for entry in parsed.get("ranked", []):
        idx = entry.get("index")
        if idx is None or idx < 0 or idx >= len(candidates):
            continue
        scored = dict(candidates[idx])
        for key in ("audience_fit", "pain_level", "comment_opportunity", "freshness", "sales_risk"):
            scored[key] = int(entry.get(key, 0))
        scored["priority_score"] = (
            scored["audience_fit"] + scored["pain_level"]
            + scored["comment_opportunity"] + scored["freshness"]
            - scored["sales_risk"]
        )
        scored["why_it_matters"] = entry.get("why_it_matters", "")
        scored["one_liner"] = entry.get("one_liner", "")
        ranked.append(scored)

    ranked.sort(key=lambda c: c["priority_score"], reverse=True)
    return ranked[:top_n], tokens
