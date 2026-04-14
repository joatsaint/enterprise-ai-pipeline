# CODE_REVIEW_CHECKLIST.md
## AI-Generated Code Review Protocol — YouTube Transcript Downloader

**Version:** 1.0
**Owner:** Randy Skiles
**Applies to:** All code generated or modified by Claude Code before merging to main

---

## Purpose

This checklist enforces the "plan and act" pattern for AI-assisted development.
No Claude Code output enters production without passing this review. The checklist
exists because AI always finds the easiest path — not always the correct one.

Run this checklist after every Claude Code scaffold execution, before committing
to GitHub. Each section takes 2-5 minutes. Total review time: 15-20 minutes.

---

## How to Use This Checklist

1. Execute the scaffold prompt in Claude Code
2. Open the generated/modified files in VS Code
3. Work through each section below in order
4. Mark each item ✅ PASS, ❌ FAIL, or ⚠️ NEEDS WORK
5. Fix all ❌ and ⚠️ items before committing
6. Never commit with unresolved ❌ items

---

## SECTION 1 — Security and Credentials

**Priority: CRITICAL — check this first, every time**

- [ ] No API keys, passwords, or tokens hardcoded anywhere in the file
- [ ] No credentials visible in print() statements, log output, or comments
- [ ] All secrets loaded from `os.getenv()` or `.env` via `_load_env()`
- [ ] `.env` is listed in `.gitignore` — verify before every commit
- [ ] No user-supplied input passed directly to shell commands (subprocess injection risk)
- [ ] URLs validated with `urlparse` before being used in API calls
- [ ] No `eval()` or `exec()` calls on user-supplied or AI-generated strings
- [ ] Proxy credentials loaded from environment, never hardcoded

**If any item fails:** Stop. Fix before proceeding. Security failures are not deferred.

---

## SECTION 2 — Error Handling

**Priority: HIGH — production reliability depends on this**

- [ ] Every external API call wrapped in try/except with a specific exception type
- [ ] Generic `except Exception` used only as a last resort catch-all, never as the primary handler
- [ ] All exceptions logged with enough context to debug: file name, video ID, error message
- [ ] Empty or None responses from APIs checked before processing
- [ ] File operations (open, write, read) wrapped in try/except
- [ ] Empty file check after write operations (pattern: check size > 0 after write)
- [ ] Specific exceptions caught before generic ones (NoTranscriptFound before Exception)
- [ ] Retry logic includes a delay (time.sleep) — never instant retry on failure
- [ ] Maximum retry count defined — system never retries infinitely
- [ ] Graceful degradation: failure of one item does not abort the entire batch

**Reference pattern from orchestrator.py:**
```python
try:
    result = fetch_transcript(url)
except NoTranscriptFound:
    state["status"] = "no_transcript"
    stats["skipped"] += 1
    continue
except Exception as e:
    if state["retry_count"] < 1:
        state["retry_count"] += 1
        time.sleep(5)
        # retry logic here
    else:
        print(f"[ERROR] Failed after retry: {video_id} — {e}")
        stats["failed"] += 1
        continue
```

---

## SECTION 3 — Rate Limiting and API Safety

**Priority: HIGH — account bans are hard to recover from**

- [ ] Delay between API calls uses `random.uniform(low, high)` — never a fixed interval
- [ ] Delay range is appropriate for the API being called:
  - YouTube transcript API: 2-5 seconds normal, 4-7 seconds full download
  - YouTube Data API (comments): 1-2 seconds
  - Anthropic Claude API: 0.5 seconds minimum
- [ ] Rate limit pause skipped after the last item in a batch (no unnecessary wait)
- [ ] Quota exhaustion caught explicitly with a clear `[WARN]` message
- [ ] Cloud environment detection present for any interactive download function
- [ ] No parallel/concurrent requests unless explicitly designed and tested for it

**Delay reference:**
```python
delay = random.uniform(delay_low, delay_high)
print(f"[RATE] Pausing {delay:.1f}s...")
time.sleep(delay)
```

---

## SECTION 4 — Input Validation

**Priority: HIGH — garbage in, garbage out (or worse, crashes)**

- [ ] All URL inputs validated with `urlparse` before use
- [ ] Video ID extraction verified — does not assume URL format
- [ ] Channel name and URL validated as non-empty before registration
- [ ] File paths checked for existence before reading
- [ ] Environment variable values checked for empty string after `os.getenv()`
- [ ] Integer conversions from env vars wrapped in try/except or defaulted safely
- [ ] User-supplied strings stripped of whitespace before comparison or storage
- [ ] Max video count enforced — no unbounded loops over API results

**Reference pattern:**
```python
def validate_input(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Invalid URL scheme: {url}")
    # extract video_id logic here
```

---

## SECTION 5 — Logging and Observability

**Priority: MEDIUM — you cannot debug what you cannot see**

- [ ] Each significant pipeline step has a `[TAG]` prefixed print statement
- [ ] Tags used consistently:
  - `[INFO]` — normal progress update
  - `[SKIP]` — item intentionally skipped with reason
  - `[WARN]` — non-fatal issue, processing continues
  - `[ERROR]` — fatal item failure, item skipped
  - `[RATE]` — rate limiting pause
  - `[RETRY]` — retry attempt in progress
  - `[COMMENTS]` — comment fetch operation
- [ ] Run summary printed at completion with counts: processed, skipped, retried, failed
- [ ] No silent failures — every exception either logs or raises
- [ ] Debug information includes enough context: video ID, channel name, file path
- [ ] No excessive logging that would obscure real errors in normal output

---

## SECTION 6 — File and Data Handling

**Priority: MEDIUM — data integrity protects the transcript library**

- [ ] Output files written to correct directory structure (transcripts/group/channel/)
- [ ] File naming convention consistent: `{video_id}_{sanitized_title}.md`
- [ ] Incremental mode check: existing files detected before re-downloading
- [ ] UTF-8 encoding specified on all file open operations
- [ ] Markdown output includes required headers (title, channel, date, URL)
- [ ] Comment files saved with `_comments.md` suffix alongside transcript
- [ ] Knowledge base index updated after new files added
- [ ] No partial writes left on disk if process interrupted mid-file

---

## SECTION 7 — Code Quality and Maintainability

**Priority: MEDIUM — future-you needs to understand this**

- [ ] Function names are descriptive verbs: `fetch_transcript()`, not `get_thing()`
- [ ] No function longer than 50 lines — if longer, break into sub-functions
- [ ] No magic numbers — constants defined at top of file or in config
- [ ] Comments explain *why*, not *what* — the code shows what, comments explain reasoning
- [ ] No commented-out dead code left in the file
- [ ] Imports organized: stdlib first, then third-party, then local modules
- [ ] No duplicate logic — if the same pattern appears twice, it should be a function
- [ ] State object keys are consistent with existing orchestrator pattern

---

## SECTION 8 — Testing

**Priority: HIGH — 39 passing tests must stay at 39 or higher**

- [ ] New functionality has at least one test covering the happy path
- [ ] New error handling has at least one test covering the failure path
- [ ] Existing tests still pass after changes: run `pytest` before committing
- [ ] Mock used for all external API calls in tests — no real API calls in test suite
- [ ] Test file follows naming convention: `test_{module_name}.py`
- [ ] Test names describe the scenario: `test_validate_input_rejects_missing_scheme()`
- [ ] Edge cases covered: empty input, None, malformed URL, quota exhausted

**Run before every commit:**
```bash
pytest tests/ -v
```
**Required result:** All tests pass. Zero failures. Zero errors.

---

## SECTION 9 — CLAUDE.md Alignment

**Priority: MEDIUM — architecture drift is how projects break**

- [ ] New module documented in CLAUDE.md architecture section
- [ ] New environment variables added to CLAUDE.md .env reference section
- [ ] New CLI commands documented in CLAUDE.md commands section
- [ ] Any new dependencies added to requirements.txt
- [ ] CLAUDE.md version number incremented if significant changes made
- [ ] New module follows the existing pattern: `_load_env()` at import time
- [ ] Module registered in the project's known file list

---

## SECTION 10 — Pre-Commit Final Check

**Run these commands before every `git commit`:**

```bash
# 1. Verify tests pass
pytest tests/ -v

# 2. Verify .env is not staged
git status | grep -i ".env"

# 3. Check for any hardcoded strings that look like keys
grep -rn "sk-\|AKIA\|Bearer " src/ --include="*.py"

# 4. Review what's being committed
git diff --staged
```

**Commit message format:**
```
[Phase/Stage] Short description of what changed

- Bullet point of specific change 1
- Bullet point of specific change 2
- Tests: X/X passing
```

**Example:**
```
[Phase 3] Add pain point extractor with comment weighting

- Two-pass extraction: questions then pain points
- Comments weighted 2x over transcript content
- Haiku model for cost efficiency (~$0.10/run)
- Tests: 39/39 passing
```

---

## Quick Reference — Common Failure Patterns

These are the most common AI code generation mistakes. Check for these explicitly:

| Pattern | What AI Does Wrong | What to Look For |
|---|---|---|
| Hardcoded credentials | Puts API key directly in code | Search for any string starting with `sk-` |
| Silent except | Catches exception and passes silently | `except: pass` or `except Exception: pass` |
| Fixed rate limit | Uses `time.sleep(2)` not `random.uniform` | Any `sleep()` with a fixed number |
| No empty check | Assumes API always returns data | Missing `if not result:` after API call |
| Unbounded retry | Retries forever on failure | Missing `retry_count < MAX` guard |
| Missing UTF-8 | Opens files without encoding | `open(path, 'r')` without `encoding='utf-8'` |
| Missing .env check | Assumes env vars are set | `os.getenv()` result used without checking empty |
| Test calls real API | Test suite makes live API calls | Any test without `@mock.patch` on external calls |

---

*Version 1.0 — April 2026*
*Review this checklist quarterly and update based on new failure patterns observed*
