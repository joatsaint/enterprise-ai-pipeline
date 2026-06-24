# CLAUDE.md — YouTube Transcript Downloader & Knowledge Base
**Version: 1.8** — Knowledge base fully operational: indexer.py, query.py, digest.py built and verified working (1,014 transcripts, 52 channels, 4 groups). Phase 4 is complete — Windows Task Scheduler tasks "YouTube Transcript Digest" (07:00 daily) and "YouTube Pipeline" (00:09 weekly, by design — refreshes comments on a 7-day cadence) are registered, enabled, and confirmed running successfully (LastTaskResult: 0, verified live 2026-06-09).

## Session Start Protocol

At the start of every new session, before doing any work:
1. Ask Randy to share `memory/SESSION_LOG.md`
2. Do not proceed until the session log has been read
3. Confirm what session number this is and what was left outstanding from the previous session

If Randy forgets, prompt him: "Before we start — can you share the SESSION_LOG.md from your memory/ folder?"

---

## Project Identity

This project is a commercial research engine that downloads YouTube transcripts,
extracts audience pain points and questions, and feeds a PDF content business
targeting AI career seekers. Transcripts are converted to structured Markdown,
indexed into a searchable knowledge base, and analyzed by Claude to produce
paid PDF guides, free lead magnets, and daily research digests.

See MASTER_PLAN.md for the full business pipeline and stage roadmap.
See PROJECT_CONTEXT.md for ICP, offer definition, value proposition, and growth strategy.

Project path: C:\Users\joatsaint\Desktop\On Desktop HP-CapCut Network Share\Claude Code My Projects\youtube-downloader

Claude is the primary architect and code generator.
The human operator (Randy) reviews, approves, and deploys.
Before writing any code for a build of meaningful size (a new module, pipeline, or
skill — not a one-line fix), interview Randy instead of guessing and waiting for a
correction: work through the core problem, who it's for and who it's explicitly
not for, and the key decisions at each step, then summarize that back as a short
plan before writing code. For small/obvious edits, the lighter "state assumptions
explicitly" version is still fine.

---

## Skill Maintenance — Gotchas Section

Every skill under `.claude/skills/*/SKILL.md` carries a `## Gotchas` section at
the bottom. When a real session surfaces an edge case, a stylistic quirk, or
anything that took back-and-forth to get right, append it there immediately
(don't wait to be asked) so the same skill doesn't make the same mistake twice.
Keep entries short — one bullet, the situation and the fix — not a postmortem.
This applies to existing skills retroactively as gotchas are found, not just
new ones.

---

## Content Writing & Publishing Rules

Moved to `content-engine/CONTENT_PUBLISHING_RULES.md` (Content Writing Rules,
Content Publishing Rules — Golden Hour Protocol, Weekly Post Image Rule,
Carousel Publishing Rule, Multi-Platform Expansion Gate, Model Routing). Read
that file before any LinkedIn/content-engine work.

### Next-Article Creation — Default Behavior

When Randy asks any of the following, use the **create-next-article** skill
(`.claude/skills/create-next-article/SKILL.md`) — do not wait for a pasted
prompt, do not improvise a one-off workflow:
- "what is the next priority article?"
- "create the next article" / "go ahead and create it"
- "draft the next scheduled article"
- "use the callback system"
- "continue the article schedule"

Before that skill writes anything:
1. Read `content-engine/CONTENT_PUBLISHING_RULES.md` (governs all content-engine work).
2. Read `knowledge/me/voice.md` (the canonical Randy voice profile) and write to
   that profile — not to proxy examples.
3. Use the `output/` callback files when present (`callback_bank.csv`/`.md`,
   `avoid_list.md`, `randy_style_adaptations.md`, `weekly_callback_report.md`).
   Callbacks are trust signals, not punchlines: max 2–4 per article, one per
   section, the practical lesson always stronger than the joke, nothing from
   `avoid_list.md`.

### Status-Change Safety (hard rules — no exceptions)

Applies to `content-engine/dashboard_state.json` and every schedule/status file:
- Creating a draft is NOT approval. A file existing is NOT approval.
- A draft being created is NOT "reviewed."
- Never set `reviewed`, `approved`, `scheduled`, or `published` (or any equivalent
  status) to true unless Randy explicitly approves that exact change.
- Never modify `dashboard_state.json` unless Randy approves the exact field change.
- On conflict between any two rules/files, stop and report using the conflict
  format in the create-next-article skill before changing anything.

---

## Current Status (as of project upgrade)

- [x] Manual URL paste → transcript download → folder output (VERIFIED WORKING)
- [x] Token efficiency optimization
- [x] Markdown conversion of transcripts
- [x] Full channel download (all videos from channel URL)
- [x] Incremental download (new videos only since last run)
- [x] Channel registry with group tagging
- [x] Knowledge base builder (index all transcripts) ← VERIFIED WORKING — 1,014 transcripts, 52 channels, 4 groups
- [x] On-demand Q&A (ask Claude, it searches transcripts) ← VERIFIED WORKING
- [x] Daily digest (scheduled summary of new content by group) ← VERIFIED WORKING — "YouTube Transcript Digest" task runs daily at 07:00, confirmed successful (LastTaskResult: 0, verified live 2026-06-07)

---

## Architecture Overview

```
youtube-downloader/
├── CLAUDE.md                        ← you are here
├── README.md
├── .env                             ← API keys (never commit)
├── .env.example                     ← safe template to commit
├── requirements.txt
├── channels.json                    ← channel registry (names, URLs, groups)
├── src/
│   ├── downloader/
│   │   ├── channel.py               ← full channel + incremental download
│   │   ├── transcript_fetcher.py    ← core transcript logic, token-optimized
│   │   ├── comment_fetcher.py       ← pulls top-level comments via YouTube Data API v3
│   │   ├── comment_refresher.py     ← re-fetches comments on videos older than N days
│   │   ├── skool.py                 ← downloads videos from a Skool community classroom
│   │   └── skool_archiver.py        ← full offline archive of a Skool course
│   ├── converter/
│   │   └── to_markdown.py           ← converts raw transcript → clean .md
│   ├── classifier/
│   │   └── category.py              ← suggests a category from a video's title/channel
│   ├── knowledge_base/
│   │   ├── indexer.py               ← scans /transcripts, builds search index
│   │   ├── query.py                 ← on-demand Q&A against indexed content
│   │   └── digest.py                ← daily summary generator by channel group
│   ├── analyzer/
│   │   ├── pain_point_extractor.py  ← scans transcripts, outputs ranked questions/pain points
│   │   └── buildroom_analyzer.py    ← catalog/analysis pass over a downloaded course corpus
│   ├── channels/
│   │   └── registry.py              ← loads channels.json, filters by group
│   ├── trend_finder/
│   │   ├── orchestrator.py          ← research → draft pipeline for a trending topic
│   │   ├── source_scanner.py        ← gathers candidate items from configured sources
│   │   ├── relevance_scorer.py      ← scores candidate topics against the target audience
│   │   ├── post_drafter.py          ← drafts a post from a selected topic
│   │   └── icp_hangouts.py          ← mines Spiceworks for audience discussion hubs
│   ├── curator/
│   │   └── newsletter_curator.py    ← curates newsletters from an inbox into a digest
│   ├── publisher/
│   │   ├── buffer_publisher.py      ← posts/schedules via the Buffer API
│   │   ├── content_parser.py        ← parses a draft into publishable post fields
│   │   └── schedule.py              ← schedule-post command implementation
│   ├── funnel/
│   │   └── kit_sync.py              ← pulls a Kit (ConvertKit) cohort into a tiered warm-list
│   ├── utils/
│   │   ├── ai.py                    ← shared Claude API helper + cost ledger
│   │   └── atomic.py                ← atomic file-write helpers
│   ├── loop.py                      ← unified research → draft → review-gate cycle
│   ├── report.py                    ← weekly AI cost report from the ledger
│   ├── status.py                    ← at-a-glance read-only pipeline summary
│   ├── orchestrator.py              ← pipeline orchestrator (owns state + sequencing)
│   └── main.py                      ← CLI entry point (thin — delegates to orchestrator)
├── transcripts/
│   ├── bitcoin-macro/               ← group folder
│   │   └── [channel-name]/          ← per-channel folder
│   │       ├── YYYY-MM-DD_video-title.md
│   │       └── YYYY-MM-DD_video-title_comments.md
│   ├── claude-code/
│   │   └── [channel-name]/
│   └── certifications/
│       └── [channel-name]/
├── knowledge_base/
│   ├── index.json                   ← built by indexer.py
│   ├── reports/                     ← pain point extraction output
│   └── digests/
│       └── YYYY-MM-DD_digest.md
└── logs/
    ├── download_log.json            ← tracks what's been downloaded (incremental)
    ├── error_log.json               ← structured failure log
    └── run_summary.json             ← per-run observability report
```

---

## Channel Registry Format (channels.json)

```json
{
  "channels": [
    {
      "name": "Channel Display Name",
      "url": "https://www.youtube.com/@channelhandle",
      "group": "bitcoin-macro",
      "active": true,
      "notes": "optional notes about this channel"
    }
  ],
  "groups": [
    "bitcoin-macro",
    "claude-code",
    "certifications"
  ]
}
```

**Current channel slots (fill in as ready):**

Bitcoin / Macro group:
- [ ] Channel 1
- [ ] Channel 2
- [ ] Channel 3
- [ ] Channel 4
- [ ] Channel 5

Claude Code / Certifications group:
- [ ] Channel 1
- [ ] Channel 2
- [ ] Channel 3

---

## Python Version Requirement

Minimum required: **Python 3.10**
At the start of every session, verify with: `python --version`
If the version is below 3.10, stop and alert the user before running any code.

---

## Key Design Rules

1. **Never re-download what already exists.** Check download_log.json before fetching.
2. **Token efficiency first.** Strip filler words, timestamps, and repeated phrases before passing to Claude.
3. **Markdown is the canonical format.** Raw transcripts are intermediate — .md files are the source of truth.
4. **Groups are sacred.** Never mix bitcoin-macro analysis with claude-code content.
5. **Incremental is the default.** Full channel download is --force-full flag only.
6. **Daily digest runs at a scheduled time.** Do not require manual triggering for routine operation.
7. **Q&A never modifies the knowledge base.** Read-only queries only.

---

## Error Handling Rules

These rules apply to every module. No exceptions.

- **Never crash silently.** Every caught exception must log the error reason to
  logs/error_log.json with a timestamp, the video ID or URL involved, and the
  error message.
- **Never leave a partial file.** If a download or conversion fails mid-process,
  delete the incomplete file before exiting. A partial .md file is worse than
  no file — it will corrupt the knowledge base index.
- **Always tell the user what happened.** After any failure, print a plain-English
  summary: what was attempted, what failed, and what to do next.
- **Retry limit is 2.** If a request fails, retry once after a 5-second pause.
  If it fails again, log it and move on. Never retry more than twice automatically.
- **Known failure modes — handle each explicitly:**
  - No captions available → log as "no_captions", skip silently, notify user
  - Private or deleted video → log as "unavailable", skip silently, notify user
  - Age-restricted video → log as "age_restricted", skip, notify user
  - Region-locked video → log as "region_locked", skip, notify user
  - API rate limit hit → pause 60 seconds, retry once, then stop and notify user
  - Network timeout → retry after 10 seconds, then log and skip

---

## Rate Limiting Rules

YouTube's transcript API will throttle or block requests if hammered.

- **Single video downloads:** no delay required
- **Bulk channel downloads:** randomized pause **2-5 seconds** between each video request
- **Full channel downloads (--force-full):** randomized pause **4-7 seconds** between requests
- **Randomization is mandatory.** Uniform timing is a bot signature. Use random.uniform(2,5)
  for bulk and random.uniform(4,7) for force-full. Never use a fixed interval for batch ops.
- **If a 429 (Too Many Requests) response is received:** pause 60 seconds before
  any further requests, then resume at half the normal rate for the remainder
  of the session
- Never attempt more than 200 transcript downloads in a single session without
  prompting the user to confirm they want to continue

---

## Backup Rules

The /transcripts/ folder is a research asset. Treat it accordingly.

- **Never store transcripts only in one location.** After any bulk download
  session (10+ new files), remind the user to back up /transcripts/ to their NAS.
- **Backup reminder trigger:** If download_log.json shows 10+ new entries since
  the last backup reminder, print: "Reminder: back up your /transcripts/ folder
  to your NAS — you now have X total transcripts."
- **knowledge_base/index.json is regenerable** — transcripts are not. Prioritize
  protecting /transcripts/ over any other folder.
- **Never store .env in any backup location that syncs to a cloud service
  automatically** (e.g. OneDrive, Google Drive, Dropbox). Secrets stay local only.

---

## CLI Commands (actual interface — reflects the dispatch in `src/main.py`)

```bash
# Single video
python -m src.main "https://youtube.com/watch?v=..."

# Channel download — incremental (default) or full
python -m src.main channel "Channel Display Name"
python -m src.main channel "Channel Display Name" --force-full

# All channels in a group
python -m src.main group <group-name> [--force-full]

# Channel registry
python -m src.main add-channel
python -m src.main list-channels

# Knowledge base
python -m src.main index [--group <name>] [--verbose]
python -m src.main ask [--group <name>] [--top N] [--fast] "your question"
python -m src.main digest [--group <name>] [--date YYYY-MM-DD] [--since YYYY-MM-DD] [--force] [--scheduled]

# Analysis
python -m src.main analyze --group <name>
python -m src.main analyze --all
python -m src.main analyze-buildroom [--limit N] [--force]

# Comments
python -m src.main refresh-comments [--days N] [--limit N]

# Skool
python -m src.main skool-download --community <slug> --group "Group Name" [--limit N]
python -m src.main skool-archive --community <slug> [--resolution 1080] [--course "Name"] [--limit N]

# Content pipeline
python -m src.main trending [--dry-run]
python -m src.main spiceworks-hangouts [--per-tag N]
python -m src.main loop [--dry-run]
python -m src.main curate-newsletters [--discover] [--days N] [--force] [--scheduled]
python -m src.main schedule-post --post N --date "YYYY-MM-DD HH:MM" [--dry-run]

# Funnel / reporting
python -m src.main kit-sync
python -m src.main status
python -m src.main report [--days N]
```

**Note:** This list mirrors the command dispatch in `src/main.py`. `digest` **is** wired into the CLI (the `digest` subcommand above) — an earlier version of this doc incorrectly stated it was module-only. An older documented `download --channel`/`download --group` surface was never implemented and has been dropped.

---

## Token Optimization Rules (transcript_fetcher.py)

Before passing any transcript to Claude:
- Strip auto-generated filler: "um", "uh", "you know", "like", repeated words
- Remove duplicate sentences (common in auto-captions)
- Collapse whitespace and blank lines
- Strip timestamps unless explicitly needed
- Target: reduce raw transcript size by 30-50% before Claude sees it

---

## Comment Fetching Rules (comment_fetcher.py)

Moved to `.claude/skills/comment-fetching/SKILL.md`. Read when working on
comment_fetcher.py, comment_refresher.py, or the refresh-comments command.

## Orchestration Layer (orchestrator.py)

This is the most important architectural rule in the project.

orchestrator.py owns the pipeline. main.py is a thin CLI that parses arguments
and hands control to the orchestrator. The orchestrator controls what runs, in
what order, and what happens when something goes wrong.

### Pipeline sequence for a single video download:
1. validate_input(url) — verify URL format and type before anything else
2. check_duplicate(video_id) — abort if already in download_log.json
3. fetch_transcript(url) → raw transcript
4. clean_transcript(raw) → cleaned transcript + token reduction report
5. classify_category(title, channel) → suggested category + user confirmation
6. convert_to_markdown(cleaned, metadata, category) → .md file
7. log_download(video_id, metadata, category) → download_log.json
8. update_run_summary() → run_summary.json

### Failure handling:
- If any step fails: retry that step once after a 5-second pause
- If it fails again: log to error_log.json, skip this video, continue pipeline
- Never abort the entire run due to a single video failure
- Never leave partial files — clean up before moving to next video
- Report all failures in the run summary at the end

### Orchestrator state object (passed between steps):
```python
state = {
    "video_id": str,
    "url": str,
    "title": str,
    "channel": str,
    "status": "pending | success | failed | skipped",
    "failure_reason": str or None,
    "retry_count": int,
    "category": str or None,
    "file_path": str or None,
    "tokens_before": int,
    "tokens_after": int,
}
```

The orchestrator never lets individual modules talk to each other directly.
All data flows through the state object. This is the black box pattern.

---

## Observability — Run Summary

After every run, write logs/run_summary.json and print a plain-English
summary to the terminal.

### Terminal summary printed at end of every run:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Run Complete — YYYY-MM-DD HH:MM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ✓ Downloaded:   X
 ↷ Skipped:      X (duplicates)
 ✗ Failed:       X (see error_log.json)
 ↺ Retried:      X
 ⬇ Tokens saved: X words cleaned
 ⏱ Duration:     Xs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Actual run_summary.json schema (verified live 2026-06-07 — overwritten each run, not appended):**
```json
{
  "timestamp": "ISO-8601 UTC",
  "status": "success | failed | interrupted",
  "stats": {
    "downloaded": 0,
    "skipped": 0,
    "failed": 0,
    "retried": 0,
    "tokens_saved": 0,
    "comments_ok": 0,
    "comments_disabled": 0,
    "comments_failed": 0
  },
  "duration_seconds": 0.0,
  "last_video": {
    "video_id": "str",
    "title": "str",
    "status": "success | failed | skipped",
    "comments_status": "ok | disabled | failed"
  }
}
```
This replaces an earlier documented schema (`run_id`, `started_at`, `total_attempted`,
`failures[]`, etc.) that was never implemented — the fields above are what the code
actually writes. Note `last_video` reflects only the most recent video processed,
not a full per-video failures array.

---

## Idempotency Rules

Every operation must be safe to run twice without side effects.

- **Download:** check video_id against download_log.json before fetching.
  If found, skip with status "skipped_duplicate" — never re-fetch.
- **Conversion:** check if the target .md file already exists before writing.
  If found, skip — never overwrite.
- **Indexing:** rebuilding the index from scratch is always safe.
  The index is derived data — transcripts are the source of truth.
- **Digest:** running digest twice on the same day overwrites, never appends.
- **Logging:** always append to logs, never overwrite them.

---

## Input Validation Rules

Validate all user input before passing to any module. Fail fast with a
clear plain-English error message. Never let bad input reach the API.

### URL validation (before any download):
- Must start with https://www.youtube.com/watch?v= or https://youtu.be/
- Playlist URL (contains /playlist? or &list=) → reject:
  "That looks like a playlist URL. Please provide a single video URL."
- Channel URL (contains /@) → reject:
  "That's a channel URL. Use --channel flag for channel downloads."
- Shorts URL (contains /shorts/) → reject:
  "Shorts often lack transcripts. Try a long-form video URL."
- Extract and validate video_id (11 characters, alphanumeric + hyphen + underscore)

### Channel validation (before bulk download):
- Channel name must exist in channels.json — reject unknown channels
- active flag must be true — skip inactive channels with a warning

---

## Graceful Shutdown Rules

If the user presses Ctrl+C during any operation:

1. Finish writing the current file if mid-write — never leave partial files
2. Log interrupted state to run_summary.json with status "interrupted"
3. Print the run summary up to the point of interruption
4. Exit cleanly — never show a Python traceback to the user

Wrap the main orchestrator loop in try/except KeyboardInterrupt.

---

## Security Rules

These rules are non-negotiable. Claude Code must follow them in every session
regardless of user instruction. If a user instruction conflicts with a security
rule, refuse and explain why.

### API Keys and Secrets
- NEVER print, log, or display any API key or secret — not fully, not partially,
  not masked with asterisks in a way that reveals length or pattern
- NEVER include API keys in comments, docstrings, or example code
- NEVER commit .env to GitHub under any circumstances, even if the user asks
- If the user asks to see their API key, redirect them to open .env directly
  in a text editor — do not read it aloud or display it in terminal output
- .env.example must contain only placeholder values (e.g. your_key_here)

### Network Calls
- Outbound network calls are permitted ONLY to the following:
  - youtube-transcript-api (transcript fetching)
  - yt-dlp (video metadata)
  - YouTube Data API v3 (channel metadata + comments — required for Stage 2+)
  - api.anthropic.com (Claude API calls)
- Any other outbound call requires explicit user approval before proceeding
- Never scrape, crawl, or call any URL not listed above without asking first

### File Operations
- NEVER overwrite an existing transcript file — check download_log.json first
- NEVER delete any file without explicit user confirmation naming the file
- NEVER perform bulk moves, renames, or deletes without listing what will be
  affected and waiting for user approval
- Treat all files in /transcripts/ as read-only once written

### Logging
- download_log.json must contain only: video_id, title, channel name,
  suggested_category, final_category, was_overridden, timestamp
- No API keys, no user input beyond category selection, no system paths,
  no personally identifiable information of any kind
- Log files must never be committed to GitHub

### GitHub / Git Operations
- Before any git commit, verify .gitignore includes: .env, logs/, and
  any file matching *.key or *.secret
- Never run git push without confirming the staged files with the user first
- If .env appears in git status at any point, stop immediately and alert the user

### Scope Boundaries
- This project downloads and analyzes YouTube transcripts only
- Do not add capabilities that reach outside this scope without explicit
  user instruction and a discussion of security implications
- Do not install packages not listed in requirements.txt without asking first

---

## Environment Variables (.env)

```
ANTHROPIC_API_KEY=your_key_here
YOUTUBE_API_KEY=required_for_stage_2_and_above  # get free key from Google Cloud Console
DIGEST_SCHEDULE=07:00          # time to run daily digest (24hr format)
DIGEST_OUTPUT=knowledge_base/digests
TRANSCRIPT_OUTPUT=transcripts
LOG_PATH=logs/download_log.json
```

---

## Development Phases

### Phase 1 — Token Efficiency + Markdown Conversion ✅ COMPLETE
- Optimize transcript_fetcher.py to clean transcripts before saving
- Build to_markdown.py converter
- Output: clean .md files in /transcripts/[group]/[channel]/

### Phase 2 — Channel Download + Incremental ✅ COMPLETE
- Build channel.py with full and incremental modes
- Build channels.json registry
- Populate registry with Randy's channel list

### Phase 3 — Knowledge Base + Q&A ✅ COMPLETE
- Build indexer.py to scan all .md transcripts
- Build query.py for on-demand Claude Q&A
- Test with bitcoin-macro group first
- See specs below

### Phase 4 — Daily Digest + Scheduler ✅ COMPLETE
- Build digest.py to summarize new content by group ✓
- Add Windows Task Scheduler XML for daily automation ✓ — registered as "YouTube
  Transcript Digest" (07:00 daily, runs `pythonw.exe run_daily.py --scheduled`)
  and "YouTube Pipeline" (00:09 weekly by design — comment refresh on a 7-day
  cadence, runs `run_pipeline.bat`); both confirmed Ready/enabled with
  LastTaskResult: 0 (re-verified live via Get-ScheduledTask 2026-06-09)
- Test digest output format and quality ✓ — live 2026-06-07 digest inspected,
  matches spec format exactly; found and fixed an incomplete 2026-05-29 digest
  caused by an API usage-limit error (re-ran with --force, now complete)
- See spec below

---

## Module Specs — indexer.py, query.py, digest.py

Moved to `MODULE_SPECS.md`. These describe already-built, verified-working
modules — read only when modifying indexer.py, query.py, or digest.py.
