"""
Newsletter curator — AI newsletter discovery + curation from Randy's Hotmail inbox.

Discovery mode connects read-only via IMAP and lists unique senders from the
last N days, so the sender allowlist in newsletter_sources.json can be built
from real inbox data instead of guesswork.

Usage (via main.py):
  python -m src.main curate-newsletters --discover [--days N]
"""
import email
import imaplib
import os
import sys
from datetime import datetime, timedelta
from email.header import decode_header

IMAP_HOST = "outlook.office365.com"
IMAP_PORT = 993


def _decode(value: str) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    decoded = ""
    for text, enc in parts:
        if isinstance(text, bytes):
            decoded += text.decode(enc or "utf-8", errors="replace")
        else:
            decoded += text
    # Email headers are attacker-controlled — strip control/escape characters
    # (e.g. ANSI sequences) so they can't affect the terminal or files written
    # from these values (newsletter_sources.json).
    return "".join(c for c in decoded if c.isprintable())


def _split_sender(from_header: str) -> tuple[str, str]:
    if "<" in from_header and ">" in from_header:
        name = from_header.split("<")[0].strip().strip('"')
        addr = from_header.split("<")[1].split(">")[0].strip()
        return name or addr, addr
    return from_header, from_header


def run_discover(days: int = 7):
    email_addr = os.getenv("HOTMAIL_EMAIL")
    app_password = os.getenv("HOTMAIL_APP_PASSWORD")
    if not email_addr or not app_password:
        print("ERROR: Set HOTMAIL_EMAIL and HOTMAIL_APP_PASSWORD in .env before running.")
        print("Generate an app password at account.live.com > Security > Advanced security options > App passwords")
        sys.exit(1)

    print(f"Connecting to {IMAP_HOST} as {email_addr} (read-only)...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(email_addr, app_password)
        mail.select("INBOX", readonly=True)
    except imaplib.IMAP4.error as exc:
        print(f"ERROR: IMAP login failed: {exc}")
        sys.exit(1)

    since_date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
    status, data = mail.search(None, f"(SINCE {since_date})")
    if status != "OK":
        print("ERROR: IMAP search failed.")
        mail.logout()
        sys.exit(1)

    ids = data[0].split()
    print(f"\n{len(ids)} messages in the last {days} days.\n")

    senders: dict[tuple[str, str], int] = {}
    for msg_id in ids:
        status, msg_data = mail.fetch(msg_id, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
        if status != "OK" or not msg_data or not msg_data[0]:
            continue
        raw_header = msg_data[0][1]
        msg = email.message_from_bytes(raw_header)
        from_header = _decode(msg.get("From", ""))
        key = _split_sender(from_header)
        senders[key] = senders.get(key, 0) + 1

    mail.logout()

    if not senders:
        print("No messages found in this window.")
        return

    print("Unique senders found (count  name <address>):\n")
    for (name, addr), count in sorted(senders.items(), key=lambda kv: -kv[1]):
        print(f"  {count:3d}x  {name} <{addr}>")

    print("\nReview the list above and tell me which senders are AI newsletters")
    print("you want tracked — I'll add them to newsletter_sources.json.")


def run_curate_newsletters(discover: bool = False, days: int = 7):
    if discover:
        run_discover(days=days)
        return
    print("Curation mode not yet built. Run with --discover first to build the sender allowlist.")
