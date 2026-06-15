"""
Tests for src/trend_finder/icp_hangouts.py — ICP hangouts miner.

1. classify maps URLs to platform labels + extracts channel/subreddit/invite handles
2. aggregate buckets + ranks links (platforms by clicks, named yt/subs, other tail)
3. render_report includes the headline platform and handles missing data gracefully
"""
from src.trend_finder import icp_hangouts as h


def test_classify():
    assert h.classify("https://www.linkedin.com/in/randy")[0] == "LinkedIn"
    lab, dom, spec = h.classify("https://youtube.com/@4sysops/videos")
    assert lab == "YouTube" and spec == "@4sysops"
    lab, dom, spec = h.classify("https://reddit.com/r/sysadmin/comments/x")
    assert lab == "Reddit" and spec == "r/sysadmin"
    lab, dom, spec = h.classify("https://discord.gg/abc123")
    assert lab == "Discord" and spec == "discord.gg/abc123"
    # unknown -> no label, but domain returned for the long tail
    lab, dom, spec = h.classify("https://example.com/blog/post")
    assert lab is None and dom == "example.com"


def test_aggregate_ranks_and_buckets():
    rows = [
        {"url": "https://linkedin.com/in/a", "clicks": 40},
        {"url": "https://linkedin.com/in/b", "clicks": 5},
        {"url": "https://youtube.com/@4sysops", "clicks": 3},
        {"url": "https://reddit.com/r/sysadmin/x", "clicks": 2},
        {"url": "https://example.com/tool", "clicks": 1},
    ]
    agg = h.aggregate(rows)
    # LinkedIn leads platforms (45 clicks across 2 mentions)
    assert agg["platforms"][0][0] == "LinkedIn"
    assert agg["platforms"][0][1] == 2 and agg["platforms"][0][2] == 45
    assert ("@4sysops", 1) in agg["youtube"]
    assert ("r/sysadmin", 1) in agg["subreddits"]
    assert agg["other"][0][0] == "example.com"


def test_render_report():
    agg = h.aggregate([{"url": "https://linkedin.com/x", "clicks": 9}])
    text = h.render_report(agg, topics_scanned=10, per_tag=12, tags=["a", "b"])
    assert "ICP Verified Hangouts" in text
    assert "LinkedIn" in text
    assert "none surfaced yet" in text  # empty youtube/subreddit buckets render gracefully
