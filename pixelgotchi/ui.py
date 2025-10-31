import pygame as pg
from typing import Optional
from .config import VIRTUAL_W, VIRTUAL_H, WHITE


def draw_bar(surf: pg.Surface, x, y, w, h, val, fg, bg=(40,40,40)):
    pg.draw.rect(surf, bg, (x, y, w, h))
    fill = int(w * max(0.0, min(1.0, val)))
    if fill > 0:
        pg.draw.rect(surf, fg, (x, y, fill, h))
    pg.draw.rect(surf, (0,0,0), (x, y, w, h), 1)


def draw_help(surf: pg.Surface, font):
    w, h = 110, 70
    x, y = (VIRTUAL_W - w)//2, (VIRTUAL_H - h)//2
    pg.draw.rect(surf, (0,0,0), (x, y, w, h))
    pg.draw.rect(surf, WHITE, (x, y, w, h), 1)
    lines = [
        "Help",
        "Arrows: choose action",
        "Enter/Space: do action",
        "F/P/S/C: hotkeys",
        "T: chat input",
        "H: toggle help",
        "M: mute",
        "Esc/Q: quit",
    ]
    for i, line in enumerate(lines):
        surf.blit(font.render(line, False, WHITE), (x+4, y+4 + i*9))


# -------- Chat dialog UI --------

def wrap_text(font: pg.font.Font, text: str, max_width: int):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + (" " if cur else "") + w)
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_chat_dialog(surf: pg.Surface, font: pg.font.Font, messages, input_text: str, cursor_on: bool):
    # Centered dialog
    w, h = int(VIRTUAL_W*0.85), int(VIRTUAL_H*0.75)
    x, y = (VIRTUAL_W - w)//2, (VIRTUAL_H - h)//2
    # panel
    pg.draw.rect(surf, (15,15,18), (x, y, w, h))
    pg.draw.rect(surf, (0,0,0), (x, y, w, h), 1)
    # title
    surf.blit(font.render("Chat", True, WHITE), (x+6, y+4))
    # content area
    pad = 6
    content_x = x + pad
    content_y = y + 16
    content_w = w - pad*2
    content_h = h - 30 - pad*2
    # draw a box for messages
    pg.draw.rect(surf, (22,22,26), (content_x, content_y, content_w, content_h))
    pg.draw.rect(surf, (0,0,0), (content_x, content_y, content_w, content_h), 1)
    # render messages (wrap and show from bottom up)
    wrapped_lines = []
    for role, text in messages[-50:]:  # last N
        tag = "You:" if role == "user" else "Pet:"
        for ln in wrap_text(font, f"{tag} {text}", content_w-4):
            wrapped_lines.append(ln)
    # keep only lines that fit
    line_h = font.get_height()+1
    max_lines = content_h // line_h
    shown = wrapped_lines[-max_lines:]
    # draw from top
    ty = content_y + 2
    for ln in shown:
        surf.blit(font.render(ln, True, WHITE), (content_x+2, ty))
        ty += line_h
    # input area
    input_y = y + h - 12
    pg.draw.rect(surf, (22,22,26), (x+pad, input_y, w - pad*2, 10))
    pg.draw.rect(surf, (0,0,0), (x+pad, input_y, w - pad*2, 10), 1)
    prompt = "> " + input_text + ("_" if cursor_on else "")
    # trim input if too long
    while font.size(prompt)[0] > w - pad*2 - 6 and len(input_text) > 0:
        input_text = input_text[1:]
        prompt = "> " + input_text + ("_" if cursor_on else "")
    surf.blit(font.render(prompt, True, WHITE), (x+pad+2, input_y+1))
    return (x, y, w, h)
