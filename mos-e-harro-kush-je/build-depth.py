#!/usr/bin/env python3
"""Depth maps of the stills, for the 2.5D parallax shader of index.html (V5).

No depth model is available here, so each map is built by hand from what the picture contains: masks drawn from the
colours of the image (window opening, sky, photographic paper) and simple geometric planes (floor, wall, hillside).
White = near, black = far. Written at half resolution (576 x 1024) and blurred, so the shader stretches pixels softly
at depth edges instead of tearing them.

Usage: python3 build-depth.py  ->  assets/img/ia/depth/<name>.png
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets/img/ia")
OUT = os.path.join(SRC, "depth")
W, H = 576, 1024


def load(name):
    im = Image.open(os.path.join(SRC, name + ".jpg")).convert("RGB").resize((W, H), Image.LANCZOS)
    a = np.asarray(im, dtype=np.float32) / 255.0
    lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    sat = (mx - mn) / (mx + 1e-4)
    return a, lum, sat


def blur(m, r):
    return np.asarray(Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) / 255.0


def poly(points):
    im = Image.new("L", (W, H), 0)
    ImageDraw.Draw(im).polygon(points, fill=255)
    return np.asarray(im, dtype=np.float32) / 255.0


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def fenetre():
    a, lum, sat = load("01-fenetre")
    # the view through the opening: bright pixels between the two open shutters, under the arch
    box = poly([(226, 272), (398, 272), (398, 646), (226, 646)])
    view = box * (lum > 0.30)
    view = blur(view, 1.5)
    view = (view > 0.5).astype(np.float32)
    # inside the room: back wall at mid depth, the shutters and the frame nearer, the floor comes to the camera
    d = np.full((H, W), 0.62, np.float32)
    shutters = poly([(118, 270), (226, 285), (226, 662), (118, 668)]) + poly([(398, 285), (476, 262), (476, 672), (398, 662)])
    d = np.maximum(d, 0.78 * np.clip(shutters, 0, 1))
    floor = np.clip((yy - 660) / 360, 0, 1)
    d = np.maximum(d, 0.62 + 0.38 * floor)
    # outside: the fog is far, the peaks a little nearer than the fog
    out = 0.06 + 0.10 * np.clip((560 - yy) / 260, 0, 1) * (lum > 0.42)
    d = d * (1 - view) + out * view
    return blur(d, 3)


def photo():
    a, lum, sat = load("02-photo")
    # the print: low saturation, inside a hand-drawn quad around the deckled edges
    paper = poly([(84, 371), (477, 341), (528, 582), (109, 628)])
    # the sill recedes toward the wall; the wall and the window are far
    d = 0.18 + 0.62 * np.clip((yy - 200) / 820, 0, 1)
    d = np.where(yy < 300, 0.12 + 0.1 * yy / 300, d)
    d = np.maximum(d, paper * 0.86)
    return blur(d, 3)


def kulla():
    # outlines traced on a 50 px grid of the still (576 x 1024)
    sky = poly([(0, 0), (576, 0), (576, 382), (520, 385), (470, 375), (430, 362), (386, 368), (386, 240), (400, 235), (402, 165),
                (415, 160), (262, 100), (120, 150), (136, 158), (136, 330), (90, 310), (40, 290), (0, 262)])
    tower = poly([(120, 150), (262, 100), (415, 160), (402, 165), (400, 235), (386, 240), (386, 505), (270, 500), (136, 470), (136, 158)])
    ridges = poly([(386, 368), (430, 362), (470, 375), (520, 385), (576, 382), (576, 560), (386, 470)])
    # the hillside and the path come toward the camera
    d = 0.30 + 0.70 * np.clip((yy - 380) / 640, 0, 1) ** 1.2
    d = np.where(ridges > 0.5, 0.14 + 0.16 * np.clip((yy - 370) / 190, 0, 1), d)
    d = np.where(tower > 0.5, 0.42, d)
    d = np.where(sky > 0.5, 0.0, d)
    return blur(d, 2.5)


def qyteti():
    # sky above the castle hill and the far ridges; the town recedes from the river (near) to the hill (far)
    sky = poly([(0, 0), (576, 0), (576, 365), (480, 360), (470, 330), (400, 345), (400, 285), (130, 285), (120, 310), (80, 320), (0, 330)])
    d = 0.18 + 0.82 * np.clip((yy - 300) / 720, 0, 1) ** 1.1
    d = np.where(sky > 0.5, 0.0, d)
    return blur(d, 2.5)


def fletorja():
    # dark room and candle far, the page rises toward the camera, the pen lies above the page
    d = 0.15 + 0.85 * np.clip((yy - 260) / 760, 0, 1)
    candle = poly([(205, 15), (325, 15), (330, 265), (200, 265)])
    d = np.where(candle > 0.5, 0.22, d)
    pen = poly([(255, 398), (300, 405), (576, 608), (576, 690), (500, 652), (296, 470)])
    d = np.maximum(d, pen * 0.92)
    return blur(d, 3)


def alpet():
    # sky, then ridge after ridge toward the camera, two dark foreground cliffs
    sky = poly([(0, 0), (576, 0), (576, 320), (500, 310), (470, 330), (420, 300), (380, 290), (330, 310), (300, 295), (240, 320),
                (150, 330), (80, 320), (0, 335)])
    d = 0.10 + 0.55 * np.clip((yy - 300) / 600, 0, 1)
    cliff_r = poly([(576, 520), (530, 540), (470, 560), (420, 600), (380, 640), (350, 700), (380, 800), (420, 900), (420, 1024), (576, 1024)])
    cliff_l = poly([(0, 650), (60, 660), (100, 720), (130, 900), (150, 1024), (0, 1024)])
    d = np.maximum(d, np.maximum(cliff_r * 0.85, cliff_l * 0.80))
    d = np.where(sky > 0.5, 0.0, d)
    return blur(d, 2.5)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in [("01-fenetre", fenetre), ("02-photo", photo), ("03-kulla", kulla), ("05-qyteti", qyteti), ("06-fletorja", fletorja),
                     ("08-alpet", alpet)]:
        Image.fromarray((np.clip(fn(), 0, 1) * 255).astype(np.uint8)).save(os.path.join(OUT, name + ".png"))
        print("wrote", os.path.join("assets/img/ia/depth", name + ".png"))
