# Atlas-Modified 🤖
### Voice-Controlled General-Purpose Computer Agent

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Phase%201%20%E2%80%94%20Computer%20Control-orange.svg)]()

> A Python-based Windows desktop agent that uses **Google Gemini** for natural-language reasoning and the **Computer Use API** for visual screen understanding. Speak naturally — the agent figures out how to do it.

---

## 🎯 Core Concept

```
User speaks naturally
        ↓
Speech recognition
        ↓
Gemini understands intent + plans task
        ↓
Gemini observes current screen
        ↓
Gemini chooses an action
        ↓
Python controller executes action locally
        ↓
New screen state is captured
        ↓
Gemini verifies result
        ↓
Next action / Task complete
```

---

## ✨ Features (Planned)

| Feature | Status |
|---|---|
| Mouse control (move, click, drag, scroll) | 🏗 Phase 1 |
| Keyboard control (keys, hotkeys, typing) | 🏗 Phase 1 |
| Screen capture + clipboard | 🏗 Phase 1 |
| Voice input (STT) + Voice output (TTS) | 🔜 Phase 2 |
| Gemini function calling (AI → action) | 🔜 Phase 3 |
| Windows app + window management | 🔜 Phase 4 |
| File system control | 🔜 Phase 4 |
| Browser automation (Playwright) | 🔜 Phase 5 |
| Screen vision + OCR | 🔜 Phase 6 |
| Full Gemini Computer Use loop | 🔜 Phase 7 |
| Autonomous multi-step task planning | 🔜 Phase 8 |
| Safety system (confirmation, emergency stop) | 🔜 Phase 8 |
| Desktop UI + system tray | 🔜 Phase 9 |

---

## 🚀 Quick Start

### Prerequisites
- Windows 10/11
- Python 3.12+
- Google Gemini API key ([get one free](https://aistudio.google.com/apikey))

### Installation

```bash
# Clone the repo
git clone https://github.com/DIGANTA100/Atlas-Modified.git
cd Atlas-Modified

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Configure environment
copy .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run the agent
python -m app.main
```

---

## 📁 Project Structure

```
Atlas-Modified/
│
├── app/                    # Core application
│   ├── main.py             # Entry point + agent loop
│   ├── config.py           # Environment config loader
│   └── state.py            # Global agent state
│
├── ai/                     # Gemini AI layer
│   ├── gemini_client.py    # Gemini API wrapper
│   ├── planner.py          # Task decomposition
│   ├── computer_use.py     # Computer Use API handler
│   ├── prompts.py          # System / action prompts
│   └── schemas.py          # Pydantic schemas
│
├── computer/               # Low-level computer control
│   ├── mouse.py            # Mouse movement + clicks
│   ├── keyboard.py         # Keys + typing + hotkeys
│   ├── screen.py           # Screenshot capture
│   ├── scroll.py           # Scroll control
│   ├── clipboard.py        # Clipboard read/write
│   └── windows.py          # Window management
│
├── voice/                  # Voice I/O
│   ├── microphone.py       # Audio capture
│   ├── speech_to_text.py   # STT (pluggable)
│   ├── wake_word.py        # Wake word detection
│   └── text_to_speech.py   # TTS output
│
├── browser/                # Browser automation
│   ├── browser.py          # High-level controller
│   ├── playwright_controller.py
│   └── browser_state.py
│
├── filesystem/             # File system operations
│   ├── files.py
│   ├── folders.py
│   └── search.py
│
├── vision/                 # Screen understanding
│   ├── screenshot.py
│   ├── ocr.py
│   └── ui_detection.py
│
├── tools/                  # Tool registry (Gemini-callable)
│   ├── registry.py
│   ├── executor.py
│   └── permissions.py
│
├── safety/                 # Safety system
│   ├── confirmation.py
│   ├── sensitive_data.py
│   └── emergency_stop.py
│
├── ui/                     # Desktop UI
│   ├── window.py
│   ├── tray.py
│   └── logs.py
│
├── tests/                  # Automated tests
│
├── .env.example            # Environment variable template
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 🗺 Development Roadmap

Following the phased plan from the master specification:

- **Phase 1** — Computer Control Foundation *(current)*
- **Phase 2** — Voice Input / Output
- **Phase 3** — Gemini Function Calling
- **Phase 4** — Windows Integration
- **Phase 5** — Browser Automation
- **Phase 6** — Screen Vision
- **Phase 7** — Gemini Computer Use Agent Loop
- **Phase 8** — Autonomous Multi-Step Tasks + Safety
- **Phase 9** — UI, Reliability & Polish

---

## 🛡 Safety

- All tools are registered and validated before execution
- Gemini cannot run arbitrary Python — it selects from a defined tool registry
- Confirmation prompts for medium/high-risk actions (delete, send, purchase)
- Emergency stop hotkey (`Ctrl+Shift+F12`) halts all actions immediately
- Sensitive data (passwords, API keys) is redacted from all logs

---

## 📜 License

Apache License 2.0 — use it, modify it, build on it.

---

## 🤝 Contributing

Contributions welcome! Open an issue or submit a pull request.
