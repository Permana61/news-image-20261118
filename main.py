#!/usr/bin/env python3
"""World News — Wednesday 18 November 2026.

Draws a 1024x1024 infographic summing up the day's world news, using
only the Python standard library. No network, no randomness, no clock:
every run writes byte-identical PNG bytes to $MAKEFUN_OUTPUT_DIR/entry.png.

Layout: navy masthead with the date, then six panels (2 columns x 3 rows),
one per verified story of 18 November 2026. Each panel has a hand-drawn
pictogram (rectangles, circles, polygons — no external images), a headline
and a one-line summary, all rendered with a built-in 5x7 bitmap font.
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
INK = (27, 42, 74)
NAVY = (20, 33, 61)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
GREY = (90, 96, 110)
RED = (178, 34, 34)
GREEN = (34, 139, 34)
ORANGE = (230, 126, 34)
BLUE = (41, 98, 168)
LIGHT = (233, 228, 216)

# ------------------------------------------------------------------ font
# 5x7 bitmap glyphs: seven strings of five '#' / '.' per character.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (6 px advance per glyph)."""
    return len(text) * 6 * scale - scale


# -------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, t, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d2 <= r * r:
                    self.set(xx, yy, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(-(thick // 2), thick // 2 + 1):
                for b in range(-(thick // 2), thick // 2 + 1):
                    self.set(x0 + a, y0 + b, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def poly(self, points, color):
        """Filled polygon via scanline fill."""
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                    self.set(x, y, color)

    def text(self, s, x, y, scale, color):
        for ci, ch in enumerate(s):
            glyph = FONT.get(ch, FONT[" "])
            ox = x + ci * 6 * scale
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == "1":
                        self.rect(ox + col * scale, y + row * scale,
                                  scale, scale, color)

    def text_center(self, s, cx, y, scale, color):
        self.text(s, cx - text_width(s, scale) // 2, y, scale, color)


# -------------------------------------------------------------- pictograms
def pic_plane(cv, x, y):
    """Airliner + red flag with a gold star (Trump lands in China)."""
    cv.rect(x + 8, y + 58, 118, 16, NAVY)          # fuselage
    cv.poly([(x + 126, y + 58), (x + 140, y + 66), (x + 126, y + 74)], NAVY)
    cv.poly([(x + 8, y + 58), (x + 22, y + 66), (x + 8, y + 74)], NAVY)
    cv.poly([(x + 55, y + 58), (x + 75, y + 28), (x + 88, y + 58)], NAVY)
    cv.poly([(x + 60, y + 74), (x + 74, y + 96), (x + 86, y + 74)], NAVY)
    cv.poly([(x + 14, y + 58), (x + 14, y + 36), (x + 30, y + 58)], NAVY)
    for wx in range(34, 118, 14):
        cv.rect(x + wx, y + 62, 7, 7, WHITE)
    cv.rect(x + 8, y + 104, 4, 26, INK)            # flag pole
    cv.rect(x + 12, y + 104, 44, 26, RED)          # flag
    star = [(x + 34, y + 106), (x + 37, y + 113), (x + 44, y + 113),
            (x + 38, y + 118), (x + 40, y + 125), (x + 34, y + 121),
            (x + 28, y + 125), (x + 30, y + 118), (x + 24, y + 113),
            (x + 31, y + 113)]
    cv.poly(star, GOLD)


def pic_strike(cv, x, y):
    """Explosion burst + quadcopter drone (Iran hits Kuwait, Bahrain)."""
    cx, cy = x + 60, y + 56
    for k in range(12):
        import math
        a = k * math.pi / 6
        a2 = a + math.pi / 12
        cv.poly([(cx, cy),
                 (int(cx + 46 * math.cos(a)), int(cy + 46 * math.sin(a))),
                 (int(cx + 20 * math.cos(a2)), int(cy + 20 * math.sin(a2)))],
                ORANGE if k % 2 == 0 else GOLD)
    cv.circle(cx, cy, 16, RED)
    cv.circle(cx, cy, 9, WHITE)
    # drone, lower right
    cv.rect(x + 92, y + 102, 42, 14, INK)
    cv.circle(x + 97, y + 102, 10, INK)
    cv.circle(x + 129, y + 102, 10, INK)
    cv.rect(x + 92, y + 92, 52, 4, INK)
    cv.rect(x + 88, y + 92, 4, 24, INK)
    cv.rect(x + 142, y + 92, 4, 24, INK)


def pic_ipo(cv, x, y):
    """Rising bar chart + dollar sign (Anthropic record IPO)."""
    bars = [(x + 12, 34, GREEN), (x + 42, 58, GREEN),
            (x + 72, 82, GREEN), (x + 102, 108, GOLD)]
    for bx, bh, col in bars:
        cv.rect(bx, y + 128 - bh, 22, bh, col)
    cv.line(x + 52, y + 26, x + 122, y + 10, RED, 4)
    cv.poly([(x + 122, y + 10), (x + 106, y + 8), (x + 118, y + 22)], RED)
    cv.text("$", x + 8, y + 8, 3, NAVY)


def pic_vangogh(cv, x, y):
    """Gilt frame with sunflowers (Van Gogh record sale)."""
    cv.rect(x + 6, y + 6, 128, 128, GOLD)
    cv.rect(x + 14, y + 14, 112, 112, (58, 110, 165))
    # sunflower 1
    for k in range(8):
        import math
        a = k * math.pi / 4
        px = int(x + 52 + 20 * math.cos(a))
        py = int(y + 52 + 20 * math.sin(a))
        cv.circle(px, py, 9, GOLD)
    cv.circle(x + 52, y + 52, 14, (101, 67, 33))
    # sunflower 2
    for k in range(8):
        import math
        a = k * math.pi / 4 + 0.4
        px = int(x + 96 + 16 * math.cos(a))
        py = int(y + 96 + 16 * math.sin(a))
        cv.circle(px, py, 7, GOLD)
    cv.circle(x + 96, y + 96, 11, (101, 67, 33))
    cv.rect(x + 52, y + 66, 5, 52, GREEN)
    cv.rect(x + 96, y + 107, 5, 18, GREEN)


def pic_gta(cv, x, y):
    """Game controller + big 99 (GTA 6 reviews)."""
    cv.rect(x + 18, y + 46, 104, 52, INK)
    cv.circle(x + 18, y + 76, 22, INK)
    cv.circle(x + 122, y + 76, 22, INK)
    cv.rect(x + 38, y + 66, 8, 22, WHITE)
    cv.rect(x + 31, y + 73, 22, 8, WHITE)
    cv.circle(x + 96, y + 66, 6, GOLD)
    cv.circle(x + 108, y + 78, 6, RED)
    cv.circle(x + 84, y + 78, 6, GREEN)
    cv.circle(x + 96, y + 90, 6, BLUE)
    cv.text("99", x + 44, y + 6, 5, RED)


def pic_brazil(cv, x, y):
    """Brazil flag + coin stack ($10B fiscal package)."""
    cv.rect(x + 8, y + 18, 124, 84, GREEN)
    cv.poly([(x + 70, y + 24), (x + 126, y + 60), (x + 70, y + 96),
             (x + 14, y + 60)], GOLD)
    cv.circle(x + 70, y + 60, 20, BLUE)
    cv.rect(x + 8, y + 112, 30, 8, GOLD)
    cv.rect(x + 14, y + 104, 30, 8, GOLD)
    cv.rect(x + 20, y + 96, 30, 8, GOLD)
    cv.text("$10B", x + 62, y + 106, 3, NAVY)


# ---------------------------------------------------------------- panels
# (tag, accent, headline lines, summary, pictogram)
PANELS = [
    ("DIPLOMACY", NAVY,
     ("TRUMP LANDS IN", "CHINA"),
     "XI GREETS HIM; 3-WAY TALKS DUE 19 NOV",
     pic_plane),
    ("CONFLICT", RED,
     ("IRAN HITS", "KUWAIT, BAHRAIN"),
     "DRONES SHOT DOWN; NO DAMAGE REPORTED",
     pic_strike),
    ("TECH & MARKETS", GREEN,
     ("ANTHROPIC IPO", "$81.3B AT $1.5T"),
     "BIGGEST IPO EVER; LISTING ON 19 NOV",
     pic_ipo),
    ("ART", GOLD,
     ("VAN GOGH SELLS", "$190.4M RECORD"),
     "RECORD PRICE AT SOTHEBY'S NEW YORK",
     pic_vangogh),
    ("GAMING", (128, 0, 128),
     ("GTA 6 SCORES 99", "ON METACRITIC"),
     "TIES ALL-TIME RECORD BEFORE LAUNCH",
     pic_gta),
    ("ECONOMY", BLUE,
     ("BRAZIL SENATE", "OKS $10B PLAN"),
     "LULA PACKAGE HEADS TO LOWER HOUSE",
     pic_brazil),
]


def draw_panel(cv, px, py, pw, ph, tag, accent, lines, summary, pic):
    cv.rect(px, py, pw, ph, WHITE)
    cv.rect(px, py, pw, 8, accent)
    # thin border
    cv.rect(px, py + 8, pw, 2, LIGHT)
    cv.rect(px, py + ph - 2, pw, 2, LIGHT)
    cv.rect(px, py, 2, ph, LIGHT)
    cv.rect(px + pw - 2, py, 2, ph, LIGHT)
    cv.text(tag, px + 16, py + 20, 2, accent)
    # pictogram box
    ix, iy = px + 16, py + 48
    cv.rect(ix - 4, iy - 4, 148, 148, LIGHT)
    pic(cv, ix, iy)
    # headline, right of pictogram
    tx = px + 180
    cv.text(lines[0], tx, py + 58, 3, INK)
    cv.text(lines[1], tx, py + 86, 3, INK)
    # summary line across the bottom
    cv.rect(px + 16, py + 216, pw - 32, 2, LIGHT)
    cv.text(summary, px + 16, py + 232, 2, GREY)


def draw():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.rect(0, 0, W, 100, NAVY)
    cv.rect(0, 100, W, 4, GOLD)
    cv.text_center("WORLD NEWS", W // 2, 14, 6, WHITE)
    cv.text_center("WEDNESDAY 18 NOVEMBER 2026", W // 2, 62, 3, GOLD)
    # grid: 2 cols x 3 rows
    margin, gap = 16, 12
    pw = (W - 2 * margin - gap) // 2
    ph = 284
    y0 = 116
    for i, (tag, accent, lines, summary, pic) in enumerate(PANELS):
        col = i % 2
        row = i // 2
        px = margin + col * (pw + gap)
        py = y0 + row * (ph + gap)
        draw_panel(cv, px, py, pw, ph, tag, accent, lines, summary, pic)
    # footer: sources
    cv.text_center("SOURCES: AP - REUTERS - BBC - POLYGON - THE ART NEWSPAPER",
                   W // 2, 996, 2, GREY)
    return cv


# ------------------------------------------------------------------- png
def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        c += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(draw())
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
