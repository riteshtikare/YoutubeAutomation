"""
ScriptAgent  — uses Claude to research trending topics and write
a full YouTube script with title, description, tags, and narration.
"""

import json
import re
import anthropic
from config.settings import Settings


SYSTEM_PROMPT = """You are an expert YouTube content strategist and scriptwriter.
You create engaging, SEO-optimised scripts that hook viewers within the first 5 seconds
and keep them watching until the end. Your scripts are conversational, clear, and
always deliver genuine value.

Always respond with ONLY valid JSON — no markdown fences, no extra text."""


SCRIPT_PROMPT = """Create a complete YouTube video script for the niche: "{niche}".
{topic_line}

Return a JSON object with these exact keys:
{{
  "title":        "YouTube title (max 70 chars, high CTR)",
  "description":  "YouTube description (300-500 chars, with keywords)",
  "tags":         ["tag1","tag2",...],   // 10-15 tags
  "hook":         "Opening 15 seconds — must create curiosity or promise value",
  "narration":    "Full narration text (spoken aloud, 600-900 words, no stage directions)",
  "sections": [
    {{"title": "Intro",   "duration_sec": 20,  "key_point": "..."}},
    {{"title": "Main 1",  "duration_sec": 60,  "key_point": "..."}},
    {{"title": "Main 2",  "duration_sec": 60,  "key_point": "..."}},
    {{"title": "Main 3",  "duration_sec": 60,  "key_point": "..."}},
    {{"title": "Outro",   "duration_sec": 20,  "key_point": "CTA + subscribe"}}
  ],
  "estimated_duration_sec": 220,
  "search_keywords": ["keyword1","keyword2","keyword3"]
}}"""


class ScriptAgent:
    def __init__(self, cfg: Settings):
        self.client = anthropic.Anthropic(api_key=cfg.ANTHROPIC_API_KEY)
        self.model = cfg.CLAUDE_MODEL

    def generate(self, topic: str = "", niche: str = "personal finance") -> dict:
        topic_line = (
            f'Topic: "{topic}"' if topic
            else "Pick the single most trending and high-search-volume topic right now."
        )

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": SCRIPT_PROMPT.format(
                        niche=niche,
                        topic_line=topic_line,
                    ),
                }
            ],
        )

        raw = message.content[0].text.strip()

        # Strip accidental markdown fences
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        data = json.loads(raw)
        return data
