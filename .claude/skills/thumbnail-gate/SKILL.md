---
name: thumbnail-gate
description: One-pass review of a YouTube thumbnail against conversion-first principles — scored 1-10 across six dimensions, checked against your REAL competing search results, with a Ship It / One Tweak / Redo verdict. Judges an image you made; never generates art.
---

> **Solves:** knowing whether a thumbnail earns the click BEFORE it ships, judged the way a cold stranger sees it — at phone size, in a feed of competitors.
> **Does NOT cover:** generating or editing thumbnail art, titles, or SEO.
> **Failure mode if misapplied:** treating the rubric as a generator and designing "to the test" — it's a gate, not a recipe.

# Thumbnail Gate — one pass, no iterating

## Input (ask for anything missing)

1. The thumbnail image file
2. The video title (thumbnail and title are one system)
3. Two sentences on what the video actually delivers
4. **The search term or niche feed this video competes in** (e.g. "home assistant tutorial") — the review is meaningless without naming the feed

## Step 1 — Format and scale

Read the image's real dimensions. ~16:9 → long-form rules below. ~9:16 → Short mode: tighten the element budget to 2, judge as a narrow vertical tile, and remember Short thumbnails only appear in search/shelves — never the swipe feed.

Judge at small-tile scale FIRST (mentally ~120×68 px). 70%+ of impressions happen there; full-size polish cannot rescue a tile that dies small.

## Step 2 — The 1-second rule

Count distinct elements (a face, a text overlay, a screen, a prop, a background object). **3 or fewer** (2 for Shorts) or flag it and name what to cut. If you have to think about what something is, it's noise.

## Step 3 — Story check

Which micro-story is it telling? **Progression** (before→after) · **Comparison** (A vs B) · **Tension** (about to break) · **Peak Moment** (the best result or funniest disaster, upfront). None detected = no reason to click = flag.

## Step 4 — Score six dimensions, 1–10, one line each

| Dimension | 8+ means | Below 6 means |
|---|---|---|
| 1-Second Clarity | A stranger gets it instantly at phone size | Requires study |
| Simplicity | Looks like a captured moment | Cluttered / over-designed |
| Curiosity Gap | Thumbnail + title open a question only the click answers | "I already get it" |
| Expression / Focal | A face doing real emotional work — or, faceless, one unmistakable focal subject | Flat, neutral, or lost at size |
| Color Contrast | Pops against the ACTUAL competing feed | Blends in |
| Story Signal | One of the four stories, clearly | No narrative tension |

A neutral, composed face caps Expression at 5 — an expressive face is the single highest-leverage pixel on the tile.

## Step 5 — Title ↔ thumbnail ↔ delivery

- Title and thumbnail must carry DIFFERENT information (one names stakes, the other shows the moment). Same info twice = one wasted hook.
- Promise vs. delivery: if the hook is bigger than the video, clickers bail and retention pays the bill. PASS / FLAG / FAIL with the gap named. A FAIL forces Redo regardless of scores.

## Step 6 — The feed check (evidence, not vibes)

Pull the REAL competition and look at your tile among them:

```bash
yt-dlp "ytsearch6:<the search term>" --flat-playlist --print "%(id)s|%(title)s"
# then per result: curl -s "https://i.ytimg.com/vi/<ID>/hqdefault.jpg" -o comp_N.jpg
```

Build a column of those six at ~168px wide with the candidate inserted, and look at it. Two questions:
1. **Separable?** Different dominant color/composition from the wall in one glance?
2. **Camouflage:** could any other channel in this niche have produced this exact tile? If yes — it reads as the category, and the category is what strangers scroll past. Camouflage FAIL forces **Redo**.

## Step 7 — Verdict

**Ship It** (all ≥7, alignment strong, story present, feed check passed) · **One Tweak** (exactly one dimension <7, fix under 10 minutes) · **Redo** (two+ below 6, no story, or a forced fail). Max 3 fixes, most-leveraged first. One pass — no "tweak and show me again" loops; the next look is the next thumbnail's review.
