#!/usr/bin/env python3
"""Front page of THE DAILY LEDGER for Thursday 26 November 2026.

Draws a 1024x1024 newsprint-style page and writes identical bytes to
./entry.png and ./output/entry.png.

Deterministic by construction: the date is a constant, the palette is fixed,
every coordinate is arithmetic, and there is no random, clock or network call.
Pillow is the only dependency.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

SIDE = 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")

# Palette: deep navy ground, cream type, one crimson band, amber accents.
BG = (11, 18, 32)
CREAM = (242, 235, 220)
CREAM_SOFT = (204, 196, 180)
DIM = (128, 136, 152)
RULE = (58, 68, 86)
CRIMSON = (142, 27, 27)
AMBER = (232, 163, 61)
RED = (216, 88, 76)
INK = (10, 14, 24)
STEEL = (108, 118, 136)
STEEL_DARK = (74, 84, 102)
BLUE = (38, 86, 150)
ORANGE = (188, 96, 34)
TAG_TRADE = (150, 100, 34)
TAG_ASIA = (162, 38, 38)

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


def draw_date_band(d, top, height=64):
    d.rectangle([0, top, SIDE, top + height], fill=CRIMSON)
    d.rectangle([0, top, SIDE, top + 3], fill=(180, 48, 42))
    label = "THURSDAY 26 NOVEMBER 2026"
    size = fit_size(label, SANS_BOLD, 690, 42, tracking=2.0)
    tracked(d, (24, top + 45), label, font(SANS_BOLD, size), (255, 252, 245), 2.0)
    tracked(d, (1000, top + 43), "THANKSGIVING DAY",
            font(SANS_BOLD, 19), (250, 226, 214), 1.4, anchor="r")


# --------------------------------------------------------------------------
# hero illustration: Manhattan skyline, three tethered balloons, gusts
# --------------------------------------------------------------------------

def _balloon_star(d, cx, cy, r):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.44
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=(226, 178, 72), outline=CREAM)


def _balloon_head(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(214, 96, 84), outline=CREAM)
    d.ellipse([cx - r * 0.44, cy - r * 0.34, cx - r * 0.12, cy + r * 0.00], fill=INK)
    d.ellipse([cx + r * 0.12, cy - r * 0.34, cx + r * 0.44, cy + r * 0.00], fill=INK)
    d.arc([cx - r * 0.44, cy + r * 0.04, cx + r * 0.44, cy + r * 0.58], 15, 165, fill=INK, width=3)


def _balloon_tube(d, cx, cy, w, h):
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                        radius=w / 2, fill=(92, 132, 176), outline=CREAM, width=2)
    d.line([(cx, cy - h / 2 + 8), (cx, cy + h / 2 - 8)], fill=CREAM, width=2)


def _tether(d, start, ground_y):
    """A thin line that drops from the balloon and kinks the same way, right."""
    sx, sy = start
    knee_y = sy + (ground_y - sy) * 0.58
    d.line([(sx, sy), (sx + 7, knee_y), (sx + 30, ground_y)],
           fill=(206, 198, 182), width=2)


def draw_hero_scene(d, box):
    x0, y0, x1, y1 = box
    w = x1 - x0
    h = y1 - y0
    ground = y1 - 12

    for fx, fy, fl in ((0.03, 0.06, 0.20), (0.30, 0.14, 0.19),
                       (0.62, 0.10, 0.20), (0.34, 0.52, 0.17)):
        ax = x0 + fx * w
        ay = y0 + fy * h
        d.line([(ax, ay), (ax + fl * w * 0.55, ay - 6), (ax + fl * w, ay - 2)],
               fill=(148, 160, 180), width=3)

    blocks = (
        (0.00, 0.15, 0.30, 0.10),
        (0.14, 0.13, 0.46, 0.06),
        (0.26, 0.11, 0.34, 0.05),
        (0.36, 0.15, 0.58, 0.09),
        (0.50, 0.11, 0.40, 0.05),
        (0.60, 0.14, 0.52, 0.07),
        (0.73, 0.13, 0.34, 0.05),
        (0.85, 0.15, 0.44, 0.06),
    )
    for i, (fx, fw, fh, step) in enumerate(blocks):
        bx = x0 + fx * w
        bw = fw * w
        bh = fh * h
        top = ground - bh
        d.rectangle([bx, top, bx + bw, ground], fill=STEEL_DARK)
        sw = bw * 0.5
        d.rectangle([bx + (bw - sw) / 2, top - step * h, bx + (bw + sw) / 2, top], fill=STEEL_DARK)
        rows = int(bh // 15)
        for r in range(rows):
            for c in range(3):
                if (i * 5 + r * 3 + c * 7) % 4 != 0:
                    continue
                wx = bx + 5 + c * (bw - 12) / 3.0
                wy = top + 6 + r * 15
                if wy + 5 > ground - 3:
                    continue
                d.rectangle([wx, wy, wx + 4, wy + 5], fill=(236, 196, 112))

    d.rectangle([x0, ground, x1, ground + 2], fill=(152, 160, 174))

    _tether(d, (x0 + 0.21 * w, y0 + 0.33 * h), ground)
    _tether(d, (x0 + 0.53 * w, y0 + 0.39 * h), ground)
    _tether(d, (x0 + 0.80 * w, y0 + 0.47 * h), ground)

    _balloon_star(d, x0 + 0.21 * w, y0 + 0.24 * h, 0.100 * w)
    _balloon_head(d, x0 + 0.53 * w, y0 + 0.28 * h, 0.086 * w)
    _balloon_tube(d, x0 + 0.80 * w, y0 + 0.32 * h, 0.064 * w, 0.24 * h)

    bx, by = x0 + 2, y0 + 2
    d.ellipse([bx, by, bx + 32, by + 32], fill=CRIMSON, outline=CREAM)
    d.text((bx + 16, by + 16), "100", font=font(SANS_BOLD, 12), fill=CREAM, anchor="mm")


# --------------------------------------------------------------------------
# hero panel
# --------------------------------------------------------------------------

HERO = (16, 210, 1008, 456)
HERO_DECK = (
    "Thanksgiving Day parade pushed to Saturday 28 November as a nor\u2019easter and a "
    "high-wind warning (gusts to 55 mph) ground the giant balloons \u2014 the first weather "
    "postponement in its 100-year history. The parade was only ever halted for WWII, 1942-44."
)


def draw_hero(d):
    x0, y0, x1, y1 = HERO
    d.rectangle([x0, y0, x1, y1], fill=(14, 21, 36), outline=RULE, width=2)
    d.rectangle([x0, y0, x0 + 5, y1], fill=CRIMSON)

    tx = x0 + 24
    tmax = 662
    tracked(d, (tx, y0 + 32), "UNITED STATES \u00b7 NEW YORK", font(SANS_BOLD, 20), RED, 2.4)

    size = fit_size("POSTPONED TO SATURDAY", SANS_BOLD, tmax, 58, tracking=0.5)
    head = font(SANS_BOLD, size)
    lh = int(size * 1.05)
    b1 = y0 + 32 + 16 + size
    tracked(d, (tx, b1), "MACY\u2019S 100TH PARADE", head, CREAM, 0.5)
    tracked(d, (tx, b1 + lh), "POSTPONED TO SATURDAY", head, CREAM, 0.5)

    deck_f = fit_block(HERO_DECK, SANS, tmax, 4, 19)
    dy = b1 + lh + 22
    for line in wrap(HERO_DECK, deck_f, tmax):
        d.text((tx, dy), line, font=deck_f, fill=CREAM_SOFT, anchor="ls")
        dy += int(deck_f.size * 1.24)

    draw_hero_scene(d, (x1 - 292, y0 + 10, x1 - 12, y1 - 10))
    return dy


# --------------------------------------------------------------------------
# card glyphs (64 px boxes)
# --------------------------------------------------------------------------

def g_trade(d, bx, by, s):
    u = s / 64.0
    cols = ((186, 108, 44), (150, 54, 48), (58, 96, 140))
    for r in range(2):
        for c in range(3):
            x = bx + 6 * u + c * 15 * u
            y = by + 24 * u + r * 10 * u
            d.rectangle([x, y, x + 13 * u, y + 8 * u], fill=cols[(r + c) % 3],
                        outline=(232, 226, 212))
    d.polygon([(bx + 2 * u, by + 45 * u), (bx + 62 * u, by + 45 * u),
               (bx + 53 * u, by + 58 * u), (bx + 11 * u, by + 58 * u)],
              fill=STEEL, outline=CREAM)
    d.rectangle([bx + 26 * u, by + 38 * u, bx + 38 * u, by + 45 * u], fill=STEEL_DARK)
    d.ellipse([bx + 40 * u, by + 1 * u, bx + 63 * u, by + 24 * u], fill=AMBER, outline=CREAM)
    d.text((bx + 51.5 * u, by + 12 * u), "%", font=font(SANS_BOLD, int(14 * u)), fill=INK, anchor="mm")


def g_asia(d, bx, by, s):
    u = s / 64.0
    d.polygon([(bx + 32 * u, by + 2 * u), (bx + 39 * u, by + 18 * u),
               (bx + 25 * u, by + 18 * u)], fill=CREAM)
    d.rectangle([bx + 26 * u, by + 18 * u, bx + 38 * u, by + 46 * u], fill=(206, 198, 182))
    d.rectangle([bx + 26 * u, by + 34 * u, bx + 38 * u, by + 39 * u], fill=CRIMSON)
    d.polygon([(bx + 26 * u, by + 46 * u), (bx + 14 * u, by + 58 * u), (bx + 26 * u, by + 52 * u)], fill=CREAM)
    d.polygon([(bx + 38 * u, by + 46 * u), (bx + 50 * u, by + 58 * u), (bx + 38 * u, by + 52 * u)], fill=CREAM)
    d.rectangle([bx + 30 * u, by + 46 * u, bx + 34 * u, by + 56 * u], fill=AMBER)
    cx, cy = bx + 48 * u, by + 10 * u
    r = 11 * u
    for start in (0, 120, 240):
        d.pieslice([cx - r, cy - r, cx + r, cy + r], start, start + 60, fill=AMBER)
    d.ellipse([cx - 2.6 * u, cy - 2.6 * u, cx + 2.6 * u, cy + 2.6 * u], fill=INK)


def g_europe(d, bx, by, s):
    u = s / 64.0
    towers = ((4, 30, 14, 32), (20, 20, 13, 42), (35, 26, 12, 36), (49, 14, 11, 48))
    for tx, ty, tw_, th in towers:
        d.rectangle([bx + tx * u, by + ty * u, bx + (tx + tw_) * u, by + (ty + th) * u],
                    fill=(52, 74, 110), outline=(120, 150, 190))
        for r in range(3):
            for c in range(2):
                d.rectangle([bx + (tx + 3 + c * 5) * u, by + (ty + 6 + r * 11) * u,
                             bx + (tx + 6 + c * 5) * u, by + (ty + 9 + r * 11) * u],
                            fill=(232, 198, 130))
    for off in (0, 12):
        d.line([(bx + (62 - off) * u, by + (4 + off * 0.5) * u),
                (bx + (34 - off) * u, by + (24 + off * 0.5) * u)], fill=AMBER, width=max(2, int(3 * u)))
        d.polygon([(bx + (34 - off) * u, by + (24 + off * 0.5) * u),
                   (bx + (41 - off) * u, by + (21 + off * 0.5) * u),
                   (bx + (40 - off) * u, by + (30 + off * 0.5) * u)], fill=AMBER)


def g_mideast(d, bx, by, s):
    u = s / 64.0
    d.rectangle([bx, by + 50 * u, bx + 64 * u, by + 52 * u], fill=(120, 140, 160))
    d.polygon([(bx + 4 * u, by + 38 * u), (bx + 60 * u, by + 38 * u),
               (bx + 51 * u, by + 51 * u), (bx + 13 * u, by + 51 * u)],
              fill=STEEL, outline=CREAM)
    d.rectangle([bx + 38 * u, by + 30 * u, bx + 52 * u, by + 38 * u], fill=STEEL_DARK, outline=CREAM)
    d.rectangle([bx + 42 * u, by + 22 * u, bx + 45 * u, by + 30 * u], fill=STEEL_DARK)
    d.polygon([(bx + 22 * u, by + 38 * u), (bx + 17 * u, by + 24 * u), (bx + 22 * u, by + 27 * u),
               (bx + 23 * u, by + 10 * u), (bx + 28 * u, by + 24 * u), (bx + 31 * u, by + 20 * u),
               (bx + 32 * u, by + 38 * u)], fill=(226, 122, 48))
    d.polygon([(bx + 23 * u, by + 38 * u), (bx + 23 * u, by + 20 * u), (bx + 26 * u, by + 27 * u),
               (bx + 27 * u, by + 18 * u), (bx + 29 * u, by + 38 * u)], fill=(244, 198, 96))
    cx, cy = bx + 52 * u, by + 56 * u
    d.ellipse([cx - 5 * u, cy - 5 * u, cx + 5 * u, cy + 5 * u], fill=(60, 68, 84), outline=AMBER, width=2)
    for dx, dy in ((0, -9), (0, 9), (-9, 0), (9, 0), (-6, -6), (6, -6), (-6, 6), (6, 6)):
        d.line([(cx + dx * 0.55 * u, cy + dy * 0.55 * u), (cx + dx * u, cy + dy * u)], fill=AMBER, width=2)


# --------------------------------------------------------------------------
# story cards
# --------------------------------------------------------------------------

CARDS = (
    (16, 464, "TRADE", TAG_TRADE, CREAM,
     "TARIFFS ON 14 TRADING PARTNERS",
     "US proposes duties over \u2018excess industrial capacity\u2019; up to 20% on China", g_trade),
    (520, 464, "ASIA", TAG_ASIA, CREAM,
     "KIM ORDERS WIDER TACTICAL NUKES",
     "North Korea expands nuclear material output, KCNA reports", g_asia),
    (16, 608, "EUROPE", BLUE, CREAM,
     "KYIV HIT BY BALLISTIC BARRAGE",
     "Missiles strike a shopping centre and two buildings; Zelensky presses NATO", g_europe),
    (520, 608, "MIDDLE EAST", ORANGE, CREAM,
     "TANKERS BURN IN HORMUZ",
     "Iran says two vessels hit mines in the strait and warns shipping", g_mideast),
)
CARD_W, CARD_H = 488, 136


def draw_card(d, x, y, tag, tag_col, tag_ink, headline, deck, glyph):
    d.rectangle([x, y, x + CARD_W, y + CARD_H], fill=(16, 25, 42), outline=RULE, width=2)

    chip_f = font(SANS_BOLD, 14)
    chip_w = tw(tag, chip_f, 1.8) + 20
    d.rounded_rectangle([x + 14, y + 9, x + 14 + chip_w, y + 31], radius=4, fill=tag_col)
    tracked(d, (x + 24, y + 25), tag, chip_f, tag_ink, 1.8)

    glyph(d, x + CARD_W - 80, y + 8, 64)

    text_w = CARD_W - 28 - 72
    head_f = fit_block(headline, SANS_BOLD, text_w, 2, 27)
    hy = y + 54
    for line in wrap(headline, head_f, text_w):
        tracked(d, (x + 14, hy), line, head_f, CREAM, 0.3)
        hy += int(head_f.size * 1.10)

    deck_f = fit_block(deck, SANS, CARD_W - 28, 2, 16)
    dy = y + 104
    for line in wrap(deck, deck_f, CARD_W - 28):
        d.text((x + 14, dy), line, font=deck_f, fill=CREAM_SOFT, anchor="ls")
        dy += int(deck_f.size * 1.24)
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


def draw_briefs(d, top):
    tracked(d, (16, top), "ALSO ON THE DAY", font(SANS_BOLD, 18), AMBER, 3.4)
    d.rectangle([178, top - 12, 1008, top - 11], fill=RULE)

    label_f = font(SANS_BOLD, 13)
    body_f = font(SANS_BOLD, 23)
    y = top + 32
    for label, headline in BRIEFS:
        tracked(d, (16, y), label, label_f, AMBER, 1.2)
        tracked(d, (150, y), headline, body_f, CREAM, 0.2)
        y += 32
    return y


def draw_footer(d, top):
    d.rectangle([16, top, 1008, top + 1], fill=RULE)
    f = font(SANS, 14)
    tracked(d, (16, top + 19),
            "SOURCES: REUTERS \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 KYIV INDEPENDENT \u00b7 ESA \u2014 CROSS-CHECKED",
            f, DIM, 0.6)
    tracked(d, (1008, top + 19), "make.fun \u00b7 news-image-20261126", f, AMBER, 0.6, anchor="r")


# --------------------------------------------------------------------------

def audit():
    """Re-measure every text block against its column; report any overflow.

    Returns a list of (label, used_px, limit_px) so a run proves nothing clips.
    """
    rows = []

    mast = font(SERIF_BOLD, fit_size("THE DAILY LEDGER", SERIF_BOLD, 990, 88))
    rows.append(("masthead", tw("THE DAILY LEDGER", mast), 992))

    band = font(SANS_BOLD, fit_size("THURSDAY 26 NOVEMBER 2026", SANS_BOLD, 690, 42, tracking=2.0))
    rows.append(("date band", tw("THURSDAY 26 NOVEMBER 2026", band, 2.0), 690))

    hero_head = font(SANS_BOLD, fit_size("POSTPONED TO SATURDAY", SANS_BOLD, 662, 58, tracking=0.5))
    for line in ("MACY\u2019S 100TH PARADE", "POSTPONED TO SATURDAY"):
        rows.append(("hero " + line[:12], tw(line, hero_head, 0.5), 662))

    hero_deck = fit_block(HERO_DECK, SANS, 662, 4, 19)
    for i, line in enumerate(wrap(HERO_DECK, hero_deck, 662)):
        rows.append(("hero deck l%d" % (i + 1), tw(line, hero_deck), 662))

    for x, y, tag, tag_col, tag_ink, headline, deck, glyph in CARDS:
        tw_ = CARD_W - 28 - 72
        head = fit_block(headline, SANS_BOLD, tw_, 2, 27)
        for i, line in enumerate(wrap(headline, head, tw_)):
            rows.append(("card %s h%d" % (tag, i + 1), tw(line, head, 0.3), tw_))
        body = fit_block(deck, SANS, CARD_W - 28, 2, 16)
        for i, line in enumerate(wrap(deck, body, CARD_W - 28)):
            rows.append(("card %s d%d" % (tag, i + 1), tw(line, body), CARD_W - 28))

    body = font(SANS_BOLD, 23)
    for label, headline in BRIEFS:
        rows.append(("brief " + label, tw(headline, body, 0.2), 1008 - 150))
    return rows


def render():
    img = Image.new("RGB", (SIDE, SIDE), BG)
    d = ImageDraw.Draw(img)

    rule_y = draw_head(d)
    draw_date_band(d, rule_y + 8)
    draw_hero(d)
    for x, y, tag, tag_col, tag_ink, headline, deck, glyph in CARDS:
        draw_card(d, x, y, tag, tag_col, tag_ink, headline, deck, glyph)
    draw_briefs(d, 768)
    draw_footer(d, 970)
    return img


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
