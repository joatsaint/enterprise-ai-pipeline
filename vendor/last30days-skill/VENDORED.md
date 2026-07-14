# Vendored: last30days-skill

**Source:** https://github.com/mvanhorn/last30days-skill (MIT License, © 2026 Matt Van Horn)
**Vendored:** 2026-07-14, from the locally installed copy at `~/.agents/skills/last30days`
**Why:** to track local modifications (Webshare proxy support in `scripts/lib/http.py`)
through this project's own git history instead of editing the global,
non-version-controlled install directly.

## Local modifications

- `scripts/lib/http.py` — added optional Webshare rotating-proxy support to
  `request()`, reusing this project's existing `WEBSHARE_PROXY_USERNAME` /
  `WEBSHARE_PROXY_PASSWORD` `.env` credentials (same pattern already used in
  `src/downloader/transcript_fetcher.py`). Falls back to a direct connection
  when the credentials aren't set — never a hard dependency.

Re-sync from upstream periodically (`npx skills add mvanhorn/last30days-skill
-g` refreshes the global copy; diff against this vendored copy before
re-applying local changes) rather than treating this fork as permanently
diverged.
