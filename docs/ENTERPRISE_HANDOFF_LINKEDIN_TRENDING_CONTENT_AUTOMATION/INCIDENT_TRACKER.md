# INCIDENT_TRACKER.md

**Purpose:** Self-healing knowledge base — what broke, how we fixed it, prevention for future  
**Updated:** Automatically when incidents occur + manual reviews  
**Last Updated:** 2026-06-07T14:45:00Z  
**Total Incidents Recorded:** 0  
**Auto-Recovery Success Rate:** N/A (first build phase)

---

## INCIDENT LOG STRUCTURE

Each incident follows this format. Claude Code reads this to understand what went wrong before.

```
### Incident #[N]: [ERROR_TYPE_IN_CAPS]

**Severity:** [CRITICAL|HIGH|MEDIUM|LOW|INFO]  
**Status:** [INVESTIGATING|RECOVERING|RECOVERED|RESOLVED|WONTFIX]  
**Date:** YYYY-MM-DDTHH:MM:SSZ  
**Affected System:** [trending-post-generator|image-generation|buffer-api|web-search|rate-limiter|vault|audit-trail]  
**Impact Duration:** X minutes  
**Auto-Recovered:** [YES|NO|PARTIAL]

#### Error Details
**Error Type:** [Python exception name, e.g. RateLimitError]  
**Error Message:** "[Exact error message from exception]"  
**Stack Trace:**
\`\`\`
[Full traceback]
\`\`\`

#### Timeline
- **14:32:00Z:** Error triggered
- **14:32:15Z:** Auto-detection fired
- **14:32:30Z:** Recovery attempt started
- **14:35:00Z:** Recovery completed / Manual intervention required

#### Context at Time of Failure
- **Operation:** [trending generate / image generation / buffer schedule / etc.]
- **Topic:** [if applicable]
- **Stage:** [which step failed]
- **Affected Data:** [what was being processed]
- **API Quota Status:** [X/Y calls used]
- **System Resources:** [CPU %, memory %, disk space]

#### Root Cause Analysis
**Primary Cause:** [What directly caused the failure]  
**Contributing Factors:** [Secondary issues that made it worse]  
**Why Not Caught Earlier:** [What should have prevented this]

#### Failure Cascade
Did this failure trigger other failures? Document the chain:
- Failure A triggered → Failure B triggered → Failure C

#### Automated Recovery Attempts
1. **Method 1:** [Description] — **Result:** [SUCCESS|FAILED|PARTIAL]
   - Reason (if failed): [Why it didn't work]
2. **Method 2:** [Description] — **Result:** [SUCCESS|FAILED|PARTIAL]

#### Manual Intervention (if needed)
**Action Taken:** [What someone did]  
**By:** [who, timestamp]  
**Result:** [outcome]

#### Fix Applied
**Code Changes:**
- File: [path]
  - Change: [before → after]
  - Commit: [git hash if merged]

**Config Changes:**
\`\`\`yaml
[What configuration changed]
\`\`\`

**Deployment:**
- Deployed to: [local test|staging|production]
- Deployed at: YYYY-MM-DDTHH:MM:SSZ
- Verified working: [YES|NO]

#### Learning & Prevention
**For Future Development:**
- [ ] [Action item]
- [ ] [Action item]
- [ ] [Action item]

**Pattern Recognized:** [If similar to past issues, note it]  
**New Rule Added to Self-Healing:** [If a new recovery rule was created]

#### Metrics
- **Time to Detection:** [X minutes]
- **Time to Recovery:** [X minutes / manual]
- **Financial Impact:** [$X if applicable]
- **Business Impact:** [description]
- **Data Loss:** [0 / details if any]
- **Users Affected:** [0 / how many]

#### Related Incidents
- #[N]: [if this cascaded from another issue]
- Linked to: [issue tracker URL if any]

#### Incident Closed
**Status:** RESOLVED / WONTFIX  
**Date Closed:** YYYY-MM-DDTHH:MM:SSZ  
**Closed By:** [who]  
**Closure Notes:** [final summary]

#### Follow-Up Actions
- [ ] PR #XXX: [description]
- [ ] Update [doc name]
- [ ] Schedule post-incident review
- [ ] Notify [stakeholder]
```

---

## CURRENT INCIDENTS (None Yet)

This project is in Phase 1 (pre-build). Incidents will be logged here as they occur.

---

## CRITICAL INCIDENT PATTERNS

Keep an eye out for these recurring issues:

### Pattern 1: Rate Limit Exhaustion
**Symptoms:** API calls start failing with "rate limit exceeded"  
**Root Cause:** Loop calling API without delay or quota checking  
**Prevention:** RateLimiter + circuit breaker before any API integration  
**Self-Healing Rule:** Exponential backoff + queue for retry

### Pattern 2: Credential Leakage
**Symptoms:** API key found in logs, error messages, or git history  
**Root Cause:** Logging secrets directly instead of using vault  
**Prevention:** PII scanner + audit trail + vault encryption  
**Self-Healing Rule:** Mask any detected credential, alert admin

### Pattern 3: Cascading Failures
**Symptoms:** One failure triggers multiple downstream failures  
**Root Cause:** Missing error boundaries between modules  
**Prevention:** Try/catch at module boundaries, fail gracefully  
**Self-Healing Rule:** Isolate failure, rollback to last known good state

### Pattern 4: Out of Memory / Disk
**Symptoms:** Process killed, no disk space for logs  
**Root Cause:** Unbounded data growth (cache, logs, images)  
**Prevention:** Cleanup jobs, retention policies, size limits  
**Self-Healing Rule:** Auto-cleanup old files, alert when 80% full

### Pattern 5: PII in Public Posts
**Symptoms:** Confidential data posted to LinkedIn accidentally  
**Root Cause:** User input not scanned before generating post  
**Prevention:** PII scanner on all user-generated content  
**Self-Healing Rule:** Block post, mask PII, alert admin

---

## TEMPLATE FOR LOGGING NEW INCIDENTS

When something breaks:

```bash
# 1. Claude Code detects error
try:
    result = generate_post(topic)
except Exception as e:
    # 2. Log incident automatically
    tracker.log_failure(
        error_type=type(e).__name__,
        message=str(e),
        traceback=traceback.format_exc(),
        context={
            'operation': 'generate_post',
            'topic': topic,
            'stage': 'image_generation',
        }
    )
    
    # 3. Attempt recovery
    recovery = self_healing.attempt_fix(e)
    
    # 4. Update incident tracker
    tracker.update_latest({
        'status': 'RECOVERED' if recovery['success'] else 'FAILED',
        'recovery_method': recovery['method'],
        'requires_manual_intervention': not recovery['success'],
    })
    
    # 5. If recovery failed, raise and alert
    if not recovery['success']:
        audit_logger.log_event(
            event_type='CRITICAL_ERROR',
            actor='claude-code',
            action='HALT',
            resource='trending-post-generator',
            status='FAILURE',
            metadata={
                'error_type': type(e).__name__,
                'recovery_attempted': recovery['method'],
                'requires_human_approval': True,
            }
        )
        raise
```

---

## RECOVERY METHODS (Self-Healing Toolkit)

### For API Quota Errors
```python
# RateLimiter automatically:
# 1. Detect rate limit error
# 2. Calculate backoff time
# 3. Queue for retry (exponential backoff, max 30s)
# 4. Resume operation
# Fallback: switch to alternate API (Gemini if DALL-E quota hit)
```

### For Credential Errors
```python
# CredentialVault automatically:
# 1. Detect auth failure
# 2. Reload credential from vault
# 3. Validate token (check expiry)
# 4. Refresh token if expired
# 5. Retry operation
```

### For PII Detection
```python
# PIIScanner + SafePost automatically:
# 1. Scan post for PII patterns
# 2. Alert admin if found
# 3. Mask sensitive data with [TYPE_REDACTED]
# 4. Log incident (HALT, not proceed)
# Requires: manual approval to post masked version
```

### For Vault Corruption
```python
# AuditTrail automatically:
# 1. Detect tampering (hash chain broken)
# 2. Restore from backup
# 3. Log incident (CRITICAL)
# 4. Trigger manual intervention
```

### For Out-of-Disk
```python
# LogRotation automatically:
# 1. Detect disk space < 10% free
# 2. Archive logs > 30 days to compressed backup
# 3. Delete image cache > 7 days old
# 4. Retry operation
# Alert: if cleanup doesn't free enough space
```

---

## METRICS TO TRACK

Claude Code automatically logs these metrics for each incident:

```json
{
  "incident_id": "INC_20260607_001",
  "timestamp": "2026-06-07T14:32:00Z",
  "error_type": "RateLimitError",
  "severity": "MEDIUM",
  "auto_recovery_attempted": true,
  "auto_recovery_succeeded": true,
  "time_to_detection_seconds": 15,
  "time_to_recovery_seconds": 45,
  "manual_intervention_required": false,
  "affected_resource": "openai_dalle3",
  "financial_impact_usd": 0,
  "business_impact_minutes": 0.75,
  "data_loss_records": 0,
  "users_affected": 0,
  "system_health_impact": "none"
}
```

---

## LEARNING LOOP

Each week, Claude Code reviews incidents:

1. **Pattern Detection:** Which errors are most common?
2. **Recovery Analysis:** Which self-healing methods work best?
3. **Prevention:** Can we catch this earlier?
4. **Knowledge Update:** Add new rules if pattern repeats

**Weekly Review Template:**
```markdown
## Week of June 7, 2026

**Incidents This Week:** [N]  
**Auto-Recovery Success Rate:** [X%]  
**Most Common Error:** [type]  
**Fastest Recovery Time:** [method]  
**Slowest Recovery Time:** [method]  

**New Patterns Discovered:**
- [ ] Pattern A (if any)
- [ ] Pattern B (if any)

**Recommended Changes:**
- [ ] Tighten rate limit from X to Y
- [ ] Add new PII pattern
- [ ] Upgrade fallback logic
```

---

## ESCALATION POLICY

### INFO (Low Priority)
- Degraded performance, minor errors auto-recovered
- Log only, no alert

### MEDIUM (Medium Priority)  
- Error recovered manually or after retry
- Health check warning (80% quota, 90% disk)
- Alert: none, logged in incident tracker

### HIGH (High Priority)
- Error not auto-recovered, manual intervention needed
- Critical system affected (credentials, audit trail)
- Alert: Slack/email to Randy within 1 hour

### CRITICAL (Immediate)
- Cascade failures, data loss possible
- PII leaked or at risk
- Vault corruption, audit trail tampered
- Alert: immediate SMS to Randy + page on-call

---

## COMMUNICATION TEMPLATES

### Alert to Randy (HIGH)
```
⚠️ HIGH PRIORITY INCIDENT

System: [trending-post-generator]  
Error: [error type]  
Status: [FAILED|MANUAL INTERVENTION NEEDED]  
Details: [one-line summary]  

Next Step: Review INCIDENT_TRACKER.md #[N]  
Action Needed: [approval|investigation|restart]  
```

### Alert to Randy (CRITICAL)
```
🚨 CRITICAL INCIDENT - IMMEDIATE ACTION REQUIRED

System: [system name]  
Error: [error type]  
Impact: [data loss / breach risk / cascade failure]  
Status: [HALTED]

STOP - Do not proceed until manual approval.  
Details: INCIDENT_TRACKER.md #[N]
Command to investigate: python scripts/health_check.py --verbose
```

---

## MONTHLY REVIEW

Every month, compile report:

```markdown
## Incident Report: June 2026

**Total Incidents:** [N]  
**Auto-Recovered:** [X] (Y%)  
**Manual Interventions:** [Z]  
**Data Loss Events:** [0]  
**Security Events:** [0]  

**Cost Impact:** $X (API overages, if any)  
**Uptime:** 99.X%  

**Top 3 Issues:**
1. [Issue] - [N occurrences]
2. [Issue] - [N occurrences]
3. [Issue] - [N occurrences]

**Improvements Made:**
- [ ] Fix for issue 1
- [ ] Fix for issue 2
- [ ] Fix for issue 3

**Recommendations for July:**
- [ ] Upgrade [component]
- [ ] Add monitoring for [metric]
- [ ] Increase quota for [API]
```

---

## INCIDENT CLOSURE CRITERIA

An incident is RESOLVED when:

1. ✅ Root cause identified and documented
2. ✅ Fix applied and verified (dry-run + real test)
3. ✅ Same error doesn't recur for 7 days
4. ✅ Self-healing rule added (if applicable)
5. ✅ Documentation updated
6. ✅ Incident closed in tracker

An incident is WONTFIX when:

1. ✅ Root cause understood but unfixable (e.g., external API limitation)
2. ✅ Workaround implemented (fallback, manual process, etc.)
3. ✅ Risk accepted (documented in decision)
4. ✅ Monitoring alerts in place to prevent cascade
5. ✅ Stakeholder approval obtained

---

## REFERENCES

- **Self-Healing Code:** `learning/self_healing.py`
- **Rate Limiter:** `security/rate_limiter.py`
- **PII Scanner:** `security/pii_scanner.py`
- **Vault:** `security/vault.py`
- **Audit Trail:** `security/audit_trail.py`
- **Health Check:** `utils/health_check.py`

---

**Generated:** 2026-06-07T14:45:00Z  
**Auto-Updated:** When incidents occur  
**Manual Review:** Weekly (Friday EOD)
