"""Persistence for generated posts, plus the history used to avoid repetition."""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import Client

FILENAME = re.compile(r"^post_(\d{8}T\d{6})_([0-9a-f]{8})\.json$")


def _new_id() -> str:
    return uuid.uuid4().hex[:8]


@dataclass
class Post:
    """One generated post and everything we know about it.

    `id` is what makes a post addressable. Without it, saving a post twice wrote
    a second file instead of updating the first, so a published post still
    looked queued and went out again on the next run.
    """

    hook: str
    body: str
    hashtags: list[str]
    topic: str
    id: str = field(default_factory=_new_id)
    image_prompt: str = ""
    image_path: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    approved: bool = False
    published: bool = False
    linkedin_urn: str | None = None
    error: str | None = None
    cost_usd: float = 0.0

    @property
    def full_text(self) -> str:
        tags = " ".join(f"#{t.lstrip('#')}" for t in self.hashtags)
        parts = [self.hook.strip(), self.body.strip()]
        if tags:
            parts.append(tags)
        return "\n\n".join(p for p in parts if p)

    @property
    def state(self) -> str:
        if self.error:
            return "error"
        if self.published:
            return "published"
        if self.approved:
            return "approved"
        return "queued"


class Store:
    """Reads and writes a client's post archive on disk."""

    def __init__(self, client: Client):
        self.client = client
        self.dir = client.output_dir
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, post: Post) -> Path:
        # Both halves come from the post itself, so saving the same post twice
        # resolves to the same file and updates it in place.
        stamp = re.sub(r"[^0-9T]", "", post.created_at.split(".")[0].split("+")[0])[:15]
        return self.dir / f"post_{stamp}_{post.id}.json"

    def save(self, post: Post) -> Path:
        path = self._path_for(post)
        path.write_text(json.dumps(asdict(post), indent=2))
        return path

    def load_all(self) -> list[Post]:
        known = {f.name for f in Post.__dataclass_fields__.values()}
        posts: list[Post] = []
        for path in sorted(self.dir.glob("post_*.json")):
            try:
                data: dict[str, Any] = json.loads(path.read_text())
            except json.JSONDecodeError:
                continue
            if not isinstance(data, dict) or "hook" not in data:
                continue
            # Archives written before posts had ids: recover the id from the
            # filename so re-saving updates this file instead of forking it.
            if not data.get("id"):
                match = FILENAME.match(path.name)
                data["id"] = match.group(2) if match else _new_id()
            posts.append(Post(**{k: v for k, v in data.items() if k in known}))
        return posts

    def get(self, post_id: str) -> Post | None:
        for post in self.load_all():
            if post.id == post_id or post.id.startswith(post_id):
                return post
        return None

    def pending_publish(self) -> list[Post]:
        """Posts eligible to go out, oldest first."""
        return [p for p in self.load_all() if not p.published and not p.error]

    def recent_hooks(self, limit: int = 25) -> list[str]:
        """Opening lines of recent posts, fed back to the model as anti-repetition context."""
        return [p.hook for p in self.load_all()[-limit:] if p.hook]

    def used_topics(self, limit: int = 40) -> list[str]:
        return [p.topic for p in self.load_all()[-limit:] if p.topic]
