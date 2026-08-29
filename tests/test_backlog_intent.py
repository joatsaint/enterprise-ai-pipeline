from src.backlog import intent


def test_clear_planning_phrases_classify_planning():
    for text in [
        "what's next?",
        "what should I work on today?",
        "any blockers right now?",
        "where are we with Jarvis?",
        "what's on the backlog?",
        "am I forgetting anything?",
        "what's the highest priority?",
        "is anything overdue?",
    ]:
        assert intent.classify(text) == intent.PLANNING, text


def test_confident_non_planning_classifies_non_planning():
    assert intent.classify("Traceback (most recent call last):\n  File x") == intent.NON_PLANNING
    assert intent.classify("rewrite this paragraph to be punchier") == intent.NON_PLANNING
    assert intent.classify("fix this code, it's throwing a syntax error") in (
        intent.NON_PLANNING,
        intent.PLANNING,  # "syntax error" pattern could co-match; either is safe here
    )


def test_ambiguous_and_novel_phrasing_defaults_uncertain_not_non_planning():
    for text in [
        "hey there",
        "can you look at this image for me",
        "asdkfj alksdjf laksjdf",
        "let's talk about the weather",
    ]:
        assert intent.classify(text) == intent.UNCERTAIN, text


def test_empty_and_non_string_input_never_crashes_and_is_uncertain():
    assert intent.classify("") == intent.UNCERTAIN
    assert intent.classify("   ") == intent.UNCERTAIN
    assert intent.classify(None) == intent.UNCERTAIN
    assert intent.classify(12345) == intent.UNCERTAIN


def test_requires_verification_true_for_planning_and_uncertain_only():
    assert intent.requires_verification("what's next?") is True
    assert intent.requires_verification("random unrelated message") is True  # uncertain
    assert intent.requires_verification("Traceback (most recent call last):") is False


def test_classify_never_raises_on_garbage_input():
    # A classifier that can crash its caller is itself a silent-failure risk.
    for garbage in [object(), [], {}, 3.14]:
        assert intent.classify(garbage) == intent.UNCERTAIN
