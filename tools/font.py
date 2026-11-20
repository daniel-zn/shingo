"""Shingō Grid: the system's own display face.

    python3 tools/font.py

Wide, short and hard, after the RADAR poster. Every stroke has one heavy weight,
every glyph is drawn from level, upright and 45° edges on a grid, and wherever a
letter would normally curve it is cut at 45°. Diagonals are long 45° strokes
at full weight; a free end is cut level and its point trimmed by an upright facet. One cut, Heavy, for display,
titles and numbers (subheads and labels are Shingo Signal, see signal_font.py).

Writes ios/Sources/ShingoKit/Resources/Fonts/ShingoGrid-Heavy.ttf and
web/fonts/ShingoGrid-Heavy.woff2. Caps only: titles set it with text-transform: uppercase; lowercase (units inside
figures, say) falls through to Shingo Signal, then Anybody.
"""
import math
import pathlib

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

ROOT = pathlib.Path(__file__).resolve().parent.parent
R2 = math.sqrt(2)
H = 700          # cap height
UPM = 1000

WEIGHTS = {
    # stroke, outer cut, body width, side bearing, space. One cut, after the RADAR reference:
    # strokes about a fifth of the cap height, small hard corner cuts (about 3/4 of the stroke), letters wider than tall.
    "Heavy": dict(S=136, C=104, B=800, SB=58, SP=300),
}


def area(pts):
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1])) / 2


def crect(x0, y0, x1, y1, tl=0, tr=0, br=0, bl=0):
    """Rectangle with 45° cuts on chosen corners (y up)."""
    p = []
    p += [(x0, y1 - tl), (x0 + tl, y1)] if tl else [(x0, y1)]
    p += [(x1 - tr, y1), (x1, y1 - tr)] if tr else [(x1, y1)]
    p += [(x1, y0 + br), (x1 - br, y0)] if br else [(x1, y0)]
    p += [(x0 + bl, y0), (x0, y0 + bl)] if bl else [(x0, y0)]
    return p


def rect(x0, y0, x1, y1):
    return crect(x0, y0, x1, y1)


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


def band(x0, y0, y1, T, rising=True):
    """A 45° stroke between heights y0 and y1, T wide measured level.
    Rising runs "/" from bottom-left x0; falling runs "\\" from top-left x0.
    Long and continuous: where it meets a level line its point is trimmed by an
    upright facet (clipbox), the same 45° cut the corners use."""
    d = y1 - y0
    if rising:
        return [(x0, y0), (x0 + T, y0), (x0 + T + d, y1), (x0 + d, y1)]
    return [(x0 + d, y0), (x0 + d + T, y0), (x0 + T, y1), (x0, y1)]


def stroke(pts, w):
    """A polyline drawn at full weight w with mitred joins and flat ends.

    The face's one rule for diagonals: they run at 45°, carry the same weight as
    the stems, and never end on the slant. A diagonal either ends inside another
    stroke, or turns into a level or upright stub first, so every terminal is
    square to the grid."""
    h = w / 2
    segs = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        segs.append(((x1 - x0) / L, (y1 - y0) / L))
    norm = [(-dy, dx) for dx, dy in segs]

    def side(k):
        out = []
        for i, (x, y) in enumerate(pts):
            if i == 0:
                nx, ny = norm[0]
            elif i == len(pts) - 1:
                nx, ny = norm[-1]
            else:
                (ax, ay), (bx, by) = norm[i - 1], norm[i]
                dot = ax * bx + ay * by
                nx, ny = (ax + bx) / (1 + dot), (ay + by) / (1 + dot)
            out.append((x + k * h * nx, y + k * h * ny))
        return out
    return side(1) + side(-1)[::-1]


def glyphs(S, C, B, **_):
    """Each glyph: (advance-body width, [shapes], [holes]). Shapes may overlap (non-zero fill)."""
    c = max(0.0, C - S * (2 - R2))     # inner cut that keeps a 45° stroke at full weight
    M = H / 2
    t, b = M + S / 2, M - S / 2        # crossbar top / bottom
    T = S * R2                        # horizontal thickness of a 45° stroke
    g = {}

    g["A"] = (B, [[(0, 0), (0, H - C), (C, H), (B - C, H), (B, H - C), (B, 0), (B - S, 0), (B - S, b), (S, b), (S, 0)]],
              [crect(S, t, B - S, H - S, tl=c, tr=c)])
    d = S * .55
    g["B"] = (B, [[(0, 0), (0, H), (B - C, H), (B, H - C), (B, M + d), (B - d, M), (B, M - d), (B, C), (B - C, 0)]],
              [crect(S, t, B - S, H - S, tr=c), crect(S, S, B - S, b, br=c)])
    g["C"] = (B, [[(C, H), (B, H), (B, H - S), (S + c, H - S), (S, H - S - c), (S, S + c), (S + c, S), (B, S), (B, 0), (C, 0), (0, C), (0, H - C)]], [])
    g["D"] = (B, [crect(0, 0, B, H, tr=C, br=C)], [crect(S, S, B - S, H - S, tr=c, br=c)])
    e = B - S * .9
    g["E"] = (B, [[(0, 0), (0, H), (B, H), (B, H - S), (S, H - S), (S, t), (e, t), (e, b), (S, b), (S, S), (B, S), (B, 0)]], [])
    g["F"] = (B, [[(0, 0), (0, H), (B, H), (B, H - S), (S, H - S), (S, t), (e, t), (e, b), (S, b), (S, 0)]], [])
    gx = B * .48
    g["G"] = (B, [[(C, H), (B, H), (B, H - S), (S + c, H - S), (S, H - S - c), (S, S + c), (S + c, S), (B - S - c, S), (B - S, S + c),
                   (B - S, b), (gx, b), (gx, t), (B, t), (B, C), (B - C, 0), (C, 0), (0, C), (0, H - C)]], [])
    g["H"] = (B, [[(0, 0), (0, H), (S, H), (S, t), (B - S, t), (B - S, H), (B, H), (B, 0), (B - S, 0), (B - S, b), (S, b), (S, 0)]], [])
    g["I"] = (S, [rect(0, 0, S, H)], [])
    jw = B * .86
    g["J"] = (jw, [[(jw - S, H), (jw, H), (jw, C), (jw - C, 0), (0, 0), (0, H * .36), (S, H * .36), (S, S), (jw - S - c, S), (jw - S, S + c)]], [])
    x0 = B - T - (H - b)
    g["K"] = (B, [rect(0, 0, S, H),
                  [(x0, b), (x0 + T, b), (B, H - (B - (x0 + T + (H - b)))), (B, H), (x0 + (H - b), H)],
                  [(x0, t), (x0 + (t), 0), (x0 + T + t, 0), (x0 + T, t)]], [])
    lw = B * .84
    g["L"] = (lw, [[(0, 0), (0, H), (S, H), (S, S), (lw, S), (lw, 0)]], [])
    mw = B * 1.16
    # M: two stems and a V that drops from the top corners to just below the middle
    sx = S * 1.3
    yt = H * .38                                   # V tip, outer edge
    k = (H - yt) / (mw / 2 - sx)                   # slope of the V arms
    yb = yt - S * 1.25                             # V tip, inner edge
    yin = yb + k * (mw / 2 - S)                    # where the inner edge meets each stem
    m_pts = [(0, 0), (0, H), (sx, H), (mw / 2, yt), (mw - sx, H), (mw, H), (mw, 0), (mw - S, 0), (mw - S, yin), (mw / 2, yb), (S, yin), (S, 0)]
    g["M"] = (mw, [m_pts], [])
    dx = S * 1.25
    g["N"] = (B, [rect(0, 0, S, H), rect(B - S, 0, B, H), [(0, H), (dx, H), (B, 0), (B - dx, 0)]], [])
    g["O"] = (B, [crect(0, 0, B, H, C, C, C, C)], [crect(S, S, B - S, H - S, c, c, c, c)])
    g["P"] = (B, [[(0, 0), (0, H), (B - C, H), (B, H - C), (B, b + C), (B - C, b), (S, b), (S, 0)]],
              [crect(S, t, B - S, H - S, tr=c, br=c)])
    g["Q"] = (B + S * .6, [crect(0, 0, B, H, C, C, 0, C), rect(B - S, 0, B + S * .6, S)], [crect(S, S, B - S, H - S, c, c, 0, c)])
    xl = B - T - b
    g["R"] = (B, [[(0, 0), (0, H), (B - C, H), (B, H - C), (B, b + C), (B - C, b), (S, b), (S, 0)],
                  [(xl, b + 1), (xl + T, b + 1), (B, 0), (B - T, 0)]],
              [crect(S, t, B - S, H - S, tr=c, br=c)])
    g["S"] = (B, [[(C, H), (B, H), (B, H - S), (S + c, H - S), (S, H - S - c), (S, t), (B - C, t), (B, t - C), (B, C), (B - C, 0), (0, 0),
                   (0, S), (B - S - c, S), (B - S, S + c), (B - S, b - c), (B - S - c, b), (C, b), (0, b + C), (0, H - C)]], [])
    g["T"] = (B, [[(0, H), (B, H), (B, H - S), (B / 2 + S / 2, H - S), (B / 2 + S / 2, 0), (B / 2 - S / 2, 0), (B / 2 - S / 2, H - S), (0, H - S)]], [])
    g["U"] = (B, [[(0, H), (S, H), (S, S + c), (S + c, S), (B - S - c, S), (B - S, S + c), (B - S, H), (B, H), (B, C), (B - C, 0), (C, 0), (0, C)]], [])
    a, f = B / 2, S * .6
    yo = a - f
    yi = yo + S * R2 - S
    g["V"] = (B, [[(0, H), (S, H), (S, yi), (a, yi - (a - S)), (B - S, yi), (B - S, H), (B, H), (B, yo), (a + f, 0), (a - f, 0), (0, yo)]], [])
    ww = mw
    g["W"] = (ww, [[(x, H - y) for x, y in m_pts]], [])   # W is the M turned over
    tx = S * 1.25
    g["X"] = (B, [[(0, H), (tx, H), (B, 0), (B - tx, 0)], [(0, 0), (tx, 0), (B, H), (B - tx, H)]], [])
    g["Y"] = (B, [[(0, H), (S, H), (S, t + c), (S + c, t), (B - S - c, t), (B - S, t + c), (B - S, H), (B, H), (B, b + C), (B - C, b),
                   (B / 2 + S / 2, b), (B / 2 + S / 2, 0), (B / 2 - S / 2, 0), (B / 2 - S / 2, b), (C, b), (0, b + C)]], [])
    g["Z"] = (B, [rect(0, H - S, B, H), rect(0, 0, B, S), [(0, S), (tx, S), (B, H - S), (B - tx, H - S)]], [])

    # figures
    g["0"] = (B, [crect(0, 0, B, H, C, C, C, C), [(B / 2 - S * .9, M - S * .9), (B / 2 - S * .1, M - S * .9), (B / 2 + S * .9, M + S * .9), (B / 2 + S * .1, M + S * .9)]],
              [crect(S, S, B - S, H - S, c, c, c, c)])
    ow = S * 2.2                       # the 1 is narrow: digits are proportional (readouts that must align use seg7)
    g["1"] = (ow, [crect(0, H - S, ow, H, tl=min(C, S)), rect(ow - S, 0, ow, H)], [])
    g["2"] = (B, [[(0, H), (B - C, H), (B, H - C), (B, b + C), (B - C, b), (S, b), (S, S), (B, S), (B, 0), (0, 0), (0, t - C), (C, t),
                   (B - S - c, t), (B - S, t + c), (B - S, H - S - c), (B - S - c, H - S), (0, H - S)]], [])
    g["3"] = (B, [[(0, H), (B - C, H), (B, H - C), (B, C), (B - C, 0), (0, 0), (0, S), (B - S - c, S), (B - S, S + c), (B - S, b),
                   (B * .3, b), (B * .3, t), (B - S, t), (B - S, H - S - c), (B - S - c, H - S), (0, H - S)]], [])
    g["4"] = (B, [[(0, H), (S, H), (S, t), (B - S, t), (B - S, H), (B, H), (B, 0), (B - S, 0), (B - S, b), (C, b), (0, b + C)]], [])
    g["5"] = (B, [[(0, H), (B, H), (B, H - S), (S, H - S), (S, t), (B - C, t), (B, t - C), (B, C), (B - C, 0), (0, 0), (0, S),
                   (B - S - c, S), (B - S, S + c), (B - S, b - c), (B - S - c, b), (0, b)]], [])
    six = [(C, H), (B, H), (B, H - S), (S + c, H - S), (S, H - S - c), (S, t), (B - C, t), (B, t - C), (B, C), (B - C, 0), (C, 0), (0, C), (0, H - C)]
    six_h = crect(S, S, B - S, b, br=c, bl=c)
    g["6"] = (B, [six], [six_h])
    g["7"] = (B, [rect(0, H - S, B - C, H), [(B - C, H), (B, H - C), (B, H - S)], [(0, 0), (tx, 0), (B, H - S), (B - tx, H - S)],
                  [(B - C, H - S), (B, H - S), (B, H - C), (B - C, H)]], [])
    n8 = S * .55                                   # the 8 is pinched at the waist on both sides (the B only on the right)
    g["8"] = (B, [[(C, H), (B - C, H), (B, H - C), (B, M + n8), (B - n8, M), (B, M - n8), (B, C), (B - C, 0), (C, 0), (0, C),
                   (0, M - n8), (n8, M), (0, M + n8), (0, H - C)]],
              [crect(S, t, B - S, H - S, c, c, 0, 0), crect(S, S, B - S, b, 0, 0, c, c)])
    flip = lambda pts: [(B - x, H - y) for x, y in pts]
    g["9"] = (B, [flip(six)], [flip(six_h)])

    # punctuation
    q = S * .9
    g["."] = (S, [rect(0, 0, S, S)], [])
    g[","] = (S, [[(0, S), (S, S), (S, 0), (S * .2, -S * .8), (0, -S * .8)]], [])
    g[":"] = (S, [rect(0, 0, S, S), rect(0, M - S / 2 + 60, S, M + S / 2 + 60)], [])
    g[";"] = (S, [[(0, S), (S, S), (S, 0), (S * .2, -S * .8), (0, -S * .8)], rect(0, M - S / 2 + 60, S, M + S / 2 + 60)], [])
    g["-"] = (B * .52, [rect(0, b, B * .52, t)], [])
    g["–"] = (B * .8, [rect(0, b, B * .8, t)], [])
    g["—"] = (B * 1.2, [rect(0, b, B * 1.2, t)], [])
    g["_"] = (B * .8, [rect(0, -S * 1.4, B * .8, -S * .4)], [])
    sw = H * .62
    g["/"] = (sw, [[(0, 0), (tx, 0), (sw, H), (sw - tx, H)]], [])
    g["·"] = (q, [rect(0, M - q / 2, q, M + q / 2)], [])
    g["'"] = (S, [rect(0, H - 260, S, H)], [])
    g['"'] = (S * 2.6, [rect(0, H - 260, S, H), rect(S * 1.6, H - 260, S * 2.6, H)], [])
    g["’"] = (S, [[(0, H), (S, H), (S, H - S), (S * .2, H - S * 1.8), (0, H - S * 1.8)]], [])
    g["‘"] = (S, [[(S, H - S * 1.8), (0, H - S * 1.8), (0, H - S * .8), (S * .8, H), (S, H)]], [])
    g["!"] = (S, [rect(0, S + 70, S, H), rect(0, 0, S, S)], [])
    qw = B * .8
    qx = qw / 2 - S / 2
    g["?"] = (qw, [[(0, H), (qw - C, H), (qw, H - C), (qw, b + C), (qw - C, b), (qx + S, b), (qx + S, S + 70), (qx, S + 70), (qx, t),
                    (qw - S - c, t), (qw - S, t + c), (qw - S, H - S - c), (qw - S - c, H - S), (0, H - S)], rect(qx, 0, qx + S, S)], [])
    pw = B * .9
    sq = S * 1.4
    g["%"] = (pw, [rect(0, H - sq, sq, H), rect(pw - sq, 0, pw, sq), [(0, 0), (tx, 0), (pw, H), (pw - tx, H)]], [])
    g["+"] = (B * .78, [rect(0, b, B * .78, t), rect(B * .39 - S / 2, M - B * .39, B * .39 + S / 2, M + B * .39)], [])
    g["="] = (B * .78, [rect(0, M + S * .35, B * .78, M + S * 1.35), rect(0, M - S * 1.35, B * .78, M - S * .35)], [])
    g["×"] = (B * .72, [[(0, M + B * .36 - 0), (tx * .8, M + B * .36), (B * .72, M - B * .36), (B * .72 - tx * .8, M - B * .36)],
                        [(0, M - B * .36), (tx * .8, M - B * .36), (B * .72, M + B * .36), (B * .72 - tx * .8, M + B * .36)]], [])
    g["°"] = (S * 3, [rect(0, H - S * 3, S * 3, H)], [rect(S * .9, H - S * 2.1, S * 2.1, H - S * .9)])
    g["º"] = (S * 3, [rect(0, H - S * 3, S * 3, H), rect(0, H - S * 4.2, S * 3, H - S * 3.6)], [rect(S * .9, H - S * 2.1, S * 2.1, H - S * .9)])
    bw = B * .44
    g["["] = (bw, [[(0, -S), (0, H + S * .4), (bw, H + S * .4), (bw, H - S * .6), (S, H - S * .6), (S, 0), (bw, 0), (bw, -S)]], [])
    g["]"] = (bw, [[(bw, -S), (bw, H + S * .4), (0, H + S * .4), (0, H - S * .6), (bw - S, H - S * .6), (bw - S, 0), (0, 0), (0, -S)]], [])
    g["("] = (bw, [[(C, H + S * .4), (bw, H + S * .4), (bw, H - S * .6), (S + c, H - S * .6), (S, H - S * .6 - c), (S, c), (S + c, 0),
                    (bw, 0), (bw, -S), (C, -S), (0, -S + C), (0, H + S * .4 - C)]], [])
    g[")"] = (bw, [[(bw - C, H + S * .4), (0, H + S * .4), (0, H - S * .6), (bw - S - c, H - S * .6), (bw - S, H - S * .6 - c), (bw - S, c),
                    (bw - S - c, 0), (0, 0), (0, -S), (bw - C, -S), (bw, -S + C), (bw, H + S * .4 - C)]], [])
    ew = B * .92
    g["€"] = (ew, [[(ew * .14 + C, H), (ew, H), (ew, H - S), (ew * .14 + S + c, H - S), (ew * .14 + S, H - S - c), (ew * .14 + S, S + c),
                    (ew * .14 + S + c, S), (ew, S), (ew, 0), (ew * .14 + C, 0), (ew * .14, C), (ew * .14, H - C)],
                   rect(0, M + S * .25, ew * .66, M + S * .9), rect(0, M - S * .9, ew * .66, M - S * .25)], [])
    g["$"] = (B, g["S"][1] + [rect(B / 2 - S / 2.4, -S * .8, B / 2 + S / 2.4, H + S * .8)], [])
    g["…"] = (S * 5, [rect(0, 0, S, S), rect(S * 2, 0, S * 3, S), rect(S * 4, 0, S * 5, S)], [])
    g["#"] = (B, [rect(0, M + S * .5, B, M + S * 1.4), rect(0, M - S * 1.4, B, M - S * .5),
                  rect(B * .28 - S / 2, 0, B * .28 + S / 2, H), rect(B * .72 - S / 2, 0, B * .72 + S / 2, H)], [])
    g["&"] = (B * 1.05, g["8"][1] + [rect(B - S, 0, B * 1.05, S)], g["8"][2])
    g["<"] = (B * .7, [[(B * .7, H * .85), (B * .7, H * .85 - T * .9), (B * .7 - (H * .35 - 0), M), (B * .7, H * .15 + T * .9), (B * .7, H * .15), (0, M)]], [])
    g[">"] = (B * .7, [[(0, H * .85), (0, H * .85 - T * .9), (H * .35, M), (0, H * .15 + T * .9), (0, H * .15), (B * .7, M)]], [])
    g["*"] = (B * .6, [rect(B * .3 - S / 2.5, H - B * .6, B * .3 + S / 2.5, H), rect(0, H - B * .3 - S / 2.5, B * .6, H - B * .3 + S / 2.5)], [])
    g["@"] = (B, [crect(0, 0, B, H, C, C, 0, C), rect(B * .4, 0, B, S)], [crect(S, S, B - S, H - S, c, c, 0, c)])
    # ---- diagonals: long 45° strokes at full weight. A free end is cut level and its
    # point trimmed by a short upright facet f; a joined end runs into its stem or bar.
    f = S * .42
    mx = lambda poly, w: [(w - x, y) for x, y in poly]
    my = lambda poly: [(x, H - y) for x, y in poly]
    # X: two strokes the full height, each landing on a facet
    xw = H + T * .9
    g["X"] = (xw, [clipbox(band(0, 0, H, T), f, xw - f, 0, H), clipbox(band(0, 0, H, T, rising=False), f, xw - f, 0, H)], [])
    # K: arms grow out of the stem and land on facets
    kw = B * .84
    ya, yb = M - S * .5, M + S * .5
    g["K"] = (kw, [rect(0, 0, S, H),
                   clipbox(band(kw - T - (H - ya), ya, H, T), 0, kw - f, ya, H),
                   clipbox(band(kw - T - yb, 0, yb, T, rising=False), 0, kw - f, 0, yb)], [])
    # R: the leg runs out of the bowl and lands on a facet
    pr = [(0, 0), (0, H), (B - C, H), (B, H - C), (B, b + C), (B - C, b), (S, b), (S, 0)]
    g["R"] = (B, [pr, clipbox(band(B - T - M, 0, M, T, rising=False), 0, B - f, 0, M)],
              [crect(S, t, B - S, H - S, tr=c, br=c)])
    # 7: the stem runs from the bar down to a facet
    y7 = H - S * .5
    g["7"] = (B, [rect(0, H - S, B, H), clipbox(band(B - T - y7, 0, y7, T), B - T - y7 + f, B, 0, y7)], [])
    # Z: the diagonal runs bar to bar
    zd = H - S
    g["Z"] = (B, [rect(0, H - S, B, H), rect(0, 0, B, S), band((B - T - zd) / 2, S / 2, H - S / 2, T)], [])
    # N: the diagonal leaves the top of the left stem and runs into the right one
    nw = B * .88
    yn = H - (nw - T)
    g["N"] = (nw, [rect(0, 0, S, H), rect(nw - S, 0, nw, H), clipbox(band(0, yn, H, T, rising=False), 0, nw, yn, H)], [])
    # M and W: the stems carry a V whose arms meet in a point
    mw = B * 1.2
    arm = clipbox(band(0, 0, H, T, rising=False), 0, mw / 2, 0, H)
    m_parts = [rect(0, 0, S, H), rect(mw - S, 0, mw, H), arm, mx(arm, mw)]
    g["M"] = (mw, m_parts, [])
    g["W"] = (mw, [my(q) for q in m_parts], [])
    # Y: arms land on facets at the top and meet over the stem
    yarm = clipbox(band(0, 0, H, T, rising=False), f, B / 2, 0, H)
    ytip = H - B / 2
    g["Y"] = (B, [yarm, mx(yarm, B), rect(B / 2 - S / 2, 0, B / 2 + S / 2, ytip + S)], [])
    # V: the U with deep cuts, the sides running down into a short foot
    cv = B / 2 - S * .75
    cvi = cv - S * (2 - R2)
    g["V"] = (B, [[(0, H), (0, cv), (cv, 0), (B - cv, 0), (B, cv), (B, H), (B - S, H), (B - S, S + cvi), (B - S - cvi, S),
                   (S + cvi, S), (S, S + cvi), (S, H)]], [])
    # 0: the O with the slash from the picture, its ends inside the frame
    zw = B * .86
    zo = crect(0, 0, zw, H, C, C, C, C)
    zs = band((zw - T - (H - 2 * S)) / 2, S, H - S, T)
    g["0"] = (zw, [zo, clipbox(zs, S * .5, zw - S * .5, S * .5, H - S * .5)], [crect(S, S, zw - S, H - S, c, c, c, c)])
    # 1 and 4: square flag and bar ends
    ow = S * 2.3
    g["1"] = (ow, [rect(0, H - S, ow, H), rect(ow - S, 0, ow, H)], [])
    g["4"] = (B, [[(0, H), (S, H), (S, t), (B - S, t), (B - S, H), (B, H), (B, 0), (B - S, 0), (B - S, b), (0, b)]], [])
    # slash and percent: steeper than 45° so they stay narrow, same facets
    sw, T2 = H * .6, S * 1.2
    sl = [(0, 0), (T2, 0), (sw, H), (sw - T2, H)]
    g["/"] = (sw, [clipbox(sl, f * .8, sw - f * .8, 0, H)], [])
    pw = B * .92
    sq = S * 1.5
    g["%"] = (pw, [rect(0, H - sq, sq, H), rect(pw - sq, 0, pw, sq), clipbox([(0, 0), (T2, 0), (pw, H), (pw - T2, H)], f, pw - f, 0, H)], [])
    # times: a small X
    th = H * .56
    tw = th + T * .8
    ty = M - th / 2
    tx = [[(x, y + ty) for x, y in clipbox(band(0, 0, th, T * .8), f * .7, tw - f * .7, 0, th)],
          [(x, y + ty) for x, y in clipbox(band(0, 0, th, T * .8, rising=False), f * .7, tw - f * .7, 0, th)]]
    g["×"] = (tw, tx, [])
    # angle brackets: two 45° strokes meeting in a point, free ends on facets
    aa = H * .36
    aw = T + aa - f
    up = clipbox(band(0, M, M + aa, T), 0, aw, M, M + aa)
    dn = clipbox(band(0, M - aa, M, T, rising=False), 0, aw, M - aa, M)
    g["<"] = (aw, [up, dn], [])
    g[">"] = (aw, [mx(up, aw), mx(dn, aw)], [])
    # comma, semicolon, quotes: upright tails
    tail = [rect(0, 0, S, S), rect(0, -S * .85, S * .55, 0)]
    g[","] = (S, tail, [])
    g[";"] = (S, tail + [rect(0, M - S / 2 + 60, S, M + S / 2 + 60)], [])
    g["’"] = (S, [rect(0, H - S, S, H), rect(S * .45, H - S * 1.85, S, H - S)], [])
    g["‘"] = (S, [rect(0, H - S, S, H), rect(0, H - S * 1.85, S * .55, H - S)], [])
    return g


ACCENTS = {  # name: shapes over the cap height, centred on 0; all square-ended like the letters
    "acute": lambda S, B: [rect(S * .1, S * .45, S * 1.1, S * 1.1), rect(-S * .45, 0, S * .55, S * .55)],
    "grave": lambda S, B: [rect(-S * 1.1, S * .45, -S * .1, S * 1.1), rect(-S * .55, 0, S * .45, S * .55)],
    "circ": lambda S, B: [rect(-S * 1.5, 0, -S * .5, S * .6), rect(-S * .6, S * .5, S * .6, S * 1.1), rect(S * .5, 0, S * 1.5, S * .6)],
    "uml": lambda S, B: [rect(-S * 1.6, 0, -S * .6, S * .8), rect(S * .6, 0, S * 1.6, S * .8)],
    "macron": lambda S, B: [rect(-B * .3, 0, B * .3, S * .6)],
    "tilde": lambda S, B: [rect(-S * 1.6, 0, -S * .6, S * .9), rect(-S * .7, S * .5, S * .7, S * .9), rect(-S * .1, 0, S * .9, S * .45),
                           rect(S * .6, 0, S * 1.6, S * .9)],
    "ring": lambda S, B: [rect(-S * 1.1, 0, S * 1.1, S * 1.4)],
}
ACCENT_HOLES = {"ring": lambda S, B: [rect(-S * .45, S * .45, S * .45, S * .95)]}
COMPOSED = {
    "À": ("A", "grave"), "Á": ("A", "acute"), "Â": ("A", "circ"), "Ä": ("A", "uml"), "Ã": ("A", "tilde"), "Å": ("A", "ring"), "Ā": ("A", "macron"),
    "È": ("E", "grave"), "É": ("E", "acute"), "Ê": ("E", "circ"), "Ë": ("E", "uml"), "Ē": ("E", "macron"),
    "Ì": ("I", "grave"), "Í": ("I", "acute"), "Î": ("I", "circ"), "Ï": ("I", "uml"),
    "Ò": ("O", "grave"), "Ó": ("O", "acute"), "Ô": ("O", "circ"), "Ö": ("O", "uml"), "Õ": ("O", "tilde"), "Ō": ("O", "macron"),
    "Ù": ("U", "grave"), "Ú": ("U", "acute"), "Û": ("U", "circ"), "Ü": ("U", "uml"), "Ū": ("U", "macron"),
    "Ñ": ("N", "tilde"), "Ý": ("Y", "acute"), "Ÿ": ("Y", "uml"),
}


def ink_left(shapes, y):
    """Leftmost ink at height y across all shapes (None if the row is empty)."""
    best = None
    for pts in shapes:
        for (xa, ya), (xb, yb) in zip(pts, pts[1:] + pts[:1]):
            if (ya <= y < yb) or (yb <= y < ya):
                x = xa + (y - ya) * (xb - xa) / (yb - ya)
                best = x if best is None else min(best, x)
    return best


def side_space(ch, shapes, SB):
    """Optical spacing. Each side gets the base bearing minus part of the white it
    already holds, so open and diagonal sides (A, K, L, T, V, X, Y, 7) sit as
    close as straight stems do. Punctuation keeps the plain bearing."""
    xs = [x for pts in shapes for x, _ in pts]
    x0, x1 = min(xs), max(xs)
    if not ch.isalnum() or ch in "×":
        return SB, SB, x0, x1
    mirrored = [[(-x, y) for x, y in pts] for pts in shapes]
    out = []
    for side, x_edge in ((shapes, x0), (mirrored, -x1)):
        gaps = []
        for y in range(10, H, 20):
            e = ink_left(side, y)
            gaps.append(min(260, (e - x_edge) if e is not None else 260))
        avg = sum(gaps) / len(gaps)
        out.append(max(SB * .3, SB - .42 * avg))
    return out[0], out[1], x0, x1


# pairs the optical spacing cannot fix on its own (units of 1/1000 em)
KERN = {("L", "T"): -70, ("L", "Y"): -60, ("L", "V"): -50, ("T", "A"): -55, ("A", "T"): -55, ("A", "V"): -40,
        ("V", "A"): -40, ("A", "Y"): -45, ("Y", "A"): -45, ("P", "A"): -45, ("F", "A"): -35, ("T", "."): -60,
        ("T", ","): -60, ("Y", "."): -50, ("Y", ","): -50, ("P", "."): -60, ("P", ","): -60, ("F", "."): -45,
        ("F", ","): -45, ("7", "."): -40, ("L", "’"): -70, ("T", "J"): -40, ("Y", "J"): -35, ("A", "’"): -40,
        ("K", "O"): -20, ("X", "O"): -15, ("T", "O"): -15, ("O", "T"): -15, ("R", "T"): -25, ("R", "Y"): -25}


def build(weight):
    P = WEIGHTS[weight]
    S, SB, SP = P["S"], P["SB"], P["SP"]
    g = glyphs(**P)
    gap = S * .45
    for ch, (base, acc) in COMPOSED.items():
        w, shapes, holes = g[base]
        dx = w / 2
        up = lambda pts: [(x + dx, y + H + gap) for x, y in pts]
        g[ch] = (w, shapes + [up(p) for p in ACCENTS[acc](S, P["B"])],
                 holes + [up(p) for p in ACCENT_HOLES.get(acc, lambda *_: [])(S, P["B"])])
    g["Ç"] = (g["C"][0], g["C"][1] + [rect(g["C"][0] * .45, -S * 1.1, g["C"][0] * .45 + S * .9, 0)], [])

    names = {ch: ("uni%04X" % ord(ch)) for ch in g}
    order = [".notdef", "space"] + [names[ch] for ch in g]
    pen_glyphs, metrics, cmap = {}, {}, {32: "space", 0xA0: "space"}

    def draw(shapes, holes):
        pen = TTGlyphPen(None)
        for pts, outer in [(s, True) for s in shapes] + [(h, False) for h in holes]:
            pts = [(round(x), round(y)) for x, y in pts]
            # TrueType: filled contours run clockwise, holes counter-clockwise (y up)
            if (area(pts) < 0) != outer:
                pts = pts[::-1]
            pen.moveTo(pts[0])
            for p in pts[1:]:
                pen.lineTo(p)
            pen.closePath()
        return pen.glyph()

    pen_glyphs[".notdef"] = draw([rect(0, 0, 500, H)], [rect(S * .6, S * .6, 500 - S * .6, H - S * .6)])
    metrics[".notdef"] = (500 + 2 * SB, 0)
    pen_glyphs["space"] = TTGlyphPen(None).glyph()
    metrics["space"] = (SP, 0)
    for ch, (w, shapes, holes) in g.items():
        n = names[ch]
        lsb, rsb, x0, x1 = side_space(ch, shapes, SB)
        shifted = lambda pts: [(x - x0 + lsb, y) for x, y in pts]
        pen_glyphs[n] = draw([shifted(s) for s in shapes], [shifted(h) for h in holes])
        metrics[n] = (round(lsb + (x1 - x0) + rsb), round(lsb))
        cmap[ord(ch)] = n
        # caps only: no lowercase, so units inside figures ("38 km/h") fall through to Shingo Signal

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(pen_glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=930, descent=-250)
    family = "Shingo Grid"
    fb.setupNameTable({"familyName": family, "styleName": weight, "uniqueFontIdentifier": f"ShingoGrid-{weight}",
                       "fullName": f"{family} {weight}", "psName": f"ShingoGrid-{weight}", "version": "Version 1.000",
                       "copyright": "Shingo Grid. MIT licence, see LICENSE."})
    fb.setupOS2(sTypoAscender=930, sTypoDescender=-250, sTypoLineGap=0, usWinAscent=1000, usWinDescent=300,
                sCapHeight=H, sxHeight=H, usWeightClass=900, achVendID="SHGO",
                fsSelection=0x20)
    fb.setupPost()
    kern = "\n".join(f"  pos {names[l]} {names[r]} {v};" for (l, r), v in KERN.items() if l in names and r in names)
    from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
    addOpenTypeFeaturesFromString(fb.font, "languagesystem DFLT dflt;\nlanguagesystem latn dflt;\nfeature kern {\n" + kern + "\n} kern;\n")
    from fontTools.misc.timeTools import timestampFromString
    ts = timestampFromString("Thu Nov 19 00:00:00 2026")     # fixed, so rebuilds are byte-identical
    fb.setupHead(unitsPerEm=UPM, macStyle=1, created=ts, modified=ts)
    return fb.font


def main():
    ios = ROOT / "ios" / "Sources" / "ShingoKit" / "Resources" / "Fonts"
    web = ROOT / "web" / "fonts"
    web.mkdir(parents=True, exist_ok=True)
    for w in WEIGHTS:
        f = build(w)
        f.save(ios / f"ShingoGrid-{w}.ttf")
        f.flavor = "woff2"
        f.save(web / f"ShingoGrid-{w}.woff2")
        print(f"ShingoGrid-{w}: {len(f.getGlyphOrder())} glyphs, woff2 {(web / f'ShingoGrid-{w}.woff2').stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
