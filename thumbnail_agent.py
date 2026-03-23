"""
ThumbnailAgent — generates eye-catching YouTube thumbnails with Pillow.
Downloads a relevant background from Pexels, overlays gradient + title text.
"""

import logging
import requests
import random
from pathlib import Path
from io import BytesIO

log = logging.getLogger(__name__)


class ThumbnailAgent:
    W, H = 1280, 720

    def __init__(self, cfg):
        self.cfg = cfg
        self.pexels_key = cfg.PEXELS_API_KEY

    def create(self, title: str, out_path: Path) -> Path:
        from PIL import Image, ImageDraw, ImageFilter, ImageFont
        import textwrap

        out_path = Path(out_path)
        img = self._get_background(title)

        # ── Dark gradient overlay ─────────────────────────────────
        overlay = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)
        for y in range(self.H):
            alpha = int(180 * (y / self.H) ** 0.5)
            draw_ov.line([(0, y), (self.W, y)], fill=(0, 0, 0, alpha))
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay).convert("RGB")

        # ── Text ──────────────────────────────────────────────────
        draw = ImageDraw.Draw(img)
        try:
            font_large = ImageFont.truetype(self.cfg.FONT_PATH, 80)
            font_small = ImageFont.truetype(self.cfg.FONT_PATH, 38)
        except Exception:
            font_large = ImageFont.load_default()
            font_small = font_large

        lines = textwrap.wrap(title.upper(), width=22)

        # Shadow
        y_start = self.H // 2 - len(lines) * 50
        for i, line in enumerate(lines):
            y = y_start + i * 95
            draw.text((62, y + 4), line, font=font_large, fill=(0, 0, 0, 180))
            draw.text((60, y), line, font=font_large, fill=(255, 220, 50))

        # Sub-label
        draw.text(
            (64, self.H - 70),
            "Watch till the end! 🔥",
            font=font_small,
            fill=(255, 255, 255),
        )

        img.save(str(out_path), "PNG")
        log.info(f"Thumbnail saved → {out_path}")
        return out_path

    # ── Background from Pexels ────────────────────────────────────
    def _get_background(self, query: str):
        from PIL import Image

        if self.pexels_key:
            try:
                headers = {"Authorization": self.pexels_key}
                params = {"query": query, "per_page": 10, "orientation": "landscape"}
                resp = requests.get(
                    "https://api.pexels.com/v1/search",
                    headers=headers, params=params, timeout=10,
                )
                resp.raise_for_status()
                photos = resp.json().get("photos", [])
                if photos:
                    photo = random.choice(photos)
                    img_url = photo["src"]["large2x"]
                    img_data = requests.get(img_url, timeout=20).content
                    img = Image.open(BytesIO(img_data)).convert("RGB")
                    return img.resize((self.W, self.H))
            except Exception as e:
                log.warning(f"Pexels thumbnail background failed: {e}")

        # Fallback: gradient background
        img = Image.new("RGB", (self.W, self.H))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        for x in range(self.W):
            r = int(20 + (x / self.W) * 60)
            g = int(10 + (x / self.W) * 30)
            b = int(80 + (x / self.W) * 100)
            draw.line([(x, 0), (x, self.H)], fill=(r, g, b))
        return img
