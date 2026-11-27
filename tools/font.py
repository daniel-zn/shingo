"""Shingo Grid: the system's own type family.

    python3 tools/font.py

A cut-plate grotesque in three weights. Its skeleton is the square, wide-shouldered one
Orbitron made familiar; its corners are the system's own. Every glyph is a plate: bars and
stems of one weight, and wherever a letter would curve the corner is cut at 45° the way every
button, tag and card in Shingō is cut: top-left and bottom-right only, so every cut in a
line of type rises left to right. The other two corners stay square.

    Heavy  900  display 40+, screen titles, big figures
    Bold   700  subheads and inline wordmarks
    Medium 500  labels, buttons, chips, tabs (caps, 10 to 13 px)

The rules, in the order the drawings apply them:

- One weight per cut. Stems SV, bars SH (a shade lighter, so three-bar letters stay open),
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

One set of drawings makes every weight: positions are shared, strokes come from the weight's
row in WEIGHTS, and details that follow the stroke (notches, points, accents) scale with it.
Glyphs are built as unions of bars, stems and 45° strokes with the cuts subtracted
(skia-pathops), on whole font units, so every edge is level, upright or exactly 45°.

Writes ios/Sources/ShingoKit/Resources/Fonts/ShingoGrid-<Weight>.ttf and
web/fonts/ShingoGrid-<Weight>.woff2. Capitals, a full lowercase, figures (proportional by
default, tabular under `tnum`), punctuation, arrows, € $ % and the accents for English,
French and Portuguese.
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

WEIGHTS = {
    # capitals and figures: stems SV, bars SH, diagonals SD (square to the stroke); lowercase: LV, LH, LD;
    # the plate cut (CUT, LCUT); the facet that trims a diagonal's point (FACET, LFACET); the bearing next
    # to a straight stem (SB); the O, the figures' body and the lowercase o, which every other width follows
    "Heavy": dict(cls=900, SV=170, SH=148, SD=158, LV=160, LH=122, LD=146, CUT=150, LCUT=118, FACET=64, LFACET=56,
                  SB=52, SPACE=290, WO=770, WFIG=720, LO=610),
    "Bold": dict(cls=700, SV=142, SH=128, SD=134, LV=134, LH=106, LD=124, CUT=142, LCUT=112, FACET=54, LFACET=46,
                 SB=60, SPACE=280, WO=760, WFIG=710, LO=600),
    # the label weight sets caps at 10 to 13 px, so its bars stay close to its stems
    "Medium": dict(cls=500, SV=120, SH=112, SD=116, LV=114, LH=94, LD=106, CUT=134, LCUT=106, FACET=46, LFACET=40,
                   SB=68, SPACE=270, WO=750, WFIG=700, LO=590),
}
# the Heavy's own numbers, for the tools that draw its construction (print_kit.py, posters.py)
SV, SH, SD, CUT, WO, WFIG = (WEIGHTS["Heavy"][k] for k in ("SV", "SH", "SD", "CUT", "WO", "WFIG"))


class Face:
    """One weight's numbers. `t(v)` scales a detail drawn for the Heavy to this weight's stroke."""

    def __init__(self, name):
        self.name = name
        self.__dict__.update(WEIGHTS[name])
        self.s = self.SV / WEIGHTS["Heavy"]["SV"]

    def t(self, v):
        return round(v * self.s)


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


def resolve(parts, trim=()):
    """A glyph is a list of parts, each (add, cut, fill): union(add + fill) minus cut.
    Parts are resolved on their own and then joined, so a cut only bites the part it belongs to;
    `trim` is taken out of the whole glyph afterwards (the stencil's bridges).
    Returns (outer contours, holes) on whole units, with no repeated or collinear points."""
    acc = None
    for add, cut, fill in parts:
        p = _union(list(add) + list(fill))
        if cut:
            p = pathops.op(p, _union(cut), pathops.PathOp.DIFFERENCE)
        acc = p if acc is None else pathops.op(acc, p, pathops.PathOp.UNION)
    if trim:
        acc = pathops.op(acc, _union(trim), pathops.PathOp.DIFFERENCE)
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


def each(part, fn):
    """Apply a point transform to every polygon of a part."""
    return tuple([fn(q) for q in lst] for lst in part)


def diag(s):
    """Level width of a 45° stroke s thick, kept even so centred strokes land on whole units."""
    return 2 * round(s * R2 / 2)


CORNER = {"tl": (0, 1, 1, -1), "tr": (1, 1, -1, -1), "br": (1, 0, -1, 1), "bl": (0, 0, 1, 1)}


class Pen:
    """The drawing rules for one set of strokes (capitals and figures, or the lowercase)."""

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
def capitals(F):
    SV, SH, WO, t = F.SV, F.SH, F.WO, F.t
    p = Pen(SV, SH, F.SD, F.CUT)
    T, f = p.T, F.FACET
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
    ya = 304 - SH // 2                         # the A's bar sits low, so the eye above it stays open
    g["A"] = (WO, [p.box(0, 0, WO, H, "tlr", "tl"), solid(R(0, ya, WO, ya + SH))])

    # stems and arms: no turn a round letter would make, so no cuts
    g["H"] = (WO, [solid(R(0, 0, SV, H), R(WO - SV, 0, WO, H), R(0, mb, WO, mt))])
    we = WO - 90
    g["E"] = (we, [solid(R(0, 0, SV, H), R(0, H - SH, we, H), R(0, 0, we, SH), R(0, mb, we - 60, mt))])
    wf = WO - 120
    g["F"] = (wf, [solid(R(0, 0, SV, H), R(0, H - SH, wf, H), R(0, mb, wf - 70, mt))])
    wl = WO - 130
    g["L"] = (wl, [solid(R(0, 0, SV, H), R(0, 0, wl, SH))])
    wt = WO - 50
    g["T"] = (wt, [solid(R(0, H - SH, wt, H), R(wt // 2 - SV // 2, 0, wt // 2 + SV // 2, H))])
    g["I"] = (SV, [solid(R(0, 0, SV, H))])
    wj = WO - 130
    g["J"] = (wj, [p.box(0, 0, wj, H, "br", "br"), solid(R(0, 0, SV, 250))])

    # S: cut at the two extremes, square at the waist
    ws = WO - 30
    g["S"] = (ws, [p.path([R(0, H - SH, ws, H), R(0, mb, SV, H), R(0, mb, ws, mt), R(ws - SV, 0, ws, mt), R(0, 0, ws, SH)],
                          ((0, 0, ws, H), "tl"), ((0, 0, ws, H), "br"))])
    # G: the C, a lower right stem and a spur back to the centre
    g["G"] = (WO, [p.path([R(0, H - SH, WO, H), R(0, 0, SV, H), R(0, 0, WO, SH), R(WO - SV, 0, WO, mt), R(WO * 5 // 11, mb, WO, mt)],
                          ((0, 0, WO, H), "tl"), ((0, 0, WO, H), "br"))])
    # B: two bowls and the sawtooth waist
    wb = WO - 30
    n = t(70)                                  # the sawtooth's depth
    bc, bf = p.corner(0, 0, wb, H, "br")
    g["B"] = (wb, [([R(0, 0, SV, H), R(0, H - SH, wb, H), R(0, mb, wb, mt), R(0, 0, wb, SH), R(wb - SV, 0, wb, H)],
                    bc + [tri(wb, M, -1, 1, n)], bf)])
    # P and R: a tall bowl with its bottom-right cut; the R's leg runs out of the bowl at 45° onto a facet
    yb = 324 - SH // 2
    wp = WO - 40
    g["P"] = (wp, [p.path([R(0, 0, SV, H), R(0, H - SH, wp, H), R(0, yb, wp, yb + SH), R(wp - SV, yb, wp, H)], ((0, yb, wp, H), "br"))])
    wr = WO - 20
    ytop = yb + SH // 2
    leg = clipbox(band(wr + f - T - ytop, 0, ytop, T, rising=False), 0, wr, 0, ytop)
    g["R"] = (wr, [p.path([R(0, 0, SV, H), R(0, H - SH, wr, H), R(0, yb, wr, yb + SH), R(wr - SV, yb, wr, H)], ((0, yb, wr, H), "br")),
                   solid(leg)])
    # Q: where the O's bottom-right corner is cut away, the Q's is pushed out: a short 45° tooth
    # square across the corner, its end cut level on a facet
    tq = diag(t(124))
    cx, cy = WO - SV // 2, SH // 2             # the corner joint's centre
    top = SH + t(114)
    tooth = clipbox(band(cx - tq // 2 - (cy + t(150)), -t(150), top, tq, rising=False), WO - SV - t(150), WO + t(76), -t(116), top)
    g["Q"] = (WO + t(76), [p.box(0, 0, WO, H, cuts="tl"), solid(tooth)])

    # diagonals
    xv = SV + T - t(14)                        # K: the arms meet at a short neck on the stem
    wk = xv + M - f
    up = clipbox(band(xv - T - M, 0, H, T), 0, wk, M, H)
    dn = clipbox(band(xv - T - M, 0, H, T, rising=False), 0, wk, 0, M)
    g["K"] = (wk, [solid(R(0, 0, SV, H), up, dn)])
    wx = H + T - 2 * f
    g["X"] = (wx, [solid(clipbox(band(-f, 0, H, T), 0, wx, 0, H), clipbox(band(-f, 0, H, T, rising=False), 0, wx, 0, H))])
    # V: the shield. Stems down to the break, then 45° to a short flat
    wv, fl = WO + 10, 2 * round(t(116) / 2)
    yo = wv // 2 - fl // 2
    yi = yo + T - SV
    g["V"] = (wv, [([[(0, H), (0, yo), (yo, 0), (wv - yo, 0), (wv, yo), (wv, H)]],
                    [[(SV, H + 10), (SV, yi), (wv // 2, yi - (wv // 2 - SV)), (wv - SV, yi), (wv - SV, H + 10)]], [])])
    # Y: arms land on facets at the top and meet over the stem
    wy = WO + 10
    stop = H - (wy // 2 - SV // 2 + f)
    arm = clipbox(band(-f, stop, H, T, rising=False), 0, wy // 2, stop, H)
    g["Y"] = (wy, [solid(arm, mirror(arm, wy), R(wy // 2 - SV // 2, 0, wy // 2 + SV // 2, stop + 1))])
    # M: the stems carry a 45° V whose point is cut level; W is the M turned over
    wm, ft = WO + 160, t(44)
    marm = clipbox(band(0, 0, H, T, rising=False), 0, wm // 2, H - wm // 2 + ft, H)
    mparts = [R(0, 0, SV, H), R(wm - SV, 0, wm, H), marm, mirror(marm, wm)]
    g["M"] = (wm, [solid(*mparts)])
    g["W"] = (wm, [solid(*[turn(q, wm, H) for q in mparts])])
    # N: one 45° stroke through the centre, running into both stems
    wn = WO + 20
    g["N"] = (wn, [solid(R(0, 0, SV, H), R(wn - SV, 0, wn, H), clipbox(band(wn // 2 - M - T // 2, 0, H, T, rising=False), 0, wn, 0, H))])
    # Z: the diagonal lands exactly on the bars' inner corners, so the width follows from the 45°
    wz = H - 2 * SH + T
    g["Z"] = (wz, [solid(R(0, H - SH, wz, H), R(0, 0, wz, SH), band(0, SH - 2, H - SH + 2, T))])
    # Ø: the O with a slash running out through both square corners
    sl = diag(t(118))
    g["Ø"] = (WO, [p.box(0, 0, WO, H), solid(clipbox(band(WO // 2 - sl // 2 - M - 70, -70, H + 70, sl), -40, WO + 40, -70, H + 70))])
    return g


# ---- figures -------------------------------------------------------------------------
def figures(F):
    """One system for all ten: the capitals' weights and cuts on one body width.
    2 and S/5 are complements: the S and 5 are cut at their extremes with a square waist,
    the 2 is square at its extremes and cut at both waist turns, so its neck runs "/"."""
    SV, SH, W, t = F.SV, F.SH, F.WFIG, F.t
    p = Pen(SV, SH, F.SD, F.CUT)
    T = p.T
    M = H // 2
    mb, mt = M - SH // 2, M + SH // 2
    n = t(70)
    g = {}
    # 0: narrower than the O, with a slash from square corner to square corner
    ts = diag(t(108))
    sl = clipbox(band(W // 2 - ts // 2 - M, 0, H, ts), SV - 2, W - SV + 2, SH - 2, H - SH + 2)
    g["0"] = (W, [p.box(0, 0, W, H), solid(sl)])
    # 1: a stem and a flag whose end is cut right through at 45°
    fa = 200
    g["1"] = (fa + SV, [([R(fa, 0, fa + SV, H), R(0, H - SH, fa + SV, H)], [tri(0, H, 1, -1, SH)], [])])
    g["2"] = (W, [p.path([R(0, H - SH, W, H), R(W - SV, mb, W, H), R(0, mb, W, mt), R(0, 0, SV, mt), R(0, 0, W, SH)],
                         ((0, 0, W, mt), "tl"), ((0, mb, W, H), "br"))])
    c3, f3 = p.corner(0, 0, W, H, "br")
    g["3"] = (W, [([R(0, H - SH, W, H), R(W - SV, 0, W, H), R(W * 11 // 36, mb, W, mt), R(0, 0, W, SH)], c3 + [tri(W, M, -1, 1, n)], f3)])
    # 4: closed. A 45° stroke from the bar's end up into the stem; the bar runs a little past the stem
    y4, ov = 224 - SH // 2, t(46)
    sr = W - ov
    d4 = clipbox(band(sr - T - (H - y4), y4, H, T), 0, W, y4, H)
    g["4"] = (W, [solid(R(sr - SV, 0, sr, H), R(0, y4, W, y4 + SH), d4)])
    g["5"] = (W, [p.path([R(0, H - SH, W, H), R(0, mb, SV, H), R(0, mb, W, mt), R(W - SV, 0, W, mt), R(0, 0, W, SH)], ((0, 0, W, H), "br"))])
    six = p.path([R(0, H - SH, W, H), R(0, 0, SV, H), R(0, mb, W, mt), R(W - SV, 0, W, mt), R(0, 0, W, SH)],
                 ((0, 0, W, H), "tl"), ((0, 0, W, mt), "br"))
    g["6"] = (W, [six])
    g["9"] = (W, [each(six, lambda q: turn(q, W, H))])
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
def punctuation(F, caps, figs):
    SV, SH, WO, t = F.SV, F.SH, F.WO, F.t
    p = Pen(SV, SH, F.SD, F.CUT)
    T, f = p.T, F.FACET
    M = H // 2
    mb, mt = M - SH // 2, M + SH // 2
    dot = SV                                   # points are stem-wide squares
    g = {}
    g["."] = (dot, [solid(R(0, 0, dot, dot))])
    tail = [R(0, 0, dot, dot), R(0, -t(120), t(92), 0)]
    g[","] = (dot, [solid(*tail)])
    cy = 96                                    # the colon's points sit centred on the figures
    g[":"] = (dot, [solid(R(0, M - cy - dot, dot, M - cy), R(0, M + cy, dot, M + cy + dot))])
    g[";"] = (dot, [solid(*tail, R(0, M + cy, dot, M + cy + dot))])
    g["…"] = (dot * 5, [solid(R(0, 0, dot, dot), R(dot * 2, 0, dot * 3, dot), R(dot * 4, 0, dot * 5, dot))])
    md = t(140)
    g["·"] = (md, [solid(R(0, M - md // 2, md, M - md // 2 + md))])
    bl = 2 * t(110)
    g["•"] = (bl, [solid(R(0, M - bl // 2, bl, M + bl // 2))])
    g["-"] = (380, [solid(R(0, mb, 380, mt))])
    g["–"] = (560, [solid(R(0, mb, 560, mt))])
    g["—"] = (860, [solid(R(0, mb, 860, mt))])
    g["_"] = (600, [solid(R(0, -40 - t(130), 600, -40))])
    g["!"] = (dot, [solid(R(0, dot + 80, dot, H), R(0, 0, dot, dot))])
    wq = 640
    xs = wq // 2 - SV // 2 - 20
    g["?"] = (wq, [p.path([R(0, H - SH, wq, H), R(wq - SV, mb, wq, H), R(xs, mb, wq, mt), R(xs, dot + 80, xs + SV, mt)], ((xs, mb, wq, H), "br")),
                   solid(R(xs, 0, xs + SV, dot))])
    # inverted marks: the same shapes turned over, standing on the baseline with the capitals
    for ch, src in (("¡", "!"), ("¿", "?")):
        w = g[src][0]
        g[ch] = (w, [each(part, lambda q, w=w: turn(q, w, H)) for part in g[src][1]])
    qh, qw, qt, qk = 250, t(140), t(120), t(92)
    g["'"] = (qw, [solid(R(0, H - qh, qw, H))])
    g['"'] = (2 * qw + 90, [solid(R(0, H - qh, qw, H), R(qw + 90, H - qh, 2 * qw + 90, H))])
    close = [R(0, H - dot, dot, H), R(dot - qk, H - dot - qt, dot, H - dot)]
    opened = [R(0, H - dot, dot, H), R(0, H - dot - qt, qk, H - dot)]
    g["’"] = (dot, [solid(*close)])
    g["‘"] = (dot, [solid(*opened)])
    step = dot + t(70)
    g["”"] = (dot + step, [solid(*close, *[shift(q, step) for q in close])])
    g["“"] = (dot + step, [solid(*opened, *[shift(q, step) for q in opened])])
    # primes: short strokes on the system's diagonal
    ph, pw = 230, t(124)
    prime = clipbox(band(-30, H - ph, H, pw), 0, ph + pw - 60, H - ph, H)
    g["′"] = (ph + pw - 60, [solid(prime)])
    g["″"] = (ph + 2 * pw - 60 + t(50), [solid(prime, shift(prime, pw + t(50)))])
    # the slash and the percent: the system's one diagonal on a facet at each end
    fs = 150
    ws = H + T - 2 * fs
    g["/"] = (ws, [solid(clipbox(band(-fs, 0, H, T), 0, ws, 0, H))])
    # percent: two small plate rings with the slash squeezed between them on tall facets
    dq, dst = 256, t(84)
    rp = Pen(dst, dst, dst, 76)
    gapp = 40
    xp = dq + gapp - (H - dq)                  # the slash clears the upper ring by gapp
    wpc = 2 * (dq + gapp) + T - (H - 2 * dq)
    g["%"] = (wpc, [solid(clipbox(band(xp, 0, H, T), dq // 2, wpc - dq // 2, 0, H)), rp.box(0, H - dq, dq, H), rp.box(wpc - dq, 0, wpc, dq)])
    g["+"] = (520, [solid(R(0, mb, 520, mt), R(260 - SH // 2, M - 260, 260 + SH // 2, M + 260))])
    g["−"] = (520, [solid(R(0, mb, 520, mt))])
    eq = t(128)
    g["="] = (520, [solid(R(0, M + 46, 520, M + 46 + eq), R(0, M - 46 - eq, 520, M - 46))])
    dd = 2 * t(70)
    g["÷"] = (520, [solid(R(0, mb, 520, mt), R(260 - dd // 2, mt + t(70), 260 + dd // 2, mt + t(70) + dd), R(260 - dd // 2, mb - t(70) - dd, 260 + dd // 2, mb - t(70)))])
    # times: a small X on facets
    th, tt, tf = 400, diag(t(124)), t(44)
    tw = th + tt - 2 * tf
    g["×"] = (tw, [solid(shift(clipbox(band(-tf, 0, th, tt), 0, tw, 0, th), 0, M - th // 2),
                         shift(clipbox(band(-tf, 0, th, tt, rising=False), 0, tw, 0, th), 0, M - th // 2))])
    # degree and ordinal: a small plate ring at the cap line
    dg, ds = 270, t(88)
    ring = Pen(ds, ds, ds, 76).box(0, H - dg, dg, H)
    g["°"] = (dg, [ring])
    under = R(0, H - dg - 40 - t(70), dg, H - dg - 40)
    g["º"] = (dg, [ring, solid(under)])
    # numero: the N and the ordinal ring
    wn = caps["N"][0]
    g["№"] = (wn + t(70) + dg, caps["N"][1] + [each(ring, lambda q: shift(q, wn + t(70))), solid(shift(under, wn + t(70)))])
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
    # guillemets: the angle bracket twice, a little smaller
    ga = 200
    gw = T + ga - f
    gu = clipbox(band(0, M, M + ga, T), 0, gw, M, M + ga)
    gd = clipbox(band(0, M - ga, M, T, rising=False), 0, gw, M - ga, M)
    gs = T + t(40)
    g["«"] = (gw + gs, [solid(gu, gd, shift(gu, gs), shift(gd, gs))])
    g["»"] = (gw + gs, [solid(*[mirror(q, gw + gs) for q in (gu, gd, shift(gu, gs), shift(gd, gs))])])
    # arrows: a bar with the angle bracket's point; the upright ones are the level one turned a quarter
    wa = H
    head = [shift(mirror(q, gw), wa - gw) for q in (gu, gd)]
    right = [R(0, mb, wa - T // 2, mt)] + head
    g["→"] = (wa, [solid(*right)])
    g["←"] = (wa, [solid(*[mirror(q, wa) for q in right])])
    quarter = lambda q: [(ga + (M - y), x) for x, y in q]      # level → upright, pointing up
    g["↑"] = (2 * ga, [solid(*[quarter(q) for q in right])])
    g["↓"] = (2 * ga, [solid(*[turn(quarter(q), 2 * ga, H) for q in right])])
    # diamond: the mark's outline, solid
    dm = 230
    g["◆"] = (2 * dm, [solid([(0, M), (dm, M + dm), (2 * dm, M), (dm, M - dm)])])
    # asterisk: an upright cross and a 45° cross on one centre, eight short arms at the cap line
    sa, ta, ah, af = 380, diag(t(84)), t(44), t(30)
    ca = H - sa // 2
    xa = lambda rising: shift(clipbox(band(-af, 0, sa, ta, rising), 0, sa + ta - 2 * af, 0, sa), (sa - (sa + ta - 2 * af)) // 2, H - sa)
    g["*"] = (sa, [solid(R(sa // 2 - ah, H - sa, sa // 2 + ah, H), R(0, ca - ah, sa, ca + ah), xa(True), xa(False))])
    hb, hu = t(124), 2 * round(t(140) / 2)
    g["#"] = (760, [solid(R(0, M + 60, 760, M + 60 + hb), R(0, M - 60 - hb, 760, M - 60), R(240 - hu // 2, 30, 240 + hu // 2, H - 30), R(520 - hu // 2, 30, 520 + hu // 2, H - 30))])
    # euro: the C with two bars through its stem
    we, eb = 740, t(104)
    g["€"] = (we, [p.box(70, 0, we, H, "tbl", "tl"), solid(R(0, M + 30, 470, M + 30 + eb), R(0, M - 30 - eb, 470, M - 30))])
    # dollar: the S with a bar showing above and below it
    ws_, sb_ = WO - 30, t(62)
    g["$"] = (ws_, [p.path([R(0, H - SH, ws_, H), R(0, mb, SV, H), R(0, mb, ws_, mt), R(ws_ - SV, 0, ws_, mt), R(0, 0, ws_, SH)],
                           ((0, 0, ws_, H), "tl"), ((0, 0, ws_, H), "br")),
                    solid(R(ws_ // 2 - sb_, H - 2, ws_ // 2 + sb_, H + 84), R(ws_ // 2 - sb_, -84, ws_ // 2 + sb_, 2))])
    # ampersand: a small plate loop over an open bowl, a 45° leg from the waist to the baseline
    wa_ = 780
    lx0, lx1, ly0 = 80, 560, 374 - SH // 2     # the loop
    loop = p.box(lx0, ly0, lx1, H, c=110)
    bx1 = 640                                  # the bowl: open to the right, bottom bar full
    bowl = p.path([R(0, ly0, lx1, ly0 + SH), R(0, 0, SV, ly0 + SH), R(0, 0, bx1, SH)], ((0, 0, bx1, ly0 + SH), "tl", 110))
    leg = clipbox(band(wa_ + f - T - (ly0 + SH // 2), 0, ly0 + SH // 2, T, rising=False), 0, wa_, 0, ly0 + SH)
    g["&"] = (wa_, [loop, bowl, solid(leg)])
    # at: a plate frame open at the lower right, a solid core, the tail running out along the baseline
    core = t(190)
    g["@"] = (WO, [p.box(0, 0, WO, H, "tbl", "tl"), solid(R(WO - SV, 250, WO, H), R(300, 250, WO, 250 + core), R(300, 250, 300 + core, 450), R(300, 0, WO, SH))])
    # superiors: the figures at six tenths, hung from the cap line
    for ch, src in (("²", "2"), ("³", "3")):
        o, h = resolve(figs[src][1])
        up = lambda q: [(round(x * .6), round(H - (H - y) * .6)) for x, y in q]
        g[ch] = (round(figs[src][0] * .6), [([up(c) for c in o], [up(c) for c in h], [])])
    return g


# ---- lowercase -----------------------------------------------------------------------
def lowercase(F):
    """The capitals' rules at x-height. Bars are lighter (LH) so the three-bar letters (a e s)
    keep their counters; cuts scale with the x-height. The rule survives a half turn, so
    n/u, b/q, d/p and m/w are each other rotated."""
    LV, LH, wo, t = F.LV, F.LH, F.LO, F.t
    p = Pen(LV, LH, F.LD, F.LCUT)
    T, f = p.T, F.LFACET
    c2 = F.LCUT - 18                           # the cut where three bars share the x-height (a e s f)
    g = {}
    mb = (X - LH) // 2                         # middle bar (a e s)
    mt = mb + LH

    g["o"] = (wo, [p.box(0, 0, wo, X)])
    wc = wo - 50
    g["c"] = (wc, [p.box(0, 0, wc, X, "tbl", "tl")])
    # e: the eye closed by the middle bar, open below it
    g["e"] = (wo, [p.path([R(0, X - LH, wo, X), R(0, 0, LV, X), R(wo - LV, mb, wo, X), R(0, mb, wo, mt), R(0, 0, wo, LH)], ((0, 0, wo, X), "tl", c2))])
    # a: two storeys. The top bar and a full right stem; the bowl hangs on the stem
    wa = wo - 20
    g["a"] = (wa, [p.path([R(30, X - LH, wa, X), R(wa - LV, 0, wa, X), R(0, mb, wa, mt), R(0, 0, LV, mt), R(0, 0, wa, LH)], ((0, 0, wa, mt), "tl", c2))])
    ws = wo - 30
    g["s"] = (ws, [p.path([R(0, X - LH, ws, X), R(0, mb, LV, X), R(0, mb, ws, mt), R(ws - LV, 0, ws, mt), R(0, 0, ws, LH)],
                          ((0, 0, ws, X), "tl", c2), ((0, 0, ws, X), "br", c2))])
    # b d p q: a bowl on a stem; the bowl's free corner on the cut diagonal is cut
    g["b"] = (wo, [p.box(0, 0, wo, X, "tbr", "br"), solid(R(0, 0, LV, ASC))])
    g["d"] = (wo, [p.box(0, 0, wo, X, "tbl", "tl"), solid(R(wo - LV, 0, wo, ASC))])
    g["p"] = (wo, [p.box(0, 0, wo, X, "tbr", "br"), solid(R(0, DSC, LV, X))])
    g["q"] = (wo, [p.box(0, 0, wo, X, "tbl", "tl"), solid(R(wo - LV, DSC, wo, X))])
    # descender hooks: the stem turns left along the descender; its corner is a bottom-right one, so it is cut
    hc = F.LCUT - 22
    def hook(xr, x0):
        return p.path([R(xr - LV, DSC, xr, X), R(x0, DSC, xr, DSC + LH)], ((x0 - LV, DSC, xr, X), "br", hc))
    g["g"] = (wo, [p.box(0, 0, wo, X, "tbl", "tl"), hook(wo, 70)])
    # n u h m r: the arch's top-left and the cup's bottom-right are cut; n is the u turned
    wn = wo - 20
    g["n"] = (wn, [p.box(0, 0, wn, X, "tlr", "tl")])
    g["u"] = (wn, [p.box(0, 0, wn, X, "lbr", "br")])
    g["h"] = (wn, [solid(R(0, 0, LV, ASC), R(0, X - LH, wn, X), R(wn - LV, 0, wn, X))])
    wm = wo + 290
    marc = p.box(0, 0, wm, X, "tlr", "tl")
    mstem = R(wm // 2 - LV // 2, 0, wm // 2 + LV // 2, X)
    g["m"] = (wm, [marc, solid(mstem)])
    g["w"] = (wm, [each(marc, lambda q: turn(q, wm, X)), solid(mstem)])
    wr = LV + 240
    g["r"] = (wr, [p.box(0, 0, wr, X, "tl", "tl")])
    # i j l: stems; the points are stem-wide squares
    gap, dh = 64, t(136)
    dot = lambda x: R(x, X + gap, x + LV, X + gap + dh)
    g["ı"] = (LV, [solid(R(0, 0, LV, X))])
    g["i"] = (LV, [solid(R(0, 0, LV, X), dot(0))])
    wj = LV + 140
    g["j"] = (wj, [hook(wj, 0), solid(dot(wj - LV))])
    g["l"] = (LV, [solid(R(0, 0, LV, ASC))])
    # t f: a stem crossed at the x-height; the t stands on a square foot, the f's head is cut
    xs = 70
    wt = xs + LV + 150
    g["t"] = (wt, [solid(R(xs, 0, xs + LV, ASC - 60), R(0, X - LH, wt, X), R(xs, 0, wt, LH))])
    wf = xs + LV + 170
    g["f"] = (wf, [p.box(xs, 0, wf, ASC, "tl", "tl", c=c2), solid(R(0, X - LH, wf - 30, X))])
    # k v x y z: the capitals' diagonals at x-height
    M = X // 2
    xv = LV + T - f
    wk = xv + M - f
    g["k"] = (wk, [solid(R(0, 0, LV, ASC), clipbox(band(xv - T - M, 0, X, T), 0, wk, M, X),
                         clipbox(band(xv - T - M, 0, X, T, rising=False), 0, wk, 0, M))])
    wv, fl = wo + 10, 2 * round(t(100) / 2)
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
def accents(F):
    """Marks over the cap height or x-height, centred on 0: 45° strokes cut level, like the letters' diagonals."""
    t = F.t
    aw, tw, cw = t(150), t(110), t(140)
    return {
        "acute": [band(-150 + (150 - aw) // 2, 0, 150, aw)],
        "grave": [band(-150 + (150 - aw) // 2, 0, 150, aw, rising=False)],
        "circ": [[(-230, 0), (-230 + cw, 0), (0, min(230 - cw, 150 - t(60))), (230 - cw, 0), (230, 0), (60, 150), (-60, 150)]],
        "uml": [R(-140 - cw // 2, 0, -140 + cw // 2 + cw % 2, t(130)), R(140 - cw // 2, 0, 140 + cw // 2 + cw % 2, t(130))],
        "macron": [R(-230, 0, 230, t(104))],
        "narrow": [R(-150, 0, 150, t(104))],
        "tilde": [band(-250, 0, 120, tw), shift(band(-250, 0, 120, tw, rising=False), 120), shift(band(-250, 0, 120, tw), 240)],
    }


COMPOSED = {
    "À": ("A", "grave"), "Á": ("A", "acute"), "Â": ("A", "circ"), "Ä": ("A", "uml"), "Ã": ("A", "tilde"), "Å": ("A", "ring"), "Ā": ("A", "macron"),
    "È": ("E", "grave"), "É": ("E", "acute"), "Ê": ("E", "circ"), "Ë": ("E", "uml"), "Ē": ("E", "macron"),
    "Ì": ("I", "grave"), "Í": ("I", "acute"), "Î": ("I", "circ"), "Ï": ("I", "uml"), "Ī": ("I", "narrow"),
    "Ò": ("O", "grave"), "Ó": ("O", "acute"), "Ô": ("O", "circ"), "Ö": ("O", "uml"), "Õ": ("O", "tilde"), "Ō": ("O", "macron"),
    "Ù": ("U", "grave"), "Ú": ("U", "acute"), "Û": ("U", "circ"), "Ü": ("U", "uml"), "Ū": ("U", "macron"),
    "Ñ": ("N", "tilde"), "Ý": ("Y", "acute"), "Ÿ": ("Y", "uml"),
    # lowercase: the same marks over the x-height; the i takes them on the dotless ı
    "à": ("a", "grave"), "á": ("a", "acute"), "â": ("a", "circ"), "ä": ("a", "uml"), "ã": ("a", "tilde"), "å": ("a", "ring"), "ā": ("a", "macron"),
    "è": ("e", "grave"), "é": ("e", "acute"), "ê": ("e", "circ"), "ë": ("e", "uml"), "ē": ("e", "macron"),
    "ì": ("ı", "grave"), "í": ("ı", "acute"), "î": ("ı", "circ"), "ï": ("ı", "uml"), "ī": ("ı", "narrow"),
    "ò": ("o", "grave"), "ó": ("o", "acute"), "ô": ("o", "circ"), "ö": ("o", "uml"), "õ": ("o", "tilde"), "ō": ("o", "macron"),
    "ù": ("u", "grave"), "ú": ("u", "acute"), "û": ("u", "circ"), "ü": ("u", "uml"), "ū": ("u", "macron"),
    "ñ": ("n", "tilde"), "ý": ("y", "acute"), "ÿ": ("y", "uml"),
}
ACCENT_GAP = 58


def glyphs(F):
    """Every glyph of one weight as (body width, parts)."""
    g = {}
    caps, figs = capitals(F), figures(F)
    g.update(caps)
    g.update(figs)
    g.update(punctuation(F, caps, figs))
    g.update(lowercase(F))
    marks = accents(F)
    rs = F.t(84)
    ring = Pen(rs, rs, rs, 70).box(-125, 0, 125, 230)
    for ch, (base, acc) in COMPOSED.items():
        w, parts = g[base]
        top = (X if base.islower() or base == "ı" else H) + ACCENT_GAP
        dx = w // 2
        if acc == "ring":
            mark = [each(ring, lambda q: shift(q, dx, top))]
        else:
            mark = [solid(*[shift(q, dx, top) for q in marks[acc]])]
        g[ch] = (w, parts + mark)
    cs, cb = F.t(62), F.t(150)
    for ch, base in (("Ç", "C"), ("ç", "c")):
        w, parts = g[base]
        cx = w // 2
        g[ch] = (w, parts + [solid(R(cx - cs, -90, cx + cs, 2), shift(band(-150 + (150 - cb) // 2, 0, 110, cb), cx, -190))])
    return g


# ---- stencil -------------------------------------------------------------------------
BRIDGE = 84        # a bridge's width, measured level (about 59 square to the slit)


def stencil(F, g):
    """Shingo Grid Stencil: the Heavy capitals and figures, bridged. Every bridge is a slit on the
    system's one diagonal, so it rises left to right like every cut.

    - A square corner where a bar and a stem join is opened by a mitre slit through its inner
      corner. Only top-right and bottom-left corners mitre "/", and those are exactly the two the
      plate rule leaves square: where the plate is not cut, the stencil opens it.
    - A glyph no mitre reaches is bridged once: across its crossbar (H), its stem (I K T Y), the
      stroke that crosses the slit (M N V W X), or a bar (F Z 4 7).
    - The zero's slash floats clear of its frame, so no counter is closed.

    Returns {character: [slits]} for the glyphs in g; lowercase is set in the capitals."""
    SV, SH, WO, W, t = F.SV, F.SH, F.WO, F.WFIG, F.t
    T, f = diag(F.SD), F.FACET
    bw = BRIDGE
    M = H // 2
    mb, mt = M - SH // 2, M + SH // 2

    def slit(cx, cy, x0, x1, y0, y1):
        """A "/" slit through (cx, cy), kept inside a box."""
        L = 1600
        return clipbox(band(cx - bw / 2 - L, cy - L, cy + L, bw), x0, x1, y0, y1)

    def tr(x, y):                               # the square top-right corner at (x, y)
        return slit(x - SV, y - SH, x - SV - bw, x + 4, y - SH - bw, y + 4)

    def bl(x, y):                               # the square bottom-left corner at (x, y)
        return slit(x + SV, y + SH, x - 4, x + SV + bw, y - 4, y + SH + bw)

    def bar(x, y0, y1):                         # across a level bar
        return slit(x, (y0 + y1) / 2, x - 400, x + 400, y0 - 2, y1 + 2)

    def stem(x0, x1, y):                        # across an upright stem
        return slit((x0 + x1) / 2, y, x0 - 2, x1 + 2, y - 400, y + 400)

    w = lambda ch: g[ch][0]
    cx = lambda ch: w(ch) // 2
    out = {
        "A": [tr(WO, H)], "B": [tr(w("B"), H), bl(0, 0)], "C": [bl(0, 0)], "D": [tr(WO, H), bl(0, 0)],
        "E": [bl(0, 0), bar(SV + bw // 2 + 26, H - SH, H)], "F": [bar(SV + bw // 2 + 26, H - SH, H)],
        "G": [bl(0, 0), tr(WO, mt)], "H": [bar(WO // 2, mb, mt)], "I": [stem(0, SV, M)], "J": [bl(0, 0)],
        "K": [stem(0, SV, M + 120)], "L": [bl(0, 0)],
        "N": [slit(cx("N"), M, SV + 2, w("N") - SV - 2, 0, H)],
        "O": [tr(WO, H), bl(0, 0)], "P": [tr(w("P"), H)], "Q": [tr(WO, H), bl(0, 0)], "R": [tr(w("R"), H)],
        "S": [tr(w("S"), mt), bl(0, mb)],
        "T": [stem(cx("T") - SV // 2, cx("T") + SV // 2, H - SH - 80)], "U": [bl(0, 0)],
        "Z": [bar(w("Z") * .34, H - SH, H), bar(w("Z") * .66, 0, SH)],
        "0": [tr(W, H), bl(0, 0)], "1": [tr(w("1"), H)], "2": [tr(W, H), bl(0, 0)], "3": [tr(W, H)],
        "5": [bl(0, mb), tr(W, mt)], "6": [bl(0, 0), tr(W, mt)], "7": [bar(W * .4, H - SH, H)],
        "8": [tr(W, H), bl(0, 0)], "9": [tr(W, H), bl(0, mb)],
    }
    # M W V: the falling stroke is cut square across its middle, as the N's is
    wm = w("M")
    ms = slit(T // 2 + 190, H - 190, SV + 2, wm // 2 - 2, H - 420, H)
    out["M"] = [ms]
    out["W"] = [turn(ms, wm, H)]
    wv = w("V")
    yo = wv // 2 - t(116) // 2                  # where the V's stem breaks into its slope
    vx = (yo + T // 2 + 96) // 2                # a point on the slope's centre line, x + y = yo + T / 2
    out["V"] = [slit(vx, yo + T // 2 - vx, SV // 2, wv // 2 - 2, 40, yo)]
    # Y: across the stem, under the fork
    wy = w("Y")
    fork = H - (wy // 2 - SV // 2 + f)
    out["Y"] = [stem(wy // 2 - SV // 2, wy // 2 + SV // 2, fork - 110)]
    # X: the falling stroke is cut either side of the crossing; the rising one runs through
    wx = w("X")
    d = 96
    out["X"] = [slit(wx // 2 + d, M - d, wx // 2 + d - 150, wx // 2 + d + 150, M - d - 150, M - d + 150),
                slit(wx // 2 - d, M + d, wx // 2 - d - 150, wx // 2 - d + 150, M + d - 150, M + d + 150)]
    # 4: the bar is cut under the counter, so the triangle opens
    sr = W - t(46)
    y4 = 224 - SH // 2
    out["4"] = [bar(sr - SV - 124, y4, y4 + SH)]
    out["1.tnum"] = [tr((500 - SV) // 2 + SV, H)]
    return out


def stencil_zero(F):
    """The stencil's zero: the frame, and the slash floating clear of it."""
    SV, SH, W = F.SV, F.SH, F.WFIG
    p = Pen(SV, SH, F.SD, F.CUT)
    ts, gap = diag(F.t(108)), 46
    sl = clipbox(band(W // 2 - ts // 2 - H // 2, 0, H, ts), SV + gap, W - SV - gap, SH + gap, H - SH - gap)
    return (W, [p.box(0, 0, W, H), solid(sl)])


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


def side_space(ch, shapes, SB):
    """Optical spacing. Each side gets the base bearing minus part of the white it already
    holds, so open and diagonal sides (C, E, K, L, T, X, Y, 7) sit as close as straight stems
    do. Punctuation keeps the plain bearing."""
    xs = [x for pts in shapes for x, _ in pts]
    x0, x1 = min(xs), max(xs)
    if not ch.isalnum() or ch in "²³":
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
    is_stencil = weight == "Stencil"
    F = Face("Heavy" if is_stencil else weight)
    SB = F.SB
    g = glyphs(F)
    trims = {}
    if is_stencil:
        g["0"] = stencil_zero(F)
        trims = stencil(F, g)
        for ch, (base, acc) in COMPOSED.items():    # accented capitals carry their letter's bridges
            if base in trims:
                trims[ch] = trims[base]
        for ch in ("Ç", "Ø"):
            trims[ch] = trims[{"Ç": "C", "Ø": "O"}[ch]]
        g = {ch: v for ch, v in g.items() if not (len(ch) == 1 and ch.islower())}      # unicase: a–z are set in the capitals
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
    metrics["space"] = (F.SPACE, 0)

    ink = {}
    for ch, (w, parts) in g.items():
        outers, holes = resolve(parts)
        lsb, rsb, x0, x1 = side_space(ch, outers, SB)       # spaced as the unbridged letter, so a bridge never shifts it
        if ch in trims:
            outers, holes = resolve(parts, trims[ch])
        if ch in digits:                                # figures: the plain bearing, so columns and readouts keep step
            lsb = rsb = SB
            ink[ch] = (outers, holes, x0, x1)
        lsb, rsb = round(lsb), round(rsb)
        pen_glyphs[names[ch]] = draw(outers, holes, lsb - x0)
        metrics[names[ch]] = (lsb + (x1 - x0) + rsb, lsb)
        cmap[ord(ch)] = names[ch]

    # tabular figures (tnum): every digit on one advance, ink centred; the 1 takes its footed form
    ink["1"] = (*resolve(tn1[1], trims.get("1.tnum", ())), 0, tn1[0])
    if is_stencil:
        lower = {ord(c.lower()): n for c, n in ((chr(k), v) for k, v in cmap.items()) if c.isupper() and len(c.lower()) == 1 and ord(c.lower()) not in cmap}
        cmap.update(lower)
        cmap[ord("ı")] = names["I"]
    tw = F.WFIG + 2 * SB
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
    fb.setupNameTable({"familyName": f"{family} {weight}", "styleName": "Regular", "typographicFamily": family, "typographicSubfamily": weight,
                       "uniqueFontIdentifier": f"ShingoGrid-{weight}-2", "fullName": f"{family} {weight}", "psName": f"ShingoGrid-{weight}",
                       "version": "Version 2.100", "copyright": "Shingo Grid. MIT licence, see LICENSE."})
    fb.setupOS2(sTypoAscender=930, sTypoDescender=-250, sTypoLineGap=0, usWinAscent=1000, usWinDescent=300,
                sCapHeight=H, sxHeight=X, usWeightClass=F.cls, achVendID="SHGO", fsSelection=0x40)
    fb.setupPost()
    kern = "\n".join(f"  pos {names[l]} {names[r]} {v};" for (l, r), v in KERN.items() if l in names and r in names)
    from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
    addOpenTypeFeaturesFromString(fb.font, "languagesystem DFLT dflt;\nlanguagesystem latn dflt;\nfeature kern {\n" + kern + "\n} kern;\n"
                                   + "feature tnum {\n" + "".join(f"  sub {names[d]} by {names[d]}.tnum;\n" for d in digits) + "} tnum;\n")
    from fontTools.misc.timeTools import timestampFromString
    ts = timestampFromString("Fri Nov 27 00:00:00 2026")     # fixed, so rebuilds are byte-identical
    fb.setupHead(unitsPerEm=UPM, macStyle=0, created=ts, modified=ts)
    return fb.font


def main():
    ios = ROOT / "ios" / "Sources" / "ShingoKit" / "Resources" / "Fonts"
    web = ROOT / "web" / "fonts"
    web.mkdir(parents=True, exist_ok=True)
    for weight in list(WEIGHTS) + ["Stencil"]:
        f = build(weight)
        f.save(ios / f"ShingoGrid-{weight}.ttf")
        f.flavor = "woff2"
        f.save(web / f"ShingoGrid-{weight}.woff2")
        print(f"ShingoGrid-{weight}: {len(f.getGlyphOrder())} glyphs, woff2 {(web / f'ShingoGrid-{weight}.woff2').stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
