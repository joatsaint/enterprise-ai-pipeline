---
name: newsletter
description: Draft the weekly LinkedIn newsletter issue — "IT to AI — The Transition Playbook" — in Randy's operator voice, using the curated AI-news digest as raw material. Use when Randy says "draft the newsletter", "write this week's newsletter", "make the newsletter issue", "newsletter from the digest", or it's the weekly Sunday newsletter slot. Produces a standalone Signal-Digest issue (Signal roundup + one Pain Point + optional Prompt + one CTA), 500-700 words, draft for review. NOT a companion to the Tuesday article — it runs independently.
---

# LinkedIn Newsletter — "IT to AI — The Transition Playbook"

Draft the **weekly standalone digest** Randy publishes as a LinkedIn newsletter. This is a
**scan-and-act digest**, NOT a condensed article and NOT a companion piece to the Tuesday article. Its
job: curate what's happening right now and tell the reader exactly what to do about it.

**The merge this skill implements:** the existing `newsletter_curator.py` pipeline mines Randy's inbox
(Gmail/Outlook AI newsletters) into a research digest. THIS skill turns that digest into the published
issue. Curator = input/mining. This skill = the output format. They chain.

**Status-change safety:** a draft is NOT approval. Output is a draft for Randy's review. Never mark it
scheduled/published, never modify `dashboard_state.json`.

## Before drafting (read these — in order)
1. `content-engine/CONTENT_PUBLISHING_RULES.md` — governs all content work.
2. **The latest curator digest** — newest file in `content-engine/newsletter_curation/YYYY-MM-DD_digest.md`.
   This is the raw material for "The Signal." If none exists or it's stale, tell Randy to run
   `python -m src.main curate-newsletters` first.
3. **`knowledge/me/icp_pain_map.md`** — the Core Pains. The Pain Point section pulls ONE from here.
   (The original spec referenced a `PILLARS.md` that does not exist — use `icp_pain_map.md`.)
4. **`knowledge/me/operator-story-bank.md`** — for the operator scar that carries the Pain Point section.
5. **`knowledge/me/voice.md`** — written voice (the newsletter is written, not spoken).

## Format (LOCKED — from LINKEDIN_NEWSLETTER_SPEC.md, references corrected)
Target total length: **500–700 words.** Scan-and-act, not long-form.

**1. Subject line / headline** — one specific line. NOT "This Week in AI." Pull the sharpest item from
the Signal into the headline itself.

**2. Open (40–60 words)** — one or two sentences, peer voice, no windup. Frame why *this particular*
set of items matters this week.

**3. The Signal (3–4 items, ~60–90 words each)** — the curated roundup, sourced from the curator digest
(news, a YouTube video, a vendor move, a regulatory shift — whatever's actually current and relevant to
an IT-to-AI transition). For each item:
- **What happened** — one sentence, specific (named company/product/event).
- **Why it matters to you** — 1–2 sentences, operator's-eye view, NOT a press-release summary.
Four sharp items beat seven padded ones. Don't pad to sound comprehensive.

**4. The Pain Point (100–150 words)** — pick ONE Core Pain from `icp_pain_map.md` that ties to this
week's Signal. State it plainly, then give ONE concrete action the reader can take **this week** (not
"stay informed," not "consider exploring"). **Carry a real operator scar here most weeks**
(`operator-story-bank.md`, rotated) — this is the section that makes the digest something people miss,
not just a resource. See "The one thing to watch" below.

**5. This Week's Prompt (OPTIONAL — only when it genuinely fits)** — when a Signal item or the Pain
Point lends itself to "paste this into AI to work through it in your own environment," include it. When
it doesn't fit, SKIP it — a forced prompt undercuts the issue's credibility. Natural funnel to the
Operator's Prompt Pack when relevant. Format when included:
```
THIS WEEK'S PROMPT — paste into Claude/ChatGPT, swap in your own details:

"[Specific prompt tailored to this week's pain point, written so the reader edits in their own
environment / tool names / constraints before running it.]"
```

**6. Close (30–50 words)** — ONE CTA, not several. Newsletters don't take a link reach-penalty, so a
direct link here is fine.

## Voice rules
- Randy Skiles, 25-year operator, peer-to-peer — not a broadcast.
- No corporate words: leverage, utilize, journey, synergy. No hype, no "in today's rapidly evolving
  landscape," no sycophancy.
- **If it wouldn't survive being the top comment on r/sysadmin, cut it.**
- A personal detail or war story is welcome — the digest format shouldn't squeeze Randy out.

## The one thing to watch (most important note)
Pure utility — news + advice with nothing of Randy in it — reads as a well-organized resource, not
something people anticipate. The format people actually look forward to carries a thread of the
writer's specific experience. You don't need a full war story every week, but **don't let this become
four bullets and a tip with zero Randy in it.** That's the line between "useful" and "the thing I look
forward to." The Pain Point section is where that voice lives.

## Cadence
Weekly, **Sunday evening** (decoupled from the Tuesday article on purpose; catches readers planning
their week). Easy to move — a starting assumption, not a constraint.

## Output
Write the draft to `content-engine/newsletter_curation/issues/YYYY-MM-DD_issue.md` (create the folder if
needed). Title the file with the issue's Sunday date. Draft for review — Randy edits, approves, and
publishes manually on LinkedIn.

## Early-stage note (zero subscribers)
You can't A/B for engagement yet (no audience to split). The experiment that matters now: producibility
(can this ship at quality weekly?) and Randy's own bar ("would I, a working IT pro, look forward to
this?"). Build the back-catalog; the engagement test comes once subscribers exist.

## Supersedes
The newsletter block in `content-engine/linkedin_atomizer.py` (the only real file from the spec's
"superseded" list — the other three named files don't exist in this repo). The article-atomization
pipeline (text post, image post, carousel, video script) is UNAFFECTED — only the newsletter piece
changes to this standalone format.

## Gotchas

- (none logged yet — append here as real sessions surface edge cases)
