# J.A.R.V.I.S. — Personal Voice AI Agent

Your Iron Man-style personal assistant running on macOS.
Stack: **Whisper** (voice in) · **Claude Haiku** (brain) · **ElevenLabs** (voice out)

---

## Quick Start (3 steps)

### 1. Run the setup script
```bash
bash setup.sh
```
This installs ffmpeg, creates a virtualenv, and installs all Python packages.

### 2. Add your API keys
Open `.env` and fill in:
```
ANTHROPIC_API_KEY=sk-ant-...        # https://console.anthropic.com
ELEVENLABS_API_KEY=...              # https://elevenlabs.io (free tier works)
ELEVENLABS_VOICE_ID=ErXwobaYiN019PkySvjV   # change to any voice you like
```

### 3. Start JARVIS
```bash
source .venv/bin/activate
python jarvis.py
```

---

## How to use it

Say the wake word to activate:
> **"Hey JARVIS"** or just **"JARVIS"**

Then speak your command naturally. JARVIS stays active for 30 seconds after the wake word — you don't need to repeat it for follow-up questions.

To shut down:
> "JARVIS, shut down" / "goodbye" / "go offline"

---

## Example commands

| What you say | What happens |
|---|---|
| "Hey JARVIS, what time is it?" | Tells you the time |
| "JARVIS, open Spotify" | Opens Spotify |
| "What's the weather in San Francisco?" | Web searches and reads the result |
| "Remind me to drink water in 20 minutes" | Sets a macOS notification |
| "Open my Downloads folder" | Opens Finder at Downloads |
| "Who won the Champions League last year?" | Web search answer |

---

## Picking your ElevenLabs voice

1. Go to https://elevenlabs.io/voice-library
2. Browse and preview voices
3. Click a voice → copy the Voice ID from the URL or settings
4. Paste into `.env` as `ELEVENLABS_VOICE_ID`

Recommended voices for a JARVIS feel:
- **Antoni** `ErXwobaYiN019PkySvjV` — deep, calm (default)
- **Adam** `pNInz6obpgDQGcFmaJgB` — strong, authoritative
- **Josh** `TxGEqnHWrfWFTfGW9XjX` — natural, warm

---

## Project structure

```
jarvis/
├── jarvis.py          # Main loop — wake word, STT, LLM, TTS
├── skills/
│   ├── web_search.py  # DuckDuckGo search (free)
│   ├── open_app.py    # Open macOS apps and files
│   └── reminders.py   # Time + macOS notifications
├── memory/
│   └── store.py       # Saves conversation history to disk
├── .env               # Your API keys (never commit this)
├── requirements.txt
└── setup.sh
```

---

## Adding new skills

Create a file in `skills/`, define a function, then:
1. Import it in `jarvis.py`
2. Add a tool definition to the `TOOLS` list
3. Add a case in `execute_tool()`

---

## Cost estimate

| Component | Usage | Monthly cost |
|---|---|---|
| Claude Haiku | ~50 commands/day | ~$1–2 |
| ElevenLabs free | up to 10k chars | $0 |
| ElevenLabs Starter | unlimited | $5 |
| Whisper (local) | unlimited | $0 |

**Total: $1.50 – $7/month** depending on ElevenLabs tier.

---

## Troubleshooting

**No audio input detected** — go to System Settings → Privacy → Microphone → allow Terminal.

**"ffmpeg not found"** — run `brew install ffmpeg`.

**ElevenLabs sounds robotic** — try a different voice ID or increase `stability` in `jarvis.py`.

**Whisper is slow** — switch to `whisper.load_model("tiny")` for faster but less accurate transcription.
