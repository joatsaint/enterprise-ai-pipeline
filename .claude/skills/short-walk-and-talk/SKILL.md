---
name: short-walk-and-talk
description: Produce a finished video from Randy's raw, unscripted, phone-shot vertical talking-head footage (a "walk and talk") — a single continuous take, no script, no HeyGen avatar. Use whenever Randy hands over a raw video file and says it's a walk-and-talk, a raw take, an off-the-cuff video, or asks to process/turn a video he shot into a Short or long-form upload. Covers the Short-vs-long-form length decision, the visual identity (color/font), thumbnail formula, caption style, and CTA-length rule for this format specifically — self-contained, no open questions needed to execute. For platform-universal Shorts rules (algorithm, hook timing, posting cadence) see youtube-shorts; this skill only covers what's specific to raw walk-and-talk footage.
allowed-tools: Read, Edit, Write, Bash, Grep, Glob
---

# short-walk-and-talk

One format among several planned format-specific skills (per Randy's system,
2026-07-24) — each distinct repeatable video format gets its own
self-contained skill so nothing has to be re-asked or re-decided per video.
This one covers **raw, unscripted, single-continuous-take vertical footage**
Randy shoots himself, walking, no script, no HeyGen avatar. Built from the
first real production pass (`Red-Flags`, 2026-07-24) — the specific numbers
and decisions below are the actual lessons from that pass, not guesses.

**Design principles, stated by Randy directly and binding on every choice
in this file:**
- **Minimalist.** Remotion graphics and fonts *enhance* the video, they
  never distract from it — no heavy motion/special-effects treatment
  unless the video's actual subject is special effects. This format gets
  a light touch: text overlays and captions only, no animated
  compositions.
- **Quality over all else.** When a production choice is ambiguous or a
  shortcut would save time at the cost of a worse result, take the higher-
  quality path. Randy's own framing (2026-07-24): "I always want to over-
  deliver on value in my content." This is the tie-breaker whenever this
  skill doesn't give an explicit answer.

---

## Format identity

- **Source:** phone-shot, vertical, single continuous take. No script,
  no teleprompter, no HeyGen render.
- **Aspect ratio:** 9:16 (matches source — do not reformat).
- **Editing philosophy:** minimal to zero internal cuts. This is not a
  fast-cut, multi-clip edit — it's one take, trimmed at the ends, not
  chopped in the middle. If a mid-video cut is ever unavoidable, it must
  land on a complete grammatical clause (see Gotchas — never cut mid-list
  or mid-sentence even if it costs a few seconds of cap margin).

## Visual identity (locked 2026-07-24)

- **Color:** `#33FF33` phosphor green — the Jarvis-series WOPR palette,
  reused deliberately for cross-format continuity, not a new scheme.
- **Font:** JetBrains Mono (`@remotion/google-fonts/JetBrainsMono`).
- **Glow:** soft `textShadow` glow on the green text, matching
  `JarvisScannerFace.tsx`/`JarvisWarGamesTyping.tsx` — same visual family,
  don't reinvent the treatment per video.
- **Where this applies:** thumbnail text overlay, any title-card text, AND
  spoken-word captions (corrected 2026-07-24 — Randy's explicit call:
  captions use the same `#33FF33` green with a black outline, matching the
  thumbnail text exactly, not a separate white/black-outline treatment).
  Outline stays black and thick enough (`Outline=4` in the ASS style) to
  hold contrast against bright outdoor backgrounds — the outline carries
  the legibility job, not a color swap away from the brand green.
- **No animated Remotion compositions for this format** — text overlays and
  burned captions only. Matches the minimalist principle above.
- **Prompt card overlay:** when a video shows the viewer a prompt to
  copy, cut to a full black card with left-aligned bright-green text and
  reveal it in short line groups — see `long-short-pair`'s "Build the
  prompt card overlay" section for the full spec. Confirmed 2026-08-18
  against a real published Short. Distinct from the burned-caption style
  above — reserve it for copy-paste prompts, not general narration.

## Thumbnail formula

- Extract a real frame of Randy's face from the actual footage — the most
  expressive/highest-motion moment near the hook, not an arbitrary frame.
- Text overlay: 3–5 words, bottom third, green/JetBrains-Mono per above.
- Wording must be specific to *this* video's actual story, not a generic
  template phrase — write it after watching the footage, not before.
  (Example from the first pass: "Red Flags I Missed," tied directly to the
  war story in that video, not a reusable stock phrase.)

**Prepend the thumbnail to the video itself — mandatory, no exceptions**
(Randy's rule, 2026-07-24): YouTube Shorts has no manual custom-thumbnail
upload option, so the only way to influence what YouTube shows as the
cover is to control what's actually in the frame it auto-picks from. Add
a **0.5-second freeze of the finished thumbnail image** (with its text
overlay) as the literal first frame(s) of the final render, before the
live footage starts. This is a safety net as much as a technique — if
Randy forgets to set a thumbnail manually, the odds favor YouTube
defaulting to a frame at/near the start of the video, which will then
already be the designed thumbnail rather than an arbitrary moment.
0.5s is long enough to plausibly register as a selectable frame, short
enough not to meaningfully eat into the critical first-3-seconds hook
window. Match the main video's exact codec/resolution/framerate/audio
params when building the freeze segment (silent audio track, same
duration) so the concat doesn't require a re-encode of the untouched
footage. Verify the seam afterward — spot-check a frame during the
freeze and a frame just after it starts, confirm the cut is clean and
the total duration still respects the 180s Short cap (0.5s adds
negligible margin, but check anyway if the payload was already close to
the ceiling).

## Length decision — Short vs. long-form

This is a decision, not a default. Work it in this order:

1. Transcribe the full take (word-level timestamps — see Gotchas).
2. Map it: hook → setup → payload (the story that delivers the title's
   actual promise) → CTA.
3. Find where the payload completes as a full, satisfying thought.
4. **If that point is under 180 seconds:** it's a Short. Cut there.
5. **If the payload itself doesn't complete until past 180 seconds:** it
   ships long-form. Never force-cut into the payload to hit the cap —
   a truncated story fails the actual title promise, which matters more
   than the format.
6. The CTA gets evaluated separately (below) — never let CTA length be the
   reason a video misses the 180s cap when the payload itself would have
   qualified.

## CTA rule for this format

- Target: spoken CTA under ~10 seconds. Randy's own instruction (2026-07-24):
  practice it down to that length before recording, rather than relying on
  editing to fix it after.
- Since this format is unscripted, `style-selector` only applies *before*
  recording — if Randy wants help shaping the spoken CTA line he's about to
  practice, `guide-positioning`'s objection-preemption move is the most
  likely fit. There is no post-hoc drafting step to attach it to once
  footage is in hand.
- **If the recorded CTA runs long and doesn't fit inside the 180s budget
  alongside the payload:** cut the CTA entirely. Do not force an
  over-cap video, and do not splice an awkward partial sentence to make a
  CTA fit. The link/offer goes in the description or pinned comment
  instead — standard practice, already covered by the `youtube_metadata.md`
  requirement in `youtube-shorts`.
- A video with zero spoken CTA but a complete, well-told payload beats a
  video with a rushed or chopped CTA every time.

## Captions

Reuse the existing `youtube-shorts` caption rules (burn in, center third,
avoid bottom 25%, 99%+ sync) with two format-specific overrides:
- **Color:** `#33FF33` green with a black outline, matching the thumbnail
  (see Visual identity above) — not the generic white/black-outline
  default.
- **Chunking: one word at a time, not multi-word groups** (Randy's
  preference, 2026-07-24) — each word appears and disappears on its own
  rather than 2+ words sharing a caption window. This is the default for
  this format. **Escape hatch:** if word-by-word genuinely causes a real
  problem (e.g. the render pipeline can't handle the event volume, or
  timing data is too sparse/unreliable to place single words cleanly),
  fall back to small multi-word chunks and say so — Randy's own framing
  was "if it would cause a problem, skip that preference," not a hard
  requirement. In practice this is usually *easier* than multi-word
  chunking (see Production steps) — expect to use it by default, not the
  fallback.

## Required deliverable

Same as `youtube-shorts`: a description/metadata file, same session as
the render, no exceptions.

**Filename convention (added 2026-07-26, same rule as `youtube-shorts` —
applies here too, not just Shorts):** name the file after the video's
own title, not a generic name — `<video title, slugified>-description.md`.
Use the whole title if short (roughly under 5-6 words / 40 characters);
if longer, use just the first three words. Always ends in `-description`.
Lets Randy identify which video a file belongs to at a glance in a folder
listing, without opening it. Replaces the old generic
`youtube_metadata.md` name for anything created from 2026-07-26 onward —
existing files keep their old name, not renamed retroactively.

**Extended to every asset in the folder (added 2026-08-11, see
`youtube-shorts`'s "All assets in a video folder get topic-named"
section):** not just the description file — no generic `script.md`,
`SOURCES.md`, etc. anywhere in a video's project folder. Only exception is
`metadata.json` (machine-read, not opened for editing context).

**Standing first-comment template (locked 2026-07-26, same as
`youtube-shorts` — applies to every video type, no exceptions):** link
first, then the pitch, drafted into the metadata file as its own `##
First Comment` section (never merged into Description):
```
rskiles.com/operator

Grab The Operator Evidence Interviewer — (free prompt kit):
Uncover the Skills That AI Can't Replace
```
Randy posts it himself after upload — not automated. Full rationale:
`youtube-shorts` skill's own section on this.

**Location — single folder, no exceptions (locked 2026-07-24):**
the description/metadata file lives in the **same folder as every other
asset for that video** — the final render, thumbnail, captions, and
transcript — not a separate `content-engine/content/` location. This is
the actual per-video project folder from `[[project_video_production_folder_convention]]`
(`video-production/shorts/<slug>/` or `video-production/long-form/<slug>/`
depending on the length decision). One folder holds the whole video: copy
that one folder and everything needed for tracking, review, or re-upload
is there. This was a real gap — the location split wasn't decided when
video production was added to a pipeline that previously only produced
text and images, and it cost a real "wait, is this actually finished?"
moment before being caught and fixed the same session it was noticed.

## Production steps (what actually gets run)

1. `ffprobe` the source file for duration/resolution — confirm 9:16 before
   anything else.
2. `faster-whisper` (`base` model, CPU, `vad_filter=True`) for a first-pass
   segment transcript — read the whole thing before deciding anything.
3. Re-run with `word_timestamps=True`, scoped to the window around the
   candidate cut point, to find the exact clean clause boundary (see
   Gotchas — segment-level timestamps are too coarse for this).
4. `ffmpeg` trim to the decided cut point — no re-encode of the untouched
   portion if avoidable.
5. `ffmpeg` frame extraction for several thumbnail candidates near the
   hook — actually look at them (not just pick a timestamp blind) before
   choosing one.
6. Thumbnail text overlay (Pillow, using the real downloaded JetBrains
   Mono TTF — `@remotion/google-fonts` only fetches at Remotion runtime,
   it doesn't leave a static font file on disk for a plain PIL script to
   use).
7. Generate captions as a **real `.ass` file** (see Gotchas — do not use
   `subtitles=...:force_style=...`), with explicit `PlayResX`/`PlayResY`
   matching the video's actual pixel resolution, one `Dialogue` event per
   word (not per multi-word chunk — see Captions above), `PrimaryColour`
   set to `&H0033FF33` (green, ASS BGR order) with a black
   `OutlineColour`, then burn with the `ass=` filter.
8. **Verify the burn actually worked** — extract and look at frames from
   several points spread across the full duration (not one frame near the
   start), confirming captions are present, correctly synced to the
   transcript, positioned in the center-third, and not covering the face.
9. **Prepend the thumbnail — mandatory, no exceptions** (see Thumbnail
   formula above). Build a 0.5s freeze segment from the finished
   thumbnail image matching the main video's exact codec/resolution/
   framerate/audio params, concat it onto the front of the captioned
   video, and verify the seam (frame during the freeze + frame just after
   it ends) before treating the render as final.
10. Write the description/metadata file (`<title>-description.md` — see
    Required Deliverable above for the naming rule).
11. Generate a plain-text transcript (`<slug>_transcript.txt` — no
    timestamps, no styling markup, just the spoken words as readable
    prose) from the same word-level data used for captions. Build it from
    the already-generated `.ass`/caption data rather than re-running
    Whisper — the words are already there.

---

## Post-Approval Cleanup

**Trigger: only after Randy explicitly approves the final video AND
thumbnail.** Never automatic, never speculative, never run mid-review. If
a change is needed after approval, rebuild from the raw source — don't
try to resurrect a deleted intermediate.

**Always keep, never auto-delete:**
- The raw source footage. Irreplaceable — everything else can be
  regenerated from it, it can't be regenerated from anything.
- The approved final video and thumbnail.
- The plain-text transcript (`<slug>_transcript.txt`) — the primary reuse
  asset for a follow-up post or article. Randy's own reasoning
  (2026-07-24): a full transcript is raw material a different piece can
  be freshly distilled from; an already-compressed YouTube description
  has thrown away the texture/detail a good repurposed piece needs.
  Starting from a summary and expanding it back out tends to read thin
  and generic — starting from the full transcript and cutting a
  *different* angle from it doesn't.
- `youtube_metadata.md` — cheap to keep, and useful as a reference for
  how the story was already framed publicly, so a follow-up piece stays
  consistent with the YouTube version instead of quietly contradicting it.
- The caption source (`.ass`) — small, cheap, saves a re-transcription
  pass if the video itself is ever revisited. Lower priority than the
  transcript.txt, but no real cost to keeping it.

**Delete once the video + thumbnail are approved:**
- The trimmed-but-uncaptioned intermediate video. Fully redundant once
  the final captioned render exists — same trim, missing only the
  caption burn. If ever needed again, it's a one-line `ffmpeg` re-trim
  from the raw source using the cut timestamp already recorded in
  `youtube_metadata.md`, not something worth keeping a 200MB copy of.
- Any debug/test renders, thumbnail candidate frames that weren't chosen,
  and other scratch output from the production process. Zero reuse value.

---

## Pre-Upload Checklist (required, run before publish)

Run the `video-distribution-checklist` skill before this video goes live
— hook-in-first-second, length target (past 50s AVD, not under it), and
turning on YouTube's native Test and Compare tool. Run this after
Post-Approval Cleanup, before the video actually gets uploaded.

**If the format-freeze test is active** (see
`memory/project_format_freeze_test_2026-08-13.md`), add a row to
`content-engine/research/format_freeze_tracking.csv` at upload time —
date, platform, video_id (fill in once known post-upload), title, topic,
format, thumbnail style, length. The weekly `Format Freeze Stats Refresh`
scheduled task fills in views/likes/comments automatically after that,
but only for rows that already exist — a video never logged here never
gets tracked.

---

## Gotchas

- **Whisper's default segment-level timestamps are too coarse for a clean
  cut point** — segments can span 5–8 seconds and don't align to sentence
  boundaries. Always re-run with `word_timestamps=True` on the specific
  window around an intended cut before trimming, don't trim off
  segment-level boundaries alone. (Found 2026-07-24, `Red-Flags`.)
- **Unscripted CTAs run long by default.** The first real pass had a
  118-second payload (under budget on its own) followed by a 99-second
  CTA — nearly 2x the platform norm. Don't assume a CTA will be short
  just because it's "supposed to" be a quick plug; check the actual
  transcript timing before planning the cut. (Found 2026-07-24, `Red-Flags`.)
- **A cut that lands mid-list or mid-clause sounds worse than losing a few
  more seconds of cap margin.** In the first pass, the only in-budget CTA
  option ended on "...my war stories," trailing into a dangling list —
  rejected in favor of ending the video with zero spoken CTA instead of
  cutting there. When no clean boundary exists inside the budget, cutting
  less (or cutting the CTA entirely) beats cutting at an awkward point.
  (Found 2026-07-24, `Red-Flags`.)
- **`ffmpeg`'s `subtitles=file.srt:force_style='...'` filter silently
  fails to render visible text with no error message the moment
  `MarginV` is set to anything sized for real pixels (e.g. 700+ on a
  1920px-tall video).** The filter auto-scales SRT-derived subtitles
  against an internal low-resolution script coordinate space (not the
  video's real pixel dimensions), so a `MarginV` value that looks
  reasonable in real-pixel terms pushes the text far outside the visible
  frame — and libass fails silent, no warning, no error, just an empty-
  looking render. Small `MarginV` values (~100) partially work but the
  scale factor is unpredictable and the same setup also force-wraps short
  2-word captions onto two lines, again because of the same undersized
  internal canvas. **Fix: don't use `force_style` on an SRT input at all.
  Write a real `.ass` file** with an explicit `[Script Info]` block
  (`PlayResX`/`PlayResY` set to the actual video resolution, e.g.
  1080x1920) and a real `[V4+ Styles]` line with real-pixel `Fontsize`/
  `MarginV` values, then burn with the `ass=file.ass` filter instead of
  `subtitles=`. This gives exact, predictable control and was the only
  approach that worked reliably. (Found 2026-07-24, `Red-Flags` — cost
  three full re-renders and roughly a dozen bisection tests before the
  root cause was found.)
- **Always verify a caption burn by sampling frames across the ENTIRE
  duration, not just one frame near the start.** A single early spot-check
  can pass by accident (or fail by accident, e.g. landing in a genuine
  gap between two caption chunks) — sample at least 5-6 points spread
  across the full video before trusting a render. (Found 2026-07-24,
  `Red-Flags`.)
