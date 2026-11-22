#!/usr/bin/env python3
"""news-image-20261122: draw one image summing up Sunday 22 November 2026.

Pure Python 3.13 standard library. No network, no time, no randomness:
the program draws a 1024x1024 newspaper-style front page with a small
built-in 5x7 bitmap font and a hand-written PNG encoder, and writes
identical bytes on every run to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).

Stories (all reported on Sunday 22 November 2026):
  - COP31 climate talks in Antalya enter a second day of overtime,
    deadlocked over fossil fuels (SBS, One Turn, Daily Edition).
  - Iran strikes an industrial site in Bahrain; two oil tankers are
    hit near the Strait of Hormuz (Bahrain / IRGC / UK maritime agency).
  - Mexican forces capture cartel boss Fausto Isidro Meza Flores,
    "El Chapo Isidro"; 11 killed in the operation (DOJ, AP, Reuters).
  - A Russian cargo ship is hit by a drone in the Baltic Sea; Russia
    strikes Kryvyi Rih (SBS, One Turn).
  - The EU and Indonesia sign a trade deal after ten years of talks
    (Reuters, European Commission).
  - A boat carrying funeral mourners capsizes in Bayelsa, Nigeria;
    24 dead, 24 rescued (Reuters, AP, NEMA).
"""

import binascii
import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 241, 229)
WHITE = (255, 255, 255)
INK = (23, 35, 59)
NAVY = (20, 33, 61)
RED = (193, 39, 45)
TEAL = (15, 118, 110)
GOLD = (183, 121, 31)
BLUE = (29, 78, 216)
GRAY = (107, 114, 128)
CREAM = (250, 244, 224)
LIGHT = (232, 184, 75)

# ---------------------------------------------------------------- font
# 5x7 bitmap font, '#' = filled pixel. Uppercase, digits, punctuation.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
}

# Fix glyph widths: every row must be exactly 5 cells.
for _ch, _rows in FONT.items():
    assert len(_rows) == 7, _ch
    for _r in _rows:
        assert len(_r) == 5, (_ch, _r)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = r, g, b

    def border(self, x, y, w, h, color, t=2):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0 - t // 2, y0 - t // 2, t, t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, t=3):
        self.disc(cx, cy, r, color)
        self.disc(cx, cy, r - t, PAPER)

    def ellipse_outline(self, cx, cy, rx, ry, color, t=2):
        steps = 360
        for k in range(steps):
            a = 2.0 * math.pi * k / steps
            x = int(cx + rx * math.cos(a))
            y = int(cy + ry * math.sin(a))
            self.fill_rect(x - t // 2, y - t // 2, t, t, color)

    def polygon(self, pts, color):
        # Even-odd scanline fill for simple polygons.
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                    xs.append(x)
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.fill_rect(int(math.ceil(xs[k])), y,
                               int(math.floor(xs[k + 1])) - int(math.ceil(xs[k])) + 1,
                               1, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        self.polygon([(x0, y0), (x1, y1), (x2, y2)], color)

    # -- text -------------------------------------------------------------
    def text_width(self, s, scale):
        return max(0, len(s) * 6 * scale - scale)

    def draw_text(self, x, y, s, scale, color):
        s = s.upper()  # the built-in font is uppercase only
        cx = x
        for ch in s:
            if ch == ' ':
                cx += 6 * scale
                continue
            rows = FONT.get(ch)
            if rows is None:
                cx += 6 * scale
                continue
            for ry, row in enumerate(rows):
                for rx, cell in enumerate(row):
                    if cell == '#':
                        self.fill_rect(cx + rx * scale, y + ry * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx

    def draw_wrapped(self, x, y, s, scale, color, max_w, line_h=None):
        if line_h is None:
            line_h = 7 * scale + 3 * scale
        words = s.split(' ')
        lines = []
        cur = ''
        for word in words:
            trial = (cur + ' ' + word).strip()
            if self.text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        for i, ln in enumerate(lines):
            self.draw_text(x, y + i * line_h, ln, scale, color)
        return y + len(lines) * line_h


# ---------------------------------------------------------------- pictures
def draw_globe(cv, cx, cy, r, ink, teal):
    cv.disc(cx, cy, r, teal)
    cv.disc(cx, cy, r - 4, PAPER)
    cv.ellipse_outline(cx, cy, r - 4, r - 4, ink, 3)
    cv.ellipse_outline(cx, cy, (r - 4) // 2, r - 4, ink, 2)
    cv.line(cx - r + 4, cy, cx + r - 4, cy, ink, 2)
    # two land blobs
    cv.disc(cx - r // 3, cy - r // 3, r // 5, teal)
    cv.disc(cx + r // 4, cy + r // 3, r // 6, teal)


def draw_thermometer(cv, x, y, w, h, red, ink):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.border(x, y, w, h, ink, 2)
    cv.fill_rect(x + 3, y + h // 3, w - 6, h - h // 3 - 3, red)
    cv.disc(x + w // 2, y + h, w // 2 + 4, red)
    cv.ring(x + w // 2, y + h, w // 2 + 4, ink, 2)


def draw_flame(cv, cx, cy, s, red, gold):
    cv.polygon([(cx, cy - 3 * s), (cx + 2 * s, cy + s), (cx + s, cy + 2 * s),
                (cx - s, cy + 2 * s), (cx - 2 * s, cy + s)], red)
    cv.polygon([(cx, cy - s), (cx + s, cy + s), (cx - s, cy + s)], gold)


def draw_tanker(cv, cx, cy, s, ink, red):
    cv.polygon([(cx - 4 * s, cy), (cx + 4 * s, cy), (cx + 3 * s, cy + 2 * s),
                (cx - 3 * s, cy + 2 * s)], ink)
    cv.fill_rect(cx - 2 * s, cy - 2 * s, 2 * s, 2 * s, red)
    cv.line(cx - 5 * s, cy + 3 * s, cx + 5 * s, cy + 3 * s, ink, 2)
    cv.line(cx - 4 * s, cy + 4 * s, cx + 4 * s, cy + 4 * s, ink, 2)


def draw_badge(cv, cx, cy, r, gold, ink):
    cv.disc(cx, cy, r, gold)
    cv.disc(cx, cy, r - 4, PAPER)
    cv.ellipse_outline(cx, cy, r - 4, r - 4, ink, 2)
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rad = r - 10 if k % 2 == 0 else (r - 10) * 0.45
        pts.append((int(cx + rad * math.cos(ang)), int(cy + rad * math.sin(ang))))
    cv.polygon(pts, ink)


def draw_ship_burst(cv, cx, cy, s, blue, red):
    cv.polygon([(cx - 4 * s, cy), (cx + 4 * s, cy), (cx + 3 * s, cy + 2 * s),
                (cx - 3 * s, cy + 2 * s)], blue)
    cv.line(cx, cy, cx, cy - 3 * s, blue, 2)
    cv.triangle(cx, cy - 3 * s, cx + 2 * s, cy - 2 * s, cx, cy - 2 * s, red)
    bx, by = cx, cy - 4 * s
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        x0 = int(bx + 2 * s * math.cos(a))
        y0 = int(by + 2 * s * math.sin(a))
        x1 = int(bx + 3 * s * math.cos(a))
        y1 = int(by + 3 * s * math.sin(a))
        cv.line(x0, y0, x1, y1, red, 2)
    cv.disc(bx, by, s // 2, red)


def draw_trade(cv, cx, cy, s, teal, gold):
    cv.line(cx - 4 * s, cy - s, cx + 3 * s, cy - s, teal, 3)
    cv.triangle(cx + 3 * s, cy - s, cx + 4 * s, cy - 2 * s, cx + 4 * s, cy, teal)
    cv.line(cx + 4 * s, cy + s, cx - 3 * s, cy + s, gold, 3)
    cv.triangle(cx - 3 * s, cy + s, cx - 4 * s, cy, cx - 4 * s, cy + 2 * s, gold)
    cv.fill_rect(cx - 2 * s, cy + 2 * s, 4 * s, 2 * s, teal)


def draw_boat(cv, cx, cy, s, ink, blue):
    cv.polygon([(cx - 4 * s, cy), (cx + 4 * s, cy), (cx + 3 * s, cy + 2 * s),
                (cx - 3 * s, cy + 2 * s)], ink)
    cv.line(cx, cy, cx, cy - 3 * s, ink, 2)
    cv.triangle(cx, cy - 3 * s, cx + 3 * s, cy, cx, cy, blue)
    cv.line(cx - 5 * s, cy + 3 * s, cx + 5 * s, cy + 3 * s, blue, 2)
    cv.line(cx - 4 * s, cy + 4 * s, cx + 4 * s, cy + 4 * s, blue, 2)


def draw_list_icon(cv, cx, cy, s, gray):
    for k in range(3):
        y = cy - 2 * s + k * 2 * s
        cv.fill_rect(cx - 4 * s, y, s, s, RED)
        cv.fill_rect(cx - 2 * s, y, 6 * s, s, gray)


# ---------------------------------------------------------------- layout
def card(cv, x, y, w, h, kicker, kcolor, headline, summary, pic):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.border(x, y, w, h, INK, 2)
    cv.fill_rect(x, y, w, 30, kcolor)
    cv.draw_text(x + 14, y + 8, kicker, 2, WHITE)
    pic(x + w // 2, y + 62)
    hy = y + 104
    cv.draw_wrapped(x + 14, hy, headline, 3, INK, w - 28, line_h=27)
    cv.draw_wrapped(x + 14, hy + 56, summary, 2, INK, w - 28, line_h=17)


def build():
    cv = Canvas(W, H, PAPER)
    cv.border(16, 16, W - 32, H - 32, INK, 2)

    # masthead
    cv.fill_rect(24, 24, 976, 132, NAVY)
    cv.draw_text(48, 42, "WORLD NEWS IN ONE IMAGE", 2, LIGHT)
    cv.draw_text(48, 66, "THE WORLD TODAY", 7, CREAM)
    cv.draw_text(48, 124, "SUNDAY 22 NOVEMBER 2026", 3, LIGHT)
    draw_globe(cv, 918, 90, 46, INK, TEAL)
    cv.disc(946, 66, 7, RED)

    # lead story: COP31
    lx, ly, lw, lh = 24, 168, 976, 300
    cv.fill_rect(lx, ly, lw, lh, WHITE)
    cv.border(lx, ly, lw, lh, INK, 2)
    cv.fill_rect(lx, ly, 10, lh, RED)
    cv.draw_text(lx + 28, ly + 18, "CLIMATE - ANTALYA, TURKEY", 2, RED)
    cv.draw_text(lx + 28, ly + 46, "CLIMATE TALKS RUN INTO", 4, INK)
    cv.draw_text(lx + 28, ly + 86, "OVERTIME AT COP31", 4, INK)
    cv.draw_wrapped(lx + 28, ly + 140,
                    "Nations deadlocked over fossil fuels", 2, INK, 620, 17)
    cv.draw_wrapped(lx + 28, ly + 160,
                    "as the summit enters a second day", 2, INK, 620, 17)
    cv.draw_wrapped(lx + 28, ly + 180,
                    "of overtime with no final text agreed.", 2, INK, 620, 17)
    cv.line(lx + 28, ly + 236, lx + 640, ly + 236, GRAY, 2)
    cv.draw_text(lx + 28, ly + 252,
                 "31ST SUMMIT - 2ND DAY OF OVERTIME - ANTALYA", 2, GRAY)
    draw_globe(cv, 838, 300, 78, INK, TEAL)
    draw_thermometer(cv, 928, 268, 16, 74, RED, INK)

    # story cards, 3 + 3
    cw, ch, gap = 314, 236, 16
    xs = [24, 24 + cw + gap, 24 + 2 * (cw + gap)]
    ys = [480, 728]
    card(cv, xs[0], ys[0], cw, ch, "MIDDLE EAST", RED,
         "IRAN STRIKES BAHRAIN SITE",
         "Tehran hits a civilian plant; two tankers struck near Hormuz.",
         lambda cx, cy: (draw_tanker(cv, cx, cy - 6, 5, INK, RED),
                          draw_flame(cv, cx, cy - 26, 5, RED, GOLD)))
    card(cv, xs[1], ys[0], cw, ch, "JUSTICE", TEAL,
         "MEXICO CAPTURES CARTEL BOSS",
         "'El Chapo Isidro' seized; 11 killed in the raid.",
         lambda cx, cy: draw_badge(cv, cx, cy - 8, 30, GOLD, INK))
    card(cv, xs[2], ys[0], cw, ch, "WAR IN EUROPE", BLUE,
         "RUSSIAN SHIP HIT IN BALTIC",
         "Drone sets cargo ship ablaze; missile hits Kryvyi Rih.",
         lambda cx, cy: draw_ship_burst(cv, cx, cy - 4, 6, BLUE, RED))
    card(cv, xs[0], ys[1], cw, ch, "ECONOMY", GOLD,
         "EU SIGNS INDONESIA DEAL",
         "Ten years of talks end in a free-trade pact.",
         lambda cx, cy: draw_trade(cv, cx, cy - 8, 5, TEAL, GOLD))
    card(cv, xs[1], ys[1], cw, ch, "DISASTER", INK,
         "BOAT CAPSIZES, 24 DEAD",
         "Funeral boat sinks in Bayelsa; 24 dead, 24 rescued.",
         lambda cx, cy: draw_boat(cv, cx, cy - 6, 5, INK, BLUE))

    # briefs card
    bx, by = xs[2], ys[1]
    cv.fill_rect(bx, by, cw, ch, WHITE)
    cv.border(bx, by, cw, ch, INK, 2)
    cv.fill_rect(bx, by, cw, 30, GRAY)
    cv.draw_text(bx + 14, by + 8, "ALSO IN BRIEF", 2, WHITE)
    cv.fill_rect(bx + 14, by + 52, 10, 10, RED)
    cv.draw_wrapped(bx + 32, by + 48, "IRAQ - FIRE AT HARTHA POWER PLANT KILLS 4",
                    2, INK, cw - 46, 17)
    cv.fill_rect(bx + 14, by + 122, 10, 10, RED)
    cv.draw_wrapped(bx + 32, by + 118,
                    "USA - FBI CONFIRMS ITS CRIME DATABASE WAS BREACHED",
                    2, INK, cw - 46, 17)
    cv.draw_wrapped(bx + 14, by + 188, "SIX STORIES, ONE DAY.",
                    2, GRAY, cw - 28, 17)

    # footer
    foot = "REPORTED ON SUNDAY 22 NOVEMBER 2026 - REUTERS, AP, SBS"
    cv.draw_text((W - cv.text_width(foot, 2)) // 2, 976, foot, 2, GRAY)
    return cv


# ---------------------------------------------------------------- png
def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw.extend(cv.px[y * cv.w * 3:(y + 1) * cv.w * 3])

    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data +
                struct.pack(">I", binascii.crc32(typ + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    out = bytearray(b"\x89PNG\r\n\x1a\n")
    out += chunk(b"IHDR", ihdr)
    out += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    out += chunk(b"IEND", b"")
    return bytes(out)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(build())
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), W, H))


if __name__ == "__main__":
    main()
