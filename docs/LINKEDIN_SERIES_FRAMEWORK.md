# LinkedIn Article Series Framework
## IT Professional to AI Architect: A Documented Journey

**Owner:** Randy Skiles
**Created:** April 2026
**Target Audience:** IT Directors, IT Managers, Senior IT Professionals
**Publishing Schedule:** Tuesday or Wednesday, 10 AM Central — one article per week
**Rule:** Bank three articles before publishing Article 1. Never publish without a buffer.

---

## Series Brand Identity

**Series Name:** *From Infrastructure to Intelligence*
**Tagline:** *25 years of IT. Starting over. Documenting everything.*

**The core brand promise to the reader:**
"I have the same background you do. I am walking the path your team is about to walk.
I will document every prerequisite they glossed over, every hour I lost, every decision
that changed the direction of the build — so you don't have to figure it out alone."

**What makes this series different from every other AI tutorial on LinkedIn:**
- Written by a career IT professional, not a developer
- Documents failure as thoroughly as success
- Connects every technical decision to a business outcome
- Treats the reader as a peer, not a student

---

## Audience Profiles

**Primary: IT Directors and VPs**
What they want: Validation that AI adoption is hard, a credible peer who has walked
the path, business case language they can use with their own leadership.
What they fear: Looking uninformed, investing in the wrong tools, their teams
disappearing into rabbit holes with no output.
What hooks them: Specific time/cost data ("6 hours lost to one undocumented
prerequisite"), business outcome framing, peer credibility signals.

**Secondary: Senior IT Professionals and Team Leads**
What they want: Practical, honest guidance they can actually use. The stuff the
official docs skip. Permission to not know everything.
What they fear: Being left behind as AI changes their field.
What hooks them: Specific error messages, exact fixes, "I wasted X hours so you
don't have to" framing.

---

## Universal Article Structure

Every article in the series follows this structure regardless of topic:

**Headline:** Problem-first or number-first. Never "Part X of My Journey."
- Good: "Claude Code Took Me 6 Hours to Install. Here's the 20-Minute Version."
- Good: "5 Things the Claude Code Course Assumes You Already Know (That Nobody Tells You)"
- Bad: "My Claude Code Journey — Part 2"

**Opening paragraph (2 sentences max):**
State the problem and promise the payoff. The reader decides in 8 seconds.

**Body (800-1,200 words total):**
- Subheading every 200-300 words (directors skim first)
- One specific "this is exactly what I did" moment — specificity is credibility
- One moment of failure or confusion — relatability is trust
- One concrete fix, decision, or insight — this is the value delivery

**Closing paragraph:**
Connect the technical experience to a business insight. This elevates it from
tutorial to thought leadership. End with one question to drive comments.

**CTA (comments, not post):**
Drive to landing page or next article in comments, not in the post body.
LinkedIn penalizes external links in posts.

---

## Two-Track Architecture

Articles alternate between two tracks, published weekly.
Both tracks are part of the same series — same author, same journey, two lenses.

**Track 1 — Technical Gotcha Series**
Audience lean: Senior IT professionals, team leads, hands-on implementers
Tone: Peer to peer, honest, specific, occasionally frustrated
Frame: "Here's what they didn't document and what it cost me"

**Track 2 — Strategic & Business Track**
Audience lean: Directors, VPs, decision makers
Tone: Thoughtful, outcome-focused, leadership-aware
Frame: "Here's what this means for your team and your budget"

---

## TRACK 1 — Technical Gotcha Series
### Course Adventures + Transcript Downloader Build

---

### ARTICLE 1 (CORNERSTONE) — Track 1
**Headline options:**
- "25 Years in IT. I Just Started Over. Here's Why I'm Documenting Everything."
- "I Have 25 Years of IT Experience. Claude Code Still Humbled Me."

**Type:** Origin story / Series introduction
**Word count:** 1,200-1,500 (cornerstone only — all others 800-1,200)
**Publish:** First. Everything links back to this.

**Outline:**
- Who I am: 25 years of IT infrastructure, systems auditing, enterprise ops
- The pivot decision: Why AI automation, why now, why Claude Code
- What I discovered immediately: This is not a beginner-friendly space
  despite being marketed as one
- What this series will document: Every prerequisite, every error, every
  gotcha, every decision that changed direction
- Who should follow: IT professionals considering the same pivot, directors
  evaluating AI tooling for their teams
- The honest admission: I am not a developer. I am an IT professional
  learning to build. That is exactly why this is worth documenting.

**Closing question:** "What's the biggest obstacle you've seen when your
team tries to adopt new AI tools?"

**LinkedIn SEO tags:** #ClaudeCode #AIAutomation #ITLeadership #CareerPivot
#ArtificialIntelligence #DigitalTransformation

---

### ARTICLE 2 — Track 1
**Headline options:**
- "Claude Code Took Me Hours to Install. Here's the 20-Minute Version."
- "5 Things the Claude Code Course Assumes You Already Know (That Nobody Documents)"

**Type:** Technical gotcha — installation prerequisites
**Word count:** 900-1,100

**Outline:**
- The promise vs. the reality: Course implies smooth setup, reality is a
  prerequisite minefield
- The undocumented list (each gets a paragraph):
  - WSL — why it's required, why it's not mentioned upfront
  - curl error 23 — what it means, exact fix
  - PATH configuration — C:\Users\joatsaint\.local\bin, why it matters
  - Node.js v24 — specific version requirement, where official docs fail you
  - GitHub CLI — installation via winget, why it's needed
  - Git initialization — the step everyone skips that breaks everything
  - Playwright MCP — what it is, why it's needed, where to find it
- Time cost: X hours of troubleshooting condensed to a 20-minute checklist
- The business implication: If one experienced IT professional lost this
  much time, what does that cost an enterprise team at scale?

**Closing question:** "Has your team hit invisible prerequisites with any
AI tooling? What was the cost?"

**Sidebar box (pull quote style):**
"The course is excellent. The prerequisites are a ghost town of missing documentation.
This article is the documentation that should have existed."

---

### ARTICLE 3 — Track 1
**Headline options:**
- "I Built an AI Tool to Solve My Own Problem. Here's What Happened Next."
- "From Manual Copy-Paste to Automated Pipeline: How a Frustrating Task
  Became a Claude Code Project"

**Type:** Transcript downloader origin story — proof of concept phase
**Word count:** 900-1,100

**Outline:**
- The manual pain: Copying YouTube transcripts by hand for research —
  why I was doing it, how long it took
- The "why not automate this" moment — what triggered the idea
- The proof of concept: One URL, one .txt file, one working tool
  built with Claude Code and Cowork
- What I expected Claude Code to do vs. what it actually did
- The first surprise: It worked faster than I thought but exposed
  how much I didn't know about production-grade thinking
- The lesson: Proof of concept is not the same as a finished tool —
  and that gap is where the real learning begins

**Closing question:** "What repetitive manual task in your workflow
is secretly begging to be automated?"

---

### ARTICLE 4 — Track 1
**Headline options:**
- "What 'Orchestration' Actually Means When You're Not a Developer"
- "The Architect Principle That Changed How I Build AI Tools"

**Type:** Technical concept — orchestration layer, CCA-F best practices
**Word count:** 900-1,100

**Outline:**
- The problem with my first build: Modules talking to each other directly,
  no central coordinator, one failure = cascade
- The air traffic controller analogy: Planes (modules) don't talk to each
  other — they all talk to the tower (orchestrator)
- What Vinh Nguyen's architect framework taught me about production thinking
- The practical difference: Before orchestrator vs. after orchestrator
  in the transcript downloader
- The state object explained in plain English — what it is, why it matters
- What this means for enterprise AI: Every AI agent your team builds
  needs a coordinator or you're building a system that fails silently
- The CCA-F connection: Why certification matters for building this correctly

**Closing question:** "Does your team have a standard architecture pattern
for AI agent pipelines, or is everyone building differently?"

---

### ARTICLE 5 — Track 1
**Headline options:**
- "The Day My Personal Research Tool Became a Business"
- "How Adding One Feature to an AI Tool Changed Its Entire Purpose"

**Type:** Transcript downloader evolution — from personal tool to business engine
**Word count:** 1,000-1,200

**Outline:**
- Where the tool was: Single URL, clean .md transcript, category sorting
- The business plan document: How a 7-day sprint plan reframed everything
- The pivot moment: Transcript downloader as research engine, not just
  personal productivity tool
- What changed in the architecture when business requirements entered:
  - Comment fetching for pain point research
  - Pain point extraction module
  - Channel batch download
  - The PDF business pipeline downstream
- The "silly GPT" connection: How Adam's framework validated the direction
- What IT directors should note: Internal tools become products when you
  document them properly — the same skills apply

**Closing question:** "Have you ever built an internal tool that had
commercial potential nobody recognized at first?"

---

### ARTICLE 6 — Track 1
**Headline options:**
- "Token Budgets, Rate Limiting, and Why Your AI Tool Will Get Banned
  Without Them"
- "The Production Checklist Nobody Gives You for Claude Code Projects"

**Type:** Technical — production best practices, security, rate limiting
**Word count:** 900-1,100

**Outline:**
- The gap between "it works on my machine" and production-ready
- Token efficiency: What it is, why it matters for cost, how the
  transcript cleaner achieves 30-50% reduction
- Rate limiting: Why YouTube will throttle you, why randomized intervals
  beat fixed ones, the bot signature problem
- Security rules: The CLAUDE.md approach to enforcing rules in code
  not just in prompts (Vinh Nguyen's programmatic hooks principle)
- The Caveman skill: What it actually saves (4-5% realistic), when to
  use it, when not to (learning phase — the explanations ARE the lesson)
- The audit log: Why every AI decision should be logged and what that
  enables downstream
- Business framing: This is the difference between a demo and a deployable

**Closing question:** "What's your team's standard for 'production ready'
when it comes to AI tools?"

---

### ARTICLE 7 — Track 1
**Headline options:**
- "I Taught an AI to Research My Market For Me. Here's the Architecture."
- "Pain Point Extraction at Scale: How 200 YouTube Transcripts Become
  a Product Roadmap"

**Type:** Pain point extractor — Stage 3 of the business pipeline
**Word count:** 1,000-1,200
**Publish:** After Stage 3 is built and verified

**Outline:**
- The research problem: How do you know what your market actually wants
  without spending weeks reading forums?
- The manual alternative: What Adam does by hand, how long it takes
- The automated solution: pain_point_extractor.py — what it does,
  how it works in plain English
- Comments vs. transcripts: Why audience comments are higher-signal
  data than creator transcripts for pain point research
- Sample output: What a ranked pain point list actually looks like
- The business application: From ranked list to PDF topic selection
  to product roadmap
- The IT director angle: This is market research automation — the same
  principle applies to internal stakeholder research, ticket pattern
  analysis, support queue analysis

**Closing question:** "How does your team currently identify recurring
pain points from unstructured data sources?"

---

## TRACK 2 — Strategic & Business Track

---

### ARTICLE A — Track 2
**Headline options:**
- "Why I Stopped Watching AI Tutorials and Started Building"
- "The Difference Between AI Literacy and AI Capability — And Why
  Your Team Needs Both"

**Type:** Strategic — consuming vs. building, the capability gap
**Word count:** 800-1,000

**Outline:**
- The tutorial trap: How it's possible to watch 100 hours of AI content
  and still not be able to build anything
- The moment the switch flipped: First working Claude Code project
- What "building" teaches that tutorials never can:
  real error handling, real constraints, real decisions
- For IT directors: Training budgets that produce consumption, not capability
- The certification question: What CCA-F is actually testing vs. what
  tutorial courses teach
- The recommendation: Build something small and real before investing
  in formal certification — in that order

**Closing question:** "How does your organization measure the difference
between AI literacy and AI capability in your team?"

---

### ARTICLE B — Track 2
**Headline options:**
- "The Hidden Cost of Undocumented AI Prerequisites"
- "What One Missing Sentence in the Docs Cost Me 6 Hours —
  and What It Would Cost Your Team"

**Type:** Strategic — documentation debt, enterprise AI adoption cost
**Word count:** 800-1,000

**Outline:**
- The specific incident: Claude Code installation, undocumented prerequisites
- The time math: X hours × senior IT professional hourly rate = real cost
- Scaled to a team: What that cost becomes at 5, 10, 20 team members
- The documentation debt problem in enterprise AI tooling:
  tools move fast, docs lag, teams pay the gap
- What good looks like: The CLAUDE.md approach — persistent context
  documentation that every session reads automatically
- The recommendation for directors: Budget for documentation time
  as part of every AI tool adoption, not as an afterthought
- The broader principle: The prerequisite gap is not unique to Claude Code —
  it is endemic to the AI tooling ecosystem right now

**Closing question:** "How does your organization handle documentation
debt when adopting new AI tools at speed?"

---

### ARTICLE C — Track 2
**Headline options:**
- "What a $5 Product Strategy Taught Me About AI Automation ROI"
- "The 'Buyer List' Principle: Why Proving Value Beats Chasing Users"

**Type:** Strategic — the silly PDF/GPT model applied to AI automation ROI
**Word count:** 900-1,100

**Outline:**
- Adam's core insight: Free lead magnets attract freeloaders, $5 products
  build buyer lists — the filter is the product
- The parallel in enterprise AI: Proof of concept tools that nobody uses
  vs. tools people pay to access (even internally via chargeback)
- The AOV principle applied internally: A tool that saves 2 hours/week
  has an implicit value — document it and you have your business case
- How the transcript downloader evolved to apply this logic:
  personal tool → research engine → PDF business → buyer list builder
- For IT directors: How to frame AI tool ROI in terms that survive
  a budget review — time saved, decisions improved, products enabled
- The one metric: First proof of value before building Phase 2

**Closing question:** "What's your team's framework for proving AI tool
ROI before scaling investment?"

---

### ARTICLE D — Track 2
**Headline options:**
- "What 200 YouTube Transcripts Taught Me About Finding a Market"
- "AI-Powered Market Research: How I Replaced Hours of Manual Research
  with an Automated Pipeline"

**Type:** Strategic — the research engine as a business intelligence tool
**Word count:** 900-1,100
**Publish:** After pain point extractor is built

**Outline:**
- The research problem every IT professional faces when pivoting:
  how do you know what the market actually needs?
- The manual approach: Forums, Reddit, YouTube comments — hours per week
- The automated approach: transcript downloader + comment fetcher +
  pain point extractor = ranked market intelligence in minutes
- What the data actually showed: Top questions, top pain points,
  content gaps where no good answer exists (those are product opportunities)
- The enterprise application: The same architecture applied to support
  tickets, internal surveys, customer feedback, stakeholder interviews
- The business intelligence angle: This is not just a YouTube tool —
  it's an unstructured data analysis framework
- For directors: What this capability looks like as an internal tool
  for your team

**Closing question:** "What unstructured data sources in your organization
are sitting unanalyzed because there's no efficient way to process them?"

---

## Publishing Calendar Template

| Week | Article | Track | Status |
|---|---|---|---|
| Week 1 | Article 1 — Cornerstone (Origin Story) | 1 | READY TO WRITE |
| Week 2 | Article A — Consuming vs. Building | 2 | READY TO WRITE |
| Week 3 | Article 2 — Claude Code Prerequisites | 1 | READY TO WRITE |
| Week 4 | Article B — Hidden Cost of Undocumented Tools | 2 | READY TO WRITE |
| Week 5 | Article 3 — Transcript Downloader Origin | 1 | READY TO WRITE |
| Week 6 | Article C — $5 Product Strategy & AI ROI | 2 | READY TO WRITE |
| Week 7 | Article 4 — Orchestration in Plain English | 1 | WRITE AFTER STAGE 1 ✓ |
| Week 8 | Article 5 — Personal Tool to Business | 1 | WRITE AFTER STAGE 2 |
| Week 9 | Article 6 — Production Checklist | 1 | WRITE AFTER STAGE 2 |
| Week 10 | Article D — Market Research Automation | 2 | WRITE AFTER STAGE 3 |
| Week 11 | Article 7 — Pain Point Extraction | 1 | WRITE AFTER STAGE 3 |

**Bank rule:** Articles 1, A, and 2 must be written and approved before
Article 1 publishes. Do not start publishing without a 3-article buffer.

---

## Article Writing Process (Per Article)

1. Open SKILLS_LOG.md — find the relevant skill entry, use the resume
   translation as your article thesis statement
2. Write the opening paragraph first — if you can't state the problem
   and payoff in 2 sentences, the article isn't focused enough yet
3. Draft the body — one specific moment of failure, one concrete fix,
   one business insight
4. Write the headline last — after you know what the article actually says
5. Check: Does a 10-second skim of subheadings tell the story?
6. Check: Is the first 23 characters of the headline the key topic?
   (LinkedIn mobile — same rule as YouTube)
7. Schedule via LinkedIn for Tuesday or Wednesday 10 AM Central
8. Stay available for first 60 minutes to respond to comments

---

## What NOT to Write

- Chronological narration without a point ("First I did X, then Y...")
- Generic AI enthusiasm ("AI is changing everything!")
- Tutorial-style step-by-step without a business frame
- Anything that requires the reader to already understand Claude Code
- Humble bragging disguised as vulnerability
- Articles longer than 1,200 words (except the cornerstone)

---

## Headline Bank (Unused — Reserve for Future Articles)

- "The Security Rules Nobody Puts in Their AI Agent Documentation"
- "Why I Added a Backup Strategy to a YouTube Downloader (And You Should Too)"
- "What the CCA-F Certification Actually Tests (vs. What the Course Teaches)"
- "How I Turned a Personal AI Tool into a Revenue Pipeline in 8 Stages"
- "The Orchestration Pattern Every Enterprise AI Team Should Know"
- "Why Comments Beat Transcripts for Market Research (And How to Automate Both)"
- "What Happens When Your AI Agent Has No Stop Condition"
- "The 5-Tool Rule: Why Giving Your AI Agent Too Many Tools Makes It Dumber"

---

*Version 1.0 — April 2026*
*Update this document after each article publishes — note what performed,
what comments surfaced, what follow-up articles those comments suggest.*
