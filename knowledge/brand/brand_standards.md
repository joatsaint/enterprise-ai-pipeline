# BRAND STANDARDS — Randy Skiles / IT→AI Transition Playbook
**Version: 1.0 | May 2026**

Read this file before creating any visual content — carousels, images, documents, slides, or any branded deliverable.

---

## 1. BRAND IDENTITY

**Name:** Randy Skiles
**Brand line:** IT→AI Transition Playbook
**Positioning:** IT professionals with 15–25 years of experience navigating the AI shift
**Core message:** You're not behind. You're early.
**Voice:** Peer-to-peer. 25 years of enterprise IT war stories applied to AI. Never expert-to-student.

---

## 2. COLOR PALETTE

These colors were extracted directly from the IT→AI logo. Use only these.

| Role | Hex | Usage |
|---|---|---|
| Background — Deep Navy | `#00001E` | Primary slide/page background |
| Background — Mid Navy | `#001E4B` | Cards, secondary backgrounds, layering |
| Electric Blue | `#0078F0` | Primary accent — numbers, borders, highlights, CTAs |
| Sky Blue | `#0096F0` | Secondary accent — labels, sub-headlines, list markers |
| Glow Blue | `#00AAFF` | Gradient endpoints, glow effects only |
| White | `#FFFFFF` | Primary headline text |
| Off-White | `#E8F0FF` | Body text, secondary text |
| Dim Grey | `#7A8FA8` | Tertiary text, metadata, footer text |

### Color Rules
- **Background is always deep navy** `#00001E` — never white, never grey
- **Primary accent is always electric blue** `#0078F0` — never purple, never green
- **Text hierarchy:** White headlines → Off-white body → Dim grey metadata
- **Never use** purple, teal, orange, red (except error/warning contexts in tech docs)
- **Gradients:** Only blue-to-blue — `#0078F0` → `#00AAFF`
- **Overlays and cards:** Use rgba transparency over navy, not solid fills

### Alert/Contrast Colors (use sparingly)
| Role | Hex | Usage |
|---|---|---|
| Warning Red | `#FF7070` | Bad outcomes, crossed-out items, warnings only |
| Success Glow | `#00AAFF` | Positive outcomes, success states |

---

## 3. TYPOGRAPHY

### Font Stack
| Font | Weight | Usage |
|---|---|---|
| **Rajdhani** | 700 | Brand mark only — "IT→AI" logotype |
| **Barlow Condensed** | 800 | Primary headlines, slide titles, section labels |
| **Barlow Condensed** | 700 | Sub-headlines, numbered items, footer name |
| **Barlow** | 600 | Bold body emphasis, key phrases |
| **Barlow** | 400 | Body text, conversational copy |

### Google Fonts Import
```
https://fonts.googleapis.com/css2?family=Rajdhani:wght=700&family=Barlow:wght=400;500;600&family=Barlow+Condensed:wght=700;800&display=swap
```

### Type Size Scale (1080x1080 carousel slides)
| Element | Size | Font |
|---|---|---|
| Big quote | 64–72px | Barlow Condensed 700, italic |
| Primary headline | 54–68px | Barlow Condensed 800 |
| Secondary headline | 42–54px | Barlow Condensed 800 |
| Tag/label | 14–18px | Barlow Condensed 700, uppercase, letter-spacing 4px |
| Body text | 28–32px | Barlow 400 |
| List items | 20–24px | Barlow 400 |
| Footer / metadata | 18–20px | Barlow Condensed 700 or Barlow 400 italic |
| Slide number | 18px | Barlow Condensed 700, uppercase, letter-spacing 3px |

### Typography Rules
- **Headlines are uppercase** in Barlow Condensed
- **Body text is sentence case** in Barlow — never all caps
- **Tags/labels are all caps** with wide letter spacing (3–4px)
- **Highlight key words** in `#0078F0` electric blue within headlines
- **Line height:** 1.0–1.1 for headlines, 1.5–1.75 for body text
- **Fragments are intentional** — Randy's voice uses short punchy lines

---

## 4. LAYOUT SYSTEM

### Slide Dimensions
- **Carousel slides:** 1080 × 1080px (square)
- **LinkedIn post images:** Vertical — 1080 × 1350px
- **LinkedIn article images:** Landscape — 1376 × 768px (with 1-inch white border)

### Standard Slide Padding
- **All slides:** 64px padding on all sides
- **Never crowd the edges** — negative space is intentional

### Required Elements on Every Carousel Slide
1. **Brand mark** (top left): `IT→AI` in Rajdhani — "IT" and "AI" white, "→" electric blue
2. **Slide number** (top right): `01 / 08` format, dim grey, Barlow Condensed uppercase
3. **Accent line** (below top bar): 64px wide, 4px tall, gradient `#0078F0` → `#00AAFF`
4. **Footer** (bottom, separated by 1px electric blue border at 20% opacity):
   - Left: `Randy SKILES` — "Randy" dim grey, "SKILES" electric blue, Barlow Condensed 700 uppercase
   - Right: `IT→AI Transition Playbook` — dim grey, italic

### Background Texture
Every slide uses a subtle circuit board grid overlay:
```css
background-image:
  linear-gradient(rgba(0,120,240,0.04) 1px, transparent 1px),
  linear-gradient(90deg, rgba(0,120,240,0.04) 1px, transparent 1px);
background-size: 40px 40px;
```

### Glow Orbs
Two soft radial glows on every slide for depth:
- **Top right:** `rgba(0,120,240,0.18)`, 400×400px, blur 80px, offset -100px
- **Bottom left:** `rgba(0,150,240,0.12)`, 300×300px, blur 80px, offset -80px

### Cards and Boxes
- **Border radius:** 3–4px (sharp, not rounded)
- **Good/positive cards:** `rgba(0,120,240,0.10)` fill, `rgba(0,120,240,0.35)` border
- **Bad/warning cards:** `rgba(255,60,60,0.07)` fill, `rgba(255,80,80,0.25)` border
- **CTA boxes:** `linear-gradient(135deg, rgba(0,120,240,0.14), rgba(0,30,75,0.7))` fill

---

## 5. BRAND MARK USAGE

### The IT→AI Mark
```html
<span style="font-family: Rajdhani; font-weight: 700; color: white; letter-spacing: 2px;">
  IT<span style="color: #0078F0;">→</span>AI
</span>
```

### Rules
- Always use Rajdhani 700 — never substitute
- The arrow `→` is always electric blue `#0078F0`
- "IT" and "AI" are always white
- Never stretch, rotate, or recolor the mark
- Minimum size: 24px on any deliverable
- Always appears top-left on carousel slides

---

## 6. VOICE + VISUAL ALIGNMENT

Visual design must reinforce Randy's voice. These rules connect the two:

| Voice Principle | Visual Expression |
|---|---|
| Peer-to-peer, not expert-to-student | No fancy podium aesthetics — grounded, direct layout |
| Short punchy sentences | Short line stacks with breathing room between lines |
| War story → lesson → implication | Slides build: hook → problem → framework → what this means for you |
| "You're not behind. You're early." | Warm blue tones — not cold corporate, not alarming red |
| Protective instinct | CTAs feel helpful, not salesy — "Grab the free guide" not "Buy Now" |
| IT professional credibility | Technical texture (circuit grid) without being overdone |

---

## 7. CAROUSEL STRUCTURE — STANDARD 8-SLIDE TEMPLATE

Every article carousel follows this structure:

| Slide | Role | Content Pattern |
|---|---|---|
| 01 | Hook | Big quote or bold opening line + 2–3 short lines setting stakes |
| 02 | The Problem | What's broken or misunderstood — Randy's specific observation |
| 03 | The Shift | The wrong approach crossed out → the right question highlighted |
| 04 | The Framework | 3-part numbered list — Randy's actual system |
| 05 | What This Means For You | Explicit bridge from IT war story to AI situation |
| 06 | The Consequence | Two-column outcome — tech demo path vs. infrastructure path |
| 07 | The Tease | Link to full article — "full story is in this week's article" |
| 08 | CTA | "You're not behind. You're early." + free guide link |

---

## 8. LINKEDIN IMAGE FORMATS

### Post Image (vertical)
- **Size:** 1080 × 1350px
- **Border:** None
- **Style:** Same brand colors, same typography
- **Ask before generating:** "Is this for a Post or Article?"

### Article Image (landscape)
- **Size:** 1376 × 768px
- **Border:** 1-inch white border around entire image
- **Style:** Realistic with subtle humor, cinematic lighting
- **Goal:** Stop professionals mid-scroll

---

## 9. WHAT NOT TO USE

| Never Use | Use Instead |
|---|---|
| Purple gradients | Blue gradients only |
| White or light backgrounds | Deep navy `#00001E` |
| Inter, Roboto, Arial, system fonts | Rajdhani + Barlow family |
| Rounded corners > 4px | 3–4px max border radius |
| Generic stock photo aesthetic | Cinematic, specific, editorial quality |
| Inspirational quote overlays | Randy's actual war story lines |
| "Leverage", "synergy", "journey" | Direct plain language |
| Purple, orange, green accents | Electric blue `#0078F0` only |

---

## 10. FILE REFERENCES

| File | Location | Purpose |
|---|---|---|
| `knowledge/me/voice.md` | Repo | Randy's voice profile — read before all content |
| `knowledge/brand/brand_standards.md` | Repo | This file — read before all visual content |
| IT→AI Logo | `/mnt/user-data/uploads/IT_to_AI_Newsletter.png` | Source logo for color reference |
| Carousel v2 | `vendor_carousel_v2.html` | Reference implementation of brand system |

---

*Version 1.0 — May 2026 | Built from IT→AI logo color extraction + carousel v2 design system*
