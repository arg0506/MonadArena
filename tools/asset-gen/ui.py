"""UI kit: icons, 9-slice panels and buttons, logo, favicons and social image."""
import json

from PIL import Image

from common import (OUT, P, SCALE, canvas, glow, hexc, outline, px, rect, save, shade,
                    upscale, with_alpha)
from font import text_image

PAL = {
    "o": P["outline"], "w": P["white"], "l": P["suit_sh"], "L": P["suit_dk"],
    "a": P["accent"], "A": P["accent_lt"], "q": P["accent_dk"],
    "c": P["c_mid"], "C": P["c_lt"], "d": P["c_dk"], "e": P["c_core"],
    "p": P["r_mid"], "P": P["r_lt"], "D": P["r_dk"],
    "g": P["gold"], "G": P["gold_dk"], "r": P["danger"], "R": shade(P["danger"], 0.7),
    "k": P["ok"], "K": shade(P["ok"], 0.7), "y": P["warn"],
}

ICONS = {
    "timer": [
        "....oooo....",
        "....owwo....",
        "..oooooooo..",
        ".owwwwwwlLo.",
        "owwwwowwwlLo",
        "owwwwowwwwlo",
        "owwwwooowwlo",
        "owwwwwwwwwlo",
        "owwwwwwwwwlo",
        ".owwwwwwwlo.",
        "..oollllLo..",
        "...oooooo...",
    ],
    "trophy": [
        "oooooooooooo",
        "oGogggggggoG",
        "oGogwgggGgoG",
        "oGogwggggGoG",
        ".oGoggggGoG.",
        "..ooggggGoo.",
        "....ogGGo...",
        ".....oGo....",
        ".....oGo....",
        "...ogggGGo..",
        "..oGGGGGGGo.",
        "..ooooooooo.",
    ],
    "crystal": [
        ".....oo.....",
        "....oeCo....",
        "...oeCCco...",
        "..oCCCccdo..",
        ".oCCCcccddo.",
        ".oCCCcccddo.",
        ".oCCCcccddo.",
        ".occcccdddo.",
        "..occccddo..",
        "...occddo...",
        "....oddo....",
        ".....oo.....",
    ],
    "crystal-rare": [
        ".....oo.....",
        "....owPo....",
        "...owPPpo...",
        "..oPPPppDo..",
        ".ogggggggGo.",
        ".oPPPpppDDo.",
        ".oPPPpppDDo.",
        ".opppppDDDo.",
        "..oppppDDo..",
        "...oppDDo...",
        "....oDDo....",
        ".....oo.....",
    ],
    "bolt": [
        "......oooo..",
        ".....oggGo..",
        "....oggGo...",
        "...oggGo....",
        "..oggggooo..",
        "..ogggggGo..",
        "..oooggGo...",
        "....oggo....",
        "...oggo.....",
        "...ogo......",
        "..ogo.......",
        "..oo........",
    ],
    "player": [
        "...oooooo...",
        "..oAAAAAaa..",
        ".oAwAAAAaaq.",
        ".ooooooooooq",
        ".ooCCooCCoo.",
        ".oooooooooo.",
        ".oaAaaaaaqo.",
        "..oooooooo..",
        "...owwwlo...",
        "..oawwwlao..",
        "..owwwwwlo..",
        "...oo..oo...",
    ],
    "crown": [
        "............",
        "o....oo....o",
        "og..ogGo..Go",
        "ogo.ogGo.oGo",
        "oggoggGGoGGo",
        "oggggggggGGo",
        "ogwggggggGGo",
        "oggggpgggGGo",
        "oGGGGGGGGGGo",
        "oooooooooooo",
        "............",
        "............",
    ],
    "check": [
        "............",
        ".........oo.",
        "........okko",
        ".......okkKo",
        "..oo..okkKo.",
        ".okkoookkKo.",
        ".oKkkokkKo..",
        "..oKkkkKo...",
        "...oKkKo....",
        "....oKo.....",
        ".....o......",
        "............",
    ],
    "cross": [
        "............",
        ".oo......oo.",
        "orroo..oorRo",
        "oRrrroorrRRo",
        ".oRrrrrrRRo.",
        "..oRrrrRRo..",
        "..orrrrRRo..",
        ".orrrRRrRRo.",
        "orrrRooRrRRo",
        "oRRoo..ooRRo",
        ".oo......oo.",
        "............",
    ],
    "sound-on": [
        ".....oo.....",
        "....owo..o..",
        "...owwo...o.",
        "ooowwwo.o..o",
        "owwwwwo..o.o",
        "owwwwwo..o.o",
        "owwwwwo..o.o",
        "ollwwwo.o..o",
        "ooolwwo...o.",
        "...ollo..o..",
        "....olo.....",
        ".....oo.....",
    ],
    "sound-off": [
        ".....oo.....",
        "....owo.....",
        "...owwo.....",
        "ooowwwo.....",
        "owwwwwor..r.",
        "owwwwwo.rr..",
        "owwwwwo.rr..",
        "ollwwwor..r.",
        "ooolwwo.....",
        "...ollo.....",
        "....olo.....",
        ".....oo.....",
    ],
    "signal": [
        "............",
        "........ooo.",
        "........okKo",
        "........okKo",
        ".....ooookKo",
        ".....okKokKo",
        ".....okKokKo",
        "..ooookKokKo",
        "..okKokKokKo",
        "..okKokKokKo",
        "..oooooooooo",
        "............",
    ],
    "link": [
        "............",
        "....oooo....",
        "...oAAAAo...",
        "..oAo..oAo..",
        "..oAo..oAo..",
        "...oAooAo...",
        "...oAooAo...",
        "..oAo..oAo..",
        "..oAo..oAo..",
        "...oAAAAo...",
        "....oooo....",
        "............",
    ],
}


def icon(rows):
    img = canvas(12, 12)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in PAL:
                px(img, x, y, PAL[ch])
    return img


def icons():
    names = list(ICONS)
    sheet = canvas(12 * len(names), 12)
    frames = {}
    for i, n in enumerate(names):
        sheet.alpha_composite(icon(ICONS[n]), (i * 12, 0))
        frames[n] = {"frame": {"x": i * 12 * SCALE, "y": 0, "w": 12 * SCALE, "h": 12 * SCALE},
                     "rotated": False, "trimmed": False,
                     "spriteSourceSize": {"x": 0, "y": 0, "w": 12 * SCALE, "h": 12 * SCALE},
                     "sourceSize": {"w": 12 * SCALE, "h": 12 * SCALE}}
    save(sheet, "ui/icons.png")
    atlas = {"frames": frames, "meta": {"image": "icons.png", "format": "RGBA8888",
                                        "size": {"w": sheet.width * SCALE, "h": 12 * SCALE}, "scale": "1"}}
    (OUT / "ui" / "icons.json").write_text(json.dumps(atlas, indent=2))
    return names


def panel(border, fill, top_hi):
    """16x16 native 9-slice panel with 1px clipped corners."""
    img = canvas(16, 16)
    rect(img, 1, 1, 14, 14, fill)
    for i in range(1, 15):
        for (x, y) in ((i, 0), (i, 15), (0, i), (15, i)):
            px(img, x, y, P["outline"])
    for i in range(2, 14):
        for (x, y) in ((i, 1), (i, 14), (1, i), (14, i)):
            px(img, x, y, border)
    px(img, 1, 1, P["outline"]); px(img, 14, 1, P["outline"])
    px(img, 1, 14, P["outline"]); px(img, 14, 14, P["outline"])
    rect(img, 2, 2, 12, 1, top_hi)
    return img


def button(fill, state):
    """24x14 native 9-slice button: normal / hover / pressed."""
    img = canvas(24, 14)
    f = shade(fill, 1.15) if state == "hover" else fill
    depth = 0 if state == "pressed" else 2
    body_top = 0 if state != "pressed" else 2
    body_h = 12
    # depth
    if depth:
        rect(img, 1, body_top + 2, 22, body_h, shade(fill, 0.55))
    rect(img, 1, body_top, 22, body_h, f)
    rect(img, 2, body_top + 1, 20, 1, shade(f, 1.35))
    rect(img, 1, body_top + body_h - 1, 22, 1, shade(f, 0.82))
    outline(img)
    return img


def logo():
    title = text_image("MONAD", with_outline=False, spacing=1)
    sub = text_image("ARENA", with_outline=False, spacing=1)
    k = 3
    w = max(title.width, sub.width) * k
    h = (title.height + sub.height) * k + k * 2
    img = canvas(w + 40, h + 16)
    grad = [P["white"], P["accent_lt"], P["accent_lt"], hexc("#a08cff"), P["accent"], P["accent"], P["accent_dk"]]
    grad2 = [P["c_core"], P["c_lt"], P["c_lt"], P["c_mid"], P["c_mid"], P["c_dk"], P["c_dk"]]
    for line, (txt, g) in enumerate(((title, grad), (sub, grad2))):
        ox = (w - txt.width * k) // 2 + 8
        oy = 6 + line * (title.height * k + k * 2)
        for y in range(txt.height):
            for x in range(txt.width):
                if txt.getpixel((x, y))[3]:
                    for yy in range(k):
                        c = g[min(6, y)]
                        for xx in range(k):
                            px(img, ox + x * k + xx, oy + y * k + yy, c)
    # drop shadow + outline
    sh = canvas(img.width, img.height)
    for y in range(img.height):
        for x in range(img.width):
            if img.getpixel((x, y))[3] > 200:
                px(sh, x + 2, y + 2, P["accent_dk"])
                px(sh, x + 3, y + 3, P["outline"])
    sh.alpha_composite(img)
    outline(sh, P["outline"], diagonal=True)
    out = glow(sh, P["accent"], 4, 70)
    return out


def favicons():
    from crystals_fx import crystal_standard
    frame = crystal_standard().crop((0, 0, 24, 24))
    crop = frame.crop((4, 1, 20, 17))
    (OUT / "ui").mkdir(parents=True, exist_ok=True)
    upscale(crop, 2).save(OUT / "ui" / "favicon-32.png")
    upscale(crop, 4).save(OUT / "ui" / "favicon-64.png")
    big = canvas(24, 24, P["bg1"])
    big.alpha_composite(frame)
    upscale(big, 8).save(OUT / "ui" / "apple-touch-icon.png")


def og_image(logo_img):
    bg = Image.open(OUT / "maps" / "arena-bg.png").convert("RGBA").crop((40, 45, 1240, 675))
    shade_layer = Image.new("RGBA", bg.size, (8, 6, 20, 150))
    bg.alpha_composite(shade_layer)
    lg = upscale(logo_img, 3)
    bg.alpha_composite(lg, ((bg.width - lg.width) // 2, 70))
    tag = upscale(text_image("EVERY CRYSTAL IS A TRANSACTION", True), 4)
    bg.alpha_composite(tag, ((bg.width - tag.width) // 2, 70 + lg.height + 20))
    players = ["red", "cyan", "yellow", "purple"]
    x = 330
    for i, n in enumerate(players):
        sp = Image.open(OUT / "sprites" / "players" / f"player-{n}.png").crop((0, 0, 48, 48))
        sp = sp.resize((96, 96), Image.NEAREST)
        bg.alpha_composite(sp, (x + i * 150, 470))
    cr = Image.open(OUT / "sprites" / "crystals" / "crystal-standard.png").crop((48 * 3, 0, 48 * 4, 48)).resize((96, 96), Image.NEAREST)
    rr = Image.open(OUT / "sprites" / "crystals" / "crystal-rare.png").crop((64 * 3, 0, 64 * 4, 64)).resize((112, 112), Image.NEAREST)
    bg.alpha_composite(cr, (190, 470))
    bg.alpha_composite(rr, (930, 455))
    bg.convert("RGB").save(OUT / "ui" / "og-image.png", optimize=True)


def build():
    names = icons()
    save(panel(P["bg3"], with_alpha(P["bg1"], 236), P["bg2"]), "ui/panel.png")
    save(panel(P["accent"], with_alpha(P["bg1"], 236), P["accent_dk"]), "ui/panel-accent.png")
    save(panel(P["c_dk"], with_alpha(P["void"], 245), P["bg1"]), "ui/input.png")
    for name, fill in (("primary", P["accent"]), ("secondary", P["bg3"]), ("danger", shade(P["danger"], 0.85))):
        for state in ("normal", "hover", "pressed"):
            suffix = "" if state == "normal" else f"-{state}"
            save(button(fill, state), f"ui/button-{name}{suffix}.png")
    # timer / progress bar pieces (9-slice, 8x6 native)
    bar = canvas(8, 6)
    rect(bar, 0, 0, 8, 6, P["outline"])
    rect(bar, 1, 1, 6, 4, P["void"])
    save(bar, "ui/bar-bg.png")
    fill = canvas(8, 6)
    rect(fill, 0, 0, 8, 6, P["c_mid"])
    rect(fill, 0, 0, 8, 1, P["c_lt"])
    rect(fill, 0, 5, 8, 1, P["c_dk"])
    save(fill, "ui/bar-fill.png")
    lg = logo()
    save(lg, "ui/logo.png")
    favicons()
    og_image(lg)
    return names


if __name__ == "__main__":
    build()
