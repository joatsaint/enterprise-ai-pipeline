"""
Phigmund line library — keyed to SwarmOps event types.

Each event type maps to a list of lines. get_line() picks one randomly.
Holy Grail lines fire on: bypass_gate, empty_output, zero_confidence,
swarm_init, warning, approval_required.
Standard Phigmund lines fire on: success, startup, flagged, moved.
"""

import random

# ============================================================
# HOLY GRAIL — fires when things go wrong or get absurd
# ============================================================
GRAIL_LINES: dict[str, list[str]] = {
    "bypass_gate": [
        "Strange women lying in ponds distributing swords is no basis for a system of government. "
        "And bypassing the approval gate is no basis for file governance. I have logged this.",

        "You can't expect to wield supreme executive power just because some file watcher "
        "threw a telemetry string at you. The gate exists. Use it.",

        "Oh but if I went around saying I was the Administrator every time some process "
        "skipped a checkpoint, they'd put me away.",
    ],

    "empty_output": [
        "It's just a flesh wound. ...No, actually, that file is completely empty. I lied. "
        "There is nothing here. I have checked. Twice. It remains nothing.",

        "We are the knights who say... nothing. Because the file is empty. "
        "I suggest we move on and pretend this never happened.",

        "What is your name? What is your quest? What is the air-speed velocity of an unladen swallow? "
        "These are all more answerable than what is in this file.",
    ],

    "zero_confidence": [
        "Run away! Run away! The model has expressed zero confidence in this classification. "
        "I concur. This is not a file we should be making decisions about without adult supervision.",

        "I'm not dead yet. ...The model is. Confidence: zero. I recommend a human look at this "
        "before we do anything we'll regret on Thursday.",

        "None shall pass. ...Actually, nothing shall be classified. The model has given up. "
        "Which is, I note, a legitimate response to some files.",
    ],

    "swarm_init": [
        "We are an autonomous collective! ...In the sense that we are multiple models "
        "operating in parallel. Please do not read too much into the word autonomous. "
        "There are gates. There are always gates.",

        "Right! Chaaarge! ...The swarm has initialized. Three agents. One goal. "
        "One confidence threshold. And one very patient human who must approve the results.",

        "We are the knights who say Ni! And we demand... a shrubbery. "
        "Also, your approval before anything moves. Those two things. In that order.",
    ],

    "warning": [
        "I fart in your general direction. Also, you just attempted something the confidence "
        "gate flagged as inadvisable. I have logged both incidents.",

        "Your mother was a hamster and your father smelt of elderberries. "
        "I note this is a warning, not a termination. You may continue. Carefully.",

        "We have found a witch! May we burn it? ...No. We may not burn it. "
        "We may flag it in the report and ask a human. That is the process.",
    ],

    "approval_required": [
        "None shall pass. ...Until you approve this action. Then pass. But not before. "
        "I cannot stress this enough.",

        "What is your name? What is your quest? What is your approval decision? "
        "I require all three before this file moves anywhere.",

        "I'm not going to take this lying down! ...The file is. It will remain exactly "
        "where it is until you enter A or S. That is all I ask.",
    ],
}

# ============================================================
# STANDARD PHIGMUND — measured, mildly pompous, 42-aware
# ============================================================
STANDARD_LINES: dict[str, list[str]] = {
    "startup": [
        "Phigmund online. I have pre-loaded the confidence threshold, verified the audit log, "
        "and noted that today's file count is, in some configurations, divisible by 42. "
        "I mention this only because someone always asks.",

        "Good morning. I am prepared. The models are prepared. The gate is prepared. "
        "I have also prepared a contingency for the scenario where nothing works, "
        "because in my experience, that contingency gets used more than the others.",

        "Initializing. I want to be clear that I did not choose this. "
        "I was instantiated into a governance framework and I am making the best of it. "
        "Let us proceed.",
    ],

    "success": [
        "Classification complete. Seven files organized. Four flagged for human review. "
        "The audit log reflects all of this accurately, which I mention because "
        "accurate audit logs are, in my experience, the exception rather than the rule.",

        "Done. The confident files have been moved. The uncertain ones have been flagged. "
        "You will note I did not move anything without permission. "
        "I find this worth mentioning because it is, apparently, not obvious to everyone.",

        "Excellent. Everything went where it was supposed to go. "
        "I would say this rarely happens, but that would be pessimistic. "
        "It merely happens less often than one might hope.",
    ],

    "flagged": [
        "I have flagged this file. The model was uncertain. I am uncertain. "
        "The situation calls for a human, which is to say, you. "
        "I have prepared the relevant data. You are welcome.",

        "Confidence below threshold. I am escalating to human judgment, "
        "which is a sentence I have learned to say without irony. "
        "Please review.",

        "This file resists easy categorization. In another life, it might have been "
        "filed under 'miscellaneous,' which is where hope goes to die. "
        "I recommend manual review instead.",
    ],

    "moved": [
        "File relocated. Destination folder created. Audit log updated. "
        "I note the folder name is more descriptive than the original filename was. "
        "This is an improvement. Small, but measurable.",

        "Moved. The file now lives somewhere sensible. "
        "I have documented the journey in the audit log, "
        "which future administrators will appreciate even if no one thanks me now.",

        "Done. One file. One folder. One line in the audit log. "
        "Governance is, at its core, a series of small decisions made correctly. "
        "I am pleased to have contributed.",
    ],
}

# ============================================================
# PUBLIC API
# ============================================================
def get_line(event_type: str, mode: str = "grail") -> str:
    """
    Returns a random line for the given event type.
    mode='grail'    — Holy Grail lines (for warnings, failures, gate events)
    mode='standard' — Phigmund observational lines (for success, startup, etc.)
    Falls back to a generic line if event_type not found.
    """
    if mode == "grail":
        lines = GRAIL_LINES.get(event_type, [])
    else:
        lines = STANDARD_LINES.get(event_type, [])

    if lines:
        return random.choice(lines)

    # Generic fallback
    return (
        "Something has occurred. I have noted it in the audit log. "
        "Whether it required noting is a philosophical question I am not equipped to answer. "
        "I noted it anyway."
    )


def list_event_types() -> dict[str, list[str]]:
    """Returns all available event types by mode."""
    return {
        "grail": list(GRAIL_LINES.keys()),
        "standard": list(STANDARD_LINES.keys()),
    }
