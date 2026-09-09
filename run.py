#!/usr/bin/env python3
"""LinkedIn Content Engine - command line interface.

  python run.py whoami   --client acme          # find your LinkedIn person ID
  python run.py generate --client acme -n 5     # generate, save, do not publish
  python run.py publish  --client acme          # publish the oldest unpublished post
  python run.py run      --client acme          # generate one and publish it
  python run.py list     --client acme          # show what is queued
  python run.py approve  --client acme --id 3f2a  # approve one post (or all, no --id)
  python run.py carousel --client acme          # document carousel (out-engages text ~6x)
  python run.py metrics  --client acme          # pull reactions/comments for reporting
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine.config import Client, Settings  # noqa: E402
from engine import carousel as carousel_mod  # noqa: E402
from engine.generator import Generator  # noqa: E402
from engine.images import ImageGenerator  # noqa: E402
from engine.linkedin import LinkedInError, Publisher  # noqa: E402
from engine.store import Post, Store  # noqa: E402


def _preview(post: Post) -> None:
    print("-" * 68)
    if post.kind == "carousel":
        print(f"[carousel: {post.doc_title}]")
    print(post.full_text)
    if post.image_path:
        print(f"[image: {post.image_path}]")
    print("-" * 68)


def cmd_whoami(args, settings: Settings) -> int:
    client = Client.load(args.client)
    try:
        info = Publisher(settings, client).whoami()
    except LinkedInError as exc:
        print(f"error: {exc}")
        return 1
    print(f"Authenticated as: {info.get('name', 'unknown')}")
    print(f"\nAdd this to your .env / GitHub secrets:")
    print(f"  {client.linkedin_person_env}={info.get('sub', '')}")
    return 0


def cmd_generate(args, settings: Settings) -> int:
    client = Client.load(args.client)
    store = Store(client)
    generator = Generator(settings)
    images = ImageGenerator(settings)

    print(f"Generating {args.count} post(s) for {client.name}...")
    posts = generator.generate(
        client,
        count=args.count,
        recent_hooks=store.recent_hooks(),
        used_topics=store.used_topics(),
    )

    for index, post in enumerate(posts, 1):
        if images.enabled and post.image_prompt:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            saved = images.generate(
                post.image_prompt, client.output_dir / f"image_{stamp}_{index}.png"
            )
            if saved:
                post.image_path = str(saved)
        path = store.save(post)
        _preview(post)
        print(f"saved -> {path}\n")

    print(f"Done. {len(posts)} post(s) queued in {client.output_dir}")
    return 0


def cmd_publish(args, settings: Settings) -> int:
    client = Client.load(args.client)
    store = Store(client)

    pending = store.pending_publish()
    if settings.require_approval:
        pending = [p for p in pending if p.approved]
        if not pending:
            print("Nothing approved to publish. Approve a post first:")
            print(f"  python run.py list --client {client.slug}")
            print(f"  python run.py approve --client {client.slug} --id <id>")
            return 1
    if not pending:
        print("Nothing queued to publish. Run 'generate' first.")
        return 1

    post = pending[0]
    _preview(post)

    if not settings.publish:
        print("DRY RUN - ENABLE_LINKEDIN_POSTING is not true, so nothing was sent.")
        print("Set ENABLE_LINKEDIN_POSTING=true when you are ready to go live.")
        return 0

    publisher = Publisher(settings, client)
    try:
        if post.kind == "carousel" and post.pdf_path:
            urn = publisher.publish_document(
                post.full_text, Path(post.pdf_path), post.doc_title or post.topic
            )
        else:
            urn = publisher.publish(
                post.full_text, Path(post.image_path) if post.image_path else None
            )
    except LinkedInError as exc:
        print(f"error: {exc}")
        post.error = str(exc)
        store.save(post)
        return 1

    post.published = True
    post.linkedin_urn = urn
    store.save(post)
    print(f"Published: {urn}")
    return 0


def cmd_run(args, settings: Settings) -> int:
    args.count = 1
    if cmd_generate(args, settings) != 0:
        return 1
    return cmd_publish(args, settings)


def cmd_list(args, settings: Settings) -> int:
    client = Client.load(args.client)
    posts = Store(client).load_all()
    if not posts:
        print(f"No posts yet for {client.name}.")
        return 0
    spend = sum(p.cost_usd for p in posts)
    print(f"{client.name}: {len(posts)} post(s), ${spend:.4f} generation cost\n")
    for post in posts:
        print(f"  {post.id}  [{post.state:9}] {post.created_at[:16]}  {post.hook[:56]}")
    return 0


def cmd_carousel(args, settings: Settings) -> int:
    """Generate a document carousel: the format that out-engages text ~6x."""
    client = Client.load(args.client)
    store = Store(client)

    print(f"Writing a carousel for {client.name}...")
    deck = carousel_mod.generate(settings, client, topic=args.topic)

    print(f"\n  {deck.title}\n")
    for index, slide in enumerate(deck.slides, 1):
        print(f"  {index:2}. {slide.get('headline', '')}")
    print()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    destination = client.output_dir / f"carousel_{stamp}.pdf"
    try:
        carousel_mod.render_pdf(deck, client, destination)
    except RuntimeError as exc:
        print(f"error: {exc}")
        return 1
    print(f"PDF: {destination}")

    post = Post(
        hook=deck.caption.split("\n")[0][:200],
        body="\n".join(deck.caption.split("\n")[1:]).strip(),
        hashtags=deck.hashtags,
        topic=args.topic or deck.title,
        kind="carousel",
        pdf_path=str(destination),
        doc_title=deck.title,
    )
    path = store.save(post)
    print(f"Queued: {path}")
    print(f"\nApprove and publish it with:")
    print(f"  python run.py approve --client {client.slug} --id {post.id}")
    print(f"  python run.py publish --client {client.slug}")
    return 0


def cmd_metrics(args, settings: Settings) -> int:
    """Pull reactions and comments for published posts. This is the reporting
    clients actually ask for, and the proof that raises your price."""
    client = Client.load(args.client)
    store = Store(client)
    posts = store.published()
    if not posts:
        print(f"No published posts for {client.name} yet.")
        return 0

    publisher = Publisher(settings, client)
    updated = 0
    for post in posts:
        try:
            stats = publisher.engagement(post.linkedin_urn)
        except LinkedInError as exc:
            print(f"error: {exc}")
            return 1
        if not stats:
            continue
        post.reactions = stats.get("reactions", 0)
        post.comments = stats.get("comments", 0)
        post.measured_at = datetime.now(timezone.utc).isoformat()
        store.save(post)
        updated += 1

    fresh = store.published()
    total = sum(p.engagement for p in fresh)
    carousels = [p for p in fresh if p.kind == "carousel"]
    texts = [p for p in fresh if p.kind != "carousel"]

    print(f"{client.name}: measured {updated} of {len(posts)} published post(s)\n")
    for post in sorted(fresh, key=lambda p: p.engagement, reverse=True)[:10]:
        mark = "carousel" if post.kind == "carousel" else "text"
        print(f"  {post.reactions:4} reactions {post.comments:3} comments  "
              f"[{mark:8}] {post.hook[:44]}")
    print(f"\n  total engagement: {total}")
    if carousels and texts:
        ca = sum(p.engagement for p in carousels) / len(carousels)
        ta = sum(p.engagement for p in texts) / len(texts)
        print(f"  carousels average {ca:.1f} vs text {ta:.1f}"
              + (f" ({ca / ta:.1f}x)" if ta else ""))
    return 0


def _set_approval(args, approved: bool) -> int:
    client = Client.load(args.client)
    store = Store(client)

    if args.id:
        post = store.get(args.id)
        if not post:
            print(f"error: no post matching id {args.id!r} for {client.slug}")
            return 1
        targets = [post]
    else:
        targets = [p for p in store.load_all() if not p.published and not p.error]
        if not targets:
            print("Nothing to act on.")
            return 1

    for post in targets:
        post.approved = approved
        store.save(post)

    verb = "Approved" if approved else "Unapproved"
    print(f"{verb} {len(targets)} post(s) for {client.name}")
    return 0


def cmd_approve(args, settings: Settings) -> int:
    return _set_approval(args, True)


def cmd_reject(args, settings: Settings) -> int:
    return _set_approval(args, False)


def cmd_clients(args, settings: Settings) -> int:
    clients = Client.load_all()
    if not clients:
        print("No client profiles in clients/. Copy clients/_template.yaml to get started.")
        return 0
    for client in clients:
        posts = Store(client).load_all()
        counts = {k: 0 for k in ("queued", "approved", "published", "error")}
        for post in posts:
            counts[post.state] += 1
        spend = sum(p.cost_usd for p in posts)
        print(
            f"  {client.slug:18} {client.name:24} "
            f"{counts['published']:3} pub  {counts['approved']:3} appr  "
            f"{counts['queued']:3} queued  ${spend:.4f}"
        )
    return 0


COMMANDS = {
    "approve": cmd_approve,
    "carousel": cmd_carousel,
    "metrics": cmd_metrics,
    "reject": cmd_reject,
    "whoami": cmd_whoami,
    "generate": cmd_generate,
    "publish": cmd_publish,
    "run": cmd_run,
    "list": cmd_list,
    "clients": cmd_clients,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=sorted(COMMANDS))
    parser.add_argument("--client", "-c", default="default", help="client slug (clients/<slug>.yaml)")
    parser.add_argument("--count", "-n", type=int, default=1, help="how many posts to generate")
    parser.add_argument("--id", help="post id for approve/reject; omit to act on all queued")
    parser.add_argument("--topic", help="topic for the carousel; omit to let Claude choose")
    args = parser.parse_args()

    settings = Settings()
    try:
        return COMMANDS[args.command](args, settings)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
