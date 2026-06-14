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
  python -m src.main ask "your question"        # Q&A against knowledge base (Sonnet)
  python -m src.main ask --fast "your question" # Q&A with Haiku (faster, cheaper)
  python -m src.main ask --group <name> "q"    # Q&A limited to a group
  python -m src.main skool-download --community <slug> --group <name> [--limit N]
  python -m src.main skool-archive --community <slug> [--resolution 1080] [--course "Name"] [--limit N]  # full offline course archive
  python -m src.main schedule-post --post N --date "YYYY-MM-DD HH:MM"  # schedule LinkedIn post via Buffer
  python -m src.main schedule-post --post N --date "YYYY-MM-DD HH:MM" --dry-run
  python -m src.main trending                   # find a trending topic, draft a post to content-engine/pending/
  python -m src.main trending --dry-run         # gather + score only, write nothing
  python -m src.main refresh-comments [--days N] [--limit N]  # re-fetch comments on videos older than N days (default 7)
  python -m src.main curate-newsletters --discover [--days N]  # list inbox senders to build newsletter_sources.json
  python -m src.main curate-newsletters [--days N] [--force]   # curate AI newsletters into content-engine/newsletter_curation/
  python -m src.main curate-newsletters --scheduled             # silent mode for Task Scheduler
"""
import sys

# Force UTF-8 on Windows consoles so emoji in channel names / titles don't crash prints
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()


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
    # analyze-buildroom — Phase B catalog pass over the Build Room corpus
    # ----------------------------------------------------------------
    if cmd == "analyze-buildroom":
        from src.analyzer.buildroom_analyzer import run_catalog
        limit = None
        force = "--force" in args
        if "--limit" in args:
            idx = args.index("--limit")
            if idx + 1 >= len(args):
                print("Usage: python -m src.main analyze-buildroom [--limit N] [--force]")
                sys.exit(1)
            limit = int(args[idx + 1])
        run_catalog(limit=limit, force=force)
        return

    # ----------------------------------------------------------------
    # kit-sync — pull Steel lead-magnet cohort from Kit into a tiered warm-list
    # ----------------------------------------------------------------
    if cmd == "kit-sync":
        from src.funnel.kit_sync import run_sync
        run_sync()
        return

    # ----------------------------------------------------------------
    # status — one read-only at-a-glance summary of the whole pipeline
    # ----------------------------------------------------------------
    if cmd == "status":
        from src.status import run_status
        run_status()
        return

    # ----------------------------------------------------------------
    # digest — generate daily content digest
    # ----------------------------------------------------------------
    if cmd == "digest":
        from src.knowledge_base.digest import run_digest
        group = None
        date_filter = None
        since_filter = None
        force = "--force" in args
        scheduled = "--scheduled" in args
        remaining = args[1:]
        if "--group" in remaining:
            idx = remaining.index("--group")
            if idx + 1 >= len(remaining):
                print("Usage: python -m src.main digest [--group <name>] [--date YYYY-MM-DD] [--since YYYY-MM-DD] [--force] [--scheduled]")
                sys.exit(1)
            group = remaining[idx + 1]
        if "--date" in remaining:
            idx = remaining.index("--date")
            if idx + 1 >= len(remaining):
                print("Usage: python -m src.main digest [--date YYYY-MM-DD]")
                sys.exit(1)
            date_filter = remaining[idx + 1]
        if "--since" in remaining:
            idx = remaining.index("--since")
            if idx + 1 >= len(remaining):
                print("Usage: python -m src.main digest [--since YYYY-MM-DD]")
                sys.exit(1)
            since_filter = remaining[idx + 1]
        run_digest(
            group_filter=group,
            date_filter=date_filter,
            since_filter=since_filter,
            force=force,
            scheduled=scheduled,
        )
        return

    # ----------------------------------------------------------------
    # ask — Q&A against knowledge base
    # ----------------------------------------------------------------
    if cmd == "ask":
        from src.knowledge_base.query import run_query
        group = None
        top_n = 10
        fast = False
        remaining = args[1:]
        if "--group" in remaining:
            idx = remaining.index("--group")
            if idx + 1 >= len(remaining):
                print("Usage: python -m src.main ask [--group <name>] [--top N] [--fast] \"question\"")
                sys.exit(1)
            group = remaining[idx + 1]
            remaining = [a for j, a in enumerate(remaining) if j != idx and j != idx + 1]
        if "--top" in remaining:
            idx = remaining.index("--top")
            if idx + 1 >= len(remaining):
                print("Usage: python -m src.main ask [--group <name>] [--top N] [--fast] \"question\"")
                sys.exit(1)
            try:
                top_n = int(remaining[idx + 1])
            except ValueError:
                print(f"--top requires an integer, got: {remaining[idx + 1]}")
                sys.exit(1)
            remaining = [a for j, a in enumerate(remaining) if j != idx and j != idx + 1]
        if "--fast" in remaining:
            fast = True
            remaining = [a for a in remaining if a != "--fast"]
        if not remaining:
            print("Usage: python -m src.main ask [--group <name>] [--top N] [--fast] \"your question\"")
            sys.exit(1)
        question = " ".join(remaining)
        run_query(question, group=group, top_n=top_n, fast=fast)
        return

    # ----------------------------------------------------------------
    # skool-download — download videos from a Skool community classroom
    # ----------------------------------------------------------------
    if cmd == "skool-download":
        community = None
        group = None
        limit = None
        if "--community" in args:
            idx = args.index("--community")
            if idx + 1 < len(args):
                community = args[idx + 1]
        if "--group" in args:
            idx = args.index("--group")
            if idx + 1 < len(args):
                group = args[idx + 1]
        if "--limit" in args:
            idx = args.index("--limit")
            if idx + 1 < len(args):
                try:
                    limit = int(args[idx + 1])
                except ValueError:
                    print(f"--limit requires an integer, got: {args[idx + 1]}")
                    sys.exit(1)
        if not community or not group:
            print('Usage: python -m src.main skool-download --community <slug> --group "Group Name" [--limit N]')
            sys.exit(1)
        from src.downloader.skool import run_skool_download
        run_skool_download(community, group, limit=limit)
        return

    # ----------------------------------------------------------------
    # skool-archive — full offline archive of a Skool community course
    # ----------------------------------------------------------------
    if cmd == "skool-archive":
        community = None
        resolution = 1080
        course_filter = None
        limit = None
        if "--community" in args:
            idx = args.index("--community")
            if idx + 1 < len(args):
                community = args[idx + 1]
        if "--resolution" in args:
            idx = args.index("--resolution")
            if idx + 1 < len(args):
                try:
                    resolution = int(args[idx + 1])
                except ValueError:
                    print(f"--resolution requires an integer, got: {args[idx + 1]}")
                    sys.exit(1)
        if "--course" in args:
            idx = args.index("--course")
            if idx + 1 < len(args):
                course_filter = args[idx + 1]
        if "--limit" in args:
            idx = args.index("--limit")
            if idx + 1 < len(args):
                try:
                    limit = int(args[idx + 1])
                except ValueError:
                    print(f"--limit requires an integer, got: {args[idx + 1]}")
                    sys.exit(1)
        if not community:
            print('Usage: python -m src.main skool-archive --community <slug> '
                  '[--resolution 1080] [--course "Name"] [--limit N]')
            sys.exit(1)
        community_only = "--community-only" in args
        author_filter = None
        if "--author" in args:
            idx = args.index("--author")
            if idx + 1 < len(args):
                author_filter = args[idx + 1]
        from src.downloader.skool_archiver import run_skool_archive
        run_skool_archive(community, resolution=resolution, limit=limit,
                          course_filter=course_filter, community_only=community_only,
                          author_filter=author_filter)
        return

    # ----------------------------------------------------------------
    # schedule-post — schedule a LinkedIn post via Buffer
    # ----------------------------------------------------------------
    if cmd == "schedule-post":
        post_num = None
        date_str = None
        dry_run = "--dry-run" in args
        if "--post" in args:
            idx = args.index("--post")
            if idx + 1 < len(args):
                try:
                    post_num = int(args[idx + 1])
                except ValueError:
                    print(f"--post requires an integer, got: {args[idx + 1]}")
                    sys.exit(1)
        if "--date" in args:
            idx = args.index("--date")
            if idx + 1 < len(args):
                date_str = args[idx + 1]
        if post_num is None or not date_str:
            print('Usage: python -m src.main schedule-post --post N --date "YYYY-MM-DD HH:MM" [--dry-run]')
            sys.exit(1)
        from src.publisher.schedule import run_schedule_post
        run_schedule_post(post_num, date_str, dry_run=dry_run)
        return

    # ----------------------------------------------------------------
    # refresh-comments — re-fetch comments for videos older than N days
    # ----------------------------------------------------------------
    if cmd == "refresh-comments":
        days = 7
        limit = None
        if "--days" in args:
            idx = args.index("--days")
            if idx + 1 >= len(args):
                print("Usage: python -m src.main refresh-comments [--days N] [--limit N]")
                sys.exit(1)
            try:
                days = int(args[idx + 1])
            except ValueError:
                print(f"--days requires an integer, got: {args[idx + 1]}")
                sys.exit(1)
        if "--limit" in args:
            idx = args.index("--limit")
            if idx + 1 >= len(args):
                print("Usage: python -m src.main refresh-comments [--days N] [--limit N]")
                sys.exit(1)
            try:
                limit = int(args[idx + 1])
            except ValueError:
                print(f"--limit requires an integer, got: {args[idx + 1]}")
                sys.exit(1)
        from src.downloader.comment_refresher import refresh_old_comments
        refresh_old_comments(days=days, limit=limit)
        return

    # ----------------------------------------------------------------
    # curate-newsletters — discover/curate AI newsletters from Hotmail inbox
    # ----------------------------------------------------------------
    if cmd == "curate-newsletters":
        discover = "--discover" in args
        force = "--force" in args
        scheduled = "--scheduled" in args
        days = 7
        if "--days" in args:
            idx = args.index("--days")
            if idx + 1 >= len(args):
                print("Usage: python -m src.main curate-newsletters [--discover] [--days N] [--force] [--scheduled]")
                sys.exit(1)
            try:
                days = int(args[idx + 1])
            except ValueError:
                print(f"--days requires an integer, got: {args[idx + 1]}")
                sys.exit(1)
        from src.curator.newsletter_curator import run_curate_newsletters
        run_curate_newsletters(discover=discover, days=days, force=force, scheduled=scheduled)
        return

    # ----------------------------------------------------------------
    # trending — find a trending topic, draft a post to content-engine/pending/
    # ----------------------------------------------------------------
    if cmd == "trending":
        dry_run = "--dry-run" in args
        from src.trend_finder.orchestrator import run as run_trending
        run_trending(dry_run=dry_run)
        return

    print(f"Unknown command: '{cmd}'")
    _print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
