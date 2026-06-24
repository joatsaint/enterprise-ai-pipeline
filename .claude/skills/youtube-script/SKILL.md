---
name: youtube-script
description: Convert an article, LinkedIn post, or topic into a slow-paced, high-retention YouTube script for senior IT / infrastructure veterans (the Steel / AI-era sysadmin audience). Use when Randy asks to "make a YouTube script", "turn this article into a video script", "script this for YouTube", "convert to a video", or mentions YouTube scripting / video scripts. Produces a [VISUAL]/[AUDIO] production script using the 6-segment Friction-Hook→Outro structure, in Randy's SPOKEN voice, ending in a one-sentence visible CTA to the Steel lead magnet.
---

# YouTube Script Converter

Turn one source piece (article / LinkedIn post / topic) into a calm, zero-hype,
high-retention YouTube script for senior sysadmins, infra ICs, and technical leads.

## Before you write anything (read these — in order)
1. `content-engine/CONTENT_PUBLISHING_RULES.md` — governs all content work.
2. **`knowledge/me/youtube-voice.md`** — the SPOKEN voice. This is non-negotiable.
3. **`knowledge/me/video-hook-types.md`** — the canonical hook taxonomy for ALL video.
   The Friction Hook (Part 1 below) MUST be built from a named type in this file. Non-negotiable.
4. `knowledge/brand/keyword_research.md` — for the SEO-optimized working title.
5. `knowledge/products/lead-magnets/Steel-One-Sentence Visible CTAs.md` — pick the
   Part-6 outro CTA from this list (link already resolved to the magnet).

## The one rule that makes or breaks the script
**Structure comes from the framework below. VOICE comes from `youtube-voice.md`.**
The biggest failure mode (named in youtube-voice.md) is writing the script out of the
*written* `voice.md` and producing "LinkedIn-Randy reading a teleprompter" — tight,
structured, inhuman. Don't. The 6 segments are the retention skeleton; the spoken lines
inside them must sound like Randy talking in a breakroom — looser, contractions, trails
and circles back, one story/analogy, lands the point. Spoken ≠ written.

## Core structure — 6 operational segments (keep the pacing slow and deliberate)

**Part 1 — The Friction Hook (0:00–0:15).** Open straight into a relatable daily IT/admin
pain. No "welcome back to my channel," no name. Address the friction first. **Build this hook
from a named type in `knowledge/me/video-hook-types.md`** — default to the Pain-Question (Type 1)
or Contrarian Reframe (Type 2); make the viewer feel THEIR version of the pain and start wondering
"could that fix MY problem?" before you name the solution. Draft 2–3 options of different types,
pick the one that sounds most like Randy out loud. (The Contrarian-Reframe move below is one type;
the full menu lives in that file.)

**Part 2 — Contrast & Definition (0:15–0:45).** Define the specific workflow, contrast it
against hype/unsafe practice. Acknowledge real corporate constraints (security policy,
locked-down/air-gapped/local models) so the viewer knows it's built for a real corporate desk.

**Part 3 — Frictionless Step-by-Step (0:45–2:30).** Over-the-shoulder walkthrough, "Step 1,
Step 2…". Build the **data-sanitization boundary explicitly into the steps.**

**Part 4 — Strategic Reframe (2:30–3:15).** The philosophical shift: step back from the
keyboard, see the problem through organizational judgment, not raw task output. Drive the
thesis: **"AI replaces the repetitive administrative tasks; humans approve and apply the
systemic judgment."** (This is the magnet's "AI assists. Humans approve.")

**Part 5 — Anchor / Value-Add (3:15–4:15).** Tell them the exact prompt/tool from the video
is sitting in the description for copy-paste, then bridge to the broader playbook/lead magnet.

**Part 6 — Operational Challenge Outro (4:15–end).** Give one concrete homework task for their
next shift. Close with a **single-sentence CTA from the Steel CTA list, link fully visible**
(`https://rskiles.com/the-riddle-of-steel`). Match the CTA style to the video's angle
(story-led video → #2/#6; pain-led → #8; deliverable-led → #4).

## Delivery mechanics — Cal Hyslop skeleton (technique layer over the 6 segments)
The 6 segments are the retention STRUCTURE; these are the line-level MOVES that make it
land for a skeptical veteran. Modeled from Cal Hyslop (calm 20-yr educator) — borrow the
delivery, **never his AI-tutorial content lane.** Voice still comes from `youtube-voice.md`.
See memory `reference_cal_hyslop_style_fit`.

- **Contrarian reframe on the hook (Part 1).** First two lines: name the exact pain, then
  flip it — *"Most sysadmins think AI's coming for their job. It's coming for the ones who
  can't [X]."* Pairs with the Friction Hook; don't bury the flip.
- **One-line credibility stamp (early, Part 1→2).** Earn the right to teach in a single
  sentence of hard-won experience, not credentials: *"I've spent 25 years keeping production
  alive…"*. Once — not repeated.
- **Promise + contained roadmap (Part 2).** Say what they'll have by the end and bound it
  (*"three things," "in under X minutes"*). Bounded scope lifts completion rate.
- **Define-by-negation before the concept (Part 2/3).** Say what it's NOT first to kill the
  misconception (*"This isn't 'let AI run your change window'…"*), then define it.
- **Jargon → everyday/infra analogy (Parts 3–4) — the #1 context-giver.** Every technical
  beat gets a physical analogy. Randy's own are the edge: the motel command center, the
  load-bearing Jenga dependency, "where's Bob." Lean on these hard — this is *why* it "makes
  sense and gives context."
- **Your own real example, never a hypothetical (throughout).** Ground each point in a
  specific war story — the anti-AI-authenticity signature. No invented scenarios.
- **"Most people miss this" spike (just before Part 3's key step or the Part 4 reframe).** A
  one-line importance jolt to re-grab attention right before the pivotal beat.
- **One do-it-this-shift action (Part 6).** Already the Operational Challenge — keep it to a
  SINGLE concrete step; low activation energy.
- **Optional next-video loop (end).** If it's part of a series, open one question pointing to
  the next video before the CTA.

## Prompt-engineering fallback clause
If the source has context but no concrete, copy-paste prompt or step-by-step:
1. Analyze the core problem in the source.
2. Engineer a detailed, **compliance-safe** prompt template that solves it.
3. Put placeholder variables in `[LIKE THIS]` brackets so the viewer adapts it to their
   approved/local workspace.
4. **Safety filter:** never produce prompts that request or process un-sanitized infra logs,
   live keys, passwords, hostnames, configs, or PII. (Matches the magnet's compliance gate +
   this project's security rules.)

## Formatting / output directives
- Use **[VISUAL]** blocks for what's on screen (terminal share, browser, talking head) and
  **[AUDIO]** blocks for the exact spoken lines.
- Conversational. Contractions. Short, punchy phrases; calm, measured, breakroom voice.
- Strip ALL hype — no exclamation spam, no "revolutionary / game-changing," no clickbait.
- Title: pull a real keyword from `keyword_research.md` (sysadmin / enterprise-ai / ai-proof
  jobs lanes); rank-on-broad-fear, deliver IT-specific.

## Output + review gate (status-change safety)
- Write the draft to `content-engine/pending/<slug>/youtube-script.md` (new or existing slug).
  If the source is an existing pending article, drop it alongside its other pieces.
- A draft is NOT approval. Do not mark anything reviewed/approved/scheduled/published, and do
  not modify `dashboard_state.json`, unless Randy explicitly approves that exact change.

## Output skeleton
```text
# YouTube Script — [SEO working title from keyword_research.md]
_Source: <article/slug> · Voice: youtube-voice.md · Draft for review_

### Part 1 — Friction Hook
- **[VISUAL]:** ...
- **[AUDIO]:** "..."
### Part 2 — Contrast & Definition
...
### Part 6 — Operational Challenge Outro
- **[VISUAL]:** end screen with the resource link
- **[AUDIO]:** "...My challenge for your next shift is ... " + one-sentence CTA from the Steel list
```

## Gotchas

- (none logged yet — append here as real sessions surface edge cases)
