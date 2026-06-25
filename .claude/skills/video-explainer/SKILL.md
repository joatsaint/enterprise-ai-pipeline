---
name: video-explainer
description: Generate a full-spec animated educational explainer video (1080x1920, 30fps, ~30s vertical short) with Remotion + Claude Code, tuned to Randy's senior-IT / AI-era niche. Use when Randy asks to "make an explainer video", "turn this into a short", "animate this concept", "video explainer for X", or wants a Shorts/Reels/LinkedIn vertical video teaching a topic. Produces a rendered MP4. Built from Sabrina Romanov's prompt #1 spec, hardened by a verified working render.
---

# /video-explainer

Turns a topic into a 5-scene animated educational explainer (vertical short).
Verified working — the reference render is `remotion-test/out/how-ai-agents-work.mp4`.

## Prerequisites (check first)

1. The **remotion-best-practices** skill must be installed (it lives at
   `.agents/skills/remotion-best-practices/`). If missing, install once:
   `npx skills add remotion-dev/skills`, then restart the session.
2. A Remotion project with `@remotion/google-fonts` and `@remotion/transitions`.
   The working one is `remotion-test/` — reuse it, or scaffold a fresh one:
   ```
   npx create-video@latest --yes --blank --no-tailwind <name>
   cd <name> && npm i && npm i @remotion/google-fonts @remotion/transitions
   ```
3. Node present (v24 verified). Render cost = Claude tokens only; Remotion is
   free for solo use (free for teams ≤3).

## Build workflow

**STEP 1 — RESEARCH & SCRIPT (approval gate — do NOT skip).**
Research the topic, then write a **5-scene script**: Hook → 3 teaching beats →
Payoff. Each scene = one-line headline + 1–2 sentence explanation + a visual
description (what SVG diagram/animation illustrates it). **Show Randy the script
and wait for approval before writing any code.** (This is the human gate; a
draft is never approval.)

**STEP 2 — BUILD.** Copy `assets/Composition.starter.tsx` into the project's
`src/Composition.tsx` and edit the five `Scene*` components for the approved
script. Keep the helpers (`SafeZone`, `SpringIn`, `CountUp`, `DrawPath`,
`ArrowHead`, `Icon`, `Node`, `Particles`) unchanged — they encode the spec.
Set `src/Root.tsx`: `width={1080} height={1920} fps={30}` and
`durationInFrames = 5*SCENE - 4*TRANS` (= 912 with the defaults).

**STEP 3 — RENDER & PREVIEW.**
`npx remotion render MyComp out/<slug>.mp4`. For a quick check render stills:
`npx remotion still MyComp out/chk.png --frame=<n> --scale=0.4`. Offer
`npx remotion studio` so Randy can preview/scrub in the browser.

## Non-negotiable spec (baked into the starter — keep it)

- **Format:** 1080x1920, 30fps, ~30s. Vertical only.
- **Safe zones:** ≥150px top, ≥170px bottom, ≥60px sides. Nothing important at edges.
- **Font floors:** headlines 56px+, body/subtitles 36px+, labels 28px min. Nothing under 28px.
- **Motion:** every element enters with `spring({ damping: 200 })` — no linear/CSS
  transitions (forbidden in Remotion renders). Stagger related items 8–12 frames.
  Cross-fade scenes with `TransitionSeries` + `fade()` (12 frames).
- **Diagrams:** built as inline SVG (no external assets), and they **draw
  themselves** via `DrawPath` (stroke-dashoffset). Use the `Icon` components and
  filled `ArrowHead` — **never emoji** (they render inconsistently).
- **Numbers:** count up with `CountUp` (interpolate + `tabular-nums`).
- **Final scene:** particle background (≈13 drifting circles).
- **Font:** Inter via `@remotion/google-fonts/Inter`.

## Randy's niche defaults (this is what makes it *his*)

- **Audience:** senior IT / infrastructure veterans in the AI era. Topics teach a
  concept they need to stay relevant (how agents/LLMs/RAG/MCP/automation work).
- **The PAYOFF scene must reframe on-niche** — land a P1 ("will AI replace me")
  or P3 ("layoff anxiety") beat that ends on agency/empowerment, e.g. "Agents
  don't replace experts. They run your playbook — faster. Be the one who runs
  them." Never end on a generic "thanks for watching". See the ICP pain map.
- **Voice:** plain, operator-to-operator, no hype. Match `knowledge/me/voice.md`.
- **Title/hook rule:** lead with the twist/irony, name a real pain — same gate as
  articles (a hook that doesn't name a pain gets rewritten).

## Palette (TBD — change in ONE place)

`COLORS` at the top of the starter. Currently a neutral dark theme
(bg `#0a0a0a`, indigo `#6366f1`, green `#22c55e`). Randy is deciding the brand
palette later (candidate: Command Deck matrix-green). Swap `COLORS` only.

## After building

- It's a build → **ship a post** with it (build → post → portfolio) when audience
  cadence allows; this is overflow work, never ahead of the LinkedIn schedule.
- Remind Randy: creating/rendering a video is NOT approval to publish.

## Gotchas

- (none logged yet — append here as real sessions surface edge cases)
