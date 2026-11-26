#!/usr/bin/env python3
"""Front page of THE DAILY LEDGER for Thursday 26 November 2026.

Draws a 1024x1024 newsprint-style page and writes identical bytes to
./entry.png and ./output/entry.png.

The lead is a full-width night scene: a three-layer Manhattan skyline under a
cold gradient sky, three giant parade balloons straining downwind on sagging
tethers, rain, gust arcs, a lamp-lit crowd with umbrellas, and the headline
sitting on a dark scrim across the lower third of the picture.

Deterministic by construction: the date is a constant, the palette is fixed,
every coordinate is arithmetic, and there is no random, clock or network call.
Pillow is the only dependency.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

SIDE = 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
LIB_DIR = "/usr/share/fonts/truetype/liberation"
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS_BOLD = os.path.join(LIB_DIR, "LiberationSans-Bold.ttf")
SANS = os.path.join(LIB_DIR, "LiberationSans-Regular.ttf")

# Palette: deep navy ground, cream type, one crimson band, amber accents.
BG = (11, 18, 32)
CREAM = (242, 235, 220)
CREAM_SOFT = (216, 208, 192)
DIM = (128, 136, 152)
RULE = (58, 68, 86)
CRIMSON = (142, 27, 27)
AMBER = (232, 163, 61)
RED = (226, 96, 84)
INK = (10, 14, 24)
STEEL = (108, 118, 136)
STEEL_DARK = (74, 84, 102)
BLUE = (38, 86, 150)
ORANGE = (188, 96, 34)
TAG_TRADE = (150, 100, 34)
TAG_ASIA = (162, 38, 38)

# Scene palette.
SKY_TOP = (12, 20, 36)
SKY_BOT = (51, 65, 94)
FAR = (80, 96, 126)
FAR_EDGE = (96, 112, 142)
MID = (26, 36, 57)
NEAR = (10, 14, 23)
WIN_MID = (226, 178, 96)
WIN_NEAR = (250, 206, 132)

MEASURE = ImageDraw.Draw(Image.new("RGB", (8, 8)))

_FONTS = {}


def font(path, size):
    key = (path, int(size))
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(path, int(size))
    return _FONTS[key]


def tw(text, fnt, tracking=0.0):
    """Width of `text` in pixels, tracking included."""
    if not text:
        return 0.0
    return MEASURE.textlength(text, font=fnt) + tracking * (len(text) - 1)


def tracked(d, xy, text, fnt, fill, tracking=0.0, anchor="l"):
    """Draw letterspaced text on a baseline; returns the width drawn."""
    total = tw(text, fnt, tracking)
    x, y = xy
    if anchor == "r":
        x -= total
    elif anchor == "c":
        x -= total / 2.0
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill, anchor="ls")
        x += MEASURE.textlength(ch, font=fnt) + tracking
    return total


def fit_size(text, path, max_w, start, floor=8, tracking=0.0):
    """Largest point size at which `text` fits inside max_w."""
    size = int(start)
    while size > floor and tw(text, font(path, size), tracking) > max_w:
        size -= 1
    return size


def wrap(text, fnt, max_w):
    """Greedy word wrap; a single over-long word is kept whole on its line."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if not cur or MEASURE.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_block(text, path, max_w, max_lines, start, floor=8):
    """Largest font whose wrapped text fits max_w within max_lines."""
    size = int(start)
    while size > floor:
        fnt = font(path, size)
        if len(wrap(text, fnt, max_w)) <= max_lines:
            return fnt
        size -= 1
    return font(path, floor)


def balanced_wrap(text, fnt, max_w, want):
    """Greedy wrap at the narrowest measure that still holds `want` lines.

    Removes the long-line/short-orphan look of a plain greedy wrap without
    touching a single word of the copy.
    """
    lines = wrap(text, fnt, max_w)
    if len(lines) >= want:
        return lines
    lo, hi, best = int(max_w * 0.40), int(max_w), max_w
    while lo <= hi:
        mid = (lo + hi) // 2
        if len(wrap(text, fnt, mid)) <= want:
            best, hi = mid, mid - 1
        else:
            lo = mid + 1
    return wrap(text, fnt, best)


def split_two(text, fnt, max_w):
    """Exact two-line split that makes the two lines as even as possible."""
    words = text.split()
    best, best_gap = None, None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        wa, wb = tw(a, fnt), tw(b, fnt)
        if wa <= max_w and wb <= max_w:
            gap = abs(wa - wb)
            if best_gap is None or gap < best_gap:
                best, best_gap = [a, b], gap
    return best if best else wrap(text, fnt, max_w)


# --------------------------------------------------------------------------
# small drawing utilities used by the scene
# --------------------------------------------------------------------------

def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def gradient(w, h, top, bottom):
    """Per-row linear interpolation, drawn one pixel wide then stretched."""
    strip = Image.new("RGB", (1, h))
    px = strip.load()
    for y in range(h):
        px[0, y] = lerp(top, bottom, y / float(max(1, h - 1)))
    return strip.resize((w, h), Image.BILINEAR)


def soft_disc(img, cx, cy, rx, ry, colour, peak, scale=4):
    """Radial falloff drawn as a mask on a small image, then pasted up."""
    sw = max(4, int(rx * 2 * scale / 4))
    sh = max(4, int(ry * 2 * scale / 4))
    mask = Image.new("L", (sw, sh))
    vals = []
    for yy in range(sh):
        dy = (yy + 0.5 - sh / 2.0) / (sh / 2.0)
        dy2 = dy * dy
        for xx in range(sw):
            dx = (xx + 0.5 - sw / 2.0) / (sw / 2.0)
            r = math.sqrt(dx * dx + dy2)
            vals.append(0 if r >= 1.0 else int(((1.0 - r) ** 2) * peak * 255))
    mask.putdata(vals)
    mask = mask.resize((max(1, int(rx * 2)), max(1, int(ry * 2))), Image.BILINEAR)
    patch = Image.new("RGBA", mask.size, colour + (255,))
    img.paste(patch, (int(cx - rx), int(cy - ry)), mask)


def vertical_ramp(w, h, colour, a_top, a_bottom):
    """A vertical alpha ramp in one colour, used for haze and soft scrims."""
    strip = Image.new("RGBA", (1, h))
    px = strip.load()
    for y in range(h):
        t = y / float(max(1, h - 1))
        px[0, y] = colour + (int(round(a_top + (a_bottom - a_top) * t)),)
    return strip.resize((w, h), Image.BILINEAR)


def bezier(p0, p1, p2, n=28):
    pts = []
    for i in range(n + 1):
        t = i / float(n)
        u = 1.0 - t
        pts.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return pts


def polyline(d, pts, fill, width=1):
    d.line([(int(x), int(y)) for x, y in pts], fill=fill, width=width, joint="curve")


def star_points(cx, cy, r, inner=0.45, phase=-math.pi / 2):
    pts = []
    for i in range(10):
        ang = phase + i * math.pi / 5
        rad = r if i % 2 == 0 else r * inner
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    return pts


# --------------------------------------------------------------------------
# masthead plate and date band
# --------------------------------------------------------------------------

def draw_head(d):
    d.rectangle([16, 10, 1008, 13], fill=AMBER)

    tracked(d, (16, 38), "THE WORLD IN ONE FRAME", font(SANS_BOLD, 19), AMBER, 4.6)

    we = font(SANS_BOLD, 20)
    we_w = tracked(d, (1008, 38), "WORLD EDITION", we, AMBER, 2.0, anchor="r")
    tracked(d, (1008 - we_w - 22, 38), "NO. 26.11.26", font(SANS, 17), CREAM_SOFT, 1.4, anchor="r")

    size = fit_size("THE DAILY LEDGER", SERIF_BOLD, 990, 88)
    mast = font(SERIF_BOLD, size)
    baseline = 46 + int(size * 0.84)
    tracked(d, (16, baseline), "THE DAILY LEDGER", mast, CREAM, 0.0)
    d.rectangle([16, baseline + 12, 1008, baseline + 13], fill=RULE)
    return baseline + 13


BAND_TOP = 141
BAND_H = 54


def draw_date_band(d, top, height=BAND_H):
    d.rectangle([0, top, SIDE, top + height], fill=CRIMSON)
    d.rectangle([0, top, SIDE, top + 2], fill=(178, 46, 40))

    label = "THURSDAY 26 NOVEMBER 2026"
    size = fit_size(label, SANS_BOLD, 660, 42, tracking=2.0)
    tracked(d, (24, top + 43), label, font(SANS_BOLD, size), (255, 252, 245), 2.0)
    tracked(d, (1000, top + 41), "THANKSGIVING DAY",
            font(SANS_BOLD, 18), (250, 226, 214), 1.4, anchor="r")


# --------------------------------------------------------------------------
# hero illustration
# --------------------------------------------------------------------------

HERO = (16, BAND_TOP + BAND_H + 8, 1008, BAND_TOP + BAND_H + 8 + 328)
SCENE_H = HERO[3] - HERO[1]
VIS = 198            # visible illustration above the scrim
SCRIM_TOP = HERO[1] + VIS
SCRIM_H = HERO[3] - SCRIM_TOP

FAR_BASE = 174
MID_BASE = 183
NEAR_BASE = 191

FAR_BLOCKS = (
    (0.000, 0.090, 72), (0.072, 0.068, 58), (0.132, 0.050, 66),
    (0.172, 0.082, 54), (0.242, 0.058, 80), (0.292, 0.086, 62),
    (0.368, 0.050, 74), (0.410, 0.080, 56), (0.480, 0.058, 68),
    (0.530, 0.090, 60), (0.610, 0.048, 78), (0.650, 0.078, 54),
    (0.720, 0.058, 70), (0.770, 0.088, 64), (0.850, 0.050, 58),
    (0.892, 0.078, 76), (0.962, 0.048, 62),
)

MID_BLOCKS = (
    (0.020, 0.070, 52), (0.098, 0.058, 44), (0.168, 0.078, 58),
    (0.256, 0.058, 40), (0.326, 0.068, 50), (0.404, 0.048, 62),
    (0.462, 0.078, 44), (0.552, 0.058, 54), (0.622, 0.068, 38),
    (0.702, 0.058, 60), (0.772, 0.078, 48), (0.862, 0.058, 42),
    (0.932, 0.058, 56),
)

NEAR_BLOCKS = (
    (0.000, 0.098, 40), (0.118, 0.068, 30), (0.198, 0.088, 44),
    (0.298, 0.058, 34), (0.376, 0.098, 38), (0.494, 0.068, 28),
    (0.574, 0.088, 46), (0.682, 0.058, 32), (0.752, 0.098, 40),
    (0.868, 0.078, 28), (0.946, 0.050, 42),
)

# (x fraction, body height, umbrella?)
CROWD = (
    (0.012, 32, 1), (0.072, 27, 0), (0.130, 35, 1), (0.192, 29, 1),
    (0.252, 33, 0), (0.310, 28, 1), (0.370, 36, 1), (0.434, 30, 0),
    (0.494, 34, 1), (0.560, 29, 1), (0.620, 32, 0), (0.682, 35, 1),
    (0.744, 28, 1), (0.804, 33, 0), (0.870, 30, 1), (0.938, 34, 1),
)


def _windows(d, x, top, w, base, lit, colour, seed, cell=6, ww=1):
    """Warm windows on an arithmetic grid."""
    cols = int((w - 6) // cell)
    rows = int((base - top - 8) // (cell + 2))
    for r in range(rows):
        for c in range(cols):
            if (seed * 7 + r * 5 + c * 3) % 11 >= lit:
                continue
            wx = x + 4 + c * cell
            wy = top + 6 + r * (cell + 2)
            if wy + ww > base - 3:
                continue
            d.rectangle([wx, wy, wx + ww, wy + ww], fill=colour)


def draw_skyline(sc, w):
    """Three flat layers, each pushed back with haze and rim light."""
    d = ImageDraw.Draw(sc)

    # far layer: pale, tall, hazy mass behind everything
    for i, (fx, fw, fh) in enumerate(FAR_BLOCKS):
        x = fx * w
        bw = fw * w
        top = FAR_BASE - fh
        d.rectangle([x, top, x + bw, FAR_BASE], fill=FAR)
        d.rectangle([x, top, x + bw, top + 1], fill=FAR_EDGE)
        if i % 4 == 1:
            d.rectangle([x + bw * 0.42, top - 6, x + bw * 0.42 + 2, top], fill=FAR_EDGE)

    # thick haze at the far layer's feet: atmospheric perspective
    sc.alpha_composite(vertical_ramp(w, 84, (56, 72, 104), 0, 96), (0, 92))

    # mid layer: navy, dim windows, cool rim
    for i, (fx, fw, fh) in enumerate(MID_BLOCKS):
        x = fx * w
        bw = fw * w
        top = MID_BASE - fh
        d.rectangle([x, top, x + bw, MID_BASE], fill=MID)
        d.rectangle([x, top, x + bw, top + 1], fill=(58, 76, 108))
        _windows(d, int(x), int(top), int(bw), MID_BASE, 2, WIN_MID, i)

    # thinner veil in front of the mid layer
    sc.alpha_composite(vertical_ramp(w, 54, (44, 58, 88), 0, 44), (0, 128))

    # near layer: near-black, warm backlit rim, a few bright windows
    for i, (fx, fw, fh) in enumerate(NEAR_BLOCKS):
        x = fx * w
        bw = fw * w
        top = NEAR_BASE - fh
        d.rectangle([x, top, x + bw, NEAR_BASE], fill=NEAR)
        d.rectangle([x, top, x + bw, top + 1], fill=(138, 106, 64))
        _windows(d, int(x), int(top), int(bw), NEAR_BASE, 2, WIN_NEAR, i + 3, ww=2)
        if i % 4 == 2:
            ax = x + bw * 0.5
            d.line([(ax, top), (ax, top - 18)], fill=(44, 40, 38), width=1)
            d.line([(ax, top - 18), (ax, top - 14)], fill=(150, 74, 58), width=1)


def draw_crowd(sc, w):
    d = ImageDraw.Draw(sc)

    # two warm lamp glows behind the crowd
    for fx in (0.205, 0.628):
        lx = fx * w
        soft_disc(sc, lx, VIS - 30, 104, 70, (188, 124, 52), 0.72)
        soft_disc(sc, lx, VIS - 34, 46, 34, (246, 190, 104), 0.72)
        d.line([(lx, VIS - 46), (lx, VIS - 2)], fill=(30, 24, 20), width=2)
        d.rectangle([lx - 5, VIS - 52, lx + 5, VIS - 44], fill=(58, 42, 28))

    for fx, bh, umb in CROWD:
        cx = fx * w
        top = VIS - bh
        d.rounded_rectangle([cx - bh * 0.21, top + bh * 0.28, cx + bh * 0.21, VIS + 2],
                            radius=bh * 0.15, fill=(3, 5, 9))
        d.ellipse([cx - bh * 0.12, top, cx + bh * 0.12, top + bh * 0.27], fill=(3, 5, 9))
        if umb:
            uw = bh * 0.62
            uy = top + bh * 0.04
            box = [cx - uw, uy - uw * 0.78, cx + uw, uy + uw * 0.78]
            d.pieslice(box, 180, 360, fill=(5, 7, 12))
            d.arc(box, 182, 358, fill=(184, 144, 96), width=2)
            d.line([(cx, uy), (cx, VIS - bh * 0.34)], fill=(9, 11, 17), width=1)

    # kerb line so the crowd is not glued to the caption block
    d.rectangle([0, VIS - 3, w, VIS - 2], fill=(52, 58, 74))


def _balloon_star(r):
    pad = int(r * 1.55)
    tile = Image.new("RGBA", (pad * 2, pad * 2), (0, 0, 0, 0))
    dt = ImageDraw.Draw(tile)
    dt.polygon(star_points(pad, pad, r), fill=(168, 34, 34), outline=(240, 232, 214))
    dt.polygon(star_points(pad, pad, r * 0.88), fill=(238, 190, 74))
    dt.polygon(star_points(pad, pad, r * 0.38), fill=(248, 216, 122))
    return tile, pad


def _balloon_head(r):
    pad = int(r * 1.55)
    tile = Image.new("RGBA", (pad * 2, pad * 2), (0, 0, 0, 0))
    dt = ImageDraw.Draw(tile)
    dt.ellipse([pad - r, pad - r * 0.92, pad + r, pad + r * 0.92],
               fill=(196, 62, 54), outline=(240, 232, 214), width=2)
    dt.ellipse([pad - r * 0.66, pad - r * 0.56, pad + r * 0.66, pad + r * 0.34],
               fill=(212, 76, 66))
    for sx in (-1, 1):
        ex = pad + sx * r * 0.34
        dt.ellipse([ex - r * 0.19, pad - r * 0.30, ex + r * 0.19, pad + r * 0.02], fill=(250, 246, 238))
        dt.ellipse([ex - r * 0.075, pad - r * 0.15, ex + r * 0.075, pad + r * 0.0], fill=(24, 20, 26))
    dt.arc([pad - r * 0.42, pad + r * 0.02, pad + r * 0.42, pad + r * 0.50],
           18, 162, fill=(250, 246, 238), width=4)
    return tile, pad


def _balloon_tube(bw, bh):
    pad = int(max(bw, bh) * 0.80)
    tile = Image.new("RGBA", (pad * 2, pad * 2), (0, 0, 0, 0))
    dt = ImageDraw.Draw(tile)
    top, bot = pad - bh / 2, pad + bh / 2
    dt.rounded_rectangle([pad - bw / 2, top, pad + bw / 2, bot],
                         radius=bw / 2, fill=(96, 142, 194), outline=(240, 232, 214), width=2)
    # lit flank
    dt.rounded_rectangle([pad - bw / 2 + 4, top + 7, pad - bw / 2 + bw * 0.34, bot - 7],
                         radius=bw * 0.17, fill=(136, 180, 222))
    # shadow flank, so it separates from the blue-grey skyline
    dt.rounded_rectangle([pad + bw / 2 - bw * 0.30, top + 7, pad + bw / 2 - 4, bot - 7],
                         radius=bw * 0.15, fill=(40, 64, 104))
    # seams, drawn as full-width bands with rounded ends
    for k in (0.24, 0.76):
        yy = top + bh * k
        dt.rectangle([pad - bw / 2 + 1, yy - 1, pad + bw / 2 - 1, yy + 1], fill=(240, 232, 214))
    # nose and tail caps
    dt.ellipse([pad - bw / 2 + 3, top + 3, pad + bw / 2 - 3, top + bw * 0.5], outline=(214, 206, 190), width=1)
    dt.ellipse([pad - bw / 2 + 3, bot - bw * 0.5, pad + bw / 2 - 3, bot - 3], outline=(214, 206, 190), width=1)
    # tail fin so it reads as a balloon and not a pill
    dt.polygon([(pad - 3, bot - 2), (pad + 3, bot - 2), (pad + 1, bot + 9), (pad - 1, bot + 9)],
               fill=(240, 232, 214))
    return tile, pad


def draw_balloons(img, w):
    """Three giant balloons, all leaning the same way, each on a sagging tether."""
    d = ImageDraw.Draw(img)

    # (centre x px, centre y px, radius, lean, tether start, hand)
    star_x, star_y, star_r = 0.212 * w, 76, 54
    head_x, head_y, head_r = 0.490 * w, 82, 48
    tube_x, tube_y = 0.792 * w, 84

    rig = (
        ((star_x, star_y + star_r - 2), (star_x - 62, 188), star_r),
        ((head_x, head_y + head_r - 2), (head_x - 58, 190), head_r),
        ((tube_x, tube_y + 64), (tube_x - 60, 186), 30),
    )
    for (bx, by), hand, half in rig:
        # harness: three short lines gathering at the balloon's base
        for off in (-half * 0.5, 0.0, half * 0.5):
            d.line([(bx + off, by - 10), (bx, by + 2)], fill=(214, 204, 186, 170), width=1)
        p2 = (hand[0], hand[1])
        mid = ((bx + p2[0]) / 2.0, (by + p2[1]) / 2.0 + 13)
        ctrl = (mid[0] - (bx - p2[0]) * 0.06, mid[1])
        polyline(d, bezier((bx, by + 2), ctrl, p2), (232, 222, 202, 205), 2)
        # gloved hand at the end of the line, on a raised arm
        d.line([(p2[0], p2[1] + 18), (p2[0], p2[1])], fill=(3, 5, 9), width=4)
        d.rounded_rectangle([p2[0] - 3, p2[1] - 10, p2[0] + 3, p2[1]], radius=3,
                            fill=(12, 14, 22))
        d.line([(p2[0] - 3, p2[1] - 10), (p2[0] + 3, p2[1] - 10)], fill=(196, 152, 104), width=1)

    for make, angle, fx, fy in (
        (lambda: _balloon_star(star_r), 13, star_x, star_y),
        (lambda: _balloon_head(head_r), 15, head_x, head_y),
        (lambda: _balloon_tube(58, 128), 15, tube_x, tube_y),
    ):
        tile, pad = make()
        tile = tile.rotate(angle, resample=Image.BICUBIC)
        img.alpha_composite(tile, (int(fx - pad), int(fy - pad)))


def draw_scene(page, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sc = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sc.paste(gradient(w, h, SKY_TOP, SKY_BOT), (0, 0))

    # amber glow low behind the skyline
    soft_disc(sc, int(w * 0.70), 176, 260, 92, (138, 90, 34), 0.66)
    soft_disc(sc, int(w * 0.24), 182, 200, 66, (128, 82, 30), 0.44)

    # gust arcs, pale blue, long and broken
    d = ImageDraw.Draw(sc)
    for ax, ay, ln, rise in ((0.02, 0.12, 0.28, 16), (0.18, 0.32, 0.30, -12),
                             (0.54, 0.18, 0.32, 14), (0.04, 0.50, 0.26, -10),
                             (0.64, 0.46, 0.30, 12)):
        p0 = (ax * w, ay * VIS)
        p1 = ((ax + ln * 0.5) * w, (ay * VIS) + rise)
        p2 = ((ax + ln) * w, (ay * VIS) + rise * 0.2)
        pts = bezier(p0, p1, p2, 40)
        for a, b in ((0, 13), (18, 28), (33, 40)):
            polyline(d, pts[a:b], (150, 174, 206, 112), 3)

    draw_skyline(sc, w)
    draw_crowd(sc, w)

    # rain, clipped above the scrim
    rain = Image.new("RGBA", (w, VIS + 4), (0, 0, 0, 0))
    dr = ImageDraw.Draw(rain)
    for i in range(48):
        rx = ((i * 197 + 41) % (w + 60)) - 30
        ry = (i * 103 + 13) % 186
        ln = 10 + (i * 7) % 9
        dr.line([(rx, ry), (rx - ln * 0.5, ry + ln * 0.87)], fill=(186, 206, 234, 58), width=1)
    sc.alpha_composite(rain, (0, 0))

    draw_balloons(sc, w)

    # crimson 100th stamp, tilted, top right
    r = 44
    pad = int(r * 1.7)
    stamp = Image.new("RGBA", (pad * 2, pad * 2), (0, 0, 0, 0))
    ds = ImageDraw.Draw(stamp)
    ds.ellipse([pad - r, pad - r, pad + r, pad + r], fill=(112, 24, 24, 240),
               outline=(226, 218, 202, 240), width=3)
    ds.ellipse([pad - r + 6, pad - r + 6, pad + r - 6, pad + r - 6],
               outline=(226, 218, 202, 110), width=2)
    ds.text((pad, pad - 1), "100th", font=font(SANS_BOLD, 21), fill=(246, 240, 228, 255), anchor="mm")
    stamp = stamp.rotate(-8, resample=Image.BICUBIC)
    sc.alpha_composite(stamp, (int(w * 0.948 - pad), int(0.150 * VIS - pad)))

    page.alpha_composite(sc, (x0, y0))


# --------------------------------------------------------------------------
# hero panel: scrim, kicker, headline, deck
# --------------------------------------------------------------------------

HERO_DECK = (
    "Thanksgiving Day parade pushed to Saturday 28 November as a nor\u2019easter and a "
    "high-wind warning (gusts to 55 mph) ground the giant balloons \u2014 the first weather "
    "postponement in its 100-year history. The parade was only ever halted for WWII, 1942-44."
)

HEAD_L1 = "MACY\u2019S 100TH PARADE"
HEAD_L2 = "POSTPONED TO SATURDAY"

HEAD_X = HERO[0] + 18
HEAD_MAX = 552
DECK_X = HERO[0] + 573
DECK_MAX = HERO[2] - DECK_X - 24
DECK_LINES = 5


def draw_hero(page):
    draw_scene(page, HERO)
    x0, y0, x1, y1 = HERO

    # scrim: the picture dissolves into the caption block over 18 px, then holds
    scrim = vertical_ramp(x1 - x0, 22, (6, 9, 16), 0, 206)
    page.alpha_composite(scrim, (x0, SCRIM_TOP))
    solid = Image.new("RGBA", (x1 - x0, SCRIM_H - 22), (6, 9, 16, 206))
    page.alpha_composite(solid, (x0, SCRIM_TOP + 22))
    d = ImageDraw.Draw(page)

    tracked(d, (HEAD_X, SCRIM_TOP + 28), "UNITED STATES \u00b7 NEW YORK",
            font(SANS_BOLD, 19), (236, 96, 74), 2.4)

    size = fit_size(HEAD_L2, SANS_BOLD, HEAD_MAX, 42, tracking=0.5)
    head = font(SANS_BOLD, size)
    lh = int(size * 1.10)
    b1 = SCRIM_TOP + 76
    tracked(d, (HEAD_X, b1), HEAD_L1, head, CREAM, 0.5)
    tracked(d, (HEAD_X, b1 + lh), HEAD_L2, head, CREAM, 0.5)

    d.rectangle([DECK_X - 14, SCRIM_TOP + 22, DECK_X - 13, SCRIM_TOP + SCRIM_H - 16], fill=(64, 72, 90))

    deck_f = fit_block(HERO_DECK, SANS, DECK_MAX, DECK_LINES, 18)
    lines = balanced_wrap(HERO_DECK, deck_f, DECK_MAX, DECK_LINES)
    lh_d = int(deck_f.size * 1.24)
    cap = int(deck_f.size * 0.72)
    total = (len(lines) - 1) * lh_d + cap
    dy = SCRIM_TOP + 22 + max(0, (SCRIM_H - 22 - total) // 2) + cap
    for line in lines:
        d.text((DECK_X, dy), line, font=deck_f, fill=(216, 209, 196), anchor="ls")
        dy += lh_d
    return b1 + lh


# --------------------------------------------------------------------------
# card mini-scenes (drawn on a 64-unit grid, scaled to `s`)
# --------------------------------------------------------------------------

def _horizon(d, bx, by, u, y, alpha=70):
    d.line([(bx + 2 * u, by + y * u), (bx + 62 * u, by + y * u)],
           fill=(96, 112, 140, alpha), width=max(1, int(u)))


def g_trade(d, bx, by, s):
    u = s / 64.0
    _horizon(d, bx, by, u, 34)
    d.rectangle([bx, by + 52 * u, bx + 64 * u, by + 64 * u], fill=(16, 24, 38))
    cols = ((186, 108, 44), (150, 54, 48), (58, 96, 140))
    for r in range(2):
        for c in range(3):
            x = bx + 8 * u + c * 15 * u
            y = by + 24 * u + r * 10 * u
            d.rectangle([x, y, x + 13 * u, y + 8 * u], fill=cols[(r + c) % 3],
                        outline=(232, 226, 212))
    d.polygon([(bx + 4 * u, by + 45 * u), (bx + 60 * u, by + 45 * u),
               (bx + 52 * u, by + 56 * u), (bx + 12 * u, by + 56 * u)],
              fill=STEEL, outline=CREAM)
    d.rectangle([bx + 27 * u, by + 38 * u, bx + 37 * u, by + 45 * u], fill=STEEL_DARK)
    d.ellipse([bx + 39 * u, by + 1 * u, bx + 63 * u, by + 25 * u], fill=AMBER, outline=CREAM)
    d.text((bx + 51 * u, by + 13 * u), "%", font=font(SANS_BOLD, int(15 * u)), fill=INK, anchor="mm")


def g_asia(d, bx, by, s):
    u = s / 64.0
    d.rectangle([bx, by + 48 * u, bx + 64 * u, by + 64 * u], fill=(12, 17, 28))
    _horizon(d, bx, by, u, 48, 90)
    # contrail arc over the horizon
    d.arc([bx + 20 * u, by + 30 * u, bx + 62 * u, by + 58 * u], 300, 20,
          fill=(168, 188, 214), width=max(2, int(2 * u)))
    d.arc([bx + 26 * u, by + 36 * u, bx + 56 * u, by + 54 * u], 300, 20,
          fill=(120, 140, 170), width=1)
    # missile
    d.polygon([(bx + 33 * u, by + 3 * u), (bx + 40 * u, by + 20 * u),
               (bx + 26 * u, by + 20 * u)], fill=CREAM)
    d.rectangle([bx + 27 * u, by + 20 * u, bx + 39 * u, by + 45 * u], fill=(206, 198, 182))
    d.rectangle([bx + 27 * u, by + 32 * u, bx + 39 * u, by + 37 * u], fill=CRIMSON)
    d.polygon([(bx + 27 * u, by + 45 * u), (bx + 14 * u, by + 56 * u), (bx + 27 * u, by + 51 * u)], fill=CREAM)
    d.polygon([(bx + 39 * u, by + 45 * u), (bx + 52 * u, by + 56 * u), (bx + 39 * u, by + 51 * u)], fill=CREAM)
    d.rectangle([bx + 31 * u, by + 45 * u, bx + 35 * u, by + 55 * u], fill=AMBER)
    # trefoil, top left
    cx, cy, r = bx + 13 * u, by + 13 * u, 9.5 * u
    for start in (0, 120, 240):
        d.pieslice([cx - r, cy - r, cx + r, cy + r], start, start + 60, fill=AMBER)
    d.ellipse([cx - 2.4 * u, cy - 2.4 * u, cx + 2.4 * u, cy + 2.4 * u], fill=INK)


def g_europe(d, bx, by, s):
    u = s / 64.0
    d.rectangle([bx, by + 52 * u, bx + 64 * u, by + 64 * u], fill=(16, 24, 38))
    _horizon(d, bx, by, u, 52, 70)
    towers = ((2, 32, 13, 22), (17, 22, 12, 32), (31, 28, 11, 26), (44, 16, 10, 38), (56, 34, 8, 20))
    for tx, ty, tw_, th in towers:
        d.rectangle([bx + tx * u, by + ty * u, bx + (tx + tw_) * u, by + (ty + th) * u],
                    fill=(52, 74, 110), outline=(120, 150, 190))
        for r in range(2):
            for c in range(2):
                d.rectangle([bx + (tx + 2.5 + c * 5) * u, by + (ty + 4 + r * 9) * u,
                             bx + (tx + 5 + c * 5) * u, by + (ty + 7 + r * 9) * u],
                            fill=(232, 198, 130))
    # smoke plume off the tallest block
    for i, (sx, sy, sr) in enumerate(((50, 10, 5), (53, 4, 6), (58, -1, 5))):
        d.ellipse([bx + (sx - sr) * u, by + (sy - sr) * u, bx + (sx + sr) * u, by + (sy + sr) * u],
                  fill=(126 + i * 14, 134 + i * 14, 148 + i * 14))
    # two missile streaks
    for off in (0, 13):
        d.line([(bx + (62 - off) * u, by + (2 + off * 0.6) * u),
                (bx + (36 - off) * u, by + (22 + off * 0.6) * u)],
               fill=AMBER, width=max(2, int(3 * u)))
        d.polygon([(bx + (36 - off) * u, by + (22 + off * 0.6) * u),
                   (bx + (43 - off) * u, by + (19 + off * 0.6) * u),
                   (bx + (42 - off) * u, by + (28 + off * 0.6) * u)], fill=AMBER)


def g_mideast(d, bx, by, s):
    u = s / 64.0
    d.rectangle([bx, by + 44 * u, bx + 64 * u, by + 64 * u], fill=(14, 26, 42))
    for yy in (50, 58):
        d.line([(bx + 4 * u, by + yy * u), (bx + 20 * u, by + yy * u)], fill=(70, 98, 130), width=1)
        d.line([(bx + 30 * u, by + yy * u), (bx + 48 * u, by + yy * u)], fill=(70, 98, 130), width=1)
    d.polygon([(bx + 4 * u, by + 38 * u), (bx + 60 * u, by + 38 * u),
               (bx + 51 * u, by + 47 * u), (bx + 13 * u, by + 47 * u)],
              fill=STEEL, outline=CREAM)
    d.rectangle([bx + 38 * u, by + 30 * u, bx + 52 * u, by + 38 * u], fill=STEEL_DARK, outline=CREAM)
    d.rectangle([bx + 42 * u, by + 22 * u, bx + 45 * u, by + 30 * u], fill=STEEL_DARK)
    d.polygon([(bx + 22 * u, by + 38 * u), (bx + 17 * u, by + 24 * u), (bx + 22 * u, by + 27 * u),
               (bx + 23 * u, by + 10 * u), (bx + 28 * u, by + 24 * u), (bx + 31 * u, by + 20 * u),
               (bx + 32 * u, by + 38 * u)], fill=(226, 122, 48))
    d.polygon([(bx + 23 * u, by + 38 * u), (bx + 23 * u, by + 20 * u), (bx + 26 * u, by + 27 * u),
               (bx + 27 * u, by + 18 * u), (bx + 29 * u, by + 38 * u)], fill=(244, 198, 96))
    cx, cy = bx + 54 * u, by + 55 * u
    d.ellipse([cx - 4.6 * u, cy - 4.6 * u, cx + 4.6 * u, cy + 4.6 * u],
              fill=(60, 68, 84), outline=AMBER, width=2)
    for dx, dy in ((0, -8), (0, 8), (-8, 0), (8, 0), (-5.5, -5.5), (5.5, -5.5), (-5.5, 5.5), (5.5, 5.5)):
        d.line([(cx + dx * 0.55 * u, cy + dy * 0.55 * u), (cx + dx * u, cy + dy * u)], fill=AMBER, width=2)


# --------------------------------------------------------------------------
# story cards
# --------------------------------------------------------------------------

CARDS = (
    (16, 535, "TRADE", TAG_TRADE, CREAM,
     "TARIFFS ON 14 TRADING PARTNERS",
     "US proposes duties over \u2018excess industrial capacity\u2019; up to 20% on China", g_trade),
    (520, 535, "ASIA", TAG_ASIA, CREAM,
     "KIM ORDERS WIDER TACTICAL NUKES",
     "North Korea expands nuclear material output, KCNA reports", g_asia),
    (16, 661, "EUROPE", BLUE, CREAM,
     "KYIV HIT BY BALLISTIC BARRAGE",
     "Missiles strike a shopping centre and two buildings; Zelensky presses NATO", g_europe),
    (520, 661, "MIDDLE EAST", ORANGE, CREAM,
     "TANKERS BURN IN HORMUZ",
     "Iran says two vessels hit mines in the strait and warns shipping", g_mideast),
)
CARD_W, CARD_H = 488, 120
GLYPH = 76


def draw_card(d, x, y, tag, tag_col, tag_ink, headline, deck, glyph):
    d.rectangle([x, y, x + CARD_W, y + CARD_H], fill=(16, 25, 42), outline=RULE, width=2)

    chip_f = font(SANS_BOLD, 13)
    chip_w = tw(tag, chip_f, 1.8) + 20
    d.rounded_rectangle([x + 14, y + 9, x + 14 + chip_w, y + 29], radius=4, fill=tag_col)
    tracked(d, (x + 24, y + 24), tag, chip_f, tag_ink, 1.8)

    glyph(d, x + CARD_W - 8 - GLYPH, y + 8, GLYPH)

    text_w = CARD_W - 14 - 8 - GLYPH - 14
    head_f = fit_block(headline, SANS_BOLD, text_w, 2, 26)
    hy = y + 52
    for line in split_two(headline, head_f, text_w):
        tracked(d, (x + 14, hy), line, head_f, CREAM, 0.3)
        hy += int(head_f.size * 1.06)

    deck_f = fit_block(deck, SANS, CARD_W - 34, 2, 16)
    dy = y + 95
    for line in split_two(deck, deck_f, CARD_W - 34):
        d.text((x + 14, dy), line, font=deck_f, fill=(220, 212, 198), anchor="ls")
        dy += int(deck_f.size * 1.10)
    return hy, dy


# --------------------------------------------------------------------------
# also on the day
# --------------------------------------------------------------------------

BRIEFS = (
    ("EGYPT", "31 KILLED IN FUEL-TRUCK FIRE ON CAIRO RING ROAD"),
    ("SPACE", "HERA FINDS STADIUM-SIZED CRATER ON ASTEROID DIMORPHOS"),
    ("BANGLADESH", "GARMENT WAGE RAISED 36% TO 17,000 TAKA AFTER PROTESTS"),
    ("BRAZIL", "FLOODS AND LANDSLIDES KILL AT LEAST 8 IN THE SOUTH"),
    ("SAUDI ARABIA", "HOUTHI PROJECTILE HITS JAZAN PORT, COALITION SAYS"),
    ("CULTURE", "DURAN DURAN GUITARIST ANDY TAYLOR DIES AT 65"),
)
BRIEF_TOP = 810
BRIEF_PITCH = 26
BRIEF_X = 152
BRIEF_F = 25


def draw_briefs(d, top):
    tracked(d, (16, top), "ALSO ON THE DAY", font(SANS_BOLD, 18), AMBER, 3.4)
    d.rectangle([178, top - 12, 1008, top - 11], fill=RULE)

    label_f = font(SANS_BOLD, 14)
    body_f = font(SANS_BOLD, BRIEF_F)
    first = top + 30
    for i in range(len(BRIEFS)):
        if i % 2 == 1:
            y = first + i * BRIEF_PITCH
            d.rectangle([10, y - 19, SIDE - 10, y + 5], fill=(20, 27, 41))
    for i in range(1, len(BRIEFS)):
        y = first + i * BRIEF_PITCH - 19
        d.rectangle([10, y, SIDE - 10, y + 1], fill=(38, 48, 68))
    d.rectangle([140, first - 18, 141, first + (len(BRIEFS) - 1) * BRIEF_PITCH + 5], fill=RULE)
    y = first
    for label, headline in BRIEFS:
        tracked(d, (16, y), label, label_f, AMBER, 1.2)
        tracked(d, (BRIEF_X, y), headline, body_f, (228, 221, 207), 0.2)
        y += BRIEF_PITCH
    return y


def draw_footer(d, top):
    d.rectangle([16, top, 1008, top + 1], fill=RULE)
    f = font(SANS, 14)
    tracked(d, (16, top + 19),
            "SOURCES: REUTERS \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 KYIV INDEPENDENT \u00b7 ESA \u2014 CROSS-CHECKED",
            f, DIM, 0.6)
    tracked(d, (1008, top + 19), "make.fun \u00b7 news-image-20261126", f, AMBER, 0.6, anchor="r")


# --------------------------------------------------------------------------
# print texture
# --------------------------------------------------------------------------

def grain_tile(n=64):
    """A fixed arithmetic dot pattern, tiled over the page at a few percent."""
    tile = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    px = tile.load()
    for y in range(n):
        for x in range(n):
            v = (x * 13 + y * 29 + (x * y) * 7) % 101
            if v < 11:
                px[x, y] = (255, 252, 244, 17)
            elif v > 91:
                px[x, y] = (0, 0, 0, 13)
    return tile


def apply_grain(page):
    tile = grain_tile()
    layer = Image.new("RGBA", page.size, (0, 0, 0, 0))
    for ty in range(0, SIDE, tile.size[1]):
        for tx in range(0, SIDE, tile.size[0]):
            layer.alpha_composite(tile, (tx, ty))
    page.alpha_composite(layer)


def apply_halftone(page, top, height):
    layer = Image.new("RGBA", (SIDE, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for row, y in enumerate(range(3, height - 2, 6)):
        off = 0 if row % 2 == 0 else 3
        for x in range(off, SIDE, 6):
            d.ellipse([x, y, x + 1, y + 1], fill=(255, 238, 228, 20))
    page.alpha_composite(layer, (0, top))


# --------------------------------------------------------------------------
# layout audit
# --------------------------------------------------------------------------

def audit():
    """Re-measure every text block against its column; report any overflow."""
    rows = []

    mast = font(SERIF_BOLD, fit_size("THE DAILY LEDGER", SERIF_BOLD, 990, 88))
    rows.append(("masthead", tw("THE DAILY LEDGER", mast), 992))

    band = font(SANS_BOLD, fit_size("THURSDAY 26 NOVEMBER 2026", SANS_BOLD, 660, 42, tracking=2.0))
    rows.append(("date band", tw("THURSDAY 26 NOVEMBER 2026", band, 2.0), 660))
    rows.append(("thanksgiving", tw("THANKSGIVING DAY", font(SANS_BOLD, 18), 1.4), 300))

    head = font(SANS_BOLD, fit_size(HEAD_L2, SANS_BOLD, HEAD_MAX, 42, tracking=0.5))
    for line in (HEAD_L1, HEAD_L2):
        rows.append(("hero " + line[:12], tw(line, head, 0.5), HEAD_MAX))

    deck_f = fit_block(HERO_DECK, SANS, DECK_MAX, DECK_LINES, 18)
    for i, line in enumerate(balanced_wrap(HERO_DECK, deck_f, DECK_MAX, DECK_LINES)):
        rows.append(("hero deck l%d" % (i + 1), tw(line, deck_f), DECK_MAX))

    for x, y, tag, tag_col, tag_ink, headline, deck, glyph in CARDS:
        text_w = CARD_W - 14 - 8 - GLYPH - 14
        head_c = fit_block(headline, SANS_BOLD, text_w, 2, 26)
        for i, line in enumerate(split_two(headline, head_c, text_w)):
            rows.append(("card %s h%d" % (tag, i + 1), tw(line, head_c, 0.3), text_w))
        body = fit_block(deck, SANS, CARD_W - 34, 2, 16)
        for i, line in enumerate(split_two(deck, body, CARD_W - 34)):
            rows.append(("card %s d%d" % (tag, i + 1), tw(line, body), CARD_W - 34))

    body = font(SANS_BOLD, BRIEF_F)
    label = font(SANS_BOLD, 14)
    for tag, headline in BRIEFS:
        rows.append(("brief " + tag, tw(headline, body, 0.2), 1008 - BRIEF_X))
        rows.append(("label " + tag, 16 + tw(tag, label, 1.2), 132))

    f = font(SANS, 14)
    src = tw("SOURCES: REUTERS \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 KYIV INDEPENDENT \u00b7 ESA \u2014 CROSS-CHECKED", f, 0.6)
    mark = tw("make.fun \u00b7 news-image-20261126", f, 0.6)
    rows.append(("footer left", src, 1008 - 16 - mark - 30))
    rows.append(("footer right", mark, 400))
    return rows


def vertical_checks():
    """Bands must not collide; type must stay inside its own panel."""
    checks = []
    band_bottom = BAND_TOP + BAND_H
    checks.append(("hero below band", band_bottom + 8, HERO[1]))
    checks.append(("cards below hero", HERO[3] + 4, CARDS[0][1]))
    checks.append(("cards row2 gap", CARDS[0][1] + CARD_H + 4, CARDS[2][1]))
    checks.append(("briefs below cards", CARDS[2][1] + CARD_H + 8, BRIEF_TOP - 13))
    last_brief = BRIEF_TOP + 30 + (len(BRIEFS) - 1) * BRIEF_PITCH
    checks.append(("footer below briefs", last_brief + 10, 980))
    checks.append(("footer in page", 980 + 19 + 4, SIDE))

    head = font(SANS_BOLD, fit_size(HEAD_L2, SANS_BOLD, HEAD_MAX, 42, tracking=0.5))
    head_bottom = SCRIM_TOP + 76 + int(head.size * 1.10)
    checks.append(("headline above scrim floor", head_bottom + 6, HERO[3]))
    checks.append(("kicker inside scrim", SCRIM_TOP + 28, SCRIM_TOP + 76 - head.size))

    deck_c = fit_block(HERO_DECK, SANS, DECK_MAX, DECK_LINES, 18)
    dlines = balanced_wrap(HERO_DECK, deck_c, DECK_MAX, DECK_LINES)
    lh_d = int(deck_c.size * 1.24)
    cap_c = int(deck_c.size * 0.72)
    total = (len(dlines) - 1) * lh_d + cap_c
    d_top = SCRIM_TOP + 22 + max(0, (SCRIM_H - 22 - total) // 2)
    checks.append(("deck starts on solid scrim", SCRIM_TOP + 22, d_top))
    checks.append(("deck inside scrim", d_top + total, SCRIM_TOP + SCRIM_H - 4))

    for x, y, tag, tag_col, tag_ink, headline, deck, glyph in CARDS:
        body = fit_block(deck, SANS, CARD_W - 34, 2, 16)
        lines = split_two(deck, body, CARD_W - 34)
        deck_bottom = y + 95 + (len(lines) - 1) * int(body.size * 1.10) + 4
        checks.append(("card %s deck floor" % tag, deck_bottom, y + CARD_H - 3))
        text_w = CARD_W - 14 - 8 - GLYPH - 14
        head_c = fit_block(headline, SANS_BOLD, text_w, 2, 26)
        hl = len(split_two(headline, head_c, text_w))
        head_bottom = y + 52 + (hl - 1) * int(head_c.size * 1.06)
        checks.append(("card %s head/deck gap" % tag, head_bottom + 6, y + 95 - 8))
    return checks


# --------------------------------------------------------------------------

def render():
    page = Image.new("RGBA", (SIDE, SIDE), BG + (255,))
    d = ImageDraw.Draw(page)

    rule_y = draw_head(d)
    draw_date_band(d, BAND_TOP)
    draw_hero(page)
    d = ImageDraw.Draw(page)
    for x, y, tag, tag_col, tag_ink, headline, deck, glyph in CARDS:
        draw_card(d, x, y, tag, tag_col, tag_ink, headline, deck, glyph)
    draw_briefs(d, BRIEF_TOP)
    draw_footer(d, 980)

    apply_halftone(page, BAND_TOP, BAND_H)
    apply_grain(page)
    return page.convert("RGB")


def main():
    img = render()
    rows = audit()
    overflow = [r for r in rows if r[1] > r[2]]
    worst = max(rows, key=lambda r: r[1] / r[2] if r[2] else 0)
    for label, used, limit in overflow:
        print("OVERFLOW %-22s %6.1f > %6.1f" % (label, used, limit))
    if overflow:
        raise SystemExit("%d text block(s) overflow their column" % len(overflow))
    print("text audit: %d blocks fit, tightest %s at %.0f/%.0f px"
          % (len(rows), worst[0], worst[1], worst[2]))

    checks = vertical_checks()
    bad = [c for c in checks if c[1] > c[2]]
    for label, used, limit in bad:
        print("COLLISION %-26s %6.1f > %6.1f" % (label, used, limit))
    if bad:
        raise SystemExit("%d layout band(s) collide" % len(bad))
    print("layout audit: %d bands clear" % len(checks))

    root = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(root, "output")
    os.makedirs(out_dir, exist_ok=True)
    main_path = os.path.join(root, "entry.png")
    img.save(main_path, format="PNG", optimize=True)
    with open(main_path, "rb") as fh:
        blob = fh.read()
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(blob)
    print("wrote entry.png and output/entry.png: %d bytes, %dx%d"
          % (len(blob), img.size[0], img.size[1]))


if __name__ == "__main__":
    main()
