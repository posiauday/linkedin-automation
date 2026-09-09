#!/usr/bin/env python3
"""Prospect sample generator — the outreach tool.

Point it at someone you want as a client. It writes five posts in their voice
and produces a shareable HTML page plus a DM you can paste into LinkedIn.

  python sample.py --name "Sarah Chen" --role "Founder" \
      --niche "recruitment tech" --company "Hirefast"

Giving something useful away before asking for money is the whole strategy.
A stranger ignores a pitch. A stranger reads five posts written for them.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine.config import Client, Settings  # noqa: E402
from engine.generator import Generator  # noqa: E402
from engine.store import Post  # noqa: E402

SAMPLES_DIR = Path(__file__).resolve().parent / "samples"

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
  :root {{ --ink:#12161c; --muted:#5b6673; --line:#e3e7ec; --bg:#fbfcfd; --accent:#1f4fd8; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
    font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif; }}
  .wrap {{ max-width:720px; margin:0 auto; padding:56px 24px 80px; }}
  .eyebrow {{ font-size:12px; letter-spacing:.14em; text-transform:uppercase;
    color:var(--muted); margin:0 0 12px; }}
  h1 {{ font-size:clamp(28px,5vw,40px); line-height:1.15; margin:0 0 16px; letter-spacing:-.02em; }}
  .lede {{ font-size:18px; color:var(--muted); margin:0 0 8px; }}
  .card {{ background:#fff; border:1px solid var(--line); border-radius:14px;
    padding:28px; margin:20px 0; }}
  .num {{ font-size:12px; font-weight:600; letter-spacing:.1em; text-transform:uppercase;
    color:var(--accent); margin:0 0 14px; }}
  .hook {{ font-size:19px; font-weight:650; line-height:1.4; margin:0 0 14px;
    letter-spacing:-.01em; }}
  .body p {{ margin:0 0 13px; white-space:pre-wrap; }}
  .tags {{ color:var(--accent); font-size:14px; margin:16px 0 0; }}
  .meta {{ font-size:13px; color:var(--muted); border-top:1px solid var(--line);
    margin-top:20px; padding-top:14px; }}
  .cta {{ background:var(--ink); color:#fff; border-radius:14px; padding:32px; margin-top:40px; }}
  .cta h2 {{ margin:0 0 12px; font-size:22px; letter-spacing:-.01em; }}
  .cta p {{ margin:0 0 10px; color:#c6cdd6; }}
  .cta strong {{ color:#fff; }}
  hr.rule {{ border:0; border-top:1px solid var(--line); margin:40px 0; }}
  .foot {{ font-size:13px; color:var(--muted); text-align:center; margin-top:36px; }}
</style></head><body><div class="wrap">
<p class="eyebrow">Written for {who}</p>
<h1>{heading}</h1>
<p class="lede">{lede}</p>
<hr class="rule">
{cards}
<div class="cta">
  <h2>Where these came from</h2>
  <p>These were not written by hand. They came out of a content engine
     configured to your field, your audience, and your way of talking.</p>
  <p>Once it is set up, it produces posts like this on a schedule and publishes
     them to your LinkedIn through the official API. You approve what goes out,
     or let it run.</p>
  <p><strong>Want it running on your account? Reply to the message I sent this with.</strong></p>
</div>
<p class="foot">Generated {stamp} · No obligation, keep the posts either way.</p>
</div></body></html>
"""

CARD = """<div class="card">
  <p class="num">Post {n}</p>
  <p class="hook">{hook}</p>
  <div class="body">{body}</div>
  <p class="tags">{tags}</p>
  <p class="meta">Angle: {topic}</p>
</div>"""

DM = """Hi {first} — no pitch in this message, just something you can use.

I built a tool that writes LinkedIn posts in a specific person's voice. I ran it \
on your profile as a test and it produced five posts about {niche} that I think \
actually sound like you.

They're here, free, use them or don't: {link}

If you want the thing that produced them running on your account, tell me and \
I'll explain how it works.
"""

FOLLOW_UP = """Hi {first} — following up once on the posts I sent over.

If they weren't right, that's useful to know and I'll leave it there. If they \
were close, the setup takes me about a day and then it runs on its own.

Either answer is fine, just don't want to leave it hanging."""


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "prospect"


def render_body(text: str) -> str:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return "".join(f"<p>{html.escape(p)}</p>" for p in paragraphs)


def build_page(prospect: str, niche: str, posts: list[Post]) -> str:
    cards = "\n".join(
        CARD.format(
            n=i,
            hook=html.escape(p.hook),
            body=render_body(p.body),
            tags=html.escape(" ".join(f"#{t}" for t in p.hashtags)),
            topic=html.escape(p.topic),
        )
        for i, p in enumerate(posts, 1)
    )
    return PAGE.format(
        title=f"5 LinkedIn posts for {prospect}",
        who=html.escape(prospect),
        heading="Five posts you could publish this week",
        lede=html.escape(
            f"Drafted for {prospect} on {niche}. Copy any of them straight into LinkedIn."
        ),
        cards=cards,
        stamp=datetime.now(timezone.utc).strftime("%d %b %Y"),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--name", required=True, help="prospect's full name")
    parser.add_argument("--niche", required=True, help="what they do or sell")
    parser.add_argument("--role", default="Founder")
    parser.add_argument("--company", default="")
    parser.add_argument("--audience", default="", help="who they sell to")
    parser.add_argument("--count", "-n", type=int, default=5)
    args = parser.parse_args()

    prospect = Client(
        slug=slugify(args.name),
        name=args.name,
        role=args.role + (f" at {args.company}" if args.company else ""),
        niche=args.niche,
        audience=args.audience or f"buyers and peers in {args.niche}",
        tone="direct, specific, experienced, sounds like a practitioner not a marketer",
        goal="build authority and attract inbound interest",
    )

    settings = Settings()
    print(f"Writing {args.count} posts for {args.name}...")
    try:
        posts = Generator(settings).generate(prospect, count=args.count)
    except RuntimeError as exc:
        print(f"error: {exc}")
        return 1

    SAMPLES_DIR.mkdir(exist_ok=True)
    out = SAMPLES_DIR / f"{prospect.slug}.html"
    out.write_text(build_page(args.name, args.niche, posts))

    first = args.name.split()[0]
    (SAMPLES_DIR / f"{prospect.slug}-dm.txt").write_text(
        DM.format(first=first, niche=args.niche, link="<PASTE LINK HERE>")
        + "\n\n--- FOLLOW UP (send 2 days later) ---\n\n"
        + FOLLOW_UP.format(first=first)
    )

    print(f"\nSample page:  {out}")
    print(f"DM script:    {SAMPLES_DIR / f'{prospect.slug}-dm.txt'}")
    print("\nNext: host the HTML anywhere with a link, paste the link into the DM, send.\n")
    for i, post in enumerate(posts, 1):
        print(f"  {i}. {post.hook[:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
