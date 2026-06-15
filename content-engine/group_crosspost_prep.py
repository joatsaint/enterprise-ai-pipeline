"""
group_crosspost_prep.py — Zero-footprint LinkedIn group cross-post prep sheet.

Removes the tedious part of cross-posting an article to your LinkedIn groups:
deciding and writing a hook for each one. Does NOT touch LinkedIn at all (no
browser, no automation, no ban risk) — it just produces a ready-to-paste sheet.

Workflow this supports (your actual flow):
  1. You open a group -> "Create a new post"
  2. Paste the ARTICLE LINK in the body (LinkedIn pulls the card: hero + title)
  3. Paste the HOOK from this sheet into the text field ABOVE the link
  4. Click Post
This sheet hands you a different hook per group (so no two look identical =
not a spam pattern) plus the link, with a checkbox to track what's done.

Usage:
    python content-engine/group_crosspost_prep.py ^
        --url "https://www.linkedin.com/pulse/your-article-url" ^
        --title "From Burned Out to Fired UP!"

Optional:
    --groups content-engine/linkedin_groups.json   (default)
    --hooks  content-engine/group_post_hooks.md     (default; reads "> " lines)
    --slug   burned-out                             (filename slug; else from title)

Stdlib only.
"""

import argparse
import datetime as dt
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_GROUPS = ROOT / "linkedin_groups.json"
DEFAULT_HOOKS = ROOT / "group_post_hooks.md"
OUT_DIR = ROOT / "crosspost_sheets"

TIER_ORDER = {"A": 0, "B": 1, "C": 2}


def load_hooks(path: Path) -> list[str]:
    """Extract hooks from a markdown file: every blockquote ('> ...') line."""
    if not path.exists():
        sys.exit(f"Hooks file not found: {path}")
    hooks = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r">\s+(.*\S)", line)
        if m:
            hooks.append(m.group(1).strip())
    if not hooks:
        sys.exit(f"No hooks found in {path} (expected lines starting with '> ').")
    return hooks


def load_groups(path: Path) -> list[dict]:
    if not path.exists():
        sys.exit(f"Groups file not found: {path}\n"
                 f"Copy linkedin_groups.example.json to linkedin_groups.json "
                 f"(local-only) and fill in your group names.")
    data = json.loads(path.read_text(encoding="utf-8"))
    groups = [g for g in data.get("groups", []) if g.get("active", True)]
    if not groups:
        sys.exit(f"No active groups in {path}.")
    groups.sort(key=lambda g: (TIER_ORDER.get(g.get("tier", "B"), 1), g["name"].lower()))
    return groups


def slugify(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")[:40]


def build_sheet(url: str, title: str, groups: list[dict], hooks: list[str]) -> str:
    random.shuffle(hooks)  # vary the rotation per run / per article
    today = dt.date.today().isoformat()
    lines = [
        f"# Group Cross-Post Sheet — {title}",
        f"**Article link:** {url}",
        f"**Generated:** {dt.datetime.now():%Y-%m-%d %H:%M}  |  **Groups:** {len(groups)}",
        "",
        "**How to use each block:** open the group → Create a new post → paste the "
        "**link** in the body (LinkedIn pulls the card) → paste the **hook** in the "
        "text field above it → Post. Tick the box when done.",
        "",
        "**Pacing (safety + engagement):** these use LinkedIn's native posting, so "
        "ban risk is low — but spread them across the week, not all 20 at once. "
        "A-tier groups first; some posts may sit in moderation depending on the admin.",
        "",
        "---",
        "",
    ]
    current_tier = None
    for i, g in enumerate(groups):
        tier = g.get("tier", "B")
        if tier != current_tier:
            current_tier = tier
            label = {"A": "A-tier — proven engagers",
                     "B": "B-tier — testing / unproven",
                     "C": "C-tier — low engagement"}.get(tier, f"{tier}-tier")
            lines += [f"## {label}", ""]
        hook = hooks[i % len(hooks)]
        note = g.get("notes", "")
        lines += [
            f"### [ ] {g['name']}" + (f"  _( {note} )_" if note else ""),
            "",
            "**Hook (paste above the link):**",
            "",
            f"> {hook}",
            "",
            "**Link (paste in the post body):**",
            "",
            f"{url}",
            "",
            "---",
            "",
        ]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate a LinkedIn group cross-post prep sheet.")
    ap.add_argument("--url", required=True, help="Published article URL")
    ap.add_argument("--title", required=True, help="Article title (for the sheet header)")
    ap.add_argument("--groups", default=str(DEFAULT_GROUPS))
    ap.add_argument("--hooks", default=str(DEFAULT_HOOKS))
    ap.add_argument("--slug", default=None)
    args = ap.parse_args()

    groups = load_groups(Path(args.groups))
    hooks = load_hooks(Path(args.hooks))
    sheet = build_sheet(args.url, args.title, groups, hooks)

    OUT_DIR.mkdir(exist_ok=True)
    slug = args.slug or slugify(args.title) or "article"
    out_path = OUT_DIR / f"{dt.date.today().isoformat()}_{slug}_crosspost.md"
    out_path.write_text(sheet, encoding="utf-8")
    print(f"Wrote: {out_path}")
    print(f"  {len(groups)} groups, {len(hooks)} hooks available (rotated).")
    print("  Open it, then post group-by-group using LinkedIn's native flow.")


if __name__ == "__main__":
    main()
