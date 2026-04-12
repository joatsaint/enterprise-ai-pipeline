# PHASE2_SCAFFOLD_PROMPT.md
## Paste this into Claude Code inside the youtube-downloader project folder

---

You are building Phase 2 of an existing YouTube transcript downloader project.
Phase 1 is complete and verified working. Do not modify any Phase 1 files unless
a conflict requires it — and if so, explain the conflict before changing anything.

Read CLAUDE.md and MASTER_PLAN.md before writing any code.
Verify Python version is 3.10+ before starting.

---

## Phase 2 Scope — Build exactly these things

### 1. Channel Batch Downloader (src/downloader/channel.py)

Build channel.py that accepts a YouTube channel homepage URL and downloads
transcripts and comments for all available videos.

**Two modes:**
- Default (incremental): only download videos not already in download_log.json
- --force-full flag: download everything regardless of log

**Channel URL formats to support:**
- https://www.youtube.com/@channelhandle
- https://www.youtube.com/@channelhandle/videos
- https://www.youtube.com/channel/UCxxxxxxxx

**How to get video list from a channel:**
Use yt-dlp to extract video IDs from the channel's video tab:
```python
import subprocess, json
result = subprocess.run(
    ["yt-dlp", "--flat-playlist", "--dump-single-json",
     "--playlist-end", "50", channel_url],
    capture_output=True, text=True
)
data = json.loads(result.stdout)
video_ids = [e["id"] for e in data.get("entries", [])]
```

Research note: test --playlist-end at 20, 50, and 100 to find practical limit
before running a full channel pull. Log the actual count retrieved.

**Rate limiting (mandatory):**
- Use random.uniform(2, 5) between each video request
- Use random.uniform(4, 7) if --force-full flag is set
- Never use fixed intervals — bot signature
- On 429 response: pause 60 seconds, retry once, then stop and notify user
- Hard cap: prompt user to confirm if session would exceed 200 downloads

**For each video in the channel:**
- Run the full Phase 1 orchestrator pipeline (validate → fetch transcript →
  fetch comments → clean → classify → convert → log)
- Reuse all existing Phase 1 modules — do not duplicate logic
- Category auto-suggestion runs per video using existing category.py
- If the channel is in channels.json with a group assigned, pre-fill the
  category suggestion with that group (user still confirms or overrides)

---

### 2. Comment Fetcher (src/downloader/comment_fetcher.py)

Build comment_fetcher.py that fetches top-level comments for a video
using the YouTube Data API v3.

**Requirements:**
- Use YOUTUBE_API_KEY from .env
- Fetch top 100 comments sorted by relevance (not newest)
- Relevance sort surfaces highest-engagement comments — better signal
  for pain point research than chronological
- Return list of dicts: {author, text, like_count, published_at}

**Failure handling:**
- Comments disabled → log as "comments_disabled", return empty list, continue
- Quota exhausted (403) → log warning "YouTube API quota exhausted for today",
  set a session flag to skip all remaining comment fetches, continue
  transcript downloads uninterrupted — never fail a transcript because
  comments are unavailable
- Video not found → log as "comments_unavailable", return empty list
- Any other error → log to error_log.json, return empty list, continue

**Output file (saved alongside transcript):**
Filename: YYYY-MM-DD_[video-slug]_comments.md
Location: same folder as the transcript file

```markdown
# Comments: [Video Title]

**Channel:** [Channel Name]
**Video URL:** [https://www.youtube.com/watch?v=VIDEO_ID]
**Comments Fetched:** [count]
**Fetched:** [YYYY-MM-DD]

---

## Top Comments (by relevance)

[comment text]
— [author] | [like_count] likes | [published_at]

---

[comment text]
— [author] | [like_count] likes | [published_at]
```

---

### 3. Updated Orchestrator (src/orchestrator.py)

Update the existing orchestrator to include comment fetching in the pipeline.
The updated 10-step sequence for Stage 2+:

1. validate_input(url)
2. check_duplicate(video_id)
3. fetch_transcript(url) → raw transcript
4. fetch_comments(video_id) → top 100 comments
5. clean_transcript(raw) → cleaned + token report
6. convert_to_markdown(cleaned, metadata, category) → transcript .md
7. convert_comments_to_markdown(comments, metadata) → comments .md
8. classify_category(title, channel) → category confirmation
9. log_download(video_id, metadata, category)
10. update_run_summary()

Update the state object to include:
```python
"comments_fetched": int,       # 0 if disabled or failed
"comments_file": str or None,  # path to comments .md file
"comments_status": str,        # "ok" | "disabled" | "quota_exhausted" | "failed"
```

Update run summary output to include comments line:
```
 [COMMENTS] Comments fetched: X files (Y disabled, Z failed)
```

---

### 4. Updated Channel Registry (channels.json)

Add a helper CLI command to register a new channel:
```
python -m src.main add-channel
```

Prompts for:
- Channel display name
- Channel URL
- Group (shows numbered list of existing groups)
- Active (y/n, default y)

Saves to channels.json automatically.

---

### 5. Updated CLI (src/main.py)

Add these commands to main.py:

```bash
# Download all new videos from a registered channel (incremental)
python -m src.main channel "Channel Name"

# Force full download of all videos from a channel
python -m src.main channel "Channel Name" --force-full

# Download all channels in a group (incremental)
python -m src.main group ai-and-claude-code

# Add a new channel to the registry
python -m src.main add-channel

# Show registered channels
python -m src.main list-channels
```

Existing single URL command must still work:
```bash
python download.py <URL>
python -m src.main <URL>
```

---

### 6. Install yt-dlp if not present

Add to requirements.txt:
- yt-dlp
- google-api-python-client  (for YouTube Data API v3 comments)

Run pip install -r requirements.txt after updating.

---

### 7. Updated .env.example

Add these lines:
```
YOUTUBE_API_KEY=your_youtube_data_api_v3_key_here
# Get free key: console.cloud.google.com > New Project > YouTube Data API v3 > Credentials
```

---

## What you must NOT build in this phase

- Do not build the knowledge base indexer
- Do not build the Q&A query system
- Do not build the pain point extractor
- Do not build the daily digest generator
- Do not modify any Phase 1 test — add new tests only

---

## Tests to write (add to tests/test_phase2.py)

1. comment_fetcher.py returns empty list when comments are disabled
2. comment_fetcher.py sets session quota flag on 403 response
3. comment_fetcher.py output file has all required header fields
4. channel.py skips videos already in download_log.json (incremental mode)
5. channel.py downloads all videos with --force-full regardless of log
6. channel.py applies randomized pause between requests (not fixed interval)
7. orchestrator state object includes comments_fetched and comments_status fields
8. run summary includes comments line in output
9. add-channel command writes correct entry to channels.json
10. list-channels command outputs registered channels

Run all Phase 1 AND Phase 2 tests after scaffolding.
Report total pass count (target: 27+ passing).

---

## Final checklist before you finish

- [ ] python download.py <URL> still works (Phase 1 preserved)
- [ ] python -m src.main channel "Name" downloads transcripts + comments
- [ ] Incremental mode skips already-downloaded videos
- [ ] --force-full downloads everything regardless of log
- [ ] comment_fetcher.py saves _comments.md alongside each transcript
- [ ] Quota exhaustion on comments does not stop transcript downloads
- [ ] Randomized pause intervals used for all batch operations
- [ ] yt-dlp and google-api-python-client installed
- [ ] channels.json add-channel command works
- [ ] All Phase 1 tests still pass
- [ ] All Phase 2 tests pass
- [ ] Run summary includes comments stats

Report checklist status when done.
