"""
Skool full course ARCHIVER — captures everything needed to complete a course
offline: videos (resolution-capped), transcripts, written lessons (desc ->
Markdown), resources, and text-only lessons. Resumable (skips already-captured
lessons) and uses randomized human-like pacing to avoid bot-pattern detection.

Output (gitignored `courses/`):
  courses/{community}/
    course_index.md
    {NN}_{course}/
      {MM}_{lesson}/
        lesson.md          # written lesson (desc) + resources + metadata
        video.<ext>        # kept video (<= resolution cap), if the lesson has one
        transcript.md      # Whisper transcript, if the lesson has a video

Pacing: navigation uses randomized delays (random.uniform) rather than fixed
sleeps, per the project rule that uniform timing is a bot signature.

Note: videos are downloaded after the browser closes. Build Room videos are all
external (YouTube/Loom) public URLs, so this is safe. For a community that serves
Skool-native Mux video (token in the stream URL), tokens could expire on a long
run — such a case would need per-course download while the session is fresh.

Usage (via main.py):
  python -m src.main skool-archive --community buildroom [--resolution 1080]
      [--course "Tech Toolbox"] [--limit N]
"""
import asyncio
import glob
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from src.downloader.skool import (
    SkoolDownloader, SESSION_FILE, _slugify, _log_error,
)


def _find_ffmpeg_dir():
    """Locate ffmpeg's bin dir so yt-dlp can merge video+audio, without depending
    on a PATH refresh. Order: FFMPEG_LOCATION env -> PATH -> winget install dir."""
    env = os.environ.get("FFMPEG_LOCATION")
    if env and Path(env).exists():
        return env
    exe = shutil.which("ffmpeg")
    if exe:
        return str(Path(exe).parent)
    local = os.environ.get("LOCALAPPDATA", "")
    if local:
        pattern = os.path.join(local, "Microsoft", "WinGet", "Packages",
                               "Gyan.FFmpeg*", "**", "bin", "ffmpeg.exe")
        hits = glob.glob(pattern, recursive=True)
        if hits:
            return str(Path(hits[0]).parent)
    return None


# --------------------------------------------------------------------------
# Rich-text (Skool "[v2]" desc) -> Markdown
# --------------------------------------------------------------------------
def _inline(node):
    t = node.get("type")
    if t == "text":
        txt = node.get("text", "")
        for mark in node.get("marks", []) or []:
            mt = mark.get("type")
            if mt in ("bold", "strong"):
                txt = f"**{txt}**"
            elif mt in ("italic", "em"):
                txt = f"*{txt}*"
            elif mt == "code":
                txt = f"`{txt}`"
            elif mt == "link":
                href = (mark.get("attrs") or {}).get("href", "")
                txt = f"[{txt}]({href})"
        return txt
    if t in ("hardBreak", "break"):
        return "  \n"
    return "".join(_inline(c) for c in node.get("content", []) or [])


def _block(node):
    t = node.get("type")
    if t == "paragraph":
        return _inline(node).strip() + "\n\n"
    if t == "heading":
        lvl = int((node.get("attrs") or {}).get("level", 2) or 2)
        return "#" * max(1, min(6, lvl)) + " " + _inline(node).strip() + "\n\n"
    if t in ("bulletList", "unorderedList"):
        items = ["- " + _inline(li).strip() for li in node.get("content", []) or []]
        return "\n".join(items) + "\n\n"
    if t in ("orderedList", "numberedList"):
        items = [f"{i}. " + _inline(li).strip()
                 for i, li in enumerate(node.get("content", []) or [], 1)]
        return "\n".join(items) + "\n\n"
    if t == "blockquote":
        inner = "".join(_block(c) for c in node.get("content", []) or []).strip()
        return "\n".join("> " + ln for ln in inner.splitlines()) + "\n\n"
    if t in ("codeBlock", "code_block"):
        return "```\n" + _inline(node) + "\n```\n\n"
    if t in ("horizontalRule", "horizontal_rule", "divider"):
        return "---\n\n"
    if t == "image":
        src = (node.get("attrs") or {}).get("src", "")
        return f"![]({src})\n\n"
    if node.get("content"):
        return "".join(_block(c) for c in node["content"])
    return _inline(node)


def richtext_to_markdown(desc):
    """Convert Skool's serialized rich-text desc ('[v2]' + JSON nodes) to Markdown.
    Degrades gracefully: unknown nodes fall back to their text; a parse failure
    falls back to extracting raw text runs."""
    if not desc or not isinstance(desc, str):
        return ""
    s = re.sub(r"^\s*\[v\d+\]\s*", "", desc)
    try:
        nodes = json.loads(s)
    except Exception:
        runs = re.findall(r'"text"\s*:\s*"((?:[^"\\]|\\.)*)"', s)
        out = []
        for r in runs:
            try:
                out.append(json.loads('"' + r + '"'))
            except Exception:
                out.append(r)
        return "\n\n".join(out).strip()
    if isinstance(nodes, dict):
        nodes = [nodes]
    if not isinstance(nodes, list):
        return ""
    return "".join(_block(n) for n in nodes).strip()


def parse_resources(resources):
    """Skool 'resources' is a JSON-string array. Return [{label,url}] defensively."""
    if not resources:
        return []
    data = resources
    if isinstance(resources, str):
        try:
            data = json.loads(resources)
        except Exception:
            return []
    out = []
    if isinstance(data, list):
        for r in data:
            if isinstance(r, dict):
                out.append({
                    "label": (r.get("label") or r.get("title") or r.get("name")
                              or r.get("text") or "resource"),
                    "url": r.get("url") or r.get("link") or r.get("href") or "",
                })
            elif isinstance(r, str):
                out.append({"label": "resource", "url": r})
    return out


def _extract_lessons_full(node):
    """Walk the course tree; capture EVERY module (incl. text-only) with desc/resources."""
    lessons = []
    for child in node.get("children", []) or []:
        c = child.get("course", {})
        meta = c.get("metadata", {})
        if c.get("unitType") == "module":
            lessons.append({
                "id": c.get("id"),
                "title": meta.get("title", "Untitled"),
                "desc": meta.get("desc"),
                "resources": meta.get("resources"),
                "video_link": meta.get("videoLink") or None,
                "video_stream": meta.get("videoStream") or None,
                "duration_ms": meta.get("videoLenMs"),
            })
        if child.get("children"):
            lessons.extend(_extract_lessons_full(child))
    return lessons


class SkoolArchiver(SkoolDownloader):
    def __init__(self, community_slug, resolution=1080, limit=None,
                 course_filter=None, base_dir="courses"):
        self.community_slug = community_slug
        self.resolution = int(resolution)
        self.limit = limit
        self.course_filter = (course_filter or "").lower() or None
        self.email = os.getenv("SKOOL_EMAIL")
        self.password = os.getenv("SKOOL_PASSWORD")
        self.root = Path(base_dir) / community_slug
        self.root.mkdir(parents=True, exist_ok=True)
        self.archive_log = self.root / "_archive_log.json"
        self._done = self._load_done()
        self._whisper = None
        self.ffmpeg_dir = _find_ffmpeg_dir()
        self.stats = {"videos": 0, "lessons": 0, "skipped": 0, "failed": 0}

    # ---- resume bookkeeping ----
    def _load_done(self):
        if self.archive_log.is_file():
            try:
                with open(self.archive_log, "r", encoding="utf-8") as f:
                    return set(json.load(f).get("done", []))
            except Exception:
                return set()
        return set()

    def _mark_done(self, lesson_id):
        if lesson_id:
            self._done.add(lesson_id)
            try:
                with open(self.archive_log, "w", encoding="utf-8") as f:
                    json.dump({"done": sorted(self._done)}, f, indent=2)
            except Exception:
                pass

    # ---- randomized pacing (uniform timing is a bot signature) ----
    async def _apause(self, lo, hi):
        await asyncio.sleep(random.uniform(lo, hi))

    def _spause(self, lo, hi):
        time.sleep(random.uniform(lo, hi))

    # ---- whisper (load once, reuse across lessons) ----
    def _transcribe(self, video_path):
        if self._whisper is None:
            from faster_whisper import WhisperModel
            self._whisper = WhisperModel("base", device="cpu", compute_type="int8")
        segments, info = self._whisper.transcribe(str(video_path), beam_size=5)
        text = "\n".join(s.text.strip() for s in segments if s.text.strip())
        return text, info

    def run(self):
        asyncio.run(self._run_async())

    async def _run_async(self):
        if not self.email or not self.password:
            print("ERROR: Set SKOOL_EMAIL and SKOOL_PASSWORD in .env before running.")
            sys.exit(1)
        from playwright.async_api import async_playwright

        structure = []  # [(course_title, [lessons])] preserving order
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            ctx_opts = {"storage_state": str(SESSION_FILE)} if SESSION_FILE.is_file() else {}
            context = await browser.new_context(**ctx_opts)
            page = await context.new_page()

            if not SESSION_FILE.is_file():
                await self._login(page, context)
            else:
                print("Reusing saved session — verifying...")
                await page.goto(f"{self.BASE_URL}/{self.community_slug}/classroom")
                await page.wait_for_load_state("domcontentloaded", timeout=15000)
                if "login" in page.url.lower():
                    SESSION_FILE.unlink(missing_ok=True)
                    await self._login(page, context)

            courses = await self._get_accessible_courses(page)
            if self.course_filter:
                courses = [
                    c for c in courses
                    if self.course_filter in
                    ((c.get("metadata", {}).get("title") or c.get("name") or "").lower())
                ]
            print(f"{len(courses)} courses to archive.")

            for course in courses:
                title = course.get("metadata", {}).get("title") or course.get("name")
                lessons = await self._get_course_lessons_full(page, course)
                structure.append((title, lessons))
                await self._apause(3, 8)  # randomized delay between course pages
            await browser.close()

        # ---- process (download + write); browser is closed, downloads hit CDNs ----
        processed = 0
        for ci, (course_title, lessons) in enumerate(structure, 1):
            course_dir = self.root / f"{ci:02d}_{_slugify(course_title)}"
            for li, lesson in enumerate(lessons, 1):
                if self.limit and processed >= self.limit:
                    break
                processed += 1
                lesson_dir = course_dir / f"{li:02d}_{_slugify(lesson['title'])}"
                if self._is_done(lesson, lesson_dir):
                    self.stats["skipped"] += 1
                    continue
                try:
                    if self._process_lesson(lesson, lesson_dir, course_title):
                        self._mark_done(lesson.get("id"))
                except Exception as exc:
                    self.stats["failed"] += 1
                    _log_error("archive", f"lesson '{lesson['title']}': {exc}")
                    print(f"  ERROR: {lesson['title']}: {exc}")
                if lesson.get("video_link") or lesson.get("video_stream"):
                    self._spause(8, 20)  # randomized pause after a real download
            if self.limit and processed >= self.limit:
                break

        self._write_index(structure)
        self._print_summary()

    def _is_done(self, lesson, lesson_dir):
        if lesson.get("id") in self._done:
            return True
        prefix = lesson_dir.name
        if not (lesson_dir / f"{prefix}_lesson.md").is_file():
            return False
        has_video = bool(lesson.get("video_link") or lesson.get("video_stream"))
        if not has_video:
            return True
        return (lesson_dir / f"{prefix}_transcript.md").is_file()

    async def _get_course_lessons_full(self, page, course):
        course_name = course.get("name", "")
        title = course.get("metadata", {}).get("title", course_name)
        print(f"\n  Course: {title}")
        await page.goto(f"{self.BASE_URL}/{self.community_slug}/classroom/{course_name}")
        await page.wait_for_load_state("domcontentloaded", timeout=15000)
        await self._apause(3.5, 6.5)  # randomized hydration wait
        nd = await page.evaluate("() => window.__NEXT_DATA__ || null")
        node = (nd or {}).get("props", {}).get("pageProps", {}).get("course")
        if not node:
            await self._apause(3, 5)
            nd = await page.evaluate("() => window.__NEXT_DATA__ || null")
            node = (nd or {}).get("props", {}).get("pageProps", {}).get("course")
        if not node:
            print("  Course data unavailable — skipping.")
            return []
        lessons = _extract_lessons_full(node)
        nv = sum(1 for l in lessons if l.get("video_link") or l.get("video_stream"))
        print(f"  {len(lessons)} lessons ({nv} with video).")
        return lessons

    def _process_lesson(self, lesson, lesson_dir, course_title):
        lesson_dir.mkdir(parents=True, exist_ok=True)
        prefix = lesson_dir.name
        title = lesson["title"]
        video_url = lesson.get("video_stream") or lesson.get("video_link")
        print(f"  Lesson: {title}")

        body = richtext_to_markdown(lesson.get("desc"))
        resources = parse_resources(lesson.get("resources"))
        dur_s = int((lesson.get("duration_ms") or 0) / 1000)
        md = [f"# {title}", "",
              f"**Course:** {course_title}",
              f"**Type:** {'video' if video_url else 'text'}"]
        if video_url:
            md.append(f"**Video URL:** {lesson.get('video_link') or lesson.get('video_stream')}")
        if dur_s:
            md.append(f"**Duration:** {dur_s}s")
        md += ["", "---", "", "## Lesson", "", body or "_(no written content)_"]
        if resources:
            md += ["", "## Resources", ""]
            for r in resources:
                md.append(f"- [{r['label']}]({r['url']})" if r["url"] else f"- {r['label']}")
        (lesson_dir / f"{prefix}_lesson.md").write_text("\n".join(md) + "\n", encoding="utf-8")
        self.stats["lessons"] += 1

        if not video_url:
            return True  # text-only lesson is fully captured
        video_path = self._download_video(video_url, lesson_dir)
        if not video_path:
            return False  # leave un-done so a re-run retries it
        text, info = self._transcribe(video_path)
        tmd = [f"# {title} — Transcript", "",
               f"**Language:** {info.language} ({info.language_probability:.0%})",
               f"**Duration:** {int(info.duration)}s", "", "---", "", text]
        (lesson_dir / f"{prefix}_transcript.md").write_text("\n".join(tmd) + "\n", encoding="utf-8")
        self.stats["videos"] += 1
        print(f"    video + transcript ({len(text.split())} words)")
        return True

    def _has_video_stream(self, path):
        """Verify a downloaded file actually contains video (ffmpeg can merge HLS
        and yet yt-dlp exits non-zero — so we trust the file, not the exit code)."""
        if self.ffmpeg_dir:
            ffprobe = Path(self.ffmpeg_dir) / "ffprobe.exe"
            if ffprobe.is_file():
                try:
                    r = subprocess.run(
                        [str(ffprobe), "-v", "error", "-select_streams", "v:0",
                         "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(path)],
                        capture_output=True, text=True, timeout=60)
                    return "video" in (r.stdout or "")
                except Exception:
                    pass
        return path.stat().st_size > 200_000  # fallback heuristic

    def _download_video(self, url, lesson_dir):
        """Download capped at the resolution, with fallbacks. Loom HLS can make
        yt-dlp exit non-zero ('Did not get any data blocks') even when ffmpeg has
        already produced a valid merged file — so success is judged by probing the
        OUTPUT file for a video stream, not by yt-dlp's exit code."""
        prefix = lesson_dir.name
        out_tmpl = str(lesson_dir / f"{prefix}_video.%(ext)s")
        res = self.resolution
        attempts = [
            f"best[height<={res}]/bestvideo[height<={res}]+bestaudio/best",
            "bestvideo+bestaudio/best",
            None,  # yt-dlp default selection
        ]
        last_err = "no attempt ran"
        for fmt in attempts:
            for p in lesson_dir.glob(f"{prefix}_video.*"):  # clear any partial from prior attempt
                try:
                    p.unlink()
                except OSError:
                    pass
            cmd = [sys.executable, "-m", "yt_dlp", "--no-playlist", "--no-warnings",
                   "--fragment-retries", "10", "--retries", "5"]
            if self.ffmpeg_dir:
                cmd += ["--ffmpeg-location", self.ffmpeg_dir]
            if fmt:
                cmd += ["-f", fmt]
            cmd += ["-o", out_tmpl, url]
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
                last_err = (r.stderr[-300:] or r.stdout[-300:] or "").strip()
            except Exception as exc:
                last_err = str(exc)[:200]
                continue
            vids = [p for p in lesson_dir.glob(f"{prefix}_video.*")
                    if p.suffix not in (".md", ".json", ".part", ".ytdl")]
            if vids:
                vid = sorted(vids, key=lambda p: p.stat().st_mtime, reverse=True)[0]
                if self._has_video_stream(vid):
                    return vid  # valid video, regardless of yt-dlp's exit code
        _log_error("archive-download", f"{url[:60]}: {last_err}")
        print(f"    download failed: {last_err or 'no valid video produced'}")
        return None

    def _write_index(self, structure):
        lines = [f"# {self.community_slug} — Course Archive", "",
                 f"_Archived {datetime.now().strftime('%Y-%m-%d')}_", ""]
        for ci, (title, lessons) in enumerate(structure, 1):
            cdir = f"{ci:02d}_{_slugify(title)}"
            nv = sum(1 for l in lessons if l.get("video_link") or l.get("video_stream"))
            lines.append(f"## {ci:02d}. {title}  ({len(lessons)} lessons, {nv} video)")
            for li, lesson in enumerate(lessons, 1):
                ldir = f"{li:02d}_{_slugify(lesson['title'])}"
                tag = "[video]" if (lesson.get("video_link") or lesson.get("video_stream")) else "[text]"
                lines.append(f"- {tag} [{lesson['title']}]({cdir}/{ldir}/{ldir}_lesson.md)")
            lines.append("")
        (self.root / "course_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _print_summary(self):
        print("\n" + "=" * 44)
        print(" Skool archive complete")
        print(f"  Lessons written:  {self.stats['lessons']}")
        print(f"  Videos saved:     {self.stats['videos']}")
        print(f"  Skipped (resume): {self.stats['skipped']}")
        print(f"  Failed:           {self.stats['failed']}")
        print(f"  Output:           {self.root}")
        print("=" * 44)


def run_skool_archive(community_slug, resolution=1080, limit=None, course_filter=None):
    """Entry point called from main.py."""
    SkoolArchiver(community_slug, resolution=resolution, limit=limit,
                  course_filter=course_filter).run()
