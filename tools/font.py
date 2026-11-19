"""Shingō Grid: the system's own display face.

    python3 tools/font.py

Wide, short and hard, after the RADAR poster. Every stroke has one heavy weight,
every glyph is drawn from level, upright and 45° edges on a grid, and wherever a
letter would normally curve it is cut at 45°. One cut, Heavy, for display,
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
    # stroke, outer cut, body width, side bearing, space. One heavy cut, after the RADAR reference:
    # strokes about a quarter of the cap height, letters wider than they are tall.
    "Heavy": dict(S=172, C=172, B=800, SB=52, SP=300),
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
    return g


ACCENTS = {  # name: shapes over the cap height, centred on 0
    "acute": lambda S, B: [[(-S * .3, 0), (S * .5, 0), (S * 1.1, S * .9), (S * .3, S * .9)]],
    "grave": lambda S, B: [[(S * .3, 0), (-S * .5, 0), (-S * 1.1, S * .9), (-S * .3, S * .9)]],
    "circ": lambda S, B: [[(-S * 1.6, 0), (-S * .8, 0), (0, S * .55), (S * .8, 0), (S * 1.6, 0), (S * .4, S), (-S * .4, S)]],
    "uml": lambda S, B: [rect(-S * 1.6, 0, -S * .6, S * .8), rect(S * .6, 0, S * 1.6, S * .8)],
    "macron": lambda S, B: [crect(-B * .3, 0, B * .3, S * .6, tl=S * .4)],
    "tilde": lambda S, B: [[(-S * 1.6, 0), (-S * .9, 0), (-S * .9, S * .3), (S * .9, S * .3), (S * .9, S * .9), (S * 1.6, S * .9),
                            (S * 1.6, S * .6), (S * .9 + S * .7 - S * .7, S * .6), (-S * .9, S * .6), (-S * 1.6, S * .6)]],
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
        shifted = lambda pts: [(x + SB, y) for x, y in pts]
        pen_glyphs[n] = draw([shifted(s) for s in shapes], [shifted(h) for h in holes])
        metrics[n] = (round(w + 2 * SB), SB)
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
