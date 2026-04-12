# GUIDE.md — YouTube Transcript Downloader: Upgrade Guide
## Plain-English Step-by-Step

---

## Where You Are Right Now

You have a working project. You paste a YouTube URL, it downloads the transcript
into a folder. That's Phase 0 — done and verified.

This guide takes you from there to a full knowledge base with daily briefings.

---

## Phase 1 — Token Efficiency + Markdown Conversion

### What you're doing
Right now the transcripts are probably raw text — full of "um", timestamps, repeated
words, and filler. Before we build anything else, we clean that up. Cleaner transcripts
mean Claude uses fewer tokens to process them, which saves money and gets better answers.

We're also converting everything to Markdown (.md) files so they're structured,
searchable, and readable.

---

### Step 1: Copy CLAUDE.md into your project root

**What:** Drop the CLAUDE.md file from this package into:
```
C:\Users\joatsaint\Desktop\On Desktop HP-CapCut Network Share\Claude Code My Projects\youtube-downloader\
```

**Why:** Claude Code reads this every session. It tells Claude what the project is,
what's already done, and what the rules are. Without it, Claude starts from scratch
every time and makes mistakes.

**Checkpoint:** CLAUDE.md is in the project root folder.

---

### Step 2: Paste the Phase 1 Upgrade Prompt into Claude Code

**What:** Open Claude Code in your project folder. Paste the scaffold prompt
(the third file in this package). Let it run.

**What gets built:**
- `src/downloader/transcript_fetcher.py` — cleaned up with token optimization
- `src/converter/to_markdown.py` — converts raw transcript to .md
- Updated folder structure under `/transcripts/`
- Updated `requirements.txt` if new packages are needed

**Checkpoint:** Run your existing single-URL download and confirm the output
is now a .md file instead of raw text.

---

### Step 3: Test the Markdown output

Download one video you already have and compare:
- Old output: raw transcript text, messy
- New output: clean .md file with title, date, channel name as headers

**Checkpoint:** The .md file looks clean and readable when you open it in VS Code.

---

## Phase 2 — Channel Download + Incremental Mode

### What you're doing
Instead of pasting one URL at a time, you'll be able to point Claude Code at
an entire YouTube channel and say "get everything" or "get what's new since last time."

---

### Step 4: Create channels.json

**What:** This is your channel registry. A simple list of channels with their URL,
name, and which group they belong to (bitcoin-macro, claude-code, certifications).

**Example entry:**
```json
{
  "name": "Channel Name Here",
  "url": "https://www.youtube.com/@channelhandle",
  "group": "bitcoin-macro",
  "active": true
}
```

Fill in your channels as you're ready. Start with just one or two to test.

**Checkpoint:** channels.json exists and has at least one channel entry.

---

### Step 5: Test full channel download

```bash
python src/main.py download --channel "Channel Name" --force-full
```

This pulls every available transcript from that channel and saves them as .md files
in the right folder. Expect this to take a few minutes for large channels.

**Checkpoint:** /transcripts/[group]/[channel-name]/ is populated with .md files.

---

### Step 6: Test incremental download

Run the same channel download without --force-full:

```bash
python src/main.py download --channel "Channel Name"
```

It should only download videos not already in your local folder.

**Checkpoint:** Running it twice in a row — second run says "0 new videos."

---

## Phase 3 — Knowledge Base + On-Demand Q&A

### What you're doing
Now that you have a folder full of clean .md transcripts, you build an index
so Claude can search across all of them to answer your questions.

---

### Step 7: Build the index

```bash
python src/main.py index
```

This scans every .md file in /transcripts/ and builds a searchable index
at knowledge_base/index.json. Run this any time you add new transcripts.

**Checkpoint:** knowledge_base/index.json exists and has entries.

---

### Step 8: Test on-demand Q&A

```bash
python src/main.py ask "What are the top Bitcoin price predictions for Q3 2026?"
```

Claude searches the index, pulls relevant transcript sections, and answers
based only on what's in your downloaded content — not the open internet.

Try a group-specific question:
```bash
python src/main.py ask --group bitcoin-macro "What is the consensus on Fed rate cuts?"
```

**Checkpoint:** You get a coherent answer that cites which channel/video it came from.

---

## Phase 4 — Daily Digest + Scheduler

### What you're doing
Every morning at a time you set, the system automatically checks for new videos
across all your channels, downloads any new transcripts, and sends you a
grouped summary: bitcoin-macro first, then claude-code, then certifications.

---

### Step 9: Test the digest manually

```bash
python src/main.py digest --all
```

Output goes to knowledge_base/digests/YYYY-MM-DD_digest.md

Open it. It should read like a morning briefing — new content from each group,
key points summarized, no fluff.

**Checkpoint:** The digest is readable and useful without watching any videos.

---

### Step 10: Set up Windows Task Scheduler

Claude Code will generate XML files for Task Scheduler — same approach used
for the arbitrage scanner. You'll register them with one PowerShell command.

The scheduler will:
- Run the incremental download for all channels at 6:00 AM
- Run the digest generator at 6:30 AM
- Leave the .md briefing file ready when you sit down at your desk

**Checkpoint:** Task Scheduler shows the tasks as active. Run them manually
once to confirm they fire correctly.

---

## You're Done When...

- Paste a URL → get a clean .md transcript (Phase 1) ✓ target
- Point at a channel → get all transcripts, new ones only on repeat runs (Phase 2)
- Ask a question → get an answer sourced from your own transcript library (Phase 3)
- Wake up → briefing is already waiting (Phase 4)

---


## The Orchestration Layer — Why It Matters

This is the concept that separates hobby projects from production systems,
and it's one of the things the best Claude Code practitioners do first.

**The problem without it:** main.py downloads a transcript, calls the cleaner,
calls the converter, saves the file. If the converter crashes halfway through,
you have a partial file, no log entry, and no idea what happened. The next run
tries to download it again. Chaos.

**The solution:** orchestrator.py sits between main.py and every module.
It owns the sequence, the state, and the failure decisions. Each module does
one job and reports back. The orchestrator decides what happens next.

Think of it like an air traffic controller. The planes (modules) don't talk
to each other — they all talk to the tower (orchestrator). The tower knows
where everything is and what to do when something goes wrong.

**What this means for you practically:** When Phase 1 scaffold runs, Claude
Code will build orchestrator.py as the central coordinator. You will not
call transcript_fetcher.py directly. You call the orchestrator, it calls
transcript_fetcher.py, gets the result, and passes it to to_markdown.py.
If transcript_fetcher.py fails, the orchestrator retries it once, logs
the failure, and moves on — without you having to do anything.

**The run summary:** At the end of every run, the terminal prints a clean
table showing exactly what succeeded, what was skipped, what failed, how
many tokens were saved, and how long it took. No more guessing whether
something worked.

---

## Rules You Don't Break

1. **Don't skip Markdown conversion.** Raw transcripts in the knowledge base break Q&A quality.
2. **Don't mix groups.** Bitcoin analysis and Claude Code tutorials never go in the same index query.
3. **Always run incremental before full.** Full download is for first-time setup only.
4. **Index after every download session.** Stale index = stale answers.
5. **Don't feed the digest to Claude without cleaning first.** Token waste = money waste.
6. **Back up /transcripts/ to your NAS after every bulk download session.** It's your research asset — treat it like one.

---

## Troubleshooting — Common Problems and Fixes

### "No transcript available" error
**What it means:** The video has no captions — either auto-generated or manual.
**Fix:** Nothing to do. The tool logs it and skips it. Check logs/error_log.json
to confirm it was recorded. Some older videos and many live-stream archives
have no transcripts available.

### Wrong Python version
**What it means:** You're running Python below 3.10.
**Fix:** Open WSL terminal and run `python --version`. If it's below 3.10,
run `python3 --version`. Use whichever points to 3.10+. Update your run
commands to use `python3` if needed.

### Package not found / ModuleNotFoundError
**What it means:** A required package isn't installed in your environment.
**Fix:** Run `pip install -r requirements.txt` from the project root in WSL.
If the error persists, run `pip install [package-name]` for the specific
missing package and then add it to requirements.txt.

### YouTube rate limit / 429 error
**What it means:** You've made too many requests too fast. YouTube is throttling you.
**Fix:** Stop the tool. Wait 5-10 minutes before running again. The tool will
auto-pause 60 seconds on a 429 and retry once — if it fails again it stops
automatically. Don't run bulk downloads back-to-back on the same session.

### Transcript downloaded but file is empty
**What it means:** The cleaning pipeline stripped everything — usually means
the transcript was timestamps-only with no real content.
**Fix:** Check the raw transcript source. If the video is auto-captioned in
a non-English language, the cleaner may over-strip it. Check logs/error_log.json
for details. Delete the empty file and skip that video.

### Category suggested wrong
**What it means:** The keyword scorer misread the title or channel name.
**Fix:** Type 1 or 2 to override when prompted. The override gets logged in
download_log.json. After 5+ overrides on the same channel, add that channel
to channels.json with the correct group — future downloads will route correctly.

### Claude Code loses project context between sessions
**What it means:** CLAUDE.md isn't in the project root, or Claude Code wasn't
opened from inside the project folder.
**Fix:** Confirm CLAUDE.md is in the project root. Open VS Code, then open
the terminal and navigate to the project folder before launching Claude Code.
Claude Code reads CLAUDE.md from whatever folder it's opened in.

### Git accidentally staged .env
**What it means:** .env is showing up in `git status` as a file to be committed.
**Fix:** Stop immediately. Do not run `git commit`. Run:
```bash
echo ".env" >> .gitignore
git rm --cached .env
```
Then verify .env no longer appears in `git status` before committing anything.

---

## Backup Reminder

After any session where you download 10 or more new transcripts, copy your
/transcripts/ folder to your NAS. The tool will remind you, but don't wait
for the reminder — your transcript library is the most valuable output of
this entire project. It cannot be regenerated if lost without re-downloading
everything from YouTube, and some videos may be deleted or made private by then.
