import threading


BITCOIN_KEYWORDS = {
    "bitcoin", "btc", "crypto", "ethereum", "eth", "macro", "fed", "inflation",
    "interest rate", "recession", "gold", "market", "s&p", "nasdaq", "dow",
    "economy", "economic", "finance", "financial", "investing", "investment",
    "wealth", "trading", "stocks", "bonds", "treasury", "dollar", "usd",
    "currency", "defi", "altcoin", "halving", "mining",
}

AI_KEYWORDS = {
    "claude", "anthropic", "ai", "artificial intelligence", "llm", "gpt",
    "chatgpt", "openai", "gemini", "cursor", "copilot", "claude code", "mcp",
    "prompt", "automation", "agent", "langchain", "rag", "vector", "embedding",
    "certification", "cert", "exam", "tutorial", "how to", "course", "learn",
    "training", "aws", "azure", "google cloud",
}

FOLDER_TO_DISPLAY = {
    "ai-and-claude-code": "AI & Claude Code",
    "bitcoin-and-economic-news": "Bitcoin and Economic News",
    "uncategorized": "Uncategorized",
}

DISPLAY_TO_FOLDER = {v: k for k, v in FOLDER_TO_DISPLAY.items()}


def _score(text, keywords):
    """Count how many keywords appear in text (case-insensitive, multi-word aware)."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def suggest_category(title, channel):
    """
    Return suggested folder name based on keyword scoring.
    Title keywords are weighted 2x; channel name keywords are weighted 1x.
    """
    title_bitcoin = _score(title, BITCOIN_KEYWORDS) * 2
    channel_bitcoin = _score(channel, BITCOIN_KEYWORDS) * 1
    title_ai = _score(title, AI_KEYWORDS) * 2
    channel_ai = _score(channel, AI_KEYWORDS) * 1

    bitcoin_total = title_bitcoin + channel_bitcoin
    ai_total = title_ai + channel_ai

    if bitcoin_total == 0 and ai_total == 0:
        return "uncategorized"
    if bitcoin_total >= ai_total:
        return "bitcoin-and-economic-news"
    return "ai-and-claude-code"


def _timed_input(prompt, timeout=10):
    """Prompt for input with a timeout. Returns None on timeout."""
    result = [None]

    def get_input():
        try:
            result[0] = input(prompt)
        except Exception:
            pass

    t = threading.Thread(target=get_input, daemon=True)
    t.start()
    t.join(timeout)
    return result[0]


def classify(title, channel, video_id=None, pre_suggestion=None):
    """
    Suggest a category, prompt user for confirmation, return final decision.

    Args:
        pre_suggestion: Optional folder name to use instead of keyword scoring.
                        Supplied by channel.py when the channel has a registered group.
                        User can still override or confirm.

    Returns: (folder_name, display_name, was_overridden)
    """
    if pre_suggestion and pre_suggestion in FOLDER_TO_DISPLAY:
        suggested_folder = pre_suggestion
    else:
        suggested_folder = suggest_category(title, channel)
    suggested_display = FOLDER_TO_DISPLAY[suggested_folder]

    print(f'\nVideo: "{title}"')
    print(f'Channel: {channel}')
    print(f'\nSuggested category: {suggested_display}')
    print('Press Enter to confirm, or type:')
    print('  1 — AI & Claude Code')
    print('  2 — Bitcoin and Economic News')
    print('  s — Skip (save to uncategorized)')

    for attempt in range(2):
        response = _timed_input('> ', timeout=10)

        if response is None:
            print(f'(No input — auto-accepted: {suggested_display})')
            return suggested_folder, suggested_display, False

        response = response.strip().lower()

        if response == '':
            return suggested_folder, suggested_display, False
        elif response == '1':
            folder = 'ai-and-claude-code'
            display = 'AI & Claude Code'
            return folder, display, (suggested_folder != folder)
        elif response == '2':
            folder = 'bitcoin-and-economic-news'
            display = 'Bitcoin and Economic News'
            return folder, display, (suggested_folder != folder)
        elif response == 's':
            folder = 'uncategorized'
            display = 'Uncategorized'
            return folder, display, (suggested_folder != folder)
        else:
            if attempt == 0:
                print('Unrecognized input. Press Enter to confirm, or type 1, 2, or s:')
            else:
                print(f'Falling back to suggestion: {suggested_display}')
                return suggested_folder, suggested_display, False

    return suggested_folder, suggested_display, False
