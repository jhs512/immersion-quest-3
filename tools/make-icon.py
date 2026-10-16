"""Render the 몰입 퀘스트 app icon: a bold Q (for 퀘스트) on the brand green tile.

The Q is drawn geometrically (a thick light ring with a gold tail) so no font is needed and
every size stays crisp. Outputs under assets/icon/: icon-1024.png (master), icon.ico (Windows),
icon-foreground.png (Android adaptive foreground on transparent), and the sizes the macOS and
Android packaging scripts use. Pillow only; no network.
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/icon"
OUT.mkdir(parents=True, exist_ok=True)

GREEN = (23, 61, 54, 255)      # .sidebar background
LIGHT = (239, 250, 245, 255)   # sidebar text
GOLD = (242, 201, 76, 255)
CLEAR = (0, 0, 0, 0)
SCALE = 4
SIZE = 1024 * SCALE


def letter_q(draw, hole, scale=1.0, offset=(0, 0)):
    """A Q centred in a 1024 box. `hole` is the colour inside the ring (tile green, or
    transparent for the adaptive foreground); `scale` shrinks it for that foreground."""
    s = SCALE * scale
    ox, oy = offset
    cx, cy = 512 * s + ox, 490 * s + oy
    outer, inner = 300 * s, 175 * s
    draw.ellipse([cx - outer, cy - outer, cx + outer, cy + outer], fill=LIGHT)
    draw.ellipse([cx - inner, cy - inner, cx + inner, cy + inner], fill=hole)
    # The tail: a thick rounded stroke from inside the ring's lower right out past the rim.
    tail = [(600 * s + ox, 600 * s + oy), (800 * s + ox, 820 * s + oy)]
    draw.line(tail, fill=GOLD, width=int(118 * s))
    for x, y in tail:
        r = 59 * s
        draw.ellipse([x - r, y - r, x + r, y + r], fill=GOLD)


def tile():
    image = Image.new("RGBA", (SIZE, SIZE), CLEAR)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=SIZE * 0.22, fill=GREEN)
    letter_q(draw, GREEN)
    return image.resize((1024, 1024), Image.LANCZOS)


def foreground():
    # Android adaptive icons are cropped to a circle inside the middle 66%, so draw the Q small.
    image = Image.new("RGBA", (SIZE, SIZE), CLEAR)
    draw = ImageDraw.Draw(image)
    letter_q(draw, CLEAR, scale=0.6, offset=(SIZE * 0.2, SIZE * 0.2))
    return image.resize((1024, 1024), Image.LANCZOS)


master = tile()
master.save(OUT / "icon-1024.png")
master.save(OUT / "icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
foreground().save(OUT / "icon-foreground.png")
for size in (48, 72, 96, 144, 192, 512):
    master.resize((size, size), Image.LANCZOS).save(OUT / f"icon-{size}.png")
# Raw RGBA for the window icon (taskbar and title bar): src/main.rs embeds it without a decoder.
(OUT / "icon-128.rgba").write_bytes(master.resize((128, 128), Image.LANCZOS).tobytes())
print("icons written to", OUT)
