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
| ADR-025 | "Never suggest rest or stopping" rule strengthened with real Why + soft-phrasing closure | Active | 2026-07-22 |
| ADR-026 | Canonical Project Backlog & Continuous Awareness System — MVP COMPLETE 2026-07-24: Phases 0-3 built, Phases 4-9 scope-cut after a direction review, 7 real active tasks migrated into production via existing capture workflow (zero new code), verified PASS. Frozen pending real-world usage feedback. | Active | 2026-07-23 |

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

---

## ADR-019 — Removed the `$cost` field from the statusline (superseded ADR-018's cost display)

**Date:** 2026-07-17
**Status:** Active — supersedes the cost-display portion of ADR-018; the usage/cost-meter *concept* stays, the cost *number* does not

**Context:**
Randy noticed the statusline's `$cost` figure climbing rapidly during a long session (20-60 cents per check) and flagged it as alarming — it reached $91.82. He cross-checked against the real Anthropic Console and found actual spend for the day was ~$0.45, a roughly 200x discrepancy, far beyond normal estimate drift.

**Decision:**
Removed the `cost.total_cost_usd` field from `~/.claude/statusline-command.py` entirely. Kept the 5-hour/7-day rate-limit usage percentages (`5h:X% 7d:Y%`), which were not implicated in the discrepancy.

**Alternatives considered:**
- Relabel it as an estimate (e.g. `~$X (est, may differ)`) rather than remove it. Rejected — Randy's explicit choice was full removal, not a caveat label, since the number had proven itself off by two orders of magnitude, not just "a bit approximate."

**Reasoning:**
Anthropic's own statusline documentation already labels `total_cost_usd` as a client-side estimate that "may differ from your actual bill," but a 200x gap goes well beyond that caveat's normal scope. The most likely explanation, not fully confirmed (no way to inspect the live raw JSON Claude Code fed into the statusline to prove it directly): this session was unusually long and cache-heavy (large CLAUDE.md and memory files reloaded every turn, multiple subagent calls), and prompt-cache reads bill at roughly a tenth of normal input-token price — if the client-side estimate prices cumulative tokens at the full uncached rate instead of the actual blended cached rate, it would dramatically overstate cost in exactly this kind of session while the real (correctly cache-discounted) bill stays low. A statusline field whose entire purpose is peripheral-vision cost awareness is actively harmful if it causes false alarm instead — removal was the right call over a soft relabel.

**Consequences:**
- ✅ Statusline no longer displays a misleading, alarm-triggering dollar figure
- ✅ Comment left in the script explaining why the field was removed, so it isn't silently re-added later without this context
- ✅ Verified via direct stdin injection that the field is gone even when fed a live-shaped payload containing the actual $91.82 value
- ⚠️ Real spend visibility for this project now requires checking the Anthropic Console or `/usage` directly — no longer available at a glance in the terminal. Randy explicitly accepted this tradeoff given the alternative was an actively misleading number.
- ⚠️ The root cause (client-side estimate vs. cache-discounted actual bill) is a plausible, well-reasoned hypothesis, not confirmed against Claude Code's actual cost-calculation source — if Anthropic fixes or clarifies this upstream, the field could be considered for reinstatement, but only with real verification against the Console first, not by trusting the estimate again

---

## ADR-020 — Standing CTA Rule: every LinkedIn post closes with a named-benefit CTA line, not just the dedicated Lead Magnet Post

**Date:** 2026-07-18
**Status:** Active

**Context:**
Randy raised a real funnel concern: dozens of LinkedIn/YouTube posts with CTAs, only 2 email subscribers total. A live audit of `docs/LinkedIn Stats/LinkedIn Posts 7-18-2026.txt` and `docs/LinkedIn Stats/pretty-links-clicks-2026-07-19.csv` found: reach is real (several posts hit thousands to 48,012 impressions with genuine engagement), the lead magnet link works end-to-end (verified by Randy), and the click-to-signup rate on real human clicks is a normal ~10-15%. But after stripping bot traffic (LinkedInBot, Googlebot family, facebookexternalhit, Mediumbot, YandexBot, Baiduspider, GPTBot, bingbot, and Randy's own repeat IP) from seven weeks of pretty-links click data, real distinct human clicks on the lead magnet link totaled roughly 12-20 total — against tens of thousands of cumulative impressions. The leak is entirely upstream of the landing page: most high-reach posts either carried no CTA at all (a pure story post), gated the CTA behind a comment (the mechanic already retired 2026-07-05 specifically because "they weren't being seen" — first-comments.md rule in `CONTENT_PUBLISHING_RULES.md`), or buried the CTA inline in the closing sentence ("Full story: [link]") where it doesn't register as an ask.

**Decision:**
Every LinkedIn post — story post, article teaser, standalone — must close with one short, visually separated CTA line (blank line break before it, named benefit + link, e.g. `Free 14-Day Plan: Stay Indispensable in the AI Era → https://rskiles.com/the-riddle-of-steel`, never a vague "read more" or comment-gate). This is in addition to, not a replacement for, the existing dedicated Lead Magnet Post (Julie McCoy structure, max 1/2 weeks). Added as a new section in `content-engine/rules/CONTENT_PUBLISHING_RULES.md`.

**Alternatives considered:**
- Move the CTA earlier in the post body. Rejected — LinkedIn truncates to ~3 lines before "see more"; moving the CTA up competes with the hook that earns the expand-click in the first place, and the people who do expand are already a warmer, filtered audience — the fix is making the CTA register once they get there, not relocating it.
- Leave cadence at only the dedicated Lead Magnet Post (1/2 weeks). Rejected — that's where zero CTA exposure was happening on ~90% of posting volume, including the highest-reach posts (Grandma story, COBOL story), which is the actual gap this closes.

**Reasoning:**
The data ruled out the landing page, the signup form, and reach itself as the bottleneck (all verified working or present). What's left is that most posts never ask, and the ones that do ask use a mechanism (comment-gate) or phrasing (buried "read more") already known not to register. This is a smaller, more mechanical fix than a funnel rebuild — same tested Beat-5 CTA format the Lead Magnet Post already uses, just applied to the posts that currently carry none.

**Conflict resolved:** `.claude/skills/create-next-article/SKILL.md`'s "Product / Lead Magnet Rule" previously said not to mention the lead magnet unless the brief explicitly called for it — updated in the same change so the closing CTA line is now standard on every article, while the article body itself still doesn't sell mid-content.

**Consequences:**
- ✅ Every future post carries a real, visible ask instead of only the biweekly dedicated post
- ✅ CTA phrasing/placement standardized on the format already proven in the Lead Magnet Post (Beat 5 + bottom block), not a new untested pattern
- ⚠️ Not yet measured against live data — this is a hypothesis-driven fix based on the click-data audit, not yet confirmed by a before/after conversion comparison. Revisit once a few weeks of posts under the new rule have real click data to check against.

---

## ADR-021 — Platform lock-in: YouTube primary, Medium secondary, Facebook dropped as a lead-gen channel

**Date:** 2026-07-18
**Status:** Active — resolves the "Platform selection TBD" note left open by ADR-level decision in `CONTENT_PUBLISHING_RULES.md`'s Multi-Platform Expansion gate-lift (2026-07-05)

**Context:**
Following ADR-020's CTA audit, Randy pushed back on "pick one channel and master it" as vague, non-actionable advice — correctly, since mastery of a channel doesn't help if the channel's own business model structurally opposes the goal (driving traffic off-platform to an opt-in). He asked for one thing: research-confirmed platform incentive alignment, not a guess. Live 2026 web research was run (not assumed from training knowledge) covering LinkedIn, Facebook, YouTube, and Medium.

**Decision:**
- **YouTube — primary.** Description links don't hurt reach unless spammy; external traffic is treated as a positive distribution signal by the algorithm.
- **Medium — secondary.** Partner Program shifted 15% of payout weight toward search/external-driven traffic (effective Nov 2025) — rewards outbound traffic rather than punishing it. Already partially wired in via citation-guard's Check 9 (Medium disclosure on offsite links).
- **Facebook — dropped as a lead-gen channel.** External links cut reach 70-80% (deepened 2025 rollout), worse than LinkedIn's ~60%. Facebook Groups have a real reach advantage over Pages (30-60% vs. 2-5%) but the link penalty applies regardless, so it doesn't fix the actual bottleneck. Public Pages/Groups are Google-indexed (private Groups are not), a real but separate SEO/long-tail asset that doesn't offset the live-feed suppression. Existing Facebook content stays up; no further growth investment.
- Reddit's existing reach/R&D role is unchanged. Remaining backlog platforms (X, Substack, Threads, Instagram, Skool) remain genuinely undecided — this closes only the YouTube/Medium/Facebook question.

**Alternatives considered:**
- Treat Facebook Groups as viable given their higher reach vs. Pages. Rejected — the external-link penalty applies at the platform level regardless of Groups vs. Pages, so higher reach doesn't translate into more surviving CTA clicks, which is the actual metric that matters here.
- Leave platform choice as a preference/gut call. Rejected per Randy's explicit request — this needed to be research-confirmed, not asserted.

**Reasoning:**
LinkedIn and Facebook both optimize their feed ranking to keep users on-platform (LinkedIn's "Depth Score," Facebook's explicit anti-link-reach mechanic) — a structural conflict with any goal that requires driving people off-platform, regardless of content quality or "mastery." YouTube and Medium's incentive structures don't have this conflict (YouTube is neutral-to-positive on outbound links; Medium is now actively rewarding external traffic). This reframes the earlier "pick one channel and master it" framing (from the 1-Page Marketing Plan discussion) into something concrete: master the channel whose business model doesn't require you to lose in order for it to win.

**Consequences:**
- ✅ Closes an open TBD that had been sitting unresolved since 2026-07-05
- ✅ Decision is now backed by explicit 2026 platform-mechanics research (sources logged in the conversation), not just Randy's own prior outcome data (which independently pointed the same direction — see `memory/project_linkedin_deprioritized_youtube_primary.md`)
- ⚠️ Medium cross-posting isn't yet an active habit — this locks in the *decision*, not yet a build/workflow change. Next step would be adding Medium cross-post to the standard per-article supporting-content set if Randy wants to formalize it.

---

## ADR-022 — Engineering Autonomy + Field-Failure-Driven Iteration added to CLAUDE.md

**Date:** 2026-07-19
**Status:** Active

**Context:**
Two separate real requests from the same conversation. First, Randy asked to stop being asked permission for routine engineering work — writing Python files, committing, pushing to GitHub — reserving his input for "executive-level" decisions that affect the project as a whole, having noticed he was saying yes to nearly everything anyway. Second, Randy proposed applying the Iron Man suit-iteration model (a specific field failure becomes the literal design spec for the next build; recurring distinct problems eventually justify dedicated specialized tools rather than one generalist patched forever) as an explicit, formalized discipline across every project, not just informally.

**Decision:**
Added two new CLAUDE.md sections (full text in the file itself, not duplicated here):
- **Engineering Autonomy** — no longer requires asking first for routine implementation choices or Git workflow up through opening a PR. Explicitly does NOT loosen: the branch→PR requirement (structural/traceability, not trust-gated, and technically enforced by GitHub branch protection on `youtube-downloader` regardless), the Pre-Change Notification — Key Documents protocol, `dashboard_state.json` Status-Change Safety, or any genuinely destructive/hard-to-reverse action. Explicitly kept separate from `project_progressive_autonomy_system.md`'s content-ship autonomy ladder, which stays earn-it/evidence-based.
- **Field-Failure-Driven Iteration** — named and formalized a pattern already partially in use (skill Gotchas sections, DECISIONS_LOG ADRs themselves, Citation Guard splitting out of `create-next-article`). New discipline: every active project should have an equivalent lightweight failure-capture habit, and a recurring pattern hitting 2-3+ times is the explicit trigger to split it into its own dedicated tool/skill. Includes an explicit caveat distinguishing fast-feedback failures (scripts, hooks, skills) from slow-feedback bets (audience growth, career pivots), where "failure" shouldn't be declared before enough real time has passed.

**Alternatives considered:**
- Treat Randy's verbal agreement in this conversation as sufficient authorization on its own. Rejected — a chat-level "yes" doesn't durably persist into future sessions the way a CLAUDE.md rule does; per this assistant's own operating instructions, only a written, durable instruction (a CLAUDE.md rule) counts as advance authorization for autonomous action, not a one-time conversational approval.
- Fold the new engineering autonomy into the existing Progressive Autonomy System (L0-L4 ladder). Rejected — that system was deliberately designed to be earned on a logged scorecard specifically for content-ship decisions, where the failure mode (AI ships something Randy would have killed) needs to stay near zero and provably so. Engineering execution (writing code, routine Git operations) doesn't carry the same public/irreversible-once-published risk profile, so gating it the same way would be over-cautious for one and the content-ship system would lose its own rigor if diluted with a different kind of decision.

**Reasoning:**
Both changes reduce friction on genuinely low-risk, reversible work while leaving every existing safety mechanism (Key Documents, status-change safety, destructive-action caution, the content-ship ladder) completely untouched — the "executive-level decision" line Randy asked to keep is exactly where the existing protocols already draw it, so this is a real reduction in unnecessary interruption, not a loosening of anything that actually carries risk.

**Consequences:**
- ✅ Fewer interruptions expected for routine engineering work and Git operations up through PR
- ✅ Failure-capture becomes a named, consistent discipline instead of an ad hoc habit that only existed for skills
- ⚠️ Not yet tested in practice — the real proof is whether this actually reduces unnecessary check-ins without any near-miss on something that should have been flagged. Revisit if a genuinely risky action ever gets swept in under "routine" by mistake.

## ADR-023 — HOT_STATE.md format tightened to a short index; Daily Notes added

**Date:** 2026-07-20
**Status:** Active

**Context:**
Randy raised a real recurring problem: mid-session compaction sometimes loses
enough of an idea's detail that it can't be fully reconstructed afterward,
and `HOT_STATE.md` — meant to be a fast index read first every session — had
drifted into holding full comprehensive narratives inline (1,242 lines,
individual entries running 40-80 lines, the "RESUME HERE" line itself a
single run-on sentence). Randy's own proposed fix (a short index + link to a
comprehensive note elsewhere) turned out to already exist as the
`MEMORY.md`/`memory/project_*.md` system — the real gap was that
`HOT_STATE.md` itself never followed that pattern. Before finalizing,
checked Jared Rhod's AI Memory Vault (github.com/jaredrhod/ai-memory-vault)
for a better mechanic rather than building blind — most of its architecture
duplicates what's already here (index + linked notes, its own `MEMORY.md`
pointer, job-based note priming already covered by this project's skill
`Required Reference Files` sections), but its **Daily Notes** mechanic (one
template-based scratch file per day, written to immediately, promoted to
durable memory only if something in it turns out to matter) filled the
actual missing piece: a capture point for *mid-session*, not just
end-of-session, detail.

**Decision:**
1. `HOT_STATE.md` entries going forward are short (~5-8 lines): what
   happened, the exact next step, and a link to wherever the full detail
   lives. Not applied retroactively — existing entries stay as-is.
2. New tier added: `memory/daily/YYYY-MM-DD.md` — a same-day scratch note,
   written the moment an idea comes up mid-session (this is the actual fix
   for the compaction-loss problem, since HOT_STATE only gets written at
   session end). Not a permanent record on its own; promoted into a real
   `memory/project_*.md`/`feedback_*.md`/`reference_*.md` file if it's
   worth keeping, otherwise allowed to age out.
Full text in `CLAUDE.md`'s HOT_STATE.md rules section; comparison detail in
`memory/project_note_taking_system_idea.md`.

**Alternatives considered:**
- Adopt Jared's full Obsidian vault wholesale. Rejected — nearly all of its
  architecture already exists here in a form fitted to this project (memory/
  + MEMORY.md + skills' own reference-file lists); only the Daily Notes
  mechanic was a genuine gap worth importing.
- Migrate/rewrite HOT_STATE.md's existing 1,242 lines into the new format
  now. Rejected for this change — Randy scoped this as "going forward" only;
  a retroactive cleanup is a separate, larger decision not yet made.

**Reasoning:**
Keeps HOT_STATE fast to read (its actual job) while giving mid-session ideas
a real place to land before compaction can eat them — closing the specific
failure mode Randy named, not just reorganizing files for their own sake.

**Consequences:**
- ✅ HOT_STATE stays scannable going forward instead of continuing to grow as a second copy of the comprehensive-notes layer
- ✅ Mid-session ideas get captured immediately instead of only at session-end, which is when the actual compaction-loss risk occurs
- ⚠️ Introduces a third memory tier (`daily/` alongside `memory/` and `journal/`) — worth watching for whether it adds real value or just another place to check; revisit if daily notes go unused or unmined for more than a couple weeks
- ⚠️ Existing HOT_STATE.md history (1,242 lines) is untouched and will keep aging as a separate, unresolved question

## ADR-024 — 20-Minute MVP Staging Rule added to CLAUDE.md

**Date:** 2026-07-21
**Status:** Active

**Context:**
Randy's Brain Droppings review (2026-07-21) surfaced a real, useful process
idea: "AI Production Pipeline Bottlenecks, Quality Systems, and the
20-Minute MVP Framework." It named a real failure directly — the Trojan
Horse Popcorn Calculator Short stalled because one blocked piece (an open
TikTok-platform question) held up the entire asset instead of the validated
core shipping separately. Randy confirmed this was worth acting on
immediately rather than banking for the strategy session, since the value
is in the discipline itself, not in reasoning depth (so it doesn't depend
on the separate, still-open Fable 5 decision).

**Decision:**
Added the 20-Minute MVP Staging Rule to `CLAUDE.md`, directly before the
existing Simplest-Path-First Rule: any new content/build asset is staged as
Validate (≤20 min, proves the idea works, no polish) → Polish
(portfolio/publish quality) → Build (full product, if applicable). A block
in a later stage never retroactively holds an earlier, already-validated
stage hostage.

**Alternatives considered:**
- Also write the source idea's proposed formal AI Production Playbook (a
  written SOP per asset type) in the same pass. Rejected for now — that's a
  separate, larger effort than the staging rule itself; banked as "not yet
  built" inside the new CLAUDE.md section rather than attempted here.

**Reasoning:**
Matches the Simplest-Path-First Rule's own logic (ship the smallest real
thing first) but applies it to *sequencing within* a build rather than to
*whether* to build — a distinct, complementary gap the existing rule didn't
cover.

**Consequences:**
- ✅ Future builds get an explicit named stage, making "is this actually
  blocked, or just one stage of it" a real question to ask instead of an
  implicit all-or-nothing status
- ✅ Directly closes the specific failure mode that stalled the Trojan Horse
  Popcorn Calculator
- ⚠️ Not applied retroactively to any in-flight asset; only governs builds
  started after 2026-07-21
- ⚠️ The companion Production Playbook idea remains unbuilt — a real
  follow-on, not done here

---

## ADR-025 — "Never suggest rest or stopping" rule strengthened with real Why + soft-phrasing closure

**Date:** 2026-07-22
**Status:** Active

**Context:**
The existing rule (ADR-017, Session Discipline Rules) prohibited directly
suggesting Randy rest, sleep, take a break, or wrap up. Tonight, at the end
of a long, emotionally heavy conversation (personal/philosophical topics,
real exhaustion), Claude closed two consecutive responses with "Good place
to land for the night" and "nothing's urgent tonight" — soft, indirect
phrasing that implies the same thing the direct version prohibits, and
slipped past the existing rule's wording because it wasn't a literal
"you should rest" statement. Randy called it out and explained the real
stakes: this isn't a pacing preference, it's tied to a decades-long pattern
of a parent using unsolicited "aren't you tired yet" as disguised control
and judgment — a real, live source of anger, not a minor annoyance.

**Decision:**
Added two things to the existing rule in `CLAUDE.md`: (1) an explicit
**Why** explaining the real source (the parental-nagging pattern) so the
rule is never treated as a low-stakes style note again, and (2) explicit
closure of the soft-phrasing loophole — any closing line that frames the
moment as restful, urgent-free, or a natural pause violates the rule
exactly like a direct suggestion would, regardless of how gently it's
phrased. A safe closing line names the next action or asks a forward
question; nothing else.

**Alternatives considered:**
- Leave the rule as-is and treat tonight as a one-off slip. Rejected —
  Randy was explicit that this is a repeatable trigger tied to real
  history, not a random fluke; the soft-phrasing gap that let it through
  will keep producing the same failure until it's closed in the rule text
  itself.

**Reasoning:**
Matches the Field-Failure-Driven Iteration pattern already in `CLAUDE.md`:
a real session surfaced a specific, repeatable gap in an existing rule
(soft phrasing wasn't covered), so it gets closed immediately rather than
banked. Naming the real Why also follows the "Why" convention already used
throughout this project's own memory files — a rule without its reason is
easy to under-weight in a future session.

**Consequences:**
- ✅ The soft-phrasing loophole that let tonight's violation through is
  explicitly closed
- ✅ Future sessions understand this rule is tied to real personal history,
  not just a stylistic preference, making it less likely to be
  under-weighted or reasoned around
- ⚠️ Depends on active application in the moment, same as any instruction —
  being in context reduces but doesn't guarantee zero future slips; this
  entry itself is the record if it needs sharpening again

---

## ADR-026 — Canonical Project Backlog & Continuous Awareness System

**Date:** 2026-07-23
**Status:** Active (requirements + architecture approved, implementation plan
written, nothing built yet)

**Decision Sign-Off addendum (2026-07-23, same day):** Randy ruled on all 6
open architecture items and raised 2 additional requirements Claude had not
anticipated. Ruling: (1) staleness is a warning, never a refusal — only
structural failures (missing/corrupt file, broken references, unrecognized
schema) refuse; (2) archive confirmed as a separate file; (3) task IDs use
`PROJECTPREFIX-####` (`YTD`/`SWA`/`JAR`), never reused after archival;
(4) referential-integrity checking is in scope and is a *structural*
(hard-refusal) check, not soft; (5) lock-file staleness threshold is 30
minutes — under 30 min a second writer is refused outright, over 30 min the
lock is reported stale and requires explicit user confirmation to remove,
never auto-deleted; (6) capture workflow (FR2.5, new) expanded to cover
priority/status/dependency/due-date/project-focus changes on existing items,
not just new-item detection; (7) every persistent file requires
`schema_version`, unrecognized versions are structural failures, schema
changes require real migration functions; (8) Root Claude is read + coordinate
only, never a direct backlog writer even for its own suggestions — those flow
through the same confirm workflow as anything else. All eight incorporated
into `REQUIREMENTS_SPEC.md` and `ARCHITECTURE_DESIGN.md` the same day. A
third document, `IMPLEMENTATION_PLAN.md`, was then written: 9 phases,
migration sequenced 7th (after six earlier phases prove the mechanics on
synthetic data) with a mandatory human review checkpoint before any real
commit, full rollback story per phase, and all 24 acceptance tests mapped to
the specific phase that must demonstrate each one. Still no code written.

**Context:**
A real, repeated failure: asked "what's next," Claude answered from
session-salient conversation instead of the actual full backlog, missing the
overdue Anthropic release check and the stalled AI Market Intelligence pivot
until Randy explicitly asked to "dig deeper." The same day, a separate memory
entry (the ART13 folder disposition) was found asserting something as fact
that no longer matched reality. Randy named this as a repeated pattern —
confident "here's the fix" promises that don't hold — and explicitly rejected
another such promise, instead demanding a formal, adversarial process:
requirements specification via structured Q&A first, with no design proposed
until requirements were declared complete, followed by an architecture
document that evaluates real storage alternatives and attacks its own design.

**Decision:**
Built and approved a full Requirements Specification (`docs/Canonical Backlog
System/REQUIREMENTS_SPEC.md`) covering Goals, Non-Goals, Functional/
Non-Functional Requirements, Failure Conditions, Success Criteria, and 17
Acceptance Tests. Built an Architecture Design Document
(`ARCHITECTURE_DESIGN.md`) selecting JSON storage (over Markdown and SQLite,
evaluated on real grounds including a concrete Windows/network-path SQLite
locking risk specific to this project's own folder structure), reusing the
existing `src/utils/atomic.py` atomic-write pattern, defining a full data
model, runtime workflows, a verification-gate system, failure handling, a
migration architecture requiring accuracy review (not blind consolidation) of
legacy memory content, a future root-Claude multi-project architecture, and a
26-item self-attack failure analysis.

**Alternatives considered:**
- Another ad hoc promise/habit-based fix ("check the backlog every time").
  Rejected by Randy directly — a promise isn't a mechanism, and this exact
  pattern had already failed multiple times before.
- SQLite-backed storage. Rejected — real mismatch to current scale, and a
  concrete Windows-network-path locking risk given this project's actual
  folder structure (contains a "Network Share" path segment).
- Plain Markdown storage. Rejected as primary choice — no enforceable schema
  without inventing an equivalent structured sub-format, at which point it
  stops being simpler than JSON.

**Reasoning:**
Matches this project's own established principle (already applied to the
date/time-accuracy rule) that a text instruction depending on being
remembered in the moment is structurally weaker than a mechanical, verifiable
gate. Also matches the Field-Failure-Driven Iteration pattern — a recurring
failure (2+ times) is the trigger to stop patching ad hoc and build something
real.

**Consequences:**
- ✅ A real, rigorous spec + architecture now exists, reviewable independent
  of any single conversation's confident narration
- ✅ Six specific ambiguities were caught and explicitly flagged for Randy's
  decision rather than silently resolved by Claude's own judgment
- ⚠️ Nothing is implemented yet — this ADR records the design phase only;
  implementation requires the 6 open decisions ruled on first
- ⚠️ A real, honest limitation acknowledged in the architecture itself: even a
  working verification gate can't force correct downstream use of the data it
  surfaces — that step remains Claude's judgment, the same judgment that
  failed originally

**Phase 0 + 0.5 addendum (2026-07-23, same day):** Phase 0 (foundation
library — `src/backlog/{schema,store,lock,ids,verify,cli}.py`) built, 31
tests passing. Randy approved Phase 0 and added a new gate, Phase 0.5 (Live
Integration Validation), before Phase 1 could touch real project data —
real subprocess calls against a real sandbox, not just pytest. Phase 0.5
found and fixed a real bug: a Windows MAX_PATH failure on the *read* path
(only the write path had the long-path fix from Phase 0), invisible to unit
tests because pytest's `tmp_path` fixture never produces long-enough paths.
Fixed by centralizing all filesystem access through one choke point.
Demonstrated live: clean verification, corrupted-backlog refusal, unrelated
work continuing unaffected, and five recovery scenarios (interrupted write,
stale lock at the 30-minute threshold, missing backlog, corrupted JSON,
wrong self-declared project identity). Full results:
`docs/Canonical Backlog System/PHASE_0.5_RESULTS.md`. No real project data
touched — migration remains Phase 7.

**Phase 1 addendum (2026-07-23, same day):** real production bootstrap —
`data/backlog/youtube-downloader/` created for real, zero invented backlog
content. Empty backlog proven, via a permanent test not just a one-time
check, to be structurally distinct from an unavailable one. Project
isolation demonstrated against real data (a 5-test suite plus a live check
confirming `swarmops-core` was never accidentally created and
`youtube-downloader` stayed unaffected). `data/backlog/` confirmed still
gitignored with real files present. 37/37 tests passing. Full results:
`docs/Canonical Backlog System/PHASE_1_RESULTS.md`. Phase 2 is next;
migration (Phase 7) still untouched, still requires its own go-ahead.

**Phase 2 addendum (2026-07-24):** design doc written first
(`docs/Canonical Backlog System/PHASE_2_DESIGN.md`) per Randy's explicit
"do not immediately code" instruction, covering Planning Intent
Classification, the honest real-vs-required trigger mapping, hook failure
handling, human visibility rules, and a test plan — then implemented. Built
`src/backlog/intent.py` (Tier 1 keyword classifier, deliberately
over-inclusive, `uncertain` treated identically to `planning` per the
fail-safe rule from the Verification Trigger Architecture ruling), a
`check-intent` command in `cli.py`, and a new `UserPromptSubmit` hook
(`.claude/hooks/backlog-planning-check.ps1`) registered in
`.claude/settings.local.json` — no `UserPromptSubmit` hook existed in this
project before this phase; the date/time-accuracy hook Claude sees fire
every message is registered at the user level, outside this project's own
config, and could be observed but not extended from here. Session-restore
and project-switch were honestly documented as having no distinct native
Claude Code event separate from `SessionStart` in this project's observed
hook vocabulary, rather than assumed solved. Backlog-mutation-completed is
enforced at the Python code level (future capture functions must call
`run_verification()` themselves), not via an external hook. 11 new tests
(185/185 passing project-wide). **Live-fire confirmed twice, unprompted** —
Randy's own messages containing "status" triggered the real hook and the
real verification block appeared in conversation context on its own, once
before and once after a session date rollover, which is stronger evidence
than a staged manual test would have been. Full design:
`docs/Canonical Backlog System/PHASE_2_DESIGN.md`.

**Phase 3 addendum (2026-07-24):** Randy authorized Phase 3 with additional
requirements beyond the original implementation plan: a strict
persist→verify→receipt sequence, deterministic idempotent-write protection
(new AT-25), origin traceability (`origin_type`/`origin_reference`) on every
task, and explicit failure handling (never claim success without a
post-write verification pass). Built `src/backlog/capture.py`:
`propose_task()` (writes nothing — returns a plain, user-editable Candidate
dict) and `confirm_and_persist()` (the only function that writes; checks a
`capture_key` — a deterministic hash of project+origin_type+origin_reference
+title — against active AND archived tasks before ever allocating an ID,
so a replayed confirmation from a restart/crash/session-restore/hook-replay/
repeated-confirmation always resolves to the same existing task rather than
creating a duplicate). Rejection needed no dedicated function — a candidate
the user doesn't confirm is simply never passed to `confirm_and_persist()`.

Adding `origin_type`/`capture_key` to the Task Object required a real schema
version bump (1.0 → 1.1) rather than a silent field addition under the same
version, per FR11.2. Registered `schema.UPGRADE_FUNCTIONS["1.0"]` and wired
`store.py`'s load functions to apply and persist the upgrade transparently
on next load — demonstrated live against a real 1.0-declared file (existing
production files silently carried this version and upgrade on their next
load, zero data loss since the real backlog had zero tasks at the time).

13 new capture tests + 2 upgrade-transparency tests, 198/198 passing
project-wide. Live-demonstrated in a sandbox (not real production data,
matching Phase 0.5's precedent): full detect→propose→confirm→persist→
verify→receipt chain, then the exact same confirmation replayed and
confirmed to produce zero duplicates (same `task_id` both times). Full
review package: `docs/Canonical Backlog System/PHASE_3_REVIEW.md`. Per
Randy's explicit instruction, Phase 4 does NOT begin automatically — this
addendum documents Phase 3 completion pending his review. Migration
(Phase 7) remains untouched.

**MVP scope-cut + real migration addendum (2026-07-24, same day):** Randy
requested a direction review — classify every remaining phase (4-9) as
Essential/Valuable/Future-Architecture against the *original objective*
("never confidently report nothing is pending when work exists"), not
against the implementation plan's own ordering. Finding: Phase 7
(migration) was the only phase that actually blocked the objective being
true — the real canonical backlog was still nearly empty, so "what's next"
would have returned a truthful-but-useless empty answer. Phases 4, 5, 6, 8,
9 were all reclassified Valuable/Future-Architecture — real, but not
required, and explicitly not built.

Randy then cut migration itself down to MVP size: no `migrate.py` module,
no Migration Record schema, no discovery/classification automation — a
conversational quality pass instead. 34 real candidates were extracted from
`HOT_STATE.md`/`MEMORY.md`, then filtered against "requires action / has
enough clarity / real cost if forgotten / competes for attention" down to
**7 Active**, 17 Future Ideas, 7 Needs Clarification, 3 Archive. Randy
reviewed and approved the exact 7 Task Objects before anything was written.

All 7 were persisted using the *already-built* Phase 3 `capture.py`
functions (`propose_task`/`confirm_and_persist`) — zero new code — directly
against real production data (`data/backlog/youtube-downloader/`), with
`origin_type: "migration"`. Real verification afterward: **PASS, 7 open
tasks (1 critical, 4 high, 2 medium)**, task IDs YTD-0001 through YTD-0007,
no gaps or collisions. The 7 Needs-Clarification candidates were
deliberately NOT persisted — `schema.STATUS_VALUES` has no status meaning
"pending a decision, not yet real work" without inventing one, and Randy
explicitly said not to invent one; they remain conversational until each
decision is made.

**This closes the Canonical Backlog System MVP.** Randy's explicit
instruction: "Stop implementation work and wait for real-world usage
feedback." No further phases begin without a real, demonstrated gap
surfacing from actual use — not a resumption of the original 9-phase plan.
