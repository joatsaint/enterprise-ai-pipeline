# Module Specs — indexer.py, query.py, digest.py

Moved from root `CLAUDE.md` during the context restructure (content unchanged,
relocated verbatim). These describe modules that are already built and marked
"VERIFIED WORKING" in CLAUDE.md's version header. Read this file only when
modifying `indexer.py`, `query.py`, or `digest.py`.

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
