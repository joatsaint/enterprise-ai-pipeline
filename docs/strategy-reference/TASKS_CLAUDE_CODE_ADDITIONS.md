# TASKS.md — Claude Code Handoff Actions
## Add These Tasks to Your Active Board

Copy these tasks into your `TASKS.md` "Active" section. Claude Code will see them and know what to do.

---

## Active ← do now

- [ ] **Read CLAUDE_CODE_MODEL_EVALUATION_HANDOFF.md** — Understand task routing and model evaluation strategy. Focus on §2 (Task Inventory), §3 (Models), §5 (Decision Tree). *(Time: 30 min. Due: This session.)*

- [ ] **Read TOKEN_EFFICIENCY_ALTERNATIVES_GUIDE.md** — Understand cost savings strategies and when to use cheaper models. Focus on §1–2 (problem), §4 (free plans). *(Time: 20 min. Due: This session.)*

- [ ] **Implement routing function in linkedin_atomizer.py** — Add `get_model_for_task()` function to route atomization tasks to Opus (research) vs. Sonnet (routine). Code template in CLAUDE_CODE_MODEL_EVALUATION_HANDOFF.md §6. *(Time: 15 min. Due: This session.)*

- [ ] **Test Claude Sonnet 4.6 on 1 routine article** — Atomize ART5 (or similar routine topic) using Sonnet model string instead of Opus. Compare output quality (voice, accuracy, tone) to Opus baseline. *(Time: 10 min + review. Due: This session.)*

- [ ] **Generate Sonnet Test Report** — Report to Randy: Quality (%), Token cost (vs. Opus), Recommendation (PASS/FAIL). See CLAUDE_CODE_HANDOFF_SUMMARY.md for template. *(Time: 5 min. Due: This session.)*

---

## Blocked on Randy ← waiting on a decision or input from you

- [ ] **Approval to roll out Sonnet routing** — Wait for Randy to review Sonnet test report. If PASS (≥90% quality), proceed with Phase 1 rollout (60% of routine work → Sonnet). If FAIL, try alternative (DeepSeek or further prompt optimization).

---

## Backlog ← later, not now

- [ ] **Phase 2 · Implement DeepSeek routing** — After Sonnet approved, add DeepSeek for non-voice-critical tasks (hashtags, descriptions, simple formatting). Requires API key + wrapper code. *(Blocked on: Sonnet approval)*

- [ ] **Phase 3 · Batch processing for background work** — After model switching working, implement batch API for overnight atomization (50% cost discount, 4–24h latency acceptable). *(Blocked on: Sonnet + DeepSeek working)*

- [ ] **Phase 4 · Token cost dashboard** — Track spend by model/task monthly. Report savings to Randy. *(Blocked on: Multi-model routing live)*

- [ ] **Phase 5 · Gemini free tier integration** — Test Google Gemini free tier (1000 requests/day) for long-context research tasks (1M context window). *(Blocked on: Cost dashboard working)*

---

## Reference: What Each Document Unlocks

| Document | Read Time | Why | Action Item |
|----------|-----------|-----|------------|
| CLAUDE_CODE_MODEL_EVALUATION_HANDOFF.md | 30 min | Your to-do list | Add routing function to atomizer |
| TOKEN_EFFICIENCY_ALTERNATIVES_GUIDE.md | 20 min | Context on cost savings | Understand which models work when |
| CLAUDE_CODE_HANDOFF_SUMMARY.md | 5 min | This summary | Know what to prioritize |
| ZAPIER_MCP_PLATFORM_HANDOFF.md | Skim §3 | Platform specs (reference) | Don't guess character limits |
| EXPERT_ENGAGEMENT_SAFETY_PRACTICES.md | Skim §2 | Best practices (reference) | Remember golden hour, avoid bans |

---

**Status:** Ready for Claude Code to execute  
**Deadline for Sonnet test:** This session  
**Reporter:** Claude Code  
**Approver:** Randy Skiles
