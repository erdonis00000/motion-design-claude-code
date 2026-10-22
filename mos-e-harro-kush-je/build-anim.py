#!/usr/bin/env python3
"""Animation maps of the stills (V7): where each still is allowed to move, and how.

One RGB map per still, 576 x 1024, read by the shader of index.html (no alpha: browsers drop the colour of fully
transparent pixels when they decode a PNG):
  R  drift  : mist, haze and clouds that flow slowly (domain warp + soft wisps tinted by the local colour)
  G  water  : the river, its ripples and the sparkle of the street lights on it; on a still without water, the
              grass that bends in a gust (the shot says which, with its water or breeze amount)
  B  light  : a flame, a lamp or lit windows (flicker, flame sway, windows that come on)
A black map means: this still stays a still (only the camera, light and dust move).

The eagle of the panorama is cut out (08-alpet-aigle.png, alpha from its contrast against the sky) and the sky behind
it is rebuilt by diffusion (08-alpet-ciel.jpg), so the shader can let it glide across the sky.

Usage: python3 build-anim.py  ->  assets/img/ia/anim/<name>.png, assets/img/ia/08-alpet-ciel.jpg, 08-alpet-aigle.png
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets/img/ia")
OUT = os.path.join(SRC, "anim")
W, H = 576, 1024
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def load(name, size=(W, H)):
    im = Image.open(os.path.join(SRC, name + ".jpg")).convert("RGB")
    if size:
        im = im.resize(size, Image.LANCZOS)
    a = np.asarray(im, dtype=np.float32) / 255.0
    lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    return a, lum, (mx - mn) / (mx + 1e-4)


def blur(m, r):
    return np.asarray(Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) / 255.0


def poly(points):
    im = Image.new("L", (W, H), 0)
    ImageDraw.Draw(im).polygon(points, fill=255)
    return np.asarray(im, dtype=np.float32) / 255.0


def disc(cx, cy, r):
    return np.clip(1 - np.hypot(xx - cx, yy - cy) / r, 0, 1)


def save(name, r=None, g=None, b=None):
    z = np.zeros((H, W), np.float32)
    rgb = np.stack([z if c is None else c for c in (r, g, b)], -1)
    Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8), "RGB").save(os.path.join(OUT, name + ".png"))
    print("wrote", "assets/img/ia/anim/" + name + ".png")


def fenetre():
    a, lum, sat = load("01-fenetre")
    view = poly([(226, 272), (398, 272), (398, 646), (226, 646)]) * (lum > 0.30)
    mist = view * np.clip((yy - 440) / 80, 0, 1)            # the sea of fog below the peaks
    save("01-fenetre", r=blur(mist, 4))


def photo():
    save("02-photo")                                        # a print does not move: only the light on it


def kulla():
    a, lum, sat = load("03-kulla")
    ridges = poly([(386, 368), (430, 362), (470, 375), (520, 385), (576, 382), (576, 560), (386, 470)])
    lamp = disc(207, 313, 9)
    tower = poly([(110, 140), (262, 92), (425, 155), (410, 245), (394, 515), (130, 480)])
    # grass only, traced by hand on a 25 px grid: the walls and the path are lit with the same warm colour as the dry
    # grass, and a stone that sways gives the trick away at once
    grass = np.maximum.reduce([
        poly([(0, 530), (40, 540), (90, 565), (150, 585), (200, 600), (235, 625), (238, 648), (160, 652), (80, 648), (0, 652)]),
        poly([(0, 420), (130, 450), (250, 500), (380, 520), (470, 545), (576, 560), (576, 630), (500, 598), (420, 606), (300, 596), (240, 582),
              (150, 556), (60, 512), (0, 498)]),
        poly([(232, 682), (258, 690), (250, 760), (215, 840), (172, 896), (152, 858), (182, 780), (220, 702)]),
        poly([(452, 662), (576, 642), (576, 800), (530, 760), (470, 702)])])
    grass = blur(grass, 4) * (tower < 0.5)
    save("03-kulla", r=blur(ridges, 6) * 0.8, g=grass, b=lamp)


def qyteti():
    a, lum, sat = load("05-qyteti")
    water = poly([(240, 635), (430, 635), (450, 710), (500, 780), (530, 850), (576, 950), (576, 1024), (20, 1024), (60, 900), (100, 810),
                  (130, 750), (190, 710)])
    sky = poly([(0, 0), (576, 0), (576, 378), (480, 372), (470, 340), (400, 357), (400, 295), (130, 295), (120, 320), (80, 330), (0, 340)])
    warm = (a[..., 0] > 0.55) & (a[..., 1] > 0.36) & (a[..., 2] < a[..., 0] * 0.62) & (yy > 420) & (yy < 590) & ((xx < 222) | (xx > 306)) & (sky < 0.5)
    windows = blur(warm.astype(np.float32), 0.8)
    windows = np.clip(windows * 1.6, 0, 1)
    save("05-qyteti", g=blur(water, 2), b=windows)


def fletorja():
    a, lum, sat = load("06-fletorja")
    flame = poly([(246, 20), (285, 20), (290, 140), (241, 140)])      # the flame and a margin it can sway into
    save("06-fletorja", b=blur(flame, 3))


def alpet():
    a, lum, sat = load("08-alpet")
    sky = poly([(0, 0), (576, 0), (576, 320), (500, 310), (470, 330), (420, 300), (380, 290), (330, 310), (300, 295), (240, 320),
                (150, 330), (80, 320), (0, 335)])
    local = blur(lum, 6)
    mist = ((lum > 0.42) & (sat < 0.62) & (yy > 380) & (yy < 820) & (np.abs(lum - local) < 0.05)).astype(np.float32)
    drift = np.maximum(sky * 0.9, blur(mist, 5) * 0.9)
    save("08-alpet", r=blur(drift, 3))


def eagle():
    """Cut the eagle out of the panorama at full resolution and rebuild the sky behind it."""
    im = Image.open(os.path.join(SRC, "08-alpet.jpg")).convert("RGB")
    a = np.asarray(im, dtype=np.float32) / 255.0
    x0, y0, x1, y1 = 540, 305, 690, 402                     # box around the bird (full resolution)
    box = a[y0:y1, x0:x1]
    lum = 0.2126 * box[..., 0] + 0.7152 * box[..., 1] + 0.0722 * box[..., 2]
    # the sky around the bird: a smooth surface fitted on the border of the box (bilinear in x and y)
    h, w = lum.shape
    gy, gx = np.mgrid[0:h, 0:w].astype(np.float32)
    ring = np.zeros((h, w), bool); ring[:4] = ring[-4:] = True; ring[:, :4] = ring[:, -4:] = True
    A = np.stack([np.ones(ring.sum()), gx[ring], gy[ring], gx[ring] * gy[ring], gx[ring] ** 2, gy[ring] ** 2], 1)
    sky = np.zeros_like(box)
    for c in range(3):
        coef, *_ = np.linalg.lstsq(A, box[..., c][ring], rcond=None)
        sky[..., c] = coef[0] + coef[1] * gx + coef[2] * gy + coef[3] * gx * gy + coef[4] * gx ** 2 + coef[5] * gy ** 2
    sky_l = 0.2126 * sky[..., 0] + 0.7152 * sky[..., 1] + 0.0722 * sky[..., 2]
    alpha = np.clip((sky_l - lum - 0.06) / 0.22, 0, 1)        # the bird is darker than the sky behind it
    alpha = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)), dtype=np.float32) / 255.0
    # colour of the bird with the sky un-mixed out of the edges
    col = np.clip((box - sky * (1 - alpha[..., None])) / np.maximum(alpha[..., None], 0.05), 0, 1)
    sprite = np.dstack([col, alpha])
    Image.fromarray((sprite * 255).astype(np.uint8), "RGBA").save(os.path.join(SRC, "08-alpet-aigle.png"))
    # clean plate: the fitted sky where the bird was, plus the grain of the surrounding sky so the patch does not show
    rng = np.random.default_rng(3)
    grain = (box - blur_rgb(box, 2.0)) * (1 - alpha[..., None])
    noise = rng.normal(0, grain[alpha < 0.05].std() * 0.62, box.shape).astype(np.float32)
    fill = sky + noise
    mask = np.clip(np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(2.5)),
                              dtype=np.float32) / 255.0 * 1.6, 0, 1)[..., None]
    clean = a.copy()
    clean[y0:y1, x0:x1] = box * (1 - mask) + fill * mask
    Image.fromarray((np.clip(clean, 0, 1) * 255).astype(np.uint8)).save(os.path.join(SRC, "08-alpet-ciel.jpg"), quality=95)
    cx, cy = (x0 + x1) / 2 / 1152, (y0 + y1) / 2 / 2048
    print(f"wrote 08-alpet-aigle.png ({x1 - x0} x {y1 - y0}) centred at uv ({cx:.4f}, {cy:.4f}) and 08-alpet-ciel.jpg")


def blur_rgb(a, r):
    return np.stack([blur(a[..., c], r) for c in range(3)], -1)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn in (fenetre, photo, kulla, qyteti, fletorja, alpet, eagle):
        fn()
