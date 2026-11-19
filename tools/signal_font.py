"""Shingo Signal: Orbitron, completed for this system.

    python3 tools/signal_font.py            (reads tools/vendor/Orbitron[wght].ttf)

Orbitron (SIL OFL 1.1, Reserved Font Name "Orbitron") sets subheads, inline
wordmarks and labels. It lacks characters the system prints, so this cuts two
static weights from the variable font, adds the missing glyphs drawn from its
own strokes, and renames the result (the OFL requires a modified version to
drop the reserved name).

Added: macron vowels (Ā Ē Ī Ō Ū and lowercase), middle dot ·, ordinals º ª,
numero №, guillemets « », arrows ← ↑ → ↓, diamond ◆, primes ′ ″, ² ³, ™ ×.

Writes ios/Sources/ShingoKit/Resources/Fonts/ShingoSignal-{SemiBold,ExtraBold}.ttf
and web/fonts/ShingoSignal-{SemiBold,ExtraBold}.woff2.
"""
import pathlib
import sys

from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = pathlib.Path(__file__).resolve().parent.parent
WEIGHTS = {"SemiBold": 600, "ExtraBold": 800}


def bounds(gs, name):
    p = BoundsPen(gs)
    gs[name].draw(p)
    return p.bounds or (0, 0, 0, 0)


def complete(font):
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    glyf, hmtx = font["glyf"], font["hmtx"]
    order = font.getGlyphOrder()
    cap = bounds(gs, cmap[ord("H")])[3]
    xh = bounds(gs, cmap[ord("x")])[3]
    # stroke weight, measured from the stem of I
    ib = bounds(gs, cmap[ord("I")])
    stroke = ib[2] - ib[0]

    def add(uni, name, draw, adv):
        pen = TTGlyphPen(gs)
        draw(pen)
        glyf[name] = pen.glyph()
        hmtx[name] = (round(adv), 0)
        if name not in order:
            order.append(name)
        for t in font["cmap"].tables:
            if t.isUnicode():
                t.cmap[uni] = name

    def place(src, sx=1, sy=1, dx=0, dy=0):
        return lambda pen: gs[src].draw(TransformPen(pen, (sx, 0, 0, sy, dx, dy)))

    def both(*fs):
        return lambda pen: [f(pen) for f in fs]

    def poly(pts):
        def d(pen):
            pen.moveTo(pts[0])
            for p in pts[1:]:
                pen.lineTo(p)
            pen.closePath()
        return d

    def rnd(pts):
        return [(round(x), round(y)) for x, y in pts]

    mac = cmap[0xAF]
    mb = bounds(gs, mac)
    for base, uni in [("A", 0x100), ("E", 0x112), ("I", 0x12A), ("O", 0x14C), ("U", 0x16A),
                      ("a", 0x101), ("e", 0x113), ("i", 0x12B), ("o", 0x14D), ("u", 0x16B)]:
        g = cmap[ord(base)]
        bb = bounds(gs, g)
        adv = hmtx[g][0]
        top = (cap if base.isupper() else xh) + stroke * .6
        dx = (bb[0] + bb[2]) / 2 - (mb[0] + mb[2]) / 2
        dy = top - mb[1]
        if base in "iI":
            # dotless base for i
            src = cmap.get(0x131, g) if base == "i" else g
            add(uni, f"uni{uni:04X}", both(place(src), place(mac, dx=dx, dy=dy)), adv)
        else:
            add(uni, f"uni{uni:04X}", both(place(g), place(mac, dx=dx, dy=dy)), adv)

    per = cmap[ord(".")]
    pb = bounds(gs, per)
    add(0xB7, "periodcentered", place(per, dy=(cap / 2) - (pb[1] + pb[3]) / 2), hmtx[per][0])

    o, a, hy = cmap[ord("o")], cmap[ord("a")], cmap[ord("-")]
    ob, hb = bounds(gs, o), bounds(gs, hy)
    k = .62
    lift = cap - ob[3] * k
    bar = lambda w0: place(hy, sx=(w0 / max(1, hb[2] - hb[0])), sy=.7, dx=-hb[0] * (w0 / max(1, hb[2] - hb[0])), dy=lift - stroke * 1.3 - hb[1] * .7)
    add(0xBA, "ordmasculine", both(place(o, k, k, 0, lift), bar(ob[2] * k)), hmtx[o][0] * k + 40)
    add(0xAA, "ordfeminine", both(place(a, k, k, 0, lift), bar(bounds(gs, a)[2] * k)), hmtx[a][0] * k + 40)
    N = cmap[ord("N")]
    nw = hmtx[N][0]
    add(0x2116, "numero", both(place(N), place(o, k, k, nw, lift),
                               place(hy, sx=(ob[2] * k) / max(1, hb[2] - hb[0]), sy=.7, dx=nw - hb[0] * (ob[2] * k) / max(1, hb[2] - hb[0]), dy=lift - stroke * 1.3 - hb[1] * .7)),
        nw + hmtx[o][0] * k + 40)

    # guillemets, arrows, diamond: drawn from the stroke weight
    s = stroke
    h = xh * .8
    def chev(x0, left=True):
        w = h * .5
        if left:
            return poly(rnd([(x0 + w, h), (x0 + w + s, h), (x0 + s, h / 2), (x0 + w + s, 0), (x0 + w, 0), (x0, h / 2)]))
        return poly(rnd([(x0, h), (x0 + s, h), (x0 + w + s, h / 2), (x0 + s, 0), (x0, 0), (x0 + w, h / 2)]))
    gw = h * .5 + s
    add(0xAB, "guillemotleft", both(chev(40), chev(40 + gw * .9)), gw * 1.9 + 80)
    add(0xBB, "guillemotright", both(chev(40, False), chev(40 + gw * .9, False)), gw * 1.9 + 80)

    L = cap * 1.25
    hd = cap * .62
    def arrow_r(pen):
        y = cap / 2
        poly(rnd([(60, y - s / 2), (60 + L - hd * .7, y - s / 2), (60 + L - hd * .7, y - hd / 2 - s * .2), (60 + L, y),
                  (60 + L - hd * .7, y + hd / 2 + s * .2), (60 + L - hd * .7, y + s / 2), (60, y + s / 2)]))(pen)
    def mirror_x(draw, w):
        return lambda pen: draw(TransformPen(pen, (-1, 0, 0, 1, w, 0)))
    def rot(draw, cx, cy, up=True):
        # 90° turn about (cx, cy)
        m = (0, 1, -1, 0, cx + cy, cy - cx) if up else (0, -1, 1, 0, cx - cy, cy + cx)
        return lambda pen: draw(TransformPen(pen, m))
    aw = L + 120
    add(0x2192, "arrowright", arrow_r, aw)
    add(0x2190, "arrowleft", mirror_x(arrow_r, aw), aw)
    add(0x2191, "arrowup", rot(arrow_r, aw / 2, cap / 2, True), aw)
    add(0x2193, "arrowdown", rot(arrow_r, aw / 2, cap / 2, False), aw)
    r = cap * .32
    add(0x25C6, "diamond", poly(rnd([(60 + r, cap / 2 + r), (60 + 2 * r, cap / 2), (60 + r, cap / 2 - r), (60, cap / 2)])), 2 * r + 120)

    q = cmap[ord("'")]
    qb = bounds(gs, q)
    add(0x2032, "minute", place(q), hmtx[q][0])
    add(0x2033, "second", both(place(q), place(q, dx=hmtx[q][0] * .7)), hmtx[q][0] * 1.7)
    for d, uni in [("2", 0xB2), ("3", 0xB3)]:
        g = cmap[ord(d)]
        add(uni, f"uni{uni:04X}", place(g, .55, .55, 0, cap * .45), hmtx[g][0] * .55 + 30)
    T, M = cmap[ord("T")], cmap[ord("M")]
    add(0x2122, "trademark", both(place(T, .45, .45, 0, cap * .55), place(M, .45, .45, hmtx[T][0] * .45, cap * .55)),
        (hmtx[T][0] + hmtx[M][0]) * .45 + 40)
    font.setGlyphOrder(order)
    font["maxp"].numGlyphs = len(order)


def rename(font, style, weight):
    fam = "Shingo Signal"
    n = font["name"]
    for rec in list(n.names):
        if rec.nameID in (1, 2, 3, 4, 6, 16, 17, 21, 22, 25):
            n.removeNames(nameID=rec.nameID)
    for nid, val in [(1, f"{fam} {style}"), (2, "Regular"), (3, f"ShingoSignal-{style}"), (4, f"{fam} {style}"),
                     (6, f"ShingoSignal-{style}"), (16, fam), (17, style)]:
        n.setName(val, nid, 3, 1, 0x409)
    old = n.getDebugName(0) or ""
    n.setName(old + " Shingo Signal is a modified version of Orbitron, with added glyphs.", 0, 3, 1, 0x409)
    font["OS/2"].usWeightClass = weight
    font["OS/2"].achVendID = "SHGO"
    if "STAT" in font:
        del font["STAT"]


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "tools" / "vendor" / "Orbitron[wght].ttf")
    ios = ROOT / "ios" / "Sources" / "ShingoKit" / "Resources" / "Fonts"
    web = ROOT / "web" / "fonts"
    web.mkdir(parents=True, exist_ok=True)
    for style, w in WEIGHTS.items():
        f = instancer.instantiateVariableFont(TTFont(src), {"wght": w})
        complete(f)
        rename(f, style, w)
        f.save(ios / f"ShingoSignal-{style}.ttf")
        f.flavor = "woff2"
        f.save(web / f"ShingoSignal-{style}.woff2")
        print(f"ShingoSignal-{style}: {len(f.getGlyphOrder())} glyphs")


if __name__ == "__main__":
    main()
