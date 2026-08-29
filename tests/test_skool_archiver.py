"""Unit tests for the pure converters in skool_archiver (no browser / network)."""
from src.downloader.skool_archiver import richtext_to_markdown, parse_resources


# A real Build Room desc sample (truncated), in Skool's "[v2]" rich-text format.
SAMPLE = (
    '[v2]['
    '{"type":"paragraph","content":[{"type":"text","text":"Here\'s the deal: 7 days, 7 builds, zero fluff."}]},'
    '{"type":"unorderedList","content":['
    '{"type":"listItem","content":[{"type":"paragraph","content":[{"type":"text","text":"Days 1-3 are beginner-friendly"}]}]},'
    '{"type":"listItem","content":[{"type":"paragraph","content":[{"type":"text","text":"Days 4-5 ramp to intermediate"}]}]}'
    ']}'
    ']'
)


def test_richtext_paragraph_and_list():
    md = richtext_to_markdown(SAMPLE)
    assert "Here's the deal: 7 days, 7 builds, zero fluff." in md
    assert "- Days 1-3 are beginner-friendly" in md
    assert "- Days 4-5 ramp to intermediate" in md


def test_richtext_marks():
    desc = ('[v2][{"type":"paragraph","content":['
            '{"type":"text","text":"bold","marks":[{"type":"bold"}]},'
            '{"type":"text","text":" and "},'
            '{"type":"text","text":"link","marks":[{"type":"link","attrs":{"href":"https://x.com"}}]}'
            ']}]')
    md = richtext_to_markdown(desc)
    assert "**bold**" in md
    assert "[link](https://x.com)" in md


def test_richtext_empty_and_none():
    assert richtext_to_markdown("") == ""
    assert richtext_to_markdown(None) == ""


def test_richtext_malformed_falls_back_to_text():
    # Not valid JSON after the prefix -> fallback extracts text runs.
    md = richtext_to_markdown('[v2]{not valid json "text":"survivor"}')
    assert "survivor" in md


def test_parse_resources_empty():
    assert parse_resources("[]") == []
    assert parse_resources("") == []
    assert parse_resources(None) == []


def test_parse_resources_objects():
    res = parse_resources('[{"title":"Template","url":"https://skool.com/x"},'
                          '{"name":"Doc","link":"https://d.com/y"}]')
    assert res[0] == {"label": "Template", "url": "https://skool.com/x"}
    assert res[1] == {"label": "Doc", "url": "https://d.com/y"}
