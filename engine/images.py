"""Image generation. Optional: the engine runs fine without an OpenAI key."""

from __future__ import annotations

from pathlib import Path

import requests

from .config import Settings

ENDPOINT = "https://api.openai.com/v1/images/generations"


class ImageGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def enabled(self) -> bool:
        return self.settings.generate_images and bool(self.settings.openai_api_key)

    def generate(self, prompt: str, destination: Path) -> Path | None:
        """Generate an image and write it to `destination`. Returns None on any failure —
        a missing image should never stop a post from going out."""
        if not self.enabled:
            return None
        try:
            response = requests.post(
                ENDPOINT,
                headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
                json={
                    "model": "dall-e-3",
                    "prompt": prompt,
                    "n": 1,
                    "size": "1024x1024",
                    "quality": "standard",
                },
                timeout=120,
            )
            response.raise_for_status()
            url = response.json()["data"][0]["url"]

            image = requests.get(url, timeout=120)
            image.raise_for_status()
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(image.content)
            return destination
        except (requests.RequestException, KeyError, IndexError) as exc:
            print(f"  image generation failed ({exc}); continuing without an image")
            return None
