---
name: citation-guard
description: Run the 11-check fact/citation verification pass on a drafted article before it reaches Randy for review. Use immediately after any article draft is written and voice-passed, before reporting the piece as ready — never skip this, and never let a piece reach the Human Gate without it having run. Full rationale, wording history, and 3 validated test runs live in content-engine/rules/CITATION_GUARD_SPEC_v6.md — read that before the first run of a session, this file is the runnable process.
---

# Citation Guard

The hard checkpoint between an AI-drafted piece and anything that publishes under
Randy's name. Runs after Draft + Voice Pass, before the piece is ever presented to
Randy as ready. It does not edit the draft — it only flags it. Full spec, rationale,
and validated test history: `content-engine/rules/CITATION_GUARD_SPEC_v6.md`. This
file is the checklist to actually execute every time, not a summary to skim.

## When this runs

Every time an article draft is finished and voice-passed — inside `create-next-article`
(wired in as a mandatory step) and any other skill that produces a full article draft.
Never present a draft to Randy as "ready" without this having run first.

## The 11 checks (run in order, full detail in the spec)

1. **War Story Authenticity** — every war story traces to the real story bank, past
   published work, or something Randy confirmed this session. Never invented.
2. **Named Entities** — every company/tech/date/person checked against confirmed
   sources. Target 15+ real, checkable entities per full article — never padded.
3. **Statistics and Numbers** — every stat/figure has a traceable source, or is
   explicitly Randy's own lived number, or is labeled as opinion/estimate.
4. **Technical Claims** — every claim about how a tool/system works is accurate.
5. **Extractable Passage** — at least one self-contained 134–167 word passage stating
   a core claim, liftable as a standalone quote.
6. **Direct Quotes** — at least one real direct quote present (soft flag if missing).
7. **Structural Format** — 2–4 sentence paragraphs, a direct-answer statement near the
   top, H2s phrased as direct questions (Mode 1 only) answered in their first sentence.
8. **Hard Do-Not List Compliance** — scan against `SHARED_BRAND_RULES.md`'s hard
   do-not list (banned phrases, question openers, link-in-body, etc.).
9. **Medium Disclosure** (Medium-bound drafts only) — every single offsite link (not
   just the primary CTA) has a one-line disclosure it leaves Medium. N/A for
   LinkedIn-only drafts.
10. **External Authority Citation** — at least one real primary-source citation on
    pieces making factual/industry claims; secondary sources (a blog summarizing a
    study) get flagged to link the original instead.
11. **Freshness Maintenance** (revisits only, not new drafts) — a genuine substantive
    change, not a cosmetic date-only edit, plus a visible "Updated [date]: [what
    changed]" line.

## Output format (exact — matches the spec)

Return the draft with inline flags at the point they apply, plus this summary block
at the top:

```
CITATION GUARD SUMMARY
- Unverified/blocking flags: [count] — MUST resolve before publish
- Soft flags (recommendations): [count]
- Named entities found: [count] (target 15+)
- Citable passage present: Yes/No
- Direct quote present: Yes/No
- Rule violations: [count]
- Medium disclosure present (Medium-bound drafts only): Yes/No/N-A
- Freshness status (revisits only): Substantive update / Cosmetic only / N-A (new draft)
```

Nothing with a blocking flag reaches the Human Gate marked "ready." Report it to Randy
as not-yet-publishable until every blocking flag is resolved.

## Human Gate (Randy's step, not part of this skill)

After this runs: Randy reads every flag, resolves each (confirm/correct/cut), confirms
the war story is real and accurately told, confirms zero unresolved blocking flags
remain, then approves for publish. Only then does the piece move to image generation
and distribution.

## Gotchas

- **Check 9 vs. Check 10 — don't conflate them.** Check 9 covers Randy's own
  self-promotional links (lead magnet, his site) and only applies to Medium-bound
  drafts. Check 10 covers third-party citation links and applies everywhere. A link
  can trigger one, both, or neither — check them independently, not as one combined
  rule.
- **Check 9 catches more than the primary CTA** — a real test run found a second,
  easy-to-miss offsite link (a closing LinkedIn sign-off) that the original wording
  would have let slip through. Scan the *whole* piece for offsite links, not just the
  obvious one.
- **Check 1 fabrication risk is the highest-severity failure mode this whole skill
  exists to prevent** — if no confirmed source exists for a war story, flag and stop;
  never write a plausible-sounding incident to fill the slot, even under time pressure.
