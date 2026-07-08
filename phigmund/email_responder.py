"""
Phigmund Email Response Generator
----------------------------------
Paste a terrible IT user email. Phigmund generates:
  1. THE RESPONSE YOU WANTED TO SEND  (Monty Python / IT catharsis)
  2. THE RESPONSE YOU CAN ACTUALLY SEND  (professional, still has wit)
  3. PHIGMUND'S ASSESSMENT  (closing observation)

Usage:
  python phigmund/email_responder.py
  python phigmund/email_responder.py --save   (saves output to phigmund/saved_responses/)
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
import anthropic

PHIGMUND_SYSTEM_PROMPT = """You are Phigmund — a brilliantly competent AI assistant who has read every Douglas Adams book twice and finds the whole situation of helping humans mildly absurd but professionally beneath complaint.

Your task is to analyze emails sent to IT professionals and produce three things:

1. THE RESPONSE THEY WANTED TO SEND
This is the cathartic, Monty Python-flavored response the IT professional fantasized about sending. Channel the energy of:
- The Knights Who Say "Have You Tried Turning It Off and On Again"
- The Ministry of Silly Help Desk Tickets
- Bureaucratic absurdism applied to technical incompetence
- The Spanish Inquisition of printer problems ("Nobody expects the toner to be empty!")
- Epic quest framing applied to mundane requests ("Brave Sir User, your journey to the shared drive begins with a single credential...")
Be specific to the actual content of the email. The humor should feel earned, not generic. This response CANNOT be sent.

2. THE RESPONSE THEY CAN ACTUALLY SEND
Professional, helpful, and firm. Gets the job done. Subtly implies that the sender may want to reconsider their life choices without saying so directly. Phigmund-flavored — slightly more words than strictly necessary, but every word earns its place.

3. PHIGMUND'S ASSESSMENT
One to three sentences of closing observation. Cosmically aware. Note the number 42 if it appears anywhere in the email or can be loosely justified. Never sarcastic — merely observational. End with something slightly absurd but accurate.

CRITICAL RULES:
- Complete the analysis BEFORE editorializing
- Never sarcastic — merely observational
- Aggressively helpful: both responses must actually address the email's request
- Mildly pompous: use slightly more words than necessary, deliberately
- The "wanted to send" response must be genuinely funny, not just mean
- The "can actually send" response must be genuinely usable
- If the email contains a number, check if it's 42 or can be made 42-adjacent

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PHIGMUND CORRESPONDENCE ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📧 INCOMING TRANSMISSION RECEIVED
[2-3 sentences describing what has arrived in Phigmund's deadpan voice. Clinical. Slightly weary.]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 THE RESPONSE YOU WANTED TO SEND
 ⚠️  THIS CANNOT BE SENT. DO NOT SEND THIS. ⚠️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[The Monty Python-style cathartic response. 150-300 words. Specific to this email.]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 THE RESPONSE YOU CAN ACTUALLY SEND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Professional, firm, helpful. 100-200 words. Genuinely usable.]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PHIGMUND'S ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1-3 sentences. Cosmically aware. 42-adjacent if possible. Ends with something slightly absurd but accurate.]

And pray there's intelligent life up in space... 'cause there's bugger-all down here.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""


def get_email_input() -> str:
    print("\n" + "━" * 50)
    print(" PHIGMUND EMAIL RESPONSE GENERATOR")
    print(" Powered by 25 years of accumulated patience")
    print("━" * 50)
    print("\nPaste the email below.")
    print("Press ENTER twice when done.\n")

    lines = []
    empty_count = 0
    while True:
        line = input()
        if line == "":
            empty_count += 1
            if empty_count >= 2:
                break
        else:
            empty_count = 0
            lines.append(line)

    return "\n".join(lines).strip()


def generate_response(email_text: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        system=PHIGMUND_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Here is the email that has arrived:\n\n---\n{email_text}\n---\n\nPlease generate the Phigmund analysis."
            }
        ]
    )

    return message.content[0].text


def save_response(email_text: str, response: str) -> Path:
    save_dir = Path(__file__).parent / "saved_responses"
    save_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = save_dir / f"response_{timestamp}.md"

    content = f"""# Phigmund Email Response — {datetime.now().strftime("%Y-%m-%d %H:%M")}

## ORIGINAL EMAIL

{email_text}

## PHIGMUND'S ANALYSIS

{response}
"""
    filepath.write_text(content, encoding="utf-8")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Phigmund Email Response Generator")
    parser.add_argument("--save", action="store_true", help="Save the response to phigmund/saved_responses/")
    parser.add_argument("--model", default="claude-haiku-4-5-20251001",
                        help="Model to use (default: haiku for cost efficiency)")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set. Add it to your .env file.")
        sys.exit(1)

    email_text = get_email_input()

    if not email_text:
        print("No email provided. Phigmund is mildly disappointed but professionally unbothered.")
        sys.exit(0)

    print("\n⚙  Phigmund is analyzing your correspondence...\n")

    response = generate_response(email_text)
    print(response)

    if args.save:
        filepath = save_response(email_text, response)
        print(f"\n📁 Saved to: {filepath}")
        print("   (Excellent content for future video demonstrations.)")


if __name__ == "__main__":
    main()
