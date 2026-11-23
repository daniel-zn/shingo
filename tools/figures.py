"""Shingo Grid figures: one system for all ten digits.

Every figure is built on the same skeleton and the same rules, so they read as a set:

- one width W for every figure (the 1 included: it fills its cell, as on the reference), the cap
  height H, the stroke S;
- one middle bar for every figure that has one (2 3 4 5 6 8 9), on the capitals' crossbar line;
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


def _union(polys):
    """Union of polygons, whatever way each one winds: every piece is resolved on its own
    (non-zero fill) before it is added, so overlaps never cancel into holes."""
    acc = None
    for pts in polys:
        p = pathops.simplify(_path([pts]))
        acc = p if acc is None else pathops.op(acc, p, pathops.PathOp.UNION)
    return acc


def _shape(add, cut=(), fill=()):
    """union(add + fill) minus cut → (outers, holes)."""
    base = _union(list(add) + list(fill))
    if cut:
        base = pathops.op(base, _union(cut), pathops.PathOp.DIFFERENCE)
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


def build(S, C, B, H, band, clip, stroke):
    """Figures 0–9 for Shingo Grid. Returns {ch: (advance, outers, holes)}.

    Verticals carry the full stroke S; horizontals are a shade lighter (.9 S) so the counters of the
    three-bar figures stay open at small sizes. Every value is a whole font unit.
    """
    Sv, Sh = S, round(S * .9)                       # vertical and horizontal strokes
    W = round(B * .9)                               # one body width for 0 2–9
    T = round(Sv * R2)                              # level width of a 45° stroke
    Mf = H // 2                                     # the middle bar: on the capitals' crossbar line
    mb = Mf - Sh // 2
    mt = mb + Sh
    xr = W - Sv
    # weight-keeping: outer cut − inner cut = (Sv + Sh)(1 − 1/√2)
    k = round((Sv + Sh) * (1 - 1 / R2))
    room = (H - Sh - mt) - round(Sv * .22)          # upper counter height, less a short flat
    c = round(room * .69)                           # inner cut at a box corner
    cm = room - c                                   # inner cut at a middle turn
    C, Cm = c + k, cm + k                           # their outer cuts
    top, bot = rect(0, H - Sh, W, H), rect(0, 0, W, Sh)
    left, right = rect(0, 0, Sv, H), rect(xr, 0, W, H)
    mid = rect(0, mb, W, mt)
    box_cuts = [corner(0, H, 1, -1, C), corner(W, H, -1, -1, C), corner(W, 0, -1, 1, C), corner(0, 0, 1, 1, C)]
    box_fills = [corner(Sv, H - Sh, 1, -1, c), corner(xr, H - Sh, -1, -1, c), corner(xr, Sh, -1, 1, c), corner(Sv, Sh, 1, 1, c)]
    n = round(Sh * .5)                              # depth of the waist notch (8, 3)
    notch_l = [(0, Mf + n), (n, Mf), (0, Mf - n)]
    notch_r = [(W, Mf + n), (W - n, Mf), (W, Mf - n)]
    g = {}

    def put(ch, add, cut=(), fill=(), w=W):
        outers, holes = _shape(add, cut, fill)
        g[ch] = (w, outers, holes)

    # 0: the cut box with a lighter slash (.7 S) through the centre; it lands on the bars, so the
    # counter's corners stay open
    t0 = 2 * round(Sv * .7 * R2 / 2)               # even, so its edges cross the cuts on whole units
    x0 = round(W / 2 - t0 / 2 - (H / 2 - Sh))
    if (Sv + Sh + c - Sh + x0) % 2:
        x0 += 1
    sl = clip(band(x0, Sh, H - Sh, t0), Sv, xr, Sh, H - Sh)
    put("0", [top, bot, left, right, sl], cut=box_cuts, fill=box_fills)

    # 1: as on the reference, it fills the figure cell: the stem on the centre line, a flag whose end
    # is cut down to half the bar, a foot across the cell, so 1284 and 11:11 keep the figures' rhythm
    x1 = (W - Sv) // 2
    fl = round(W * .12)
    put("1", [rect(fl, H - Sh, x1 + Sv, H), rect(x1, 0, x1 + Sv, H), rect(round(W * .1), 0, round(W * .9), Sh)],
        cut=[corner(fl, H, 1, -1, Sh // 2)])

    # 2: top, right upper, middle, left lower, foot; the top-right and both middle turns are cut
    put("2", [top, rect(xr, mb, W, H), mid, rect(0, 0, Sv, mt), bot],
        cut=[corner(W, H, -1, -1, C), corner(W, mb, -1, 1, Cm), corner(0, mt, 1, -1, Cm)],
        fill=[corner(xr, H - Sh, -1, -1, c), corner(xr, mt, -1, 1, cm), corner(Sv, mb, 1, -1, cm)])

    # 3: top, full right, a middle arm from a third of the way in, foot; the 8's waist notch on the right
    put("3", [top, right, rect(round(W * .34), mb, W, mt), bot],
        cut=[corner(W, H, -1, -1, C), corner(W, 0, -1, 1, C), notch_r],
        fill=[corner(xr, H - Sh, -1, -1, c), corner(xr, Sh, -1, 1, c), corner(xr, mt, -1, 1, cm), corner(xr, mb, -1, -1, cm)])

    # 4: open, as on the reference: a left stroke down to the bar, the bar, a full stem flush right
    put("4", [rect(0, mb, Sv, H), mid, right], cut=[corner(0, mb, 1, 1, Cm)], fill=[corner(Sv, mt, 1, 1, cm)])

    # 5: top, left upper, middle, right lower, foot; cut at the middle turn and the bottom right
    put("5", [top, rect(0, mb, Sv, H), mid, rect(xr, 0, W, mt), bot],
        cut=[corner(W, mt, -1, -1, Cm), corner(W, 0, -1, 1, C)],
        fill=[corner(xr, mb, -1, -1, cm), corner(xr, Sh, -1, 1, c)])

    # 6: the top arm stops at two thirds, so the 6 never reads as 8; full left, bowl below
    put("6", [rect(0, H - Sh, round(W * .68), H), left, mid, rect(xr, 0, W, mt), bot],
        cut=[corner(0, H, 1, -1, C), corner(0, 0, 1, 1, C), corner(W, 0, -1, 1, C), corner(W, mt, -1, -1, Cm)],
        fill=[corner(Sv, H - Sh, 1, -1, c), corner(Sv, Sh, 1, 1, c), corner(xr, Sh, -1, 1, c), corner(xr, mb, -1, -1, cm)])
    # 9: drawn on the shared middle bar (not the 6 turned, which would drop its bar below the others):
    # bowl above, full right, the foot arm stops at two thirds
    put("9", [top, rect(0, mb, Sv, H), mid, right, rect(W - round(W * .68), 0, W, Sh)],
        cut=[corner(0, H, 1, -1, C), corner(W, H, -1, -1, C), corner(W, 0, -1, 1, C), corner(0, mb, 1, 1, Cm)],
        fill=[corner(Sv, H - Sh, 1, -1, c), corner(xr, H - Sh, -1, -1, c), corner(xr, Sh, -1, 1, c), corner(Sv, mt, 1, 1, cm)])

    # 7: bent, as on the reference: the top bar turns down the right side, breaks at 45° and lands on
    # a short upright foot left of centre
    # a middle-turn cut at the corner, so the drop shows before the break and the inside turns at 135°
    xf = W // 2                                    # the foot sits on the centre line
    yf = round(H * .17)                             # the foot's height
    yk = yf + (W - Sv // 2 - xf)                    # where the right side breaks into the diagonal
    leg = stroke([(W - Sv / 2, H - Sh / 2), (W - Sv / 2, yk), (xf, yf), (xf, 0)], Sv)
    put("7", [top, leg], cut=[corner(W, H, -1, -1, Cm)], fill=[corner(xr, H - Sh, -1, -1, cm)])

    # 8: two bowls on one middle bar, every corner cut, the waist notched on both sides
    put("8", [top, bot, left, right, mid],
        cut=box_cuts + [notch_l, notch_r],
        fill=box_fills + [corner(Sv, mt, 1, 1, cm), corner(xr, mt, -1, 1, cm), corner(Sv, mb, 1, -1, cm), corner(xr, mb, -1, -1, cm)])
    return g
