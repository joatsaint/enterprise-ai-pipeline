# RANDY'S PRE-HANDOFF CHECKLIST

**Before you give the handoff to Claude Code, complete this checklist.**

Run in order. Stop at any ❌ and fix before proceeding.

---

## STEP 1: DOCUMENT REVIEW (15 minutes)

- [ ] Read HANDOFF_PACKAGE_SUMMARY.md (index + overview)
- [ ] Skim TRENDING_POST_GENERATOR_HANDOFF.md §1 (architecture)
- [ ] Skim TRENDING_POST_GENERATOR_HANDOFF.md §5 (security — does it fit your use case?)
- [ ] Review SESSION_LOG_LATEST.md (what Claude Code will see)
- [ ] Review CLAUDE_CODE_QUICK_REFERENCE.md (quick patterns)

**When done:** You understand the architecture and can explain it in 2 minutes.

---

## STEP 2: ENVIRONMENT SETUP (10 minutes)

### 2.1: Create .env file (NEVER commit this)

**In your youtube-downloader folder:**

```bash
# Create .env file
cat > .env << 'EOF'
# NEVER commit this file
# Add to .gitignore immediately

# 1. Encryption key for credential vault
VAULT_ENCRYPTION_KEY=<GENERATE_NEW>

# 2. Your API keys (get from services)
ANTHROPIC_API_KEY=sk-...
BUFFER_API_TOKEN=...
OPENAI_API_KEY=...
LINKEDIN_OAUTH=...
EOF
```

**To generate VAULT_ENCRYPTION_KEY:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output and paste into .env

### 2.2: Verify .env in .gitignore

```bash
# Check if .env is protected
grep ".env" .gitignore

# If NOT found, add it:
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore (never commit credentials)"
```

**Status Check:** ✅ `.env` file exists and is in `.gitignore`

---

## STEP 3: VAULT INITIALIZATION (5 minutes)

**Initialize the credential vault** (one-time only):

```bash
# Create vault directory
mkdir -p config/.vault

# Initialize vault (this will be interactive)
python scripts/init_vault.py
```

**It will ask you:**
- ANTHROPIC_API_KEY: paste your key
- BUFFER_API_TOKEN: paste your token
- OPENAI_API_KEY: paste your key
- LINKEDIN_OAUTH: paste your oauth token

**Verify vault works:**
```bash
python -c "from security.vault import CredentialVault; v = CredentialVault(); key = v.retrieve('ANTHROPIC_API_KEY'); print('✅ Vault working. Key starts with:', key[:10])"
```

**If error:** Check .env has VAULT_ENCRYPTION_KEY set.

**Status Check:** ✅ Vault initialized and verified

---

## STEP 4: GIT SETUP (5 minutes)

### 4.1: Ensure you're on clean main branch

```bash
# Check status
git status
# Expected: "On branch main" or "On branch master", "nothing to commit, working tree clean"

# If not clean:
git stash  # save uncommitted work
git checkout main
git pull origin main
```

### 4.2: Create feature branch for this work

```bash
git checkout -b feature/trending-post-gen
```

### 4.3: Verify protection rules

```bash
# Check branch protection (should prevent direct pushes to main)
git branch -v

# Try to push to a test branch (this is OK)
git push origin feature/trending-post-gen --set-upstream
```

**Status Check:** ✅ You're on `feature/trending-post-gen`, clean working tree

---

## STEP 5: DEPENDENCY CHECK (10 minutes)

### 5.1: Verify Python version

```bash
python --version
# Expected: Python 3.11+
```

If Python < 3.11, upgrade before proceeding.

### 5.2: Create requirements-tpg.txt (lock exact versions)

```bash
# Generate dependency snapshot
pip freeze > requirements-tpg.txt

# Add to git
git add requirements-tpg.txt
git commit -m "Lock dependencies for trending-post-generator"
```

### 5.3: Install security/testing tools

```bash
# For security scanning
pip install bandit

# Already have: pytest, httpx, anthropic, python-dotenv (from existing requirements)
```

**Status Check:** ✅ Dependencies verified, snapshot created

---

## STEP 6: PRE-FLIGHT VALIDATION (10 minutes)

**Run the preflight check (blocking gate):**

```bash
python scripts/preflight_check.py --strict
```

**Expected output:**
```
✅ Python 3.11+ detected
✅ Required dependencies installed
✅ .env file exists with REQUIRED keys:
   - ANTHROPIC_API_KEY
   - BUFFER_API_TOKEN
   - OPENAI_API_KEY
   - LINKEDIN_OAUTH
✅ /logs directory writable and initialized
✅ Vault integrity verified
✅ Existing youtube-downloader imports validate
✅ Git repository clean
✅ Current branch is feature/trending-post-gen
```

**If any ❌:** Fix that item, then re-run until all ✅

**Status Check:** 🟢 ALL PRE-FLIGHT GATES PASS

---

## STEP 7: EXISTING SYSTEM SMOKE TEST (10 minutes)

**Verify nothing is broken in existing systems:**

```bash
# Test 1: Can existing CLI commands import?
python -c "from commands.schedule import *; print('✅ schedule imports')"
python -c "from integrations.buffer_api import *; print('✅ buffer_api imports')"
python -c "from generators.post_writer import *; print('✅ post_writer imports')"

# Test 2: Do existing tests still pass?
pytest tests/ -v --ignore=tests/test_trending* -x 2>&1 | tail -20
# Expected: all tests pass (or all existing tests at least)

# Test 3: Can you run an existing command (dry-run)?
python cli.py ask "test query" --fast --dry-run 2>&1 | head -5
# Expected: some output or error about no results, not an import error

# Test 4: Git clean?
git status
# Expected: "nothing to commit, working tree clean"
```

**If any fails:** DO NOT PROCEED. Fix the existing system first.

**Status Check:** ✅ Existing systems still work

---

## STEP 8: SECURITY REVIEW (10 minutes)

**Read the compliance checklist** (HANDOFF.md §5.5):

```bash
# Relevant for you?
cat << 'EOF'
These are the industries this system is designed for:
- Banking (financial institution compliance)
- Insurance (data protection regulations)
- Healthcare (HIPAA data protection)
- Government (federal office security standards)

Does TPG run in one of these environments?
EOF
```

- [ ] TPG is for a **banking/financial** environment
  - If yes: Review GLBA requirements (financial data protection)
  
- [ ] TPG is for a **healthcare** environment
  - If yes: Review HIPAA requirements (patient data protection)
  
- [ ] TPG is for a **government** environment
  - If yes: Review federal security standards
  
- [ ] TPG is for an **insurance** company
  - If yes: Review data protection regulations

**Answer:** Check the box that applies, or if none (personal use), note that.

**Status Check:** ✅ Compliance requirements understood

---

## STEP 9: ALERTING & ESCALATION SETUP (5 minutes)

**Decide how to be notified of issues:**

```bash
# Fill in these answers (add to a note file):

Q1: Where should critical alerts go?
    A: ☐ Email (randy@...)
    B: ☐ Slack channel (#security)
    C: ☐ PagerDuty
    D: ☐ Phone call to [number]

Q2: When should I be alerted?
    A: ☐ Only CRITICAL errors
    B: ☐ CRITICAL + HIGH severity
    C: ☐ All errors (CRITICAL, HIGH, MEDIUM)

Q3: How often do you want incident reviews?
    A: ☐ Weekly (Friday EOD)
    B: ☐ Bi-weekly
    C: ☐ Monthly
```

Document your answers. You'll configure these alerts in HANDOFF.md §5.4 (Escalation Policy).

**Status Check:** ✅ Alerting plan decided

---

## STEP 10: FINAL DECISION GATE (5 minutes)

**Answer these questions:**

1. **Are you ready for Claude Code to start building?**
   - ☐ Yes, I've completed steps 1-9
   - ☐ No, something is missing

2. **Do you understand the architecture?** (Could you explain it to someone else?)
   - ☐ Yes
   - ☐ No, need to re-read HANDOFF.md §1

3. **Are you comfortable with the security model?** (Vault encryption, PII scanning, audit logs)
   - ☐ Yes
   - ☐ No, need to re-read HANDOFF.md §5

4. **Do you have the 4 API keys ready?**
   - ☐ Yes (ANTHROPIC_API_KEY, BUFFER_API_TOKEN, OPENAI_API_KEY, LINKEDIN_OAUTH)
   - ☐ No, missing one or more

5. **Are you on `feature/trending-post-gen` branch?**
   - ☐ Yes (verified with `git branch`)
   - ☐ No, need to create

6. **Did pre-flight validation pass (Step 6)?**
   - ☐ Yes, all ✅
   - ☐ No, had failures

**If all "Yes" → Proceed to Step 11**  
**If any "No" → Go back and fix before proceeding**

---

## STEP 11: FINAL COMMIT (2 minutes)

**Commit your setup work:**

```bash
# Verify what's staged
git status

# Should show:
# - modified: .gitignore (added .env)
# - modified: requirements-tpg.txt (OR new file if first time)
# - possibly: HANDOFF documents (if you copied them here)

# Commit
git add .
git commit -m "Pre-handoff setup: vault, .env protection, dependencies locked"

# Verify clean
git status
# Expected: "nothing to commit, working tree clean"
```

**Status Check:** ✅ Setup committed to git

---

## STEP 12: HAND OFF TO CLAUDE CODE (2 minutes)

**Now you're ready. Tell Claude Code:**

```
You have 5 documents to read:

1. HANDOFF_PACKAGE_SUMMARY.md (index + overview)
2. TRENDING_POST_GENERATOR_HANDOFF.md (master spec)
3. SESSION_LOG_LATEST.md (your startup context)
4. INCIDENT_TRACKER.md (learning log template)
5. CLAUDE_CODE_QUICK_REFERENCE.md (quick reference)

All in: /mnt/user-data/outputs/

Current status:
- Branch: feature/trending-post-gen ✅
- Pre-flight validation: PASSED ✅
- Vault: initialized ✅
- .env: protected ✅
- Existing systems: working ✅
- Ready to build: YES ✅

Build Phase 1 (Core Architecture):
- Command: cli.py trending generate
- Scope: trend analyzer + web search + post generation
- Tests: 100% coverage required
- Security: vault, PII, audit, rate limiting
- Dry-run mode: working before any real API calls

Success criteria:
- `python cli.py trending generate --date today --dry-run` works end-to-end
- Post text matches my voice system
- Topics score high on ICP relevance
- All tests pass
- Zero incidents (first time you build)
- PR ready for my review (don't merge to main)

Go.
```

---

## POST-HANDOFF MONITORING (Ongoing)

**Every morning, check:**

```bash
# Check latest status
cat SESSION_LOG_LATEST.md | head -30

# Check for incidents
cat INCIDENT_TRACKER.md | grep "Incident #" | tail -5

# Check system health (if Claude Code is building)
python scripts/health_check.py
```

**If Claude Code gets stuck:**
1. Check `SESSION_LOG_LATEST.md` for context
2. Check `INCIDENT_TRACKER.md` for similar issues
3. Run `python scripts/health_check.py --verbose` for diagnostics
4. If needed, pause Claude Code and investigate

**Weekly review (Friday EOD):**
- Read INCIDENT_TRACKER.md (what went wrong?)
- Check metrics (API quota usage, test coverage, error rate)
- Approve any PRs waiting
- Update escalation/alerting if needed

---

## SUCCESS CHECKLIST

When complete, you'll have:

- ✅ All 5 handoff documents ready
- ✅ .env file created and protected (in .gitignore)
- ✅ Vault initialized with encrypted credentials
- ✅ Feature branch created (`feature/trending-post-gen`)
- ✅ Pre-flight validation PASSED
- ✅ Existing systems verified working
- ✅ Compliance requirements understood
- ✅ Alert/escalation plan documented
- ✅ Ready to hand to Claude Code

**Time to complete:** ~90 minutes (first time) or 15 minutes (if you've done similar setup)

---

## IF YOU GET STUCK

| Issue | Fix |
|-------|-----|
| "ModuleNotFoundError" in preflight | Install missing deps: `pip install -r requirements.txt` |
| ".env file not found" | Create it: see Step 2.1 above |
| "Vault key not set" | Copy output from `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` into .env |
| "Git branch wrong" | Switch: `git checkout -b feature/trending-post-gen` |
| "Existing tests fail" | Fix those first before handing to Claude Code |
| "Pre-flight still failing" | Re-read error message carefully, fix that specific issue |

---

## FINAL GATE

**Before you hand to Claude Code, answer these 3 questions:**

1. **Can you explain the trending-post-generator architecture in 1 minute?**
   - If no: re-read HANDOFF.md §1
   
2. **Do you know where your credentials are stored?**
   - If no: they're in `config/.vault/` (encrypted)
   
3. **Do you know how to check if something went wrong?**
   - If no: run `python scripts/health_check.py --verbose`

**If you answered "yes" to all 3 → Ready to proceed**

---

**Checklist Created:** 2026-06-07  
**Estimated Time:** 90 minutes  
**Status:** 🟢 READY TO USE

**Next Step:** Follow this checklist, then hand the 5 documents to Claude Code.
