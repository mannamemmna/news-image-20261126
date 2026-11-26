#!/usr/bin/env python3
"""Front page of THE DAILY LEDGER for Thursday 26 November 2026.

A classic LIGHT newsprint broadsheet: cream paper, black ink, one red spot
colour and a single accent blue.  The page packs the day's whole news
budget — a lead story with a drawn ink-and-red scene, six column stories,
and a three-column "day in brief" strip of eighteen one-line items.

Everything sits on one strict grid.  `plan()` measures every string with
draw.textlength and fixes every baseline BEFORE a pixel is drawn, and the
audits re-check that same plan, so the drawing and the checking can never
disagree and the run refuses to save on any overflow or collision.
No rounded cards, no dark panels, no gradients.

Deterministic by construction: the date is a constant, the palette is
fixed, every coordinate is arithmetic, and there is no random, clock or
network call.  Pillow is the only dependency.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

SIDE = 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")

# Palette: cream newsprint, black ink, muted rule, one red spot, one blue.
PAPER = (244, 239, 227)          # F4EFE3
INK = (21, 22, 26)               # 15161A
MUTED = (138, 133, 119)          # 8A8577
RED = (179, 38, 30)              # B3261E
BLUE = (47, 79, 111)             # 2F4F6F
SOFT = (63, 64, 68)              # body-copy grey-black
FAINT = (210, 203, 186)          # hairline between brief items

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


def wrap(text, fnt, max_w, tracking=0.0):
    """Greedy word wrap that honours letterspacing.

    A single over-long word is kept whole, except that a word carrying
    hyphens may break after a hyphen — the broadsheet convention — so
    compounds such as STADIUM-SIZED or 3,000-TROOP set in a narrow
    column without clipping.
    """
    def w(s):
        return MEASURE.textlength(s, font=fnt) + tracking * max(0, len(s) - 1)

    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if not cur or w(trial) <= max_w:
            cur = trial
            continue
        if w(word) > max_w and "-" in word[:-1]:
            parts, seg = [], ""
            for piece in word.split("-"):
                cand = piece + "-" if seg == "" else seg + "-" + piece
                if seg and w(cand) > max_w:
                    parts.append(seg + "-")
                    seg = piece
                else:
                    seg = cand
            parts.append(seg)
            lines.append(cur)
            cur = parts[0]
            for p in parts[1:-1]:
                lines.append(p)
            continue
        lines.append(cur)
        cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_block(text, path, max_w, max_lines, start, floor=8, tracking=0.0):
    """Largest font whose wrapped text fits max_w within max_lines."""
    size = int(start)
    while size > floor:
        fnt = font(path, size)
        if len(wrap(text, fnt, max_w, tracking)) <= max_lines:
            return fnt
        size -= 1
    return font(path, floor)


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
# page geometry: one strict grid, four horizontal bands
# --------------------------------------------------------------------------

ML, MR = 14, 1010                 # page margins (left ink edge, right ink edge)

LEAD_TOP = 186
LEAD_BOT = 486
COL_TOP = 496
COL_BOT = 686
BRIEF_TOP = 696
BRIEF_BOT = 958
FOOT_RULE = 970

DIV_X = 646                       # hairline between lead text and the scene
TEXT_L, TEXT_R = ML, 630          # lead text column
SCENE_L, SCENE_R = 662, MR        # lead illustration box

N_COLS = 6
GUT = 10
COL_W = (MR - ML - (N_COLS - 1) * GUT) / N_COLS            # ~156.7
COL_XS = tuple(ML + i * (COL_W + GUT) for i in range(N_COLS))
COL_DIV = tuple(ML + (i + 1) * COL_W + i * GUT + GUT / 2.0 for i in range(N_COLS - 1))

N_BRIEF_COLS = 3
BGUT = 14
BRIEF_W = (MR - ML - (N_BRIEF_COLS - 1) * BGUT) / N_BRIEF_COLS      # ~322.7
BRIEF_XS = tuple(ML + i * (BRIEF_W + BGUT) for i in range(N_BRIEF_COLS))
BRIEF_DIV = tuple(ML + (i + 1) * BRIEF_W + i * BGUT + BGUT / 2.0
                  for i in range(N_BRIEF_COLS - 1))

FLAG_LINE = "THE WORLD IN ONE FRAME \u00b7 WORLD EDITION \u00b7 NO. 26.11.26"
DATE_LINE = "THURSDAY 26 NOVEMBER 2026"
XMAS_LINE = "THANKSGIVING DAY \u00b7 26.11.2026"

# --------------------------------------------------------------------------
# text package (the only facts allowed on this page)
# --------------------------------------------------------------------------

LEAD_KICKER = "NEW YORK \u00b7 THE PARADE THAT WAITED"
LEAD_HEAD = "MACY\u2019S 100TH PARADE POSTPONED TO SATURDAY"
LEAD_DECK = (
    "A nor\u2019easter and a high-wind warning with gusts to 55 mph grounded the giant "
    "balloons, so the Thanksgiving Day parade moves to Saturday 28 November \u2014 the "
    "first weather postponement in its 100-year history. It was halted only for "
    "WWII, 1942-44."
)
LEAD_P1 = (
    "The parade will now march on Saturday 28 November, one day after "
    "Thanksgiving Day, 26.11.2026. The giant balloons stayed grounded: a "
    "nor\u2019easter arrived with a high-wind warning, gusts to 55 mph."
)
LEAD_P2 = (
    "It is the first weather postponement in the parade\u2019s 100-year history. "
    "In all that time the parade was halted only for WWII, 1942-44. The 100th "
    "edition had been set for New York on Thanksgiving Day itself."
)

CARDS = (
    ("TRADE", RED,
     "US PROPOSES TARIFFS ON 14 TRADING PARTNERS",
     "Duties over what Washington calls structural excess industrial capacity. "
     "Up to 20% on China, 25% on India, 17% if a deal is struck. World stocks "
     "slid as the AI rally faded.",
     "Reuters \u00b7 RNZ \u00b7 SBS \u00b7 Business Standard"),
    ("ASIA", BLUE,
     "KIM ORDERS WIDER TACTICAL NUCLEAR DEPLOYMENT",
     "Kim Jong Un inspected nuclear material production and weapons research "
     "facilities and said the country should deploy tactical nuclear weapons "
     "across multiple domains.",
     "Reuters \u00b7 KCNA"),
    ("EUROPE", BLUE,
     "KYIV HIT BY BALLISTIC MISSILES",
     "The strike late on Wednesday hit a shopping centre and two other "
     "buildings; three people were injured, one seriously. Zelensky pressed "
     "NATO on membership.",
     "Reuters \u00b7 Kyiv Independent \u00b7 Ukrinform"),
    ("MIDDLE EAST", RED,
     "TANKERS BURN IN THE STRAIT OF HORMUZ",
     "Iran\u2019s Revolutionary Guards said an LNG carrier and an oil tanker "
     "caught fire after hitting naval mines. Tehran warned shipping to "
     "follow its instructions.",
     "Reuters \u00b7 Arab News \u00b7 Gulf News"),
    ("AFRICA", RED,
     "EGYPT FIRE KILLS 31 ON CAIRO RING ROAD",
     "A vehicle carrying petroleum products overturned and caught fire. "
     "21 people were wounded.",
     "Reuters \u00b7 AP"),
    ("SCIENCE", BLUE,
     "HERA FINDS A STADIUM-SIZED CRATER ON DIMORPHOS",
     "ESA released the first images from its Hera probe, showing the crater "
     "left by NASA\u2019s 2022 DART impact across the asteroid\u2019s whole "
     "width. Dimorphos is tumbling.",
     "ESA \u00b7 CNN \u00b7 Ars Technica \u00b7 Sci. Am."),
)

BRIEFS = (
    ("US", "SECOND JUDGE BLOCKS BIRTHRIGHT CITIZENSHIP ORDER"),
    ("US", "SENATE DEMOCRAT QUESTIONS NVIDIA ON HUANG\u2019S RETURN"),
    ("EU", "RUSSIA\u2019S MURMANSK GOVERNOR HELD ON CORRUPTION CHARGES"),
    ("EU", "34 COUNTRIES URGE RUSSIA TO STOP USING RIOT GAS"),
    ("EU", "ITALY: NEARLY 60 PRIESTS JAILED FOR ABUSE, REPORT SAYS"),
    ("EU", "BULGARIA INTERCEPTS FIRST MIGRANT BOAT IN MONTHS"),
    ("ME", "HOUTHI PROJECTILE HITS JAZAN PORT, COALITION SAYS"),
    ("ME", "IS ATTACK KILLS TWO SYRIAN SECURITY PERSONNEL"),
    ("ME", "IRAN SAYS IT CAN WITHSTAND A US NAVAL BLOCKADE"),
    ("AF", "BANGLADESH RAISES GARMENT WAGE 36% TO 17,000 TAKA"),
    ("AF", "NIGERIA: GUNMEN KILL AT LEAST 30 IN NIGER STATE"),
    ("AF", "KENYA CULT LEADER CONVICTED ON NEW CHARGES"),
    ("AS", "N KOREA EXPELS SWISS ENVOY OVER SANCTIONS"),
    ("AS", "CHINA JOINS 3,000-TROOP DRILLS IN CAMBODIA"),
    ("LA", "BRAZIL FLOODS AND LANDSLIDES KILL AT LEAST 8"),
    ("LA", "ECUADOR AND US REVIEW JOINT OPERATIONS"),
    ("CU", "DURAN DURAN GUITARIST ANDY TAYLOR DIES AT 65"),
    ("SP", "SINDAROV AND GUKESH DRAW GAME 2 OF TITLE MATCH"),
)

FOOT_SRC = ("SOURCES: REUTERS \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 KYIV INDEPENDENT "
            "\u00b7 ESA \u00b7 UPI \u00b7 AL JAZEERA \u2014 EVERY ITEM CROSS-CHECKED "
            "IN TWO OUTLETS")
FOOT_MARK = "make.fun \u00b7 news-image-20261126"


# --------------------------------------------------------------------------
# the plan: every box measured before anything is drawn
# --------------------------------------------------------------------------

def plan():
    p = {}

    # masthead band ---------------------------------------------------------
    p["flag_base"] = 28
    p["mast_size"] = fit_size("THE DAILY LEDGER", SERIF_BOLD, MR - ML, 104, 60)
    p["mast_base"] = 116
    p["rule1"] = 124
    p["rule2"] = 131
    p["date_size"] = 46
    p["date_base"] = 170
    p["flag_rule"] = 179

    # lead text -------------------------------------------------------------
    p["kick_base"] = LEAD_TOP + 22
    p["kick_rule"] = LEAD_TOP + 29
    hf = fit_block(LEAD_HEAD, SERIF_BOLD, TEXT_R - TEXT_L, 2, 42, floor=28)
    p["head_f"] = hf.size
    p["head_lines"] = split_two(LEAD_HEAD, hf, TEXT_R - TEXT_L)
    p["head_lh"] = int(hf.size * 1.08)
    p["head_base0"] = p["kick_rule"] + 6 + int(hf.size * 0.80)
    p["head_bot"] = (p["head_base0"] + (len(p["head_lines"]) - 1) * p["head_lh"]
                     + int(hf.size * 0.24))

    df = fit_block(LEAD_DECK, SANS, TEXT_R - TEXT_L, 5, 17, floor=12)
    p["deck_f"] = df.size
    p["deck_lines"] = wrap(LEAD_DECK, df, TEXT_R - TEXT_L)
    p["deck_lh"] = int(df.size * 1.22)
    p["deck_base0"] = p["head_bot"] + 12 + int(df.size * 0.78)
    p["deck_bot"] = (p["deck_base0"] + (len(p["deck_lines"]) - 1) * p["deck_lh"]
                     + int(df.size * 0.24))

    p["body_rule"] = p["deck_bot"] + 8
    p["body_half"] = (TEXT_R - TEXT_L - 26) / 2.0
    pf = font(SANS, 12)
    p["body1"] = wrap(LEAD_P1, pf, p["body_half"])
    p["body2"] = wrap(LEAD_P2, pf, p["body_half"])
    p["body_lh"] = 14
    p["body_base0"] = p["body_rule"] + 14
    p["body_bot"] = (p["body_base0"]
                     + (max(len(p["body1"]), len(p["body2"])) - 1) * p["body_lh"] + 10)

    # six columns -----------------------------------------------------------
    cols = []
    for tag, tagc, headline, deck, src in CARDS:
        c = {"tag": tag, "colour": tagc}
        c["tag_base"] = COL_TOP + 14
        ch = fit_block(headline, SANS_BOLD, COL_W, 3, 21, floor=12)
        c["head_f"] = ch.size
        c["head_lines"] = wrap(headline, ch, COL_W)
        c["head_lh"] = int(ch.size * 1.04)
        c["head_base0"] = c["tag_base"] + 12 + int(ch.size * 0.78)
        c["head_bot"] = (c["head_base0"] + (len(c["head_lines"]) - 1) * c["head_lh"]
                         + int(ch.size * 0.26))
        cd = fit_block(deck, SANS, COL_W, 4, 12, floor=9)
        c["deck_f"] = cd.size
        c["deck_lines"] = wrap(deck, cd, COL_W)
        c["deck_lh"] = int(cd.size * 1.18)
        c["deck_base0"] = c["head_bot"] + 6 + int(cd.size * 0.74)
        c["deck_bot"] = (c["deck_base0"] + (len(c["deck_lines"]) - 1) * c["deck_lh"]
                         + int(cd.size * 0.26))
        sf = fit_block(src, SANS, COL_W, 2, 8, floor=7)
        c["src_f"] = sf.size
        c["src_lines"] = wrap(src, sf, COL_W)
        c["src_lh"] = int(sf.size * 1.25)
        c["src_base0"] = c["deck_bot"] + 7 + int(sf.size * 0.75)
        c["src_bot"] = (c["src_base0"] + (len(c["src_lines"]) - 1) * c["src_lh"] + 4)
        cols.append(c)
    p["cols"] = cols

    # the day in brief ------------------------------------------------------
    p["brief_title_base"] = BRIEF_TOP + 16
    p["brief_rule"] = BRIEF_TOP + 24
    stacks = []
    per = math.ceil(len(BRIEFS) / N_BRIEF_COLS)
    for col in range(N_BRIEF_COLS):
        stack = []
        base = p["brief_rule"] + 16
        for tag, headline in BRIEFS[col * per:(col + 1) * per]:
            tf = font(SANS_BOLD, 11)
            tag_w = tw(tag, tf, 1.0)
            avail = BRIEF_W - (tag_w + 16)
            bf = fit_block(headline, SANS_BOLD, avail, 2, 12, floor=10)
            lines = wrap(headline, bf, avail)
            lh = int(bf.size * 1.16)
            block = len(lines) * lh
            stack.append({"tag": tag, "tag_w": tag_w, "f": bf.size, "lines": lines,
                          "lh": lh, "base0": base,
                          "bottom": base + block - bf.size + int(bf.size * 1.08)})
            base += block + 8
        stacks.append(stack)
    p["brief_items"] = stacks
    p["brief_bottoms"] = [s[-1]["bottom"] + 4 for s in stacks]
    return p


P = plan()


# --------------------------------------------------------------------------
# masthead band
# --------------------------------------------------------------------------

def draw_masthead(d):
    tracked(d, ((ML + MR) / 2.0, P["flag_base"]), FLAG_LINE, font(SANS, 12), SOFT, 1.1,
            anchor="c")
    tracked(d, ((ML + MR) / 2.0, P["mast_base"]), "THE DAILY LEDGER",
            font(SERIF_BOLD, P["mast_size"]), INK, 0.0, anchor="c")

    d.rectangle([ML, P["rule1"], MR, P["rule1"] + 2], fill=INK)      # double rule
    d.rectangle([ML, P["rule2"], MR, P["rule2"]], fill=INK)

    tracked(d, ((ML + MR) / 2.0, P["date_base"]), DATE_LINE,
            font(SANS_BOLD, P["date_size"]), INK, 2.5, anchor="c")
    tracked(d, (MR, P["flag_base"]), XMAS_LINE, font(SANS_BOLD, 12), RED, 1.2, anchor="r")

    d.rectangle([ML, P["flag_rule"], MR, P["flag_rule"]], fill=MUTED)


# --------------------------------------------------------------------------
# lead illustration: ink + one red spot on paper
# --------------------------------------------------------------------------

BLDGS = (
    # (x fraction, width px, height px, window cols, lit-pattern seed)
    (0.000, 38, 108, 2, 0), (0.115, 30, 76, 2, 1), (0.205, 44, 132, 3, 2),
    (0.335, 26, 84, 1, 3), (0.410, 40, 116, 2, 4), (0.545, 32, 70, 2, 5),
    (0.635, 46, 138, 3, 6), (0.790, 28, 88, 1, 7), (0.865, 40, 110, 2, 8),
)

UMBRELLAS = (0.03, 0.13, 0.22, 0.31, 0.42, 0.52, 0.61, 0.71, 0.80, 0.90, 0.97)


def draw_lead_scene(page):
    """Flat black skyline with cream lit windows, three red balloons heeling
    in the wind on sagging tethers, diagonal rain, an umbrella crowd.
    Chunky shapes, ink plus one red spot, no gradients."""
    x0, y0 = SCENE_L, LEAD_TOP + 8
    w, h = SCENE_R - SCENE_L, LEAD_BOT - 8 - y0
    sc = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(sc)

    ground = h - 30                       # baseline of buildings and crowd

    # night skyline: flat black slabs, a few windows punched out in paper
    for i, (fx, bw, bh, wcols, seed) in enumerate(BLDGS):
        bx = fx * w
        top = ground - bh
        d.rectangle([bx, top, bx + bw, ground], fill=INK)
        if i % 3 == 1:                    # aerials on some roofs
            ax = bx + bw * 0.5
            d.line([(ax, top), (ax, top - 8)], fill=INK, width=2)
        cw = (bw - 8) / wcols
        rows = int((bh - 12) // 15)
        for r in range(rows):
            for c in range(wcols):
                if (seed * 5 + r * 3 + c * 7) % 4 != 0:
                    continue              # arithmetic pattern, ~25% lit
                wx = bx + 4 + c * cw + cw * 0.22
                wy = top + 7 + r * 15
                d.rectangle([wx, wy, wx + cw * 0.5, wy + 6], fill=PAPER)

    # diagonal rain: thin ink strokes slanting with the wind
    for i in range(44):
        rx = ((i * 173 + 29) % (w + 40)) - 20
        ry = (i * 71 + 11) % (ground - 8)
        ln = 11 + (i * 5) % 8
        d.line([(rx, ry), (rx - ln * 0.45, ry + ln)], fill=INK, width=1)

    # three balloons, all heeling the same way (wind from the right); each is
    # drawn upright on a paper-filled tile and rotated about its centre
    tilt = 14

    # star balloon
    sr, scx, scy = 30, w * 0.19, 62
    t = sr * 3
    tile = Image.new("RGB", (t, t), PAPER)
    td = ImageDraw.Draw(tile)
    pad = t / 2.0
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rad = sr if i % 2 == 0 else sr * 0.45
        pts.append((pad + rad * math.cos(a), pad + rad * math.sin(a)))
    td.polygon(pts, fill=RED, outline=INK)
    td.polygon([(pad + (x - pad) * 0.5, pad + (y - pad) * 0.5) for x, y in pts], fill=PAPER)
    td.polygon(pts, outline=INK)
    sc.paste(tile.rotate(tilt, resample=Image.BICUBIC, center=(pad, pad)),
             (int(scx - pad), int(scy - pad)))

    # round-face balloon
    fr, fcx, fcy = 26, w * 0.49, 70
    t = fr * 3
    tile = Image.new("RGB", (t, t), PAPER)
    fpad = t / 2.0
    td = ImageDraw.Draw(tile)
    td.ellipse([fpad - fr, fpad - fr, fpad + fr, fpad + fr], fill=RED, outline=INK, width=3)
    for sx in (-1, 1):                    # cream eyes, ink pupils
        ex = fpad + sx * fr * 0.38
        td.ellipse([ex - 5, fpad - fr * 0.34, ex + 5, fpad - fr * 0.10],
                   fill=PAPER, outline=INK)
        td.ellipse([ex - 2, fpad - fr * 0.28, ex + 2, fpad - fr * 0.16], fill=INK)
    td.arc([fpad - fr * 0.45, fpad + fr * 0.02, fpad + fr * 0.45, fpad + fr * 0.52],
           20, 160, fill=INK, width=3)
    sc.paste(tile.rotate(tilt, resample=Image.BICUBIC, center=(fpad, fpad)),
             (int(fcx - fpad), int(fcy - fpad)))

    # capsule balloon
    cw2, ch2, ccx, ccy = 19, 42, w * 0.80, 66
    tile = Image.new("RGB", (cw2 * 5, int(ch2 * 2.6)), PAPER)
    tp = (tile.size[0] / 2.0, tile.size[1] / 2.0)
    td = ImageDraw.Draw(tile)
    td.rounded_rectangle([tp[0] - cw2, tp[1] - ch2, tp[0] + cw2, tp[1] + ch2],
                         radius=cw2, fill=RED, outline=INK, width=3)
    for k in (-ch2 * 0.45, ch2 * 0.45):   # seam bands
        td.rectangle([tp[0] - cw2 + 3, tp[1] + k - 2, tp[0] + cw2 - 3, tp[1] + k + 2],
                     fill=PAPER)
    td.ellipse([tp[0] - 7, tp[1] - 7, tp[0] + 7, tp[1] + 7], fill=PAPER, outline=INK)
    sc.paste(tile.rotate(tilt, resample=Image.BICUBIC, center=tp),
             (int(ccx - tile.size[0] / 2.0), int(ccy - tile.size[1] / 2.0)))

    # sagging tethers down to the handlers' hands
    for bx, by, hx in ((scx, scy + sr, scx - 30), (fcx, fcy + fr, fcx - 26),
                       (ccx, ccy + ch2, ccx - 32)):
        mid = ((bx + hx) / 2.0, (by + (ground - 4)) / 2.0 + 10)
        curve = [((1 - t) * (1 - t) * bx + 2 * (1 - t) * t * mid[0] + t * t * hx,
                  (1 - t) * (1 - t) * by + 2 * (1 - t) * t * mid[1] + t * t * (ground - 4))
                 for t in [i / 24.0 for i in range(25)]]
        d.line([(int(x), int(y)) for x, y in curve], fill=INK, width=2)

    # crowd of umbrella silhouettes along the bottom
    d.rectangle([0, ground + 26, w, h], fill=INK)          # kerb mass
    for i, fx in enumerate(UMBRELLAS):
        ux = fx * w
        uy = ground + 6 + (i % 3) * 5
        uw = 15 + (i % 4) * 3
        d.pieslice([ux - uw, uy - uw * 0.8, ux + uw, uy + uw * 0.8], 180, 360, fill=INK)
        d.line([(ux, uy), (ux, uy + 13)], fill=INK, width=2)

    # the red spot: the wind itself, an arrow across the top of the frame
    d.line([(w - 28, 16), (28, 16)], fill=RED, width=3)
    d.polygon([(28, 16), (44, 9), (44, 23)], fill=RED)
    tracked(d, (w - 30, 10), "GUSTS TO 55 MPH", font(SANS_BOLD, 10), RED, 1.0, anchor="r")

    page.paste(sc, (x0, y0))
    return (x0, y0, x0 + w, y0 + h)


# --------------------------------------------------------------------------
# lead text
# --------------------------------------------------------------------------

def draw_lead(d):
    tracked(d, (TEXT_L, P["kick_base"]), LEAD_KICKER, font(SANS_BOLD, 17), RED, 1.4)
    d.rectangle([TEXT_L, P["kick_rule"], TEXT_R, P["kick_rule"]], fill=MUTED)

    hf = font(SERIF_BOLD, P["head_f"])
    y = P["head_base0"]
    for line in P["head_lines"]:
        tracked(d, (TEXT_L, y), line, hf, INK, 0.0)
        y += P["head_lh"]

    df = font(SANS, P["deck_f"])
    y = P["deck_base0"]
    for line in P["deck_lines"]:
        d.text((TEXT_L, y), line, font=df, fill=INK, anchor="ls")
        y += P["deck_lh"]

    d.rectangle([TEXT_L, P["body_rule"], TEXT_R, P["body_rule"]], fill=MUTED)
    pf = font(SANS, 12)
    y = P["body_base0"]
    for line in P["body1"]:
        d.text((TEXT_L, y), line, font=pf, fill=SOFT, anchor="ls")
        y += P["body_lh"]
    y = P["body_base0"]
    for line in P["body2"]:
        d.text((TEXT_L + P["body_half"] + 26, y), line, font=pf, fill=SOFT, anchor="ls")
        y += P["body_lh"]


# --------------------------------------------------------------------------
# six story columns
# --------------------------------------------------------------------------

def draw_columns(d):
    d.rectangle([ML, COL_TOP - 8, MR, COL_TOP - 7], fill=INK)
    for dx in COL_DIV:
        d.rectangle([dx, COL_TOP - 2, dx, COL_BOT - 6], fill=MUTED, width=1)

    for i, c in enumerate(P["cols"]):
        x = COL_XS[i]
        tracked(d, (x, c["tag_base"]), c["tag"], font(SANS_BOLD, 14), c["colour"], 1.6)
        d.rectangle([x, c["tag_base"] + 5, x + COL_W, c["tag_base"] + 5], fill=MUTED)

        hf = font(SANS_BOLD, c["head_f"])
        y = c["head_base0"]
        for line in c["head_lines"]:
            tracked(d, (x, y), line, hf, INK, 0.0)
            y += c["head_lh"]

        df = font(SANS, c["deck_f"])
        y = c["deck_base0"]
        for line in c["deck_lines"]:
            d.text((x, y), line, font=df, fill=SOFT, anchor="ls")
            y += c["deck_lh"]

        sf = font(SANS, c["src_f"])
        y = c["src_base0"]
        for line in c["src_lines"]:
            d.text((x, y), line, font=sf, fill=MUTED, anchor="ls")
            y += c["src_lh"]


# --------------------------------------------------------------------------
# THE DAY IN BRIEF
# --------------------------------------------------------------------------

def draw_briefs(d):
    d.rectangle([ML, BRIEF_TOP - 8, MR, BRIEF_TOP - 7], fill=INK)
    tracked(d, (ML, P["brief_title_base"]), "THE DAY IN BRIEF",
            font(SANS_BOLD, 18), INK, 3.0)
    w = tw("THE DAY IN BRIEF", font(SANS_BOLD, 18), 3.0)
    d.rectangle([ML + w + 12, BRIEF_TOP + 8, MR, BRIEF_TOP + 8], fill=MUTED)
    tracked(d, (MR, P["brief_title_base"]), "ALL TIMES LOCAL \u00b7 18 ITEMS \u00b7 8 REGIONS",
            font(SANS, 11), MUTED, 0.8, anchor="r")
    d.rectangle([ML, P["brief_rule"], MR, P["brief_rule"]], fill=MUTED)

    for dx in BRIEF_DIV:
        d.rectangle([dx, P["brief_rule"] + 4, dx, BRIEF_BOT], fill=MUTED, width=1)

    for col, stack in enumerate(P["brief_items"]):
        x = BRIEF_XS[col]
        for k, it in enumerate(stack):
            tf = font(SANS_BOLD, 11)
            tracked(d, (x, it["base0"]), it["tag"], tf, RED, 1.0)
            d.rectangle([x + it["tag_w"] + 6, it["base0"] - 9,
                         x + it["tag_w"] + 6, it["base0"] + 2], fill=MUTED)
            hf = font(SANS_BOLD, it["f"])
            y = it["base0"]
            for line in it["lines"]:
                d.text((x + it["tag_w"] + 16, y), line, font=hf, fill=INK, anchor="ls")
                y += it["lh"]
            if k < len(stack) - 1:
                sep = it["bottom"] + 2
                d.rectangle([x, sep, x + BRIEF_W, sep], fill=FAINT)


# --------------------------------------------------------------------------
# footer
# --------------------------------------------------------------------------

def draw_footer(d):
    d.rectangle([ML, FOOT_RULE, MR, FOOT_RULE + 1], fill=INK)
    tracked(d, (ML, FOOT_RULE + 18), FOOT_SRC, font(SANS, 10), SOFT, 0.3)
    tracked(d, (MR, FOOT_RULE + 18), FOOT_MARK, font(SANS_BOLD, 10), RED, 0.3, anchor="r")


# --------------------------------------------------------------------------
# layout audit: nothing clips, nothing overlaps, ink stays in its band
# --------------------------------------------------------------------------

def audit():
    """Re-measure every text string against its column; report any overflow."""
    rows = []
    rows.append(("flag line", tw(FLAG_LINE, font(SANS, 12), 1.1), MR - ML))
    flag_w = tw(FLAG_LINE, font(SANS, 12), 1.1)
    xmas_w = tw(XMAS_LINE, font(SANS_BOLD, 12), 1.2)
    rows.append(("flag vs thanksgiving share row", (ML + MR) / 2.0 + flag_w / 2.0,
                 MR - xmas_w - 12))
    rows.append(("masthead", tw("THE DAILY LEDGER", font(SERIF_BOLD, P["mast_size"]), 0.0),
                 MR - ML))
    rows.append(("date line", tw(DATE_LINE, font(SANS_BOLD, P["date_size"]), 2.5), MR - ML))
    rows.append(("thanksgiving", tw(XMAS_LINE, font(SANS_BOLD, 12), 1.2), 300))

    rows.append(("lead kicker", tw(LEAD_KICKER, font(SANS_BOLD, 17), 1.4), TEXT_R - TEXT_L))
    hf = font(SERIF_BOLD, P["head_f"])
    for i, line in enumerate(P["head_lines"]):
        rows.append(("lead head l%d" % (i + 1), tw(line, hf), TEXT_R - TEXT_L))
    df = font(SANS, P["deck_f"])
    for i, line in enumerate(P["deck_lines"]):
        rows.append(("lead deck l%d" % (i + 1), tw(line, df), TEXT_R - TEXT_L))
    pf = font(SANS, 12)
    for j, lines in enumerate((P["body1"], P["body2"])):
        for i, line in enumerate(lines):
            rows.append(("lead p%d l%d" % (j + 1, i + 1), tw(line, pf), P["body_half"]))

    for c in P["cols"]:
        tag = c["tag"]
        rows.append(("%s tag" % tag, tw(tag, font(SANS_BOLD, 14), 1.6), COL_W))
        hfn = font(SANS_BOLD, c["head_f"])
        for i, line in enumerate(c["head_lines"]):
            rows.append(("%s head l%d" % (tag, i + 1), tw(line, hfn), COL_W))
        dfn = font(SANS, c["deck_f"])
        for i, line in enumerate(c["deck_lines"]):
            rows.append(("%s deck l%d" % (tag, i + 1), tw(line, dfn), COL_W))
        sfn = font(SANS, c["src_f"])
        for i, line in enumerate(c["src_lines"]):
            rows.append(("%s src l%d" % (tag, i + 1), tw(line, sfn), COL_W))

    rows.append(("brief header", tw("THE DAY IN BRIEF", font(SANS_BOLD, 18), 3.0), 420))
    rows.append(("brief meta", tw("ALL TIMES LOCAL \u00b7 18 ITEMS \u00b7 8 REGIONS",
                                  font(SANS, 11), 0.8), 300))
    for stack in P["brief_items"]:
        for it in stack:
            tf = font(SANS_BOLD, 11)
            rows.append(("brief tag " + it["tag"], tw(it["tag"], tf, 1.0), it["tag_w"] + 4))
            bf = font(SANS_BOLD, it["f"])
            avail = BRIEF_W - (it["tag_w"] + 16)
            for i, line in enumerate(it["lines"]):
                rows.append(("brief %s l%d" % (it["tag"] + line[:6], i + 1), tw(line, bf), avail))

    rows.append(("footer src", tw(FOOT_SRC, font(SANS, 10), 0.3),
                 (MR - ML) - tw(FOOT_MARK, font(SANS_BOLD, 10), 0.3) - 24))
    rows.append(("footer mark", tw(FOOT_MARK, font(SANS_BOLD, 10), 0.3), 300))
    return rows


def vertical_checks():
    """Bands must not collide and every block's ink must stay inside its band."""
    ck = []
    ck.append(("flag cap above page", 4, P["flag_base"] - 10))
    ck.append(("masthead below flag", P["flag_base"] + 4,
               P["mast_base"] - int(P["mast_size"] * 0.76)))
    ck.append(("masthead above rule1", P["mast_base"] + 4, P["rule1"]))
    ck.append(("rule1 above rule2", P["rule1"] + 3, P["rule2"]))
    ck.append(("date below rule2", P["rule2"] + 2,
               P["date_base"] - int(P["date_size"] * 0.76)))
    ck.append(("date above foot rule", P["date_base"] + 4, P["flag_rule"]))
    ck.append(("lead below flag rule", P["flag_rule"] + 2, LEAD_TOP))
    ck.append(("kicker inside lead", LEAD_TOP + 8, P["kick_base"] - 14))
    ck.append(("head below kicker rule", P["kick_rule"] + 2,
               P["head_base0"] - int(P["head_f"] * 0.80)))
    ck.append(("deck below head", P["head_bot"] + 2,
               P["deck_base0"] - int(P["deck_f"] * 0.78)))
    ck.append(("body below deck", P["deck_bot"] + 2, P["body_rule"]))
    ck.append(("body inside lead", P["body_bot"], LEAD_BOT - 4))
    ck.append(("columns below lead", LEAD_BOT + 2, COL_TOP - 8))

    for c in P["cols"]:
        tag = c["tag"]
        ck.append(("col %s head below tag" % tag, c["tag_base"] + 6,
                   c["head_base0"] - int(c["head_f"] * 0.78)))
        ck.append(("col %s deck below head" % tag, c["head_bot"] + 2,
                   c["deck_base0"] - int(c["deck_f"] * 0.74)))
        ck.append(("col %s src below deck" % tag, c["deck_bot"] + 2,
                   c["src_base0"] - int(c["src_f"] * 0.75)))
        ck.append(("col %s inside band" % tag, c["src_bot"], COL_BOT - 8))

    ck.append(("brief below columns", COL_BOT - 6, BRIEF_TOP - 8))
    for i, bottom in enumerate(P["brief_bottoms"]):
        ck.append(("brief col %d floor" % (i + 1), bottom, BRIEF_BOT))
    ck.append(("footer below briefs", BRIEF_BOT + 2, FOOT_RULE))
    ck.append(("footer inside page", FOOT_RULE + 18 + 4, SIDE - 6))
    return ck


def scene_checks(box):
    """The illustration must sit inside its box, clear of the text column."""
    x0, y0, x1, y1 = box
    return [("scene right of divider", DIV_X + 4, x0),
            ("scene left of divider", x1, SCENE_R),
            ("scene top in band", LEAD_TOP, y0),
            ("scene bottom in band", y1, LEAD_BOT - 4)]


# --------------------------------------------------------------------------

def render():
    page = Image.new("RGB", (SIDE, SIDE), PAPER)
    d = ImageDraw.Draw(page)

    draw_masthead(d)
    draw_lead(d)
    box = draw_lead_scene(page)
    d = ImageDraw.Draw(page)
    d.rectangle([DIV_X, LEAD_TOP, DIV_X, LEAD_BOT], fill=MUTED, width=1)
    draw_columns(d)
    draw_briefs(d)
    draw_footer(d)
    return page, box


def main():
    img, box = render()

    rows = audit()
    overflow = [r for r in rows if r[1] > r[2]]
    worst = max(rows, key=lambda r: r[1] / r[2] if r[2] else 0)
    for label, used, limit in overflow:
        print("OVERFLOW %-30s %6.1f > %6.1f" % (label, used, limit))
    if overflow:
        raise SystemExit("%d text block(s) overflow their column" % len(overflow))
    print("text audit: %d blocks fit, tightest %s at %.0f/%.0f px"
          % (len(rows), worst[0], worst[1], worst[2]))

    checks = vertical_checks() + scene_checks(box)
    bad = [c for c in checks if c[1] > c[2]]
    for label, used, limit in bad:
        print("COLLISION %-30s %6.1f > %6.1f" % (label, used, limit))
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
    if len(blob) > 1_048_576:
        raise SystemExit("entry.png is %d bytes, over the 1 MiB gate" % len(blob))
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(blob)
    print("wrote entry.png and output/entry.png: %d bytes, %dx%d"
          % (len(blob), img.size[0], img.size[1]))


if __name__ == "__main__":
    main()
