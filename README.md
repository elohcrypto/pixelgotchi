# Pixelgotchi

A tiny pixel-styled Tamagotchi-like desktop pet built with Python and Pygame.

## Features
- Crisp pixel art via low-res canvas scaled up
- Needs: hunger, energy, fun, hygiene (decay over time)
- Actions: feed, play, sleep toggle, clean
- Idle animation, simple UI bars
- Autosave on exit, load on start; offline catch-up

## Setup

1. Ensure Python 3.9+ is installed.
2. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python -m pixelgotchi
```

## Controls
- Arrow keys: left/right to cycle actions, up/down to confirm/cancel
- Hotkeys: F feed, P play, S sleep toggle, C clean
- H: help overlay
- M: mute/unmute beeps
- Esc/Q: quit (autosaves)

## Notes
- The window is pixel-scaled; resizing is fixed to preserve crisp pixels.
