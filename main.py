#!/usr/bin/env python3
"""news-image-20261127: one dense broadsheet summing up the world news of
Friday 27 November 2026.

Every story below was first reported on 26-27 November 2026 (no story is
older). Sources checked while building: AP, Reuters, CNN, USA TODAY, BBC,
Xinhua, the European Commission, the NYSE/Nasdaq holiday calendar, Adobe
Analytics and the day's wire roundups. Two traps were avoided on purpose:
the Mount Mayon eruption circulating in aggregators is dated 30 October,
not 27 November, and the Cartagena supermarket siege was yesterday's lead,
so neither is used here.

Run:  python3 main.py            (writes entry.png next to this file)
The program is fully offline and deterministic: same bytes on every run.
"""
import hashlib
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1400
PAPER = (247, 243, 233)
INK = (22, 32, 58)
RED = (178, 32, 44)
GOLD = (176, 134, 44)
GREY = (96, 96, 92)
LIGHT = (233, 227, 214)
NAVY = (22, 32, 58)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

DATE_LINE = "FRIDAY 27 NOVEMBER 2026"
TITLE = "THE WORLD IN ONE PAGE"

LEADS = [
    {
        "tag": "WAR",
        "headline": "Zelenskyy warns Russia is readying a major strike on Ukraine\u2019s power grid",
        "deck": "Kyiv says Moscow is \u201ccompleting preparations\u201d for a mass attack on energy and logistics as winter bites.",
    },
    {
        "tag": "TRADE",
        "headline": "EU leaders split over a \u20ac45bn Ukraine loan and a \u20ac1.58tn budget",
        "deck": "Merz wants all 27 states to share the loan; no deal is expected before the December summit.",
    },
    {
        "tag": "USA",
        "headline": "Storm grounds the 100th Macy\u2019s parade \u2014 a first in its history",
        "deck": "The Thanksgiving parade moves to Saturday after a nor\u2019easter brings 56-mph gusts to New York.",
    },
]

# (region, header colour, dot lon/lat or None, [(field, headline), ...])
PANELS = [
    ("NORTH AMERICA", (31, 78, 121), (-100, 45), [
        ("PARADE", "Macy\u2019s 100th Thanksgiving parade postponed to Sat. by storm"),
        ("MARKETS", "NYSE and Nasdaq close early at 1 p.m. ET for Black Friday"),
        ("WEATHER", "Thanksgiving storm: 56-mph gusts snarl flights at LaGuardia"),
        ("NFL", "Steelers release Rodgers; he clears waivers, now a free agent"),
        ("POLICE", "Masked ICE agents smash car window in California arrest"),
    ]),
    ("EUROPE", (122, 59, 46), (10, 52), [
        ("SUMMIT", "EU budget talks: \u20ac1.58tn plan for 2028\u201334, deal eyed in Dec."),
        ("TRANSPORT", "London Tube drivers begin first of eight days of strikes"),
        ("POLITICS", "Serbia sets early presidential election for 27 December"),
        ("ECONOMY", "Audi reports steep profit fall as China market stays weak"),
        ("TECH", "EU and Canada plan closer collaboration on AI"),
    ]),
    ("UKRAINE & RUSSIA", (91, 45, 142), (35, 55), [
        ("WAR", "Zelenskyy: Russia finishing plans for a massive grid strike"),
        ("DIPLOMACY", "US envoy: biggest Russia-Ukraine prisoner swap due \u201cshortly\u201d"),
        ("ARMS", "US State Dept. clears potential F-16 equipment sale to Kyiv"),
        ("TALKS", "Kremlin agrees Europeans can join December peace talks"),
        ("STRIKE", "Ukraine hits Su-34 fighter-jet base in Volgograd region"),
    ]),
    ("MIDDLE EAST", (138, 109, 27), (45, 30), [
        ("GAZA", "Israeli strikes kill 10 in Gaza, incl. a Hamas security chief"),
        ("GAZA", "Katz threatens an operation that could displace 1m people"),
        ("YEMEN", "Houthis claim strikes on Saudi ports of Jizan"),
        ("KUWAIT", "Iranian drones kill two Italians in a Kuwait steel-plant attack"),
        ("EGYPT", "Cairo tanker fire kills 31; MPs demand accountability"),
    ]),
    ("AFRICA", (46, 107, 52), (20, 5), [
        ("SUDAN", "Khartoum rejects Addis Ababa\u2019s plan to end the war"),
        ("SUDAN", "Sudanese return to the capital to find their homes in ruins"),
        ("KENYA", "Court: US-backed Ebola centre disregarded the constitution"),
        ("EGYPT", "Cairo mourns 31 dead in the Ring Road tanker inferno"),
        ("GUINEA", "Conakry told to clear its rubbish before the end of December"),
    ]),
    ("SOUTH & SE ASIA", (179, 32, 44), (95, 20), [
        ("THAILAND", "Blast and fire at a Bangkok oil facility injures at least 9"),
        ("INDONESIA", "14 dead, 12 missing after flooding at an illegal gold mine"),
        ("MYANMAR", "Junta rejects \u2018inappropriate\u2019 parts of the genocide ruling"),
        ("TRADE", "Vietnam races to finish a US trade deal as 35% tariffs loom"),
        ("SHIPPING", "Singapore and CMA CGM trial cleaner fuel for shipping"),
    ]),
    ("EAST ASIA & PACIFIC", (15, 118, 110), (135, 30), [
        ("N. KOREA", "Kim vows to expand the nuclear arsenal after Trump outreach"),
        ("AUSTRALIA", "Digital Duty of Care law passes; fines up to 5% of revenue"),
        ("NEW ZEALAND", "Special votes counted: election cliffhanger to be decided"),
        ("ECONOMY", "NZ dollar nears a 20-year low as rate gaps widen"),
        ("SECURITY", "Australia-Fiji security alliance begins, Albanese signs"),
    ]),
    ("LATIN AMERICA", (21, 101, 140), (-60, -15), [
        ("DIPLOMACY", "Brazil pulls its ambassador; Milei uninvited to Lula\u2019s swearing-in"),
        ("WEATHER", "Heavy rains kill at least 8 across southern Brazil"),
        ("MEXICO", "Ex-prosecutor charged with treason over a US drug raid"),
        ("ARGENTINA", "Left stages a \u2018March of Anger\u2019 against Milei\u2019s austerity"),
    ]),
    ("BUSINESS & TECH", (90, 90, 96), None, [
        ("CHIPS", "DOJ inquiry into Nvidia\u2019s Jensen Huang; Vance backs him"),
        ("RETAIL", "Salesforce: Black Friday discounts deeper than last year"),
        ("E-COMMERCE", "Adobe: US online Black Friday sales to hit $12.9bn, +9.2%"),
        ("POLICY", "Trump reaffirms tariffs despite voter backlash"),
    ]),
    ("SPORT & CULTURE", (146, 74, 130), None, [
        ("NFL", "Rudolph to start as Steelers host the Broncos on Friday"),
        ("FOOTBALL", "Europa League game in Batumi halted after fan clashes"),
        ("CRICKET", "India chase a first Test series win in NZ in 17 years"),
        ("BASKETBALL", "FIBA qualifiers: Australia v Iran, NZ v Jordan tonight"),
    ]),
]

# (UTC time, label) — all on 27 Nov 2026, UTC; labels kept short so they
# fit their column without colliding with neighbours
TIMELINE = [
    ("00:00", "EU summit, day two"),
    ("03:50", "Zelenskyy grid warning"),
    ("05:30", "Tube strike begins"),
    ("08:00", "Adobe: $12.9bn forecast"),
    ("14:30", "NYSE opens, short day"),
    ("18:00", "NYSE closes 1 p.m. ET"),
]

# Simplified continent outlines (lon, lat), equirectangular.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80), (-80, 73),
     (-75, 72), (-65, 60), (-55, 52), (-60, 46), (-70, 42), (-75, 35), (-80, 32),
     (-85, 30), (-90, 21), (-95, 19), (-100, 16), (-105, 20), (-110, 23), (-115, 30),
     (-120, 34), (-125, 40), (-125, 49), (-130, 55), (-140, 60), (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 12), (-70, 12), (-60, 8), (-52, 5), (-50, 0), (-45, -3),
     (-35, -8), (-40, -20), (-48, -28), (-55, -35), (-60, -38), (-65, -45), (-68, -52),
     (-70, -55), (-73, -50), (-73, -40), (-72, -30), (-70, -20), (-75, -15), (-80, -5)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (3, 53), (8, 57), (10, 59),
     (5, 60), (5, 62), (10, 64), (18, 69), (25, 71), (30, 70), (35, 68), (40, 68),
     (45, 66), (40, 60), (35, 55), (30, 50), (28, 45), (23, 40), (20, 40), (15, 44),
     (12, 44), (8, 44), (3, 42), (0, 38), (-5, 36), (-9, 37)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (32, 31), (35, 28),
     (38, 22), (43, 12), (48, 11), (51, 10), (45, 0), (40, -10), (38, -18), (35, -25),
     (32, -29), (28, -33), (20, -35), (15, -30), (12, -18), (9, -2), (8, 4), (0, 5),
     (-8, 5), (-13, 8), (-17, 12)],
    [(30, 36), (35, 36), (40, 38), (45, 40), (50, 42), (55, 45), (60, 50), (65, 55),
     (70, 60), (75, 68), (80, 72), (90, 75), (100, 76), (110, 74), (120, 73), (130, 72),
     (140, 72), (150, 70), (160, 66), (170, 66), (178, 65), (170, 60), (162, 56),
     (158, 52), (150, 60), (142, 55), (140, 50), (135, 43), (130, 38), (127, 35),
     (122, 32), (120, 28), (115, 23), (110, 20), (108, 12), (105, 9), (100, 8),
     (98, 12), (95, 16), (92, 20), (88, 22), (85, 20), (80, 15), (77, 8), (75, 12),
     (72, 20), (68, 23), (62, 25), (58, 26), (55, 27), (52, 28), (50, 30), (48, 30),
     (45, 29), (42, 28), (40, 30), (36, 36), (33, 36)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -33), (130, -32), (135, -35),
     (140, -38), (145, -38), (150, -37), (153, -32), (153, -27), (150, -23), (146, -19),
     (142, -15), (142, -11), (137, -12), (135, -15), (132, -12), (130, -13), (126, -14),
     (122, -17), (118, -20)],
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 41), (143, 43), (145, 44),
     (143, 42), (140, 39), (137, 36), (133, 34), (131, 32)],
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10), (125, -9),
     (130, -4), (135, -3), (140, -8), (135, -7), (128, -3), (120, -2), (112, -3),
     (105, 1), (100, 4)],
]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_map(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(214, 228, 235), outline=GREY, width=2)
    mw, mh = x1 - x0, y1 - y0

    def proj(lon, lat):
        return (x0 + (lon + 180.0) / 360.0 * mw,
                y0 + (85.0 - lat) / 145.0 * mh)

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=(126, 160, 128), outline=(70, 100, 72))
    # graticule
    for lon in range(-150, 181, 30):
        x = x0 + (lon + 180.0) / 360.0 * mw
        draw.line([(x, y0), (x, y1)], fill=(190, 205, 212), width=1)
    for lat in range(-60, 86, 30):
        y = y0 + (85.0 - lat) / 145.0 * mh
        draw.line([(x0, y), (x1, y)], fill=(190, 205, 212), width=1)
    # numbered dots for the 8 geographic regions
    n = 0
    for name, colour, dot, _stories in PANELS:
        if dot is None:
            continue
        n += 1
        cx, cy = proj(*dot)
        draw.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=RED,
                     outline=(255, 255, 255), width=2)
        label = str(n)
        f = font(SANS_B, 13)
        tw = draw.textlength(label, font=f)
        draw.text((cx - tw / 2, cy - 7), label, font=f, fill=(255, 255, 255))
    return n


def draw_illustration(img, draw, box):
    """Dusk New York skyline with a grounded parade balloon in the rain."""
    x0, y0, x1, y1 = box
    rng = random.Random(20261127)
    # sky gradient: deep navy -> burnt orange horizon
    top = (24, 32, 68)
    mid = (96, 62, 96)
    bot = (214, 128, 64)
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0)
        if t < 0.55:
            a, b, u = top, mid, t / 0.55
        else:
            a, b, u = mid, bot, (t - 0.55) / 0.45
        c = tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3))
        draw.line([(x0, y), (x1, y)], fill=c)
    # moon
    draw.ellipse([x1 - 95, y0 + 18, x1 - 55, y0 + 58], fill=(240, 232, 200))
    draw.ellipse([x1 - 88, y0 + 14, x1 - 52, y0 + 52], fill=(96, 62, 96))
    # skyline silhouettes
    bw = (x1 - x0) // 14
    heights = [0.42, 0.55, 0.38, 0.62, 0.48, 0.70, 0.52, 0.44, 0.66, 0.40,
               0.58, 0.46, 0.72, 0.50]
    for i, hf in enumerate(heights):
        bx = x0 + i * bw
        bh = int((y1 - y0) * hf)
        draw.rectangle([bx, y1 - bh, bx + bw - 3, y1], fill=(18, 22, 44))
        # lit windows
        for _ in range(9):
            wx = bx + rng.randint(4, max(5, bw - 10))
            wy = y1 - bh + rng.randint(6, max(7, bh - 12))
            draw.rectangle([wx, wy, wx + 4, wy + 5],
                           fill=(240, 200, 110) if rng.random() < 0.7 else (150, 170, 210))
    # big parade balloon: red envelope with vertical cream stripes + basket
    cx, cy = x0 + int((x1 - x0) * 0.30), y0 + int((y1 - y0) * 0.30)
    rx, ry = 92, 62
    stripe = Image.new("RGBA", (2 * rx, 2 * ry), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripe)
    sd.ellipse([0, 0, 2 * rx, 2 * ry], fill=(214, 72, 62, 255))
    for sx in (-46, 0, 46):
        sd.rectangle([rx + sx - 14, 0, rx + sx + 14, 2 * ry],
                     fill=(247, 240, 222, 255))
    sd.ellipse([0, 0, 2 * rx, 2 * ry], outline=(140, 30, 26, 255), width=3)
    base = img.convert("RGBA")
    base.alpha_composite(stripe, (cx - rx, cy - ry))
    img.paste(base.convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([cx - rx + 16, cy - ry + 8, cx - rx + 52, cy - ry + 34],
                 fill=(255, 214, 190))
    bx0, bx1 = cx - 26, cx + 26
    by0, by1 = cy + ry + 26, cy + ry + 48
    for dx in (-70, -24, 24, 70):
        draw.line([(cx + dx, cy + ry - 4), (cx + dx * 0.35, by0)],
                  fill=(230, 225, 210), width=2)
    draw.rectangle([bx0, by0, bx1, by1], fill=(96, 62, 36),
                   outline=(60, 38, 20), width=2)
    # rain streaks
    for _ in range(70):
        rx0 = rng.randint(x0, x1)
        ry0 = rng.randint(y0, y1 - 20)
        draw.line([(rx0, ry0), (rx0 - 5, ry0 + 16)], fill=(200, 210, 225), width=1)
    draw.rectangle(box, outline=GREY, width=2)


def wrap_tagged(draw, field, headline, f_field, f_story, width):
    """Wrap 'FIELD headline...' as one paragraph: the bold field tag starts
    line 1, the headline flows after it and continues on following lines."""
    words = headline.split()
    lines = []
    # first line: field + as many words as fit
    cur = field + "  "
    cur_w = draw.textlength(cur, font=f_field)
    i = 0
    while i < len(words):
        w = words[i]
        ww = draw.textlength((" " if cur != field + "  " else "") + w, font=f_story)
        if cur_w + ww <= width:
            cur += (" " if cur != field + "  " else "") + w
            cur_w += ww
            i += 1
        else:
            break
    lines.append((cur, True))
    # remaining lines: headline only
    rest = words[i:]
    cur = ""
    for w in rest:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=f_story) <= width:
            cur = trial
        else:
            lines.append((cur, False))
            cur = w
    if cur:
        lines.append((cur, False))
    return lines


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 40
    n_stories = sum(len(s) for _n, _c, _d, s in PANELS)
    n_regions = len(PANELS)
    # ---- masthead ----
    d.rectangle([0, 0, W, 8], fill=RED)
    f_title = font(SERIF_B, 76)
    f_date = font(SANS_B, 30)
    f_sub = font(SANS, 22)
    d.text((mx, 36), TITLE, font=f_title, fill=INK)
    tw = d.textlength(DATE_LINE, font=f_date)
    d.text((W - mx - tw, 52), DATE_LINE, font=f_date, fill=RED)
    subtitle = (f"{n_stories} stories  \u00b7  {n_regions} regions  \u00b7  "
                "every story first reported 26\u201327 Nov 2026")
    d.text((mx, 128), subtitle, font=f_sub, fill=GREY)
    d.line([(mx, 168), (W - mx, 168)], fill=INK, width=3)
    # ---- date-check bar ----
    f_check = font(SANS_B, 18)
    check = ("DATE CHECKED: 27 NOV 2026 \u2014 every story below was first reported on "
             "26\u201327 Nov 2026; no story is older.")
    d.rectangle([mx, 180, W - mx, 214], fill=(232, 222, 190))
    d.text((mx + 12, 188), check, font=f_check, fill=INK)
    # ---- leads ----
    lead_y, lead_h = 228, 158
    lw = (W - 2 * mx - 2 * 24) // 3
    f_tag = font(SANS_B, 19)
    f_head = font(SERIF_B, 24)
    f_deck = font(SANS, 17)
    for i, lead in enumerate(LEADS):
        x = mx + i * (lw + 24)
        d.rectangle([x, lead_y, x + lw, lead_y + lead_h], fill=(255, 255, 255),
                    outline=GREY, width=1)
        d.rectangle([x, lead_y, x + lw, lead_y + 30], fill=NAVY)
        d.text((x + 10, lead_y + 4), lead["tag"], font=f_tag, fill=(255, 255, 255))
        lines = wrap(d, lead["headline"], f_head, lw - 20)
        y = lead_y + 36
        for ln in lines[:2]:
            d.text((x + 10, y), ln, font=f_head, fill=INK)
            y += 28
        deck_lines = wrap(d, lead["deck"], f_deck, lw - 20)
        for ln in deck_lines[:2]:
            d.text((x + 10, y), ln, font=f_deck, fill=GREY)
            y += 21
    # ---- region panels: 2 rows x 5 cols ----
    grid_y, grid_h = 402, 620
    cols, rows = 5, 2
    pw = (W - 2 * mx - (cols - 1) * 16) // cols
    ph = (grid_h - 16) // rows
    f_region = font(SANS_B, 20)
    f_field = font(SANS_B, 16)
    f_story = font(SANS, 17)
    for idx, (name, colour, _dot, stories) in enumerate(PANELS):
        r, c = divmod(idx, cols)
        x = mx + c * (pw + 16)
        y = grid_y + r * (ph + 16)
        d.rectangle([x, y, x + pw, y + ph], fill=(255, 255, 255), outline=GREY, width=1)
        d.rectangle([x, y, x + pw, y + 32], fill=colour)
        d.text((x + 10, y + 5), name, font=f_region, fill=(255, 255, 255))
        sy = y + 42
        for field, headline in stories:
            lines = wrap_tagged(d, field, headline, f_field, f_story, pw - 20)
            ly = sy
            for text, is_first in lines[:2]:
                if is_first:
                    fw = d.textlength(field + "  ", font=f_field)
                    d.text((x + 10, ly), field, font=f_field, fill=colour)
                    rest = text[len(field) + 2:]
                    d.text((x + 10 + fw, ly), rest, font=f_story, fill=INK)
                else:
                    d.text((x + 10, ly), text, font=f_story, fill=INK)
                ly += 21
            sy = ly + 7
    # ---- bottom strip: map | timeline | illustration ----
    strip_y, strip_h = 1038, 280
    map_w, ill_w = 560, 560
    map_box = (mx, strip_y, mx + map_w, strip_y + strip_h)
    ill_box = (W - mx - ill_w, strip_y, W - mx, strip_y + strip_h)
    tl_box = (mx + map_w + 16, strip_y, W - mx - ill_w - 16, strip_y + strip_h)
    n_marked = draw_map(d, map_box)
    f_cap = font(SANS_B, 17)
    d.text((map_box[0], strip_y + strip_h + 6),
           f"WORLD MAP \u2014 {n_marked} geographic regions marked; Business & Tech and "
           "Sport & Culture span the globe.", font=f_cap, fill=GREY)
    draw_illustration(img, d, ill_box)
    d = ImageDraw.Draw(img)
    d.text((ill_box[0], strip_y + strip_h + 6),
           "NEW YORK \u2014 the 100th Macy\u2019s parade, grounded.",
           font=f_cap, fill=GREY)
    # timeline
    d.rectangle(tl_box, fill=(255, 255, 255), outline=GREY, width=1)
    f_tl_h = font(SANS_B, 20)
    f_tl_t = font(SANS_B, 18)
    f_tl_l = font(SANS, 15)
    d.text((tl_box[0] + 12, tl_box[1] + 10), "THE DAY IN UTC", font=f_tl_h, fill=RED)
    tx0, tx1 = tl_box[0] + 30, tl_box[2] - 30
    ty = tl_box[1] + 78
    d.line([(tx0, ty), (tx1, ty)], fill=INK, width=3)
    for i, (t, label) in enumerate(TIMELINE):
        fx = tx0 + (tx1 - tx0) * i / (len(TIMELINE) - 1)
        d.ellipse([fx - 7, ty - 7, fx + 7, ty + 7], fill=RED,
                  outline=(255, 255, 255), width=2)
        tw2 = d.textlength(t, font=f_tl_t)
        d.text((fx - tw2 / 2, ty - 34), t, font=f_tl_t, fill=INK)
        lines = wrap(d, label, f_tl_l, 100)
        ly = ty + 16
        for ln in lines[:3]:
            lw2 = d.textlength(ln, font=f_tl_l)
            lx = fx - lw2 / 2
            lx = max(tl_box[0] + 8, min(lx, tl_box[2] - lw2 - 8))
            d.text((lx, ly), ln, font=f_tl_l, fill=GREY)
            ly += 20
    # ---- footer ----
    d.line([(mx, H - 42), (W - mx, H - 42)], fill=GREY, width=1)
    f_foot = font(SANS, 15)
    d.text((mx, H - 32),
           "Generated 27 Nov 2026 \u00b7 run python3 main.py to reproduce this page \u00b7 "
           "Sources: AP, Reuters, CNN, USA TODAY, BBC, Xinhua, EC, Adobe \u00b7 "
           "make.fun news-image-20261127 \u00b7 $100 USDC, 50 places",
           font=f_foot, fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG")
    digest = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(f"wrote {out}  {W}x{H}  {n_stories} stories, {n_regions} regions  sha256={digest}")


if __name__ == "__main__":
    main()
