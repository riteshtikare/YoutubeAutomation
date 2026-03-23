"""
TTSAgent — converts narration text to speech using ElevenLabs.
Falls back to pyttsx3 (offline) if no API key is set.
"""

import logging
from pathlib import Path

log = logging.getLogger(__name__)


class TTSAgent:
    def __init__(self, cfg):
        self.api_key = cfg.ELEVENLABS_API_KEY
        self.voice_id = cfg.ELEVENLABS_VOICE_ID

    # ─────────────────────────────────────────────────────────────
    def generate(self, text: str, out_path: Path) -> Path:
        out_path = Path(out_path)

        if self.api_key:
            return self._elevenlabs(text, out_path)
        else:
            log.warning("No ELEVENLABS_API_KEY — using offline TTS fallback.")
            return self._pyttsx3(text, out_path)

    # ── ElevenLabs ────────────────────────────────────────────────
    def _elevenlabs(self, text: str, out_path: Path) -> Path:
        from elevenlabs.client import ElevenLabs
        from elevenlabs import save

        client = ElevenLabs(api_key=self.api_key)
        audio = client.text_to_speech.convert(
            voice_id=self.voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        save(audio, str(out_path))
        log.info(f"ElevenLabs TTS → {out_path}")
        return out_path

    # ── Offline fallback (pyttsx3) ────────────────────────────────
    def _pyttsx3(self, text: str, out_path: Path) -> Path:
        import pyttsx3

        engine = pyttsx3.init()
        engine.setProperty("rate", 165)   # words per minute
        engine.setProperty("volume", 0.95)

        # pyttsx3 saves as .wav; convert to mp3 with pydub if available
        wav_path = out_path.with_suffix(".wav")
        engine.save_to_file(text, str(wav_path))
        engine.runAndWait()

        try:
            from pydub import AudioSegment
            AudioSegment.from_wav(str(wav_path)).export(str(out_path), format="mp3")
            wav_path.unlink(missing_ok=True)
        except ImportError:
            out_path = wav_path  # just use .wav

        log.info(f"pyttsx3 TTS → {out_path}")
        return out_path
