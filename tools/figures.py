"""Shingo Grid figures: one system for all ten digits.

Every figure is built on the same skeleton and the same rules, so they read as a set:

- one width W for 0 2–9 (the 1 is narrower), the cap height H, the stroke S;
- one middle bar for every figure that has one (2 3 4 5 6 8 9), set a little above centre so
  upper bowls are a touch smaller than lower ones;
- strokes are unions of level and upright bars (plus the 45° diagonals of 7 and the zero's slash);
- a stroke that turns gets a 45° cut on its outer corner and the matching inner cut on its inner
  corner, so it never thins: big cuts (C / c) at the box corners, capped cuts (S / cm) at the
  middle turns, where a big cut would run past the bar;
- stroke ends are square.

Shapes are combined with skia-pathops (union, then the cuts are subtracted and the inner fills
added) and returned as (advance, outer contours, holes) for tools/font.py.
"""
import math

import pathops

R2 = math.sqrt(2)


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


def _area(pts):
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1])) / 2


def _shape(add, cut=(), fill=()):
    """union(add + fill) minus cut → (outers, holes)."""
    base = _path(list(add) + list(fill))
    base = pathops.simplify(base) if hasattr(pathops, "simplify") else base
    if cut:
        base = pathops.op(base, _path(list(cut)), pathops.PathOp.DIFFERENCE)
    base = pathops.simplify(base)
    cs = [[(round(x, 3), round(y, 3)) for x, y in c] for c in _contours(base)]
    cs = [c for c in cs if abs(_area(c)) > 1]
    if not cs:
        return [], []
    big = max(cs, key=lambda c: abs(_area(c)))
    sign = _area(big) > 0
    return [c for c in cs if (_area(c) > 0) == sign], [c for c in cs if (_area(c) > 0) != sign]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def corner(x, y, sx, sy, a):
    """Triangle at corner (x, y) with legs of length a running in directions sx, sy (±1)."""
    return [(x, y), (x + sx * a, y), (x, y + sy * a)]


def build(S, C, B, H, band, clip):
    W = round(B * .84)
    T = S * R2                      # level width of a 45° stroke
    Mf = H * .5                     # the middle bar's centre: both bowls get the same counter height
    mb, mt = Mf - S / 2, Mf + S / 2
    # Cut sizes come from the counters. A bowl's side can carry two inner cuts (a corner cut and a
    # middle-turn cut); together they must leave a short flat, or they cross and leave a speck. The
    # outer cuts follow from the inner ones (outer = inner + S(2 - √2)), so strokes never thin.
    k = S * (2 - R2)
    room = (H - S - mt) - S * .22                   # one counter's height, less the flat between two cuts
    c0, cm0 = C - k, S * (R2 - 1)                   # the letters' cuts
    f = min(1.0, room / (c0 + cm0))
    c, cm = c0 * f, cm0 * f                         # inner cuts for figures
    C, Cm = c + k, cm + k                           # outer cuts for figures
    xr = W - S
    top, bot = rect(0, H - S, W, H), rect(0, 0, W, S)
    left, right = rect(0, 0, S, H), rect(xr, 0, W, H)
    mid = rect(0, mb, W, mt)
    g = {}

    def put(ch, add, cut=(), fill=(), w=W):
        outers, holes = _shape(add, cut, fill)
        g[ch] = (w, outers, holes)

    # 0: the box, cut at all four corners, with the slash at full weight inside the counter
    sl = clip(band((W - T - (H - 2 * S)) / 2, S, H - S, T), S - 1, W - S + 1, S - 1, H - S + 1)
    put("0", [top, bot, left, right, sl],
        cut=[corner(0, H, 1, -1, C), corner(W, H, -1, -1, C), corner(W, 0, -1, 1, C), corner(0, 0, 1, 1, C)],
        fill=[corner(S, H - S, 1, -1, c), corner(xr, H - S, -1, -1, c), corner(xr, S, -1, 1, c), corner(S, S, 1, 1, c)])

    # 1: a stem, a flag with a cut on its upper end, a foot (spaced by its ink, so narrower than W)
    x1 = S * 1.3
    put("1", [rect(x1 - S * 1.3, H - S, x1 + S, H), rect(x1 - S * 1.2, 0, x1 + S * 2.2, S), rect(x1, 0, x1 + S, H)],
        cut=[corner(x1 - S * 1.3, H, 1, -1, S * .9)], w=round(S * 3.4))

    # 2: top, right upper, middle, left lower, foot; turns cut at top-right and both middle turns
    put("2", [top, rect(xr, mb, W, H), mid, rect(0, 0, S, mt), bot],
        cut=[corner(W, H, -1, -1, C), corner(W, mb, -1, 1, Cm), corner(0, mt, 1, -1, Cm)],
        fill=[corner(xr, H - S, -1, -1, c), corner(xr, mt, -1, 1, cm), corner(S, mb, 1, -1, cm)])

    # 3: top, full right, a middle arm that stops short, foot; cut at the two right corners
    put("3", [top, right, rect(W * .36, mb, W, mt), bot],
        cut=[corner(W, H, -1, -1, C), corner(W, 0, -1, 1, C)],
        fill=[corner(xr, H - S, -1, -1, c), corner(xr, S, -1, 1, c)])

    # 4: open: left upper stroke down to the middle bar, the bar runs past a full stem; the turn is cut
    sr = W - S * .45
    put("4", [rect(0, mb, S, H), rect(0, mb, W, mt), rect(sr - S, 0, sr, H)],
        cut=[corner(0, mb, 1, 1, Cm)], fill=[corner(S, mt, 1, 1, cm)])

    # 5: top, left upper, middle, right lower, foot; cut at the middle turn and the bottom-right
    put("5", [top, rect(0, mb, S, H), mid, rect(xr, 0, W, mt), bot],
        cut=[corner(W, mt, -1, -1, Cm), corner(W, 0, -1, 1, C)],
        fill=[corner(xr, mb, -1, -1, cm), corner(xr, S, -1, 1, c)])

    # 6: top, full left, middle, right lower, foot: a bowl below; 9 is the 6 turned
    six = dict(add=[top, left, mid, rect(xr, 0, W, mt), bot],
               cut=[corner(0, H, 1, -1, C), corner(0, 0, 1, 1, C), corner(W, 0, -1, 1, C), corner(W, mt, -1, -1, Cm)],
               fill=[corner(S, H - S, 1, -1, c), corner(S, S, 1, 1, c), corner(xr, S, -1, 1, c), corner(xr, mb, -1, -1, cm)])
    put("6", **six)
    turn = lambda polys: [[(W - x, H - y) for x, y in pts] for pts in polys]
    put("9", turn(six["add"]), turn(six["cut"]), turn(six["fill"]))

    # 7: top bar into a 45° stroke to the baseline; the turn is cut
    d7 = H - S
    x7 = W - T - d7
    put("7", [top, band(x7, 0, H - S + 1, T)], cut=[corner(W, H, -1, -1, C * .8)])

    # 8: two bowls on one middle bar, all four corners cut, the waist notched on both sides
    n8 = S * .5
    put("8", [top, bot, left, right, mid],
        cut=[corner(0, H, 1, -1, C), corner(W, H, -1, -1, C), corner(W, 0, -1, 1, C), corner(0, 0, 1, 1, C),
             [(0, Mf + n8), (n8, Mf), (0, Mf - n8)], [(W, Mf + n8), (W - n8, Mf), (W, Mf - n8)]],
        fill=[corner(S, H - S, 1, -1, c), corner(xr, H - S, -1, -1, c), corner(xr, S, -1, 1, c), corner(S, S, 1, 1, c),
              corner(S, mt, 1, 1, cm), corner(xr, mt, -1, 1, cm), corner(S, mb, 1, -1, cm), corner(xr, mb, -1, -1, cm)])
    return g
