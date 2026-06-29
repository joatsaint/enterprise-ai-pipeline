# SKILL: YouTube Shorts — Creation & Optimization
**Last updated:** 2026-06-26 (researched from live 2026 sources)

Read this file before writing any YouTube Shorts script, generating a HeyGen video, or advising on Shorts strategy. All rules below are current as of 2026.

---

## Randy's Shorts Pipeline (canonical setup)

**HeyGen generation settings (locked — see `memory/reference_heygen_avatar_voice.md`):**
- Avatar: `Randy_DigitalTwin_v2` (look ID `f41f558ae99a4c57a8c084da1a35380c`)
- Voice: `10c4865426d34d8b80b2c29bad890178`
- Engine: `avatar_v`
- Format: `mp4` with bright green background (`#00FF00`)
- Aspect ratio: `9:16` (portrait — full body, shoulders visible, no crop)
- Resolution: `1080p`
- Background: `#00FF00` solid green — Randy uses CapCut's one-click Remove BG to key it out

**Why 9:16 (not 1:1):** 1:1 crops a portrait source recording, cutting off the avatar's shoulders. 9:16 preserves the full frame.
**Why mp4 + green (not webm):** CapCut PC doesn't render webm alpha — shows as black. Green + Remove BG is one click and reliable.

**CapCut composite layout (Randy's workflow — CapCut PC):**
- Canvas: 1080×1920 (9:16)
- Layer 1 (bottom): `desk_background.png` — fill bottom 1080×960
- Layer 2: import 9:16 avatar mp4 → click "Remove BG" (one step, auto) → zoom slider to ~50% to fit bottom half → position center-bottom
- Layer 3 (top half): graphics, text, cards, animations
- Audio: from the avatar mp4

**Critical framing requirement:** The avatar source recording MUST be a tight head-and-shoulders / bust-up shot — NOT a full-length standing portrait. When a full 9:16 portrait is scaled to 50% to fit the bottom half of the canvas, the shoulders sit near the TOP of that scaled area, which clips against the upper boundary of the bottom-half zone. A tight bust/chest-up frame ensures the head and shoulders land well inside the 960px bottom zone at 50% scale.

**Side-gap issue:** At 50% scale, the avatar is only 540px wide in a 1080px canvas. The 270px on each side must be covered by the `desk_background.png` or a background fill layer — otherwise canvas edges are exposed. Ensure the background layer extends the full 1080px width.

---

## Format Rules

- **Aspect ratio:** 9:16 portrait — non-negotiable, Shorts are mobile-only
- **Resolution:** 1080×1920 minimum
- **Length:** 30–180 seconds. Sweet spot for algorithm = **30–60 seconds**. Sub-15s collapsed in 2026 (can't hit absolute watch-time floor even at 100% retention). Over 90s requires exceptional hook+retention or it bleeds views.
- **Frame rate:** 30fps or 60fps

---

## The Algorithm (2026) — What Actually Drives Distribution

YouTube's Shorts algorithm runs a **Priority Test Window of 30–60 minutes** after publish. It shows the Short to a small test audience and scores four signals:

| Signal | Why it matters |
|---|---|
| **First-loop watch-through rate** | #1 metric. Did they watch the whole thing? |
| **Replay rate** | Did they loop it? Forces re-watch = top signal |
| **Swipe-away rate** | Swipe in first 3 seconds = immediate penalty |
| **Engagement rate** | Likes, comments, shares after watching |

**Retention benchmark:** 70%+ is what the algorithm rewards. A 30-second Short at 85% retention outranks a 60-second Short at 50% retention. Optimize for % watched, not total views.

**Anti-Repetitive Content AI (2026):** YouTube now actively filters Shorts that repost near-identical content. Each Short needs a distinct hook, angle, or information gain — don't just re-cut the same clip with different text.

**Niche consistency matters:** If your recent uploads cover multiple unrelated topics, the algorithm can't identify who to show them to. Stay on-niche (IT/AI/operator career for Randy).

---

## Hook — First 3 Seconds (most critical real estate)

50–60% of drop-offs happen in the first 3 seconds. The hook must:

1. **Start mid-action or mid-statement** — never a slow intro, logo, or "hey guys"
2. **Name the viewer's pain or curiosity immediately** — "Here's what nobody tells sysadmins about AI..."
3. **Create a visual jolt** — movement, color change, or something unexpected in the first frame
4. **Make a promise** — the viewer should know in 3 seconds what they're going to learn or feel

**Hook formulas that work for Randy's ICP (IT ops / AI anxiety):**
- **The Contrarian:** "Everyone says AI will replace IT. They're looking at the wrong data."
- **The Time Bomb:** "You have about 6 months before this role fills itself from the outside."
- **The Insider:** "Here's what 25 years in IT ops actually tells you about the AI transition."
- **The Specific Number:** "Three questions your CISO will ask about every AI workflow — and why you already know the answers."
- **The Story open:** "In 1999, I watched a colleague go from 'computer guy' to IT Director in six months. Same thing is happening right now."

Videos that hook in the first 15 seconds retain 65% of viewers through 3 minutes. Without a hook by 15 seconds, retention drops below 45%.

---

## Script Structure

```
[0–3s]   HOOK — pain, curiosity, or bold claim. No intro.
[3–20s]  SETUP — context that makes the hook land. One idea only.
[20–50s] PAYLOAD — the specific, credible insight. Randy's 25-yr operator lens.
[50–60s] CLOSE + PATTERN INTERRUPT — end with the sharpest line, not a summary.
          Optional: soft CTA ("link in bio" or "follow for more") — keep it 1 line.
```

**Script length → duration guide:**
- 120 words ≈ 55–60 seconds
- 150 words ≈ 70–75 seconds
- 200 words ≈ 90–100 seconds
- 300 words ≈ 135–150 seconds

**Voice rules (Randy's operator voice — always apply):**
- Short sentences. No filler.
- Operator-specific language (ticket queue, blast radius, change window, 2 AM page)
- No motivational-speaker cadence — calm, direct, experienced
- One idea per Short — don't try to cover the whole article
- Read `knowledge/me/voice.md` before drafting

---

## Captions (required — most viewers watch muted)

- **Always burn captions into the video** (CapCut auto-caption or HeyGen `caption` parameter with `style: "default"`)
- Position: **center third of screen** — avoid top 20% (title/channel overlay) and bottom 25% (like/comment buttons)
- Accuracy: 99%+ sync within 0.5 seconds of audio
- Font: bold, sans-serif, high contrast — legible at mobile size
- One or two words highlighted per beat works better than full-sentence blocks

---

## Title (under 40 characters — primary discovery lever)

- **Under 40 characters** — longer gets truncated on mobile
- **Declarative statements, not questions** — "AI Won't Replace You. This Will." not "Will AI Replace You?"
- **Echo the hook from the video's opening line** — title and first frame should feel like one thing
- **Include searchable keywords** for the ICP: AI, sysadmin, IT career, enterprise, automation
- Titles matter most **outside the Shorts feed** (search, channel page, suggested) — they're invisible in the feed itself

**Randy title formulas:**
- `[Specific claim]. [Twist].` — "AI Cuts Jobs. Not Yours."
- `[Time + stakes]` — "6 Months Before They Hire From Outside"
- `[What you already have]` — "25 Years = Your AI Advantage"

---

## Thumbnail

- Not shown in the Shorts feed (autoplay) — matters for search, channel page, suggested
- Pick the **hook moment frame** — the most visually striking second of the video
- **3–4 words max** if adding text — bold, sans-serif, legible at thumbnail size
- Text should complement the title, not duplicate it
- Randy's top-half info graphic in the CapCut composite often makes a strong thumbnail frame

---

## Hashtags

- Put hashtags in the **description**, not the title
- 3–5 hashtags max: `#YouTubeShorts` + 2–3 niche tags (`#SysAdmin #AICareer #EnterprisIT`)
- `#Shorts` is required for Shorts feed eligibility
- Avoid tag-stuffing — the 2026 algorithm penalizes it

---

## Posting & Engagement

- **Post time:** Tue–Thu, 12–3 PM or 6–9 PM in your audience's primary timezone (CDT for Randy)
- **Golden Hour:** Reply to every comment within 60 minutes of posting — this is the same rule as LinkedIn and it matters just as much here
- **Reply as a Short:** When a comment asks a question that deserves a video answer, respond with a new Short — YouTube surfaces these prominently
- **Consistency > frequency:** 3–4 Shorts/week on-niche beats 7/week off-niche every time

---

## One Short Per Article (minimum)

Each article → at least 1 Short. Atom the sharpest single idea, not a summary of the whole article. The Short should stand alone — viewers shouldn't need to have read the article.

**ART7 → Short:** "You Already Know Kung Fu" (the 1999 first-mover frame)
**ART8 → Short:** TBD
**ART9 → Short:** TBD

---

## Gotchas

- **Don't summarize the article** — pick ONE idea and go deep for 45–60 seconds. A summary Short has no replay value.
- **Sub-15s Shorts are dead in 2026** — the algorithm can't score them even at 100% retention. Minimum ~25–30 seconds.
- **YouTube Shorts cap is 180 seconds (3 minutes)** — not 60 seconds (that was pre-2024). Do not tell Randy the cap is 60s.
- **webm alpha does NOT work in CapCut PC** — shows as black background. Use mp4 with `#00FF00` green background; Randy uses CapCut's one-click Remove BG to key it out.
- **Shoulder crop is a framing problem, not an aspect ratio problem.** When a full 9:16 standing portrait is scaled to 50% to fit the bottom half, the shoulders sit at the very top of the bottom zone and get clipped. Fix: always generate with a TIGHT bust/head-and-shoulders recording, not a full standing shot. The avatar source video must frame the person from the chest up.
- **Side gaps at 50% scale:** A 9:16 avatar scaled to 50% is only 540px wide in a 1080px canvas — leaves 270px exposed on each side. The background layer must fill the full 1080px width.
- **CapCut PC has no pinch-zoom.** Scaling is done with the zoom slider only. It maintains AR uniformly.
- **Captions must avoid the bottom 25%** of the frame — that's where YouTube's like/comment/share buttons overlay in the Shorts feed.
