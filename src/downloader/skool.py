"""
Skool community downloader.

Architecture:
  1. Playwright (headless=False, to pass AWS WAF) navigates to each course page.
  2. After client-side hydration, window.__NEXT_DATA__ contains the full lesson
     tree including videoLink (Loom/Vimeo/YouTube) and videoStream (Skool/Mux HLS).
  3. yt-dlp downloads each video URL — no browser cookies needed for download
     because Loom/Vimeo links are open and Skool native URLs include a token.
  4. faster-whisper transcribes the downloaded video to text.
  5. Transcript saved as .md in transcripts/{group}/{community}/ — picked up
     automatically by the existing indexer and Q&A pipeline.

Usage (via main.py):
  python -m src.main skool-download --community cloudtechexec \\
      --group "cloud-tech-free-training" --limit 2
"""
import asyncio
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

LOGS_DIR = Path("logs")
ERROR_LOG = LOGS_DIR / "error_log.json"
SESSION_FILE = LOGS_DIR / "skool_session.json"

# Windows console defaults to cp1252 which can't encode emojis in lesson titles
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")[:60]


def _log_error(module: str, message: str):
    LOGS_DIR.mkdir(exist_ok=True)
    log = {"errors": []}
    if ERROR_LOG.is_file():
        try:
            with open(ERROR_LOG, "r", encoding="utf-8") as f:
                log = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    log.setdefault("errors", []).append({
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "module": f"skool/{module}",
        "error": message,
    })
    with open(ERROR_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def _extract_lessons(node: dict) -> list[dict]:
    """Recursively walk the course tree and collect module-type lessons."""
    lessons = []
    for child in node.get("children", []):
        c = child.get("course", {})
        meta = c.get("metadata", {})
        if c.get("unitType") == "module":
            video_link = meta.get("videoLink") or None
            video_stream = meta.get("videoStream") or None
            if video_link or video_stream:
                lessons.append({
                    "id": c.get("id"),
                    "title": meta.get("title", "Untitled"),
                    "video_link": video_link,
                    "video_stream": video_stream,
                    "duration_ms": meta.get("videoLenMs"),
                })
        if child.get("children"):
            lessons.extend(_extract_lessons(child))
    return lessons


class SkoolDownloader:
    BASE_URL = "https://www.skool.com"

    def __init__(self, community_slug: str, group: str, limit: int | None = None):
        self.community_slug = community_slug
        self.group_dir = _slugify(group)
        self.limit = limit
        self.email = os.getenv("SKOOL_EMAIL")
        self.password = os.getenv("SKOOL_PASSWORD")
        self.output_dir = Path(f"transcripts/{self.group_dir}/{community_slug}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        asyncio.run(self._run_async())

    async def _run_async(self):
        if not self.email or not self.password:
            print("ERROR: Set SKOOL_EMAIL and SKOOL_PASSWORD in .env before running.")
            sys.exit(1)

        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            # headless=False is required — AWS WAF blocks headless Chromium
            need_login = not SESSION_FILE.is_file()
            browser = await p.chromium.launch(headless=False)
            ctx_opts = {"storage_state": str(SESSION_FILE)} if SESSION_FILE.is_file() else {}
            context = await browser.new_context(**ctx_opts)
            page = await context.new_page()

            # Verify or perform login
            if need_login:
                await self._login(page, context)
            else:
                print("Reusing saved session — verifying...")
                await page.goto(f"{self.BASE_URL}/{self.community_slug}/classroom")
                await page.wait_for_load_state("domcontentloaded", timeout=15000)
                if "login" in page.url.lower():
                    print("Session expired — logging in again.")
                    SESSION_FILE.unlink(missing_ok=True)
                    await self._login(page, context)

            # Collect all courses with access
            courses = await self._get_accessible_courses(page)
            print(f"Found {len(courses)} accessible courses.")

            all_lessons: list[dict] = []
            for course in courses:
                lessons = await self._get_course_lessons(page, course)
                all_lessons.extend(lessons)
                if self.limit and len(all_lessons) >= self.limit:
                    break

            await browser.close()

        targets = all_lessons[: self.limit] if self.limit else all_lessons
        print(f"\n{len(targets)} lessons with videos to download.")

        downloaded = 0
        for lesson in targets:
            success = self._process_lesson(lesson)
            if success:
                downloaded += 1

        print(f"\n{'='*40}")
        print(f" Skool download complete")
        print(f" Downloaded:  {downloaded} / {len(targets)}")
        print(f" Output dir:  {self.output_dir}")
        print(f"{'='*40}")

    async def _login(self, page, context):
        print("Logging in to Skool (browser window will open)...")
        await page.goto(f"{self.BASE_URL}/login")
        await page.wait_for_selector('input[type="email"], input[name="email"]', timeout=15000)
        await page.fill('input[type="email"], input[name="email"]', self.email)
        await page.fill('input[type="password"], input[name="password"]', self.password)
        await page.click('button[type="submit"]')
        try:
            await page.wait_for_url(lambda url: "login" not in url.lower(), timeout=20000)
        except Exception:
            print("Login redirect timed out — complete any 2FA in the browser window.")
            await asyncio.sleep(15)
        LOGS_DIR.mkdir(exist_ok=True)
        await context.storage_state(path=str(SESSION_FILE))
        print(f"Logged in. Session saved.")

    async def _get_accessible_courses(self, page) -> list[dict]:
        await page.goto(f"{self.BASE_URL}/{self.community_slug}/classroom")
        await page.wait_for_load_state("domcontentloaded", timeout=15000)
        await asyncio.sleep(2)

        next_data = await page.evaluate("() => window.__NEXT_DATA__ || null")
        if not next_data:
            return []

        all_courses = (
            next_data.get("props", {})
            .get("pageProps", {})
            .get("allCourses", [])
        )
        # Only courses where user has access and has at least one module
        return [
            c for c in all_courses
            if c.get("metadata", {}).get("hasAccess") == 1
            and c.get("metadata", {}).get("numModules", 0) > 0
        ]

    async def _get_course_lessons(self, page, course: dict) -> list[dict]:
        course_name = course.get("name", "")
        title = course.get("metadata", {}).get("title", course_name)
        url = f"{self.BASE_URL}/{self.community_slug}/classroom/{course_name}"

        print(f"\n  Course: {title}")
        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded", timeout=15000)
        # Give client-side hydration time to fetch course data from the API
        await asyncio.sleep(4)

        next_data = await page.evaluate("() => window.__NEXT_DATA__ || null")
        if not next_data:
            print(f"  No __NEXT_DATA__ found — skipping.")
            return []

        course_node = next_data.get("props", {}).get("pageProps", {}).get("course")
        if not course_node:
            print(f"  Course data not yet loaded — trying with extra wait...")
            await asyncio.sleep(4)
            next_data = await page.evaluate("() => window.__NEXT_DATA__ || null")
            course_node = (next_data or {}).get("props", {}).get("pageProps", {}).get("course")

        if not course_node:
            print(f"  Course data unavailable — skipping.")
            return []

        lessons = _extract_lessons(course_node)
        print(f"  {len(lessons)} lessons with video found.")
        return lessons

    def _process_lesson(self, lesson: dict) -> bool:
        title = lesson["title"]
        video_url = lesson.get("video_stream") or lesson.get("video_link")
        if not video_url:
            return False

        print(f"\n  Lesson: {title}")
        video_path = self._download_video(video_url, title)
        if not video_path:
            return False

        transcript_path = self._transcribe(video_path, title, lesson)
        if transcript_path:
            print(f"  Transcript: {transcript_path.name}")
            video_path.unlink(missing_ok=True)
            return True
        return False

    def _download_video(self, url: str, title: str) -> Path | None:
        slug = _slugify(title)
        date_str = datetime.now().strftime("%Y-%m-%d")
        # yt-dlp may choose extension; use template and find the result
        output_template = str(self.output_dir / f"{date_str}_{slug}.%(ext)s")

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            _log_error("download", f"refused non-http URL: {url[:80]!r}")
            print(f"  Refused non-http URL: {url[:60]}")
            return None
        print(f"  Downloading: {url[:70]}...")
        try:
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "--no-playlist",
                "--no-warnings",
                "-o", output_template,
                "--", url,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode != 0:
                raise RuntimeError(result.stderr[-400:] or result.stdout[-400:])

            # Find the downloaded file (yt-dlp picks the extension)
            candidates = sorted(
                self.output_dir.glob(f"{date_str}_{slug}.*"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            video_candidates = [p for p in candidates if p.suffix not in (".md", ".json")]
            if not video_candidates:
                raise RuntimeError("yt-dlp exited 0 but no video file found.")

            path = video_candidates[0]
            print(f"  Saved: {path.name}")
            return path

        except subprocess.TimeoutExpired:
            msg = f"Download timed out for '{title}'"
            print(f"  ERROR: {msg}")
            _log_error("download", msg)
            return None
        except Exception as exc:
            msg = f"Download failed for '{title}': {exc}"
            print(f"  ERROR: {msg}")
            _log_error("download", msg)
            return None

    def _transcribe(self, video_path: Path, title: str, lesson: dict) -> Path | None:
        slug = _slugify(title)
        date_str = datetime.now().strftime("%Y-%m-%d")
        md_path = self.output_dir / f"{date_str}_{slug}.md"

        try:
            from faster_whisper import WhisperModel

            print("  Transcribing with Whisper (base model)...")
            model = WhisperModel("base", device="cpu", compute_type="int8")
            segments, info = model.transcribe(str(video_path), beam_size=5)

            lines = [seg.text.strip() for seg in segments if seg.text.strip()]
            full_text = "\n".join(lines)

            video_url = lesson.get("video_link") or lesson.get("video_stream") or ""
            duration_s = int((lesson.get("duration_ms") or 0) / 1000) or int(info.duration)

            md_content = f"""# {title}

**Channel:** {self.community_slug}
**Source:** Skool — {self.community_slug}
**Group:** {self.group_dir}
**Downloaded:** {date_str}
**Language:** {info.language} (detected, confidence {info.language_probability:.0%})
**Duration:** {duration_s}s
**Video URL:** {video_url}

---

{full_text}
"""
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)

            word_count = len(full_text.split())
            print(f"  Transcribed: {word_count} words, {duration_s}s")
            return md_path

        except Exception as exc:
            msg = f"Transcription failed for '{title}': {exc}"
            print(f"  ERROR: {msg}")
            _log_error("transcribe", msg)
            return None


def run_skool_download(community_slug: str, group: str, limit: int | None = None):
    """Entry point called from main.py."""
    dl = SkoolDownloader(community_slug, group, limit=limit)
    dl.run()
