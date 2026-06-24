"""
Buffer GraphQL publisher — schedules posts to LinkedIn via Buffer's GraphQL API.
Reads BUFFER_ACCESS_TOKEN and BUFFER_LINKEDIN_CHANNEL_ID from .env.
"""
import os
import requests

GRAPHQL_URL = "https://api.buffer.com/graphql"

_CREATE_POST = """
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess {
      post { id status dueAt }
    }
    ... on RestProxyError { message }
    ... on InvalidInputError { message }
    ... on UnexpectedError { message }
  }
}
"""

_DELETE_POST = """
mutation DeletePost($input: DeletePostInput!) {
  deletePost(input: $input) {
    ... on DeletePostSuccess { id }
    ... on VoidMutationError { message }
  }
}
"""


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


def _graphql(query, variables):
    token = os.getenv("BUFFER_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("BUFFER_ACCESS_TOKEN not set in .env")
    r = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=30,
    )
    r.raise_for_status()
    try:
        data = r.json()
    except ValueError as exc:
        raise RuntimeError(
            f"Buffer returned non-JSON response (HTTP {r.status_code}): {r.text[:200]}"
        ) from exc
    if "errors" in data:
        raise RuntimeError(f"Buffer API error: {data['errors']}")
    return data["data"]


def schedule_post(text, due_at_utc, assets=None):
    """
    Schedule a LinkedIn post via Buffer.

    Args:
        text:        Post body string.
        due_at_utc:  datetime (UTC) for when Buffer should publish.
        assets:      Optional list of AssetInput dicts, e.g.
                     [{"image": {"url": "https://..."}}] or
                     [{"document": {"url": ..., "title": ..., "thumbnailUrl": ...}}]

    Returns dict with keys: id, status, dueAt.
    """
    channel_id = os.getenv("BUFFER_LINKEDIN_CHANNEL_ID")
    if not channel_id:
        raise RuntimeError("BUFFER_LINKEDIN_CHANNEL_ID not set in .env")

    data = _graphql(_CREATE_POST, {
        "input": {
            "channelId": channel_id,
            "text": text,
            "schedulingType": "automatic",
            "mode": "customScheduled",
            "dueAt": due_at_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "assets": assets or [],
        }
    })
    post = (data.get("createPost") or {}).get("post")
    if not post:
        raise RuntimeError(f"Unexpected Buffer response: {data}")
    return post


def add_image(post_id, image_url, due_at_utc):
    """
    Attach an image to an existing scheduled Buffer post.

    Args:
        post_id:     Buffer post ID string.
        image_url:   Publicly accessible image URL.
        due_at_utc:  Original scheduled datetime (UTC) — required by Buffer on edits.

    Returns dict with keys: id, status, dueAt.
    """
    _EDIT_POST = """
    mutation EditPost($input: EditPostInput!) {
      editPost(input: $input) {
        ... on PostActionSuccess {
          post { id status dueAt }
        }
        ... on RestProxyError { message }
        ... on InvalidInputError { message }
        ... on UnexpectedError { message }
      }
    }
    """
    data = _graphql(_EDIT_POST, {
        "input": {
            "id": post_id,
            "schedulingType": "automatic",
            "mode": "customScheduled",
            "dueAt": due_at_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "assets": [{"image": {"url": image_url}}],
        }
    })
    result = data.get("editPost", {})
    post = result.get("post")
    if not post:
        raise RuntimeError(f"Buffer editPost failed: {result.get('message', result)}")
    return post


def delete_post(post_id):
    """Delete a scheduled Buffer post by ID. Returns the deleted post ID."""
    data = _graphql(_DELETE_POST, {"input": {"id": post_id}})
    result = data.get("deletePost") or {}
    deleted_id = result.get("id")
    if not deleted_id:
        raise RuntimeError(f"Buffer deletePost failed: {result.get('message', result)}")
    return deleted_id
