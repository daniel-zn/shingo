"""Shingo Grid: the system's own display face.

    python3 tools/font.py

A cut-plate grotesque. Its skeleton is the square, wide-shouldered one Orbitron made
familiar; its corners are the system's own. Every glyph is a plate: bars and stems of one
heavy weight, and wherever a letter would curve the corner is cut at 45° the way every
button, tag and card in Shingō is cut: top-left and bottom-right only, so every cut in a
line of type rises left to right. The other two corners stay square.

The rules, in the order the drawings apply them:

- One heavy weight. Stems SV, bars SH (a shade lighter, so three-bar letters stay open),
  diagonals SD. Letters are a little wider than tall; nothing is condensed.
- Cuts sit top-left and bottom-right, CUT deep, wherever a stroke turns a corner a round
  letter would curve through. The inner corner takes the matching cut, so the stroke
  keeps its weight round the turn. Top-right and bottom-left turns are square.
- Terminals are square. A corner a letter is recognised by stays square too (the 5's top-left,
  the D's top-left, the E's corners).
- Diagonals run at 45°, both ways, as the hard X and the chevrons do. Where one ends on the
  baseline or the cap line it is cut level and its point trimmed by a short upright facet.
- Waists (B 3 8) take a sawtooth: the upper bowl's bottom-right corner is cut, the lower
  bowl starts square. The same cut, the same direction.
- Turned letters agree: the rule survives a half turn, so 6/9, b/q, d/p, n/u, M/W are
  each other rotated.

Glyphs are built as unions of bars, stems and 45° strokes with the cuts subtracted
(skia-pathops), on whole font units, so every edge is level, upright or exactly 45°.

Writes ios/Sources/ShingoKit/Resources/Fonts/ShingoGrid-Heavy.ttf and
web/fonts/ShingoGrid-Heavy.woff2. Capitals, a full lowercase, figures (proportional by
default, tabular under `tnum`), punctuation, € $ % and the accents for English, French and
Portuguese.
"""
import math
import pathlib

import pathops
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

ROOT = pathlib.Path(__file__).resolve().parent.parent
R2 = math.sqrt(2)
UPM = 1000

# ---- the design, in font units -------------------------------------------------------
H = 700            # cap height
X = 540            # x-height
ASC = 740          # ascenders (b d f h k l) rise a little past the caps
DSC = -190         # descenders (g j p q y)
SV, SH = 170, 148  # capitals and figures: stems, bars
SD = 158           # diagonals, measured square to the stroke
LV, LH = 160, 122  # lowercase: stems, bars
LD = 146           # lowercase diagonals
CUT = 150          # the plate cut (outer), capitals and figures
LCUT = 118         # the lowercase cut
FACET = 64         # the upright facet that trims a diagonal's point
SB = 52            # side bearing next to a straight stem
SPACE = 290
WO = 770           # the O; every other width is set against it
WFIG = 720         # one body width for the figures


# ---- geometry kernel -----------------------------------------------------------------
def _path(polys):
    p = pathops.Path()
    pen = p.getPen()
    for pts in polys:
        pen.moveTo(pts[0])
        for q in pts[1:]:
            pen.lineTo(q)
        pen.closePath()
    return p


def _contours(path):
    out, cur = [], []
    for verb, pts in path:
        if verb == pathops.PathVerb.MOVE:
            cur = [pts[0]]
        elif verb == pathops.PathVerb.LINE:
            cur.append(pts[0])
        elif verb == pathops.PathVerb.CLOSE:
            if len(cur) > 2:
                out.append(cur)
            cur = []
    return out


def area(pts):
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1])) / 2


def _union(polys):
    """Union of polygons, whatever way each one winds."""
    acc = None
    for pts in polys:
        p = pathops.simplify(_path([pts]))
        acc = p if acc is None else pathops.op(acc, p, pathops.PathOp.UNION)
    return acc


def resolve(parts):
    """A glyph is a list of parts, each (add, cut, fill): union(add + fill) minus cut.
    Parts are resolved on their own and then joined, so a cut only bites the part it belongs to.
    Returns (outer contours, holes) on whole units, with no repeated or collinear points."""
    acc = None
    for add, cut, fill in parts:
        p = _union(list(add) + list(fill))
        if cut:
            p = pathops.op(p, _union(cut), pathops.PathOp.DIFFERENCE)
        acc = p if acc is None else pathops.op(acc, p, pathops.PathOp.UNION)
    acc = pathops.simplify(acc)
    out = []
    for c in _contours(acc):
        c = [(round(x), round(y)) for x, y in c]
        d = [p for i, p in enumerate(c) if p != c[i - 1]]
        e = [p for i, p in enumerate(d)
             if (p[0] - d[i - 1][0]) * (d[(i + 1) % len(d)][1] - p[1]) != (p[1] - d[i - 1][1]) * (d[(i + 1) % len(d)][0] - p[0])]
        if len(e) > 2 and abs(area(e)) > 1:
            out.append(e)
    if not out:
        return [], []
    sign = area(max(out, key=lambda c: abs(area(c)))) > 0
    return [c for c in out if (area(c) > 0) == sign], [c for c in out if (area(c) > 0) != sign]


def R(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def tri(x, y, sx, sy, a):
    """Triangle at corner (x, y) with legs of length a running in directions sx, sy (±1)."""
    return [(x, y), (x + sx * a, y), (x, y + sy * a)]


def band(x0, y0, y1, T, rising=True):
    """A 45° stroke between heights y0 and y1, T wide measured level.
    Rising runs "/" from bottom-left x0; falling runs "\\" from top-left x0."""
    d = y1 - y0
    if rising:
        return [(x0, y0), (x0 + T, y0), (x0 + T + d, y1), (x0 + d, y1)]
    return [(x0 + d, y0), (x0 + d + T, y0), (x0 + T, y1), (x0, y1)]


def clip(poly, a, b, c):
    """Keep the part of a convex polygon where a*x + b*y + c >= 0."""
    out = []
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        fp, fq = a * p[0] + b * p[1] + c, a * q[0] + b * q[1] + c
        if fp >= 0:
            out.append(p)
        if (fp >= 0) != (fq >= 0):
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def clipbox(poly, x0, x1, y0, y1):
    for a, b, c in ((1, 0, -x0), (-1, 0, x1), (0, 1, -y0), (0, -1, y1)):
        poly = clip(poly, a, b, c)
    return poly


def mirror(poly, w):
    return [(w - x, y) for x, y in poly]


def turn(poly, w, h):
    """Half a turn about the centre of a w × h cell."""
    return [(w - x, h - y) for x, y in poly]


def shift(poly, dx, dy=0):
    return [(x + dx, y + dy) for x, y in poly]


def diag(s):
    """Level width of a 45° stroke s thick, kept even so centred strokes land on whole units."""
    return 2 * round(s * R2 / 2)


CORNER = {"tl": (0, 1, 1, -1), "tr": (1, 1, -1, -1), "br": (1, 0, -1, 1), "bl": (0, 0, 1, 1)}


class Pen:
    """The drawing rules for one set of weights (capitals and figures, or the lowercase)."""

    def __init__(self, sv, sh, sd, cut):
        self.sv, self.sh, self.cut = sv, sh, cut
        self.T = diag(sd)
        self.k = round((sv + sh) * (1 - 1 / R2))      # outer cut minus inner cut, for a turn that keeps its weight

    def corner(self, x0, y0, x1, y1, name, c=None, inner=True):
        """Cut the named corner of the box (x0, y0, x1, y1): (cut triangles, inner fills)."""
        ix, iy, sx, sy = CORNER[name]
        c = self.cut if c is None else c
        ox, oy = (x1 if ix else x0), (y1 if iy else y0)
        ci = c - self.k
        fill = [tri(ox + sx * self.sv, oy + sy * self.sh, sx, sy, ci)] if inner and ci > 0 else []
        return [tri(ox, oy, sx, sy, c)], fill

    def box(self, x0, y0, x1, y1, sides="tblr", cuts="tl br", c=None):
        """Bars and stems round a box, with the named corners cut. sides: t b l r."""
        add, cut, fill = [], [], []
        if "t" in sides:
            add.append(R(x0, y1 - self.sh, x1, y1))
        if "b" in sides:
            add.append(R(x0, y0, x1, y0 + self.sh))
        if "l" in sides:
            add.append(R(x0, y0, x0 + self.sv, y1))
        if "r" in sides:
            add.append(R(x1 - self.sv, y0, x1, y1))
        for n in cuts.split():
            a, b = self.corner(x0, y0, x1, y1, n, c, inner=all(s in sides for s in n))
            cut += a
            fill += b
        return add, cut, fill

    def path(self, bars, *corners):
        """Bars plus the corners they turn: each corner is (box, name[, size])."""
        cut, fill = [], []
        for bx, name, *size in corners:
            a, b = self.corner(*bx, name, *(size or [None]))
            cut += a
            fill += b
        return list(bars), cut, fill


def solid(*polys):
    return list(polys), [], []


# ---- capitals ------------------------------------------------------------------------
def capitals():
    p = Pen(SV, SH, SD, CUT)
    T, f = p.T, FACET
    M = H // 2
    mb, mt = M - SH // 2, M + SH // 2          # the middle bar, on the centre line
    g = {}

    # plates: O D C U and the flat-topped A
    g["O"] = (WO, [p.box(0, 0, WO, H)])
    g["D"] = (WO, [p.box(0, 0, WO, H, cuts="br")])
    wc = WO - 50
    g["C"] = (wc, [p.box(0, 0, wc, H, "tbl", "tl")])
    wu = WO - 10
    g["U"] = (wu, [p.box(0, 0, wu, H, "lbr", "br")])
    ya = 230                                   # the A's bar sits low, so the eye above it stays open
    g["A"] = (WO, [p.box(0, 0, WO, H, "tlr", "tl"), solid(R(0, ya, WO, ya + SH))])

    # stems and arms: no turn a round letter would make, so no cuts
    g["H"] = (WO, [solid(R(0, 0, SV, H), R(WO - SV, 0, WO, H), R(0, mb, WO, mt))])
    we = 680
    g["E"] = (we, [solid(R(0, 0, SV, H), R(0, H - SH, we, H), R(0, 0, we, SH), R(0, mb, we - 60, mt))])
    wf = 650
    g["F"] = (wf, [solid(R(0, 0, SV, H), R(0, H - SH, wf, H), R(0, mb, wf - 70, mt))])
    wl = 640
    g["L"] = (wl, [solid(R(0, 0, SV, H), R(0, 0, wl, SH))])
    wt = 720
    g["T"] = (wt, [solid(R(0, H - SH, wt, H), R(wt // 2 - SV // 2, 0, wt // 2 + SV // 2, H))])
    g["I"] = (SV, [solid(R(0, 0, SV, H))])
    wj = 640
    g["J"] = (wj, [p.box(0, 0, wj, H, "br", "br"), solid(R(0, 0, SV, 250))])

    # S: cut at the two extremes, square at the waist
    ws = WO - 30
    g["S"] = (ws, [p.path([R(0, H - SH, ws, H), R(0, mb, SV, H), R(0, mb, ws, mt), R(ws - SV, 0, ws, mt), R(0, 0, ws, SH)],
                          ((0, 0, ws, H), "tl"), ((0, 0, ws, H), "br"))])
    # G: the C, a lower right stem and a spur back to the centre
    g["G"] = (WO, [p.path([R(0, H - SH, WO, H), R(0, 0, SV, H), R(0, 0, WO, SH), R(WO - SV, 0, WO, mt), R(350, mb, WO, mt)],
                          ((0, 0, WO, H), "tl"), ((0, 0, WO, H), "br"))])
    # B: two bowls and the sawtooth waist
    wb = WO - 30
    n = 70                                     # the sawtooth's depth
    bc, bf = p.corner(0, 0, wb, H, "br")
    g["B"] = (wb, [([R(0, 0, SV, H), R(0, H - SH, wb, H), R(0, mb, wb, mt), R(0, 0, wb, SH), R(wb - SV, 0, wb, H)],
                    bc + [tri(wb, M, -1, 1, n)], bf)])
    # P and R: a tall bowl with its bottom-right cut; the R's leg runs out of the bowl at 45° onto a facet
    yb = 250
    wp = WO - 40
    g["P"] = (wp, [p.path([R(0, 0, SV, H), R(0, H - SH, wp, H), R(0, yb, wp, yb + SH), R(wp - SV, yb, wp, H)], ((0, yb, wp, H), "br"))])
    wr = WO - 20
    ytop = yb + SH // 2
    leg = clipbox(band(wr + f - T - ytop, 0, ytop, T, rising=False), 0, wr, 0, ytop)
    g["R"] = (wr, [p.path([R(0, 0, SV, H), R(0, H - SH, wr, H), R(0, yb, wr, yb + SH), R(wr - SV, yb, wr, H)], ((0, yb, wr, H), "br")),
                   solid(leg)])
    # Q: where the O's bottom-right corner is cut away, the Q's is pushed out: a short 45° tooth
    # square across the corner, its end cut level on a facet
    tq = diag(124)
    cx, cy = WO - SV // 2, SH // 2             # the corner joint's centre
    tooth = clipbox(band(cx - tq // 2 - (cy + 150), -150, 262, tq, rising=False), WO - SV - 150, WO + 76, -116, 262)
    g["Q"] = (WO + 76, [p.box(0, 0, WO, H, cuts="tl"), solid(tooth)])

    # diagonals
    xv = 380                                   # K: the arms meet at a short neck on the stem
    wk = xv + M - f
    up = clipbox(band(xv - T - M, 0, H, T), 0, wk, M, H)
    dn = clipbox(band(xv - T - M, 0, H, T, rising=False), 0, wk, 0, M)
    g["K"] = (wk, [solid(R(0, 0, SV, H), up, dn)])
    wx = H + T - 2 * f
    g["X"] = (wx, [solid(clipbox(band(-f, 0, H, T), 0, wx, 0, H), clipbox(band(-f, 0, H, T, rising=False), 0, wx, 0, H))])
    # V: the shield. Stems down to the break, then 45° to a short flat
    wv, fl = 780, 116
    yo = wv // 2 - fl // 2
    yi = yo + T - SV
    g["V"] = (wv, [([[(0, H), (0, yo), (yo, 0), (wv - yo, 0), (wv, yo), (wv, H)]],
                    [[(SV, H + 10), (SV, yi), (wv // 2, yi - (wv // 2 - SV)), (wv - SV, yi), (wv - SV, H + 10)]], [])])
    # Y: arms land on facets at the top and meet over the stem
    wy = 780
    stop = H - (wy // 2 - SV // 2 + f)
    arm = clipbox(band(-f, stop, H, T, rising=False), 0, wy // 2, stop, H)
    g["Y"] = (wy, [solid(arm, mirror(arm, wy), R(wy // 2 - SV // 2, 0, wy // 2 + SV // 2, stop + 1))])
    # M: the stems carry a 45° V whose point is cut level; W is the M turned over
    wm, ft = 930, 44
    marm = clipbox(band(0, 0, H, T, rising=False), 0, wm // 2, H - wm // 2 + ft, H)
    mparts = [R(0, 0, SV, H), R(wm - SV, 0, wm, H), marm, mirror(marm, wm)]
    g["M"] = (wm, [solid(*mparts)])
    g["W"] = (wm, [solid(*[turn(q, wm, H) for q in mparts])])
    # N: one 45° stroke through the centre, running into both stems
    wn = 790
    g["N"] = (wn, [solid(R(0, 0, SV, H), R(wn - SV, 0, wn, H), clipbox(band(wn // 2 - M - T // 2, 0, H, T, rising=False), 0, wn, 0, H))])
    # Z: the diagonal lands exactly on the bars' inner corners, so the width follows from the 45°
    wz = H - 2 * SH + T
    g["Z"] = (wz, [solid(R(0, H - SH, wz, H), R(0, 0, wz, SH), band(0, SH - 2, H - SH + 2, T))])
    # Ø: the O with a slash running out through both square corners
    sl = diag(118)
    g["Ø"] = (WO, [p.box(0, 0, WO, H), solid(clipbox(band(WO // 2 - sl // 2 - M - 70, -70, H + 70, sl), -40, WO + 40, -70, H + 70))])
    return g


# ---- figures -------------------------------------------------------------------------
def figures():
    """One system for all ten: the capitals' weights and cuts on one body width.
    2 and S/5 are complements: the S and 5 are cut at their extremes with a square waist,
    the 2 is square at its extremes and cut at both waist turns, so its neck runs "/"."""
    p = Pen(SV, SH, SD, CUT)
    T, f, W = p.T, FACET, WFIG
    M = H // 2
    mb, mt = M - SH // 2, M + SH // 2
    n = 70
    g = {}
    # 0: narrower than the O, with a slash from square corner to square corner
    ts = diag(108)
    sl = clipbox(band(W // 2 - ts // 2 - M, 0, H, ts), SV - 2, W - SV + 2, SH - 2, H - SH + 2)
    g["0"] = (W, [p.box(0, 0, W, H), solid(sl)])
    # 1: a stem and a flag whose end is cut right through at 45°
    fa = 200
    g["1"] = (fa + SV, [([R(fa, 0, fa + SV, H), R(0, H - SH, fa + SV, H)], [tri(0, H, 1, -1, SH)], [])])
    g["2"] = (W, [p.path([R(0, H - SH, W, H), R(W - SV, mb, W, H), R(0, mb, W, mt), R(0, 0, SV, mt), R(0, 0, W, SH)],
                         ((0, 0, W, mt), "tl"), ((0, mb, W, H), "br"))])
    c3, f3 = p.corner(0, 0, W, H, "br")
    g["3"] = (W, [([R(0, H - SH, W, H), R(W - SV, 0, W, H), R(220, mb, W, mt), R(0, 0, W, SH)], c3 + [tri(W, M, -1, 1, n)], f3)])
    # 4: closed. A 45° stroke from the bar's end up into the stem; the bar runs a little past the stem
    y4, ov = 150, 46
    sr = W - ov
    d4 = clipbox(band(sr - T - (H - y4), y4, H, T), 0, W, y4, H)
    g["4"] = (W, [solid(R(sr - SV, 0, sr, H), R(0, y4, W, y4 + SH), d4)])
    g["5"] = (W, [p.path([R(0, H - SH, W, H), R(0, mb, SV, H), R(0, mb, W, mt), R(W - SV, 0, W, mt), R(0, 0, W, SH)], ((0, 0, W, H), "br"))])
    six = p.path([R(0, H - SH, W, H), R(0, 0, SV, H), R(0, mb, W, mt), R(W - SV, 0, W, mt), R(0, 0, W, SH)],
                 ((0, 0, W, H), "tl"), ((0, 0, W, mt), "br"))
    g["6"] = (W, [six])
    g["9"] = (W, [tuple([turn(q, W, H) for q in lst] for lst in six)])
    # 7: the bar and a 45° leg down to a facet
    g["7"] = (W, [solid(R(0, H - SH, W, H), clipbox(band(W - T - (H - SH), 0, H - SH + 2, T), 0, W, 0, H))])
    c8, f8 = p.corner(0, 0, W, H, "tl")
    c8b, f8b = p.corner(0, 0, W, H, "br")
    g["8"] = (W, [([R(0, H - SH, W, H), R(0, 0, W, SH), R(0, 0, SV, H), R(W - SV, 0, W, H), R(0, mb, W, mt)],
                   c8 + c8b + [tri(W, M, -1, 1, n), tri(0, M, 1, -1, n)], f8 + f8b)])
    # the tabular 1 stands on a foot, so it fills its cell
    foot = 500
    x1 = (foot - SV) // 2
    g["1.tnum"] = (foot, [([R(x1, 0, x1 + SV, H), R(x1 - fa, H - SH, x1 + SV, H), R(0, 0, foot, SH)], [tri(x1 - fa, H, 1, -1, SH)], [])])
    return g


# ---- punctuation and symbols ----------------------------------------------------------
def punctuation():
    p = Pen(SV, SH, SD, CUT)
    T, f = p.T, FACET
    M = H // 2
    mb, mt = M - SH // 2, M + SH // 2
    dot = SV                                   # points are stem-wide squares
    g = {}
    g["."] = (dot, [solid(R(0, 0, dot, dot))])
    tail = [R(0, 0, dot, dot), R(0, -120, 92, 0)]
    g[","] = (dot, [solid(*tail)])
    cy = 96                                    # the colon's points sit centred on the figures
    g[":"] = (dot, [solid(R(0, M - cy - dot, dot, M - cy), R(0, M + cy, dot, M + cy + dot))])
    g[";"] = (dot, [solid(*tail, R(0, M + cy, dot, M + cy + dot))])
    g["…"] = (dot * 5, [solid(R(0, 0, dot, dot), R(dot * 2, 0, dot * 3, dot), R(dot * 4, 0, dot * 5, dot))])
    g["·"] = (140, [solid(R(0, M - 70, 140, M + 70))])
    g["-"] = (380, [solid(R(0, mb, 380, mt))])
    g["–"] = (560, [solid(R(0, mb, 560, mt))])
    g["—"] = (860, [solid(R(0, mb, 860, mt))])
    g["_"] = (600, [solid(R(0, -170, 600, -40))])
    g["!"] = (dot, [solid(R(0, dot + 80, dot, H), R(0, 0, dot, dot))])
    wq = 640
    xs = wq // 2 - SV // 2 - 20
    g["?"] = (wq, [p.path([R(0, H - SH, wq, H), R(wq - SV, mb, wq, H), R(xs, mb, wq, mt), R(xs, dot + 80, xs + SV, mt)], ((xs, mb, wq, H), "br")),
                   solid(R(xs, 0, xs + SV, dot))])
    qh = 250
    g["'"] = (140, [solid(R(0, H - qh, 140, H))])
    g['"'] = (370, [solid(R(0, H - qh, 140, H), R(230, H - qh, 370, H))])
    g["’"] = (dot, [solid(R(0, H - dot, dot, H), R(dot - 92, H - dot - 120, dot, H - dot))])
    g["‘"] = (dot, [solid(R(0, H - dot, dot, H), R(0, H - dot - 120, 92, H - dot))])
    # the slash and the percent: the system's one diagonal on a facet at each end
    fs = 150
    ws = H + T - 2 * fs
    g["/"] = (ws, [solid(clipbox(band(-fs, 0, H, T), 0, ws, 0, H))])
    # percent: two small plate rings with the slash squeezed between them on tall facets
    dq, dst = 256, 84
    rp = Pen(dst, dst, dst, 76)
    gapp = 40
    xp = dq + gapp - (H - dq)                  # the slash clears the upper ring by gapp
    wpc = 2 * (dq + gapp) + T - (H - 2 * dq)
    g["%"] = (wpc, [solid(clipbox(band(xp, 0, H, T), dq // 2, wpc - dq // 2, 0, H)), rp.box(0, H - dq, dq, H), rp.box(wpc - dq, 0, wpc, dq)])
    g["+"] = (520, [solid(R(0, mb, 520, mt), R(260 - SH // 2, M - 260, 260 + SH // 2, M + 260))])
    g["="] = (520, [solid(R(0, M + 46, 520, M + 46 + 128), R(0, M - 46 - 128, 520, M - 46))])
    # times: a small X on facets
    th, tt = 400, diag(124)
    tw = th + tt - 2 * 44
    g["×"] = (tw, [solid(shift(clipbox(band(-44, 0, th, tt), 0, tw, 0, th), 0, M - th // 2),
                         shift(clipbox(band(-44, 0, th, tt, rising=False), 0, tw, 0, th), 0, M - th // 2))])
    # degree and ordinal: a small plate ring at the cap line
    dg, ds = 270, 88
    ring = Pen(ds, ds, ds, 76).box(0, H - dg, dg, H)
    g["°"] = (dg, [ring])
    g["º"] = (dg, [ring, solid(R(0, H - dg - 110, dg, H - dg - 40))])
    bw, top, bot = 330, H + 60, -150           # brackets: square; parentheses: brackets with the plate cuts
    g["["] = (bw, [solid(R(0, bot, SV, top), R(0, top - SH, bw, top), R(0, bot, bw, bot + SH))])
    g["]"] = (bw, [solid(R(bw - SV, bot, bw, top), R(0, top - SH, bw, top), R(0, bot, bw, bot + SH))])
    g["("] = (bw, [p.box(0, bot, bw, top, "tbl", "tl")])
    g[")"] = (bw, [p.box(0, bot, bw, top, "tbr", "br")])
    # angle brackets: two 45° strokes meeting in a point, free ends on facets
    aa = 250
    aw = T + aa - f
    upa = clipbox(band(0, M, M + aa, T), 0, aw, M, M + aa)
    dna = clipbox(band(0, M - aa, M, T, rising=False), 0, aw, M - aa, M)
    g["<"] = (aw, [solid(upa, dna)])
    g[">"] = (aw, [solid(mirror(upa, aw), mirror(dna, aw))])
    g["*"] = (400, [solid(R(200 - 60, H - 400, 200 + 60, H), R(0, H - 200 - 60, 400, H - 200 + 60))])
    g["#"] = (760, [solid(R(0, M + 60, 760, M + 60 + 124), R(0, M - 60 - 124, 760, M - 60), R(170, 30, 170 + 140, H - 30), R(450, 30, 450 + 140, H - 30))])
    # euro: the C with two bars through its stem
    we = 740
    g["€"] = (we, [p.box(70, 0, we, H, "tbl", "tl"), solid(R(0, M + 30, 470, M + 30 + 104), R(0, M - 30 - 104, 470, M - 30))])
    # dollar: the S with a bar showing above and below it
    ws_ = WO - 30
    g["$"] = (ws_, [p.path([R(0, H - SH, ws_, H), R(0, mb, SV, H), R(0, mb, ws_, mt), R(ws_ - SV, 0, ws_, mt), R(0, 0, ws_, SH)],
                           ((0, 0, ws_, H), "tl"), ((0, 0, ws_, H), "br")),
                    solid(R(ws_ // 2 - 62, H - 2, ws_ // 2 + 62, H + 84), R(ws_ // 2 - 62, -84, ws_ // 2 + 62, 2))])
    # ampersand: a small plate loop over an open bowl, a 45° leg from the waist to the baseline
    wa = 780
    lx0, lx1, ly0 = 80, 560, 300               # the loop
    loop = p.box(lx0, ly0, lx1, H, c=110)
    bx1 = 640                                  # the bowl: open to the right, bottom bar full
    bowl = p.path([R(0, ly0, lx1, ly0 + SH), R(0, 0, SV, ly0 + SH), R(0, 0, bx1, SH)], ((0, 0, bx1, ly0 + SH), "tl", 110))
    leg = clipbox(band(wa + f - T - (ly0 + SH // 2), 0, ly0 + SH // 2, T, rising=False), 0, wa, 0, ly0 + SH)
    g["&"] = (wa, [loop, bowl, solid(leg)])
    # at: a plate frame open at the lower right, a solid core, the tail running out along the baseline
    g["@"] = (WO, [p.box(0, 0, WO, H, "tbl", "tl"), solid(R(WO - SV, 250, WO, H), R(300, 250, WO, 250 + 190), R(300, 250, 300 + 190, 450), R(300, 0, WO, SH))])
    return g


# ---- lowercase -----------------------------------------------------------------------
def lowercase():
    """The capitals' rules at x-height. Bars are lighter (LH) so the three-bar letters (a e s)
    keep their counters; cuts scale with the x-height. The rule survives a half turn, so
    n/u, b/q, d/p and m/w are each other rotated."""
    p = Pen(LV, LH, LD, LCUT)
    T, f = p.T, 56
    wo = 610                                   # the o; bowls share it
    g = {}
    mb = (X - LH) // 2                         # middle bar (a e s)
    mt = mb + LH

    g["o"] = (wo, [p.box(0, 0, wo, X)])
    wc = wo - 50
    g["c"] = (wc, [p.box(0, 0, wc, X, "tbl", "tl")])
    # e: the eye closed by the middle bar, open below it
    g["e"] = (wo, [p.path([R(0, X - LH, wo, X), R(0, 0, LV, X), R(wo - LV, mb, wo, X), R(0, mb, wo, mt), R(0, 0, wo, LH)], ((0, 0, wo, X), "tl", 100))])
    # a: two storeys. The top bar and a full right stem; the bowl hangs on the stem
    wa = wo - 20
    g["a"] = (wa, [p.path([R(30, X - LH, wa, X), R(wa - LV, 0, wa, X), R(0, mb, wa, mt), R(0, 0, LV, mt), R(0, 0, wa, LH)], ((0, 0, wa, mt), "tl", 100))])
    ws = wo - 30
    g["s"] = (ws, [p.path([R(0, X - LH, ws, X), R(0, mb, LV, X), R(0, mb, ws, mt), R(ws - LV, 0, ws, mt), R(0, 0, ws, LH)],
                          ((0, 0, ws, X), "tl", 100), ((0, 0, ws, X), "br", 100))])
    # b d p q: a bowl on a stem; the bowl's free corner on the cut diagonal is cut
    g["b"] = (wo, [p.box(0, 0, wo, X, "tbr", "br"), solid(R(0, 0, LV, ASC))])
    g["d"] = (wo, [p.box(0, 0, wo, X, "tbl", "tl"), solid(R(wo - LV, 0, wo, ASC))])
    g["p"] = (wo, [p.box(0, 0, wo, X, "tbr", "br"), solid(R(0, DSC, LV, X))])
    g["q"] = (wo, [p.box(0, 0, wo, X, "tbl", "tl"), solid(R(wo - LV, DSC, wo, X))])
    # descender hooks: the stem turns left along the descender; its corner is a bottom-right one, so it is cut
    hc = 96
    def hook(xr, x0):
        return p.path([R(xr - LV, DSC, xr, X), R(x0, DSC, xr, DSC + LH)], ((x0 - LV, DSC, xr, X), "br", hc))
    g["g"] = (wo, [p.box(0, 0, wo, X, "tbl", "tl"), hook(wo, 70)])
    # n u h m r: the arch's top-left and the cup's bottom-right are cut; n is the u turned
    wn = wo - 20
    g["n"] = (wn, [p.box(0, 0, wn, X, "tlr", "tl")])
    g["u"] = (wn, [p.box(0, 0, wn, X, "lbr", "br")])
    g["h"] = (wn, [solid(R(0, 0, LV, ASC), R(0, X - LH, wn, X), R(wn - LV, 0, wn, X))])
    wm = 900
    marc = p.box(0, 0, wm, X, "tlr", "tl")
    mstem = R(wm // 2 - LV // 2, 0, wm // 2 + LV // 2, X)
    g["m"] = (wm, [marc, solid(mstem)])
    g["w"] = (wm, [tuple([turn(q, wm, X) for q in lst] for lst in marc), solid(mstem)])
    wr = 400
    g["r"] = (wr, [p.box(0, 0, wr, X, "tl", "tl")])
    # i j l: stems; the points are stem-wide squares
    gap = 64
    dot = lambda x: R(x, X + gap, x + LV, X + gap + 136)
    g["ı"] = (LV, [solid(R(0, 0, LV, X))])
    g["i"] = (LV, [solid(R(0, 0, LV, X), dot(0))])
    wj = 300
    g["j"] = (wj, [hook(wj, 0), solid(dot(wj - LV))])
    g["l"] = (LV, [solid(R(0, 0, LV, ASC))])
    # t f: a stem crossed at the x-height; the t stands on a square foot, the f's head is cut
    xs = 70
    wt = xs + LV + 150
    g["t"] = (wt, [solid(R(xs, 0, xs + LV, ASC - 60), R(0, X - LH, wt, X), R(xs, 0, wt, LH))])
    wf = xs + LV + 170
    g["f"] = (wf, [p.box(xs, 0, wf, ASC, "tl", "tl", c=100), solid(R(0, X - LH, wf - 30, X))])
    # k v x y z: the capitals' diagonals at x-height
    M = X // 2
    xv = 310
    wk = xv + M - f
    g["k"] = (wk, [solid(R(0, 0, LV, ASC), clipbox(band(xv - T - M, 0, X, T), 0, wk, M, X),
                         clipbox(band(xv - T - M, 0, X, T, rising=False), 0, wk, 0, M))])
    wv, fl = 620, 100
    yo = wv // 2 - fl // 2
    yi = yo + T - LV
    g["v"] = (wv, [([[(0, X), (0, yo), (yo, 0), (wv - yo, 0), (wv, yo), (wv, X)]],
                    [[(LV, X + 10), (LV, yi), (wv // 2, yi - (wv // 2 - LV)), (wv - LV, yi), (wv - LV, X + 10)]], [])])
    wx = X + T - 2 * f
    g["x"] = (wx, [solid(clipbox(band(-f, 0, X, T), 0, wx, 0, X), clipbox(band(-f, 0, X, T, rising=False), 0, wx, 0, X))])
    g["y"] = (wn, [p.box(0, 0, wn, X, "lb", ""), hook(wn, 70)])
    wz = X - 2 * LH + T
    g["z"] = (wz, [solid(R(0, X - LH, wz, X), R(0, 0, wz, LH), band(0, LH - 2, X - LH + 2, T))])
    return g


# ---- accents -------------------------------------------------------------------------
def _ab(x0, h, w, rising=True):
    return band(x0, 0, h, w, rising)


AS = 124   # accent stroke
ACCENTS = {  # shapes over the cap height or x-height, centred on 0: 45° strokes cut level, like the letters' diagonals
    "acute": lambda: [_ab(-150, 150, 150)],
    "grave": lambda: [_ab(-150, 150, 150, rising=False)],
    "circ": lambda: [[(-230, 0), (-90, 0), (0, 90), (90, 0), (230, 0), (60, 150), (-60, 150)]],
    "uml": lambda: [R(-210, 0, -70, 130), R(70, 0, 210, 130)],
    "macron": lambda: [R(-230, 0, 230, 104)],
    "tilde": lambda: [_ab(-250, 120, 110), [(x + 120, y) for x, y in _ab(-250, 120, 110, rising=False)], [(x + 240, y) for x, y in _ab(-250, 120, 110)]],
}
COMPOSED = {
    "À": ("A", "grave"), "Á": ("A", "acute"), "Â": ("A", "circ"), "Ä": ("A", "uml"), "Ã": ("A", "tilde"), "Å": ("A", "ring"), "Ā": ("A", "macron"),
    "È": ("E", "grave"), "É": ("E", "acute"), "Ê": ("E", "circ"), "Ë": ("E", "uml"), "Ē": ("E", "macron"),
    "Ì": ("I", "grave"), "Í": ("I", "acute"), "Î": ("I", "circ"), "Ï": ("I", "uml"),
    "Ò": ("O", "grave"), "Ó": ("O", "acute"), "Ô": ("O", "circ"), "Ö": ("O", "uml"), "Õ": ("O", "tilde"), "Ō": ("O", "macron"),
    "Ù": ("U", "grave"), "Ú": ("U", "acute"), "Û": ("U", "circ"), "Ü": ("U", "uml"), "Ū": ("U", "macron"),
    "Ñ": ("N", "tilde"), "Ý": ("Y", "acute"), "Ÿ": ("Y", "uml"),
    # lowercase: the same marks over the x-height; the i takes them on the dotless ı
    "à": ("a", "grave"), "á": ("a", "acute"), "â": ("a", "circ"), "ä": ("a", "uml"), "ã": ("a", "tilde"), "å": ("a", "ring"), "ā": ("a", "macron"),
    "è": ("e", "grave"), "é": ("e", "acute"), "ê": ("e", "circ"), "ë": ("e", "uml"), "ē": ("e", "macron"),
    "ì": ("ı", "grave"), "í": ("ı", "acute"), "î": ("ı", "circ"), "ï": ("ı", "uml"), "ī": ("ı", "macron"),
    "ò": ("o", "grave"), "ó": ("o", "acute"), "ô": ("o", "circ"), "ö": ("o", "uml"), "õ": ("o", "tilde"), "ō": ("o", "macron"),
    "ù": ("u", "grave"), "ú": ("u", "acute"), "û": ("u", "circ"), "ü": ("u", "uml"), "ū": ("u", "macron"),
    "ñ": ("n", "tilde"), "ý": ("y", "acute"), "ÿ": ("y", "uml"),
}
ACCENT_GAP = 58


def glyphs():
    """Every glyph as (body width, parts)."""
    g = {}
    g.update(capitals())
    g.update(figures())
    g.update(punctuation())
    g.update(lowercase())
    ring = Pen(84, 84, 84, 70).box(-125, 0, 125, 230)
    for ch, (base, acc) in COMPOSED.items():
        w, parts = g[base]
        top = (X if base.islower() or base == "ı" else H) + ACCENT_GAP
        dx = w // 2
        if acc == "ring":
            mark = [tuple([shift(q, dx, top) for q in lst] for lst in ring)]
        else:
            polys = ACCENTS[acc]()
            if acc == "macron" and base == "ı":
                polys = [R(-150, 0, 150, 104)]
            mark = [solid(*[shift(q, dx, top) for q in polys])]
        g[ch] = (w, parts + mark)
    for ch, base in (("Ç", "C"), ("ç", "c")):
        w, parts = g[base]
        cx = w // 2
        g[ch] = (w, parts + [solid(R(cx - 62, -90, cx + 62, 2), shift(_ab(-150, 110, 150), cx, -190))])
    return g


# ---- spacing -------------------------------------------------------------------------
def ink_left(shapes, y):
    """Leftmost ink at height y across all contours (None if the row is empty)."""
    best = None
    for pts in shapes:
        for (xa, ya), (xb, yb) in zip(pts, pts[1:] + pts[:1]):
            if (ya <= y < yb) or (yb <= y < ya):
                x = xa + (y - ya) * (xb - xa) / (yb - ya)
                best = x if best is None else min(best, x)
    return best


def side_space(ch, shapes):
    """Optical spacing. Each side gets the base bearing minus part of the white it already
    holds, so open and diagonal sides (C, E, K, L, T, X, Y, 7) sit as close as straight stems
    do. Punctuation keeps the plain bearing."""
    xs = [x for pts in shapes for x, _ in pts]
    x0, x1 = min(xs), max(xs)
    if not ch.isalnum():
        return SB, SB, x0, x1
    mirrored = [[(-x, y) for x, y in pts] for pts in shapes]
    top = X if ch.islower() else H                  # lowercase meet their neighbours in the x-height
    out = []
    for side, x_edge in ((shapes, x0), (mirrored, -x1)):
        gaps = []
        for y in range(10, top, 20):
            e = ink_left(side, y)
            gaps.append(min(240, (e - x_edge) if e is not None else 240))
        out.append(max(SB * .3, SB - .34 * (sum(gaps) / len(gaps))))
    l, r = TRIM.get(ch, (0, 0))
    return out[0] - l, out[1] - r, x0, x1


# open sides the measure under-reads: (left, right) trims in units
TRIM = {"C": (0, 22), "G": (0, 6), "L": (0, 30), "J": (22, 0), "F": (0, 20), "E": (0, 14), "T": (10, 10), "S": (4, 4),
        "c": (0, 20), "r": (0, 34), "f": (0, 24), "t": (0, 20), "j": (16, 0), "e": (0, 8), "a": (6, 0), "s": (4, 4)}

# pairs the optical spacing cannot fix on its own (units of 1/1000 em). The face is square-shouldered,
# so the classic diagonal pairs (AV, TA) need nothing; what is left are the open corners.
KERN = {("L", "T"): -90, ("L", "Y"): -80, ("L", "V"): -24, ("L", "7"): -60, ("L", "’"): -110, ("L", "4"): -50,
        ("T", "J"): -70, ("Y", "J"): -60, ("F", "J"): -70, ("P", "J"): -70,
        ("P", "."): -110, ("P", ","): -110, ("F", "."): -110, ("F", ","): -110, ("T", "."): -90, ("T", ","): -90,
        ("Y", "."): -90, ("Y", ","): -90, ("7", "."): -90, ("7", ","): -90, ("r", "."): -90, ("r", ","): -90,
        ("K", "T"): -20, ("X", "T"): -20, ("T", "X"): -20, ("Y", "X"): -24, ("X", "Y"): -24, ("K", "Y"): -24,
        ("R", "T"): -30, ("R", "Y"): -36, ("T", "Z"): -20, ("Z", "T"): -20, ("Z", "Z"): -16,
        ("T", "T"): -24, ("T", "Y"): -24, ("Y", "T"): -24, ("Y", "Y"): -30, ("7", "7"): -30,
        ("L", "t"): -40, ("L", "y"): -30, ("T", "a"): -56, ("T", "e"): -56, ("T", "o"): -56, ("T", "c"): -56, ("T", "s"): -50,
        ("T", "r"): -40, ("T", "u"): -40, ("T", "n"): -40, ("T", "m"): -40, ("T", "y"): -40,
        ("Y", "a"): -60, ("Y", "e"): -60, ("Y", "o"): -60, ("Y", "s"): -50, ("Y", "u"): -40,
        ("F", "a"): -40, ("F", "e"): -30, ("F", "o"): -30, ("P", "a"): -30, ("P", "e"): -24, ("P", "o"): -24,
        ("r", "a"): -30, ("r", "e"): -20, ("r", "o"): -20, ("f", "f"): -20, ("t", "t"): -20, ("f", "."): -60, ("f", ","): -60,
        ("k", "o"): -16, ("k", "e"): -16, ("x", "o"): -12, ("z", "z"): -12}
# figures close up on a decimal point or a thousands comma (42.6, 1,284)
KERN.update({(d, p): -24 for d in "0123456789" for p in ".," if (d, p) not in KERN})
# the slash nests against figures and letters (3/8, 09/29, A–Z / a–z)
KERN.update({(a, b): -44 for d in "0123456789" for a, b in ((d, "/"), ("/", d))})
KERN.update({(a, b): -36 for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" for a, b in ((l, "/"), ("/", l))})
KERN[("1", "1")] = -10
KERN[("7", "4")] = -50
KERN[("/", "/")] = -150


# ---- build ---------------------------------------------------------------------------
def build(weight="Heavy"):
    g = glyphs()
    digits = "0123456789"
    tn1 = g.pop("1.tnum")
    names = {ch: ("uni%04X" % ord(ch)) for ch in g}
    order = [".notdef", "space"] + [names[ch] for ch in g] + [names[d] + ".tnum" for d in digits]
    pen_glyphs, metrics, cmap = {}, {}, {32: "space", 0xA0: "space"}

    def draw(outers, holes, dx):
        pen = TTGlyphPen(None)
        for pts, outer in [(c, True) for c in outers] + [(c, False) for c in holes]:
            pts = [(x + dx, y) for x, y in pts]
            # TrueType: filled contours run clockwise, holes counter-clockwise (y up)
            if (area(pts) < 0) != outer:
                pts = pts[::-1]
            pen.moveTo(pts[0])
            for q in pts[1:]:
                pen.lineTo(q)
            pen.closePath()
        return pen.glyph()

    nd = Pen(90, 90, 90, 90)
    o, h = resolve([nd.box(0, 0, 500, H)])
    pen_glyphs[".notdef"] = draw(o, h, SB)
    metrics[".notdef"] = (500 + 2 * SB, SB)
    pen_glyphs["space"] = TTGlyphPen(None).glyph()
    metrics["space"] = (SPACE, 0)

    ink = {}
    for ch, (w, parts) in g.items():
        outers, holes = resolve(parts)
        lsb, rsb, x0, x1 = side_space(ch, outers)
        if ch in digits:                                # figures: the plain bearing, so columns and readouts keep step
            lsb = rsb = SB
            ink[ch] = (outers, holes, x0, x1)
        lsb, rsb = round(lsb), round(rsb)
        pen_glyphs[names[ch]] = draw(outers, holes, lsb - x0)
        metrics[names[ch]] = (lsb + (x1 - x0) + rsb, lsb)
        cmap[ord(ch)] = names[ch]

    # tabular figures (tnum): every digit on one advance, ink centred; the 1 takes its footed form
    ink["1"] = (*resolve(tn1[1]), 0, tn1[0])
    tw = WFIG + 2 * SB
    for d, (outers, holes, x0, x1) in ink.items():
        off = (tw - (x1 - x0)) // 2
        pen_glyphs[names[d] + ".tnum"] = draw(outers, holes, off - x0)
        metrics[names[d] + ".tnum"] = (tw, off)

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(pen_glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=930, descent=-250)
    family = "Shingo Grid"
    fb.setupNameTable({"familyName": family, "styleName": weight, "uniqueFontIdentifier": f"ShingoGrid-{weight}-2",
                       "fullName": f"{family} {weight}", "psName": f"ShingoGrid-{weight}", "version": "Version 2.000",
                       "copyright": "Shingo Grid. MIT licence, see LICENSE."})
    fb.setupOS2(sTypoAscender=930, sTypoDescender=-250, sTypoLineGap=0, usWinAscent=1000, usWinDescent=300,
                sCapHeight=H, sxHeight=X, usWeightClass=900, achVendID="SHGO", fsSelection=0x20)
    fb.setupPost()
    kern = "\n".join(f"  pos {names[l]} {names[r]} {v};" for (l, r), v in KERN.items() if l in names and r in names)
    from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
    addOpenTypeFeaturesFromString(fb.font, "languagesystem DFLT dflt;\nlanguagesystem latn dflt;\nfeature kern {\n" + kern + "\n} kern;\n"
                                   + "feature tnum {\n" + "".join(f"  sub {names[d]} by {names[d]}.tnum;\n" for d in digits) + "} tnum;\n")
    from fontTools.misc.timeTools import timestampFromString
    ts = timestampFromString("Fri Nov 27 00:00:00 2026")     # fixed, so rebuilds are byte-identical
    fb.setupHead(unitsPerEm=UPM, macStyle=1, created=ts, modified=ts)
    return fb.font


def main():
    ios = ROOT / "ios" / "Sources" / "ShingoKit" / "Resources" / "Fonts"
    web = ROOT / "web" / "fonts"
    web.mkdir(parents=True, exist_ok=True)
    f = build("Heavy")
    f.save(ios / "ShingoGrid-Heavy.ttf")
    f.flavor = "woff2"
    f.save(web / "ShingoGrid-Heavy.woff2")
    print(f"ShingoGrid-Heavy: {len(f.getGlyphOrder())} glyphs, woff2 {(web / 'ShingoGrid-Heavy.woff2').stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
