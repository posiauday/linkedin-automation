"""LinkedIn publishing against the official versioned REST API.

The image flow is three calls, and skipping any of them is why most LinkedIn
automation scripts silently post text only:
  1. initializeUpload  -> returns a one-time uploadUrl and the image URN
  2. PUT the bytes     -> to that uploadUrl
  3. create the post   -> referencing the image URN
"""

from __future__ import annotations

from pathlib import Path

from urllib.parse import quote

import requests

from .config import Client, Settings

API_ROOT = "https://api.linkedin.com"


class LinkedInError(RuntimeError):
    pass


class Publisher:
    def __init__(self, settings: Settings, client: Client):
        self.settings = settings
        self.client = client

    def _headers(self) -> dict[str, str]:
        token = self.client.access_token
        if not token:
            raise LinkedInError(
                f"{self.client.linkedin_token_env} is not set for client "
                f"'{self.client.slug}'. Publishing needs a valid access token."
            )
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": self.settings.linkedin_version,
        }

    def whoami(self) -> dict:
        """Fetch the authenticated member's profile. The 'sub' field is the person ID
        you put in LINKEDIN_PERSON_ID — this saves hunting for it by hand."""
        response = requests.get(
            f"{API_ROOT}/v2/userinfo", headers=self._headers(), timeout=30
        )
        if response.status_code == 401:
            raise LinkedInError("Access token is invalid or expired. Generate a new one.")
        if response.status_code == 403:
            raise LinkedInError(
                "Token lacks the required scopes. You need 'openid', 'profile' and 'w_member_social'."
            )
        response.raise_for_status()
        return response.json()

    @property
    def author_urn(self) -> str:
        person_id = self.client.person_id
        if not person_id:
            raise LinkedInError(
                f"{self.client.linkedin_person_env} is not set. Run: python run.py whoami "
                f"--client {self.client.slug}"
            )
        if person_id.startswith("urn:"):
            return person_id
        return f"urn:li:person:{person_id}"

    def upload_image(self, path: Path) -> str:
        """Upload an image and return its URN."""
        init = requests.post(
            f"{API_ROOT}/rest/images?action=initializeUpload",
            headers=self._headers(),
            json={"initializeUploadRequest": {"owner": self.author_urn}},
            timeout=60,
        )
        if not init.ok:
            raise LinkedInError(f"Image upload init failed ({init.status_code}): {init.text[:300]}")
        value = init.json()["value"]
        upload_url, image_urn = value["uploadUrl"], value["image"]

        put = requests.put(
            upload_url,
            headers={"Authorization": f"Bearer {self.client.access_token}"},
            data=path.read_bytes(),
            timeout=180,
        )
        if not put.ok:
            raise LinkedInError(f"Image byte upload failed ({put.status_code}): {put.text[:300]}")
        return image_urn

    def upload_document(self, path: Path) -> str:
        """Upload a PDF and return its document URN. Same three-step dance as
        images, against the Documents API."""
        init = requests.post(
            f"{API_ROOT}/rest/documents?action=initializeUpload",
            headers=self._headers(),
            json={"initializeUploadRequest": {"owner": self.author_urn}},
            timeout=60,
        )
        if not init.ok:
            raise LinkedInError(
                f"Document upload init failed ({init.status_code}): {init.text[:300]}"
            )
        value = init.json()["value"]
        put = requests.put(
            value["uploadUrl"],
            headers={"Authorization": f"Bearer {self.client.access_token}"},
            data=path.read_bytes(),
            timeout=300,
        )
        if not put.ok:
            raise LinkedInError(
                f"Document byte upload failed ({put.status_code}): {put.text[:300]}"
            )
        return value["document"]

    def publish_document(self, text: str, pdf_path: Path, title: str) -> str:
        """Publish a document (carousel) post. `title` shows above the carousel."""
        if not pdf_path.exists():
            raise LinkedInError(f"No PDF at {pdf_path}")
        payload = {
            "author": self.author_urn,
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "content": {
                "media": {"id": self.upload_document(pdf_path), "title": title[:100]}
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        response = requests.post(
            f"{API_ROOT}/rest/posts", headers=self._headers(), json=payload, timeout=90
        )
        if not response.ok:
            raise LinkedInError(
                f"Carousel post failed ({response.status_code}): {response.text[:300]}"
            )
        return response.headers.get("x-restli-id") or response.json().get("id", "unknown")

    def engagement(self, post_urn: str) -> dict | None:
        """Reactions and comments for one published post.

        This is what turns 'we posted 12 times' into something a client can show.

        Returns None when the lookup failed (bad token, wrong scope, deleted post)
        and {} only when the response carried no counts, so the caller can tell
        "nothing to report" apart from "nothing worked".
        """
        # The URN contains colons, which must not be read as path syntax.
        response = requests.get(
            f"{API_ROOT}/rest/socialActions/{quote(post_urn, safe='')}",
            headers=self._headers(),
            timeout=30,
        )
        if response.status_code in (401, 403):
            raise LinkedInError(
                "Cannot read post analytics: the token is expired or lacks the "
                "scope. Reading engagement needs the member analytics permission."
            )
        if not response.ok:
            return None
        data = response.json()
        return {
            "reactions": (data.get("likesSummary") or {}).get("totalLikes", 0),
            "comments": (data.get("commentsSummary") or {}).get(
                "totalFirstLevelComments", 0
            ),
        }

    def publish(self, text: str, image_path: Path | None = None) -> str:
        """Create a post. Returns the post URN."""
        payload: dict = {
            "author": self.author_urn,
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }

        if image_path and image_path.exists():
            payload["content"] = {
                "media": {"id": self.upload_image(image_path), "title": "post image"}
            }

        response = requests.post(
            f"{API_ROOT}/rest/posts", headers=self._headers(), json=payload, timeout=60
        )
        if response.status_code == 422:
            raise LinkedInError(
                f"LinkedIn rejected the post content ({response.text[:300]}). "
                "Most often this is a duplicate of a recent post."
            )
        if not response.ok:
            raise LinkedInError(f"Post failed ({response.status_code}): {response.text[:300]}")

        return response.headers.get("x-restli-id") or response.json().get("id", "unknown")
