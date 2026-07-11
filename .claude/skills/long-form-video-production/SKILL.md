---
name: long-form-video-production
description: End-to-end pipeline for producing a long-form (16:9) HeyGen-avatar YouTube build video — title/hook/script through HeyGen generation, screen-recording SRT, motion-graphic overlays, and CapCut assembly. Use when Randy says "build a new video", "let's make the next long-form video", "start a video project", or asks to produce assets for a build/tutorial-style YouTube video with his HeyGen avatar. Chains the youtube-script skill (writing) with the HeyGen/Remotion/CapCut asset pipeline (production) into one repeatable process. Not for Shorts — see youtube-shorts / shorts-script for those.
---

# Long-Form Video Production Pipeline

One entry point for the whole process, so no step depends on remembering
what happened in a past session. Built 2026-07-10 after two scripts were
lost mid-production because they only ever existed in chat — every step
below writes to a file before moving on.

## Stage 0 — Create the project folder FIRST

Before writing a single word of script, create:
```
video-production/long-form/<slug>/
  heygen/  overlays/  srt/  screen-recordings/  final/
```
This folder is portable and tool-free — no `.tsx` source, no skill files,
nothing but the video's own assets, so it can be copied wholesale to a
local CapCut machine. See `[[project_video_production_folder_convention]]`.

## Stage 1 — Title, hook, script structure

Use the **youtube-script** skill for this stage — don't duplicate its rules
here. Read (in order): `content-engine/CONTENT_PUBLISHING_RULES.md`,
`knowledge/me/youtube-voice.md`, `knowledge/me/video-hook-types.md`,
`knowledge/brand/keyword_research.md`. Output: the 6-segment
Friction-Hook→Outro structure, spoken-voice narration.

Write the finished script straight into `<slug>/script.md`, split into
scenes/segments matching what will actually be submitted to HeyGen as
separate jobs. Include a title (even a working one) and note format
(long-form, 16:9) at the top. Also write `<slug>/metadata.json` — see the
folder-convention memory for the schema.

**Do not proceed to Stage 2 until script.md exists on disk.** A script only
in the conversation is not saved — this is the exact failure this skill
was built to prevent.

## Stage 2 — HeyGen avatar/voice — verify before submitting, don't trust cached names

**Known trap:** a saved name like "Randy_DigitalTwin_v2" may refer to the
*voice*, not the *avatar* — they can share a name. Before submitting
anything, confirm live:
1. `mcp__heygen__get_current_user` — confirm account + credit balance.
2. `mcp__heygen__list_avatar_groups` (ownership: private) — list avatar
   groups.
3. `mcp__heygen__list_avatar_looks` (ownership: private) — find the actual
   `avatar_id` (a specific look inside a group), not just the group name.
4. `mcp__heygen__list_voices` (type: private) — find the `voice_id`,
   confirm it matches the avatar's `default_voice_id` if you want them paired.
5. Note the avatar's native orientation (portrait/landscape) from the look's
   `image_width`/`image_height` — ask Randy whether to match it or force the
   opposite aspect ratio before submitting (this changes the whole
   downstream CapCut canvas).

Submit each scene via `mcp__heygen__create_video_from_avatar` with the
confirmed `avatarId`/`voiceId`. **Always confirm settings with Randy before
submitting** — this costs real credits (see `feedback_heygen_ask_before_submit`).
Consider submitting Scene 1 alone as a test before batch-generating the
rest, so a framing/lip-sync problem doesn't cost credits across every scene.

Poll `mcp__heygen__get_video` until `status: completed`, download each mp4
with `curl`, and save directly into `<slug>/heygen/`.

## Stage 3 — Screen recording + SRT

Randy records the actual screen-capture footage for the parts of the video
that aren't the avatar talking, and assembles a rough cut in CapCut
(avatar clips + screen recording, in whatever order the script implies).

Once that rough cut exists, generate captions in CapCut (Auto Captions →
export as .srt, unchecking video export so only the caption file is
produced) and save it into `<slug>/srt/`. This SRT is the master timeline
for Stage 4 — read every caption's start/end time directly from it, never
estimate.

**Two different situations you'll find in the SRT — check which one applies:**
- **Gap-based:** real silence exists between caption blocks where the
  screen recording plays without narration. Build motion graphics sized to
  fill those exact silent durations.
- **Continuous narration (found on the file-organizer-build video):** no
  meaningful silence exists — narration runs wall-to-wall. In this case
  build a **persistent overlay system** (a card/panel that evolves with the
  story) synced to caption *content*, not caption *gaps*. Compute this by
  diffing every consecutive caption's end/start time — if gaps are all
  under ~1s, you're in the continuous case.

## Stage 4 — Overlay storyboard + Remotion render

Design a segment-by-segment storyboard: `[start] – [end]: visual
description`, timed directly off SRT caption boundaries (not estimated).
Get Randy's sign-off on the storyboard before rendering anything.

**Spatial rule:** confirm where Randy appears in frame (this varies per
video — e.g. right 25% in this one) and keep all graphics out of that zone.

**Render technique:** motion graphics render on **pure `#00FF00`**
background (chroma-key), composited in CapCut exactly like the HeyGen
avatar layer already is. Never use green tones inside the graphic itself.

**Build with Remotion — never VidIQ's render tool** (see
`[[feedback_remotion_not_vidiq]]` — hit a hard credit wall the one time it
was tried). Reuse `video-production/remotion/src/FileOrganizerShared.tsx`
as the pattern for a new shared-style file per video series: exported
`COLORS`, card geometry constants, `SpringIn`/`Divider`/`Pill`/`TraceLine`
animation helpers. Each segment gets its own component file exporting the
component + a `_DIMS` constant (`W`, `H`, `FRAMES`), registered as a
`<Composition>` in `Root.tsx`. Match frame counts to the SRT segment
duration (`seconds * 30`, at the project's standard 30fps).

Render each with `npx remotion render <CompositionId> out/<Name>.mp4` from
`video-production/remotion/`, then copy the output into `<slug>/overlays/`
— never leave it referenced only in `remotion/out/`, since that breaks the
project folder's portability.

## Stage 5 — CapCut assembly

Randy assembles in CapCut: HeyGen avatar layer (chroma-keyed) + background
(screen recording or Randy's chosen image) + overlay layer (chroma-keyed,
confined to the non-avatar zone) + any audio. Final export goes in
`<slug>/final/`.

Update `metadata.json`'s `status` field as the project moves through
in-production → ready → published, and fill in `title`/`publish_date` once
locked.

## Stage 6 — Hero/background image + thumbnail

Two SEPARATE images, not one — they have opposite requirements:

- **In-video background** (behind the avatar, seen full-size): detail-rich is
  good — legible file names, readable text, busy scenes all work because the
  viewer has time and screen size to take it in.
- **Thumbnail** (seen at ~120-150px wide in a mobile feed, half-second glance):
  needs the opposite — one dominant expressive face, huge bold text, minimal
  fine detail. Fine text that's legible in the in-video version will NOT
  survive thumbnail compression. Generate these as two separate images, not
  one image doing both jobs.

**Tool:** `content-engine/generate_hook_background.py` — a 16:9 (1920x1080)
counterpart to `generate_short_card.py`/`generate_carousel_images.py` (reuses
their `generate_image()`/`load_dotenv_env()` helpers, same `--quality low`
default rule). Generates a textless photographic scene; bake any text on
top with Pillow as a separate step afterward (same two-pass pattern as the
Shorts cards) — don't rely on the AI model to render legible text directly,
it garbles filenames/words unreliably above a handful of characters.

**Copyright:** never reproduce a recognizable copyrighted character (e.g.
Bill Lumbergh/Office Space) even via AI generation — real legal and
image-gen-policy risk. Build an *original* archetype that evokes the same
trope instead (generic corporate-manager visual cues, an original line in
the same rhythm) — gets the same recognition without reproducing the IP.

**Recurring character — "the operator":** a consistent visual identity used
across LinkedIn article images (`04_operator.png` in several `content-engine/
pending/` article folders) and this video's assets: man in his 50s, short
gray/salt-and-pepper beard, dark polo shirt, IT-office/server-room setting.
Keep new generations consistent with this description rather than
re-deriving it from scratch each time.

**Title/thumbnail-text pairing:** once the video title is locked, thumbnail
text should complement it, not repeat it — title carries the stakes/hook,
thumbnail text is the shortest possible resolution/punch (e.g. title "Your
Company Has a Truth Problem" + thumbnail text "AI FIXED IT"). Don't lock
thumbnail text before the title, and don't finalize it as pure duplication
of the title.

## Stage 7 — YouTube publish metadata (title, description, tags)

Write to `<slug>/youtube_metadata.md`, then lock the final title into
`metadata.json`.

**Title:** run through the `youtube-script` skill's title fact-check rule —
verify every claim in the title against the actual script/description
before presenting it as an option. A curiosity-gap title shape is only
valid if the specific claim inside it is true of the story being told.

**Description SEO rules:**
- **First sentence carries the most search-ranking weight** — lead with the
  primary keyword (pull from `knowledge/brand/keyword_research.md`), not
  the CTA. CTA goes in the second sentence — still inside the visible
  portion before YouTube's "Show more" cutoff, so it doesn't lose
  visibility, it just isn't in the highest-SEO-value position.
- **CTA:** pull from `knowledge/products/lead-magnets/Steel-One-Sentence
  Visible CTAs.md`, matched to the video's awareness stage per that file's
  rotation table (top 4 to lead with: #8, #2, #5, #4).
- **Chapters/timestamps:** include `0:00 Label` format lines — YouTube
  auto-generates chapters from these (first one must start at 0:00, need
  at least 3), and they measurably improve watch time + search surfacing.
  Recalculate against the actual final CapCut cut, not the draft script
  timing.
- **Hashtags:** cap at 3 in the description — YouTube only displays the
  first 3 above the title, more than that in-body doesn't add value there.
- **Tags:** pull from `keyword_research.md`'s lowest-competition targets
  first (e.g. `sysadmin` comp 22, `enterprise ai implementation` comp 16),
  then content-specific secondary tags. ~15-20 total, stay under YouTube's
  ~500-character combined limit.

## Gotchas

- HOT_STATE.md dual-copy rule applies to any resume-state written mid-project
  — see `[[feedback_hot_state_dual_copy]]`.
- If files get moved between folders (e.g. during a reorg like the one that
  created this skill), any CapCut project already referencing the old paths
  will show offline media — warn Randy before moving anything mid-edit.
- Avatar orientation may not match the intended video format — always check
  before choosing aspect ratio, don't assume from the avatar's name.
- **Title generation** (Stage 1) needs a fact-check pass against the actual
  script/description before presenting — see the fact-check rule and Gotcha
  entry in the `youtube-script` skill (a suggested title once misattributed
  "AI" to a story event that had no AI involvement, caught by Randy).
