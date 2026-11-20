"""Shingō Grid: the system's own display face.

    python3 tools/font.py

Wide, short and hard, after the RADAR poster. Every stroke has one heavy weight,
every glyph is drawn from level, upright and 45° edges on a grid, and wherever a
letter would normally curve it is cut at 45°. Diagonals are long 45° strokes
at full weight; a free end is cut level and its point trimmed by an upright facet. One cut, Heavy, for display,
titles and numbers (subheads and labels are Shingo Signal, see signal_font.py).

Writes ios/Sources/ShingoKit/Resources/Fonts/ShingoGrid-Heavy.ttf and
web/fonts/ShingoGrid-Heavy.woff2. Capitals, figures and a full lowercase (x-height X, ascenders A,
descenders D, all drawn on the same weight and cuts).
"""
import math
import pathlib

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

ROOT = pathlib.Path(__file__).resolve().parent.parent
R2 = math.sqrt(2)
H = 650          # cap height (short: the face is stubby, wider than tall)
UPM = 1000

WEIGHTS = {
    # stroke, outer cut, body width, side bearing, space. One cut, after the RADAR reference:
    # strokes about a fifth of the cap height, cuts a little larger than the stroke, letters wider than tall.
    "Heavy": dict(S=132, C=170, B=860, SB=84, SP=330),
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
    e = B * .76                                    # middle arm shorter than top and foot, so E/F have rhythm
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
    qy1 = S * .95                                  # the tail stays below the counter and crosses the chamfer square-on
    qtail = clipbox(band(B - C / 2 - (qy1 - C / 2) - T / 2, -S * .45, qy1, T, rising=False), 0, B + S * .55, -S * .45, H)
    g["Q"] = (B + S * .55, [crect(0, 0, B, H, C, C, C, C), qtail], [crect(S, S, B - S, H - S, c, c, c, c)])
    xl = B - T - b
    g["R"] = (B, [[(0, 0), (0, H), (B - C, H), (B, H - C), (B, b + C), (B - C, b), (S, b), (S, 0)],
                  [(xl, b + 1), (xl + T, b + 1), (B, 0), (B - T, 0)]],
              [crect(S, t, B - S, H - S, tr=c, br=c)])
    Cm, cm = S, S * (R2 - 1)                    # middle turns: outer cut = bar height, inner keeps full weight
    g["S"] = (B, [[(C, H), (B, H), (B, H - S), (S + c, H - S), (S, H - S - c), (S, t + cm), (S + cm, t), (B - Cm, t), (B, t - Cm), (B, C), (B - C, 0), (0, 0),
                   (0, S), (B - S - c, S), (B - S, S + c), (B - S, b - cm), (B - S - cm, b), (Cm, b), (0, b + Cm), (0, H - C)]], [])
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
    g["2"] = (B, [[(0, H), (B - C, H), (B, H - C), (B, b + Cm), (B - Cm, b), (S + cm, b), (S, b - cm), (S, S), (B, S), (B, 0), (0, 0), (0, t - Cm), (Cm, t),
                   (B - S - cm, t), (B - S, t + cm), (B - S, H - S - c), (B - S - c, H - S), (0, H - S)]], [])
    g["3"] = (B, [[(0, H), (B - C, H), (B, H - C), (B, C), (B - C, 0), (0, 0), (0, S), (B - S - c, S), (B - S, S + c), (B - S, b),
                   (B * .3, b), (B * .3, t), (B - S, t), (B - S, H - S - c), (B - S - c, H - S), (0, H - S)]], [])
    g["4"] = (B, [[(0, H), (S, H), (S, t), (B - S, t), (B - S, H), (B, H), (B, 0), (B - S, 0), (B - S, b), (C, b), (0, b + C)]], [])
    g["5"] = (B, [[(0, H), (B, H), (B, H - S), (S, H - S), (S, t), (B - Cm, t), (B, t - Cm), (B, C), (B - C, 0), (0, 0), (0, S),
                   (B - S - c, S), (B - S, S + c), (B - S, b - cm), (B - S - cm, b), (0, b)]], [])
    six = [(C, H), (B, H), (B, H - S), (S + c, H - S), (S, H - S - c), (S, t), (B - Cm, t), (B, t - Cm), (B, C), (B - C, 0), (C, 0), (0, C), (0, H - C)]
    six_h = crect(S, S, B - S, b, tr=cm, br=c, bl=c)
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
    q7 = S * .7
    g["·"] = (q7, [rect(0, M - q7 / 2, q7, M + q7 / 2)], [])
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
    # $: the S with two upright bars through it, the same weight, set symmetrically about the centre
    dbw, dbg = S * .42, S * .55
    g["$"] = (B, g["S"][1] + [rect(B / 2 - dbg / 2 - dbw, -S * .7, B / 2 - dbg / 2, H + S * .7),
                              rect(B / 2 + dbg / 2, -S * .7, B / 2 + dbg / 2 + dbw, H + S * .7)], [])
    g["…"] = (S * 5, [rect(0, 0, S, S), rect(S * 2, 0, S * 3, S), rect(S * 4, 0, S * 5, S)], [])
    g["#"] = (B, [rect(0, M + S * .5, B, M + S * 1.4), rect(0, M - S * 1.4, B, M - S * .5),
                  rect(B * .28 - S / 2, 0, B * .28 + S / 2, H), rect(B * .72 - S / 2, 0, B * .72 + S / 2, H)], [])
    # &: a small cut loop on top, an open bowl below, and a 45° leg from the waist to the baseline
    aw = B * .92
    lt = M + S * .35                                   # top of the lower bowl
    cl = C * .75
    cin = max(0, cl - S * (2 - R2))
    loop = crect(S * .35, M - S * .25, aw * .62, H, cl, cl, cl, cl)
    loop_h = crect(S * 1.35, M + S * .75, aw * .62 - S, H - S, cin, cin, cin, cin)
    x1 = aw * .7
    bowl = [(cl, lt), (x1, lt), (x1, lt - S), (S + cin, lt - S), (S, lt - S - cin), (S, S + max(0, C - S * (2 - R2))),
            (S + max(0, C - S * (2 - R2)), S), (x1, S), (x1, 0), (C, 0), (0, C), (0, lt - cl)]
    leg = clipbox(band(aw - T - lt, 0, lt, T, rising=False), 0, aw, 0, lt)
    g["&"] = (aw, [loop, bowl, leg], [loop_h])
    g["<"] = (B * .7, [[(B * .7, H * .85), (B * .7, H * .85 - T * .9), (B * .7 - (H * .35 - 0), M), (B * .7, H * .15 + T * .9), (B * .7, H * .15), (0, M)]], [])
    g[">"] = (B * .7, [[(0, H * .85), (0, H * .85 - T * .9), (H * .35, M), (0, H * .15 + T * .9), (0, H * .15), (B * .7, M)]], [])
    g["*"] = (B * .6, [rect(B * .3 - S / 2.5, H - B * .6, B * .3 + S / 2.5, H), rect(0, H - B * .3 - S / 2.5, B * .6, H - B * .3 + S / 2.5)], [])
    # @: a cut frame open at the lower right, a solid core, and the tail running out along the baseline
    g["@"] = (B, [crect(0, 0, B, H, C, C, 0, C), rect(B / 2 - S * .85, M - S * .85, B / 2 + S * .85, M + S * .85), rect(B * .45, 0, B, S)],
              [crect(S, S, B - S, H - S, c, c, 0, c)])
    # ---- diagonals: long 45° strokes at full weight. A free end is cut level and its
    # point trimmed by a short upright facet f; a joined end runs into its stem or bar.
    f = S * .42
    mx = lambda poly, w: [(w - x, y) for x, y in poly]
    my = lambda poly: [(x, H - y) for x, y in poly]
    # X: two strokes the full height, each landing on a facet
    xw = H + T * .9
    g["X"] = (xw, [clipbox(band(0, 0, H, T), f, xw - f, 0, H), clipbox(band(0, 0, H, T, rising=False), f, xw - f, 0, H)], [])
    # K: arms grow out of the stem and land on facets
    ya, yb = M - S * .5, M + S * .5
    kw = B * .94                                   # wide: a level spur at the waist carries the arms out from the stem
    kx = kw - T - (H - ya)
    g["K"] = (kw, [rect(0, 0, S, H), rect(S * .5, ya, kx + T * .5, yb),
                   clipbox(band(kw - T - (H - ya), ya, H, T), 0, kw - f, ya, H),
                   clipbox(band(kw - T - yb, 0, yb, T, rising=False), 0, kw - f, 0, yb)], [])
    # R: the leg runs out of the bowl and lands on a facet
    pr = [(0, 0), (0, H), (B - C, H), (B, H - C), (B, b + C), (B - C, b), (S, b), (S, 0)]
    g["R"] = (B, [pr, clipbox(band(B - T - M, 0, M, T, rising=False), 0, B - f, 0, M)],
              [crect(S, t, B - S, H - S, tr=c, br=c)])
    # 7: the stem runs from the bar down to a facet
    y7 = H - S
    g["7"] = (B, [crect(0, H - S, B, H, tr=C * .75), clipbox(band(B - T - y7, 0, y7, T), B - T - y7 + f, B, 0, y7)], [])
    # Z: the diagonal runs bar to bar
    # Z: the diagonal's edges land exactly on the bars' inner corners, so the width follows from the 45°
    zd = H - 2 * S
    zw = zd + T
    g["Z"] = (zw, [rect(0, H - S, zw, H), rect(0, 0, zw, S), band(0, S - 1, H - S + 1, T)], [])
    # N: the diagonal leaves the top of the left stem and runs into the right one
    # N: one 45° stroke from the top-left corner to the bottom-right corner, between full stems
    nw = H + T
    g["N"] = (nw, [rect(0, 0, S, H), rect(nw - S, 0, nw, H), band(0, 0, H, T, rising=False)], [])
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
    # figures share one width (tabular) and the letters' chamfers
    zo = crect(0, 0, B, H, C, C, C, C)
    zt = T                                         # the slash at full stroke weight
    zs = band((B - zt - (H - 2 * S)) / 2, S, H - S, zt)
    g["0"] = (B, [zo, clipbox(zs, S - 1, B - S + 1, S - 1, H - S + 1)], [crect(S, S, B - S, H - S, c, c, c, c)])
    # 1 and 4: square flag and bar ends
    xs1 = B / 2 + S * .2                            # the 1: stem just right of centre, a chamfered flag, a foot
    g["1"] = (B, [crect(xs1 - S * 1.5, H - S, xs1 + S, H, tl=C * .8), rect(xs1, 0, xs1 + S, H),
                  rect(xs1 - S * 1.3, 0, xs1 + S * 2.3, S)], [])
    # the 4: closed by a 45° diagonal from the bar's left end up into the stem; the bar runs a little past the stem
    # full width: the diagonal rises from the bar's left end to the cap line, a top bar carries it into the
    # stem through a chamfer, and the crossbar runs a little past the stem
    d4 = H - b
    sr = B - S * .55                                # stem's right edge
    g["4"] = (B, [rect(sr - S, 0, sr, H), band(0, b, H, T), crect(d4, H - S, sr, H, tr=C * .75), rect(0, b, B, t)], [])
    # the 3: the middle bar reaches back as far as the top and bottom ends do
    g["3"] = (B, [[(0, H), (B - C, H), (B, H - C), (B, C), (B - C, 0), (0, 0), (0, S), (B - S - c, S), (B - S, S + c), (B - S, b),
                   (B * .45, b), (B * .45, t), (B - S, t), (B - S, H - S - c), (B - S - c, H - S), (0, H - S)]], [])
    # the 5: the top-left turn takes the chamfer too
    g["5"] = (B, [[(C, H), (B, H), (B, H - S), (S + c, H - S), (S, H - S - c), (S, t), (B - Cm, t), (B, t - Cm), (B, C), (B - C, 0), (0, 0), (0, S),
                   (B - S - c, S), (B - S, S + c), (B - S, b - cm), (B - S - cm, b), (0, b), (0, H - C)]], [])
    # slash and percent: steeper than 45° so they stay narrow, same facets
    sw, T2 = H * .6, S * 1.2
    sl = [(0, 0), (T2, 0), (sw, H), (sw - T2, H)]
    g["/"] = (sw, [clipbox(sl, f * .8, sw - f * .8, 0, H)], [])
    pw = B * .92
    sq = S * 1.5
    sq = S * 1.55                                  # two big square dots and a steep slash between them
    pw = H * .95
    sl_ = clipbox([(0, 0), (T2, 0), (pw, H), (pw - T2, H)], 0, pw, 0, H)
    g["%"] = (pw, [rect(0, H - sq, sq, H), rect(pw - sq, 0, pw, sq),
                   clipbox(sl_, 0, pw, 0, H)], [])
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
    g.update(lowercase(S, C, B, f))
    return g


X = round(H * .74)     # x-height: high, so the heavy stroke still leaves open counters
A = round(H * 1.05)    # ascenders (b d f h k l) rise a little past the caps; t stops at the cap height
D = -round(H * .30)    # descenders (g j p q y)


def lowercase(S, C, B, f):
    """The lowercase: the capitals' DNA at x-height. One upright weight S, level bars, 45°
    cuts wherever a letter would curve (scaled with the x-height, so they read as big as the
    capitals' do), inner corners cut to keep the weight, diagonals at full weight cut level.
    Short turns (the descender hooks, the f's head, the middle of the s) take a cut no deeper
    than the bar they turn into. Only e and s, which stack three bars inside the x-height,
    carry lighter bars (Se), so their counters stay open."""
    T = S * R2
    k = S * (2 - R2)                   # outer cut minus inner cut, for a corner of two S strokes
    Cl = round(C * .8)                 # the lowercase cut (C scaled towards the x-height)
    cl = Cl - k
    Cm, cm = S, S * (R2 - 1)           # short turns: outer cut = the bar, inner keeps the weight
    W = B * .84                        # bowls: a little narrower than the caps, still wider than tall
    Wn = B * .8                        # n h u v y
    gi = A - X - S                     # the gap under the i/j dot, the f's head
    g = {}

    def ring(x0, y0, x1, y1, tl=0, tr=0, br=0, bl=0):
        i = lambda v: max(0.0, v - k) if v else 0
        return crect(x0, y0, x1, y1, tl, tr, br, bl), crect(x0 + S, y0 + S, x1 - S, y1 - S, i(tl), i(tr), i(br), i(bl))

    o, oh = ring(0, 0, W, X, Cl, Cl, Cl, Cl)
    g["o"] = (W, [o], [oh])
    a, ah = ring(0, 0, W, X, tl=Cl, bl=Cl)                # single storey: the bowl hangs on a square stem
    g["a"] = (W, [a], [ah])
    g["d"] = (W, [a, rect(W - S, 0, W, A)], [ah])
    g["q"] = (W, [a, rect(W - S, D, W, X)], [ah])
    bb, bh = ring(0, 0, W, X, tr=Cl, br=Cl)
    g["b"] = (W, [bb, rect(0, 0, S, A)], [bh])
    g["p"] = (W, [bb, rect(0, D, S, X)], [bh])
    cw = W * .92
    g["c"] = (cw, [[(Cl, X), (cw, X), (cw, X - S), (S + cl, X - S), (S, X - S - cl), (S, S + cl), (S + cl, S), (cw, S), (cw, 0),
                    (Cl, 0), (0, Cl), (0, X - Cl)]], [])
    # n h m: the shoulder takes the cut, the stem stays square; u is the n turned over
    arch = lambda w, top: [(0, 0), (0, top)] + ([(S, top), (S, X)] if top > X else []) + \
        [(w - Cl, X), (w, X - Cl), (w, 0), (w - S, 0), (w - S, X - S - cl), (w - S - cl, X - S), (S, X - S), (S, 0)]
    g["n"] = (Wn, [arch(Wn, X)], [])
    g["h"] = (Wn, [arch(Wn, A)], [])
    mw = B * 1.2
    mx = mw / 2
    g["m"] = (mw, [arch(mw, X), rect(mx - S / 2, 0, mx + S / 2, X - S + 1)], [])
    g["u"] = (Wn, [[(0, X), (S, X), (S, S + cl), (S + cl, S), (Wn - S, S), (Wn - S, X), (Wn, X), (Wn, 0), (Cl, 0), (0, Cl)]], [])

    # e and s: three bars in the x-height, so lighter bars and cuts sized to their counters
    Se = round(S * .8)
    ke = S * R2 - S - Se               # inner cut = outer cut + ke, for a corner of stem S and bar Se
    ha = 68                            # e: the lower aperture
    y1 = Se + ha                       # crossbar bottom
    y2 = y1 + Se                       # crossbar top
    ie = 70                            # inner cut of the eye's top corners
    Ce = ie - ke
    Cb = ha - ke                       # bottom-left: the inner cut runs exactly up to the crossbar
    g["e"] = (W, [[(0, X - Ce), (Ce, X), (W - Ce, X), (W, X - Ce), (W, y1), (S, y1), (S + ha, Se), (W, Se), (W, 0), (Cb, 0), (0, Cb)]],
              [crect(S, y2, W - S, X - Se, tl=ie, tr=ie)])
    Ws = W * .9
    mb = (X - Se) / 2
    mt = mb + Se
    it, im = 42, 28                    # inner cuts: end turns, middle turns (they share each counter's side)
    Ct, Cs = it - ke, im - ke
    g["s"] = (Ws, [[(Ct, X), (Ws, X), (Ws, X - Se), (S + it, X - Se), (S, X - Se - it), (S, mt + im), (S + im, mt), (Ws - Cs, mt), (Ws, mt - Cs),
                    (Ws, Ct), (Ws - Ct, 0), (0, 0), (0, Se), (Ws - S - it, Se), (Ws - S, Se + it), (Ws - S, mb - im), (Ws - S - im, mb), (Cs, mb),
                    (0, mb + Cs), (0, X - Ct)]], [])

    # descender hooks: the stem turns left along the descender with a short-turn cut
    def hook(xr, x0):
        return [(xr - S, S), (xr, S), (xr, D + Cm), (xr - Cm, D), (x0, D), (x0, D + S), (xr - S - cm, D + S), (xr - S, D + S + cm)]
    g["g"] = (W, [a, hook(W, 0)], [ah])

    # i j l: stems; dots are S squares; l and t stand on a short cut foot
    dot = lambda x: rect(x, X + gi, x + S, A)
    g["ı"] = (S, [rect(0, 0, S, X)], [])
    g["i"] = (S, [rect(0, 0, S, X), dot(0)], [])
    jw = S * 2.2
    g["j"] = (jw, [[(jw - S, X), (jw, X)] + hook(jw, 0)[2:], dot(jw - S)], [])
    foot = lambda x, top, w: [(x, top), (x + S, top), (x + S, S + cl), (x + S + cl, S), (w, S), (w, 0), (x + Cl, 0), (x, Cl)]
    g["l"] = (S * 2.1, [foot(0, A, S * 2.1)], [])
    xs = S * .55
    tw = xs + S + S * 1.15
    g["t"] = (tw, [foot(xs, H, tw), rect(0, X - S, tw, X)], [])
    # f: the head's inner cut runs exactly down to the crossbar, so no sliver of white is left
    Cf = gi + k
    fw = xs + S + S * 1.25
    g["f"] = (fw, [[(xs, 0), (xs, A - Cf), (xs + Cf, A), (fw, A), (fw, A - S), (xs + S + gi, A - S), (xs + S, X), (xs + S, 0)],
                   rect(0, X - S, xs + S + S * 1.05, X)], [])
    # r: the n's shoulder, cut short and level
    rw = S * 3.1
    g["r"] = (rw, [[(0, 0), (0, X), (rw - Cl, X), (rw, X - Cl), (rw, X - S - cl), (rw - S, X - S - cl), (rw - S - cl, X - S), (S, X - S), (S, 0)]], [])
    # k: arms grow out of the stem and land on facets, as in the K
    ya, yb = X / 2 - S * .5, X / 2 + S * .5
    kw = S * .4 + T + (X - ya)
    g["k"] = (kw, [rect(0, 0, S, A),
                   clipbox(band(kw - T - (X - ya), ya, X, T), 0, kw - f, ya, X),
                   clipbox(band(kw - T - yb, 0, yb, T, rising=False), 0, kw - f, 0, yb)], [])
    # v: the V's deep cuts into a short foot; y: the left half of the v, the right side a stem
    # running down into the descender hook; w: a u with both feet cut and a short middle stem
    cv = Wn / 2 - S * .75
    cvi = cv - k
    g["v"] = (Wn, [[(0, X), (0, cv), (cv, 0), (Wn - cv, 0), (Wn, cv), (Wn, X), (Wn - S, X), (Wn - S, S + cvi), (Wn - S - cvi, S),
                    (S + cvi, S), (S, S + cvi), (S, X)]], [])
    g["y"] = (Wn, [[(0, X), (S, X), (S, S + cvi), (S + cvi, S), (Wn - S, S), (Wn - S, X), (Wn, X), (Wn, 0), (cv, 0), (0, cv)], hook(Wn, 0)], [])
    ww = mw
    wm = X * .78
    g["w"] = (ww, [[(0, X), (S, X), (S, S + cl), (S + cl, S), (mx - S / 2, S), (mx - S / 2, wm), (mx + S / 2, wm), (mx + S / 2, S),
                    (ww - S - cl, S), (ww - S, S + cl), (ww - S, X), (ww, X), (ww, Cl), (ww - Cl, 0), (Cl, 0), (0, Cl)]], [])
    # x z: the X and Z at x-height; the z's bars run a little past its diagonal
    xw = X + T * .9
    g["x"] = (xw, [clipbox(band(0, 0, X, T), f, xw - f, 0, X), clipbox(band(0, 0, X, T, rising=False), f, xw - f, 0, X)], [])
    ze = S * .35
    zw = X - 2 * S + T + 2 * ze
    g["z"] = (zw, [rect(0, X - S, zw, X), rect(0, 0, zw, S), band(ze, S - 1, X - S + 1, T)], [])
    return g


def _acc_band(x0, h, w, rising=True):
    return band(x0, 0, h, w, rising)


ACCENTS = {  # shapes over the cap height, centred on 0: 45° strokes cut level, like the letters' diagonals
    "acute": lambda S, B: [_acc_band(-S * .95, S * 1.15, S * .8)],
    "grave": lambda S, B: [_acc_band(-S * .15 - S * .05, S * 1.15, S * .8, rising=False)],
    "circ": lambda S, B: [[(-S * 1.55, 0), (-S * .75, 0), (0, S * .75), (S * .75, 0), (S * 1.55, 0), (S * .4, S * 1.15), (-S * .4, S * 1.15)]],
    "uml": lambda S, B: [rect(-S * 1.7, 0, -S * .6, S * 1.0), rect(S * .6, 0, S * 1.7, S * 1.0)],
    "macron": lambda S, B: [rect(-B * .3, 0, B * .3, S * .62)],
    "tilde": lambda S, B: [_acc_band(-S * 1.9, S * .95, S * .75), [(x + S * .95, y) for x, y in _acc_band(-S * 1.9, S * .95, S * .75, rising=False)],
                           [(x + S * 1.9, y) for x, y in _acc_band(-S * 1.9, S * .95, S * .75)]],
    "ring": lambda S, B: [crect(-S * 1.25, 0, S * 1.25, S * 1.6, tl=S * .6, tr=S * .6, br=S * .6, bl=S * .6)],
}
ACCENT_HOLES = {"ring": lambda S, B: [crect(-S * .5, S * .5, S * .5, S * 1.1, tl=S * .2, tr=S * .2, br=S * .2, bl=S * .2)]}
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


def snap(pts):
    """Whole font units, keeping every 45° edge exactly 45°: a point that starts a 45°
    edge from an already snapped point moves by the same amount in x and y."""
    out = [(round(pts[0][0]), round(pts[0][1]))]
    for (px, py), (x, y) in zip(pts, pts[1:]):
        dx, dy = x - px, y - py
        if abs(abs(dx) - abs(dy)) < 1e-6 and abs(dx) > 1e-6:      # a true 45° step
            d = round(abs(dx))
            out.append((out[-1][0] + (d if dx > 0 else -d), out[-1][1] + (d if dy > 0 else -d)))
        else:
            out.append((round(x), round(y)))
    return out


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
    top = X if ch.islower() else H                  # lowercase meet their neighbours in the x-height
    out = []
    for side, x_edge in ((shapes, x0), (mirrored, -x1)):
        gaps = []
        for y in range(10, top, 20):
            e = ink_left(side, y)
            gaps.append(min(260, (e - x_edge) if e is not None else 260))
        avg = sum(gaps) / len(gaps)
        out.append(max(SB * .4, SB - .36 * avg))
    l, r = TRIM.get(ch, (0, 0))
    return out[0] - l * S_TRIM, out[1] - r * S_TRIM, x0, x1


S_TRIM = 132
# open sides the measure under-reads: (left, right) trims in strokes
TRIM = {"C": (0, .3), "G": (0, .25), "L": (0, .4), "J": (.25, 0), "F": (0, .2), "E": (0, .08), "K": (0, .1),
        "O": (.1, .1), "Q": (.1, 0), "D": (0, .1), "R": (0, .1), "T": (.05, .05),
        "c": (0, .25), "r": (0, .35), "f": (0, .3), "t": (0, .2), "j": (.2, 0), "k": (0, .1), "e": (0, .1), "o": (.08, .08)}


# pairs the optical spacing cannot fix on its own (units of 1/1000 em)
KERN = {("L", "T"): -110, ("L", "Y"): -110, ("L", "V"): -100, ("L", "A"): -40, ("L", "O"): -35, ("L", "’"): -110,
        ("T", "A"): -75, ("A", "T"): -75, ("A", "V"): -85, ("V", "A"): -85, ("A", "Y"): -85, ("Y", "A"): -85,
        ("A", "W"): -40, ("W", "A"): -40, ("P", "A"): -75, ("F", "A"): -65, ("P", "."): -90, ("P", ","): -90,
        ("F", "."): -70, ("F", ","): -70, ("T", "."): -80, ("T", ","): -80, ("Y", "."): -80, ("Y", ","): -80,
        ("V", "."): -70, ("V", ","): -70, ("7", "."): -60, ("T", "J"): -60, ("Y", "J"): -55, ("A", "’"): -70,
        ("K", "O"): -30, ("X", "O"): -25, ("T", "O"): -25, ("O", "T"): -25, ("Y", "O"): -30, ("O", "Y"): -30,
        ("O", "V"): -25, ("V", "O"): -25, ("R", "T"): -40, ("R", "Y"): -45, ("R", "V"): -35, ("F", "L"): -20,
        ("L", "U"): -20, ("T", "T"): -20, ("1", "1"): -30,
        # lowercase and mixed
        ("T", "a"): -70, ("T", "e"): -70, ("T", "o"): -70, ("T", "c"): -60, ("T", "r"): -40, ("T", "u"): -40, ("T", "y"): -40,
        ("V", "a"): -50, ("V", "e"): -50, ("V", "o"): -50, ("Y", "a"): -60, ("Y", "e"): -60, ("Y", "o"): -60,
        ("P", "a"): -40, ("P", "o"): -35, ("F", "a"): -40, ("F", "o"): -35, ("L", "y"): -60, ("L", "v"): -50,
        ("r", "."): -70, ("r", ","): -70, ("f", "."): -50, ("f", ","): -50, ("y", "."): -50, ("y", ","): -50, ("v", "."): -45,
        ("r", "a"): -20, ("a", "v"): -25, ("a", "y"): -25, ("v", "a"): -25, ("y", "a"): -25, ("y", "o"): -20, ("o", "y"): -20,
        ("k", "o"): -20, ("k", "e"): -20, ("f", "f"): -20}


def build(weight):
    P = WEIGHTS[weight]
    S, SB, SP = P["S"], P["SB"], P["SP"]
    g = glyphs(**P)
    gap = S * .5
    for ch, (base, acc) in COMPOSED.items():
        w, shapes, holes = g[base]
        dx = w / 2
        top = X if base.islower() else H                # marks sit the same gap over the x-height or the caps
        bw = P["B"] if base != "ı" else S * 3.5         # the macron over the i stays narrow
        up = lambda pts: [(x + dx, y + top + gap) for x, y in pts]
        g[ch] = (w, shapes + [up(p) for p in ACCENTS[acc](S, bw)],
                 holes + [up(p) for p in ACCENT_HOLES.get(acc, lambda *_: [])(S, bw)])
    for ch, base in (("Ç", "C"), ("ç", "c")):
        cx = g[base][0] * .5
        g[ch] = (g[base][0], g[base][1] + [rect(cx - S * .45, -S * .55, cx + S * .45, 0),
                 [(x, y - S * 1.25) for x, y in _acc_band(cx - S * 1.15, S * .7, S * .9)]], [])

    names = {ch: ("uni%04X" % ord(ch)) for ch in g}
    order = [".notdef", "space"] + [names[ch] for ch in g]
    pen_glyphs, metrics, cmap = {}, {}, {32: "space", 0xA0: "space"}

    def draw(shapes, holes):
        pen = TTGlyphPen(None)
        for pts, outer in [(s, True) for s in shapes] + [(h, False) for h in holes]:
            pts = snap(pts)
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
        if ch.isdigit():                                # figures: plain, slightly open bearings (no optical tightening)
            lsb = rsb = SB * 1.15
        shifted = lambda pts: [(x - x0 + lsb, y) for x, y in pts]
        pen_glyphs[n] = draw([shifted(s) for s in shapes], [shifted(h) for h in holes])
        metrics[n] = (round(lsb + (x1 - x0) + rsb), round(lsb))
        cmap[ord(ch)] = n

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
                sCapHeight=H, sxHeight=X, usWeightClass=900, achVendID="SHGO",
                fsSelection=0x20)
    fb.setupPost()
    # one clean outline per glyph: overlapping strokes (bowl and leg, stem and arms, the X's
    # crossing) are merged, so joins and cuts render as single crisp edges
    from fontTools.ttLib.removeOverlaps import removeOverlaps
    removeOverlaps(fb.font)
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
