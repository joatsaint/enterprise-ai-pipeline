"""
CLI entry point for the YouTube transcript downloader.

Usage:
  python -m src.main <YouTube URL>              # single video
  python -m src.main channel "Name"             # incremental channel download
  python -m src.main channel "Name" --force-full
  python -m src.main group ai-and-claude-code   # all channels in a group
  python -m src.main add-channel                # register a new channel
  python -m src.main list-channels              # show registered channels
  python -m src.main index                      # build/rebuild knowledge base index
  python -m src.main analyze --group <name>     # run pain point analysis on a group
  python -m src.main analyze --all              # run pain point analysis on all groups
  python -m src.main ask "your question"        # Q&A against knowledge base
  python -m src.main ask --group <name> "q"    # Q&A limited to a group
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

    # ----------------------------------------------------------------
    # index — build/rebuild the knowledge base index
    # ----------------------------------------------------------------
    if cmd == "index":
        group = None
        verbose = "--verbose" in args
        if "--group" in args:
            idx = args.index("--group")
            if idx + 1 >= len(args):
                print("Usage: python -m src.main index [--group <name>] [--verbose]")
                sys.exit(1)
            group = args[idx + 1]
        from src.knowledge_base.indexer import build_index
        build_index(group_filter=group, verbose=verbose)
        return

    # ----------------------------------------------------------------
    # analyze — run pain point extraction
    # ----------------------------------------------------------------
    if cmd == "analyze":
        from src.analyzer.pain_point_extractor import run_extractor
        if "--all" in args:
            run_extractor(group=None)
        elif "--group" in args:
            idx = args.index("--group")
            if idx + 1 >= len(args):
                print("Usage: python -m src.main analyze --group <group-name>")
                sys.exit(1)
            run_extractor(group=args[idx + 1])
        else:
            print("Usage: python -m src.main analyze --group <name> | --all")
            sys.exit(1)
        return

    # ----------------------------------------------------------------
    # ask — Q&A against knowledge base
    # ----------------------------------------------------------------
    if cmd == "ask":
        from src.knowledge_base.query import run_query
        group = None
        top_n = 10
        remaining = args[1:]
        if "--group" in remaining:
            idx = remaining.index("--group")
            if idx + 1 >= len(remaining):
                print("Usage: python -m src.main ask [--group <name>] [--top N] \"question\"")
                sys.exit(1)
            group = remaining[idx + 1]
            remaining = [a for j, a in enumerate(remaining) if j != idx and j != idx + 1]
        if "--top" in remaining:
            idx = remaining.index("--top")
            if idx + 1 >= len(remaining):
                print("Usage: python -m src.main ask [--group <name>] [--top N] \"question\"")
                sys.exit(1)
            try:
                top_n = int(remaining[idx + 1])
            except ValueError:
                print(f"--top requires an integer, got: {remaining[idx + 1]}")
                sys.exit(1)
            remaining = [a for j, a in enumerate(remaining) if j != idx and j != idx + 1]
        if not remaining:
            print("Usage: python -m src.main ask [--group <name>] [--top N] \"your question\"")
            sys.exit(1)
        question = " ".join(remaining)
        run_query(question, group=group, top_n=top_n)
        return

    print(f"Unknown command: '{cmd}'")
    _print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
