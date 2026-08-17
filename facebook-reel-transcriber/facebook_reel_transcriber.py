"""Facebook Reels -> local download -> Whisper transcript, one output file.

Usage:
    python facebook_reel_transcriber.py "https://www.facebook.com/PAGE/reels/" --cookies facebook_cookies.txt

Flow: Playwright (discover_reels.py) loads the Reels tab logged-in via
your exported cookies and scrolls to collect every /reel/<id> link --
yt-dlp has no extractor for a profile's Reels tab (confirmed against its
source, 2026-08-16), only for individual reel URLs. yt-dlp then downloads
each discovered reel through the residential proxy rotator (same cookies,
for reels that need auth to view), and faster-whisper transcribes locally.
All transcripts append to one .txt.

Cookies: export via a browser extension ("Get cookies.txt LOCALLY" or
similar) while logged into Facebook. Real gotcha found live: Python's
stdlib cookiejar is strict about a domain with a leading dot needing
"TRUE" in the include-subdomains column -- many export extensions write
FALSE regardless. If you re-export and hit "invalid Netscape format
cookies file", run this one-liner to fix it:
    awk -F'\t' 'BEGIN{OFS="\t"} /^#/{print;next} {if($1~/^[.]/)$2="TRUE";print}' cookies.txt > fixed.txt
"""
from __future__ import annotations

import argparse
import os
import random
import sys
import time
from pathlib import Path

import yt_dlp
from dotenv import load_dotenv
from faster_whisper import WhisperModel

from discover_reels import discover_reel_urls

load_dotenv(Path(__file__).parent / ".env")


def _resolve_proxy_url() -> str | None:
    """Prefer an explicit PROXY_URL; otherwise build one from Webshare's
    separate username/password vars against their standard rotating
    gateway (p.webshare.io:80 -- Webshare's documented default endpoint)."""
    explicit = os.getenv("PROXY_URL")
    if explicit and "gateway.example.com" not in explicit:
        return explicit
    user = os.getenv("WEBSHARE_PROXY_USERNAME")
    pw = os.getenv("WEBSHARE_PROXY_PASSWORD")
    host = os.getenv("WEBSHARE_PROXY_HOST", "p.webshare.io:80")
    if user and pw:
        return f"http://{user}:{pw}@{host}"
    return None


PROXY_URL = _resolve_proxy_url()
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")


def _page_slug(page_url: str) -> str:
    """Derives a filesystem-safe slug from a Facebook page URL, e.g.
    'https://www.facebook.com/alisa.cohn/reels/' -> 'alisa.cohn'. Used to
    namespace output per page so two concurrent runs (different pages)
    never share a downloads folder or transcript file."""
    parts = [p for p in page_url.split("/") if p and p not in ("reels", "reels_tab")]
    for p in reversed(parts):
        if "facebook.com" not in p and "profile.php" not in p and "?" not in p:
            return p
    # profile.php?id=... case -- fall back to the numeric id
    if "id=" in page_url:
        return "profile_" + page_url.split("id=")[1].split("&")[0]
    return "reels"


def download_reel(url: str, cookies_path: Path, out_dir: Path) -> Path | None:
    out_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "outtmpl": str(out_dir / "%(id)s.%(ext)s"),
        "quiet": True,
        "noprogress": True,
        "cookiefile": str(cookies_path),
    }
    if PROXY_URL:
        ydl_opts["proxy"] = PROXY_URL
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return Path(ydl.prepare_filename(info))
    except Exception as e:
        print(f"[download failed] {url}: {e}")
        return None


def transcribe(model: WhisperModel, video_path: Path) -> str:
    segments, _ = model.transcribe(str(video_path))
    return " ".join(seg.text.strip() for seg in segments)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("page_url", help="Facebook profile/page reels-tab URL")
    parser.add_argument("--cookies", required=True, help="Path to a Netscape-format cookies.txt")
    parser.add_argument("--min-delay", type=float, default=4.0)
    parser.add_argument("--max-delay", type=float, default=9.0)
    parser.add_argument("--limit", type=int, default=None, help="Only process the first N reels (testing)")
    args = parser.parse_args()

    cookies_path = Path(args.cookies)

    # Per-page namespacing (added 2026-08-16): each page gets its own
    # downloads subfolder + transcript file, derived from the URL, so
    # multiple runs against different pages can run concurrently without
    # sharing (and racing on) the same output files.
    slug = _page_slug(args.page_url)
    out_dir = Path(__file__).parent / "downloads" / slug
    transcript_path = Path(__file__).parent / f"transcripts_{slug}.txt"

    print(f"Discovering reel URLs from {args.page_url} ...")
    urls = discover_reel_urls(args.page_url, cookies_path)
    if not urls:
        print("No reel URLs found.")
        sys.exit(1)
    if args.limit:
        urls = urls[: args.limit]
    print(f"Found {len(urls)} reels.")

    # Resume-safety: skip any URL that already has a transcript block --
    # a large, multi-hour run needs to be restartable without redoing
    # finished work (same idempotency principle as this repo's own
    # download_log.json convention).
    done_urls: set[str] = set()
    if transcript_path.exists():
        for line in transcript_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("=== ") and line.endswith(" ==="):
                done_urls.add(line[4:-4])
    urls = [u for u in urls if u not in done_urls]
    if done_urls:
        print(f"Skipping {len(done_urls)} already-transcribed reels.")

    # device="cpu" forced -- GPU (CUDA) mode failed here with a missing
    # cublas64_12.dll, a common faster-whisper/CTranslate2 gotcha when the
    # NVIDIA CUDA/cuBLAS runtime isn't installed. CPU is slower but works
    # everywhere without a GPU dependency to manage.
    model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")

    with open(transcript_path, "a", encoding="utf-8") as out:
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] {url}")
            video_path = download_reel(url, cookies_path, out_dir)
            if video_path is None or not video_path.exists():
                continue

            try:
                text = transcribe(model, video_path)
                out.write(f"=== {url} ===\n{text}\n\n")
                out.flush()
            except Exception as e:
                print(f"[transcribe failed] {url}: {e}")

            if i < len(urls):
                time.sleep(random.uniform(args.min_delay, args.max_delay))

    print(f"Done. Transcripts written to {transcript_path}")


if __name__ == "__main__":
    main()
