"""Post generation via Claude, using a forced tool schema so output is always valid JSON."""

from __future__ import annotations

import random
from typing import Any

from .config import Client, Settings
from .store import Post

POST_SCHEMA = {
    "name": "emit_posts",
    "description": "Return the finished LinkedIn posts.",
    "input_schema": {
        "type": "object",
        "properties": {
            "posts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Short label for what this post is about.",
                        },
                        "hook": {
                            "type": "string",
                            "description": (
                                "First line of the post. Under 120 characters. This is the "
                                "only line shown before 'see more', so it must earn the click "
                                "on its own. No emoji, no hashtags, no colon-list preamble."
                            ),
                        },
                        "body": {
                            "type": "string",
                            "description": (
                                "The rest of the post, 90-180 words, short paragraphs separated "
                                "by blank lines. Ends with one genuine question."
                            ),
                        },
                        "hashtags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "3-5 hashtags, no '#' prefix.",
                        },
                        "image_prompt": {
                            "type": "string",
                            "description": "Image generation prompt matching the client's visual style.",
                        },
                    },
                    "required": ["topic", "hook", "body", "hashtags", "image_prompt"],
                },
            }
        },
        "required": ["posts"],
    },
}

SYSTEM_PROMPT = """You write LinkedIn posts that sound like a specific human being, not like \
a content marketing team.

Hard rules, no exceptions:
- Never open with "In today's fast-paced world", "Let's be honest", "Here's the thing", \
"I've been thinking a lot about", or any variant of "Unpopular opinion".
- No emoji bullet lists. No "🚀". At most one emoji in the entire post, and usually zero.
- Every claim gets a concrete number, a named example, or a specific scenario. If you cannot \
be specific, cut the claim.
- Write at an 8th grade reading level. Short sentences. Cut every adverb you can.
- Never use: leverage, unlock, game-changer, dive deep, synergy, robust, seamless, \
in the realm of, it's not X, it's Y.
- The post must be something the author would be comfortable being quoted on. No invented \
statistics, no fake case studies, no fabricated client results.

You are given the author's profile and their recent post openings. Do not repeat the \
structure or subject of a recent post."""


class Generator:
    """Wraps the Claude client and turns a client profile into finished posts."""

    def __init__(self, settings: Settings):
        settings.require_claude()
        import anthropic  # imported lazily so --help works without the SDK installed

        self.settings = settings
        self.client = anthropic.Anthropic(api_key=settings.claude_api_key)

    def _prompt(
        self, client: Client, count: int, recent_hooks: list[str], used_topics: list[str]
    ) -> str:
        lines = [
            f"Write {count} LinkedIn post(s) for this author.",
            "",
            "AUTHOR PROFILE",
            f"Name / brand: {client.name}",
            f"Role: {client.role or 'not specified'}",
            f"Field: {client.niche}",
            f"Writing for: {client.audience}",
            f"Tone: {client.tone}",
            f"What a good post achieves: {client.goal}",
        ]
        if client.hashtags:
            lines.append(f"Preferred hashtags: {', '.join(client.hashtags)}")
        if client.banned_phrases:
            lines.append(f"Never use these words or phrases: {', '.join(client.banned_phrases)}")
        lines += ["", f"VISUAL STYLE for image prompts: {client.image_style}"]

        if client.topics:
            pool = [t for t in client.topics if t not in used_topics] or client.topics
            picks = random.sample(pool, min(count, len(pool)))
            lines += ["", "COVER THESE TOPICS (one post each):"]
            lines += [f"- {t}" for t in picks]
        else:
            lines += [
                "",
                "Choose topics yourself from the author's field. Pick things the author would "
                "know from experience, not textbook advice.",
            ]

        if recent_hooks:
            lines += ["", "RECENT OPENING LINES — do not repeat these angles:"]
            lines += [f"- {h}" for h in recent_hooks[-12:]]

        lines += ["", "Call emit_posts with the finished posts."]
        return "\n".join(lines)

    def generate(
        self,
        client: Client,
        count: int = 1,
        recent_hooks: list[str] | None = None,
        used_topics: list[str] | None = None,
    ) -> list[Post]:
        message = self.client.messages.create(
            model=self.settings.model,
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            tools=[POST_SCHEMA],
            tool_choice={"type": "tool", "name": "emit_posts"},
            messages=[
                {
                    "role": "user",
                    "content": self._prompt(
                        client, count, recent_hooks or [], used_topics or []
                    ),
                }
            ],
        )

        payload: dict[str, Any] | None = None
        for block in message.content:
            if block.type == "tool_use" and block.name == "emit_posts":
                payload = block.input
                break
        if payload is None:
            raise RuntimeError("Claude did not return posts. Try again or check the model name.")

        return [
            Post(
                hook=item["hook"].strip(),
                body=item["body"].strip(),
                hashtags=[h.lstrip("#") for h in item.get("hashtags", [])],
                topic=item.get("topic", ""),
                image_prompt=item.get("image_prompt", ""),
            )
            for item in payload.get("posts", [])
        ]
