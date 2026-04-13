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

    max_videos_input = input(
        "Max videos to download (leave blank to use default from .env): "
    ).strip()
    max_videos = int(max_videos_input) if max_videos_input.isdigit() else None

    entry = {
        "name": name,
        "url": url,
        "group": group,
        "active": active,
        "notes": "",
    }
    if max_videos is not None:
        entry["max_videos"] = max_videos

    data["channels"].append(entry)
    save_channels(data)
    print(f"[OK] Added '{name}' to group '{group}'.")


def list_channels():
    """Print all registered channels with max_videos status."""
    data = load_channels()
    channels = data.get("channels", [])
    default_max = int(os.getenv("MAX_VIDEOS_DEFAULT", "20"))

    if not channels:
        print("No channels registered. Use 'add-channel' to add one.")
        return

    for i, ch in enumerate(channels, 1):
        active_str = "yes" if ch.get("active", True) else "no"
        if "max_videos" in ch:
            max_str = f"{ch['max_videos']} (custom)"
        else:
            max_str = f"{default_max} (default)"

        print(f"[{i}] {ch['name']}")
        print(f"    URL: {ch.get('url', '')}")
        print(f"    Group: {ch.get('group', '')}")
        print(f"    Max videos: {max_str}")
        print(f"    Active: {active_str}")
        print()
