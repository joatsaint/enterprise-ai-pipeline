---
name: ghost-token-audit
description: Find your ghost tokens — audit what your Claude Code setup silently loads on every message (CLAUDE.md, imports, rules, MCP servers, skills menu) and get a ranked trim list. Run it when context feels tight, responses feel slow, or you have never once looked.
---

# Ghost-Token Audit (Starter)

**What this does:** measures the standing overhead your Claude Code setup pays on EVERY message —
before you type a single word — and hands you a ranked list of what to trim. "Ghost tokens" are
the ones you pay for without knowing: the plugin you disabled but whose menu still loads, the
rules file that restates another rules file, the 2,000-word status doc that fires every turn.

**What it does NOT do:** delete anything. It measures and recommends; you decide. (That's not a
disclaimer — it's the method. Measure first. Anthropic deleted 80% of Claude Code's own system
prompt only after evals proved no measurable loss.)

## Run it

Open Claude Code in the project you care about and say:

> Run the ghost-token audit from this skill.

Claude will:

1. **Inventory the always-loaded layer.** Read `CLAUDE.md` (project + `~/.claude/CLAUDE.md`),
   every `@import` they pull in, and everything in `.claude/rules/` (or equivalent). For each
   file: word count × 1.33 ≈ tokens. These fire on EVERY message — this is the layer that leaks.
2. **Inventory the on-demand layer.** List `.claude/skills/` (and global skills). Note: skills
   cost ~0 until invoked — they are the model to copy, not the problem. If your rules/context
   files hold workflow instructions a skill could hold instead, that's a move, not a delete.
3. **Check the menus.** List enabled plugins and MCP servers in your settings. A disabled-but-
   listed plugin or an unused MCP server still pays its menu/schema listing every message.
   Flag any with zero recent use.
4. **Report the table.** Per file/source: tokens, load frequency (every message vs on-demand),
   and tokens/message cost. Then the headline: total standing overhead, and what % of a 200K
   window is gone before you type.
5. **Rank the top 5 trims** by tokens saved × confidence it's safe, each tagged with its move:
   - **Archive** — never-used skills/plugins/servers (move, don't delete)
   - **Stub** — long situational detail → short pointer + on-demand file
   - **One home** — the same fact stated in 2+ always-loaded places (pick one, point the rest)
   - **Demote** — always-loaded content only needed in one workflow → into a skill

## Read the results with these three rules

- **Load frequency × size is the metric — not size.** A small file loaded every message costs
  more than a huge file loaded once.
- **Six copies means five are free to rot.** Duplicated facts aren't safety; they're future
  contradictions. One home per fact, pointers everywhere else.
- **A warning addressed to a human is not enforcement.** If a rule matters, wire it into a tool,
  a hook, or a file the system actually reads — don't just write "remember to…" in a doc.

## Prerequisites

- Claude Code (any plan). Nothing else — no API keys, no installs. The audit is Claude reading
  your own files and settings and doing arithmetic.

## After the audit

Re-run it after you trim. The number should drop and nothing should break — if a removal breaks
something, it wasn't a ghost token, and you put it back. Measure → trim → verify. That's the
whole discipline.
