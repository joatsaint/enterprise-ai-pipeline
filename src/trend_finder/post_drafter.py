"""
Post Drafter — turns the top-ranked trending topic into a ready-to-edit
LinkedIn post draft in Randy's voice, plus a short rationale note explaining
why the topic was chosen.

This module never publishes anything. It produces text for a human review
queue (content-engine/pending/) — the same review→approve→schedule→publish
flow every other piece of content in this project goes through.
"""
import os

import anthropic


def _load_env():
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

_load_env()


def _build_prompt(topic, voice_profile):
    voice_block = f"VOICE AND STYLE:\n{voice_profile}\n\n" if voice_profile else ""

    return f"""{voice_block}You are drafting a LinkedIn post about a trending topic for Randy's audience
of experienced IT/sysadmin professionals navigating the AI shift.

TOPIC: {topic.get('title', '')}
CONTEXT: {topic.get('summary', '')}
WHY THIS FITS THE AUDIENCE: {topic.get('why_it_fits', '')}
SOURCE: {topic.get('source', '')}

Write a complete, ready-to-edit LinkedIn post in Randy's voice — conversational,
peer-to-peer, grounded in real experience, no corporate-speak, no generic AI-voice
platitudes. It should make an experienced IT person stop scrolling and feel seen.

If the post opens with an old-IT-world story or analogy (the VMware-snapshot
bridge pattern, the on-call pager pattern, etc.), and a self-deprecating
"we've all been there" beat fits naturally into that same story, include one.
Done well, it does three things at once: it signals lived experience rather than
borrowed authority (peer, not student — exactly what this audience responds to),
it ties directly into the story's own mechanic rather than landing as a random
aside, and it raises the stakes right before the story's payoff line, so that
line lands with more weight because the reader has just been reminded of the pain
that made the old solution indispensable in the first place. Skip it if it would
feel forced — it only works when it grows out of the story already being told.

Return your response in exactly this format (two sections, plain text, no markdown
headers other than these two labels):

POST:
<the full post text, ready to publish as-is>

RATIONALE:
<2-3 sentences: why this topic, why now, why this audience will care — for
Randy's quick gut-check before he edits and schedules it>"""


def draft_post(topic, voice_profile=None, model=None):
    """
    Draft a LinkedIn post + rationale note for the given topic.

    Args:
        topic: dict with at least {"title", "summary", "source", "why_it_fits"}
               — typically the top-ranked entry from relevance_scorer.score_topics
        voice_profile: contents of knowledge/me/voice.md (or None to skip)
        model: Claude model override (defaults to TREND_DRAFTER_MODEL env or Sonnet)

    Returns:
        (result, tokens_used)
        result: dict {"post_text": str, "rationale": str} or None on failure
        tokens_used: int total input+output tokens consumed (0 on failure)
    """
    if not topic:
        return None, 0

    model = model or os.getenv("TREND_DRAFTER_MODEL", "claude-sonnet-4-6")
    client = anthropic.Anthropic()

    try:
        response = client.messages.create(
            model=model,
            max_tokens=1200,
            system="You are Randy Skiles, drafting a LinkedIn post in your own authentic voice. Follow the requested output format exactly.",
            messages=[{"role": "user", "content": _build_prompt(topic, voice_profile)}],
        )
        text = response.content[0].text.strip()
        tokens = response.usage.input_tokens + response.usage.output_tokens
    except Exception as e:
        print(f"[WARN] Post drafting failed: {e}")
        return None, 0

    post_text, rationale = "", ""
    if "RATIONALE:" in text:
        post_part, rationale_part = text.split("RATIONALE:", 1)
        rationale = rationale_part.strip()
    else:
        post_part = text

    post_text = post_part.replace("POST:", "", 1).strip()

    if not post_text:
        return None, tokens

    return {"post_text": post_text, "rationale": rationale}, tokens
