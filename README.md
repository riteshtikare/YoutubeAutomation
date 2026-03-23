# 🎬 AI YouTube Automation Pipeline

> **Fully automated YouTube channel** — from trending topic research to published video — powered by Claude AI, ElevenLabs TTS, Pexels stock footage, and the YouTube Data API.

---

## 🗺️ How It Works

```
Trending Topic
     │
     ▼
[Claude AI] ──► Script + Title + Tags + Description
     │
     ▼
[ElevenLabs] ──► Professional voiceover (MP3)
     │
     ▼
[Pexels API] ──► Relevant stock footage clips
     │
     ▼
[MoviePy] ──► Assembled video with subtitles (MP4)
     │
     ▼
[Pillow] ──► Click-worthy thumbnail (PNG)
     │
     ▼
[YouTube API] ──► Auto-upload + set thumbnail
```

---

## ⚡ Quickstart

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/ai-youtube-automator.git
cd ai-youtube-automator
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
# Edit .env with your keys (see table below)
```

| Key | Where to get it | Required? |
|-----|----------------|-----------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | ✅ Yes |
| `ELEVENLABS_API_KEY` | [elevenlabs.io](https://elevenlabs.io) | Optional (offline fallback) |
| `PEXELS_API_KEY` | [pexels.com/api](https://www.pexels.com/api) | Optional (colour fallback) |

### 3. YouTube OAuth setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → Enable **YouTube Data API v3**
3. Create **OAuth 2.0 credentials** (Desktop app)
4. Download `client_secrets.json` → place in `src/config/`
5. On first run a browser window opens to authorise — token is cached

### 4. Run the pipeline

```bash
cd src

# One video with AI-chosen topic
python pipeline.py

# Specify your own topic
python pipeline.py --topic "5 Money Habits That Changed My Life" --niche "personal finance"

# Run on a daily schedule (10 AM)
python scheduler.py

# Run every 6 hours
python scheduler.py --interval 6
```

---

## 📁 Project Structure

```
ai-youtube-automator/
├── src/
│   ├── pipeline.py          # Main orchestrator
│   ├── scheduler.py         # Automated daily posting
│   ├── agents/
│   │   ├── script_agent.py  # Claude AI script writer
│   │   ├── tts_agent.py     # ElevenLabs / pyttsx3 voiceover
│   │   ├── video_agent.py   # MoviePy video assembler
│   │   ├── thumbnail_agent.py  # Pillow thumbnail creator
│   │   └── upload_agent.py  # YouTube Data API uploader
│   └── config/
│       └── settings.py      # All config & env loading
├── output/                  # Generated videos, audio, thumbnails
├── requirements.txt
├── .env.example
└── README.md
```

---

## 💰 Monetisation Tips

| Strategy | How |
|----------|-----|
| **Ad Revenue** | Enable monetisation once you hit 1,000 subs + 4,000 watch hours |
| **Affiliate links** | Add product links to video descriptions |
| **Niche selection** | High CPM niches: Finance, Tech, Health, Legal, Business |
| **Consistency** | Use the scheduler to post daily — the algorithm rewards it |
| **SEO** | Claude generates optimised titles, descriptions, and tags automatically |

---

## 🔧 Customisation

- **Change voice**: Update `ELEVENLABS_VOICE_ID` in `.env` (browse voices at elevenlabs.io)
- **Change niche**: Set `DEFAULT_NICHE` in `.env`
- **Video length**: Adjust `estimated_duration_sec` in the script prompt inside `script_agent.py`
- **Upload privacy**: Set `YOUTUBE_PRIVACY=unlisted` to review before going public
- **Thumbnail style**: Edit colours/fonts in `thumbnail_agent.py`

---

## 📋 Requirements

- Python 3.10+
- `ffmpeg` installed (`brew install ffmpeg` / `apt install ffmpeg`)
- API keys (see table above)

---

## 📄 License

MIT
