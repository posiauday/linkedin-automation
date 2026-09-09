"""Document carousels — the highest-performing format on LinkedIn.

Carousels are PDFs uploaded as document posts. They out-engage text-only posts
by roughly 6x, because readers swipe and swiping is dwell time.

Three steps: Claude writes the slides, Chromium renders them to a square PDF,
the Documents API uploads it. Rendering needs Playwright:

    pip install playwright && playwright install chromium
"""

from __future__ import annotations

import html
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from .config import Client, Settings

SLIDE_PX = 1080  # square renders identically on desktop and mobile feeds

CAROUSEL_SCHEMA = {
    "name": "emit_carousel",
    "description": "Return a finished LinkedIn document carousel.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": (
                    "Document title shown above the carousel in the feed. Under 60 "
                    "characters, concrete, no colon-subtitle."
                ),
            },
            "caption": {
                "type": "string",
                "description": (
                    "The post text introducing the carousel. 40-80 words. First line "
                    "must work alone. Ends with a question. No links — posts with "
                    "external links lose about 60% of their reach."
                ),
            },
            "hashtags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3-5 hashtags, no '#' prefix.",
            },
            "slides": {
                "type": "array",
                "minItems": 6,
                "maxItems": 10,
                "description": (
                    "6-10 slides. Slide 1 is the hook. The middle slides are one "
                    "concrete step or idea each. The last slide is the takeaway and "
                    "an invitation to comment."
                ),
                "items": {
                    "type": "object",
                    "properties": {
                        "kind": {
                            "type": "string",
                            "enum": ["hook", "point", "close"],
                            "description": "hook for slide 1, close for the last, point for the rest.",
                        },
                        "headline": {
                            "type": "string",
                            "description": "Under 60 characters. Readable at a glance on a phone.",
                        },
                        "body": {
                            "type": "string",
                            "description": (
                                "Under 220 characters. One idea. A slide nobody can read "
                                "in three seconds is a slide nobody reads."
                            ),
                        },
                    },
                    "required": ["kind", "headline", "body"],
                },
            },
        },
        "required": ["title", "caption", "hashtags", "slides"],
    },
}

SYSTEM = """You design LinkedIn document carousels. A carousel earns its reach by \
being swiped, so every slide has to make the next one worth seeing.

Structure:
- Slide 1 is the hook. A specific claim, number, or moment. Not a title card.
- Middle slides carry one concrete idea each, in a sequence that goes somewhere.
- The last slide lands the takeaway and invites a comment.

Hard rules:
- Every slide must be readable in about three seconds. Under 60 characters of \
headline, under 220 of body.
- Specifics only: numbers, named examples, real scenarios. Never invent a \
statistic or a client result.
- Never use: leverage, unlock, game-changer, dive deep, synergy, robust, \
seamless, "it's not X, it's Y".
- No emoji. No "In today's fast-paced world", "Let's be honest", "Unpopular opinion".
- No links anywhere: LinkedIn suppresses posts carrying them by about 60%."""


@dataclass
class Carousel:
    title: str
    caption: str
    hashtags: list[str] = field(default_factory=list)
    slides: list[dict] = field(default_factory=list)
    pdf_path: str | None = None
    cost_usd: float = 0.0

    @property
    def full_caption(self) -> str:
        tags = " ".join(f"#{t.lstrip('#')}" for t in self.hashtags)
        return f"{self.caption.strip()}\n\n{tags}".strip()


def generate(settings: Settings, client: Client, topic: str | None = None) -> Carousel:
    settings.require_claude()
    import anthropic

    lines = [
        "Write a LinkedIn document carousel for this author.",
        "",
        f"Author: {client.name}",
        f"Role: {client.role or 'not specified'}",
        f"Field: {client.niche}",
        f"Audience: {client.audience}",
        f"Tone: {client.tone}",
    ]
    if client.banned_phrases:
        lines.append(f"Never use: {', '.join(client.banned_phrases)}")
    if client.hashtags:
        lines.append(f"Preferred hashtags: {', '.join(client.hashtags)}")
    lines += ["", f"Topic: {topic}" if topic else
              "Pick a topic from the author's field that they would know from experience."]
    lines += ["", "Call emit_carousel."]

    message = anthropic.Anthropic(api_key=settings.claude_api_key).messages.create(
        model=settings.model,
        max_tokens=4000,
        system=SYSTEM,
        tools=[CAROUSEL_SCHEMA],
        tool_choice={"type": "tool", "name": "emit_carousel"},
        messages=[{"role": "user", "content": "\n".join(lines)}],
    )
    from .generator import estimate_cost

    for block in message.content:
        if block.type == "tool_use":
            data = block.input
            return Carousel(
                title=data["title"].strip(),
                caption=data["caption"].strip(),
                hashtags=[h.lstrip("#") for h in data.get("hashtags", [])],
                slides=data.get("slides", []),
                cost_usd=estimate_cost(settings.model, message.usage),
            )
    raise RuntimeError("Claude returned no carousel. Try again.")


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

SLIDE_CSS = """
  @page {{ size: {px}px {px}px; margin: 0; }}
  * {{ box-sizing: border-box; margin: 0; }}
  body {{ font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
         -webkit-font-smoothing: antialiased; }}
  .s {{ width: {px}px; height: {px}px; padding: 92px 88px; display: flex;
       flex-direction: column; justify-content: space-between;
       background: {bg}; color: {fg}; page-break-after: always;
       position: relative; overflow: hidden; }}
  .s:last-child {{ page-break-after: auto; }}
  .s.hook {{ background: {ink}; color: {paper}; }}
  .s.close {{ background: {accent}; color: #fff; }}
  .num {{ font-size: 22px; letter-spacing: .22em; text-transform: uppercase;
         font-weight: 600; opacity: .5; }}
  .mid {{ display: flex; flex-direction: column; justify-content: center; flex: 1; }}
  h2 {{ font-size: 74px; line-height: 1.06; letter-spacing: -.025em; font-weight: 700; }}
  .s.hook h2 {{ font-size: 88px; }}
  p {{ font-size: 34px; line-height: 1.42; margin-top: 34px; opacity: .88;
      max-width: 24ch; }}
  .foot {{ display: flex; justify-content: space-between; align-items: flex-end;
          font-size: 24px; opacity: .55; }}
  .rule {{ width: 96px; height: 6px; background: currentColor; opacity: .32;
          margin-top: 40px; }}
"""


def _slide_html(carousel: Carousel, client: Client) -> str:
    palette = dict(
        px=SLIDE_PX, bg="#EAEDE6", fg="#161A16",
        ink="#161A16", paper="#EAEDE6", accent="#C0402A",
    )
    total = len(carousel.slides)
    parts = []
    for index, slide in enumerate(carousel.slides, 1):
        kind = slide.get("kind", "point")
        parts.append(
            f'<section class="s {html.escape(kind)}">'
            f'<div class="num">{index:02d} / {total:02d}</div>'
            f'<div class="mid"><h2>{html.escape(slide.get("headline", ""))}</h2>'
            f'<p>{html.escape(slide.get("body", ""))}</p><div class="rule"></div></div>'
            f'<div class="foot"><span>{html.escape(client.name)}</span>'
            f"<span>{'swipe →' if index < total else ''}</span></div>"
            f"</section>"
        )
    css = SLIDE_CSS.format(**palette)
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{''.join(parts)}</body></html>"


def render_pdf(carousel: Carousel, client: Client, destination: Path) -> Path:
    """Render the slides to a PDF. Raises RuntimeError with a fix if it cannot."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Carousel rendering needs Playwright:\n"
            "  pip install playwright && playwright install chromium"
        ) from exc

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "slides.html"
        # The document declares UTF-8 and the slides contain an arrow glyph, so
        # the encoding cannot be left to the platform default.
        source.write_text(_slide_html(carousel, client), encoding="utf-8")
        launch: dict = {}
        for candidate in ("/opt/pw-browsers/chromium", shutil.which("chromium")):
            if candidate and Path(candidate).is_file():
                launch["executable_path"] = candidate
                break
        with sync_playwright() as pw:
            browser = pw.chromium.launch(**launch)
            page = browser.new_page(viewport={"width": SLIDE_PX, "height": SLIDE_PX})
            page.goto(source.as_uri())
            page.pdf(
                path=str(destination),
                width=f"{SLIDE_PX}px",
                height=f"{SLIDE_PX}px",
                print_background=True,
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
            )
            browser.close()
    carousel.pdf_path = str(destination)
    return destination
