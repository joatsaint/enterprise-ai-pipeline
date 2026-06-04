# All LinkedIn Articles — Randy Skiles
## IT→AI Transition Playbook
## Compiled: June 3, 2026
## Total articles: 13

---

## ARTICLE INDEX

| # | Title | Source | Status | Scheduled |
|---|---|---|---|---|
| 1 | Your AI Demo Is Lying To You | Drive | Published May 6, 2026 | — |
| 2 | The Vendor You Can't Fire | Project / ART2 | Published May 21, 2026 | — |
| 3 | I Ran Enterprise IT From a Motel That Banned Prostitution | Project / ART3 | Published June 2, 2026 | — |
| 4 | Two Rollback Plans Before You Touch Production | Drive | Not posted | TBD |
| 5 | What a ServiceNow Install Taught Me About Enterprise AI Security | Drive | Not posted | July 9, 2026 |
| 6 | How to Talk to Stakeholders Who Don't Understand What You're Building | Drive | Not posted | June 16 or June 23 |
| 7 | I Earned 25 Certifications While Implementing Enterprise Software Full Time | Drive | Not posted | July 23, 2026 |
| 8 | Scope Creep Killed Our ServiceNow Timeline | Drive | Not posted | July 16, 2026 |
| 9 | Why Enterprise AI Deployments Need a Scrum Master and a Translator | Drive | Not posted | Unscheduled |
| 10 | The Greenfield Implementation Nobody Was Ready For | Drive | Not posted | June 23, 2026 |
| 11 | How I Taught a Room Full of People a Platform I Was Still Learning | Drive | Not posted | Unscheduled |
| 12 | The $0 Ransomware Decision That Almost Cost Everything | Drive | Not posted | Unscheduled |
| 13 | Don't Panic: A Sysadmin's Guide to Surviving the AI Wave | Project / ART4 | Scheduled June 9, 2026 | June 9, 2026 |
| 14 | A Sysadmin With 25 Years Answers the 10 Questions Every Sysadmin Is Asking About AI | Project / ART5 | Drafted | June 16, 2026 |

> **Note on ART2:** No standalone article body exists in the ART2 project file — it was built in the older format. The text feed post (which contains the full narrative) is used here. The full article was published manually on LinkedIn on May 21, 2026.

---
---

# ARTICLE 1 — Your AI Demo Is Lying To You
**Source:** Drive (linkedin_article_work_primitive.md)
**Status:** Published May 6, 2026

---

Every "AI agent clicks a button" demo on your feed right now is selling you the bridge — not the destination.

Here's the most unbelievable disconnect in the AI market today:

Founders are raising $50M rounds on screen recordings of agents booking flights and moving calendar invites. Boards are greenlighting "AI transformations" based on Twitter videos. Procurement teams are signing seven-figure contracts for tools that, technically, can click a button.

And almost none of them understand what that button actually means.

This is the great melt-up of agentic AI. And the bill is coming due faster than anyone wants to admit.

---

## The Three Layers Nobody In The Pitch Deck Is Talking About

When an AI agent moves a calendar invite, three things are happening underneath:

- **Access** — Can the agent reach the system? (Computer use, browsers, MCP)
- **Meaning** — Does the agent understand what the action represents?
- **Authority** — Is the agent allowed to do this, and who reviews it?

Every flashy demo you've seen optimizes for layer one.

The platform power lives in layers two and three.

Moving a calendar invite isn't "click save." It might:

- Notify five people
- Break a commitment to a customer
- Conflict with something more important
- Turn a private conversation into a political problem

The human sees the meeting and brings the context. The agent sees fields in a database and fills them out.

That gap is where production breaks. Quietly. Confidently. Expensively.

---

## Why "Trusted Write Access" Is The Wrong Frame

Trust isn't a switch. An agent might be:

- Trusted to **read** but not write
- Trusted to **draft** but not send
- Trusted to **stage** but not deploy
- Trusted to **recommend** but not approve
- Trusted in **sandbox** but nowhere near production

Real production systems have already been deleted because an agent couldn't tell the difference between staging and prod. That's not an AI failure. That's a semantic failure. The agent had access. It didn't have meaning.

---

## Why Coding Agents Worked First

Everyone says coding agents arrived first because LLMs are good at text. That's lazy analysis.

Coding agents arrived first because software development already has unusually rich work semantics: modules and dependencies, tests that fail loudly, type systems and linters, git history, package managers, build pipelines. The codebase itself gives the agent feedback.

Now compare that to your average knowledge work: a strategy doc has no tests. A calendar event hides political weight. A sales process depends on unwritten account history. A procurement decision depends on budget signals nobody documented.

The agent can act. But the environment doesn't tell it whether it succeeded. This is the verification gap. And it's where most "AI transformation" projects go to die.

---

## The Hidden Asset In Your IT Career

Here's what nobody is telling the people who spent decades in IT operations: you are sitting on the most undervalued asset in the AI labor market right now.

The work that built your career — the late-night triage, the post-incident reviews, the change management approvals, the "why did production go down at 3 AM" forensics — that wasn't grunt work. That was semantic verification.

You were the human layer that understood: what the action meant, whether it was reversible, who needed to approve it, what "correct" looked like, when the system was lying with confidence.

Map your background to where the actual demand is going:

- **Change management experience** → Agent permission architecture
- **Incident post-mortems** → Verification frameworks for autonomous systems
- **Production vs. staging discipline** → Authority-layer design
- **Documentation rigor** → Semantic interface specification
- **Vendor risk assessment** → MCP/connector governance

Every one of those is an AI Automation Architect role. Most of them don't have titles yet. The ones that do are paying real money.

---

## The Question I'd Ask Every AI Product From Here On Out

Forget "can the agent act?" Ask whether the product knows what that action means.

That is the entire game for the next 24 months. Access is commoditizing. Meaning is where the moat lives.

If you spent 20+ years learning what production systems actually mean — what breaks, what's reversible, what's load-bearing, what's political — you are not behind on AI.

You are early to the part of AI that hasn't been built yet.

---

*Free guide pulling from 50+ strategic video breakdowns on the IT → AI Automation Architect transition is in the comments.*

---
---

# ARTICLE 2 — The Vendor You Can't Fire
**Source:** Project / ART2 (text feed post — no standalone article body in file)
**Status:** Published May 21, 2026

---

"We're pretty sure it will work."

Those six words once nearly took down a university's critical infrastructure.

I was preparing a major Windows Server upgrade at Lamar University. Thousands of concurrent users. Mission-critical systems. No margin for extended downtime.

So I asked our software vendor the most important question in enterprise IT: "Have you tested your software on Windows Server 2019?"

Their answer: "We haven't formally tested it yet, but we're pretty sure it will work."

Pretty sure.

I've spent 25 years in enterprise IT. Those two words are a red flag, a warning siren, and a career-ending event waiting to happen — all at the same time.

Here's what I've learned about vendor confidence vs. vendor commitment:

A vendor knows their software better than anyone on your team ever will. But they don't know YOUR environment. Your network topology. Your security constraints. Your specific configurations.

When a vendor says "pretty sure" — what they actually mean is "we tested it in our lab, in a generic environment, with standard configurations." That's not your environment.

So I stopped asking "do you think it will work?" and started asking "what's your commitment if it doesn't?"

I couldn't force them to have tested the software. But I could negotiate a contractual SLA — a one-hour response time, a technician on the line, a documented escalation path. The vendor commitment mattered more than the vendor confidence.

Now I watch AI teams make the exact same mistake. They accept "it's been proven and tested" from AI vendors without asking the same three questions I asked every vendor for 25 years:

What versions have you actually tested in an environment like mine?
What's your compatibility guarantee?
What's your SLA if something breaks in production?

The organizations treating AI deployments like enterprise infrastructure upgrades — methodical, vendor-accountable, risk-managed — are the ones that succeed. The ones treating them like tech demos are the ones I get calls from at 2 AM.

---

*Change at work will never be as slow as it is today.*

If you're an IT professional figuring out where you fit in the AI shift, I put together a free guide based on analysis of 50 videos and 2,900 audience comments: **"The AI Skills That Won't Be Replaced"** — https://joatsaint.gumroad.com/l/wngpso

#EnterpriseIT #AIDeployment #ITLeadership

---
---

# ARTICLE 3 — I Ran Enterprise IT From a Motel That Banned Prostitution
**Source:** Project / ART3
**Status:** Published June 2, 2026
**Subtitle:** And It Taught Me Everything About What's Happening With AI Right Now

---

It was a Friday afternoon. 3:00 PM.

Hurricane Laura was 24 hours from making landfall near Lake Charles. Category 4. 150 mph winds. One of the strongest Gulf Coast storms in decades.

That's when leadership called it.

"Move everything to the cloud. Now."

Not a drill. Not a tabletop exercise. The first live cloud migration in Lamar University's history — kicked off on a Friday afternoon, with a Category 4 hurricane bearing down on Southeast Texas, while half the state was already on the highway trying to get out.

I've spent 25 years in enterprise IT. I've watched MCI WorldCom go bankrupt. Watched Lucent go the same way. Survived more "this will be seamless" promises than I can count. And in all that time, I've learned one thing about leadership decisions like this one:

Pure disbelief is not panic. It's experience.

---

## The Scramble

Roughly 50 people across multiple departments scrambled simultaneously. Networking equipment. Databases. Every piece of software students and staff depended on. All of it had to move — now — while Friday evening evacuation traffic turned every highway into a parking lot.

Some of my teammates were reached by phone while they were in that traffic. They had to pull over and find a free wifi hotspot to work remotely. Because Lamar University — the same institution that had, days earlier, praised its IT staff as consummate professionals, the same staff with multiple Master's degrees on the team — couldn't justify the cost of a portable hotspot for a hurricane emergency.

They also made us pay for our own soap in the restrooms that year.

I mention this not to be petty. I mention it because the penny-pinching is part of the pattern. The same leadership that won't spend $30 on a hotspot is the same leadership that decides, on a Friday afternoon with a hurricane coming, to do the first live cloud migration in university history. Same instinct. Different scale.

I grabbed my laptop, headset, and power cords from the office. Went home. Added an external monitor, keyboard, and mouse. Then started looking for a hotel room. Northwest Houston. Highway 290 side. It was the last available room at the cheapest place that had anything open.

---

## The Motel

The first sign something was off was the hand-lettered notice near the registration desk.

It read — and I am not embellishing — approximately:

*"Prostitution is illegal on this property."*
*"Drugs are not allowed to be sold on this property."*

The room itself was fine. The sign was the warning label for the neighborhood.

About seven doors down, a room with the door wide open all weekend. Two women playing music, dancing in and out. A man standing outside against the railing. My assessment, formed quietly and kept to myself: entrepreneurially priced short-term companionship.

Between the buildings, a man in a casual pullover — looked like any regular guy — pacing back and forth by the back fence. Phone to his ear. Still there an hour later when I left for groceries. Still there when I came back.

The motel sign wasn't a warning. It was a menu.

I kept to myself. I set up my external monitor. I opened my laptop. And I waited to do my part.

---

## The Job

My role that weekend was specific: test all systems once network operations finished moving everything to the cloud. Verify connections. Document status. Be ready.

So I sat there. External monitor glowing. Storm moving in outside the window. The sounds of the neighborhood doing its weekend business somewhere down the walkway.

I was coiled like a spring. Time was short. The storm was coming. And I was a professional — my IT Director had said so himself, just days before — ready to hold up my end the moment they needed me.

I didn't sleep much. Not because I was worried about the work. I was worried about what was outside the door. But every time I considered stepping away from the screen, I thought: what if they need me right now? What if a system goes down and I'm the one who's supposed to catch it?

I stayed. I tested. I documented. Professionally. In a motel that had a posted policy against selling drugs.

---

## The Part Nobody Told Me About

The storm came through. Rain. Some campus damage. Nothing catastrophic.

By Monday, we were migrating everything back from the cloud to the local campus servers. I was at my station, ready.

And then the systems started breaking. Not from the storm. Not from the cloud migration itself. From something nobody had told me about.

During the return migration, the network director had decided — apparently with the CTO's sign-off, and apparently without telling anyone else — to make significant changes to Lamar University's network backbone. In the middle of a recovery operation. After the university's first live cloud migration in history.

Nobody announced it. Nobody planned around it. Nobody thought to mention it to the people who were depending on network stability to do their jobs.

The result: broken connections everywhere. Servers that couldn't talk to each other. Systems down across the board. A 12-hour delay before everything was functional again.

I sat there, watching error messages cascade across my screen, trying to diagnose failures that had nothing to do with anything I'd done. The whole picture didn't emerge until a few days later, when the story finally came out.

My reaction when it did? Resignation. The specific, quiet kind you develop after 25 years of watching this happen. The kind that doesn't get angry anymore because anger requires surprise. And I was not surprised.

I had held up my end. I had stayed in that motel room all weekend, ready to move the moment they needed me. I had tested every system. Documented everything. Stayed professional under conditions that were, to put it gently, atmospherically unusual.

And someone with a title had quietly broken everything while I was doing that.

The professional betrayal isn't the loudest feeling in a moment like that. It's the quietest. The one you carry home.

---

## Here's What This Means For You

I lived through the dot-com bubble in the early 2000s. The fear then: brick-and-mortar stores would disappear. What actually happened: the internet became another sales channel. The humans with judgment, empathy, and years of accumulated knowledge didn't disappear — they became the people who knew how to use the new tools.

I'm watching the same thing happen right now with AI.

Companies are doing exactly what Lamar's leadership did on that Friday afternoon. Scrambling. Moving fast. Cutting people before they understand what those people actually do. They call it "efficiency."

Here's what it actually looks like: Where's Bob? You know Bob — the guy who just got laid off with a tweet. He'd been here 20 years. He knew every undocumented system configuration, every legacy workaround, every quirk of the infrastructure that nobody ever wrote down because Bob was always just there.

The printers just went offline. Does anyone know the print server's IP?

Nobody does. Bob knew. Bob's gone.

That's not efficiency. That's a Friday afternoon cloud migration with a hurricane coming.

---

## What to Do Right Now

Nobody predicted the trucking industry when the first automobile appeared. Nobody predicted FedEx. Nobody predicted Amazon Prime. That's where we are with AI. Not the end of IT professionals. A new road.

But the people who thrived in the dot-com transition were the ones who started learning the tools early. Not the ones who waited until the panic set in.

You don't have to predict where this goes. You just have to be the person who knows how the systems work when they break. That instinct — the one that keeps you at the screen, coiled and ready, while the world outside does whatever it does — is the one AI cannot automate.

Start building it now.

---

*Change at work will never be as slow as it is today.*

Free guide: https://lnkd.in/gny5Q2Jp — No email required.

#EnterpriseIT #AIDeployment #ITCareers

---
---

# ARTICLE 4 — Two Rollback Plans Before You Touch Production
**Source:** Drive (not posted - Article 3)
**Status:** Not posted — scheduled TBD
**Series:** Lamar University Series | Risk Mitigation Through Redundancy & Pre-Flight Verification

---

In 25 years of enterprise IT, I had one rule that never changed regardless of the system, the vendor, or the timeline:

Before you touch production, you need two ways out.

Not one. Two. Because the first rollback plan is the one you're confident about. The second rollback plan is the one you'll actually need.

This wasn't pessimism. It was discipline. And it's the single most important habit I'm watching AI deployment teams skip right now.

---

## Why One Rollback Plan Is Never Enough

Most teams doing a major upgrade think about rollback the same way most people think about a spare tire. You have one, you know it's there, and you assume you'll never need it.

But in enterprise IT, you learn fast that assumptions are liabilities.

I managed software upgrades at Lamar University for years. Every single upgrade had a rollback conversation before a single line of code was touched in production. And that conversation always started with the same question: if this goes wrong, how do we get back to exactly where we were — and how fast?

The answer was never "we'll figure it out if it happens." The answer was always a documented, tested, agreed-upon procedure that every person on the team understood before the upgrade window opened.

---

## The Two-Plan System

**Rollback Plan One: Parallel Virtual Servers**

Whenever resources allowed, we didn't upgrade the existing servers. We spun up brand new virtual servers alongside the old ones. The old servers went offline but stayed intact — untouched, exactly as they were. The new servers got the fresh operating system install and the upgraded software.

If the upgrade worked, the new servers went live and the old ones were eventually decommissioned. If the upgrade failed, we powered the old servers back on. Recovery time: minutes. Data loss: zero. User impact: minimal.

This was the preferred approach because it gave us a complete, intact copy of the original environment. We weren't restoring from a backup. We weren't hoping a snapshot captured everything correctly. We were literally just turning the old system back on.

**Rollback Plan Two: VM Snapshots**

Sometimes we didn't have the resources to run parallel servers. Storage constraints, licensing limits, infrastructure capacity — sometimes you just can't spin up a duplicate environment.

In those cases, we took a snapshot of the virtual machine immediately before the upgrade began. The network team would notify me the moment the snapshot was confirmed, and only then would the upgrade proceed. That snapshot was our insurance policy — a point-in-time copy of the entire server state that we could restore in a matter of minutes if the upgrade went sideways.

The snapshot wasn't as clean as parallel servers. Restoration took longer. But it was still a documented, tested, agreed-upon path back to safety — and that made all the difference.

---

## The Mindset Underneath the Method

Here's what both rollback plans have in common: they were decided, documented, and communicated to every stakeholder before the upgrade window opened.

The department head whose software was being upgraded knew which rollback plan we were using and why. The vendor knew. The network team knew. Everyone understood that if we hit a problem we couldn't resolve within a defined window, we were rolling back — no debate, no extended troubleshooting in production, no "let's just try one more thing."

That clarity is what prevents the worst kind of enterprise IT disaster: the extended production outage caused by a team that didn't have a rollback plan and kept trying to fix a broken upgrade instead of reverting to a known good state.

---

## The Translation to AI Deployments

If you are deploying AI systems in an enterprise environment right now, you need to have this conversation before you push anything to production.

What is your rollback plan if the model behaves unexpectedly at scale? What is your rollback plan if the API integration breaks a downstream process? What is your rollback plan if the automation workflow produces incorrect outputs during a critical business period?

And here is the harder question: is your rollback plan actually documented and tested, or is it just an assumption that you could figure it out if you needed to?

AI systems are enterprise infrastructure now. They connect to your data, your workflows, your customer-facing processes. When they fail — and eventually they will fail — the organizations that recover in minutes are the ones that built two rollback plans before they ever touched production.

The organizations that recover in days are the ones that assumed it would work.

I know which one I'd rather be.

---

*I spent 25 years making sure enterprise systems could always be put back exactly the way they were. I'm now applying that discipline to AI deployment strategy. Free guide: https://joatsaint.gumroad.com/l/wngpso*

---
---

# ARTICLE 5 — What a ServiceNow Install Taught Me About Enterprise AI Security
**Source:** Drive (not posted - ServiceNow Article 2)
**Status:** Not posted — scheduled July 9, 2026
**Series:** ServiceNow Series | Security Architecture & Segmentation

---

Before we could install a single ServiceNow module at American National Insurance, we had to solve a problem that had nothing to do with ServiceNow.

We had to figure out how to let a cloud-based platform shake hands with an on-premises Active Directory infrastructure — without giving that cloud platform any access it wasn't supposed to have.

That problem took weeks to solve. And everything we learned solving it applies directly to the AI security conversations happening in enterprise boardrooms right now.

---

## The Cloud Handshake Problem

ServiceNow lives in the cloud. Active Directory lives on-premises. ServiceNow needs to authenticate users — meaning when someone logs in, it needs to verify who they are against the organization's directory of employees.

The obvious solution is to connect ServiceNow directly to Active Directory. Point one system at the other, build a connector, done.

The problem is that Active Directory doesn't just contain usernames and passwords. It contains the entire organizational directory — every employee, every system, every permission, every security group across the whole company. It is the master key to everything.

Giving a cloud-based system direct access to that infrastructure is not a connection. It's an exposure. And American National's security team — correctly — was not going to allow it.

---

## The Isolated Architecture Solution

What the security team built instead was a completely separate Active Directory structure exclusively for ServiceNow. Think of it as a walled garden inside the larger Active Directory forest. ServiceNow could see inside the garden. It could not see anything outside it.

Inside that walled garden, we built a folder structure that mirrored the organization's departmental layout. Each department got its own folder. Each folder contained only the users from that department who needed ServiceNow access. Each folder mapped directly to a corresponding group inside ServiceNow.

Those ServiceNow groups were permission-scoped to their specific module only. The device inventory team could access the asset management module. HR could access the HR module. The network security team could access the security operations module. Nobody could see outside their lane.

---

## The Double Lock

On top of the isolated AD structure, there was a second layer of access control: your PC also had to be on an IP allowlist — a specific list of approved machine addresses permitted to even contact the ServiceNow environment.

If you had valid credentials but your machine wasn't on the allowlist, the connection was refused before authentication even started. Two separate gatekeeping mechanisms, working in sequence, before a single user could touch the system.

That double lock wasn't bureaucracy. It was defense in depth — the principle that no single security control should be the only thing standing between an attacker and your data.

---

## The Production Wall

There was a third security discipline that shaped the entire implementation: strict segregation of duties between environments.

My role as team lead gave me full access to test and development environments. I could install updates, configure modules, test integrations, and break things safely all day long.

Production was a different story. I was never allowed to touch the production environment directly. When an update needed to move from test to production, I would prepare everything in test, verify it was stable, document exactly what needed to happen, and hand it off to a dedicated security team whose specific job was managing production deployments.

I told them what to do. They did it. I could not do it myself.

That separation exists for a reason: the person who builds and tests a change should not be the same person who deploys it to production.

---

## Why This Matters for Enterprise AI

Every security principle I just described applies directly to AI systems deployed in enterprise environments. And most AI teams are not thinking about any of them.

The isolated architecture question: when your AI system needs to access your organization's data, what exactly can it see? Is it connected to everything, or is it scoped to only the data it actually needs?

The double lock question: what are the gatekeeping layers between an external AI system and your internal data? Credentials alone are not enough.

The segregation of duties question: who is allowed to push changes to your production AI system? Is it the same person who built and tested the change? If yes, you have a control gap.

These are not theoretical concerns. They are the same questions that kept a major insurance company's security team busy for weeks before a single ServiceNow module was installed.

AI is not exempt from enterprise security discipline. It never was.

---

*I spent 25 years learning how enterprise security teams think about system integration, access control, and production governance. Free guide: https://joatsaint.gumroad.com/l/wngpso*

---
---

# ARTICLE 6 — How to Talk to Stakeholders Who Don't Understand What You're Building
**Source:** Drive (not posted - ServiceNow Article 3)
**Status:** Not posted — scheduled June 16 or June 23, 2026
**Series:** ServiceNow Series | Stakeholder Communication & Emotional Intelligence

---

When I joined American National Insurance as the ServiceNow team lead, I walked into a room full of people who had never seen ServiceNow before.

Not my teammates. Not the department heads. Not the directors who had approved the purchase. Nobody in the entire organization had firsthand experience with the platform they had just committed millions of dollars to implement.

Except me.

That's a specific kind of pressure that most IT professionals don't talk about. Not the technical pressure of standing up a complex enterprise platform. The human pressure of being the only person in the building who understands what's actually happening — and having to keep everyone else informed, confident, and calm while it happens.

Here's what I learned.

---

## The Translation Problem

The first thing I figured out is that stakeholder communication in a complex implementation is not about sharing information. It's about translation.

The vendor spoke ServiceNow. They talked about CMDB population, MID server configuration, Active Directory connector setup, scoped applications, and update set deployment. That language was precise, accurate, and completely useless to the department heads who needed to understand what was going on.

The department heads spoke business. They wanted to know when their team could start using the system, why it was taking longer than expected, what was going to happen to their existing data, and what they needed to do to help the project move forward.

My job was to stand in the middle of those two languages and translate in both directions. That translation work never stopped for the entire twelve months I was there.

---

## What Stakeholders Actually Need to Hear

Here's the mistake most technical people make when communicating with non-technical stakeholders: they either say too much or too little.

What stakeholders actually need is three things:

First, what just happened — in plain language, one or two sentences, no jargon.

Second, what it means for them — how does this affect their team, their timeline, their ability to do their job.

Third, what happens next — what are we doing about it, when will they hear from us again.

That structure works whether you're delivering good news, bad news, or a delay.

---

## The Emotional Intelligence Layer

Knowing what to say is only half of stakeholder communication. Knowing how to say it — and when — is the other half.

At American National, the implementation moved slowly. Weeks of coordination work. Timelines that slipped and then slipped again. Stakeholders who had been promised a working system by a certain date were watching that date move.

When a stakeholder came to me upset, the worst thing I could do was respond with a technical explanation of why the delay happened. They didn't want the explanation first. They wanted to know that I understood why it mattered to them.

So I led with acknowledgment before explanation. I made sure they knew I understood the impact before I walked them through the cause. And I always left the conversation with a specific next step and a specific time when they would hear from me again — because uncertainty is what turns frustration into distrust.

---

## Communicating Upward Without Getting Blindsided

I learned this lesson early in my career and it held true at American National: executives do not want to be blindsided by bad news. They want to be in the loop.

So when something went wrong — a delay, a technical blocker, a scope conflict — my first move was always to get the right people informed before they heard about it from someone else. A brief, factual summary: what happened, what we're doing about it, what the timeline impact is, what we need from leadership if anything.

That proactive communication built more credibility than any technical achievement.

---

## The Translation to AI Deployments

If you are leading an AI implementation in an enterprise environment, you are in the exact same translation role I was in at American National. Except harder.

Because at least with ServiceNow, stakeholders had a rough mental model of what enterprise software was. With AI, you are often explaining systems that feel unpredictable, abstract, and vaguely threatening to people who have been reading headlines about AI going wrong for the past three years.

The same principles apply. Translate between technical and business language. Give stakeholders what happened, what it means for them, and what happens next. Lead with acknowledgment when they're frustrated. Keep leadership in the loop before they have to ask.

And never let the information vacuum fill itself. When stakeholders stop hearing from you, they don't assume everything is fine. They assume the worst.

---

*I spent 25 years translating between technical teams and business stakeholders in enterprise environments. Free guide: https://joatsaint.gumroad.com/l/wngpso*

---
---

# ARTICLE 7 — I Earned 25 Certifications While Implementing Enterprise Software Full Time. Here's Why.
**Source:** Drive (not posted - ServiceNow Article 4)
**Status:** Not posted — scheduled July 23, 2026
**Series:** ServiceNow Series | Accelerated Self-Directed Learning

---

When I started as the ServiceNow team lead at American National Insurance, I had one problem that nobody had a solution for.

I was the only person in the organization who was supposed to understand ServiceNow. But I didn't fully understand it yet either.

The certified vendor partner was doing the implementation. I was learning alongside them — absorbing how the platform worked, asking questions, watching configurations get built, understanding the reasoning behind every architectural decision. At the same time, I was responsible for translating all of that to my teammates and stakeholders who had zero ServiceNow experience.

I was learning and teaching simultaneously. And if I fell behind on the learning, the teaching collapsed with it.

So I made a decision early: I was not going to wait for the implementation to teach me ServiceNow. I was going to get ahead of it.

---

## The Certification Strategy

The first thing I did was enroll in the ServiceNow Certified System Administrator course — the CSA — the foundational certification for anyone working on the platform.

I didn't wait until the implementation was stable. I didn't wait until I had more bandwidth. I started it during the implementation, studying in parallel with the actual work happening around me.

That parallel track turned out to be the most valuable thing I could have done. Every concept I studied in the CSA course showed up in the implementation within days or weeks. I wasn't just reading about CMDB architecture in the abstract — I was watching our vendor configure it in our actual environment. The theory and the practice reinforced each other in real time.

I passed the CSA while the implementation was active. But I didn't stop there.

---

## Getting Ahead of the Curve

Here's the discipline I developed after earning the CSA: whenever the vendor announced they were about to start working on a new module, I would immediately find the corresponding ServiceNow learning path for that module and start it.

If we were about to install the IT Asset Management module, I was already taking the ITAM courses before the vendor touched it. I set up a personal ServiceNow developer instance — a free sandbox environment — and practiced every concept I was learning in a safe space where I could break things without consequences.

By the time the vendor started working on each module, I had already built a basic version of it in my developer instance. I understood the configuration options. I knew the common pitfalls. I had already made the obvious mistakes in a place where they didn't matter.

That preparation changed the quality of every conversation I had with the vendor. Instead of watching and taking notes, I was asking specific questions. Instead of nodding along, I was catching configuration choices that didn't match our organizational requirements.

---

## The Number That Surprises People

In twelve months at American National, working a full-time implementation role, I earned the CSA plus approximately 25 additional badges, micro-certifications, and module certifications on the ServiceNow learning platform.

When I tell people that number, the reaction is usually the same: how?

The answer is that I stopped treating certification as something that happened after the work slowed down. I treated it as part of the work. Every module the vendor was about to implement was a learning opportunity. Every gap in my knowledge was a course waiting to be taken. Every evening and weekend was time that could either go toward passive consumption or active skill building.

I chose skill building. Consistently. For twelve months straight.

---

## The Same Discipline Applied to AI

The approach I used at American National — get ahead of the curve, learn in parallel with the work, practice in a safe environment before touching production, earn credentials in the modules you're about to need — is exactly the approach I'm applying to AI right now.

The AI field moves faster than any enterprise software platform I've worked with. New models, new frameworks, new deployment patterns, new security considerations — the landscape shifts every few months. Waiting until you need a skill to start learning it means you are always behind.

The professionals who will succeed in AI roles are the ones who treat learning as a continuous parallel track, not something that happens when the workload eases up. The workload never eases up. You have to build the habit of learning alongside the work, not instead of it.

---

*I spent 25 years building the habit of learning faster than the job required. Free guide: https://joatsaint.gumroad.com/l/wngpso*

---
---

# ARTICLE 8 — Scope Creep Killed Our ServiceNow Timeline. Here's What I'd Do Differently.
**Source:** Drive (not posted - ServiceNow Article 5)
**Status:** Not posted — scheduled July 16, 2026
**Series:** ServiceNow Series | Scope Management Under Political Pressure

---

Six months into our ServiceNow implementation at American National Insurance, we were behind schedule.

Not because the technology failed. Not because the vendor underperformed. Not because the team wasn't working hard enough.

We were behind because powerful people wanted things that weren't in the plan. And when we said wait, they went around us.

---

## How It Started

The implementation plan was straightforward in concept. The certified ServiceNow partner would complete the baseline installation across all three environments — test, development, and production — before any customization work began. Baseline first. Customizations after.

That sequencing wasn't arbitrary. The baseline installation was the foundation everything else would be built on. If you start customizing before the foundation is stable, you build on sand.

Then the modules started going in. And the stakeholders started paying attention.

---

## The Moment Scope Creep Begins

Here's the thing about scope creep in enterprise implementations: it never announces itself as scope creep. It announces itself as a reasonable request.

A department head sitting in on a configuration meeting sees something that's almost what they need — and asks if it could just be adjusted slightly. A director notices that the out-of-the-box workflow doesn't match their existing process. A senior vice president hears that ServiceNow can integrate with an existing system and asks why that integration isn't already on the roadmap.

Each request sounds reasonable in isolation. Each one represents a small deviation from the baseline plan. And each one costs vendor hours — the finite, contracted hours that were budgeted for the baseline installation, not for custom development.

At American National, those requests started coming in before the baseline was anywhere close to complete. And the people making them had seniority, relationships, and direct access to decision-makers that I didn't have as the new person twelve months into the job.

---

## What Happened When We Pushed Back

The vendor pushed back first. Politely, professionally, and repeatedly. They explained that the contracted troubleshooting hours were being consumed by customization work. That the baseline timeline was slipping.

I reinforced that message in every stakeholder conversation I could. It didn't matter.

The stakeholders who wanted their customizations done had been with the company for years. They had relationships with directors and vice presidents that predated my arrival by decades. When they wanted something, they went to their friends in leadership and asked for it directly. And leadership — not wanting to disappoint long-tenured colleagues — approved it.

My director, caught between the implementation team's recommendation and pressure from above, caved. Every time.

I documented everything in a personal journal I kept outside the Agile tracking system — because the Agile board captured tasks, but it didn't capture the political decisions that were causing those tasks to multiply.

---

## What I'd Do Differently Today

The political dynamics that drove scope creep at American National were not solvable by better communication or clearer documentation alone. When a senior vice president tells a director to give a department head what they want, the implementation team's recommendation doesn't carry enough weight to override that decision without executive sponsorship at the highest level.

What I would do differently is establish that executive sponsorship before the first module goes in. Not assumed sponsorship. Explicit, documented, named sponsorship — a C-suite owner who has agreed in writing that baseline completion is a prerequisite for any customization approval, and who will enforce that boundary when it gets tested.

Because it will get tested. It always gets tested.

I would also use AI-powered project tracking tools to make the cost of scope creep visible in real time. A live dashboard showing the timeline impact of every approved customization request is much harder to dismiss than a verbal warning in a status meeting.

---

## The Translation to AI Deployments

Enterprise AI projects face identical scope creep dynamics. Business users see an AI system being built and immediately start imagining what it could do for their specific team. The requests are reasonable. The timing is wrong. And the people making the requests often have more organizational leverage than the implementation team.

The organizations that get enterprise AI right are the ones that treat the implementation plan as a commitment — not a suggestion that evaporates the moment a senior stakeholder has a better idea.

---

*I spent 25 years navigating the political realities of enterprise implementations. Free guide: https://joatsaint.gumroad.com/l/wngpso*

---
---

# ARTICLE 9 — Why Enterprise AI Deployments Need a Scrum Master and a Translator
**Source:** Drive (not posted - ServiceNow Article 6)
**Status:** Not posted — unscheduled
**Series:** ServiceNow Series | Agile Project Management in Practice

---

When American National Insurance stood up their ServiceNow implementation, they did something right that most organizations skip entirely.

They hired a scrum master.

Not a project manager who had read about Agile. Not a team lead who was also responsible for tracking tasks on the side. A dedicated scrum master whose entire job was managing the implementation backlog, coordinating sprint cycles, assigning tasks across teams, and keeping the project moving forward.

That decision was sound. And it still wasn't enough.

Because what the scrum master couldn't do — what no Agile framework can do on its own — was translate what was happening inside the sprints to the people outside them who needed to understand it.

That was my job. And it turns out those are two completely different skills.

---

## What Agile Actually Looks Like in a Large Enterprise Implementation

A large enterprise implementation involving a certified vendor partner, multiple internal teams, dozens of stakeholders across different departments, and a platform with hundreds of configuration options looks nothing like a small software development team running two-week sprints.

At American National, the Agile framework was the skeleton of the project. The scrum master maintained the backlog — every task, who it was assigned to, what sprint it was scheduled for, what its dependencies were.

The problem was that almost nobody outside the core implementation team had the context to interpret what they were seeing on the board.

---

## The Gap Between the Board and the Business

Here's what a task on the Agile board might look like: "Configure AD connector for ITSM module — blocked pending security team review of IP allowlist requirements."

To the implementation team, that task tells a complete story. To a department head waiting for the ITSM module to go live, that task is meaningless. They don't know what an AD connector is. They don't know why security team review is required. All they know is that the thing they're waiting for has a status that says "blocked."

That gap — between what the Agile board shows and what the business needs to understand — is where implementations lose stakeholder trust.

I spent twelve months bridging that gap. The scrum master kept the implementation honest. I kept the organization informed. Both roles were essential. Neither one could do the other's job.

---

## What Agile Doesn't Protect You From

Here's the failure mode I watched play out that no Agile framework can prevent on its own: scope additions that bypass the backlog entirely.

When a senior stakeholder went directly to a director and got a customization approved outside the normal request process, the vendor would sometimes begin working on it before the scrum master had a chance to assess the timeline impact.

Agile gives you visibility into what the implementation team is doing. It does not give you control over what the organization decides to ask for.

---

## The Translation to AI Deployments

Enterprise AI projects need exactly what the ServiceNow implementation at American National had — and one thing it was missing.

They need the Agile structure. They need the translator. And they need what American National was missing: executive-level governance that requires all scope additions to go through the backlog before work begins — no exceptions, no end-runs, no verbal approvals from directors who don't understand the downstream consequences.

Agile is a tool. Like every tool, it works when it's used correctly and fails when the people with the most organizational power decide the rules don't apply to them.

---

*I spent 25 years working inside enterprise Agile implementations. Free guide: https://joatsaint.gumroad.com/l/wngpso*

---
---

# ARTICLE 10 — The Greenfield Implementation Nobody Was Ready For
**Source:** Drive (not posted - ServiceNow Article 7)
**Status:** Not posted — scheduled June 23, 2026
**Series:** ServiceNow Series | Cross-Functional Coordination Under Resource Constraints

---

When American National Insurance signed the contract for ServiceNow, every department head got the same message: your team is getting a new platform that will consolidate everything — HR, IT, security, asset management, help desk — into one unified system.

What nobody told them was what that actually required from their team before a single module would be ready to use.

Participation in architecture decisions. Availability for configuration reviews. Sign-off on security requirements. Data cleanup and migration preparation. Training time. Testing time. User acceptance feedback.

And all of that on top of their existing jobs.

That gap — between what the organization expected and what the implementation actually required — is what made cross-functional coordination the hardest part of the entire project. Harder than the technology. Harder than the vendor relationship. Harder than the scope creep.

---

## The Resource Constraint Nobody Budgeted For

Most organizations budget carefully for vendor hours. That number is visible, measurable, and taken seriously.

Organizational availability is invisible. Nobody budgets for it. Nobody tracks it. And it is almost always the constraint that determines whether the project moves forward or stalls.

At American National, the implementation required participation from the Active Directory team, the network security team, the device inventory team, the HR department, the IT operations group, the vendor partner, and my own team — all coordinating simultaneously on a platform none of them had implemented before.

Every one of those teams had other projects. Other priorities. Other emergencies. When the Active Directory team needed to build the isolated folder structure for ServiceNow authentication, they were also supporting the rest of the organization's directory infrastructure.

The implementation didn't get their full attention. It got whatever was left after everything else was handled.

---

## What Coordination Actually Looked Like

My job was to keep the implementation moving forward despite those constraints. Not by demanding availability that didn't exist. But by understanding the constraint, working around it wherever possible, and making sure the right people had the right information at the right time.

That meant tracking dependencies constantly. Front-loading the decisions that required the most coordination. If a configuration choice needed sign-off from three teams, I tried to get that conversation scheduled weeks before the vendor needed the answer — because getting three busy teams in the same meeting required at least two weeks of lead time on a good day.

It meant maintaining my own documentation outside the Agile board — a running record of who was waiting on whom, what the dependency chain looked like, and what the realistic timeline was given actual resource availability rather than theoretical availability.

The Agile board showed what should happen. My documentation showed what was actually going to happen given the human constraints in play.

---

## The Translation to AI Deployments

If you are planning an enterprise AI deployment, the resource constraint you are least prepared for is not compute capacity or model costs or integration complexity.

It is organizational availability.

The data governance team that needs to approve what data your AI system can access is also managing every other data request across the organization. The security team reviewing your AI deployment architecture is also reviewing every other security initiative in the pipeline. The department leads validating AI output are also running their departments.

The coordination discipline that makes enterprise AI projects succeed: understand the human constraints, build lead time into every decision that requires cross-team participation, follow up persistently without burning relationships, and keep moving on everything that doesn't require the blocked resource while you wait.

The technology is the easy part. The humans are where the work actually is.

---

*I spent 25 years learning how to keep complex multi-team projects moving when the humans involved have everything else on their plates. Free guide: https://joatsaint.gumroad.com/l/wngpso*

---
---

# ARTICLE 11 — How I Taught a Room Full of People a Platform I Was Still Learning
**Source:** Drive (not posted - ServiceNow Article 8)
**Status:** Not posted — unscheduled
**Series:** ServiceNow Series | Formal Knowledge Transfer & Instructional Design

---

Every two weeks at American National Insurance, I stood in front of my teammates and taught them something about ServiceNow.

Not something I had mastered months ago. Not something I had practiced until it was second nature. Something I had learned recently — sometimes very recently — while the implementation was actively happening around us.

I was the only person in the organization with ServiceNow experience. My teammates had none. And the implementation wasn't going to pause while I got comfortable enough with the platform to feel ready to teach it.

So I taught it anyway. Simultaneously learning and transferring knowledge, for twelve months straight.

---

## The Curriculum Problem

The first question I had to answer was: where do you start when your students know absolutely nothing?

Starting in the middle — jumping into module configuration or workflow design — would have been useless. You can't explain how to configure an asset management module to someone who doesn't know how to navigate the platform's basic interface.

So I went back to first principles. I borrowed the sequence from the official ServiceNow Certified System Administrator curriculum — the CSA — which was designed to take someone from zero knowledge to certified competency in a structured order. Then I adapted it for people who were learning in a live implementation environment rather than a controlled training setting.

---

## What the First Training Session Looked Like

The first formal session I delivered covered one topic: how to log into ServiceNow.

That sounds almost insultingly simple. But it wasn't.

ServiceNow at American National had two login methods. Single sign-on through Active Directory. And individual application credentials used as a backup when SSO wasn't available.

Both methods needed to be understood. Both had different use cases. So the first session covered what SSO is, why it exists, how to use it, what individual credentials are, when you would use them instead, and how to navigate the login screen for each method.

By the end of that session, every person in the room could get into ServiceNow. That was the entire goal. One skill, fully understood, fully practiced, fully functional before we moved to the next topic.

---

## The Parallel Learning Problem

Here's the honest reality of teaching a platform while learning it yourself: you are always one step ahead of your students, and sometimes less than that.

When the vendor started configuring a module I hadn't studied yet, I had two options. Wait until I understood it thoroughly before trying to explain it. Or get ahead of it as fast as possible and teach it before the implementation moved past it.

Waiting was not an option. The implementation moved on its own timeline.

So I built a personal system: the moment the vendor announced the next module on the roadmap, I immediately started the corresponding ServiceNow learning path. I used my developer instance to build a working version. I made my mistakes there, in a sandbox where they didn't matter, before I had to explain the concepts to anyone else.

---

## What I Learned About How Adults Learn Enterprise Software

Twelve months of bi-weekly training sessions taught me things about adult learning that no textbook had ever made clear.

People need to do, not just watch. Watching me navigate ServiceNow gave my teammates a general sense of the interface. Sitting at their own machines and navigating it themselves locked in the knowledge.

People need context before mechanics. Explaining how to configure a workflow before explaining what a workflow is produces confusion, not competence. The why has to come before the how.

People need permission to not know things. My teammates were experienced professionals who were suddenly beginners at something new. Creating an environment where questions were expected and welcomed — where not knowing something was the normal starting point, not an embarrassment — made the difference between people who engaged and people who sat quietly and fell further behind.

---

## The Translation to AI Deployments

Every organization deploying AI right now has the same knowledge transfer problem I had at American National. Except larger.

The organizations that close that gap successfully are the ones that treat AI training like I treated ServiceNow training: start from absolute zero, sequence the curriculum so each concept builds on the last, include hands-on practice in every session, lead with context before mechanics, and create an environment where not knowing is the expected starting point.

The organizations that struggle are the ones that send a link to a help document and assume the problem is solved.

People don't learn enterprise systems from documentation. They learn them from someone who understands the system, understands the learner, and is willing to stand in front of a room every two weeks and build competence one session at a time.

---

*I spent 25 years building the skill of translating complex technical systems into knowledge that non-technical people can actually use. Free guide: https://joatsaint.gumroad.com/l/wngpso*

---
---

# ARTICLE 12 — The $0 Ransomware Decision That Almost Cost Everything
**Source:** Drive (not posted - Article 18, Icorp / Sage Automation Series)
**Status:** Not posted — unscheduled
**Series:** Icorp / Sage Automation Series | Incident Response, AI Monitoring, and the Real Cost of Doing Nothing

---

It started with desktop icons.

A woman in the Icorp main office noticed that the names on her desktop icons had changed overnight. Instead of recognizable file names, they were replaced with strings of cryptographic garbage characters — unreadable, unrecognizable, wrong.

She didn't call us the first time it happened.

She didn't call us the second time either.

By the time she called us the third time, we had already lived through two full ransomware recovery events — each one costing 20+ hours of restoration work, each one putting decades of irreplaceable engineering blueprints at risk across two separate companies.

This is the story of those three events. And what an AI monitoring system would have done differently.

---

## What the Ransomware Actually Did

This was the early era of encryption ransomware — the kind where the original designer released the source code and thousands of script kiddies started making their own variations.

Here's how it worked: once it landed on your machine, it encrypted every file on your C drive — scrambling both the file contents and the file names into unreadable cryptographic characters. Then it worked its way through every mapped network drive connected to that PC. Then it deleted itself, leaving behind thousands of folders full of garbage and a text file in every infected folder with instructions for paying the ransom in cryptocurrency.

Because it deleted itself on completion, tracing the source was nearly impossible.

---

## The Blast Radius Nobody Expected

The infected PC belonged to one person in the Icorp office. But that PC had network shares mapped to it — shared drives that connected to both Icorp and Sage Automation file systems.

Sage Automation was a separate legal entity. Different company, same family ownership, same building. Their primary business was designing and engineering robotic gantry systems — and they had decades of project files, blueprints, drawings, and specifications representing their entire intellectual property portfolio sitting on those network drives.

One infected PC. Two companies exposed. Decades of irreplaceable engineering work at risk.

That's the blast radius nobody thinks about until it's too late.

---

## What Saved Us: Nightly Tape Backups

The only reason this story doesn't end in catastrophe is a habit that predated me: nightly tape backups.

Every day, I verified the previous night's backup had completed successfully. It was on my daily checklist — not optional, not something I got to when I had time. Every morning, confirmed.

When the ransomware hit, those nightly backups were what stood between Sage Automation and total loss of their engineering archive. We restored every encrypted folder from the previous night's backup. We deleted the thousands of ransom demand text files manually. We rebuilt the affected PCs from clean images.

First event: 20+ hours of restoration work. Second event: another 20+ hours. Third event — the one where she finally called us while it was still happening — we caught the executable before it deleted itself, pulled her network cable, and stopped the encryption before it reached the network drives.

Total cost in my time alone across three events: over 100 hours. Not counting lost productivity across both companies.

---

## The Human Factor You Can't Engineer Around

The infected user was the owner's wife.

We gave management our recommendations after the first event: no personal email on company machines, restrict mapped network drive access on her PC. After the second event, we repeated those recommendations with more urgency.

The owner overrode every recommendation. She kept her Yahoo email. She kept the mapped drives.

I had learned something important by then: executives don't want to be blindsided. They want the facts — what happened, what we're doing about it, what the timeline looks like. That part went fine. The part that didn't go fine was the part where the business decision overruled the security recommendation. That happens in every enterprise. You document it, accept it, and make sure the backup discipline is airtight for when it happens again.

---

## What an AI Monitoring Agent Would Have Done

Here's where 25 years of enterprise IT experience meets the AI conversation I'm having with employers today.

The three infections, the 100+ hours of restoration work, the risk to decades of engineering intellectual property — all of it was downstream of one problem: by the time a human noticed something was wrong, the damage was already done.

An AI-powered network monitoring agent changes that equation entirely.

Here's what it would look like: a lightweight agent monitoring the file system in real time, trained on the specific behavioral signature of encryption ransomware — mass file renaming, rapid sequential file modification, cryptographic pattern changes in file names and contents. The moment it detects that pattern, two things happen simultaneously. First, it blocks file system access across the network — not after the damage is done, but while it's happening. Second, it sends an immediate alert with the affected machine identified, the scope of the spread mapped, and a recommended response action queued up.

The owner's wife unplugging her PC manually the third time because she happened to notice the icons changing — that's the human-dependent version of this response. It worked once, by luck, three infections in.

The AI version works every time, in the first seconds of the first infection, without depending on a user to notice something and remember to call IT.

The ROI case for a CFO or COO is straightforward: 100+ hours of IT recovery time, two companies' productivity disrupted across three separate events, and decades of irreplaceable intellectual property held hostage — versus the cost of an AI monitoring agent that catches the behavioral signature before the first file is encrypted.

The math isn't close.

---

*I spent over 8 years protecting enterprise systems from threats that humans couldn't catch fast enough. Free guide: https://joatsaint.gumroad.com/l/wngpso*

---
---

# ARTICLE 13 — Don't Panic: A Sysadmin's Guide to Surviving the AI Wave
**Source:** Project / ART4
**Status:** Scheduled June 9, 2026
**Subtitle:** The Hitchhiker's Guide to the Galaxy described Earth in two words: "Mostly Harmless." That's AI for your career — if you know what you're actually looking at.

---

Pull up a chair.

The server fans are running. The indicator lights are blinking green down the rack. You've got about ten minutes before the next ticket comes in.

I want to tell you something I wish someone had told me twenty years ago.

---

## The First Wave

It was sometime in the mid-2000s at Region 5 Education Service Center in Southeast Texas.

Region 5 serves 90,000 students and over 6,100 educators across multiple school districts. Jefferson County, Hardin County, Orange County. A regional education hub created by the Texas state legislature in 1967 to do the things individual school districts couldn't afford to do alone.

The IT team was small. Stretched thin in the way every public education IT team is stretched thin — too many systems, too many users, not enough people, never enough budget.

And then we got our first virtual server appliance.

I remember the feeling. Not fear. Not anxiety about being replaced. Relief. Pure, unambiguous relief.

Because before that appliance, when a physical server died — and they died, all of them eventually — you were looking at a cascade. Emergency calls. Waiting for replacement hardware to arrive. Configuring it from scratch. Getting it back on the network. Days of disruption for the school districts depending on those systems.

The VM stack changed all of that. A server crashes — the appliance spawns a new one. Automatically. We weren't scared of virtualization. We were excited about it.

---

## Meanwhile, Somewhere Else

While we were setting up that first VM stack at Region 5, there were forums full of sysadmins convinced it was over.

"VMware is going to eliminate our jobs."
"Why would anyone need a server admin when the software manages itself?"
"Physical server skills are dead."

Sound familiar? Replace "VMware" with "AI" and you have Reddit in 2026.

I was on one of those threads yesterday. A 25-year-old in Nigeria — teaching computer skills at a secondary school, trying to break into sysadmin, genuinely scared. Asking if he's wasting his time. Watching the layoff headlines. Wondering if the road he's trying to get onto is being demolished while he's still looking for the on-ramp.

Good kid. Smart questions. And completely understandable fear.

But here's what I know — because I've been standing in this room before.

---

## What Actually Happened With Virtualization

The physical server admins who panicked and walked away from IT — they left.

The ones who learned VMware, learned vSphere, learned how virtual infrastructure actually worked under the hood — they became more valuable. Not less.

Because someone still had to understand what was happening when the automated system broke. When the VM migration failed. When the storage backend corrupted.

The automation didn't replace the sysadmin. It raised the floor on what a sysadmin needed to know.

Every technology wave I've watched come through IT in 25 years has done the same thing: dot-com bubble, cloud computing, virtualization. The wave never killed IT. It changed what IT meant.

---

## Don't Panic

The Hitchhiker's Guide to the Galaxy — Douglas Adams, 1979 — contains, in its millions of pages covering every planet, civilization, and life form in the known universe, the following entry for the planet Earth:

*Mostly Harmless.*

That's AI for your career right now.

Not because AI isn't real. It is. But because the people reading doom headlines and concluding "IT is over" are making the same mistake the Guide made about Earth — they're summarizing something enormously complex in a way that sounds definitive but misses everything that actually matters.

Here's what the headlines aren't telling you: the backbone of every Large Language Model running today is Linux. Every major cloud platform — AWS, Azure, GCP — runs on Linux. AI doesn't manage its own infrastructure. It runs on infrastructure that humans have to build, maintain, secure, and fix when it breaks.

Companies are terrified of giving an AI root access to its own life support system.

AI predicts the next most likely word or line of code. It doesn't understand why. You do.

---

## Where's Bob

Companies are cutting experienced IT staff right now to fund AI deployments. Laying people off with a tweet. Calling it efficiency.

Where's Bob? The guy with 20 years in. Knew every undocumented system configuration. Every quirk of the infrastructure that nobody ever wrote down because Bob was always just there.

The printers just went offline. Does anyone know the print server's IP?

Nobody does. Bob knew. Bob's gone.

That's not efficiency. That's a hurricane evacuation with no plan.

The companies that are cutting Bob to fund AI are going to need Bob back. At higher rates. With less institutional knowledge remaining. Having already broken things that Bob would have caught before they became incidents. The reckoning comes later. It always does.

---

## What This Means For You

To the 25-year-old in Nigeria asking if he's wasting his time: No.

Here's what I'd tell you — and every IT professional watching the AI wave and wondering if it's different this time:

**Learn the tools.** Not to replace yourself. To make yourself the person who knows how the tools work when they break.

**Don't wait for the panic.** The virtualization wave rewarded the people who got certified early — before the demand spike, before everyone was scrambling to learn it at the same time. Same thing is happening right now with AI infrastructure skills.

**Protect your institutional knowledge.** Document everything Bob knows. Because Bob might be you someday.

**Keep watching the skies.** Not with fear. With the alert competence of someone who has been through waves before and knows the pattern.

---

## The New Road

Nobody predicted FedEx when the first automobile appeared. Nobody predicted Amazon Prime. The horse-to-automobile transition didn't eliminate transportation jobs — it created an entirely new road that nobody could fully see from where they were standing.

That's where we are. Not the end of IT professionals. A new road.

The server fans are still running. The green lights are still blinking down the rack. Somewhere right now a VM migration is failing silently and nobody knows why yet.

They're going to need someone who does. That someone is you — if you keep learning.

Don't panic. Mostly harmless.

---

*Change at work will never be as slow as it is today.* Free guide: https://lnkd.in/gny5Q2Jp

#EnterpriseIT #ITCareers #AIAutomation

---
---

# ARTICLE 14 — A Sysadmin With 25 Years Answers the 10 Questions Every Sysadmin Is Asking About AI
**Source:** Project / ART5
**Status:** Drafted — scheduled June 16, 2026
**Subtitle:** The questions come up every week on r/sysadmin. Here are straight answers from someone who's watched three technology waves roll through this industry and is paying close attention to this one.

---

Every week on r/sysadmin, the same questions surface. Different usernames. Same anxiety underneath.

I've been in enterprise IT for 25 years. Watched MCI WorldCom go bankrupt. Watched Lucent go the same way. Survived the dot-com bubble, the virtualization wave, the cloud migration era. I'm not watching this one from the sidelines.

Here are straight answers to the ten questions I see most often. No hype. No reassurance theater.

---

## 1. Which skills must I learn right now to remain indispensable?

I want to tell you something that has nothing to do with technology.

Early in my career I was working with a company that ran Dow Chemical accounts. There was a foreman who'd been there for years. Every morning — before the rest of the crew showed up — he'd walk the floor and fill out the safety compliance forms himself. Nobody told him to. It was technically someone else's job. He did it because he understood that the forms mattered, and he was the most reliable person to do them.

That man was untouchable. Not because of his technical skills. Because of his pattern recognition and his initiative.

The skill that will keep you indispensable in the AI era is the same one that kept him indispensable then: watching management for the pain they haven't verbalized yet, and solving the problem before it becomes a ticket.

AI is excellent at executing on defined tasks. It is not good at noticing that a director has been sighing in every Monday meeting for three months because the compliance reports are always wrong. That takes someone who's been paying attention.

Watch. Anticipate. Act. That instinct is yours to keep.

---

## 2. How do I pivot from traditional infrastructure to AI infrastructure?

A few months ago I was walking through the parking lot at my gym and I overheard a woman talking anxiously to a friend. She ran reports all day, she said. What used to take her six hours was now taking two. She was afraid her job was going to disappear.

I walked to my car thinking: if she's worried, a lot of people are worried.

The first thing you have to unlearn isn't a technical skill. It's the identity.

I spent years as the lone wolf. The guy who owns the uptime, carries the pager, bears the weight of the infrastructure alone. That instinct — that I must know everything, fix things quietly in the dark of night, protect my domain — is the wrong instinct for the AI world.

AI infrastructure is inseparable from data pipelines and software engineering code. You cannot be the sole keeper of the keys anymore. You have to share ownership with data scientists and ML engineers. You have to get comfortable saying "I don't know — let's look at the telemetry together." You have to stop fixing things silently and start running blameless post-mortems, because AI failures are frequently non-deterministic.

The identity shift: from gatekeeper to enabler.

Now here's the good news for the VMware and network people specifically. Your existing skills are not a liability. They're a foundation. Swap vCenter for Kubernetes. Learn GPU virtualization. Translate your network knowledge into HPC fabrics — RDMA, InfiniBand. Build a local lab with Minikube or K3s.

That's not starting over. That's crossing a bridge built specifically for people with your experience.

---

## 3. What routine tasks will AI fully absorb first?

The honest answer: the tasks that have always felt beneath you.

Tier 1 help desk tickets. Password resets. Log parsing for known patterns. Scheduled compliance reports. Monitoring alert noise — the stuff where you've been saying for years "a script should handle this."

It will. It does.

What remains — and what will be more valued, not less — is the judgment layer. The person who looks at what the automation produced and knows when to trust it and when to override it. That's 15 years of pattern recognition.

---

## 4. How will the definition of "Senior SysAdmin" change?

Right now, a Senior SysAdmin is the person who keeps everything running. In five years, a Senior SysAdmin will be the person who knows when to trust the automation and when to override it.

It means moving from "I fix the broken thing" to "I validate that the AI's diagnosis is correct before it acts." It means being the human in the loop who carries enough institutional knowledge to catch what the system can't see. The 20 years of undocumented system quirks in your head become more valuable, not less — because they're the things the model was never trained on.

Senior, in the AI era, means judgment. Not tenure.

---

## 5. Should I be scared right now?

No. You should be paying attention. There's a difference.

Fear makes you freeze. Attention makes you move. The people who came out ahead of the dot-com bubble and the virtualization wave weren't the ones who saw it coming and panicked. They were the ones who saw it coming and started learning before the panic spread.

The panic is already spreading. That's your signal to move, not freeze.

---

## 6. Is cloud certification enough, or do I need to understand ML?

You need to understand the infrastructure that ML runs on. You do not need to become a data scientist.

The gap most IT professionals need to close is not "how does a neural network learn" — it's "how do I provision, monitor, and maintain the systems that neural networks run on." AWS SageMaker, Azure ML, Google Vertex AI — these are not foreign territory if you already know the cloud. They're an extension of skills you already have.

---

## 7. How long do I realistically have before this becomes urgent?

Shorter than you'd like. Longer than the headlines suggest.

The infrastructure to support full AI automation of knowledge work is still being built. The data centers aren't finished. The power plants aren't finished. The chips aren't arriving fast enough. The companies making the loudest noise about AI efficiency are still quietly dependent on the humans who know where the bodies are buried.

You have runway. Use it.

---

## 8. What does an AI infrastructure team actually look like day-to-day?

A sysadmin who understands containers and GPU provisioning. A data engineer who owns the pipelines. An ML engineer who trains and deploys the models. A DevOps engineer who manages CI/CD. And usually one person — often the most experienced person in the room — who translates between all of them when things break.

Guess which seat has the most job security.

---

## 9. Will AI replace junior admins first or senior ones?

Junior admins first, because their work is more routine and more easily automated.

But here's the catch: the senior admins who only know how to do what junior admins used to do are next. The credential that protects you isn't your title. It's whether you can do the judgment work that the automation can't.

---

## 10. What's the one thing you wish you'd started earlier?

Building in public. Documenting the transition as I went through it.

The people who come out of this shift with the most credibility won't be the ones who got the certifications first. They'll be the ones who showed their work — who wrote about what they were learning, what broke, what surprised them, what the theory got wrong when it hit the real environment.

Your 25 years of context is the asset. Start putting it somewhere people can find it.

---

That's all I've got. The questions aren't going to stop coming. Neither is the technology.

You're not behind. You're early.

---

*Change at work will never be as slow as it is today.* Free guide: https://joatsaint.gumroad.com/l/wngpso

#EnterpriseIT #AIDeployment #ITCareers

---

*End of compiled articles — June 3, 2026*
*Sources: Claude Project (ART2–ART5) + Google Drive ("not posted" series)*
*Next scheduled: ART4 Don't Panic — June 9, 2026*
*Articles needing scheduling: Two Rollback Plans, Scrum Master & Translator, How I Taught a Room, $0 Ransomware*
