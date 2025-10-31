import os
from dotenv import load_dotenv
from pathlib import Path
# Gameplay/Emotion configuration
EMOTION_THRESHOLDS = {
    "energy_low": float(os.getenv("ENERGY_LOW", "0.20")),
    "hunger_high": float(os.getenv("HUNGER_HIGH", "0.85")),
    "fun_low": float(os.getenv("FUN_LOW", "0.20")),
    "hygiene_low": float(os.getenv("HYGIENE_LOW", "0.20")),
}

# Priority order (first match wins)
EMOTION_PRIORITY = [x.strip() for x in os.getenv(
    "EMOTION_PRIORITY",
    "energy_low,hunger_high,fun_low,hygiene_low"
).split(",") if x.strip()]

# Surprise chance on Play (0..1)
SURPRISE_PROB_PLAY = float(os.getenv("SURPRISE_PROB_PLAY", "0.25"))
WAKE_ANGRY = os.getenv("WAKE_ANGRY", "true").lower() in ("1","true","yes","on")

# Chat dialog font (override via .env)
CHAT_FONT_NAME = os.getenv("CHAT_FONT_NAME", "DejaVu Sans")
CHAT_FONT_SIZE = int(os.getenv("CHAT_FONT_SIZE", "11"))
CHAT_FONT_BOLD = os.getenv("CHAT_FONT_BOLD", "false").lower() in ("1","true","yes","on")
CHAT_FONT_PATH = os.getenv("CHAT_FONT_PATH")  # optional absolute or relative TTF path
# If true, waking from sleep shows angry
WAKE_ANGRY = True



# Window / canvas configuration
VIRTUAL_W, VIRTUAL_H = 128, 96  # low-res pixel canvas
SCALE = 6                       # window size = virtual * SCALE
WINDOW_W, WINDOW_H = VIRTUAL_W * SCALE, VIRTUAL_H * SCALE

# Load .env if present
load_dotenv()

# Chat feature config (can be overridden by .env)
ENABLE_CHAT = os.getenv("ENABLE_CHAT", "true").lower() in ("1","true","yes","on")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
CHAT_MAX_HISTORY = int(os.getenv("CHAT_MAX_HISTORY", "6"))
CHAT_SENTIMENT_FUN_GAIN = float(os.getenv("CHAT_SENTIMENT_FUN_GAIN", "0.25"))
CHAT_SENTIMENT_FUN_LOSS = float(os.getenv("CHAT_SENTIMENT_FUN_LOSS", "0.25"))
CHAT_SENTIMENT_ENERGY_GAIN = float(os.getenv("CHAT_SENTIMENT_ENERGY_GAIN", "0.05"))
CHAT_SENTIMENT_ENERGY_LOSS = float(os.getenv("CHAT_SENTIMENT_ENERGY_LOSS", "0.05"))
CHAT_SENTIMENT_HYGIENE_GAIN = float(os.getenv("CHAT_SENTIMENT_HYGIENE_GAIN", "0.00"))
CHAT_SENTIMENT_HYGIENE_LOSS = float(os.getenv("CHAT_SENTIMENT_HYGIENE_LOSS", "0.00"))

# Allow overriding the OpenAI-compatible base URL (e.g., vLLM, OpenRouter, local server)
# Set environment variable OPENAI_BASE_URL to use. Example: http://localhost:8000/v1
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # None = use default api.openai.com

FPS = 60

# Save location
SAVE_PATH = Path.home() / ".pixelgotchi_save.json"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (60, 60, 60)
LIGHT_GRAY = (160, 160, 160)
RED = (232, 69, 69)
GREEN = (67, 217, 124)
BLUE = (64, 156, 255)
YELLOW = (255, 214, 10)
PURPLE = (180, 90, 225)
CYAN = (50, 220, 220)
BROWN = (139, 94, 60)
