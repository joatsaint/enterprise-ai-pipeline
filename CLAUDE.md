# CLAUDE.md — YouTube Transcript Downloader & Knowledge Base
**Version: 1.6** — Orchestration layer, observability, idempotency, input validation, graceful shutdown, CCA-F best practices, business pipeline integrated, comment fetching added, randomized rate limiting. Knowledge base module specs added: indexer.py, query.py, digest.py.

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
Before writing any code, state assumptions explicitly and ask Randy for confirmation if anything is ambiguous.

---
---

## Content Writing Rules

Before drafting any article, LinkedIn content, newsletter, email, or 
any written content for the audience:

- Read knowledge/me/voice.md and apply Randy's voice profile to all writing
- Never write content in a generic AI voice — always apply the voice profile
- The voice profile contains the master style-transfer prompt — use it
---

## Current Status (as of project upgrade)

- [x] Manual URL paste → transcript download → folder output (VERIFIED WORKING)
- [x] Token efficiency optimization
- [x] Markdown conversion of transcripts
- [x] Full channel download (all videos from channel URL)
- [x] Incremental download (new videos only since last run)
- [x] Channel registry with group tagging
- [ ] Knowledge base builder (index all transcripts) ← SPEC WRITTEN — ready to build
- [ ] On-demand Q&A (ask Claude, it searches transcripts) ← SPEC WRITTEN — ready to build
- [ ] Daily digest (scheduled summary of new content by group) ← SPEC WRITTEN — ready to build

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
│   │   ├── single.py                ← single video by URL (existing, working)
│   │   ├── channel.py               ← full channel + incremental download
│   │   ├── transcript_fetcher.py    ← core transcript logic, token-optimized
│   │   └── comment_fetcher.py       ← pulls top-level comments via YouTube Data API v3
│   ├── converter/
│   │   └── to_markdown.py           ← converts raw transcript → clean .md
│   ├── knowledge_base/
│   │   ├── indexer.py               ← scans /transcripts, builds search index
│   │   ├── query.py                 ← on-demand Q&A against indexed content
│   │   └── digest.py               ← daily summary generator by channel group
│   ├── analyzer/
│   │   └── pain_point_extractor.py  ← scans transcripts, outputs ranked questions/pain points
│   ├── channels/
│   │   └── registry.py              ← loads channels.json, filters by group
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

## CLI Commands (target interface)

```bash
# Single video (existing behavior)
python src/main.py download --url "https://youtube.com/watch?v=..."

# Full channel download (first time)
python src/main.py download --channel bitcoin-macro --force-full

# Incremental (new videos only)
python src/main.py download --channel bitcoin-macro

# Download all channels in a group
python src/main.py download --group bitcoin-macro

# Ask a question against the knowledge base
python src/main.py ask "What are the top Bitcoin price predictions for Q3 2026?"

# Ask limited to a specific group
python src/main.py ask --group bitcoin-macro "What is the consensus on Fed rate cuts?"

# Generate today's digest manually
python src/main.py digest --group bitcoin-macro

# Run scheduled digest (all groups)
python src/main.py digest --all
```

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

Comments are fetched alongside transcripts for every video download.
They are stored as a separate file and fed into the pain point extractor
as a second, higher-signal data source.

### Why comments outperform transcripts for pain point research:
- Transcripts = what the creator says
- Comments = what the audience actually struggles with, asks, and argues about
- Comments surface questions the creator never answered (your content opportunity)
- Comments reveal frustrations, gaps, and high-demand topics transcripts miss

### API requirements:
- Requires YouTube Data API v3 key (free tier: 10,000 quota units/day)
- Top-level comments only — no reply threads needed for Phase 1
- Cost: ~1-3 quota units per video comment fetch
- Free tier supports hundreds of videos per day comfortably
- Get key at: console.cloud.google.com → New Project → YouTube Data API v3

### Output format (YYYY-MM-DD_[video-slug]_comments.md):
```markdown
# Comments: [Video Title]

**Channel:** [Channel Name]
**Video URL:** [URL]
**Comments Fetched:** [count]
**Fetched:** [YYYY-MM-DD]

---

## Top Comments

[comment text]
— [author], [like count] likes

[comment text]
— [author], [like count] likes
```

### Fetch rules:
- Fetch top 100 comments sorted by relevance (not newest)
- Relevance sort surfaces highest-engagement comments — better signal
- If video has comments disabled → log as "comments_disabled", skip silently
- If quota exhausted → log warning, skip remaining comment fetches for session,
  continue transcript downloads uninterrupted
- Comments file saved in same folder as transcript file
- Comment fetch runs AFTER transcript fetch in orchestrator pipeline
- If comment fetch fails, do not fail the transcript — log and continue

### Updated orchestrator pipeline sequence (Stage 2+):
1. validate_input(url)
2. check_duplicate(video_id)
3. fetch_transcript(url) → raw transcript
4. fetch_comments(video_id) → top 100 comments by relevance
5. clean_transcript(raw) → cleaned transcript + token report
6. convert_to_markdown(cleaned, metadata, category) → transcript .md
7. convert_comments_to_markdown(comments, metadata) → comments .md
8. classify_category(title, channel) → category confirmation
9. log_download(video_id, metadata, category)
10. update_run_summary()

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

run_summary.json fields: run_id, started_at, completed_at, duration_seconds,
total_attempted, succeeded, skipped_duplicates, skipped_failures, retried,
tokens_saved, failures array.

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

### Phase 3 — Knowledge Base + Q&A ← BUILD NEXT
- Build indexer.py to scan all .md transcripts
- Build query.py for on-demand Claude Q&A
- Test with bitcoin-macro group first
- See specs below

### Phase 4 — Daily Digest + Scheduler
- Build digest.py to summarize new content by group
- Add Windows Task Scheduler XML for daily automation
- Test digest output format and quality
- See spec below

---

## Module Spec — indexer.py

**Purpose:**
Scans all .md transcript files in /transcripts/, extracts metadata from each
file header, and builds a flat JSON index at knowledge_base/index.json.
The index is the lookup table for query.py and digest.py. It is derived data —
if lost or corrupted, it can always be rebuilt by re-running indexer.py.

**Inputs:**
- /transcripts/ directory (read-only scan)
- Optional --group flag to index a single group only

**Outputs:**
- knowledge_base/index.json (overwrite on every run — index is always rebuilt from scratch)
- Terminal confirmation: "Index built: X transcripts indexed across Y channels"

**index.json schema:**
```json
{
  "built_at": "YYYY-MM-DD HH:MM:SS",
  "total_transcripts": 159,
  "groups": {
    "bitcoin-macro": {
      "total": 120,
      "channels": {
        "channel-name": {
          "total": 45,
          "transcripts": [
            {
              "file_path": "transcripts/bitcoin-macro/channel-name/YYYY-MM-DD_title.md",
              "video_id": "abc123",
              "title": "Video Title",
              "channel": "channel-name",
              "group": "bitcoin-macro",
              "date": "YYYY-MM-DD",
              "has_comments": true,
              "word_count": 4500
            }
          ]
        }
      }
    }
  }
}
```

**Idempotency:**
Rebuilding the index from scratch is always safe and always correct.
Never append to index.json — always overwrite with a full rebuild.
The index reflects the current state of /transcripts/ at the time of the run.

**Failure modes — handle each explicitly:**
- /transcripts/ directory not found → fail fast: "transcripts/ directory not found.
  Run a channel download first."
- Malformed .md file (missing header) → log as warning, skip file, continue indexing
- knowledge_base/ directory not found → create it before writing index.json
- Partial write interrupted → delete incomplete index.json, log error, notify user

**Pipeline sequence:**
1. Validate /transcripts/ directory exists
2. Scan all .md files recursively (exclude _comments.md files from main index)
3. For each .md file: extract metadata from file header (title, date, channel, video_id)
4. Check for matching _comments.md file — set has_comments: true/false
5. Count word count of transcript body
6. Build index.json structure in memory
7. Write index.json atomically (write to temp file, rename — never partial write)
8. Print terminal confirmation

**CLI interface:**
```
python main.py index                    # index all groups
python main.py index --group bitcoin-macro  # index one group only
python main.py index --verbose          # show each file as it's indexed
```

**Integration with orchestrator:**
indexer.py is called by the orchestrator after every bulk channel download.
It is also callable standalone via CLI. It does not use the state object —
it operates on the file system directly and reports results to terminal only.

**Testing requirements:**
- Test with empty /transcripts/ directory → graceful empty index output
- Test with one valid .md file → correct index entry produced
- Test with malformed .md file → skip and continue, warning logged
- Test idempotency → running twice produces identical index.json

---

## Module Spec — query.py

**Purpose:**
Accepts a natural language question from the user, searches the knowledge
base index for relevant transcripts, passes matching content to Claude API,
and returns a synthesized answer with source citations. Read-only — never
modifies any file in the knowledge base or transcripts.

**Inputs:**
- User question (string, from CLI)
- Optional --group flag to scope query to one group
- Optional --top N flag to limit number of transcripts searched (default: 10)
- knowledge_base/index.json (must exist — run indexer.py first)

**Outputs:**
- Plain-English answer printed to terminal
- Source citations: list of transcript filenames that contributed to the answer
- No files written — query.py is strictly read-only

**Query pipeline sequence:**
1. Validate index.json exists → fail fast if missing:
   "Index not found. Run: python main.py index"
2. Load index.json into memory
3. Apply --group filter if provided
4. Keyword search across transcript titles and file paths for relevance
5. Load top N matching transcript .md files (default: 10)
6. Build Claude API prompt with transcript content + user question
7. Call Claude API (model: claude-haiku-4-5-20251001 — see ADR-002)
8. Parse and print response with source citations
9. Log query to logs/query_log.json (question, timestamp, sources used, tokens consumed)

**Claude API prompt structure:**
```
You are a research assistant with access to YouTube transcript excerpts.
Answer the following question using ONLY the transcript content provided.
If the answer is not in the transcripts, say so clearly.
Always cite which transcript(s) you drew from.

Question: [user question]

Transcripts:
[transcript content, truncated to fit context window]
```

**Context window management:**
- Max total transcript content passed to Claude: 50,000 tokens
- If matching transcripts exceed limit: prioritize most recent files
- Always include token count in query_log.json for cost tracking

**query_log.json schema:**
```json
{
  "queries": [
    {
      "timestamp": "YYYY-MM-DD HH:MM:SS",
      "question": "user question text",
      "group_filter": "bitcoin-macro or null",
      "transcripts_searched": 10,
      "transcripts_used": ["path1.md", "path2.md"],
      "tokens_consumed": 4200,
      "model": "claude-haiku-4-5-20251001"
    }
  ]
}
```

**Idempotency:**
Query is always read-only. Running the same query twice produces the same
answer (within Claude API response variance). No side effects on any file
except appending to query_log.json.

**Failure modes — handle each explicitly:**
- index.json not found → fail fast with clear instruction to run indexer first
- Transcript file in index not found on disk → skip that file, log warning, continue
- Claude API error → print error, suggest retrying, log to error_log.json
- Empty search results → "No transcripts found matching your query. Try broader terms."
- Context window exceeded → truncate gracefully, notify user which files were excluded

**CLI interface:**
```
python main.py query "what AI skills are most in demand"
python main.py query "bitcoin halving impact" --group bitcoin-macro
python main.py query "how to use Claude Code" --top 5
```

**Integration with orchestrator:**
query.py is standalone — called directly via CLI, not part of the download
pipeline. It does not use the orchestrator state object. It reads index.json
and transcript files, calls Claude API, and returns results to terminal.

**Testing requirements:**
- Test with valid question + populated index → answer returned with citations
- Test with missing index.json → clear error message produced
- Test read-only guarantee → no files modified after query run
- Test --group filter → only transcripts from specified group returned
- Test context window limit → graceful truncation, user notified

---

## Module Spec — digest.py

**Purpose:**
Generates a daily summary of new transcript content added since the last
digest run, organized by channel group. Runs on a schedule (Windows Task
Scheduler) or on demand via CLI. Output is a dated .md file saved to
knowledge_base/digests/. Designed for daily consumption — tells Randy
what new content was added and what the key themes were.

**Inputs:**
- knowledge_base/index.json (must exist and be current)
- logs/download_log.json (to identify what's new since last digest)
- Optional --group flag to digest one group only
- Optional --date flag to digest a specific date (default: today)
- Optional --since flag to digest since a specific date

**Outputs:**
- knowledge_base/digests/YYYY-MM-DD_digest.md (one file per day)
- Terminal confirmation: "Digest complete: X new transcripts summarized"
- If no new content: "No new transcripts since last digest. Nothing to summarize."

**Digest .md output format:**
```markdown
# Daily Digest — YYYY-MM-DD
Generated: YYYY-MM-DD HH:MM

## Summary
X new transcripts added across Y channels since YYYY-MM-DD.

## bitcoin-macro
### [Channel Name] — X new videos
**[Video Title]** (YYYY-MM-DD)
Key themes: [2-3 sentence summary of main topics]
Top audience questions: [top 2-3 questions from comments if available]

### [Channel Name] — X new videos
...

## claude-code
...

## What to Act On
[Claude's synthesis: 2-3 actionable insights from today's new content
relevant to the PDF content business]
```

**Digest pipeline sequence:**
1. Validate index.json exists and is current (warn if older than 24 hours)
2. Load download_log.json to identify transcripts added since last digest
3. If no new transcripts → print "Nothing new" and exit cleanly
4. Load new transcript .md files (full content for summarization)
5. Group new transcripts by group and channel
6. For each new transcript: call Claude API for 2-3 sentence summary + key themes
7. Aggregate summaries into digest structure
8. Generate "What to Act On" section via final Claude API call across all summaries
9. Write digest .md file to knowledge_base/digests/
10. Update digest_log.json with run timestamp
11. Print terminal confirmation

**Claude API usage:**
- Per-transcript summary: claude-haiku-4-5-20251001 (cost-efficient, adequate for summarization)
- "What to Act On" synthesis: claude-haiku-4-5-20251001
- Never use Sonnet for digest unless quality is demonstrably insufficient

**Idempotency:**
Running digest twice on the same day overwrites the existing digest file —
never appends. This means re-running produces a fresh digest for that day.
digest_log.json always appends — never overwrites.

**digest_log.json schema:**
```json
{
  "runs": [
    {
      "timestamp": "YYYY-MM-DD HH:MM:SS",
      "date_digested": "YYYY-MM-DD",
      "new_transcripts": 12,
      "groups_covered": ["bitcoin-macro", "claude-code"],
      "output_file": "knowledge_base/digests/YYYY-MM-DD_digest.md",
      "tokens_consumed": 8400,
      "model": "claude-haiku-4-5-20251001"
    }
  ]
}
```

**Scheduled operation (Windows Task Scheduler):**
- Run daily at time defined by DIGEST_SCHEDULE in .env (default: 07:00)
- Task Scheduler XML already documented in project
- Digest runs silently — output goes to digest file, not terminal, when scheduled
- If run fails silently: error logged to error_log.json with timestamp

**Failure modes — handle each explicitly:**
- index.json not found → fail fast: "Run python main.py index first"
- index.json older than 24 hours → warn user, proceed with stale index
- No new transcripts found → exit cleanly, log run, no digest file written
- Claude API error on individual transcript → skip that transcript, log warning, continue
- Claude API error on synthesis → write partial digest with note: "Synthesis unavailable"
- Digest output directory not found → create it before writing

**CLI interface:**
```
python main.py digest                        # digest today's new content
python main.py digest --group bitcoin-macro  # one group only
python main.py digest --date 2026-04-28      # specific date
python main.py digest --since 2026-04-01     # all new content since date
python main.py digest --force                # re-digest today even if already run
```

**Integration with orchestrator:**
digest.py runs standalone — not part of the download pipeline. It reads
index.json and transcript files, calls Claude API, and writes the digest file.
It does not use the orchestrator state object. It is the final consumer of
the knowledge base, not a producer.

**Testing requirements:**
- Test with no new transcripts → clean "nothing new" exit, no file written
- Test with new transcripts → correct digest file produced with proper format
- Test idempotency → running twice on same day overwrites, not appends
- Test --group filter → only specified group summarized
- Test scheduled mode → no terminal output, error goes to error_log.json
- Test stale index warning → warning printed but digest proceeds
