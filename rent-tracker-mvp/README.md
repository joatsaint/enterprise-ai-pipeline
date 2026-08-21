# Free Rent Tracker for Small Landlords

A free, no-signup tool that uses Google's Gemini AI to build and maintain a
rent-payment log — scans your Gmail for Zelle/Cash App/Venmo/bank payment
notifications and logs them into a Google Sheet you fully own. No app to
install, no account to create beyond Google's own, no monthly fee, ever.

Built for small landlords managing a handful of single-family homes or a
condo — the exact setup most "professional" property-management software
is overkill for.

## Quick Start

1. Read `STEP_BY_STEP_GUIDE.md` — five short setup steps, written for
   someone who's never used AI before.
2. Copy the prompt in `SETUP_PROMPT.md` into [gemini.google.com](https://gemini.google.com).
3. Answer its questions about your properties. Done.

## What this is NOT

- Not a hosted service — nothing runs on Randy's servers, because there are
  none. It's a set of instructions that runs inside *your* Google account.
- Not a full property-management suite (no tenant portal, no automated
  late-fee reminders, no P&L tax reports) — those exist elsewhere
  (Landlord Cart, Stessa, Landlord Studio) if you want them. This solves
  one specific, tedious problem: manually re-typing rent payments.
- Not legal, tax, or financial advice.

## Status

MVP / Validate stage (2026-08-02) — built and about to be tested against a
real 5-property, 7-income-stream setup before anything gets shared publicly.

---

**🔴 Open decision, not yet resolved:** how does this actually reach the
Facebook landlord groups? A GitHub repo (the pattern used for Pain Point
Miner) assumes comfort with GitHub that this specific audience — "AI-curious
but not AI-fluent" novice landlords — likely doesn't have. A single shareable
Google Doc (matching how you already distribute other free assets to these
groups) is probably the better fit, but that's your call, not decided here.
