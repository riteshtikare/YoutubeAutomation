"""
AI YouTube Automation Pipeline
Full end-to-end: Topic → Script → Voiceover → Video → Upload
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

from agents.script_agent import ScriptAgent
from agents.tts_agent import TTSAgent
from agents.video_agent import VideoAgent
from agents.thumbnail_agent import ThumbnailAgent
from agents.upload_agent import UploadAgent
from config.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)


def run_pipeline(topic: str = None, niche: str = None):
    cfg = Settings()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(cfg.OUTPUT_DIR) / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    log.info("═" * 60)
    log.info("  🎬  AI YouTube Automation Pipeline")
    log.info("═" * 60)

    # ── 1. Script Generation ──────────────────────────────────────
    log.info("STEP 1 ▶ Generating script …")
    script_agent = ScriptAgent(cfg)
    script_data = script_agent.generate(
        topic=topic or cfg.DEFAULT_TOPIC,
        niche=niche or cfg.DEFAULT_NICHE,
    )
    script_path = run_dir / "script.json"
    script_path.write_text(json.dumps(script_data, indent=2))
    log.info(f"  ✓  Script saved → {script_path}")

    # ── 2. Text-to-Speech ────────────────────────────────────────
    log.info("STEP 2 ▶ Generating voiceover …")
    tts_agent = TTSAgent(cfg)
    audio_path = tts_agent.generate(
        text=script_data["narration"],
        out_path=run_dir / "voiceover.mp3",
    )
    log.info(f"  ✓  Audio saved → {audio_path}")

    # ── 3. Video Assembly ────────────────────────────────────────
    log.info("STEP 3 ▶ Assembling video …")
    video_agent = VideoAgent(cfg)
    video_path = video_agent.assemble(
        script_data=script_data,
        audio_path=audio_path,
        out_path=run_dir / "final_video.mp4",
    )
    log.info(f"  ✓  Video saved → {video_path}")

    # ── 4. Thumbnail ─────────────────────────────────────────────
    log.info("STEP 4 ▶ Creating thumbnail …")
    thumb_agent = ThumbnailAgent(cfg)
    thumb_path = thumb_agent.create(
        title=script_data["title"],
        out_path=run_dir / "thumbnail.png",
    )
    log.info(f"  ✓  Thumbnail saved → {thumb_path}")

    # ── 5. YouTube Upload ────────────────────────────────────────
    log.info("STEP 5 ▶ Uploading to YouTube …")
    upload_agent = UploadAgent(cfg)
    result = upload_agent.upload(
        video_path=video_path,
        thumbnail_path=thumb_path,
        title=script_data["title"],
        description=script_data["description"],
        tags=script_data["tags"],
    )
    log.info(f"  ✓  Uploaded! Video ID: {result.get('id', 'N/A')}")
    log.info(f"     URL: https://youtube.com/watch?v={result.get('id', '???')}")

    # ── Summary ──────────────────────────────────────────────────
    summary = {
        "timestamp": timestamp,
        "topic": script_data["title"],
        "audio": str(audio_path),
        "video": str(video_path),
        "thumbnail": str(thumb_path),
        "youtube_id": result.get("id"),
        "youtube_url": f"https://youtube.com/watch?v={result.get('id', '')}",
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    log.info("═" * 60)
    log.info("  🎉  Pipeline complete!")
    log.info("═" * 60)
    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI YouTube Automation Pipeline")
    parser.add_argument("--topic", type=str, help="Video topic override")
    parser.add_argument("--niche", type=str, help="Channel niche override")
    args = parser.parse_args()
    run_pipeline(topic=args.topic, niche=args.niche)
