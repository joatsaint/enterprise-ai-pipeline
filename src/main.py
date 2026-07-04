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
  python -m src.main loop                        # unified cycle: research -> draft -> review gate (status readout, no publish)
  python -m src.main loop --dry-run              # run the cycle without writing a draft
  python -m src.main shadow-score <slug>         # autonomy L1: predict+log a ship/fix/kill verdict for a pending asset
  python -m src.main shadow-verdict <slug> ship|fix|kill [--note "..."]  # record your real call
  python -m src.main shadow-report               # AI-vs-Randy agreement scorecard
  python -m src.main status                      # at-a-glance pipeline summary
  python -m src.main report [--days N]           # weekly AI cost report
  python -m src.main refresh-comments [--days N] [--limit N]  # re-fetch comments on videos older than N days (default 7)
  python -m src.main curate-newsletters --discover [--days N]  # list inbox senders to build newsletter_sources.json
  python -m src.main curate-newsletters [--days N] [--force]   # curate AI newsletters into content-engine/newsletter_curation/
  python -m src.main curate-newsletters --scheduled             # silent mode for Task Scheduler
  python -m src.main audience-radar [--dry-run] [--top N]       # Daily Audience Radar: find conversations, draft comments
  python -m src.main radar-status <rank> approve|edit|skip|posted|needs_reply [--note "..."] [--date YYYY-MM-DD]

  # YouTube Shorts pipeline
  python -m src.main shorts [--pain-point "..."] [--variant a|b|both] [--dry-run]

  # Web page link downloader (Playwright — clicks Markdown button, saves file)
  python -m src.main fetch-links --scan-dir <path> --domain <domain> --output-dir <path>
  # Example:
  #   python -m src.main fetch-links \\
  #       --scan-dir transcripts/ai-job-intelligence/nate-b-jones \\
  #       --domain promptkit.natebjones.com \\
  #       --output-dir transcripts/ai-job-intelligence/nate-b-jones-guides
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
    # report — weekly AI cost report from the ledger
    # ----------------------------------------------------------------
    if cmd == "report":
        from src.report import run_report
        days = 7
        if "--days" in args:
            idx = args.index("--days")
            if idx + 1 >= len(args):
                print("Usage: python -m src.main report [--days N]")
                sys.exit(1)
            days = int(args[idx + 1])
        run_report(days=days)
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

    # ----------------------------------------------------------------
    # spiceworks-hangouts — mine Spiceworks for where the ICP hangs out
    # ----------------------------------------------------------------
    if cmd == "spiceworks-hangouts":
        from src.trend_finder.icp_hangouts import run_hangouts
        per_tag = 12
        if "--per-tag" in args:
            idx = args.index("--per-tag")
            if idx + 1 >= len(args):
                print("Usage: python -m src.main spiceworks-hangouts [--per-tag N]")
                sys.exit(1)
            per_tag = int(args[idx + 1])
        run_hangouts(per_tag=per_tag)
        return

    # ----------------------------------------------------------------
    # loop — unified content cycle: research -> draft -> review gate (no publish)
    # ----------------------------------------------------------------
    if cmd == "loop":
        dry_run = "--dry-run" in args
        from src.loop import run_loop
        run_loop(dry_run=dry_run)
        return

    # ----------------------------------------------------------------
    # shadow-score — autonomy L1: predict + log a verdict for a pending asset
    # ----------------------------------------------------------------
    if cmd == "shadow-score":
        if len(args) < 2:
            print("Usage: python -m src.main shadow-score <slug> [content_type]")
            sys.exit(1)
        content_type = args[2] if len(args) > 2 and not args[2].startswith("-") else None
        from src.autonomy.shadow import run_shadow_score
        run_shadow_score(args[1], content_type=content_type)
        return

    # ----------------------------------------------------------------
    # shadow-verdict — autonomy L1: record Randy's real ship/fix/kill call
    # ----------------------------------------------------------------
    if cmd == "shadow-verdict":
        if len(args) < 3:
            print('Usage: python -m src.main shadow-verdict <slug> ship|fix|kill [--type T] [--note "..."]')
            sys.exit(1)
        slug, verdict = args[1], args[2]
        note = ""
        content_type = None
        if "--note" in args:
            idx = args.index("--note")
            if idx + 1 < len(args):
                note = args[idx + 1]
        if "--type" in args:
            idx = args.index("--type")
            if idx + 1 < len(args):
                content_type = args[idx + 1]
        from src.autonomy.shadow import run_shadow_verdict
        run_shadow_verdict(slug, verdict, note=note, content_type=content_type)
        return

    # ----------------------------------------------------------------
    # shadow-report — autonomy L1: AI-vs-Randy agreement scorecard
    # ----------------------------------------------------------------
    if cmd == "shadow-report":
        from src.autonomy.shadow import run_shadow_report
        run_shadow_report()
        return

    # ----------------------------------------------------------------
    # audience-radar — Daily Audience Radar v1: find conversations, draft comments
    # ----------------------------------------------------------------
    if cmd == "audience-radar":
        dry_run = "--dry-run" in args
        top_n = 10
        if "--top" in args:
            idx = args.index("--top")
            if idx + 1 >= len(args):
                print("Usage: python -m src.main audience-radar [--dry-run] [--top N]")
                sys.exit(1)
            top_n = int(args[idx + 1])
        from src.radar.daily_radar import run as run_radar
        run_radar(dry_run=dry_run, top_n=top_n)
        return

    # ----------------------------------------------------------------
    # radar-status — record Randy's approval-gate call on a radar item
    # ----------------------------------------------------------------
    if cmd == "radar-status":
        if len(args) < 3:
            print('Usage: python -m src.main radar-status <rank> approve|edit|skip|posted|needs_reply [--note "..."] [--date YYYY-MM-DD]')
            sys.exit(1)
        rank, status = args[1], args[2]
        note = ""
        date_str = None
        if "--note" in args:
            idx = args.index("--note")
            if idx + 1 < len(args):
                note = args[idx + 1]
        if "--date" in args:
            idx = args.index("--date")
            if idx + 1 < len(args):
                date_str = args[idx + 1]
        from src.radar.daily_radar import set_status
        try:
            set_status(rank, status, note=note, date_str=date_str)
        except (ValueError, FileNotFoundError) as e:
            print(f"Error: {e}")
            sys.exit(1)
        return

    # ----------------------------------------------------------------
    # shorts — YouTube Shorts pipeline
    # ----------------------------------------------------------------
    if cmd == "shorts":
        pain_point = None
        variant = "both"
        dry_run = "--dry-run" in args
        if "--pain-point" in args:
            idx = args.index("--pain-point")
            if idx + 1 >= len(args):
                print('Usage: python -m src.main shorts [--pain-point "..."] [--variant a|b|both] [--dry-run]')
                sys.exit(1)
            pain_point = args[idx + 1]
        if "--variant" in args:
            idx = args.index("--variant")
            if idx + 1 >= len(args):
                print('Usage: python -m src.main shorts [--variant a|b|both]')
                sys.exit(1)
            variant = args[idx + 1]
            if variant not in ("a", "b", "both"):
                print(f"--variant must be a, b, or both. Got: {variant}")
                sys.exit(1)
        from src.shorts.orchestrator import run as run_shorts
        run_shorts(manual_pain_point=pain_point, variant=variant, dry_run=dry_run)
        return

    # ----------------------------------------------------------------
    # fetch-links — scan transcripts for ## LINK: URLs, download via Playwright
    # ----------------------------------------------------------------
    if cmd == "fetch-links":
        scan_dir = None
        domain = None
        output_dir = None
        channel_name = ""
        if "--scan-dir" in args:
            idx = args.index("--scan-dir")
            if idx + 1 < len(args):
                scan_dir = args[idx + 1]
        if "--domain" in args:
            idx = args.index("--domain")
            if idx + 1 < len(args):
                domain = args[idx + 1]
        if "--output-dir" in args:
            idx = args.index("--output-dir")
            if idx + 1 < len(args):
                output_dir = args[idx + 1]
        if "--channel-name" in args:
            idx = args.index("--channel-name")
            if idx + 1 < len(args):
                channel_name = args[idx + 1]
        if not scan_dir or not domain or not output_dir:
            print(
                "Usage: python -m src.main fetch-links "
                "--scan-dir <path> --domain <domain> --output-dir <path> "
                "[--channel-name <name>]"
            )
            sys.exit(1)
        from src.downloader.web_page import run_fetch_links
        run_fetch_links(
            scan_dir=scan_dir, domain=domain,
            output_dir=output_dir, channel_name=channel_name,
        )
        return

    print(f"Unknown command: '{cmd}'")
    _print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
