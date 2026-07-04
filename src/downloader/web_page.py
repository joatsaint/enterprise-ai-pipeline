"""
src/downloader/web_page.py

Scans a folder of transcript .md files for ## LINK: lines matching a target
domain, then uses Playwright to click the "Markdown" download button on each
page and saves the resulting file named after the source article.

Naming convention:
  Source article:   2026-03-26_your-ai-credentials-dont-matter-your.md
  Promptkit output: 2026-03-26_your-ai-credentials-dont-matter-your_promptkit.md
  Guide output:     2026-03-26_your-ai-credentials-dont-matter-your_guide.md

Log file: logs/web_download_log.json  (separate from video download_log.json)

CLI (via src/main.py):
  python -m src.main fetch-links \\
      --scan-dir transcripts/ai-job-intelligence/nate-b-jones \\
      --domain promptkit.natebjones.com \\
      --output-dir transcripts/ai-job-intelligence/nate-b-jones-guides
"""

import json
import os
import random
import re
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_PROJECT_ROOT  = Path(__file__).parent.parent.parent
LOG_PATH       = _PROJECT_ROOT / "logs" / "web_download_log.json"
ERROR_LOG_PATH = _PROJECT_ROOT / "logs" / "error_log.json"

# ---------------------------------------------------------------------------
# Link extraction
# ---------------------------------------------------------------------------

_URL_RE = re.compile(r'\[.*?\]\((https?://[^\s)]+)\)')


def scan_articles_for_links(scan_dir: str, domain: str) -> list:
    """
    Walk all .md files in scan_dir. For every ## LINK: or ### LINK: line
    containing a URL on target domain, collect:
      (article_stem, url, suffix)

    suffix:
      '_promptkit'  for URLs containing 'promptkit'  (but not '_guide_')
      '_guide'      for URLs containing '_guide_'
      '_link'       fallback

    Returns list of tuples sorted by article_stem.
    """
    results = []
    seen_urls = set()
    scan_path = _resolve(scan_dir)

    if not scan_path.exists():
        print(f"[ERROR] Scan directory not found: {scan_path}")
        return results

    for md_file in sorted(scan_path.glob("*.md")):
        article_stem = md_file.stem
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"[WARN] Could not read {md_file.name}: {e}")
            continue

        for line in text.splitlines():
            stripped = line.strip()
            if not (stripped.startswith("## LINK:") or stripped.startswith("### LINK:")):
                continue
            for url in _URL_RE.findall(stripped):
                if domain not in url:
                    continue
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                suffix = _url_suffix(url)
                results.append((article_stem, url, suffix))

    print(f"[INFO] Found {len(results)} link(s) on '{domain}' across {scan_path.name}/")
    return results


def _url_suffix(url: str) -> str:
    lower = url.lower()
    if "_guide_" in lower or lower.endswith("_guide"):
        return "_guide"
    if "promptkit" in lower:
        return "_promptkit"
    return "_link"


def _resolve(path_str: str) -> Path:
    """Resolve path relative to project root if not absolute."""
    p = Path(path_str)
    if p.is_absolute():
        return p
    return _PROJECT_ROOT / p


# ---------------------------------------------------------------------------
# Log helpers
# ---------------------------------------------------------------------------

def _load_log() -> dict:
    if LOG_PATH.exists():
        try:
            with open(LOG_PATH, encoding="utf-8") as f:
                data = json.load(f)
                if "pages" not in data:
                    data["pages"] = []
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return {"pages": []}


def _save_log(log: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def _already_downloaded(url: str, log: dict) -> bool:
    return any(
        p.get("url") == url and p.get("status") == "success"
        for p in log["pages"]
    )


def _log_error(url: str, output_file: str, error: Exception) -> None:
    errors = []
    if ERROR_LOG_PATH.exists():
        try:
            with open(ERROR_LOG_PATH, encoding="utf-8") as f:
                errors = json.load(f)
        except (json.JSONDecodeError, OSError):
            errors = []
    errors.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "web_page",
        "url": url,
        "output_file": output_file,
        "error": str(error),
    })
    with open(ERROR_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Metadata injection
# ---------------------------------------------------------------------------

def _inject_metadata(path: Path, url: str, article_stem: str, channel_name: str) -> None:
    """
    Prepend **Channel:**, **Published:**, and **URL:** fields into a
    downloaded file so the indexer recognises it.

    Inserts after the closing --- of YAML frontmatter if present,
    otherwise at the top of the file. No-ops if **Channel:** already exists.
    """
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return

    if "**Channel:**" in content:
        return

    date_str = article_stem[:10] if len(article_stem) >= 10 else ""
    header = (
        f"**Channel:** {channel_name}\n"
        f"**Published:** {date_str}\n"
        f"**URL:** {url}\n\n"
    )

    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            insert_at = end + 4
            if insert_at < len(content) and content[insert_at] == "\n":
                insert_at += 1
            content = content[:insert_at] + "\n" + header + content[insert_at:]
        else:
            content = header + content
    else:
        content = header + content

    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Playwright download
# ---------------------------------------------------------------------------

def _download_one(page, url: str, output_path: Path,
                  article_stem: str, channel_name: str) -> None:
    """
    Navigate to url, click the 'Markdown' link, intercept the file download,
    save to output_path, then inject indexer-required metadata fields.
    """
    page.goto(url, wait_until="networkidle", timeout=30_000)

    btn = page.get_by_role("link", name="Markdown")
    btn.wait_for(state="visible", timeout=10_000)

    with page.expect_download(timeout=30_000) as dl_info:
        btn.click()

    download = dl_info.value
    if download.failure():
        raise RuntimeError(f"Download reported failure: {download.failure()}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    download.save_as(str(output_path))
    _inject_metadata(output_path, url, article_stem, channel_name)


# ---------------------------------------------------------------------------
# Batch entry point
# ---------------------------------------------------------------------------

def run_fetch_links(scan_dir: str, domain: str, output_dir: str,
                    channel_name: str = "") -> None:
    """
    Full pipeline:
      1. Inject missing metadata into any already-downloaded files in output_dir
      2. Scan scan_dir .md files for ## LINK: URLs on domain
      3. Skip already-downloaded URLs (web_download_log.json)
      4. Download each via Playwright Markdown button click
      5. Save to output_dir with article-derived filename + inject metadata
      6. Log results and print run summary
    """
    from playwright.sync_api import sync_playwright

    output_path = _resolve(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Derive channel name from output directory if not supplied
    if not channel_name:
        channel_name = output_path.name.replace("-", " ").title()

    # 0. Migration pass — inject metadata into existing files that lack it
    migrated = 0
    log = _load_log()
    url_by_stem: dict[str, str] = {
        Path(p["output_file"]).stem: p["url"]
        for p in log["pages"]
        if p.get("status") == "success" and p.get("url")
    }
    for existing in output_path.glob("*.md"):
        url = url_by_stem.get(existing.stem, "")
        article_stem = existing.stem
        # strip suffix (_promptkit, _guide, _link) to get clean date prefix
        for suffix in ("_promptkit", "_guide", "_link"):
            if article_stem.endswith(suffix):
                article_stem = article_stem[: -len(suffix)]
                break
        if "**Channel:**" not in existing.read_text(encoding="utf-8", errors="replace"):
            _inject_metadata(existing, url, article_stem, channel_name)
            migrated += 1

    if migrated:
        print(f"[INFO] Injected metadata into {migrated} existing file(s).")

    # 1. Scan
    links = scan_articles_for_links(scan_dir, domain)
    if not links:
        print("[INFO] No matching links found. Nothing to download.")
        _print_summary(0, 0, 0)
        return

    # 2. Deduplicate against log + existing files
    to_download = []
    skipped = 0

    for article_stem, url, suffix in links:
        out_file = output_path / f"{article_stem}{suffix}.md"

        if _already_downloaded(url, log):
            skipped += 1
            continue

        if out_file.exists():
            log["pages"].append({
                "url": url,
                "output_file": str(out_file),
                "status": "success",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "note": "found_on_disk",
            })
            skipped += 1
            continue

        to_download.append((article_stem, url, suffix, out_file))

    _save_log(log)
    print(f"[INFO] {len(to_download)} to download, {skipped} already done.")

    if not to_download:
        _print_summary(0, skipped, 0)
        return

    # 3. Download
    downloaded = 0
    failed = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        for i, (article_stem, url, suffix, out_file) in enumerate(to_download):
            print(f"[{i+1}/{len(to_download)}] {out_file.name}")
            print(f"  URL: {url}")
            try:
                _download_one(page, url, out_file, article_stem, channel_name)
                log["pages"].append({
                    "url": url,
                    "output_file": str(out_file),
                    "status": "success",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                _save_log(log)
                print("  ✓ Saved")
                downloaded += 1
            except Exception as exc:
                print(f"  ✗ Failed: {exc}")
                _log_error(url, str(out_file), exc)
                log["pages"].append({
                    "url": url,
                    "output_file": str(out_file),
                    "status": "failed",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error": str(exc),
                })
                _save_log(log)
                failed += 1

            if i < len(to_download) - 1:
                time.sleep(random.uniform(2, 5))

        context.close()
        browser.close()

    _print_summary(downloaded, skipped, failed)


def _print_summary(downloaded: int, skipped: int, failed: int) -> None:
    print()
    print("━" * 40)
    print(" fetch-links complete")
    print("━" * 40)
    print(f" ✓ Downloaded:  {downloaded}")
    print(f" ↷ Skipped:     {skipped} (already done)")
    print(f" ✗ Failed:      {failed}")
    print("━" * 40)
