---
name: linkedin-carousel
description: Generate a code-rendered LinkedIn carousel (1080x1350 portrait, GenX-IT engineering aesthetic) from one of Randy's articles, compiled to a single PDF Document post. Use when Randy asks to "make a carousel", "turn this article into a carousel", "carousel for ART#", or wants slides for a LinkedIn post. Produces PNGs + a compiled PDF. Built from the GenX-IT carousel blueprint; renders via the Remotion still pipeline (no image-gen cost). Currently being A/B-tested against the gpt-image-1 image carousels.
---

# /linkedin-carousel

Turns an article into an 8–9 slide LinkedIn carousel using a terminal/engineering
visual system the GenX-IT audience respects — code-rendered (deterministic, $0,
editable), as opposed to the AI-image carousels (`generate_carousel_images.py`).
Reference output: `content-engine/content/articles/ART3-motel/ART3-motel_carousel_CODE.pdf`.

> **A/B STATUS (2026-06-20):** Randy is testing this code-rendered style vs the
> existing image-gen carousels for ICP engagement/value. Keep both pipelines until
> the test calls it. Don't retire image carousels.

## Read first (mandatory, content-engine rules)

1. `content-engine/CONTENT_PUBLISHING_RULES.md` (Carousel Publishing Rule, image-format rule)
2. `knowledge/me/voice.md` — **Guardrail A**, below
3. `knowledge/me/icp_pain_map.md` + `knowledge/me/kill_rubric.md` — title rule

## Two guardrails (do not skip)

**A. All copy routes through the voice profile + title rule.**
Never paste raw article text or external-tool (e.g. Gemini) phrasing onto a slide.
Every headline/sub-line is rewritten in Randy's voice (`knowledge/me/voice.md`),
and the Slide-1 hook obeys the title rule: lead with the twist/irony, name a Core
Pain (P1 "will AI replace me", P3 layoff anxiety, P4 "25 yrs devalued"). A hook
that doesn't name a pain gets rewritten or killed (`kill_rubric.md`). If the
article already has a `carousel.md` with `reviewed: true` copy, reuse it verbatim
(it's already on-voice) — that also keeps an A/B render-test honest.

**B. CTA defaults to the first-comment technique — SWIP/DM gate is OPTIONAL, OFF.**
Randy uses the first-comment link method (lead-magnet link in the first comment,
never the post body — LinkedIn link penalty). The last slide says "link in
comments". The blueprint's "comment SWIP and I'll DM you" gate is **not** a
default — only add it if Randy explicitly asks this time.

## Design system (baked into the starter)

- **Format:** 1080×1350 (4:5 portrait). 8 slides default (match the article; 9-slide
  arc below). One standalone thought per slide.
- **Palette (GitHub-dark):** bg `#0D1117`, text `#FFFFFF`, muted `#8B949E`, border
  `#30363D`, panel `#161B22`, alert-orange `#FF7B72`, firewall-yellow `#E3B341`.
- **Type:** Inter (headlines/body), Fira Code mono (terminal labels, commands, stack
  items). Body ≥ 24pt-equivalent for mobile.
- **Aesthetic:** terminal blocks, status dots, 2-col panels, dependency stacks,
  grep/command blocks, flow arrows, 1px borders. **No abstract corporate art, no emoji.**

## 9-slide narrative arc (psychological progression for the GenX-IT reader)

1 Hook (the incident) · 2 Chaos (the scramble) · 3 True Crisis (breakdown) ·
4 Scapegoat (unfair blame) · 5 Root Cause (hidden upstream change) · 6 Shift in
Thinking (real threat isn't the tech) · 7 Unreplaceable Skill (operational logic) ·
8 The Verifier (human-in-the-loop) · 9 Hype Filter / CTA.
Collapse to 8 when the article's beats merge (ART3 does). End on a P1/P3 empowerment
reframe — same spine as `/video-explainer`.

## Build workflow

**STEP 1 — MAP & APPROVE (gate).** Map the article to the arc; draft each slide's
headline + sub-line in Randy's voice. **Show Randy the slide copy and wait for
approval before rendering.** Status-change safety: creating slides is NOT approval;
**never edit `content-engine/dashboard_state.json`** or set any review/approve/
schedule/publish flag unless Randy approves that exact change.

**STEP 2 — BUILD.** Copy `assets/Carousel.starter.tsx` into a Remotion project
(reuse `remotion-test/`, which already has `@remotion/google-fonts` +
`@remotion/transitions`). Compose slides from the provided patterns (`TerminalAlert`,
`TwoCol`, `DependencyStack`, `GrepBlock`, `VerifierFlow`, `CtaPanel`). Register a
composition in `src/Root.tsx`: `id="Carousel"`, `width=1080 height=1350 fps=1`,
`durationInFrames=CAROUSEL_DIMS.COUNT` (one frame per slide).

**STEP 3 — RENDER STILLS.** One PNG per slide:
```
for i in 0..COUNT-1: npx remotion still Carousel out/carousel/slide-0{i+1}.png --frame={i}
```

**STEP 4 — COMPILE PDF** (single Document post per the Carousel Publishing Rule):
```python
from PIL import Image
import PIL.JpegImagePlugin; Image.init()   # register JPEG handler (Pillow lazy-init bug on this box)
imgs = [Image.open(p).convert("RGB") for p in sorted(glob("out/carousel/slide-*.png"))]
imgs[0].save("<article>/<slug>_carousel_CODE.pdf", format="PDF", save_all=True, append_images=imgs[1:])
```
Name it distinctly (`_carousel_CODE.pdf`) — never overwrite the image-gen `_carousel.pdf`.
> Known bug: `content-engine/generate_carousel_images.py:compile_carousel_pdf()`
> omits the `Image.init()` / JpegImagePlugin import and will `KeyError: 'JPEG'` on
> Python 3.14's Pillow. Same fix applies if/when that's patched.

## After building

- Upload the PDF as a LinkedIn **Document** post (not individual images). Lead-magnet
  link goes in the **first comment**.
- Building a carousel is NOT approval to publish. Don't touch dashboard state.
- This is overflow/build work — stays behind the LinkedIn posting cadence.

## Gotchas

- **Article must be live before carousel is scheduled.** ART6 had its teaser and first-comments published weeks before the article existed — carousel was then orphaned from the launch window. The hard publishing gate in CONTENT_PUBLISHING_RULES.md now enforces sequence: article live → teaser same day → carousel next day. Never schedule a carousel until you have the live LinkedIn article URL in hand.

- Known Pillow bug already documented above (`Image.init()` / JpegImagePlugin fix) — keep it
  here too since this is the section future sessions check first.
- Every carousel slide MUST have both `overlay_text` (headline) AND `support_text` (sub-headline) populated in the Gemini storyboard. A headline alone doesn't deliver enough value — the sub-headline completes the contract with the reader. If Gemini skips `support_text`, add it manually from the carousel.md copy before generating images.
- Re-overlaying existing PNGs: if slides need text re-applied, the gradient must use a two-phase approach — soft fade (top 30% of zone) → fully opaque solid block (bottom 70%). A plain gradient (alpha 0→225) is NOT enough to suppress baked-in text from a prior run and causes double headlines.
- Word wrap on sub-headlines: use balanced wrapping (iteratively narrow target width until last line has ≥3 words). A naive max-width wrap leaves 1-2 word orphan tails that look unprofessional.
- **HARD RULE — LinkedIn URL:** Randy's correct LinkedIn URL is `https://www.linkedin.com/in/randy-skiles/` (with hyphen). Never use `randyskiles` (no hyphen). This has been wrong multiple times. Before writing any URL into content, check `memory/reference_randy_profile_links.md`.
