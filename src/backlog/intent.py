"""
Planning Intent Classification — Phase 2 design, Section 1.

Tier 1 only (deliberate scope cut, see PHASE_2_DESIGN.md Section 1): a broad,
over-inclusive keyword/pattern net, not a semantic model. Biased hard toward
"planning" and "uncertain" over "non_planning" — a false positive costs one
cheap local verification run; a false negative reintroduces the exact
failure this whole system exists to prevent (Decision Sign-Off, Verification
Trigger Architecture ruling: "false positives acceptable, false negatives
are not").

classify() never raises and never returns anything but one of the three
literal strings below — a classifier that can crash or return something
unexpected is itself a silent-failure risk in the calling hook.
"""
import re

PLANNING = "planning"
NON_PLANNING = "non_planning"
UNCERTAIN = "uncertain"

# Broad net, deliberately over-inclusive. Word stems, not exact phrases.
_PLANNING_PATTERNS = [
    r"\bnext\b",
    r"\bpriorit\w*",
    r"\bblock\w*",
    r"\bbacklog\w*",
    r"what should i",
    r"\bforgetting\b",
    r"\bworking on\b",
    r"\bfocus\w*",
    r"\bstatus\b",
    r"where are we",
    r"\btodo\b",
    r"\bpending\b",
    r"\boverdue\b",
    r"what'?s left",
    r"\bstuck\b",
    r"\bre-?prioritiz\w*",
    r"\bwhat.{0,15}do (next|now)\b",
]

# Confident, specific "this is definitely not planning" patterns only.
# Never used as the default — see UNCERTAIN below.
_NON_PLANNING_PATTERNS = [
    r"traceback \(most recent call last\)",
    r"^\s*(rewrite|translate|summarize|proofread|reword)\b",
    r"\bsyntax error\b",
    r"\bstack trace\b",
    r"^\s*(fix|debug) this (code|error|bug)\b",
]

_planning_re = re.compile("|".join(_PLANNING_PATTERNS), re.IGNORECASE)
_non_planning_re = re.compile("|".join(_NON_PLANNING_PATTERNS), re.IGNORECASE)


def classify(text: str) -> str:
    """Classify a message as PLANNING, NON_PLANNING, or UNCERTAIN.

    UNCERTAIN is treated identically to PLANNING by callers (fail-safe rule)
    — it exists so nothing unmatched silently defaults to NON_PLANNING.
    Never raises: empty/garbled/non-string input safely falls to UNCERTAIN.
    """
    try:
        if not text or not isinstance(text, str) or not text.strip():
            return UNCERTAIN

        if _planning_re.search(text):
            return PLANNING

        if _non_planning_re.search(text):
            return NON_PLANNING

        return UNCERTAIN
    except Exception:
        # A classifier that can crash the caller is itself a silent-failure
        # risk (Section 3 of the design doc) — fail safe, never fail loud here.
        return UNCERTAIN


def requires_verification(text: str) -> bool:
    """True for PLANNING and UNCERTAIN — the actual gate callers use."""
    return classify(text) in (PLANNING, UNCERTAIN)
