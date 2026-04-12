"""
Channel registry — loads and manages channels.json.
"""
import json
import os


CHANNELS_FILE = "channels.json"

_DEFAULT = {
    "channels": [],
    "groups": [
        "ai-and-claude-code",
        "bitcoin-and-economic-news",
    ],
    "display_names": {
        "ai-and-claude-code": "AI & Claude Code",
        "bitcoin-and-economic-news": "Bitcoin and Economic News",
    },
    "notes": "Add channels here. Each entry needs name, url, group, active fields.",
}


def load_channels():
    """Return parsed channels.json, or default structure if file is missing."""
    if not os.path.exists(CHANNELS_FILE):
        return dict(_DEFAULT)
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_channels(data):
    with open(CHANNELS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_channel(name_or_url):
    """Return channel dict matching name (case-insensitive) or URL, or None."""
    data = load_channels()
    for ch in data.get("channels", []):
        if ch["name"].lower() == name_or_url.lower() or ch["url"] == name_or_url:
            return ch
    return None


def channels_in_group(group_name):
    """Return list of active channel dicts in a given group."""
    data = load_channels()
    return [
        ch for ch in data.get("channels", [])
        if ch.get("group") == group_name and ch.get("active", True)
    ]


# ---------------------------------------------------------------------------
# Interactive commands
# ---------------------------------------------------------------------------

def add_channel():
    """Interactively add a new channel to channels.json."""
    data = load_channels()
    groups = data.get("groups", [])

    name = input("Channel display name: ").strip()
    if not name:
        print("[ERROR] Name cannot be empty.")
        return

    url = input("Channel URL: ").strip()
    if not url:
        print("[ERROR] URL cannot be empty.")
        return

    if groups:
        print("Available groups:")
        for i, g in enumerate(groups, 1):
            print(f"  {i} — {g}")
        choice = input("Group number (or type name): ").strip()
        try:
            group = groups[int(choice) - 1]
        except (ValueError, IndexError):
            group = choice
    else:
        group = input("Group name: ").strip()

    active_input = input("Active? (Y/n): ").strip().lower()
    active = active_input != "n"

    data["channels"].append({
        "name": name,
        "url": url,
        "group": group,
        "active": active,
        "notes": "",
    })
    save_channels(data)
    print(f"[OK] Added '{name}' to group '{group}'.")


def list_channels():
    """Print all registered channels."""
    data = load_channels()
    channels = data.get("channels", [])
    if not channels:
        print("No channels registered. Use 'add-channel' to add one.")
        return

    print(f"\n{'Name':<30} {'Group':<28} {'Active'}")
    print("-" * 65)
    for ch in channels:
        active_str = "yes" if ch.get("active", True) else "no"
        print(f"{ch['name']:<30} {ch.get('group',''):<28} {active_str}")
    print()
