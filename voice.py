#!/usr/bin/env python3
"""Voice profile builder — learn how someone writes from what they have written.

The client profile was the weakest part of this system: a hand-written guess at
someone's tone. This reads their actual posts and derives the profile from
evidence, quoting the lines it drew each conclusion from.

  python voice.py --posts their-posts.txt --slug acme --name "Sarah Chen"
  pbpaste | python voice.py --slug acme --name "Sarah Chen"

Separate posts with a line containing only --- (or a blank line will do).
Ten posts is enough. Twenty is better.

Use it on a client during onboarding, and on yourself before you sell anything.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine.config import CLIENTS_DIR, SLUG_PATTERN, Settings  # noqa: E402

MIN_POSTS = 3

VOICE_SCHEMA = {
    "name": "emit_voice",
    "description": "Return a voice profile derived from the writing samples.",
    "input_schema": {
        "type": "object",
        "properties": {
            "tone": {
                "type": "string",
                "description": (
                    "How this person actually writes, in one line a stranger could act "
                    "on. Describe observed habits, not compliments. Good: 'blunt, "
                    "leads with the mistake, short sentences, dry humour at own "
                    "expense'. Bad: 'engaging and professional'."
                ),
            },
            "niche": {"type": "string", "description": "What they demonstrably know about."},
            "audience": {
                "type": "string",
                "description": "Who they are visibly writing for, judged from the samples.",
            },
            "goal": {
                "type": "string",
                "description": "What a good post appears to be trying to achieve for them.",
            },
            "topics": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "5-8 topics they have first-hand authority on, drawn from what they "
                    "already wrote about. Phrase each as a post subject, not a category."
                ),
            },
            "hashtags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Hashtags they actually use, no '#'. Empty if they use none.",
            },
            "banned_phrases": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Words and phrases this person visibly avoids, or that would sound "
                    "wrong in their voice. Include corporate filler absent from their "
                    "writing. This list matters more than any other field."
                ),
            },
            "habits": {
                "type": "array",
                "description": "3-6 concrete structural habits, each with evidence.",
                "items": {
                    "type": "object",
                    "properties": {
                        "habit": {"type": "string", "description": "The habit, in a few words."},
                        "evidence": {
                            "type": "string",
                            "description": "A short quote from their own posts showing it.",
                        },
                    },
                    "required": ["habit", "evidence"],
                },
            },
            "avg_words": {"type": "integer", "description": "Typical post length in words."},
            "notes": {
                "type": "string",
                "description": (
                    "Anything a ghostwriter would get wrong on the first attempt. Be "
                    "specific and honest, including where the samples are too thin to tell."
                ),
            },
        },
        "required": ["tone", "niche", "audience", "goal", "topics", "hashtags",
                     "banned_phrases", "habits", "avg_words", "notes"],
    },
}

SYSTEM = """You analyse how a specific person writes so someone else can write as them \
without it being obvious.

Work only from the samples. Every conclusion must be traceable to something actually \
in the text — if the samples do not show it, say so in notes rather than inventing it.

What matters most, in order:
1. What they never say. Corporate filler absent from their writing is the strongest \
signal you have, and the banned list is what stops generated posts drifting into \
LinkedIn voice.
2. Structural habits: how they open, whether they use one-line paragraphs, whether \
they close on a question, how they handle numbers.
3. Vocabulary that is characteristically theirs.

Be blunt in the notes. "The samples are all wins, so I cannot tell how they write \
about failure" is more useful than a confident guess."""


def split_posts(raw: str) -> list[str]:
    """Split pasted posts. A --- line is the reliable separator; failing that,
    fall back to a blank line, which is what the help text promises."""
    if re.search(r"\n\s*-{3,}\s*\n", raw):
        chunks = re.split(r"\n\s*-{3,}\s*\n", raw)
    else:
        chunks = re.split(r"\n\s*\n+", raw)
    return [c.strip() for c in chunks if len(c.strip()) > 60]


def yaml_quote(value: str) -> str:
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def yaml_list(items: list) -> str:
    return "[" + ", ".join(yaml_quote(i) for i in items) + "]"


def build_yaml(data: dict, name: str, role: str) -> str:
    lines = [
        "# Derived by voice.py from this person's own posts.",
        "# Re-run it after they publish more; voice drifts.",
        "",
        f"name: {yaml_quote(name)}",
        f"role: {yaml_quote(role)}" if role else 'role: ""',
        f"niche: {yaml_quote(data['niche'])}",
        f"audience: {yaml_quote(data['audience'])}",
        f"tone: {yaml_quote(data['tone'])}",
        f"goal: {yaml_quote(data['goal'])}",
        "",
        "topics:",
    ]
    lines += [f"  - {yaml_quote(t)}" for t in data.get("topics", [])]
    lines += [
        "",
        f"hashtags: {yaml_list(data.get('hashtags', []))}",
        "",
        "# The most important field here. These are the words that would give it away.",
        f"banned_phrases: {yaml_list(data.get('banned_phrases', []))}",
        "",
        "image_style: >",
        "  clean minimalist editorial illustration, flat vector, generous whitespace,",
        "  muted professional palette, no text in image",
        "",
        "linkedin_token_env: \"LINKEDIN_ACCESS_TOKEN\"",
        "linkedin_person_env: \"LINKEDIN_PERSON_ID\"",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--posts", "-p", help="file of their posts; omit to read stdin")
    parser.add_argument("--slug", "-s", required=True, help="client slug to write")
    parser.add_argument("--name", "-n", required=True, help="their name")
    parser.add_argument("--role", "-r", default="", help="their role")
    parser.add_argument("--write", action="store_true",
                        help="write clients/<slug>.yaml instead of printing it")
    args = parser.parse_args()

    if not SLUG_PATTERN.match(args.slug):
        print(f"error: invalid slug {args.slug!r}. Use lowercase letters, digits, "
              "hyphens and underscores, starting with a letter or digit.")
        return 1

    if args.posts:
        path = Path(args.posts)
        if not path.exists():
            print(f"error: no file at {path}")
            return 1
        raw = path.read_text()
    elif not sys.stdin.isatty():
        raw = sys.stdin.read()
    else:
        print("error: pass --posts, or pipe their posts into stdin")
        return 1

    posts = split_posts(raw)
    if len(posts) < MIN_POSTS:
        print(f"error: found {len(posts)} post(s). Need at least {MIN_POSTS} to say "
              "anything useful — separate them with a --- line.")
        return 1

    settings = Settings()
    try:
        settings.require_claude()
    except RuntimeError as exc:
        print(f"error: {exc}")
        return 1

    import anthropic

    print(f"Reading {len(posts)} posts by {args.name}...")
    body = "\n\n--- POST ---\n\n".join(posts[:40])
    message = anthropic.Anthropic(api_key=settings.claude_api_key).messages.create(
        model=settings.model,
        max_tokens=4000,
        system=SYSTEM,
        tools=[VOICE_SCHEMA],
        tool_choice={"type": "tool", "name": "emit_voice"},
        messages=[{
            "role": "user",
            "content": (
                f"These are posts written by {args.name}"
                + (f", {args.role}" if args.role else "")
                + f".\n\n--- POST ---\n\n{body}\n\n--- END ---\n\nCall emit_voice."
            ),
        }],
    )

    data = None
    for block in message.content:
        if block.type == "tool_use":
            data = block.input
            break
    if data is None:
        print("error: no profile returned. Try again.")
        return 1

    print(f"\n  tone: {data['tone']}")
    print(f"  typical length: {data['avg_words']} words\n")
    print("  Habits observed:")
    for h in data.get("habits", []):
        print(f"    - {h['habit']}")
        print(f"        \"{h['evidence'][:88]}\"")
    print(f"\n  Never says: {', '.join(data.get('banned_phrases', [])[:8])}")
    print(f"\n  Notes: {data['notes']}\n")

    profile = build_yaml(data, args.name, args.role)
    if args.write:
        destination = CLIENTS_DIR / f"{args.slug}.yaml"
        if destination.exists():
            backup = destination.with_suffix(".yaml.bak")
            backup.write_text(destination.read_text())
            print(f"  existing profile backed up to {backup.name}")
        destination.write_text(profile)
        print(f"Wrote {destination}")
        print(f"\nCheck it, then: python run.py generate --client {args.slug} -n 5")
    else:
        print("-" * 68)
        print(profile, end="")
        print("-" * 68)
        print(f"\nRe-run with --write to save it to clients/{args.slug}.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
