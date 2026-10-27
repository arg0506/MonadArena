"""ArenaPixel: an original 5x7 bitmap font, exported as BMFont XML for Phaser.

Two variants:
  fonts/arena-font.png/.xml          plain white glyphs (tint in code)
  fonts/arena-font-outline.png/.xml  white glyphs with a dark 1px outline (readable over gameplay)
Exported at 2x: cap height 14 px (plain) / 18 px line (outline).
"""
from common import OUT, P, SCALE, canvas, outline, px

G = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "J": ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    ".": [".", ".", ".", ".", ".", ".", "#"],
    ",": ["..", "..", "..", "..", "..", ".#", "#."],
    ":": [".", ".", "#", ".", ".", "#", "."],
    ";": ["..", "..", ".#", "..", "..", ".#", "#."],
    "!": ["#", "#", "#", "#", "#", ".", "#"],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "-": ["...", "...", "...", "###", "...", "...", "..."],
    "+": ["...", "...", ".#.", "###", ".#.", "...", "..."],
    "=": ["...", "...", "###", "...", "###", "...", "..."],
    "/": ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."],
    "(": [".#", "#.", "#.", "#.", "#.", "#.", ".#"],
    ")": ["#.", ".#", ".#", ".#", ".#", ".#", "#."],
    "'": ["#", "#", ".", ".", ".", ".", "."],
    '"': ["#.#", "#.#", "...", "...", "...", "...", "..."],
    "#": [".#.#.", "#####", ".#.#.", ".#.#.", "#####", ".#.#.", "....."],
    "%": ["##..#", "##.#.", "...#.", "..#..", ".#...", ".#.##", "#..##"],
    "_": [".....", ".....", ".....", ".....", ".....", ".....", "#####"],
    "<": ["...", "..#", ".#.", "#..", ".#.", "..#", "..."],
    ">": ["...", "#..", ".#.", "..#", ".#.", "#..", "..."],
    "*": ["...", "#.#", ".#.", "#.#", "...", "...", "..."],
    "·": [".", ".", ".", "#", ".", ".", "."],
    "…": [".....", ".....", ".....", ".....", ".....", ".....", "#.#.#"],
    "×": ["...", "...", "#.#", ".#.", "#.#", "...", "..."],
    "→": [".....", "..#..", "...#.", "#####", "...#.", "..#..", "....."],
    " ": ["...", "...", "...", "...", "...", "...", "..."],
}


def render_glyph(rows, with_outline):
    w = len(rows[0])
    pad = 1 if with_outline else 0
    img = canvas(w + pad * 2, 7 + pad * 2)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == "#":
                px(img, x + pad, y + pad, P["white"] if y < 4 or not with_outline else (226, 222, 255, 255))
    if with_outline:
        outline(img, P["outline"], diagonal=True)
    return img


def build_font(name, with_outline):
    chars = list(G.keys())
    glyphs = {c: render_glyph(G[c], with_outline) for c in chars}
    cols = 16
    cell_w = max(g.width for g in glyphs.values()) + 1
    cell_h = glyphs["A"].height + 1
    rows = (len(chars) + cols - 1) // cols
    atlas = canvas(cols * cell_w, rows * cell_h)
    entries = []
    for i, c in enumerate(chars):
        g = glyphs[c]
        x, y = (i % cols) * cell_w, (i // cols) * cell_h
        atlas.alpha_composite(g, (x, y))
        adv = g.width + (1 if not with_outline else -1)
        if c == " ":
            g_w = 3 + (2 if with_outline else 0)
            adv = 4
        else:
            g_w = g.width
        ids = [ord(c)]
        if c.isalpha() and c.isascii():
            ids.append(ord(c.lower()))
        for cid in ids:
            entries.append((cid, x * SCALE, y * SCALE, g_w * SCALE, g.height * SCALE, adv * SCALE))
    from PIL import Image
    big = atlas.resize((atlas.width * SCALE, atlas.height * SCALE), Image.NEAREST)
    (OUT / "fonts").mkdir(parents=True, exist_ok=True)
    big.save(OUT / "fonts" / f"{name}.png", optimize=True)
    line_h = (cell_h + 2) * SCALE
    xml = [
        '<?xml version="1.0"?>',
        "<font>",
        f'  <info face="ArenaPixel{"Outline" if with_outline else ""}" size="{7 * SCALE}" bold="0" italic="0" charset="" unicode="1" stretchH="100" smooth="0" aa="0" padding="0,0,0,0" spacing="1,1"/>',
        f'  <common lineHeight="{line_h}" base="{(7 + (1 if with_outline else 0)) * SCALE}" scaleW="{big.width}" scaleH="{big.height}" pages="1" packed="0"/>',
        "  <pages>",
        f'    <page id="0" file="{name}.png"/>',
        "  </pages>",
        f'  <chars count="{len(entries)}">',
    ]
    for cid, x, y, w, h, adv in entries:
        xml.append(f'    <char id="{cid}" x="{x}" y="{y}" width="{w}" height="{h}" xoffset="0" yoffset="0" xadvance="{adv}" page="0" chnl="15"/>')
    xml += ["  </chars>", '  <kernings count="0"/>', "</font>"]
    (OUT / "fonts" / f"{name}.xml").write_text("\n".join(xml) + "\n")


def text_image(text, with_outline=True, colour=None, spacing=1):
    """Render text at native scale (used by the logo, OG image and preview)."""
    glyphs = [render_glyph(G.get(c.upper(), G["?"]), with_outline) for c in text]
    step = (lambda g: g.width + spacing) if not with_outline else (lambda g: g.width - 1)
    w = sum(step(g) for g in glyphs) + (1 if with_outline else 0)
    h = glyphs[0].height
    img = canvas(max(1, w), h)
    x = 0
    for g in glyphs:
        if colour:
            data = g.load()
            for yy in range(g.height):
                for xx in range(g.width):
                    if data[xx, yy][3] and data[xx, yy][:3] != P["outline"][:3]:
                        data[xx, yy] = colour
        img.alpha_composite(g, (x, 0))
        x += step(g)
    return img


def build():
    build_font("arena-font", False)
    build_font("arena-font-outline", True)


if __name__ == "__main__":
    build()
