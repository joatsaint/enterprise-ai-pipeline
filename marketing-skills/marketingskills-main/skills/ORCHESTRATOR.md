# ORCHESTRATOR.md  *(DRAFT v0.1 — structural choices flagged for Randy's sign-off)*

**Created:** May 31, 2026
**Owner:** Randy Skiles (joatsaint)
**Status now:** forward-design. Lives in `youtube-downloader/` and is read by Claude
Code, but the root layer is **not stood up yet** (see §2, Staging).
**Status later:** moves to the root folder; a thin root `CLAUDE.md` points here; this
becomes the brain that makes Claude Code the cross-project orchestrator.

---

## 0. PRIME DIRECTIVE

**This is the map of maps. At the root folder, read this first — every session,
Claude Code included.**

It tells you what projects exist, what each one is for, where each one's *own*
brain lives, and how they relate. It does **not** contain any project's internals.
When you need to actually work inside a project, this file points you to that
project's brain (e.g. `LinkedIn_CONTENT_OS.md`) and you go there.

**The one rule that keeps this from becoming a monolith:** the root holds the
*map*; each project holds its *territory*; nothing is duplicated. Root points
down. Root never copies up. The day this file starts restating what's already in
a project's brain is the day the system begins to rot.

---

## 1. THE TWO-TIER MODEL

```
ROOT FOLDER  (the orchestrator)
│
├── CLAUDE.md              ← thin: "read ORCHESTRATOR.md first, then act"
├── ORCHESTRATOR.md        ← THIS FILE. The map. Read first.
├── SESSION_LOG.md         ← shared continuity log across all projects
│
├── _shared/               ← assets every project uses (see §5)   [DECISION: §7]
│   ├── voice/             ← RANDY_VOICE_SKILL.md, voice.md, youtube-voice.md, Voice_Profile_v2.docx
│   ├── PILLARS.md         ← the five ICP pain pillars (shared by content + job-search)
│   └── ICP/               ← PROJECT_CONTEXT.md, MASTER_PLAN.md (positioning, offer ladder)
│
├── youtube-downloader/    ← PROJECT: deep research pipeline (the moat)
│   └── (its own CLAUDE.md + pipeline files = its brain)
│
├── content-engine/        ← PROJECT: LinkedIn content system
│   ├── LinkedIn_CONTENT_OS.md   ← its LinkedIn brain (+ future YouTube_CONTENT_OS.md, etc.)
│
├── video-to-pdf/          ← PROJECT: live Streamlit app
│   └── (its repo = its brain)
│
└── ai-job-search-agent/   ← PROJECT: planned
    └── AI_JOB_SEARCH_AGENT_SPEC.md   ← its brain (spec exists, not built)
```

**Tier 1 (root):** orchestrator — knows the map, the shared assets, the
cross-project state.
**Tier 2 (each project):** self-contained brain that owns its own details.

---

## 2. STAGING — NOW vs LATER  *(the discipline that prevents premature scaffolding)*

| Phase | Where Claude Code runs | What's true |
|-------|------------------------|-------------|
| **NOW** | inside `youtube-downloader/` | Single-project operation. This file is the forward-design; Claude Code can read it but does **not** yet orchestrate across folders. Don't build root machinery. |
| **MIGRATION TRIGGER** | — | You move `youtube-downloader/` into a parent root folder, alongside the other projects. |
| **LATER** | inside the **root** folder | Move this file to root. Add thin root `CLAUDE.md` → points here. Stand up `_shared/`. Claude Code now reads this first and orchestrates across all projects. |

**Do not stand up the root layer before the folder move.** It's a lift when the
time comes, not a rebuild. Until then, single-project is correct.

---

## 3. PROJECT REGISTRY  *(DRAFT — Randy: confirm/complete the list)*

Each row points to a project's own brain. The orchestrator tracks status here;
the details live in the linked brain.

| Project | What it is | Its brain | Status |
|---------|-----------|-----------|--------|
| **youtube-downloader** *(enterprise-ai-pipeline)* | Multi-agent YouTube transcript analysis — the **deep research moat**. Runs via `run_pipeline.bat`; notifies via `send_notification.ps1`. | its `CLAUDE.md` + pipeline files | Operational |
| **content-engine** | Multi-platform content system — generation, visuals, scheduling, email, reminders. **LinkedIn first**; other platforms become sibling brains. | `LinkedIn_CONTENT_OS.md` *(+ future `YouTube_CONTENT_OS.md`, etc.)* | Phase 1 (spine being built) |
| **video-to-pdf** | Live Streamlit app (video-to-pdf-guide-creator.streamlit.app). | its repo | Live |
| **ai-job-search-agent** | Planned: personal tool → Gumroad PDF → "AI Job Match Scorer" Streamlit app. | `AI_JOB_SEARCH_AGENT_SPEC.md` | Spec only, not built |

*Gumroad products / lead magnets are **outputs/assets**, not code projects — they
sit under content-engine (or `_shared/`), not their own folder. Confirm in §7.*

---

## 4. THE TWO RESEARCH LAYERS  *(keep these separate — this is where your trend-miner decision lives)*

You have two research functions. They must not blur.

| | **Deep research** | **Trend research** |
|---|---|---|
| **What** | Systematic transcript + comment analysis | Mining live community discussion |
| **Project** | youtube-downloader (the moat) | `trend-miner` skill, inside content-engine |
| **Cadence** | Quarterly-ish | **Monthly default; weekly when wanted** |
| **Depth** | Deep, strategic | Shallow, tactical |
| **Answers** | What to build the library around | What's spiking *now* / what to publish next |
| **Output** | Durable pillar definitions | `content-engine/research/pain-points-YYYY-MM.md` |

**`trend-miner` — locked decisions:**
- Runs as a **Claude Code skill** (not a standalone script). Uses Claude Code's
  **web search** — a sanctioned search API, so no scraper and no ToS exposure.
- Method: `site:` queries against the IT communities (r/sysadmin,
  r/ITCareerQuestions, community.spiceworks.com, theregister.com, etc.) with a
  recent date filter. *(Reddit is indexed only by Google now — `site:reddit.com`
  via Google search is the sanctioned front door, not a workaround.)*
- Output: one run → a month of pain points, **sorted into the five pillars**,
  written to `content-engine/research/`. The content-generator reads this once the
  article queue runs dry.

The orchestrator's job re: research is only to **know both layers exist and feed
different things.** It doesn't run either — it points to where each lives.

---

## 5. SHARED ASSETS  *(live at root in `_shared/`, referenced by projects — never copied into them)*

Things more than one project uses. They belong at root so there's one copy:

- **Voice files** — used by every drafting task (content + job search + YouTube).
- **The five pillars** (`PILLARS.md`) — used by content-engine *and* ai-job-search-agent (same ICP fears).
- **ICP / positioning** (`PROJECT_CONTEXT.md`, `MASTER_PLAN.md`) — strategic reference for all projects.
- **SESSION_LOG.md** — one continuity log across everything.
- **Handoff protocol** — every changed file gets mirrored to both locations (project folder + Skills Master Folder).

If a project needs one of these, it *reads* it from `_shared/`. It does not keep
its own copy. (Same anti-duplication rule as §0.)

---

## 6. SESSION PROTOCOL  *(root level)*

**Start:**
1. Read `ORCHESTRATOR.md` (this file) — the map.
2. Check the registry (§3) — which project(s) are active this session.
3. Drop into that project's brain (e.g. `content-engine/LinkedIn_CONTENT_OS.md`) and follow its protocol.

**End:**
1. Update the active project's brain + `TASKS.md`.
2. Update the registry status here if a project advanced a phase.
3. Update `SESSION_LOG.md`.
4. Mirror all changed files to both locations (handoff protocol).

**Branch naming:** no slashes (avoids the Windows filesystem deletion prompt).

---

## 7. OPEN STRUCTURAL DECISIONS  *(yours to make — Claude drafts, you decide)*

- [ ] **Project list (§3):** is the four-project list complete? Anything missing
  (e.g. a separate repo for the Gumroad products, or other tools)?
- [ ] **Shared assets (§5):** confirm `_shared/` as the home for voice, pillars,
  ICP, session log — or you prefer a different layout.
- [ ] **Naming:** keep `ORCHESTRATOR.md` (your word), or rename (e.g.
  `MISSION_CONTROL.md`)?
- [ ] **Migration trigger (§2):** confirm the trigger is the folder move, and that
  single-project is how we operate until then.
- [ ] **Gumroad products:** asset under content-engine, under `_shared/`, or own folder?

---

*Draft v0.1 — May 31, 2026. This is the forward-design for a root orchestrator that
is not yet stood up. It activates at the folder move. Until then it documents the
target so the migration is a lift, not a rebuild.*
