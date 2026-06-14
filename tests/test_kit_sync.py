"""
Tests for src/funnel/kit_sync.py — Steel lead-magnet warm-list sync.

Covers:
1. classify_tier maps real Kit tag names to the right tier in priority order
2. has_steel detects the Steel lead-magnet tag (case-insensitive)
3. _days_since parses ISO timestamps against a fixed "now"
4. build_rows assigns tiers and sorts (customer > hot > warm > lead, then recency)
5. tier_counts tallies tiers
6. fetch_tag_map builds per-email tag sets + detail across tags (mocked _get)
7. run_sync with no KIT_API_KEY does nothing and writes no files
"""
from datetime import datetime, timezone
from unittest.mock import patch

from src.funnel import kit_sync


FIXED_NOW = datetime(2026, 6, 14, tzinfo=timezone.utc)


def test_classify_tier_priority():
    assert kit_sync.classify_tier(["Buyer - Field Manual"]) == "customer"
    # buyer beats field-manual/interest when both present
    assert kit_sync.classify_tier(["Buyer - Field Manual", "Interest - Field Manual"]) == "customer"
    assert kit_sync.classify_tier(["Interest - Field Manual"]) == "hot"
    assert kit_sync.classify_tier(["Field Manual Waitlist"]) == "hot"
    assert kit_sync.classify_tier(["Interest - AI Sysadmin"]) == "warm"
    assert kit_sync.classify_tier(["Newsletter - Main"]) == "warm"
    assert kit_sync.classify_tier(["Lead Magnet - Steel Server Room"]) == "lead"


def test_has_steel():
    assert kit_sync.has_steel(["Lead Magnet - Steel Server Room"]) is True
    assert kit_sync.has_steel(["lead magnet - steel server room"]) is True
    assert kit_sync.has_steel(["Newsletter - Main"]) is False


def test_days_since():
    assert kit_sync._days_since("2026-06-04T00:00:00Z", FIXED_NOW) == 10
    assert kit_sync._days_since("", FIXED_NOW) == ""
    assert kit_sync._days_since("not-a-date", FIXED_NOW) == ""


def test_build_rows_tiers_and_sort():
    cohort = ["lead@x.com", "hot@x.com", "cust@x.com", "warm@x.com", "hot2@x.com"]
    tags_map = {
        "lead@x.com": {"Lead Magnet - Steel Server Room"},
        "hot@x.com": {"Lead Magnet - Steel Server Room", "Interest - Field Manual"},
        "cust@x.com": {"Lead Magnet - Steel Server Room", "Buyer - Field Manual"},
        "warm@x.com": {"Lead Magnet - Steel Server Room", "Newsletter - Main"},
        "hot2@x.com": {"Lead Magnet - Steel Server Room", "Field Manual Waitlist"},
    }
    detail_map = {
        "lead@x.com": {"email": "lead@x.com", "created_at": "2026-06-13T00:00:00Z"},
        "hot@x.com": {"email": "hot@x.com", "created_at": "2026-06-10T00:00:00Z"},   # older
        "cust@x.com": {"email": "cust@x.com", "created_at": "2026-06-01T00:00:00Z"},
        "warm@x.com": {"email": "warm@x.com", "created_at": "2026-06-12T00:00:00Z"},
        "hot2@x.com": {"email": "hot2@x.com", "created_at": "2026-06-13T00:00:00Z"},  # newer
    }
    rows = kit_sync.build_rows(cohort, detail_map, tags_map, now=FIXED_NOW)

    # customer first, then both hot (newest first), then warm, then lead
    assert [r["email"] for r in rows] == [
        "cust@x.com", "hot2@x.com", "hot@x.com", "warm@x.com", "lead@x.com",
    ]
    by_email = {r["email"]: r for r in rows}
    assert by_email["cust@x.com"]["tier"] == "customer"
    assert by_email["hot@x.com"]["tier"] == "hot"
    assert by_email["warm@x.com"]["tier"] == "warm"
    assert by_email["lead@x.com"]["tier"] == "lead"
    # signals rendered, days computed
    assert by_email["hot@x.com"]["days_since_signup"] == 4
    assert "Interest - Field Manual" in by_email["hot@x.com"]["signals"]


def test_tier_counts():
    rows = [{"tier": "hot"}, {"tier": "hot"}, {"tier": "lead"}]
    assert kit_sync.tier_counts(rows) == {"hot": 2, "lead": 1}


def test_fetch_signal_map_builds_sets():
    # Forms carry the cohort signal (Steel form); tags + the waitlist form enrich tiering.
    responses = {
        "/forms": {"forms": [
            {"id": 10, "name": "Steel"},
            {"id": 11, "name": "Field Manual Waitlist"},
        ], "pagination": {"has_next_page": False}},
        "/forms/10/subscribers": {"subscribers": [
            {"email_address": "A@x.com", "first_name": "A", "state": "active",
             "created_at": "2026-06-01T00:00:00Z"},
            {"email_address": "b@x.com", "first_name": "B", "state": "active",
             "created_at": "2026-06-02T00:00:00Z"},
        ], "pagination": {"has_next_page": False}},
        "/forms/11/subscribers": {"subscribers": [
            {"email_address": "b@x.com", "first_name": "B", "state": "active",
             "created_at": "2026-06-02T00:00:00Z"},
        ], "pagination": {"has_next_page": False}},
        "/tags": {"tags": [
            {"id": 3, "name": "Newsletter - Main"},
        ], "pagination": {"has_next_page": False}},
        "/tags/3/subscribers": {"subscribers": [
            {"email_address": "c@x.com", "first_name": "C", "state": "active",
             "created_at": "2026-06-03T00:00:00Z"},
        ], "pagination": {"has_next_page": False}},
    }

    def fake_get(session, path, params=None):
        return responses[path]

    with patch.object(kit_sync, "_get", fake_get):
        signals_map, detail_map = kit_sync.fetch_signal_map(session=None)

    # email keys are lowercased; A@x.com -> a@x.com
    assert signals_map["a@x.com"] == {"Steel"}
    assert signals_map["b@x.com"] == {"Steel", "Field Manual Waitlist"}
    assert signals_map["c@x.com"] == {"Newsletter - Main"}
    # original-cased email preserved in detail
    assert detail_map["a@x.com"]["email"] == "A@x.com"

    cohort = [k for k, sig in signals_map.items() if kit_sync.has_steel(sig)]
    assert set(cohort) == {"a@x.com", "b@x.com"}  # c is not on a Steel form
    # b is on the Field Manual waitlist -> hot
    assert kit_sync.classify_tier(signals_map["b@x.com"]) == "hot"
    assert kit_sync.classify_tier(signals_map["a@x.com"]) == "lead"


def test_run_sync_no_key(capsys, tmp_path):
    written = []
    with patch.object(kit_sync.os, "getenv", return_value=""), \
         patch.object(kit_sync, "_write_csv", lambda *a, **k: written.append(a)):
        kit_sync.run_sync()
    out = capsys.readouterr().out
    assert "No KIT_API_KEY" in out
    assert written == []
