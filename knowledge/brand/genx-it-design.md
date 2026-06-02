# genx-it-design.md

**Visual design system — Randy Skiles / IT-to-AI Transition Playbook**
Version 1.0 · May 30 2026
Pairs with `voice.md` (the written voice) and `LINKEDIN_CONTENT_SKILL.md` (the content engine).

Load this before generating ANY image, carousel, or graphic. `voice.md` keeps the *writing* consistent. This file keeps the *look* consistent — the same way, and for the same reason.

---

## Core principle

**One hero relic per piece. The relic does the same job in the image that the war story does in the writing: it earns belief before a word is read.**

A sysadmin scrolls past a glossy AI gradient. He stops for a beige tower, a ZIP disk, a green terminal — because his hands remember it. Recognition is the credential.

Three rules govern everything below:

1. **One hero relic, chosen to rhyme with the lesson.** Not a pile of nostalgia. One object, deliberately matched to the point the piece is making.
2. **Era, not brand, in images.** Evoke the generic artifact (beige tower, green CRT, the 56k handshake). Never reproduce trademarked characters or logos — legal risk, and it looks like a reposted meme. Named references (Hitchhiker's, Office Space, etc.) live in the *written copy*, capped at two per piece.
3. **Realism over cartoon.** WSJ / TIME feature-photo quality. The humor is in the contrast, never in exaggeration.

---

## Palette

| Name | Hex | Use |
|---|---|---|
| Void black | `#0C0C0E` | primary background, server-room dark |
| Charcoal | `#16161A` | panels, secondary surfaces |
| Industrial amber | `#E0A21A` | primary accent — hero headlines, warning triangle, side rail |
| Bone | `#E8E2D5` | distressed display type, "paper" white |
| Clean white | `#F2F0EA` | subheads, body overlay, mobile-legible text |
| CRT phosphor green | `#3CE874` | terminal text, "all systems OK" — the calm signal |
| Amber mono (alt) | `#FFB000` | alternate monochrome-monitor screens |
| Incident red | `#C1432E` | warning sticky notes, alert states — use sparingly |
| Ash grey | `#8A8780` | secondary / caption text |

Lighting is always two-source: **warm monitor/lamp glow + cool server-room blue.** Cinematic, never flat.

---

## Typography

- **Display (hero words):** heavy compressed/condensed sans with grunge/eroded texture — field-manual feel. Anton, Compacta, Trade Gothic Bold Condensed, or a distressed slab. This is the "THE STEEL / SERVER ROOM" face.
- **Subhead + overlay body:** clean grotesque/humanist sans — Inter, Archivo, Söhne, Helvetica Neue. Always legible on mobile.
- **Mono (terminal + ticket):** IBM Plex Mono, JetBrains Mono, or Courier. Screen readouts and the incident-ticket header only.

---

## Recurring framing devices

The "brand furniture." Reusing these ties a carousel together and makes a one-off feel like part of the series:

- **Incident ticket header** — `INCIDENT #` / `PRIORITY: UNDEFINED` / `ROOT CAUSE` / `NOTES`, in mono. Already the chapter-opener device.
- **Peeling sticky notes** — handwritten, worn-manual paper stock. Carry the gag or the dread (`RESTORE TESTED?`, `DON'T PANIC`, `WHERE'S BOB?`).
- **The mug** — `CAFFEINE / SARCASM / UPTIME`, in frame, steaming.
- **The spiral notebook** — `DOCUMENT THE STUFF THAT MATTERS`.
- **Vertical side rail** — small-caps mono running up the left edge: `FIELD MANUAL // [SECTION]`.
- **Texture grade** — fine film grain, faint CRT scanlines, slight analog degradation on *accents only* (never on faces or the whole frame).

---

## Hero-relic library

Pick ONE. Match it to the lesson.

**Physical relics** (era-accurate, generic, no branding):
beige tower PC · deep CRT monitor · 3.5" floppy / ZIP disk · RJ45 crimper + cable rat's-nest · dot-matrix tractor-feed paper (perforated edges) · on-call pager / first-gen thumb-keyboard handheld · LTO/DAT backup tapes + off-site rotation box · raised-floor data-center tile lifted · KVM switch · Brother label maker · UPS unit (the battery beep) · punch-down / 110 block.

**Screen relics** (texture *and* the argument):
phosphor-green terminal — `uptime`, load averages, rows of `[ OK ]` · bare `C:\>` prompt · Norton defrag block-grid mid-reorganize · BSOD · ScanDisk · raw `ipconfig` / `ping` output · the boot-chime moment · the hourglass cursor.

---

## Overlay & caption phrase bank

Recognition lines safe for overlays and post copy (Tier 1 — reinforce authority, never undercut it):

"Have you tried turning it off and on again." · "Is it even plugged in." · PEBKAC / ID-10-T / a layer-8 problem · the 2 a.m. page · "works on my machine" · "patience: dial-up certified" · "caffeine first, questions later."

**Thesis lines** — treat as recurring series motifs, not throwaways:

- *"The bridge between analog and digital chaos."* → the translation-layer thesis.
- *"Retro, not irrelevant."* → "you're not behind — you're early," compressed.

---

## What stays out

Hard cuts, because they cost authority with IT directors:

- **No fashion / cartoon / playground nostalgia** (scrunchies, He-Man, pogo sticks). Gen X, but not *this* brand.
- **No innuendo / "dirty" humor.** Credibility leak on LinkedIn.
- **No generational punch-down** (Gen Z jokes). Sarcasm aims at bad vendors and bad practices — never at people.

---

## Format specs

**Always confirm post vs. article before generating.**

| | Post image | Article header |
|---|---|---|
| Orientation | Vertical | Landscape |
| Size | 1080 × 1350 | 1376 × 768 |
| Border | 1-inch clean white | 1-inch clean white |
| Title overlay | Lower third, large | Lower third, gradient backing |

If the piece is a **carousel**: base every slide on Void black + one consistent relic motif + the ticket/sticky devices; follow the hook → pain → steps → result → CTA structure from the content system.

---

## Reusable image-prompt template

Drop the brackets, keep the rest. This bakes the system in so every prompt starts on-brand.

```
Create a [POST: high-impact vertical LinkedIn feed image, 1080x1350 | ARTICLE: professional LinkedIn article header, landscape 1376x768].
Clean 1-inch white border. Realistic, cinematic, WSJ/TIME feature-photo quality — never cartoonish. The humor is in the contrast, not exaggeration.

SCENE: [one concrete scenario — a real IT moment]
HERO RELIC (single focal object): [pick one from the relic library — matched to the lesson]
BRAND FURNITURE (subtle, in frame): peeling sticky note reading "[short line]"; "CAFFEINE / SARCASM / UPTIME" mug; faint CRT scanlines and film grain.
PALETTE: void-black/charcoal base; industrial amber accent; CRT phosphor-green screen text; cool blue + warm monitor lighting.
TYPE: heavy distressed condensed sans for the title; clean sans for the subline; mono for any screen/ticket text.

TEXT OVERLAY: "[title]" — [placement], legible on mobile.
```
