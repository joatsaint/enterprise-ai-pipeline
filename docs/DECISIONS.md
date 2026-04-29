# DECISIONS.md
## Architectural Decision Log — YouTube Transcript Downloader

**Version:** 2.0
**Owner:** Randy Skiles
**Last updated:** April 29 2026

---

## Why This Document Exists

AI-assisted development has a fundamental problem: session amnesia. Each Claude Code
session starts with no memory of previous decisions. Without a decision log, the same
architectural questions get re-litigated every session — often with different answers.

This document also serves as a portfolio artifact. When an interviewer asks "walk me
through your architectural decisions," this document is the answer. Every entry
demonstrates the shift from vibe coding to vibe engineering: deliberate choices made
with explicit tradeoffs acknowledged.

**Read this file at the start of every Claude Code session before writing any code.**

---

## Decision Log Format

Each entry follows this structure:

- **Context:** The situation that forced a decision
- **Decision:** What was chosen
- **Alternatives considered:** What else was evaluated
- **Reasoning:** Why this option won
- **Consequences:** What this decision costs and gains
- **Status:** Active / Superseded / Deprecated / Deferred

---

## ADR-001 — Orchestrator Pattern for Pipeline Coordination
**Date:** Phase 1, April 2026
**Status:** Active

**Context:**
The pipeline has multiple sequential steps: URL validation → transcript fetch →
category classification → Markdown conversion → file write → index update.
Each step can fail independently. Multiple modules need to share state about
the current video being processed.

**Decision:**
Single `orchestrator.py` owns the entire pipeline. All other modules are
called by the orchestrator. State is passed explicitly via a `state` dictionary
object, not via global variables or module-level state.

**Alternatives considered:**
- Event-driven pipeline (each module emits events to a queue)
- Direct module-to-module calls (downloader calls converter calls indexer)
- Global state object shared across modules

**Reasoning:**
Event-driven adds complexity that isn't justified at this scale. Direct
module-to-module calls create tight coupling — changing one module breaks
callers. Global state makes debugging impossible. Explicit state passed through
the orchestrator means any failure is traceable to a specific step with full
context available.

**Consequences:**
- ✅ Failures are isolated to specific steps with clear logging
- ✅ Each module can be tested independently with a mock state object
- ✅ Adding a new pipeline step requires changes only in orchestrator.py
- ⚠️ Orchestrator.py grows large — must be actively managed to stay readable
- ⚠️ All state changes must go through the orchestrator, not modules directly

**State object schema:**
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

---

## ADR-002 — Haiku Model for Pain Point Extraction
**Date:** Phase 3, April 2026
**Status:** Active

**Context:**
Pain point extraction runs Claude API calls against up to 50 transcript files
plus comment files per run. Model choice directly determines cost per run and
therefore whether the system is economically viable to run regularly.

**Decision:**
Use `claude-haiku-4-5-20251001` for all pain point extraction analysis.

**Alternatives considered:**
- Claude Sonnet (higher quality, ~3-4x cost)
- Claude Opus (highest quality, ~15x cost)
- Local model via Ollama (zero API cost, lower quality, setup complexity)

**Reasoning:**
Pain point extraction is a classification and summarization task, not a
reasoning task. Haiku performs adequately for identifying repeated questions
and themes across transcripts. Measured cost: ~$0.10 per 50-file run.
At Sonnet pricing this would be ~$0.35-$0.40/run, making weekly runs significantly
more expensive. Quality difference for this specific task does not justify
the cost difference.

**Consequences:**
- ✅ ~$0.10 per full analysis run — economically viable to run weekly
- ✅ Same model keeps output format consistent across runs
- ⚠️ Haiku may miss subtle thematic connections that Sonnet would catch
- ⚠️ If extraction quality degrades, upgrade to Sonnet before adding complexity

**Upgrade trigger:** If pain point reports start producing obviously wrong or
generic outputs, upgrade to Sonnet and re-run comparison before assuming
prompt changes are needed.

---

## ADR-003 — Webshare Rotating Residential Proxy
**Date:** Phase 2, April 2026
**Status:** Active

**Context:**
YouTube blocks transcript API requests from cloud IP addresses. Claude Code
runs in a cloud environment. Running channel batch downloads from within
Claude Code causes `TranscriptsDisabled` errors that are actually IP blocks,
not actual disabled transcripts.

**Decision:**
Use Webshare rotating residential proxy ($3.50/month) for all transcript
fetch operations. Channel downloads must be run from local PowerShell
terminal, not the Claude Code terminal.

**Alternatives considered:**
- Fixed residential proxy (cheaper, but single IP gets flagged faster)
- VPN (not programmatically controllable from Python)
- Running entirely on local machine without Claude Code (eliminates cloud issue)
- Scraping via browser automation with Playwright (more complex, more detectable)

**Reasoning:**
Rotating residential IPs are the industry standard for avoiding YouTube's
bot detection. Fixed IPs exhaust their reputation faster. VPNs cannot be
controlled via Python's requests library. Local-only operation limits
development flexibility. Webshare's Python integration is documented and
straightforward. At $3.50/month the cost is negligible relative to the
value of the transcript library.

**Consequences:**
- ✅ Reliable transcript fetching at scale without manual intervention
- ✅ Randomized IP rotation reduces bot signature
- ⚠️ $3.50/month recurring cost — must be tracked as operating expense
- ⚠️ Channel downloads MUST run from PowerShell, not Claude Code terminal
- ⚠️ Proxy credentials in .env — must never be committed to GitHub

**Operational note:** This is documented in GUIDE.md troubleshooting section.
If transcripts start failing en masse, check Webshare dashboard for quota
status before assuming a code problem.

---

## ADR-004 — Flat File Index Over Vector Database
**Date:** Phase 3, April 2026
**Status:** Active — review at 500+ transcripts

**Context:**
The knowledge base needs to support querying across 159+ transcripts.
Options range from simple flat file scanning to a full vector database
with semantic search.

**Decision:**
Use flat file JSON index (`knowledge_base/index.json`) with keyword-based
search. No vector database at this stage.

**Alternatives considered:**
- ChromaDB (local vector database, semantic search)
- Pinecone (cloud vector database, requires API key + cost)
- SQLite (relational, fast for structured queries)
- Direct file scanning on each query (no index)

**Reasoning:**
At 159 transcripts, a flat file index is fast enough. Query time is
acceptable for research use (not real-time user-facing). Vector databases
add operational complexity — dependencies, embedding costs, index management
— that aren't justified until the library reaches 500+ transcripts or
semantic search becomes genuinely necessary. YAGNI (You Aren't Gonna Need It)
principle applies here. The flat file approach can be replaced later
without changing the query interface.

**Consequences:**
- ✅ Zero additional dependencies or costs
- ✅ Index is human-readable and debuggable
- ✅ Simple to back up alongside transcripts
- ⚠️ Keyword search only — no semantic "find transcripts similar to this"
- ⚠️ Performance will degrade at 500+ transcripts — revisit threshold

**Upgrade trigger:** If query response time exceeds 5 seconds or the library
reaches 500 transcripts, evaluate ChromaDB as the first upgrade path.

---

## ADR-005 — Randomized Rate Limiting
**Date:** Phase 2, April 2026
**Status:** Active

**Context:**
API requests to YouTube sent at fixed intervals create a recognizable
bot signature. Fixed 2-second delays are trivially detectable by
YouTube's bot detection systems.

**Decision:**
All rate limiting uses `random.uniform(low, high)` with two modes:
- Normal mode: 2-5 second random delay between requests
- Full download mode: 4-7 second random delay between requests
Rate limiting pause is skipped after the last item in any batch.

**Alternatives considered:**
- Fixed 2-second delay (simple, detectable)
- Fixed 5-second delay (safer but slow)
- Exponential backoff (appropriate for errors, not normal operation)
- No delay (fast, high ban risk)

**Reasoning:**
Random intervals within a human-plausible range mimic organic browsing
behavior. The range was chosen based on documented YouTube API rate limit
documentation and community-verified safe ranges. Two modes allow for
faster operation when quota is less of a concern vs. during large batch
operations where sustained requests are more likely to trigger detection.

**Consequences:**
- ✅ Significantly reduced bot detection risk vs. fixed delays
- ✅ Two modes give operational flexibility
- ✅ Last-item skip prevents unnecessary wait after batch completion
- ⚠️ Adds 2-7 seconds per video — 159 videos = ~5-18 minutes download time
- ⚠️ Timing is non-deterministic — batch time estimates are ranges, not exact

---

## ADR-006 — .env File with os.environ.setdefault() Pattern
**Date:** Phase 1, April 2026
**Status:** Active

**Context:**
Multiple modules need access to API keys and configuration values.
Credentials must never appear in code or git history. The solution
must work both in local development (reading from .env file) and in
production/cloud environments (reading from system environment variables).

A security incident occurred during development where API credentials
(Anthropic API key and Kalshi password) were surfaced in context during
a Claude Code session. Both were rotated immediately. Git history was
confirmed clean. This decision formalizes the lessons learned.

**Decision:**
Each module that needs credentials implements `_load_env()` at module
import time using `os.environ.setdefault()`. This loads `.env` file
values only if the key is not already set in the system environment.
.env files are never committed to GitHub, never synced to cloud storage
(OneDrive, Google Drive, Dropbox), and never displayed in terminal output.

**Alternatives considered:**
- `python-dotenv` library (standard approach, adds dependency)
- Config file (config.py with constants — not suitable for secrets)
- Single credentials module imported by all others
- Secret manager (AWS Secrets Manager, Azure Key Vault — overkill for this scale)

**Reasoning:**
`os.environ.setdefault()` means system environment variables take
precedence over `.env` file values. This is the correct behavior for
deployment — you set real credentials in the server environment and
the `.env` file is for local development only. Avoiding `python-dotenv`
reduces dependencies. The pattern is consistent across all modules that
need credentials.

**Consequences:**
- ✅ Works in both local development and cloud deployment without code changes
- ✅ System environment overrides .env — correct deployment behavior
- ✅ No additional dependencies required
- ⚠️ Pattern duplicated across 4 modules — if it needs to change, change all 4
- ⚠️ No validation that required keys are present at startup — fails at use time

**Future improvement:** Add a startup validation function that checks for
required environment variables and fails fast with a clear error message
if any are missing.

**Security rules (non-negotiable):**
- NEVER print, log, or display any API key — not fully, not partially
- NEVER commit .env to GitHub under any circumstances
- If .env appears in git status at any point, stop all operations immediately
- If a key is exposed, rotate it immediately before continuing any work

---

## ADR-007 — Comments Weighted Higher Than Transcripts in Pain Point Analysis
**Date:** Phase 3, April 2026
**Status:** Active

**Context:**
Pain point extraction analyzes both video transcripts and YouTube comment files.
The question was whether to treat both equally or weight one type higher.

**Decision:**
Comments are weighted higher than transcripts for question and pain point
signals. The extractor prioritizes comment file analysis for identifying
what the audience is struggling with.

**Alternatives considered:**
- Equal weighting (simpler, no distinction)
- Transcripts weighted higher (creator's framing over audience response)
- Comments only (ignore transcript content entirely)

**Reasoning:**
Transcripts reflect what the content creator thinks is important.
Comments reflect what the audience is actually confused about, struggling
with, and asking. For the purpose of identifying PDF topic opportunities,
audience pain points are more valuable than creator framing. A creator
can cover a topic confidently while the audience comment section reveals
that nobody actually understood it or could apply it.

**Consequences:**
- ✅ Pain point reports reflect real audience behavior, not creator assumptions
- ✅ Validated by results: comment analysis surfaced more specific questions
- ⚠️ Requires comment files to exist — channels with disabled comments
  produce lower-quality pain point reports
- ⚠️ Comment quality varies — spam, off-topic comments add noise

---

## ADR-008 — Two-Pass Extraction (Questions Then Pain Points)
**Date:** Phase 3, April 2026
**Status:** Active

**Context:**
Initial single-pass pain point extraction produced mixed output that
blended questions, frustrations, and desired outcomes together in ways
that were hard to act on for PDF topic selection.

**Decision:**
Two-pass extraction approach: first pass identifies questions, second pass
identifies pain points and desired outcomes. Results are kept separate in
the output report.

**Alternatives considered:**
- Single pass extracting everything at once (faster, less structured)
- Three passes (questions, pain points, opportunities — more granular)
- One pass with structured JSON output (format enforcement, not semantic separation)

**Reasoning:**
Questions and pain points serve different content purposes. A question
("How do I get an AI job?") maps to a how-to guide. A pain point
("I don't know which skills to learn") maps to a decision framework.
Separating them during extraction produces more actionable output for
content planning. Two passes is the minimum that achieves this without
excessive API cost.

**Consequences:**
- ✅ Output is directly usable for PDF topic selection without re-processing
- ✅ Questions and pain points mapped separately — different content types
- ⚠️ Two API calls per batch instead of one — slightly higher cost
- ⚠️ Requires consistent prompt design across both passes

---

## ADR-009 — Claude Code as Primary Development Platform
**Date:** April 27 2026
**Status:** Active

**Context:**
Question arose whether to diversify AI development platforms (Cursor,
GitHub Copilot, etc.) to reduce dependency and cost risk on Anthropic.

**Decision:**
All project development stays in Claude Code (Anthropic). No diversification
to other AI development platforms until after first paid sale. All code is
built model-agnostic to enable future switching if needed.

**Validated by:** LLM Council session April 27 2026 — 5-advisor analysis
confirmed this recommendation unanimously.

**Alternatives considered:**
- Cursor — evaluated, rejected at current stage due to switching cost
- GitHub Copilot — evaluated, rejected, weaker for agentic pipeline work
- Multi-platform from day one — rejected, over-engineered for current scale

**Reasoning:**
Randy has existing proficiency in Claude Code — switching costs are real.
Diversifying platforms at Stage 5 with 0 paid sales splits learning and
slows the only thing that matters: reaching first paid sale. Claude Code
is Anthropic's core revenue product — low risk of deprecation. Model-agnostic
architecture provides free insurance without extra platform cost.

**Model-agnostic implementation requirement:**
- All Claude API calls must be isolated in one module (analyzer/)
- API calls must accept a model parameter rather than hardcoding model names
- Switching to GPT-4 or Gemini must require changing one file, not many

**Consequences:**
- ✅ No switching cost, no split learning curve
- ✅ Model-agnostic pattern provides free insurance
- ⚠️ Single platform dependency — mitigated by model-agnostic architecture
- ⚠️ Monitor Anthropic pricing — if per-run cost exceeds $1.00, re-evaluate

**Trigger to revisit:**
- First paid sale confirmed, OR
- Claude API pricing increases >50% from current baseline, OR
- A specific project requirement cannot be met by Claude Code

---

## ADR-010 — Spec-First Development (No Code Before Spec)
**Date:** April 29 2026
**Status:** Active

**Context:**
Enterprise readiness audit (April 29 2026) identified three unbuilt modules
(indexer.py, query.py, digest.py) with no detailed specs in CLAUDE.md.
Code built without spec produces modules that don't integrate cleanly with
the existing orchestrator pattern.

**Decision:**
No new module is built until its full specification is written in CLAUDE.md.
The spec must include: purpose, inputs, outputs, failure modes, idempotency
behavior, CLI interface, and integration points with the orchestrator.
The orchestrator section of CLAUDE.md is the gold standard for spec quality.

**Alternatives considered:**
- Build first, document later — rejected, produces undocumentable code
- Lightweight spec (just inputs/outputs) — rejected, insufficient for enterprise grade

**Reasoning:**
Aligns with Randy's IT background — design before deploy. Spec-first forces
architectural thinking before implementation thinking. Three remaining modules
(indexer, query, digest) need specs before any code is touched.

**Consequences:**
- ✅ Every module integrates cleanly with the orchestrator from day one
- ✅ CLAUDE.md stays current as the authoritative technical reference
- ⚠️ Adds time before coding begins — this is intentional, not a bug
- ⚠️ CLAUDE.md version number must increment with every spec addition

**Modules requiring specs before build:**
- [ ] indexer.py — scans /transcripts, builds search index
- [ ] query.py — on-demand Q&A against indexed content
- [ ] digest.py — daily summary generator by channel group

---

## ADR-011 — Ghost Database Deferred
**Date:** April 29 2026
**Status:** Deferred

**Context:**
Ghost ephemeral database (MCP server integration) was evaluated as a potential
addition for storing agent intermediate states, prompt logs, and generated code.

**Decision:**
Ghost is not added to this project at current stage. Deferred until first
agentic multi-agent build begins.

**What Ghost provides:**
Ephemeral/local storage for AI agents to store prompt logs, intermediate states,
and generated code rapidly without polluting production databases. MCP server
integration allows Claude to read/write data and manage schema changes directly.

**Reasoning:**
Current project is a pipeline tool, not a multi-agent system. No intermediate
agent states need to be stored between sessions. Project stores state in flat
files (download_log.json, run_summary.json) which is sufficient for current
architecture. Adding infrastructure before it's needed creates maintenance overhead.

**Consequences:**
- ✅ No added complexity or dependencies at current stage
- ⚠️ Will need to be revisited when first agentic project begins

**Trigger to revisit:**
- LinkedIn automation agent build begins, OR
- Healthcare plan analyzer agent build begins, OR
- Any project requiring Claude to store intermediate states between agent steps

---

## Decision Backlog — To Be Documented

These decisions were made but not yet formally documented:

- [ ] Category system design (groups vs. channels vs. tags)
- [ ] Video limiter implementation (MAX_VIDEOS_DEFAULT=20)
- [ ] Markdown header format for transcripts
- [ ] Knowledge base directory structure
- [ ] Test file organization and mock strategy
- [ ] Git branching strategy

---

## Superseded Decisions

*None yet*

---

## Template — Copy This for New Decisions

```markdown
## ADR-00X — [Short Title]
**Date:** [Month Year]
**Status:** Active | Deferred | Superseded by ADR-[NUMBER]

**Context:**
[What situation forced this decision]

**Decision:**
[What was chosen, in one clear sentence]

**Alternatives considered:**
- Option A (why rejected)
- Option B (why rejected)

**Reasoning:**
[Why this option won over the alternatives]

**Consequences:**
- ✅ What this gains
- ⚠️ What this costs or risks

**Upgrade trigger:** [Optional — what would cause you to revisit this]
```

---

*Version 2.0 — April 29 2026*
*Merged from original DECISIONS.md v1.0 and April 29 2026 session decisions*
*Update this document whenever a significant architectural decision is made*
*Do not wait until "later" — session amnesia is real*
