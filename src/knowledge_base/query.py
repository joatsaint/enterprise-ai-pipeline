"""
On-demand Q&A against the transcript knowledge base.

Keyword-searches the index for the top N most relevant transcripts,
sends them to Claude, and returns a synthesized answer with citations.

Rules:
- Read-only. Never modifies any file except appending to logs/query_log.json.
- One Claude API call per query.
- Answer based only on transcript content — never general knowledge.
- Always cite sources.

CLI (via main.py):
    python -m src.main ask "what AI skills are most in demand"
    python -m src.main ask "bitcoin halving impact" --group bitcoin-macro
    python -m src.main ask "how to use Claude Code" --top 5
"""
import json
import os
import re
import sys
from datetime import datetime, timezone


MODEL = "claude-haiku-4-5-20251001"
INDEX_PATH = "knowledge_base/index.json"
QUERY_LOG_PATH = "logs/query_log.json"
ERROR_LOG_PATH = "logs/error_log.json"

# 50,000 token budget → ~200,000 chars (4 chars/token).
# Use 180,000 to leave headroom for the prompt template.
MAX_CONTEXT_CHARS = 180_000


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_keywords(question):
    """Strip stop words and return meaningful search terms."""
    stop_words = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "through", "about",
        "what", "how", "why", "when", "where", "who", "which", "that", "this",
        "i", "you", "we", "they", "it", "and", "or", "but", "if", "so",
    }
    words = re.findall(r'\b\w+\b', question.lower())
    return [w for w in words if w not in stop_words and len(w) > 2]


def _score_file(entry, keywords):
    """Score a transcript entry by keyword relevance against title, channel, and path."""
    score = 0
    text_fields = [
        entry.get("title", "").lower(),
        entry.get("channel", "").lower(),
        entry.get("file_path", "").lower(),
    ]
    for kw in keywords:
        kw_lower = kw.lower()
        for field in text_fields:
            if kw_lower in field:
                score += 2

    # Also scan first 3,000 chars of file content for keyword hits
    path = entry.get("file_path", "")
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read(3000).lower()
            for kw in keywords:
                score += content.count(kw.lower())
        except OSError:
            pass
    return score


def _read_file_content(path, max_chars=None):
    """Read transcript content, capped at max_chars if provided."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read(max_chars) if max_chars else fh.read()
    except OSError:
        return ""


def _call_claude(question, context):
    """
    Send question + transcript context to Claude.
    Returns (answer_text, tokens_consumed).
    """
    import anthropic
    client = anthropic.Anthropic()

    prompt = (
        "You are a research assistant with access to YouTube transcript excerpts.\n"
        "Answer the following question using ONLY the transcript content provided.\n"
        "If the answer is not in the transcripts, say so clearly.\n"
        "Always cite which transcript(s) you drew from.\n\n"
        f"Question: {question}\n\n"
        f"Transcripts:\n{context}"
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    tokens = response.usage.input_tokens + response.usage.output_tokens
    return response.content[0].text, tokens


def _append_query_log(entry):
    """Append one record to logs/query_log.json."""
    os.makedirs("logs", exist_ok=True)
    log = {"queries": []}
    if os.path.isfile(QUERY_LOG_PATH):
        try:
            with open(QUERY_LOG_PATH, "r", encoding="utf-8") as fh:
                log = json.load(fh)
        except (json.JSONDecodeError, OSError):
            pass
    log.setdefault("queries", []).append(entry)
    with open(QUERY_LOG_PATH, "w", encoding="utf-8") as fh:
        json.dump(log, fh, indent=2, ensure_ascii=False)


def _append_error_log(message):
    """Append one record to logs/error_log.json."""
    os.makedirs("logs", exist_ok=True)
    log = {"errors": []}
    if os.path.isfile(ERROR_LOG_PATH):
        try:
            with open(ERROR_LOG_PATH, "r", encoding="utf-8") as fh:
                log = json.load(fh)
        except (json.JSONDecodeError, OSError):
            pass
    log.setdefault("errors", []).append({
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "module": "query",
        "error": message,
    })
    with open(ERROR_LOG_PATH, "w", encoding="utf-8") as fh:
        json.dump(log, fh, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_index():
    """Load index.json. Fails fast with a clear message if missing."""
    if not os.path.isfile(INDEX_PATH):
        print("Index not found. Run: python -m src.main index")
        sys.exit(1)
    with open(INDEX_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def ask(question, group=None, top_n=10):
    """
    Answer a question using the transcript knowledge base.

    Args:
        question: Natural language question string.
        group:    Optional group name to restrict search.
        top_n:    Max number of transcripts to pass to Claude (default 10).

    Returns: (answer_text, sources_list)
    """
    index = load_index()
    keywords = _extract_keywords(question)

    if not keywords:
        return "Could not extract keywords from the question.", []

    # Step 3 — gather candidate transcript entries, applying group filter
    candidates = []
    for group_name, group_data in index.get("groups", {}).items():
        if group and group_name != group:
            continue
        for channel_data in group_data.get("channels", {}).values():
            for entry in channel_data.get("transcripts", []):
                candidates.append(entry)

    if not candidates:
        suffix = f" in group '{group}'" if group else ""
        return (
            f"No transcripts found{suffix}. "
            "Run 'python -m src.main index' first.",
            [],
        )

    # Step 4 — keyword score every candidate
    transcripts_searched = len(candidates)
    scored = [
        (score, entry)
        for entry in candidates
        if (score := _score_file(entry, keywords)) > 0
    ]

    if not scored:
        return (
            "No transcripts found matching your query. Try broader terms.",
            [],
        )

    # Step 5 — take top N, then sort by date descending to prioritize most recent
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_n]
    top.sort(key=lambda x: x[1].get("date", ""), reverse=True)

    # Step 5 cont — build context within the 50,000-token budget
    context_parts = []
    sources = []
    excluded = []
    chars_used = 0

    for _score, entry in top:
        path = entry.get("file_path", "")
        remaining = MAX_CONTEXT_CHARS - chars_used
        if remaining <= 0:
            excluded.append(os.path.basename(path))
            continue

        content = _read_file_content(path, max_chars=remaining)
        if not content:
            if not os.path.isfile(path):
                print(f"[QUERY] WARNING: file not found on disk, skipping — {path}")
            continue

        label = f"[{entry.get('title', path)} — {entry.get('channel', '')}]"
        context_parts.append(f"{label}\n{content}")
        chars_used += len(content)
        sources.append({
            "file_path": path,
            "filename": os.path.basename(path),
            "channel": entry.get("channel", ""),
            "title": entry.get("title", ""),
        })

    if excluded:
        print(
            f"[QUERY] Context limit reached — {len(excluded)} file(s) excluded: "
            + ", ".join(excluded)
        )

    if not context_parts:
        return (
            "No transcripts found matching your query. Try broader terms.",
            [],
        )

    context = "\n\n---\n\n".join(context_parts)

    # Step 7 — call Claude API
    try:
        answer, tokens_consumed = _call_claude(question, context)
    except Exception as exc:
        msg = f"Claude API error: {exc}. Try again in a moment."
        _append_error_log(str(exc))
        return msg, sources

    # Step 9 — log query
    _append_query_log({
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "group_filter": group,
        "transcripts_searched": transcripts_searched,
        "transcripts_used": [s["file_path"] for s in sources],
        "tokens_consumed": tokens_consumed,
        "model": MODEL,
    })

    return answer, sources


def run_query(question, group=None, top_n=10):
    """CLI entry point — prints answer and sources to terminal."""
    group_label = f" (group: {group})" if group else ""
    print(f"\nSearching knowledge base{group_label}...")

    answer, sources = ask(question, group=group, top_n=top_n)

    source_count = len(sources)
    print(
        f"\nANSWER (based on {source_count} "
        f"transcript{'s' if source_count != 1 else ''}{group_label}):\n"
    )
    print(answer)

    if sources:
        print("\nSOURCES:")
        for s in sources:
            print(f"  - {s['filename']} ({s['channel']})")
    print()
