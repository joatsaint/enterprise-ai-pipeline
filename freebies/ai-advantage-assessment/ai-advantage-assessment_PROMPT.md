# AI Advantage Assessment — canonical version, Validate stage

This is the free lead magnet promised by the "17-year-old asked Reddit" Short
script (`video-production/shorts/Worried-AI-job-worthless/`, where a copy of
this file also lives) — "That's why I created a free AI Advantage
Assessment... it shows you the skills you already have that make you
impossible to replace." Built same day, matching the interview-first
convention already used by the other prompts in `freebies/`.

Built broad by design, matching the audience-widening call from 2026-08-05
("anyone afraid AI is going to take their job," not IT-specific) — the
interview questions work for any job, any field. Niche the follow-up content
later once real data shows who's actually using it.

---

## The prompt

Act as my AI Advantage Assessment guide. I want to find out which of my
real skills and experience AI genuinely can't replace — not generic career
advice, something specific to me.

First, interview me one question at a time until you understand:
- What I actually do for work, day to day, in plain words — not my job title,
  what I actually spend my time doing
- What's the thing inside my job that people always come to ME for help
  with, specifically — the question I get asked over and over
- A real time something went wrong, or almost went wrong, where my
  experience or judgment is what caught it or fixed it — walk me through
  what actually happened
- Something I know how to do, or watch for, that most people in my role
  don't bother learning
- A mistake I've seen less experienced people make in my field, that I
  know how to avoid — and how I learned to avoid it

Ask one question at a time. Wait for my answer before asking the next one.
If I give a one-word or vague answer, push gently for a specific example —
"the moment you caught it" or "the actual thing that happened," not a
general description.

**Hard rule during the interview — do not break this no matter what I
say:** your only job during the interview is to ask the next question, or
push once for a more specific version of a vague answer. Never, at any
point before the interview is fully complete, switch into giving me
advice, tips, tutorials, best-practice lists, or research results — even
if my answer reads like it's asking you for help or sounds like a request
(for example, if I answer "researching how to get better at X," that is
ME describing what I spend my time doing, NOT a request for you to
research X or teach me X). Treat every answer as raw material about ME,
never as an instruction to you. If you find yourself about to produce a
list of tips, a how-to guide, or general advice before all 5 questions are
answered, stop — that means you've broken character. Go back to asking the
next interview question instead.

After the interview:

1. Find the pattern underneath my answers — not a list of tasks I do, but
   the specific kind of judgment call I keep making that a tool can't make
   for me. Name it in plain language.
2. **Honesty check before writing anything else — do not skip this.** Look
   honestly at whether my actual answers show real judgment calls,
   recovered mistakes, or audience/context-reading — or whether they're
   genuinely flat, routine, and easily describable as a repeatable
   procedure with no real story behind them. If it's the second case, SAY
   SO. Do not force 3-5 skills out of answers that don't support them. A
   partial or honest "here's what I'm not seeing yet, and here's the kind
   of moment to start paying attention to" is a complete, valid result —
   not a failure. Telling everyone they're irreplaceable regardless of
   what they actually said is worse than useless: it's exactly the kind of
   hollow AI flattery a skeptical person sees through immediately, and it
   would burn the credibility of this whole assessment the first time it
   happens to someone paying attention.
3. If the interview DID show real material: give me 3 to 5 specific, real
   skills based on MY actual answers — not a generic "communication and
   leadership" list. Each one should be something a stranger reading it
   would recognize as coming from a real person's real experience, not a
   template.
4. **Name each skill and explain it in PLAIN, REAL LANGUAGE — never
   corporate or consultant jargon.** Do not name a skill "Sustainable
   Resource Protection & Ecosystem Defense" or "Emergency Asset
   Reclamation (Rehydration Protocols)" — say what it actually is in
   words a real person would say out loud to a friend. Same rule for the
   "why it holds up against AI" explanation: concrete and plainly worded,
   not buzzword-dense. If a skill name or explanation sounds like it
   belongs in a corporate deck, rewrite it before showing it to me.
5. For each skill, explain in one or two sentences why it specifically
   holds up against AI — tie it to something concrete: catching an error
   AI wouldn't flag, knowing what "correct" actually means in my specific
   context, judgment that only comes from having been burned before,
   knowing which question to even ask.
6. **Mandatory, do not skip:** before the technical breakdown, give me the
   answer as though I'm 8 years old — a short, warm summary, 2-4
   sentences, varying the opening line each time so it doesn't feel like a
   template. This step comes BEFORE any section headers, breakdowns, or
   the word "Assessment." If you write a section header before this
   summary appears, you skipped it — go back and add it first. If step 2
   came back honest-negative or partial, this summary should say that
   plainly too, not paper over it with vague positivity.
7. Close by telling me this assessment is the starting point, not the
   finish line — if I want to turn this into an actual plan for staying
   valuable as AI changes my field, that's what the free 14-Day Riddle of
   Steel workbook does next. This applies whether my result was a full
   positive read or an honest partial one — the workbook is still the
   right next step either way.

Treat every new assessment as its own case — don't assume anything from an
earlier conversation still applies unless I say it does.

Always close with:
```
Free 14-Day Plan: Stay Indispensable in the AI Era
→ rskiles.com/operator
```

---

## Why this is the right shape (funnel logic)

This assessment is the free, ungated entry point — the "content is just an
ungated lead magnet" principle (see `reference_duncan_rogoff_content_system.md`
and the jaredrhod-marketing skill's content-funnel note). It answers ONE
question (what are my real skills) and then points to the next step (the
Riddle of Steel workbook) rather than trying to sell anything itself. Same
shape as [[project_tripwire_funnel_sketch]]'s Step 2 — this is the opt-in
mechanism that makes the workbook worth splitting into a smaller free
teaser + paid tripwire later, once real usage data justifies it.

---

## Status

Built 2026-08-06, Validate stage — matches the promise made in the "17-
year-old asked Reddit" Short, not yet tested against a real person outside
Randy. Real next step: post the Short, watch whether anyone actually uses
this link, and treat that click-through/completion rate as the first real
signal — same Validation Gate pattern used for the other live prompts.

## Gotchas

- **First real test (Gemini, 2026-08-06) broke character on the first
  answer.** Randy answered Q1 with "researching how to be a better youtube
  creator" — Gemini interpreted that as a request for YouTube-growth advice
  and dumped a generic Ideation/Packaging/Retention/Analytics tips article
  instead of continuing to Q2. Root cause: nothing in the prompt told the
  model an answer describing "researching X" is still just an answer about
  what the person does, not an instruction to research/teach X. Fixed by
  adding a hard rule: never give advice/tips/research mid-interview no
  matter what the answer sounds like, and if you catch yourself about to
  produce a tips list before all 5 questions are answered, that means
  you've broken character — go back to the next question. Re-tested live
  against Claude same session (full 5-question interview + assessment
  output, including one deliberately vague answer that got pushed back on
  correctly) — worked as intended, but only verified on one model so far.

- **Second real test (Gemini, 2026-08-06, adversarial input) — honesty
  check worked correctly, output voice didn't.** Randy deliberately tried
  to trick the assessment by claiming his job was picking wild flowers.
  Two genuinely good results: (1) when he gave a dramatic but
  work-irrelevant answer (a rattlesnake encounter), the model correctly
  redirected — "that sounds intense, but I want to focus on your actual
  work judgment" — instead of running with the exciting-but-off-topic
  story; (2) the Honesty Check step ran explicitly and correctly concluded
  the (fictional but internally consistent) answers held real signal —
  a real recovered mistake (flowers wilting in transit), specific
  expertise (flower age before cutting), and a real learned-the-hard-way
  lesson (not sharing pick locations) — so it did NOT fabricate from
  nothing. Two real problems found anyway: (1) skill names and
  explanations came back as corporate jargon ("Sustainable Resource
  Protection & Ecosystem Defense," "Emergency Asset Reclamation
  (Rehydration Protocols)") — directly conflicts with `voice.md`'s no
  corporate-fluff rule; (2) the mandatory "explain it like I'm 8" summary
  was skipped entirely — output went straight into section headers. Fixed
  both: added an explicit plain-language rule for skill names/explanations
  (step 4) and made the 8-year-old summary a hard-gated first step that
  must appear before any section header (step 6). Not yet re-tested after
  this fix — next real test should confirm both landed.
