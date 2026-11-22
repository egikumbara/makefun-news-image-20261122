#!/usr/bin/env python3
"""The World Today -- Sunday 22 November 2026.

Draws a one-page newspaper front page summing up six real stories
first reported on Sunday 22 November 2026, as a single 1024x1024 PNG.

Pure standard library only: hand-rolled PNG writer and a hand-built
5x7 bitmap font (glyphs stored as integer bit rows). No network, no
clock, no randomness: two runs write byte-identical files.
"""
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (248, 244, 233)
INK = (18, 18, 18)
RED = (168, 24, 34)
BLUE = (28, 74, 132)
GOLD = (176, 130, 30)
GREY = (96, 93, 84)
LIGHT = (233, 227, 211)
WHITE = (255, 255, 255)
SKY = (172, 203, 228)
GREEN = (44, 108, 60)
ORANGE = (210, 106, 28)
TEAL = (24, 110, 108)
DARKBLUE = (22, 46, 84)

# ------------------------------------------------------------------ font --
# 5x7 glyphs. Each glyph is 7 rows; each row is a 5-bit integer, the
# high bit being the leftmost pixel. Only the characters the page
# needs are included. Written from the letterforms, not copied.
FONT = {
    'A': (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    'B': (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    'C': (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    'D': (0b11100, 0b10010, 0b10001, 0b10001, 0b10001, 0b10010, 0b11100),
    'E': (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    'F': (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    'G': (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    'H': (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    'I': (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    'J': (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    'K': (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    'L': (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    'M': (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    'N': (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    'O': (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    'P': (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    'Q': (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    'R': (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    'S': (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    'T': (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    'U': (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    'V': (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    'W': (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001),
    'X': (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    'Y': (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    'Z': (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    '0': (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    '1': (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    '2': (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    '3': (0b11110, 0b00001, 0b00001, 0b01110, 0b00001, 0b00001, 0b11110),
    '4': (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    '5': (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    '6': (0b01110, 0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    '7': (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    '8': (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    '9': (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00001, 0b01110),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0b01100, 0b01100),
    ',': (0, 0, 0, 0, 0b01100, 0b00100, 0b01000),
    ':': (0, 0b01100, 0b01100, 0, 0b01100, 0b01100, 0),
    ';': (0, 0b01100, 0b01100, 0, 0b01100, 0b00100, 0b01000),
    '-': (0, 0, 0, 0b01110, 0, 0, 0),
    "'": (0b00100, 0b00100, 0b01000, 0, 0, 0, 0),
    '(': (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ')': (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    '/': (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    '%': (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    '+': (0, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0),
    '=': (0, 0, 0b11111, 0, 0b11111, 0, 0),
    '&': (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    '!': (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100),
    '?': (0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0, 0b00100),
    '"': (0b01010, 0b01010, 0b01010, 0, 0, 0, 0),
    '*': (0, 0b10101, 0b01110, 0b11111, 0b01110, 0b10101, 0),
    '$': (0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100),
}

CHAR_W = 6  # glyph cell width in font units (5 + 1 spacing)


def text_w(text, scale):
    return len(text) * CHAR_W * scale - scale


def wrap(text, max_chars):
    """Greedy word wrap to at most max_chars per line."""
    lines = []
    cur = ""
    for word in text.split():
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas --
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def rect(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            for xx in (cx - dx, cx + dx):
                self.fill_rect(xx - t // 2, cy + dy, t, 1, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s.upper():
            rows = FONT.get(ch, FONT[' '])
            for r in range(7):
                bits = rows[r]
                for col in range(5):
                    if bits >> (4 - col) & 1:
                        self.fill_rect(cx + col * scale, y + r * scale,
                                       scale, scale, c)
            cx += CHAR_W * scale
        return cx

    def text_center(self, y, s, scale, c):
        self.text((self.w - text_w(s, scale)) // 2, y, s, scale, c)

    def para(self, x, y, s, scale, c, max_chars, leading=None):
        if leading is None:
            leading = 7 * scale + 4
        for line in wrap(s, max_chars):
            self.text(x, y, line, scale, c)
            y += leading
        return y


# -------------------------------------------------------------- pictures --
def pic_gulf(cv, x, y, w, h):
    """Night sky over the Gulf: radar arcs, a rising missile trail."""
    cv.fill_rect(x, y, w, h, DARKBLUE)
    for sx, sy in ((18, 22), (52, 14), (96, 30), (140, 12), (176, 26),
                   (34, 44), (120, 46), (162, 44), (70, 10)):
        cv.fill_rect(x + sx, y + sy, 3, 3, WHITE)
    # radar dish arcs
    cx, cy = x + 52, y + h - 18
    for r in (14, 26, 38):
        cv.ring(cx, cy, r, SKY, 3)
    cv.fill_rect(cx - 3, cy - 3, 7, 7, SKY)
    cv.fill_rect(cx - 2, cy, 5, h - cy - 2, SKY)
    # missile streaks
    for mx, my, ln in ((130, 30, 46), (155, 48, 34), (112, 56, 26)):
        cv.fill_rect(x + mx, y + my, 4, ln, ORANGE)
        cv.fill_rect(x + mx - 2, y + my - 8, 8, 8, GOLD)
    # explosion burst bottom right
    ex, ey = x + w - 42, y + h - 34
    cv.disc(ex, ey, 16, ORANGE)
    cv.disc(ex, ey, 9, GOLD)
    cv.disc(ex, ey, 4, WHITE)


def pic_cop(cv, x, y, w, h):
    """A globe with a green leaf: climate talks."""
    cv.fill_rect(x, y, w, h, SKY)
    cx, cy = x + w // 2 - 14, y + h // 2
    cv.disc(cx, cy, 40, BLUE)
    cv.disc(cx - 12, cy - 10, 12, GREEN)
    cv.disc(cx + 14, cy + 12, 10, GREEN)
    cv.fill_rect(cx - 40, cy - 3, 80, 6, WHITE)
    cv.fill_rect(cx - 3, cy - 40, 6, 80, WHITE)
    # leaf
    lx, ly = x + w - 44, y + 14
    cv.disc(lx, ly, 12, GREEN)
    cv.fill_rect(lx - 12, ly + 8, 4, 16, GREEN)


def pic_quake(cv, x, y, w, h):
    """Cracked ground and a shaking mountain skyline."""
    cv.fill_rect(x, y, w, h, LIGHT)
    cv.fill_rect(x, y + h - 34, w, 34, GOLD)
    # mountains
    for mx, my, mh in ((10, 46, 44), (66, 30, 60), (128, 50, 40)):
        for dy in range(mh):
            half = dy * 30 // mh
            cv.fill_rect(x + mx + 30 - half, y + my + dy, 2 * half + 1, 1,
                         GREY if dy % 2 else INK)
    # crack zig-zag
    cx = x + 20
    cy = y + h - 34
    pts = [(cx, cy), (cx + 26, cy - 12), (cx + 44, cy - 4),
           (cx + 70, cy - 18), (cx + 96, cy - 6), (cx + 124, cy - 16),
           (cx + 150, cy - 8)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        steps = max(abs(bx - ax), abs(by - ay))
        for i in range(steps + 1):
            px = ax + (bx - ax) * i // steps
            py = ay + (by - ay) * i // steps
            cv.fill_rect(px, py, 3, 3, RED)


def pic_card(cv, x, y, w, h):
    """A credit card on a desk."""
    cv.fill_rect(x, y, w, h, TEAL)
    cv.fill_rect(x + 24, y + 22, w - 48, h - 44, WHITE)
    cv.fill_rect(x + 24, y + 34, w - 48, 14, BLUE)
    cv.fill_rect(x + 40, y + 62, 34, 22, GOLD)
    cv.fill_rect(x + 40, y + 96, 90, 8, INK)
    cv.text(x + 92, y + 62, "10", 2, RED)


def pic_boat(cv, x, y, w, h):
    """Waves and a small boat tipping over."""
    cv.fill_rect(x, y, w, h, SKY)
    for wy in (y + h - 46, y + h - 30, y + h - 14):
        for wx in range(x, x + w, 26):
            cv.fill_rect(wx, wy, 18, 5, BLUE)
    # hull, tilted
    for i in range(56):
        cv.fill_rect(x + 46 + i, y + h - 62 + i // 6, 3, 3, RED)
    cv.fill_rect(x + 62, y + h - 88, 4, 26, INK)
    cv.fill_rect(x + 66, y + h - 88, 30, 16, WHITE)


def pic_storm(cv, x, y, w, h):
    """Storm cloud, rain and a broken roofline."""
    cv.fill_rect(x, y, w, h, (198, 205, 214))
    cv.disc(x + 52, y + 34, 22, GREY)
    cv.disc(x + 84, y + 28, 26, INK)
    cv.disc(x + 116, y + 36, 20, GREY)
    cv.fill_rect(x + 34, y + 40, 104, 16, INK)
    for rx in range(38, 150, 14):
        cv.fill_rect(x + rx, y + 62, 3, 16, BLUE)
        cv.fill_rect(x + rx + 5, y + 82, 3, 16, BLUE)
    # broken roof
    cv.fill_rect(x + 30, y + h - 22, 110, 6, RED)
    cv.fill_rect(x + 44, y + h - 34, 8, 14, RED)


# ----------------------------------------------------------------- page --
def draw_page():
    cv = Canvas(W, H, PAPER)
    M = 32                      # margin
    CW = W - 2 * M              # 960 content width

    # ---- masthead ------------------------------------------------------
    cv.text_center(30, "THE WORLD TODAY", 7, INK)
    cv.hline(M, 96, CW, INK, 4)
    cv.hline(M, 104, CW, INK, 1)

    # ---- date banner ---------------------------------------------------
    cv.fill_rect(M, 112, CW, 40, RED)
    cv.text_center(121, "SUNDAY 22 NOVEMBER 2026", 3, WHITE)
    cv.text(M, 160, "WORLD NEWS IN BRIEF", 2, GREY)
    cv.text(W - M - text_w("SIX STORIES THAT SHAPED THE DAY", 2), 160,
            "SIX STORIES THAT SHAPED THE DAY", 2, GREY)
    cv.hline(M, 182, CW, INK, 2)

    # ---- lead story: Gulf war widens ------------------------------------
    ly = 196
    cv.text(M, ly, "GULF WAR WIDENS", 4, RED)
    ly += 7 * 4 + 10
    cv.text(M, ly, "IRAN CLAIMS NEW STRIKES ON US", 3, INK)
    ly += 7 * 3 + 6
    cv.text(M, ly, "RADARS IN BAHRAIN", 3, INK)
    ly += 7 * 3 + 12
    pic_gulf(cv, W - M - 300, 196, 300, 172)
    lead_body = ("Iran's Revolutionary Guard said it hit two US Patriot "
                 "air-defence radars at bases in Bahrain, as Houthi "
                 "forces struck the Saudi capital and tankers were hit "
                 "in the Gulf. No casualties were reported in Bahrain.")
    cv.para(M, ly, lead_body, 2, INK, 52)
    cv.hline(M, 384, CW, INK, 2)

    # ---- row 2: COP31 + Peru --------------------------------------------
    ry = 400
    col_w = (CW - 24) // 2
    # COP31 (left)
    cv.text(M, ry, "COP31 NEARS A DEAL", 3, GREEN)
    pic_cop(cv, M, ry + 34, col_w, 96)
    cv.para(M, ry + 142, "Climate talks in Antalya tabled a new package in "
             "the early hours of Sunday. Nearly 200 delegations hope to "
             "approve it at a session later today.", 2, INK, 40)
    # Peru (right)
    px = M + col_w + 24
    cv.text(px, ry, "PERU SHAKEN BY 6.9 QUAKE", 3, ORANGE)
    pic_quake(cv, px, ry + 34, col_w, 96)
    cv.para(px, ry + 142, "A magnitude 6.9 earthquake struck Peru's Andes "
             "on Sunday. Shaking was felt across the region, with no "
             "deaths or major damage immediately reported.", 2, INK, 40)
    cv.vline(M + col_w + 12, ry, 208, GREY, 1)
    cv.hline(M, 620, CW, INK, 2)

    # ---- row 3: three stories -------------------------------------------
    ty = 636
    tw = (CW - 48) // 3
    stories = [
        ("TRUMP BACKS 10% CARD CAP", BLUE, pic_card,
         "President Trump said he will work with Democrats to cap "
         "credit-card interest rates at 10%, a move aimed at easing "
         "costs for borrowers."),
        ("BOAT SINKS IN NIGERIA", RED, pic_boat,
         "At least 24 people died when an overloaded boat carrying "
         "mourners to a funeral capsized in southern Nigeria."),
        ("BRAZIL TOWN CLEARS RUBBLE", TEAL, pic_storm,
         "Residents of a Brazilian town cleared rubble after a deadly "
         "storm tore through homes. Survivors said: we lost "
         "everything."),
    ]
    for i, (head, col, pic, body) in enumerate(stories):
        sx = M + i * (tw + 24)
        cv.text(sx, ty, head, 2, col)
        pic(cv, sx, ty + 30, tw, 96)
        cv.para(sx, ty + 138, body, 2, INK, 27)
        if i:
            cv.vline(sx - 12, ty, 236, GREY, 1)
    cv.hline(M, 884, CW, INK, 2)

    # ---- footer strip ----------------------------------------------------
    cv.text(M, 900, "ALSO TODAY:", 2, RED)
    cv.para(M + text_w("ALSO TODAY: ", 2), 900,
            "Bitcoin rebounds after a two-year low. French protesters "
            "march for a sixth weekend. Belgium faces an air shutdown "
            "in Monday's strike.",
            2, INK, 64)
    cv.hline(M, 956, CW, INK, 4)
    cv.text_center(968, "THE WORLD TODAY - SUNDAY 22 NOVEMBER 2026", 2, GREY)
    return cv


# ------------------------------------------------------------------- png --
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw.extend(cv.px[y * cv.w * 3:(y + 1) * cv.w * 3])
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.environ.get(
        "OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    cv = draw_page()
    write_png(cv, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
