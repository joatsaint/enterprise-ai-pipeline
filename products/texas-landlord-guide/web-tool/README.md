# Texas Landlord Advisor — interactive Stage 1 MVP

A free, public, interactive version of `products/texas-landlord-guide/
03_the_prompt.md`, delivered as a single Cloudflare Worker. This is the
frictionless-lead-magnet build discussed 2026-08-12 — replaces the
"static PDF" lead-magnet pattern with a live Q&A tool, same pattern
could later apply to the Steel/Sysadmin project once this one proves out.

## Architecture

- **One Cloudflare Worker** (`src/worker.js`) — serves the page (GET /)
  and handles questions (POST /ask). No separate frontend build, no
  hosting plan.
- **3-tier answer chain:**
  1. **Anthropic API, `claude-sonnet-4-6`** — primary, real per-query
     cost (~$0.01–$0.02/question, see Cost section below).
  2. **Gemini API, `gemini-2.5-flash`** — free tier (1,500 requests/day,
     up to 15 RPM), kicks in automatically if Anthropic errors. Uses the
     real `GEMINI_API_KEY` already in the project's `.env` — no new
     signup.
  3. **Cloudflare Workers AI** (`@cf/meta/llama-3.1-8b-instruct`) — free,
     edge-native, last resort if both of the above fail.
  Not reachable from local Ollama/OmniRoute at any tier — those run on
  Randy's own PC, not Cloudflare's edge (reasoning captured 2026-08-12
  for why that setup doesn't transfer to this deployment). Every
  non-primary tier shows an on-screen backup banner naming which tier
  answered, so a degraded answer is never presented as primary-quality.
- **Rate limiting:** Workers KV, per-IP, resets daily. **DECIDED
  2026-08-12: `RATE_LIMIT_PER_DAY = 5`.**
- **Admin testing bypass:** a separate `X-Admin-Key` header, checked
  before the rate limit applies and never present in the public page's
  client-side JS (a UI field for this would expose it to anyone viewing
  page source). Set the real value via `wrangler secret put
  ADMIN_BYPASS_KEY`, then test with curl, not the browser form:
  ```
  curl -X POST https://texas-landlord-advisor.<your-subdomain>.workers.dev/ask \
    -H "Content-Type: application/json" \
    -H "X-Admin-Key: <the real value you set>" \
    -d '{"question":"Can I keep a deposit if the tenant owed rent?"}'
  ```
  Real deployed URL isn't known until after the first `wrangler deploy`
  — Wrangler prints it on deploy.

## Cost estimate — Anthropic primary tier

Sonnet 4.6: $3/M input tokens, $15/M output tokens. This prompt runs
~250–450 input tokens (template + question), ~400–700 output tokens
typically (up to the 1,024 max). **Roughly $0.01–$0.02 per question.**
At the placeholder 5-questions/day/IP rate limit, heavy sustained use
could run a few dollars a day; realistic light-to-moderate traffic
(most visitors asking 1 question) is closer to a few dollars a month.
Set a hard budget alert on the Anthropic console regardless of traffic
assumptions — real usage is unpredictable on a public surface.

## Real decisions still needed before this goes live

1. ~~Confirm `RATE_LIMIT_PER_DAY`~~ — **DECIDED 2026-08-12: 5/day/IP.**
2. ~~Confirm primary model~~ — **DECIDED 2026-08-12: Sonnet 4.6**, for
   citation-quality reasons over Haiku's lower cost.
3. ~~The "evidence of market" usage threshold~~ — **DECIDED 2026-08-12:
   50 distinct questions within any single 7-day window** (usage, not
   just clicks — stronger intent signal than the Steel funnel's click
   data, which this doesn't reuse since it's a different funnel).
4. ~~Go-ahead to actually deploy~~ — **GIVEN 2026-08-12.** Deploy
   attempted same day, **blocked on a real Cloudflare auth error, not
   yet resolved** — see Deployment status below. Randy's call: bank this
   for now, resume later.

## Deployment status — LIVE, deployed 2026-08-13

**Live URL:** https://texas-landlord-advisor.region5dl.workers.dev

The real blocker was found and fixed 2026-08-13: it wasn't a token-scope
problem after all — `.env`'s `CF_API_TOKEN` value had been accidentally
overwritten with the literal text `npx wrangler login` (not a real
token), which is why every earlier attempt failed with an auth error.
Fixed by clearing that line and running a real `wrangler login` OAuth
flow instead, confirmed via `wrangler whoami` (correct scopes: `workers`,
`workers_kv`, `workers_scripts`, `ai`, all `write`).

KV namespace: created as `TEXAS_LANDLORD_RATE_LIMIT` (title collision
with the Riddle of Steel tool's own `RATE_LIMIT`-titled namespace, since
both tools use the same binding name — the binding stays `RATE_LIMIT` in
`wrangler.toml`, only the underlying namespace title differs). Secrets
(`ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `ADMIN_BYPASS_KEY`) uploaded live.
End-to-end tested via the admin-bypass curl command below — real Anthropic
response confirmed working.

`admin_bypass_key.secret` (this folder) holds the real generated admin
key for the curl-testing command in this README — gitignored via `*.secret`.

## Deployment steps (already run — kept for reference / redeploys)

```
cd products/texas-landlord-guide/web-tool
npx wrangler kv namespace create RATE_LIMIT
# paste the returned id into wrangler.toml's [[kv_namespaces]] id field
npx wrangler secret put ANTHROPIC_API_KEY
npx wrangler secret put GEMINI_API_KEY
npx wrangler secret put ADMIN_BYPASS_KEY
# pick any real random string for ADMIN_BYPASS_KEY yourself — it isn't
# in .env, it's specific to this tool
npx wrangler deploy
```

Both keys already exist as real values in the project's own `.env` —
reuse those when the CLI prompts for the secret value, don't generate
new ones.

Uses the existing Cloudflare account (`region5dl@gmail.com`, see
`memory/reference_cloudflare_accounts.md`) — no new account needed.

## Status

Live and verified 2026-08-13. Usage-threshold decision (50 distinct
questions within any 7-day window) still governs whether this graduates
toward a paid tier — not yet tracked/automated, check manually via
`wrangler tail` or KV key counts until real traffic exists.
