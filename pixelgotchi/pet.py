import math
import pygame as pg
from typing import Optional, List, Tuple
from .config import *

class PetSprite:
    def __init__(self):
        self.t = 0.0
        self.reaction = 0.0
        self.face_mode: str = ""
        self.face_timer: float = 0.0

    def update(self, dt: float):
        self.t += dt
        if self.reaction > 0:
            self.reaction = max(0.0, self.reaction - dt * 3)
        if self.face_timer > 0:
            self.face_timer = max(0.0, self.face_timer - dt)
            if self.face_timer == 0:
                self.face_mode = ""

    def draw(self, surf: pg.Surface, x: int, y: int, mood: float, asleep: bool, app: Optional[dict] = None):
        if app is None:
            app = {
                "w": 24, "h": 16,
                "squash_x": 1.0, "squash_y": 1.0,
                "roundness": 0.22,
                "base_color": (120, 200, 140),
                "belly_color": (200, 230, 210),
                "spots": [],
                "eyes": "dot",
            }
        base_col = lerp_color(app.get("base_color", (80,200,120)), (200, 80, 80), 1 - mood)
        w = int(app.get("w", 24)); h = int(app.get("h", 16))
        squash_x = float(app.get("squash_x", 1.0)); squash_y = float(app.get("squash_y", 1.0))
        roundness = float(app.get("roundness", 0.22))
        ry = int(self.reaction * 2)
        px = pg.PixelArray(surf)
        for yy in range(h):
            for xx in range(w):
                rx = xx - w//2
                ryy = yy - h//2
                if (rx*rx)/(w*w*roundness*squash_x) + (ryy*ryy)/(h*h*0.3*squash_y) <= 1.0:
                    px[x+xx, y+yy - ry] = base_col
        del px
        belly = app.get("belly_color")
        if belly:
            bx0, by0 = x + w//2, y + h//2 - ry
            for yy in range(-h//3, h//3):
                for xx in range(-w//4, w//4):
                    if (xx*xx)/(w*w*0.06) + (yy*yy)/(h*h*0.10) <= 1.0:
                        sx, sy = bx0+xx, by0+yy
                        if 0 <= sx < VIRTUAL_W and 0 <= sy < VIRTUAL_H:
                            surf.set_at((sx, sy), belly)
        for ox, oy, rr, col in app.get("spots", []):
            cx, cy = x + w//2 + int(ox), y + h//2 - ry + int(oy)
            for yy in range(-rr, rr+1):
                for xx in range(-rr, rr+1):
                    if xx*xx + yy*yy <= rr*rr:
                        sx, sy = cx+xx, cy+yy
                        if 0 <= sx < VIRTUAL_W and 0 <= sy < VIRTUAL_H:
                            surf.set_at((sx, sy), col)
        blink = 1 if (int(self.t*2)%6==0) else 0
        eye_open = 0 if blink and not asleep else 1
        eye_y = y + h//2 - 4 - ry
        eye_x1 = x + w//2 - 6
        eye_x2 = x + w//2 + 3
        col_eye = BLACK if eye_open else base_col
        if asleep:
            pg.draw.line(surf, BLACK, (eye_x1-1, eye_y), (eye_x1+1, eye_y))
            pg.draw.line(surf, BLACK, (eye_x2-1, eye_y), (eye_x2+1, eye_y))
        else:
            style = app.get("eyes", "dot")
            if self.face_mode in ("love", "excited"): style = "wide"
            elif self.face_mode in ("tired", "sleepy"): style = "flat"
            elif self.face_mode == "star": style = "star"
            elif self.face_mode == "angry": style = "flat"
            elif self.face_mode == "surprised": style = "wide"
            elif self.face_mode == "sad": style = "oval"
            if style == "dot":
                surf.set_at((eye_x1, eye_y), col_eye); surf.set_at((eye_x1, eye_y+1), col_eye)
                surf.set_at((eye_x2, eye_y), col_eye); surf.set_at((eye_x2, eye_y+1), col_eye)
            elif style == "oval":
                for dy in range(3):
                    surf.set_at((eye_x1, eye_y+dy), col_eye); surf.set_at((eye_x2, eye_y+dy), col_eye)
            elif style == "wide":
                for dx in range(3):
                    surf.set_at((eye_x1+dx, eye_y), col_eye); surf.set_at((eye_x2+dx, eye_y), col_eye)
            elif style == "flat":
                pg.draw.line(surf, col_eye, (eye_x1-1, eye_y), (eye_x1+1, eye_y))
                pg.draw.line(surf, col_eye, (eye_x2-1, eye_y), (eye_x2+1, eye_y))
            elif style == "star":
                for ex in (eye_x1, eye_x2):
                    for dx, dy in ((0,0),(-1,0),(1,0),(0,-1),(0,1)):
                        surf.set_at((ex+dx, eye_y+dy), YELLOW)
            if self.face_mode == "angry":
                pg.draw.line(surf, BLACK, (eye_x1-2, eye_y-2), (eye_x1+1, eye_y-1))
                pg.draw.line(surf, BLACK, (eye_x2+2, eye_y-2), (eye_x2-1, eye_y-1))
        mlen = 6
        my = y + h//2 + 2 - ry
        mx = x + w//2 - mlen//2
        mouth_mode = None
        if self.face_mode in ("love", "excited"): mouth_mode = "big_smile"
        elif self.face_mode in ("tired", "sleepy"): mouth_mode = "flat"
        elif self.face_mode == "yuck": mouth_mode = "zigzag"
        elif self.face_mode == "surprised": mouth_mode = "oh"
        elif self.face_mode == "angry": mouth_mode = "frown_deep"
        elif self.face_mode == "sad": mouth_mode = "frown"
        if mouth_mode == "big_smile":
            for i in range(mlen):
                surf.set_at((mx+i, my + (i in (0, mlen-1)) ), BLACK)
                if i % 2 == 0 and my+1 < VIRTUAL_H: surf.set_at((mx+i, my+1), BLACK)
        elif mouth_mode == "zigzag":
            for i in range(mlen):
                oy = -1 if i % 2 == 0 else 1
                if 0 <= my+oy < VIRTUAL_H: surf.set_at((mx+i, my+oy), BLACK)
        elif mouth_mode == "flat":
            for i in range(mlen): surf.set_at((mx+i, my), BLACK)
        elif mouth_mode == "oh":
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    if abs(dx)+abs(dy) <= 1: surf.set_at((mx+2+dx, my+dy), BLACK)
        elif mouth_mode == "frown_deep":
            for i in range(mlen):
                surf.set_at((mx+i, my - 1), BLACK)
                if i in (0, mlen-1) and my-2 >= 0: surf.set_at((mx+i, my - 2), BLACK)
        elif mouth_mode == "frown":
            for i in range(mlen): surf.set_at((mx+i, my - (i in (0, mlen-1)) ), BLACK)
        if self.face_mode == "love":
            draw_heart_icon(surf, x + w//2 + 10, y - 6 - ry)
            draw_heart_icon(surf, x + w//2 + 6, y - 10 - ry)
        elif self.face_mode == "excited":
            draw_sparkle_icon(surf, x + w//2 + 10, y - 6 - ry)
        elif self.face_mode == "tired":
            draw_sweat_icon(surf, x + w//2 + 9, eye_y - 6)
        elif self.face_mode == "sad":
            draw_teardrop_icon(surf, eye_x2+1, eye_y+2)
        if not asleep:
            pg.draw.rect(surf, (10,10,10), (x+4, y+h+4, w-8, 2))

    def set_emotion(self, mode: str, duration: float = 1.2):
        self.face_mode = mode
        self.face_timer = duration


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i]) * t) for i in range(3))


def draw_heart_icon(surf: pg.Surface, x: int, y: int):
    pts = [(1,0),(3,0),(0,1),(2,1),(4,1),(0,2),(4,2),(1,3),(3,3),(2,2)]
    for dx, dy in pts:
        if 0 <= x+dx < VIRTUAL_W and 0 <= y+dy < VIRTUAL_H:
            surf.set_at((x+dx, y+dy), RED)

def draw_sparkle_icon(surf: pg.Surface, x: int, y: int):
    for dx in (-1,0,1):
        if 0 <= x+dx < VIRTUAL_W and 0 <= y < VIRTUAL_H: surf.set_at((x+dx, y), YELLOW)
    for dy in (-1,0,1):
        if 0 <= x < VIRTUAL_W and 0 <= y+dy < VIRTUAL_H: surf.set_at((x, y+dy), YELLOW)

def draw_sweat_icon(surf: pg.Surface, x: int, y: int):
    if 0 <= x < VIRTUAL_W and 0 <= y < VIRTUAL_H: surf.set_at((x, y), BLUE)
    for dy in (1,2):
        if 0 <= x < VIRTUAL_W and 0 <= y+dy < VIRTUAL_H: surf.set_at((x, y+dy), CYAN)

def draw_teardrop_icon(surf: pg.Surface, x: int, y: int):
    for dy in range(3):
        if 0 <= x < VIRTUAL_W and 0 <= y+dy < VIRTUAL_H: surf.set_at((x, y+dy), CYAN)
