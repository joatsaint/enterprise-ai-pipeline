# Zapier MCP Multi-Platform Content Automation Handoff
## Complete Platform Reference & Strategy Guide for Claude Code

**Status:** Ready for Claude Code implementation  
**Created:** June 2026  
**Scope:** LinkedIn, Instagram, Pinterest, Twitter/X, TikTok, Facebook  
**Tier:** Zapier Free Plan (Phase 1) → Paid (Phase 2, if ROI justifies)

---

## Table of Contents
1. [Overview & Context](#overview--context)
2. [Platform Specifications Matrix](#platform-specifications-matrix)
3. [Detailed Platform Guides](#detailed-platform-guides)
4. [Content Type Requirements](#content-type-requirements)
5. [Posting Limits & Rate Limits](#posting-limits--rate-limits)
6. [Strategic Automation Workflows](#strategic-automation-workflows)
7. [Free Plan Constraints & Paid Plan Benefits](#free-plan-constraints--paid-plan-benefits)
8. [Error Handling & Edge Cases](#error-handling--edge-cases)

---

## Overview & Context

### Mission
Enable automated, multi-platform content distribution via Zapier MCP for Randy Skiles' IT-to-AI transition brand. Content source: `linkedin_atomizer.py` output (atomized articles into multiple formats). Goal: Maximize reach with minimal manual overhead while respecting each platform's unique audience, algorithms, and technical constraints.

### Key Principles
- **Atomic content units:** One article → five atomized pieces (text post, image post, carousel, newsletter hook, video script)
- **Platform-native formatting:** Each platform gets properly sized images, tailored copy, platform-specific metadata
- **Distribution discipline:** Respect posting limits; maintain quality over quantity; avoid spam filters
- **Manual-to-automated ladder:** Start manual or semi-manual on free Zapier tier; automate fully once patterns established
- **Randy's final call:** All automation decisions are reviewed by Randy; Zapier is a *tool*, not the *decision-maker*

---

## Platform Specifications Matrix

| Platform | Character Limit (Post) | Hidden Display Cap | Content Types | Image Size | Video | Rate Limit | Optimal Frequency |
|----------|------------------------|-------------------|----------------|-----------|-------|-----------|------------------|
| **LinkedIn** | 3,000 | ~210 chars | Text, Image, Carousel, Article, Video | 1200x627px | ✅ MP4/MOV | 2 posts/24h (rate-limited API) | 2-5/week |
| **Instagram** | 2,200 | ~125 chars | Feed Post, Carousel, Reels, Stories | 1080x1350px | ✅ MP4 (up to 10min) | 100/24h* | 3-5/week |
| **Pinterest** | 500 (description) | N/A (search-driven) | Pins (static), Rich Pins, Video Pins | 1000x1500px (min) | ✅ MP4 (max 30min) | Unlimited public | 5-15/day |
| **Twitter/X** | 280 (Free) / 25,000 (Premium) | Visible all | Text, Image, Thread, Video | 1024x512px | ✅ MP4 | 500/month (Free) | 1-3/day possible |
| **TikTok** | 4,000 | N/A (title-driven) | Video, Carousel, Text overlay | N/A (native) | ✅ Required | ~6-15/day published | 2-5/week |
| **Facebook** | 63,206 | ~477 chars (desktop) / ~125 (mobile) | Text, Image, Carousel, Video, Story | 1200x628px | ✅ MP4/MOV | 25/24h | 1-2/day |

*Instagram's 100/24h limit includes posts + reels + stories combined*

---

## Detailed Platform Guides

### LinkedIn
**Best for:** Professional IT audience (Randy's primary ICP)

#### Content Types Available
- **Native Posts** (text + image): 1200x627px image, 3,000 char caption
- **Carousels:** Multiple cards (5-10), each with image + text
- **Articles:** Native LinkedIn publishing (100,000 char limit) — perfect for long-form field manual / technical deep-dives
- **Video:** MP4/MOV, 1200x627px, auto-play on feed
- **Polling:** Text-based engagement (optional)

#### Character Limits & Display Rules
- **Post limit:** 3,000 characters
- **Critical detail:** Only ~210 characters visible before "See more" link
- **Strategy:** Front-load hook (30 words max) with the strongest value statement or story hook
- **Hashtags:** 3-5 highly relevant tags; avoid hashtag spam
- **Links:** Full URLs display; shortening optional but not required

#### Posting Rules & Limits
- **Daily limit:** No official cap, but algorithm penalizes spam (recommendation: 2 quality posts per week max for Randy's brand voice)
- **Rate limit:** LinkedIn API is limited to 2 API calls per 24-hour rolling window *per user token* — this is important for Zapier automation
- **Spacing:** No forced spacing required; however, posting same content to multiple profiles triggers detection
- **Best times:** Tuesday–Thursday, 10–11 AM CST (Randy's current schedule via Buffer)

#### Image & Video Specs
- **Image:** 1200x627px (16:9 aspect ratio), JPG/PNG, max 10MB
- **Video:** MP4/MOV, 1200x627px, max 5GB, 600 sec (10 min)
- **Carousel cards:** 1200x627px per card, up to 10 cards

#### LinkedIn-Specific Gotchas
- **API rate limit is ruthless:** With only 2 calls/24h, you cannot post 3+ times per day via API automation. Zapier free tier will hit this wall fast. Solution: Use Zapier to *draft* or *schedule*, then manually publish via LinkedIn's native composer for high-frequency posting.
- **Article vs. Post:** Articles show in Randy's profile page and feed, offering higher discoverability. Posts are time-sensitive. Choose strategically.
- **Links don't boost reach:** LinkedIn's algorithm favors native content over external links. If promoting field manual or lead magnet, consider an image + text post instead of link post.

#### Free Zapier Strategy
- Use Zapier to *queue* LinkedIn posts (store in Airtable or Google Sheets)
- Randy manually publishes via LinkedIn's native interface (respects scheduling, no API call overhead)
- Track posts in LINKEDIN_TRACKER.md for analytics pull later

#### Paid Zapier Strategy
- Direct API posting to LinkedIn (if Zapier's plan supports >2 posts/24h)
- Automatic formatting of article content into LinkedIn native articles
- Scheduled posting respecting the 2-call/24h limit with buffer time

---

### Instagram
**Best for:** Visual storytelling, IT culture, younger professionals

#### Content Types Available
- **Feed Posts** (single image or carousel): 1080x1350px, 2,200 char caption
- **Carousel Posts** (2–10 images): 1080x1350px each, single 2,200 char caption for all cards
- **Reels:** Vertical video (9:16), 15 sec–10 min, 4,000 char description
- **Stories:** 1080x1920px, vertical, 15 sec per story, 100 stories/day limit
- **IGTV** (deprecated in 2024, use Reels instead)

#### Character Limits & Display Rules
- **Feed caption limit:** 2,200 characters
- **Critical detail:** Only ~125 characters visible before "more" link (mobile); 150 chars on desktop
- **Strategy:** Hook first (15–20 words), then context. Hook must answer "why should I care?"
- **Hashtags:** Max 30 per post, but 3–5 highly relevant tags perform better (algorithm evolved; hashtag spam triggers shadowban)
- **Links:** NOT clickable in captions (links only work in bio); lead people to bio link via CTA

#### Posting Rules & Limits
- **Feed posts:** 1–3/day recommended; no official hard cap, but >5/day triggers spam detection
- **Stories:** Up to 100/day, but realistic limit is 5–10/day for normal accounts
- **Reels:** 1 per day recommended; algorithm heavily favors reels
- **Carousel posts:** Count as 1 post toward daily limit
- **Spacing:** Avoid posting identical content within 24 hours of previous post

#### Image & Video Specs
- **Feed image:** 1080x1350px (9:16 aspect), JPG/PNG, <8MB
- **Feed carousel:** 1080x1350px per card, max 10 cards
- **Reel:** MP4, 9:16 aspect, 15 sec–10 min, max 8GB
- **Story:** 1080x1920px, MP4 or image, max 8MB
- **Text overlays:** Add directly in post editor; captions are secondary

#### Instagram-Specific Gotchas
- **Text captions matter less than video content:** For Reels especially, the text overlay *inside* the video is more critical than the caption below. Claude should prioritize motion graphic copy over caption copy.
- **Bio link is your only clickable link:** All CTAs must direct to a single bio link (use Linktree-style or direct to rskiles.com/field-manual-waitlist). Every CTA in captions must say "Link in bio."
- **Hashtag strategy shifted:** Algorithm now relies on *semantic context* of caption, not tag matching. Using all 30 hashtags looks spammy; use 3–5 highly precise tags.
- **Account age matters:** Newer accounts (<6 months) have tighter rate limits on follows, comments, likes. Randy's account is mature, so this is low concern.
- **Shadowbanning risk:** Excessive automation, bot-like commenting, hashtag spam, or posting >5 times/day can trigger temporary shadowban (content stops showing in feeds). **Solution:** Keep post frequency low (3–5/week), space posts 4+ hours apart, use authentic voice.

#### Free Zapier Strategy
- Zapier drafts Instagram post (caption + image)
- Randy reviews and posts manually via mobile app (preserves authenticity, avoids shadowban)
- Track posts in a shared spreadsheet

#### Paid Zapier Strategy
- Direct Instagram Business API integration (requires verified business account)
- Automatic reel description + caption generation
- Scheduled posting (up to 24-hour advance scheduling via Meta's native scheduler)

---

### Pinterest
**Best for:** Long-form discovery, IT professionals researching solutions, evergreen content

#### Content Types Available
- **Pins** (static images): 1000x1500px (min), text overlay optional
- **Rich Pins** (with metadata): Product pins, recipe pins, article pins (article pins include headline + description snippet)
- **Video Pins:** MP4, 9:16, 15 sec–30 min, auto-plays in feed
- **Idea Pins** (carousel): Multiple cards, similar to TikTok carousel
- **Boards:** Organize pins by topic (Randy could organize by content pillar: "The Flood," "What AI Can't Do," etc.)

#### Character Limits & Display Rules
- **Pin description limit:** 500 characters (publicly visible)
- **Pin title limit:** 100 characters (appears in search results + pin preview)
- **No visible truncation:** Descriptions show in full on pin detail page; titles fully visible in search
- **Strategy:** Optimize for Pinterest's search engine, not feed algorithm. Use keywords in title + description. Pins have 4-year shelf life (unlike Instagram's 24-hour spike).

#### Posting Rules & Limits
- **Daily limit:** Technically no hard cap for organic pins; recommendation is 5–15/day for brands
- **Rate limits:** No published API rate limit; treat as unlimited for practical purposes
- **Scheduled pins:** Can schedule up to 100 pins in advance
- **Best times:** No strong "best time" on Pinterest; evergreen content performs consistently across hours/days

#### Image & Video Specs
- **Pin image:** 1000x1500px (2:3 aspect), JPG/PNG, max 20MB
- **Video pin:** MP4, 9:16 aspect, 15 sec–30 min, max 500MB
- **Text overlay:** Max ~40 chars visible on pin preview; detailed text goes in description
- **Pin title:** 100 chars (feeds search algorithm)

#### Pinterest-Specific Gotchas
- **It's a search engine, not a social network:** People come to Pinterest to *find* content, not follow friends. Keyword optimization is everything.
- **Pins live forever:** A pin can drive traffic 6–12 months after posting. Don't worry about frequency; quality matters.
- **Link pins:** Every pin *must* link somewhere (rskiles.com, lead magnet landing page, Gumroad product). Unlinked pins are not pinnable.
- **Rich Pins get preference:** Adding metadata (headline, description, article schema) gives pins a boost in search ranking.
- **No bot-like behavior:** Avoid pinning the same image 10 times per day with different text. Mix up images and timing.

#### Free Zapier Strategy
- Zapier formats pin title + description (optimized for Pinterest search)
- Generates pin image or pulls from Canva design
- Queue pins in Airtable for Randy to manually pin to boards (respects Pinterest's anti-bot policies)
- Batch pin 5–10 pins on Monday morning (respects rate limits, looks authentic)

#### Paid Zapier Strategy
- Direct Pinterest API integration (requires app approval)
- Automatic pinning to specific boards
- Scheduled pin release (daily 1–2 pins over several weeks from single atomized article)

---

### Twitter/X
**Best for:** Real-time IT community, hot takes, quick engagement

#### Content Types Available
- **Posts** (text only): 280 chars (free) or 25,000 chars (premium)
- **Posts + Image:** 280 chars + 1–4 images (1024x512px each)
- **Posts + Video:** 280 chars + 1 video (MP4, 15 min max)
- **Threads:** Multiple posts chained together (each post 280 chars)
- **Quote posts:** Reply to existing post with commentary

#### Character Limits & Display Rules
- **Free user limit:** 280 characters (strict)
- **Premium limit:** 25,000 characters (Randy not on premium, so assume 280)
- **Critical detail:** All URLs count as 23 characters regardless of actual length
- **Strategy:** Be punchy. Lead with hook (20 words max), then detail. Threads are better for longer stories.

#### Posting Rules & Limits
- **Monthly limit (free):** 500 posts/month (X's "API v2" free tier includes this quota)
- **Daily estimate:** ~16 posts/day (500÷30 days), but X doesn't enforce daily hard cap, only monthly
- **Spacing:** No forced spacing; however, posting >3 identical posts/hour triggers spam detection
- **Rate limit:** 500 posts/month quota resets monthly

#### Image & Video Specs
- **Image:** 1024x512px (16:9), JPG/PNG, max 5MB, up to 4 per post
- **Video:** MP4/MOV, 1024x512px or 9:16, up to 15 min, max 512MB
- **GIF:** Supported, max 15MB

#### Twitter/X-Specific Gotchas
- **Algorithm favors engagement over recency:** A post from 3 hours ago can still trend if replies/RTs spike. Don't assume posts disappear after 2 hours.
- **Ratio culture:** Aggressive ratio (ratio'd = more replies than RTs/likes) can hurt visibility. Avoid controversial takes unless intentional.
- **Premium is different:** Randy isn't on premium, so 280-char limit is hard ceiling. Threads (chained posts) are the workaround for longer stories.
- **Hashtag performance declined:** X's algorithm doesn't weight hashtags heavily anymore. Use 1–2 maximum.
- **Link cards:** URLs auto-expand into card previews (headline + preview image from linked page). Important for lead magnet promotion.

#### Free Zapier Strategy
- Zapier drafts tweets (keeps them under 280 chars)
- Randy reviews and posts manually (builds engagement through replies)
- Use threads for longer stories (Zapier chains multiple 280-char posts)

#### Paid Zapier Strategy
- Direct X API integration (requires developer account approval)
- Automatic thread composition (break long copy into 280-char chunks, post as thread)
- Scheduled posting (no native X scheduler on free tier, but Zapier can queue)

---

### TikTok
**Best for:** Viral reach, younger IT professionals, short-form video content

#### Content Types Available
- **Videos:** MP4, 9:16, 15 sec–10 min, native TikTok editor required for optimal reach
- **Carousels:** Multiple short clips stitched together
- **Duets/Stitches:** Responses to other videos (engagement play)
- **Text-heavy posts:** Text overlay + trending audio (Randy's "motel story" energy)

#### Character Limits & Display Rules
- **Caption limit:** 4,000 characters (expanded for SEO)
- **Visible in feed:** Title/first line critical; full caption hidden until user taps
- **Strategy:** Hook in first 3 seconds of video is more important than caption. Caption is for SEO/search indexing.
- **Hashtags:** #FYP (For You Page) not required but used heavily; 3–5 relevant hashtags + trending hashtag

#### Posting Rules & Limits
- **Published daily limit:** ~6–15 posts/day (no official cap; varies by account age + follower count)
- **Rate limit (API):** 6 requests/minute per user token for initiating posts (very restrictive)
- **Scheduling:** Very limited; TikTok prefers immediate posting (no native scheduler)
- **Content approval:** Unaudited apps forced to private visibility (see "Zapier Constraints" below)

#### Image & Video Specs
- **Video:** MP4, 9:16 aspect (1080x1920px minimum), 15 sec–10 min, max 287.6MB, 30 fps max
- **Thumbnail:** Auto-generated; can customize but must be from video frame
- **Audio:** Native TikTok sounds perform better than external audio; trending audio = visibility boost

#### TikTok-Specific Gotchas
- **API restrictions are harsh:** TikTok's Content Posting API requires app audit approval; unapproved apps can only post to *private* visibility. **This means Zapier automation may force posts to private.** Workaround: Use Zapier to draft, Randy posts manually via app (ensures public visibility).
- **First 3 seconds are everything:** Slow intro = scroll away. Video *must* hook in first frame.
- **Trending audio is key:** Using trending audio in first 2 weeks = 3x visibility boost. Static voice-over without trending audio = limited reach.
- **No link in caption:** Links don't work in TikTok captions (mobile web links only in bio). CTAs must be "link in bio" or direct follow.
- **Posting frequency ≠ virality:** Posting 10 videos/day won't make a bad video viral. Quality + hook + trending audio = virality.

#### Free Zapier Strategy
- **NOT RECOMMENDED for TikTok:** Zapier's TikTok posting will force content to private (due to unaudited app status). 
- **Best approach:** Use Zapier to organize video script + trending audio suggestion, Randy posts manually via TikTok app.
- **Alternative:** Randy manually re-edits CapCut content into TikTok-native format (9:16, trending audio), then posts natively.

#### Paid Zapier Strategy
- **Requires TikTok app audit:** If Zapier integrates with audited TikTok app, posts will be public
- **Best case:** Zapier schedules/queues posts; Randy reviews + publishes via app (retains control, avoids audit risks)
- **Worst case:** Full automation with risk of platform policy violation or audited app revocation

---

### Facebook
**Best for:** Broad audience, older demographics, community engagement

#### Content Types Available
- **Posts** (text only): 63,206 chars (longest of any platform)
- **Posts + Image:** Single image (1200x628px)
- **Carousels:** 2–10 images, carousel-style
- **Video:** MP4/MOV, auto-plays in feed
- **Stories:** Vertical, 1080x1920px, 24-hour lifespan
- **Polls:** Text + options (engagement driver)

#### Character Limits & Display Rules
- **Post limit:** 63,206 characters (practically unlimited)
- **Critical detail:** Posts truncate at ~477 chars (desktop) and ~125 chars (mobile) with "See More" link
- **Strategy:** Hook hard in first 80 characters. Posts under 80 chars get 66% higher engagement.
- **Hashtags:** 1–3 relevant hashtags; avoid hashtag spam

#### Posting Rules & Limits
- **Business page daily limit:** 25 posts/day max (hard cap)
- **Personal profile:** Recommendation is 5–10/day to avoid spam detection
- **Spacing:** Wait at least 20 minutes between posts to avoid spam filter
- **Optimal:** 1–2 strong posts/day (Randy's target)

#### Image & Video Specs
- **Image:** 1200x628px (16:9), JPG/PNG, max 4MB
- **Carousel:** 1200x628px per card, 2–10 cards
- **Video:** MP4/MOV, 1200x628px, max 4GB, 240 min (4 hours)
- **Story:** 1080x1920px, MP4/image, max 4MB

#### Facebook-Specific Gotchas
- **Algorithm heavily weights engagement:** Likes, comments, shares matter more than reach. Posts that spark conversation (polls, questions) perform better.
- **Video performs better than text:** Native Facebook video (uploaded directly, not YouTube link) gets algorithmic boost.
- **Organic reach is limited:** Facebook prioritizes paid ads over organic posts. Expect lower organic reach; use to nurture existing audience, not acquire new.
- **Personal profile vs. page:** Business page posts reach followers; personal profile posts (if Randy posts as himself) reach friends + algorithm spillover. Both have different rate limits.

#### Free Zapier Strategy
- Zapier drafts Facebook post (image + caption)
- Randy reviews and posts manually via Facebook's composer
- Use polling feature for engagement (Zapier can help draft poll options)

#### Paid Zapier Strategy
- Direct Facebook Graph API integration
- Automatic posting to page (respects 25 posts/day limit)
- Cross-posting to Facebook Pages + personal profile simultaneously

---

## Content Type Requirements

### Text Post (LinkedIn, Twitter, Facebook)
- **Purpose:** Drive engagement, start conversation, share hot take
- **Character range:** 
  - Twitter: 280 chars (hard)
  - LinkedIn: 1,500–3,000 chars (optimal: 1,500–2,000 for mobile readability)
  - Facebook: 150–500 chars (optimal <80 for engagement boost)
- **Structure:**
  1. Hook (20–30 words): Why should reader care?
  2. Context (40–80 words): Story setup or problem statement
  3. Bridge (30–50 words): IT → AI transition angle
  4. CTA (15–20 words): What action? (link in bio, engage, reply)
- **Voice:** Raw Randy (authentic, specific, comma-heavy)
- **Example hook:** "I ran enterprise IT from a motel that banned prostitution. Here's what I learned about staying nimble when everything's on fire."

### Image Post (Instagram, Pinterest, Facebook)
- **Purpose:** Visual storytelling, education, brand aesthetic
- **Image specs:**
  - Instagram: 1080x1350px (9:16)
  - Pinterest: 1000x1500px (2:3)
  - Facebook: 1200x628px (16:9)
- **Requirements:**
  - Article title overlaid (readable on mobile)
  - Cinematic lighting, realistic people/environments
  - Subtle humor without cartoonish feel
  - 1-inch white border (for brand consistency)
- **Handoff:** Request from Claude asking "Post or Article layout?" before generating image prompt

### Carousel Post (Instagram, Facebook, LinkedIn)
- **Purpose:** Tell multi-part story, educate step-by-step, showcase portfolio work
- **Specs:**
  - Instagram: 2–10 cards @ 1080x1350px, single 2,200-char caption
  - Facebook: 2–10 cards @ 1200x628px, single 63k-char caption
  - LinkedIn: 5–10 cards @ 1200x627px, single 3,000-char caption
- **Structure:** Each card = one idea/lesson
  - Card 1: Hook (visual + 1-line promise)
  - Cards 2–N: Progression (context → insight → action)
  - Final card: CTA (link, sign-up, follow)
- **Caption:** Tells the meta-story (why these cards matter), not card-by-card narration

### Video Post (TikTok, Instagram Reels, YouTube Shorts)
- **Purpose:** Viral reach, storytelling with motion, trendy engagement
- **Specs:**
  - TikTok: MP4, 9:16 (1080x1920px), 15 sec–10 min, trending audio critical
  - Reels: MP4, 9:16, 15 sec–10 min, CapCut-native format preferred
  - YouTube Shorts: MP4, 9:16, 15–60 sec
- **Structure:**
  - 0–3 sec: Hook (text overlay or motion graphic)
  - 3–15 sec: Story setup or value prop
  - 15–25 sec: Payoff or lesson (for longer videos, maintain momentum)
  - 25–end: CTA or brand moment
- **Voice:** Fast, punchy, text-heavy overlays (captions often off)
- **Audio:** Trending sounds > original voice-over (for TikTok/Reels reach)

### Newsletter/Email Hook (ConvertKit, substack via Zapier)
- **Purpose:** Drive lead magnet signups, nurture waitlist
- **Character limit:** 160 chars for subject line, 300–500 for preview text
- **Structure:**
  1. Subject: Curiosity gap or strong promise (40–60 chars)
  2. Preview text: Extend promise or tease content (100–150 chars)
  3. Body: Newsletter signup CTA + linked article
- **Example:** Subject: "The Skills Your Boss Can't Automate" Preview: "25-year IT pro breaks down what AI won't replace (and why you're actually early)"

---

## Posting Limits & Rate Limits

### Hard Caps (Free/Paid Zapier)

| Platform | Daily Limit | Monthly Limit | Per-Minute Limit | Notes |
|----------|-------------|---------------|-----------------|-------|
| **LinkedIn** | No official cap | N/A | 2 API calls/24h | API is the bottleneck; native posting unlimited but algorithmically penalized >2/day |
| **Instagram** | 100 (posts+reels+stories combined) | N/A | None published | Organic posting no official limit; API has undocumented limits (3–5/day safe) |
| **Pinterest** | No official cap | N/A | None published | Recommend 5–15/day; evergreen content has no expiry |
| **Twitter/X** | No daily cap | 500/month | None published | Monthly quota resets; ~16 posts/day average |
| **TikTok** | ~15 (estimates vary) | N/A | 6 reqs/min | API posting requires audit; unaudited posts forced private |
| **Facebook** | 25 (business page) | N/A | None published | Personal profile: ~5–10/day safe; business page hard cap 25/day |

### Recommended Posting Schedule (To Respect Algorithms & Avoid Spam Flags)

```
WEEKLY RHYTHM (Randy's current approach):

Monday: 
  - Pinterest: 5 pins (atomized article repurposing)
  - Check analytics from previous week

Tuesday 10:05 AM CST:
  - LinkedIn: 1 article or native post (main brand push)
  - Twitter/X: 1–2 posts (quick hits, threads)
  - Facebook: 1 post (reach out to broader network)

Wednesday:
  - Instagram: 1 Reel or carousel post (mid-week engagement)

Thursday 10:05 AM CST:
  - LinkedIn: 1 post (buffer for engagement)
  - Twitter/X: 1–2 posts (hot takes, replies to comments)

Friday–Sunday:
  - Organic community management (no scheduled posts)
  - Repost/retweet comments, engage with audience
  - Pinterest: Batch 5 pins (evergreen content, low-effort engagement)

MONTHLY:
  - 8–10 LinkedIn posts (2 per week)
  - 12–20 Instagram posts (3–5 per week)
  - 30–60 Pinterest pins (5–15 per day, batch)
  - 30–60 Twitter posts (16/day max across month)
  - 1–2 TikTok posts (if native posting, not API automation)
  - 4–8 Facebook posts (1–2 per day, 4–5 days/week)
```

### What Triggers Spam Detection & Account Restrictions

- **Instagram:** >5 posts/day, identical hashtag-only comments, bot-like engagement, identical content reposted within 24 hrs
- **LinkedIn:** >2 API posts/24h, identical posts to multiple profiles, external link spam
- **Facebook:** Posting <20 min apart, >25 posts/day (page), promotional link spam
- **Twitter/X:** >10 posts/hour, identical RT of same post, bot-like follow/unfollow
- **TikTok:** Posting identical videos multiple times, link spam, policy violation (audited app status)
- **Pinterest:** Pinning same image 10x/day, pinning non-existent links, bot-like repinning

---

## Strategic Automation Workflows

### Workflow 1: Article Atomization → Multi-Platform Distribution

**Trigger:** Randy publishes new article (stored in GitHub + `/mnt/project/`)

**Steps:**
1. Claude runs `linkedin_atomizer.py` → outputs 5 formats:
   - LinkedIn post (1,500–2,000 chars + hook)
   - Instagram caption (2,000 chars, hook-first)
   - Pinterest description (500 chars + keywords)
   - Twitter thread (3–5 tweets @ 280 chars each)
   - Newsletter teaser (300–500 chars)

2. Zapier receives atomized content (via CSV/Airtable input OR manual Claude paste)

3. Zapier *queues* content (stores in Airtable "Queue" table with platform, copy, image, scheduling)

4. Randy reviews queue Monday morning:
   - Approve/edit copy per platform
   - Assign images (auto-fetch from Canva or manual upload)
   - Set publish dates (respecting posting limits)

5. Zapier triggers on approved row:
   - **LinkedIn:** Drafts post (Zapier → LinkedIn); Randy manually publishes (respects API limit)
   - **Instagram:** Drafts post; Randy manually publishes (avoids shadowban risk)
   - **Pinterest:** Auto-pins to board (5 pins per article, staggered over 1 week)
   - **Twitter:** Auto-tweets thread (each 280-char chunk as individual tweet, chained via quote-tweet)
   - **Facebook:** Drafts post; Randy manually publishes
   - **TikTok:** Drafts caption; Randy posts manually via app (ensures public, not private)

**Free Zapier Tier:** 
- Automations: 100/month (sufficient for ~2 articles/week)
- Airtable integration (track queue status)
- Webhook triggers (webhook → Zapier → queue)

**Paid Zapier Tier:**
- Unlimited automations
- Direct API posting (LinkedIn, Facebook, Twitter)
- Scheduled publishing (24-hour advance queue)

---

### Workflow 2: LinkedIn Engagement → Cross-Platform Amplification

**Trigger:** High-performing LinkedIn post (>100 comments/5K impressions)

**Steps:**
1. Zapier monitors LinkedIn post metrics (via Zapier → Buffer or manual daily check)
2. If post hits engagement threshold, Zapier:
   - Pulls post copy + image
   - Shortens copy for Twitter (280 chars)
   - Adapts image for Instagram (adjust aspect ratio if needed)
   - Drafts Twitter thread (expand post into 5-tweet narrative)
   - Drafts Instagram carousel (break insights into 5 cards)

3. Randy reviews & publishes within 24–48 hours (strike while hot)

**Free Zapier Tier:**
- Conditional logic (IF engagement >100 comments THEN trigger)
- Airtable lookup (cross-reference article to existing assets)

---

### Workflow 3: Lead Magnet Promotion (Evergreen)

**Trigger:** New lead magnet published (e.g., "Steel and the Server Room" PDF)

**Steps:**
1. Zapier creates promotional content per platform:
   - **LinkedIn:** "New resource: [title]. Free PDF—link in bio"
   - **Instagram:** Image (design from Canva) + "Grab the free guide (bio link)"
   - **Pinterest:** Rich pin (title + description + link to landing page)
   - **Twitter:** Thread (3–5 tweets, each highlighting one insight from PDF)
   - **Facebook:** Post + image + "Download now (link in bio)"
   - **TikTok:** Voiceover script (Randy records quick 30-sec hook)

2. Zapier schedules posts on rotating cycle:
   - Week 1: LinkedIn + Twitter (launch)
   - Week 2: Instagram + Pinterest (broad reach)
   - Week 3: Facebook + TikTok (re-engagement)
   - Repeat every 4 weeks (evergreen promotion)

3. Zapier tracks clicks to landing page (via utm_source + utm_medium)

**Free Zapier Tier:**
- Schedule 100 posts/month (sufficient for rotating promotion)
- Basic UTM tracking

---

## Free Plan Constraints & Paid Plan Benefits

### Zapier Free Tier

**Limits:**
- 100 automations per month (runs)
- 2 steps per automation (e.g., trigger + 1 action; to do more, chain automations)
- 1 task/step per minute (throughput)
- No advanced filters/logic beyond simple IF/THEN
- No Airtable integration (if primary storage)
- No webhooks or custom integrations

**What This Means:**
- Can run ~3 workflows per day (100 automations ÷ 30 days)
- Simple workflows only (e.g., "Form submission → send email"; not "Form → AI formatting → multi-platform posting")
- Manual review gates needed (Randy reviews before publishing)

**Workaround:** Zapier-to-Airtable-to-Claude (multi-step: Zapier queues, Claude reviews, Zapier publishes)

**Best Use:** 
- Zapier → Airtable (queue content)
- Manual trigger (Randy runs Zapier zap manually when ready)
- Batch scheduling (all posts for week at once, respects rate limits)

---

### Zapier Paid Plans (Premium/Advanced)

**Premium Tier ($19.99/mo):**
- Unlimited automations
- 5 steps per automation (more complex workflows)
- 15 tasks/minute (faster throughput)
- Airtable integration included
- Webhook support
- **Cost:** $20/mo (vs. current Buffer $6/mo)

**Advanced Tier ($49/mo):**
- Everything Premium +
- 10 steps per automation
- 100 tasks/minute
- Custom integrations (Slack, Discord, etc.)
- Advanced filters + multi-conditional logic

**When to Upgrade:**
- After first month of free tier usage (measure ROI)
- If Randy sees >10 signups/month from atomized content
- If posting 2+ articles/week (automation pays for itself in saved time)

**ROI Calculation:**
- Time saved (manual posting across 6 platforms): 30 min/article × 2 articles/week = 1 hr/week = 52 hrs/year
- Value: 52 hrs × $50/hr (Randy's consulting rate) = $2,600/year
- Zapier cost: $240/year (Premium)
- **Net savings: $2,360/year** ✅ *Easy upgrade justification*

---

## Error Handling & Edge Cases

### LinkedIn API Rate Limit Exceeded
**Problem:** Zapier tries to post 3rd time in 24 hours; LinkedIn rejects (2 calls/24h limit)

**Solution:**
- Zapier queues post in Airtable with "Rate limit exceeded" status
- Zapier sends Randy a Slack notification ("LinkedIn posted 2x today; queue next post for tomorrow")
- Randy manually posts via LinkedIn native interface (no API call)
- Claude Code updates `LINKEDIN_TRACKER.md` with post details

**Prevention:**
- Build Zapier workflow to check LinkedIn posting history (last 24h)
- If 2 posts already exist, skip LinkedIn action, store in queue instead

---

### Instagram Shadowban (Posting Too Frequently)
**Problem:** Randy posts 6 times on Tuesday; Wednesday post gets 0 reach (shadowban)

**Solution:**
- Zapier enforces minimum 4-hour spacing between Instagram posts
- Workflow checks last Instagram post timestamp
- If <4 hours, stores post in queue with "wait" status, reschedules for later

**Prevention:**
- Max 3 Instagram posts/week (Zapier enforces this via weekly budget)
- Randomize posting times (10 AM, 3 PM, 6 PM on different days)

---

### TikTok API Posts Forced Private
**Problem:** Zapier posts to TikTok via unaudited app; post auto-sets to private visibility

**Solution:**
- Disable TikTok automation in Zapier (don't attempt API posting)
- Use Zapier only for content drafting (script + audio suggestion)
- Randy posts manually via TikTok app (ensures public visibility)
- Claude Code logs drafts in `TASKS.md` ("Post TikTok: [title]" reminder)

**Prevention:**
- Accept that TikTok requires manual native posting (no API automation for public content until audited)

---

### Image Aspect Ratio Mismatch (Wrong Size Posted)
**Problem:** Image generated for Instagram (1080x1350px) gets posted to Pinterest (should be 1000x1500px); thumbnail looks squished

**Solution:**
- Zapier includes image dimension requirement in post metadata
- Before posting, Zapier checks image dimensions
- If wrong size, posts to queue with "resize needed" status
- Claude Code or Canva auto-resizes for target platform
- Re-trigger post after resize

**Prevention:**
- Canva/Claude generates multiple versions of image per platform upfront (LinkedIn 1200x627px, Instagram 1080x1350px, Pinterest 1000x1500px)
- Zapier metadata labels each image with platform + dimensions
- Zapier logic matches image to platform automatically

---

### Character Limit Exceeded
**Problem:** Copy is 2,500 chars but LinkedIn post limit is 3,000; copy is 3,200 chars → truncation

**Solution:**
- Zapier checks copy length against platform limit BEFORE queuing
- If over limit, posts to queue with "shorten needed" status
- Claude Code or Randy manually edits copy to fit
- Zapier re-checks, approves, publishes

**Prevention:**
- `linkedin_atomizer.py` outputs platform-specific character limits in metadata
- Claude Code builds validation into atomization script (LinkedIn output auto-truncates at 3,000 chars, etc.)

---

### Hashtag Spam Detection (Instagram/Twitter)
**Problem:** Instagram post includes all 30 allowed hashtags; post triggers spam filter, reaches 0 accounts

**Solution:**
- Zapier caps hashtags per platform:
  - Instagram: Max 5 hashtags (remove hashtag spam)
  - Twitter: Max 2 hashtags
  - LinkedIn: 3 hashtags (already in guidelines)
  - Pinterest: Keywords only, no hashtags
  - TikTok: 3 hashtags + trending sound

**Prevention:**
- `linkedin_atomizer.py` outputs curated, platform-specific hashtag sets (not a wall of 30)
- Zapier strips excess hashtags before posting

---

### Scheduling Conflict (Same Content Posted Twice)
**Problem:** Zapier schedules post A for Tuesday 10 AM; Randy manually publishes same post Tuesday 9:50 AM; Zapier publishes duplicate at 10 AM

**Solution:**
- Zapier marks post as "published" in Airtable *before* Zapier publishes (not after)
- On scheduled time, Zapier checks "published" status
- If already published, Zapier cancels action + sends Randy a note

**Prevention:**
- Manual rule: Randy publishes, immediately marks "published" in Airtable
- Zapier automation includes status check before every publish action

---

### API Token Expiration (OAuth refresh fails)
**Problem:** Zapier's LinkedIn access token expires; Zapier loses auth, posts fail

**Solution:**
- Zapier sends notification ("LinkedIn token expired; please re-authenticate")
- Randy clicks "Reconnect" in Zapier UI
- Zapier refreshes token; automation resumes

**Prevention:**
- Set calendar reminder to refresh Zapier integrations quarterly
- Test Zapier workflow monthly (publish 1 test post per platform)

---

## Implementation Checklist for Claude Code

### Phase 1: Setup & Testing (Week 1)

- [ ] Install Zapier MCP in Claude Code
- [ ] Document all 6 platform specifications (character limits, image sizes, rate limits)
- [ ] Build initial Airtable schema:
  - Columns: Article ID, Platform, Copy, Image URL, Status (Draft/Approved/Queued/Published), Published URL
  - Views: By Platform, By Status, By Week
- [ ] Test Zapier → Airtable integration (manual row creation)
- [ ] Test Zapier → LinkedIn draft (Zapier pulls test copy, creates draft)
- [ ] Test Zapier → Twitter post (minimal 280-char test)
- [ ] Test Zapier → Pinterest pin (test pin with link)

**Deliverable:** ZAPIER_SETUP_COMPLETE.md (docs all connections, test results)

---

### Phase 2: Atomizer Integration (Week 2)

- [ ] Modify `linkedin_atomizer.py` to output Zapier-compatible format:
  - CSV or JSON with Platform | Copy | Image Path | Hashtags | Link
  - Include character count per platform
  - Include image dimension requirement per platform
- [ ] Build Zapier trigger: "New CSV uploaded to Google Drive" → parses row → creates Airtable entry
- [ ] Test atomizer output → Airtable queue (2–3 articles)
- [ ] Build Zapier action: "On approval in Airtable" → platform-specific publishing

**Deliverable:** Integration test report (atomizer → Zapier → Airtable → published posts)

---

### Phase 3: Automation Workflows (Week 3–4)

- [ ] Build Workflow 1: Article atomization → multi-platform distribution
- [ ] Build Workflow 2: LinkedIn engagement amplification (conditional)
- [ ] Build Workflow 3: Lead magnet promotional rotation
- [ ] Add error handling for each workflow:
  - Character limits exceeded
  - API rate limits
  - Image dimension mismatches
  - Scheduling conflicts
- [ ] Set up monitoring:
  - Zapier error notifications → Slack or email
  - Monthly analytics pull (UTM tracking from Zapier → Google Analytics)

**Deliverable:** ZAPIER_WORKFLOWS_LIVE.md (docs all 3 workflows, error handling, monitoring)

---

### Phase 4: QA & Optimization (Week 4+)

- [ ] Run full workflow test: 1 article → all 6 platforms → validate posts
- [ ] Check analytics after 2 weeks (which platforms drive most engagement?)
- [ ] Optimize atomizer output based on platform performance:
  - If Instagram high engagement: allocate more Canva design resources to Reels
  - If Pinterest high CTR: increase pin frequency from 5 to 10 per article
  - If TikTok low reach: pivot to manual posting (don't use Zapier API)
- [ ] Measure free plan automation usage (runs/month vs. 100 limit)
- [ ] Calculate ROI: time saved vs. Zapier cost (justify upgrade to paid if needed)

**Deliverable:** ZAPIER_ROI_ANALYSIS.md (metrics, optimization recommendations, paid plan justification)

---

## Critical Success Factors

1. **Randy makes final decisions:** Zapier is a tool; Randy owns content quality, timing, and brand voice
2. **Test on free tier first:** Prove ROI before upgrading to paid
3. **Manual gates for high-stakes platforms:** LinkedIn (API rate limit), Instagram (shadowban risk), TikTok (public visibility risk) all need manual review
4. **Image quality non-negotiable:** Cinematic lighting, realistic visuals, 1-inch white border (brand consistency)
5. **Character limits are hard ceilings:** Build automation to enforce limits, not suggest them
6. **Posting frequency > daily frequency:** Quality consistency across week beats daily posting
7. **Monitor for shadowbans/restrictions:** Check reach weekly; adjust frequency if engagement drops

---

## Summary Table: Platform Readiness

| Platform | Free Zapier Readiness | Paid Zapier Capability | Risk Level | Manual Gate |
|----------|----------------------|------------------------|-----------|-----------| 
| **LinkedIn** | ✅ Queue → Manual | Full automation (2 API calls/24h) | Medium (API limits) | ✅ Recommended |
| **Instagram** | ✅ Queue → Manual | Semi-automation (API limited) | High (shadowban) | ✅ Recommended |
| **Pinterest** | ✅ Full automation | Full automation | Low | ❌ Not needed |
| **Twitter/X** | ✅ Queue → Manual | Full automation | Low | ❌ Not needed |
| **TikTok** | ⚠️ Queue → Manual only | Semi-automation (requires app audit) | Very High (private visibility) | ✅ Required |
| **Facebook** | ✅ Queue → Manual | Full automation | Low | ❌ Not needed |

---

## References & Resources

- [LinkedIn API Rate Limits](https://docs.microsoft.com/en-us/linkedin/shared/api-reference-v2?context=linkedin%2Fcontext)
- [Instagram Platform Guidelines](https://business.instagram.com/help)
- [Pinterest API Documentation](https://developers.pinterest.com)
- [Twitter/X API v2 Docs](https://developer.twitter.com/en/docs/twitter-api)
- [TikTok Content Posting API](https://developers.tiktok.com/doc/content-posting-api)
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api)
- [Zapier Documentation](https://zapier.com/help)
- [2026 Social Media Character Limits Guide](https://typecount.com/blog/social-media-character-limits)

---

**Document Version:** 1.0  
**Last Updated:** June 2026  
**Next Review:** After 4-week pilot (July 2026)  
**Owner:** Randy Skiles (decisions), Claude Code (implementation)
