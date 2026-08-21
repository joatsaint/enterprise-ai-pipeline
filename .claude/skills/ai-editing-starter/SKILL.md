---
name: ai-editing-starter
description: Turn a raw talking recording (screen capture, voice memo, camera file) into a clean cut — silences compressed, stumbles removed, captions generated — using Claude Code, ffmpeg, and Whisper. You approve the cut list; it does the cutting.
---

> **Solves:** the first and slowest part of editing — cutting dead air, false starts, and repeated takes out of a raw recording, then generating captions that match the finished cut.
> **Does NOT cover:** uploading, thumbnails, titles, or publishing. This is the cut pass — the part you'd otherwise scrub through by hand.
> **Failure mode if misapplied:** running it on an already-edited file (it will try to compress pauses that are intentional). Feed it raw recordings.

# AI Editing Starter — the cut pass

You talk. It cuts. This skill walks Claude Code through the same editing core used in production on a real YouTube channel: transcribe → propose a cut list → you approve → execute → **verify every splice by listening back with fresh ears** → captions.

## Prerequisites (check these first, tell the user if one is missing)

- **ffmpeg** on PATH (`ffmpeg -version`) — macOS: `brew install ffmpeg`
- **Node 18+** (`node --version`) — used for `npx hyperframes transcribe` (local Whisper, no API key)
- A raw recording: `.mp4`, `.mov`, `.m4a`, `.wav` — anything ffmpeg reads
- No API keys. Nothing leaves the machine.

## Step 1 — Intake

The user drops a file and says some form of "cut this." Confirm the file exists and probe it:

```bash
ffprobe -v error -show_entries format=duration -show_entries stream=codec_type,width,height -of default=noprint_wrappers=1 "<recording>"
```

Create a working folder `edit/` next to the recording. Everything generated goes there.

## Step 2 — Transcribe (word-level, local)

```bash
npx --yes hyperframes transcribe "<recording>" --model large-v3
```

This writes `transcript.json` — a word array with start/end times — next to the input. Move it into `edit/`.

- **Use `--model large-v3`.** The default small model garbles real-world audio and the cut list inherits every error.
- On files longer than ~4 minutes, transcribe in **90–100 second chunks** with 2s overlap and stitch (long-form Whisper hallucination-loops: it will repeat one sentence with fake timestamps — a transcript whose word count looks too low for the duration is the tell).

## Step 3 — Build the cut list (propose, don't execute)

Three finds, in order:

**a. Dead air.** Run silence detection and list every gap over 1 second:

```bash
ffmpeg -i "<recording>" -af silencedetect=noise=-32dB:d=1.0 -f null - 2>&1 | grep silence_
```

Plan: keep ~0.6s of every long gap (cut from `start+0.35` to `end−0.25`). Real speech needs breath — never cut a silence to zero.

**b. Restarts and stutters.** Scan the transcript for adjacent repeated runs of 3+ words within a few seconds ("I give it to— I give it to…"), and for restart markers: *"hold on," "let me redo," "I'm sorry," "wait," "scratch that."* On a restart, the LAST take is almost always the keeper — plan the cut from the start of the abandoned take to the start of the final take.

**c. The bracket trim.** Recordings start with setup noise and end with a reach for the stop button. Trim to the first and last spoken words, ±0.3s.

**Then present the cut list as a table** — start, end, duration, what's being removed, quoted text — with total time saved. **Wait for approval.** The human approves the cut; the machine executes it. Adjust anything they flag.

## Step 4 — Execute the cut

Extract every KEEP range with tiny edge fades (kills clicks at joins), then concatenate:

```bash
ffmpeg -y -v error -ss <in> -t <dur> -i "<recording>" \
  -af "afade=t=in:d=0.008,afade=t=out:st=<dur-0.008>:d=0.008" edit/keep_001.wav
# ...one per keep range, then:
ffmpeg -y -v error -f concat -safe 0 -i edit/concat.txt -c pcm_s16le edit/cut.wav
```

For video sources, do the same with `-c:v libx264 -crf 18` per segment and concat — or cut audio first, lock it, then conform the picture.

## Step 5 — Verify every splice (the step everyone skips)

A green ffmpeg exit is not a clean edit. **Re-transcribe 8 seconds around every join and read the text:**

```bash
# for each join time J in the cut file:
ffmpeg -y -ss <J-4> -t 8 -i edit/cut.wav edit/join_check.wav
npx --yes hyperframes transcribe edit/join_check.wav --model large-v3
```

A clean join reads as a normal sentence. A broken one shows a half-word or a stutter that wasn't in either source take — that means a cut point clipped into a word; move the boundary to the word timing from the transcript and re-cut that one join. (Real example from production: a cut landed 0.7s late and manufactured a stutter — "I was us— I was using" — that neither take contained. The re-transcription caught it; nothing else would have.)

## Step 6 — Captions

Build an `.srt` from the transcript of the FINISHED cut (Step 5's full re-transcription, or re-run Step 2 on `edit/cut.wav`): group words into lines of ≤40 characters, break on gaps >0.7s. Number sequentially, `HH:MM:SS,mmm` timestamps.

## Step 7 — The ship gates (before you call it done)

The cut isn't finished because it plays. Run four checks and answer each with a TIMESTAMP or a HALT — never a vibe:

1. **Opening gate:** the cut OPENS on the thing the title promises — it is on screen from the first second, with nothing in front of it. Name what's at 0:00 and confirm it's the promise. No agenda, no throat-clearing, no setup; if anything precedes the payoff, cut it.
2. **CTA gate:** if the video wants an action (subscribe, download, link), it appears — spoken or on-screen — inside **0:30**, dry and tied to the content. Check the first 30s of the captions; if it's not there and no overlay covers it, say so.
3. **Demo gate:** name the timestamp where the thing the video is about is **on screen doing its job** — running, producing output. A screenshot of it is not evidence. No timestamp → the cut isn't done.
4. **Splice gate:** Step 5 ran on every join, and you read the text. Green exit codes don't count.

Any gate you can't answer → HALT and say which one, instead of delivering. Gates, not magic.

## Step 8 — Deliver

Hand back, with durations: `edit/cut.wav` (or `.mp4`) · `edit/captions.srt` · the cut list as `edit/cutlist.json` · one line of honest math: raw length → cut length, N cuts, M seconds of dead air removed.

## Notes for the person running this

- The whole pass is local. Your recording never uploads anywhere.
- Approve the cut list before anything is destructive — and nothing here overwrites your original file.
- If the result sounds choppy, the silence floor is too aggressive: raise `d=1.0` to `d=1.4` and re-run Step 3a.
