---
name: kb-research
description: Run structured knowledge-base research before drafting any article. Queries the 1,944-transcript KB across phased inputs and produces a one-page research brief: quarterly pain report highlights, ICP pain alignment, Nate's existing take, broader transcript signal, repetition guard, callback bank scan, pain-map P# score, and recent post themes. Call this as Step 0 before any content draft.
when_to_use: Invoke at the start of every article-creation session, before any draft is written. Also useful standalone when Randy wants to know what the KB says about a topic before deciding whether to write about it.
---

# KB Research Skill

## Purpose

Query the local knowledge base and supporting content files to produce a structured
research brief before any article draft begins.

This replaces ad-hoc KB queries and guesswork with a repeatable, phased signal sweep
that prevents:
- Repeating a topic already covered in a prior article
- Writing blind without knowing what the audience actually says about this pain
- Missing a strong callback from the bank
- Drifting to a P# weaker than P1/P3/P4 when sharper material exists
- Spending API credits on a topic that fails the on-niche check

## When to Run

- **Always** as Step 0 before `create-next-article` (wired in there)
- Standalone when Randy wants a topic-viability read before deciding whether to write
- Before pitching article ideas — check the KB first, then recommend

## Inputs Required

One input: `[TOPIC]` — the article topic, working title, or pain angle.

If no topic is provided yet, run Phase A inputs 0, 4, 6, and 7 first to surface what's
MOST NEEDED based on pain map gaps and recent post themes, then ask Randy to confirm the
topic before running Phase B.

---

## Research Inputs — Two Phases

**Phase A** costs nothing (file reads only). Run all of Phase A first.
**Phase B** costs API credits. Run Phase B ONLY if Input 6 (on-niche check) passes.

If Input 6 fails, stop after Phase A, show the partial brief with a STOP flag, and ask
Randy to adjust the topic or framing before spending any API credits.

---

### Phase A — Free Reads (run always, in this order)

#### Input 0 — Quarterly Pain Report (most recent distilled audience intelligence)

**What to do:** Find the most recent file matching
`knowledge_base/reports/pain_points_*_ai-job-intelligence.md`.

If one exists, read it and extract:
- Top 3 questions the audience is asking
- Top 3 pain points expressed
- Any PDF product opportunities flagged

If no report exists yet, note "No quarterly pain report yet — first run scheduled Oct 4" and continue.

**Why this runs first:** This is 200 transcripts already distilled into ranked audience
intelligence. It's the highest-signal input and it's free. Every brief should start here.

---

#### Input 4 — Repetition Guard

**Files to read:**
- `content-engine/ARTICLES.md` (or equivalent article schedule/index)
- `content-engine/POSTED_LOG.md`
- `content-engine/pending/_ideas/_CONTENT_INVENTORY.md` (if exists)

**What to extract:** Has this topic or angle already been covered?
- If yes: name the article (number + full title), the angle used, and whether a new
  angle exists that's meaningfully distinct. Flag as "COVERED — find new angle" or
  "COVERED — but [new angle] is distinct."
- If no: flag as "No prior coverage ✓"

A topic is "covered" if the same pain (P#) + same practical angle already exists in a
published or drafted article. A new angle on the same P# is valid.

---

#### Input 5 — Callback Bank Scan

**Files to read:**
- `output/callback_bank.csv` (primary)
- `output/callback_bank.md` (if csv unreadable)

**What to extract:** 1–2 callbacks relevant to this topic. Note the callback name,
the cultural reference, and why it fits. If no relevant callbacks exist, say so — do not force one.

Check against `output/avoid_list.md` — if a potentially relevant callback appears there,
exclude it and note why.

---

#### Input 6 — ICP Pain Map Alignment ← ON-NICHE GATE

**File to read:** `knowledge/me/icp_pain_map.md`

**What to extract:**
1. Which Core Pain(s) does this topic map to? Name the P# explicitly.
2. Is it a ★ sharpest pain (P1, P3, P4)? If not, is there a framing adjustment that
   would pull it into P1/P3/P4 territory?
3. Which Theme/Pillar does it sit inside?
4. Does the topic pass the On-Niche Title Check (all 5 conditions)?

**GATE:** If the topic fails the on-niche check, stop here. Show the partial brief with:

```
⛔ STOP — ON-NICHE CHECK FAILED
Topic: [topic]
Problem: [which of the 5 conditions it fails]
Suggested fix: [one-line reframe that would pass]
No API credits spent. Adjust the topic and re-run.
```

Do not proceed to Input 7 or Phase B until the topic passes.

---

#### Input 7 — Recent Post Themes

**File to read:** `content-engine/dashboard_state.json`

**What to extract:** The last 5–10 published posts. For each, note:
- The P# it targeted
- The Theme/Pillar

Then identify: which P# and Theme has NOT been hit recently? Use this to recommend
variety or confirm the current topic fills a gap.

If dashboard_state.json is unavailable, check `content-engine/POSTED_LOG.md` as fallback.

---

### Phase B — KB Queries (run only if Input 6 passes)

All three commands use `--fast` (Haiku model). These are search and retrieval tasks —
speed and cost matter more than synthesis quality here.

#### Input 1 — ICP Pain Angles (Nate's audience, fear/struggle framing)

**Command:**
```
python -m src.main ask --group ai-job-intelligence --fast "[TOPIC] IT professional fear struggle layoff replace"
```

**What to extract:** The top 3 fear/struggle angles the audience expresses about this
topic. Direct quotes from transcripts are more useful than paraphrases — these become
hook language.

**If the group returns no results:** note in the brief and rely on the quarterly pain
report (Input 0) for audience signal.

---

#### Input 2 — Nate's Existing Take (differentiation check)

**Command:**
```
python -m src.main ask --group ai-job-intelligence --fast "[TOPIC]"
```

**What to extract:** What has Nate already said about this topic? The goal is
differentiation — Randy's article should go deeper, go practical, or go IT-specific
in a direction Nate hasn't covered. Note the angle Nate occupies so Randy can own
adjacent territory.

---

#### Input 3 — Broader KB Signal (all channels)

**Command:**
```
python -m src.main ask --fast "[TOPIC] IT sysadmin career"
```

**What to extract:** 2–3 supporting data points from non-Nate channels. Note the source
channel if identifiable.

---

## Output Format

After running all inputs, produce this brief. Display it to Randy before any draft begins.

```
RESEARCH BRIEF — [TOPIC]
─────────────────────────────────────────────────────────────
P# ALIGNMENT:      P3 (layoff anxiety) — strong signal
                   Also touches P4 (25 years devalued) — secondary
ON-NICHE CHECK:    ✓ passes all 5 conditions
REPETITION CHECK:  No prior coverage ✓
                   (or: ART4 "title" covered this angle — new angle: [X])
─────────────────────────────────────────────────────────────
PAIN REPORT HIGHLIGHTS (quarterly distillation — most recent report):
  Top questions:
  • [#1 ranked question from pain report]
  • [#2]
  Top pain points:
  • [#1 ranked pain point]
  • [#2]
  (or: No report yet — first run Oct 4)
─────────────────────────────────────────────────────────────
ICP PAIN ANGLES (from KB — live transcripts):
  • [top pain point — direct quote or close paraphrase]
  • [second pain point]
  • [third pain point]

NATE'S TAKE (differentiate here):
  • Nate's angle: [what he said / his framing]
  • Differentiation opportunity: [where Randy can go deeper/different]

BROADER KB SIGNAL (all channels):
  • [data point or angle from non-Nate source — note channel]
  • [second data point if available]
─────────────────────────────────────────────────────────────
CALLBACKS AVAILABLE:
  • [callback name] — [cultural ref] — fits because [reason]
  • (or: No strong callback match for this topic)

RECENT POST THEMES (last 5 published):
  • P1, P3, P4, P1, P3 — P2/P5/P6 territory is open
─────────────────────────────────────────────────────────────
RECOMMENDED ANGLE:  [one-sentence synthesis]
SUGGESTED HOOK TERRITORY: [one-sentence hook direction — not a finished hook]
─────────────────────────────────────────────────────────────
MISSING INPUTS: [list any inputs that returned no data or files not found]
```

---

## Decision Gate After the Brief

After displaying the brief, ask Randy ONE question:

"Does this angle work, or do you want to adjust before I draft?"

If Randy says yes / go ahead → proceed to draft (or return control to
`create-next-article` if called from there).

If Randy adjusts the angle → update the RECOMMENDED ANGLE line and confirm before drafting.

Do not draft anything before this gate.

---

## Failure Handling

- **KB not indexed:** Run `python -m src.main index` first, then retry.
- **ask command returns empty results:** Note in brief as "KB returned no results for this query."
- **dashboard_state.json unreadable:** Fall back to POSTED_LOG.md; note the fallback.
- **icp_pain_map.md missing:** Stop and alert Randy — this file is essential for the gate.
- **callback_bank.csv missing:** Note in brief; continue without callback recommendations.
- **No quarterly pain report yet:** Note "First run Oct 4" and continue — Phase B covers it.

---

## Gotchas

- (none logged yet — append here as real sessions surface edge cases)
