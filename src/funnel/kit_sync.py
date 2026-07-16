"""
Kit Sync — pull the Steel lead-magnet cohort from Kit (ConvertKit) and write a
warm-list, tiered by engagement, for follow-up.

Part of the sales/conversion engine (see courses/buildroom/ANALYSIS_feature-feasibility.md
§6). Read-only against Kit — it never writes back to Kit, never publishes anything.

Cohort signal: in Kit, filling a form subscribes someone, but tags are only applied by
a separate automation. So the definitive "downloaded Steel" signal is **Steel form
membership**, not a tag. We therefore build each subscriber's signal set from BOTH their
form memberships AND their tags, and tier on the combined set:
  - Steel form           -> in the cohort
  - Field Manual waitlist/interest -> "hot" (wants the paid product)
  - Buyer tag            -> "customer"
  - Newsletter/interest  -> "warm"
  - Steel only           -> "lead"

Pipeline:
  1. Kit V4 API (X-Kit-Api-Key auth): list forms + tags, then list each one's subscribers.
  2. Build per-subscriber signal sets (form names + tag names).
  3. Cohort = everyone whose signals include a "Steel" form; classify each by tier.
  4. Write a CSV warm-list + a counts-only summary; append a PII-free run log.

Output: content-engine/distribution/warmlist/steel_warmlist.csv   (gitignored — contains emails/PII)
        content-engine/distribution/warmlist/steel_warmlist_summary.md  (counts only)
Log:    logs/kit_sync_log.json   (counts only — never emails, per CLAUDE.md logging rules)

Kit is an approved outbound integration for this project (Randy directed the funnel
build + provided the V4 key). The API key is read from .env and never printed/logged.
"""
import csv
import json
import os
import time
from datetime import datetime, timezone

import requests

KIT_BASE = "https://api.kit.com/v4"
KIT_LOG = "logs/kit_sync_log.json"
OUT_DIR = os.path.join("content-engine", "distribution", "warmlist")
CSV_PATH = os.path.join(OUT_DIR, "steel_warmlist.csv")
SUMMARY_PATH = os.path.join(OUT_DIR, "steel_warmlist_summary.md")

# A subscriber is in the cohort if any of their signals (form/tag names) contains this.
STEEL_MARKER = "steel"

# Engagement tiers, checked in priority order. First match wins.
TIER_RULES = [
    ("customer", ("buyer",)),                 # Buyer - Field Manual (tag)
    ("hot", ("field manual", "waitlist")),    # Field Manual waitlist form / interest tag
    ("warm", ("interest", "newsletter")),     # Interest - AI Sysadmin, Newsletter - Main
]
TIER_RANK = {"customer": 0, "hot": 1, "warm": 2, "lead": 3}

CSV_COLUMNS = ["email", "first_name", "state", "created_at", "days_since_signup", "tier", "signals"]


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


# --------------------------------------------------------------------------
# Pure logic (unit-tested) — no network
# --------------------------------------------------------------------------
def classify_tier(signals):
    """Return the engagement tier for a set/list of signal names (forms + tags)."""
    low = [s.lower() for s in signals]
    for tier, markers in TIER_RULES:
        if any(marker in s for s in low for marker in markers):
            return tier
    return "lead"


def has_steel(signals):
    return any(STEEL_MARKER in s.lower() for s in signals)


def _days_since(created_at, now):
    if not created_at:
        return ""
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        return (now - dt).days
    except Exception:
        return ""


def build_rows(cohort_emails, detail_map, signals_map, now=None):
    """
    Build sorted warm-list rows.

    cohort_emails: iterable of lowercased email keys in the cohort
    detail_map:    {email_key: {email, first_name, state, created_at}}
    signals_map:   {email_key: set(form/tag name)}
    """
    now = now or datetime.now(timezone.utc)
    rows = []
    for key in cohort_emails:
        signals = sorted(signals_map.get(key, set()))
        tier = classify_tier(signals)
        d = detail_map.get(key, {})
        rows.append({
            "email": d.get("email", key),
            "first_name": (d.get("first_name") or "").strip(),
            "state": d.get("state", "") or "",
            "created_at": d.get("created_at", "") or "",
            "days_since_signup": _days_since(d.get("created_at", ""), now),
            "tier": tier,
            "signals": "; ".join(signals),
        })

    def _sort_key(r):
        ds = r["days_since_signup"]
        return (TIER_RANK.get(r["tier"], 9), ds if isinstance(ds, int) else 10 ** 9)

    rows.sort(key=_sort_key)
    return rows


def tier_counts(rows):
    counts = {}
    for r in rows:
        counts[r["tier"]] = counts.get(r["tier"], 0) + 1
    return counts


# --------------------------------------------------------------------------
# Kit V4 API (network)
# --------------------------------------------------------------------------
def _session(api_key):
    s = requests.Session()
    s.headers.update({"X-Kit-Api-Key": api_key, "Accept": "application/json"})
    return s


def _get(session, path, params=None):
    """GET with one 429 backoff retry (Kit allows 120 req / 60s)."""
    url = KIT_BASE + path
    for attempt in range(2):
        r = session.get(url, params=params, timeout=30)
        if r.status_code == 429 and attempt == 0:
            time.sleep(60)
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()


def _paginate(session, path, key, params=None):
    """Follow Kit V4 cursor pagination, collecting items under `key`."""
    params = dict(params or {})
    params.setdefault("per_page", 500)
    items = []
    while True:
        data = _get(session, path, params)
        items.extend(data.get(key, []))
        pg = data.get("pagination", {}) or {}
        if pg.get("has_next_page") and pg.get("end_cursor"):
            params["after"] = pg["end_cursor"]
            time.sleep(0.3)
        else:
            break
    return items


def _ingest(session, collection, item_path, signals_map, detail_map):
    """
    For each item in a collection (forms or tags), add its name to every
    subscriber's signal set and capture subscriber detail once.
    """
    for item in collection:
        item_id = item.get("id")
        name = item.get("name", "")
        if item_id is None:
            continue
        subs = _paginate(session, item_path.format(id=item_id), "subscribers")
        for sub in subs:
            email = sub.get("email_address") or ""
            if not email:
                continue
            key = email.lower()
            signals_map.setdefault(key, set()).add(name)
            detail_map.setdefault(key, {
                "email": email,
                "first_name": sub.get("first_name"),
                "state": sub.get("state"),
                "created_at": sub.get("created_at"),
            })


def fetch_signal_map(session):
    """
    Build {email_key: set(form/tag name)} and {email_key: detail} across all forms
    and tags. The combined signal set drives both cohort detection and tiering.
    """
    signals_map = {}
    detail_map = {}
    forms = _paginate(session, "/forms", "forms")
    tags = _paginate(session, "/tags", "tags")
    _ingest(session, forms, "/forms/{id}/subscribers", signals_map, detail_map)
    _ingest(session, tags, "/tags/{id}/subscribers", signals_map, detail_map)
    return signals_map, detail_map


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------
def _write_csv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _write_summary(rows, path):
    counts = tier_counts(rows)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Steel Warm-List — Summary",
        f"_Generated {now} from Kit (read-only). Counts only — no PII here._",
        "",
        f"**Total cohort (Steel form subscribers):** {len(rows)}",
        "",
        "| Tier | Count | Meaning |",
        "|------|-------|---------|",
        f"| customer | {counts.get('customer', 0)} | Tagged as a Field Manual buyer |",
        f"| hot | {counts.get('hot', 0)} | On the Field Manual waitlist/interest — wants the paid product |",
        f"| warm | {counts.get('warm', 0)} | Newsletter or topic-interest subscriber |",
        f"| lead | {counts.get('lead', 0)} | Has the Steel guide only — top of funnel |",
        "",
        "Signals = form memberships + tags. Full list (with emails): "
        f"`{CSV_PATH}` (gitignored).",
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _append_log(rows):
    os.makedirs("logs", exist_ok=True)
    log = {"runs": []}
    if os.path.exists(KIT_LOG):
        try:
            with open(KIT_LOG, "r", encoding="utf-8") as f:
                log = json.load(f)
        except Exception:
            pass
    log["runs"].append({
        "run_id": datetime.now().strftime("%Y-%m-%d_%H%M%S"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cohort_size": len(rows),
        "tier_counts": tier_counts(rows),  # counts only — no emails
        "output_file": CSV_PATH,
    })
    with open(KIT_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
def run_sync():
    api_key = os.getenv("KIT_API_KEY", "").strip()
    if not api_key:
        print("[KIT-SYNC] No KIT_API_KEY in .env. Add your Kit V4 key and re-run.")
        return

    print("[KIT-SYNC] Pulling forms + tags + subscribers from Kit (read-only)...")
    session = _session(api_key)
    try:
        signals_map, detail_map = fetch_signal_map(session)
    except requests.HTTPError as e:
        # Never surface the key; status only.
        print(f"[KIT-SYNC] Kit API error: {getattr(e.response, 'status_code', '?')} — "
              f"check the KIT_API_KEY (V4) and try again.")
        return
    except requests.RequestException as e:
        print(f"[KIT-SYNC] Network error reaching Kit: {e}")
        return

    cohort = [k for k, sig in signals_map.items() if has_steel(sig)]
    if not cohort:
        print("[KIT-SYNC] No subscribers found on a 'Steel' form. "
              "Confirm the Steel form name contains 'Steel' and has subscribers.")
        return

    rows = build_rows(cohort, detail_map, signals_map)
    _write_csv(rows, CSV_PATH)
    _write_summary(rows, SUMMARY_PATH)
    _append_log(rows)

    counts = tier_counts(rows)
    print(f"[KIT-SYNC] Warm-list written: {CSV_PATH}")
    print(f"[KIT-SYNC] Cohort: {len(rows)} | "
          f"customer {counts.get('customer', 0)}, hot {counts.get('hot', 0)}, "
          f"warm {counts.get('warm', 0)}, lead {counts.get('lead', 0)}")
    print(f"[KIT-SYNC] Summary: {SUMMARY_PATH}")
