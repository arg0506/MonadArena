"""Crystals and effects.

crystal-standard.png : 8 frames, 24x24 native (48x48 exported)  - idle shimmer + bob
crystal-rare.png     : 8 frames, 32x32 native (64x64 exported)  - glow pulse + orbiting sparks
fx-spawn*.png        : 7 frames, 32x32 native                   - crystal appearing
fx-pop*.png          : 7 frames, 32x32 native                   - crystal claimed (shatter)
fx-contested.png     : 4 frames, 32x32 native                   - dashed ring while tickets are out
fx-sparkle.png       : 4 frames, 8x8 native                     - white twinkle (tint in code)
fx-dust.png          : 4 frames, 10x8 native                    - footstep puff
fx-beaten.png        : 5 frames, 16x16 native                   - red cross burst for a lost race
"""
import math

from common import (P, canvas, ellipse, glow, outline, polygon_fill, px, save, sheet,
                    with_alpha)


def gem(img, cx, cy, hw, top, mid_top, mid_bot, bottom, pal, shimmer=None, rim=None):
    """Draw a faceted hexagonal gem.

    hw: half width; top/bottom: y of the points; mid_top/mid_bot: y of the girdle corners.
    pal: dict with core, lt, mid, dk, deep. shimmer: x+y diagonal position of a light band.
    """
    pts = [(cx, top), (cx - hw, mid_top), (cx - hw, mid_bot), (cx, bottom), (cx + hw, mid_bot), (cx + hw, mid_top)]

    def colour(x, y):
        xc = x + 0.5
        yc = y + 0.5
        left = xc < cx
        # facet regions: crown (above girdle line from top), pavilion (below)
        crown_line = top + (mid_top - top) * (abs(xc - cx) / hw) + 2.5
        pav_line = mid_bot - 0.5
        if yc < crown_line:
            c = pal["lt"] if left else pal["mid"]
            if left and abs(xc - cx) < hw * 0.45 and yc < crown_line - 1:
                c = pal["core"]
        elif yc > pav_line:
            c = pal["mid"] if left else pal["deep"]
        else:
            c = pal["mid"] if left else pal["dk"]
            if left and abs(xc - (cx - hw * 0.45)) < 0.6:
                c = pal["lt"]
        if shimmer is not None:
            d = (xc - cx) + (yc - cy) - shimmer
            if -1.0 <= d <= 0.6:
                c = pal["core"]
            elif 0.6 < d <= 1.6:
                c = pal["lt"] if c not in (pal["core"],) else c
        return c

    polygon_fill(img, pts, colour)
    if rim:
        # metal girdle band
        for x in range(int(cx - hw), int(cx + hw)):
            px(img, x, int(mid_top) + 1, rim[0] if x < cx else rim[1])


CRYSTAL = {"core": P["c_core"], "lt": P["c_lt"], "mid": P["c_mid"], "dk": P["c_dk"], "deep": P["c_deep"]}
RARE = {"core": P["r_core"], "lt": P["r_lt"], "mid": P["r_mid"], "dk": P["r_dk"], "deep": P["r_deep"]}


def star(img, x, y, size, c, core=None):
    """Pixel sparkle: size 0 dot, 1 plus, 2 long plus with diagonals."""
    px(img, x, y, core or c)
    if size >= 1:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            px(img, x + dx, y + dy, c)
    if size >= 2:
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            px(img, x + dx, y + dy, with_alpha(c, 170))


def crystal_standard():
    frames = []
    for f in range(8):
        img = canvas(24, 24)
        bob = round(math.sin(f / 8 * math.tau) * -1.2)
        sw = 5.5 - bob * 0.5
        ellipse(img, 12, 21.5, sw, 1.5, P["shadow"])
        g = canvas(24, 24)
        shimmer = [-14, -8, -3, 2, 7, None, None, None][f]
        gem(g, 12, 11 + bob, 5, 3 + bob, 8 + bob, 13 + bob, 19 + bob, CRYSTAL, shimmer)
        outline(g, P["c_deep"])
        strength = [70, 85, 100, 110, 100, 85, 70, 60][f]
        g = glow(g, P["c_mid"], 3, strength)
        img.alpha_composite(g)
        if f in (3, 4):
            star(img, 16, 5 + bob, 1 if f == 3 else 0, P["white"])
        frames.append(img)
    return sheet([frames])


def crystal_rare():
    frames = []
    for f in range(8):
        img = canvas(32, 32)
        bob = round(math.sin(f / 8 * math.tau) * -1.4)
        ellipse(img, 16, 29, 7 - bob * 0.5, 1.8, P["shadow"])
        g = canvas(32, 32)
        shimmer = [None, -16, -10, -4, 2, 8, None, None][f]
        gem(g, 16, 15 + bob, 7, 4 + bob, 10 + bob, 18 + bob, 26 + bob, RARE, shimmer,
            rim=(P["gold"], P["gold_dk"]))
        # gold crown point
        px(g, 16, 3 + bob, P["gold"])
        outline(g, P["r_deep"])
        strength = [90, 110, 130, 150, 130, 110, 90, 80][f]
        g = glow(g, P["r_mid"], 4, strength)
        # orbiting sparks (behind first, then gem, then front sparks)
        back, front = canvas(32, 32), canvas(32, 32)
        for k in range(3):
            a = math.tau * (f / 8 + k / 3)
            sx = round(16 + math.cos(a) * 11)
            sy = round(15 + bob + math.sin(a) * 5)
            target = front if math.sin(a) > 0 else back
            star(target, sx, sy, 1 if math.sin(a) > 0 else 0, P["gold"], P["white"])
        img.alpha_composite(back)
        img.alpha_composite(g)
        img.alpha_composite(front)
        frames.append(img)
    return sheet([frames])


def fx_spawn(pal, accent):
    frames = []
    for f in range(7):
        img = canvas(32, 32)
        if f <= 2:  # beam
            w = [1, 3, 2][f]
            for y in range(0, 26):
                a = int(255 * (y / 26) ** 0.5)
                for x in range(16 - w, 16 + w):
                    px(img, x, y, with_alpha(P["white"] if abs(x - 15.5) < 1 else pal["lt"], a))
        if 1 <= f <= 5:  # ground ring
            r = [0, 3, 6, 9, 11, 13][f]
            a = [0, 255, 230, 180, 120, 60][f]
            for y in range(32):
                for x in range(32):
                    nx = (x + 0.5 - 16) / r
                    ny = (y + 0.5 - 24) / (r * 0.4)
                    d = nx * nx + ny * ny
                    if 0.7 <= d <= 1.0:
                        px(img, x, y, with_alpha(pal["lt"], a))
        if 2 <= f <= 4:
            rx, ry = [0, 0, 4, 3, 2][f], [0, 0, 6, 5, 3][f]
            ellipse(img, 16, 18, rx, ry, with_alpha(pal["lt"], 230))
            ellipse(img, 16, 18, max(1, rx - 2), max(1, ry - 2), P["white"])
        if f >= 3:  # sparks rising
            for k, (sx, base) in enumerate(((9, 22), (23, 20), (13, 16), (20, 12))):
                y = base - (f - 3) * 3 - k
                star(img, sx, y, 1 if f < 5 else 0, with_alpha(accent, 255 - (f - 3) * 60), P["white"])
        frames.append(img)
    return sheet([frames])


def fx_pop(pal, accent, shards=6):
    frames = []
    for f in range(7):
        img = canvas(32, 32)
        if f == 0:
            ellipse(img, 16, 16, 6, 6, P["white"])
            ellipse(img, 16, 16, 4, 4, pal["core"])
        if 1 <= f <= 4:
            r = 5 + f * 3
            a = 255 - f * 55
            for y in range(32):
                for x in range(32):
                    d = math.hypot(x + 0.5 - 16, y + 0.5 - 16)
                    if r - 1 <= d <= r:
                        px(img, x, y, with_alpha(pal["lt"], a))
        if f >= 1:
            dist = 3 + f * 2.6
            for k in range(shards):
                ang = math.tau * k / shards + 0.4
                sx = round(16 + math.cos(ang) * dist)
                sy = round(16 + math.sin(ang) * dist + (f * f) * 0.12)
                a = max(0, 255 - (f - 1) * 45)
                c = [pal["lt"], pal["mid"], accent][k % 3]
                px(img, sx, sy, with_alpha(c, a))
                if f < 5:
                    px(img, sx + 1, sy, with_alpha(pal["dk"], a))
                    px(img, sx, sy - 1, with_alpha(P["white"], a))
        if 2 <= f <= 5:
            for k, (sx, sy) in enumerate(((8, 9), (24, 11), (10, 24), (23, 23))):
                if (k + f) % 2 == 0:
                    star(img, sx, sy, 1, with_alpha(accent, 255 - (f - 2) * 50), P["white"])
        frames.append(img)
    return sheet([frames])


def fx_contested():
    frames = []
    for f in range(4):
        img = canvas(32, 32)
        for y in range(32):
            for x in range(32):
                nx = (x + 0.5 - 16) / 13
                ny = (y + 0.5 - 22) / 6
                d = nx * nx + ny * ny
                if 0.72 <= d <= 1.0:
                    ang = math.atan2(ny, nx)
                    seg = int(((ang + math.pi) / math.tau * 12 + f * 0.75)) % 2
                    if seg == 0:
                        px(img, x, y, P["warn"] if ny > -0.2 else with_alpha(P["warn"], 150))
        frames.append(img)
    return sheet([frames])


def fx_sparkle():
    frames = []
    for size, a in ((0, 200), (1, 255), (2, 255), (1, 160)):
        img = canvas(8, 8)
        star(img, 4, 4, size, with_alpha(P["white"], a))
        frames.append(img)
    return sheet([frames])


def fx_dust():
    frames = []
    for f in range(4):
        img = canvas(10, 8)
        a = [200, 170, 120, 60][f]
        c = with_alpha(P["suit_sh"], a)
        ellipse(img, 3.5 - f * 0.4, 5 - f * 0.5, 1.2 + f * 0.5, 1.0 + f * 0.4, c)
        ellipse(img, 6.5 + f * 0.4, 5.2 - f * 0.4, 1.0 + f * 0.5, 0.9 + f * 0.4, c)
        frames.append(img)
    return sheet([frames])


def fx_beaten():
    frames = []
    for f in range(5):
        img = canvas(16, 16)
        r = [2, 4, 5, 5, 5][f]
        a = [255, 255, 255, 180, 90][f]
        c = with_alpha(P["danger"], a)
        for i in range(-r, r + 1):
            for w in (0, 1):
                px(img, 8 + i, 8 + i + w, c)
                px(img, 8 + i, 8 - i + w, c)
        if f < 3:
            outline(img, with_alpha(P["outline"], a))
        frames.append(img)
    return sheet([frames])


def build():
    save(crystal_standard(), "sprites/crystals/crystal-standard.png")
    save(crystal_rare(), "sprites/crystals/crystal-rare.png")
    save(fx_spawn(CRYSTAL, P["c_lt"]), "sprites/fx/fx-spawn.png")
    save(fx_spawn(RARE, P["gold"]), "sprites/fx/fx-spawn-rare.png")
    save(fx_pop(CRYSTAL, P["white"], 6), "sprites/fx/fx-pop.png")
    save(fx_pop(RARE, P["gold"], 10), "sprites/fx/fx-pop-rare.png")
    save(fx_contested(), "sprites/fx/fx-contested.png")
    save(fx_sparkle(), "sprites/fx/fx-sparkle.png")
    save(fx_dust(), "sprites/fx/fx-dust.png")
    save(fx_beaten(), "sprites/fx/fx-beaten.png")


if __name__ == "__main__":
    build()
