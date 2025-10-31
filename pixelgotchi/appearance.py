import random
from typing import Dict, List, Tuple
from .config import VIRTUAL_W, VIRTUAL_H

Color = Tuple[int,int,int]


def random_color() -> Color:
    return (random.randint(60,220), random.randint(60,220), random.randint(60,220))


def random_appearance() -> Dict:
    w = random.randint(20, 30)
    h = random.randint(14, 22)
    squash_x = round(random.uniform(0.8, 1.3), 2)
    squash_y = round(random.uniform(0.8, 1.3), 2)
    roundness = round(random.uniform(0.16, 0.30), 2)
    base_color = random_color()
    belly_color = random_color() if random.random() < 0.6 else None
    spots: List[Tuple[int,int,int,Color]] = []
    for _ in range(random.randint(0,3)):
        ox = random.randint(-w//3, w//3)
        oy = random.randint(-h//3, h//3)
        rr = random.randint(2,4)
        spots.append((ox, oy, rr, random_color()))
    eyes = random.choice(["dot","oval","wide"])
    return {
        "w": w,
        "h": h,
        "squash_x": squash_x,
        "squash_y": squash_y,
        "roundness": roundness,
        "base_color": base_color,
        "belly_color": belly_color,
        "spots": spots,
        "eyes": eyes,
    }
