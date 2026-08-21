---
name: youtube-title-hook-generator
description: Turns a single statistic, study finding, or core concept into a batch of high-CTR YouTube titles and thumbnail text, sorted by psychological angle (Drama & Conflict, Fear & Urgency, Curiosity & Number-Driven). Use when Randy has a real stat/finding/concept in hand and needs title + thumbnail options fast, before committing to a script. Complements title-generator (LinkedIn Pulse articles, GEO-scored formulas) and video-hook-types.md (opening spoken hooks) — this one is titles + thumbnail text specifically, and works for both Shorts and long-form.
---

# YouTube Title & Thumbnail Hook Generator

Adapted 2026-08-11 from a skill file Randy supplied. Converted to this
project's real skill format (frontmatter + markdown, matching every other
skill here) and wired into the existing title/hook/thumbnail ecosystem
instead of standing alone.

## When to use this vs. the other title/hook tools

- **This skill** — you have one real stat, study finding, or concept and
  need a batch of YouTube title + thumbnail-text options fast, sorted by
  psychological angle. Works for Shorts and long-form.
- **`title-generator`** — LinkedIn Pulse articles specifically. 10-formula
  library, GEO-strength scoring, wired into the article content workflow.
  Don't use this skill for LinkedIn article titles.
- **`video-hook-types.md`** (`reference_video_hook_types`) — the *spoken,
  opening* hook of a video (first 0-10s), not the YouTube title/thumbnail
  text. A video still needs both: this skill for the title/thumbnail,
  `video-hook-types.md` for what's actually said in the first line.
- **`thumbnail-phrase-bank.md`** (`docs/Mark Savant/`) — a running bank of
  already-used/considered thumbnail phrases, format-agnostic. Check it
  before finalizing thumbnail text from this skill, to avoid repeating a
  phrase already used on a different video.

## Inputs needed

1. **Core concept** (required) — the stat, study finding, or concept to
   build titles from. Real and verified, not invented — same
   citation-guard discipline as everything else in this pipeline.
2. **Channel vibe** (optional, default: matches Randy's existing
   operator/Gen-X-IT voice — not generic "sensational" or "corporate")
3. **Target audience** (optional, default: IT/sysadmin AI-anxiety ICP —
   see `[[project_icp_pain_map]]`, unless the piece is explicitly for one
   of the channel's other lanes)

## Workflow

1. **Analyze the strengths.** Identify the most emotionally charged
   element of the input — a stat gap, a conflict between two groups, a
   hidden risk, a surprising reversal. Name it explicitly before drafting
   titles, so every title traces back to the same real hook.

2. **Generate 3 titles per angle** (9 total), short and punchy sentences:
   - **Drama & Conflict** — opposition, tension, secrets (e.g., leadership
     vs. practitioners, experts vs. outsiders)
   - **Fear & Urgency** — immediate risk, blind spot, warning, a mistake
     already made
   - **Curiosity & Number-Driven** — a specific, real number or a
     paradoxical statement that forces a click

3. **Thumbnail text** — 3-4 options, strictly 2-4 words each, that
   complement the chosen title without repeating its wording. Check
   `docs/Mark Savant/thumbnail-phrase-bank.md` first to avoid reusing a
   phrase already logged there; add the chosen one to that bank after
   Randy picks.

4. **Format for scannability** — markdown headers per angle, bold the key
   word/number in each title, bullet points throughout.

## Output format

```
## Titles — [core concept, one line]

**Real hook identified:** [the specific emotionally-charged element this
batch is built from]

### Drama & Conflict
- [Title 1]
- [Title 2]
- [Title 3]

### Fear & Urgency
- [Title 1]
- [Title 2]
- [Title 3]

### Curiosity & Number-Driven
- [Title 1]
- [Title 2]
- [Title 3]

### Thumbnail Text (2-4 words each)
- [Option 1]
- [Option 2]
- [Option 3]
- [Option 4 (optional)]
```

## Gotchas

- Every title must trace back to something real and verified — this skill
  generates phrasing, not facts. If the core concept hasn't been
  citation-checked yet, do that first (see `citation-guard` /
  `kb-research`), don't generate titles from an unverified claim.
- Don't let "Fear & Urgency" tip into fabricated stakes. The real stat
  should already carry enough weight — inventing a scarier framing than
  the source supports is exactly the kind of embellishment Citation Guard
  exists to catch (see `ai-cant-tell-sources.md` for a real example of
  this being caught and dropped).
- This skill doesn't replace `video-hook-types.md`'s job. A punchy title
  can still open with a flat, generic spoken hook — check both.
