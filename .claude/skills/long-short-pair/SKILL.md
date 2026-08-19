---
name: long-short-pair
description: Turn one raw, unscripted, landscape talking-head take into two outputs — a long-form YouTube video and a Short that links back to it. Use this skill when Randy hands over raw landscape footage and wants both a long-form video and a Short cut from it, or when he asks you to apply "the long-short pair" or "the raw editing rule" to a new video. Built 2026-08-18 from a real raw-vs-final comparison, not designed in the abstract.
allowed-tools: Read, Edit, Write, Bash, Grep, Glob
---

# long-short-pair

Use this skill for raw, unscripted, **landscape** talking-head footage.
It differs from `short-walk-and-talk`, which covers vertical footage and
produces one output — a Short or a long-form video, not both. This skill
always produces both outputs from the same raw source. The Short links
back to the long-form video; it doesn't stand alone.

**How this skill was built:** on 2026-08-18, transcribe and diff two raw
takes (`PXL_20260815_150153844.mp4`, 6:50; `PXL_20260815_151013140.mp4`,
1:40) against their published long-form video (6:12) and Short (2:30) —
"AI Won't Take Your Job. But Someone Who Uses It Will,"
`docs/Youtube My Channel/`. The rules below come directly from that diff.

## Run the pipeline as staged checkpoints, not one pass

Process a raw video in stages, and get Randy's approval at each one before
you move to the next. Track every cut and overlay in an edit decision list
(EDL) — a JSON file of timestamps and operations — instead of committing
to a rendered file at each stage. This keeps review fast and avoids a full
re-render every time Randy approves a step.

1. **Remove pauses.** Find every gap over 0.7 seconds from the word-level
   timestamps (the same data this skill already pulls for card timing) and
   list them as cuts in the EDL.
   - **Add a 0.5-second buffer before any cut that starts right after the
     last word in a clip.** Whisper's word-end timestamp can land early,
     especially on a clip's final word — confirmed 2026-08-18 when a
     trailing-silence cut clipped the tail end of "AI" in a real clip.
     Push the cut point 0.5 seconds later than the raw timestamp so the
     word finishes cleanly before the pause starts.
2. **Render a preview with stream-copy**, not a full encode
   (`ffmpeg -c copy`). Stream-copy repackages the existing footage instead
   of re-encoding it, so a preview takes seconds even on a long video. Use
   this preview for every review checkpoint, not the final file.
3. **Get Randy's approval on the preview.** Only add the next stage's cuts
   and overlays to the EDL after he approves the current one.
4. **Repeat for each later stage** (prompt cards, captions, thumbnails,
   whatever the pipeline eventually covers) — each one adds to the same
   EDL and gets its own stream-copy preview for review.
5. **Render the final file once**, with full-quality settings, only after
   Randy approves every stage. This is the only step that pays the real
   encode-time cost — every review before it stays fast.

**Why this matters:** a full-quality re-encode is the slow, expensive
part of this pipeline. Checkpointing on stream-copy previews instead of
final renders means Randy can review and correct each stage without
paying that cost more than once.

**Target end state, not yet built:** hand over one raw video, get back a
finished long-form video, a finished Short, and every asset (captions,
prompt cards, thumbnail, metadata) — one review at the end, not one per
asset. This staged, EDL-based pipeline is how you get there without
re-rendering at every step along the way.

## Set the length from the content, not a target

Aim for 8-10 minutes on the long-form video and about 2 minutes on the
Short, but treat these as starting points, not fixed durations. Let the
content set the real runtime. Don't pad a video to reach a target, and
don't cut it short to hit one.

## Build the long-form video close to the raw take

Keep the long-form video close to a straight edit of the raw footage.
Concatenate the raw clips in order and trim dead air, pauses, and false
starts, but don't cut content. In the reference example, the long-form
video kept nearly all of the raw transcript's words — it only tightened
the pacing. Treat the long-form video as the full-context version: keep
every story, example, and analogy from the raw footage.

- Don't add captions to the long-form video.
- Add a screen overlay only when the viewer needs it — a prompt, a URL,
  or other text that helps them follow along. Use overlays for that one
  purpose, not as a captioning system. Build the overlay as a prompt card
  (see below), not as a caption-style treatment.
- Fix obvious editing mistakes using your own judgment — a bad cut, a
  repeated line, a technical glitch. Don't preserve an error just because
  a prior reference video had it.

## Build the prompt card overlay

Use this treatment whenever a video shows the viewer a prompt to copy —
in a long-form video or a Short. It's a distinct overlay style, separate
from burned-in captions, confirmed 2026-08-18 against a real published
example ("How I Went From Almost Fired to Indispensable,"
`docs/Youtube My Channel/`, sampled at 90-165 seconds).

- Cut away from the talking-head footage to a full black card. This
  isn't a semi-transparent overlay on top of the video — it replaces the
  frame while the narration continues as voiceover.
- Space these cards roughly once a minute through the video. Randy's own
  pacing rule, confirmed 2026-08-18 on a real edit: don't save the
  technique for a single prompt-heavy section, spread it through the
  video wherever the script gives you a line worth carding.
- Set the text in bright green, left-aligned, in a bold rounded
  geometric sans-serif (not a monospace font — measured against the real
  example, the closest brand match is the same phosphor green used
  elsewhere in this project; sample the source video's own pixels if you
  need an exact hex before you commit to one).
- Reveal the prompt in short line groups. Build the card up one phrase or
  sentence at a time instead of dropping the whole prompt on screen at
  once, and leave a blank line between groups.
- Keep this treatment reserved for prompts the viewer would copy and
  paste. Use the smaller, targeted overlay style (a single line, a URL)
  for anything else that doesn't warrant a full card.

## Build the Short from the long-form video, not from scratch

Cut the Short from the finished long-form video. Don't reshoot it or
write it as a separate script. In the reference example, every line that
survived into the Short was a thesis statement or a repeatable framework
line. Every line that got cut was a concrete story, example, or analogy.

**Cut these every time:** war stories and extended examples or analogies.
The reference example cut a USPS/Amazon delivery-pivot story, a
Kodak/film-kiosk example, a newsletter-curation walkthrough, a golf-cart/
robot-caddy aside, and a full movie-scene anecdote. All of them stayed in
the long-form video and none made the Short.

**Keep these every time:** the hook, the core thesis statement, any
framework or "how to think about this" line, and the closing call to
action.

**One exception:** keep a concrete example if it directly supports the
core thesis rather than standing on its own. The reference example kept a
short robot/new-hire-training bit because it reinforced the main claim —
not because every example gets a pass. Judge each one: does it add
evidence, or does it just decorate the point?

**Structure the Short in the Julia McCoy format:** hook, core problem,
solution or framework, payoff, one action step, and a call to action.
This structure comes from the 2026-08-17 brain-dropping script-conversion
example — see the `project_genx_game_show_format.md` memory for the
reference script.

**Frame the Short as a teaser.** Its job is to send the viewer to the
long-form video for the full picture, not to cover the topic on its own.

- Add captions to the Short. Follow the burn-in and timing rules in the
  `youtube-shorts` skill. The long-form video is the one that skips
  captions, not the Short.

## Correct the transcript before you generate captions

CapCut's automatic transcription makes real errors. In the reference
example, it rendered "Grok" (Elon Musk's AI) as "GROC" or "rock bot," and
"I, Robot" (the movie) as "Eye Robot." Proper nouns and titles carry the
highest risk of a misread. Proofread the transcript against what was
actually said and correct it before you generate any captions from it.
Don't treat CapCut's raw transcript as final.

## Gotchas

(None yet. This skill is based on a single worked example — add entries
here after the next real production pass.)
