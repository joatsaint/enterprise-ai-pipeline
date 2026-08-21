"""
One-time OAuth setup for YouTube Analytics API access (read-only).

Opens a browser consent screen -- Randy logs in as the account that owns
the channel being analyzed and approves read-only Analytics access. Saves
a refresh token to .youtube_oauth_token.json (gitignored) so future runs
don't need to re-authorize.

This is an interactive, real-login step -- run it yourself, not something
Claude Code runs on your behalf:

    python -m src.youtube_oauth_setup

Requires YOUTUBE_OAUTH_CLIENT_ID and YOUTUBE_OAUTH_CLIENT_SECRET in .env
(from Google Cloud Console -> APIs & Services -> Credentials -> OAuth
client ID -> Desktop app).
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

load_dotenv()

TOKEN_PATH = Path(__file__).resolve().parents[1] / ".youtube_oauth_token.json"

# Read-only scope -- this can never write to or change anything on the
# channel, only read analytics data.
SCOPES = ["https://www.googleapis.com/auth/yt-analytics.readonly"]


def main():
    client_id = os.getenv("YOUTUBE_OAUTH_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_OAUTH_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("YOUTUBE_OAUTH_CLIENT_ID / YOUTUBE_OAUTH_CLIENT_SECRET not set in .env.")
        return

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    print("Opening browser for Google login -- approve read-only YouTube")
    print("Analytics access for the account that owns the channel you want")
    print("to analyze (e.g. Meditate with Me).")
    creds = flow.run_local_server(port=0)

    TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    print(f"\nSaved. Token written to {TOKEN_PATH} (gitignored, stays local).")
    print("Future analytics pulls will use this automatically -- no need to re-run this.")


if __name__ == "__main__":
    main()
