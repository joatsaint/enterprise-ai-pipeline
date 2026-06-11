"""
Tests for src/curator/newsletter_curator.py — curation mode.

Covers:
1. _load_sources returns only active entries
2. _html_to_text strips tags/entities into plain text
3. _extract_body prefers text/plain over text/html in a multipart message
4. run_curate with no matching messages -> no digest file, log records 0 items
5. run_curate with a relevant + irrelevant item -> digest file with correct format
6. Idempotency -> second run without --force is skipped, --force regenerates
"""
import json
import os
import tempfile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from unittest.mock import patch, MagicMock

import pytest


def _write_sources(sources):
    with open("newsletter_sources.json", "w", encoding="utf-8") as fh:
        json.dump({"sources": sources}, fh)


def _sample_item(source_name="Test AI News", subject="Big AI News", date="2026-06-10"):
    return {
        "source_name": source_name,
        "sender_name": source_name,
        "sender_address": "news@example.com",
        "subject": subject,
        "date": date,
        "body": "Some newsletter content about AI tools and careers.",
    }


# ---------------------------------------------------------------------------
# 1 — _load_sources filters to active only
# ---------------------------------------------------------------------------

def test_load_sources_returns_only_active():
    from src.curator.newsletter_curator import _load_sources

    with tempfile.TemporaryDirectory() as tmpdir:
        orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            _write_sources([
                {"name": "Active One", "sender": "a@example.com", "active": True},
                {"name": "Inactive One", "sender": "b@example.com", "active": False},
            ])
            sources = _load_sources()
            assert [s["name"] for s in sources] == ["Active One"]
        finally:
            os.chdir(orig)


def test_load_sources_missing_file_exits():
    from src.curator.newsletter_curator import _load_sources

    with tempfile.TemporaryDirectory() as tmpdir:
        orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            with pytest.raises(SystemExit):
                _load_sources()
        finally:
            os.chdir(orig)


# ---------------------------------------------------------------------------
# 2 — _html_to_text
# ---------------------------------------------------------------------------

def test_html_to_text_strips_tags_and_entities():
    from src.curator.newsletter_curator import _html_to_text

    html = "<html><body><p>AI &amp; you</p><br><div>Second line</div></body></html>"
    text = _html_to_text(html)
    assert "AI & you" in text
    assert "Second line" in text
    assert "<" not in text and ">" not in text


# ---------------------------------------------------------------------------
# 3 — _extract_body prefers text/plain
# ---------------------------------------------------------------------------

def test_extract_body_prefers_plain_text():
    from src.curator.newsletter_curator import _extract_body

    msg = MIMEMultipart("alternative")
    msg.attach(MIMEText("<p>HTML version</p>", "html"))
    msg.attach(MIMEText("Plain version", "plain"))

    body = _extract_body(msg)
    assert body == "Plain version"


def test_extract_body_falls_back_to_html():
    from src.curator.newsletter_curator import _extract_body

    msg = MIMEMultipart("alternative")
    msg.attach(MIMEText("<p>Only HTML <b>here</b></p>", "html"))

    body = _extract_body(msg)
    assert "Only HTML" in body
    assert "<" not in body


# ---------------------------------------------------------------------------
# 4 — run_curate with no matching messages
# ---------------------------------------------------------------------------

def test_run_curate_no_matches_writes_no_digest():
    from src.curator.newsletter_curator import run_curate

    with tempfile.TemporaryDirectory() as tmpdir:
        orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            _write_sources([
                {"name": "Test AI News", "sender": "news@example.com", "active": True},
            ])

            with patch("src.curator.newsletter_curator._imap_connect",
                       return_value=(MagicMock(), "user@hotmail.com")), \
                 patch("src.curator.newsletter_curator._fetch_curatable_messages",
                       return_value=[]):
                run_curate(days=7)

            today = __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).strftime("%Y-%m-%d")
            assert not os.path.isfile(
                f"content-engine/newsletter_curation/{today}_digest.md"
            )

            with open("logs/newsletter_curation_log.json", encoding="utf-8") as fh:
                log = json.load(fh)
            assert log["runs"][-1]["items_found"] == 0
            assert log["runs"][-1]["output_file"] is None
        finally:
            os.chdir(orig)


# ---------------------------------------------------------------------------
# 5 — run_curate with relevant + irrelevant items
# ---------------------------------------------------------------------------

def test_run_curate_produces_digest_with_relevant_items():
    from src.curator.newsletter_curator import run_curate

    with tempfile.TemporaryDirectory() as tmpdir:
        orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            _write_sources([
                {"name": "Test AI News", "sender": "news@example.com", "active": True},
            ])

            relevant_item = _sample_item(subject="New AI Model Released")
            irrelevant_item = _sample_item(subject="Unrelated Promo")

            def fake_curate_item(client, item):
                if item["subject"] == "New AI Model Released":
                    return True, "A new AI model was announced with strong coding skills.", \
                        "Useful for AI tooling content.", 100
                return False, "Promotional content unrelated to AI careers.", "N/A", 50

            with patch("src.curator.newsletter_curator._imap_connect",
                       return_value=(MagicMock(), "user@hotmail.com")), \
                 patch("src.curator.newsletter_curator._fetch_curatable_messages",
                       return_value=[relevant_item, irrelevant_item]), \
                 patch("src.curator.newsletter_curator._curate_item",
                       side_effect=fake_curate_item), \
                 patch("src.curator.newsletter_curator._synthesize_action_items",
                       return_value=("1. Cover the new AI model launch.", 75)), \
                 patch("anthropic.Anthropic", return_value=MagicMock()):
                run_curate(days=7)

            import datetime as dt
            today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
            digest_path = f"content-engine/newsletter_curation/{today}_digest.md"
            assert os.path.isfile(digest_path)

            content = open(digest_path, encoding="utf-8").read()
            assert "## Test AI News" in content
            assert "New AI Model Released" in content
            assert "Unrelated Promo" not in content
            assert "Cover the new AI model launch" in content

            with open("logs/newsletter_curation_log.json", encoding="utf-8") as fh:
                log = json.load(fh)
            run = log["runs"][-1]
            assert run["items_found"] == 2
            assert run["items_relevant"] == 1
            assert run["output_file"] == digest_path
            assert run["tokens_consumed"] == 225
        finally:
            os.chdir(orig)


# ---------------------------------------------------------------------------
# 6 — Idempotency
# ---------------------------------------------------------------------------

def test_run_curate_idempotent_unless_forced():
    from src.curator.newsletter_curator import run_curate

    with tempfile.TemporaryDirectory() as tmpdir:
        orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            _write_sources([
                {"name": "Test AI News", "sender": "news@example.com", "active": True},
            ])

            with patch("src.curator.newsletter_curator._imap_connect",
                       return_value=(MagicMock(), "user@hotmail.com")), \
                 patch("src.curator.newsletter_curator._fetch_curatable_messages",
                       return_value=[]):
                run_curate(days=7)
                run_curate(days=7)  # not forced -> skipped, no second log entry

            with open("logs/newsletter_curation_log.json", encoding="utf-8") as fh:
                log = json.load(fh)
            assert len(log["runs"]) == 1

            with patch("src.curator.newsletter_curator._imap_connect",
                       return_value=(MagicMock(), "user@hotmail.com")), \
                 patch("src.curator.newsletter_curator._fetch_curatable_messages",
                       return_value=[]):
                run_curate(days=7, force=True)

            with open("logs/newsletter_curation_log.json", encoding="utf-8") as fh:
                log = json.load(fh)
            assert len(log["runs"]) == 2
        finally:
            os.chdir(orig)
