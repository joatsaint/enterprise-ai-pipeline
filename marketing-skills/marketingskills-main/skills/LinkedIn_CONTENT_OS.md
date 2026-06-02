# LinkedIn_CONTENT_OS.md

**Version:** 1.4
**Created:** May 31, 2026
**Owner:** Randy Skiles (joatsaint)
**Home folder:** `content-engine/` (lives in the youtube-downloader project folder; mirror to the Skills Master Folder per the handoff protocol)
**Scope:** This is the **LinkedIn** content engine. Renamed from the generic `CONTENT_OS.md` so the filename says which platform it serves. As the project adds platforms, each gets its own sibling brain — `YouTube_CONTENT_OS.md`, `X_CONTENT_OS.md` — under the same orchestrator.
**Nests under:** `ORCHESTRATOR.md` (root). This is one project brain in a two-tier system — the orchestrator holds the map across all projects; this file owns the LinkedIn engine's territory. The trend-miner's place in the wider research picture is defined in ORCHESTRATOR §4.

---

## 0. PRIME DIRECTIVE

**Read this file first, every session — Claude Code included.**

This is not another tracker. It is the *map*. Everything in the content business
(generation, visuals, scheduling, the email funnel, the reminders) runs through
the system described here. When you sit down and don't know where to start, you
start here. When a new Claude Code session opens, it reads this first to know how
the pieces connect.

**The one rule that keeps this from sprawling:** this file holds the *orchestration*
state — the build phase, which skill is half-finished, where work sits in the
approval pipeline. It does **not** duplicate data that already lives somewhere
else. The article queue lives in `LINKEDIN_TRACKER.md`. The rules live in
`LINKEDIN_CONTENT_SKILL.md`. The voice lives in the voice files. CONTENT_OS points
*to* those. Nothing gets copied into two places, because the moment a fact lives in
two files, the two files start to disagree — and that disagreement is exactly the
fragmentation we're solving for.

---

## 1. THE MENTAL MODEL

You have six things that feel like six fires: multi-format production, scheduling,
the email funnel, the sequences, learning Claude Code, and a reminder system.

They are not six things. They are **one system with one brain and a few
single-purpose tools around it.**

```
                      ┌───────────────────────┐
                      │     CONTENT_OS.md     │   ← the brain (the map)
                      │   + TASKS.md (board)  │
                      └───────────┬───────────┘
                                  │ every tool reads the rules,
                                  │ writes its output, updates the board
          ┌───────────────┬───────┴───────┬────────────────┐
          ▼               ▼               ▼                ▼
  content-generator  visual-producer   (scheduling)    email-drafter
   (all copy +        (carousels +      built into       (sequences,
    schedule +         image prompts)    the generator    drafted only)
    visual specs)                        output)
```

Each tool does **exactly one job**, reads the same rules, and drops its output
into the approval pipeline. You inspect and approve before anything is scheduled
or published. The brain tells you what's done and what's next.

That's the whole design. Everything below is detail.

---

## 2. WHAT THE BRAIN TRACKS (and where each thing actually lives)

The "source of truth" tracks four things. Two of them live *inline* here because
they're volatile orchestration state. Two live in established files and this doc
just points to them.

| What | Where it lives | Why |
|------|----------------|-----|
| **Build state** (which phase, which skill is partly built) | Inline, §7 below | Changes as we build; belongs in the orchestrator |
| **Approval pipeline state** (what's in pending vs approved vs scheduled) | The folders themselves (§5) + `TASKS.md` | The folder a file sits in *is* its status |
| **Content queue** (articles, publish dates, status) | `LINKEDIN_TRACKER.md` — pointer only | Already exists and is maintained; don't duplicate |
| **The rules** (timing, formats, voice, image specs) | The skill/rule files (§9) — pointer only | Already exists; the tools read them directly |

When those four are in sync, the system is healthy. The job of every session is to
leave them in sync.

---

## 3. SYSTEM MAP (folder structure)

```
content-engine/
├── LinkedIn_CONTENT_OS.md     ← this file. The LinkedIn brain. Read first.
├── TASKS.md                   ← active reminder board (see §6)
├── CLAUDE.md                  ← thin file: "read LinkedIn_CONTENT_OS.md first, then act"
│
├── rules/                     ← the constitution. Tools read these; never duplicated.
│   ├── LINKEDIN_CONTENT_SKILL.md
│   ├── RANDY_VOICE_SKILL.md
│   ├── voice.md
│   ├── youtube-voice.md
│   └── LinkedIn_Image_prompts.txt
│
├── skills/                    ← the single-purpose tools (each is a Claude Code skill)
│   ├── content-generator/SKILL.md
│   ├── visual-producer/SKILL.md
│   └── email-drafter/SKILL.md
│
├── articles/                  ← INPUT: finished article drafts go here
│   └── ART3-motel.md
│
├── pending/                   ← Claude Code writes drafts here. AWAITING YOUR REVIEW.
│   └── ART3-motel/
│       ├── text-post.md
│       ├── image-post.md
│       ├── carousel.md  + carousel.html
│       ├── newsletter.md
│       ├── first-comments.md
│       ├── poll.md
│       ├── ART_3_..._image-prompts_Gemini.md   ← Gemini template (§4.2 naming rule)
│       └── buffer-schedule.md
│
├── approved/                  ← YOU move items here after review = "cleared to schedule"
│
├── scheduled/                 ← loaded into Buffer / queued. Archive of what's live-pending.
│
└── published/                 ← archive of what shipped. Closes the loop.
```

**The folder a piece of content lives in is its status.** No status column to
maintain — moving a folder *is* the status update. `pending/` → you review →
`approved/` → loaded into Buffer → `scheduled/` → it fires → `published/`.

---

## 4. THE SKILLS

Three tools. Each does one job. Scheduling is **not** a separate tool — the
generator already emits the exact schedule block, so "scheduling" is just you
loading the approved copy into Buffer (manual on the free plan; that's fine).

### 4.0 THE FIVE CONTENT PILLARS  *(the shared taxonomy — read before the skills)*

Every piece of content maps to one of five pillars. This is the spine of the ICP
(GenX enterprise IT, end-of-career, afraid of being AI'd out before retirement).
The pillars are shared infrastructure: the **content-generator** tags each output
by pillar, the **trend-miner** sorts its findings into them, and the
**ai-job-search-agent** keys off the same fears. Communities hand you fresh,
quotable *instances*; the pillars are the fixed buckets they drop into — that's
what keeps the engine from chasing noise and your voice from drifting.

1. **The Flood** — too much AI news, too many skills and platforms; what can I
   safely ignore.
2. **What AI Can't Do** — the irreplaceable judgment; the who / what / when /
   why / *whether* of an organization.
3. **The Pivot** — from doing the work to managing the AI (the AI manager).
4. **Hand Off the Grunt Work** — practical delegation; what to offload and how
   (the Four Agents live here).
5. **Don't Get AI'd Out Before Retirement** — the survival / indispensability
   fear underneath all of it.

The renewable-series format (`...questions every [role] is asking`) draws one role
per installment from these pillars, sourced from that role's community corner.

*(At the folder migration these graduate to `_shared/PILLARS.md` per ORCHESTRATOR
§5, so the job-search agent reads the same copy. Inline here until then.)*

### 4.1 `content-generator`  *(this is linkedin_atomizer.py, upgraded)*

- **ONE JOB:** Take one article → produce *every* format's copy, the schedule
  block, AND the visual specs, dropped into `pending/ART#-slug/`.
- **READS:** the article in `articles/`, plus `rules/LINKEDIN_CONTENT_SKILL.md`
  and the voice files.
- **WRITES:** `pending/ART#-slug/` — text post, image post, carousel copy,
  newsletter, first comments (A–D), poll, **image prompts** (per
  `LinkedIn_Image_prompts.txt`, named with the destination-tool suffix — see §4.2),
  and the Buffer schedule block.
- **STATUS:** Today's `linkedin_atomizer.py` already produces 7 sections including
  the schedule block. The upgrade adds: (1) the image *prompts* as a saved file,
  and (2) a carousel spec clean enough for the visual-producer to build HTML from.
  This is the **biggest single hit on "takes too long."**

### 4.2 `visual-producer`  *(formalizes what you already do by hand)*

- **ONE JOB:** Turn approved copy + specs into finished visual files.
- **READS:** the approved `carousel.md` and `image-prompts.md`.
- **WRITES:**
  - **Carousels → code-generated HTML** (you already do this — "build ART3
    carousel HTML with brand colors"). Build the brand template *once*; every
    future carousel is near-instant. Optionally render to PDF for Buffer.
  - **AI images → the prompt is generated; you run Gemini.** Honest line in the
    sand: the skill writes the Gemini-ready prompt (vertical 1376×768 + 1-inch
    white border for posts, landscape for article headers). You generate in
    Gemini and drop the file back into the folder. Image *generation* stays
    manual; image *prompting* is automated.
  - **NAMING RULE — hand-carried generation templates.** Any file whose contents
    you paste into a third-party *generation* tool (Gemini, etc.) is named with the
    destination tool as the suffix, so the filename itself tells you where it goes
    and a folder of outputs is self-documenting:
    **`ART_#_[Article_Title]_[type]_[Tool].md`** — e.g.
    `ART_3_Hurricane_Motel_image-prompts_Gemini.md` or
    `ART_4_Dont_Panic_carousel_Gemini.md`. This applies anywhere a template leaves
    the pipeline for an external site. Finished copy you paste straight into
    LinkedIn or Buffer (text post, newsletter, comments) keeps its plain name —
    the suffix is specifically the "I have to carry this somewhere to generate
    something" flag.
- **STATUS:** Not built. Phase 3. The HTML carousel template is the asset that
  pays off forever — and it doubles as a portfolio artifact for Goal 2.

### 4.3 `email-drafter`  *(drafts only — do NOT build funnel automation yet)*

- **ONE JOB:** Draft the welcome sequence, nurture emails, and soft-pitch
  (Email 3), in your voice.
- **READS:** `PROJECT_CONTEXT.md` (offer ladder), the voice files.
- **WRITES:** `pending/email/` — one file per email.
- **STATUS:** Not built. Phase 5. **Blunt note:** your list is tiny. Building an
  elaborate funnel machine now is exactly the over-engineering your own rule warns
  against. Draft the sequences so they *exist*, send them simply (your existing
  Gmail SMTP via App Password is enough), and let Phases 2–4 grow the list before
  you sink time into automation.

### 4.4 Phase-4 engagement skills *(reach — build after the core loop works)*

- **`trend-miner`** — a **Claude Code skill** (not a standalone script) that mines
  live community discussion and sorts it into the five content pillars. Runs
  **monthly by default** (weekly when you want a fresh read); one run yields a
  month of content. Uses Claude Code's **web search** (a sanctioned search API —
  no scraper, no ToS exposure): `site:` queries with a recent date filter, then
  synthesis into the pillars. *Compliance rule: read public pages via a sanctioned
  search API; never bulk-scrape and never reproduce whole threads. Reddit is now
  indexed only by Google, so `site:reddit.com` via Google search is the sanctioned
  front door, not a workaround. If ever productized, re-read each platform's terms
  — redistribution is a different question than reading.* Starter query set:

  ```
  site:reddit.com/r/sysadmin AI job
  site:reddit.com/r/ITCareerQuestions "AI" obsolete
  site:reddit.com/r/experienced_devs AI replace senior
  site:community.spiceworks.com AI career
  site:theregister.com sysadmin AI
  # secondary veins: r/devops, r/networking, r/cybersecurity, r/msp,
  # Hacker News, Microsoft Q&A / TechNet
  ```

  Writes `content-engine/research/pain-points-YYYY-MM.md`, which the
  content-generator reads once the article queue runs dry. Complements the
  transcript-analysis moat: the moat finds durable fears, this finds which one is
  spiking now. *(Full research-layer definition: ORCHESTRATOR §4.)*
- **`lead-magnet-post`** — produces the recurring "comment [word] and I'll send
  it" post format. This is the engagement lever you're currently missing — it
  feeds the algorithm *and* captures leads in the DM. Mechanics borrowed from
  Duncan Rogoff; topic/voice stays 100% yours (your ICP wants to keep their job,
  not start an agency).

---

## 5. THE APPROVAL FLOW (the human gate, preserved)

Nothing is scheduled or published without your eyes on it. The gate is folders,
not tooling:

```
1. content-generator writes → pending/ART#-slug/
2. YOU review. Edit anything in place.
3. YOU move the folder → approved/        (= "cleared")
4. visual-producer builds visuals into the approved folder
5. YOU load the approved copy + visuals into Buffer
6. Move folder → scheduled/               (= "in Buffer, firing on schedule")
7. After it fires → published/            (= "shipped")
```

**Always manual, forever (by design / by platform):**
- Publishing the LinkedIn **Article** and **Newsletter** (LinkedIn allows no
  automation here)
- Loading into **Buffer** (free plan has no API — you paste; the generator makes
  this fast by handing you exact copy + times)
- **Commenting** on others' posts and **replying** during golden hour (automating
  these risks a ban and defeats the point)

---

## 6. THE REMINDER SYSTEM

Two parts: a **board** (the list) and a **nudge** (the notification). Both reuse
patterns you already have.

### `TASKS.md` — the board

Lives in `content-engine/`. Claude Code reads and updates it every session.
Adapted from a proven format — four sections, checkbox tasks, bold titles:

```markdown
# Tasks — Content Engine

## Active            ← what to do now
- [ ] **Build ART3 carousel HTML** — brand colors, due before June 2
- [ ] **Load ART3 week into Buffer** — publish June 2

## Blocked on Randy  ← waiting on a decision or input from you
- [ ] **ART5 Q5 answer** — pivot question, blocks the whole ART5 package — since May 28

## Backlog           ← later, not now
- [ ] **Build visual-producer skill** — Phase 3

## Done              ← keep ~1 week, then clear
- [x] ~~ART2 content week closed out~~ (May 26)
```

Conventions: `- [ ] **Title** — context, due [date]`. Completed:
`- [x] ~~Title~~ (date)`. "Blocked on Randy" is the section that catches the
ART5-style stalls where the system is waiting on *you*.

### The nudge — `notify-content.ps1`

Model it on your existing `send_notification.ps1` (same SMTP pattern). Instead of
tailing a pipeline log, it reads `TASKS.md` and emails you the **Active** items +
the single most important next action.

- **Trigger:** Windows Task Scheduler — same mechanism as your pending "weekly
  pipeline run." Suggest a Monday-morning send (lines up with your weekly batch
  block) and optionally a publish-day-morning send Tue/Thu/Fri.
- **Result:** you never have to *remember* to check. The system tells you what's
  done and what's left, on a schedule.

---

## 7. BUILD ORDER  *(one fully working before the next — this is non-negotiable)*

The real failure mode for a solo operator with your ambition is five half-finished
systems. Finish each before starting the next.

| Phase | Build | Status | Why this order |
|-------|-------|--------|----------------|
| **1** | This file + `TASKS.md` + thin `CLAUDE.md` pointer + folder tree | 🔨 doing now | The spine. Nothing else works without it. |
| **2** | `content-generator` (atomizer v2 — all formats + image prompts + schedule) | ⬜ next | Biggest hit on "takes too long." Closes the generate→schedule loop. |
| **3** | `visual-producer` (HTML carousel template + Gemini prompt output) | ⬜ | The other half of the time problem. Template pays off forever. |
| **4** | Engagement skills (`trend-miner` + `lead-magnet-post`) | ⬜ | This is what moves reach and lead capture. |
| **5** | `email-drafter` (sequences drafted; simple send) | ⬜ | Cheap to draft. Do **not** automate the funnel until the list justifies it. |

**Discipline check:** if a phase isn't fully working and in daily use, the next
phase doesn't start. Half-built skills are worse than no skills — they look done
and quietly fail.

---

## 8. THE VISUAL DECISION  *(recommended default — you own the final call)*

The one fork that most changes the build: how visuals get made.

- **Code-generated (recommended for repeatable, data-heavy formats):** stat
  carousels and infographics built from an HTML/SVG brand template. Build once,
  near-instant forever, maximum automation, strong portfolio artifact. You're
  already doing this with carousel HTML — this just makes it the default.
- **Manual tools (keep for one-offs):** Gemini for AI hero images where you want
  real art direction; Canva only if a specific piece needs hand assembly.

**DECIDED (May 31):** code-generated carousels/infographics + Gemini-prompted hero
images. The content-generator emits a structured carousel spec (slide-by-slide
fields, not prose); the visual-producer renders finished slides from an HTML/SVG
brand template. Canva stays optional, for the occasional hero piece that genuinely
needs hand art-direction. This is what you already do by hand with carousel HTML —
Phase 2/3 just make it the default and build the template once.

---

## 9. FILE REGISTRY  *(existing assets — the tools read these; never re-create them)*

| File | Role | Where the tools use it |
|------|------|------------------------|
| `LINKEDIN_CONTENT_SKILL.md` | The rules engine (timing, formats, specs) | Read by content-generator |
| `RANDY_VOICE_SKILL.md`, `voice.md`, `youtube-voice.md` | Voice fingerprint (Raw Randy / Brand Voice) | Read by every drafting skill |
| `Randy_Skiles_Voice_Profile_v2.docx` | Deep voice reference | Source for the voice skills |
| `LinkedIn_Image_prompts.txt`, `LinkedIn_Post_Image_Prompt.md` | Image spec (sizes, borders, style) | Read by visual-producer |
| `linkedin_atomizer.py` | Current generator | Becomes content-generator v2 |
| `ARTICLE_WEEK_PROMPT.md` | 9-output single-session production prompt | Folds into content-generator |
| `LINKEDIN_TRACKER.md` | The content queue + status | Pointed to by §2; not duplicated |
| `SESSION_LOG.md` | Session-to-session continuity | Updated each session (see §10) |
| `MASTER_PLAN.md`, `PROJECT_CONTEXT.md` | Strategy, offer ladder, ICP | Read by email-drafter; strategic reference |
| `run_pipeline.bat` | Existing pipeline runner | Scheduling pattern for the notifier |
| `send_notification.ps1` | Existing SMTP notifier | Template for `notify-content.ps1` (§6) |

---

## 10. SESSION PROTOCOL  *(how this fits your existing discipline)*

This sits on top of your current `SESSION_LOG.md` habit — it doesn't replace it.

**Start of session (Claude Code):**
1. Read `CONTENT_OS.md` (this file) — the map.
2. Read `TASKS.md` — what's active and what's blocked.
3. Confirm current build phase (§7).

**End of session:**
1. Update `TASKS.md` — move finished items to Done, surface new ones.
2. Update §7 build state here if a phase advanced.
3. Update `SESSION_LOG.md` as usual.
4. Produce changed files for download → copy to **both** locations
   (youtube-downloader folder + Skills Master Folder) per the handoff protocol.

**Branch naming reminder:** no slashes in branch names (avoids the Windows
filesystem deletion prompt).

---

## 11. OPEN DECISIONS

Things you own that aren't locked yet. Resolve, then move to the relevant section.

- [x] **Visual fork (§8):** ~~confirm code-generated default, or keep Canva in the
  loop for carousels.~~ **DECIDED May 31 — code-generated carousels.** The
  content-generator emits a structured carousel spec; the visual-producer renders
  it from an HTML/SVG brand template. Canva stays optional for one-off hero pieces.
- [ ] **Notifier cadence (§6):** Monday-only, or Monday + publish-day mornings?
- [ ] **Home folder:** confirm `content-engine/` lives inside the youtube-downloader
  project, or gets its own top-level folder.
- [ ] **Scheduler skill:** skip for now (Buffer free = manual). Revisit only if you
  move to a Buffer tier with API access.

---

*Version 1.0 — May 31, 2026. Update this file when the build phase advances, a
skill changes job, or a structural decision is made. It is the first thing every
session reads.*
