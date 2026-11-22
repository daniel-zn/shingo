"""Posters XP·07 to XP·12 of the Shingō field series.

  from posters import posters      # six SVG strings, XP·07 .. XP·12

SPECIMEN, PULSE, SECTOR, TRANSIT, PROOF and UNIT. Each one is drawn in the
shared frame (build._xp_frame: masthead, rule, display word, vertical kanji,
mono line, "nn / 12") with its art in the window y 44..470. Colours are CSS
variables only, so every poster prints in both modes. Coral is one or two
solid blocks per poster plus small signal text; guides, rails, crosshairs and
grid paper print in ground-dim or ground-3.
"""
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

HI, DIM, GR, G2, G3 = "var(--ground-hi)", "var(--ground-dim)", "var(--ground)", "var(--ground-2)", "var(--ground-3)"
CORAL, SIG = "var(--coral)", "var(--signal-text)"
INKF = "#0c0c0a"      # ink on coral, both modes (as every coral component)
MONO = .64   # IBM Plex Mono advance (.6 em) + the .04 em tracking of .xp-m


def _build():
    """tools/build.py: the running script when it is the caller, else the module."""
    main = sys.modules.get("__main__")
    if main is not None and hasattr(main, "_xp_frame"):
        return main
    import build
    return build


# ---------------------------------------------------------------- small drawing kit
def n(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def text(x, y, s, size=7, cls="xp-m", fill=DIM, anchor=None, extra=""):
    a = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{n(x)}" y="{n(y)}" class="{cls}" font-size="{n(size)}" fill="{fill}"{a}{extra}>{s}</text>'


def rect(x, y, w, h, fill=HI, extra=""):
    return f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="{fill}"{extra}/>'


def cut(x0, y0, x1, y1, c):
    """Plate points with the system cuts: top-left and bottom-right."""
    pts = [(x0 + c, y0), (x1, y0), (x1, y1 - c), (x1 - c, y1), (x0, y1), (x0, y0 + c)]
    return " ".join(f"{n(x)},{n(y)}" for x, y in pts)


def poly(pts, fill=HI, extra=""):
    return f'<polygon points="{pts}" fill="{fill}"{extra}/>'


def lines(d, col=DIM, w=.8, extra=""):
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{n(w)}"{extra}/>'


def plus(x, y, s=4, col=DIM, w=.8):
    return lines(f"M{n(x - s)} {n(y)}H{n(x + s)}M{n(x)} {n(y - s)}V{n(y + s)}", col, w)


def use(sym, x, y, w, h, col=HI, extra=""):
    return f'<use href="#g-{sym}" x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" style="color:{col}"{extra}/>'


def hazard(cid, x, y, w, h, step=10, fill=HI):
    """'/' stripes, half ink half ground, clipped to the band."""
    o = [f'<clipPath id="{cid}"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}"/></clipPath><g clip-path="url(#{cid})">']
    k = x - h - step
    while k < x + w:
        o.append(poly(f"{n(k)},{n(y + h)} {n(k + step / 2)},{n(y + h)} {n(k + step / 2 + h)},{n(y)} {n(k + h)},{n(y)}", fill))
        k += step
    o.append("</g>")
    return "".join(o)


def hatch(cid, x, y, w, h, step=3, col=DIM, sw=.8):
    """'/' hatching inside a box (the caution fill)."""
    d = "".join(f"M{n(x + k)} {n(y + h)}L{n(x + k + h)} {n(y)}" for k in range(-int(h), int(w) + 1, step))
    return (f'<clipPath id="{cid}"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}"/></clipPath>'
            f'<g clip-path="url(#{cid})">{lines(d, col, sw)}</g>')


def barcode(x, y, w, h, seed=1, fill=HI):
    rnd, o, cx = random.Random(seed), [], x
    while True:
        bw = rnd.choice((.8, .8, 1.2, 1.6, 2.4))
        if cx + bw > x + w - 2:
            break
        o.append(rect(cx, y, bw, h, fill))
        cx += bw + rnd.choice((.8, 1.2, 1.6))
    o.append(rect(x + w - 1.6, y, 1.6, h, fill))
    return "".join(o)


def spread(rows, x0, x1, y, lh, size=6.2, fill=DIM):
    """Word-spaced microtext: every word set on its own, the line justified to the measure."""
    o = []
    for i, row in enumerate(rows):
        ws = row.split()
        wid = [len(w) * size * MONO - size * .04 for w in ws]
        gap = (x1 - x0 - sum(wid)) / max(1, len(ws) - 1)
        x = x0
        for w, wd in zip(ws, wid):
            o.append(text(x, y + i * lh, w, size, fill=fill))
            x += wd + gap
    return "".join(o)


def leader_rows(rows, width):
    """Mono spec rows with dot leaders, padded to one width (monospace keeps the right edge)."""
    out = []
    for k, v in rows:
        dots = max(2, width - len(k) - len(v) - 2)
        out.append(f"{k} {'.' * dots} {v}")
    return out


# ---------------------------------------------------------------- XP·07 SPECIMEN
def _specimen():
    o = []
    # grid paper: 10 px cells, every fifth line darker
    gx0, gx1, gy0, gy1 = 26, 376, 80, 340
    mi, ma = [], []
    for i in range(36):
        x = gx0 + 10 * i
        (ma if i % 5 == 0 else mi).append(f"M{x} {gy0}V{gy1}")
    for j in range(27):
        y = gy0 + 10 * j
        (ma if j % 5 == 0 or y == gy1 else mi).append(f"M{gx0} {y}H{gx1}")
    o.append(lines("".join(mi), G3, .5, ' opacity=".6"'))
    o.append(lines("".join(ma), G3, 1))
    # the giant letter: cap 190 on the grid, baseline 320
    k = 190 / 650
    x0, base = 30 - 54 * k, 320
    o.append(text(x0, base, "S", 1000 * k, "xp-d", G3))
    # construction: cap, x-height, baseline; side bearings; the two 45° cuts
    cap, xh = base - 650 * k, base - 481 * k
    il, ir = x0 + 54 * k, x0 + 914 * k
    o.append(lines(f"M26 {n(cap)}H290M26 {n(xh)}H290M26 {base}H290", DIM, .7))
    o.append(lines(f"M{n(il)} 84V336M{n(ir)} 84V336", DIM, .6, ' stroke-dasharray="2 3"'))
    s1 = il + (base - 480 * k)          # x + y of the top-left cut
    s2 = x0 + 914 * k + base - 170 * k  # x + y of the bottom-right cut
    o.append(lines(f"M26 {n(s1 - 26)}L{n(s1 - 80)} 80M{n(s2 - 340)} 340L290 {n(s2 - 290)}", DIM, .7, ' stroke-dasharray="3 2"'))
    o.append(lines(f"M{n(il)} 92H{n(ir)}M{n(il)} 89V95M{n(ir)} 89V95", DIM, .7))
    o.append(text((il + ir) / 2, 89, "ADVANCE 967", 5.6, anchor="middle"))
    o.append(text(il + 2, 101, "LSB 54", 5.6))
    o.append(text(ir - 2, 101, "RSB 53", 5.6, anchor="end"))
    o.append(text(30, cap - 3, "CAP · 650", 5.6))
    o.append(text(ir, xh - 3, "X-HEIGHT · 481", 5.6, anchor="end"))
    o.append(text(30, base + 9, "BASELINE · 0", 5.6))
    o.append(text(s1 - 102, 98, "45°", 5.6, anchor="end"))
    o.append(text(s2 - 284, 292, "45°", 5.6))
    # specimen card over the grid
    cx0, cx1, cy0, cy1 = 290, 376, 88, 332
    o.append(poly(cut(cx0, cy0, cx1, cy1, 8), GR, f' stroke="{HI}" stroke-width="1.2"'))
    o.append(text(297, 99, "GLYPH SET · 36", 5.5))
    o.append(lines("M296 104H370M296 236H370M296 298H370", G3, .8))
    cols = [305.25 + 18.5 * c for c in range(4)]
    for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        o.append(text(cols[i % 4], 122 + 17.5 * (i // 4), ch, 14, "xp-d", HI, "middle"))
    for i, ch in enumerate("0123456789&#"):
        o.append(text(cols[i % 4], 256 + 17.5 * (i // 4), ch, 14, "xp-d", SIG if ch.isdigit() else HI, "middle"))
    o.append(text(297, 311, "HEAVY 900", 5.5))
    o.append(text(297, 321, "CAP .65 · X .48", 5.5))
    # header: coral mark tile, type name, test stamp
    o.append(rect(24, 46, 26, 26, CORAL))
    o.append(use("mark", 26, 48, 22, 22, INKF))
    o.append(text(58, 57, "SHINGO GRID HEAVY", 11, "xp-t", HI))
    o.append(text(58, 68, "TYPE SPECIMEN · WEIGHT 900 · ONE STROKE · 45° CUTS", 6))
    o.append(rect(290, 46, 86, 26, "none", f' stroke="{HI}" stroke-width="1.2"'))
    o.append(rect(292.5, 48.5, 81, 21, "none", f' stroke="{HI}" stroke-width=".5"'))
    o.append(lines("M340 48.5V69.5", HI, .8))
    o.append(text(297, 63.5, "TEST", 10, "xp-d", HI))
    o.append(text(358, 63.5, "V01", 10, "xp-d", HI, "middle"))
    # coordinate stack
    stack = [(360, "NORTH / WEST", 12, "HEMISPHERE"), (393, "2026", 26, "YEAR"), (418, "38° 42' 49\"", 13, "LAT N"),
             (443, "UNIT 04", 13, "FIELD"), (466, "A–Z / 0–9", 13, "SET")]
    for y, s, size, tag in stack:
        o.append(text(26, y, s.replace('"', "&quot;"), size, "xp-d", HI))
        o.append(text(196, y, tag, 5.8, anchor="end"))
    o.append(lines("M26 367H196M26 400H196M26 425H196M26 450H196", G3, .8))
    # upper and lower case
    o.append(text(212, 404, "Aa", 44, "xp-d", HI))
    o.append(text(212, 420, "UPPER / LOWER", 5.8))
    o.append(text(212, 430, "ONE HEAVY STROKE", 5.8))
    # colophon
    for i, s in enumerate(["DRAWN · LIS 2026", "STROKE 1/5 CAP", "CUTS 45° TL / BR", "UPM 1000"]):
        o.append(text(376, 356 + 10 * i, s, 5.8, anchor="end"))
    return o


# ---------------------------------------------------------------- XP·08 PULSE
def _pulse(B):
    o = []
    # word-spaced microtext
    o.append(spread(["ABOVE THE NOISE, MACHINES", "HUM IN SILENCE. PIPES,", "WIRES, STEEL. ONE PULSE", "RETURNS EVERY 2.5 S."], 24, 166, 56, 10))
    # rails with spec text
    for i, s in enumerate(["2835×1890 PX", "200 PPI", "“SILENT PULSE”", "MADE BY AXIOM"]):
        x = 184 + 14 * i
        o.append(lines(f"M{x} 44V118", DIM, .7))
        o.append(rect(x - 1.5, 116, 3, 3, HI))
        o.append(text(x + 2, 50, s, 5.8, extra=f' transform="rotate(90 {x + 2} 50)"'))
    # barcode + warning in a cut box
    o.append(poly(cut(296, 50, 376, 86, 6), "none", f' stroke="{HI}" stroke-width="1.2"'))
    o.append(use("warn", 303, 57, 22, 22, HI))
    o.append(barcode(332, 57, 38, 22, 11))
    o.append(text(376, 96, "REF SP-11 · 2026", 5.8, anchor="end"))
    for x, y in [(262, 60), (262, 104), (376, 112)]:
        o.append(plus(x, y))
    # the exploded X
    o.append(B.exploded_x(298, 192, 62))
    # subhead, trace and spec rows
    o.append(text(24, 118, "“SILENT PULSE”", 12, "xp-t", HI))
    o.append(text(24, 130, "FIELD RECORDING · CHANNEL 11 · 0.4 HZ", 6))
    rnd = random.Random(8)
    for i in range(44):
        x = 24 + i * 4
        env = 3 + 23 * max(0, 1 - abs(i - 27) / 9) ** 1.4 + 6 * max(0, 1 - abs(i - 9) / 4)
        hgt = max(1.5, env * (.65 + .35 * rnd.random()))
        o.append(rect(x, 172 - hgt, 2, hgt * 2, HI))
    o.append(lines("M24 206H200" + "".join(f"M{24 + 22 * k} 206V{210 if k % 2 == 0 else 208.5}" for k in range(9)), DIM, .7))
    for k in range(0, 9, 2):
        o.append(text(24 + 22 * k, 218, ["0", "1", "2", "3", "4 S"][k // 2], 5.4, anchor={0: "start", 8: "end"}.get(k, "middle")))
    for i, row in enumerate(leader_rows([("PEAK", "−12 DB"), ("FLOOR", "−62 DB"), ("PERIOD", "2.5 S")], 30)):
        o.append(text(24, 238 + 10 * i, row, 6))
    # second microtext block under the X
    o.append(spread(["NO VOICE, NO ALARM,", "ONLY THE STEADY BEAT"], 232, 376, 274, 10))
    # coral tag: kanji knocked out
    o.append(poly(cut(24, 296, 80, 470, 14), CORAL))
    o.append(rect(48, 306, 8, 8, INKF))
    for ch, y in (("静", 342), ("寂", 368), ("脈", 408)):
        o.append(text(52, y, ch, 22, "xp-j", INKF, "middle"))
    o.append(rect(34, 378, 36, 1.5, INKF))
    o.append(text(52, 452, "11", 22, "xp-d", INKF, "middle"))
    # monolith block with city callouts
    # (the girder monolith printed a step up, in ground-3 on a ground-2 block)
    fx0, fy0, fx1, fy1 = 92, 296, 376, 460
    o.append(rect(fx0, fy0, fx1 - fx0, fy1 - fy0, G2))
    o.append(f'<svg x="{fx0}" y="{fy0}" width="{fx1 - fx0}" height="{fy1 - fy0}" viewBox="0 468 390 {n(390 * (fy1 - fy0) / (fx1 - fx0))}" '
             f'preserveAspectRatio="xMidYMid slice" style="--ground-2:var(--ground-3)"><use href="#g-bg-girder" width="390" height="844"/></svg>')
    o.append(lines(f"M{fx0} {fy0 + 10}V{fy0}H{fx0 + 10}M{fx1 - 10} {fy0}H{fx1}V{fy0 + 10}M{fx1} {fy1 - 10}V{fy1}H{fx1 - 10}M{fx0 + 10} {fy1}H{fx0}V{fy1 - 10}", DIM, 1))
    cities = [("LISBON", "545 K", "100 KM²", "38.7N 9.1W", 100, 306, (136, 384)),
              ("PORTO", "232 K", "41 KM²", "41.1N 8.6W", 284, 306, (270, 370)),
              ("LYON", "522 K", "48 KM²", "45.8N 4.8E", 100, 412, (206, 382)),
              ("OSAKA", "2.7 M", "225 KM²", "34.7N 135.5E", 284, 412, (318, 390))]
    for name, pop, area, loc, x, y, (nx, ny) in cities:
        w = 84
        o.append(rect(x, y, w, 40, GR))
        o.append(rect(x, y, 2, 40, HI))
        o.append(text(x + 6, y + 10, name, 8, "xp-t", HI))
        for i, (a, b) in enumerate((("POPULATION", pop), ("AREA", area), ("LOCATION", loc))):
            o.append(text(x + 6, y + 20 + 8 * i, a, 5.2))
            o.append(text(x + w - 3, y + 20 + 8 * i, b, 5.2, fill=HI, anchor="end"))
        # leader: one '/' run between the plate edge and the node
        ey = y + 40 if ny > y else y
        o.append(lines(f"M{n(nx)} {n(ny)}L{n(nx + ny - ey)} {n(ey)}", DIM, .8))
        o.append(rect(nx - 2.5, ny - 2.5, 5, 5, HI))
        o.append(plus(nx, ny, 7, DIM, .6))
    return o


# ---------------------------------------------------------------- XP·09 SECTOR
def _sector(B):
    o = []
    word, w = B.constructed("S-0", unit=8, x=24, y=52)
    o.append(word)
    o.append(f'<path transform="translate({n(24 + w + 6.4)} 52) scale(8)" d="M0 0H1.4V2.4H4.6V0H6V6H4.6V3.8H0Z" fill="{HI}"/>')
    o.append(text(226, 60, "SECTOR 04 / 08", 10, "xp-t", HI))
    for i, s in enumerate(["GRID 8 × 8 · 64 CELLS · ONE LIT", "REF 38.72 N · 9.14 W · ELEV 112 M", "ROUTES RUN LEVEL OR 45° ONLY"]):
        o.append(text(226, 73 + 10 * i, s, 6))
    gx, gy, p, c = 40, 124, 32, 28
    lit, held, tone, caution, nominal, offline = {(5, 2)}, {(1, 0), (6, 6), (3, 5)}, {(0, 4), (4, 7), (7, 1), (2, 2), (5, 5)}, {(2, 5), (6, 3)}, {(0, 0), (3, 3), (7, 5), (1, 6)}, {(7, 7)}
    for r in range(8):
        o.append(text(30, gy + p * r + 17, str(r + 1), 7.5, "xp-t", DIM, "middle"))
        for col in range(8):
            x, y = gx + p * col, gy + p * r
            pts = cut(x, y, x + c, y + c, 5)
            if (col, r) in lit:
                o.append(poly(pts, CORAL))
            elif (col, r) in held:
                o.append(poly(pts, G3))
            elif (col, r) in tone:
                o.append(poly(pts, G2, f' stroke="{G3}" stroke-width="1"'))
            else:
                o.append(poly(pts, "none", f' stroke="{G3}" stroke-width="1"'))
            if (col, r) in caution:
                o.append(hatch(f"xp9h{col}{r}", x + 1, y + 1, c - 2, c - 2, 3, DIM, .8))
            if (col, r) in nominal:
                o.append(rect(x + 10, y + 10, 8, 8, HI))
            if (col, r) in offline:
                o.append(lines(f"M{x + 9} {y + 9}L{x + 19} {y + 19}M{x + 19} {y + 9}L{x + 9} {y + 19}", DIM, 2))
    for col, ch in enumerate("ABCDEFGH"):
        o.append(text(gx + p * col + c / 2, 116, ch, 7.5, "xp-t", DIM, "middle"))

    def ctr(col, r):
        return gx + p * col + c / 2, gy + p * r + c / 2
    # routes through cell centres, level, upright or '/'; R-1 stops at the lit cell's edge
    routes = [[(0, 7), (2, 7), (5, 4), (5, 2)], [(7, 0), (6, 0), (3, 3), (1, 3)]]
    for k, rt in enumerate(routes):
        pp = [ctr(*q) for q in rt]
        if k == 0:
            pp[-1] = (pp[-1][0], gy + p * 2 + c)
        pts = " ".join(f"{n(a)},{n(b)}" for a, b in pp)
        o.append(f'<polyline points="{pts}" fill="none" stroke="{HI}" stroke-width="{2 if k == 0 else 1.5}" stroke-linejoin="miter"/>')
        for a, b in pp[1:-1]:
            o.append(rect(a - 2.5, b - 2.5, 5, 5, HI))
        a, b = pp[0]
        o.append(rect(a - 4, b - 4, 8, 8, GR, f' stroke="{HI}" stroke-width="1.5"'))
        if k == 1:
            a, b = pp[-1]
            o.append(poly(cut(a - 4, b - 4, a + 4, b + 4, 2), HI))
    # callouts, leaders along the gutters
    calls = [((1, 0), "B-01", ["HELD · DOCK 2", "SINCE 06:10"]),
             ((5, 2), "F-03", ["LIT · LOAD 82%", "ROUTE R-1 END"]),
             ((2, 5), "C-06", ["CAUTION · VENT", "CHECK 11:30"]),
             ((7, 7), "H-08", ["OFFLINE · NO LINK", "LAST 02:14"])]
    for (col, r), title, rows in calls:
        x, y = gx + p * col + c, gy + p * r
        ly = y - 2
        o.append(lines(f"M{x} {y}L{x + 2} {ly}H302", DIM, .8))
        o.append(rect(300.5, ly - 1.5, 3, 3, HI))
        o.append(text(308, ly + 3, title, 8.5, "xp-t", HI))
        for i, s in enumerate(rows):
            o.append(text(308, ly + 12 + 8 * i, s, 5.6))
    o.append(lines("M34 128V118H44M302 128V118H292M34 376V386H44M302 376V386H292", DIM, 1))
    # hazard, legend, scale
    o.append(hazard("xp9z", 24, 396, 352, 12, 10))
    legend = [("sq", "NOMINAL"), ("hatch", "CAUTION"), ("held", "HELD"), ("lit", "LIT"), ("x", "OFFLINE")]
    for i, (kind, label) in enumerate(legend):
        x, y = 24 + i * 71, 422
        if kind == "sq":
            o.append(rect(x, y, 8, 8, HI))
        elif kind == "hatch":
            o.append(rect(x, y, 8, 8, "none", f' stroke="{DIM}" stroke-width=".8"'))
            o.append(hatch("xp9lh", x, y, 8, 8, 3, DIM, .8))
        elif kind == "held":
            o.append(poly(cut(x, y, x + 8, y + 8, 2), G3))
        elif kind == "lit":
            o.append(poly(cut(x, y, x + 8, y + 8, 2), CORAL))
        else:
            o.append(lines(f"M{x} {y}L{x + 8} {y + 8}M{x + 8} {y}L{x} {y + 8}", DIM, 1.6))
        o.append(text(x + 13, y + 7, label, 6))
    o.append(text(24, 448, "R-1 · 7 HOPS · F-03", 6, fill=HI))
    o.append(text(24, 458, "R-2 · 6 HOPS · B-04", 6))
    o.append(lines("M176 452H296M176 449V455M206 450V454M236 449V455M266 450V454M296 449V455", DIM, .8))
    o.append(text(176, 445, "0", 5.4))
    o.append(text(296, 445, "400 M", 5.4, anchor="end"))
    return o


# ---------------------------------------------------------------- XP·10 TRANSIT
def _transit():
    o = []
    o.append(text(24, 60, "LOCAL TIME · LISBON", 6))
    o.append(text(22, 112, "09:41", 62, "xp-d", HI))
    o.append(text(376, 66, "SUN · W47", 6, anchor="end"))
    o.append(text(376, 86, "22 NOV", 15, "xp-d", HI, "end"))
    o.append(text(376, 98, "UTC +00:00", 6, anchor="end"))
    o.append(text(376, 112, ":36", 12, "xp-d", SIG, "end"))
    # slash-step progress
    nstep, h, w = 16, 14, 12
    pitch = (352 - h - w) / (nstep - 1)
    for i in range(nstep):
        x = 24 + i * pitch
        o.append(poly(f"{n(x)},{n(138)} {n(x + w)},{n(138)} {n(x + w + h)},{n(124)} {n(x + h)},{n(124)}", HI if i < 9 else G3))
    o.append(text(24, 152, "BOARDING · 9 / 16", 6))
    o.append(text(376, 152, "GATE CLOSES 09:52", 6, anchor="end"))
    # board
    o.append(rect(24, 160, 352, 1.5, HI))
    for x, s, a in [(32, "Nº", None), (52, "DESTINATION", None), (192, "PLAT", "middle"), (216, "DEPART", None), (290, "STATUS", None)]:
        o.append(text(x, 171, s, 5.8, anchor=a))
    o.append(rect(24, 175, 352, .8, G3))
    rows = [("OSAKA", "VIA LYON · R-12", "04", "09:52", "ok"), ("PORTO", "VIA COIMBRA · R-07", "02", "09:58", "ok"),
            ("LYON", "VIA MADRID · R-02", "07", "10:06", "warn"), ("SEOUL", "VIA OSAKA · R-09", "11", "10:15", "ok"),
            ("REYKJAVIK", "VIA LISBON · R-14", "03", "10:21", "fault"), ("MARSEILLE", "VIA LYON · R-05", "09", "10:34", "warn"),
            ("BERLIN", "VIA LYON · R-03", "05", "10:47", "ok")]
    for i, (city, via, plat, t, st) in enumerate(rows):
        y = 176 + 30 * i
        if i == 0:
            o.append(rect(24, y + 3, 3, 24, CORAL))
        o.append(text(32, y + 15, f"{i + 1:02d}", 6.5, fill=HI if i == 0 else DIM))
        o.append(text(52, y + 15, city, 10.5, "xp-t", HI))
        o.append(text(52, y + 24, via, 5.6))
        o.append(text(192, y + 20, plat, 13, "xp-d", HI, "middle"))
        o.append(text(216, y + 20, t, 13, "xp-d", HI))
        mx, my = 290, y + 9
        if st == "ok":
            o.append(rect(mx, my, 8, 8, HI))
        elif st == "warn":
            o.append(rect(mx + .5, my + .5, 7, 7, "none", f' stroke="{HI}" stroke-width="1"'))
            o.append(hatch(f"xp10h{i}", mx, my, 8, 8, 3, HI, .8))
        else:
            o.append(use("x-solid", mx - 1.5, my - 1.5, 11, 11, CORAL))
        word = {"ok": "NOMINAL", "warn": "CAUTION", "fault": "FAULT"}[st]
        o.append(text(303, y + 16, word, 6.5, fill=SIG if st == "fault" else HI))
        o.append(rect(24, y + 30, 352, .8, G3))
    # ticket
    o.append(poly(cut(24, 400, 376, 458, 10), HI))
    o.append(text(36, 414, "TICKET · SINGLE · 2ND CLASS", 5.8, fill=GR))
    o.append(text(36, 438, "LIS–OSA", 20, "xp-d", GR))
    o.append(text(36, 450, "SEAT 04A · CAR 3 · PLAT 04 · 09:52", 5.8, fill=GR))
    for y in range(404, 456, 5):
        o.append(rect(282, y, 2, 2.5, GR))
    o.append(text(294, 414, "STUB", 5.8, fill=GR))
    o.append(barcode(294, 419, 70, 22, 4, GR))
    o.append(text(294, 450, "Nº 0941 2611", 5.8, fill=GR))
    o.append(text(170, 438, "R-12", 12, "xp-d", GR))
    return o


# ---------------------------------------------------------------- XP·11 PROOF
def _proof():
    o = []
    x0, y0, x1, y1 = 32, 52, 368, 450
    o.append(lines(f"M{x0 - 14} {y0}H{x0 - 4}M{x0} {y0 - 14}V{y0 - 4}M{x1 + 4} {y0}H{x1 + 14}M{x1} {y0 - 14}V{y0 - 4}"
                   f"M{x0 - 14} {y1}H{x0 - 4}M{x0} {y1 + 4}V{y1 + 12}M{x1 + 4} {y1}H{x1 + 14}M{x1} {y1 + 4}V{y1 + 12}", DIM, .8))
    o.append(lines(f"M200 {y0 - 10}V{y0 - 4}M200 {y1 + 4}V{y1 + 10}M{x0 - 10} 251H{x0 - 4}M{x1 + 4} 251H{x1 + 10}", DIM, .8))
    o.append(text(22, 440, "AXIOM PRESS · PROOF 09 · PLATE 1 / 2 · FIRST PULL", 5.4, extra=' transform="rotate(-90 22 440)"'))
    o.append(text(40, 72, "PROOF 09 · INK / SAGE / CORAL", 11, "xp-t", HI))
    o.append(text(40, 84, "SHEET A · TWO INKS AND ONE SIGNAL · 45° SCREEN · 175 LPI", 6))
    o.append(use("reg", 334, 56, 30, 30, HI))
    # colour bar
    sw = [("GROUND", GR, "STRIPE"), ("GROUND-2", G2, "TONE"), ("GROUND-3", G3, "RULES"), ("DIM", DIM, "PRINT 2"), ("HI", HI, "PRINT"), ("CORAL", CORAL, "SIGNAL")]
    pw = 320 / 6
    for i, (name, col, role) in enumerate(sw):
        x = 40 + i * pw
        o.append(rect(x, 96, pw, 28, col))
        o.append(text(x + 2, 133, name, 5.4, fill=HI))
        o.append(text(x + 2, 141, role, 5.4))
    o.append(rect(40, 96, 320, 28, "none", f' stroke="{G3}" stroke-width=".8"'))
    # tonal step wedge
    for i in range(11):
        x = 40 + i * (320 / 11)
        o.append(rect(x, 162, 320 / 11, 18, HI, f' fill-opacity="{i / 10:.1f}"'))
        o.append(text(x + 160 / 11, 188, str(i * 10), 5.2, anchor="middle"))
    o.append(rect(40, 162, 320, 18, "none", f' stroke="{G3}" stroke-width=".8"'))
    o.append(text(40, 157, "TINT · 0–100 %", 5.4, fill=HI))
    # 45° line resolution
    o.append(text(40, 202, "45° RESOLUTION", 5.4, fill=HI))
    for i, (sp, lpi) in enumerate([(6, 25), (4.5, 40), (3.5, 50), (2.5, 75), (1.8, 100)]):
        x = 40 + i * 31
        d = "".join(f"M{n(x + k)} 280L{n(x + k + 72)} 208" for k in [j * sp for j in range(-int(72 / sp) - 1, int(28 / sp) + 1)])
        o.append(f'<clipPath id="xp11r{i}"><rect x="{x}" y="208" width="28" height="72"/></clipPath>'
                 f'<g clip-path="url(#xp11r{i})">{lines(d, HI, sp / 2)}</g>')
        o.append(text(x + 14, 290, str(lpi), 5.2, anchor="middle"))
    o.append(text(40, 299, "LPI", 5.2))
    # stroke ladder
    o.append(text(212, 202, "STROKE WEIGHT", 5.4, fill=HI))
    for i, wgt in enumerate([.25, .5, .75, 1, 1.5, 2, 3, 4]):
        y = 212 + i * 10
        o.append(rect(212, y - wgt / 2, 116, wgt, HI))
        o.append(text(360, y + 2, f"{wgt:g} PT", 5.4, anchor="end"))
    # glyph proof
    o.append(rect(40, 306, 320, .8, G3))
    o.append(text(40, 340, "AXIOM 0123 ØÉÅÇ", 26, "xp-d", HI))
    o.append(text(40, 358, "SIGNAL ABCDEF 456789", 11, "xp-t", HI))
    o.append(text(40, 372, "PLEX MONO 0123456789 +-/× · TELEMETRY", 7, fill=HI))
    o.append(text(40, 390, "信号 校正 見本 機器", 12, "xp-j", HI))
    o.append(text(360, 318, "GLYPH PROOF", 5.4, anchor="end"))
    o.append(rect(40, 398, 320, .8, G3))
    # registration, slur gauges, approval
    o.append(use("reg", 40, 408, 32, 32, HI))
    o.append(lines("".join(f"M84 {410 + k * 2.5}H112" for k in range(12)), HI, 1))
    o.append(lines("".join(f"M{118 + k * 2.5} 410V438" for k in range(12)), HI, 1))
    o.append(text(84, 446, "SLUR · H / V", 5.2))
    for i, (label, on) in enumerate([("CHECKED", True), ("OK TO PRINT", False)]):
        x = 176 + i * 94
        o.append(rect(x, 412, 10, 10, "none", f' stroke="{HI}" stroke-width="1.2"'))
        if on:
            o.append(lines(f"M{x + 2.5} 414.5L{x + 7.5} 419.5M{x + 7.5} 414.5L{x + 2.5} 419.5", HI, 1.6))
        o.append(text(x + 15, 420, label, 6, fill=HI))
        o.append(lines(f"M{x} 438H{x + 84}", DIM, .7))
        o.append(text(x, 446, "SIGN / DATE", 5.2))
    return o


# ---------------------------------------------------------------- XP·12 UNIT
def _unit():
    o = []
    o.append(poly(cut(24, 50, 376, 296, 18), HI))
    for x, y in [(46, 58), (366, 58), (34, 288), (354, 288)]:
        o.append(rect(x - 2.5, y - 2.5, 5, 5, GR))
    o.append(text(40, 76, "AXIOM SIGNAL SYSTEMS", 11, "xp-t", GR))
    o.append(text(360, 75, "FIELD RELAY UNIT", 6, fill=GR, anchor="end"))
    o.append(rect(40, 84, 320, 1, GR))
    o.append(text(40, 98, "MODEL", 6, fill=GR))
    o.append(text(40, 122, "AX-RU 09", 24, "xp-d", GR))
    o.append(text(236, 98, "UNIT 09 / 12", 6, fill=GR))
    for i in range(12):
        x = 236 + i * 10.3
        o.append(rect(x, 106, 8, 14, CORAL if i == 8 else GR, "" if i <= 8 else ' fill-opacity=".35"'))
    o.append(text(40, 140, "SERIAL Nº", 6, fill=GR))
    o.append(text(38, 178, "0941·2611", 34, "xp-d", GR))
    o.append(rect(40, 190, 320, 1, GR))
    spec = leader_rows([("INPUT", "24 V DC"), ("CURRENT", "1.8 A"), ("MASS", "4.2 KG"), ("INGRESS", "IP67"),
                        ("TEMP", "−20 / +55 °C"), ("BUILT", "2026-11")], 30)
    for i, s in enumerate(spec):
        o.append(text(40, 206 + 12 * i, s, 6.6, fill=GR))
    o.append(use("matrix", 296, 200, 64, 64, GR))
    o.append(text(328, 276, "AX/RU/09/2611", 5.4, fill=GR, anchor="middle"))
    # class II (concentric squares), caution, mark
    o.append(rect(222, 202, 22, 22, "none", f' stroke="{GR}" stroke-width="2"'))
    o.append(rect(228, 208, 10, 10, "none", f' stroke="{GR}" stroke-width="2"'))
    o.append(use("warn", 252, 202, 22, 22, GR))
    o.append(use("mark", 222, 236, 22, 22, GR))
    o.append(use("x-line", 252, 236, 22, 22, GR))
    o.append(text(222, 270, "CLASS II · IP67", 5.4, fill=GR))
    # hazard strip
    o.append(hazard("xp12z", 24, 306, 352, 14, 12))
    # trilingual warning, framed in print with a hazard spine
    o.append(rect(24.6, 330.6, 211, 74, "none", f' stroke="{HI}" stroke-width="1.2"'))
    o.append(hazard("xp12s", 25, 331, 10, 73, 8))
    for i, (code, s, cls, size) in enumerate([("EN", "HANDLE WITH CARE", "xp-t", 10), ("JP", "取扱注意", "xp-j", 12), ("FR", "MANIPULER AVEC SOIN", "xp-t", 10)]):
        y = 350 + 22 * i
        o.append(text(44, y, code, 6))
        o.append(text(62, y, s, size, cls, HI))
    o.append(lines("M44 358H230M44 380H230", G3, .8))
    # pictograms
    picts = ["up", "warn", "stack", "lift"]
    for i, kind in enumerate(picts):
        x, y = 248 + i * 32, 330
        o.append(rect(x + .6, y + .6, 26.8, 26.8, "none", f' stroke="{HI}" stroke-width="1.2"'))
        if kind == "up":
            o.append(lines(f"M{x + 9} {y + 22}V{y + 8}M{x + 19} {y + 22}V{y + 8}", HI, 2))
            o.append(poly(f"{x + 5},{y + 11} {x + 9},{y + 7} {x + 13},{y + 11}", HI))
            o.append(poly(f"{x + 15},{y + 11} {x + 19},{y + 7} {x + 23},{y + 11}", HI))
        elif kind == "warn":
            o.append(use("warn", x + 5, y + 5, 18, 18, HI))
        elif kind == "stack":
            o.append(rect(x + 7, y + 15, 14, 8, "none", f' stroke="{HI}" stroke-width="1.5"'))
            o.append(lines(f"M{x + 9} {y + 3}L{x + 19} {y + 13}M{x + 19} {y + 3}L{x + 9} {y + 13}", HI, 1.5))
        else:
            o.append(use("i-send", x + 4, y + 4, 20, 20, HI))
    for i, s in enumerate(["UP", "WARN", "NO STACK", "LIFT"]):
        o.append(text(248 + i * 32 + 14, 366, s, 5, anchor="middle"))
    for i, s in enumerate(["GROSS 6.1 KG · NET 4.2 KG", "STACK MAX 0 · TILT MAX 45°"]):
        o.append(text(248, 384 + 10 * i, s, 5.4))
    # barcode + imprint
    o.append(barcode(24, 418, 140, 30, 12))
    o.append(text(24, 458, "0 941261 109 4", 6, fill=HI))
    for i, s in enumerate(["AXIOM FIELD EQUIPMENT · LISBON", "PN AX-RU-09 / 2611 · REV C", "INSPECTED 2026-11-22 · LOT 47"]):
        o.append(text(180, 426 + 11 * i, s, 6))
    return o


def posters():
    """The six new posters, XP·07 .. XP·12, as SVG strings."""
    B = _build()
    frame = B._xp_frame
    return [
        frame("07", "SPECIMEN", "見本", "SHINGO GRID HEAVY · A–Z / 0–9 · ONE STROKE", "".join(_specimen())),
        frame("08", "PULSE", "脈動", "SILENT PULSE · ABOVE THE NOISE · CHANNEL 11", "".join(_pulse(B))),
        frame("09", "SECTOR", "区画", "64 CELLS · ONE LIT · ROUTES LEVEL OR 45°", "".join(_sector(B))),
        frame("10", "TRANSIT", "発車", "DEPARTURES · LISBON CENTRAL · PLATFORM 04", "".join(_transit())),
        frame("11", "PROOF", "校正", "PROOF 09 · INK / SAGE / CORAL", "".join(_proof())),
        frame("12", "UNIT", "機器", "FIELD RELAY UNIT · AX-RU 09 · SERIAL 0941·2611", "".join(_unit())),
    ]
