# Tasks — Content Engine

*The active reminder board. Claude Code reads and updates this every session.
Convention: `- [ ] **Title** — context, due [date]`. Done: `- [x] ~~Title~~ (date)`.
This board also doubles as the Phase 2 build map — see Backlog.*

---

## Active  ← do now

- [ ] **Phase 2 · Stage 1 — separate-file output** — make the generator write each
  piece to its own `.md` in `pending/ART#-slug/` instead of one blob file. First
  testable upgrade; biggest visible win.

## Blocked on Randy  ← waiting on a decision or input from you

- *(none right now)*

## Backlog  ← later, not now — the rest of Phase 2, then later phases

- [ ] **Phase 2 · Stage 2 — image-prompts.md** — generator emits Gemini-ready prompts
  per `LinkedIn_Image_prompts.txt` (vertical 1376×768 + 1" white border for the feed
  image; landscape for the article header).
- [ ] **Phase 2 · Stage 3 — HTML-ready carousel spec** — replace the prose carousel
  outline with structured slide data (headline / body / label / pillar / visual note)
  the Phase 3 template consumes.
- [ ] **Phase 2 · Stage 4 — pillar tagging + read voice/rules from source files** —
  tag each output by pillar (CONTENT_OS §4.0); stop hardcoding voice/rules in the
  script, read `RANDY_VOICE_SKILL.md` + `LINKEDIN_CONTENT_SKILL.md` so there's one
  copy, not a drifting duplicate.
- [ ] **Phase 3 — visual-producer** — HTML/SVG carousel template (build once,
  near-instant forever) + Gemini prompt output. Portfolio artifact for Goal 2.
- [ ] **Phase 4 — trend-miner + lead-magnet-post** — NOT before the article queue
  runs dry (~late July). Trend data is perishable; run it when it's live.
- [ ] **Phase 5 — email-drafter** — draft the welcome / nurture / soft-pitch
  sequence only. No funnel automation until the list justifies it.

## Done  ← keep ~1 week, then clear

- [x] ~~LinkedIn_CONTENT_OS.md created (v1.2) — the content-engine brain~~ (May 31)
- [x] ~~ORCHESTRATOR.md drafted — root cross-project map (forward-design)~~ (May 31)
- [x] ~~Five content pillars + trend-miner `site:` query list captured in LinkedIn_CONTENT_OS~~ (May 31)
- [x] ~~Visual fork resolved — code-generated carousels~~ (May 31)
- [x] ~~TASKS.md created — this board~~ (May 31)
- [x] ~~Finish the Phase 1 spine — folder tree + CLAUDE.md pointer created~~ (May 31)
