import os
from typing import List, Tuple

try:
    from openai import OpenAI
except Exception:  # optional
    OpenAI = None

from .config import ENABLE_CHAT, OPENAI_MODEL, CHAT_MAX_HISTORY, OPENAI_BASE_URL


class ChatEngine:
    def __init__(self):
        self.enabled = ENABLE_CHAT and (OpenAI is not None) and (os.getenv("OPENAI_API_KEY") is not None)
        self.history: List[Tuple[str,str]] = []  # (role, content)
        if self.enabled:
            kwargs = {"api_key": os.getenv("OPENAI_API_KEY")}
            if OPENAI_BASE_URL:
                kwargs["base_url"] = OPENAI_BASE_URL
            self.client = OpenAI(**kwargs)
        else:
            self.client = None

    def is_ready(self) -> bool:
        return bool(self.enabled)

    def push_user(self, content: str):
        self.history.append(("user", content))
        if len(self.history) > CHAT_MAX_HISTORY:
            self.history = self.history[-CHAT_MAX_HISTORY:]

    def reply(self) -> str:
        if not self.enabled:
            return "(Chat disabled. Set OPENAI_API_KEY to enable.)"
        messages = [{"role": r, "content": c} for r,c in self.history]
        if not any(r == "system" for r,_ in self.history):
            messages = [{"role": "system", "content": "You are a friendly, concise pet character. Keep responses short."}] + messages
        resp = self.client.chat.completions.create(model=OPENAI_MODEL, messages=messages)
        text = resp.choices[0].message.content.strip()
        self.history.append(("assistant", text))
        if len(self.history) > CHAT_MAX_HISTORY:
            self.history = self.history[-CHAT_MAX_HISTORY:]
        return text
