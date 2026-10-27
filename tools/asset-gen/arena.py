"""Arena background (1280x720 exported), collision/spawn data, and a 16px tileset.

All coordinates in arena.json are in exported (display) pixels, matching the
1280x720 world in SPEC.md.
"""
import json
import math
import random

from common import (OUT, P, SCALE, canvas, ellipse, px, rect, save, shade, with_alpha)

W, H = 640, 360
T = 16

WALLS = [
    # outer border
    (0, 0, 640, 24), (0, 340, 640, 20), (0, 0, 16, 360), (624, 0, 16, 360),
    # bars
    (112, 84, 72, 22), (456, 84, 72, 22), (112, 252, 72, 22), (456, 252, 72, 22),
    # pillars beside the centre
    (206, 152, 20, 46), (414, 152, 20, 46),
    # nooks top and bottom centre
    (296, 52, 48, 18), (296, 290, 48, 18),
]
PADS = [(56, 62), (584, 62), (56, 302), (584, 302)]
FACE = 8


def floor_tile(img, tx, ty, rng, variant=None):
    x0, y0 = tx * T, ty * T
    base = P["floor"] if (tx + ty) % 2 == 0 else P["floor_alt"]
    rect(img, x0, y0, T, T, base)
    for i in range(T):
        px(img, x0 + i, y0, P["floor_line"])
        px(img, x0, y0 + i, P["floor_line"])
    px(img, x0 + 1, y0 + 1, P["floor_hi"])
    px(img, x0 + 2, y0 + 1, P["floor_hi"])
    px(img, x0 + 1, y0 + 2, P["floor_hi"])
    v = variant if variant is not None else rng.random()
    if v < 0.07:  # bolts
        for bx, by in ((3, 3), (12, 3), (3, 12), (12, 12)):
            px(img, x0 + bx, y0 + by, P["floor_line"])
            px(img, x0 + bx + 1, y0 + by, P["floor_hi"])
    elif v < 0.12:  # crack
        x, y = x0 + rng.randint(4, 10), y0 + 3
        for _ in range(8):
            px(img, x, y, P["floor_line"])
            y += 1
            x += rng.choice((-1, 0, 0, 1))
    elif v < 0.16:  # circuit trace with node
        y = y0 + rng.randint(5, 10)
        c = with_alpha(P["accent"], 70)
        for x in range(x0 + 1, x0 + 10):
            px(img, x, y, c)
        for yy in range(y, y0 + T):
            px(img, x0 + 9, yy, c)
        px(img, x0 + 9, y, with_alpha(P["accent_lt"], 150))
        px(img, x0 + 10, y, with_alpha(P["accent"], 110))
    elif v < 0.19:  # floor vent
        for i in range(4):
            rect(img, x0 + 4, y0 + 4 + i * 2, 8, 1, P["floor_line"])
            rect(img, x0 + 4, y0 + 5 + i * 2, 8, 1, P["floor_hi"])


def seal(img, cx, cy):
    """Centre floor emblem: rings, spokes and an inner hexagon (original design)."""
    for y in range(cy - 70, cy + 70):
        for x in range(cx - 70, cx + 70):
            d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.0)
            if 63 <= d <= 64.2:
                px(img, x, y, with_alpha(P["accent"], 90))
            elif 57 <= d <= 58:
                px(img, x, y, with_alpha(P["accent"], 55))
            elif 22 <= d <= 23:
                px(img, x, y, with_alpha(P["accent_lt"], 60))
    for k in range(6):
        a = k * math.tau / 6 + math.pi / 6
        for r in range(32, 57):
            px(img, round(cx + math.cos(a) * r), round(cy + math.sin(a) * r), with_alpha(P["accent"], 40))
        rx, ry = round(cx + math.cos(a) * 60.5), round(cy + math.sin(a) * 60.5)
        rect(img, rx - 1, ry - 1, 3, 3, with_alpha(P["accent_lt"], 130))
        px(img, rx, ry, with_alpha(P["white"], 200))
    # hexagon
    pts = [(cx + math.cos(k * math.tau / 6) * 32, cy + math.sin(k * math.tau / 6) * 32) for k in range(6)]
    for i in range(6):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % 6]
        steps = int(max(abs(x2 - x1), abs(y2 - y1)))
        for s in range(steps + 1):
            px(img, round(x1 + (x2 - x1) * s / steps), round(y1 + (y2 - y1) * s / steps), with_alpha(P["accent"], 110))
    ellipse(img, cx, cy, 12, 12, with_alpha(P["accent"], 25))
    ellipse(img, cx, cy, 6, 6, with_alpha(P["accent"], 35))


def pad(img, cx, cy):
    ellipse(img, cx, cy, 22, 13, with_alpha(P["accent"], 20))
    pts = [(cx + math.cos(k * math.tau / 6) * 17, cy + math.sin(k * math.tau / 6) * 10) for k in range(6)]
    for i in range(6):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % 6]
        steps = int(max(abs(x2 - x1), abs(y2 - y1))) or 1
        for s in range(steps + 1):
            px(img, round(x1 + (x2 - x1) * s / steps), round(y1 + (y2 - y1) * s / steps), with_alpha(P["accent_lt"], 170))
    ellipse(img, cx, cy, 13, 7, with_alpha(P["bg3"], 200))
    ellipse(img, cx, cy, 5, 3, with_alpha(P["accent"], 120))
    px(img, cx, cy, P["accent_lt"])
    for k in range(6):
        x, y = pts[k]
        px(img, round(x), round(y), P["white"])


def wall(img, x, y, w, h, outer=False):
    top_h = h - FACE
    # top surface
    rect(img, x, y, w, top_h, P["wall_top"])
    for i in range(16, w, 16):
        for yy in range(y + 2, y + top_h - 2):
            px(img, x + i, yy, shade(P["wall_top"], 0.85))
    rect(img, x, y, w, 1, P["wall_top_hi"])
    rect(img, x, y, 1, top_h, P["wall_top_hi"])
    rect(img, x + w - 1, y, 1, top_h, shade(P["wall_top"], 0.8))
    for rx, ry in ((x + 3, y + 3), (x + w - 4, y + 3)):
        if top_h > 6:
            px(img, rx, ry, P["wall_top_hi"])
    # neon trim where top meets face, with a soft spill onto the face
    rect(img, x, y + top_h - 1, w, 1, P["accent_lt"])
    rect(img, x, y + top_h, w, 1, with_alpha(P["accent"], 170))
    # glowing end caps on interior blocks
    if not outer and top_h >= 8:
        for cx in (x + 2, x + w - 5):
            rect(img, cx, y + 2, 3, 3, P["wall_top_hi"])
            px(img, cx + 1, y + 3, P["white"])
    # face
    rect(img, x, y + top_h, w, FACE, P["wall_face"])
    for i in range(0, w, 8):
        rect(img, x + i, y + top_h, 1, FACE, P["wall_face_dk"])
    rect(img, x, y + h - 1, w, 1, P["wall_dark"])
    # lamps
    for i in range(12, w - 8, 32):
        px(img, x + i, y + top_h + 3, P["accent_lt"])
        px(img, x + i + 1, y + top_h + 3, P["accent"])
        px(img, x + i, y + top_h + 4, with_alpha(P["accent"], 140))


def drop_shadow(img, x, y, w, h):
    for i, a in enumerate((90, 60, 35, 15)):
        rect(img, x + 2, y + h + i, w, 1, (0, 0, 0, a))
    for i, a in enumerate((60, 30)):
        rect(img, x + w + i, y + 4, 1, h - 4 + 2, (0, 0, 0, a))


def vignette(img):
    for y in range(H):
        for x in range(W):
            nx = (x - W / 2) / (W / 2)
            ny = (y - H / 2) / (H / 2)
            d = math.hypot(nx * 0.9, ny)
            if d > 0.75:
                a = int(min(110, (d - 0.75) * 200))
                a = a // 10 * 10
                if a:
                    px(img, x, y, (6, 4, 18, a))


def arena():
    rng = random.Random(7)
    img = canvas(W, H, P["floor"])
    for ty in range(math.ceil(H / T)):
        for tx in range(W // T):
            floor_tile(img, tx, ty, rng)
    seal(img, 320, 180)
    for cx, cy in PADS:
        pad(img, cx, cy)
    for x, y, w, h in sorted(WALLS, key=lambda r: r[1] + r[3]):
        if not (w == 640 or h == 360):
            drop_shadow(img, x, y, w, h)
    # outer walls first (left/right/top), bottom last so it overlaps side faces
    for r in [WALLS[2], WALLS[3], WALLS[0]]:
        wall(img, *r, outer=True)
    for r in WALLS[4:]:
        wall(img, *r)
    wall(img, *WALLS[1], outer=True)
    # inner glow strip on outer walls' inner edges
    for y in range(24, 340):
        px(img, 16, y, with_alpha(P["accent"], 60))
        px(img, 623, y, with_alpha(P["accent"], 60))
    vignette(img)
    return img


def spawn_points():
    pts = []
    for cx, cy in PADS:
        for dx, dy in ((-9, -4), (9, -4), (-9, 5), (9, 5)):
            pts.append({"x": (cx + dx) * SCALE, "y": (cy + dy) * SCALE})
    return pts


def tileset():
    """16px tiles for building custom maps: 8 columns x 2 rows (32px exported)."""
    rng = random.Random(3)
    img = canvas(T * 8, T * 2)
    for i, v in enumerate((0.5, 0.5, 0.03, 0.09, 0.15, 0.2, 0.5, 0.5)):
        tile = canvas(T * 2, T * 2)
        floor_tile(tile, i % 2, 0, rng, v)
        img.alpha_composite(tile.crop(((i % 2) * T, 0, (i % 2) * T + T, T)), (i * T, 0))
    # row 2: wall top, wall top with trim, wall face, wall face lamp, pad quarter, seal fragment, blank dark, outline
    t = canvas(T, T)
    rect(t, 0, 0, T, T, P["wall_top"])
    rect(t, 0, 0, T, 1, P["wall_top_hi"])
    img.alpha_composite(t, (0, T))
    t = canvas(T, T)
    rect(t, 0, 0, T, T, P["wall_top"])
    rect(t, 0, T - 1, T, 1, P["accent_lt"])
    img.alpha_composite(t, (T, T))
    for k, lamp in enumerate((False, True)):
        t = canvas(T, T)
        rect(t, 0, 0, T, T, P["wall_face"])
        rect(t, 0, 0, 1, T, P["wall_face_dk"])
        rect(t, 8, 0, 1, T, P["wall_face_dk"])
        rect(t, 0, T - 1, T, 1, P["wall_dark"])
        if lamp:
            px(t, 4, 6, P["accent_lt"])
            px(t, 5, 6, P["accent"])
        img.alpha_composite(t, ((2 + k) * T, T))
    t = canvas(T, T)
    rect(t, 0, 0, T, T, P["wall_dark"])
    img.alpha_composite(t, (4 * T, T))
    return img


def build():
    save(arena(), "maps/arena-bg.png")
    save(tileset(), "maps/tileset.png")
    data = {
        "width": W * SCALE,
        "height": H * SCALE,
        "walls": [{"x": x * SCALE, "y": y * SCALE, "w": w * SCALE, "h": h * SCALE} for x, y, w, h in WALLS],
        "spawns": spawn_points(),
        "center": {"x": 320 * SCALE, "y": 180 * SCALE},
        "crystalMargin": 48,
        "notes": "Walls are axis-aligned rectangles in world pixels. Crystals must spawn at least crystalMargin px from any wall.",
    }
    (OUT / "maps" / "arena.json").write_text(json.dumps(data, indent=2))


if __name__ == "__main__":
    build()
