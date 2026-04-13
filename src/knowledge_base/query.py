"""
On-demand Q&A against the transcript knowledge base.

Uses keyword search to find the top 5 most relevant transcripts,
then sends them to Claude to answer the user's question.

Rules:
- Maximum 1 Claude API call per query.
- Answer based only on transcript content — never general knowledge.
- Always cite sources.
- If no relevant transcripts found, say so clearly.
"""
import os
import re

from src.knowledge_base.indexer import load_index


def _score_file(entry, keywords):
    """Score a transcript file by keyword relevance."""
    score = 0
    text_fields = [
        entry.get("title", "").lower(),
        entry.get("channel", "").lower(),
        entry.get("filename", "").lower(),
    ]
    for kw in keywords:
        kw = kw.lower()
        for field in text_fields:
            if kw in field:
                score += 2

    # Also scan file content (first 3000 chars for speed)
    path = entry.get("path", "")
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(3000).lower()
            for kw in keywords:
                score += content.count(kw.lower())
        except Exception:
            pass
    return score


def _extract_keywords(question):
    """Simple keyword extraction — strip stop words."""
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


def _read_file_content(path, max_chars=4000):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(max_chars)
    except Exception:
        return ""


def _call_claude(question, transcripts_context, sources):
    """Make one Claude API call to answer the question."""
    import anthropic

    client = anthropic.Anthropic()
    model = os.getenv("ANALYZER_MODEL", "claude-haiku-4-5-20251001")

    source_labels = "\n".join(
        f"- {os.path.basename(s['path'])} ({s['channel']})"
        for s in sources
    )

    prompt = f"""You are a research assistant with access to a library of YouTube transcript excerpts.
Answer the user's question based ONLY on the content provided below.
Do NOT use general knowledge. If the transcripts don't contain enough information, say so explicitly.
Always cite which transcript(s) supported your answer.

QUESTION: {question}

TRANSCRIPT EXCERPTS:
{transcripts_context}

Answer the question directly and concisely. Then list the sources you used."""

    response = client.messages.create(
        model=model,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def ask(question, group=None):
    """
    Answer a question using the transcript knowledge base.

    Args:
        question: The question to answer.
        group: Optional group name to restrict search.

    Returns: (answer_text, sources_list)
    """
    index = load_index()
    keywords = _extract_keywords(question)

    if not keywords:
        return "Could not extract keywords from the question.", []

    # Gather candidate files
    candidates = []
    for group_name, group_data in index.get("groups", {}).items():
        if group and group_name != group:
            continue
        for entry in group_data.get("files", []):
            candidates.append((group_name, entry))

    if not candidates:
        msg = f"No transcripts found"
        if group:
            msg += f" in group '{group}'"
        return msg + ". Run 'python -m src.main index' first.", []

    # Score and rank
    scored = []
    for group_name, entry in candidates:
        score = _score_file(entry, keywords)
        if score > 0:
            scored.append((score, group_name, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:5]

    if not top:
        return (
            f"No transcripts relevant to '{question}' were found in the knowledge base. "
            "Try different keywords or download more content first.",
            [],
        )

    # Build context
    context_parts = []
    sources = []
    for score, group_name, entry in top:
        path = entry.get("path", "")
        content = _read_file_content(path, max_chars=3000)
        label = f"[{entry.get('title', entry['filename'])} — {entry.get('channel', '')}]"
        context_parts.append(f"{label}\n{content}")
        sources.append({
            "filename": entry["filename"],
            "path": path,
            "channel": entry.get("channel", ""),
            "title": entry.get("title", ""),
        })

    transcripts_context = "\n\n---\n\n".join(context_parts)

    try:
        answer = _call_claude(question, transcripts_context, sources)
    except Exception as e:
        return f"Claude API error: {e}", sources

    return answer, sources


def run_query(question, group=None):
    """CLI entry point — prints answer and sources."""
    group_label = f" (group: {group})" if group else ""
    print(f"\nSearching knowledge base{group_label}...")

    answer, sources = ask(question, group=group)

    source_count = len(sources)
    print(f"\nANSWER (based on {source_count} transcript{'s' if source_count != 1 else ''}"
          f"{group_label}):\n")
    print(answer)

    if sources:
        print("\nSOURCES:")
        for s in sources:
            print(f"  - {s['filename']} ({s['channel']})")
    print()
