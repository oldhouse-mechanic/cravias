# CRAVIAS — C.R.A.V.I.A.S.
### Computer Response Automation - Voice Input Assistance
**Version 2.0.0** | Built for Linux

---

## Project Structure

```
crax/
├── main.py                   # Entry point (run this)
├── requirements.txt
├── config/
│   └── settings.yaml         # All configuration
├── core/
│   ├── assistant.py          # Main orchestrator & loop
│   ├── brain.py              # Intent engine (understands what you say)
│   ├── listener.py           # Speech-to-Text (Vosk offline / Google fallback)
│   └── speaker.py            # Text-to-Speech (espeak / pyttsx3)
├── modules/
│   ├── greet.py              # Greetings, personality, small talk
│   ├── memory.py             # Conversation history + learning
│   ├── music.py              # Play local music (VLC/MPV)
│   ├── search.py             # Web search & Wikipedia
│   └── system.py             # OS controls (time, volume, apps, shutdown)
└── data/
    ├── memory.json            # Conversation history (auto-generated)
    └── learned.json           # Facts Cravias learned about you (auto-generated)
```

---

## Setup

### 1. System Dependencies (Linux)

```bash
# TTS engine (lightweight, works offline)
sudo apt install espeak

# Audio support
sudo apt install portaudio19-dev python3-pyaudio

# Optional: media player for local music
sudo apt install vlc
# or
sudo apt install mpv
```

### 2. Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Vosk Offline STT Model (recommended)

Download a small English model for fully offline voice recognition:

```bash
cd ~
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 vosk-model-small-en-us
```

If you skip this, Cravias will fall back to Google STT (requires internet).

---

## Running Cravias

```bash
cd crax

# Voice mode (default)
python main.py

# Text mode (no microphone needed — great for testing)
python main.py --text

# Custom config
python main.py --config /path/to/settings.yaml
```

---

## What Cravias Can Do

| Command Example | Action |
|---|---|
| "What time is it?" | Tells the current time |
| "What's today's date?" | Tells today's date |
| "Search for Python tutorials" | Opens DuckDuckGo search |
| "Wikipedia Albert Einstein" | Reads a Wikipedia summary |
| "Open YouTube" | Opens YouTube in browser |
| "Play music" | Plays a song from ~/Music |
| "Play something by Radiohead" | Searches local library |
| "Stop music" | Stops playback |
| "Volume up / Volume down" | Adjusts system volume |
| "Open Firefox / Terminal" | Launches an application |
| "Battery status" | Reports battery level |
| "CPU and RAM usage" | Reports system resources |
| "Lock screen" | Locks your desktop |
| "Shutdown" | Schedules system shutdown |
| "Remember that I like jazz" | Cravias stores this fact |
| "What do you know about me?" | Cravias recalls learned facts |
| "Tell me a joke" | Cravias tells a joke |
| "Bye / Goodbye" | Exits gracefully |

---

## Learning & Memory

Cravias automatically learns from conversation. Say things like:

- *"My name is Alex"* → Cravias remembers your name
- *"I live in Mumbai"* → Cravias stores your location
- *"I love classical music"* → Cravias notes your taste
- *"Remember that my password hint is blue sky"* → Stored as a note

All memory is saved in `data/memory.json` and `data/learned.json` locally on your machine. Nothing is sent to the cloud.

---

## Configuration

Edit `config/settings.yaml` to customize everything:

- Voice speed and engine
- Music directory
- Browser preference
- Enable/disable shutdown commands
- Max conversation history length
- Your name (or let Cravias ask)

---

## Credits

Built by Om as part of the **CRA VI a.s.** project.

**CRAVIAS** — C.R.A.V.I.A.S.
C.R.A.V.I.A.S. = Carbon Robotic Artificial Xenium Intelligence Assistance System
