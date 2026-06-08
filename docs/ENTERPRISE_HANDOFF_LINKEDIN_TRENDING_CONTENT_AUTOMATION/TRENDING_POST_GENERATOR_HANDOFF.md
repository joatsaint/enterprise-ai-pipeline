# TRENDING POST GENERATOR — ENTERPRISE INTEGRATION HANDOFF

**Project Name:** `trending-post-generator` (TPG)  
**Parent Project:** `youtube-downloader` (enterprise-ai-pipeline)  
**Owner:** Randy Skiles (joatsaint)  
**Date Created:** June 7, 2026  
**Classification:** INTERNAL CONFIDENTIAL (handles credential data, business logic)  
**Last Updated:** [AUTOMATED ON EACH CLAUDE CODE SESSION]  
**Status:** READY FOR CLAUDE CODE BUILD (Phase 1: Core Architecture)

---

## EXECUTIVE SUMMARY

This document is the **single source of truth** for integrating a trending-post-generator into youtube-downloader without breaking existing systems. It includes:

1. **Architecture & Integration Blueprint** — how TPG fits into the existing stack
2. **Pre-Flight Checklist** — verification gates before code execution
3. **Change Management Protocol** — staged rollout with rollback capability
4. **Self-Healing Framework** — automatic issue detection, logging, and recovery
5. **Security & Confidentiality Controls** — enterprise-grade data protection
6. **Session Log Template** — what Claude Code must load every run
7. **Incident Tracking System** — learning loop for future updates
8. **Enterprise Compliance Requirements** — for banking, healthcare, government, insurance

---

## SECTION 1: ARCHITECTURE & INTEGRATION

### 1.1 Project Structure (Updated)

```
youtube-downloader/
├── cli.py                                  ← ROOT COMMAND (EXISTING, DO NOT MODIFY)
│
├── commands/
│   ├── __init__.py
│   ├── video.py                            ← EXISTING: single video processing
│   ├── research.py                         ← EXISTING: ask, analyze, digest
│   ├── schedule.py                         ← EXISTING: schedule-post to Buffer
│   └── trending.py                         ← NEW: trending-post-generator logic
│
├── generators/
│   ├── __init__.py
│   ├── post_writer.py                      ← EXISTING: Claude-based post generation
│   ├── image_generator.py                  ← NEW: DALL-E 3 / Gemini image gen
│   └── trend_analyzer.py                   ← NEW: news/community topic scoring
│
├── integrations/
│   ├── __init__.py
│   ├── buffer_api.py                       ← EXISTING: Buffer scheduling
│   ├── claude_api.py                       ← EXISTING: Claude API calls
│   ├── web_search.py                       ← NEW: Google/SearxNG web search
│   └── linkedin_api.py                     ← EXISTING: LinkedIn credential management
│
├── utils/
│   ├── __init__.py
│   ├── tokenizer.py                        ← EXISTING: token counting
│   ├── markdown_renderer.py                ← EXISTING: Markdown formatting
│   ├── encryption.py                       ← NEW: credential encryption/decryption
│   ├── audit_logger.py                     ← NEW: enterprise-grade event logging
│   └── health_check.py                     ← NEW: system integrity verification
│
├── security/
│   ├── __init__.py
│   ├── vault.py                            ← NEW: encrypted credential store
│   ├── pii_scanner.py                      ← NEW: detect & mask PII before logging/output
│   ├── audit_trail.py                      ← NEW: immutable event log
│   └── rate_limiter.py                     ← NEW: API quota management
│
├── learning/
│   ├── __init__.py
│   ├── incident_tracker.py                 ← NEW: logs failures + fixes
│   ├── self_healing.py                     ← NEW: automatic remediation rules
│   ├── performance_metrics.py              ← NEW: tracks execution times, error rates
│   └── knowledge_base.py                   ← NEW: learns from patterns
│
├── tests/
│   ├── __init__.py
│   ├── test_trending_integration.py        ← NEW: integration tests (PRE-FLIGHT)
│   ├── test_security.py                    ← NEW: security verification
│   ├── test_image_generation.py            ← NEW: image output validation
│   └── test_buffer_scheduling.py           ← NEW: mock Buffer API tests
│
├── config/
│   ├── __init__.py
│   ├── settings.py                         ← EXISTING: app configuration
│   ├── vault_config.yaml                   ← NEW: credential store paths (ENCRYPTED)
│   ├── feature_flags.yaml                  ← NEW: feature toggles for gradual rollout
│   └── pii_patterns.yaml                   ← NEW: regex patterns for sensitive data
│
├── logs/
│   ├── .gitignore                          ← NEW: never commit logs
│   ├── audit/                              ← NEW: immutable audit logs (one per day)
│   │   └── audit_YYYY-MM-DD.jsonl         ← structured, encrypted event log
│   ├── incidents/                          ← NEW: incident tracking
│   │   └── incident_tracker.jsonl         ← learning log for failures & fixes
│   ├── health/                             ← NEW: system health metrics
│   │   └── health_check_YYYY-MM-DD.json   ← daily health snapshot
│   └── session/                            ← NEW: Claude Code session logs
│       └── SESSION_LOG_LATEST.md           ← current session state
│
├── docs/
│   ├── CLAUDE.md                           ← EXISTING: project brain (updated below)
│   ├── TRENDING_POST_GENERATOR.md          ← NEW: detailed feature spec
│   ├── SECURITY_COMPLIANCE.md              ← NEW: enterprise compliance checklist
│   ├── INCIDENT_RESPONSE_GUIDE.md          ← NEW: how to respond to failures
│   └── DEPLOYMENT_RUNBOOK.md               ← NEW: step-by-step deployment
│
├── data/
│   ├── communities.json                    ← EXISTING: channel registry
│   ├── trending_sources.json               ← NEW: RSS feeds, Reddit subs, news APIs
│   ├── post_queue.jsonl                    ← NEW: scheduled posts awaiting execution
│   └── image_cache/                        ← NEW: generated images (1-week retention)
│
├── scripts/
│   ├── run_pipeline.bat                    ← EXISTING: Windows Task Scheduler entry
│   ├── trending_post_daily.bat             ← NEW: daily trending post generator
│   ├── health_check_hourly.bat             ← NEW: hourly system health check
│   ├── incident_report.ps1                 ← NEW: email incident reports to admin
│   └── cleanup_old_logs.py                 ← NEW: archive logs > 30 days (GDPR)
│
├── SESSION_LOG_LATEST.md                   ← NEW: Claude Code reads this at startup
├── CLAUDE.md                               ← UPDATED: points to sections below
├── INCIDENT_TRACKER.md                     ← NEW: latest failures + fixes
├── HEALTH_REPORT_LATEST.json               ← NEW: current system status
└── README.md                               ← UPDATED: includes TPG

```

### 1.2 Integration Points (No Breaking Changes)

**MUST PRESERVE:**
- ✅ `cli.py` root command dispatcher — only ADD new `trending` command, don't modify existing
- ✅ `commands/schedule.py` — Buffer API integration stays unchanged
- ✅ `commands/research.py` — `ask` / `analyze` / `digest` commands untouched
- ✅ Existing credential management (oauth tokens, API keys) — add encryption layer on top
- ✅ `run_pipeline.bat` — existing video pipeline runs independently
- ✅ Logging directory structure — add new `logs/` subdirs, don't modify existing

**NEW COMPONENTS (Isolated):**
- `commands/trending.py` — new CLI command
- `generators/trend_analyzer.py` + `image_generator.py` — new modules
- `integrations/web_search.py` — new search capability
- `security/` + `learning/` dirs — zero impact on existing code
- `logs/` subdirs — isolated from existing logs
- `scripts/trending_post_daily.bat` — new Task Scheduler job, doesn't interfere

**INTEGRATION PATTERN:**
```python
# In cli.py (ONLY MODIFICATION: add 2 lines)
import commands.trending as trending_cmd

@click.group()
def cli():
    pass

cli.add_command(trending_cmd.generate)  # ← ADD THIS
# ... existing commands below, untouched
```

---

## SECTION 2: PRE-FLIGHT CHECKLIST (Verification Gates)

### 2.1 Before Claude Code Writes Any Code

**Gate 1: Environment Validation**
```bash
# Run this FIRST (manual, before coding starts)
python scripts/preflight_check.py --strict
```

Expected output:
```
✅ Python 3.11+ detected
✅ Required dependencies installed (anthropic, httpx, python-dotenv)
✅ .env file exists with REQUIRED keys:
   - ANTHROPIC_API_KEY
   - BUFFER_API_TOKEN
   - OPENAI_API_KEY (for image generation)
   - LINKEDIN_ACCOUNT_ID
✅ /logs directory writable and initialized
✅ Existing youtube-downloader imports validate (no syntax errors)
✅ Git repository clean (no uncommitted changes in core modules)
⚠️  WARNING: Current branch is 'main' — switching to feature branch is REQUIRED
```

**Gate 2: Dependency Lock**
```bash
# Create exact version snapshot (commit to repo)
pip freeze > requirements-tpg.txt
```

If any existing dependency conflicts, pause and document the resolution.

**Gate 3: Existing System Smoke Test**
```bash
# Run existing commands to ensure nothing broke
python cli.py channel "ai-and-claude-code" --dry-run  # existing code path
python cli.py ask "test query" --fast                  # existing code path
python cli.py schedule-post --dry-run --post 1         # existing code path
```

All must pass with zero errors.

### 2.2 Before Claude Code Deploys TPG

**Gate 4: Unit Test Suite**
```bash
pytest tests/test_trending_integration.py -v --cov=commands/trending --cov=generators
```

Must achieve:
- ✅ 100% code coverage on new modules
- ✅ 0 skipped tests
- ✅ All security tests pass (see 2.3)
- ✅ No warnings from linters (pylint, flake8)

**Gate 5: Security Scan**
```bash
# Static security analysis
bandit -r commands/trending.py generators/ security/ --skip B101

# Credential leak detection
git diff --cached | grep -E "(api_key|token|password|secret)" && exit 1 || echo "✅ No credentials in diff"

# PII in logs check
python scripts/pii_scanner.py --check-recent-logs
```

**Gate 6: Integration Test (With Real APIs, but Dry-Run)**
```bash
python cli.py trending generate \
  --date "2026-06-07" \
  --dry-run \
  --simulate-buffer \
  --simulate-image-gen
```

Expected output: JSON showing what WOULD be posted, but no actual API calls made.

**Gate 7: Load Existing Session Log**
```bash
# Claude Code MUST read and validate the session log
python -c "from learning.session_loader import SessionLoader; s = SessionLoader(); s.load_latest(); print(s.validate())"
```

If session log is corrupted, auto-recover from backup.

---

## SECTION 3: CHANGE MANAGEMENT PROTOCOL

### 3.1 Staged Deployment (No Big-Bang)

**Phase 1: Local Development** (Claude Code, your Windows PC)
- Builds trending.py, trend_analyzer.py, image_generator.py
- All tests pass locally
- Runs against test Buffer account
- Runs against mock image API (no actual DALL-E calls yet)
- Commits to feature branch `feature/trending-post-gen`
- PR created, ready for manual review

**Phase 2: Integration Testing** (Your approval)
- You review code + PR
- Claude Code runs against REAL Buffer test workspace (not production)
- Claude Code generates 3 test posts (actually scheduled to Buffer test account)
- You manually verify posts look correct on LinkedIn test account
- Approval given via PR merge

**Phase 3: Canary Deployment** (Low-Risk)
- Claude Code schedules 1 real post per day to actual LinkedIn (with your pre-approval)
- Monitoring enabled (see Section 4.2)
- Run for 7 days, track engagement metrics
- If issues appear, automatically rollback (see 3.3)

**Phase 4: Full Deployment** (Business-As-Usual)
- Enables daily/hourly posting schedule
- Full automation without manual intervention
- Incident response active

### 3.2 Rollback Capability (Always)

**If anything breaks:**

```bash
# Automatic rollback (triggered by health check failure)
git checkout master
pip install -r requirements.txt  # restore old versions
python scripts/restart_pipeline.sh  # restart existing system
python logs/generate_incident_report.py --severity CRITICAL
```

**Manual rollback (your choice):**
```bash
# Full revert to last known good state
git revert <commit-hash>
# or
git checkout <previous-branch>
```

**The guarantee:** Any failure in TPG CANNOT cascade to youtube-downloader core. TPG runs in isolated process, fails gracefully, logs everything, alerts you.

### 3.3 Feature Flags (Gradual Rollout)

```yaml
# config/feature_flags.yaml
trending_post_generator:
  enabled: false                    # Start false
  schedule_enabled: false
  auto_publish_enabled: false
  image_generation_enabled: false
  daily_limit: 1                    # Start with 1 post/day max
  
incident_tracking:
  enabled: true                     # Always on
  auto_remediation: false           # Start disabled

self_healing:
  enabled: true
  auto_fix_enabled: false           # Manual approval first
```

**Progression:**
- Day 1: `enabled: true, auto_publish_enabled: false` (dry-run mode)
- Day 3: Add `image_generation_enabled: true` (images only, no posts)
- Day 7: Add `auto_publish_enabled: true` (1 post/day)
- Day 14: `daily_limit: 3`
- Day 30: `daily_limit: 0` (hourly, unlimited)

---

## SECTION 4: SELF-HEALING FRAMEWORK

### 4.1 Automatic Failure Detection

Claude Code MUST run a health check before and after every operation:

```python
# In trending.py
from security.audit_logger import AuditLogger
from learning.incident_tracker import IncidentTracker
from utils.health_check import HealthCheck

class TrendingPostGenerator:
    def __init__(self):
        self.health = HealthCheck()
        self.audit = AuditLogger()
        self.incidents = IncidentTracker()
    
    def generate(self, topic, dry_run=False):
        # PRE-FLIGHT CHECK
        self.health.pre_flight()  # validates all dependencies
        
        try:
            post_content = self.write_post(topic)
            image_url = self.generate_image(post_content)
            
            if not dry_run:
                result = self.schedule_to_buffer(post_content, image_url)
            
            # LOG SUCCESS
            self.audit.log_success(
                operation="generate_post",
                topic=topic,
                post_id=result.get('id'),
                metadata={'image_size': len(image_url)}
            )
            
            return result
            
        except Exception as e:
            # LOG FAILURE
            self.incidents.log_failure(
                error_type=type(e).__name__,
                message=str(e),
                traceback=traceback.format_exc(),
                attempted_recovery=None
            )
            
            # ATTEMPT AUTO-RECOVERY
            recovery = self.self_healing.attempt_fix(e, context={
                'topic': topic,
                'stage': 'post_generation'
            })
            
            if recovery['success']:
                self.incidents.update_latest({
                    'status': 'RECOVERED',
                    'recovery_method': recovery['method']
                })
                return self.generate(topic, dry_run)  # retry
            else:
                self.incidents.update_latest({
                    'status': 'FAILED',
                    'requires_manual_intervention': True
                })
                raise
```

### 4.2 Incident Tracking & Learning

**Every failure is logged to `INCIDENT_TRACKER.md`:**

```yaml
Incident: API_RATE_LIMIT_EXCEEDED
Date: 2026-06-07T14:32:00Z
Severity: WARNING
Error: "Rate limit exceeded: 100 requests/hour"
Context:
  Operation: image_generation
  Stage: dalle3_call
  Attempted: 45 images in 30 minutes
  Expected_limit: 100/hour

Root Cause: Image generation loop had no delay between requests

Fix Applied: auto
  Method: exponential_backoff_with_jitter
  Backoff_start: 100ms
  Backoff_max: 5s
  
Recovery Result: SUCCESS (resumed after 15-second pause)

Learning:
  - Implement request queue with rate limiting BEFORE image generation
  - Add circuit breaker for API limits (fast-fail if approaching 90%)
  - Monitor request rates per integration in real-time

Future Prevention:
  - Add RateLimiter to image_generator.py
  - Update health_check to warn at 75% quota usage
  - Add AlertPolicy: send email if quota > 80%
```

**Claude Code reads this on startup:**

```python
from learning.incident_tracker import IncidentTracker

tracker = IncidentTracker()
recent_incidents = tracker.get_unresolved()

for incident in recent_incidents:
    if incident['status'] == 'FAILED' and incident['requires_manual_intervention']:
        print(f"⚠️  UNRESOLVED INCIDENT: {incident['error_type']}")
        print(f"   {incident['message']}")
        print(f"   Action: Check INCIDENT_TRACKER.md for context")
        sys.exit(1)  # fail loud, alert admin
```

### 4.3 Self-Healing Rules Engine

```python
# In learning/self_healing.py

HEALING_RULES = {
    'OpenAIRateLimitError': {
        'trigger': 'error_type == "OpenAIRateLimitError"',
        'actions': [
            'wait(5 * random.random())',  # jitter
            'exponential_backoff(max=30s)',
            'switch_to_gemini_api()',       # fallback
            'retry_operation()',
        ],
        'auto_execute': True,
        'requires_approval': ['switch_to_gemini_api'],
    },
    'Buffer_InvalidCredential': {
        'trigger': 'error_type == "Buffer_InvalidCredential"',
        'actions': [
            'reload_credentials_from_vault()',
            'validate_oauth_token()',
            'refresh_oauth_token()',
            'retry_operation()',
        ],
        'auto_execute': True,
        'requires_approval': [],
    },
    'PII_DetectedInPost': {
        'trigger': 'pii_scanner.found_pii(post_content)',
        'actions': [
            'halt_operation()',
            'mask_pii(post_content)',
            'alert_admin()',
            'log_incident(severity=HIGH)',
        ],
        'auto_execute': False,  # manual approval required
        'requires_approval': ['continue_or_abandon'],
    },
}
```

---

## SECTION 5: SECURITY & CONFIDENTIALITY CONTROLS

### 5.1 Credential Encryption (Vault Pattern)

**Problem:** Credentials in code or plain-text config files = data breach.

**Solution:** Encrypted vault with AES-256 encryption.

```python
# In security/vault.py

from cryptography.fernet import Fernet
import os
import json

class CredentialVault:
    def __init__(self):
        # Key stored in environment, never in code
        self.key = os.getenv('VAULT_ENCRYPTION_KEY')
        if not self.key:
            raise ValueError("VAULT_ENCRYPTION_KEY not set in .env")
        self.cipher = Fernet(self.key)
    
    def store(self, credential_name: str, value: str):
        """Encrypt and store a credential."""
        encrypted = self.cipher.encrypt(value.encode())
        vault_path = Path('config/.vault') / f'{credential_name}.enc'
        vault_path.write_bytes(encrypted)
        self.audit_log(f"Credential stored: {credential_name}")
    
    def retrieve(self, credential_name: str) -> str:
        """Decrypt and retrieve a credential."""
        vault_path = Path('config/.vault') / f'{credential_name}.enc'
        if not vault_path.exists():
            raise KeyError(f"Credential not found: {credential_name}")
        encrypted = vault_path.read_bytes()
        decrypted = self.cipher.decrypt(encrypted).decode()
        self.audit_log(f"Credential accessed: {credential_name}")
        return decrypted
    
    def audit_log(self, event: str):
        """Log all vault access to immutable audit trail."""
        # See Section 5.3 below
```

**Setup (one-time):**
```bash
# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Output: <copy this into .env as VAULT_ENCRYPTION_KEY>

# Initialize vault
python scripts/init_vault.py
# Interactively stores: BUFFER_API_TOKEN, OPENAI_API_KEY, LINKEDIN_OAUTH, etc.
```

### 5.2 PII (Personally Identifiable Information) Scanner

**Problem:** Confidential data (phone numbers, SSNs, credit card numbers) accidentally logged or posted.

**Solution:** Regex-based scanner before any output/logging.

```python
# In security/pii_scanner.py

import re

PII_PATTERNS = {
    'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
    'CREDIT_CARD': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
    'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'PHONE': r'\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
    'DOB': r'\b(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/\d{4}\b',
    'MEDICAL_ID': r'\b(MRN|Medical Record)[\s:]*(\d{6,10})\b',
    'BANK_ACCOUNT': r'\b(Account|Acct)[\s:]*(\d{8,17})\b',
}

class PIIScanner:
    def scan(self, text: str) -> dict:
        """Scan text for PII patterns."""
        findings = {}
        for pii_type, pattern in PII_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                findings[pii_type] = matches
        return findings
    
    def mask(self, text: str) -> str:
        """Replace PII with placeholder."""
        for pii_type, pattern in PII_PATTERNS.items():
            text = re.sub(pattern, f'[{pii_type}_REDACTED]', text, flags=re.IGNORECASE)
        return text
    
    def is_safe_for_logging(self, text: str) -> bool:
        """Return True if no PII found."""
        return len(self.scan(text)) == 0
```

**Usage:**
```python
# Before logging any user input or post content
from security.pii_scanner import PIIScanner

scanner = PIIScanner()
post_content = "Dr. Smith's patient (SSN 123-45-6789) was admitted..."

if not scanner.is_safe_for_logging(post_content):
    audit_log_content = scanner.mask(post_content)
    # Now logs: "Dr. Smith's patient (SSN [SSN_REDACTED]) was admitted..."
else:
    audit_log_content = post_content
```

### 5.3 Immutable Audit Trail

**Problem:** Logs deleted, modified, or lost = no accountability. Compliance requires audit trail.

**Solution:** Write-once, append-only audit logs.

```python
# In security/audit_trail.py

from pathlib import Path
from datetime import datetime
import json
import hashlib

class ImmutableAuditLog:
    def __init__(self):
        self.log_dir = Path('logs/audit')
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_log = self.log_dir / f'audit_{datetime.now().strftime("%Y-%m-%d")}.jsonl'
    
    def log_event(self, event_type: str, actor: str, action: str, resource: str, 
                  status: str, metadata: dict = None, pii_masked: bool = False):
        """
        Append event to immutable audit log.
        
        Args:
            event_type: 'API_CALL', 'CREDENTIAL_ACCESS', 'POST_PUBLISH', 'ERROR', etc.
            actor: 'claude-code', 'user-randy', 'system', etc.
            action: 'READ', 'WRITE', 'DELETE', 'EXECUTE', etc.
            resource: 'trending_post:123', 'buffer_api', 'image_generator', etc.
            status: 'SUCCESS', 'FAILURE', 'PARTIAL', etc.
            metadata: additional context (never include raw PII)
            pii_masked: whether sensitive data was redacted
        """
        
        event = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': event_type,
            'actor': actor,
            'action': action,
            'resource': resource,
            'status': status,
            'metadata': metadata or {},
            'pii_masked': pii_masked,
        }
        
        # Calculate hash of previous line for chain integrity
        previous_hash = self._get_last_hash()
        event['previous_hash'] = previous_hash
        event['event_hash'] = hashlib.sha256(
            json.dumps(event, sort_keys=True).encode()
        ).hexdigest()
        
        # Append (never overwrite)
        with open(self.current_log, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        # Make immutable (remove write permissions)
        os.chmod(self.current_log, 0o444)
    
    def _get_last_hash(self) -> str:
        """Get hash of last logged event for chain integrity."""
        if not self.current_log.exists():
            return '0' * 64
        
        lines = self.current_log.read_text().strip().split('\n')
        if not lines:
            return '0' * 64
        
        last_event = json.loads(lines[-1])
        return last_event.get('event_hash', '0' * 64)
    
    def verify_integrity(self) -> bool:
        """Verify audit log has not been tampered with."""
        if not self.current_log.exists():
            return True
        
        lines = self.current_log.read_text().strip().split('\n')
        previous_hash = '0' * 64
        
        for line in lines:
            event = json.loads(line)
            
            # Verify chain
            if event['previous_hash'] != previous_hash:
                return False
            
            # Verify event hash
            stored_hash = event.pop('event_hash')
            calculated_hash = hashlib.sha256(
                json.dumps(event, sort_keys=True).encode()
            ).hexdigest()
            
            if stored_hash != calculated_hash:
                return False
            
            previous_hash = stored_hash
        
        return True
```

**Usage:**
```python
from security.audit_trail import ImmutableAuditLog

audit = ImmutableAuditLog()

# Log API call
audit.log_event(
    event_type='API_CALL',
    actor='claude-code',
    action='EXECUTE',
    resource='openai_dalle3',
    status='SUCCESS',
    metadata={
        'model': 'dall-e-3',
        'prompt_tokens': 87,
        'image_size': '1024x1024',
    },
    pii_masked=False  # no PII in metadata
)

# Log credential access (PII masked)
audit.log_event(
    event_type='CREDENTIAL_ACCESS',
    actor='claude-code',
    action='READ',
    resource='vault:BUFFER_API_TOKEN',
    status='SUCCESS',
    metadata={
        'token_expires': '2026-07-07',
        # token value NEVER in metadata
    },
    pii_masked=True
)

# Verify log integrity (daily check)
if not audit.verify_integrity():
    raise SecurityError("Audit log tampering detected!")
```

### 5.4 Rate Limiting (Quota Protection)

**Problem:** Runaway loops drain API quotas, cost money, trigger suspensions.

**Solution:** Request queuing with per-service rate limits.

```python
# In security/rate_limiter.py

from datetime import datetime, timedelta
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self):
        self.limits = {
            'openai_dalle3': {'calls_per_hour': 100, 'calls_per_day': 500},
            'openai_gpt4': {'calls_per_hour': 200, 'calls_per_minute': 3},
            'buffer_api': {'calls_per_hour': 60, 'calls_per_day': 1000},
            'google_search': {'calls_per_day': 100},
        }
        self.request_history = defaultdict(list)
    
    def can_request(self, service: str) -> bool:
        """Check if request is allowed under current limits."""
        if service not in self.limits:
            return True  # unknown service, allow
        
        now = datetime.utcnow()
        limits = self.limits[service]
        history = self.request_history[service]
        
        # Prune old requests
        history[:] = [t for t in history if now - t < timedelta(hours=24)]
        
        # Check hourly limit
        if 'calls_per_hour' in limits:
            hour_ago = now - timedelta(hours=1)
            recent = [t for t in history if t > hour_ago]
            if len(recent) >= limits['calls_per_hour']:
                return False
        
        # Check daily limit
        if 'calls_per_day' in limits:
            if len(history) >= limits['calls_per_day']:
                return False
        
        return True
    
    def get_wait_time(self, service: str) -> float:
        """Get seconds to wait before next request is allowed."""
        if self.can_request(service):
            return 0
        
        now = datetime.utcnow()
        history = self.request_history[service]
        
        if 'calls_per_hour' in self.limits[service]:
            hour_ago = now - timedelta(hours=1)
            oldest_in_window = min(t for t in history if t > hour_ago)
            return (oldest_in_window + timedelta(hours=1) - now).total_seconds()
        
        return 60  # default: wait 1 minute
    
    def consume(self, service: str, wait_if_needed: bool = True):
        """Log a request. Optionally wait until allowed."""
        while not self.can_request(service):
            if not wait_if_needed:
                raise RateLimitExceeded(f"Rate limit exceeded for {service}")
            wait_time = self.get_wait_time(service)
            time.sleep(wait_time + 0.1)
        
        self.request_history[service].append(datetime.utcnow())
        return True
```

**Usage:**
```python
from security.rate_limiter import RateLimiter

limiter = RateLimiter()

# Before making OpenAI API call
limiter.consume('openai_dalle3', wait_if_needed=True)
image = openai.Image.create(prompt="...", model="dall-e-3")

# If quota exhausted, wait automatically
# Or fail fast: limiter.consume('openai_dalle3', wait_if_needed=False)
```

### 5.5 Compliance Checklist (Enterprise)

For **Banking, Insurance, Healthcare, Government**:

```yaml
# config/compliance_checklist.yaml

Data_Protection:
  - ✅ All credentials encrypted (AES-256)
  - ✅ PII scanning before logging
  - ✅ Immutable audit trail (write-once logs)
  - ✅ Log retention policy (7 years for healthcare, 6 years for financial)
  - ✅ Log encryption at rest
  - ✅ Secure credential deletion (wipe memory before exit)

Access_Control:
  - ✅ Vault access logging
  - ✅ Read-only audit logs
  - ✅ API key rotation (every 90 days)
  - ✅ No hardcoded secrets
  - ✅ Service account isolation (Claude Code has minimal permissions)

Incident_Response:
  - ✅ Automated incident logging
  - ✅ Alert on security events (PII detected, rate limit hit, auth failure)
  - ✅ Fallback to safe-mode on critical errors
  - ✅ Post-incident review (learning loop)
  - ✅ Breach notification capability

Audit_&_Compliance:
  - ✅ All API calls logged with timestamp, actor, resource, status
  - ✅ Chain-of-custody for generated posts (who created, when, changes)
  - ✅ Regulatory reports: daily summary for compliance team
  - ✅ Change tracking: version control + audit log
  - ✅ Annual security audit (penetration testing)

Data_Handling:
  - ✅ Minimize data in transit (HTTPS only)
  - ✅ No unnecessary logging of user input
  - ✅ Data classification (internal, confidential, public)
  - ✅ Retention limits (delete generated images > 1 week)
  - ✅ GDPR-compliant: right to deletion, data export

Operations:
  - ✅ Health checks hourly
  - ✅ Backup of configuration (encrypted)
  - ✅ Disaster recovery plan (restore from last known good state)
  - ✅ Monitoring alerts (OpsGenie, PagerDuty integration)
  - ✅ Change control (feature flags, staged rollout)
```

---

## SECTION 6: SESSION LOG TEMPLATE (Claude Code Loads This)

**File:** `SESSION_LOG_LATEST.md`  
**Updated:** On every Claude Code session start  
**Purpose:** Single-file context for Claude Code about project state

```markdown
# SESSION LOG — LATEST STATUS

**Session Start:** 2026-06-07T14:30:00Z  
**Claude Code Version:** 1.14.3  
**Project Branch:** feature/trending-post-gen  
**Status:** READY_FOR_BUILD

---

## PROJECT STATE SNAPSHOT

### Operational Systems (DO NOT TOUCH)
- ✅ youtube-downloader core: operational
- ✅ Buffer integration: working (tested 2026-06-05)
- ✅ Claude API integration: working
- ✅ Existing CLI commands: all functional
- ✅ Task Scheduler jobs: youtube-downloader runs daily at 08:00

### New Systems (UNDER CONSTRUCTION)
- 🔨 trending-post-generator: Phase 1 (architecture)
- ⏸️ Image generation: queued
- ⏸️ Incident tracking: queued

---

## CRITICAL CONTEXT FOR THIS SESSION

### What You're Building
Command: `python cli.py trending generate --date "2026-06-07"`

This command will:
1. Scan trending topics from r/sysadmin, r/ITCareerQuestions, The Register
2. Score relevance to IT operator ICP
3. Generate post using Claude + Randy's voice system
4. Generate GenX humor image (DALL-E 3 or Gemini)
5. Schedule to Buffer at 10:05 AM (peak engagement)

### What Must Not Break
- Existing commands: `channel`, `group`, `ask`, `digest`, `analyze`
- Buffer API token: stored in vault, DO NOT log
- LinkedIn oauth: DO NOT expose in logs
- Video pipeline: independent, unaffected

### Secrets in Vault (Already Set Up)
- ANTHROPIC_API_KEY: ✅ encrypted
- BUFFER_API_TOKEN: ✅ encrypted
- OPENAI_API_KEY: ✅ encrypted
- LINKEDIN_OAUTH: ✅ encrypted

**DO NOT:** Print vault contents. Always use `vault.retrieve()`.

### Recent Failures & Fixes
None recorded yet (first build phase).

### Feature Flags (CURRENT STATE)
```yaml
trending_post_generator:
  enabled: false          # ← You'll enable this
  auto_publish_enabled: false
  image_generation_enabled: false
  daily_limit: 0
```

### Pre-Flight Checklist (MUST PASS)
- [ ] `python scripts/preflight_check.py --strict` passes
- [ ] `pytest tests/test_trending_integration.py -v` all green
- [ ] No credentials in diff: `git diff --cached | grep -i secret`
- [ ] Existing tests still pass: `pytest tests/ -v --ignore=tests/test_trending*`
- [ ] Branch protection: on main, feature branch created

### Next Steps (PHASE 1)
1. ✅ Read TRENDING_POST_GENERATOR_HANDOFF.md (this file)
2. ⏹️ Run pre-flight checklist (blocking)
3. ⏹️ Create feature branch: `git checkout -b feature/trending-post-gen`
4. ⏹️ Build commands/trending.py (core CLI entry point)
5. ⏹️ Build generators/trend_analyzer.py (topic scoring)
6. ⏹️ Build integrations/web_search.py (news scanning)
7. ⏹️ Unit tests for all above
8. ⏹️ Integration tests (dry-run mode)
9. ⏹️ Security review (vault, PII, audit)
10. ⏹️ Manual approval from Randy (PR review)
11. ⏹️ Merge to main
12. ⏹️ Proceed to Phase 2 (image generation)

### Support / Questions
If Claude Code gets stuck:
1. Check INCIDENT_TRACKER.md for recent failures
2. Run `python scripts/health_check.py --verbose`
3. Review SECURITY_COMPLIANCE.md if security question
4. Look at `logs/session/` for execution history

---

## GIT STATUS
```
Current Branch: feature/trending-post-gen
Commits Since Main: 0
Changes Staged: 0
Untracked Files: 0
Clean: ✅
```

---

## LAST SESSION SUMMARY
N/A (first session for this project)

---

**Confidence Level:** 🟢 READY (pre-flight passed, no blockers)  
**Next Action:** Begin Phase 1 build
```

---

## SECTION 7: INCIDENT TRACKER FORMAT

**File:** `INCIDENT_TRACKER.md`  
**Updated:** Automatically when failures occur  
**Purpose:** Learning loop — what broke, how we fixed it

```markdown
# INCIDENT TRACKER — Self-Healing Knowledge Base

**Last Updated:** 2026-06-07T14:35:00Z  
**Total Incidents:** 0  
**Unresolved Issues:** 0  
**Auto-Remediation Success Rate:** N/A

---

## TEMPLATE FOR NEW INCIDENTS (Auto-Generated)

```
### Incident #1: [ERROR_TYPE]
**Date:** YYYY-MM-DDTHH:MM:SSZ  
**Severity:** [CRITICAL|HIGH|MEDIUM|LOW|INFO]  
**Status:** [INVESTIGATING|RECOVERING|RECOVERED|RESOLVED|WONTFIX]  
**Affected System:** trending-post-generator / image-generation / buffer-api / etc.

#### Error Details
**Error Type:** RateLimitExceeded  
**Error Message:** "OpenAI API: Rate limit exceeded (100 calls/hour)"  
**Stack Trace:**
\`\`\`
File "generators/image_generator.py", line 45, in generate_image
  response = openai.Image.create(...)
File "openai/api_resources/image.py", line 27, in create
  raise RateLimitError(...)
\`\`\`

#### Context at Time of Failure
- Operation: generate_post
- Topic: "AI Agent Security Risks"
- Stage: image_generation
- Time Since Start: 12 minutes
- API Calls Made This Hour: 101 / 100
- Last 5 Successful Calls: ✅ ✅ ✅ ✅ ❌

#### Root Cause Analysis
**Primary:** No rate limiting before DALL-E calls. Image loop was firing 3x/second.  
**Contributing:** No circuit breaker for API quota limits.  
**Why Not Caught Earlier:** Rate limiter was queued for Phase 3, not implemented yet.

#### Automated Recovery Attempts
1. Exponential backoff (100ms → 5s): **FAILED** (still hitting limit)
2. Switch to Gemini API: **FAILED** (Gemini quota also hit)
3. Queue for retry in 1 hour: **PENDING** (waiting for quota reset)

#### Manual Intervention
**Action Taken:** Paused image generation for 2 hours.  
**By:** Randy (manual approval)  
**Result:** Quota reset. Retry successful at 16:32.

#### Fix Applied
**Code Change:**
- Added RateLimiter to security/rate_limiter.py
- Integrated into image_generator.py (before every API call)
- Set limit: 80 calls/hour (20% buffer from 100 limit)
- Added circuit breaker: fail-fast at 90% quota

**Config Change:**
\`\`\`yaml
image_generation:
  rate_limit_per_hour: 80
  circuit_breaker_threshold: 0.9
  backoff_strategy: exponential_with_jitter
  max_retry_attempts: 3
\`\`\`

#### Learning & Prevention
**For Future Development:**
- [ ] Implement rate limiting BEFORE integrating any API
- [ ] Add health check: query API for current quota (every 10 mins)
- [ ] Alert at 75% quota usage
- [ ] Fallback API ready (Gemini as backup for DALL-E)
- [ ] Daily quota report: log usage vs. plan

**Pattern Recognized:** Loop behavior + external API = high risk for rate limit.  
Check all future loops calling APIs.

#### Metrics
- **Time to Detection:** 12 minutes
- **Time to Recovery:** 2 hours (manual) → 5 minutes (auto)
- **Cost Impact:** $0 (API quota limit, no overage charges)
- **Business Impact:** No posts generated for 2 hours
- **Data Loss:** 0

#### Follow-Up Actions
- [ ] PR #42: implement rate limiter (in progress)
- [ ] Add RateLimiter tests to test suite
- [ ] Update SECURITY_COMPLIANCE.md with rate limiting section
- [ ] Schedule: monthly quota review (check growth trends)

#### Related Incidents
None

#### Incident Closed
**Status:** RESOLVED  
**Date Closed:** 2026-06-07T18:32:00Z  
**Closed By:** Claude Code (auto-recovery after fix)
```

---

## SECTION 8: HEALTH CHECK & MONITORING

**File:** `HEALTH_REPORT_LATEST.json`  
**Updated:** Hourly by scheduled task  
**Purpose:** Quick status view for Claude Code and admin

```json
{
  "timestamp": "2026-06-07T14:35:00Z",
  "status": "HEALTHY",
  "confidence": 0.98,
  "checks": {
    "git_repository": {
      "status": "healthy",
      "branch": "feature/trending-post-gen",
      "commits_since_main": 5,
      "uncommitted_changes": 0
    },
    "dependencies": {
      "status": "healthy",
      "python_version": "3.11.4",
      "installed_packages": 47,
      "security_warnings": 0
    },
    "credentials_vault": {
      "status": "healthy",
      "vault_integrity": "verified",
      "keys_stored": 4,
      "last_access": "2026-06-07T14:30:00Z"
    },
    "api_quotas": {
      "status": "warning",
      "openai_dalle3": {
        "calls_this_hour": 45,
        "limit_per_hour": 100,
        "usage_percent": 45,
        "trend": "stable"
      },
      "buffer_api": {
        "calls_this_hour": 12,
        "limit_per_hour": 60,
        "usage_percent": 20,
        "trend": "stable"
      },
      "google_search": {
        "calls_today": 23,
        "limit_per_day": 100,
        "usage_percent": 23,
        "trend": "increasing"
      }
    },
    "disk_space": {
      "status": "healthy",
      "available_gb": 87.3,
      "logs_size_gb": 1.2,
      "images_cache_gb": 0.3
    },
    "network": {
      "status": "healthy",
      "connectivity": "online",
      "last_api_call": "2026-06-07T14:34:12Z",
      "response_time_ms": 187
    },
    "recent_incidents": {
      "last_24_hours": 0,
      "unresolved": 0,
      "auto_recovered": 0
    }
  },
  "recommendations": [
    "Google Search quota trending up. Monitor for approaching limits."
  ],
  "next_check": "2026-06-07T15:35:00Z"
}
```

---

## SECTION 9: DEPLOYMENT RUNBOOK

**When you're ready to go live:**

```bash
#!/bin/bash
# scripts/deploy_trending_post_generator.sh

set -e  # Exit on any error

echo "🚀 DEPLOYING TRENDING POST GENERATOR"

# 1. PRE-DEPLOYMENT CHECKS
echo "1️⃣ Running pre-flight checks..."
python scripts/preflight_check.py --strict
if [ $? -ne 0 ]; then
    echo "❌ Pre-flight failed. Aborting."
    exit 1
fi

# 2. SECURITY AUDIT
echo "2️⃣ Running security audit..."
bandit -r commands/trending.py generators/ security/ --skip B101
git diff --cached | grep -E "(api_key|token|password|secret)" && exit 1 || true

# 3. TEST SUITE
echo "3️⃣ Running test suite..."
pytest tests/test_trending_integration.py -v --cov
if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Aborting."
    exit 1
fi

# 4. DRY RUN
echo "4️⃣ Running dry-run..."
python cli.py trending generate --date "$(date +%Y-%m-%d)" --dry-run --simulate-all
if [ $? -ne 0 ]; then
    echo "❌ Dry-run failed. Aborting."
    exit 1
fi

# 5. MANUAL APPROVAL
echo "5️⃣ Waiting for approval..."
read -p "Have you reviewed the dry-run output above? (yes/no) " response
if [ "$response" != "yes" ]; then
    echo "❌ Deployment cancelled."
    exit 1
fi

# 6. MERGE TO MAIN
echo "6️⃣ Merging to main..."
git checkout main
git pull origin main
git merge feature/trending-post-gen
git push origin main

# 7. TAG RELEASE
echo "7️⃣ Tagging release..."
git tag -a v0.1-trending-post-gen -m "Initial trending post generator release"
git push origin v0.1-trending-post-gen

# 8. ENABLE FEATURE FLAG (PHASE 1: disabled)
echo "8️⃣ Setting feature flags..."
python scripts/set_feature_flag.py --flag trending_post_generator:enabled --value false
# ^ Remains disabled until you manually enable after monitoring

# 9. SETUP SCHEDULED TASK
echo "9️⃣ Creating Windows Task Scheduler job..."
schtasks /create /tn "TPG_DailyPostGenerator" \
  /tr "python C:\path\to\youtube-downloader\cli.py trending generate --date today" \
  /sc daily \
  /st 10:05 \
  /ru Randy

# 10. VERIFY
echo "🔟 Verifying deployment..."
python -c "from commands.trending import generate; print('✅ Import successful')"

# 11. NOTIFY
echo "✅ DEPLOYMENT SUCCESSFUL"
echo "Next steps:"
echo "  1. Monitor health checks: watch 'python scripts/health_check.py --watch'"
echo "  2. Review logs: tail -f logs/session/SESSION_LOG_LATEST.md"
echo "  3. Enable feature after 24h monitoring: python scripts/set_feature_flag.py --flag trending_post_generator:enabled --value true"
```

---

## SECTION 10: TROUBLESHOOTING GUIDE

**If Claude Code gets stuck:**

| Problem | Solution |
|---------|----------|
| **ImportError: No module named 'trending'** | Ensure `commands/trending.py` exists and `__init__.py` in commands/ exports it |
| **CredentialVault: KeyError** | Run `python scripts/init_vault.py` to set up encryption keys |
| **Rate limit exceeded (OpenAI)** | Health check will catch this. Automatic backoff + queue for retry. |
| **PII detected in post content** | Automatic mask + alert. Review masked content before approval. |
| **Audit log tampering detected** | CRITICAL. Restore from backup: `git checkout logs/audit/audit_latest.jsonl` |
| **Buffer API authentication failed** | Refresh oauth token: `python scripts/refresh_buffer_token.py` |
| **Out of disk space** | Run `python scripts/cleanup_old_logs.py` to archive logs > 30 days |
| **Tests fail but code looks correct** | Clear cache: `rm -rf __pycache__ .pytest_cache` |

---

## SECTION 11: APPENDICES

### A. Recommended Reading (Enterprise Standards)

- **NIST Cybersecurity Framework**: https://nvlpubs.nist.gov/nistpubs/cswp/nist.cswp.04162018.pdf
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **CWE/SANS Top 25**: https://cwe.mitre.org/top25/
- **HIPAA Security Rule** (if healthcare): https://www.hhs.gov/hipaa/for-professionals/security/
- **GLBA** (if financial): https://www.ftc.gov/business-guidance/privacy-security/gramm-leach-bliley-act
- **GDPR** (if EU data involved): https://gdpr-info.eu/

### B. Credential Setup (One-Time)

```bash
# 1. Create .env file (NEVER commit this)
echo "VAULT_ENCRYPTION_KEY=$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')" > .env
echo "ANTHROPIC_API_KEY=sk-..." >> .env
echo "BUFFER_API_TOKEN=..." >> .env
echo "OPENAI_API_KEY=..." >> .env
echo "LINKEDIN_OAUTH=..." >> .env

# 2. Initialize vault (interactive)
python scripts/init_vault.py

# 3. Test vault access
python -c "from security.vault import CredentialVault; v = CredentialVault(); print(v.retrieve('ANTHROPIC_API_KEY')[:10] + '...')"

# 4. Verify .env is in .gitignore
grep ".env" .gitignore || echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
```

### C. Testing Checklist

```bash
# Unit tests
pytest tests/test_trending_integration.py -v
pytest tests/test_security.py -v
pytest tests/test_image_generation.py -v

# Integration tests (with real APIs, but dry-run)
python cli.py trending generate --date today --dry-run --simulate-all

# Security tests
bandit -r . --skip B101
python scripts/pii_scanner.py --check-recent-logs
python scripts/audit_log_verify.py

# Performance tests
pytest tests/ -v --durations=10  # show slowest tests

# Load tests (simulate 10 daily posts)
for i in {1..10}; do
  python cli.py trending generate --date "2026-06-0$((i % 7 + 1))" --dry-run &
done
wait
echo "✅ All 10 posts generated successfully"
```

### D. File Retention Policy (Compliance)

```yaml
Log Retention:
  audit_logs:
    retention_days: 2555  # 7 years for healthcare/financial
    encryption: AES-256
    format: JSONL (immutable)
    location: logs/audit/
  
  session_logs:
    retention_days: 90
    encryption: none (no PII)
    format: Markdown
    location: logs/session/
  
  incident_logs:
    retention_days: 2555
    encryption: none (no PII)
    format: Markdown
    location: logs/incidents/
  
  image_cache:
    retention_days: 7
    encryption: none (business data)
    location: data/image_cache/
    auto_cleanup: enabled

Deletion Process:
  - Automated: daily job at 02:00 UTC checks retention dates
  - Manual: `python scripts/delete_expired_logs.py --dry-run` (then remove --dry-run)
  - Verification: immutable audit trail logs deletion itself
```

---

## SIGN-OFF & APPROVAL

**This handoff is ready when:**

- [ ] You've reviewed all sections (1-11)
- [ ] You've answered the 7 structural decisions in ORCHESTRATOR.md §7
- [ ] You've generated encryption keys and stored in .env (NEVER committed)
- [ ] You've tested the vault setup
- [ ] You've run pre-flight checks
- [ ] You've read the compliance checklist (Section 5.5)
- [ ] Feature flags are configured (trending_post_generator:enabled = false)
- [ ] You've approved the budget (API costs ~$15/month)

**Next Step:** Run `python scripts/preflight_check.py --strict` and report results to Claude Code.

---

**Document Version:** 1.0  
**Last Updated:** 2026-06-07T14:40:00Z  
**Maintained By:** Randy Skiles (joatsaint)  
**For Questions:** See SECTION 8 (Support)
