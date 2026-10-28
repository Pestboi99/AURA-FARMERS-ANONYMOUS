# 🔥 AURA FARMERS ANONYMOUS 🔥

> **"We spent 2 years of engineering effort to make logging in 40x slower, with AI nobody asked for."**

*Log in. Lose your dignity.*

A satirical login system where logging in is deliberately the most absurd, over-engineered, AI-judged experience ever made. Built for the "Brainrot Engineering / Artificial Super Unintelligence / The Ultimate Inconvenience" hackathon track.

## ✨ Features

- **Absurd Password Requirements**: Must contain a prime number, an emoji, a fruit name, and the word "sigma"
- **The Brainrot Trial**: 3 random challenges judged by an AI Bouncer (or hilarious offline fallbacks)
- **AI Bouncer**: A confidently unintelligent, Gen-Z slang-speaking gatekeeper powered by Google Gemini
- **5 Challenge Types**: Meme Explainer, Sigma Timer, Spot the Real Meme, Vibe Check, Slider of Doom
- **Aura Points & Ranks**: From "NPC" to "Ohio Final Boss"
- **Emotional Support Password Reset**: Compliment the AI 3 times to reset your password
- **Hall of Shame Leaderboard**: Most humiliated users and their worst answers
- **Tung Tung Tung Sahur**: Every button click plays the iconic sound
- **Easter Eggs**: Konami code, runaway buttons, fake notifications, and more

## 🚀 Setup

### 1. Clone and Install

```bash
cd aura-farmers
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY (optional - app works without it!)
```

### 3. Add Audio (Optional)

Drop your `tung.mp3` file into `static/audio/tung.mp3`. If missing, the app synthesizes the sound using Web Audio API and Speech Synthesis.

### 4. Run

```bash
python app.py
```

Open http://localhost:5000 and prepare to lose your dignity.

## 🎮 60-Second Demo Script

1. **Register** — Username: anything, Password: `🍎Sigma7prime!` (meets all absurd requirements)
2. **Login** — Try to catch the "Forgot Password" button (it runs away!)
3. **Brainrot Trial** — Face 3 random challenges judged by the AI Bouncer
4. **Dashboard** — See your aura points, rank, and watch the password "expiry" timer
5. **Leaderboard** — Check the Hall of Shame (pre-seeded with 5 hilarious users)
6. **Password Reset** — Compliment the AI 3 times to unlock reset

### Demo Account
- **Username**: `demo`
- **Password**: `🍎Sigma7prime!`

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, Flask, SQLite |
| Frontend | Jinja2 templates, vanilla HTML/CSS/JS |
| AI | Google Gemini (gemini-2.0-flash) with offline fallbacks |
| Audio | Web Audio API + Speech Synthesis |
| Auth | werkzeug.security password hashing |

## 📁 Project Structure

```
aura-farmers/
├── app.py                 # Flask app + all routes
├── database.py            # SQLite schema + helpers
├── ai_bouncer.py          # Gemini AI integration + fallback
├── fallback_responses.py  # 30+ offline bouncer responses
├── requirements.txt
├── .env.example
├── README.md
├── templates/
│   ├── base.html          # Layout + emoji rain + mascot + cookie banner
│   ├── register.html      # Absurd password rules
│   ├── login.html         # Login + runaway forgot button
│   ├── trial.html         # Challenge rendering + AI analysis
│   ├── dashboard.html     # Aura meter + stats + achievements
│   ├── reset.html         # Emotional support compliment flow
│   ├── leaderboard.html   # Hall of Shame
│   └── 404.html           # Funny 404
└── static/
    ├── css/style.css      # Maximalist chaos styling
    ├── js/
    │   ├── main.js        # Core UI, modals, notifications
    │   ├── sounds.js      # Tung tung tung audio system
    │   ├── challenges.js  # Timer, slider, choice logic
    │   ├── mascot.js      # SVG mascot + cursor following
    │   └── confetti.js    # Confetti + screen effects
    └── audio/
        └── tung.mp3       # (User-provided) Tung tung tung sound
```

## 🔌 Offline Mode

The app works perfectly without a Gemini API key. All AI responses fall back to a bank of 30+ pre-written bouncer responses written in peak brainrot. The demo can survive bad Wi-Fi, no Wi-Fi, or if Gemini is having an existential crisis.

## 🎵 Audio

- **tung.mp3**: Place your own "tung tung tung sahur" audio file at `static/audio/tung.mp3`
- **Fallback**: If no file exists, the browser synthesizes the sound using Speech Synthesis + Web Audio
- **Mute toggle**: Top-right corner of every page
- **Chaos Level**: Slider to control animation intensity (1-5)

## 🐛 Known Limitations

- Rate limiting is in-memory (resets on server restart) — sufficient for hackathon demo
- SQLite is single-file — not for production scale
- The runaway button might escape off-screen on very small viewports
- The AI Bouncer may occasionally make sense (known bug, severity: critical)
- Side effects may include: loss of dignity, excessive mewing, involuntary brainrot

## 📜 License

MIT — Use responsibly. Or don't. We're not your sigma.
