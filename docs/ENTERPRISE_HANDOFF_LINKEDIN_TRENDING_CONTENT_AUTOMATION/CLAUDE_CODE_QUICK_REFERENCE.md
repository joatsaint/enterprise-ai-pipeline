# CLAUDE_CODE_QUICK_REFERENCE.md

**For:** Claude Code building trending-post-generator  
**Read When:** Stuck, confused, or unsure about architecture  
**Length:** 5 minutes

---

## THE ONE-PAGE SUMMARY

You are adding a new feature to youtube-downloader **without breaking anything**.

**What:** Trending Post Generator — automatically finds trending IT topics, writes viral posts, (later) generates images, (later) schedules to LinkedIn.

**How:** New isolated command `trending generate` + new modules (trend_analyzer, image_generator, web_search) + security layer (vault, PII, audit).

**Why:** Automate daily LinkedIn posting with Randy's authentic voice + trending topics + GenX humor.

**When:** Phase 1 (Core): Finish by June 14. Phase 2 (Images): June 21. Phase 3 (Scheduling): June 28.

---

## DO's AND DON'Ts

### ✅ DO
- Add new files/modules (don't modify existing code)
- Use feature flags to disable TPG by default
- Log everything to audit trail
- Scan user input for PII before logging
- Use vault for credentials
- Test in dry-run mode first
- Commit incrementally (one feature per commit)
- Update SESSION_LOG_LATEST.md when done
- Ask before breaking existing tests

### ❌ DON'T
- Modify `cli.py` root except for 2 lines (add trending command)
- Change existing Buffer API integration
- Commit credentials to git
- Log raw PII (phone, SSN, email without masking)
- Use global variables for state
- Skip testing (100% coverage on new code)
- Deploy to production without dry-run
- Trust user input (validate everything)

---

## ARCHITECTURE (30-Second Version)

```
User Input (web search + reddit scanning)
    ↓
[NEW] TrendAnalyzer (score relevance to ICP)
    ↓
[EXISTING] Claude API (write post using voice system)
    ↓
[PHASE 2] ImageGenerator (DALL-E 3 or Gemini)
    ↓
[PHASE 3] Buffer Scheduler (post to LinkedIn)
    ↓
Audit Trail + Incident Logging (everything logged, encrypted)
```

**Key Principle:** Each step isolated. If image gen fails, post gen still works.

---

## INTEGRATION CHECKLIST

Before you start, verify nothing breaks:

```bash
# 1. Can you import existing modules?
python -c "from commands.schedule import *; print('✅')"
python -c "from integrations.buffer_api import *; print('✅')"
python -c "from generators.post_writer import *; print('✅')"

# 2. Do existing tests pass?
pytest tests/ -v --ignore=tests/test_trending* 2>&1 | tail -5

# 3. Is git clean?
git status  # Should show only your new files

# 4. Can you read the session log?
python -c "import json; open('SESSION_LOG_LATEST.md').read(); print('✅')"

# 5. Is vault accessible?
python -c "from security.vault import CredentialVault; print(CredentialVault().retrieve('ANTHROPIC_API_KEY')[:10])"
```

If any fail, STOP and fix before proceeding.

---

## CODE PATTERNS TO FOLLOW

### Pattern 1: Always Log to Audit Trail

```python
from security.audit_trail import ImmutableAuditLog

audit = ImmutableAuditLog()

audit.log_event(
    event_type='API_CALL',
    actor='claude-code',
    action='EXECUTE',
    resource='google_search',
    status='SUCCESS',
    metadata={'query': 'sysadmin AI automation', 'results': 5}
)
```

### Pattern 2: Scan for PII Before Logging

```python
from security.pii_scanner import PIIScanner

scanner = PIIScanner()
user_input = "Call me at 555-123-4567"

if scanner.is_safe_for_logging(user_input):
    audit_log_content = user_input
else:
    audit_log_content = scanner.mask(user_input)
    # Now: "Call me at [PHONE_REDACTED]"
```

### Pattern 3: Use Vault for Credentials

```python
from security.vault import CredentialVault

vault = CredentialVault()
api_key = vault.retrieve('ANTHROPIC_API_KEY')  # ✅ Do this

# ❌ Don't do this:
api_key = os.getenv('ANTHROPIC_API_KEY')  # Plain text
api_key = "sk-..."  # Hardcoded
```

### Pattern 4: Fail Gracefully with Incident Logging

```python
from learning.incident_tracker import IncidentTracker

tracker = IncidentTracker()

try:
    result = generate_post(topic)
except RateLimitError as e:
    tracker.log_failure(
        error_type='RateLimitError',
        message=str(e),
        context={'topic': topic, 'stage': 'post_generation'}
    )
    # Auto-recovery will kick in (RateLimiter + backoff)
    raise  # Let error propagate after logging
except Exception as e:
    tracker.log_failure(
        error_type=type(e).__name__,
        message=str(e),
        context={'topic': topic}
    )
    raise
```

### Pattern 5: Rate Limit Before API Calls

```python
from security.rate_limiter import RateLimiter

limiter = RateLimiter()

# Before calling OpenAI
limiter.consume('openai_dalle3', wait_if_needed=True)
image = openai.Image.create(...)

# If quota exhausted, automatically waits or fails gracefully
```

### Pattern 6: Use Feature Flags

```python
from config.feature_flags import get_flag

if get_flag('trending_post_generator.auto_publish_enabled'):
    publish_to_linkedin(post)
else:
    print(f"[DRY RUN] Would post: {post}")
```

---

## FILES YOU'LL MODIFY (Minimal)

### cli.py (Add 3 lines)
```python
# At the top, add:
import commands.trending as trending_cmd

# In the @click.group() / cli definition, add:
cli.add_command(trending_cmd.generate)

# That's it. Everything else stays untouched.
```

### No Other Existing Files Modified

Everything else (buffer_api.py, post_writer.py, etc.) stays exactly as is.

---

## NEW FILES YOU'LL CREATE

**Phase 1 (Core):**
- `commands/trending.py` — CLI entry point
- `generators/trend_analyzer.py` — score topics
- `integrations/web_search.py` — scan communities
- `security/rate_limiter.py` — quota protection
- `security/pii_scanner.py` — detect sensitive data
- `security/vault.py` — encrypt credentials
- `security/audit_trail.py` — immutable logs
- `learning/incident_tracker.py` — log failures
- `learning/self_healing.py` — auto-recovery rules
- `utils/health_check.py` — system diagnostics
- `tests/test_trending_integration.py` — unit tests
- `tests/test_security.py` — security tests
- `config/feature_flags.yaml` — toggles
- `config/vault_config.yaml` — vault settings
- `scripts/preflight_check.py` — pre-flight validation

**Phase 2 & 3:** Image generation, scheduling, etc. (future)

---

## TESTING (Do This First, Always)

### Unit Test Pattern

```python
# tests/test_trending_integration.py
import pytest
from commands.trending import generate
from generators.trend_analyzer import TrendAnalyzer

def test_trend_analyzer_scores_it_topics():
    analyzer = TrendAnalyzer()
    score = analyzer.score_topic("AI replacing sysadmins")
    assert score > 0.7  # High relevance to ICP
    
    score = analyzer.score_topic("Pokemon card prices")
    assert score < 0.3  # Low relevance to ICP

def test_generate_post_dry_run(capsys):
    result = generate(topic="Claude Code release", dry_run=True)
    assert 'dry_run' in result or result['status'] == 'DRY_RUN'
    assert 'post_text' in result
    assert result['post_text'] is not None
    
    captured = capsys.readouterr()
    assert 'BUFFER' not in captured.out  # No actual API call

@pytest.mark.security
def test_pii_scanner_detects_ssn():
    from security.pii_scanner import PIIScanner
    scanner = PIIScanner()
    findings = scanner.scan("My SSN is 123-45-6789")
    assert 'SSN' in findings
```

### Run Before Every Commit

```bash
pytest tests/test_trending_integration.py -v --cov=commands/trending --cov=generators
# Should see: 100% coverage, 0 skipped tests, all green
```

---

## COMMON ERRORS & FIXES

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'trending'` | trending.py doesn't exist or not imported in cli.py | Create file + add 3 lines to cli.py |
| `CredentialVault: KeyError` | Vault not initialized | Run `python scripts/init_vault.py` |
| `RateLimitError: 100 calls/hour` | No rate limiting before API call | Add `limiter.consume()` before call |
| `PII detected in logs` | Forgot to mask before logging | Use `PIIScanner.mask()` |
| `Audit log tampering detected` | Log file modified externally | Restore from backup: `git checkout logs/audit/` |
| `ImportError in test` | Circular import or missing __init__.py | Verify `__init__.py` exists in all dirs |
| `Git merge conflict` | Changing same file in main | Rebase: `git rebase main` |

---

## WHEN YOU'RE DONE (Phase 1)

1. ✅ All tests pass: `pytest tests/ -v`
2. ✅ Security scan passes: `bandit -r . --skip B101`
3. ✅ No credentials in git: `git diff --cached | grep -i secret` (returns nothing)
4. ✅ Dry-run works: `python cli.py trending generate --date today --dry-run`
5. ✅ Commit message clear: `git commit -m "Phase 1: trending post core (analyzer + web search)"`
6. ✅ Update SESSION_LOG_LATEST.md with status
7. ✅ Open PR (don't merge yet, wait for Randy's review)
8. ✅ Review INCIDENT_TRACKER.md (should still be empty)

---

## PHASE PROGRESSION

### Phase 1 (THIS PHASE) — Due June 14
- ✅ CLI command working (dry-run mode)
- ✅ Trend analyzer scoring topics
- ✅ Web search scanning communities
- ✅ Post text generation
- ✅ All tests green

### Phase 2 — Due June 21
- Image generation (DALL-E 3 / Gemini)
- GenX IT aesthetic applied
- Rate limiting working
- Image tests passing

### Phase 3 — Due June 28
- Buffer scheduling working
- Optimal time logic (10:05 AM Tuesday)
- Real posts to LinkedIn (with approval)
- Monitoring/alerts active

---

## EMERGENCY ESCAPE HATCHES

### If Something Breaks Everything

```bash
# Revert to last known good state
git checkout master
git pull
pip install -r requirements.txt
python scripts/restart_pipeline.sh

# Then: analyze what broke
git log --oneline -n 5
git diff master..feature/trending-post-gen --stat
```

### If Vault Corrupted

```bash
# Restore vault from backup
cp config/.vault.backup config/.vault
python scripts/verify_vault_integrity.py
```

### If You Need to Skip a Test

```bash
# Only with Randy's approval
@pytest.mark.skip(reason="Approved by Randy - Issue #XXX")
def test_something():
    ...

# Then: Document in INCIDENT_TRACKER.md
```

---

## SUCCESS LOOKS LIKE

When you run:
```bash
python cli.py trending generate --date "2026-06-07" --dry-run
```

You see:
```json
{
  "status": "dry_run_success",
  "topic": "Claude Code Agents: The Automation Wave",
  "relevance_score": 0.87,
  "post_text": "Claude Code just raised the bar on what... [full post]",
  "why_this_topic": "Gen X sysadmins worried about automation displacement",
  "published": false,
  "would_publish_time": "2026-06-11T10:05:00Z"
}
```

And NO API calls were made (dry-run = safe).

---

## QUESTIONS?

1. **Architecture question?** → Read TRENDING_POST_GENERATOR_HANDOFF.md Section 1
2. **Security question?** → Read Section 5 (HANDOFF)
3. **Test question?** → Read HANDOFF Section 2 (Pre-Flight)
4. **Stuck on error?** → Check INCIDENT_TRACKER.md for similar issues
5. **How to use vault?** → See "Pattern 3" above
6. **Need to debug?** → Run `python scripts/health_check.py --verbose`

---

**Print This Out.** Literally. Keep it next to your desk.

**Last Updated:** 2026-06-07T14:50:00Z  
**Version:** 1.0 (Phase 1)
