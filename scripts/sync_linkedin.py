#!/usr/bin/env python3
"""Sync LinkedIn-approved member posts to the public portfolio's static JSON.

Requires approved r_member_social access. Never scrapes a LinkedIn webpage.
"""
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

FEED = Path(__file__).resolve().parents[1] / "data" / "linkedin-posts.json"
AUTHOR_PROFILE = "https://www.linkedin.com/in/ali-ahmed-khoso/"
MAX_POSTS = 24


def normalize(post, person_urn):
    if not isinstance(post, dict) or post.get("author") != person_urn:
        return None
    if post.get("lifecycleState") != "PUBLISHED" or post.get("visibility") != "PUBLIC":
        return None
    if post.get("distribution", {}).get("feedDistribution") == "NONE":
        return None
    urn = post.get("id", "")
    if not (urn.startswith("urn:li:share:") or urn.startswith("urn:li:ugcPost:")):
        return None
    caption = post.get("commentary") or ""
    if isinstance(caption, dict):
        caption = caption.get("text", "")
    caption = " ".join(str(caption).split()) or "Read this post on LinkedIn."
    published = post.get("publishedAt") or post.get("createdAt")
    iso_date = None
    if isinstance(published, (int, float)) and published > 0:
        iso_date = datetime.fromtimestamp(published / 1000, timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "url": f"https://www.linkedin.com/feed/update/{urn}/",
        "title": caption[:110] + ("…" if len(caption) > 110 else ""),
        "excerpt": caption[:430] + ("…" if len(caption) > 430 else ""),
        "date": iso_date,
        "urn": urn,
    }


def main():
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "").strip()
    author = os.environ.get("LINKEDIN_PERSON_URN", "").strip()
    version = os.environ.get("LINKEDIN_API_VERSION", "202608").strip()
    if not token or not author:
        print("LinkedIn sync not configured; keeping existing posts.")
        return
    if not author.startswith("urn:li:person:"):
        raise ValueError("LINKEDIN_PERSON_URN must be a person URN, not a public profile link.")
    if len(version) != 6 or not version.isdigit():
        raise ValueError("LINKEDIN_API_VERSION must use YYYYMM format.")

    query = urlencode({"author": author, "q": "author", "count": MAX_POSTS, "sortBy": "LAST_MODIFIED"})
    request = Request("https://api.linkedin.com/rest/posts?" + query, headers={
        "Authorization": "Bearer " + token,
        "X-Restli-Protocol-Version": "2.0.0",
        "Linkedin-Version": version,
        "Accept": "application/json",
    })
    try:
        with urlopen(request, timeout=25) as response:
            result = json.load(response)
    except HTTPError as error:
        raise RuntimeError(
            f"LinkedIn API HTTP {error.code}; verify approved member-read access, "
            "token expiry, member URN and API version."
        ) from None

    if not isinstance(result.get("elements"), list):
        raise RuntimeError("Unexpected LinkedIn API response; retaining the existing feed.")

    posts = [normalized for post in result["elements"]
             if (normalized := normalize(post, author))]
    posts.sort(key=lambda p: p.get("date") or "", reverse=True)
    data = json.loads(FEED.read_text(encoding="utf-8"))
    data["profile"] = AUTHOR_PROFILE
    data.setdefault("posts", [])
    data["synced_posts"] = posts[:MAX_POSTS]
    data["last_synced"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    FEED.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated LinkedIn post feed with {len(posts)} authorized public posts.")


if __name__ == "__main__":
    main()
