# genx-it-carousel.md

**Carousel extension — Randy Skiles / IT-to-AI Transition Playbook**
Version 1.0 · May 30 2026
Inherits everything from `genx-it-design.md` (palette, type, brand furniture, relic library, the don't-list). This file adds only the carousel layer. Read `genx-it-design.md` first.

Maps to the carousel spec in `LINKEDIN_CONTENT_SKILL.md`: 5–8 slides, headline under 8 words, body under 30 words, built in Canva → exported PDF → uploaded to Buffer as a document post.

---

## Core principle

**A single image gets one hero relic. A carousel gets one relic motif, threaded across every slide — and the relic's STATE tracks the emotional arc.**

The mistake (and what generic "make me a design system" carousels do): a different relic on every slide. That reads as a scrapbook, dilutes recognition, and makes 8 slides feel like 8 unrelated posts.

The move: pick ONE relic for the whole carousel — then let it *change state* as the story turns. The relic becomes the through-line that makes the swipe feel like one continuous piece, and its state does the emotional work the body text doesn't have room for (under 30 words a slide leaves the picture to carry the feeling).

A terminal is the cleanest example. Same machine, every slide — but:
- it's **erroring** on the pain slides,
- **executing** on the proof slides,
- showing **all-green `[ OK ]`** on the result slide.

Same relic. The arc is told in its state, not in five different objects.

---

## The arc → relic-state map

Your slide structure already IS hook → pain → steps → result → CTA, even though the atomizer doesn't label it. Here's the mapping, with the relic state for each beat:

| Slides | Beat | Relic state | Feeling |
|---|---|---|---|
| **01** | Hook | The relic at its most arresting — the *incident* moment, frozen | "Stop scrolling." |
| **02–03** | Pain / setup | The relic showing the problem — error state, BSOD, the 2 a.m. page, the dead drive | Recognition, dread |
| **04–06** | Proof / steps | The relic resolving — commands running, `[ OK ]` checks appearing one by one, the bar filling | Momentum, competence |
| **07** | Result / tease | The relic at rest — `uptime`, all-green, the calm after | Earned calm |
| **08** | CTA | Hand off to **brand furniture** — the relic recedes; the sticky note / mug carries the ask | "You can do this too." |

The CTA slide deliberately drops the relic and lets the furniture (a peeling sticky note, the `CAFFEINE / SARCASM / UPTIME` mug) deliver the offer. It's a visual gear-change that signals "the story's done, here's the door."

---

## Format specs

| | Carousel slide |
|---|---|
| Orientation | Portrait (more mobile feed space than square) |
| Working size | 1080 × 1350 per slide |
| Count | 5–8 slides (8 is the full arc; 5 compresses pain+proof) |
| Build | Canva (matches your pipeline) |
| Export | Single multi-page PDF → Buffer document post |
| Border | The 1-inch white border is the single-image rule — for carousels, instead run a **thin amber keyline** (4px) inside each slide edge so the deck feels bound as a set. White borders on every slide waste scarce real estate. |

**Text limits (from the skill — do not exceed):** headline under 8 words, body under 30 words. The relic absorbs the overflow. If a slide needs more than 30 words, the relic isn't doing its job — strengthen the picture, cut the text.

---

## Continuity devices — what stays fixed vs. what moves

This is what makes 8 slides read as one piece.

**Fixed on every slide:**
- The palette (void-black base, amber accent, phosphor-green screens)
- The display typeface and the headline position (top third, consistent slide to slide)
- The **slide counter** — small mono, e.g. `03 / 08`, bottom corner. Cheap, and it signals "keep swiping."
- The **side rail** — `FIELD MANUAL // [SECTION]` running up the left edge, same as the single-image spec.
- The relic's *identity* (it's the same terminal / same drive / same pager throughout).

**Changes slide to slide:**
- The relic's **state** (per the arc map above).
- The headline and body.

That split is the whole trick: fixed frame, evolving relic. Continuity without monotony.

---

## Picking the carousel relic

Same rule as single images — match it to the lesson — but with one added test: **the relic has to have states.** A relic that can only sit there (a floppy disk, a label maker) makes a flat carousel. A relic that can error → resolve → rest tells a story across the swipe.

Strong carousel relics (they have an arc built in):
- **Terminal** — error → `[ OK ]` checks → `uptime`. The default.
- **Boot sequence** — BIOS POST → loading bar → login prompt → desktop. Literally a progress narrative.
- **Norton defrag grid** — fragmented blocks → reorganizing → clean. Visual order-from-chaos.
- **Rack of indicator lights** — all red → mixed → all green.
- **The pager / on-call screen** — alert firing → acknowledged → quiet.

Weaker for carousels (fine as a single-image hero, static across slides): floppies, label maker, the mug alone, a single sign.

---

## Worked example — "Don't Panic" as a carousel

Your real ART4 8-slide outline, with the design layer applied. Relic motif: **the phosphor-green terminal** (already the article's hero relic — so the carousel and the Thursday post share it, reinforcing the week). Watch the state track the arc.

| Slide | Headline (your copy) | Relic state — the visual suggestion | 
|---|---|---|
| 01 | Don't Panic. | Terminal, frozen mid-blink at a single calm `$ _` prompt against the void. The worn Hitchhiker's paperback beside the keyboard. Arresting because it's *quiet* amid a loud topic. |
| 02 | I've seen this before. | Same terminal — now scrolled back to an old session: `mounting vsphere…`, dated timestamp. The relic "remembers" the virtualization wave. |
| 03 | The VM stack saved us. | Terminal showing a server auto-spawning — `node-02 … [ SPAWNED ]`. The relic doing the thing the slide describes. |
| 04 | The automation raised the floor. | Split: blurred panic headlines behind, the sharp terminal foreground running clean. Same contrast as the Thursday post — deliberate echo. |
| 05 | Every wave does the same thing. | Terminal log, three stamped lines: `dotcom`, `virtualization`, `cloud` — each `[ SURVIVED ]`. History as a command history. |
| 06 | AI runs on Linux. | The payoff slide — terminal full of green `[ OK ]` service checks, `uptime 128 days`. The relic at its most reassuring. |
| 07 | A new road, not the end. | Terminal at rest, cursor blinking calm. A peeling sticky note enters frame: `WHERE'S BOB?` — the planted hook from the article header. |
| 08 | You're not behind. You're early. | Relic recedes to soft-focus. Foreground: the `CAFFEINE / SARCASM / UPTIME` mug and a sticky note with the offer — "Free guide → link in comments." Furniture carries the CTA. |

Notice slide 04 and slide 07 deliberately reuse motifs from the Don't Panic *post* and *article header* (the blurred-headlines contrast; the `WHERE'S BOB?` note). That cross-format echo is the point of having one system — the Tuesday article, Thursday post, and Friday carousel all visibly belong to the same week.

---

## Per-slide prompt template (feeds the atomizer's "visual suggestion" field)

The atomizer already asks for a visual suggestion per slide. Drop this in for each:

```
SLIDE [n] / [total] — beat: [hook | pain | proof | result | CTA]
RELIC STATE: [the one motif, in its state for this beat — e.g. "terminal showing
  cascading errors" / "terminal, three green [ OK ] checks" / "relic in soft focus"]
FIXED FRAME: void-black; amber 4px keyline; headline top-third in distressed
  condensed sans; "[SECTION]" side rail; "[n] / [total]" counter bottom corner.
HEADLINE: "[under 8 words]"
BODY: "[under 30 words]"
[CTA slide only] FURNITURE: mug + sticky note carrying the offer; relic recedes.
```

---

## Quick checklist (carousel-specific, on top of the skill's)

- [ ] One relic motif, not one-per-slide
- [ ] Relic *state* tracks hook → pain → proof → result → CTA
- [ ] Fixed frame: palette, headline position, side rail, slide counter consistent
- [ ] Amber keyline, not white border, per slide
- [ ] Headlines under 8 words; body under 30 words (skill rule)
- [ ] CTA slide drops the relic for brand furniture
- [ ] At least one motif echoes that week's post or article header
- [ ] Exported as one PDF for the Buffer document post
