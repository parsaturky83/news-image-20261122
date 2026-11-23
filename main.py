#!/usr/bin/env python3
"""THE WORLD TODAY - newspaper front page, 1024x1024 PNG.
Pure Python 3.13 stdlib only. No network, clock or randomness.
Own mixed-case bitmap font designed in this session (6x11 grid).
Writes entry.png to $MAKEFUN_OUTPUT_DIR (default /output).
"""
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (246, 241, 229)
WHITE = (255, 255, 255)
INK = (23, 35, 59)
NAVY = (20, 33, 61)
RED = (193, 39, 45)
TEAL = (15, 118, 110)
GOLD = (183, 121, 31)
BLUE = (29, 78, 216)
GREY = (107, 114, 128)
CREAM = (250, 244, 224)
LGOLD = (232, 184, 75)
LBLUE = (176, 208, 228)
GREEN = (34, 120, 70)
ORANGE = (230, 120, 30)
YELLOW = (245, 200, 60)
LIGHTGREY = (238, 236, 230)

# ---------------------------------------------------------------- font
# 6 columns x 11 rows. Row 0 top margin, rows 1-8 cap height,
# rows 4-8 x-height, rows 9-10 descenders. '#' = ink pixel.
# Designed from scratch here: 0 is slashed, O is plain; 2 and 7 have
# flat top bars; lowercase c sits at x-height; ascenders reach row 1,
# descenders reach rows 9-10.
FONT = {
'A': ["......",".####.","#....#","#....#","#....#","######","#....#","#....#","#....#","......","......"],
'B': ["......","#####.","#....#","#....#","#####.","#....#","#....#","#....#","#####.","......","......"],
'C': ["......",".####.","#....#","#.....","#.....","#.....","#.....","#....#",".####.","......","......"],
'D': ["......","#####.","#....#","#....#","#....#","#....#","#....#","#....#","#####.","......","......"],
'E': ["......","######","#.....","#.....","#####.","#.....","#.....","#.....","######","......","......"],
'F': ["......","######","#.....","#.....","#####.","#.....","#.....","#.....","#.....","......","......"],
'G': ["......",".####.","#....#","#.....","#.....","#..###","#....#","#....#",".####.","......","......"],
'H': ["......","#....#","#....#","#....#","######","#....#","#....#","#....#","#....#","......","......"],
'I': ["......","..##..","..#...","..#...","..#...","..#...","..#...","..#...","..##..","......","......"],
'J': ["......","....##",".....#",".....#",".....#",".....#",".....#","#....#",".####.","......","......"],
'K': ["......","#...#.","#..#..","#.#...","###...","#.#...","#..#..","#...#.","#...#.","......","......"],
'L': ["......","#.....","#.....","#.....","#.....","#.....","#.....","#.....","######","......","......"],
'M': ["......","#....#","##..##","#.##.#","#.##.#","#....#","#....#","#....#","#....#","......","......"],
'N': ["......","#....#","##...#","#.#..#","#..#.#","#...##","#....#","#....#","#....#","......","......"],
'O': ["......",".####.","#....#","#....#","#....#","#....#","#....#","#....#",".####.","......","......"],
'P': ["......","#####.","#....#","#....#","#####.","#.....","#.....","#.....","#.....","......","......"],
'Q': ["......",".####.","#....#","#....#","#....#","#....#","#..#.#","#...#.",".####.","....#.","....#."],
'R': ["......","#####.","#....#","#....#","#####.","#.#...","#..#..","#...#.","#...#.","......","......"],
'S': ["......",".####.","#.....","#.....",".####.",".....#",".....#",".....#",".####.","......","......"],
'T': ["......","######","..#...","..#...","..#...","..#...","..#...","..#...","..#...","......","......"],
'U': ["......","#....#","#....#","#....#","#....#","#....#","#....#","#....#",".####.","......","......"],
'V': ["......","#....#","#....#","#....#","#....#","#....#",".#..#.",".#..#.","..##..","......","......"],
'W': ["......","#....#","#....#","#....#","#.##.#","#.##.#","#.##.#","##..##","#....#","......","......"],
'X': ["......","#...#.",".#.#..","..#...","..#...","..#...",".#.#..","#...#.","#...#.","......","......"],
'Y': ["......","#...#.","#...#.",".#.#..","..#...","..#...","..#...","..#...","..#...","......","......"],
'Z': ["......","######","....#.","...#..","...#..","..#...",".#....","#.....","######","......","......"],
'a': ["......","......","......","......",".####.",".....#",".####.","#....#",".####.","......","......"],
'b': ["......","#.....","#.....","#.....","#####.","#....#","#....#","#....#","#####.","......","......"],
'c': ["......","......","......","......",".####.","#.....","#.....","#.....",".####.","......","......"],
'd': ["......","....#.","....#.","....#.",".####.","#....#","#....#","#....#",".####.","......","......"],
'e': ["......","......","......","......",".####.","#....#","######","#.....",".####.","......","......"],
'f': ["......","..###.",".#....",".#....","#####.",".#....",".#....",".#....",".#....","......","......"],
'g': ["......","......","......","......",".####.","#....#","#....#","#....#",".####.","....#.",".###.."],
'h': ["......","#.....","#.....","#.....","#####.","#....#","#....#","#....#","#....#","......","......"],
'i': ["......","......","..#...","......","..#...","..#...","..#...","..#...","..#...","......","......"],
'j': ["......","......","...#..","......","...#..","...#..","...#..","...#..","...#..","...#..","..##.."],
'k': ["......","#.....","#.....","#.....","#...#.","#..#..","###...","#..#..","#...#.","......","......"],
'l': ["......","..#...","..#...","..#...","..#...","..#...","..#...","..#...","..#...","......","......"],
'm': ["......","......","......","......","##.##.","#.#.#.","#.#.#.","#.#.#.","#.#.#.","......","......"],
'n': ["......","......","......","......","#####.","#....#","#....#","#....#","#....#","......","......"],
'o': ["......","......","......","......",".####.","#....#","#....#","#....#",".####.","......","......"],
'p': ["......","......","......","......","#####.","#....#","#....#","#####.","#.....","#.....","#....."],
'q': ["......","......","......","......",".####.","#....#","#....#","#....#",".####.","....#.","....#."],
'r': ["......","......","......","......","#####.","#....#","#.....","#.....","#.....","......","......"],
's': ["......","......","......","......",".####.","#.....",".####.",".....#",".####.","......","......"],
't': ["......","...#..","...#..","...#..","#####.","...#..","...#..","...#..","..##..","......","......"],
'u': ["......","......","......","......","#....#","#....#","#....#","#....#",".####.","......","......"],
'v': ["......","......","......","......","#...#.","#...#.","#...#.",".#.#..","..#...","......","......"],
'w': ["......","......","......","......","#...#.","#...#.","#.#.#.","#.#.#.",".#.#..","......","......"],
'x': ["......","......","......","......","#...#.",".#.#..","..#...",".#.#..","#...#.","......","......"],
'y': ["......","......","......","......","#...#.","#...#.","#...#.",".###..","...#..","...#..","..##.."],
'z': ["......","......","......","......","######","....#.","...#..","..#...","######","......","......"],
'0': ["......",".####.","#...##","#..#.#","#.#..#","##...#","#....#","#....#",".####.","......","......"],
'1': ["......","...#..","..##..","...#..","...#..","...#..","...#..","...#..",".####.","......","......"],
'2': ["......",".####.","#....#",".....#","....#.","...#..","..#...",".#....","######","......","......"],
'3': ["......",".####.",".....#",".....#",".####.",".....#",".....#",".....#",".####.","......","......"],
'4': ["......","#...#.","#...#.","#...#.","######","....#.","....#.","....#.","....#.","......","......"],
'5': ["......","######","#.....","#####.",".....#",".....#",".....#","#....#",".####.","......","......"],
'6': ["......",".####.","#.....","#.....","#####.","#....#","#....#","#....#",".####.","......","......"],
'7': ["......","######",".....#","....#.","...#..","...#..","..#...","..#...","..#...","......","......"],
'8': ["......",".####.","#....#","#....#",".####.","#....#","#....#","#....#",".####.","......","......"],
'9': ["......",".####.","#....#","#....#","#....#",".#####",".....#",".....#",".####.","......","......"],
'.': ["......","......","......","......","......","......","......","......","..#...","......","......"],
',': ["......","......","......","......","......","......","......","......","..#...","..#...",".#...."],
':': ["......","......","......","......","..#...","......","......","..#...","......","......","......"],
';': ["......","......","......","......","..#...","......","......","..#...","..#...","..#...",".#...."],
"'": ["......","..#...","..#...","......","......","......","......","......","......","......","......"],
'-': ["......","......","......","......","......","......","#####.","......","......","......","......"],
'/': ["......",".....#","....#.","...#..","...#..","..#...","..#...",".#....","#.....","......","......"],
'(': ["......","....#.","...#..","..#...","..#...","..#...","..#...","...#..","....#.","......","......"],
')': ["......",".#....","..#...","...#..","...#..","...#..","...#..","..#...",".#....","......","......"],
'%': ["......","##..#.","##.#..","...#..","..#...","..#...",".#..##","#.##..","......","......","......"],
'!': ["......","..#...","..#...","..#...","..#...","..#...","..#...","......","..#...","......","......"],
'?': ["......",".####.","#....#",".....#","...##.","..#...","......","..#...","......","......","......"],
'&': ["......",".####.","#....#","#....#",".###..","#.#.#.","#..#.#","#...#.",".##.#.","......","......"],
'$': ["......","..#...",".####.","#.#...",".####.","..#.#.",".####.","..#...","......","......","......"],
'+': ["......","......","......","......","...#..","...#..",".#####","...#..","...#..","......","......"],
'=': ["......","......","......","......","######","......","######","......","......","......","......"],
'"': ["......",".#.#..",".#.#..","......","......","......","......","......","......","......","......"],
' ': ["......","......","......","......","......","......","......","......","......","......","......"],
}
CHAR_W = 6
CHAR_ADV = 6

# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)

def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i+1], px[i+2] = c

def rect(x, y, w, h, c):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i], px[i+1], px[i+2] = c

def hline(x, y, w, c):
    rect(x, y, w, 1, c)

def vline(x, y, h, c):
    rect(x, y, 1, h, c)

def line(x0, y0, x1, y1, c, th=1):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        rect(x, y, th, th, c)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy; x += sx
        if e2 < dx:
            err += dx; y += sy

def circle(cx, cy, r, c, fill=True):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d2 = (xx - cx) ** 2 + (yy - cy) ** 2
            if fill:
                if d2 <= r * r:
                    set_px(xx, yy, c)
            else:
                if r * r - 2 * r <= d2 <= r * r:
                    set_px(xx, yy, c)

def ellipse(cx, cy, rx, ry, c):
    for yy in range(cy - ry, cy + ry + 1):
        for xx in range(cx - rx, cx + rx + 1):
            if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1:
                set_px(xx, yy, c)

def poly(points, c):
    # scanline fill of a simple polygon
    ys = [p[1] for p in points]
    for yy in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for k in range(n):
            x0, y0 = points[k]
            x1, y1 = points[(k + 1) % n]
            if (y0 <= yy < y1) or (y1 <= yy < y0):
                xs.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            for xx in range(int(xs[k]), int(xs[k + 1]) + 1):
                set_px(xx, yy, c)

def star(cx, cy, r, c):
    # 5-point star as 10-vertex polygon
    import math
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((int(cx + rr * math.cos(ang)), int(cy + rr * math.sin(ang))))
    poly(pts, c)

# ---------------------------------------------------------------- text
def text_w(s, scale):
    return len(s) * CHAR_ADV * scale - scale

def draw_text(x, y, s, scale, c, bold=False):
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for r in range(11):
            row = g[r]
            for col in range(6):
                if row[col] == '#':
                    rect(cx + col * scale, y + r * scale, scale, scale, c)
                    if bold:
                        rect(cx + col * scale + 1, y + r * scale, scale, scale, c)
        cx += CHAR_ADV * scale
    return cx

def draw_text_centred(cx, y, s, scale, c, bold=False):
    draw_text(cx - text_w(s, scale) // 2, y, s, scale, c, bold)

def wrap(s, max_w, scale):
    words = s.split(' ')
    lines, cur = [], ''
    for wd in words:
        trial = wd if not cur else cur + ' ' + wd
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

def draw_wrapped(x, y, s, max_w, scale, c, lh, bold=False):
    lines = wrap(s, max_w, scale)
    for i, ln in enumerate(lines):
        draw_text(x, y + i * lh, ln, scale, c, bold)
    return y + len(lines) * lh


# ---------------------------------------------------------------- PNG
def chunk(typ, data):
    out = struct.pack('>I', len(data)) + typ + data
    out += struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff)
    return out

def save_png(path):
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw.extend(px[yy * W * 3:(yy + 1) * W * 3])
    data = b'\x89PNG\r\n\x1a\n'
    data += chunk(b'IHDR', ihdr)
    data += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    data += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(data)
    return len(data)

# ---------------------------------------------------------------- motifs
def globe(cx, cy, r, outline=INK, sea=LBLUE):
    """World globe: sea disc, meridian + equator, recognisable
    Africa (left-bottom) and Eurasia (top-right) continent shapes."""
    circle(cx, cy, r, sea)
    circle(cx, cy, r, outline, fill=False)
    # meridian + equator (thin dark arcs approximated by lines)
    for dx in (-r // 2, 0, r // 2):
        pass
    ellipse(cx, cy, r // 3, r, outline)  # placeholder overwritten below
    # redraw sea inside the ellipse outline trick: paint meridian as
    # vertical ellipse rings using outline pixels only
    # (ellipse() above filled; fix by repainting sea then drawing rings)
    circle(cx, cy, r - 2, sea)
    # equator
    hline(cx - r + 3, cy, 2 * r - 6, outline)
    # meridian ellipse outline: draw by sampling
    import math
    for deg in range(0, 360):
        a = math.radians(deg)
        set_px(int(cx + (r // 3) * math.cos(a)), int(cy + r * math.sin(a)), outline)
        set_px(int(cx + (2 * r // 3) * math.cos(a)), int(cy + r * math.sin(a)), outline)
    circle(cx, cy, r, outline, fill=False)
    # Africa: simplified outline (west bulge, tapering to the south)
    af = [(cx - r // 3, cy - r // 6), (cx - r // 8, cy - r // 3),
          (cx + r // 5, cy - r // 4), (cx + r // 4, cy + r // 8),
          (cx + r // 12, cy + r // 2), (cx - r // 8, cy + r // 2),
          (cx - r // 3, cy + r // 6)]
    poly(af, GREEN)
    # Eurasia: broad landmass across the top right
    eu = [(cx - r // 4, cy - r // 2 - 4), (cx + r // 4, cy - r // 2 - 10),
          (cx + r // 2 + 6, cy - r // 3), (cx + r // 2, cy - r // 6),
          (cx + r // 8, cy - r // 5), (cx - r // 8, cy - r // 3)]
    poly(eu, TEAL)
    # small island (Britain) and Arabia hint
    circle(cx + r // 3, cy - r // 6, 4, TEAL)
    circle(cx, cy - r // 2 - 2, 3, GREEN)

def thermometer(x, y, h):
    w = 22
    rect(x, y, w, h - 26, WHITE)
    rect(x, y, w, h - 26, INK)  # placeholder, repainted below
    # body: white tube with ink border
    rect(x, y, w, h - 26, WHITE)
    for xx in range(x, x + w):
        set_px(xx, y, INK); set_px(xx, y + h - 27, INK)
    for yy in range(y, y + h - 26):
        set_px(x, yy, INK); set_px(x + w - 1, yy, INK)
    # red column
    rect(x + 8, y + 18, 6, h - 44, RED)
    # bulb
    circle(x + w // 2, y + h - 16, 15, RED)
    circle(x + w // 2, y + h - 16, 15, INK, fill=False)
    # tick marks
    for k in range(4):
        yy = y + 14 + k * 14
        hline(x + w - 6, yy, 6, INK)
    draw_text(x - 2, y + h + 2, "38C", 1, RED, bold=True)

def tanker(x, y, w):
    # sea
    rect(x, y + 44, w, 12, BLUE)
    # hull
    poly([(x + 6, y + 30), (x + w - 6, y + 30), (x + w - 16, y + 46),
          (x + 16, y + 46)], INK)
    rect(x + 12, y + 18, w - 40, 12, RED)
    rect(x + w - 30, y + 8, 10, 10, GREY)
    # flame above funnel (larger, two-tone)
    poly([(x + w - 30, y + 8), (x + w - 20, y - 14), (x + w - 10, y + 8)], ORANGE)
    poly([(x + w - 26, y + 8), (x + w - 20, y - 6), (x + w - 14, y + 8)], YELLOW)

def medal(x, y, w):
    cx = x + w // 2
    # ribbons
    poly([(cx - 22, y + 4), (cx - 8, y + 4), (cx - 2, y + 26), (cx - 16, y + 26)], RED)
    poly([(cx + 22, y + 4), (cx + 8, y + 4), (cx + 2, y + 26), (cx + 16, y + 26)], BLUE)
    circle(cx, y + 40, 20, LGOLD)
    circle(cx, y + 40, 20, GOLD, fill=False)
    circle(cx, y + 40, 14, GOLD, fill=False)
    star(cx, y + 40, 11, RED)

def explosion_ship(x, y, w):
    rect(x, y + 46, w, 10, BLUE)
    poly([(x + 10, y + 34), (x + w - 10, y + 34), (x + w - 20, y + 48),
          (x + 20, y + 48)], INK)
    rect(x + w // 2 - 4, y + 22, 8, 12, GREY)
    # red/orange burst above ship: spiked star + radiating sparks
    bx, by = x + w // 2, y + 12
    star(bx, by, 20, RED)
    star(bx, by, 11, ORANGE)
    star(bx, by, 5, YELLOW)
    line(bx - 26, by - 10, bx - 14, by - 4, ORANGE, 2)
    line(bx + 26, by - 10, bx + 14, by - 4, ORANGE, 2)
    line(bx - 24, by + 12, bx - 13, by + 6, RED, 2)
    line(bx + 24, by + 12, bx + 13, by + 6, RED, 2)

def trade_ship(x, y, w):
    # Defect 2 fix: cargo ship with containers + ring of stars above.
    cx = x + w // 2
    # arch of stars above the ship (EU-style ring, upper arc only)
    import math
    for k in range(7):
        a = math.pi + k * math.pi / 6
        sx = int(cx + 50 * math.cos(a)); sy = int(y + 36 + 30 * math.sin(a))
        star(sx, sy, 5, GOLD)
    # containers
    rect(x + 22, y + 30, 26, 14, RED)
    rect(x + 52, y + 30, 26, 14, TEAL)
    rect(x + 82, y + 30, 26, 14, BLUE)
    rect(x + 36, y + 16, 26, 14, LGOLD)
    rect(x + 66, y + 16, 26, 14, GREEN)
    # hull + sea
    poly([(x + 8, y + 44), (x + w - 8, y + 44), (x + w - 20, y + 58),
          (x + 20, y + 58)], NAVY)
    rect(x, y + 58, w, 6, BLUE)

def boat_waves(x, y, w):
    # waves: solid blue sine strokes
    import math
    for k in range(3):
        for xx in range(x, x + w):
            yy = y + 46 + k * 6 + int(2 * math.sin((xx - x) / 9.0 + k * 1.7))
            rect(xx, yy, 2, 2, BLUE)
    # boat
    poly([(x + 30, y + 30), (x + w - 30, y + 30), (x + w - 44, y + 46),
          (x + 44, y + 46)], (120, 60, 30))
    line(x + w // 2, y + 30, x + w // 2, y + 8, INK, 2)
    poly([(x + w // 2 + 2, y + 8), (x + w // 2 + 2, y + 28),
          (x + w // 2 + 24, y + 28)], LBLUE)

# ---------------------------------------------------------------- page
def main():
    rect(0, 0, W, H, PAPER)
    # outer border, 16 px inset
    rect(16, 16, 992, 3, INK); rect(16, 1005, 992, 3, INK)
    rect(16, 16, 3, 992, INK); rect(1005, 16, 3, 992, INK)

    # ---- masthead
    rect(24, 24, 976, 132, NAVY)
    draw_text_centred(500, 36, "WORLD NEWS IN ONE IMAGE", 2, LGOLD)
    draw_text_centred(500, 66, "THE WORLD TODAY", 5, CREAM, bold=True)
    draw_text_centred(500, 126, "SUNDAY 22 NOVEMBER 2026", 2, LGOLD)
    globe(938, 90, 38, outline=CREAM, sea=(40, 70, 110))

    # ---- lead box
    rect(24, 168, 976, 300, WHITE)
    rect(24, 168, 976, 3, INK); rect(24, 465, 976, 3, INK)
    rect(24, 168, 3, 300, INK); rect(997, 168, 3, 300, INK)
    rect(24, 168, 10, 300, RED)
    draw_text(52, 188, "CLIMATE - ANTALYA, TURKEY", 2, RED, bold=True)
    draw_text(52, 222, "CLIMATE TALKS RUN INTO", 3, INK, bold=True)
    draw_text(52, 258, "OVERTIME AT COP31", 3, INK, bold=True)
    draw_text(52, 308, "Nations deadlocked over fossil fuels", 2, INK)
    draw_text(52, 334, "as the summit enters a second day", 2, INK)
    draw_text(52, 360, "of overtime with no final text agreed.", 2, INK)
    hline(52, 402, 620, GREY)
    draw_text(52, 420, "31ST SUMMIT - 2ND DAY OF OVERTIME - ANTALYA", 2, GREY)
    globe(830, 316, 88)
    thermometer(936, 210, 150)

    # ---- story cards
    cards = [
        ("MIDDLE EAST", RED, "IRAN STRIKES BAHRAIN SITE",
         "Tehran hits a civilian plant; two tankers struck near Hormuz.", tanker),
        ("JUSTICE", TEAL, "MEXICO CAPTURES CARTEL BOSS",
         "'El Chapo Isidro' seized; 11 killed in the raid.", medal),
        ("WAR IN EUROPE", BLUE, "RUSSIAN SHIP HIT IN BALTIC",
         "Drone sets cargo ship ablaze; missile hits Kryvyi Rih.", explosion_ship),
        ("ECONOMY", GOLD, "EU SIGNS INDONESIA DEAL",
         "Ten years of talks end in a free-trade pact.", trade_ship),
        ("DISASTER", INK, "BOAT CAPSIZES, 24 DEAD",
         "Funeral boat sinks in Bayelsa; 24 dead, 24 rescued.", boat_waves),
    ]
    xs = [24, 354, 684]
    ys = [480, 728]
    idx = 0
    for row in range(2):
        for col in range(3):
            if row == 1 and col == 2:
                break
            sec, colr, head, summ, pic = cards[idx]; idx += 1
            x, y = xs[col], ys[row]
            rect(x, y, 314, 236, WHITE)
            rect(x, y, 314, 3, INK); rect(x, y + 233, 314, 3, INK)
            rect(x, y, 3, 236, INK); rect(x + 311, y, 3, 236, INK)
            rect(x + 3, y + 3, 308, 30, colr)
            draw_text(x + 12, y + 10, sec, 2, WHITE, bold=True)
            pic(x + 12, y + 44, 290)
            # headline, wrapped, bold, scale 2
            draw_wrapped(x + 12, y + 108, head, 290, 2, INK, 24, bold=True)
            draw_wrapped(x + 12, y + 162, summ, 290, 2, INK, 22)

    # ---- briefs card (bottom right, same size as a story card)
    x, y = 684, 728
    rect(x, y, 314, 236, WHITE)
    rect(x, y, 314, 3, INK); rect(x, y + 233, 314, 3, INK)
    rect(x, y, 3, 236, INK); rect(x + 311, y, 3, 236, INK)
    rect(x + 3, y + 3, 308, 30, GREY)
    draw_text(x + 12, y + 10, "ALSO IN BRIEF", 2, WHITE, bold=True)
    draw_wrapped(x + 28, y + 48, "Iraq - Fire at Hartha power plant kills 4", 252, 2, INK, 22)
    rect(x + 12, y + 52, 8, 8, RED)
    rect(x + 12, y + 100, 8, 8, RED)
    draw_wrapped(x + 28, y + 96, "USA - FBI confirms its crime database was breached", 252, 2, INK, 22)
    # Defect 4 fix: divider + tiny globe motif + closing line at the bottom
    hline(x + 12, y + 178, 290, GREY)
    globe(x + 42, y + 202, 16, outline=INK, sea=LBLUE)
    draw_text(x + 68, y + 194, "SIX STORIES, ONE DAY.", 2, INK, bold=True)

    # ---- footer
    draw_text_centred(512, 976, "REPORTED ON SUNDAY 22 NOVEMBER 2026 - REUTERS, AP, SBS", 2, GREY)

    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "entry.png")
    size = save_png(path)
    print(path)
    print(size)

if __name__ == "__main__":
    main()
