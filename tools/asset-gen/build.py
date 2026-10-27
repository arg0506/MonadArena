"""Build every Monad Arena asset, the manifest, and a preview sheet.

Usage (from the repo root):
    pip install pillow numpy      # ffmpeg must be on PATH for audio
    python3 tools/asset-gen/build.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from PIL import Image  # noqa: E402

import arena  # noqa: E402
import audio  # noqa: E402
import characters  # noqa: E402
import crystals_fx  # noqa: E402
import font  # noqa: E402
import ui  # noqa: E402
from common import OUT, P, PLAYER_COLORS, ROOT, upscale  # noqa: E402

BASE = "assets/"


def anim(key, frames, rate, repeat=-1):
    return {"key": key, "frames": frames, "frameRate": rate, "repeat": repeat}


def manifest(icon_names, sfx_names):
    players = []
    for name in list(PLAYER_COLORS) + ["neutral"]:
        k = f"player-{name}"
        players.append({
            "key": k, "type": "spritesheet", "url": f"{BASE}sprites/players/{k}.png",
            "frameWidth": 48, "frameHeight": 48, "origin": [0.5, 0.86],
            "color": PLAYER_COLORS.get(name, "#e4e2f0"),
            "anims": [
                anim(f"{k}-walk-down", [0, 1, 2, 3], 8),
                anim(f"{k}-walk-left", [4, 5, 6, 7], 8),
                anim(f"{k}-walk-right", [8, 9, 10, 11], 8),
                anim(f"{k}-walk-up", [12, 13, 14, 15], 8),
                anim(f"{k}-idle-down", [16, 17], 2),
                anim(f"{k}-idle-up", [18, 19], 2),
                anim(f"{k}-idle-left", [5], 1),
                anim(f"{k}-idle-right", [9], 1),
            ],
        })

    def sheet(key, url, fw, fh, frames, rate, repeat=-1, origin=(0.5, 0.5)):
        return {"key": key, "type": "spritesheet", "url": BASE + url, "frameWidth": fw, "frameHeight": fh,
                "origin": list(origin), "anims": [anim(key, list(range(frames)), rate, repeat)]}

    sprites = [
        sheet("player-marker", "sprites/players/player-marker.png", 48, 20, 4, 6),
        sheet("player-arrow", "sprites/players/player-arrow.png", 18, 20, 4, 6, origin=(0.5, 1)),
        sheet("crystal-standard", "sprites/crystals/crystal-standard.png", 48, 48, 8, 10, origin=(0.5, 0.78)),
        sheet("crystal-rare", "sprites/crystals/crystal-rare.png", 64, 64, 8, 10, origin=(0.5, 0.8)),
        sheet("fx-spawn", "sprites/fx/fx-spawn.png", 64, 64, 7, 18, 0, origin=(0.5, 0.75)),
        sheet("fx-spawn-rare", "sprites/fx/fx-spawn-rare.png", 64, 64, 7, 18, 0, origin=(0.5, 0.75)),
        sheet("fx-pop", "sprites/fx/fx-pop.png", 64, 64, 7, 20, 0),
        sheet("fx-pop-rare", "sprites/fx/fx-pop-rare.png", 64, 64, 7, 20, 0),
        sheet("fx-contested", "sprites/fx/fx-contested.png", 64, 64, 4, 8, origin=(0.5, 0.69)),
        sheet("fx-sparkle", "sprites/fx/fx-sparkle.png", 16, 16, 4, 12, 0),
        sheet("fx-dust", "sprites/fx/fx-dust.png", 20, 16, 4, 12, 0),
        sheet("fx-beaten", "sprites/fx/fx-beaten.png", 32, 32, 5, 12, 0),
    ]
    images = [
        {"key": "arena-bg", "url": BASE + "maps/arena-bg.png"},
        {"key": "logo", "url": BASE + "ui/logo.png"},
        {"key": "tileset", "url": BASE + "maps/tileset.png", "tileWidth": 32, "tileHeight": 32},
    ]
    nine = {"slice": 8, "items": []}
    for f in sorted((OUT / "ui").glob("*.png")):
        if f.stem.startswith(("panel", "input", "button", "bar")):
            nine["items"].append({"key": f.stem, "url": f"{BASE}ui/{f.name}"})
    data = {
        "pixelArt": True,
        "world": {"width": 1280, "height": 720},
        "players": players,
        "sprites": sprites,
        "images": images,
        "nineSlice": nine,
        "atlases": [{"key": "icons", "textureURL": BASE + "ui/icons.png", "atlasURL": BASE + "ui/icons.json",
                     "frames": icon_names}],
        "bitmapFonts": [
            {"key": "arena-font", "textureURL": BASE + "fonts/arena-font.png", "fontDataURL": BASE + "fonts/arena-font.xml", "size": 14},
            {"key": "arena-font-outline", "textureURL": BASE + "fonts/arena-font-outline.png",
             "fontDataURL": BASE + "fonts/arena-font-outline.xml", "size": 14},
        ],
        "audio": {
            "sfx": [{"key": f"sfx-{n}", "urls": [f"{BASE}audio/sfx/{n}.ogg", f"{BASE}audio/sfx/{n}.mp3"]} for n in sfx_names],
            "music": [{"key": "music-arena-loop", "urls": [f"{BASE}audio/music/arena-loop.ogg", f"{BASE}audio/music/arena-loop.mp3"],
                       "loop": True, "bpm": 128, "seconds": 15}],
        },
        "data": [{"key": "arena-map", "url": BASE + "maps/arena.json"}],
        "web": {"favicon32": BASE + "ui/favicon-32.png", "favicon64": BASE + "ui/favicon-64.png",
                "appleTouchIcon": BASE + "ui/apple-touch-icon.png", "ogImage": BASE + "ui/og-image.png"},
    }
    (OUT / "manifest.json").write_text(json.dumps(data, indent=2))
    return data


def preview():
    """Labelled contact sheet of everything, for the README."""
    W = 1280
    blocks = []

    def label(txt):
        return upscale(font.text_image(txt or " ", True), 2) if txt else Image.new("RGBA", (1, 1))

    def row(title, paths, crop=None, scale=1):
        ims = []
        for p in paths:
            im = Image.open(OUT / p).convert("RGBA")
            if crop:
                im = im.crop(crop)
            if scale != 1:
                im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
            ims.append(im)
        blocks.append((label(title), ims))

    row("PLAYERS - 8 COLOURS + NEUTRAL FOR TINTING",
        [f"sprites/players/player-{n}.png" for n in list(PLAYER_COLORS) + ["neutral"]], crop=(0, 0, 192, 48))
    row("WALK CYCLE + MARKER + ARROW", ["sprites/players/player-purple.png", "sprites/players/player-marker.png",
                                        "sprites/players/player-arrow.png"])
    row("CRYSTALS", ["sprites/crystals/crystal-standard.png", "sprites/crystals/crystal-rare.png"])
    row("EFFECTS: SPAWN, POP, CONTESTED",
        ["sprites/fx/fx-spawn.png", "sprites/fx/fx-pop.png", "sprites/fx/fx-pop-rare.png"])
    row("", ["sprites/fx/fx-spawn-rare.png", "sprites/fx/fx-contested.png", "sprites/fx/fx-beaten.png",
             "sprites/fx/fx-sparkle.png", "sprites/fx/fx-dust.png"])
    row("UI: ICONS, PANELS, BUTTONS, BARS",
        ["ui/icons.png", "ui/panel.png", "ui/panel-accent.png", "ui/input.png", "ui/button-primary.png",
         "ui/button-primary-hover.png", "ui/button-primary-pressed.png", "ui/button-secondary.png",
         "ui/button-danger.png", "ui/bar-bg.png", "ui/bar-fill.png"], scale=2)
    row("FONT: ARENA PIXEL", [], None)
    blocks[-1] = (blocks[-1][0], [upscale(font.text_image("ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789 +25 ?!", True), 3)])
    row("ARENA (1280X720)", ["maps/arena-bg.png"])
    blocks[-1] = (blocks[-1][0], [blocks[-1][1][0].resize((640, 360), Image.NEAREST),
                                  Image.open(OUT / "ui/logo.png").convert("RGBA")])

    pad = 24
    h = pad
    for lab, ims in blocks:
        h += (lab.height + 8 if lab.height > 1 else 0)
        x, rh = pad, 0
        for im in ims:
            if x + im.width > W - pad:
                h += rh + 8
                x, rh = pad, 0
            x += im.width + 16
            rh = max(rh, im.height)
        h += rh + 28
    sheet = Image.new("RGBA", (W, h), P["bg1"])
    y = pad
    for lab, ims in blocks:
        if lab.width > 4:
            sheet.alpha_composite(lab, (pad, y))
            y += lab.height + 8
        x, rh = pad, 0
        for im in ims:
            if x + im.width > W - pad:
                y += rh + 8
                x, rh = pad, 0
            sheet.alpha_composite(im, (x, y))
            x += im.width + 16
            rh = max(rh, im.height)
        y += rh + 28
    dest = ROOT / "docs" / "assets-preview.png"
    sheet.convert("RGB").save(dest, optimize=True)
    return dest


def main():
    characters.build()
    crystals_fx.build()
    arena.build()
    font.build()
    icon_names = ui.build()
    sfx_names = audio.build()
    manifest(icon_names, sfx_names)
    print("preview:", preview())


if __name__ == "__main__":
    main()
