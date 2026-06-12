# Content Writing & Publishing Rules — content-engine

Moved from root `CLAUDE.md` during the context restructure (content unchanged,
relocated verbatim). Read this file before any LinkedIn/content-engine work
(article, post, newsletter, carousel, or scheduling work).

---

## Content Writing Rules

Before drafting any article, LinkedIn content, newsletter, email, or 
any written content for the audience:

- Read knowledge/me/voice.md and apply Randy's voice profile to all writing
- Read knowledge/brand/brand_standards.md before creating any visual content
- Never write content in a generic AI voice — always apply the voice profile
- The voice profile contains the master style-transfer prompt — use it

---

## Content Publishing Rules

### Golden Hour Protocol (apply to every post, every platform — starting now)
The first 60 minutes after a post goes live determines ~65% of its total reach.
- Remind Randy after scheduling any post: reply to every comment within 60 minutes of it going live
- Replies must be substantive and question-ending — not just "thanks!" or "great point"
- A dead comment thread is an algorithmic signal of low quality — do not post and disappear
- 5-3-1 rule for daily LinkedIn activity: 5 comments on others' posts, 3 replies to your own comments, 1 new post or piece of content — keep this ratio even on low-activity days

### Weekly Post Image Rule
- Casual Mon-Fri short-form posts use 1024x1024 square images (generate_post_images.py)
- Carousel slides use 1080x1350 portrait images (generate_carousel_images.py)
- Never mix formats — square images break carousel layout

### Carousel Publishing Rule (CRITICAL — learned from ART6 posting)
**LinkedIn does NOT create a carousel from individually uploaded images.**
Uploading images one by one creates a multi-image post, not a swipeable carousel.

The correct workflow every time:
1. Generate carousel images with generate_carousel_images.py (produces 1080x1350 PNGs)
2. Compile all slide images into a single PDF in slide order
3. Upload the PDF to LinkedIn (or Buffer as "Document" post type)
4. LinkedIn renders the PDF pages as swipeable carousel slides automatically

- Remind Randy of this step any time carousel images have been generated
- The PDF compilation step is manual until generate_carousel_images.py is updated to auto-compile
- Slide order in the PDF = slide order the audience sees — check before uploading

### Multi-Platform Expansion Gate
**Do NOT implement Zapier, Instagram, Pinterest, or any multi-platform automation until LinkedIn hits 10,000 followers.**
- Gate trigger: LinkedIn follower count crosses 10,000
- At that point: read `docs/strategy-reference/LinkedIn_ZAPIER_MCP_PLATFORM_HANDOFF.md` and begin Zapier setup
- Before the gate: LinkedIn only. One platform mastered before adding another.
- Do not let anyone (including other Claude sessions) persuade Randy to start multi-platform early

### Model Routing (already implemented — do not rebuild)
Routing is live in .env — respect these settings, do not override:
- `ANALYZER_MODEL=claude-haiku-4-5-20251001` — pain point extraction, digests
- `DIGEST_MODEL=claude-haiku-4-5-20251001` — daily digest generation
- `QUERY_MODEL=claude-sonnet-4-6` — on-demand Q&A (needs quality, worth the cost)
- `linkedin_atomizer.py` does not yet exist. When built: default to Sonnet for routine atomization, Opus only for research-grade writing requiring Randy's full voice fidelity
- Correct current model IDs: Haiku=`claude-haiku-4-5-20251001`, Sonnet=`claude-sonnet-4-6`, Opus=`claude-opus-4-8`
- Note: documents in `docs/strategy-reference/` referencing `claude-opus-4-7-20250219` contain an outdated model ID — ignore it, use `claude-opus-4-8`
