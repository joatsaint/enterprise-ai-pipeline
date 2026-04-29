# MASTER_PLAN.md — AI Transcript Business
## Unified Roadmap: Transcript Downloader + PDF Business + Automation

**Version: 1.5** — Created April 2026. Owner: Randy.
**Last Updated:** April 29 2026 — FIRST OPT-IN RECEIVED. Email 2 sent manually. Full system operational.

---

## The Core Engine (How Everything Connects)

This is not just a transcript downloader. It is a commercial research engine
that feeds a content business. Every component feeds the next.

```
YouTube Channels
       ↓
Transcript Downloader (Claude Code project)
       ↓
Pain Point Extraction (AI analysis module)
       ↓
┌──────────────────────────────────────────┐
│  FREE: PDF Lead Magnet (5-8 pages)       │
│  PAID: PDF Guide ($7-$17)                │
└──────────────────────────────────────────┘
       ↓
Mailchimp Landing Page → Email List
       ↓
3-Email Welcome Sequence → First Sale
       ↓
Scale: More PDFs → Larger List → Higher Revenue
```

**The unfair advantage:** Competitors researching these topics manually
spend hours per channel. Your system does it in minutes and improves
with every transcript added.

---

## The One Metric That Matters First

**First email signup on the landing page.**

✅ ACHIEVED — April 29 2026. First opt-in received. Email 2 sent manually.
Proof of concept confirmed. Funnel works end to end.

Next metric: **First paid sale.**

Everything else — paid products, automation, scaling — is secondary
until one real person buys your paid PDF. Do not skip to Stage 6
before achieving this.

---

## Prioritized Stage Roadmap

Stages are ordered by what unlocks what, not by calendar days.
Complete each stage before moving to the next. No skipping.

---

### STAGE 1 — Complete the Research Engine Foundation
**Type:** Technical (Claude Code)
**Status:** ✅ COMPLETE — 17/17 tests passing
**Unlocks:** Everything downstream

**What to build:**
- Run PHASE1_UPGRADE_PROMPT.md in Claude Code
- Verify: single URL → clean .md transcript with headers
- Verify: category confirmation prompt works (auto-suggest + override)
- Verify: orchestrator pipeline runs cleanly with run summary output
- Verify: all tests pass

**Done when:** Paste a YouTube URL, get a clean categorized .md file,
see the run summary. Token reduction reported. No crashes.

---

### STAGE 2 — Batch Channel Download
**Type:** Technical (Claude Code)
**Status:** ✅ COMPLETE — 27/27 tests passing, Webshare proxy active
**Unlocks:** Stage 3 (need bulk transcripts for pain point analysis)

**What to build:**
- Channel homepage URL → batch download all available transcripts
- Target: 20+ transcripts per channel minimum
- Incremental mode: only download new videos since last run
- Priority channel category for this stage: AI careers, skills, job paths,
  prompt engineering (this feeds the PDF business niche)
- Research the actual maximum transcripts retrievable per channel
  before building (YouTube limits vary)

**Channel targets for initial batch (populate channels.json):**
- [ ] 5-8 top AI career / skills / prompt engineering YouTube channels
- Focus: channels covering AI jobs, no-code AI, ChatGPT for work,
  career pivots into AI

**Prerequisites before building Stage 2:**
- Get a free YouTube Data API v3 key from console.cloud.google.com
- Steps: New Project → Enable YouTube Data API v3 → Create Credentials → API Key
- Add key to .env as YOUTUBE_API_KEY
- Free tier (10,000 units/day) is sufficient — no billing required

**What to build (updated):**
- Channel homepage URL → batch download transcripts AND comments per video
- comment_fetcher.py pulls top 100 comments by relevance for each video
- Comments saved as separate _comments.md file alongside transcript
- Randomized pause intervals between requests (not fixed — bot signature)
- Target: 20+ transcript + comment pairs per channel minimum
- Research actual maximum transcripts retrievable per channel before building

**Done when:** Point at one channel URL, get 20+ clean .md file pairs
(transcript + comments). Run it again — only new videos download.

---

### STAGE 3 — Pain Point Extraction Module
**Type:** Technical (Claude Code) + Business crossover
**Status:** ✅ COMPLETE — 45/45 tests passing, first report generated
**Unlocks:** Stage 4 (PDF content comes from this output)

**What to build:**
- New module: src/analyzer/pain_point_extractor.py
- Scans all transcripts AND comment files in a specified category
- Comments are weighted higher than transcripts for question/pain point signals
- Uses Claude API to identify and count:
  - Most repeated questions across all transcripts
  - Most repeated pain points (frustrations, blockers, fears)
  - Most repeated desired outcomes (what people want to achieve)
- Output: structured report per channel AND aggregated across all channels
- Format: pain_points_YYYY-MM-DD.md saved to knowledge_base/reports/

**Sample output structure:**
```
TOP QUESTIONS (across 8 channels, 160 transcripts)
1. "How do I get an AI job without a CS degree?" — 47 mentions
2. "What certifications actually matter for AI roles?" — 38 mentions
3. "How long does it take to transition into AI?" — 31 mentions

TOP PAIN POINTS
1. Overwhelm — too many tools, don't know where to start (89 mentions)
2. Imposter syndrome — feel unqualified despite learning (62 mentions)
3. No portfolio proof — don't know what projects to build (54 mentions)
```

**Done when:** Run the extractor against your AI careers channel group,
get a ranked list of questions and pain points with mention counts —
sourced from both transcript content and audience comments.

---

### STAGE 4 — First PDF Lead Magnet + Landing Page
**Type:** Business
**Status:** ✅ COMPLETE — April 15 2026
**Unlocks:** Stage 5 (need something to drive traffic to)

**What to do:**
- Review Stage 3 output — identify the single most-asked question
- Choose one hyper-specific niche angle
  (NOT "AI careers" — something like "5 AI jobs you can get in 90 days
  without a CS degree")
- Validate on Quora and Reddit: are people actively asking this?
- Write a tight 5-8 page PDF guide:
  - Actionable format: checklist, roadmap, or step-by-step
  - Source material comes entirely from your transcript research
  - NOT a general overview — solve one specific problem completely
- Set up Mailchimp landing page
- Write 3-email welcome sequence:
  - Email 1: Deliver the free PDF
  - Email 2: Build trust / tell your story
  - Email 3: Soft pitch to paid guide (Stage 6)
- Test the full flow: signup → email delivery → sequence fires

**Done when:** You can sign up on your own landing page and receive
all three emails correctly. The PDF downloads. The flow works end to end.

**COMPLETED April 15 2026:**
- PDF lead magnet built (8 pages, matches carousel color palette)
- Mailchimp landing page live (Lead Generation — Wild Country template)
- Headline: "Stop Learning the Wrong AI Skills"
- PDF hosted on Mailchimp, delivered automatically on opt-in
- LinkedIn carousel posted with landing page link in first comment
- Carousel CTA: "The AI Skills That Won't Be Replaced — Grab it in first comment"
- LinkedIn URL: linkedin.com/in/randy-skiles

**PDF production note:** Use Claude Code + Cowork to draft the PDF content
from your transcript research output. Claude drafts, you review and refine.
Keep it under 10 pages. Actionable beats comprehensive every time.

---

### STAGE 5 — First Traffic Push (Manual)
**Type:** Business
**Status:** 🔄 IN PROGRESS — LinkedIn Posts 1 & 2 live, Email 2 ready, traffic push active
**Unlocks:** Stage 6 (need proof of signup before building paid product)

**Platform priority order:**
1. **Quora** ⭐⭐⭐⭐⭐ — Long answers with links are expected. High SEO value.
   Answers surface in Google for months. Best ROI for this model.
2. **LinkedIn** ⭐⭐⭐⭐⭐ — Your strongest platform given IT background.
   Carousel posts and personal stories outperform plain links.
   Drive to landing page in comments, not the post itself.
3. **Reddit** ⭐⭐⭐⭐ — High traffic but link-hostile. Lead with genuine
   value first. r/learnmachinelearning, r/artificial, r/cscareerquestions.
4. **Facebook Groups** ⭐⭐⭐ — Join 5-10 active AI/career groups.
   Answer questions, mention free guide only when directly relevant.
5. **Pinterest** ⭐⭐⭐ — Underrated for PDF content. Simple infographic
   pins linking to landing page. Set-and-forget long-tail traffic.
6. **Twitter/X** ⭐⭐ — Good for visibility, lower conversion. Use to
   amplify LinkedIn and Quora content only.

**What to do:**
- Write 3-5 genuine, helpful answers on Quora and Reddit
- End each answer naturally: "I put together a free guide on exactly
  this" + link where allowed
- Post one LinkedIn article or carousel on the same topic
- Share in 2-3 Facebook groups where it fits organically

**Done when:** First email signup on the landing page.
**Stop. Celebrate. Then move to Stage 6.**

---

### STAGE 6 — First Paid Product
**Type:** Business
**Status:** NOT STARTED
**Unlocks:** Stage 7 (validated model = worth building automation for)

**What to do:**
- Pick the 2nd most-asked question from Stage 3 as the paid guide topic
- Price point: $7-$17 (low friction for first purchase, proof of concept)
- Set up Gumroad or Mailchimp product page
- Add paid guide offer into Email 3 of welcome sequence
- Write 1-2 additional nurture emails

**Done when:** First paid sale, any amount.
**This validates the entire system.**

---

### STAGE 7 — Knowledge Base + On-Demand Q&A + Daily Digest
**Type:** Technical (Claude Code)
**Status:** NOT STARTED
**Unlocks:** Ongoing research efficiency, content calendar automation

**What to build:**
- knowledge_base/indexer.py — index all .md transcripts
- knowledge_base/query.py — on-demand Q&A against transcript library
- knowledge_base/digest.py — daily summary of new content by category
- Windows Task Scheduler automation for daily digest

**This stage runs in parallel with Stage 6 traffic work.**
It is not a blocker — it makes future content production faster.

**Code quality tasks to complete in this stage:**
- Add professional docstrings and inline comments to all src/ modules
  (explains why each section exists, not just what it does)
- Add startup environment variable validation function — fail fast with
  clear error if required keys are missing at launch
- General code refactoring for efficiency (defer until after first sale)
- These are Claude Code tasks — scaffold via docs/ prompt files


**Recursive OS Integration (Stage 7 addition):**

Add three folders to project root based on Recursive Operating System framework:

knowledge/              ← persistent context improving every session
  consultants/          ← Sabrina, Greg, theMITmonk transcripts as queryable personas
  audience/             ← pain point reports (move from knowledge_base/reports/)
  me/                   ← voice.md, brand rules, personal preferences
skills/                 ← scaffold prompts renamed and formalized
  extract-pain-points.md
  generate-titles.md
  write-linkedin-post.md
  atomize-content.md
  draft-email.md
projects/               ← content_drafts/ renamed

Session end hook: Save new learnings to knowledge/ before closing Claude Code.
Skill chaining target: Pain-Extractor → Title-Generator → Script-Writer → Publisher

CREATE NOW (15 minutes, no code):
knowledge/me/voice.md — Randy's voice patterns and brand rules
Claude Code references this every session for consistent content output.

**New analyzer modules to add in this stage:**

src/analyzer/title_pattern_analyzer.py
- Extracts video titles from existing transcript markdown headers
- Adds view count field to channel download (YouTube Data API v3 already integrated)
- Sends titles + view counts to Claude for pattern analysis
- Identifies title formulas, hook structures, topic selection patterns
- Output: knowledge_base/reports/title_patterns_YYYY-MM-DD.md

src/analyzer/script_generator.py
- Takes pain point topic from existing report
- Takes title pattern report as context
- Generates complete video script matching proven hook structures
- Outputs: hook line, full script, thumbnail concept, image prompt
- Saves to: content_drafts/scripts/YYYY-MM-DD_topic-name.md
- One script session produces content for all 7 atomized platform versions

**Manual version available NOW (no code needed):**
1. List 20 video titles from Matt Wolfe or Jack Roberts transcript folder
2. Paste into Claude chat — ask for title pattern analysis
3. Ask Claude to generate 10 video ideas using patterns
4. Ask Claude to write full script for best idea
5. Script becomes YouTube video + LinkedIn post + email + website article
See CONTENT_ATOMIZATION_RULES.md for platform-specific distribution rules

---

### STAGE 8 — Semi-Automation Layer
**Type:** Technical + Business
**Status:** NOT STARTED
**Unlocks:** Scale without proportional time increase

**Only build this after Stage 6 proves the model works.**
Full automation gets accounts banned. Start semi-automated.

**Recommended semi-auto workflow (10-15 min/day):**
- Script scrapes questions from Quora and Reddit (read-only, no posting risk)
- Feed top questions into Claude to draft answers
- You review, lightly edit, post manually
- Pinterest can be more fully automated via Tailwind scheduler

**What to automate in this stage:**
- Question scraping across multiple platforms on a schedule
- Batch answer drafting using Claude API with transcript context
- Pinterest pin creation from PDF guide content
- Email sequence extensions triggered by subscriber behavior
- Pain point extraction running automatically on new transcripts

**Platform scraping research required BEFORE building (API terms changed):**
- Reddit: Changed API terms 2023 — paid API now required above low thresholds.
  Research current r/learnmachinelearning, r/artificial, r/cscareerquestions
  access options. RSS feed fallback may be the only free approach.
- Quora: Official API discontinued. Scraping violates ToS. Use Quora Partner
  Program or monitor via Google Alerts for Quora question URLs instead.
- Facebook Groups: No public API for group content. Read-only scraping
  feasible only for public groups. Private groups not accessible.
  Assess feasibility separately before building.
- YouTube comments: ✅ Already built — comment_fetcher.py handles this.
- LinkedIn: No scraping API. Manual monitoring only — automate only posting.
- Pinterest: Official API available — lowest risk platform to automate.
- Twitter/X: Paid API only since 2023. RSS workarounds exist but unreliable.

**Recommended build order for scraping:**
1. Pinterest (official API, low risk) — automate pin creation first
2. Reddit RSS feeds (public subreddits only, no auth required)
3. Google Alerts → email → parse (catches Quora + news + blogs)
4. Evaluate paid Reddit API if ROI justifies cost

---


---

## Immediate Next Actions (Outside Claude Code)

These are your next moves in priority order. Do not skip to #2 before completing #1.

**1. ✅ COMPLETE — Channels registered and pain point analysis done**

**Registered channels (8 total):**
- ✅ AI News & Strategy Daily | Nate B Jones — 20 transcripts, 0 comments
- ✅ Matt Wolfe — 19 transcripts, 19 comments
- ✅ Jeff Su — 20 transcripts, ~20 comments
- ✅ Learn with Lukas — 20 transcripts, ~20 comments
- ✅ Tina Huang — 20 transcripts, ~20 comments
- ✅ Tech With Tim — 20 transcripts, ~20 comments
- ✅ Technical Program Management Hub — 18 transcripts, 3 comments
- ✅ AI Explained — 20 transcripts, 20 comments

**Library total:** 159 files across 3 groups
**Pain point reports generated:** 3 (improving with each run)
**Final report:** knowledge_base/reports/pain_points_2026-04-13_ai-and-claude-code.md
— 50 transcripts + 29 comment files analyzed

**2. ✅ COMPLETE — Pain point extractor re-run with comments included**
Final report: pain_points_2026-04-13_ai-and-claude-code.md
50 transcripts + 29 comment files. PDF topic confirmed from data.

**3. ✅ COMPLETE — PDF lead magnet built and delivered**

**Confirmed PDF topic from pain point data:**
*"The AI Skills That Won't Be Replaced: 7 Capabilities Worth Building Right Now (Backed by Data)"*

This directly addresses:
- Pain point #3: Difficulty determining which AI skills will remain valuable (4 videos)
- Pain point #5: Lack of understanding about which roles become obsolete (4 videos)
- Question #4: How to identify skills that remain valuable as AI advances (3 videos)
- Desired outcome #3: Clear understanding of AI skills for career advancement (3 videos)
- Your differentiator: "Backed by data" — you analyzed 50 videos + 29 comment files

PDF built: "The AI Skills That Won't Be Replaced: 7 Capabilities Worth Building Right Now"
File: docs/The AI Skills That Wont Be Replaced - Lead Magnet.pdf
8 pages, IBM Plex Sans, charcoal/navy/teal color scheme matching carousel.
Hosted on Mailchimp. Delivered automatically via Email 1 on opt-in.

**GitHub status:** github.com/joatsaint/youtube-downloader (public)
Latest commit: Knowledge base modules complete — indexer.py, query.py, digest.py
45/45 tests passing. CI/CD green. Branch protection active.
CLAUDE.md v1.6 — all module specs written.
DECISIONS.md v2.0 — 11 architectural decision records.

**Knowledge base modules completed April 29 2026:**
- ✅ indexer.py — scans /transcripts/, builds knowledge_base/index.json
- ✅ query.py — on-demand Q&A against indexed transcripts with citations
- ✅ digest.py — daily automated summary by channel group, scheduled operation

**Proof assets saved to /assets/:**
- terminal_running_test_suite_39-tests-passing.png
- test_phase4.py.png (45/45 green)

**4. Write LinkedIn Article 1 this week**
You now have everything you need:
- A working AI pipeline (proof of capability)
- Market research data from 20 real transcripts (proof of methodology)
- A documented journey from manual copy-paste to automated extraction (the story)
- 39 passing tests and a GitHub repo (proof of execution)

Article 1 is the cornerstone piece — see LINKEDIN_SERIES_FRAMEWORK.md in docs\.
90 minutes. Write it this week. Everything else in the series links back to it.

---

## Daily Non-Negotiables

Protect these even on heavy work days. They compound.

| 🐿️ Squirrel Video | 💼 LinkedIn | 📚 Claude Code Academy |
|---|---|---|
| 1 video per day | 3 posts per week | 1 lesson minimum |
| Builds audience consistently | Highest leverage for AI job search | Compounds into CCA-F |

---

## PDF Side Project Integration Notes

The PDF business is not a separate project — it runs on the same
transcript research infrastructure. Key integration points:

- **Source material:** Pain point extraction output (Stage 3) is the
  direct input for every PDF guide written. No guessing what people want.
- **Production tool:** Claude Code + Cowork drafts PDF content.
  You review, refine, approve.
- **Format rule:** Every PDF must be actionable — checklist, roadmap,
  or step-by-step. Essays do not convert.
- **Content calendar:** Each PDF guide topic comes from the ranked
  question list produced by the extractor. Work down the list in order.
- **Reinvestment rule:** Revenue from paid guides funds expansion of
  the channel list and transcript library, which produces better research,
  which produces better guides. This is the flywheel.

---

## Vinh Nguyen Best Practices Applied to This Project

From the "Becoming a Claude Architect" framework — all applied:

| Principle | Where Applied |
|---|---|
| Orchestration layer owns the pipeline | orchestrator.py — central coordinator |
| Sub-agent isolated context, pass explicitly via state | State object passed between all modules |
| Tool count max 4-5 per agent | Hard rule in CLAUDE.md |
| Deterministic stop conditions | Retry-once-then-skip, never natural language parsing |
| Explicit tool descriptions | Rule in CLAUDE.md — no vague or overlapping descriptions |
| Programmatic hooks over prompt suggestions | Security rules enforce sequence in code |
| Plan mode for complex multi-file work | GUIDE.md documents when to use each mode |
| Human handoff triggers (deterministic) | Phase 3 Q&A agent design |

---

## Open Research Items (address before building each stage)

These need answers before the relevant stage starts:

- **Stage 2:** What is the actual maximum number of transcripts
  retrievable per channel via youtube-transcript-api? Does it vary
  by channel size? Is there a pagination approach?

- **Stage 2:** YouTube Data API v3 comment fetch — does "relevance" sort
  consistently surface the highest-signal comments, or does "top" rating
  perform better for pain point extraction? Test both on one channel first.

- **Stage 3:** What is the most token-efficient way to run pain point
  extraction across 160 transcripts without hitting context limits?
  (Chunking strategy needed — see Vinh's context window notes)

- **Stage 4:** Mailchimp free tier limits — how many contacts and
  emails per month before paid tier required?

- **Stage 8:** Platform API research completed in session — see Stage 8
  notes above. Reddit and Quora have significant restrictions post-2023.
  Pinterest official API is the lowest-risk first target.
  Build order: Pinterest → Reddit RSS → Google Alerts → evaluate paid options.

---


---

## The Manager Framework — Weekly Operating System

**Time budget:** 3 hours per week, allocated as follows:

| Hour | Day | Task |
|---|---|---|
| Hour 1 | Mon/Tue | Create — write and publish one LinkedIn post |
| Hour 2 | Mon/Tue | Engage — replies, one Quora answer, one Facebook group post |
| Hour 3 | Thu/Fri | Build — rotate through email sequence, paid PDF, YouTube video |

**Weekly review (Sunday, 15 minutes):**
Check three numbers only:
- LinkedIn post impressions
- Mailchimp opt-ins total
- Gumroad sales total

**Standing rules:**
1. One platform mastered before adding another — LinkedIn first
2. Content creation before content optimization
3. New ideas written to PRODUCT_IDEAS.md, ignored for 30 days
4. Paid PDF ships before any new free content is built
5. Personal outreach to every carousel engager — fastest path to first sale

**Platform priority:**
- Primary: LinkedIn (all original content)
- Support: Quora (one answer per week, set and forget SEO)
- Repurpose only: Facebook, YouTube community tab
- Do NOT start yet: TikTok, Instagram, Pinterest, Twitter/X

---

## 90-Day Execution Checklist

### Weeks 1-4 — Foundation
- ✅ Carousel posted on LinkedIn (April 15 2026)
- ✅ Landing page live on Mailchimp
- ✅ PDF lead magnet delivering (browser redirect on signup)
- ✅ Email 2 written — AI Orchestration deep dive (fires immediately on signup)
- ✅ LinkedIn Post 1 live — April 27 2026 (AI Orchestration)
- ✅ LinkedIn Post 2 live — April 29 2026 (You Are Not Behind)
- ✅ Post 1 & 2 first comments posted with landing page link
- ✅ Posts shared to 5 AI LinkedIn groups
- ✅ 2 Quora answers posted (April 27)
- ✅ 10+ Facebook group comments posted (April 27-28)
- ✅ 10+ LinkedIn post comments (April 28)
- ✅ Personal outreach to carousel engager (Tash — April 27)
- ✅ First YouTube personal brand video created and live (April 27)
- ✅ First email opt-in received — April 29 2026 🎉
- ✅ Email 2 manually sent to first subscriber — April 29 2026
- ⬜ Email 3 written — soft pitch to paid PDF
- ⬜ Reddit answers (eligible May 5 2026 — 7-day account rule)

### Weeks 5-8 — First Paid Product
- ⬜ Paid PDF topic confirmed from pain point report rank #2
- ⬜ Gumroad account set up (free)
- ⬜ Paid PDF outline built in Claude Code
- ⬜ Paid PDF written and uploaded to Gumroad
- ⬜ Email 3 updated with Gumroad link
- ⬜ LinkedIn post announcing paid PDF

### Weeks 9-12 — First Sale Push
- ⬜ 3 Quora answers live and driving traffic
- ⬜ LinkedIn carousel #2 posted
- ⬜ First YouTube video uploaded (carousel repurposed via CapCut Pro)
- ⬜ Personal outreach to 10 warm LinkedIn connections
- ⬜ FIRST PAID SALE — stop and celebrate

---

## What Not To Build Until After First Paid Sale

- Faceless YouTube channel (separate business, different audience)
- TikTok, Instagram Reels, Pinterest, Twitter/X accounts
- UltraPlan for Claude Code (scaffold prompts already cover this)
- Resume crossmatch prompt tool (PRODUCT_IDEAS.md Idea 002)
- Executive AI integration framework (PRODUCT_IDEAS.md Idea 003)
- Multi-platform posting automation
- Paid advertising of any kind

## What's NOT In Scope (until Stage 6 is complete)

- Multi-model routing (Haiku vs Sonnet vs Opus per task)
- Full automation of any platform posting
- Vector database for knowledge base (flat file index is sufficient for now)
- Mobile app or web interface
- Paid advertising of any kind
- Additional business niches beyond AI careers/skills

---

*Version 1.5 — April 29 2026*
*Updated: First opt-in received, Email 2 sent, full system operational*
