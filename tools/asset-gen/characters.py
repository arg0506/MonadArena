"""Player characters: a small helmeted crystal-runner robot, 24x24 native frames.

Sheet layout (4 columns x 5 rows, frame = 24x24 native, 48x48 exported):
  row 0: walk down  (frames 0-3)
  row 1: walk left  (frames 4-7)
  row 2: walk right (frames 8-11)
  row 3: walk up    (frames 12-15)
  row 4: idle down 0-1 (16-17), idle up 0-1 (18-19)
"""
from common import (P, PLAYER_COLORS, canvas, ellipse, hexc, mirror, outline, px,
                    rect, save, shade, sheet, with_alpha)

F = 24
BOB = [0, -1, 0, -1]
FOOT_L = [0, 0, -1, 0]   # vertical lift of left foot (down/up views)
FOOT_R = [-1, 0, 0, 0]
ARM_L = [1, 0, -1, 0]    # arm swing (down/up views: y; side view: x)
ARM_R = [-1, 0, 1, 0]
SIDE_FRONT = [1, 0, -1, 0]  # side view: x offset of front foot


def tones(base_hex):
    base = hexc(base_hex)
    return {
        "hi": shade(base, 1.6),
        "lt": shade(base, 1.25),
        "mid": base,
        "dk": shade(base, 0.72),
        "deep": shade(base, 0.5),
    }


def shadow_layer():
    img = canvas(F, F)
    ellipse(img, 12, 21.6, 6.2, 1.9, P["shadow"])
    return img


def helmet(img, t, cy, facing):
    cx, rx, ry = 12, 6.6, 5.6

    def sh(nx, ny):
        d = nx * -0.6 + ny * -0.8  # light from upper-left
        if d > 0.55:
            return t["hi"]
        if d > 0.1:
            return t["lt"]
        if d < -0.6:
            return t["dk"]
        return t["mid"]

    ellipse(img, cx, cy, rx, ry, None, sh)
    top = round(cy - 5)
    # specular highlight
    if facing != "up":
        px(img, 8, top + 1, P["white"])
        px(img, 9, top + 1, t["hi"])
        px(img, 8, top + 2, t["hi"])
    if facing == "down":
        # visor: rounded dark screen with a rim and two eye lights
        for x in range(7, 17):
            for y in range(top + 3, top + 8):
                if x in (7, 16) and y in (top + 3, top + 7):
                    continue
                px(img, x, y, P["visor"])
        for x in range(8, 16):
            px(img, x, top + 7, t["deep"])
        px(img, 7, top + 7, None)
        eye = P["visor_glint"]
        for ex in (9, 13):
            px(img, ex, top + 5, eye)
            px(img, ex + 1, top + 5, eye)
            px(img, ex, top + 4, with_alpha(eye, 120))
        px(img, 15, top + 3, with_alpha(P["white"], 140))
        # cheek vents
        px(img, 7, top + 9, t["dk"])
        px(img, 16, top + 9, t["deep"])
    elif facing == "up":
        for y in range(top + 1, top + 9):
            px(img, 12, y, t["lt"] if y < top + 5 else t["mid"])
        px(img, 11, top + 2, t["hi"])
        rect(img, 9, top + 7, 6, 1, t["dk"])
    elif facing == "left":
        for x in range(5, 11):
            for y in range(top + 3, top + 8):
                if x == 5 and y in (top + 3, top + 7):
                    continue
                px(img, x, y, P["visor"])
        for x in range(6, 11):
            px(img, x, top + 7, t["deep"])
        px(img, 6, top + 5, P["visor_glint"])
        px(img, 7, top + 5, P["visor_glint"])
        px(img, 6, top + 4, with_alpha(P["visor_glint"], 120))
        px(img, 15, top + 6, t["deep"])
        px(img, 15, top + 5, t["dk"])


def antenna(img, t, cy, x, blink=False):
    top = round(cy - 5)
    px(img, x, top - 1, P["suit_dk"])
    px(img, x, top - 2, P["suit_dk"])
    tip = P["white"] if blink else t["hi"]
    px(img, x, top - 4, tip)
    px(img, x - 1, top - 3, t["mid"])
    px(img, x, top - 3, tip)
    px(img, x + 1, top - 3, t["dk"])


def body_front(img, t, y0, back=False):
    # torso 8x6 with rounded bottom corners
    for y in range(y0, y0 + 6):
        for x in range(8, 16):
            if y == y0 + 5 and x in (8, 15):
                continue
            c = P["suit"]
            if x >= 14:
                c = P["suit_sh"]
            if y == y0 + 5:
                c = P["suit_dk"] if x > 9 else P["suit_sh"]
            px(img, x, y, c)
    # belt
    for x in range(8, 16):
        px(img, x, y0 + 3, t["dk"] if x >= 14 else t["mid"])
    if back:
        # power pack
        rect(img, 9, y0, 6, 4, P["boot"])
        rect(img, 9, y0 + 3, 6, 1, P["boot_dk"])
        px(img, 10, y0 + 1, t["hi"])
        px(img, 11, y0 + 1, t["lt"])
        px(img, 13, y0 + 1, t["lt"])
        px(img, 10, y0 + 2, t["mid"])
    else:
        px(img, 11, y0 + 3, t["hi"])
        px(img, 12, y0 + 3, t["lt"])
        px(img, 10, y0 + 1, P["white"])


def arm(img, t, x, y, side_shade=False):
    for yy in range(y, y + 3):
        px(img, x, yy, P["suit_sh"] if side_shade else P["suit"])
        px(img, x + 1, yy, P["suit_dk"] if side_shade else P["suit_sh"])
    px(img, x, y + 3, t["mid"])
    px(img, x + 1, y + 3, t["dk"])


def foot(img, x, y, w=3):
    for xx in range(x, x + w):
        px(img, xx, y, P["boot"])
        px(img, xx, y + 1, P["boot_dk"])


def frame_down(t, f, idle=False):
    img = canvas(F, F)
    bob = 0 if idle else BOB[f]
    head_y = 9 + bob + (1 if idle and f == 1 else 0)
    foot(img, 8, 19 + (0 if idle else FOOT_L[f]))
    foot(img, 13, 19 + (0 if idle else FOOT_R[f]))
    arm(img, t, 6, 14 + bob + (0 if idle else ARM_L[f]))
    arm(img, t, 16, 14 + bob + (0 if idle else ARM_R[f]), side_shade=True)
    body_front(img, t, 13 + bob)
    helmet(img, t, head_y, "down")
    antenna(img, t, head_y, 14, blink=idle and f == 1)
    return finish(img)


def frame_up(t, f, idle=False):
    img = canvas(F, F)
    bob = 0 if idle else BOB[f]
    head_y = 9 + bob + (1 if idle and f == 1 else 0)
    foot(img, 8, 19 + (0 if idle else FOOT_R[f]))
    foot(img, 13, 19 + (0 if idle else FOOT_L[f]))
    arm(img, t, 6, 14 + bob + (0 if idle else ARM_R[f]))
    arm(img, t, 16, 14 + bob + (0 if idle else ARM_L[f]), side_shade=True)
    body_front(img, t, 13 + bob, back=True)
    helmet(img, t, head_y, "up")
    antenna(img, t, head_y, 9, blink=idle and f == 1)
    return finish(img)


def frame_left(t, f):
    img = canvas(F, F)
    bob = BOB[f]
    head_y = 9 + bob
    # back foot then front foot
    foot(img, 12 - SIDE_FRONT[f], 19, 3)
    foot(img, 9 + SIDE_FRONT[f], 19, 3)
    # back arm (darker, behind torso)
    for yy in range(14 + bob, 17 + bob):
        px(img, 13 - ARM_L[f], yy, P["suit_dk"])
    # torso 6 wide
    for y in range(13 + bob, 19 + bob):
        for x in range(9, 15):
            if y == 18 + bob and x in (9, 14):
                continue
            c = P["suit"] if x < 13 else P["suit_sh"]
            if y == 18 + bob:
                c = P["suit_dk"]
            px(img, x, y, c)
    for x in range(9, 15):
        px(img, x, 16 + bob, t["mid"] if x < 13 else t["dk"])
    # pack on back (right side when facing left)
    rect(img, 14, 13 + bob, 2, 4, P["boot"])
    px(img, 15, 14 + bob, t["lt"])
    # front arm
    ax = 10 + ARM_R[f]
    for yy in range(14 + bob, 17 + bob):
        px(img, ax, yy, P["suit"])
        px(img, ax + 1, yy, P["suit_sh"])
    px(img, ax, 17 + bob, t["mid"])
    px(img, ax + 1, 17 + bob, t["dk"])
    helmet(img, t, head_y, "left")
    antenna(img, t, head_y, 15)
    return finish(img)


def finish(img):
    outline(img)
    out = shadow_layer()
    out.alpha_composite(img)
    return out


def character_sheet(colour_hex):
    t = tones(colour_hex)
    down = [frame_down(t, f) for f in range(4)]
    left = [frame_left(t, f) for f in range(4)]
    right = [mirror(fr) for fr in left]
    up = [frame_up(t, f) for f in range(4)]
    idle = [frame_down(t, 0, True), frame_down(t, 1, True), frame_up(t, 0, True), frame_up(t, 1, True)]
    return sheet([down, left, right, up, idle])


def marker_sheet():
    """Pulsing ground ring for the local player (white, tint in code). 24x10 frames."""
    frames = []
    for f in range(4):
        img = canvas(24, 10)
        rx, ry = 10.5 + (f % 2) * 0.6, 3.6 + (f % 2) * 0.3
        a = [255, 200, 150, 200][f]
        for y in range(10):
            for x in range(24):
                nx = (x + 0.5 - 12) / rx
                ny = (y + 0.5 - 5) / ry
                d = nx * nx + ny * ny
                if 0.62 <= d <= 1.0:
                    px(img, x, y, (255, 255, 255, a if ny > -0.2 else int(a * 0.55)))
        frames.append(img)
    return sheet([frames])


def arrow_sheet():
    """Bouncing arrow shown above the local player (white, tint in code). 8x10 frames."""
    shape = ["#######", ".#####.", "..###..", "...#..."]
    frames = []
    for f, dy in enumerate([0, 1, 2, 1]):
        img = canvas(9, 10)
        for y, row in enumerate(shape):
            for x, ch in enumerate(row):
                if ch == "#":
                    px(img, x + 1, y + 2 + dy, P["white"] if y < 2 else hexc("#d6d2ff"))
        outline(img)
        frames.append(img)
    return sheet([frames])


def build():
    out = {}
    for name, hx in PLAYER_COLORS.items():
        save(character_sheet(hx), f"sprites/players/player-{name}.png")
        out[name] = hx
    # neutral variant for Phaser tinting (player 9-16 or custom colours)
    save(character_sheet("#e4e2f0"), "sprites/players/player-neutral.png")
    save(marker_sheet(), "sprites/players/player-marker.png")
    save(arrow_sheet(), "sprites/players/player-arrow.png")
    return out


if __name__ == "__main__":
    build()
