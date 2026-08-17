"""Playwright-based Reels discovery for a Facebook profile/page.

yt-dlp has no extractor for a profile's Reels tab (confirmed against its
source, 2026-08-16) -- it only recognizes individual /reel/<id> URLs. This
module loads the tab in a real headless browser, scrolls to trigger lazy
loading, and collects the individual reel links -- which yt-dlp then
downloads fine, one at a time.

Auth: reuses the same Netscape-format cookies.txt this project's main
script already uses (facebook_cookies.txt), converted into Playwright's
cookie format so the page loads already logged in -- no separate login
flow needed here.
"""
from __future__ import annotations

import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

REEL_URL_RE = re.compile(r"/reel/(\d+)")


def _load_netscape_cookies(cookies_path: Path) -> list[dict]:
    cookies = []
    for line in cookies_path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 7:
            continue
        domain, _include_sub, path, secure, expiry, name, value = parts
        cookies.append(
            {
                "name": name,
                "value": value,
                "domain": domain,
                "path": path,
                "expires": float(expiry) if expiry not in ("", "0") else -1,
                "secure": secure.upper() == "TRUE",
            }
        )
    return cookies


def discover_reel_urls(
    page_url: str,
    cookies_path: Path,
    max_scrolls: int = 30,
    scroll_pause: float = 2.0,
) -> list[str]:
    """Returns deduplicated, full https://www.facebook.com/reel/<id> URLs."""
    found: set[str] = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(_load_netscape_cookies(cookies_path))
        page = context.new_page()
        page.goto(page_url, wait_until="domcontentloaded", timeout=30000)

        stagnant_rounds = 0
        prev_count = 0
        for _ in range(max_scrolls):
            hrefs = page.eval_on_selector_all("a[href*='/reel/']", "els => els.map(e => e.href)")
            for href in hrefs:
                m = REEL_URL_RE.search(href)
                if m:
                    found.add(f"https://www.facebook.com/reel/{m.group(1)}")

            if len(found) == prev_count:
                stagnant_rounds += 1
                if stagnant_rounds >= 3:
                    break
            else:
                stagnant_rounds = 0
            prev_count = len(found)

            page.mouse.wheel(0, 3000)
            time.sleep(scroll_pause)

        browser.close()

    return sorted(found)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("page_url")
    parser.add_argument("--cookies", default="facebook_cookies.txt")
    args = parser.parse_args()

    urls = discover_reel_urls(args.page_url, Path(args.cookies))
    print(f"Found {len(urls)} reels:")
    for u in urls:
        print(u)
