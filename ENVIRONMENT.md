# Environment Configuration

Pixelgotchi can load configuration from a `.env` file at the project root. We use `python-dotenv` to read it on startup.

1. Create a `.env` file in `~/pixelgotchi/` (same folder as requirements.txt):

```
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
ENABLE_CHAT=true
CHAT_MAX_HISTORY=6
SURPRISE_PROB_PLAY=0.25
WAKE_ANGRY=true

# Emotion thresholds
ENERGY_LOW=0.20
HUNGER_HIGH=0.85
FUN_LOW=0.20
HYGIENE_LOW=0.20
```

2. Run the game normally:

```
cd ~/pixelgotchi
source .venv/bin/activate
pip install -r requirements.txt
python3 -m pixelgotchi
```

3. Notes
- Values in `.env` override defaults in `config.py`.
- If you change `.env` while the game is running, restart to apply.
- If `OPENAI_BASE_URL` is set, the chat client will use it.
- If `ENABLE_CHAT` is `false`, chat is disabled even if keys are present.
