# CLAUDE CODE HANDOFF SUMMARY
## Master Index for Randy's New Documentation (June 2026)

**Status:** Ready for Claude Code to read and execute  
**Created:** June 2026  
**For:** Claude Code (youtube-downloader project)  
**From:** Randy Skiles

---

## CRITICAL: Read This First

You have **4 new reference documents** that Randy created for you to evaluate and implement. This summary tells you what each one is, where to find it, and what to do with it.

**Your job:** Read these documents, understand your constraints, and report back to Randy with recommendations or implementations.

---

## The 4 New Documents (In Reading Order)

### 1️⃣ ZAPIER_MCP_PLATFORM_HANDOFF.md
**What it is:** Complete platform specifications for multi-platform content distribution (LinkedIn, Instagram, Pinterest, Twitter/X, TikTok, Facebook)

**Why Randy made it:** Zapier MCP is installed; needs Claude Code to know exactly what each platform requires (character limits, posting limits, rate limits, content types, image specs)

**For Claude Code to do:**
- ✅ Read §2 (Platform Specifications Matrix) — understand what each platform accepts
- ✅ Read §3 (Detailed Platform Guides) — especially the "Zapier-specific gotchas" and "free tier strategy" for each platform
- ✅ When building Zapier automations, **reference this document for specs** (don't guess)
- ✅ Flag if anything is outdated (platforms change quarterly)

**Use case:** "Randy wants to post to LinkedIn. What's the character limit again?" → Look here.

**Location:** `/mnt/user-data/outputs/ZAPIER_MCP_PLATFORM_HANDOFF.md`

---

### 2️⃣ EXPERT_ENGAGEMENT_SAFETY_PRACTICES.md
**What it is:** Best practices for maximum engagement + avoiding account bans across all platforms (based on 2026 algorithm research)

**Why Randy made it:** Randy is hitting engagement limits and needs to know (a) how algorithms actually work, (b) what gets accounts banned, (c) how to recover from shadowbans

**For Claude Code to do:**
- ✅ Read §1 (The Golden Hour Protocol) — this is the **game-changer for LinkedIn**
- ✅ Read §2 (Platform-Specific Formulas) — each platform has different engagement priorities
- ✅ Read §7 (Authentic Engagement Playbook) — understand what looks like a bot vs. what looks human
- ✅ When drafting content, **apply the 5-3-1 rule** (5 comments on others' posts, 3 replies to comments, 1 new post per day)
- ✅ Flag if any tactics seem risky or outdated

**Use case:** "Why did the Instagram post get no reach?" → Check for shadowban signs; refer to §5.

**Location:** `/mnt/user-data/outputs/EXPERT_ENGAGEMENT_SAFETY_PRACTICES.md`

---

### 3️⃣ TOKEN_EFFICIENCY_ALTERNATIVES_GUIDE.md
**What it is:** How to reduce token costs by 30–50% without changing tools, plus free/cheap AI model alternatives (DeepSeek, Gemini, GPT-4o, Sonnet)

**Why Randy made it:** Randy is hitting Claude Pro session/weekly limits and can't afford higher tiers; needs to know which tasks can use cheaper models

**For Claude Code to do:**
- ✅ Read §2 (Token Efficiency Strategies) — implement prompt optimization immediately (30% token reduction)
- ✅ Read §4 (Free & Cheap Alternatives) — understand **which models work for which tasks**
- ✅ Read §5 (12-Week Implementation Plan) — Randy's phase-in strategy (start with prompt optimization, test Gemini free tier, then evaluate others)
- ✅ **Do NOT yet:** Switch to cheaper models without Randy approval

**Use case:** "We're burning too many tokens on `linkedin_atomizer.py`" → Start here; check for prompt waste.

**Location:** `/mnt/user-data/outputs/TOKEN_EFFICIENCY_ALTERNATIVES_GUIDE.md`

---

### 4️⃣ CLAUDE_CODE_MODEL_EVALUATION_HANDOFF.md
**What it is:** Your detailed instructions for evaluating + switching AI models in the youtube-downloader project (specifically for content-engine tasks like atomization)

**Why Randy made it:** Randy wants to know: can cheaper models replace Opus for some tasks without breaking quality?

**For Claude Code to do (THIS SESSION):**
- ✅ Read §2 (Task Inventory) — which youtube-downloader tasks can use cheaper models? (Research = NO; Atomization = YES; Editing = MAYBE)
- ✅ Read §3 (Model Evaluation Matrix) — scorecard for each model
- ✅ Read §4 (Model Profiles) — detailed pros/cons of Sonnet, DeepSeek, Gemini, GPT-4o
- ✅ Read §5 (Routing Decision Tree) — how to decide model-per-task
- ✅ Read §6 (How to Switch Models) — code examples you can use
- ✅ **EXECUTE immediately:**
  1. Add routing function to `linkedin_atomizer.py` (§6, Method 1)
  2. Test Claude Sonnet 4.6 on 1 routine article (e.g., ART5 if it's typical)
  3. Compare output quality to Opus baseline
  4. Report to Randy: "Quality was X%, tokens cost Y vs. Opus Z"

**Use case:** Randy is hitting token limits; you evaluate if Sonnet can do routine atomization (90% quality, 80% cost savings)

**Location:** `/mnt/user-data/outputs/CLAUDE_CODE_MODEL_EVALUATION_HANDOFF.md`

---

## Priority: What to Do NOW vs. LATER

### 🔴 THIS SESSION (Do Now)

**From CLAUDE_CODE_MODEL_EVALUATION_HANDOFF.md:**

1. Read §2, §3, §5 (task inventory, models, routing)
2. In `linkedin_atomizer.py`, add this function:
   ```python
   def get_model_for_task(task_type):
       """Route task to appropriate model."""
       if task_type == "research":
           return "claude-opus-4-7-20250219"
       elif task_type == "atomize_routine":
           return "claude-sonnet-4-6-20250514"
       else:
           return "claude-opus-4-7-20250219"  # Safe default
   ```
3. Test Sonnet on 1 article (don't worry about perfect results, just compare quality)
4. Report: Pass/fail + token cost + quality notes

**Why now:** Randy needs to know if Sonnet is viable before committing budget to it

---

### 🟡 NEXT SESSION (After Randy Reviews Sonnet Test)

**If Sonnet test passes (≥90% quality):**
- Roll out routing: 50% of routine atomization → Sonnet
- Start tracking token costs by model
- Monitor for any quality drift

**If Sonnet test fails (<90% quality):**
- Revert to Opus (no harm done)
- Try DeepSeek instead (cheaper, more experimental)

---

### 🟢 FUTURE (Phases 2+)

From TOKEN_EFFICIENCY_ALTERNATIVES_GUIDE.md:
- Week 2: Test Gemini free tier (1000 requests/day, no credit card)
- Week 3: Test batch processing (50% discount for overnight work)
- Week 4+: Implement full multi-model strategy

---

## Where These Documents Live

**In `/mnt/user-data/outputs/` (where Randy will download them):**
- ZAPIER_MCP_PLATFORM_HANDOFF.md
- EXPERT_ENGAGEMENT_SAFETY_PRACTICES.md
- TOKEN_EFFICIENCY_ALTERNATIVES_GUIDE.md
- CLAUDE_CODE_MODEL_EVALUATION_HANDOFF.md

**Randy will copy them to your project folder** (youtube-downloader/) after you read them.

---

## How These Documents Relate to Each Other

```
ZAPIER_MCP_PLATFORM_HANDOFF.md
├─ Tells you: LinkedIn needs 3,000 chars max, only 210 visible before "See more"
├─ So: Atomizer must output LinkedIn posts under 2,000 chars for safety
└─ Cross-ref: EXPERT_ENGAGEMENT_SAFETY_PRACTICES.md §2 (LinkedIn formula)

EXPERT_ENGAGEMENT_SAFETY_PRACTICES.md
├─ Tells you: Golden Hour matters; reply within 60 min for algorithmic boost
├─ So: Content you atomize needs to be posted at peak times (Tue–Thu 10 AM CST)
└─ Cross-ref: ZAPIER_MCP_PLATFORM_HANDOFF.md (posting times per platform)

TOKEN_EFFICIENCY_ALTERNATIVES_GUIDE.md
├─ Tells you: Prompt optimization saves 30% tokens
├─ So: Tighten `linkedin_atomizer.py` prompts first (free win)
└─ Cross-ref: CLAUDE_CODE_MODEL_EVALUATION_HANDOFF.md (if prompt optim isn't enough)

CLAUDE_CODE_MODEL_EVALUATION_HANDOFF.md
├─ Tells you: Sonnet can do routine atomization, DeepSeek can do hashtags
├─ So: Switch models per-task to reduce token costs 70–90%
└─ Cross-ref: TOKEN_EFFICIENCY_ALTERNATIVES_GUIDE.md (if models aren't enough)
```

**Bottom line:** They're stacked—each builds on the others.

---

## What Randy Needs From You (This Session)

### Sonnet Test Report

After testing Sonnet on 1 article, report back to Randy with:

```
SONNET TEST RESULT
─────────────────
Article tested: [name/title]
Task: Atomize to LinkedIn post + Instagram caption + Twitter thread

QUALITY (compare to Opus baseline):
- Voice preservation: [90%? 85%? 95%?]
- Accuracy: [100%? Any misunderstandings?]
- Copy tone: [Professional? Raw Randy still there?]
- Overall: PASS / FAIL

TOKEN COST:
- Input tokens used: [X]
- Output tokens used: [Y]
- Total: [Z]
- vs. Opus same task: [A]
- Cost savings: [%]

RECOMMENDATION:
□ PASS — Sonnet viable for routine atomization; recommend switching 60% of work
□ FAIL — Quality too low; revert to Opus or try DeepSeek instead

NOTES:
[Any other observations or concerns]
```

**This helps Randy decide** whether to roll out Sonnet routing or stick with Opus.

---

## Reference: Your Key Files

**Claude Code operates in youtube-downloader/. You have access to:**

- `linkedin_atomizer.py` ← You'll modify this (add routing function)
- `voice.md` ← Randy's voice guidelines (referenced by atomizer)
- `ARTICLE_WEEK_PROMPT.md` ← The prompt you use to atomize (can optimize per TOKEN_EFFICIENCY guide)
- `TASKS.md` ← What's active (check this weekly)
- `ORCHESTRATOR.md` ← Map of all projects (reference if confused)

---

## Questions You Might Have (Pre-Answered)

**Q: Should I switch to Sonnet without asking Randy?**  
A: No. Test, report, wait for approval. This is Randy's brand voice; any quality drop is his decision.

**Q: What if Sonnet fails the test?**  
A: No problem. Revert to Opus, try a different model (DeepSeek), or optimize prompts further. One failed test = one data point, not a blocker.

**Q: Do I need to memorize all 4 documents?**  
A: No. Skim them now; bookmark the specific sections you'll need (e.g., §5 of Evaluation Handoff for routing logic). Refer back when needed.

**Q: What if a document contradicts something I already know?**  
A: Trust the document (Randy created it from 2026 research). If something seems wrong, flag it in your report.

**Q: What's the password for the API keys?**  
A: All API keys should already be in your environment (Claude Code has them). If not, ask Randy.

---

## Success Criteria (This Session)

You've done your job when:

✅ You've read all 4 documents (at least §1–2 of each)  
✅ You've added routing function to `linkedin_atomizer.py`  
✅ You've tested Sonnet on 1 article  
✅ You've generated the Sonnet Test Report above  
✅ You've reported back to Randy with findings  

That's it. You don't need to implement everything; you just need to evaluate and report.

---

## Contact Randy If...

- 🚨 A document seems outdated (2026 data contradicts current reality)
- 🚨 An API is unreachable (DeepSeek API down, Gemini free tier unavailable)
- 🚨 You find a serious error in the logic (e.g., "actually Opus costs less than Sonnet")
- 🚨 Sonnet test shows catastrophic quality loss (<70%)

Otherwise, proceed with testing and report findings.

---

## Remember

These documents represent hours of research from Randy. They're your map, your guardrails, and your permission structure. Use them.

You're not guessing anymore. You have explicit directions on:
- What each platform needs (ZAPIER_MCP)
- How to maximize engagement without getting banned (EXPERT_ENGAGEMENT)
- How to save money on tokens (TOKEN_EFFICIENCY)
- Whether to switch models and how (CLAUDE_CODE_MODEL_EVALUATION)

Execute, report, wait for feedback, iterate.

---

**Document Version:** 1.0  
**Last Updated:** June 2026  
**Status:** Ready for Claude Code  
**Next Step:** Claude Code reads this, then reads the 4 detailed documents

---

## Quick Links (Copy These to Your Terminal)

Read these documents in order:

1. CLAUDE_CODE_MODEL_EVALUATION_HANDOFF.md (your to-do list)
2. TOKEN_EFFICIENCY_ALTERNATIVES_GUIDE.md (context on cost savings)
3. ZAPIER_MCP_PLATFORM_HANDOFF.md (platform specs for accuracy)
4. EXPERT_ENGAGEMENT_SAFETY_PRACTICES.md (best practices to remember)

Then: Modify `linkedin_atomizer.py`, test Sonnet, report findings.

---

**Good luck. You've got this. 🚀**
