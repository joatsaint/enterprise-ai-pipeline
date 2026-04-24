# AI Orchestrator for Multi-Source Data Automation

> **Automated intelligence pipeline** that scrapes YouTube transcripts and audience comments at scale, extracts market intelligence using Claude AI, and generates actionable research reports — without human intervention.

[![Tests](https://github.com/joatsaint/youtube-downloader/actions/workflows/test-suite.yml/badge.svg)](https://github.com/joatsaint/youtube-downloader/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![Claude](https://img.shields.io/badge/AI-Claude%20Haiku-orange)](https://anthropic.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## What This Does

Most market research tools tell you what people are saying. This system tells you what they're **actually asking** — extracted from real audience behavior at scale.

**In one command**, this system:
- Downloads transcripts and top comments from any YouTube channel
- Classifies and indexes content by topic category
- Runs AI analysis to extract the most repeated questions, pain points, and desired outcomes
- Generates a ranked intelligence report ready for product and content decisions

**Result:** Market research that would take a human 40+ hours manually, completed in minutes.

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
│  • Pipeline sequencing  • Error handling + retry logic      │
│  • Run statistics    • Graceful shutdown                    │
└──────┬──────────────┬───────────────┬───────────────────────┘
       │              │               │
       ▼              ▼               ▼
┌──────────┐  ┌──────────────┐  ┌───────────────┐
│Transcript│  │   Comment    │  │   Markdown    │
│ Fetcher  │  │   Fetcher    │  │  Converter    │
│          │  │              │  │               │
│Webshare  │  │YouTube Data  │  │ Structured    │
│Rotating  │  │API v3        │  │ output with   │
│Proxy     │  │Top 100/video │  │ headers +     │
│          │  │              │  │ timestamps    │
└──────────┘  └──────────────┘  └───────────────┘
       │              │               │
       └──────────────┴───────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Knowledge Base                             │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Indexer   │  │Pain Point    │  │  Query Engine    │  │
│  │             │  │Extractor     │  │                  │  │
│  │Flat-file    │  │              │  │On-demand Q&A     │  │
│  │JSON index   │  │Two-pass AI   │  │against indexed   │  │
│  │159+ files   │  │analysis      │  │transcript library│  │
│  │             │  │~$0.10/run    │  │                  │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Intelligence Reports                           │
│   knowledge_base/reports/pain_points_YYYY-MM-DD.md         │
│                                                             │
│   • Top questions ranked by frequency                       │
│   • Top pain points with mention counts                     │
│   • Desired outcomes analysis                               │
│   • PDF product opportunities identified                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Real-World Use Cases

### 1. Market Intelligence & Scraping
```bash
# Download all content from a channel
python -m src.main channel "Matt Wolfe"

# Run across entire channel group
python -m src.main analyze --group ai-and-claude-code
```
**Output:** Ranked list of the most asked questions and pain points across 9 channels, 159 transcripts, and 2,900+ audience comments — updated in minutes.

### 2. Automated Monitoring
The system runs on Windows Task Scheduler during US market hours, continuously expanding the transcript library without manual intervention.

```
Task: Daily channel scan
Schedule: Weekdays 9 AM CST
Action: python -m src.main channel [channel-name]
Alert: New pain point reports generated automatically
```

### 3. Alert System — Pain Point Detection
```python
# Two-pass extraction identifies emerging pain points
# Pass 1: Questions audiences are asking
# Pass 2: Frustrations and blockers expressed

# Output flags HIGH/MEDIUM/LOW demand signals
# for content and product decisions
```

### 4. Intelligence Workflows
```
Channel Registry → Batch Download → Index → Extract → Report
     ↓                  ↓             ↓         ↓        ↓
channels.json    transcripts/    index.json  Claude   pain_points.md
9 channels       159 files       searchable  Haiku    ranked insights
```

---

## Key Technical Decisions

| Decision | Choice | Reasoning |
|---|---|---|
| AI Model | Claude Haiku | ~$0.10/run vs $0.40 Sonnet — adequate for classification tasks |
| Proxy | Webshare Rotating Residential | YouTube blocks cloud IPs — rotating residential avoids detection |
| Index | Flat-file JSON | Vector DB overhead not justified at <500 transcripts |
| Rate limiting | `random.uniform(2-7s)` | Fixed intervals create bot signature — randomized mimics human behavior |
| Error handling | Retry-once-then-skip | Never abort batch on single failure — idempotent by design |
| Credentials | `.env` + `os.environ.setdefault()` | System env vars take precedence — cloud-deployment ready |

---

## Pipeline Stats

| Metric | Value |
|---|---|
| Channels registered | 9 |
| Transcripts downloaded | 159 |
| Comment files analyzed | 29 |
| Test coverage | 39/39 passing |
| Cost per full analysis run | ~$0.10 |
| Pain point reports generated | 3+ |
| API calls handled | YouTube Data API v3 + Anthropic |

---

## Installation

```bash
# Clone repository
git clone https://github.com/joatsaint/youtube-downloader.git
cd youtube-downloader

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add: ANTHROPIC_API_KEY, YOUTUBE_API_KEY, WEBSHARE credentials
```

### Prerequisites
- Python 3.10+
- Anthropic API key (console.anthropic.com)
- YouTube Data API v3 key (console.cloud.google.com)
- Webshare proxy account (webshare.io — $3.50/month)

---

## Usage

```bash
# Add a channel to registry
python -m src.main add-channel

# Download single video
python -m src.main download "https://youtube.com/watch?v=..."

# Batch download entire channel
python -m src.main channel "Channel Name"

# Rebuild knowledge base index
python -m src.main index

# Run pain point extraction
python -m src.main analyze --group ai-and-claude-code

# Query the knowledge base
python -m src.main query "what skills do IT professionals need for AI roles"
```

---

## Project Structure

```
youtube-downloader/
├── CLAUDE.md                    # Architecture + Claude Code behavior rules
├── MASTER_PLAN.md               # Business pipeline and stage roadmap
├── PROJECT_CONTEXT.md           # ICP, offer definition, growth strategy
├── channels.json                # Channel registry with group tags
├── src/
│   ├── main.py                  # CLI entry point
│   ├── orchestrator.py          # Pipeline coordinator + state management
│   ├── downloader/
│   │   ├── channel.py           # Batch channel download + incremental mode
│   │   ├── transcript_fetcher.py # Proxy-enabled transcript extraction
│   │   └── comment_fetcher.py   # YouTube Data API comment fetcher
│   ├── converter/
│   │   └── to_markdown.py       # Raw transcript → structured Markdown
│   ├── analyzer/
│   │   └── pain_point_extractor.py # Two-pass Claude AI analysis
│   ├── knowledge_base/
│   │   ├── indexer.py           # Flat-file JSON index builder
│   │   ├── query.py             # On-demand Q&A against transcript library
│   │   └── digest.py            # Daily summary generator
│   └── channels/
│       └── registry.py          # Channel registry management
├── knowledge/
│   └── me/
│       └── voice.md             # Brand voice + content generation rules
├── docs/
│   ├── DECISIONS.md             # 8 architectural decision records
│   ├── CODE_REVIEW_CHECKLIST.md # AI code review protocol
│   ├── CONTENT_DRAFTS.md        # Ready-to-publish content
│   └── [scaffold prompts]       # Claude Code implementation prompts
├── transcripts/                 # Downloaded content library
│   └── [group]/[channel]/       # Organized by group and channel
├── knowledge_base/
│   ├── index.json               # Searchable transcript index
│   └── reports/                 # Pain point intelligence reports
└── tests/                       # 39/39 passing
```

---

## Error Handling

The pipeline implements production-grade error handling across all external API calls:

- `NoTranscriptFound` — logged and skipped gracefully
- `TranscriptsDisabled` — caught specifically, processing continues
- API quota exhaustion — `[WARN]` logged, batch continues
- Generic failures — single retry with 5-second backoff, then skip
- Already-downloaded content — detected and skipped (idempotent)
- Full run statistics — processed, skipped, retried counts at completion

---

## Security

- API keys loaded via `.env` with `os.environ.setdefault()` — system env takes precedence
- `.env` gitignored — credentials never committed
- URL validation via `urlparse` at pipeline entry — malformed inputs rejected
- Cloud environment detection — warns against running interactive downloads in restricted environments
- Randomized rate limiting — reduces bot detection signature

---

## Architectural Decisions

Full decision log with context, alternatives considered, and tradeoffs documented in [`docs/DECISIONS.md`](docs/DECISIONS.md).

---

## Built By

**Randy Skiles** — 25+ year IT professional pivoting into AI automation.

This project is the research engine behind a content business targeting IT professionals making the same pivot. Every architectural decision is documented. Every pain point finding is real data from 2,900+ audience comments.

- LinkedIn: [linkedin.com/in/randy-skiles](https://linkedin.com/in/randy-skiles)
- Live project: Actively developed, new channels added weekly

---

*Built with Claude Code · Tested with pytest · Deployed on Windows Task Scheduler*
