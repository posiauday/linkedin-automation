"""Configuration: global settings from env, per-client profiles from YAML."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

try:  # optional, but the README tells people to create a .env
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

CLIENTS_DIR = REPO_ROOT / "clients"
OUTPUT_ROOT = REPO_ROOT / "linkedin_posts"

# A slug becomes a path segment in two places, so it may not escape its parent.
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def _flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    """Process-wide settings, all sourced from environment variables."""

    claude_api_key: str = field(default_factory=lambda: os.getenv("CLAUDE_API_KEY", ""))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    model: str = field(default_factory=lambda: os.getenv("CLAUDE_MODEL", "claude-sonnet-5"))
    linkedin_version: str = field(
        default_factory=lambda: os.getenv("LINKEDIN_API_VERSION", "202405")
    )
    generate_images: bool = field(default_factory=lambda: _flag("ENABLE_IMAGE_GENERATION", True))
    publish: bool = field(default_factory=lambda: _flag("ENABLE_LINKEDIN_POSTING", False))

    def require_claude(self) -> None:
        if not self.claude_api_key:
            raise RuntimeError(
                "CLAUDE_API_KEY is not set. Copy .env.example to .env and fill it in, "
                "or add it as a GitHub Actions secret."
            )


@dataclass
class Client:
    """A single LinkedIn account we generate and publish content for."""

    slug: str
    name: str
    niche: str
    audience: str = "founders and operators"
    role: str = ""
    tone: str = "direct, specific, no hype"
    goal: str = "book discovery calls"
    topics: list[str] = field(default_factory=list)
    banned_phrases: list[str] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)
    image_style: str = (
        "clean minimalist editorial illustration, flat vector, generous whitespace, "
        "muted professional palette, no text in image"
    )
    linkedin_token_env: str = "LINKEDIN_ACCESS_TOKEN"
    linkedin_person_env: str = "LINKEDIN_PERSON_ID"

    @property
    def access_token(self) -> str:
        return os.getenv(self.linkedin_token_env, "")

    @property
    def person_id(self) -> str:
        return os.getenv(self.linkedin_person_env, "")

    @property
    def output_dir(self) -> Path:
        return OUTPUT_ROOT / self.slug

    @classmethod
    def load(cls, slug: str) -> "Client":
        if not SLUG_PATTERN.match(slug):
            raise ValueError(
                f"Invalid client slug {slug!r}. Use lowercase letters, digits, "
                "hyphens and underscores only."
            )
        path = CLIENTS_DIR / f"{slug}.yaml"
        if not path.exists():
            available = ", ".join(c.stem for c in sorted(CLIENTS_DIR.glob("*.yaml"))) or "none"
            raise FileNotFoundError(f"No client profile at {path}. Available: {available}")
        data: dict[str, Any] = yaml.safe_load(path.read_text()) or {}
        data.setdefault("slug", slug)
        known = {f.name for f in cls.__dataclass_fields__.values()}
        unknown = set(data) - known
        if unknown:
            raise ValueError(f"{path.name} has unknown keys: {sorted(unknown)}")
        return cls(**data)

    @classmethod
    def load_all(cls) -> list["Client"]:
        return [
            cls.load(p.stem)
            for p in sorted(CLIENTS_DIR.glob("*.yaml"))
            if not p.stem.startswith("_")
        ]
