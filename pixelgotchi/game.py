import os
os.environ["SDL_HINT_RENDER_SCALE_QUALITY"] = "0"  # nearest-neighbor
import math
import pygame as pg
from typing import Optional, List

from .config import *
from .state import PetState, load_state, save_state, clamp
from .appearance import random_appearance
from .pet import PetSprite
from .ui import draw_bar, draw_help, draw_chat_dialog
from .chat import ChatEngine
from .sentiment import sentiment_score

actions = [
    ("Feed", "F", "Decrease hunger"),
    ("Play", "P", "Increase fun"),
    ("Sleep", "S", "Toggle sleep"),
    ("Clean", "C", "Increase hygiene"),
]

class PixelCanvas:
    def __init__(self, vw, vh, scale):
        self.vw, self.vh, self.scale = vw, vh, scale
        self.surface = pg.Surface((vw, vh))

    def begin(self):
        self.surface.fill((20, 20, 20))

    def end_blit(self, screen):
        scaled = pg.transform.scale(self.surface, (self.vw * self.scale, self.vh * self.scale))
        screen.blit(scaled, (0, 0))


def compute_mood(state: PetState) -> float:
    good = [state.energy, state.fun, state.hygiene, 1 - state.hunger]
    return clamp(sum(good)/len(good))


def beep(enabled: bool, freq=880, dur_ms=60):
    if not enabled:
        return
    try:
        pg.mixer.init()
        sample_rate = 22050
        n = int(sample_rate * (dur_ms/1000.0))
        buf = bytearray()
        for i in range(n):
            t = i / sample_rate
            s = int(32767 * 0.2 * math.sin(2*math.pi*freq*t))
            buf += s.to_bytes(2, byteorder='little', signed=True)
        snd = pg.mixer.Sound(buffer=bytes(buf))
        snd.play()
    except Exception:
        pass


def random_choice(options):
    import random
    return options[random.randrange(len(options))]


def do_action(state: PetState, name: str):
    if not state.alive:
        return
    if name == "Feed":
        state.feed()
    elif name == "Play":
        state.play()
    elif name == "Sleep":
        state.toggle_sleep()
    elif name == "Clean":
        state.clean()
    state.last_timestamp = pg.time.get_ticks() / 1000.0


def do_action_with_fx(state: PetState, name: str, pet: PetSprite,
                      particles: List, floats: List, muted: bool, font):
    was_asleep = state.asleep
    do_action(state, name)
    pet.reaction = 1.0
    px, py = VIRTUAL_W//2, VIRTUAL_H//2
    if name == "Feed":
        spawn_particles_burst(particles, px, py, color=GREEN)
        floats.append((font.render(random_choice(["Yum!","Delish!","Nom nom!","Mmmm!"]), False, WHITE), px-12, py-18))
        beep(not muted, freq=520)
        pet.set_emotion("love", 1.2)
    elif name == "Play":
        spawn_particles_confetti(particles, px, py)
        floats.append((font.render(random_choice(["Fun!","Yay!","Woo!","Nice!"]), False, WHITE), px-10, py-18))
        beep(not muted, freq=760)
        pet.set_emotion("excited", 1.2)
        # Random surprise during play
        import random
        if random.random() < SURPRISE_PROB_PLAY:
            pet.set_emotion("surprised", 0.8)
            floats.append((font.render(random_choice(["Whoa!","Woah!","Huh?","Oh!"]), False, WHITE), px-8, py-28))
    elif name == "Sleep":
        spawn_particles_stars(particles, px+16, py-10)
        floats.append((font.render(random_choice(["ZzZ","Sleepy...","Nap time"]), False, WHITE), px-12, py-20))
        beep(not muted, freq=400)
        pet.set_emotion("sleepy", 1.5)
    elif name == "Clean":
        spawn_particles_bubbles(particles, px, py)
        floats.append((font.render(random_choice(["Fresh!","Squeaky!","Shiny!","So clean!"]), False, WHITE), px-14, py-20))
        beep(not muted, freq=640)
        pet.set_emotion("yuck", 0.9)

    # Stat-based emotion overlays
    apply_stat_emotions(state, pet, floats, font)

    # Angry if you woke the pet from sleep
    if WAKE_ANGRY and name == "Sleep" and was_asleep and not state.asleep:
        pet.set_emotion("angry", 1.2)
        floats.append((font.render(random_choice(["Hey!","Grr...","Let me sleep!","Ugh!"]), False, WHITE), px-16, py-32))
        beep(not muted, freq=300)


class Particle:
    def __init__(self, x, y, vx, vy, life, color):
        self.x, self.y, self.vx, self.vy, self.life, self.color = x, y, vx, vy, life, color

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, surf: pg.Surface):
        if self.life > 0:
            if 0 <= int(self.x) < VIRTUAL_W and 0 <= int(self.y) < VIRTUAL_H:
                surf.set_at((int(self.x), int(self.y)), self.color)


def spawn_particles_burst(particles, cx, cy, color=WHITE, n=20):
    import random
    for _ in range(n):
        ang = random.random() * math.tau
        spd = 20 + random.random()*30
        vx, vy = math.cos(ang)*spd, math.sin(ang)*spd
        particles.append(Particle(cx, cy, vx, vy, life=0.4+random.random()*0.3, color=color))


def spawn_particles_confetti(particles, cx, cy, n=30):
    import random
    cols = [RED, GREEN, BLUE, YELLOW, PURPLE, CYAN]
    for _ in range(n):
        vx = (random.random()-0.5) * 50
        vy = -20 - random.random()*30
        color = random.choice(cols)
        particles.append(Particle(cx + (random.random()-0.5)*10, cy, vx, vy, life=0.8, color=color))


def spawn_particles_stars(particles, cx, cy, n=8):
    import random
    for _ in range(n):
        vx = (random.random()-0.5) * 10
        vy = -5 - random.random()*10
        particles.append(Particle(cx, cy, vx, vy, life=1.0, color=YELLOW))


def spawn_particles_bubbles(particles, cx, cy, n=16):
    import random
    for _ in range(n):
        vx = (random.random()-0.5) * 10
        vy = -10 - random.random()*10
        particles.append(Particle(cx + (random.random()-0.5)*8, cy+8, vx, vy, life=0.9, color=BLUE))


def apply_stat_emotions(state: PetState, pet: PetSprite, floats: List, font):
    # Priority-driven thresholds from config
    px, py = VIRTUAL_W//2, VIRTUAL_H//2
    for key in EMOTION_PRIORITY:
        if key == "energy_low" and state.energy < EMOTION_THRESHOLDS["energy_low"]:
            pet.set_emotion("tired", 1.2)
            floats.append((font.render(random_choice(["Tired...","So sleepy","Low energy"]), False, WHITE), px-18, py-34))
            return
        if key == "hunger_high" and state.hunger > EMOTION_THRESHOLDS["hunger_high"]:
            pet.set_emotion("sad", 1.2)
            floats.append((font.render(random_choice(["Hungry...","Feed me","Stomach growls"]), False, WHITE), px-20, py-34))
            return
        if key == "fun_low" and state.fun < EMOTION_THRESHOLDS["fun_low"]:
            pet.set_emotion("sad", 1.0)
            floats.append((font.render(random_choice(["Bored...","Play?","Lonely..."]), False, WHITE), px-16, py-34))
            return
        if key == "hygiene_low" and state.hygiene < EMOTION_THRESHOLDS["hygiene_low"]:
            pet.set_emotion("yuck", 1.0)
            floats.append((font.render(random_choice(["Dirty...","Messy","Eww!"]), False, WHITE), px-12, py-34))
            return


def main():
    pg.init()
    screen = pg.display.set_mode((WINDOW_W, WINDOW_H))
    pg.display.set_caption("Pixelgotchi")
    clock = pg.time.Clock()

    canvas = PixelCanvas(VIRTUAL_W, VIRTUAL_H, SCALE)
    # Main UI font
    font = pg.font.SysFont("Courier", 8)
    # Chat font (configurable)
    try:
        if CHAT_FONT_PATH:
            chat_font = pg.font.Font(CHAT_FONT_PATH, CHAT_FONT_SIZE)
        else:
            chat_font = pg.font.SysFont(CHAT_FONT_NAME, CHAT_FONT_SIZE, bold=CHAT_FONT_BOLD)
    except Exception:
        chat_font = font  # fallback

    state = load_state()
    if not state.appearance:
        state.appearance = random_appearance()
    pet = PetSprite()
    chat = ChatEngine()
    typing = False
    input_text = ""
    chat_open = False
    chat_messages: List[tuple] = []  # (role, text)

    running = True
    show_help = False
    muted = False
    action_idx = 0
    hovered_idx: Optional[int] = None
    particles: List[Particle] = []
    floats: List[tuple] = []  # (surface, x, y)
    hovered_chat: bool = False

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                # When in chat dialog, capture keys exclusively
                if chat_open:
                    if event.key == pg.K_ESCAPE:
                        chat_open = False
                        typing = False
                        input_text = ""
                    elif event.key == pg.K_RETURN:
                        # send
                        if input_text.strip():
                            user_text = input_text.strip()
                            chat_messages.append(("user", user_text))
                            if chat.is_ready():
                                chat.push_user(user_text)
                                reply = chat.reply()
                            else:
                                reply = "(chat disabled)"
                            chat_messages.append(("assistant", reply))
                            apply_chat_sentiment_effects(state, pet, user_text + "\n" + reply, floats, font)
                            input_text = ""
                        else:
                            # empty enter closes dialog
                            chat_open = False
                            typing = False
                    elif event.key == pg.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        ch = event.unicode
                        if ch and 32 <= ord(ch) < 127 and len(input_text) < 200:
                            input_text += ch
                    # do not process other hotkeys while chat dialog open
                # When typing minimal overlay (legacy)
                elif typing:
                    if event.key == pg.K_ESCAPE:
                        typing = False
                        input_text = ""
                    elif event.key == pg.K_RETURN:
                        typing = False
                        if input_text.strip():
                            if chat.is_ready():
                                chat.push_user(input_text.strip())
                                reply = chat.reply()
                            else:
                                reply = "(chat disabled)"
                            floats.append((font.render(f"You: {input_text.strip()}", False, WHITE), 6, VIRTUAL_H-30))
                            floats.append((font.render(f"Pet: {reply[:28]}", False, WHITE), 6, VIRTUAL_H-20))
                            apply_chat_sentiment_effects(state, pet, input_text + "\n" + reply, floats, font)
                        input_text = ""
                    elif event.key == pg.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        ch = event.unicode
                        if ch and 32 <= ord(ch) < 127 and len(input_text) < 80:
                            input_text += ch
                    # do not process other hotkeys while typing
                elif event.key in (pg.K_ESCAPE, pg.K_q):
                    running = False
                elif event.key == pg.K_h and not (chat_open or typing):
                    show_help = not show_help
                elif event.key == pg.K_m:
                    muted = not muted
                elif event.key == pg.K_t:
                    # open dialog chat UI instead of inline
                    chat_open = True
                    typing = True
                    input_text = ""
                elif event.key == pg.K_r and not state.alive:
                    state = PetState(); state.apply_offline(pg.time.get_ticks()/1000.0)
                    state.appearance = random_appearance(); particles.clear(); floats.clear()
                elif event.key == pg.K_LEFT:
                    action_idx = (action_idx - 1) % len(actions)
                elif event.key == pg.K_RIGHT:
                    action_idx = (action_idx + 1) % len(actions)
                elif event.key in (pg.K_UP, pg.K_RETURN, pg.K_SPACE):
                    name, _, _ = actions[action_idx]
                    do_action_with_fx(state, name, pet, particles, floats, muted, font)
                elif event.key == pg.K_f:
                    do_action_with_fx(state, "Feed", pet, particles, floats, muted, font)
                elif event.key == pg.K_p:
                    do_action_with_fx(state, "Play", pet, particles, floats, muted, font)
                elif event.key == pg.K_s:
                    do_action_with_fx(state, "Sleep", pet, particles, floats, muted, font)
                elif event.key == pg.K_c:
                    do_action_with_fx(state, "Clean", pet, particles, floats, muted, font)
            elif event.type == pg.MOUSEMOTION:
                mx, my = event.pos
                vx, vy = mx // SCALE, my // SCALE
                if state.alive:
                    hovered_idx = hit_test_action(vx, vy, font)
                else:
                    hovered_idx = None
                # chat button hover
                hovered_chat = get_chat_button_rect(font).collidepoint(vx, vy)
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                vx, vy = mx // SCALE, my // SCALE
                # chat button click
                if get_chat_button_rect(font).collidepoint(vx, vy):
                    chat_open = True
                    typing = True
                    input_text = ""
                    continue
                if state.alive:
                    idx = hit_test_action(vx, vy, font)
                    if idx is not None:
                        action_idx = idx
                        name, _, _ = actions[action_idx]
                        do_action_with_fx(state, name, pet, particles, floats, muted, font)
                else:
                    if hit_test_respawn(vx, vy, font):
                        state = PetState(); state.apply_offline(pg.time.get_ticks()/1000.0)
                        state.appearance = random_appearance(); particles.clear(); floats.clear(); save_state(state)

        if state.alive:
            state.tick(dt)
            pet.update(dt)
        for p in particles: p.update(dt)
        particles = [p for p in particles if p.life > 0]
        floats = [(s, x, y-12*dt) for (s, x, y) in floats if y > -10]

        canvas.begin(); surf = canvas.surface
        for gx in range(0, VIRTUAL_W, 8): pg.draw.line(surf, (24,24,24), (gx,0), (gx,VIRTUAL_H))
        for gy in range(0, VIRTUAL_H, 8): pg.draw.line(surf, (24,24,24), (0,gy), (VIRTUAL_W,gy))

        mood = compute_mood(state)
        px = VIRTUAL_W//2 - 12; py = VIRTUAL_H//2 - 10
        if not state.appearance: state.appearance = random_appearance()
        pet.draw(surf, px, py, mood, state.asleep, state.appearance)

        draw_bar(surf, 6, 6, 40, 4, 1 - state.hunger, GREEN); surf.blit(font.render("Food", False, WHITE), (6, 1))
        draw_bar(surf, 6, 16, 40, 4, state.energy, YELLOW); surf.blit(font.render("Energy", False, WHITE), (6, 11))
        draw_bar(surf, 6, 26, 40, 4, state.fun, CYAN); surf.blit(font.render("Fun", False, WHITE), (6, 21))
        draw_bar(surf, 6, 36, 40, 4, state.hygiene, BLUE); surf.blit(font.render("Clean", False, WHITE), (6, 31))

        if state.alive:
            draw_actions(surf, font, action_idx, hovered_idx)
            surf.blit(font.render(f"Mood {int(mood*100)}%", False, WHITE), (VIRTUAL_W-52, 2))
            if state.asleep: surf.blit(font.render("Z z z", False, WHITE), (px+18, py-6))
        else:
            draw_death_screen(surf, font, state.death_reason)

        for s, x, y in floats: surf.blit(s, (int(x), int(y)))

        if show_help and state.alive: draw_help(surf, font)

        # Chat button
        draw_chat_button(surf, font, hovered_chat, chat_open)

        # Chat dialog box
        if chat_open:
            draw_chat_dialog(surf, chat_font, chat_messages, input_text, int(pg.time.get_ticks()/300)%2==0)

        canvas.end_blit(screen); pg.display.flip()

    save_state(state); pg.quit()


def draw_actions(surf: pg.Surface, font, active_idx: int, hovered_idx: Optional[int]):
    margin = 6; ax = margin; row_h = font.get_height() + 6
    x = ax; y = VIRTUAL_H - (row_h + 4); gap = 4
    for i, (name, hot, _) in enumerate(actions):
        label = f"[{hot}] {name}"; w, h = font.size(label)
        if x + w + 6 > VIRTUAL_W - margin: x = ax; y -= row_h
        rect = pg.Rect(x-2, y-2, w+4, h+4)
        bg = (30,30,30); bg = (40,40,60) if i == active_idx else bg; bg = (60,60,80) if hovered_idx == i else bg
        pg.draw.rect(surf, bg, rect); pg.draw.rect(surf, (0,0,0), rect, 1)
        surf.blit(font.render(label, False, WHITE), (x, y)); x += w + gap + 6


def hit_test_action(vx: int, vy: int, font) -> Optional[int]:
    margin = 6; ax = margin; row_h = font.get_height() + 6
    x = ax; y = VIRTUAL_H - (row_h + 4); gap = 4
    for i, (name, hot, _) in enumerate(actions):
        label = f"[{hot}] {name}"; w, h = font.size(label)
        if x + w + 6 > VIRTUAL_W - margin: x = ax; y -= row_h
        rect = pg.Rect(x-2, y-2, w+4, h+4)
        if rect.collidepoint(vx, vy): return i
        x += w + gap + 6
    return None


def draw_death_screen(surf: pg.Surface, font, reason: str):
    pg.draw.rect(surf, (0,0,0), (0,0,VIRTUAL_W,VIRTUAL_H))
    w, h = 110, 60; x, y = (VIRTUAL_W - w)//2, (VIRTUAL_H - h)//2
    pg.draw.rect(surf, (20,20,20), (x, y, w, h)); pg.draw.rect(surf, WHITE, (x, y, w, h), 1)
    lines = ["Your Pixelgotchi", f"has died ({reason}).", "Press R or click"]
    for i, line in enumerate(lines): surf.blit(font.render(line, False, WHITE), (x+6, y+6 + i*12))
    bx, by, bw, bh = x+8, y+h-18, w-16, 12
    pg.draw.rect(surf, (40,40,60), (bx, by, bw, bh)); pg.draw.rect(surf, (0,0,0), (bx, by, bw, bh), 1)
    label = "Respawn"; tw, th = font.size(label)
    surf.blit(font.render(label, False, WHITE), (bx + (bw - tw)//2, by + (bh - th)//2))


def hit_test_respawn(vx: int, vy: int, font) -> bool:
    w, h = 110, 60; x, y = (VIRTUAL_W - w)//2, (VIRTUAL_H - h)//2
    bx, by, bw, bh = x+8, y+h-18, w-16, 12
    return pg.Rect(bx, by, bw, bh).collidepoint(vx, vy)


def get_chat_button_rect(font):
    label = "Chat"
    w, h = font.size(label)
    bx = VIRTUAL_W - (w + 10) - 4
    by = 2 + 12  # below mood text
    return pg.Rect(bx, by, w + 10, h + 6)


def draw_chat_button(surf: pg.Surface, font, hovered: bool, active: bool):
    rect = get_chat_button_rect(font)
    bg = (30,30,30)
    if active:
        bg = (40,60,40)
    elif hovered:
        bg = (50,50,70)
    pg.draw.rect(surf, bg, rect)
    pg.draw.rect(surf, (0,0,0), rect, 1)
    label = "Chat"
    w, h = font.size(label)
    surf.blit(font.render(label, False, WHITE), (rect.x + (rect.w - w)//2, rect.y + (rect.h - h)//2))


def apply_chat_sentiment_effects(state: PetState, pet: PetSprite, text: str, floats: List, font):
    from .config import (
        CHAT_SENTIMENT_FUN_GAIN, CHAT_SENTIMENT_FUN_LOSS,
        CHAT_SENTIMENT_ENERGY_GAIN, CHAT_SENTIMENT_ENERGY_LOSS,
        CHAT_SENTIMENT_HYGIENE_GAIN, CHAT_SENTIMENT_HYGIENE_LOSS,
    )
    s, label = sentiment_score(text)
    # map [-1,1] → [-loss, +gain]
    if s > 0:
        dfun = s * CHAT_SENTIMENT_FUN_GAIN
        denergy = s * CHAT_SENTIMENT_ENERGY_GAIN
        dhyg = s * CHAT_SENTIMENT_HYGIENE_GAIN
        pet.set_emotion("love", 1.0)
        floats.append((font.render("(feels better)", False, WHITE), 6, 6))
    elif s < 0:
        dfun = s * CHAT_SENTIMENT_FUN_LOSS
        denergy = s * CHAT_SENTIMENT_ENERGY_LOSS
        dhyg = s * CHAT_SENTIMENT_HYGIENE_LOSS
        pet.set_emotion("sad", 1.0)
        floats.append((font.render("(feels worse)", False, WHITE), 6, 6))
    else:
        dfun = denergy = dhyg = 0.0
        floats.append((font.render("(neutral)", False, WHITE), 6, 6))
    # apply, clamp
    from .state import clamp
    state.fun = clamp(state.fun + dfun)
    state.energy = clamp(state.energy + denergy)
    state.hygiene = clamp(state.hygiene + dhyg)
