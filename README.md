# AI Orchestrator for Multi-Source Data Automation

> **End-to-end AI pipeline** that scrapes YouTube transcripts and audience comments at scale, extracts market intelligence using Claude AI, generates short-form video with voice cloning and motion graphics, and surfaces daily audience engagement opportunities — without human intervention.

[![Tests](https://github.com/joatsaint/enterprise-ai-pipeline/actions/workflows/test-suite.yml/badge.svg)](https://github.com/joatsaint/enterprise-ai-pipeline/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![Claude](https://img.shields.io/badge/AI-Claude%20Sonnet%20%2F%20Haiku-orange)](https://anthropic.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## What This Does

Most market research tools tell you what people are saying. This system tells you what they're **actually asking** — extracted from real audience behavior at scale, then turned into content automatically.

**In one command**, the research engine:
- Downloads transcripts and top comments from any YouTube channel
- Classifies and indexes content by topic category
- Runs AI analysis to extract the most repeated questions, pain points, and desired outcomes
- Generates a ranked intelligence report ready for product and content decisions

**Result:** Market research that would take a human 40+ hours manually, completed in minutes.

### The full pipeline — research to published content

| Stage | What it does |
|---|---|
| **Research** | Scrapes YouTube transcripts + comments → AI pain-point extraction → ranked intelligence reports |
| **Daily Radar** | Scans Reddit and Spiceworks daily → scores threads for audience fit → drafts on-voice comments for human approval |
| **Content generation** | Source piece → article / carousel / newsletter / LinkedIn post in a configured voice profile |
| **YouTube Shorts** | Pain point → Claude script → HeyGen voice-clone avatar → Whisper timestamps → Remotion motion graphics → FFmpeg composite → captioned 9:16 Short |
| **Newsletter curation** | Gmail inbox → relevance-filtered AI newsletter digest via MCP integration |
| **Scheduling** | Buffer API integration → posts queue behind a human approval gate |
| **Observability** | At-a-glance `status` + weekly AI-cost `report` from a per-call usage ledger |

Every stage flows through a single orchestrator and stops at a human review gate before anything is published.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Entry Point                          │
│                     src/main.py                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Orchestrator                              │
│                 src/orchestrator.py                         │
│  • URL validation    • State management                     │
│  • Pipeline sequencing  • Retry + rate-limit backoff        │
│  • Run statistics    • Graceful shutdown (Ctrl-C safe)       │
└──────┬──────────────┬───────────┬──────────┬────────────────┘
       │              │           │          │
       ▼              ▼           ▼          ▼
┌──────────┐  ┌──────────┐  ┌────────┐  ┌──────────────────┐
│Transcript│  │ Comment  │  │Markdown│  │  Knowledge Base  │
│ Fetcher  │  │ Fetcher  │  │Converter│  │                  │
│          │  │          │  │        │  │ Indexer · Query  │
│Rotating  │  │YouTube   │  │Struct- │  │ Digest · Extract │
│Proxy     │  │Data API  │  │ured .md│  │                  │
└──────────┘  └──────────┘  └────────┘  └──────────────────┘
                                                │
                       ┌────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Downstream Pipelines                           │
│                                                             │
│  ┌─────────────────┐      ┌──────────────────────────────┐  │
│  │  Daily Radar    │      │    YouTube Shorts Pipeline   │  │
│  │                 │      │                              │  │
│  │ Reddit/Spice-   │      │ Pain point selector          │  │
│  │ works scan      │      │   → Claude script writer     │  │
│  │   → AI scoring  │      │   → HeyGen voice-clone avatar│  │
│  │   → Comment     │      │   → Whisper word timestamps  │  │
│  │     drafts      │      │   → Remotion motion graphics │  │
│  │   → Human gate  │      │   → FFmpeg chromakey/overlay │  │
│  └─────────────────┘      │   → Captioned 9:16 Short     │  │
│                           └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## YouTube Shorts Pipeline — Multi-Modal AI

The Shorts pipeline chains six distinct AI systems into a single command:

```bash
python -m src.main shorts --pain-point "IT pros are terrified of being replaced"
```

```
Step 1  Pain point selector   reads Daily Radar state, picks highest-priority sysadmin topic
Step 2  Script writer         Claude Sonnet → 5-section script (~150 words, ~75 sec) + screen hook
Step 3  HeyGen renderer       voice-clone avatar render via HeyGen v2 API (1080×1920, 9:16)
                              → tracks credit spend per render (measured: 0.34 credits/sec)
Step 4  Whisper transcriber   word-level timestamps, 2-word caption chunks, section frame mapping
Step 5  Remotion graphics     animated text-card composition (brand colors, section transitions)
Step 6  FFmpeg stitcher       chromakey composite + drawtext captions + hook overlay → final MP4
```

**Output:** `content-engine/content/_video/shorts/{slug}/final_a.mp4` — ready to review and post.

---

## Daily Audience Radar

Runs every morning. Scans Reddit (`r/sysadmin`, `r/ITCareerQuestions`) and Spiceworks for threads where Randy's audience is active:

```
Gather candidates → Score 5 dimensions (Audience Fit, Pain Level, Comment Opportunity,
Freshness, Sales Risk) → Rank by priority score → Draft on-voice comments → Human approves
```

Nothing auto-posts. Every comment draft goes through a human gate before Randy pastes it manually.

---

## Key Technical Decisions

| Decision | Choice | Reasoning |
|---|---|---|
| AI models | Claude Sonnet (scripts) · Haiku (scoring/digest) | Right model for the task — quality where it matters, cost where it doesn't |
| Rate-limit handling | Exponential backoff in `ai.call_with_retry()` | 429s were crashing the radar silently — now retries at 60s → 120s across all callers |
| Video avatar | HeyGen v2 API, transparent/greenscreen bg | Voice-clone avatar renders without manual recording; chromakey composited in FFmpeg |
| Motion graphics | Remotion (React-based) | Programmatic animation tied to Whisper timestamps; brand-consistent without a designer |
| Transcription | OpenAI Whisper (local, word-level) | Word timestamps enable 2-word caption sync and section-frame matching |
| Index | Flat-file JSON | Vector DB overhead not justified at <1,500 transcripts |
| Rate limiting | `random.uniform(2-7s)` between requests | Fixed intervals create bot signature — randomized mimics human behavior |
| Credentials | `.env` + `os.environ.setdefault()` | System env vars take precedence — cloud-deployment ready |
| Idempotency | Check logs before every fetch/write | Safe to re-run any step; partial files cleaned up on failure |

---

## Pipeline Stats

| Metric | Value |
|---|---|
| Channels registered | 52 |
| Topic groups | 4 |
| Transcripts indexed | 1,014 |
| Audience comments analyzed | 47,000+ |
| Test coverage | **129 passing** |
| Cost per full analysis run | ~$0.10 (Haiku) |
| Cost per YouTube Short | ~16 HeyGen credits (~$0.50) |
| Scheduled jobs | Daily digest · Daily radar · Weekly comment refresh · Weekly newsletter curation |
| External integrations | YouTube Data API v3 · Anthropic · HeyGen · OpenAI Whisper · Remotion · Buffer · Kit · Gmail MCP |

---

## Installation

```bash
# Clone repository
git clone https://github.com/joatsaint/enterprise-ai-pipeline.git
cd enterprise-ai-pipeline

# Install dependencies
pip install -r requirements.txt

# Install Whisper (for Shorts pipeline)
pip install openai-whisper

# Install Remotion (for motion graphics)
cd remotion/shorts && npm install && cd ../..

# Configure environment
cp .env.example .env
# Add: ANTHROPIC_API_KEY, YOUTUBE_API_KEY, HEYGEN_API_KEY, OPENAI_API_KEY
```

### Prerequisites
- Python 3.10+
- Node.js 18+ (for Remotion motion graphics)
- FFmpeg on PATH
- Anthropic API key
- YouTube Data API v3 key
- HeyGen account (Creator plan, ~$29/mo — for Shorts avatar rendering)

---

## Usage

```bash
# Research pipeline
python -m src.main channel "Channel Name"        # incremental download
python -m src.main group claude-code             # all channels in a group
python -m src.main index                         # rebuild knowledge base
python -m src.main analyze --group claude-code   # pain point extraction
python -m src.main ask "what skills do IT pros need for AI roles"

# YouTube Shorts
python -m src.main shorts --dry-run              # script only, no API calls
python -m src.main shorts                        # full pipeline from radar
python -m src.main shorts --pain-point "..."     # manual pain point override
python -m src.main shorts --variant a            # Remotion text cards only

# Daily operations
python -m src.main digest                        # daily transcript summary
python -m src.main curate-newsletters            # inbox → newsletter digest
python -m src.main loop                          # research → draft → review cycle

# Observability
python -m src.main status                        # at-a-glance pipeline summary
python -m src.main report                        # weekly AI-cost report
```

---

## Project Structure

```
enterprise-ai-pipeline/
├── src/
│   ├── main.py                   # Thin CLI — delegates to orchestrator
│   ├── orchestrator.py           # Pipeline coordinator + state management
│   ├── downloader/               # Transcript + comment fetching, channel registry
│   ├── converter/                # Raw transcript → structured Markdown
│   ├── classifier/               # AI-suggested content categorization
│   ├── analyzer/                 # Two-pass pain-point extraction
│   ├── knowledge_base/           # Indexer · cited Q&A · daily digest
│   ├── shorts/                   # YouTube Shorts pipeline (6 modules)
│   │   ├── pain_point_selector.py  # Reads Daily Radar, picks top sysadmin topic
│   │   ├── script_writer.py        # Claude Sonnet → 5-section script + screen hook
│   │   ├── heygen_renderer.py      # Voice-clone avatar via HeyGen v2 API
│   │   ├── whisper_transcriber.py  # Word-level timestamps + section frame matching
│   │   ├── top_half_renderer.py    # Remotion animated text cards (1080×1920)
│   │   ├── ffmpeg_stitcher.py      # Chromakey composite + captions + hook overlay
│   │   └── orchestrator.py         # 6-step idempotent state machine
│   ├── radar/                    # Daily audience radar (scan → score → draft)
│   ├── curator/                  # Gmail inbox → newsletter digest (MCP)
│   ├── trend_finder/             # Trend scan → relevance score → post draft
│   ├── publisher/                # Buffer scheduling + human approval gate
│   ├── funnel/                   # Kit cohort sync
│   └── utils/
│       ├── ai.py                 # Shared Claude helper · cost ledger · rate-limit retry
│       └── atomic.py             # Atomic file writes
├── remotion/shorts/              # React/Remotion motion graphics project
│   └── src/TextCard.tsx          # Animated brand-color section cards (1080×1920)
├── tests/                        # 129 passing
├── channels.example.json         # Template — real registry is git-ignored
├── newsletter_sources.example.json
└── .env.example                  # All required env vars documented
```

> `content-engine/`, `transcripts/`, `logs/`, `docs/`, and real config files are git-ignored — the repo ships code and `.example` templates, not private data.

---

## Error Handling

Production-grade error handling across all external API calls:

- **Rate limits (429)** — `call_with_retry()` in `src/utils/ai.py`: 60s → 120s exponential backoff, up to 3 attempts, applied to every Anthropic API caller in the system
- `NoTranscriptFound` — logged and skipped gracefully
- `TranscriptsDisabled` — caught specifically, processing continues
- API quota exhaustion — `[WARN]` logged, batch continues
- Generic failures — single retry with 5-second backoff, then skip with structured error log
- Already-downloaded content — detected via `download_log.json` and skipped (idempotent)
- Partial files — cleaned up before exit; a partial `.md` file is never left in the index
- Graceful shutdown — `KeyboardInterrupt` caught; current file finishes writing before exit

---

## Security

- API keys in `.env` with `os.environ.setdefault()` — system env takes precedence, cloud-ready
- `.env` gitignored — credentials never committed
- URL validation via `urlparse` at pipeline entry — malformed inputs rejected before any API call
- Randomized rate limiting — reduces bot detection signature on bulk requests
- Output directories scoped per-run — no cross-contamination between pipeline executions

---

## Built By

**Randy Skiles** — 25-year enterprise IT professional (infrastructure, systems, network operations) building AI automation tooling.

This repo is the research and content engine behind a content business targeting IT professionals navigating the AI transition. Every architectural decision is documented. Every pain point finding comes from real audience data — 47,000+ comments analyzed, not assumed.

- LinkedIn: [linkedin.com/in/randy-skiles](https://linkedin.com/in/randy-skiles)
- Actively developed — new pipeline stages added continuously

---

*Built with Claude Code · 129 tests · Deployed on Windows Task Scheduler · Shorts rendered with HeyGen + Remotion + FFmpeg*
