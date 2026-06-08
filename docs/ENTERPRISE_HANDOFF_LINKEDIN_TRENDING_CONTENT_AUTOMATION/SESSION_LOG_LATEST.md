# SESSION_LOG_LATEST.md

**Purpose:** Single source of truth for Claude Code about youtube-downloader project state  
**Updated:** Automatically on each session start  
**Last Updated:** 2026-06-07T14:45:00Z  
**Confidence Level:** 🟢 READY TO BUILD

---

## ⚡ QUICK START FOR CLAUDE CODE

**You are building:** Trending Post Generator (TPG)  
**Into:** youtube-downloader (enterprise-ai-pipeline)  
**Read this first:** TRENDING_POST_GENERATOR_HANDOFF.md (in outputs/)  
**Then run:** `python scripts/preflight_check.py --strict`

**Status:** Phase 1 (Core Architecture) — Ready to begin

---

## 🔒 SECURITY CONTEXT

### Credential Vault Status
```
Vault Location: config/.vault/
Encryption: AES-256 (FERNET)
Keys Stored:
  ✅ ANTHROPIC_API_KEY (size: 48 bytes)
  ✅ BUFFER_API_TOKEN (size: 64 bytes)
  ✅ OPENAI_API_KEY (size: 48 bytes)
  ✅ LINKEDIN_OAUTH (size: 256 bytes)
Last Integrity Check: 2026-06-07T14:40:00Z (PASSED)
```

### PII Patterns Active
- SSN (###-##-####)
- Credit cards (####-####-####-####)
- Phone numbers (###-###-####)
- Email addresses
- Medical IDs (MRN#, Account#)
- Dates of birth (MM/DD/YYYY)

**Action:** Before logging any user input or post content, scan with `PIIScanner.scan(text)`.

### Audit Trail Status
```
Audit Log Location: logs/audit/
Chain Integrity: VERIFIED
Recent Events:
  - 2026-06-07T14:40:00Z: Vault initialization complete (actor: system)
  - 2026-06-07T14:35:00Z: Health check passed (actor: scheduled_job)
  - 2026-06-07T14:30:00Z: Session started (actor: claude-code)
```

---

## 📊 SYSTEM HEALTH

```json
{
  "status": "HEALTHY",
  "python_version": "3.11.4",
  "disk_available_gb": 87.3,
  "api_quotas": {
    "openai_dalle3": "45/100 per hour (45% used)",
    "buffer_api": "12/60 per hour (20% used)",
    "google_search": "23/100 per day (23% used)"
  },
  "git_status": "clean",
  "current_branch": "main",
  "uncommitted_changes": 0,
  "last_full_test": "2026-06-06T22:00:00Z"
}
```

**Next Health Check:** 2026-06-07T15:45:00Z (automatic)

---

## 🚀 WHAT YOU'RE BUILDING (PHASE 1)

### Command
```bash
python cli.py trending generate --date "2026-06-07" [--dry-run]
```

### What It Does
1. Scans trending topics from 5 communities (r/sysadmin, r/ITCareerQuestions, etc.)
2. Scores relevance to IT operator ICP (Irreplacible In the AI Era)
3. Researches top topic via web search + Claude analysis
4. Generates viral post using Randy's voice system + LinkedIn authority playbook
5. **Phase 2** (later): Generates GenX humor image (DALL-E 3)
6. **Phase 3** (later): Schedules to Buffer at optimal time (10:05 AM Tuesday)

### Current Status
- ✅ Architecture designed (Section 1, HANDOFF)
- ✅ Integration points verified (no breaking changes)
- ✅ Security controls documented (vault, PII, audit)
- ⏹️ Code not written yet (you start here)

### Scope (Phase 1 ONLY)
- ✅ Core CLI entry point (commands/trending.py)
- ✅ Trend analyzer (generators/trend_analyzer.py)
- ✅ Web search integration (integrations/web_search.py)
- ✅ Rate limiting (security/rate_limiter.py)
- ✅ Unit tests + security tests
- ⏹️ Image generation (Phase 2)
- ⏹️ Buffer scheduling (Phase 3)

---

## ⚠️ CRITICAL: DO NOT BREAK

**These systems are LIVE and revenue-generating:**

| System | Status | What Happens If You Break It |
|--------|--------|------------------------------|
| youtube-downloader core | ✅ Running | Daily video ingestion stops → no research material |
| Buffer API integration | ✅ Running | Can't schedule posts → no LinkedIn activity |
| Claude API calls | ✅ Running | Content generation fails → no output |
| Existing CLI commands | ✅ All working | Users can't use `ask`, `digest`, `analyze` → workflow blocked |

**Prevention:**
- Only ADD to `commands/` (new trending.py)
- DO NOT MODIFY existing command files
- Use feature flags (all TPG features start disabled)
- Run pre-flight checks before each change

---

## 📋 PRE-FLIGHT CHECKLIST (BEFORE YOU CODE)

```bash
# ✅ Run this first
python scripts/preflight_check.py --strict

# Expected output:
# ✅ Python 3.11+ detected
# ✅ Dependencies installed
# ✅ .env file exists with required keys
# ✅ /logs directory initialized
# ✅ Vault integrity verified
# ✅ Git repository clean
# ⚠️  Create feature branch: git checkout -b feature/trending-post-gen
```

**Do not proceed until all checks pass.**

---

## 🔄 INCIDENT HISTORY

### Last 30 Days
- **Total Incidents:** 0
- **Unresolved:** 0
- **Auto-Recovered:** 0

### Failure Patterns to Watch
None yet. First build phase will establish patterns.

---

## 🧠 WHAT YOU NEED TO KNOW

### Voice System (Your Authentic Tone)
Location: `/mnt/project/voice.md` and `linkedin_atomizer.py`

**Key Principles:**
- Specific, story-driven, vulnerable
- Dry, tired-veteran register with dark humor
- Repetition builds emphasis (whole-phrase construction)
- Gen X IT humor (ID10T, PEBKAC references)
- Concrete details beat generic advice
- Short punchy sentences

**Example Hook:** "Hurricane Laura. Motel. No hands-on experience. One engineer proved you don't need it."

**When generating posts:** Pass Randy's voice context to Claude as system prompt.

### LinkedIn Playbook (Viral Framework)
Location: `/mnt/project/LINKEDIN_TITLE_AND_FORMAT_STRATEGY.md`

**Hook Formulas:**
1. **Contrarian:** "Everyone says X. I did Y. Here's why."
2. **Problem Statement:** "If you've never experienced [specific pain], you're lucky."
3. **Story + Lesson:** "[Real story]. Here's what I learned."
4. **Pattern Recognition:** "I've seen this 3 times in 25 years."
5. **Vulnerability:** "I was wrong about [thing]. Here's the truth."

**Don't generate generic content.** Every post must:
- ✅ Start with a specific detail (name, date, stat, question)
- ✅ Include a real experience from Randy's 25-year career
- ✅ End with actionable advice (not just inspiration)
- ✅ Target the ICP: Gen X IT operators worried about AI displacement

### Content Pillars (Your Niche)
1. **The Flood:** Information overwhelm (AI news is chaos)
2. **What AI Can't Do:** Irreplaceable human judgment
3. **The Pivot:** From doer to AI manager
4. **Hand Off the Grunt Work:** Automation as delegation
5. **Don't Get AI'd Out Before Retirement:** Career insurance

**Every post maps to one pillar.** Trend analyzer scores topics against these.

---

## 🎯 SUCCESS CRITERIA (How You Know You're Done)

### Phase 1 (Core): COMPLETE when
- ✅ `python cli.py trending generate --date today --dry-run` works
- ✅ Outputs: topic, relevance score, post text, why this post (structured JSON)
- ✅ No API calls made in dry-run mode
- ✅ Post text follows Randy's voice system
- ✅ All unit tests pass (100% coverage on new code)
- ✅ Security tests pass (no PII, no credentials leaked)
- ✅ You can manually review output before approving merge

### Phase 2 (Images): Ready when
- Image generation library integrated (DALL-E 3 or Gemini)
- GenX IT aesthetic defined (one hero artifact per post)
- Rate limiting prevents API quota overages
- Tests confirm images match spec

### Phase 3 (Scheduling): Ready when
- Buffer scheduling works (already have integration)
- Optimal time logic implemented (10:05 AM Tuesday + time zones)
- Schedule can be triggered manually or via Task Scheduler
- Posts actually appear on LinkedIn

---

## 🔧 COMMON TASKS (Checklists)

### When Starting a Build Session
- [ ] Read this file (SESSION_LOG_LATEST.md) — 5 min
- [ ] Check health status: `python scripts/health_check.py`
- [ ] Verify vault access: `python -c "from security.vault import CredentialVault; CredentialVault().retrieve('ANTHROPIC_API_KEY')"`
- [ ] Review recent incidents: check INCIDENT_TRACKER.md
- [ ] Update SESSION_LOG_LATEST.md with your task
- [ ] Create feature branch: `git checkout -b feature/task-name`

### When Pushing Code
- [ ] Run pre-flight: `python scripts/preflight_check.py --strict`
- [ ] Run tests: `pytest tests/ -v --cov`
- [ ] Security scan: `bandit -r . --skip B101`
- [ ] Check for credentials: `git diff --cached | grep -i secret`
- [ ] Update SESSION_LOG_LATEST.md
- [ ] Commit: `git commit -m "Descriptive message"`
- [ ] Create PR (don't merge directly to main)

### When Tests Fail
- [ ] Check error message carefully
- [ ] Run: `python scripts/health_check.py --verbose`
- [ ] Check INCIDENT_TRACKER.md for similar issues
- [ ] Run single test in isolation: `pytest tests/test_failing.py::test_name -vvs`
- [ ] If still stuck, log incident and ask for approval to skip

### When API Quota Gets Low
- [ ] Check: `python scripts/check_quota.py`
- [ ] Rate limiter will auto-queue requests if near limit
- [ ] If overages occur, health check will alert
- [ ] Fallback APIs available (Gemini if DALL-E quota hit)

---

## 📞 GETTING HELP

| Problem | Action | Why |
|---------|--------|-----|
| Code not running | Check `python scripts/health_check.py --verbose` | Detects missing deps, credential issues, etc. |
| Test fails | Run `pytest tests/failing_test.py -vvs` | See detailed output |
| Credential error | Run `python scripts/init_vault.py` | Re-initialize vault |
| Git issues | Check git status: `git status` | See uncommitted changes |
| Out of disk | Run `python scripts/cleanup_old_logs.py` | Archive old logs |
| Rate limited | Wait automatically (RateLimiter does this) | Or check quota: `python scripts/check_quota.py` |

**If you're really stuck:**
1. Update INCIDENT_TRACKER.md with problem
2. Run: `python scripts/generate_incident_report.py`
3. Take a screenshot of health_check output
4. Send error to Randy with context

---

## 📈 METRICS TO TRACK

As you build, monitor these (health_check.py auto-logs):

- **Build time per module:** How long to write commands/trending.py?
- **Test coverage:** Aim for 100% on new code
- **API quota usage:** Rate limiter should stay < 80%
- **Error rate:** Should be 0 in dry-run mode
- **Log size:** Shouldn't grow > 100MB during build
- **Security scan time:** Bandit should complete < 10 seconds

---

## 🎓 LEARNING FOR FUTURE

As you build, log learnings:

```markdown
## Learning: [Topic]
**Date:** 2026-06-07  
**Discovery:** [What you learned]  
**Why It Matters:** [Impact on project]  
**For Next Time:** [How to apply elsewhere]
```

Examples:
- How to integrate with rate limiter properly
- Unexpected dependency conflicts
- PII scanning edge cases
- Image generation prompt engineering
- Buffer API quirks

---

## 🏁 NEXT IMMEDIATE STEPS

1. **Read TRENDING_POST_GENERATOR_HANDOFF.md** (20 min)
2. **Run `python scripts/preflight_check.py --strict`** (2 min)
3. **Review HANDOFF Section 2 (Pre-Flight Checklist)** (10 min)
4. **Update this file:** change status to "PHASE 1 IN PROGRESS"
5. **Create feature branch:** `git checkout -b feature/trending-post-gen`
6. **Start building:** commands/trending.py first (primary entry point)
7. **Report back:** update SESSION_LOG_LATEST.md with progress

---

**Status at Start:** 🟢 READY  
**Status Now:** [UPDATE AS YOU PROGRESS]  
**Confidence Level:** 🟢 (all pre-flight checks passing)

---

## APPENDIX: Files You'll Reference

| File | Purpose | Location |
|------|---------|----------|
| TRENDING_POST_GENERATOR_HANDOFF.md | Master spec for this project | outputs/ |
| INCIDENT_TRACKER.md | Learning log (auto-updated) | project root |
| HEALTH_REPORT_LATEST.json | System status snapshot | project root |
| ORCHESTRATOR.md | Cross-project architecture | project root |
| voice.md | Randy's voice system | /mnt/project/ |
| linkedin_atomizer.py | Atomization logic (reference) | /mnt/project/ |
| requirements-tpg.txt | Python dependencies | project root |

---

**Generated:** 2026-06-07T14:45:00Z  
**Next Auto-Update:** 2026-06-08T06:00:00Z (daily, before build time)
