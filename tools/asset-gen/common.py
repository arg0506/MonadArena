"""Shared palette and pixel helpers for the Monad Arena asset generator.

All art is drawn at native pixel resolution and exported at SCALE x with
nearest-neighbour upscaling, so Phaser should run with `pixelArt: true`.
"""
from __future__ import annotations

import colorsys
import math
import os
from pathlib import Path

from PIL import Image

SCALE = 2
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "apps" / "web" / "public" / "assets"


def hexc(h: str, a: int = 255) -> tuple[int, int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def with_alpha(c, a):
    return (c[0], c[1], c[2], a)


def shade(c, factor: float):
    """factor < 1 darkens (and shifts hue slightly towards blue), > 1 lightens."""
    r, g, b = [x / 255 for x in c[:3]]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if factor < 1:
        l = l * factor
        h = (h + (0.66 - h) * 0.08) % 1.0  # cool the shadows
    else:
        l = min(1.0, l + (1 - l) * (factor - 1))
        h = (h + (0.14 - h) * 0.05) % 1.0  # warm the highlights a touch
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (round(r * 255), round(g * 255), round(b * 255), c[3] if len(c) > 3 else 255)


# --- Core palette (dark neon) -------------------------------------------------
P = {
    "outline": hexc("#0a0818"),
    "void": hexc("#0d0b1e"),
    "bg1": hexc("#15122e"),
    "bg2": hexc("#1e1a40"),
    "bg3": hexc("#2a2557"),
    "floor": hexc("#1a1733"),
    "floor_alt": hexc("#1c1937"),
    "floor_line": hexc("#141129"),
    "floor_hi": hexc("#242046"),
    "circuit": hexc("#2f2866"),
    "wall_top": hexc("#4b3f8f"),
    "wall_top_hi": hexc("#6d5fd0"),
    "wall_face": hexc("#2e2660"),
    "wall_face_dk": hexc("#211b49"),
    "wall_dark": hexc("#1a1538"),
    "accent": hexc("#836ef9"),
    "accent_lt": hexc("#b5a6ff"),
    "accent_dk": hexc("#4f3fb8"),
    "white": hexc("#f4f2ff"),
    "suit": hexc("#e8e6ff"),
    "suit_sh": hexc("#a9a4d6"),
    "suit_dk": hexc("#5c5791"),
    "visor": hexc("#10102a"),
    "visor_glint": hexc("#7df9ff"),
    "boot": hexc("#5a5499"),
    "boot_dk": hexc("#3b3670"),
    "shadow": (0, 0, 0, 90),
    # standard crystal (cyan)
    "c_core": hexc("#e9fdff"),
    "c_lt": hexc("#7df3ff"),
    "c_mid": hexc("#3ec6ef"),
    "c_dk": hexc("#1b7fbf"),
    "c_deep": hexc("#123f7a"),
    # rare crystal (magenta + gold)
    "r_core": hexc("#fff1fb"),
    "r_lt": hexc("#ff9cea"),
    "r_mid": hexc("#f04fc9"),
    "r_dk": hexc("#a2259a"),
    "r_deep": hexc("#561a63"),
    "gold": hexc("#ffe066"),
    "gold_dk": hexc("#e0a31a"),
    "warn": hexc("#ffb020"),
    "danger": hexc("#ff4d6d"),
    "ok": hexc("#4ade80"),
}

PLAYER_COLORS = {
    "red": "#ff4d6d",
    "orange": "#ff9f43",
    "yellow": "#ffd93d",
    "green": "#4ade80",
    "cyan": "#22d3ee",
    "blue": "#4f7cff",
    "purple": "#a78bfa",
    "pink": "#f472b6",
}


# --- Canvas helpers -----------------------------------------------------------
def canvas(w: int, h: int, fill=(0, 0, 0, 0)) -> Image.Image:
    return Image.new("RGBA", (w, h), fill)


def px(img: Image.Image, x: int, y: int, c) -> None:
    if 0 <= x < img.width and 0 <= y < img.height and c is not None:
        if len(c) == 4 and c[3] < 255:
            base = img.getpixel((x, y))
            img.putpixel((x, y), blend(base, c))
        else:
            img.putpixel((x, y), c if len(c) == 4 else (*c, 255))


def blend(dst, src):
    sa = src[3] / 255
    da = dst[3] / 255
    oa = sa + da * (1 - sa)
    if oa == 0:
        return (0, 0, 0, 0)
    out = [round((src[i] * sa + dst[i] * da * (1 - sa)) / oa) for i in range(3)]
    return (*out, round(oa * 255))


def rect(img, x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(img, xx, yy, c)


def ellipse(img, cx, cy, rx, ry, c, shade_fn=None):
    """Filled ellipse centred on (cx, cy) using pixel-centre sampling.

    shade_fn(nx, ny) -> colour lets callers shade by normalised position (-1..1).
    """
    for y in range(int(cy - ry - 1), int(cy + ry + 2)):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            nx = (x + 0.5 - cx) / rx
            ny = (y + 0.5 - cy) / ry
            if nx * nx + ny * ny <= 1.0:
                px(img, x, y, shade_fn(nx, ny) if shade_fn else c)


def polygon_fill(img, pts, colour_fn):
    """Scanline polygon fill; colour_fn(x, y) returns a colour or None."""
    ys = [p[1] for p in pts]
    for y in range(int(math.floor(min(ys))), int(math.ceil(max(ys))) + 1):
        yc = y + 0.5
        xs = []
        n = len(pts)
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            if (y1 <= yc < y2) or (y2 <= yc < y1):
                xs.append(x1 + (yc - y1) * (x2 - x1) / (y2 - y1))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(int(math.ceil(xs[i] - 0.5)), int(math.floor(xs[i + 1] - 0.5)) + 1):
                c = colour_fn(x, y)
                if c:
                    px(img, x, y, c)


def outline(img: Image.Image, colour=None, diagonal=False, min_alpha=200) -> Image.Image:
    """Add a 1px outline around opaque pixels (alpha >= min_alpha)."""
    colour = colour or P["outline"]
    src = img.copy()
    w, h = img.size
    nbrs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if diagonal:
        nbrs += [(1, 1), (-1, -1), (1, -1), (-1, 1)]
    for y in range(h):
        for x in range(w):
            if src.getpixel((x, y))[3] >= min_alpha:
                continue
            for dx, dy in nbrs:
                xx, yy = x + dx, y + dy
                if 0 <= xx < w and 0 <= yy < h and src.getpixel((xx, yy))[3] >= min_alpha:
                    img.putpixel((x, y), colour)
                    break
    return img


def glow(img: Image.Image, colour, radius: int, strength: int) -> Image.Image:
    """Soft pixel glow under existing opaque pixels (quantised alpha steps)."""
    w, h = img.size
    src = img.copy()
    solid = [(x, y) for y in range(h) for x in range(w) if src.getpixel((x, y))[3] > 200]
    layer = canvas(w, h)
    for y in range(h):
        for x in range(w):
            if src.getpixel((x, y))[3] > 0:
                continue
            d = min((math.hypot(x - sx, y - sy) for sx, sy in solid), default=99)
            if d <= radius:
                a = strength * (1 - (d - 1) / radius)
                a = int(round(a / 16) * 16)  # quantise for pixel-art banding
                if a > 0:
                    layer.putpixel((x, y), with_alpha(colour, min(255, a)))
    layer.alpha_composite(src)
    return layer


def upscale(img: Image.Image, s: int = SCALE) -> Image.Image:
    return img.resize((img.width * s, img.height * s), Image.NEAREST)


def sheet(frames: list[list[Image.Image]]) -> Image.Image:
    """Rows of frames -> single spritesheet (all frames same size)."""
    fw, fh = frames[0][0].size
    cols = max(len(r) for r in frames)
    out = canvas(fw * cols, fh * len(frames))
    for r, row in enumerate(frames):
        for c, f in enumerate(row):
            out.alpha_composite(f, (c * fw, r * fh))
    return out


def save(img: Image.Image, rel: str, scale: int = SCALE) -> Path:
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    (upscale(img, scale) if scale != 1 else img).save(path, optimize=True)
    return path


def mirror(img: Image.Image) -> Image.Image:
    return img.transpose(Image.FLIP_LEFT_RIGHT)


def ensure_dirs():
    os.makedirs(OUT, exist_ok=True)
