# Claude Code Handoff — Why ChatGPT’s LinkedIn Images Are Better, and How to Reproduce the Recipe

**Project:** Sysadmin AI Survival Playbook / IT→AI Transition Playbook  
**Audience:** Experienced Gen-X sysadmins, infrastructure operators, enterprise software admins, ServiceNow admins, software analysts, and IT professionals with 20–30 years of production experience  
**Purpose:** Answer Claude’s image-generation questions and give Claude Code a repeatable production recipe for generating images closer to the ChatGPT-created LinkedIn article/post/carousel visuals.

---

## 0. Direct Answer: What Image Generator Is Being Used?

The images in ChatGPT are generated through OpenAI’s built-in image generation system. In API terms, the closest target model family is **OpenAI GPT Image**, not classic DALL·E 3-style prompting.

For Claude Code or an external automation pipeline, use:

- **Preferred current API target:** `gpt-image-2`, if available in the account
- **Compatible prior target:** `gpt-image-1`
- **Do not think of this as “just DALL·E.”** The prompt strategy should be written for multimodal GPT Image-style generation, with detailed art direction, semantic constraints, layout requirements, and brand rules.

Important: I cannot guarantee the exact hidden backend model used by ChatGPT’s consumer image tool in every session. What I can give you is the **production prompt strategy** that produces the look: cinematic editorial realism, Operator consistency, field-manual grit, white-border documentary framing, controlled color grade, Gen-X sysadmin recognition, and a recurring hidden red stapler.

---

# 1. Claude’s Question 1

## Question

Generate a LinkedIn carousel image for this scene:

> The Operator — a calm Gen-X sysadmin in his early 50s — stands at a locked enterprise security gate. Signs read PII, PROD, HR DATA. Beyond the gate, an AI workflow system is visible but inaccessible. Text overlay: “The hard part is permission.”

Then ask for the complete verbatim prompt sent to the image generator.

## Answer Claude Should Understand

The weak version of this prompt is the literal scene:

> Man at gate. Signs. AI workflow behind gate. Text overlay.

That is not enough.

The strong version adds **brand physics**:

- who the image is emotionally for
- why the Operator matters
- what the image must make the viewer feel
- what genre the image belongs to
- what lighting should do
- what color grade should do
- where the visual tension lives
- what must be avoided
- where the hidden stapler goes
- why the metaphor matters
- how the text should behave

The generator needs more than the scene. It needs the **visual universe**.

## Production Prompt I Would Send

```text
Create a high-impact LinkedIn carousel image in the established Sysadmin AI Survival Playbook / IT→AI Transition Playbook visual style.

Asset type: LinkedIn carousel slide.
Final format: vertical portrait, 1080 x 1350 px, with a clean white documentary-style border around the entire image.

CORE MESSAGE:
The hard part of enterprise AI adoption is not whether AI can do the task. The hard part is whether it has permission to touch production systems, sensitive data, identity workflows, HR records, finance data, customer data, or regulated business processes.

The image must make an experienced Gen-X IT professional think:
"Exactly. Capability is not approval."

STYLE AND MOOD:
Use cinematic editorial realism. The image should feel like a serious Wall Street Journal feature photograph crossed with a gritty IT field manual cover. Realistic, grounded, professional, slightly gritty, not stock photography, not glossy SaaS marketing.

Mood: dry, world-weary competence. The scene should communicate sober operational judgment, not fear. The Operator is not blocking progress. He is preventing a future incident report.

MAIN CHARACTER — THE OPERATOR:
Show a recurring Gen-X enterprise sysadmin / infrastructure operator:
- male, early-to-mid 50s
- salt-and-pepper hair
- slightly tired but sharp eyes
- average build
- practical business-casual clothing, dark polo or faded button-down, practical jacket or fleece vest
- badge/lanyard or access card
- calm under pressure
- focused, skeptical, grounded, emotionally stable
- never panicking
- never posing like a consultant
- never smiling broadly
- never worshiping technology

He should look like the person who keeps production alive while everyone else creates chaos.

SCENE:
The Operator stands at a robust locked enterprise security checkpoint or access gate inside a realistic corporate technology facility. The gate protects critical internal systems.

Clear signs on or near the gate should read:
- PII
- PROD
- HR DATA
- FINANCE
- IDENTITY
- CUSTOMER DATA
- APPROVAL REQUIRED
- AUDIT LOGGING

Beyond the locked gate, show a powerful AI-assisted workflow system waiting for access. Do not represent AI as a robot, glowing brain, holographic face, or sci-fi entity. Represent AI as a serious enterprise workflow console, automation dashboard, approval queue, or abstract business process interface.

The AI system should look capable but contained. It is visible, ready, and useful, but not allowed to proceed without human approval.

The Operator holds a clipboard and access badge. His posture is calm and practical. He is enforcing boundaries, not resisting progress.

COMPOSITION:
Use a strong rule-of-thirds composition.
- Foreground: security desk or checkpoint surface with badge scanner, visitor log, coffee mug, paperwork, and hidden stapler.
- Midground: The Operator at the locked gate, calm and grounded.
- Background: AI workflow system visible beyond the gate, cool blue interface glow, inaccessible but waiting.

The image should work even if all text is removed. The metaphor must be obvious: AI is not blocked by intelligence; it is blocked by permission.

LIGHTING:
Use dramatic but realistic cinematic lighting:
- warm amber practical light on the Operator’s face, hands, and clipboard
- cool blue-gray glow from the AI workflow system beyond the gate
- subtle green status lights from access control panels or enterprise equipment
- deep shadows with detail preserved
- high contrast but not crushed blacks
- realistic reflections on glass, badge scanner, and polished security desk

COLOR GRADE:
Use a restrained dark editorial palette:
- deep navy
- charcoal
- black
- muted gray
- storm blue
- cool cyan screen glow
- muted green status lights
- aged paper beige
- amber practical light
- warning yellow accents
- off-white typography

Avoid purple, neon pink, rainbow gradients, bright startup colors, glossy SaaS-blue marketing palettes, and overly clean white backgrounds.

TEXT OVERLAY:
Render this text in bold condensed sans-serif typography:
"THE HARD PART IS PERMISSION."

Text placement: top third or upper-left, whichever least interferes with the gate and Operator.
Typography style:
- uppercase
- white primary text
- warning yellow accent on the word "PERMISSION"
- subtle dark gradient behind text for mobile readability
- no decorative fonts
- no tiny critical text
- do not cover The Operator’s face
- do not cover the gate signs

RECURRING EASTER EGG:
Hide exactly one small red Swingline-style stapler half-hidden behind a coffee mug on the security checkpoint desk. It must be off-center, naturally placed, not labeled, not glowing, not oversized, not in the Operator’s hand, and visible only after closer inspection.

AVOID:
No robots. No glowing AI brains. No holographic human heads. No cyberpunk city. No stock-photo corporate smiles. No young startup founder. No lab coat. No hacker hoodie. No fantasy armor. No fake futuristic nonsense. No plastic skin. No distorted hands. No unreadable critical labels.

IMAGE QUALITY:
High-resolution, realistic, cinematic, editorial, detailed, professional, emotionally grounded. The image should stop a LinkedIn scroll in under two seconds and make a 50-year-old enterprise sysadmin feel immediate recognition.
```

---

# 2. Claude’s Question 2

## Question

> When I give you an image request, do you rewrite or enhance my description before sending it to the image generator? Walk me through exactly what you add, change, or remove — and why.

## Answer

Yes. A short user image request is almost always rewritten into a fuller production prompt before image generation.

The key is that I do **not** merely make the prompt longer. I make it more **visually deterministic** and more **emotionally specific**.

## What Gets Added

### 1. Audience Psychology

Original user request usually says what should appear.

I add who the image must affect.

Example:

```text
Target viewer: experienced Gen-X sysadmin, 20–30 years in enterprise IT, skeptical of AI hype, worried about being replaced, trained to notice operational risk.
```

Why this matters:
The image generator cannot literally know the audience, but audience definition changes every downstream decision: lighting, props, facial expression, environment, humor, and realism.

### 2. Emotional Function

Every slide gets an emotional job.

Examples:

- Recognition
- Disbelief
- Stress
- Competence
- Mystery
- Validation
- Hope

Why this matters:
A carousel is not a list of facts. It is an emotional progression. The Hurricane Motel carousel worked because it moved from absurdity to stress to competence to recognition to hope.

### 3. Visual Archetype

I map the article idea to a reusable metaphor:

| Concept | Visual Archetype |
|---|---|
| Permission risk | Security checkpoint / permission gate |
| Bad leadership | Jenga tower / load-bearing block |
| Institutional memory | Empty Bob chair |
| Resourcefulness | Motel command center |
| Vendor overconfidence | Lab experiment / demo room |
| AI governance | Air traffic control / approval console |
| Career defensibility | Castle moat |

Why this matters:
The metaphor carries the argument. Text should sharpen the image, not rescue it.

### 4. The Operator Standard

I replace generic people with a consistent recurring protagonist:

```text
The Operator: male Gen-X sysadmin, early-to-mid 50s, salt-and-pepper hair, tired but sharp-eyed, calm under pressure, practical clothing, headset often nearby, emotionally stable while chaos unfolds around him.
```

Why this matters:
Without a character standard, every image becomes “random middle-aged dashboard guy.” Recognition dies.

### 5. Lighting and Color Grade

I specify lighting like a cinematographer:

- warm monitor glow on face/hands
- cool storm/server/dashboard glow in background
- practical lamps
- subtle green status lights
- high contrast but detail-preserving shadows

I specify palette:

- deep navy
- charcoal
- storm blue
- amber light
- muted green
- warning yellow
- off-white type

Why this matters:
The strong images are not just scenes. They share a color grammar.

### 6. Composition

I add foreground, midground, background instructions.

Example:

```text
Foreground: coffee mug, keyboard, notes, hidden stapler.
Midground: The Operator working calmly.
Background: storm, dashboards, executives, server racks, or failure metaphor.
```

Why this matters:
Good images have depth and hierarchy. Weak AI images often flatten everything into a poster.

### 7. Negative Constraints

I aggressively remove generic AI garbage:

- no robots
- no glowing brains
- no holographic heads
- no cyberpunk city
- no startup stock-photo smiles
- no generic blue SaaS marketing

Why this matters:
Most AI images fail because the generator falls into default “AI art” clichés.

### 8. Easter Egg Rules

I add the red Swingline-style stapler as a recurring hidden detail.

Why this matters:
It creates repeat-view behavior, Gen-X recognition, and a non-cheesy engagement mechanic.

### 9. Text Overlay Rules

I specify not just the text, but how the text behaves:

- short
- bold
- mobile-readable
- does not cover the main subject
- white/yellow contrast
- dark gradient if needed

Why this matters:
AI-generated text often fails. When possible, generate clean imagery first and add text afterward in code or an editing layer.

## What Gets Removed

I remove or reduce:

- excessive literal explanation
- too many labels
- too many background jokes
- every possible easter egg crammed into one scene
- vague adjectives like “cool,” “professional,” “engaging” unless supported by concrete visual instructions
- generic AI references
- anything that makes the Operator look like the joke

## The Core Rewrite Formula

```text
User idea → audience emotion → visual metaphor → Operator role → scene hierarchy → lighting → palette → easter egg → overlay → anti-cliché constraints → QA criteria
```

---

# 3. Claude’s Question 3

## Question

> Analyze a sample image and write the exact prompt that was used to generate it. I need to reproduce this quality through the API — give me the full, production-ready prompt, word for word, as if you were about to send it to the image generator right now.

## Answer

No one can honestly recover the exact original hidden prompt from an image unless the prompt was logged. What can be done is a **production-grade reverse-engineered prompt** that reproduces the image’s key aesthetic, structure, and mood.

Below is the reverse-engineered production prompt for the strongest established image family: **The Hurricane Motel / Operator in Chaos**.

## Reverse-Engineered Production Prompt — Hurricane Motel Hero Style

```text
Create a cinematic editorial LinkedIn article hero image in the established Sysadmin AI Survival Playbook / IT→AI Transition Playbook visual style.

Asset type: LinkedIn article hero image.
Final format: 1376 x 768 px landscape, with a clean white documentary-style border around the entire image.

CORE MESSAGE:
Experienced IT professionals are not obsolete in the AI era. Their operational judgment, calm under pressure, improvisation, and institutional memory are exactly what AI cannot replace.

The scene should communicate this idea:
Production does not care whether the environment is professional. Experienced operators keep systems alive anyway.

STYLE AND MOOD:
Use cinematic editorial realism. The image should feel like a Wall Street Journal feature photograph crossed with a gritty IT field manual cover. It should be realistic, grounded, professional, slightly worn, not polished stock photography.

Mood: dry, world-weary competence. Serious but subtly humorous. The humor comes from the absurd contrast between a sketchy motel room and a highly professional enterprise IT command setup.

MAIN CHARACTER — THE OPERATOR:
Show a recurring Gen-X enterprise sysadmin / infrastructure operator:
- male, early-to-mid 50s
- salt-and-pepper hair
- slightly tired but sharp eyes
- average build
- practical dark clothing, dark polo or worn hoodie
- headset on or nearby
- glasses optional
- calm under pressure
- focused, skeptical, grounded, emotionally stable
- not posing
- not smiling broadly
- not panicking

He should look like the person who has survived every outage, every vendor promise, every rushed leadership decision, and still keeps production alive.

SCENE:
The Operator is working from a cheap, worn budget motel room during a hurricane evacuation. The motel room is dingy but believable: worn carpet, basic furniture, thin curtains, cheap wall lamp, old bedspread, textured walls, and practical clutter.

He has built an improvised enterprise IT command center using:
- laptop
- external monitor
- keyboard
- mouse
- headset
- cables
- coffee mug
- small desk or motel table
- incident notes
- system dashboard
- network status screen

Through the window, show heavy rain, storm clouds, wet parking lot, motel lights, and visible hurricane weather. The storm should be obvious but not fantasy-level exaggerated.

On the wall or door in the background, include a readable but not dominant sign:
"NO DRUGS / NO PROSTITUTION"

The sign should be visible enough to create the absurd contrast, but it must not become the main subject. The Operator and workstation remain the story.

COMPOSITION:
Use a strong cinematic composition:
- Operator on the right third or center-right, face lit by monitor glow
- large monitor or laptop screen on the left or foreground
- motel room depth visible behind him
- storm visible through window in background
- sign visible in background but secondary
- desk/workstation objects in foreground

The image should work even if all text is removed. The viewer should instantly understand: serious professional work is happening in a ridiculous real-world environment.

LIGHTING:
Use realistic cinematic lighting:
- warm amber motel lamp light
- warm monitor glow on the Operator’s face and hands
- cool blue-gray storm light through the window
- subtle green system status lights on screens
- deep shadows with detail preserved
- high contrast but not crushed blacks
- realistic reflections on glasses, monitor edges, wet window, and desk surfaces

COLOR GRADE:
Use a restrained dark editorial palette:
- deep navy shadows
- charcoal clothing
- warm amber motel lamp
- cool storm blue through window
- muted green dashboard/status lights
- worn brown motel furniture
- aged beige walls
- off-white text if text is used
- warning yellow accents only if needed

Avoid purple, neon pink, glossy SaaS blue, cyberpunk colors, bright startup palette, and overly clean white backgrounds.

TEXT OVERLAY:
If text is required, place it in the lower third with a subtle dark gradient behind it. Use bold condensed sans-serif typography, large white text, with optional yellow accent. Do not cover the Operator’s face, workstation, window storm, or motel sign.

Suggested overlay:
"I Ran Enterprise IT From A Motel That Banned Prostitution"

Secondary small line:
"And it taught me everything about AI."

RECURRING EASTER EGG:
Hide exactly one small red Swingline-style stapler naturally in the workstation area, off-center. Place it near the keyboard, under the desk edge, near the coffee mug, or partly hidden behind cables. It should be visible only after closer inspection. Do not center it, label it, spotlight it, make it glow, or place it in the Operator’s hand.

OPTIONAL SECONDARY DETAIL:
Include one orange towel draped casually over the chair, couch, or laptop bag if it fits naturally. Do not make it a focal point.

AVOID:
No robots. No glowing AI brains. No holographic heads. No cyberpunk city. No generic startup office. No stock-photo smiles. No heroic superhero pose. No fake hacker hoodie. No fantasy storm. No plastic skin. No distorted hands. No unreadable critical text.

IMAGE QUALITY:
High-resolution, realistic, cinematic, editorial, emotionally grounded, detailed, professional. The image should stop a LinkedIn scroll in under two seconds and make an experienced 50-year-old sysadmin think:
"I’ve worked from worse."
```

---

# 4. Claude’s Question 4

## Question

> I’m going to paste a prompt I wrote. Tell me everything you would change about it before sending it to the image generator — and write the enhanced version.

The pasted prompt is a long carousel production sheet for **ART6-from-no-to-safe-enough-yes**, with repeated base prompt blocks for each slide.

## High-Level Diagnosis

The current prompt is strong in raw detail but weak in production architecture.

It has the ingredients, but it is asking the image generator to cook the whole meal in one overstuffed pan.

## Problems To Fix

### Problem 1 — The Base Prompt Is Repeated Too Much

The long master style prompt is repeated for every slide. This bloats the prompt and can dilute the scene-specific instruction.

Better structure:

```text
SYSTEM STYLE BLOCK: constant across all slides
SLIDE-SPECIFIC BLOCK: unique per image
NEGATIVE BLOCK: constant
OUTPUT BLOCK: constant
```

Claude Code should store the style block once and compose prompts programmatically.

### Problem 2 — Too Much Embedded Text

The prompt asks the image generator to render lots of screen labels, gate signs, UI buttons, and overlay text.

This is risky. Even strong image models can mangle text.

Better approach:

1. Generate the clean cinematic image with minimal critical text.
2. Add final overlay text afterward using code, Canva, PIL, Figma, or another deterministic layer.
3. Only ask the image generator to render large environmental labels when absolutely necessary.

### Problem 3 — Scene Archetype Is Sometimes Too Abstract

Example:

> chaotic AI everywhere landscape vs barren no AI zone

This may produce fantasy/metaphorical art instead of grounded enterprise IT realism.

Better:

Use concrete enterprise objects:

- locked doors
- security desk
- approval workflow
- access badge
- ticket queue
- change approval board
- server room glass
- compliance binder
- legal/security review room

### Problem 4 — The Operator Is Sometimes Too Passive

The Operator should not merely stand in the background. He should have a clear operational role:

- gatekeeper
- reviewer
- approver
- diagnostician
- stabilizer
- translator
- controller

Every prompt should answer:

```text
What is The Operator doing that proves experience matters?
```

### Problem 5 — The Stapler Placement Is Sometimes Too Easy Or Too Random

The stapler must fit the environment and difficulty level.

Bad:

```text
Stapler on conference table.
```

Better:

```text
A small red stapler is half-hidden under printed approval forms near the coffee mug on the far edge of the conference table, visible only after close inspection.
```

### Problem 6 — The Carousel Has Too Many Slides

The attached production sheet says 10 slides. Most of the time, 8 is stronger unless the article has a true 10-part escalation.

For LinkedIn, the strongest sequence is usually:

1. Hook
2. Wrong question
3. Risk
4. Human bottleneck
5. Framework
6. Operational proof
7. Identity validation
8. CTA / lesson

### Problem 7 — The Prompt Does Not Separate “Image Generation” From “Final Layout”

Claude Code should not expect the image generator to do everything.

Production pipeline should be:

```text
1. Generate background art.
2. Inspect for composition and visual metaphor.
3. Add overlay text deterministically.
4. Add border deterministically if the model fails.
5. Export final PNG.
6. QA against checklist.
```

This is how to avoid mangled typography and inconsistent borders.

---

# 5. The Secret Recipe

## The Recipe In One Sentence

The images work because they are not “AI images.” They are **recognition machines** for experienced IT operators.

## The 12-Part Recipe

### 1. Start With Audience Identity, Not The Object

Weak prompt:

```text
Create an image of a sysadmin at a gate.
```

Strong prompt:

```text
Create an image that makes a 50-year-old enterprise sysadmin think, "I’ve been in that meeting, and I know exactly what will break."
```

### 2. Assign One Emotional Job Per Image

Do not ask one image to do everything.

Examples:

- Slide 1: curiosity
- Slide 2: disbelief
- Slide 3: stress
- Slide 4: competence
- Slide 5: mystery
- Slide 6: validation
- Slide 7: recognition
- Slide 8: hope

### 3. Use A Repeating Protagonist

The Operator is the brand anchor.

He is:

- older
- calm
- practical
- not trendy
- not impressed by AI
- not hostile to AI
- aware of blast radius
- emotionally stable while others react

### 4. Use Metaphors That Carry The Argument

Good metaphors:

- Permission Gate
- Jenga Tower
- Empty Bob Chair
- Motel Command Center
- Shadow AI Server Rack
- Approval Console
- Castle Moat
- Vendor Lab Experiment

Bad metaphors:

- generic robots
- glowing brains
- floating code
- abstract neon AI
- smiling people pointing at dashboards

### 5. Give The Scene Physical Reality

Strong images include tactile objects:

- cables
- coffee
- keyboard
- old runbooks
- sticky notes
- badges
- binders
- printed tickets
- workstations
- motel lamps
- server racks

Physical reality is what makes the images feel credible.

### 6. Control Lighting Like A Cinematographer

The consistent lighting recipe:

```text
Warm human light + cold technical light + practical environmental light.
```

Examples:

- warm monitor glow on face/hands
- amber desk lamp or motel lamp
- cool blue storm/server/dashboard light
- muted green status LEDs

### 7. Use A Restricted Color Grade

The recurring palette is:

- deep navy
- charcoal
- black
- storm blue
- amber practical light
- muted green LEDs
- aged beige paper
- warning yellow accent
- off-white typography

This palette is why the images feel like the same universe.

### 8. Avoid AI Clichés Aggressively

Always include negative constraints:

```text
No robots, no glowing AI brains, no holographic human heads, no cyberpunk city, no stock-photo smiles, no Silicon Valley startup office, no glossy SaaS marketing, no purple neon, no fake futurism.
```

### 9. Make The Image Work Without Text

The rule:

```text
If all text disappeared, the viewer should still understand the joke, tension, or lesson.
```

This prevents prompt-dependent poster slop.

### 10. Use The Red Stapler As A Reward, Not A Prop

The stapler is a hidden engagement system.

It should be:

- present
- natural
- off-center
- unmentioned
- findable
- never the subject

### 11. Generate Art First, Add Text Later When Possible

This is critical for Claude Code.

For best quality:

```text
Prompt the image model for cinematic scene + negative space.
Then add overlay text using deterministic code.
```

Use image generation for atmosphere and composition. Use code for exact typography.

### 12. QA Like A Sysadmin

Every image must pass:

- 2-second comprehension test
- no generic AI cliché test
- Operator consistency test
- visual metaphor test
- red stapler test
- text readability test
- emotional job test
- mobile crop test

---

# 6. Recommended Claude Code Prompt Architecture

Claude Code should not create one giant handwritten prompt manually each time.

It should assemble prompts from reusable blocks.

## Prompt Object Structure

```json
{
  "asset_type": "carousel_slide",
  "dimensions": "1080x1350",
  "style_block": "cinematic_editorial_realism",
  "character_block": "the_operator_v1",
  "scene_archetype": "permission_gate",
  "emotional_job": "recognition",
  "scene_specifics": "locked enterprise security gate protecting PII, PROD, HR DATA, FINANCE, IDENTITY",
  "operator_action": "stands calmly with clipboard and badge enforcing safe access",
  "lighting_block": "warm_monitor_cool_server",
  "color_block": "dark_editorial_navy_amber_green_yellow",
  "composition_block": "foreground_midground_background",
  "easter_egg": {
    "object": "red Swingline-style stapler",
    "placement": "half-hidden behind a coffee mug on the checkpoint desk",
    "difficulty": "medium"
  },
  "overlay": {
    "text": "The hard part is permission.",
    "placement": "top third",
    "render_in_generator": false
  },
  "negative_constraints": "no robots, no glowing AI brains, no cyberpunk, no stock-photo smiles"
}
```

## Prompt Assembly Order

```text
1. Asset type and size
2. Core audience and message
3. Style and mood
4. Operator description
5. Scene-specific visual metaphor
6. Operator action
7. Foreground / midground / background
8. Lighting
9. Color grade
10. Easter egg
11. Negative constraints
12. Text strategy / negative space
13. Output quality instructions
```

---

# 7. Enhanced Version Of The Attached Prompt Strategy

The attached prompt is directionally good, but Claude Code should refactor it into this:

```text
Create a LinkedIn carousel slide in the Sysadmin AI Survival Playbook / IT→AI Transition Playbook style.

Asset: 1080 x 1350 vertical carousel slide with clean white documentary border.

Audience: experienced Gen-X enterprise IT professionals, sysadmins, infrastructure operators, ServiceNow admins, software analysts, and IT people with 20–30 years of operational experience who are skeptical of AI hype and worried about relevance.

Core brand idea: experienced IT professionals are not obsolete. AI can assist, but human judgment, context, institutional memory, and operational responsibility decide what is safe.

Style: cinematic editorial realism, Wall Street Journal feature photo crossed with gritty IT field manual. Realistic, dark, grounded, professional, slightly worn. Dry world-weary competence. Serious but subtly humorous.

The Operator: male Gen-X enterprise sysadmin, early-to-mid 50s, salt-and-pepper hair, tired but sharp eyes, average build, practical dark business-casual clothing, calm under pressure, focused and skeptical, never panicking, never posing, never amazed by technology. He is the most emotionally stable person in the scene.

Scene archetype: [INSERT ARCHETYPE]
Emotional job: [INSERT EMOTION]
Viewer takeaway: [INSERT TAKEAWAY]

Scene: [INSERT CONCRETE SCENE DESCRIPTION]

Operator action: [INSERT WHAT HE IS DOING THAT PROVES EXPERIENCE MATTERS]

Composition: foreground contains tactile operational details; midground contains The Operator and the work surface or decision point; background contains the tension or metaphor. Use rule-of-thirds composition. The image must work without text.

Lighting: warm amber practical light or monitor glow on the Operator; cool blue-gray server/dashboard/storm light in the environment; muted green status LEDs; deep shadows with detail preserved; realistic reflections.

Color grade: deep navy, charcoal, black, storm blue, amber light, muted green status lights, aged paper beige, warning yellow accents, off-white type. Avoid purple, neon pink, glossy SaaS-blue, bright startup colors, cyberpunk palette.

Hidden easter egg: exactly one small red Swingline-style stapler, [INSERT PLACEMENT], off-center, natural, unlabelled, not glowing, not oversized, visible only after close inspection.

Negative constraints: no robots, no glowing AI brains, no holographic heads, no cyberpunk city, no stock-photo smiles, no startup founder aesthetic, no generic SaaS marketing, no plastic skin, no distorted hands, no unreadable critical text.

Text strategy: leave clean negative space for overlay text. Do not rely on the image generator for precise final typography unless the text is short and large. Final overlay will be added afterward if needed.

Output: high-resolution, realistic, cinematic, emotionally grounded, mobile-readable LinkedIn image that stops the scroll and makes a 50-year-old sysadmin think, "I’ve been there."
```

---

# 8. What Claude Should Change Immediately

## Stop Doing This

```text
Generate the full carousel with embedded text, exact UI labels, all visual jokes, all signs, all overlays, all easter eggs, and all brand rules in one pass.
```

## Start Doing This

```text
Generate one clean cinematic image per slide with strong composition and negative space.
Add text overlays deterministically afterward.
QA each final slide against the brand checklist.
```

## Recommended Production Pipeline

```text
1. Analyze article.
2. Pick visual metaphor.
3. Assign emotional arc.
4. Create storyboard.
5. Generate clean background scenes.
6. Add overlays with code.
7. Add border with code if needed.
8. Export ordered PNGs.
9. Package caption + CTA + checklist.
10. Fix only broken slides.
```

---

# 9. Final Note For Claude

The “secret” is not a magic model setting.

The secret is **visual continuity plus emotional specificity**.

The images are better because they are built from a repeatable brand universe:

- The Operator
- the red stapler
- the white documentary frame
- cinematic editorial realism
- Gen-X sysadmin physical reality
- enterprise chaos
- operational judgment
- one clear metaphor per image
- one emotional job per slide
- anti-AI-cliché constraints
- deterministic text overlay whenever possible

The generator is only one part of the system.

The real image quality comes from the prompt architecture and the QA discipline.

Or, in sysadmin terms:

The model is the server.

The prompt system is the architecture.

The QA pass is change control.

Do not skip change control.

---

# 10. Update — How Claude Code Can Connect To The OpenAI Image Generation Engine

## Short Answer

Claude Code cannot directly call ChatGPT’s internal `image_gen` tool.

The practical equivalent is for Claude Code to call the **OpenAI API** using an OpenAI API key and one of the GPT Image models through either:

1. **Responses API with the `image_generation` tool**, or  
2. **Images API**.

For this project, the best production path is:

```text
Claude Code → OpenAI API → GPT Image model → generated base image → local post-processing → final LinkedIn PNG
```

Do **not** rely on the image model to do every final production task perfectly. Use the image model to create the cinematic scene, then use code to add:

- exact LinkedIn crop
- clean white border
- final typography
- consistent lower-third gradient
- final export filenames

That is the difference between “pretty AI image” and “repeatable content production system.”

---

## 10.1 Recommended Model Strategy

Use the newest GPT Image model available to the account.

Recommended order:

```text
1. gpt-image-2, if available
2. gpt-image-1, if gpt-image-2 is unavailable
```

Do **not** assume DALL·E 3 is the best match for these images. The established look was built around modern GPT Image behavior: strong instruction following, realistic details, world knowledge, scene consistency, and a long production prompt.

Important limitation:

```text
The ChatGPT consumer image tool may not expose the exact same backend behavior as the API.
```

So Claude Code should not chase a hidden “magic ChatGPT engine.” It should reproduce the **production method**:

- detailed prompt architecture
- controlled visual metaphor
- Operator character definition
- lighting/color grade instructions
- negative constraints
- post-processing overlays
- QA pass

---

## 10.2 Environment Setup For Claude Code

Claude Code needs an OpenAI API key available as an environment variable.

### macOS / Linux

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### Windows PowerShell

```powershell
$env:OPENAI_API_KEY="sk-your-key-here"
```

Do not hard-code the API key in scripts.

---

## 10.3 Node.js Example — Responses API Image Generation

Install the OpenAI SDK:

```bash
npm install openai
```

Create `generate-image.mjs`:

```js
import OpenAI from "openai";
import fs from "fs";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const prompt = `
Create a cinematic editorial LinkedIn article hero image in the Sysadmin AI Survival Playbook style.

Scene: A calm Gen-X enterprise sysadmin Operator in his early-to-mid 50s works from an improvised motel command center during a hurricane. He wears a headset and practical dark clothing, with salt-and-pepper hair, tired but sharp eyes, calm under pressure. He sits at a desk with a laptop, external monitor, keyboard, mouse, coffee mug, cables, and incident notes. Outside the motel window, hurricane rain and palm trees bend in the storm. A realistic motel room surrounds him, including worn furniture, cheap lamp light, patterned bedspread, and a wall sign reading NO DRUGS / NO PROSTITUTION. Warm amber monitor and lamp light on the Operator, cool blue-gray storm light through the window, green status lights on the screen. Dry world-weary competence. Realistic Wall Street Journal feature photo crossed with gritty IT field manual. No robots, no glowing AI brains, no cyberpunk, no stock-photo smiles.

Hide exactly one small red Swingline-style stapler naturally on the desk, off-center, partly obscured, visible only after close inspection.

Leave room in the lower third for a title overlay that will be added later. Do not render final headline text in the image.
`;

const response = await openai.responses.create({
  model: "gpt-5.5",
  input: prompt,
  tools: [{ type: "image_generation" }],
});

const imageBase64 = response.output
  .filter((item) => item.type === "image_generation_call")
  .map((item) => item.result)[0];

if (!imageBase64) {
  throw new Error("No image returned from image_generation tool.");
}

fs.writeFileSync("generated_base.png", Buffer.from(imageBase64, "base64"));
console.log("Saved generated_base.png");
```

Run:

```bash
node generate-image.mjs
```

This route is useful when Claude Code is already orchestrating a broader content-generation pipeline with text analysis, storyboard generation, QA notes, and image generation in one process.

---

## 10.4 Python Example — Responses API Image Generation

Install the SDK:

```bash
pip install openai
```

Create `generate_image.py`:

```python
from openai import OpenAI
import base64

client = OpenAI()

prompt = """
Create a cinematic editorial LinkedIn feed post image in the Sysadmin AI Survival Playbook style.

Scene: A calm Gen-X enterprise sysadmin Operator in his early-to-mid 50s works from a budget motel room during a storm. He wears a headset, has salt-and-pepper hair, tired but sharp eyes, and practical dark clothing. He sits at an improvised workstation with laptop, external monitor, keyboard, coffee mug, cables, outage dashboard, and incident notes. The motel room is worn and realistic, with cheap lamp light, old curtains, patterned bedspread, and a wall sign reading NO DRUGS / NO PROSTITUTION. Rain streaks the window. Outside, a red motel sign glows through the storm. Warm amber monitor glow on his face and hands, cool blue storm light from the window, subtle green server/status lights. The mood is calm competence surrounded by absurd enterprise chaos.

Hide exactly one small red Swingline-style stapler naturally near the keyboard, off-center and partly obscured. No robots, no glowing AI brains, no cyberpunk, no stock-photo smiles, no glossy SaaS marketing look.

Leave clean lower-third negative space for overlay text to be added later. Do not render final headline text in the image.
"""

response = client.responses.create(
    model="gpt-5.5",
    input=prompt,
    tools=[{"type": "image_generation"}],
)

image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if not image_data:
    raise RuntimeError("No image returned.")

with open("generated_base.png", "wb") as f:
    f.write(base64.b64decode(image_data[0]))

print("Saved generated_base.png")
```

Run:

```bash
python generate_image.py
```

---

## 10.5 Images API Alternative

Claude Code can also use the Images API directly.

A typical request should include:

```text
model: gpt-image-2 or gpt-image-1
prompt: production prompt
size: 1536x1024 for article hero landscape OR 1024x1536 for vertical post/carousel
quality: high
output_format: png
```

Important: API image sizes are not always the exact LinkedIn final sizes.

Use this mapping:

| Final Asset | Generate With API | Then Post-Process To |
|---|---:|---:|
| LinkedIn Article Hero | 1536 x 1024 | 1376 x 768 with white border |
| LinkedIn Feed Post | 1024 x 1536 | 1080 x 1350 with white border |
| LinkedIn Carousel Slide | 1024 x 1536 | 1080 x 1350 with white border |
| Square Avatar | 1024 x 1024 | 300 x 300 |

This matters because the exact LinkedIn dimensions should be handled by code, not left to the image generator.

---

## 10.6 Recommended Production Architecture For Claude Code

Claude Code should not try to make the image generator produce the final polished LinkedIn slide in one shot.

Use this production architecture instead:

```text
1. Analyze article/post.
2. Identify emotional job.
3. Choose visual metaphor.
4. Write image prompt.
5. Generate clean cinematic base image with minimal or no embedded text.
6. Use code to crop/pad to final LinkedIn dimensions.
7. Use code to add white border.
8. Use code to add lower-third dark gradient if needed.
9. Use code to add exact typography.
10. Export final PNG.
11. QA against brand checklist.
```

Why this is better:

- image models can mangle text
- generated signs can drift
- exact dimensions are easier in code
- repeated carousel typography needs consistency
- the white border should be pixel-perfect
- future carousels need repeatability

Image model creates the world.

Code finishes the asset.

That is the recipe.

---

# 11. Verification Of The Two Attached Favorite Images

The two attached images are absolutely reproducible by the system described in this markdown file.

They are not “lucky one-offs.”

They are strong because they follow the same brand recipe:

```text
The Operator + absurd real-world enterprise setting + cinematic lighting + warm/cool contrast + white border + minimal strong text + Gen-X sysadmin recognition + no generic AI clichés.
```

The two images should be treated as **canonical reference examples** for future Claude Code generation.

---

## 11.1 Image 1 — Hurricane Motel Article Hero

### File

```text
Hurricane_hero.png
```

### Observed Format

```text
Current file dimensions: 1678 x 937 px
Intended final use: LinkedIn article hero / landscape header
Recommended production target: generate 1536 x 1024, then crop/pad/export to 1376 x 768 with clean white border
```

### Why This Image Works

This is one of the strongest visual assets because it communicates the entire article in under two seconds.

It contains:

- The Operator in profile, wearing a headset
- serious enterprise dashboard screens
- improvised motel command center
- hurricane visible through the window
- warm motel lamp and monitor light
- cool storm light outside
- “NO DRUGS / NO PROSTITUTION” sign on the wall
- cheap motel bed and furniture
- professional workstation in an unprofessional environment
- lower-third title overlay with strong hierarchy
- white documentary border

The image works because the viewer immediately understands the contradiction:

```text
The environment is absurd.
The work is serious.
The Operator is calm.
```

That is the brand.

### Reproduction Prompt For Claude Code / OpenAI API

```text
Create a cinematic editorial LinkedIn article hero image in the Sysadmin AI Survival Playbook / IT→AI Transition Playbook visual style.

Final intended asset: LinkedIn article hero image, landscape format. Generate in 1536 x 1024 and leave safe room for cropping/export to 1376 x 768 with a clean white documentary-style border.

Core emotional idea: An experienced Gen-X enterprise IT operator keeps production alive from an absurd motel command center during a hurricane. The scene should make a 50-year-old sysadmin think, “I’ve been there.”

Style: cinematic editorial realism, like a Wall Street Journal feature photograph crossed with a gritty IT field manual. Realistic, grounded, professional, detailed, emotionally tense, not stock photography, not glossy SaaS marketing.

Main character — The Operator: male Gen-X enterprise sysadmin, early-to-mid 50s, salt-and-pepper hair, tired but sharp eyes, average build, practical dark clothing, wearing a headset, calm under pressure, focused, skeptical, grounded, emotionally stable. He is not panicking, not smiling broadly, not posing, not acting amazed by technology. He looks like the person who keeps production alive while everyone else creates chaos.

Scene: A worn budget motel room during a hurricane. The Operator sits at a real improvised enterprise IT workstation: large external monitor showing dashboards and system status, laptop, keyboard, mouse, headset, cables, coffee mug, incident notes, and a small hurricane evacuation checklist on the desk. The professional workstation should look sharp and serious, completely out of place in the cheap motel room.

Environment details: worn motel bed with patterned bedspread on the right, cheap motel wall lamp, textured beige walls, old curtains, wall-mounted air conditioner, cluttered but believable travel/IT setup, window showing hurricane rain, dark storm clouds, palm trees bending in the wind, wet parking lot lights outside. On the wall near the door, include a readable but not dominant red-and-white sign: “NO DRUGS / NO PROSTITUTION.”

Composition: landscape hero composition. The Operator sits slightly right of center, facing left toward the monitors. Monitors and desk occupy the left third. Storm window and motel sign occupy the background. Bed and motel room details occupy the right side. Leave a clean lower-third zone for title overlay without covering the Operator’s face, monitors, storm, or motel sign. Use rule-of-thirds composition and strong depth.

Lighting: warm amber monitor glow and motel lamp light on the Operator’s face, arms, and workstation. Cool blue-gray storm light through the window. Subtle green dashboard/status lights on screens. Deep shadows with detail preserved. High contrast but not crushed blacks. Realistic screen reflections and practical motel lighting.

Color grade: deep navy, charcoal, storm blue, muted brown, aged beige wall tones, amber practical light, cool cyan dashboard glow, muted green status lights, off-white typography zone. Avoid purple, neon pink, cyberpunk colors, glossy startup colors, over-clean white backgrounds.

Recurring easter egg: hide exactly one small red Swingline-style stapler naturally on or near the workstation, off-center and partly obscured by desk clutter or a coffee mug. It must not be centered, labeled, glowing, oversized, or in the Operator’s hand. It should be visible only after close inspection.

Avoid: no robots, no glowing AI brains, no holographic faces, no futuristic city, no stock-photo smiles, no young tech founder, no hacker hoodie stereotype, no fantasy armor, no plastic skin, no distorted hands, no unreadable critical text, no polished corporate stock-photo look.

Text overlay: reserve lower third for text overlay to be added in post-processing. If rendering text directly, use bold condensed sans-serif white title text with a subtle dark gradient behind it and a thin electric-blue vertical accent line at the left. Text should read: “I Ran Enterprise IT From a Motel That Banned Prostitution —” with smaller subtitle “And It Taught Me Everything About AI.” Text must be mobile-readable and must not cover the Operator’s face or workstation.

Final result should feel like a captured operational war story: professional competence in a ridiculous environment, hurricane outside, enterprise systems inside, calm Operator in the middle.
```

---

## 11.2 Image 2 — Hurricane Motel Vertical Post / “Where’s Bob?”

### File

```text
Hurricane_post.png
```

### Observed Format

```text
Current file dimensions: 1024 x 1536 px
Intended final use: LinkedIn feed post / vertical image
Recommended production target: generate 1024 x 1536, then crop/pad/export to 1080 x 1350 with clean white border if needed
```

### Why This Image Works

This image is strong because it shifts from article hero to operator-centered recognition humor.

It contains:

- tight vertical portrait composition
- The Operator in side profile
- headset and keyboard
- monitor dashboards close to the viewer
- motel room background
- storm/rain through the window
- red motel sign outside
- “NO DRUGS / NO PROSTITUTION” sign in background
- warm/cool lighting contrast
- lower-third dark gradient
- short quotation-style overlay text
- white border

The overlay works because it is not generic motivation. It sounds like a real bridge-call panic moment:

```text
“The printers just went offline.”
“Does anyone know the print server’s IP?”
“Where’s Bob?”
```

That is exactly the kind of line experienced IT people recognize.

### Reproduction Prompt For Claude Code / OpenAI API

```text
Create a cinematic editorial LinkedIn feed post image in the Sysadmin AI Survival Playbook / IT→AI Transition Playbook visual style.

Final intended asset: vertical LinkedIn post image. Generate in 1024 x 1536 and leave safe room for post-processing/export to 1080 x 1350 with a clean white documentary-style border.

Core emotional idea: A calm experienced Gen-X sysadmin is running enterprise IT from a sketchy motel command center during a storm while the organization panics over an undocumented print server and missing institutional knowledge. The image should create instant recognition for experienced sysadmins: “Every company has a Bob.”

Style: cinematic editorial realism, serious but subtly humorous, like a documentary IT war-story photograph crossed with a gritty enterprise field manual. Realistic, grounded, professional, slightly worn, not stock photography and not AI-bro futurism.

Main character — The Operator: male Gen-X enterprise sysadmin, early-to-mid 50s, salt-and-pepper hair, slightly tired but sharp eyes, average build, wearing glasses and a headset, practical dark hoodie or dark casual workwear, calm under pressure, focused on the screen, emotionally stable. He is not panicking, not smiling broadly, not posing for the camera, not amazed by technology. He is quietly working the problem.

Scene: Tight vertical composition inside a worn budget motel room during heavy rain. The Operator sits on the right side of the frame in profile, facing left toward a large monitor and laptop. His hands are on a mechanical keyboard. The foreground left contains the monitor with enterprise system status dashboards, server health indicators, network overview, active alerts, storage usage, terminal/log output, and green system status lights. A laptop is open below the monitor. A coffee mug sits on the desk.

Environment details: cheap motel bed in the background, old curtains, rain-streaked window, red motel sign glowing outside, warm lamp on the right, textured beige wall, wall sign in the background reading “NO DRUGS / NO PROSTITUTION.” The room should feel real, slightly dingy, and practical, not exaggerated.

Composition: vertical portrait. Monitor and dashboard dominate the left third. Operator profile dominates the right third. Motel window and background sign sit in the upper middle/background. Lower third should have clean dark gradient space for large quote text. The Operator’s face and hands must remain visible and not be covered by text.

Lighting: warm amber desk/lamp light on the Operator’s face, hands, and keyboard. Cool blue-gray rain light through the window. Screen glow from dashboards on the left side of his face and hands. Subtle green status indicators on the screen. High contrast with detail preserved in shadows. Realistic reflections on glasses, monitor, and headset.

Color grade: dark editorial palette with deep navy, charcoal, muted brown, storm blue, cool cyan dashboard glow, amber practical lamp light, muted green status lights, off-white text. Avoid purple, neon pink, rainbow gradients, glossy SaaS colors, over-clean white backgrounds, cyberpunk neon.

Recurring easter egg: hide exactly one small red Swingline-style stapler naturally on the desk near the keyboard or partly behind the coffee mug, off-center and visible only after close inspection. Do not center it, label it, glow it, oversize it, or put it in the Operator’s hand.

Optional desk detail: coffee mug may read “CAFFEINE PATCHES PATIENCE” or another dry sysadmin phrase, but do not let the mug text become more important than the scene.

Avoid: no robots, no glowing AI brains, no holographic people, no cyberpunk city, no stock-photo smiles, no startup founder look, no exaggerated comedy faces, no plastic skin, no distorted hands, no fantasy lighting.

Text overlay: reserve the lower third for deterministic typography added after generation. If the image generator renders the text directly, use bold condensed sans-serif white quote text with subtle shadow and a thin electric-blue vertical accent line at the left. Text should read exactly:

“The printers just went offline.”
“Does anyone know the print server’s IP?”
“Where’s Bob?”

The text must be large, mobile-readable, and placed over a dark lower-third gradient. It must not cover the Operator’s face, hands, keyboard, monitor dashboards, motel sign, or window.

Final result should feel like an absurd but believable IT incident snapshot: professional competence, motel-room chaos, storm outside, dashboard glow inside, and the universal panic of needing the one person who knows the undocumented system.
```

---

# 12. Claude Code QA Checklist For Recreating These Two Images

Claude Code should not accept the first image just because it is “pretty.”

Use this checklist.

## Hero Image QA

```text
[ ] Landscape composition works as article header.
[ ] Operator is calm and competent.
[ ] Motel room is realistic, not cartoonish.
[ ] Hurricane is visible through the window.
[ ] Professional workstation contrasts with sketchy motel.
[ ] NO DRUGS / NO PROSTITUTION sign is readable but not dominant.
[ ] Warm lamp/monitor light contrasts with cool storm light.
[ ] Lower third has room for title overlay.
[ ] White border is clean and consistent.
[ ] Red stapler is present but not obvious.
[ ] No robots or glowing AI brains.
[ ] Image still communicates the story without text.
```

## Vertical Post QA

```text
[ ] Vertical portrait composition works for LinkedIn feed.
[ ] Operator profile is strong and emotionally calm.
[ ] Monitor dashboard reads as enterprise IT, not generic sci-fi.
[ ] Motel room remains visible in background.
[ ] Storm/rain is visible through window.
[ ] NO DRUGS / NO PROSTITUTION sign is visible but not focal.
[ ] Lower-third text is mobile-readable.
[ ] Text sounds like real IT incident dialogue.
[ ] White border is clean.
[ ] Red stapler is hidden naturally.
[ ] Image creates “Where’s Bob?” recognition.
[ ] No stock-photo corporate energy.
```

---

# 13. Final Instruction To Claude Code

If Claude Code wants images closer to these two examples, it should stop treating image generation as one prompt.

Treat it as a production pipeline:

```text
1. Use the long visual-universe prompt.
2. Generate the cinematic/documentary base image.
3. Add exact text overlay in code when possible.
4. Add white border in code.
5. Crop/export to LinkedIn dimensions in code.
6. QA against the recognition test.
```

The recognition test is the final judge:

```text
If all text were removed, would a 50-year-old sysadmin still understand the tension, joke, or lesson?
```

If the answer is no, regenerate.

The goal is not prettier AI art.

The goal is **recognition**.

Important technical clarification: Claude Code cannot directly call ChatGPT’s internal image tool, but it can call the OpenAI API using an API key. The current OpenAI docs describe image generation through the Responses API with an image_generation tool and through the Images API; the docs also state that GPT Image models can use text and image inputs to generate or edit images.

For final LinkedIn production, the Images API supports common output sizes such as 1024x1024, 1024x1536, and 1536x1024, so Claude Code should generate close-aspect images first, then crop/pad/export to your exact LinkedIn sizes in code.

    paraphrasing the Wolf from Pulp fiction: About the md file, is there anything I  
                         need to know? Does it stall, does it 
                         make a lot of noise, does it smoke, 
                         is there gas in it, anything? lol
Worked for 28s
Wolf-style status report on the MD file

Yeah — there are a few things you need to know before you hand this thing to Claude Code and tell it to drive.

The file has gas in it. It starts. It does not smoke badly. But it will rattle if Claude Code treats it like a single magic prompt instead of a production workflow.

What’s good

The MD file gives Claude Code the full recipe:

how to connect to OpenAI image generation through the API
why Claude cannot directly use ChatGPT’s internal image tool
how to generate close-aspect images first
why final LinkedIn sizing needs post-processing
how to recreate the two attached reference images
production prompts for the Hurricane Hero and Where’s Bob? style images
QA rules for checking whether the results are actually close

That matches the technical clarification already captured: Claude Code can’t call ChatGPT’s internal image generator directly, but it can call the OpenAI API with an API key. The file also notes that final LinkedIn dimensions may require generating a close aspect ratio first, then cropping/padding/exporting to the exact final size.

What may stall
1. Exact dimensions

OpenAI image generation may not give you exact custom LinkedIn sizes directly.

So for these:

1376 x 768
1080 x 1350
1200 x 627

Claude Code should generate the closest supported aspect ratio, then use code to crop/pad/resize/export.

That is not a bug. That is the transmission making a little noise before second gear.

2. Text inside the image

The file contains overlay instructions, but image models can still mangle text.

Best production workflow:

Generate the image with minimal or no embedded text.
Add title overlays afterward with Python/Pillow, Canva, Photoshop, or another deterministic renderer.
Export final LinkedIn-ready PNG.

This is especially important for long titles like:

I Ran Enterprise IT From a Motel That Banned Prostitution — And It Taught Me Everything About AI

The model may get close, but “close” on text is how you get haunted refrigerator magnet poetry.

3. The white border

Tell Claude Code not to rely only on the image model for the border.

The image prompt can request a clean white border, but Claude Code should also add the final white border in post-processing so it is consistent every time.

4. The red stapler

The stapler may be too obvious, too hidden, or missing.

That is normal. The file explains the rule, but the model may not obey perfectly. The QA step matters. Earlier slide QA already showed this exact issue: some staplers worked, some were too obvious and started acting like props instead of easter eggs.

5. The Operator may drift

Claude Code needs to keep The Operator description in every prompt.

If it shortens the prompt too aggressively, the Operator may turn into:

generic AI dashboard guy
cybersecurity stock-photo man
tech founder in a hoodie
sad helpdesk dad
handsome silver-haired consultant pointing at charts

That’s the smoke coming out of the tailpipe.

The biggest warning

Do not let Claude Code feed the entire MD file as one giant prompt every time.

That will get noisy and expensive.

Instead, it should use the MD file as a reference system, then assemble a shorter production prompt per image:

Base visual style
+ Operator definition
+ scene archetype
+ lighting/color rules
+ composition rules
+ text overlay rule
+ stapler placement
+ negative constraints
+ output/post-processing instructions

The best version of the process is the 3-pass workflow we already locked down:

Storyboard
Full image build
Final QA and fix only broken slides

That workflow is explicitly part of the carousel system: storyboard first, generate after approval, QA once, then fix only what is broken.

Can the two attached images be recreated?

Yes — with a caveat.

They can be recreated in style, structure, mood, lighting, and composition.

They probably cannot be recreated as pixel-perfect identical images unless Claude Code uses the originals as image references and performs image editing or variation. But the MD file should absolutely be able to guide Claude Code toward:

Hurricane Hero
landscape article hero
motel command center
storm visible outside
warm motel lamp vs cold storm light
Operator calm at workstation
“NO DRUGS / NO PROSTITUTION” sign
lower-third bold white typography
clean white border
Vertical “Where’s Bob?” Post
vertical LinkedIn post
close operator workstation view
motel/server dashboard atmosphere
cool monitor glow
warm lamp light
quote-style lower-third text block
calm Operator
dark gradient behind typography
white border

Those two images work because they follow the strongest system rules: cinematic editorial realism, Gen-X sysadmin recognition, Operator consistency, white documentary border, restrained palette, and clear under-two-second comprehension. The broader system also says the image should create recognition and make the reader think “I’ve been there,” not merely summarize the article.

My blunt operator recommendation

The MD file is good enough to hand to Claude Code.

But tell Claude Code this:

Do not treat this markdown as one prompt.

Treat it as a production manual.

For each image, extract the relevant rules, build one focused prompt, generate the closest supported aspect ratio, then post-process to the exact LinkedIn size with border and text overlays.

That’s the difference between:

“The car starts.”

and:

“The car gets you to Winston Wolf’s house without leaving fluids on the driveway.”

