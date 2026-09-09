"""Persistence for generated posts, plus the history used to avoid repetition."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import Client


@dataclass
class Post:
    """One generated post and everything we know about it."""

    hook: str
    body: str
    hashtags: list[str]
    topic: str
    image_prompt: str = ""
    image_path: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    published: bool = False
    linkedin_urn: str | None = None
    error: str | None = None

    @property
    def full_text(self) -> str:
        tags = " ".join(f"#{t.lstrip('#')}" for t in self.hashtags)
        parts = [self.hook.strip(), self.body.strip()]
        if tags:
            parts.append(tags)
        return "\n\n".join(p for p in parts if p)


class Store:
    """Reads and writes a client's post archive on disk."""

    def __init__(self, client: Client):
        self.client = client
        self.dir = client.output_dir
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, post: Post) -> Path:
        stamp = post.created_at.replace(":", "").replace("-", "")[:15]
        return self.dir / f"post_{stamp}.json"

    def save(self, post: Post) -> Path:
        path = self._path_for(post)
        # Collisions happen when several posts are generated in the same second.
        counter = 1
        while path.exists():
            path = path.with_name(f"{path.stem}_{counter}.json")
            counter += 1
        path.write_text(json.dumps(asdict(post), indent=2))
        return path

    def load_all(self) -> list[Post]:
        posts: list[Post] = []
        for path in sorted(self.dir.glob("post_*.json")):
            try:
                data: dict[str, Any] = json.loads(path.read_text())
            except json.JSONDecodeError:
                continue
            known = {f.name for f in Post.__dataclass_fields__.values()}
            posts.append(Post(**{k: v for k, v in data.items() if k in known}))
        return posts

    def recent_hooks(self, limit: int = 25) -> list[str]:
        """Opening lines of recent posts, fed back to the model as anti-repetition context."""
        return [p.hook for p in self.load_all()[-limit:] if p.hook]

    def used_topics(self, limit: int = 40) -> list[str]:
        return [p.topic for p in self.load_all()[-limit:] if p.topic]
