YouTube Transcript Downloader - Project Rules

🛠️ Verification Loop

After downloading, verify file exists in transcripts/ folder.

Check if file size is > 0 bytes.

🪙 Token Efficiency Rules

Format: Save transcripts as raw .txt to minimize metadata overhead.

Cleaning: Strip timestamps (e.g., 00:01) unless explicitly requested. Timestamps are "Token Vampires."

Summarization: When analyzing later, only feed Claude the first 20% and last 20% if the video is over 30 minutes (The "Context Sandwich" method).

🚀 Commands

Install: pip install youtube-transcript-api

Run: python download.py [URL]