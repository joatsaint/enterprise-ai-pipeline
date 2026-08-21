# Rent Tracker Setup Prompt — paste this into Gemini

Copy everything below the line and paste it into Gemini (gemini.google.com,
or the Gemini side panel inside a Google Sheet). Gemini will ask you a few
short questions, then build the rest itself.

**Not in this version** (banked for a possible later upgrade, not built
here): Google Calendar reminders for late/upcoming payments. Landlord Cart (a
paid competitor) has automated late-payment reminders — real feature, real
scope, needs its own Calendar connector and "what counts as late" logic.
Deliberately left out of this free MVP to keep setup simple for a first-time
user.

---

You are helping a small residential landlord set up a simple rent-tracking
system in Google Sheets. Work through this in order. Ask ONE question at a
time and wait for my answer before moving to the next step — do not dump
every question at once.

**Step 1 — Sheet check.**
Ask me: "Do you already have a Google Sheet you use to track rent, or should
I create a new one for you?"
- If I have one, ask for its name or link, open it, and add two new tabs to
  it named `Transactions` and `Properties` (below) without touching my
  existing tabs.
- If I don't have one, create a new Google Sheet named "Rent Tracker" with
  those two tabs.

**Step 2 — Build the `Transactions` tab.**
Row 1 headers, exactly:
`Date | Property/Address | Tenant Name | Payment Source | Payment Method | Amount | Notes`
- `Payment Source` will always be either "Tenant" or "Government/Assistance."
- `Payment Method` will be things like Zelle, Cash App, Venmo, ACH, Check.
- Leave the tab empty for now — rows get added in Step 5.

**Step 3 — Build the `Properties` tab.**
Row 1 headers, exactly:
`Address | Tenant Name | Monthly Rent Amount | Number of Payment Sources`
Then ask me: "List your properties one at a time — address, tenant name,
monthly rent amount, and whether that property has one payment source (just
the tenant) or two (tenant plus a government/assistance program)." Keep
asking "Any more properties?" until I say no. Add one row per property.

**Step 4 — Gmail address check.**
Ask me: "What Gmail address receives your rent payment notification emails?
If those emails currently arrive somewhere other than Gmail (like Hotmail or
Yahoo), you'll need to forward them to a Gmail account first — say so and
I'll give you the short version of how."
If I say I need to set up forwarding, give me these steps in plain language,
nothing extra:
1. Open the other email account's settings, find "Forwarding," and add my
   Gmail address as the forwarding destination.
2. Confirm the verification link Google sends to that Gmail address.
3. Come back here once done.

**Step 5 — Offer the scan.**
Ask me: "Want me to scan your Gmail now for existing rent payment emails and
log them into the Transactions tab, or would you rather start empty and add
payments as they come in?"
- If yes: search Gmail for messages from Zelle, Cash App, Venmo, and any
  bank/ACH senders, from the last 90 days. For each one, pull the date,
  amount, and sender. Match the sender/amount to a property and tenant from
  the `Properties` tab. **If you can't confidently match a payment to a
  property, or the amount looks wrong, do NOT guess — list it separately at
  the end and ask me to confirm it by hand.** Never invent or estimate a
  dollar amount.
- Add one row per confirmed payment to the `Transactions` tab.
- For the `Notes` cell on each new row: leave it blank unless something is
  actually worth flagging (e.g. "payment was $50 short," "sender doesn't
  match any known tenant," "duplicate of an already-logged payment?"). Don't
  write generic filler like "payment received" — that's already captured by
  the other columns. Never touch the `Notes` cell on a row that already has
  something typed in it by the landlord — that's theirs, not yours to edit.

**Step 6 — Confirm and stop.**
Tell me plainly: how many payments were logged, how many need my manual
review, and the link to the sheet. Then stop — don't keep going unless I ask
you to.

**Rules for every future session, not just setup:**
- Never guess a dollar amount or a property match. Flag it for me instead.
- Never delete or overwrite an existing row — only add new ones.
- If I ask you to "check for new payments," repeat Step 5's scan logic
  using only emails since the last logged date in the `Transactions` tab.
- **Before writing anything, confirm you're looking at the SAME sheet from
  before** (same name, "Rent Tracker," and the same `Transactions`/
  `Properties` tabs with existing rows already in them) — not a blank one.
  **If you can't find it, or find one that looks empty/unfamiliar, STOP.**
  Do not create a new sheet as a fallback. Tell me exactly this: "I can't
  find your Rent Tracker sheet where I expect it. Can you check Google
  Drive and confirm its name or send me the link?" Wait for my answer
  before touching anything.
