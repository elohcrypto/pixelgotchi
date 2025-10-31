# Pixelgotchi

A tiny, pixel-styled Tamagotchi-like desktop pet built with Python and Pygame. Pixelgotchi lives in a crisp low‑res world, has needs and moods, learns from your chat, and reacts with expressive, pixelated emotions.

## Features

- Pixel aesthetic
  - Low-resolution virtual canvas scaled up with nearest-neighbor for crisp pixels.
  - Simple but expressive pet with randomized “genetic” appearances (size, shape, colors, spots, eye styles).
- Needs & moods
  - Hunger, Energy, Fun, Hygiene decay over time.
  - Mood = average of positives (Energy, Fun, Hygiene, inverse Hunger).
  - Death and respawn (Starved/Exhausted), with a small death screen and “Respawn” button.
- Emotions
  - Reactions to actions (Feed / Play / Sleep / Clean).
  - Stat-triggered emotions (e.g., tired when low energy, sad when hungry/bored, yuck when dirty).
  - Angry if you wake the pet; occasional surprise during play.
- Chat dialog (LLM‑ready)
  - Press T or click the Chat button to open a centered dialog with wrapped text and a dedicated, readable font.
  - Uses an OpenAI‑compatible API (OpenAI, OpenRouter, vLLM, local servers) with configurable base URL and model via `.env`.
  - Lightweight sentiment analysis nudges Fun/Energy and triggers emotions.
- Quality of life
  - Save/load to a file in your HOME directory, with offline catch‑up.
  - Help overlay with keybinds.
  - Modular code: config, state, rendering, UI, chat, and sentiment separated.

## Controls

- Arrow keys: select action
- Enter / Space / Up: perform selected action
- F / P / S / C: Feed / Play / Sleep toggle / Clean
- T or Chat button: open chat dialog (Enter sends, Esc closes)
- H: toggle help overlay (disabled while chat dialog is open)
- M: mute/unmute
- Esc / Q: quit (autosaves)

## Install & Run

Requirements: Python 3.9+ (Pygame wheels usually include SDL libs)

```bash
cd ~/pixelgotchi
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m pixelgotchi
```

## Optional: Enable LLM Chat

Create a `.env` file in the project root:

```env
# LLM config
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1   # or OpenRouter/vLLM/local
OPENAI_MODEL=gpt-3.5-turbo

# Toggle chat and general behavior
ENABLE_CHAT=true
CHAT_MAX_HISTORY=6
SURPRISE_PROB_PLAY=0.25
WAKE_ANGRY=true

# Emotion thresholds (adjust to taste)
ENERGY_LOW=0.20
HUNGER_HIGH=0.85
FUN_LOW=0.20
HYGIENE_LOW=0.20

# Chat font for readability
CHAT_FONT_NAME=DejaVu Sans
CHAT_FONT_SIZE=13
CHAT_FONT_BOLD=true
# Or use a custom font file (overrides name/size/bold)
# CHAT_FONT_PATH=/path/to/SomeFont.ttf
```

Then run as usual. The game will load `.env` on startup.

### Using a custom OpenAI‑compatible server

Set `OPENAI_BASE_URL` to your server, e.g.:

```env
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_MODEL=meta-llama/Meta-Llama-3-8B-Instruct
OPENAI_API_KEY=dummy
```

The client uses the Chat Completions API route `/v1/chat/completions`. If your server only supports the legacy `/v1/completions` route, open an issue or PR—we can add a mode switch.

## Configuration (high‑level)

- All tunables are loaded from `.env` in addition to sensible defaults in `pixelgotchi/config.py`.
- Highlights you may want to tweak:
  - SCALE (pixel scaling factor) in `config.py` if the window is too large/small.
  - Emotion thresholds and priority.
  - Chat font, size, and weight for readability.

## Troubleshooting

- Blurry pixels
  - Set OS display scaling to 100% or reduce `SCALE` in `pixelgotchi/config.py`.
- Chat doesn’t reply
  - Check `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL`.
  - Test your endpoint with curl:
    ```bash
    curl -s "$OPENAI_BASE_URL/chat/completions" \
      -H "Authorization: Bearer $OPENAI_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "'
OPENAI_MODEL'",
        "messages": [
          {"role": "system", "content": "You are a short, friendly pet."},
          {"role": "user", "content": "Say hi!"}
        ],
        "max_tokens": 32
      }'
    ```

## Tech Stack & Structure

- Python + Pygame
- Optional OpenAI‑compatible client via `openai` SDK
- `python-dotenv` for `.env` support

```
pixelgotchi/
  ├─ config.py        # settings, .env loading
  ├─ state.py         # PetState, actions, decay, save/load
  ├─ appearance.py    # random appearance generator
  ├─ pet.py           # sprite rendering + emotions
  ├─ ui.py            # UI helpers (bars, help, chat dialog)
  ├─ chat.py          # LLM client wrapper (base_url support)
  ├─ sentiment.py     # lightweight sentiment scoring
  └─ game.py          # main loop, input, particles, orchestration
```

## Roadmap ideas

- Always‑on‑top desktop pet mode
- More animations/accessories
- Minigames for “Play”
- In‑game Settings to edit `.env` values
- Persistent chat history and reactions

## License

MIT (or your preferred license). Let me know and I’ll add the file.
