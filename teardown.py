#!/usr/bin/env python3
"""Teardown generator — rewrite an existing post and explain what changed.

Paste in a post somebody already published. Get back a rewrite plus a short
explanation of each change. Two uses, both high value:

  1. Outreach. "I rewrote your post, here's why it works better." Far stronger
     than a pitch, because it is proof rather than a claim.
  2. Content. Publish the teardown yourself. Demonstrating the skill in public
     is the highest-leverage thing you can post while you have no case studies.

  python teardown.py --file post.txt --author "Sarah Chen"
  pbpaste | python teardown.py --author "Sarah Chen"

Only tear down a public post, and only rewrite someone's work publicly if you
are comfortable being seen doing it. Punching down reads badly and spreads fast.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine.config import Settings  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent / "samples"

SCHEMA = {
    "name": "emit_teardown",
    "description": "Return the rewritten post and the reasoning behind each change.",
    "input_schema": {
        "type": "object",
        "properties": {
            "verdict": {
                "type": "string",
                "description": (
                    "One sentence on what the original's central problem is. Specific and "
                    "fair. If the post is genuinely good, say so and focus on the one thing "
                    "that would sharpen it."
                ),
            },
            "original_hook": {
                "type": "string",
                "description": "The original's first line, quoted exactly.",
            },
            "rewritten_hook": {
                "type": "string",
                "description": "A replacement first line, under 120 characters.",
            },
            "rewritten_body": {
                "type": "string",
                "description": (
                    "The rewritten post after the hook. Same facts and same claims as the "
                    "original — never invent details the author did not state. Short "
                    "paragraphs separated by blank lines. Ends with one genuine question."
                ),
            },
            "changes": {
                "type": "array",
                "description": "3-5 specific changes, most important first.",
                "items": {
                    "type": "object",
                    "properties": {
                        "change": {"type": "string", "description": "What was changed, in a few words."},
                        "why": {
                            "type": "string",
                            "description": "Why it matters, one or two sentences. Mechanical, not vague.",
                        },
                    },
                    "required": ["change", "why"],
                },
            },
        },
        "required": ["verdict", "original_hook", "rewritten_hook", "rewritten_body", "changes"],
    },
}

SYSTEM = """You are an editor who rewrites LinkedIn posts. You are precise, fair, and \
never condescending.

Rules for the rewrite:
- Keep every fact, number and claim the author made. Never invent a detail, a \
statistic, or an outcome they did not state. If the original has no specifics, the \
rewrite has no specifics either — say so in the changes instead of inventing them.
- The first line must work alone. LinkedIn truncates around 120 characters, so the \
hook carries the whole post.
- Cut throat-clearing openers, emoji bullet lists, and hashtag padding.
- Never use: leverage, unlock, game-changer, dive deep, synergy, robust, seamless, \
"it's not X, it's Y".
- Short paragraphs. Blank line between each. 8th grade reading level.
- End on a real question, not "Thoughts?".

Rules for the critique:
- Be specific and mechanical. "The first line is a category label, not a claim" \
beats "the hook is weak".
- Be fair. If the post is good, say so. A teardown that manufactures problems to \
look clever is worthless and the author can tell.
- Never mock the author."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--file", "-f", help="file containing the post; omit to read stdin")
    parser.add_argument("--author", "-a", default="", help="who wrote it (for the page)")
    parser.add_argument("--context", "-c", default="", help="what the author does")
    parser.add_argument("--public", action="store_true",
                        help="frame the page as a public teardown rather than a private note")
    return parser.parse_args()


def read_post(args: argparse.Namespace) -> str:
    if args.file:
        path = Path(args.file)
        if not path.exists():
            raise SystemExit(f"error: no file at {path}")
        text = path.read_text()
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        raise SystemExit("error: pass --file, or pipe the post into stdin")
    text = text.strip()
    if len(text) < 40:
        raise SystemExit("error: that post is too short to tear down")
    return text


def generate(settings: Settings, post: str, author: str, context: str) -> dict:
    settings.require_claude()
    import anthropic

    who = author or "the author"
    prompt = (
        f"Rewrite this LinkedIn post and explain what you changed.\n\n"
        f"Author: {who}\n"
        + (f"What they do: {context}\n" if context else "")
        + f"\n--- ORIGINAL POST ---\n{post}\n--- END ---\n\n"
        "Call emit_teardown."
    )
    message = anthropic.Anthropic(api_key=settings.claude_api_key).messages.create(
        model=settings.model,
        max_tokens=3000,
        system=SYSTEM,
        tools=[SCHEMA],
        tool_choice={"type": "tool", "name": "emit_teardown"},
        messages=[{"role": "user", "content": prompt}],
    )
    for block in message.content:
        if block.type == "tool_use":
            return block.input
    raise RuntimeError("Claude returned no teardown. Try again.")


def paragraphs(text: str) -> str:
    return "".join(
        f"<p>{html.escape(p.strip())}</p>" for p in text.split("\n\n") if p.strip()
    )


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>
 :root{{--paper:#EAEDE6;--surface:#fff;--ink:#161A16;--body:#2C332C;--muted:#5C665C;
   --line:#D2D8CB;--signal:#C0402A;--good:#2F6B4F}}
 @media(prefers-color-scheme:dark){{:root{{--paper:#11140F;--surface:#181C16;--ink:#E8EDE3;
   --body:#C6CDC0;--muted:#8B9488;--line:#2E352B;--signal:#E4785F;--good:#7FBF9B}}}}
 *{{box-sizing:border-box}}
 body{{margin:0;background:var(--paper);color:var(--body);
   font:400 17px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
 .wrap{{max-width:720px;margin:0 auto;padding:56px 24px 88px}}
 .eyebrow{{font:500 12px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.14em;
   text-transform:uppercase;color:var(--muted);margin:0 0 18px}}
 h1{{font:400 clamp(30px,5.5vw,44px)/1.1 Georgia,"Times New Roman",serif;color:var(--ink);
   letter-spacing:-.02em;margin:0 0 18px;text-wrap:balance}}
 h2{{font:400 24px/1.25 Georgia,serif;color:var(--ink);margin:48px 0 14px}}
 p{{margin:0 0 15px;max-width:62ch}}
 .verdict{{font-size:19px;line-height:1.55;color:var(--ink);border-left:3px solid var(--signal);
   padding-left:18px;margin:0 0 12px}}
 .post{{background:var(--surface);border:1px solid var(--line);border-radius:4px;padding:24px}}
 .post.before{{opacity:.82}}
 .label{{font:500 10px/1 ui-monospace,monospace;letter-spacing:.16em;text-transform:uppercase;
   margin:0 0 14px}}
 .label.b{{color:var(--muted)}} .label.a{{color:var(--good)}}
 .hook{{font-size:17px;font-weight:600;color:var(--ink);margin:0 0 12px;line-height:1.5}}
 .post p{{margin:0 0 12px;max-width:none}}
 table{{width:100%;border-collapse:collapse;margin-top:8px}}
 td{{padding:16px 0;border-top:1px solid var(--line);vertical-align:top}}
 td.k{{width:34%;padding-right:22px;color:var(--ink);font-weight:600;font-size:15px}}
 td.v{{color:var(--muted);font-size:15px}}
 footer{{margin-top:56px;padding-top:20px;border-top:1px solid var(--line);
   font:400 13px/1.6 ui-monospace,monospace;color:var(--muted)}}
</style></head><body><div class="wrap">
<p class="eyebrow">{eyebrow}</p>
<h1>{heading}</h1>
<p class="verdict">{verdict}</p>

<h2>Before</h2>
<div class="post before"><p class="label b">As published</p>{before}</div>

<h2>After</h2>
<div class="post"><p class="label a">Rewritten</p>
<p class="hook">{hook}</p>{after}</div>

<h2>What changed</h2>
<table>{rows}</table>

<footer>{foot}</footer>
</div></body></html>"""


def main() -> int:
    args = parse_args()
    post = read_post(args)

    try:
        data = generate(Settings(), post, args.author, args.context)
    except RuntimeError as exc:
        print(f"error: {exc}")
        return 1

    slug = re.sub(r"[^a-z0-9]+", "-", (args.author or "teardown").lower()).strip("-")
    rows = "".join(
        f'<tr><td class="k">{html.escape(c["change"])}</td>'
        f'<td class="v">{html.escape(c["why"])}</td></tr>'
        for c in data.get("changes", [])
    )
    # Escaped once here: the author name is routinely pasted from a LinkedIn
    # profile, so it is untrusted input on a page that gets hosted publicly.
    who = html.escape(args.author or "this post")
    page = PAGE.format(
        title=f"Teardown: {who}",
        eyebrow="Post teardown" if args.public else "Written for you, no pitch",
        heading=f"A rewrite of {who}'s post" if args.author else "A rewrite",
        verdict=html.escape(data["verdict"]),
        before=paragraphs(post),
        hook=html.escape(data["rewritten_hook"]),
        after=paragraphs(data["rewritten_body"]),
        rows=rows,
        foot="Same facts, same claims, restructured. Nothing was invented."
        + ("" if args.public else " Yours to use or ignore."),
    )

    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / f"teardown-{slug}.html"
    out.write_text(page)

    print(f"\n{data['verdict']}\n")
    print(f"  before: {data['original_hook'][:70]}")
    print(f"  after:  {data['rewritten_hook'][:70]}\n")
    for c in data.get("changes", []):
        print(f"  - {c['change']}")
    print(f"\nPage: {out}")
    print(f"Generated {datetime.now(timezone.utc).strftime('%d %b %Y')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
