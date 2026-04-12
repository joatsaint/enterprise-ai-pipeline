"""
CLI entry point for the YouTube transcript downloader.

Usage:
  python -m src.main <YouTube URL>              # single video
  python -m src.main channel "Name"             # incremental channel download
  python -m src.main channel "Name" --force-full
  python -m src.main group ai-and-claude-code   # all channels in a group
  python -m src.main add-channel                # register a new channel
  python -m src.main list-channels              # show registered channels
"""
import sys


def _print_help():
    print(__doc__)


def main():
    args = sys.argv[1:]

    if not args:
        _print_help()
        sys.exit(1)

    cmd = args[0]

    # ----------------------------------------------------------------
    # Single video URL (existing Phase 1 behaviour)
    # ----------------------------------------------------------------
    if cmd.startswith("http") or cmd.startswith("youtu"):
        from src.orchestrator import run
        run(cmd)
        return

    # ----------------------------------------------------------------
    # channel — batch download by channel name or URL
    # ----------------------------------------------------------------
    if cmd == "channel":
        if len(args) < 2:
            print("Usage: python -m src.main channel <name-or-url> [--force-full]")
            sys.exit(1)
        name = args[1]
        force_full = "--force-full" in args
        from src.downloader.channel import run_channel
        run_channel(name, force_full=force_full)
        return

    # ----------------------------------------------------------------
    # group — download all channels in a group
    # ----------------------------------------------------------------
    if cmd == "group":
        if len(args) < 2:
            print("Usage: python -m src.main group <group-name> [--force-full]")
            sys.exit(1)
        force_full = "--force-full" in args
        from src.downloader.channel import run_group
        run_group(args[1], force_full=force_full)
        return

    # ----------------------------------------------------------------
    # add-channel — interactive channel registration
    # ----------------------------------------------------------------
    if cmd == "add-channel":
        from src.channels.registry import add_channel
        add_channel()
        return

    # ----------------------------------------------------------------
    # list-channels — show registered channels
    # ----------------------------------------------------------------
    if cmd == "list-channels":
        from src.channels.registry import list_channels
        list_channels()
        return

    print(f"Unknown command: '{cmd}'")
    _print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
