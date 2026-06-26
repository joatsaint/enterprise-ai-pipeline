"""
Selects the freshest, highest-scoring sysadmin-relevant pain point from the
Daily Audience Radar state, or accepts a manual override via --pain-point.

Returns:
    {
        "title": str,
        "url": str | None,
        "why_it_matters": str,
        "source": str,
        "priority_score": float,
        "pain_summary": str,   # condensed description for script writer
    }
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RADAR_STATE = ROOT / "content-engine" / "daily_radar" / "radar_state.json"

SYSADMIN_KEYWORDS = [
    "sysadmin", "sys admin", "system admin", "it admin", "network admin",
    "helpdesk", "help desk", "it support", "infrastructure", "server",
    "firewall", "zero trust", "patch", "active directory", "azure ad",
    "powershell", "linux", "windows server", "vmware", "hyper-v",
    "kubernetes", "docker", "cloud", "aws", "azure", "gcp",
    "security", "compliance", "endpoint", "monitoring", "ticketing",
    "servicenow", "jira", "ai replace", "automation", "layoff", "job",
    "career", "certification", "cissp", "azure cert", "it pro",
    "burnout", "on call", "oncall", "weekend", "legacy", "tech debt",
    "vendor", "budget", "management", "director",
]


def _is_sysadmin_relevant(item: dict) -> bool:
    text = " ".join([
        item.get("title", ""),
        item.get("why_it_matters", ""),
        item.get("source", ""),
    ]).lower()
    return any(kw in text for kw in SYSADMIN_KEYWORDS)


def _load_radar_state() -> dict:
    if not RADAR_STATE.exists():
        return {}
    try:
        return json.loads(RADAR_STATE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def select(manual_override: str | None = None) -> dict:
    """
    Return the best available pain point.

    If manual_override is set, wraps it in a minimal dict and returns it.
    Otherwise reads the most recent radar state and picks the highest-scoring
    sysadmin-relevant item that hasn't been marked 'skip' or 'posted'.
    """
    if manual_override:
        return {
            "title": manual_override,
            "url": None,
            "why_it_matters": manual_override,
            "source": "manual",
            "priority_score": 10.0,
            "pain_summary": manual_override,
        }

    state = _load_radar_state()
    if not state:
        raise FileNotFoundError(
            "No radar state found at content-engine/daily_radar/radar_state.json. "
            "Run `python -m src.main audience-radar` first, or pass --pain-point."
        )

    # Get the most recent date's items
    latest_date = sorted(state.keys())[-1]
    items = state[latest_date].get("items", [])
    if not items:
        raise ValueError(f"Radar state for {latest_date} has no items. Re-run audience-radar.")

    # Filter: sysadmin-relevant AND not skipped/posted
    blocked = {"skip", "posted"}
    candidates = [
        i for i in items
        if i.get("status", "not_reviewed") not in blocked
        and _is_sysadmin_relevant(i)
    ]

    # Fall back to all non-blocked items if nothing matches keywords
    if not candidates:
        candidates = [i for i in items if i.get("status", "not_reviewed") not in blocked]

    if not candidates:
        raise ValueError(
            f"All {latest_date} radar items are already skipped/posted. "
            "Run audience-radar again or pass --pain-point."
        )

    # Highest priority_score wins
    best = max(candidates, key=lambda i: float(i.get("priority_score", 0)))

    pain_summary = best.get("why_it_matters") or best.get("title") or ""

    return {
        "title": best.get("title", ""),
        "url": best.get("url"),
        "why_it_matters": best.get("why_it_matters", ""),
        "source": best.get("source", ""),
        "priority_score": float(best.get("priority_score", 0)),
        "pain_summary": pain_summary,
    }
