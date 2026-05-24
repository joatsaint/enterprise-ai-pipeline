# Council Transcript — 2026-05-23

## Original Question

"Council those two files for best practices" — referring to:
- `docs/Claude.md Enterprise Level Standards file created by gemini-code-1779582258979.md`
- `docs/Claude.md Enterprise Level Standards file created by ChatGPT.md`

---

## Framed Question

Randy has two AI-generated enterprise CLAUDE.md standards documents to compare. He wants to know which represents stronger guidance for Claude Code sessions, what to keep from each, and what each gets wrong. The files would serve as a general-purpose template for new projects.

**File 1 (Gemini):** Short (~40 lines), persona-driven ("elite, cynical Principal DevOps Engineer"), strong on Docker mandates and IaC, has unfilled placeholder commands in Section 5.

**File 2 (ChatGPT):** Comprehensive (~340 lines, 18+ sections), principle-based, covers observability, reliability, API design, databases, CI/CD, documentation, operational readiness.

**Context:** Randy already has a detailed project-specific CLAUDE.md for his youtube-downloader. This general template would be used for new projects.

---

## Advisor Responses

### The Contrarian

File 2 looks comprehensive until you ask: will Claude actually follow 340 lines of general guidance when a project-specific CLAUDE.md exists? No. Project-level files override or dilute general templates. The length is the bug — Claude will pattern-match on the most specific context available and treat the rest as noise.

File 1's fatal flaw is obvious: Section 5 ships with unfilled placeholders. That's not a standard, that's a draft. Any document with "[Insert build command]" in a Claude Code session will either get hallucinated values or ignored. Disqualifying.

But here's what both get wrong that nobody's asking about: neither document defines failure modes for Claude's own suggestions. They tell Claude to write tests, enforce coverage, use conventional commits — but what happens when Claude proposes a solution that violates these rules? There's no "reject your own output if X" instruction. These are aspirational lists, not behavioral constraints.

File 2's "analyze → plan → explain → implement" workflow sounds rigorous. It's actually theater. Without a forcing function — like requiring Claude to output a checklist before touching code — that workflow collapses on the first complex task.

What to keep: File 1's explicit code-as-liability framing (behavioral, not procedural) and File 2's reliability patterns (retries, circuit breakers, idempotency) — those are specific enough to constrain behavior. Everything else is documentation cosplay.

---

### The First Principles Thinker

The fundamental question Randy hasn't asked: what problem is a general-purpose CLAUDE.md actually solving?

Claude Code already knows Docker best practices. It already knows OWASP. It already knows conventional commits. Restating industry-standard knowledge in a CLAUDE.md doesn't make Claude smarter — it consumes context window space and creates maintenance overhead.

A general-purpose template should do only three things: (1) Constrain behavior that has no correct default. (2) Encode decisions that reasonable engineers disagree on. (3) Define the workflow Claude should follow before acting.

File 1 is wrong about itself: persona-definition ("cynical Principal Engineer") is theater, not instruction. File 2 is right about structure but wrong about scope — 90% of its content is Claude restating what Claude already knows. The actual value lives in four sections: Core Workflow, Decision-Making bias (maintainability over cleverness), Communication norms, and the "no TODOs / no dead code" behavioral constraints.

The correct approach: a general-purpose template should be under 50 lines, contain zero industry-standard knowledge, and consist entirely of team-specific decisions, workflow sequencing, and behavioral constraints Claude wouldn't otherwise default to. Both files fail this standard. File 2 fails more expensively.

---

### The Expansionist

File 2 wins on architecture, but both documents are thinking too small.

The real opportunity is building a CLAUDE.md that functions as a compounding asset — one that gets smarter as Randy builds more projects. Neither document captures this.

What File 2 gets right that's undervalued: the workflow loop (analyze → plan → explain → implement → test → validate → summarize). That "summarize" step is gold nobody's talking about. If Claude summarizes decisions at session end, Randy accumulates an institutional memory layer across projects. That's a flywheel.

What File 1 gets right that's undervalued: the persona framing. A cynical Principal Engineer who treats code as a liability? That's a forcing function. It changes Claude's default posture from "helpful assistant adding code" to "skeptical engineer removing code." That cognitive frame shapes thousands of micro-decisions.

What both miss entirely: neither document tells Claude to identify reusable patterns and propose them as shared modules. The biggest upside nobody's capturing: a CLAUDE.md that includes a section instructing Claude to propose updates to itself when it encounters patterns not covered.

Keep: File 2's comprehensiveness, File 1's persona, File 2's summarize step. Add: cross-project pattern detection, self-update proposals, shared module extraction.

---

### The Outsider

File 1 has a fatal flaw that disqualifies it as a template: Section 5 ships with "[Insert build command]" placeholders. That's not a template — that's an unfinished draft. The persona framing ("elite, cynical Principal DevOps engineer") is also cargo-culting. It sounds cool but adds zero actionable guidance.

File 2 has the opposite problem: it's so comprehensive that it's invisible. At 340 lines, a new project session will treat it as wallpaper. Claude will skim-acknowledge it and proceed however it wants. Length is not thoroughness — it's dilution.

What File 2 gets right that File 1 misses entirely: the analyze → plan → explain → implement → test → validate → summarize workflow. That's the single most valuable thing in either document. It forces Claude to show its work before writing code.

What File 1 gets right that File 2 buries: specificity. "90% coverage minimum," "pinned versions," "non-root containers," "gitleaks scanning" — these are concrete enough to fail against. File 2's equivalent sections are vaguer and easier to technically satisfy while ignoring the intent.

The actual answer: neither file works as-is. File 2's workflow section plus File 1's specific enforcement rules, stripped to one page, would outperform both.

---

### The Executor

File 2 wins on execution value, but it has a fatal flaw: at 340 lines, Claude will context-compress it or ignore the bottom half entirely. Long CLAUDE.md files degrade in practice.

Keep from File 1: the persona framing ("code is liability"), specific Docker mandates (multi-stage, pinned versions, non-root), the gitleaks scanning call-out (names a tool, not a category).

Keep from File 2: the analyze → plan → explain → implement → test → validate → summarize workflow (changes Claude's process, not just output rules), reliability patterns (retries, backoff, circuit breakers), communication standards ("no exaggeration, identify assumptions/risks" directly reduces Claude hallucination noise).

Cut from both: File 1's Section 5 placeholders. File 2's documentation section — Claude already knows what a README is. File 2's API Design and Database sections — too domain-specific for a general template.

What to build: One document, under 120 lines. Lead with the persona and workflow. Everything else is a bulleted constraint list. Test it on a fresh project next week and cut anything Claude ignores in practice. The measure of a CLAUDE.md isn't how comprehensive it looks. It's whether Claude behaves differently on line 1 of a new session.

---

## Anonymization Map (Peer Review)

- Response A = The Expansionist
- Response B = The Executor
- Response C = The Contrarian
- Response D = The Outsider
- Response E = The First Principles Thinker

---

## Peer Reviews

### Reviewer 1
- **Strongest: B (Executor)** — Most actionable. Gives specific keep/cut recommendations, names a concrete output target (120 lines), includes a falsifiable success metric. Every recommendation traceable to a real failure mode.
- **Biggest blind spot: A (Expansionist)** — Self-improving CLAUDE.md is operationally unworkable. Who validates those updates? Creates ambiguity and drift.
- **What all missed:** Inheritance and override behavior. All five discussed the general template as if it operates in isolation. The real design question — what belongs in the general template versus project-level files — was never answered.

### Reviewer 2
- **Strongest: B (Executor)** — Context-compression problem is practical not theoretical. Every recommendation traceable to a real failure mode.
- **Biggest blind spot: A (Expansionist)** — Self-improving idea creates drift with no version control, review gate, or stability guarantee.
- **What all missed:** Inheritance and composition. The entire comparison assumed a flat, single-file model — wrong mental model for a template meant to scale across projects.

### Reviewer 3
- **Strongest: E (First Principles Thinker)** — Only advisor who asked what CLAUDE.md should do that Claude cannot do alone. The three-part framework is precise and actionable.
- **Biggest blind spot: A (Expansionist)** — Claude has no persistent memory between sessions; a self-improving document is a fantasy.
- **What all missed:** Maintenance governance. Who updates the template? When? Triggered by what? A CLAUDE.md with no maintenance contract will be ignored within three projects.

### Reviewer 4
- **Strongest: E (First Principles Thinker)** — Resolves the length debate from first principles rather than preference.
- **Biggest blind spot: A (Expansionist)** — No specific keep/cut decisions; doesn't answer the actual question asked.
- **What all missed:** No one tested context-window behavior empirically. The length debate was entirely theoretical. Should include a concrete A/B test.

### Reviewer 5
- **Strongest: E (First Principles Thinker)** — Only framework that functions as a usable filter, not a preference.
- **Biggest blind spot: A (Expansionist)** — Romanticizes the self-improving concept without confronting the mechanism.
- **What all missed:** Governance — who maintains the template after it ships? Content debate is secondary to accountability.

---

## Chairman's Verdict

### Where the Council Agrees

**File 1 is disqualified as a template.** Unfilled placeholders in a document that Claude will treat as authoritative instruction is not a standard — it is a draft that will produce hallucinated values or silent failures. Every advisor reached this conclusion independently.

**Length is a liability, not an asset.** File 2's 340 lines will be context-compressed into noise. Claude pattern-matches on the most specific available context and treats general guidance as wallpaper. Most of File 2 restates knowledge Claude already has — consuming context window for zero behavioral delta.

**File 2's workflow is the single most valuable artifact in either document.** Analyze → Plan → Explain → Implement → Test → Validate → Summarize is the one instruction pattern specific enough to change Claude's behavior and general enough to survive across project types.

**Specificity beats principles.** "90% coverage," "pinned versions," "gitleaks" are concrete enough to fail against. "Write tests" and "follow best practices" are not.

### Where the Council Clashes

**The persona framing.** Executor and Expansionist find value in it as a posture-shifting forcing function. Contrarian, First Principles Thinker, and Outsider call it theater. Resolution: cut it unless Randy observes a measurable behavioral difference in a real session. Burden of proof falls on inclusion.

**Target length.** First Principles Thinker: under 50 lines. Executor: under 120 lines. Neither resolved this with evidence. Working ceiling: 80 lines. Cut based on observed session behavior.

**The Expansionist's self-improving document concept.** Three of five peer reviews identified this as the council's biggest blind spot. Claude has no persistent memory between sessions. Discard it.

### Blind Spots the Council Caught

**Inheritance and composition architecture.** Every advisor assumed a flat, single-file model. The correct mental model: the general template contains only what no project-level file will ever override. Project files handle stack, commands, domain logic. The general template handles workflow, communication norms, behavioral constraints, and universal decisions.

**Maintenance governance.** A template with no maintenance contract is archaeology within three projects. Needs an owner, update triggers, and a version marker.

**No forcing function for Claude rejecting its own output.** Every instruction in both documents tells Claude what to produce. None tell Claude what to reject. This is the difference between aspirational documentation and a behavioral constraint.

### The Recommendation

Build a merged document targeting **80 lines maximum**. Structure: (1) behavioral constraints — what Claude must not do and what Claude must reject in its own output; (2) the workflow — the seven-step sequence verbatim from File 2; (3) specific enforcement rules from File 1's concrete mandates — pinned versions, named tools, numeric thresholds; (4) communication norms from File 2.

Do not include: persona framing, domain-specific sections, documentation standards, anything Claude already knows.

Add two structural elements neither file included: a statement of what this template does not cover and where project-level files take precedence, and a maintenance header with version date and update trigger condition.

### The One Thing to Do First

Write the workflow section — the seven-step analyze/plan/explain/implement/test/validate/summarize sequence — as a standalone block, drop it into a fresh Claude Code session on a real project (not the youtube-downloader), and observe whether Claude follows it without being reminded mid-session. That single empirical test will tell you more about what the template actually needs than anything either original document contains or anything this council produced.
