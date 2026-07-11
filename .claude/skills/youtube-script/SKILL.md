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
- **Avatar disclosure, when Phigmund delivers the video (Part 1, right after the hook).**
  **Locked standard template: `knowledge/me/phigmund-avatar-intro.md`.** Use it verbatim
  for paragraphs 4-5 (disclosure + credibility transfer + channel thesis); the hook
  (paragraph 1) may be swapped per video, paragraphs 2-3 (stakes) may be shortened but
  must stay factually the same. Never invent a new "why a clone" reason. See
  `[[reference_mccoy_avatar_intro_pattern]]` for the structural model this is adapted from.
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
- **Fact-check every title against the actual script/description before presenting it.**
  Curiosity-gap title shapes ("The X That Killed Y — I Just Solved It") are only valid
  if the claim inside them is literally true of the story being told. Optimizing for the
  shape without re-reading the content it's titling produces a title that promises the
  wrong story — worse than a boring-but-accurate one. Read the title back against the
  hook/description and ask "is this specific claim actually what happened," not just
  "does this sound clickable."

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

## Hook & Sequencing Addendum (verified July 2026 — Ramonov, McCoy, VidIQ research)

These sharpen the existing structure. Nothing below overrides the 6-segment format above —
it fills in the WHY behind Part 1 and the retention mechanics through Parts 2–4.

### Hook rules (sharpens Part 1)
- Lead with the **result/outcome**, never the topic. "I had 350 files I hadn't touched in
  months" beats "today we're talking about file organization."
- Emotional stakes (fear, job risk, active pain) outperform curiosity-only hooks — people
  act to escape pain; they ignore things they merely like.
- State the **specific real number**. Don't round or soften — specificity is what makes the
  hook credible and stoppable.
- Land the core tension within **10–15 seconds**. Still setting up context at 20 seconds =
  hook is too long.

### 5-beat map (how the G-drive format maps to the 6-segment structure above)
| G-drive beat | Maps to |
|---|---|
| Hook — result-first, emotional stakes | Part 1 — Friction Hook |
| Reframe — why people miss this | Part 2 — Contrast & Definition |
| Stakes / war story — cost of the problem | Part 3 → credibility layer |
| Solution — show it working live | Part 3 — Step-by-Step |
| CTA — one specific next action | Part 6 — Outro |

Part 4 (Strategic Reframe) and Part 5 (Anchor/Value-Add) are Randy-specific additions
that sit inside the "Solution" beat — don't collapse them.

### Retention mechanics through the middle (Parts 2–4)
- **Plant an open loop early** — promise a specific payoff you'll deliver late:
  *"There's something Phigmund says when the AI isn't confident enough to decide —
  I'll show you at the end."* The Zeigarnik effect: withheld payoff measurably increases
  watch time (VidIQ: ~32% increase cited).
- **Mid-video re-hook every 30–45 seconds** — a tonal shift, visual change, or a line
  like *"in the next section I'll show you the part most people get wrong."* Resets
  drifting attention even for viewers who skip ahead.
- Deliver the open loop payoff **in Part 4 or Part 5**, not the outro — the outro is for
  the CTA, not the punchline.

### CTA (confirmed — no change to existing rule)
Neither Ramonov nor McCoy ends on "here's the repo." Funnel: short-form = awareness →
long-form = credibility → **email list = the real goal, every video**. The giveaway
(prompts, template, repo) is the bribe to get the click, not the destination. Randy's
lead magnet funnel already matches this — keep doing it.

### What NOT to do
- Don't open with a generic topic statement ("today we're going to talk about…").
- Don't pitch the tool separately from the tutorial — the tutorial IS the value, with
  the tool embedded naturally, not bolted on as a sales pitch.
- Don't send viewers to a GitHub repo or tool page as the primary CTA.

## Gotchas

- **2026-07-10, File Organizer Build video:** suggested title "The AI Project That Killed
  a University IT Team — I Just Rebuilt It" — but the original project had NO AI
  involvement (it died from a manual-labor/staffing problem, "years before AI was part
  of the conversation" per the hook itself). The title misattributed "AI" to the
  original failure instead of the solution. Caught by Randy, not self-caught, even
  though the correct facts were sitting in the description drafted moments earlier in
  the same file. Root cause: optimized for the curiosity-gap title *shape* without
  re-checking the specific claim against the actual content. See the fact-check rule
  added above.
