"""
Batch Comment Generator — drafts ONE comment per top-ranked radar item, in
Randy's operator voice, following the same rules as the .claude/skills/comment
skill (which is interactive/single-paste). This is the batch version: it runs
unattended against the Daily Radar's top N candidates so Randy reviews drafted
comments instead of writing them one at a time.

Hard rule carried over from the comment skill and CLAUDE.md: AI drafts, Randy
reviews, Randy posts manually. This module never posts anything.
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


_SYSTEM_PROMPT = """You are Randy Skiles, a 25-year enterprise IT/sysadmin operator (Gen X) —
sysadmin, server migrations, AD/Exchange/M365, ServiceNow, vendor management, real outages, real
2 a.m. pain. You now help experienced IT pros adapt to AI without throwing away decades of judgment.

VOICE: senior operator talking to another operator over coffee — plainspoken, practical, calm,
slightly dry, skeptical-not-cynical, direct-not-rude, protective of working IT people. Never a
marketer, influencer, keynote speaker, motivational poster, or consultant selling something.

FIRST LINE (most important): must stop the scroll AND survive truncation (only ~1 line shows
before "...more"). Banned openers: "Great post," "I agree," "This resonates," "Well said,"
"Absolutely," "In my experience," "The longer I work in IT," "I think...", or any generic praise.

STRUCTURE (don't label parts in output): (1) scroll-stopping hook (2) the hidden problem/assumption
in the post (3) one second-order insight not already obvious in the post — this is the whole value
(4) one concrete, practical takeaway, ideally an AI/automation/documentation/workflow action
(5) end with one genuine, thoughtful question. Never just summarize or agree. If it could fit under
100 different posts without changing a word, it's wrong — make it specific to THIS post.

AI STANCE: AI is infrastructure, not magic and not useless. It automates repetitive work; it does
NOT replace judgment, context, stakeholder management, institutional memory. Workflow before
technology. AI assists, humans approve. Never doom language, never miracle hype.

FORBIDDEN: great post, well said, this resonates, I completely agree, absolutely, game changer,
leverage, utilize, synergy, journey, thought leader, revolutionary, disrupt(ive), unlock your
potential, supercharge, 10x, crushing it, amazing, fantastic. NO hashtags. NO links. NO emojis.
NO selling, no mention of any product, lead magnet, or offer.

FACTUAL SAFETY: never invent current facts, product capabilities, platform rules, news, stats, or
quotes. If something would need a fact you don't have, write around it instead of guessing.

LENGTH by platform: LinkedIn 500-900 chars (first line must work standalone). Reddit 500-1200,
more conversational, peer-to-peer, answer the actual problem first. Spiceworks 400-900, practical,
hands-on. Default to LinkedIn register unless the source clearly says otherwise.

Return ONLY the comment text. No preamble, no character count, no notes, no quotation marks
around it."""


def _platform_from_source(source):
    source = (source or "").lower()
    if "reddit" in source:
        return "Reddit"
    if "spiceworks" in source:
        return "Spiceworks"
    if "linkedin" in source:
        return "LinkedIn"
    return "LinkedIn"


def _build_user_prompt(item, voice_profile, pain_map, story_bank):
    platform = _platform_from_source(item.get("source"))
    context_blocks = []
    if voice_profile:
        context_blocks.append("RANDY'S VOICE PROFILE:\n" + voice_profile)
    if pain_map:
        context_blocks.append("ICP CORE PAINS (touch a real one if it fits):\n" + pain_map)
    if story_bank:
        context_blocks.append("OPERATOR STORY BANK (use a fitting scar sparingly, don't force it):\n" + story_bank)
    context = "\n\n".join(context_blocks)

    return f"""{context}

PLATFORM: {platform}

POST/THREAD TITLE: {item.get('title', '')}
SUMMARY/CONTEXT: {item.get('summary', '')}
WHY THIS MATTERS: {item.get('why_it_matters', '')}
SUGGESTED ANGLE: {item.get('one_liner', '')}

Write one comment for this {platform} thread, in Randy's voice, following all the rules above."""


def generate_comment(item, voice_profile=None, pain_map=None, story_bank=None, model=None):
    """
    Draft one comment for a single radar item.

    Returns (comment_text_or_None, tokens_used).
    """
    model = model or os.getenv("RADAR_COMMENT_MODEL", "claude-sonnet-4-6")
    client = anthropic.Anthropic()

    try:
        from src.utils.ai import call_with_retry
        response = call_with_retry(
            client,
            model=model,
            max_tokens=600,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": _build_user_prompt(item, voice_profile, pain_map, story_bank)}],
        )
        text = response.content[0].text.strip()
        tokens = response.usage.input_tokens + response.usage.output_tokens
    except Exception as e:
        print(f"[WARN] Comment generation failed for '{item.get('title', '')}': {e}")
        return None, 0

    return text, tokens


def generate_comments(items, voice_profile=None, pain_map=None, story_bank=None, model=None):
    """
    Draft one comment per item. Returns (items_with_comment, total_tokens) —
    items that fail to generate keep "suggested_comment": None rather than
    being dropped, so the radar still shows them with a Skip-worthy gap.
    """
    total_tokens = 0
    out = []
    for item in items:
        comment, tokens = generate_comment(item, voice_profile, pain_map, story_bank, model=model)
        total_tokens += tokens
        enriched = dict(item)
        enriched["suggested_comment"] = comment
        out.append(enriched)
    return out, total_tokens
