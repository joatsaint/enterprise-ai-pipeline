# Facebook Reel Transcriber

Given a Facebook profile/page URL: finds its Reel links, downloads each one
through a residential proxy rotator, transcribes with local Whisper, and
appends every transcript to one `transcripts.txt`.

## Setup

```
cp .env.example .env
# fill in PROXY_URL with your rotator's gateway (user:pass@host:port)
```

`yt-dlp`, `faster-whisper`, and `python-dotenv` are already installed in
this project's environment.

## Run

```
python facebook_reel_transcriber.py https://www.facebook.com/SOME_PAGE/reels/
```

Downloaded videos land in `downloads/` (gitignored). All transcripts
append to `transcripts.txt` (gitignored), one `=== url ===` block per reel.

## Real caveat

yt-dlp's Facebook extractor is solid for single reel URLs but less
consistent at enumerating an entire profile's Reels tab — Facebook changes
its page markup often. If discovery returns zero reels:
1. `pip install -U yt-dlp` first (Facebook support gets patched frequently).
2. If it's still empty, the extractor genuinely can't parse that page —
   the fallback is a headless-browser scroll-and-collect script, not
   built here yet.
