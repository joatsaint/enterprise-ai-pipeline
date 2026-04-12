# PHASE1_UPGRADE_PROMPT.md
## Paste this into Claude Code inside the youtube-downloader project folder

---

You are upgrading an existing YouTube transcript downloader project. The project
currently works: the user pastes a single YouTube URL and a transcript is downloaded
to a folder. That behavior must be preserved exactly as-is.

Your job is to add the following capabilities in Phase 1 only. Do not build anything
outside of Phase 1 scope.

---

## Project path context

This project lives at:
C:\Users\joatsaint\Desktop\On Desktop HP-CapCut Network Share\Claude Code My Projects\youtube-downloader

Read the CLAUDE.md file in the project root before writing any code. Follow all
rules and architecture defined there.

---

## Categories

There are exactly two categories. Use these exact folder names:

```
transcripts/
  ai-and-claude-code/
  bitcoin-and-economic-news/
  uncategorized/              ← only used if auto-assign fails completely
```

Display names (for prompts shown to the user):
- "AI & Claude Code"
- "Bitcoin and Economic News"

---

## Phase 1 Scope — Build exactly these things

### 1. Token-Optimized Transcript Fetcher (src/downloader/transcript_fetcher.py)

Refactor or create transcript_fetcher.py to clean transcripts before saving.
Apply these cleaning steps in order:

- Remove timestamps (e.g. [00:01:23] or 0:01:23 patterns)
- Strip filler words: "um", "uh", "you know", "like" when used as filler
- Collapse 3+ consecutive spaces or newlines into single breaks
- Remove duplicate consecutive sentences (auto-caption artifact)
- Remove "[Music]", "[Applause]", "[Laughter]" and similar auto-caption tags
- Do NOT alter meaning, speaker content, or factual statements

After cleaning, report: "Reduced from X words to Y words (Z% reduction)"

The existing single-URL download flow must still work after this change.

---

### 2. Category Classifier (src/classifier/category.py)

Create category.py that handles category suggestion, confirmation, and fallback.

**Logic flow:**

Step 1 — Auto-suggest using keyword scoring:

Score the video TITLE first (title keywords outweigh channel name keywords).
Then score the CHANNEL NAME as a secondary signal.
Title match weight = 2x. Channel name match weight = 1x.

Bitcoin and Economic News keywords (title or channel):
  bitcoin, btc, crypto, ethereum, eth, macro, fed, inflation, interest rate,
  recession, gold, market, s&p, nasdaq, dow, economy, economic, finance,
  financial, investing, investment, wealth, trading, stocks, bonds, treasury,
  dollar, usd, currency, defi, altcoin, halving, mining

AI & Claude Code keywords (title or channel):
  claude, anthropic, ai, artificial intelligence, llm, gpt, chatgpt, openai,
  gemini, cursor, copilot, claude code, mcp, prompt, automation, agent,
  langchain, rag, vector, embedding, certification, cert, exam, tutorial,
  how to, course, learn, training, aws, azure, google cloud

Step 2 — Present suggestion to user:

```
Video: "Bitcoin Will Hit $200K Before 2027 — Here's Why"
Channel: Some Channel Name

Suggested category: Bitcoin and Economic News
Press Enter to confirm, or type:
  1 — AI & Claude Code
  2 — Bitcoin and Economic News
  s — Skip (save to uncategorized)
>
```

Step 3 — Handle response:
- Enter / no input within 10 seconds → accept suggestion
- "1" → AI & Claude Code
- "2" → Bitcoin and Economic News
- "s" → save to uncategorized, log as manually skipped
- Any unrecognized input → re-prompt once, then fall back to suggestion

Step 4 — Log the decision in download_log.json:
  video_id, title, channel, suggested_category, final_category,
  was_overridden (bool), timestamp

---

### 3. Markdown Converter (src/converter/to_markdown.py)

Create to_markdown.py that outputs a .md file with this structure:

```markdown
# [Video Title]

**Channel:** [Channel Name]
**Category:** [AI & Claude Code | Bitcoin and Economic News | Uncategorized]
**Published:** [YYYY-MM-DD]
**URL:** [original YouTube URL]
**Downloaded:** [YYYY-MM-DD]
**Word Count:** [approximate word count after cleaning]

---

## Transcript

[cleaned transcript content here]
```

---

### 4. Updated Folder Structure

Create these folders if they don't exist:

```
transcripts/
  ai-and-claude-code/
  bitcoin-and-economic-news/
  uncategorized/
```

Filename format: YYYY-MM-DD_[video-title-slug].md

---

### 5. Updated requirements.txt

Add any new packages required. Common ones:
- youtube-transcript-api (if not already present)
- yt-dlp (if not already present)
- python-slugify (for filename generation)

Do not remove any existing packages.

---

### 6. Create channels.json in project root

```json
{
  "channels": [],
  "groups": [
    "ai-and-claude-code",
    "bitcoin-and-economic-news"
  ],
  "display_names": {
    "ai-and-claude-code": "AI & Claude Code",
    "bitcoin-and-economic-news": "Bitcoin and Economic News"
  },
  "notes": "Add channels here. Each entry needs name, url, group, active fields."
}
```

---

### 7. Create logs/download_log.json

```json
{
  "downloads": [],
  "last_updated": null,
  "notes": "Tracks downloaded video IDs, categories, and override history."
}
```

---


### 8. Orchestrator (src/orchestrator.py)

Create orchestrator.py as the central pipeline coordinator. main.py must
delegate all work to the orchestrator — it should never call modules directly.

Pipeline sequence the orchestrator must execute in order:
1. validate_input(url) — URL format check before anything else
2. check_duplicate(video_id) — check download_log.json, skip if found
3. fetch_transcript(url) — get raw transcript
4. clean_transcript(raw) — token optimization, return cleaned + word counts
5. classify_category(title, channel) — suggest + confirm category
6. convert_to_markdown(cleaned, metadata, category) — write .md file
7. log_download(video_id, metadata, category) — append to download_log.json
8. update_run_summary() — write/update run_summary.json

Failure handling per step:
- On failure: wait 5 seconds, retry the failed step once
- On second failure: log to error_log.json, delete any partial file, skip
  this video, continue with next
- Never abort the entire run for a single video failure

State object passed between all steps:
```python
{
    "video_id": str,
    "url": str,
    "title": str,
    "channel": str,
    "status": str,  # pending | success | failed | skipped
    "failure_reason": str or None,
    "retry_count": int,
    "category": str or None,
    "file_path": str or None,
    "tokens_before": int,
    "tokens_after": int,
}
```

### 9. Input Validation (inside orchestrator.py validate_input())

Before processing any URL, validate:
- Must be a YouTube watch URL (youtube.com/watch?v= or youtu.be/)
- Reject playlist URLs with: "That looks like a playlist URL. Please provide a single video URL."
- Reject channel URLs with: "That's a channel URL. Use --channel flag for channel downloads."
- Reject Shorts URLs with: "Shorts often lack transcripts. Try a long-form video URL."
- Extract video_id and validate it is 11 alphanumeric characters

### 10. Observability — Run Summary

After every run, write logs/run_summary.json and print this terminal summary:

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

### 11. Graceful Shutdown

Wrap the orchestrator's main loop in try/except KeyboardInterrupt.
On Ctrl+C:
- Finish writing the current file if mid-write
- Log status "interrupted" to run_summary.json
- Print the run summary up to that point
- Exit with code 0 — never show a Python traceback to the user

### 12. Idempotency Enforcement

- Before fetch: check video_id in download_log.json — skip if found
- Before write: check if target .md file exists — skip if found
- After any failed write: delete the partial file before logging failure
- All log operations must append, never overwrite

## What you must NOT build in this phase

- Do not build channel.py or any channel-level download logic
- Do not build the knowledge base indexer
- Do not build the Q&A query system
- Do not build the digest generator
- Do not build the CLI main.py command router (unless it already exists — preserve it)

---

## Tests to write

Write tests in tests/ that verify:

1. transcript_fetcher.py removes timestamps correctly
2. transcript_fetcher.py removes filler words without altering real content
3. to_markdown.py produces a valid .md file with all required header fields
4. Output filename follows YYYY-MM-DD_[slug].md format
5. category.py correctly scores a bitcoin-titled video as Bitcoin and Economic News
6. category.py correctly scores a Claude/AI-titled video as AI & Claude Code
7. category.py title keywords score 2x higher than channel name keywords
8. category.py falls back to suggestion when user provides no input within 10 seconds
9. download_log.json records was_overridden=true when user changes the suggestion
10. Existing single-URL download still produces output in the correct category folder

Run all tests after scaffolding. Report pass/fail count.

---

## Final checklist before you finish

- [ ] Existing single-URL download still works
- [ ] Agent auto-suggests category based on title (title weighted 2x over channel name)
- [ ] User can confirm with Enter, override with 1 or 2, or skip with s
- [ ] No response within 10 seconds → auto-accepts suggestion
- [ ] Output is a .md file with all header fields including Category
- [ ] Token reduction percentage is reported after each download
- [ ] download_log.json records suggestion, final category, and override flag
- [ ] channels.json exists with correct group names and display names
- [ ] All tests pass

Report the checklist status when done.
