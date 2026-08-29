# Riddle of Steel — Operator Evidence Interview (Stage 1 MVP)

A live, no-copy-paste version of the "Total Recall" interview prompts
already written into the guide itself (`knowledge/products/lead-magnets/
steel_server_room_lead_magnet_final/steel_server_room_lead_magnet_final.md`,
Section 09, Prompts 1–3) — those prompts already assumed the reader would
paste them into their own ChatGPT/Claude account by hand. This tool does
that step for them, matching Adam Dukes' "$100/Day Game Plan" pattern
Randy referenced: a short live interview → a personalized output, not a
document to read.

Built 2026-08-13 as a direct copy of `products/texas-landlord-guide/
web-tool`'s scaffold — that build is the template, this reuses its
architecture wholesale (3-tier fallback, KV rate limiting, admin bypass,
backup-tier banner). No content in the guide itself was rewritten — the
interview/brief prompts used here are verbatim from Section 09, not new
copywriting, so this doesn't touch the production freeze on the guide's
own text.

## Architecture

- **One Cloudflare Worker** (`src/worker.js`) — serves the page (GET /),
  runs the interview (POST /chat), and produces the final brief
  (POST /finalize). No separate frontend build, no hosting plan.
- **3-tier answer chain** — identical to the Texas Landlord tool:
  Anthropic (`claude-sonnet-4-6`, primary) → Gemini (`gemini-2.5-flash`,
  free tier) → Cloudflare Workers AI (free, edge-native, last resort).
  Every non-primary tier shows an on-screen backup banner.
- **Interview flow:** the AI asks one question at a time (Prompt 1,
  verbatim) about outages, migrations, fragile systems, undocumented
  dependencies, ugly workarounds, security decisions, business-risk
  situations, and moments where judgment mattered. Full conversation
  history is passed with every request (Workers are stateless — no
  server-side session, the client just resends the transcript).
- **Offer + email gate:** after `INTERVIEW_TURNS_BEFORE_OFFER` (currently
  4) real answers, the page offers to generate the brief. Email is
  required before the final output is shown — same two-tier-funnel role
  the existing PDF opt-in plays today (Monetization #10 in
  `content-engine/launch_playbook/monetization_ideas.md`).
- **Finalize:** combines Prompt 2 (incident brief structure) + Prompt 3
  (resume bullet options), run against the actual interview transcript —
  not invented, not templated from nothing.
- **Rate limiting:** Workers KV, per-IP, resets daily.
  `RATE_LIMIT_PER_DAY = 10` — placeholder, confirm with Randy.
- **Lead storage — Stage 1 only:** captured emails are logged into the
  same KV namespace as a `lead:<timestamp>:<email>` key. No ESP
  (Mailchimp/ConvertKit/etc.) wired up yet — Randy pulls this list
  manually via `wrangler kv key list` until real volume justifies
  automating it. This is the intentional Stage 1 shortcut per the
  20-Minute MVP Staging Rule — Stage 2 (Polish) would wire this to a real
  list instead.
- **Admin testing bypass:** same pattern as Texas Landlord — an
  `X-Admin-Key` header, checked before rate limiting, never present in
  client-side JS.

## Real decisions still needed from Randy before this goes live

1. **`RATE_LIMIT_PER_DAY`** — currently a 10/day/IP placeholder (a real
   interview session uses more calls per visitor than a single Q&A
   question, so this should probably be lower than Texas Landlord's 5, not
   higher — flagging this as worth a second look, not a made decision).
2. **`INTERVIEW_TURNS_BEFORE_OFFER`** — currently 4. Adam Dukes' tool was
   described as "10 minutes" — 4 real answers may be short or long
   relative to that, untested.
3. **Where captured emails actually go** — KV-only for now (see above).
   Confirm this is acceptable for Stage 1, and what volume should trigger
   wiring a real ESP.
4. **Deploy go-ahead** — not yet run. Same Cloudflare-auth blocker
   documented in the Texas Landlord tool's README may apply here too
   (same account) — check whether that's been resolved before assuming
   this one will deploy cleanly.

## Deployment steps (not yet run)

```
cd products/riddle-of-steel-interview-tool/web-tool
npx wrangler kv namespace create RATE_LIMIT
# paste the returned id into wrangler.toml's [[kv_namespaces]] id field
npx wrangler secret put ANTHROPIC_API_KEY
npx wrangler secret put GEMINI_API_KEY
npx wrangler secret put ADMIN_BYPASS_KEY
npx wrangler deploy
```

Both API keys already exist as real values in the project's own `.env` —
reuse those when the CLI prompts for the secret value, don't generate new
ones. Uses the existing Cloudflare account (`region5dl@gmail.com`, see
`memory/reference_cloudflare_accounts.md`) — no new account needed.

## Status

**Live, deployed 2026-08-13:** https://riddle-of-steel-interview.region5dl.workers.dev

End-to-end verified via the admin-bypass curl command (real Anthropic
response confirmed, interview flow works as designed). `admin_bypass_key
.secret` (this folder) holds the real generated admin key — gitignored
via `*.secret`.

The Cloudflare deploy blocker on the Texas Landlord tool (see that
project's own README) turned out to be a real bug, not a permissions
issue — `.env`'s `CF_API_TOKEN` had been accidentally overwritten with
the literal text `npx wrangler login`. Fixed by clearing it and running a
real OAuth `wrangler login`. Same account, so this tool deployed cleanly
right after.

This is the Stage 1 (Validate) build per the 20-Minute MVP Staging Rule —
rough on purpose: no styling polish, no ESP integration, no analytics.
The only question it's built to answer is whether the interview-then-brief
pattern actually works and whether visitors will complete it. Stage 2
(Polish) and Stage 3 (Build, if warranted) come only after that's proven.
