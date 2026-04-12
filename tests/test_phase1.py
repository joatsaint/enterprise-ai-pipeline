"""
Phase 1 test suite.
Run: pytest tests/test_phase1.py -v
"""
import json
import os
import tempfile
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class FakeSnippet:
    """Minimal stand-in for a youtube_transcript_api snippet."""
    def __init__(self, text):
        self.text = text


def _snippets(*texts):
    return [FakeSnippet(t) for t in texts]


# ---------------------------------------------------------------------------
# Test 1 — transcript_fetcher removes timestamps
# ---------------------------------------------------------------------------

def test_clean_removes_timestamps():
    from src.downloader.transcript_fetcher import clean_transcript

    snippets = _snippets(
        "Hello 0:01 world",
        "[00:01:23] this is text",
        "check at 1:30:00 for more",
    )
    cleaned, _, _ = clean_transcript(snippets)

    assert "0:01" not in cleaned
    assert "00:01:23" not in cleaned
    assert "1:30:00" not in cleaned
    assert "Hello" in cleaned
    assert "world" in cleaned
    assert "this is text" in cleaned


# ---------------------------------------------------------------------------
# Test 2 — transcript_fetcher removes filler words without altering real content
# ---------------------------------------------------------------------------

def test_clean_removes_um_uh():
    from src.downloader.transcript_fetcher import clean_transcript

    snippets = _snippets("Hello um how are uh you doing today")
    cleaned, _, _ = clean_transcript(snippets)

    assert " um " not in cleaned.lower()
    assert " uh " not in cleaned.lower()
    assert "Hello" in cleaned
    assert "how are" in cleaned
    assert "you doing today" in cleaned


def test_clean_preserves_non_filler_like():
    from src.downloader.transcript_fetcher import clean_transcript

    snippets = _snippets("I like Python programming")
    cleaned, _, _ = clean_transcript(snippets)

    assert "Python programming" in cleaned


def test_clean_removes_music_tag():
    from src.downloader.transcript_fetcher import clean_transcript

    snippets = _snippets("Intro [Music] now the real content")
    cleaned, _, _ = clean_transcript(snippets)

    assert "[Music]" not in cleaned
    assert "now the real content" in cleaned


# ---------------------------------------------------------------------------
# Test 3 — to_markdown.py produces a valid .md file with all required headers
# ---------------------------------------------------------------------------

def test_markdown_has_all_headers():
    from src.converter.to_markdown import convert_to_markdown

    metadata = {
        "title": "Test Video",
        "channel": "Test Channel",
        "published": "2024-01-01",
        "word_count_after": 100,
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            file_path = convert_to_markdown(
                "Test transcript content",
                metadata,
                "AI & Claude Code",
                "https://youtu.be/test1234567",
                "2024-04-12",
            )
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        finally:
            os.chdir(orig_dir)

    assert "# Test Video" in content
    assert "**Channel:** Test Channel" in content
    assert "**Category:** AI & Claude Code" in content
    assert "**Published:** 2024-01-01" in content
    assert "**URL:** https://youtu.be/test1234567" in content
    assert "**Downloaded:** 2024-04-12" in content
    assert "**Word Count:** 100" in content
    assert "## Transcript" in content
    assert "Test transcript content" in content


# ---------------------------------------------------------------------------
# Test 4 — Output filename follows YYYY-MM-DD_[slug].md format
# ---------------------------------------------------------------------------

def test_filename_format():
    from src.converter.to_markdown import build_filename

    filename = build_filename("Test Video Title", "2024-04-12")

    assert filename.startswith("2024-04-12_")
    assert filename.endswith(".md")
    assert " " not in filename
    assert filename == "2024-04-12_test-video-title.md"


def test_filename_special_chars_stripped():
    from src.converter.to_markdown import build_filename

    filename = build_filename("Bitcoin's Price: $200K?!", "2024-04-12")

    assert " " not in filename
    assert "?" not in filename
    assert "!" not in filename
    assert filename.endswith(".md")


# ---------------------------------------------------------------------------
# Test 5 — bitcoin-titled video → Bitcoin and Economic News
# ---------------------------------------------------------------------------

def test_bitcoin_title_suggests_bitcoin():
    from src.classifier.category import suggest_category

    result = suggest_category("Bitcoin Will Hit $200K Before 2027", "Some Channel")
    assert result == "bitcoin-and-economic-news"


def test_crypto_title_suggests_bitcoin():
    from src.classifier.category import suggest_category

    result = suggest_category("Ethereum and DeFi Market Outlook", "Generic Channel")
    assert result == "bitcoin-and-economic-news"


# ---------------------------------------------------------------------------
# Test 6 — Claude/AI-titled video → AI & Claude Code
# ---------------------------------------------------------------------------

def test_claude_title_suggests_ai():
    from src.classifier.category import suggest_category

    result = suggest_category("How to Use Claude Code for Automation", "Some Channel")
    assert result == "ai-and-claude-code"


def test_llm_title_suggests_ai():
    from src.classifier.category import suggest_category

    result = suggest_category("LLM Prompt Engineering Tutorial", "Generic Channel")
    assert result == "ai-and-claude-code"


# ---------------------------------------------------------------------------
# Test 7 — Title keywords score 2x higher than channel name keywords
# ---------------------------------------------------------------------------

def test_title_2x_outweighs_channel_1x():
    """
    Title 'bitcoin btc' (2 bitcoin kw × 2 = score 4) beats
    channel 'ai claude automation agent' (4 AI kw × 1 = score 4 → tie → bitcoin).

    Without 2x weighting: bitcoin=2, ai=4 → AI would win.
    With 2x weighting: bitcoin=4, ai=4 → tie → bitcoin wins (>= branch).
    """
    from src.classifier.category import suggest_category

    result = suggest_category("bitcoin btc", "ai claude automation agent")
    assert result == "bitcoin-and-economic-news"


def test_title_score_is_double_channel_score():
    """Direct unit test of the _score weighting math."""
    from src.classifier.category import _score, BITCOIN_KEYWORDS

    title = "bitcoin market"       # 2 keywords
    channel = "bitcoin market"     # same 2 keywords

    title_weighted = _score(title, BITCOIN_KEYWORDS) * 2
    channel_weighted = _score(channel, BITCOIN_KEYWORDS) * 1

    assert title_weighted == channel_weighted * 2


# ---------------------------------------------------------------------------
# Test 8 — Falls back to suggestion when user provides no input (timeout)
# ---------------------------------------------------------------------------

def test_classify_timeout_accepts_suggestion():
    from src.classifier.category import classify

    with patch("src.classifier.category._timed_input", return_value=None):
        folder, display, was_overridden = classify(
            "Bitcoin Analysis Deep Dive", "Crypto Channel"
        )

    assert folder == "bitcoin-and-economic-news"
    assert display == "Bitcoin and Economic News"
    assert was_overridden is False


# ---------------------------------------------------------------------------
# Test 9 — download_log.json records was_overridden=True when user changes category
# ---------------------------------------------------------------------------

def test_classify_override_records_flag():
    from src.classifier.category import classify

    # Suggestion will be bitcoin; user selects AI (1)
    with patch("src.classifier.category._timed_input", return_value="1"):
        folder, display, was_overridden = classify(
            "Bitcoin Trading Strategy", "Crypto Channel"
        )

    assert folder == "ai-and-claude-code"
    assert display == "AI & Claude Code"
    assert was_overridden is True


def test_classify_no_override_when_user_confirms():
    from src.classifier.category import classify

    # Suggestion is bitcoin; user hits Enter (confirm)
    with patch("src.classifier.category._timed_input", return_value=""):
        folder, display, was_overridden = classify(
            "Bitcoin Market Outlook", "Crypto Channel"
        )

    assert folder == "bitcoin-and-economic-news"
    assert was_overridden is False


# ---------------------------------------------------------------------------
# Test 10 — Existing single-URL download produces output in correct category folder
# ---------------------------------------------------------------------------

def test_single_url_download_lands_in_category_folder():
    """
    Integration test: mocks network calls, verifies the .md lands in the
    correct category subfolder and download_log.json is updated.
    """
    from src.orchestrator import run

    fake_snippets = _snippets(
        "This is a transcript about Bitcoin and crypto markets and macro economy."
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            with (
                patch("src.orchestrator.fetch_transcript", return_value=fake_snippets),
                patch("src.orchestrator.get_video_metadata", return_value={
                    "title": "Bitcoin Market Analysis",
                    "channel": "Crypto Channel",
                    "published": "2024-01-01",
                }),
                patch("src.classifier.category._timed_input", return_value=None),
            ):
                state = run("https://youtu.be/dQw4w9WgXcQ")

            # Resolve absolute path while still inside tmpdir
            abs_file = (
                os.path.abspath(state["file_path"]) if state["file_path"] else None
            )
            file_exists = abs_file is not None and os.path.exists(abs_file)

            log_path = os.path.join(tmpdir, "logs", "download_log.json")
            with open(log_path, "r") as f:
                log = json.load(f)
        finally:
            os.chdir(orig_dir)

    assert state["status"] == "success", f"Expected success, got: {state['status']}"
    assert abs_file is not None
    assert "bitcoin-and-economic-news" in abs_file
    assert file_exists, f"File not found: {abs_file}"

    # Verify log was written
    assert len(log["downloads"]) == 1
    assert log["downloads"][0]["video_id"] == "dQw4w9WgXcQ"
    assert log["downloads"][0]["final_category"] == "bitcoin-and-economic-news"
