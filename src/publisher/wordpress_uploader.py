"""
WordPress media uploader — hosts images/PDFs on rskiles.com so Buffer's
add_image()/DocumentAssetInput (which require a public URL, not file bytes)
have something to point at.

Auth: WP Application Password (WP_USERNAME + WP_APP_PASSWORD in .env), sent as
HTTP Basic Auth to the REST API. Create one at rskiles.com/wp-admin > Users >
Profile > Application Passwords.
"""
import mimetypes
import os
from pathlib import Path

import requests

MEDIA_ENDPOINT = "/wp-json/wp/v2/media"


def _load_env():
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    value = value.strip().strip('"').strip("'")
                    os.environ.setdefault(key.strip(), value)


_load_env()


def upload_media(file_path, title=None):
    """
    Upload a file to the WordPress media library on rskiles.com.
    Args: file_path (str — local path to an image or PDF), title (str, optional)
    Returns dict with keys: id, url, mime_type.
    """
    wp_url = os.getenv("WP_URL")
    username = os.getenv("WP_USERNAME")
    app_password = os.getenv("WP_APP_PASSWORD")
    if not wp_url or not username or not app_password:
        raise RuntimeError("WP_URL, WP_USERNAME, and WP_APP_PASSWORD must be set in .env")

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {file_path}")

    mime_type, _ = mimetypes.guess_type(str(path))
    mime_type = mime_type or "application/octet-stream"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ClaudeCodeWPUploader/1.0",
        "Accept": "application/json",
    }
    with open(path, "rb") as f:
        files = {"file": (path.name, f, mime_type)}
        r = requests.post(
            wp_url.rstrip("/") + MEDIA_ENDPOINT,
            headers=headers,
            files=files,
            auth=(username, app_password),
            timeout=60,
        )
    if r.status_code not in (200, 201):
        raise RuntimeError(f"WordPress media upload failed (HTTP {r.status_code}): {r.text[:300]}")

    result = r.json()
    media_id = result.get("id")
    media_url = result.get("source_url")
    if not media_url:
        raise RuntimeError(f"WordPress upload succeeded but returned no source_url: {result}")

    if title:
        requests.post(
            f"{wp_url.rstrip('/')}{MEDIA_ENDPOINT}/{media_id}",
            json={"title": title},
            auth=(username, app_password),
            timeout=30,
        )

    return {"id": media_id, "url": media_url, "mime_type": mime_type}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Local path to image or PDF to upload")
    parser.add_argument("--title", help="Optional media title")
    args = parser.parse_args()

    media = upload_media(args.file, title=args.title)
    print(f"[OK] Uploaded — media ID: {media['id']}")
    print(f"     Public URL: {media['url']}")
