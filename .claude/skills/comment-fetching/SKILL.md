---
name: comment-fetching
description: Rules and pipeline spec for comment_fetcher.py / comment_refresher.py — when fetching or refreshing YouTube video comments, including output format, API requirements, and the Stage 2+ orchestrator pipeline sequence. Moved from root CLAUDE.md during the context restructure (content unchanged, relocated verbatim).
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
