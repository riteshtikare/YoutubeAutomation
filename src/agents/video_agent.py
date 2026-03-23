"""
VideoAgent — downloads relevant stock clips from Pexels,
overlays subtitles, and assembles the final MP4 with MoviePy.
"""

import logging
import requests
import random
import textwrap
from pathlib import Path

log = logging.getLogger(__name__)


class VideoAgent:
    def __init__(self, cfg):
        self.cfg = cfg
        self.pexels_key = cfg.PEXELS_API_KEY
        self.resolution = cfg.VIDEO_RESOLUTION   # (1920, 1080)
        self.fps = cfg.VIDEO_FPS

    # ─────────────────────────────────────────────────────────────
    def assemble(self, script_data: dict, audio_path: Path, out_path: Path) -> Path:
        from moviepy.editor import (
            VideoFileClip, AudioFileClip, TextClip,
            CompositeVideoClip, concatenate_videoclips,
            ColorClip,
        )

        audio_path = Path(audio_path)
        out_path = Path(out_path)
        tmp_dir = out_path.parent / "clips"
        tmp_dir.mkdir(exist_ok=True)

        # ── Load audio ───────────────────────────────────────────
        audio = AudioFileClip(str(audio_path))
        total_duration = audio.duration

        # ── Fetch stock clips ────────────────────────────────────
        keywords = script_data.get("search_keywords", [script_data.get("title", "nature")])
        clip_paths = self._fetch_clips(keywords, tmp_dir, target_duration=total_duration)

        # ── Build background video ───────────────────────────────
        bg_clips = []
        accumulated = 0.0
        idx = 0
        while accumulated < total_duration:
            src = clip_paths[idx % len(clip_paths)]
            try:
                clip = VideoFileClip(str(src)).without_audio()
                clip = clip.resize(self.resolution)
                need = total_duration - accumulated
                if clip.duration > need:
                    clip = clip.subclip(0, need)
                bg_clips.append(clip)
                accumulated += clip.duration
                idx += 1
            except Exception as e:
                log.warning(f"Skipping clip {src}: {e}")
                idx += 1
                if idx > len(clip_paths) * 3:
                    break

        if not bg_clips:
            log.warning("No clips available, using black background.")
            bg_clips = [ColorClip(self.resolution, color=(0, 0, 0), duration=total_duration)]

        background = concatenate_videoclips(bg_clips, method="compose")
        background = background.set_duration(total_duration)

        # ── Subtitle overlay ─────────────────────────────────────
        subtitle_clips = self._make_subtitles(
            narration=script_data.get("narration", ""),
            total_duration=total_duration,
        )

        # ── Compose final video ──────────────────────────────────
        layers = [background] + subtitle_clips
        final = CompositeVideoClip(layers).set_audio(audio)
        final.write_videofile(
            str(out_path),
            fps=self.fps,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=str(out_path.parent / "temp_audio.m4a"),
            remove_temp=True,
            logger=None,
        )
        log.info(f"Video assembled → {out_path}")
        return out_path

    # ── Pexels stock footage ──────────────────────────────────────
    def _fetch_clips(self, keywords: list, tmp_dir: Path, target_duration: float) -> list:
        clip_paths = []
        headers = {"Authorization": self.pexels_key}
        per_keyword = max(2, int(target_duration // 30) + 1)

        for kw in keywords[:3]:
            try:
                url = "https://api.pexels.com/videos/search"
                params = {"query": kw, "per_page": per_keyword, "orientation": "landscape"}
                resp = requests.get(url, headers=headers, params=params, timeout=15)
                resp.raise_for_status()
                videos = resp.json().get("videos", [])
                random.shuffle(videos)
                for v in videos:
                    files = sorted(
                        v.get("video_files", []),
                        key=lambda f: f.get("width", 0),
                        reverse=True,
                    )
                    for vf in files:
                        if vf.get("width", 0) >= 1280:
                            dl = requests.get(vf["link"], timeout=60, stream=True)
                            fname = tmp_dir / f"{v['id']}.mp4"
                            with open(fname, "wb") as f:
                                for chunk in dl.iter_content(8192):
                                    f.write(chunk)
                            clip_paths.append(fname)
                            break
            except Exception as e:
                log.warning(f"Pexels fetch failed for '{kw}': {e}")

        if not clip_paths:
            log.warning("No Pexels clips fetched — using colour fallback.")
        return clip_paths

    # ── Subtitle generation ───────────────────────────────────────
    def _make_subtitles(self, narration: str, total_duration: float) -> list:
        from moviepy.editor import TextClip

        words = narration.split()
        if not words:
            return []

        words_per_second = len(words) / total_duration
        chunk_size = max(5, int(words_per_second * 3))   # ~3s per subtitle
        chunks = [
            " ".join(words[i: i + chunk_size])
            for i in range(0, len(words), chunk_size)
        ]
        dt = total_duration / len(chunks)
        subtitle_clips = []

        font = self.cfg.FONT_PATH

        for i, chunk in enumerate(chunks):
            try:
                txt = TextClip(
                    textwrap.fill(chunk, width=45),
                    fontsize=self.cfg.SUBTITLE_FONT_SIZE,
                    font=font,
                    color=self.cfg.SUBTITLE_COLOR,
                    stroke_color=self.cfg.SUBTITLE_STROKE_COLOR,
                    stroke_width=self.cfg.SUBTITLE_STROKE_WIDTH,
                    method="caption",
                    size=(self.resolution[0] - 100, None),
                )
                txt = (
                    txt
                    .set_start(i * dt)
                    .set_duration(dt)
                    .set_position(("center", self.resolution[1] - 180))
                )
                subtitle_clips.append(txt)
            except Exception as e:
                log.warning(f"Subtitle clip {i} failed: {e}")

        return subtitle_clips
