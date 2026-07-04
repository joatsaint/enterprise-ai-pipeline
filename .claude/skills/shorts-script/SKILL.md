---
name: shorts-script
description: Convert one article, prompt pack, LinkedIn post, or topic into a batch of teleprompter-ready ~3-minute SHORTS scripts (spoken voice) for Randy to film during his morning hour → CapCut teleprompter → LinkedIn/YouTube Shorts. Use when Randy asks to "make shorts", "turn this into shorts", "script these as shorts", "break this into shorts", "shorts script for X", or mentions his morning shorts / filming reps. Produces clean spoken-word teleprompter files (one per short) + an intro + outro + production notes + a stitch plan so the shorts recombine into one long-form. Spoken sibling of /youtube-script.
---

# Shorts Script Builder

Turn ONE source piece into a **batch of short-form video scripts** Randy films across mornings, then
recombines into a single long-form. The math: **1 article → N shorts (+ intro + outro) → 1 long-form
= N+1 pieces.** See `memory/project_morning_shorts_workflow.md`.

This is the spoken, short-form sibling of `/youtube-script` (long-form). Same voice/hook DNA, different
mechanics: faster, tighter, no [VISUAL]/[AUDIO] blocks in the read text.

## Before you write anything (read these — in order)
1. `content-engine/CONTENT_PUBLISHING_RULES.md` — governs all content work.
2. **`knowledge/me/youtube-voice.md`** — the SPOKEN voice. Non-negotiable.
3. **`knowledge/me/video-hook-types.md`** — the hook taxonomy. Every short's hook MUST be built from a
   named type here. Non-negotiable.
4. `knowledge/me/icp_pain_map.md` — the on-niche gate. Every short maps to ≥1 Core Pain (prefer ★ P1/P3/P4).
5. The source piece itself (article / prompt pack / post).

## THE constraint that makes or breaks a short (read twice)
**The teleprompter file contains ONLY the words Randy says out loud.** No `[VISUAL]`, no production
notes, no brackets he'd read by accident. Shot/card/caption notes go in a SEPARATE production-notes
file. Randy opens one script on his phone, selects all, pastes into CapCut's teleprompter, and films.
If the file has anything he shouldn't read, it's broken.

**Voice comes from `youtube-voice.md`.** The #1 failure is writing tight "LinkedIn-Randy reading a
teleprompter." Shorts are looser than that — breakroom talk, contractions, one breath per line, blank
line = a beat.

---

## The locked format (proven on the Operator's Prompt Pack, 2026-06-21)

### Length & shape
- **~280–320 spoken words ≈ 2:45–3:10.** Randy is "teaching himself to be more concise" — don't bloat.
- **One breath per line. Blank line = a beat/pause.** Written for a scrolling screen, not a page.
- Hook must land in the **first 2–3 seconds**.

### Every short follows the same rhythm (this is what makes them recombine cleanly)
1. **HOOK** — a named type from `video-hook-types.md`, pointed at THIS unit's specific pain. Default
   **Pain-Question (Type 1)**; use **Cost-of-Inaction (Type 3)** or **Contrarian Reframe (Type 2)** when
   they fit better. Built on the 3-part spine: **Stop → Credibility → Payoff**, tuned with Hormozi's
   levers (↑dream outcome, ↑likelihood, ↓time, ↓effort). Make them feel THEIR pain and wonder "could
   that fix MY problem?" before you name the tool.
2. **"Here's the deal."** — the pivot into the substance (or "Here's the thing/problem").
3. **What it produces** — concrete, plain-talk, IT-grounded. Plain advice in the action beats (no
   metaphor when giving instructions — `youtube-voice.md` 2.5).
4. **The judgment-spine landing** — vary the wording, never a catchphrase: *the AI drafts, you approve;
   the prompt removes the blank page, your 25 years removes the mistakes; that part's still your job.*
   Always lands on **stay indispensable, not replaceable** (P1/P4).
5. **Reassuring on-ramp** — *"try it once," "you don't gotta overhaul how you work."* "You're not behind
   — you're early."
6. **Light tag-out** — *"That's [unit] N."* (NOT the full signoff — that lives in the outro).

### Series-level rules (for the recombine)
- **The intro carries shared rules ONCE.** Anything repeated across every unit (e.g. a pack's two
  safety rules, the bio drop) goes in the **intro**, filmed once — NOT restated in all N shorts.
- **Per-short, include only what that unit specifically needs** — e.g. a one-line varied safety nod on
  the risky ones, so each short still stands alone.
- **Each short ends "That's [unit] N"** → a natural chapter seam.
- **Full signoff lives in the outro** (filmed once): *"That's it for now. I'm Randy, your IT guy. And
  I'll talk to you later."* (from `youtube-voice.md` 2.12).
- **Consistent micro-tag** burned in on every short: `[UNIT] N / TOTAL` (e.g. `PROMPT 3 / 8`).

---

## Workflow

### 1. Plan the split
Read the source. Decide the unit of repetition (a prompt, a step, a question, a myth). One unit = one
short. Name the batch slug and the unit label (Prompt / Step / Question / Lesson). Confirm the count.

### 2. Sample-then-batch (DO IT RIGHT — don't skip)
Write **ONE** sample short first and present it to Randy to lock format + voice. Only after he approves
do you batch the rest. (This is how the Operator's Pack was built.) For the sample, draft **2–3 hook
options of different types** and recommend one.

### 3. Batch the rest
Write every remaining short + the intro + the outro, each as its own clean teleprompter file.

### 4. Write the two reference docs
- `_PRODUCTION-NOTES.md` — per-unit: card line 1 (white) / line 2 (amber), caption emphasis words, hook
  type used, ICP pain mapping, style preset. Plus the shared filming reminders.
- `_STITCH-PLAN.md` — the intro → 1..N → outro recombine recipe, why it stitches, standalone-vs-stitched,
  a working long-form title pulled from `knowledge/brand/keyword_research.md`.

### 5. Deliver to Google Drive (teleprompter files only)
Randy films from his phone, so the spoken-script files go to Google Drive via the Drive integration.
Ask which folder (or confirm an existing one); create the intro + N shorts + outro as Google Docs
titled with leading numbers so they sort in film order (`00 INTRO…`, `01 — …`, `09 OUTRO…`). The two
reference docs stay in the repo (edit-bench only, not read on camera). Verify one doc's content after
upload (the API reports `fileSize: 1` for Docs even when populated — read it back to confirm).

---

## Production spec (for `_PRODUCTION-NOTES.md`) — see `memory/project_shorts_card_pipeline.md`
- **9:16 vertical.** Top half = 1080×960 card (`content-engine/generate_short_card.py`); bottom half =
  Randy's talking-head footage. Text baked into the card with Pillow (line 1 white, line 2 amber).
- **Card headline = 3–5 words, 2 lines.** First frame / cover = the card headline.
- **Style preset** from `content-engine/pending/_video/SHORTS_STYLE_PRESETS.md` — default **Enterprise-IT**
  for a consistent series; swap only when a unit wants a different cold open. Style serves the script.
- **Captions required** (most watch on mute): white default, **industrial amber `#E0A21A`** on the
  emphasis word, CRT green only for literal "system OK", incident red on a single alert beat. Charcoal
  pill behind text so it survives the pool/outdoor background.
- **Animate the card as a rigid block** (CapCut entrance/fly-in) — NEVER AI image-to-video; that warps
  the baked-in text. Fal.ai is NOT needed for these.
- Known bug to watch: `generate_carousel_images.py:compile_carousel_pdf()` `KeyError: 'JPEG'` on
  Py3.14 Pillow (carousel path, flagged Session 15) — if card export hits it, `import
  PIL.JpegImagePlugin; Image.init()`.

## Filming reminders (put in the notes, not the script)
- Outdoors / morning / natural pool light is the warm-human layer; the dark relic system stays in the
  graphics (`youtube-voice.md` 7.1). Don't make the footage look like a server room.
- Authenticity > polish — usually take 1; stumbles are fine.
- Human-paced release: 2–3/week, don't dump all N the same day.

## Output location
`content-engine/pending/{slug}/_shorts/` — per `memory/project_content_folder_convention.md` (one folder
per article; `_video/`-adjacent shorts live under the article's folder). Files:
`00_INTRO.md`, `01_*.md` … `0N_*.md`, `0(N+1)_OUTRO.md`, `_PRODUCTION-NOTES.md`, `_STITCH-PLAN.md`.

## Status-change safety (hard rule)
A draft is NOT approval. Do NOT set reviewed/approved/scheduled/published and do NOT modify
`content-engine/dashboard_state.json` unless Randy explicitly approves that exact change. The next step
after this skill is Randy FILMING, not a publish action.

## Per-short teleprompter file skeleton (clean — this is all Randy reads)
```text
[UNIT] N OF TOTAL — THE [NAME]
(teleprompter — read everything below this line)

[HOOK — named type, pointed at this unit's pain, one breath per line]

[beat]

[CREDIBILITY — one real, unbragged line]

Here's the deal.

[what it produces — plain, concrete]

[one-line safety nod IF this unit needs it]

[judgment-spine landing — varied wording]

[reassuring on-ramp]

That's [unit] N.
```

## Quick reference — what this skill produces
1 source → ONE approved sample → batch of N clean teleprompter shorts + intro + outro +
`_PRODUCTION-NOTES.md` + `_STITCH-PLAN.md`, delivered to Google Drive + repo. Drafts only.

## Gotchas

- Google Docs API reports `fileSize: 1` for a freshly uploaded doc even when it's fully
  populated — read the doc back after upload to confirm content, don't trust the size field.
- **HARD RULE — LinkedIn URL:** Randy's correct LinkedIn URL is `https://www.linkedin.com/in/randy-skiles/` (with hyphen). Never use `randyskiles` (no hyphen). Check `memory/reference_randy_profile_links.md` before writing any URL into content.
