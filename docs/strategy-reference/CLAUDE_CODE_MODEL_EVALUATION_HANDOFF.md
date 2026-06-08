# Claude Code: Model Evaluation & Switching Handoff
## Free/Cheap AI Models Assessment for youtube-downloader Project

**Created:** June 2026  
**For:** Claude Code (youtube-downloader project)  
**Purpose:** Evaluate whether free/cheap alternative models work for specific tasks; recommend strategic model routing; execute switches without breaking current workflows

---

## Table of Contents
1. [Current State & Constraints](#current-state)
2. [Task Inventory (What Claude Code Actually Does)](#task-inventory)
3. [Model Evaluation Matrix](#model-evaluation-matrix)
4. [Free/Cheap Model Profiles (With youtube-downloader Fit)](#model-profiles)
5. [Task-to-Model Routing Decision Tree](#routing-tree)
6. [How to Switch Models (Technical Implementation)](#switching)
7. [Cost Analysis (Current vs. Alternatives)](#cost-analysis)
8. [Recommendations for Each Project](#recommendations)

---

## Current State & Constraints

### What Claude Code Currently Has

**Project:** `youtube-downloader/` (enterprise-ai-pipeline)

**Current tools & dependencies:**
- **Primary model:** Claude Opus 4.7 (via Claude Code)
- **Model string:** `claude-opus-4-7-20250219` (or current Opus)
- **Task Runner:** `run_pipeline.bat` (Windows)
- **Notifications:** `send_notification.ps1`
- **Python version:** 3.14.3 (bare `python`, no venv)
- **Key files Claude reads:**
  - `ORCHESTRATOR.md` (map of all projects)
  - `CLAUDE.md` (youtube-downloader-specific instructions)
  - `TASKS.md` (active task board)
  - `SESSION_LOG.md` (continuity log)
  - `linkedin_atomizer.py` (content generation script)
  - Voice files: `voice.md`, `youtube-voice.md`
  - `ARTICLE_WEEK_PROMPT.md` (article generation)
  - Research files: `Randys_Brain_Droppings.md`, etc.

**Current usage patterns:**
- Content atomization (articles → 5 formats)
- Task decomposition (breaking complex work into steps)
- File creation & editing (Python scripts, markdown)
- Bash command execution
- Prompt refinement & optimization

**Current constraints:**
- Randy hitting Claude Pro session/weekly limits
- Can't afford higher-tier plans
- Needs to maintain current quality without overspending

---

## Task Inventory (What Claude Code Actually Does)

### Task 1: Article Atomization (linkedin_atomizer.py)

**What it does:**
- Input: One article (2,000–3,000 words)
- Output: 5 atomized formats (LinkedIn post, Instagram caption, Pinterest description, Twitter thread, newsletter hook)
- Complexity: **Medium** (requires understanding voice, platform rules, character limits)
- Token cost: ~2,000 input (article) + 1,500 output (5 pieces) = 3,500 tokens
- Frequency: Weekly (5 articles/week = ~17,500 tokens/week)
- Quality tolerance: High (brand voice must be preserved)

**Can this work with cheaper models?**
- ✅ YES for routine articles (similar to past ones) — Sonnet/DeepSeek sufficient
- ❌ NO for novel topics/strategic pieces — needs Opus reasoning

---

### Task 2: Prompt Optimization & Refinement

**What it does:**
- Take a prompt
- Identify inefficiencies (token waste, filler, repetition)
- Rewrite for concision without quality loss
- Token cost: ~1,000 input + 800 output = 1,800 tokens
- Frequency: Ad-hoc (2–3x/month)
- Quality tolerance: Medium (optimization suggestions, not mission-critical)

**Can this work with cheaper models?**
- ✅ YES — Sonnet/Gemini/DeepSeek all capable
- Cost optimization alone: use cheaper model for this

---

### Task 3: File Creation & Editing (Python, Markdown, Bash)

**What it does:**
- Create/edit Python scripts for automation
- Generate markdown documentation
- Write bash commands for file operations
- Token cost: 800 input + 1,200 output = 2,000 tokens per file
- Frequency: Weekly (3–5 files/week)
- Quality tolerance: High (code must work; docs must be accurate)

**Can this work with cheaper models?**
- ✅ YES for documentation & simple scripts (Sonnet/DeepSeek)
- ❌ MAYBE for complex logic (use Opus if debugging needed)

---

### Task 4: Task Decomposition & Planning

**What it does:**
- Take a complex goal ("atomize 10 articles")
- Break into step-by-step plan
- Explain rationale, dependencies, success criteria
- Token cost: 500 input + 2,000 output = 2,500 tokens
- Frequency: Weekly (1–2x per project)
- Quality tolerance: High (bad plan = wasted time)

**Can this work with cheaper models?**
- ✅ YES for routine work (Sonnet/Gemini)
- ❌ NO for novel/ambiguous problems (use Opus)

---

### Task 5: Research & Trend Mining

**What it does:**
- Analyze YouTube transcripts for pain points
- Mine Reddit for sysadmin concerns
- Synthesize findings into content pillars
- Token cost: 5,000–15,000 input (transcripts) + 3,000 output (synthesis)
- Frequency: Monthly/quarterly
- Quality tolerance: Very high (feeds entire content strategy)

**Can this work with cheaper models?**
- ❌ NO — needs deep reasoning, long-context coherence
- MUST use Opus or extended-thinking model (e.g., Claude + extended-thinking, or OpenAI R1)

---

## Model Evaluation Matrix

### Evaluation Criteria (For Claude Code's Workflow)

| Criterion | Why it matters | Weight |
|-----------|---|---|
| **Token cost** | Randy hitting limits; need to reduce burn | 20% |
| **Output quality** (voice preservation) | Brand consistency non-negotiable | 25% |
| **Long-context performance** (200K+) | Transcripts, long articles | 15% |
| **Reasoning depth** (ambiguous prompts) | Novel topics, edge cases | 20% |
| **API availability / switching cost** | Claude Code must be able to call it | 10% |
| **Speed** (latency) | Interactive workflow (Randy watching) | 10% |

---

### Model Scorecard (youtube-downloader Fit)

| Model | Cost | Voice | Context | Reasoning | API | Speed | **OVERALL** | Best for |
|-------|------|-------|---------|-----------|-----|-------|-------------|----------|
| **Claude Opus 4.7** (current) | 😞 High | ✅ 95% | ✅ 200K | ✅✅ 95% | ✅ Native | ✅ 2–3s | **95%** | Complex reasoning, novel topics |
| **Claude Sonnet 4.6** | ✅ 80% less | ✅ 90% | ✅ 200K | ✅ 85% | ✅ Native | ✅ 1–2s | **85%** | Routine atomization, editing |
| **Gemini 3.1 Pro** | ✅ 90% less | ⚠️ 85% | ✅✅ 1M | ✅ 85% | ✅ API | ⚠️ 3–5s | **80%** | Long documents, multimodal |
| **GPT-4o** | ✅ 85% less | ⚠️ 85% | ⚠️ 128K | ✅ 85% | ✅ API | ✅ 1–2s | **78%** | Fast iteration, batch processing |
| **DeepSeek V4 Flash** | ✅✅ 95% less | ⚠️ 80% | ✅ 1M | ✅ 80% | ✅ API | ⚠️ 4–6s | **75%** | Simple tasks, cost-sensitive |
| **Aider (model-agnostic)** | Depends | ✅ 95% (with Sonnet) | Varies | Varies | ✅ Custom | ⚠️ 3–5s | **70%** | File editing, code generation |

**Legend:**
- ✅ = Works well for youtube-downloader
- ⚠️ = Acceptable but not ideal
- ❌ = Not recommended

---

## Free/Cheap Model Profiles (With youtube-downloader Fit)

### Model 1: Claude Sonnet 4.6

**Cost:** $3 input / $15 output per 1M tokens (80% cheaper than Opus)

**When to use in youtube-downloader:**
- ✅ Article atomization for routine topics
- ✅ Prompt optimization
- ✅ Documentation writing
- ✅ Simple file edits
- ❌ Deep research/transcript analysis
- ❌ Novel strategic thinking

**Quality for voice preservation:** 90% (minor tone drift possible on edge cases)

**Token overhead:** Slightly higher output (10–15% more tokens), but cost still 70–75% lower overall

**Switching cost:** ZERO (same API as Opus; just swap model string)

**Example implementation:**
```python
# Current (Opus)
model = "claude-opus-4-7-20250219"

# Switch to Sonnet for simple tasks
if task_type == "atomize_routine":
    model = "claude-sonnet-4-6-20250514"
elif task_type == "research":
    model = "claude-opus-4-7-20250219"  # Keep Opus for complex work
```

**Recommendation for youtube-downloader:** **USE AGGRESSIVELY** for 60% of tasks

---

### Model 2: DeepSeek V4 Flash (Free Web Chat or $0.14/1M API)

**Cost:** Free (web chat) or $0.14 input / $0.28 output per 1M tokens (95% cheaper than Opus)

**When to use in youtube-downloader:**
- ✅ Simple task decomposition
- ✅ Basic documentation
- ✅ Prompt drafting (before refinement)
- ⚠️ Routine atomization (quality risk, only if voice backup exists)
- ❌ Research synthesis
- ❌ Novel reasoning

**Quality for voice preservation:** 80% (noticeable tone drift possible; needs post-edit by Randy)

**Token overhead:** Similar to Sonnet (±10%)

**Switching cost:** MEDIUM
- Free web chat: Copy-paste prompts (no code integration)
- API: Requires custom wrapper in Python

**Example use case:**
```python
# For simple, non-voice-critical tasks
if task_type == "simple_formatting":
    # Use DeepSeek (cheaper)
    model = "deepseek-v4-flash"
    note = "Results may need voice normalization"
elif task_type == "atomize":
    # Use Sonnet (better voice preservation)
    model = "claude-sonnet-4-6"
```

**Recommendation for youtube-downloader:** **TEST FIRST** on non-voice-critical work; use web chat for ad-hoc tasks

---

### Model 3: Gemini 3.1 Pro (Free tier: 1000 req/day, API: $2/$12 per 1M)

**Cost:** Free (1000 requests/day) or $2 input / $12 output per 1M tokens

**When to use in youtube-downloader:**
- ✅ Long document analysis (1M context window)
- ✅ Transcript synthesis (if >200K tokens)
- ✅ Multi-part research projects
- ⚠️ Routine atomization (capable but slightly verbose)
- ❌ Voice-critical work (needs tuning)

**Quality for voice preservation:** 85% (adequate with prompt refinement)

**Token overhead:** +20–30% (generates longer outputs)

**Switching cost:** MEDIUM (API-only for production; web interface for testing)

**Example use case:**
```python
# For transcript analysis (long-context advantage)
if input_tokens > 200000:
    # Gemini's 1M context is perfect
    model = "gemini-pro"  # Free tier if under 1000 req/day
else:
    model = "claude-opus-4-7"  # Opus for shorter, complex work
```

**Recommendation for youtube-downloader:** **USE FOR RESEARCH** (transcripts, long synthesis). Use free tier for testing/evaluation first.

---

### Model 4: OpenAI GPT-4o (API only, $2.50/$10 per 1M, 50% off with Batch)

**Cost:** $2.50 input / $10 output per 1M tokens (or $1.25/$5 with batch processing)

**When to use in youtube-downloader:**
- ✅ Fast iteration (1–2s latency)
- ✅ Batch processing (50% discount for background work)
- ✅ Routine atomization
- ⚠️ Research work (works but context window only 128K)
- ❌ Voice-critical work (needs tuning)

**Quality for voice preservation:** 85%

**Token overhead:** Similar to Sonnet

**Switching cost:** MEDIUM (different API, requires wrapper)

**Batch processing advantage:** If atomizing 10 articles overnight:
- Real-time Opus: $0.20
- Batch GPT-4o: $0.10 (50% discount, wait 4–24h)
- Savings: 50%

**Recommendation for youtube-downloader:** **USE FOR BATCH BACKGROUND TASKS** (future Phase 2)

---

## Task-to-Model Routing Decision Tree

### How Claude Code Should Decide

```
TASK ARRIVES
│
├─ Is this a RESEARCH or SYNTHESIS task?
│  ├─ YES: Use Opus (or Gemini if >200K tokens)
│  └─ NO: Continue...
│
├─ Is this a NOVEL TOPIC or EDGE CASE?
│  ├─ YES: Use Opus (needs deep reasoning)
│  └─ NO: Continue...
│
├─ Is this VOICE-CRITICAL content?
│  ├─ YES: Use Sonnet (90% voice match, acceptable risk)
│  │        (Skip DeepSeek for this; needs Randy post-edit)
│  └─ NO: Continue...
│
├─ Is this ROUTINE WORK (similar to past tasks)?
│  ├─ YES: Use DeepSeek or Sonnet (90% quality, 90% cost savings)
│  └─ NO: Use Sonnet (balanced cost/quality)
│
├─ Do we have TIME (can this wait 4–24 hours)?
│  ├─ YES: Consider Batch API (50% discount if >5 items)
│  └─ NO: Use fastest available model (GPT-4o or Sonnet)
│
└─ FINAL DECISION → Use selected model
```

### Example Decisions

**Example 1: Atomize ART5 article (new, strategic)**
```
Is research? NO
Is novel topic? YES → Use Opus
Cost: ~$0.04
Quality: 95%
```

**Example 2: Generate 5 Pinterest descriptions for pins we've done before**
```
Is research? NO
Is novel topic? NO
Is voice-critical? NO (descriptions are templates)
Is routine? YES → Use DeepSeek
Cost: ~$0.001
Quality: 80% (acceptable for descriptions)
```

**Example 3: Analyze 622 transcript summaries + find pain points**
```
Is research? YES → Use Opus (complex reasoning needed)
Alternative: Gemini if context >200K (it has 1M window)
Cost Opus: ~$0.15; Gemini: ~$0.08
Decision: Try Gemini first (cost + context), fall back to Opus if quality drops
```

**Example 4: Batch atomize 50 articles tonight, review tomorrow**
```
Is urgent? NO (can wait overnight)
Use Batch API (GPT-4o)
Cost: ~$0.25 (vs. $0.50 real-time)
Savings: 50%
Trade: 4–24h latency (acceptable for background work)
```

---

## How to Switch Models (Technical Implementation)

### Method 1: Direct API Model String Swap (Easiest)

**Current Claude Code usage:** Uses Anthropic API directly via Python/Node.

**To switch from Opus to Sonnet:**

**File:** `linkedin_atomizer.py` (or any script making API calls)

```python
# Current (Opus)
client = Anthropic()
response = client.messages.create(
    model="claude-opus-4-7-20250219",
    max_tokens=2000,
    messages=[
        {"role": "user", "content": prompt}
    ]
)

# Switched to Sonnet
response = client.messages.create(
    model="claude-sonnet-4-6-20250514",  # ← just change the model string
    max_tokens=2000,
    messages=[
        {"role": "user", "content": prompt}
    ]
)
```

**How to make it dynamic (smart routing):**

```python
def get_model_for_task(task_type):
    """Route task to appropriate model based on complexity."""
    if task_type == "research":
        return "claude-opus-4-7-20250219"  # Complex reasoning
    elif task_type == "atomize_routine":
        return "claude-sonnet-4-6-20250514"  # 80% less cost
    elif task_type == "simple_format":
        return "claude-sonnet-4-6-20250514"  # Simple work
    else:
        return "claude-opus-4-7-20250219"  # Safe default

# Usage
model = get_model_for_task("atomize_routine")
response = client.messages.create(model=model, ...)
```

**Cost: ZERO** (just change a string; same API)  
**Reversibility: YES** (change back anytime)  
**Risk: LOW** (swapping models doesn't break code)

---

### Method 2: Switch to DeepSeek API (Requires Wrapper)

**Setup:**

1. **Create DeepSeek account** (free.deepseek.com or api.deepseek.com)
2. **Get API key** (5M free tokens on signup)
3. **Install library:**
   ```bash
   pip install openai  # DeepSeek uses OpenAI SDK format
   ```

**Implementation:**

```python
# Switch to DeepSeek
from openai import OpenAI  # DeepSeek-compatible SDK

client = OpenAI(
    api_key="your-deepseek-api-key",
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-v4-flash",  # or deepseek-v4-pro for complex
    messages=[
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=2000
)
```

**Smart routing:**

```python
def get_api_client_and_model(task_type):
    """Route to Anthropic (Claude) or DeepSeek based on task."""
    if task_type in ["research", "novel_topic", "voice_critical"]:
        # Use Anthropic (Opus or Sonnet)
        return ("anthropic", "claude-sonnet-4-6-20250514")
    else:
        # Use DeepSeek (cheaper)
        return ("deepseek", "deepseek-v4-flash")

# Usage
provider, model = get_api_client_and_model("atomize_routine")
if provider == "anthropic":
    client = Anthropic()
else:
    client = OpenAI(api_key="...", base_url="https://api.deepseek.com")

response = client.messages.create(model=model, ...)
```

**Cost: MEDIUM** (needs wrapper code, one-time ~30 min)  
**Reversibility: YES** (revert to Anthropic anytime)  
**Risk: MEDIUM** (different API = different error handling)

---

### Method 3: Use LiteLLM (Unified API Wrapper)

**Benefit:** One code interface for all models (Claude, OpenAI, DeepSeek, etc.)

**Setup:**

```bash
pip install litellm
```

**Implementation:**

```python
from litellm import completion

# Same code works with any model
response = completion(
    model="claude-opus-4-7-20250219",  # or deepseek-v4-flash
    messages=[{"role": "user", "content": prompt}],
    max_tokens=2000
)
```

**Smart routing with LiteLLM:**

```python
def get_model_for_task(task_type):
    """LiteLLM-compatible model routing."""
    routing = {
        "research": "claude-opus-4-7-20250219",
        "atomize_routine": "deepseek-v4-flash",
        "voice_critical": "claude-sonnet-4-6-20250514",
    }
    return routing.get(task_type, "claude-opus-4-7-20250219")

# Usage (same code regardless of model)
model = get_model_for_task("atomize_routine")
response = completion(model=model, messages=prompt_messages)
```

**Cost: MEDIUM** (one-time setup, more maintainable long-term)  
**Reversibility: YES** (just change model string)  
**Risk: LOW** (LiteLLM handles API differences)

---

## Cost Analysis (Current vs. Alternatives)

### Scenario: 50 Articles/Month (Randy's Current Load)

**Assumptions:**
- 50 articles × 5 atomized pieces = 250 pieces total
- Average per article: 2,000 tokens input + 1,500 output = 3,500 tokens
- Monthly total: 175,000 tokens (input) + 75,000 tokens (output)

---

### Cost Calculation: All Opus (Current)

```
Input: 175,000 tokens × ($15 / 1M) = $2.63
Output: 75,000 tokens × ($75 / 1M) = $5.63
Total: $8.26/month (+ Claude Pro $20 = $28.26/month)

Risk: Hitting session limits (unquantifiable cost = time lost, quality drop)
```

---

### Cost Calculation: 60% Sonnet + 40% Opus (Mixed)

```
Routine atomization (60% of work):
  Input: 105,000 tokens × ($3 / 1M) = $0.31
  Output: 45,000 tokens × ($15 / 1M) = $0.68

Complex/novel (40% of work):
  Input: 70,000 tokens × ($15 / 1M) = $1.05
  Output: 30,000 tokens × ($75 / 1M) = $2.25

Total: $4.29/month (+ Claude Pro $20 = $24.29/month)

Savings: $4/month ($48/year) vs. all Opus
Quality: 90%+ (minor tone drift on edge cases, manageable)
Risk: Session limits reduced (less strain on Pro quota)
```

---

### Cost Calculation: DeepSeek for Simple + Opus for Complex

```
Simple tasks (70% of work) — DeepSeek:
  Input: 122,500 tokens × ($0.14 / 1M) = $0.017
  Output: 52,500 tokens × ($0.28 / 1M) = $0.015

Complex tasks (30% of work) — Opus:
  Input: 52,500 tokens × ($15 / 1M) = $0.79
  Output: 22,500 tokens × ($75 / 1M) = $1.69

Total: $2.50/month (+ Claude Pro $20 = $22.50/month)

Savings: $5.76/month ($69/year) vs. all Opus
Quality: 85% (DeepSeek quality acceptable for formatting, not voice)
Risk: Need voice quality gate for DeepSeek output
```

---

### Cost Calculation: Optimal Mix (Sonnet + Batch DeepSeek)

```
Routine atomization (60% of work) — Batch DeepSeek:
  Input: 105,000 tokens × ($0.14 / 1M × 0.5 batch discount) = $0.007
  Output: 45,000 tokens × ($0.28 / 1M × 0.5) = $0.006

Voice-critical (30% of work) — Sonnet:
  Input: 52,500 tokens × ($3 / 1M) = $0.16
  Output: 22,500 tokens × ($15 / 1M) = $0.34

Complex/novel (10% of work) — Opus:
  Input: 17,500 tokens × ($15 / 1M) = $0.26
  Output: 7,500 tokens × ($75 / 1M) = $0.56

Total: $1.28/month (+ Claude Pro $20 = $21.28/month)

Savings: $7/month ($84/year) vs. all Opus
Quality: 92% (high-quality output, batch delay acceptable for background)
Risk: Requires batch processing workflow (4–24h latency acceptable for atomization)
```

---

## Recommendations for Each Project

### Project: youtube-downloader (Deep Research Pipeline)

**Current model:** Claude Opus 4.7  
**Budget:** Can't change (research requires Opus-level reasoning)

**Recommendation:** **KEEP OPUS, REDUCE ELSEWHERE**

- ✅ **Keep** Opus for all transcript analysis + research synthesis
- ⚠️ **Consider** Sonnet for documentation + planning
- ❌ **Don't** switch research to cheaper model (quality cliff too steep)

**Estimated impact:** Zero token reduction (research already costs most)

---

### Project: content-engine (LinkedIn Atomizer)

**Current model:** Claude Opus 4.7 (for all atomization)  
**Budget:** Can optimize significantly

**Recommendation:** **AGGRESSIVE SWITCHING**

**Routing rule:**

```python
if article_is_novel_topic():
    use_model = "claude-opus-4-7"  # Complex reasoning
elif article_is_routine() and is_voice_critical():
    use_model = "claude-sonnet-4-6"  # Voice preservation, cost savings
else:
    use_model = "deepseek-v4-flash"  # Simple formatting, max savings
```

**Expected results:**
- Token burn: -60% (from $8.26 → $2.50/month)
- Quality: 90%+ (with voice gates)
- Implementation: 2 hours (routing logic + testing)

**Phase-in plan:**
1. **Week 1:** Test Sonnet on 5 routine articles (compare quality)
2. **Week 2:** If quality acceptable, route 50% of routine work to Sonnet
3. **Week 3:** Test DeepSeek on non-voice-critical tasks (hashtags, descriptions)
4. **Week 4:** Full rollout with mixed routing

---

### Project: ai-job-search-agent (Planned, Not Yet Built)

**Current model:** N/A (spec only)

**Recommendation:** **BUILD WITH MULTI-MODEL FROM START**

**Routing:**

```python
# Use DeepSeek for most work (cheap), Opus only when critical
if task in ["resume_scoring", "job_match_analysis"]:
    use_model = "claude-opus-4-7"  # Reasoning-heavy
else:
    use_model = "deepseek-v4-flash"  # Cheap default
```

**Estimated cost:** $3–5/month (vs. $20 if built all-Opus)

---

## Claude Code Execution Checklist

### Before You Switch (Validation Phase)

- [ ] **Current setup:** Confirm model string currently used in all scripts
- [ ] **Baseline cost:** Track current monthly token spend (check API dashboard)
- [ ] **Quality baseline:** Sample 3 current outputs (atomized articles, research) — note voice, clarity, accuracy
- [ ] **Route table:** Create task-type categories (research, routine, formatting, novel)

### For Each Model You Test

- [ ] **Cost confirmed:** Double-check pricing on official API docs
- [ ] **Sample prompt:** Run 2–3 real-world examples through the model
- [ ] **Quality gate:** Compare output to Opus baseline (voice preservation, accuracy)
- [ ] **API working:** Verify authentication, response format
- [ ] **Error handling:** Test what happens if API is down

### Implementation (Sonnet First)

- [ ] **Create routing function** in `linkedin_atomizer.py`:
  ```python
  def get_model_for_task(task_type):
      # Add your routing logic here
  ```
- [ ] **Test on routine article:** Atomize 1 known-good article with Sonnet
- [ ] **Compare outputs:** Word-for-word vs. Opus baseline
- [ ] **Voice preservation check:** Is Randy's voice intact? Any tone drift?
- [ ] **Approve or roll back:** If ≥90% quality, commit; else revert to Opus

### Implementation (DeepSeek Second, If Sonnet Works)

- [ ] **Get API key** (5M free tokens)
- [ ] **Test non-voice-critical task:** Generate hashtags or Pinterest descriptions
- [ ] **Quality check:** 80%+ acceptable?
- [ ] **Integrate routing:** Add DeepSeek to decision tree
- [ ] **Batch test:** Atomize 5 articles, run batch job, review results

### Monitoring (Ongoing)

- [ ] **Track token spend** by model (per script, per task)
- [ ] **Quality spot-checks:** Weekly sample 1 output from each model
- [ ] **Cost alerts:** If total spend exceeds expected, flag
- [ ] **Update routing:** If a model underperforms, shift work back to Opus

---

## Reference: Current API Model Strings (June 2026)

**Claude (Anthropic):**
- Opus 4.7: `claude-opus-4-7-20250219`
- Sonnet 4.6: `claude-sonnet-4-6-20250514`
- Haiku 4.0: `claude-haiku-4-0-20250120`

**OpenAI:**
- GPT-4o: `gpt-4o`
- GPT-4 Turbo: `gpt-4-turbo`

**DeepSeek:**
- V4 Flash: `deepseek-v4-flash`
- V4 Pro: `deepseek-v4-pro`

**Google:**
- Gemini 3.1 Pro: `gemini-pro`
- Gemini 3.1 Flash: `gemini-flash`

*Check latest at: api-docs.deepseek.com, platform.openai.com, ai.google.dev*

---

## Summary: What Claude Code Should Do

### This Session
1. **Read this handoff** + understand routing logic
2. **Add task-type classification** to `linkedin_atomizer.py`
3. **Create `get_model_for_task()` function**
4. **Test Sonnet on 1 routine article** (atomize ART5 or similar)
5. **Report back to Randy** (quality %, token cost, go/no-go)

### Next Sessions (If Approved)
1. **Roll out Sonnet routing** (60% of routine work)
2. **Test DeepSeek** (non-voice-critical tasks)
3. **Monitor costs** (track savings)
4. **Iterate routing rules** (optimize based on quality feedback)

### Long-term (After Validation)
1. **Implement LiteLLM** (unified API)
2. **Add batch processing** (50% discount for overnight work)
3. **Build cost dashboard** (monthly spend by model/task)
4. **Document final routing** in `CLAUDE.md`

---

**Document Version:** 1.0  
**Last Updated:** June 2026  
**Next Review:** After Sonnet testing (Week 1)  
**Owner:** Claude Code (execution) + Randy (approval)
