---
name: niche-research
description: "Surface the most relevant real stories in Randy's actual niche from the last 7 days, using Claude for Chrome to live-browse Reddit, X, and Google with verified publish dates. Use whenever Randy says 'research my niche', 'what's trending', 'find stories', 'this week's news', or asks what's happening in IT/AI-career/enterprise-AI right now. Fills a real, previously-documented gap: the project's existing Reddit RSS pipeline (src/trend_finder/source_scanner.py) cannot reach X/Twitter at all (session-cookie auth, not IP-based) — this skill can, because it drives an actual logged-in browser. Requires the Claude for Chrome extension."
---

# Niche Research

Adapted from charlie947/social-media-skills (MIT license) — reality-checked 2026-08-03,
cherry-picked as one of three genuinely non-duplicate skills found in that repo. Original
hardcoded British English and a blanket no-em-dash rule for Charlie Hills' own voice; both
removed here — this project's actual voice/register rules below fully override the source
repo's defaults, same pattern already used in `linkedin-hook-writer`.

## PROJECT GUARDRAIL — read FIRST, before any step below

1. **LOAD these anchors — they govern subject matter, not the source repo's defaults:**
   - `knowledge/me/icp_pain_map.md` — the ICP Core Pains, Themes, and Out-of-Scope list.
   - `knowledge/me/voice.md` — Randy's actual voice (formal B2B / operator register).
2. **ON-NICHE GATE (hard):** every story surfaced must map to ≥1 Core Pain in `icp_pain_map.md`
   (prefer the sharpest — P1/P3/P4) and sit inside a Theme. If a story can't name a P# and a
   Theme, it's off-niche — drop it, do not include it in the table.
3. **REGISTER:** standard American English, standard capitalization. Em dashes are fine —
   they're part of Randy's actual voice; the source repo's blanket ban does not apply here.
4. **This complements, not replaces,** the project's own Reddit RSS pipeline
   (`src/trend_finder/source_scanner.py`, see `reference_reddit_rss_fetch_method.md`). That
   pipeline already covers Reddit on a schedule. This skill's real new value is **X/Twitter
   access** (the RSS method explicitly cannot reach X — session-cookie auth, not IP-based)
   plus live, human-scroll-style Reddit/Google coverage for an on-demand, interactive research
   pass — not a replacement for the scheduled scanner.

---

## Prerequisites

This skill needs live browsing. Use this order of preference:

1. **Claude for Chrome extension** (preferred). Load the browser tools first if deferred —
   `ToolSearch` with `select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__tabs_create_mcp`
   — then confirm the extension is enabled and has permission on the current tab. If not,
   tell Randy:
   > Enable the Claude for Chrome extension and open a blank tab. I need to drive the browser
   > to scroll Reddit, X, and run Google searches with verified dates.
2. **WebSearch + WebFetch tools** as a fallback if Claude for Chrome isn't available — weaker
   on X (WebFetch cannot reach x.com reliably) and on feed-scroll discovery, but usable for
   the Google-search leg.

Pick the best available path and continue. If neither Reddit nor X can actually be covered,
say so plainly rather than faking the scan — matches this project's Search Before Assuming
discipline (real search, not a guessed answer).

## Step 1. Gather the niche

Default to pulling from `knowledge/me/icp_pain_map.md`'s Core Pains and Themes — Randy's niche
is already documented there, no need to ask unless he wants to research something adjacent
(e.g. a specific audience segment like landlord/GLP-1 Facebook groups, which fall outside
`icp_pain_map.md`'s scope). If researching one of those adjacent audiences, ask Randy to name
it directly rather than guessing.

## Step 2. Browse like a human researcher

Drive the browser through these actions in order. Verify publish dates on every item. Exclude
anything older than 7 days from today (check the real injected timestamp, not a guess) without
exception.

### 2a. Reddit feed scanning

1. Navigate to the relevant subreddits already known from `channels.json`'s research groups
   and from real threads mined this session (r/sysadmin, r/ITCareerQuestions, r/ClaudeAI,
   r/ArtificialIntelligence, r/webdev, r/Anthropic, etc.) — check `src/trend_finder/
   source_scanner.py`'s `SUBREDDITS` list for the current full set before starting.
2. Scroll each feed, load more posts, open niche-relevant posts.
3. Check the "posted X days ago" timestamp on each. Discard anything older than 7 days.

### 2b. X (Twitter) scanning — the real new capability this skill adds

1. Navigate to https://x.com/home (For You feed) or a targeted search.
2. Scroll multiple screens, open full threads for niche-relevant posts.
3. Check the post timestamp on each thread. Discard anything older than 7 days, even if
   engagement is high.

### 2c. Google web search

Run searches scoped to Randy's actual niche terms (from `icp_pain_map.md`), Tools → Any time →
Past week. For each promising result: open the page, locate the visible publish date, verify
it's within 7 days, exclude if missing/unclear/older.

## Step 3. Synthesize into themes

Group related items into themes. Select themes showing at least two of: strong attention/
discussion, clear disagreement, novel insight, real-world implications for the niche.

## Step 4. Output

First line before the table:

```
As of [real date from the injected timestamp]
```

Then a markdown table:

```
| Theme / Story | Platforms | Key Communities/Accounts | Links | Attention Signals | What's Being Debated | Which Core Pain (P#) | Shareable Angle |
```

No prose outside the table.

## Step 5. Offer the next move

After the table, ask:

> Any row here you want turned into a post? I can run it through `create-next-article` for a
> full article, or `linkedin-hook-writer` for hook options on a shorter post.

## Rules

- Never invent links, metrics, or dates.
- Exclude anything older than 7 days without exception — verify against the real injected
  timestamp, never a guess.
- Table only at the end. No commentary, no summary paragraph.
- If fewer themes pass the on-niche gate than expected, say so — do not pad with off-niche or
  weak items just to hit a target count.
- If Claude for Chrome isn't available and WebSearch/WebFetch can't cover X, tell Randy what's
  missing rather than faking the scan.
- Standard American English, em dashes allowed — this project's `voice.md` governs register,
  not the source repo's defaults.

## Gotchas

- **X/Twitter is the actual reason this skill exists** — the project's own RSS-based Reddit
  scanner (`src/trend_finder/source_scanner.py`) already covers Reddit on a schedule and hits a
  hard wall on X (session-cookie auth). Don't duplicate effort scanning Reddit here if the
  scheduled scanner already has recent coverage — check `logs/` or the last digest run first.
- **Untested as of 2026-08-03** — adapted from the source repo's SKILL.md but not yet run
  end-to-end in this project. First real run should be treated as a validation pass, not
  assumed to work exactly as written.
