"""
Central settings — loaded from environment variables / .env file
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # ── Anthropic (Claude) ───────────────────────────────────────
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"

    # ── ElevenLabs TTS ───────────────────────────────────────────
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

    # ── Pexels (stock footage) ────────────────────────────────────
    PEXELS_API_KEY: str = os.getenv("PEXELS_API_KEY", "")

    # ── YouTube ──────────────────────────────────────────────────
    YOUTUBE_CLIENT_SECRETS: str = os.getenv(
        "YOUTUBE_CLIENT_SECRETS", "config/client_secrets.json"
    )
    YOUTUBE_CREDENTIALS_FILE: str = "config/youtube_credentials.json"
    YOUTUBE_SCOPES: list = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube",
    ]
    YOUTUBE_CATEGORY_ID: str = "22"   # People & Blogs (change per niche)
    YOUTUBE_PRIVACY: str = "public"   # public | unlisted | private

    # ── Channel defaults ─────────────────────────────────────────
    DEFAULT_NICHE: str = os.getenv("DEFAULT_NICHE", "personal finance")
    DEFAULT_TOPIC: str = os.getenv("DEFAULT_TOPIC", "")   # empty = AI picks

    # ── Video settings ───────────────────────────────────────────
    VIDEO_RESOLUTION: tuple = (1920, 1080)
    VIDEO_FPS: int = 30
    FONT_PATH: str = os.getenv("FONT_PATH", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    SUBTITLE_FONT_SIZE: int = 48
    SUBTITLE_COLOR: str = "white"
    SUBTITLE_STROKE_COLOR: str = "black"
    SUBTITLE_STROKE_WIDTH: int = 3

    # ── Paths ────────────────────────────────────────────────────
    ROOT_DIR: Path = Path(__file__).parent.parent
    OUTPUT_DIR: Path = ROOT_DIR / "output"
    ASSETS_DIR: Path = ROOT_DIR / "assets"
