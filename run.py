#!/usr/bin/env python3
"""LinkedIn Content Engine - command line interface.

  python run.py whoami   --client acme          # find your LinkedIn person ID
  python run.py generate --client acme -n 5     # generate, save, do not publish
  python run.py publish  --client acme          # publish the oldest unpublished post
  python run.py run      --client acme          # generate one and publish it
  python run.py list     --client acme          # show what is queued
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine.config import Client, Settings  # noqa: E402
from engine.generator import Generator  # noqa: E402
from engine.images import ImageGenerator  # noqa: E402
from engine.linkedin import LinkedInError, Publisher  # noqa: E402
from engine.store import Post, Store  # noqa: E402


def _preview(post: Post) -> None:
    print("-" * 68)
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

    pending = [p for p in store.load_all() if not p.published and not p.error]
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
    print(f"{client.name}: {len(posts)} post(s)\n")
    for post in posts:
        state = "published" if post.published else ("error" if post.error else "queued")
        print(f"  [{state:9}] {post.created_at[:16]}  {post.hook[:60]}")
    return 0


def cmd_clients(args, settings: Settings) -> int:
    clients = Client.load_all()
    if not clients:
        print("No client profiles in clients/. Copy clients/_template.yaml to get started.")
        return 0
    for client in clients:
        posts = Store(client).load_all()
        published = sum(1 for p in posts if p.published)
        print(f"  {client.slug:20} {client.name:28} {published} published / {len(posts)} total")
    return 0


COMMANDS = {
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
    args = parser.parse_args()

    settings = Settings()
    try:
        return COMMANDS[args.command](args, settings)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
