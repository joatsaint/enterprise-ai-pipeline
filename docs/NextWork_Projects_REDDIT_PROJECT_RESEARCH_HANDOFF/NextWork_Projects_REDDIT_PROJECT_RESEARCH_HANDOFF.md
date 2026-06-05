# Reddit Project Research Scraper — Product Expansion Handoff
**Owner:** Randy Skiles  
**Date:** June 4, 2026  
**Status:** Planning phase — awaiting field manual sales proof before implementation  
**Priority:** Phase 2+ (after field manual → sales velocity confirmed)

---

## Overview

This document describes a **new research workflow** that feeds a future product expansion: **dual-track AI automation projects** (Doer vs. Operator) adapted from NextWork's catalog and validated against real sysadmin pain points.

**Why this matters:**
- Your lead magnet targets sysadmins who fear AI displacement. They have automated tasks they don't even realize could be automated.
- r/sysadmin is a **raw complaint repository** — if you can extract the actual work pain (not just the venting), you can build projects that solve real frustrations.
- **Proof of concept:** Once the field manual starts selling, pick 1–3 top complaints from Reddit, adapt them as dual-track projects, post as LinkedIn one-offs. Measure engagement. Then decide if it becomes a product.

**Decision principle:** No infrastructure investment until you have sales velocity. This handoff documents *what* to build and *when* — but implementation doesn't start until field manual revenue validates the audience.

---

## 1. Research Workflow Overview

### Current State (ORCHESTRATOR.md §4)
You have **two research layers** already mapped:

| Layer | Purpose | Tool | Cadence | Output |
|-------|---------|------|---------|--------|
| **Deep research** | Transcript analysis (youtube-downloader) | YouTube pipeline | Quarterly | Pillar definitions |
| **Trend research** | Live community discussion (planned `trend-miner`) | Claude Code + web search (`site:` queries) | Monthly/weekly | `pain-points-YYYY-MM.md` |

### New Addition: Project-Specific Research
**What:** Mining r/sysadmin (and related communities) for **complaints about repetitive, automatable tasks** that the complainer doesn't realize could be automated.

**Why separate from trend-miner:** 
- Trend-miner feeds article topics (broad community sentiment).
- Project-miner feeds product decisions (specific task workflows).

**Tool:** Python scraper (PRAW API) or manual audit (Google `site:` search).  
**Cadence:** One-time initial audit (post field manual launch) → quarterly refresh.  
**Output:** `project-research/sysadmin-pain-points.md` (structured list of automatable complaints).

---

## 2. The Two-Track Project Idea (Proof of Concept Phase)

Once you have field manual sales, test this:

### Workflow
1. **Pick 1–3 top complaints** from `sysadmin-pain-points.md`.
2. **Match against NextWork catalog** (84 projects) or build from scratch if no match.
3. **Create two versions:**
   - **Doer track:** Step-by-step, hands-on guide (understand the architecture).
   - **Operator track:** "Supervise an AI agent to build this" (prompt-first, platform-agnostic).
4. **Post on LinkedIn** as a one-off value drop (no product pitch).
5. **Measure:** Engagement, comments, ask-fors. Let demand decide if it becomes a product.

### Example (Hypothetical)
**Reddit complaint:** "I spend 2 hours every Monday morning manually pulling patch reports from 15 different servers and consolidating them into a spreadsheet."

**Dual-track project:**
- **Doer:** "How to build a patch report aggregator in 4 hours" (Python + cron + CSV output).
- **Operator:** "How to prompt Claude Code to build a patch aggregator for you" (Claude Code + instructions on what to ask for).

**LinkedIn post:** "Sysadmins waste 100 hours a year on manual patch consolidation. Here's how to kill it in one afternoon — the hard way or the agent way."

---

## 3. Phasing & Implementation Timeline

### **Phase 0 (Now → Field Manual Launch)**
**What:** Document the idea, prepare the scraper.  
**Action items:**
- [ ] Decide: PRAW scraper OR manual audit via Google `site:` search?
- [ ] If PRAW: set up Reddit API credentials (takes 10 min).
- [ ] If manual: document the audit query list (search terms + date filters).
- [ ] Create placeholder structure in `project-research/` folder (in `content-engine/`).

**Output:** Ready-to-run scraper or audit checklist.

---

### **Phase 1 (Field Manual Sales → Proof Point)**
**Trigger:** Field manual starts converting (sales velocity confirmed).  
**What:** Run the scraper/audit once. Build the pain-points list.  
**Action items:**
- [ ] Execute scraper or manual audit on r/sysadmin (50 most-upvoted recent posts).
- [ ] Extract complaints: task name, frequency, why they hate it, blocker (skill/time/awareness).
- [ ] Categorize into pillars (your five pain pillars from CONTENT_OS.md).
- [ ] Write to `project-research/sysadmin-pain-points-YYYY-MM.md`.
- [ ] Flag top 3–5 as "high-signal, automatable" for product testing.

**Output:** Validated list of real sysadmin pain points + top candidates for dual-track projects.

---

### **Phase 2 (Post Validation → One-Off LinkedIn Test)**
**Trigger:** You've confirmed the pain-points list resonates + you have bandwidth.  
**What:** Pick 1 complaint, build both versions, post as LinkedIn value drop.  
**Action items:**
- [ ] Adapt the complaint as a dual-track project (from NextWork or custom build).
- [ ] Write Doer track (step-by-step technical guide).
- [ ] Write Operator track (Claude Code prompts + agent supervision instructions).
- [ ] Create LinkedIn post + carousel + article.
- [ ] Measure: engagement, comments, product interest signals.

**Output:** One LinkedIn content cycle + data on whether the dual-track concept resonates.

---

### **Phase 3 (Optional → Product Decision)**
**Trigger:** Phase 2 shows strong demand signals (high engagement, explicit ask-fors).  
**Decision:** Does this become a paid product (10–15 projects), or stay as ad-hoc content?

**If YES:** Plan a "Sysadmin Automation Library" as a Gumroad product ($47–$97).  
**If NO:** Keep running occasional one-offs. Don't build infrastructure.

---

## 4. Scraper Technical Details (For Claude Code Implementation)

### Option A: PRAW Scraper (Python)
**Pros:**
- Programmatic, repeatable.
- Captures metadata (upvotes, comment count, author, timestamp).
- Can filter by subreddit, score, date range.

**Cons:**
- Requires Reddit API credentials.
- Reddit ToS requires transparency (bots must identify themselves).

**Implementation:**
```python
# Pseudocode — Claude Code builds the actual implementation
import praw
import json

reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="sysadmin-pain-miner/1.0 by u/your_handle"
)

# Search r/sysadmin for pain signals
subreddit = reddit.subreddit("sysadmin")
complaints = []

for post in subreddit.search("manual OR repetitive OR tedious", time_filter="month", sort="top"):
    if post.score > 50:  # threshold for traction
        complaints.append({
            "title": post.title,
            "text": post.selftext,
            "score": post.score,
            "comments": post.num_comments,
            "url": post.url,
            "created": post.created_utc
        })

# Write to markdown with analysis
write_pain_points_md(complaints)
```

**Credentials setup:**
1. Go to https://www.reddit.com/prefs/apps → create a "personal use script."
2. Copy `client_id`, `client_secret`.
3. Store in `pipeline_secrets.env` (same as your YouTube pipeline).

### Option B: Manual Audit via Google `site:` Search
**Pros:**
- No API keys, no ToS friction.
- Uses your existing keyword research (five pillars).
- Fast for one-time audits.

**Cons:**
- Manual (slower for frequent runs).
- Can't programmatically extract as much metadata.

**Implementation:**
```
Search queries (run in browser, capture top 20):
- site:reddit.com/r/sysadmin "manual" OR "tedious" OR "tired of" after:2026-05-01
- site:reddit.com/r/sysadmin "repetitive" after:2026-05-01
- site:reddit.com/r/sysadmin "waste of time" after:2026-05-01
```

Then manually audit each post and write to markdown.

---

## 5. Data Structure: `sysadmin-pain-points.md`

```markdown
# Sysadmin Pain Points — r/sysadmin Audit
**Date:** June 2026  
**Source:** r/sysadmin top posts (last 30 days, score > 50)  
**Compiled by:** [Manual audit / PRAW scraper v1.0]

---

## High-Signal Automatable Tasks (Top 3)

### 1. Patch Report Consolidation
- **Complaint:** "Every Monday I spend 2 hours pulling patch reports from 15 servers and manually consolidating into one spreadsheet"
- **Frequency:** Weekly recurring
- **Blocker:** Doesn't know how to script it / no time to learn
- **Pillar:** Hand Off the Grunt Work
- **Potential project:** Build a patch aggregator (NextWork parallel or custom)
- **Score:** 3.5/5 (high frequency, high frustration, clearly automatable)

### 2. Password Reset Ticketing
- **Complaint:** "We could automate 90% of our password reset tickets but we have no budget for AD automation"
- **Frequency:** Daily (50+ resets/day)
- **Blocker:** Budget, legacy system constraints
- **Pillar:** Hand Off the Grunt Work
- **Potential project:** AD integration via PowerShell + agent supervision
- **Score:** 4/5 (highest volume, but budget blocker)

### 3. Server Inventory Sync
- **Complaint:** "Our inventory spreadsheet is always out of sync with actual servers"
- **Frequency:** Triggered by new deployments (2–3x/week)
- **Blocker:** No central inventory system; manual updates
- **Pillar:** Hand Off the Grunt Work
- **Potential project:** Auto-sync via API polling + reconciliation logic
- **Score:** 3/5 (useful, but solution is architecture-heavy)

---

## Medium-Signal Tasks (5–10 more)

[Captured but lower priority]

---

## False Positives (Complaints Not Automatable)
[E.g., "managing difficult employees," "legacy system vendor won't help," etc.]
```

---

## 6. Integration with ORCHESTRATOR.md

### Current Structure (from §4 — The Two Research Layers)
```
| Layer | Purpose | Tool | Cadence | Output |
| Deep research | YouTube transcripts | pipeline | Quarterly | pillar definitions |
| Trend research | Community discussion | Claude Code + web search | Monthly | pain-points-YYYY-MM.md |
```

### With Project Research Added
```
| Layer | Purpose | Tool | Cadence | Output |
| Deep research | YouTube transcripts | pipeline | Quarterly | pillar definitions |
| Trend research | Community discussion | Claude Code + web search | Monthly | pain-points-YYYY-MM.md |
| Project research | Automatable task complaints | PRAW / manual audit | After FM launch, then quarterly | sysadmin-pain-points.md |
```

**Storage location:** `content-engine/project-research/`  
**Brain file:** Add reference to this layer in `LinkedIn_CONTENT_OS.md` (§4.2) or create a thin `PROJECT_RESEARCH.md` in the research folder.

---

## 7. Explicit Non-Decisions (What We're NOT Doing Now)

- ❌ **No project library yet.** Awaiting sales proof.
- ❌ **No scraper runs until field manual has real sales.** Infrastructure before revenue is a sunk cost.
- ❌ **No Operator track platform lock-in.** The platform fits the user, not vice versa. (If they use Claude Code at work, they don't learn Cursor.)
- ❌ **No full NextWork adaptation.** Waiting to see which 3–5 complaints actually validate.
- ❌ **No email nurture automation.** That's Phase 5, after the list justifies it.

---

## 8. Claude Code Action Items

**When Phase 0 → Phase 1 transition happens:**

1. **If PRAW:** Set up scraper, store credentials in `pipeline_secrets.env`, test on r/sysadmin.
2. **If manual:** Document the Google `site:` query list in `PROJECT_RESEARCH.md`.
3. **Create folder:** `content-engine/project-research/` → placeholder `README.md`.
4. **First run (Phase 1):** Execute audit, write `sysadmin-pain-points-YYYY-MM.md`, flag top 3–5.
5. **Update TASKS.md:** Phase 4 becomes "Phase 4A — Project Research Audit" (complete after FM sales proof).

---

## 9. Success Criteria

**Phase 0 completion:** Scraper/audit process is documented and ready to run.  
**Phase 1 completion:** You have a ranked list of 5–10 automatable sysadmin complaints with pillar tags.  
**Phase 2 completion:** First dual-track project is live on LinkedIn; engagement measured.  
**Phase 3 decision:** You decide whether this becomes a product or stays as content.

---

## 10. Questions for Randy

Before Claude Code implements:

1. **Scraper tool:** PRAW (requires API setup) or manual audit (slower, simpler)?
2. **Audit scope:** r/sysadmin only, or also r/ITCareerQuestions + Spiceworks?
3. **Storage:** Phase 0, do you want Claude Code to create the folder structure now, or wait until Phase 1?
4. **Reporting:** Simple markdown list, or structured JSON + markdown?

---

**Handoff complete. Ready for Claude Code to ingest and phase into the ORCHESTRATOR/TASKS workflow.**
