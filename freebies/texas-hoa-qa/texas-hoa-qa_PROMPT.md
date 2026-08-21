# HOA Dispute Q&A Prompt — canonical version, Validate stage

NOT yet posted anywhere. Randy hasn't found/joined a dedicated Texas HOA
Facebook group yet — this is built and ready for the moment he does,
matching the same staged approach as the Texas landlord and GLP-1 prompts.

Built state-aware by design (asks the user's state, then instructs the AI
to look up that state's own real current law) rather than hardcoding Texas
citations — the mechanics generalize to any state, the actual statute
content doesn't, and this way expanding later is a scope change, not a
rebuild. Launch scope stays Texas-only for now, matching Randy's own real,
verifiable expertise (same reason the landlord prompt works).

---

## The prompt

Act as my HOA/condo association dispute assistant. I need help understanding
what's actually enforceable against me, not legal advice.

First, interview me one question at a time until you understand:
- What state and county I'm in
- Whether this is an HOA (single-family) or condo association
- What the association is claiming I violated, and any fine or demand amount
- What documents I already have (governing documents, bylaws, CC&Rs, rules,
  the actual violation notice) — paste the exact text where I have it
- What I don't have yet, so you can tell me what to go get

After the interview:

1. Tell me exactly which documents I still need to track down — filed
   governing documents from the county real property records, the
   association's specific rule being cited, meeting minutes, financial
   records — whatever is actually relevant to my situation, not a generic
   list.
2. Cite the exact current statute sections for my state that apply — verify
   they're accurate and current as of today's date, not from memory or a
   guess.
3. If the association's rule or fine demand isn't backed by a specific,
   properly filed, citable rule, say so explicitly — that gap is often the
   whole case.
4. Give me the answer as though I'm 8 years old, as a short summary at the
   top, varying the introduction sentence each time. Then give the full
   citation-backed breakdown below it.

Treat each new dispute as its own case — don't assume anything from an
earlier conversation still applies unless I say it does.

Always close with: "I am not an attorney. Consult one familiar with your
state's HOA/condo association law for guidance specific to your
situation."

---

## Calibration case — real, anonymized (2026-08-04)

Randy's own real, resolved HOA dispute — used here to calibrate the
prompt's tone and citation depth, not published as-is anywhere public. HOA
name and management company deliberately not used (settled out of court,
no need to name them). Every fact below is real and confirmed by Randy,
not AI-embellished.

**What happened:** a Texas condo association fined Randy $50 for a minor
driveway oil spot, then escalated to $250 after he questioned it, demanding
"professional cleaning" — a standard that didn't actually exist anywhere
in the association's own filed rules. Randy used AI to pull the association's
recorded governing documents and cross-check them against Texas Property
Code § 202.006, which states a dedicatory instrument (a filed rule) "has no
effect until the instrument is filed" in the county's real property records.
The "professional cleaning" requirement wasn't in the filed 2019 rules at
all — an unenforceable "ghost rule." He also documented widespread,
unaddressed oil staining elsewhere on the property, supporting a selective-
enforcement pattern, and sent certified letters disputing the fine on that
basis.

**Outcome:** the association dropped the fine and never produced
documentation for the standard they'd tried to enforce. Settled, no court
filing, no admission of anything by either side.

**Why this matters for the prompt:** the real lesson isn't "get angry" —
it's "make the HOA prove the rule they're citing actually exists and was
properly filed." That's a mechanical, citable question an AI can help
answer fast. The prompt above is built to surface exactly that gap.

---

## Status

**Live and tested — 2026-08-04.** Randy found a real Texas HOA-dispute
Facebook group, tested this prompt against a real live question, and
confirmed it worked. Companion Short ("I Beat My HOA Fine With Just Two
Words," built from Randy's own calibration case below) published the same
day to YouTube, LinkedIn, and Facebook — first comment links this prompt
directly (Google Doc). YTD-0019 marked completed.

Next real step: watch for recurring-question volume in the group before
considering the PDF/tool product-ladder step (banked in Randy's Brain
Dropping) — same Validation Gate used elsewhere in this project.

**Real prior-art note:** at least two existing sites (hoarebuttal.com,
fixmyhoaviolation.com) already offer AI-powered HOA-violation-audit tools
built around Texas Property Code Chapter 209 — this space isn't novel as a
tool. Randy's real edge is the same one already working in the landlord
group: real presence and trust in a community, not a SaaS landing page.
