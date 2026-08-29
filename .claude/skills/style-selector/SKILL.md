---
name: style-selector
description: Decide which optional style/persuasion/ideation skill(s) — if any — should be layered onto a piece of content before drafting it. Called as an early step by every content-production skill (create-next-article, shorts-script, longform-script, youtube-script, linkedin-hook-writer, linkedin-carousel, video-explainer, long-form-video-production, short-walk-and-talk). Not itself a format skill — it recommends which format-agnostic technique(s) to apply, then hands off to the calling skill's own workflow.
---

# Style Selector

A decision step, not a new production pipeline. This project already has two
kinds of skills:

1. **Format/genre skills** — own the actual shape of a specific content type
   (`create-next-article`, `shorts-script`, `youtube-script`,
   `longform-script`, `linkedin-hook-writer`, `linkedin-carousel`,
   `video-explainer`, `long-form-video-production`, `short-walk-and-talk`).
   These are auto-selected by content type already — a Short is
   `shorts-script`, an article is `create-next-article`. This skill does
   NOT choose between these.

2. **Technique/style skills** — optional, format-agnostic layers that can be
   applied on top of whichever format skill is producing the piece. These
   are what this skill helps choose between, and what "toolkit, not a
   formula" already means for each of them individually.

Built 2026-08-10, same session `guide-positioning` was banked — created
specifically because the toolkit had grown past the point where Randy could
reliably remember every option without a menu.

## The catalog

| Skill | Phase | Best-fit signals | Anti-fit signals |
|---|---|---|---|
| `guide-positioning` | Persuasion — hooks/closings/CTAs | Piece needs to move from problem to "why I can help" without a hard sell; a reader objection is easy to name in one sentence; closing section of an article, or a Short's pivot into CTA | Piece is pure information/tutorial with no persuasion beat; objection isn't real/specific enough to voice honestly |
| `infomercial-pitch` | Persuasion — feature pitch | Pitching a real product/lead magnet's actual feature list; teleprompter/walk-and-talk delivery | Build/demo video where the build IS the content; war-story-led piece; anything where "sell me this" energy would clash |
| `lateral` (routes to: `random-stimulus`, `provocation`, `inversion`, `concept-fan`, `analogy`, `scamper`, `six-hats`, `worst-idea`) | Ideation — before/during angle-finding | Stuck on a creative angle, topic/format has been repeated too many times, need a genuinely different direction rather than a new hook template | Angle is already clear and specific (a real war story, a real Reddit thread) — skip straight to the format skill |

**Update this table in the same session any new technique/style skill is
created** — same standing discipline as the Skill Maintenance Gotchas rule
in CLAUDE.md, extended to cover this catalog specifically.

## Workflow

### Step 1 — Identify which phase(s) this piece actually needs

Most pieces need zero or one technique skill, not both phases. Ask:
- Is the angle/topic itself already clear and specific? If yes, skip
  Ideation phase entirely — jump to Step 2 for Persuasion only.
- Does the piece have a real closing/CTA/persuasion beat at all? A pure
  reference or tutorial piece may need neither.

If neither phase applies, say so plainly and hand off to the format skill's
normal workflow — don't force a technique skill onto a piece that doesn't
need one.

### Step 2 — Score the piece against the catalog's fit signals

For each candidate skill, check its best-fit signals against the actual
piece (topic, war story, audience pain point, what section of the piece is
being written). Note anti-fit signals too — a skill that fails its own
anti-fit check should not be recommended even if one fit signal matches.

### Step 3 — Recommend, don't decide

Present the top 1-3 matches (fewer is fine, including zero) with one
sentence of reasoning each — which fit signal triggered it, and why it
suits this specific piece. Combining is allowed and often correct (e.g.
`lateral` for angle-finding, then `guide-positioning` for the eventual
closing) — present combinations explicitly rather than forcing a single
pick.

Use `AskUserQuestion` when the fit is genuinely close between 2+ options;
skip asking and just state the pick when one option is a clear, obvious
fit — don't manufacture a menu prompt for a decision that isn't actually
close.

### Step 4 — Wait for Randy's confirm/override

Randy may accept the recommendation, pick a different skill from the full
catalog, combine skills differently, or say none apply. Do not proceed to
drafting until this is settled.

### Step 5 — Record the selection

Note which technique skill(s) were applied and why, in whatever
tracking artifact the calling format skill already uses (an article's own
notes, a video's `metadata.json`, etc.) — so a later read of the piece
shows why a technique was used, not just that the final draft happens to
read a certain way. This is a one-line note, not a new file.

## How each format skill wires this in

Each format skill gets one short addition near the top of its own
workflow (not a rewrite): "Before drafting, run `style-selector` to
determine which optional technique skill(s), if any, apply to this piece."
Placed early enough that the recommendation can shape structure (e.g.
`guide-positioning`'s stage 3 needs to be planned into the closing before
the draft is written, not patched in after).

## Gotchas

- Don't run this on autopilot for every single piece — a straightforward
  war-story Short with an obvious angle and the standard Riddle of Steel
  close needs neither Ideation nor a persuasion technique skill layered on
  top. Recommending "none" is a valid, complete Step 3 output.
- The lateral-thinking family and `guide-positioning`/`infomercial-pitch`
  solve different problems (finding an angle vs. landing a persuasion
  beat) — don't recommend a lateral-thinking technique when the real gap
  is in the CTA, or vice versa.
