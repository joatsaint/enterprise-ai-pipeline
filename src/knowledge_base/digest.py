"""
Daily digest generator for the transcript knowledge base.

Identifies new transcript content since the last digest run, calls Claude to
summarize each new transcript, then synthesizes a "What to Act On" section
and writes a dated .md file to knowledge_base/digests/.

Idempotency: Running twice on the same day overwrites the existing digest file.
digest_log.json always appends — never overwrites.

CLI (via main.py):
    python -m src.main digest
    python -m src.main digest --group bitcoin-macro
    python -m src.main digest --date 2026-04-28
    python -m src.main digest --since 2026-04-01
    python -m src.main digest --force
    python -m src.main digest --scheduled
"""
import json
import os
import sys
from datetime import datetime, timezone


INDEX_PATH = "knowledge_base/index.json"
DOWNLOAD_LOG_PATH = "logs/download_log.json"
DIGEST_LOG_PATH = "logs/digest_log.json"
ERROR_LOG_PATH = "logs/error_log.json"
DIGESTS_DIR = "knowledge_base/digests"

MAX_TRANSCRIPT_CHARS = 60_000  # covers a full ~1-hour transcript at typical speaking pace
MAX_COMMENTS_CHARS = 8_000


def _load_env():
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

_load_env()

MODEL = os.getenv("DIGEST_MODEL", "claude-haiku-4-5-20251001")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _now_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _log(msg, scheduled):
    """Print only when not in scheduled (silent) mode."""
    if not scheduled:
        print(msg)


def _append_error_log(message):
    # error_log.json is a flat list on disk (matches every other module in
    # the codebase, e.g. orchestrator.py's _append_error) -- not a
    # {"errors": [...]} dict. Calling .setdefault() on the loaded list
    # crashed this function on every transient Claude API error during
    # summarization, silently killing the whole day's digest (root cause
    # of 4 missing digest days, found 2026-07-15 via Task Scheduler event
    # log + daily_run_output.log cross-reference).
    os.makedirs("logs", exist_ok=True)
    log = []
    if os.path.isfile(ERROR_LOG_PATH):
        try:
            with open(ERROR_LOG_PATH, "r", encoding="utf-8") as fh:
                log = json.load(fh)
        except (json.JSONDecodeError, OSError):
            pass
    if not isinstance(log, list):
        log = []
    log.append({
        "timestamp": _now_str(),
        "module": "digest",
        "error": message,
    })
    with open(ERROR_LOG_PATH, "w", encoding="utf-8") as fh:
        json.dump(log, fh, indent=2, ensure_ascii=False)


def _append_digest_log(run_entry):
    os.makedirs("logs", exist_ok=True)
    log = {"runs": []}
    if os.path.isfile(DIGEST_LOG_PATH):
        try:
            with open(DIGEST_LOG_PATH, "r", encoding="utf-8") as fh:
                log = json.load(fh)
        except (json.JSONDecodeError, OSError):
            pass
    log.setdefault("runs", []).append(run_entry)
    with open(DIGEST_LOG_PATH, "w", encoding="utf-8") as fh:
        json.dump(log, fh, indent=2, ensure_ascii=False)


def _last_digest_timestamp():
    """Return the timestamp string of the most recent digest run, or None."""
    if not os.path.isfile(DIGEST_LOG_PATH):
        return None
    try:
        with open(DIGEST_LOG_PATH, "r", encoding="utf-8") as fh:
            log = json.load(fh)
        runs = log.get("runs", [])
        if runs:
            return runs[-1]["timestamp"]
    except (json.JSONDecodeError, OSError, KeyError):
        pass
    return None


def _digest_already_run_today():
    """Return True if a digest was already produced for today's date."""
    if not os.path.isfile(DIGEST_LOG_PATH):
        return False
    try:
        with open(DIGEST_LOG_PATH, "r", encoding="utf-8") as fh:
            log = json.load(fh)
        today = _today()
        return any(r.get("date_digested") == today for r in log.get("runs", []))
    except (json.JSONDecodeError, OSError):
        return False


def _load_download_log():
    if not os.path.isfile(DOWNLOAD_LOG_PATH):
        return []
    try:
        with open(DOWNLOAD_LOG_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data.get("downloads", [])
    except (json.JSONDecodeError, OSError):
        return []


def _read_file_safe(path, max_chars):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read(max_chars)
    except OSError:
        return ""


# ---------------------------------------------------------------------------
# Claude API calls
# ---------------------------------------------------------------------------

def _summarize_transcript(client, title, channel, date, content, comments_content=""):
    """
    Produce a 2-3 sentence summary + top audience questions for one transcript.
    Returns (response_text, tokens_consumed).
    """
    comments_section = ""
    if comments_content.strip():
        comments_section = (
            f"\n\nAUDIENCE COMMENTS (top by relevance):\n{comments_content}"
        )

    prompt = (
        "Summarize the following YouTube transcript in 2-3 sentences covering the main topics.\n"
        "Then identify the top 2-3 questions or concerns the audience expressed in the comments "
        "(if comment content is provided). If no comments are provided, write 'None'.\n\n"
        f"Video title: {title}\n"
        f"Channel: {channel}\n"
        f"Date: {date}\n\n"
        f"TRANSCRIPT:\n{content}"
        f"{comments_section}\n\n"
        "Respond in exactly this format:\n"
        "Summary: [2-3 sentence summary of key themes]\n"
        "Top questions: [top 2-3 audience questions, or 'None']"
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    tokens = response.usage.input_tokens + response.usage.output_tokens
    return response.content[0].text.strip(), tokens


def _synthesize_action_items(client, all_summaries, group_filter):
    """
    Produce 2-3 actionable insights from today's new content.
    Returns (synthesis_text, tokens_consumed).
    """
    group_context = f" in the {group_filter} group" if group_filter else ""
    summaries_text = "\n\n".join(
        f"**{s['title']}** ({s['channel']}, {s['date']})\n{s['summary_raw']}"
        for s in all_summaries
    )

    prompt = (
        "You are advising a content creator who publishes paid PDF guides and free lead magnets "
        "for IT professionals pivoting into AI careers. "
        f"Based on the following YouTube transcript summaries{group_context}, "
        "identify 2-3 specific, actionable insights for what content to create next, "
        "what audience pain points to address, or what opportunities to capitalize on.\n\n"
        "Be specific and direct. Focus on what the creator should actually DO.\n\n"
        f"TRANSCRIPT SUMMARIES:\n{summaries_text}"
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    tokens = response.usage.input_tokens + response.usage.output_tokens
    return response.content[0].text.strip(), tokens


# ---------------------------------------------------------------------------
# Digest output formatting
# ---------------------------------------------------------------------------

def _build_digest_md(digest_date, generated_at, since_str, summarized, what_to_act_on, total):
    """Assemble the complete digest .md string from processed entries."""
    channel_count = sum(len(channels) for channels in summarized.values())
    lines = [
        f"# Daily Digest — {digest_date}",
        f"Generated: {generated_at}",
        "",
        "## Summary",
        (
            f"{total} new transcript{'s' if total != 1 else ''} added across "
            f"{channel_count} channel{'s' if channel_count != 1 else ''} since {since_str}."
        ),
        "",
    ]

    for group_name, channels in sorted(summarized.items()):
        lines.append(f"## {group_name}")
        for channel_name, entries in sorted(channels.items()):
            count = len(entries)
            lines.append(
                f"### {channel_name} — {count} new video{'s' if count != 1 else ''}"
            )
            for entry in entries:
                lines.append(f"**{entry['title']}** ({entry['date']})")
                lines.append(f"Key themes: {entry['summary_text']}")
                lines.append(f"Top audience questions: {entry['top_questions']}")
                lines.append("")
        lines.append("")

    lines.append("## What to Act On")
    lines.append(what_to_act_on)
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_digest(
    group_filter=None,
    date_filter=None,
    since_filter=None,
    force=False,
    scheduled=False,
):
    """
    Generate the daily digest.

    Args:
        group_filter:  Only summarize this group name (str or None).
        date_filter:   Only include downloads from this exact date (YYYY-MM-DD or None).
        since_filter:  Include all downloads on or after this date (YYYY-MM-DD or None).
        force:         Overwrite today's digest even if it was already run today.
        scheduled:     Suppress terminal output; errors go to error_log.json only.
    """
    import anthropic

    today = _today()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    # Step 1 — Validate index.json exists
    if not os.path.isfile(INDEX_PATH):
        msg = "index.json not found. Run: python -m src.main index"
        if scheduled:
            _append_error_log(msg)
        else:
            print(msg)
        sys.exit(1)

    # Step 1 cont — Warn if index is stale (older than 24 hours)
    index_age_hours = (
        datetime.now(timezone.utc).timestamp() - os.path.getmtime(INDEX_PATH)
    ) / 3600
    if index_age_hours > 24:
        _log(
            f"[DIGEST] WARNING: index.json is {index_age_hours:.0f} hours old. "
            "Consider running 'python -m src.main index' to refresh it.",
            scheduled,
        )

    # Guard: skip if digest already run today (unless --force)
    if not force and _digest_already_run_today():
        _log(
            f"Digest already run for {today}. Use --force to regenerate.",
            scheduled,
        )
        return

    # Step 2 — Determine cutoff and filter downloads
    downloads = _load_download_log()

    if date_filter:
        new_downloads = [
            d for d in downloads
            if d.get("timestamp", "").startswith(date_filter)
        ]
        since_str = date_filter
        digest_date = date_filter
    elif since_filter:
        new_downloads = [
            d for d in downloads
            if d.get("timestamp", "") >= since_filter
        ]
        since_str = since_filter
        digest_date = today
    else:
        last_ts = _last_digest_timestamp()
        if last_ts:
            new_downloads = [
                d for d in downloads
                if d.get("timestamp", "") > last_ts
            ]
            since_str = last_ts[:10]
        else:
            new_downloads = list(downloads)
            since_str = downloads[0]["timestamp"][:10] if downloads else today
        digest_date = today

    # Apply group filter
    if group_filter:
        new_downloads = [
            d for d in new_downloads
            if d.get("final_category", "") == group_filter
        ]

    # Step 3 — Exit cleanly if nothing new
    if not new_downloads:
        _log("No new transcripts since last digest. Nothing to summarize.", scheduled)
        _append_digest_log({
            "timestamp": _now_str(),
            "date_digested": digest_date,
            "new_transcripts": 0,
            "groups_covered": [],
            "output_file": None,
            "tokens_consumed": 0,
            "model": MODEL,
        })
        return

    # Step 4-5 — Load and group transcript files by group and channel
    grouped = {}
    skipped = 0
    for dl in new_downloads:
        file_path = dl.get("file_path", "")
        if not file_path or not os.path.isfile(file_path):
            skipped += 1
            continue
        group = dl.get("final_category", "uncategorized")
        channel = dl.get("channel", "Unknown")
        grouped.setdefault(group, {}).setdefault(channel, []).append(dl)

    if skipped:
        _log(
            f"[DIGEST] {skipped} entr{'ies' if skipped != 1 else 'y'} skipped — "
            "file not found on disk.",
            scheduled,
        )

    if not grouped:
        _log("No transcript files found on disk. Nothing to summarize.", scheduled)
        return

    # Step 6 — Per-transcript Claude API call
    client = anthropic.Anthropic()
    total_tokens = 0
    all_summaries = []
    summarized = {}

    for group_name, channels in sorted(grouped.items()):
        summarized[group_name] = {}
        for channel_name, entries in sorted(channels.items()):
            summarized[group_name][channel_name] = []
            for dl in entries:
                file_path = dl["file_path"]
                content = _read_file_safe(file_path, MAX_TRANSCRIPT_CHARS)
                comments_content = ""
                if dl.get("comments_file") and os.path.isfile(dl["comments_file"]):
                    comments_content = _read_file_safe(
                        dl["comments_file"], MAX_COMMENTS_CHARS
                    )

                date_str = dl.get("timestamp", "")[:10]
                title = dl.get("title", os.path.basename(file_path))

                try:
                    raw_summary, tokens = _summarize_transcript(
                        client, title, channel_name, date_str,
                        content, comments_content,
                    )
                    total_tokens += tokens
                except Exception as exc:
                    warning = f"Claude API error summarizing '{title}': {exc}"
                    _log(f"[DIGEST] WARNING: {warning}", scheduled)
                    _append_error_log(warning)
                    raw_summary = "Summary unavailable."

                # Parse structured response
                summary_text = raw_summary
                top_questions = "None"
                if "Summary:" in raw_summary and "Top questions:" in raw_summary:
                    parts = raw_summary.split("Top questions:", 1)
                    summary_text = parts[0].replace("Summary:", "").strip()
                    top_questions = parts[1].strip()

                entry_data = {
                    "title": title,
                    "channel": channel_name,
                    "date": date_str,
                    "summary_text": summary_text,
                    "top_questions": top_questions,
                    "summary_raw": raw_summary,
                }
                summarized[group_name][channel_name].append(entry_data)
                all_summaries.append(entry_data)

    # Step 8 — "What to Act On" synthesis
    what_to_act_on = "Synthesis unavailable."
    if all_summaries:
        try:
            what_to_act_on, synthesis_tokens = _synthesize_action_items(
                client, all_summaries, group_filter,
            )
            total_tokens += synthesis_tokens
        except Exception as exc:
            warning = f"Claude API error on synthesis: {exc}"
            _log(
                f"[DIGEST] WARNING: {warning} Writing partial digest.",
                scheduled,
            )
            _append_error_log(warning)

    # Step 9 — Write digest .md file
    os.makedirs(DIGESTS_DIR, exist_ok=True)
    output_file = os.path.join(DIGESTS_DIR, f"{digest_date}_digest.md")
    total_count = sum(
        len(entries)
        for channels in summarized.values()
        for entries in channels.values()
    )
    digest_content = _build_digest_md(
        digest_date, generated_at, since_str,
        summarized, what_to_act_on, total_count,
    )
    with open(output_file, "w", encoding="utf-8") as fh:
        fh.write(digest_content)

    # Step 10 — Update digest_log.json
    _append_digest_log({
        "timestamp": _now_str(),
        "date_digested": digest_date,
        "new_transcripts": total_count,
        "groups_covered": sorted(summarized.keys()),
        "output_file": output_file.replace("\\", "/"),
        "tokens_consumed": total_tokens,
        "model": MODEL,
    })

    # Step 11 — Terminal confirmation
    _log(
        f"Digest complete: {total_count} new "
        f"transcript{'s' if total_count != 1 else ''} summarized -> {output_file}",
        scheduled,
    )
