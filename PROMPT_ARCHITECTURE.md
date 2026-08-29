# PROMPT_ARCHITECTURE.md
## How This Project Was Built Using AI-Assisted Development

**Project:** Enterprise AI Pipeline
**Owner:** Randy Skiles
**GitHub:** github.com/joatsaint/enterprise-ai-pipeline
**Last Updated:** May 2026

---

## What This Document Is

This document explains how AI was used to build this project — not just
that Claude was used, but *how* it was directed, what constraints were
given, how outputs were validated, and what patterns produced reliable
results versus what failed.

This is a portfolio document for recruiters and hiring managers evaluating
AI-assisted development capability. It demonstrates the difference between
"using AI to autocomplete code" and "directing AI to build production
systems with enterprise-grade discipline."

The core skill demonstrated here is **prompting as architecture** —
using natural language specifications to direct AI precisely enough that
the output integrates with existing systems, passes automated tests, and
doesn't require rewrites.

---

## The Methodology: Spec-First AI Development

Every module in this project followed the same sequence:

```
1. WRITE THE SPEC (human)
   ↓
2. COMMIT THE SPEC TO CLAUDE.md (human)
   ↓
3. DIRECT CLAUDE TO BUILD AGAINST THE SPEC (AI-assisted)
   ↓
4. VALIDATE OUTPUT AGAINST SPEC (human + automated tests)
   ↓
5. DOCUMENT THE ARCHITECTURAL DECISION (human)
   ↓
6. MERGE ONLY WHEN TESTS PASS (CI/CD enforced)
```

No module was built until its specification existed in `CLAUDE.md`.
No code was merged until the automated test suite passed.
No architectural decision was made without a corresponding ADR entry.

This is documented formally in **ADR-010** (Spec-First Development).

---

## How Claude Code Sessions Were Structured

### Session Opening Protocol

Every Claude Code session began with the same three steps:

```
1. Read CLAUDE.md — architectural rules and module specs
2. Read DECISIONS.md — all 11 ADRs to avoid re-litigating settled decisions
3. State the session goal — one specific deliverable, not a list
```

This solved the **session amnesia problem**: Claude Code has no memory
between sessions. Without a structured opening, the same architectural
questions get re-answered differently each time. CLAUDE.md and DECISIONS.md
serve as persistent project memory.

### Session Goal Format

Goals were stated as deliverables, not tasks:

```
❌ "Help me with the indexer"
✅ "Build indexer.py to the spec in CLAUDE.md section 4.3.
    Output must be a flat JSON file at knowledge_base/index.json.
    Must be idempotent. Must use atomic write (temp + rename).
    Tests must pass before we consider this done."
```

The difference: the second version gives Claude a definition of done,
a constraint set, and a verification method. The first version produces
a conversation. The second produces a module.

---

## Module-by-Module Prompt Patterns

### orchestrator.py — The Pipeline Coordinator

**The core directive:**
```
Build an orchestrator that owns the entire pipeline via a shared state
dictionary. No module talks to another module. All state changes go
through the orchestrator. Any failure at any step must be catchable,
loggable, and recoverable without corrupting state.
```

**Key constraint that shaped everything:**
```
The state object is the contract between the orchestrator and each module.
Define the schema first. Modules receive state in, return state out.
They do not store state internally.
```

**Why this worked:** Giving Claude an explicit state schema before asking
it to build modules meant every module had compatible interfaces from day
one. No integration debugging.

---

### transcript_fetcher.py — YouTube Transcript Download

**The anti-bot problem prompt:**
```
YouTube blocks cloud IPs. We're using Webshare rotating residential proxy.
The fetcher must route all requests through the proxy.
Rate limiting must use random.uniform(2, 5) for normal mode and
random.uniform(4, 7) for full download mode.
Fixed delays are detectable — randomization is required.
```

**The failure mode directive:**
```
Three failure types need distinct handling:
1. TranscriptsDisabled — log and skip, this video cannot be processed
2. VideoUnavailable — log and skip, not a proxy issue
3. Any other exception — log, increment retry_count, attempt retry once

Never raise an exception that stops the pipeline.
Return state with status="failed" and failure_reason populated.
```

**What this produced:** A fetcher that handles every known YouTube failure
gracefully and logs enough information to diagnose production issues
without stopping the pipeline.

---

### indexer.py — Knowledge Base Index Builder

**The idempotency requirement:**
```
The index must always be rebuilt from scratch on every run.
It is derived data — the transcripts are the source of truth.
An index built from partial data is worse than no index.
Use atomic write: write to a temp file first, then rename.
A crash during write must never produce a corrupted index.
```

**The schema directive:**
```
Index structure must support:
- Lookup by channel name
- Lookup by video ID
- Lookup by date range
- Count of transcripts per channel group
Human-readable JSON. No binary formats.
```

**Why atomic write matters:** This was the explicit constraint that
prevented a subtle production bug. Without it, a Ctrl+C during indexing
produces a partial file that silently corrupts subsequent queries.

---

### query.py — On-Demand Q&A Engine

**The RAG prompt:**
```
This is a retrieval-augmented generation implementation.
Step 1: Search the index for transcripts relevant to the query
Step 2: Load matched transcripts up to a 50,000 token budget
Step 3: Pass loaded content + query to Claude API
Step 4: Return answer with source citations (channel + video title)
Step 5: If files were excluded due to token budget, notify the user

Token budget is a hard limit. Graceful truncation is required.
The user must always know if their answer is based on partial data.
```

**The citation requirement:**
```
Every answer must include which transcripts it drew from.
Format: [Channel Name — Video Title]
Never answer without citing sources.
An uncited answer cannot be verified and has no value for research.
```

**What this produced:** A query engine that behaves like a researcher,
not a chatbot — answers are sourced, bounded, and transparent about
their limitations.

---

### pain_point_extractor.py — Two-Pass Analysis Engine

**The two-pass architecture prompt:**
```
Single-pass extraction blends questions and pain points in ways
that are hard to act on for content planning.

Pass 1 — Questions: What is the audience explicitly asking?
Pass 2 — Pain Points: What is the audience frustrated by or struggling with?

Keep passes separate. A question ("how do I get an AI job?") maps to
a how-to guide. A pain point ("I don't know which skills matter") maps
to a decision framework. Same content, different products.
```

**The cost governance constraint:**
```
Use claude-haiku-4-5-20251001 for all extraction.
This is a classification task, not a reasoning task.
Haiku is adequate. Document the model choice in ADR-002.
Target: under $0.15 per full 50-file run.
If quality degrades, upgrade to Sonnet — but only then.
```

**Why this matters for enterprise:** Showing explicit model selection
with cost reasoning demonstrates financial discipline. Most AI
practitioners don't think about this until the AWS bill arrives.

---

### digest.py — Daily Automated Summary

**The scheduling directive:**
```
The digest must run unattended on a schedule.
It reads the most recent analysis output and produces a summary
grouped by channel category (ai-and-claude-code, career-and-job-search, etc.)
Output: markdown file with date stamp.
No human input required to run. No interactive prompts.
```

**The "What to Act On" requirement:**
```
The digest is not just a summary — it must end with a section called
"What to Act On" that identifies the 2-3 most actionable content
opportunities from the analysis.

Format:
## What to Act On
1. [Specific opportunity] — [Why it's high priority]
2. [Specific opportunity] — [Why it's high priority]

A digest that summarizes without recommending action has no business value.
```

---

## Prompt Patterns That Produced Reliable Results

These patterns consistently produced better output across all modules:

### 1. Define Done Before Starting
```
"This task is complete when:
- The module passes all tests in test_[name].py
- It can be called from the orchestrator with no changes to orchestrator.py
- It handles all three failure modes documented in CLAUDE.md"
```

### 2. Constraint-First Specification
```
"Before writing any code, confirm you understand these constraints:
[list constraints]
Only proceed when you can state back what the module must NOT do."
```

### 3. The Anti-Nuclear Option
```
"Do not delete and rewrite. Make surgical edits only.
If you think a rewrite is necessary, explain why first.
I will approve or reject the rewrite before any code is changed."
```
This prevented Claude from deleting working code when it encountered
a bug. A common failure mode in AI-assisted development.

### 4. Explicit Schema First
```
"Define the complete input/output schema for this function
before writing the implementation. We agree on the contract,
then we build to it."
```

### 5. Failure Mode Enumeration
```
"List every way this module can fail before writing it.
For each failure mode, specify: log it, skip it, or stop the pipeline.
We will handle all of them explicitly. 'Unhandled exception' is not acceptable."
```

---

## Prompt Patterns That Failed

These approaches produced unreliable or unusable output:

### ❌ Vague Goals
```
"Help me build the indexer" → produced code with no clear
integration points and incompatible state schema
```

### ❌ No Definition of Done
```
"Make the tests pass" without specifying which tests,
what behavior they validate, or what the module contract is
→ produced code that gamed the tests rather than implementing behavior
```

### ❌ Asking Claude to Hold Context
```
"Remember what we discussed earlier about the state schema..."
→ session amnesia means this never works reliably
Solution: all context lives in CLAUDE.md, re-loaded every session
```

### ❌ Accepting First Output Without Validation
```
Early sessions merged Claude's first output without running tests.
This produced modules that looked correct but failed on edge cases.
Solution: never merge without green CI.
```

---

## Validation Strategy

AI-generated code was validated at three levels:

### Level 1 — Automated Tests (non-negotiable)
Every module has an independent test file. Tests use mock state objects
so modules can be tested without the full pipeline running.
CI/CD via GitHub Actions enforces green tests before any merge to master.
45 tests across 4 phases. 100% pass rate required.

### Level 2 — Spec Compliance Check (manual)
Before considering a module complete, verify against the spec in CLAUDE.md:
- Does the output format match the spec exactly?
- Are all documented failure modes handled?
- Is the CLI interface correct?
- Can it be called from the orchestrator with no changes to orchestrator.py?

### Level 3 — Live Run Validation (integration)
After unit tests pass, run the module against a small real dataset.
Automated tests catch logic errors. Live runs catch integration failures
that mocks don't surface — network behavior, file encoding, API quirks.

---

## The Enterprise Discipline Translation

The prompting patterns above are direct translations of enterprise IT
discipline into AI-assisted development:

| Enterprise IT Practice | AI Development Equivalent |
|---|---|
| Design before deploy | Spec in CLAUDE.md before any code |
| Change management documentation | ADR for every significant decision |
| Rollback plan before production | Atomic writes, graceful shutdown |
| Incident response playbook | Explicit failure mode enumeration |
| Vendor SLA documentation | ADR-009 platform strategy + upgrade triggers |
| Post-incident review | Session debrief → DECISIONS.md update |

This project was built by someone who knows what happens when systems
fail in production — and designed AI-assisted development workflows
that apply the same discipline.

---

## What This Demonstrates for Employers

1. **Prompt engineering at enterprise scale** — not single-turn queries,
   but structured multi-session development workflows with persistent
   context management

2. **AI output validation** — automated testing, spec compliance checks,
   and live integration validation — not trusting first output

3. **Cost governance** — explicit model selection with documented reasoning
   and upgrade triggers, not default to most expensive model

4. **Vendor risk management** — model-agnostic architecture designed for
   provider switching from day one (ADR-009)

5. **Institutional knowledge capture** — CLAUDE.md and DECISIONS.md as
   persistent project memory that survives session amnesia

6. **The 80/20 discipline** — AI handles the repeatable 80%, human judgment
   owns the architectural 20% that determines whether the system is
   production-ready

---

*This document is maintained alongside the codebase.*
*Last updated: May 2026*
*For questions: linkedin.com/in/randy-skiles*
