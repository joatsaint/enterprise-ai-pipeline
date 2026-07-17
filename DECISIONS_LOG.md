# DECISIONS_LOG.md
## Architectural Decision Log — YouTube Transcript Research Engine

**Owner:** Randy Skiles  
**Format:** ADR (Architectural Decision Record)  
**Read at:** Session start, before any architecture or pipeline work  
**Last Updated:** 2026-06-29 (Session 23 — initial population from PROMPT_ARCHITECTURE.md + CLAUDE.md)

---

## How to Use This File

Each ADR captures: the decision, the context that forced it, alternatives that were considered, the reasoning, and the consequences. Reading the decisions without reading the context produces rules without understanding — which gets overridden during the next context reset.

**When to add an entry:** Any decision that took more than 10 minutes to arrive at, or that was reached through rejected alternatives, or that would be re-litigated without this record.

---

## Decision Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| ADR-001 | Orchestrator owns the pipeline — modules never talk to each other | Active | April 2026 |
| ADR-002 | Markdown is the canonical format — raw transcripts are intermediate | Active | April 2026 |
| ADR-003 | Incremental download is the default — full download requires --force-full | Active | April 2026 |
| ADR-004 | Groups are sacred — never mix content across groups | Active | April 2026 |
| ADR-005 | Rate limiting must use randomized intervals — fixed delay is a bot signature | Active | April 2026 |
| ADR-006 | Retry limit is 2 — one retry after 5s, then log and move on | Active | April 2026 |
| ADR-007 | Haiku for classification tasks, Sonnet for reasoning tasks | Active | April 2026 |
| ADR-008 | All LLM calls route through src/utils/ai.py — never directly from modules | Active | May 2026 |
| ADR-009 | Atomic writes for all file operations — write to temp, then rename | Active | April 2026 |
| ADR-010 | Index always rebuilds from scratch — never appended | Active | April 2026 |
| ADR-011 | Query.py is read-only — it never modifies the knowledge base | Active | April 2026 |
| ADR-012 | Comments are weighted higher than transcripts in pain point extraction | Active | May 2026 |
| ADR-013 | Two-pass extraction — questions separate from pain points | Active | May 2026 |
| ADR-014 | Digest must include a "What to Act On" section | Active | May 2026 |
| ADR-015 | Windows Task Scheduler, not cron, for automation | Active | May 2026 |
| ADR-016 | Token cleaning happens before any Claude API call | Active | April 2026 |
| ADR-017 | Session discipline rules adopted from Jared's Locked Session Rules v2 | Active | 2026-07-17 |
| ADR-018 | Extend existing custom statusline rather than replace with ccstatusline | Active | 2026-07-17 |

---

## ADR-001 — Orchestrator owns the pipeline

**Date:** April 2026  
**Status:** Active

**Context:**  
The pipeline has 8 sequential steps (validate → check duplicate → fetch → clean → classify → convert → log → summarize). Without a coordinator, modules would need to call each other directly, creating a web of imports where a change in one module breaks another unexpectedly.

**Decision:**  
`orchestrator.py` owns all pipeline state and sequence. No module calls another module directly. All data flows through a shared state dictionary. The orchestrator calls modules and passes state in; modules return state out. They store nothing internally.

**Alternatives considered:**
- Direct function chaining — modules call each other in sequence. Rejected: debugging becomes impossible when step 4 fails because step 4 received bad data from step 3 which received it from step 2.
- Event bus — modules emit/subscribe to events. Rejected: overkill for a single-user CLI tool; introduces async complexity with no benefit.

**Reasoning:**  
Defining the state schema first and making it the contract between modules meant every module had compatible interfaces from day one. No integration debugging. A failure at any step is catchable and loggable without stopping the entire pipeline.

**Consequences:**
- ✅ Any step can fail and the pipeline continues with remaining videos
- ✅ Every module is independently testable using a mock state object
- ✅ Adding a new pipeline step requires only a new module + one orchestrator call
- ⚠️ The state object schema must be kept in sync with CLAUDE.md — any new field added to a module must be added to the schema

---

## ADR-002 — Markdown is the canonical format

**Date:** April 2026  
**Status:** Active

**Context:**  
Transcripts from `youtube-transcript-api` arrive as JSON lists of timestamped segments. We need a format that is human-readable, searchable with grep, diff-able in git, renderable in any editor, and can be processed by Claude without additional parsing.

**Decision:**  
`to_markdown.py` converts raw JSON transcripts to `.md` files immediately after download. Raw JSON transcripts are not saved long-term. `.md` files are the source of truth. The knowledge base indexes `.md` files only.

**Alternatives considered:**
- Keep raw JSON — preserves timestamps and segment structure. Rejected: Claude can't efficiently process timestamped JSON arrays; adding tooling to parse/convert at query time doubles complexity.
- Plain `.txt` — simple, universal. Rejected: `.md` enables structured headers (title, channel, date, group) in frontmatter that the indexer can parse without a separate metadata store.
- SQLite database — fast lookup, structured queries. Rejected: introduces a dependency, requires migrations as schema evolves, can't be diffed in git, can't be read without tooling.

**Reasoning:**  
Markdown works without tooling. If Claude Code, the indexer, or any module fails, the transcripts can still be read, searched, and processed manually. A database failure is an outage. A directory of `.md` files with a corrupt index is an inconvenience (re-run the indexer).

**Consequences:**
- ✅ Transcripts are human-readable and immediately useful without any tooling
- ✅ git diff on transcript files shows actual content changes
- ✅ indexer.py can be rebuilt or replaced without losing any data
- ⚠️ Frontmatter format in `.md` headers must stay consistent — the indexer parses it

---

## ADR-003 — Incremental download is the default

**Date:** April 2026  
**Status:** Active

**Context:**  
A YouTube channel can have hundreds of videos. Re-downloading all of them on every run is slow, burns API quota, and triggers rate limiting or blocks. After the initial download, most runs only need the last few new videos.

**Decision:**  
Every download checks `download_log.json` first. If the `video_id` is already present, skip it — no fetch, no file write. `--force-full` flag bypasses this check and re-downloads everything. Incremental is the default. Full download is an explicit opt-in.

**Alternatives considered:**
- Always download, detect duplicates by checking if `.md` file exists. Rejected: filesystem check is slower than a JSON lookup for large libraries; file existence doesn't guarantee the download succeeded cleanly last time.
- Date-based incremental (only fetch videos newer than last run date). Rejected: upload dates and transcript availability dates can differ; a video uploaded 6 months ago might have captions added last week.

**Reasoning:**  
`download_log.json` is the authoritative record of what was successfully downloaded. It records `video_id`, not filename — so even if files are reorganized or renamed, the log prevents re-downloading. This also satisfies the idempotency rule: running the pipeline twice in a row produces exactly the same result.

**Consequences:**
- ✅ Running the pipeline on 50 channels takes seconds if everything is current
- ✅ Idempotency is satisfied — safe to re-run at any time
- ⚠️ `download_log.json` is the source of truth for what's been downloaded; if it's deleted, the next run re-downloads everything (this is correct behavior, not a bug)
- ⚠️ Transcript content updates (e.g., auto-caption corrections by YouTube) will not be picked up without `--force-full`

---

## ADR-004 — Groups are sacred

**Date:** April 2026  
**Status:** Active

**Context:**  
The knowledge base contains transcripts across multiple research topics: bitcoin/macro, Claude Code/AI tools, certifications. Pain point extraction, digests, and Q&A are all audience-specific. A question about Bitcoin macro cycles is not a pain point for an IT professional seeking certifications.

**Decision:**  
Groups (`bitcoin-macro`, `claude-code`, `certifications`) are enforced at every level: download routing, index structure, query scope, and digest generation. No module mixes data across groups. The `--group` flag is required for most operations.

**Alternatives considered:**
- Single global index, filter by tag at query time. Rejected: Claude's context window is finite; loading 1,000 transcripts to filter them client-side wastes tokens; group-scoped index means group-scoped cost.
- Nested groups (e.g., `ai/claude-code`, `ai/certifications`). Rejected: adds complexity without adding value; current four groups cover the actual content categories.

**Reasoning:**  
Pain point research is the commercial core of this system. Contaminating a group's pain point report with off-topic content produces noise that misleads PDF content creation. A certification-focused report that includes Bitcoin macro opinions has no business value and actively damages the product output.

**Consequences:**
- ✅ Every output (digest, Q&A, pain point report) is scoped to a single audience
- ✅ Adding a new channel is a two-step operation: add to `channels.json` with group tag, done
- ⚠️ Cross-group content (e.g., "Claude Code for AI career seekers") must be resolved at channels.json assignment — assign to the primary audience group, not both

---

## ADR-005 — Rate limiting must use randomized intervals

**Date:** April 2026  
**Status:** Active

**Context:**  
YouTube's transcript API throttles or blocks requests that follow predictable patterns. A fixed 3-second delay between every request is as detectable as no delay at all — uniform timing is a bot signature that rate-limiting systems specifically look for.

**Decision:**  
All bulk download operations use `random.uniform(2, 5)` seconds between requests. Full download (`--force-full`) uses `random.uniform(4, 7)`. The specific values are documented in `CLAUDE.md`. Never use a fixed interval for batch operations.

**Alternatives considered:**
- Fixed 3-second delay. Rejected: uniform timing is detectable; this was the pattern that caused blocks in early testing.
- Exponential backoff only on errors. Rejected: doesn't prevent throttling; only responds after a block has occurred.
- No delay. Rejected: direct path to a 429 or IP block.

**Reasoning:**  
Randomization mimics human browsing behavior. A 2–5 second range with uniform distribution produces inter-request intervals that are statistically indistinguishable from a human clicking through a playlist. The residential proxy (Webshare) handles IP rotation; randomization handles timing.

**Consequences:**
- ✅ Bulk downloads of 200+ videos run without blocks
- ✅ Full channel downloads complete without triggering rate limits
- ⚠️ Do not optimize by removing randomization — this is not technical debt, it is a functional requirement
- ⚠️ If YouTube behavior changes and blocks increase, widen the range (e.g., 3–8 seconds) before any other intervention

---

## ADR-006 — Retry limit is 2

**Date:** April 2026  
**Status:** Active

**Context:**  
Download failures have two distinct causes: permanent failures (no captions available, video deleted, age restriction, region lock) and transient failures (network timeout, momentary API hiccup). Permanent failures will not resolve with retries. Transient failures usually resolve within seconds.

**Decision:**  
Retry any failed step once after a 5-second pause. If it fails again, log to `error_log.json` and move to the next video. Never retry more than twice. The failure reason is categorized explicitly: `no_captions`, `unavailable`, `age_restricted`, `region_locked`, `timeout`. Permanent failures are not retried.

**Alternatives considered:**
- Retry 3 or 5 times. Rejected: YouTube failures are predominantly permanent (no captions is the most common); 5 retries on a video with no captions wastes 25 seconds per video with zero chance of success.
- No retries. Rejected: network timeouts are transient and would produce false failures.
- Unlimited retries with exponential backoff. Rejected: a pipeline stalled on one unavailable video is worse than a logged failure.

**Reasoning:**  
The retry count is calibrated to transient failure recovery, not permanent failure resolution. One retry catches the vast majority of network hiccups. A second retry would only catch highly unlikely timing issues at a cost of pipeline slowdown across all failures.

**Consequences:**
- ✅ Transient network failures don't produce permanent gaps in the transcript library
- ✅ Permanent failures are logged immediately without wasting time
- ⚠️ If a batch run shows >10% failures, check `error_log.json` — likely a YouTube API change or proxy issue, not a retry limit problem

---

## ADR-007 — Haiku for classification, Sonnet for reasoning

**Date:** April 2026  
**Status:** Active

**Context:**  
The system makes Claude API calls in three contexts: pain point extraction (classification), Q&A queries (reasoning over retrieved content), and digest generation (synthesis + recommendation). These are fundamentally different task types with different cost profiles.

**Decision:**  
`pain_point_extractor.py` uses `claude-haiku-4-5-20251001`. Cost target: under $0.15 per full 50-file run. `query.py` and `digest.py` use `claude-sonnet-4-6`. Model constants are defined in `src/utils/ai.py`. Upgrade trigger from Haiku to Sonnet for extraction: quality degrades noticeably or Haiku pricing reaches 3x current baseline.

**Alternatives considered:**
- Sonnet for everything. Rejected: extraction is pattern-matching ("does this sentence contain a pain point?") not reasoning; Sonnet-level capability is waste at Haiku prices.
- Haiku for everything. Rejected: Q&A over 50,000 tokens of transcript content requires coherent reasoning and synthesis; Haiku output quality on complex RAG tasks is insufficient.
- GPT-4o or Gemini alternatives. Deferred: addressed in ADR-008 (abstraction layer); not rejected, just not immediately justified when Anthropic models are already integrated.

**Reasoning:**  
Classification is pattern recognition. Haiku performs equivalently to Sonnet on structured classification tasks at approximately 1/5 the cost. Using Sonnet for extraction would increase cost by 5x with no measurable quality improvement. The cost discipline here is a production habit, not a penny-pinching decision.

**Consequences:**
- ✅ Extraction costs remain under $0.15/run for 50-file batches
- ✅ Model selection is documented — no re-litigating "why not GPT" each session
- ⚠️ If extraction output quality degrades (categories become inconsistent, pain points become generic), upgrade to Sonnet before investigating anything else
- ⚠️ Monitor Anthropic console spend alerts at $5 and $10/month thresholds

---

## ADR-008 — All LLM calls route through src/utils/ai.py

**Date:** May 2026  
**Status:** Active  
**Also documented in:** MASTER_PLAN.md Stage 6 backlog as "Platform Agnostic Refactor"

**Context:**  
As the system grew, multiple modules were making Claude API calls directly: `pain_point_extractor.py`, `query.py`, `digest.py`. Switching model versions or providers required updating each module separately. A provider outage or price change became a multi-file change.

**Decision:**  
All Claude API calls must route through `src/utils/ai.py`. No module imports `anthropic` directly. `ai.py` owns: API key loading, model constants, retry logic, cost ledger, and the shared `ask_claude()` helper. A module that needs Claude calls `ai.ask_claude(prompt, model)` — it does not touch the API client.

**Alternatives considered:**
- Keep direct imports in each module — simpler, fewer abstractions. Rejected: already caused pain when Haiku model ID changed; discovered by finding the old ID hardcoded in three places.
- Use an existing LangChain or LlamaIndex abstraction. Rejected: adds a dependency for a problem that can be solved with 40 lines of Python; framework abstractions also add their own versioning complexity.

**Reasoning:**  
Switching from Anthropic to a different provider or switching model versions requires changing one file. The cost ledger in `ai.py` also enables `src/report.py` to produce weekly spend reports — this only works if all calls flow through one accounting point.

**Consequences:**
- ✅ Provider switch = change one file + one API key in `.env`
- ✅ Model version update = change constants in one place
- ✅ Cost ledger is always complete — no missing calls
- ⚠️ New modules that need Claude must import from `src/utils/ai` — never import `anthropic` directly; enforce this in code review

---

## ADR-009 — Atomic writes for all file operations

**Date:** April 2026  
**Status:** Active  
**See also:** ADR-010 — both address the same failure mode (corrupt/partial `index.json`); ADR-009 governs *how* files are written, ADR-010 governs *what* the index contains

**Context:**  
During early testing, a `Ctrl+C` during an indexer run produced a partial `index.json` — the file existed but contained truncated JSON that silently corrupted all subsequent queries. The error manifested as query results returning fewer transcripts than expected, with no error message.

**Decision:**  
Every file write in the pipeline uses the atomic write pattern: write to a temp file first (`filename.tmp`), verify the write succeeded, then `os.rename(tmp, target)`. `os.rename()` is atomic on both POSIX and Windows NTFS. If the process is interrupted mid-write, the original file is untouched.

**Alternatives considered:**
- Direct write (`open(target, 'w')`). Rejected: any interruption during write produces a partial file; already caused a real production incident.
- Write + verify + overwrite. Rejected: still has a window between verify and overwrite where an interrupt corrupts state.
- Database transactions. Rejected: overkill; the system uses flat files by design (ADR-002).

**Reasoning:**  
Discovered through a real production failure. A partial `index.json` is worse than no `index.json` because it doesn't raise an error — queries return incomplete results silently. The atomic write pattern closes this failure mode completely. `os.rename()` makes this a one-line change per write operation.

**Consequences:**
- ✅ A `Ctrl+C` or crash during any file write leaves existing files untouched
- ✅ The system can be safely interrupted at any point without corrupting state
- ⚠️ All new file-writing code must use the `src/utils/atomic.py` helpers, not direct `open()` + `write()`

---

## ADR-010 — Index always rebuilds from scratch

**Date:** April 2026  
**Status:** Active  
**See also:** ADR-009 — both address the same failure mode (corrupt/partial `index.json`); ADR-010 governs *what* the index contains, ADR-009 governs *how* files are written

**Context:**  
The knowledge base index (`knowledge_base/index.json`) maps video IDs and file paths for query.py and digest.py. An append-only index would grow stale if transcript files were renamed, moved, or if metadata changed.

**Decision:**  
`indexer.py` always rebuilds `index.json` from scratch by scanning the entire `/transcripts/` directory. It never appends. The index is derived data — the `.md` transcript files are the source of truth. If the index is lost or corrupted, re-running `indexer.py` restores it fully.

**Alternatives considered:**
- Incremental index (only index new files since last run). Rejected: tracking what's "new" for the index is a separate bookkeeping problem; since rebuild takes under 5 seconds for 1,000 transcripts, there's no performance justification for the complexity.
- Persistent index with version tracking. Rejected: same problem; introduces state that can diverge from the filesystem.

**Reasoning:**  
A full rebuild is always correct. An incremental update can diverge from the filesystem (renamed files, deleted files, moved files). The rebuild cost is negligible relative to the reliability guarantee.

**Consequences:**
- ✅ `index.json` is always consistent with the actual filesystem state
- ✅ Reorganizing the `/transcripts/` folder structure requires only a re-index, not a migration
- ⚠️ Do not design features that assume the index is append-only — it is not

---

## ADR-011 — Query.py is read-only

**Date:** April 2026  
**Status:** Active

**Context:**  
The Q&A function (query.py) searches transcripts, loads relevant content, and passes it to Claude. It would be technically easy to have it cache answers or write updated metadata back to the index.

**Decision:**  
`query.py` makes no writes. It reads `index.json`, reads transcript `.md` files, calls the Claude API, and returns an answer to the terminal. No file is modified or created during a query run.

**Alternatives considered:**
- Cache query results to disk to avoid re-running identical queries. Deferred: not implemented because query behavior should always reflect the current transcript library; a cached answer from last week may be wrong today if new transcripts were added.
- Write query history to a log for audit trail. Rejected: the system is single-user; a query log provides no operational value and adds write-complexity to a component that currently has none.

**Reasoning:**  
Treating query as a pure read function eliminates an entire class of failure modes. A bug in query.py cannot corrupt the knowledge base. A partial query run cannot leave the index in an inconsistent state. The function is referentially transparent: same query + same transcripts = same answer.

**Consequences:**
- ✅ Running a query is always safe — no side effects
- ✅ Multiple queries can run simultaneously without conflict
- ⚠️ If query caching is ever added, it must be to a separate cache store — never to `index.json` or the transcript files

---

## ADR-012 — Comments weighted higher than transcripts in pain point extraction

**Date:** May 2026  
**Status:** Active

**Context:**  
The commercial objective of this system is to identify real audience pain points and questions to drive PDF product creation. Transcripts capture what the creator says. Comments capture what the audience actually asks, struggles with, and argues about.

**Decision:**  
In `pain_point_extractor.py`, content from `_comments.md` files receives higher weight in scoring than content from the corresponding transcript. When both are available, a pain point mentioned in comments is prioritized over a pain point mentioned only in the transcript.

**Alternatives considered:**
- Equal weighting. Rejected: creator content is structured and polished; it does not reflect audience confusion or gaps. A creator explaining a concept clearly does not mean the audience isn't confused by it.
- Transcripts only (ignore comments). Rejected: comments are the unfiltered market signal; ignoring them means analyzing the supply side (what creators teach) instead of the demand side (what audiences need).
- Comments only. Rejected: transcripts provide topic context and vocabulary that helps Claude classify comments correctly.

**Reasoning:**  
The business creates products that solve audience problems. The audience states those problems in the comments. A viewer who types "but what about [specific scenario]?" in a YouTube comment is doing free market research. Comments weighted higher means the pain point output is audience-driven, not creator-driven.

**Consequences:**
- ✅ Pain point reports reflect what the audience actually struggles with, not what creators assume they struggle with
- ✅ Product ideas derived from reports have a higher signal-to-noise ratio
- ⚠️ Videos without comment data (`_comments.md` absent) produce lower-confidence pain point signals — flag these in the output

---

## ADR-013 — Two-pass extraction: questions separate from pain points

**Date:** May 2026  
**Status:** Active

**Context:**  
Early single-pass extraction produced a mixed output where questions and pain points were interleaved. "How do I get an AI job without a CS degree?" and "I feel overwhelmed by too many tools" were ranked in the same list. These have different shapes as products.

**Decision:**  
`pain_point_extractor.py` runs two distinct passes over the same content.  
- **Pass 1 (Questions):** What is the audience explicitly asking? ("How do I...?", "What is...?", "Can I...?")  
- **Pass 2 (Pain Points):** What is the audience frustrated by or struggling with? ("I don't know...", "Nobody explains...", "I keep failing at...")  
Outputs are separate sections in the report.

**Alternatives considered:**
- Single pass with type tagging (tag each item as "question" or "pain point"). Rejected: Claude's single-pass classification bleeds between categories; a frustrated question ("how do I get an AI job?") gets classified differently depending on surrounding context.
- Three passes (add "desired outcomes" as third category). Deferred: adds cost without immediate product value; "desired outcomes" can be inferred from questions + pain points; add when the content business reaches Stage 6.

**Reasoning:**  
A question maps to a how-to guide. A pain point maps to a decision framework or reassurance piece. The same topic ("AI job search") produces different products depending on whether the audience is asking "how do I do this?" (how-to guide) or feeling "I'm falling behind" (validation + roadmap piece). Keeping them separate at extraction time means product creation doesn't require re-analysis.

**Consequences:**
- ✅ Pain point reports are directly actionable for product creation without secondary analysis
- ✅ Content calendar can be built directly from the two-column output
- ⚠️ The two-pass approach costs approximately 2x the tokens of single-pass; this is justified given the output value; do not combine passes to "optimize cost"

---

## ADR-014 — Digest must include a "What to Act On" section

**Date:** May 2026  
**Status:** Active

**Context:**  
The daily digest summarizes new transcript content by group. An early version produced summaries that were accurate but not useful — "three new videos were published about X" with no guidance on what, if anything, to do about it.

**Decision:**  
Every digest output must end with a section titled `## What to Act On` containing 2–3 specific, prioritized content opportunities derived from the day's new content. Format: `1. [Specific opportunity] — [Why it's high priority]`. This section is required — a digest without it is incomplete.

**Alternatives considered:**
- Summary only (no action recommendation). Rejected: a summary that describes without recommending has no business value; Randy would need to re-read the summary and derive the action himself, duplicating Claude's analytical work.
- Action list generated by a separate module. Rejected: the summary and the action list are derived from the same content; separating them would require loading the same transcripts twice.

**Reasoning:**  
The digest runs at 07:00 daily and Randy reads it as a morning brief. The "What to Act On" section is what converts research into content decisions. Without it, the digest is an information dump. With it, it's a daily editorial brief with a ready-made content calendar stub.

**Consequences:**
- ✅ Each daily digest produces at least one actionable content opportunity
- ✅ Digest quality can be evaluated by asking "are the action items specific enough to act on immediately?"
- ⚠️ If `What to Act On` produces generic items ("write a post about AI"), the digest prompt needs to be tightened, not the module structure

---

## ADR-015 — Windows Task Scheduler, not cron

**Date:** May 2026  
**Status:** Active

**Context:**  
The daily digest and weekly pipeline need to run on a schedule. The development and production environment is Randy's Windows PC. Cross-platform scheduling portability is not a goal.

**Decision:**  
Windows Task Scheduler is the automation layer. Digest runs via "YouTube Transcript Digest" task (07:00 daily, `pythonw.exe run_daily.py --scheduled`). Pipeline runs via "YouTube Pipeline" task (00:09 weekly). Both tasks are registered, enabled, and verified (LastTaskResult: 0, confirmed 2026-06-09).

**Alternatives considered:**
- Python `schedule` library (in-process scheduling). Rejected: requires the Python process to stay running; if the PC restarts, the process doesn't restart with it; Windows Task Scheduler survives reboots.
- WSL cron. Rejected: introduces WSL dependency; adds a Linux subsystem for a task the native Windows scheduler handles natively.
- n8n automation. Deferred: n8n roadmap (docs/N8N_AUTOMATION_ROADMAP.md) covers this as a future layer; Task Scheduler is the interim solution that works now.

**Reasoning:**  
Windows Task Scheduler is the native scheduler for this environment. It survives reboots, runs as a service, produces LastTaskResult codes for verification, and requires no additional software. Using the native tool for a native task is not a compromise — it is correct engineering for the deployment environment.

**Consequences:**
- ✅ Both scheduled tasks run unattended and have verified clean exit codes
- ✅ Rebooting the PC does not break the schedule
- ⚠️ Migrating to a different machine requires re-registering the Task Scheduler entries; the XML definitions should be saved in `docs/` or the task re-created manually

---

## ADR-016 — Token cleaning happens before any Claude API call

**Date:** April 2026  
**Status:** Active

**Context:**  
YouTube auto-captions contain significant noise: filler words ("um", "uh", "you know"), repeated phrases, duplicate sentences from caption overlap, and raw timestamps. Passing this noise to Claude wastes tokens and degrades output quality.

**Decision:**  
`transcript_fetcher.py` cleans all transcript content before it reaches any downstream module or Claude API call. Cleaning steps: strip filler words, remove duplicate sentences, collapse whitespace, strip timestamps unless explicitly requested. Target: 30–50% token reduction from raw to clean. The reduction percentage is reported in the run summary.

**Alternatives considered:**
- Clean at query time (pass raw transcripts to Claude, let it handle noise). Rejected: Claude's context window is finite; feeding 30% more tokens reduces how many transcripts fit; Haiku at 50,000 raw tokens costs more than Haiku at 25,000 cleaned tokens for identical useful content.
- Clean in a separate post-processing step after saving. Rejected: raw files would need to be stored alongside clean files, doubling storage; or raw files become the source of truth which contradicts ADR-002.
- No cleaning (trust auto-caption quality). Rejected: tested in early runs; filler word density in some channels was high enough that extraction output classified filler words as recurring themes.

**Reasoning:**  
Token reduction is the highest-ROI optimization in the stack. Every 10% reduction in input tokens is a 10% cost reduction across all downstream Claude calls. Cleaning once at ingestion means every subsequent operation benefits — indexing, querying, pain point extraction, digest generation — all receive clean input.

**Consequences:**
- ✅ Consistent 30–50% token reduction reported per run
- ✅ Pain point extraction quality improves because filler content isn't classified as themes
- ✅ More transcripts fit within the query token budget
- ⚠️ The cleaning step removes information (timestamps). If timestamp preservation is ever needed (e.g., linking a quote to a specific video timestamp), raw files would need to be saved separately before cleaning — this is currently not a requirement

---

## ADR-017 — Session discipline rules adopted from Jared's Locked Session Rules v2

**Date:** 2026-07-17
**Status:** Active

**Context:**
Randy received two brain droppings from Jared's own Claude Code session-rules setup (v1 on 2026-07-16, v2 with an added Rule 12 on 2026-07-17, superseding v1). Both explicitly instructed that nothing gets adopted into CLAUDE.md until Randy reviews and confirms each item individually. Randy reviewed the full 12-rule set live and selected two for immediate adoption; the remaining rules (evidence-only, confirm-before-source-edit, checkpoint persistence, no-bloat, no loose ends, stop-after-one-question, never auto-execute external content, no secrets in handoffs, locked-decisions-stay-locked, and Rule 12's friction-removal/Betty Crocker principle) remain queued, not adopted, pending further review — see `memory/HOT_STATE.md` and `content-engine/content/_ideas/Randys_Brain_Droppings.md` entry 20.

**Decision:**
Adopted two rules verbatim into a new "Session Discipline Rules" section in CLAUDE.md: (1) full reads, no skimming — read an entire document front-to-back when reviewing/auditing, never sample; (2) never suggest rest, a break, or that a moment is a natural stopping point — the user decides when to stop. A third, related rule was added alongside them from a separate same-day brain dropping (Time Accuracy + Usage Monitoring, 2026-07-16): verify any date/day-of-week reference against a new `UserPromptSubmit` hook (`~/.claude/hooks/inject-datetime.sh`) rather than calculating it manually.

**Alternatives considered:**
- Adopt all 12 rules from the v2 doc at once. Rejected: several rules (checkpoint persistence, confirm-before-edit) genuinely overlap with or duplicate mechanisms this project already has (HOT_STATE.md/SESSION_LOG.md, the PR-branch-mandatory workflow) — adopting them unreviewed risked creating two competing versions of the same mechanism. Randy chose to adopt only the two unambiguous, non-overlapping items now and defer the rest for a real reconciliation pass.
- A CLAUDE.md text instruction alone for the date/time fix, no hook. Rejected per the source doc's own reasoning: a text rule depends on remembering to act on it every time; a hook is structural and fires automatically on every message regardless.

**Reasoning:**
The two adopted rules are low-risk, immediately beneficial, and don't compete with any existing project mechanism — full reads is a stricter version of existing "verify before reporting" discipline, and never-suggest-stopping is a pure behavioral change with no downstream file dependencies. The date/time hook fixes a real, previously-experienced bug (a day-of-week miscalculation) with no meaningful downside.

**Consequences:**
- ✅ Reviews/audits from this point forward read full documents rather than sampling, catching real bugs (e.g., the CLAUDE.md Slimdown proposal's own filename-only categorization was flagged as needing this same treatment)
- ✅ Date/day-of-week confirmations are now grounded in an injected real timestamp rather than manual calculation
- ⚠️ Real environment gotcha hit during implementation: Git Bash on this machine has no IANA zoneinfo database installed, so the originally-proposed `TZ='America/Chicago' date ...` approach silently fell back to GMT. Fixed by shelling out to PowerShell/.NET `TimeZoneInfo` instead, which correctly reads Windows' own DST-aware timezone data. Anyone porting this hook to a different machine should verify zoneinfo is present before assuming the simpler `TZ=` approach will work.
- ⚠️ 9 of the 12 rules from the source doc remain unreviewed/unadopted — this ADR covers only the 2 (+1 companion) that were actually confirmed; do not treat this entry as full adoption of Jared's rule set

---

## ADR-018 — Extend existing custom statusline rather than replace with ccstatusline

**Date:** 2026-07-17
**Status:** Active

**Context:**
The "Time Accuracy + Usage Monitoring" brain dropping (2026-07-16, see ADR-017) proposed installing `ccstatusline` as a persistent usage/cost meter, treating it as a simple install-only addition. Investigation before acting on it found Randy already has a custom statusline configured (`~/.claude/statusline-command.py`, registered in `~/.claude/settings.json`), showing `cwd | model | context% remaining`. Installing `ccstatusline` would have overwritten the `statusLine.command` config key entirely, silently discarding the existing custom script rather than layering on top of it — this was surfaced to Randy as a real decision rather than executed as an assumed "easy yes."

**Decision:**
Extend the existing `statusline-command.py` in place to also read and display `cost.total_cost_usd` and `rate_limits.five_hour`/`rate_limits.seven_day` (`used_percentage` from each) from the statusLine JSON payload, rather than installing `ccstatusline`. Both new fields are optional/degrade gracefully — `rate_limits` is only present for Pro/Max subscribers and only after the first API response of a session, so the script omits that segment entirely when absent rather than erroring or printing a blank field.

**Alternatives considered:**
- Install `ccstatusline`, replacing the custom script. Rejected: would have silently discarded existing, working, custom-built functionality (the `~`-abbreviated cwd display, the specific field selection) for a generic tool that wasn't actually a strict superset of what was already there.
- Run both side-by-side somehow. Rejected: Claude Code's `statusLine.command` config accepts exactly one command; there's no supported way to run two statusline scripts simultaneously.

**Reasoning:**
The existing script already did most of what was needed and was working correctly; the only real gap was cost/usage visibility. Extending it is strictly additive, preserves everything already verified working, and required verifying the real statusLine JSON schema first (`cost.total_cost_usd`, `rate_limits.five_hour.used_percentage`, `rate_limits.seven_day.used_percentage`, confirmed via Anthropic's own statusline documentation) rather than assuming field names.

**Consequences:**
- ✅ Statusline now shows `cwd | model | context% | $cost | 5h:X% 7d:Y%` in one line, satisfying the original ask (a persistent, always-visible usage/cost meter) without losing any existing functionality
- ✅ Verified working both with and without `rate_limits` present in the payload (tested via direct stdin injection, not just assumed)
- ⚠️ A real testing gotcha hit and worked around: piping JSON containing Windows backslash-escaped paths through Git Bash's `echo` mangled the escaping and caused a silent parse failure (the script's `except JSONDecodeError: sys.exit(0)` swallowed it with no output) — not a bug in the script itself, but a reminder that `echo`-based JSON testing on this machine is unreliable; write to a temp file and redirect stdin from it instead
