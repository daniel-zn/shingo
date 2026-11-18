#!/usr/bin/env python3
"""Build Shingō 信号.

  python3 tools/build.py

1. Generates the glyph sprite (X marks, diamond mark, rings, topo badge, ...)
2. Exports every glyph as a standalone SVG to assets/svg/  (drop into Xcode
   asset catalogs, "Preserve Vector Data", render as template where mono)
3. Generates the poster study SVG from the same primitives
4. Inlines web/shingo.css + sprite + posters into web/gallery.src.html
   -> dist/index.html (one self-contained file)
"""
import json, math, pathlib, re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Colours are CSS variables so the same SVG renders in light and dark mode
# (the page resolves them). Exports resolve them to literal hex per mode.
C = dict(ink="var(--ink)", sage="var(--sage)", hi="var(--sage-hi)", lo="var(--sage-lo)",
         line="var(--sage-line)", ghost="var(--sage-ghost)", coral="var(--coral)",
         oninc="var(--on-ground)", ghi="var(--ground-hi)", ground="var(--ground)", ground2="var(--ground-2)")
PALETTE = {
    "dark":  {"ground": "#0b0b0a", "ground-2": "#1b1c18", "ground-3": "#2e2f2a", "on-ground": "#c9ccc2", "ground-hi": "#dcdfd5", "ground-dim": "#8b8d85",
              "sage": "#dcdfd5", "sage-hi": "#dcdfd5", "sage-lo": "#8b8d85", "sage-line": "#8b8d85", "sage-ghost": "#c9ccc2",
              "ink": "#0b0b0a", "ink-dim": "#55574f", "coral": "#ff715e", "coral-deep": "#e65b48", "signal-text": "#ff715e"},
    "light": {"ground": "#bcbfb4", "ground-2": "#b0b3a8", "ground-3": "#9fa297", "on-ground": "#1c1d19", "ground-hi": "#0f100d", "ground-dim": "#4d4f47",
              "sage": "#0f100d", "sage-hi": "#0f100d", "sage-lo": "#4d4f47", "sage-line": "#4d4f47", "sage-ghost": "#2e2f2a",
              "ink": "#bcbfb4", "ink-dim": "#8e9187", "coral": "#ff715e", "coral-deep": "#e65b48", "signal-text": "#8f2b1c"},
}
ROLES = {"ground": "striped background", "ground-2": "stripe highlight", "ground-3": "rules, frames, tracks",
         "on-ground": "body text on the ground", "ground-hi": "the print: titles, line art, plates of text", "ground-dim": "secondary print",
         "sage": "solid print plates", "sage-hi": "plates you press or carry (= print)", "sage-lo": "perforations, pressed plates", "sage-line": "hairlines on plates",
         "sage-ghost": "faint marks on plates", "ink": "text knocked out of plates (= ground)", "ink-dim": "secondary text on plates",
         "coral": "the signal", "coral-deep": "pressed signal", "signal-text": "coral as text (deep coral on sage)"}


def resolve(svg, mode):
    """Replace var(--x) with the literal colour for one mode (for standalone files)."""
    fonts = {"f-display": "Anybody, sans-serif", "f-title": "Anybody, sans-serif", "f-cap": "Anybody, sans-serif", "f-sans": "Anybody, sans-serif",
             "f-mono": "'IBM Plex Mono', monospace", "f-jp": "'BIZ UDGothic', 'Hiragino Sans', sans-serif", "f-stencil": "'Saira Stencil One', sans-serif"}
    return re.sub(r"var\(--([a-z0-9-]+)\)", lambda m: PALETTE[mode].get(m.group(1)) or fonts[m.group(1)], svg)


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- geometry
def x_sharp(h=12.5, L=33.0, c=50.0):
    """Industrial X: two crossed bars with square-cut ends (no rounding)."""
    r2 = math.sqrt(0.5); s_ = h * math.sqrt(2)
    d = (r2, -r2); n = (r2, r2)
    a1 = (L * d[0] - h * n[0], L * d[1] - h * n[1]); a2 = (L * d[0] + h * n[0], L * d[1] + h * n[1])
    def rot(p, k):
        x, y = p
        for _ in range(k): x, y = -y, x
        return x, y
    pts = []
    for k in range(4):
        for q in ((0, -s_), a1, a2):
            x, y = rot(q, k); pts.append(f"{f(c + x)} {f(c + y)}")
    return "M" + " L".join(pts) + " Z"


def octagon(cx, cy, r):
    return " ".join(f"{f(cx + r * math.cos(math.radians(22.5 + 45 * k)))},{f(cy + r * math.sin(math.radians(22.5 + 45 * k)))}" for k in range(8))


# ---------------------------------------------------------------- seven-segment
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
       "7": "abc", "8": "abcdefg", "9": "abcdfg", "-": "g", " ": "", "E": "afged", "r": "eg", "o": "cdeg", "P": "abefg", "A": "abcefg"}


def _segs(w=44, h=60, t=5.6, g=1.3):
    def hseg(x0, x1, yc):
        return [(x0, yc), (x0 + t / 2, yc - t / 2), (x1 - t / 2, yc - t / 2), (x1, yc), (x1 - t / 2, yc + t / 2), (x0 + t / 2, yc + t / 2)]
    def vseg(xc, y0, y1):
        return [(xc, y0), (xc + t / 2, y0 + t / 2), (xc + t / 2, y1 - t / 2), (xc, y1), (xc - t / 2, y1 - t / 2), (xc - t / 2, y0 + t / 2)]
    x0, x1, m = t / 2 + g, w - t / 2 - g, h / 2
    return {"a": hseg(x0, x1, t / 2), "g": hseg(x0, x1, m), "d": hseg(x0, x1, h - t / 2),
            "f": vseg(t / 2, t / 2 + g, m - g), "b": vseg(w - t / 2, t / 2 + g, m - g),
            "e": vseg(t / 2, m + g, h - t / 2 - g), "c": vseg(w - t / 2, m + g, h - t / 2 - g)}


def seg7(text, height=48, hot="", ghost=False, cls=""):
    """Inline SVG seven-segment readout. Characters in `hot` (indexes) light coral.
    Unlit segments draw in --off unless ghost=False. Supports 0-9 - . : and a few letters."""
    w, h, gap = 44, 60, 9
    S = _segs()
    parts, x = [], 0
    for i, ch in enumerate(text):
        state = "hot" if str(i) in hot.split(",") else "on"
        if ch == ".":
            parts.append(f'<rect class="{state}" x="{x}" y="{h-7}" width="7" height="7"/>'); x += 7 + gap; continue
        if ch == ":":
            parts.append(f'<rect class="{state}" x="{x}" y="{h*0.28:.1f}" width="7" height="7"/><rect class="{state}" x="{x}" y="{h*0.64:.1f}" width="7" height="7"/>'); x += 7 + gap; continue
        lit = SEG.get(ch, "")
        for k, pts in S.items():
            if k in lit or ghost:
                c = state if k in lit else "off"
                parts.append(f'<polygon class="{c}" points="{" ".join(f"{f(px + x)},{f(py)}" for px, py in pts)}"/>')
        x += w + gap
    W = x - gap + 4
    return (f'<svg class="seg7 {cls}" data-hot="{hot}" viewBox="0 0 {W} {h}" height="{height}" width="{f(height * W / h)}" role="img" aria-label="{text}">'
            f'<g transform="translate(2 0)">{"".join(parts)}</g></svg>')


def _matrix(n=21, seed=7):
    import random
    rnd = random.Random(seed)
    cells = []
    def finder(x0, y0):
        for y in range(7):
            for x in range(7):
                if x in (0, 6) or y in (0, 6) or (2 <= x <= 4 and 2 <= y <= 4):
                    cells.append((x0 + x, y0 + y))
    for fx, fy in ((0, 0), (n - 7, 0), (0, n - 7)):
        finder(fx, fy)
    reserved = lambda x, y: (x < 8 and y < 8) or (x >= n - 8 and y < 8) or (x < 8 and y >= n - 8)
    for y in range(n):
        for x in range(n):
            if not reserved(x, y) and rnd.random() < 0.48:
                cells.append((x, y))
    return "".join(f'<rect x="{x}" y="{y}" width="1" height="1"/>' for x, y in cells)


XS = x_sharp(9.5, 34)   # sharp X: the interface (slim arms)

# ---------------------------------------------------------------- glyphs
# id -> (viewBox, inner svg). Mono glyphs use currentColor.
G = {}
G["x-line"] = ("0 0 100 100", f'<path d="{XS}" fill="none" stroke="currentColor" stroke-width="6.5" stroke-linejoin="miter"/>')
G["x-solid"] = ("0 0 100 100", f'<path d="{XS}" fill="currentColor"/>')
G["mark"] = ("0 0 100 100", '<g transform="rotate(45 50 50)"><path fill-rule="evenodd" fill="currentColor" d="M20 20H80V80H20Z M38 42H58V62H38Z"/></g>')
G["reticle"] = ("0 0 100 100", '<path d="M8 32V8H32 M68 8H92V32 M92 68V92H68 M32 92H8V68" fill="none" stroke="currentColor" stroke-width="7"/><path d="M50 34V66M34 50H66" stroke="currentColor" stroke-width="6"/>')
G["grid"] = ("0 0 100 100", '<path d="M10 10H90V90H10Z M36.7 10V90 M63.3 10V90 M10 36.7H90 M10 63.3H90" fill="none" stroke="currentColor" stroke-width="6"/>')
G["signal"] = ("0 0 100 100", '<g fill="currentColor"><path d="M8 70H24V92H8Z"/><path d="M32 52H48V92H32Z"/><path d="M56 32H72V92H56Z"/><path d="M80 10H96V92H80Z"/></g>')
_scope = [f'<polygon points="{octagon(100, 100, r)}" fill="none" stroke="currentColor" stroke-width="1.5" opacity=".55"/>' for r in (92, 70, 48, 26)]
_scope.append('<path d="M100 4V196 M4 100H196" stroke="currentColor" stroke-width="1" opacity=".4"/>')
_scope.append('<polygon points="100,100 178,52 190,84" fill="var(--coral)" opacity=".5"/>')
G["scope"] = ("0 0 200 200", "".join(_scope))
_spec = []
for i in range(40):
    hgt = 10 + 62 * abs(math.sin(i * 0.53) * math.cos(i * 0.21 + 1.1))
    _spec.append(f'<rect x="{i*6}" y="{f(80-hgt)}" width="3.5" height="{f(hgt)}" fill="currentColor"/>')
G["spectrum"] = ("0 0 240 80", "".join(_spec))
G["plus"] = ("0 0 100 100", '<path d="M50 6V94M6 50H94" stroke="currentColor" stroke-width="7"/>')
G["arrow"] = ("0 0 100 100", '<path d="M18 82 L62 38" stroke="currentColor" stroke-width="14"/><path d="M36 18H82V64Z" fill="currentColor"/>')
G["bars"] = ("0 0 100 100", '<g fill="currentColor"><rect x="12" y="20" width="76" height="8"/><rect x="12" y="46" width="52" height="8"/><rect x="12" y="72" width="64" height="8"/></g>')
G["play"] = ("0 0 100 100", '<path d="M28 16 L86 50 L28 84Z" fill="currentColor"/>')
G["skip"] = ("0 0 100 100", '<path d="M18 22 L58 50 L18 78Z M50 22 L90 50 L50 78Z" fill="currentColor"/>')
G["chev"] = ("0 0 100 100", '<path d="M36 18 L68 50 L36 82" fill="none" stroke="currentColor" stroke-width="11"/>')
# --- motifs from the trilingual print reference ---
_chev = []
for _ay, _d1 in zip([18, 82, 146, 210], [70, 150, 40, 112]):
    _chev.append(f'<path d="M-30 {_ay+180} L150 {_ay} L330 {_ay+180}" fill="none" stroke="currentColor" stroke-width="26" stroke-linejoin="miter" stroke-dasharray="{_d1} 16 9999"/>')
_chev.append('<path d="M0 0 H62 L0 62Z" fill="currentColor"/><path d="M300 0 V44 L256 0Z" fill="currentColor"/>')
G["chevrons"] = ("0 0 300 230", "".join(_chev))
G["warn"] = ("0 0 100 100", '<path fill-rule="evenodd" fill="currentColor" d="M50 6 L96 90 H4 Z M44 34 H56 V64 H44 Z M44 70 H56 V80 H44 Z"/>')
G["reg"] = ("0 0 100 100", '<path d="M50 4V96 M4 50H96" stroke="currentColor" stroke-width="4"/><path d="M26 26H74V74H26Z" fill="none" stroke="currentColor" stroke-width="4"/><path d="M40 40H60V60H40Z" fill="currentColor"/>')
G["matrix"] = ("0 0 21 21", f'<g fill="currentColor">{_matrix()}</g>')
G["wave"] = ("0 0 240 60", '<polyline fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="miter" points="0,30 20,30 26,8 34,52 42,8 50,52 56,30 90,30 96,18 102,42 108,30 140,30 146,4 154,56 162,4 170,56 176,30 210,30 216,22 222,38 228,30 240,30"/>')
# --- interface icons: one family. 24-unit grid, 2-unit stroke, square caps, miter joins,
#     45° only, built from the system's shapes (diamond, bars, brackets, cut plates, "/").
_I = {
    "i-home": '<path d="M12 3 L21 12 L12 21 L3 12 Z"/><path d="M10.5 10.5H13.5V13.5H10.5Z" fill="currentColor" stroke="none"/>',
    "i-stats": '<path d="M5 20V15 M10 20V11 M15 20V7 M20 20V3"/>',
    "i-scan": '<path d="M3 8V3H8 M16 3H21V8 M21 16V21H16 M8 21H3V16 M12 9V15 M9 12H15"/>',
    "i-grid": '<path d="M3 3H21V21H3Z M9 3V21 M15 3V21 M3 9H21 M3 15H21"/>',
    "i-me": '<path d="M7 3H21V17L17 21H3V7Z M7 15H17 M7 18H13"/><path d="M12 6L15 9L12 12L9 9Z" fill="currentColor" stroke="none"/>',
    "i-send": '<path d="M4 20L19 5 M10 5H19V14"/>',
    "i-spam": '<path d="M5 5L19 19 M19 5L5 19"/>',
    "i-routes": '<path d="M3 19L9 13H15L21 7"/><path d="M2 18H5V21H2Z M19 5H22V8H19Z" fill="currentColor" stroke="none"/>',
    "i-wallet": '<path d="M6 5H21V16L18 19H3V8Z M3 11H21"/>',
    "i-inbox": '<path d="M3 4H21V20H3Z M3 13H8L10 16H14L16 13H21"/>',
    "i-contacts": '<path d="M5 6H11V12H5Z M13 10H19V16H13Z M3 21H13 M11 18H21"/>',
    "i-spend": '<path d="M5 4V9 M10 4V13 M15 4V17 M20 4V21"/>',
    "i-today": '<path d="M3 5H21V21H3Z M3 10H21 M8 2V7 M16 2V7"/><path d="M13 13H17V17H13Z" fill="currentColor" stroke="none"/>',
    "i-log": '<path d="M3 3H17L21 7V21H3Z M7 9H17 M7 13H17 M7 17H13"/>',
}
for _k, _v in _I.items():
    G[_k] = ("0 0 24 24", f'<g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square" stroke-linejoin="miter">{_v}</g>')




# ---------------------------------------------------------------- backdrops
# Large compositions behind screens, built only from the shape alphabet and
# the one "/" diagonal. Tonal (ground-2 / ground-3) so content stays legible;
# at most one small coral element. 390 x 844, bleeding off the edges.
def _chamf(cx, cy, hw, hh, c):
    return (f"{f(cx-hw+c)},{f(cy-hh)} {f(cx+hw)},{f(cy-hh)} {f(cx+hw)},{f(cy+hh-c)} "
            f"{f(cx+hw-c)},{f(cy+hh)} {f(cx-hw)},{f(cy+hh)} {f(cx-hw)},{f(cy-hh+c)}")


def _bg_tunnel(cx=150, cy=228):
    # clipped to the hero window so the masthead and body stay clean
    o = ['<clipPath id="bgt"><rect x="0" y="118" width="390" height="214"/></clipPath><g clip-path="url(#bgt)">',
         f'<path d="M{cx-520} {cy+520} L{cx+520} {cy-520}" stroke="var(--ground-3)" stroke-width="1" stroke-dasharray="2 6"/>']
    for i, h in enumerate(range(18, 330, 18)):
        col = "var(--ground-hi)" if i < 3 else "var(--ground-3)"
        op = ' opacity=".55"' if i < 3 else ""
        o.append(f'<polygon points="{_chamf(cx, cy, h * 1.18, h * .78, h * .3)}" fill="none" stroke="{col}" stroke-width="1.5"{op}/>')
    o.append(f'<polygon points="{_chamf(cx, cy, 11, 7, 3)}" fill="var(--coral)"/></g>')
    return "".join(o)


def _bg_slashes():
    o = []
    for k in range(10):
        x = -150 + k * 64
        w = 22
        col = "var(--ground-2)"
        o.append(f'<polygon points="{x},560 {x+w},560 {x+w+560},0 {x+560},0" fill="{col}"/>')
    return "".join(o)


def _bg_stack(x, y, w, h, c=24, n=3, step=14):
    o = []
    for k in range(n, 0, -1):
        dx, dy = k * step, -k * step
        col = "var(--ground-2)" if k == n else "var(--ground-3)"
        o.append(f'<polygon points="{_chamf(x+dx+w/2, y+dy+h/2, w/2, h/2, c)}" fill="none" stroke="{col}" stroke-width="1.5"/>')
    return "".join(o)


def _bg_diamonds():
    o = []
    for i, (cx, cy) in enumerate([(20, 560), (150, 430), (280, 300), (410, 170), (540, 40)]):
        s = 96
        pts = f"{cx},{cy-s} {cx+s},{cy} {cx},{cy+s} {cx-s},{cy}"
        o.append(f'<polygon points="{pts}" fill="{"var(--ground-2)" if i == 2 else "none"}" stroke="var(--ground-3)" stroke-width="1.5"/>')
    return "".join(o)


def _bg_lattice():
    o = []
    for r in range(12):
        for c in range(6):
            x, y = c * 78 + (39 if r % 2 else 0) - 20, r * 78 - 10
            col = "var(--coral)" if (r, c) == (9, 0) else "var(--ground-2)"
            o.append(f'<path transform="translate({x} {y}) scale(.56)" d="{XS}" fill="none" stroke="{col}" stroke-width="3"/>')
    return "".join(o)


def _bg_bars():
    o = []
    for i in range(20):
        h = 60 + 150 * abs(math.sin(i * 0.61) * math.cos(i * 0.23 + .4))
        o.append(f'<rect x="{i*20}" y="{f(844-h)}" width="13" height="{f(h)}" fill="var(--ground-2)"/>')
    return "".join(o)


def _bg_notch():
    return ('<polygon points="40,232 430,232 430,900 40,900" fill="none" stroke="var(--ground-3)" stroke-width="1.5"/>'
            '<polygon points="58,250 430,250 430,900 58,900" fill="none" stroke="var(--ground-2)" stroke-width="1.5"/>'
            '<polygon points="40,204 230,204 202,232 40,232" fill="var(--ground-2)"/>'
            '<path d="M240 218 H430" stroke="var(--ground-3)" stroke-width="1.5"/>')


def _bg_wedge():
    grid = "".join(f'<path d="M{x} 0 V300" stroke="var(--ground-2)" stroke-width="1"/>' for x in range(96, 391, 12))
    grid += "".join(f'<path d="M90 {y} H390" stroke="var(--ground-2)" stroke-width="1"/>' for y in range(0, 301, 12))
    return (f'<clipPath id="bgw"><polygon points="390,0 390,300 90,300"/></clipPath><g clip-path="url(#bgw)">{grid}</g>'
            '<path d="M60 330 L420 -30" stroke="var(--ground-hi)" stroke-width="1.5" opacity=".5"/>'
            '<polygon points="390,0 390,300 90,300" fill="none" stroke="var(--ground-3)" stroke-width="1.5"/>')


def _bg_ticks():
    o = []
    for side in (0, 1):
        for i, y in enumerate(range(130, 844, 8)):
            L = 18 if i % 5 == 0 else 8
            x0 = 0 if side == 0 else 390 - L
            col = "var(--ground-3)" if i % 5 else "var(--ground-dim)"
            o.append(f'<rect x="{x0}" y="{y}" width="{L}" height="1.5" fill="{col}"/>')
    o.append('<rect x="0" y="434" width="22" height="3" fill="var(--coral)"/>')
    return "".join(o)


BACKDROPS = {"tunnel": _bg_tunnel(), "slashes": _bg_slashes(), "stack-card": _bg_stack(24, 132, 342, 170),
             "stack-badge": _bg_stack(24, 128, 342, 300, 30), "plates": _bg_stack(170, 40, 240, 150, 20, 4, 16),
             "diamonds": _bg_diamonds(), "lattice": _bg_lattice(), "bars": _bg_bars(), "notch": _bg_notch(),
             "wedge": _bg_wedge(), "ticks": _bg_ticks()}
for _k, _v in BACKDROPS.items():
    G["bg-" + _k] = ("0 0 390 844", _v)


# ---------------------------------------------------------------- content motifs
# Shapes taken from each screen's subject, drawn with the alphabet's rules:
# level, upright or "/" only, square ends, print + ground + one coral.
def _m_tumblers():
    o = ['<path d="M0 48H342" stroke="var(--ground-dim)" stroke-width="1" stroke-dasharray="3 4"/>']
    offs = [0, 0, 0, 12, -10, 18]
    for i, d in enumerate(offs):
        x = 7 + i * 56
        o.append(f'<rect x="{x}" y="6" width="44" height="84" fill="none" stroke="var(--ground-3)" stroke-width="1.5"/>')
        col = "var(--coral)" if i == 2 else "currentColor"
        top = 46 + d
        o.append(f'<rect x="{x+14}" y="12" width="16" height="{top-12}" fill="{col}"/>')
        bot = 50 + d
        o.append(f'<polygon points="{x+14},{bot} {x+30},{bot} {x+30},{84-8} {x+22},84 {x+14},84" fill="none" stroke="{col}" stroke-width="2"/>')
        o.append(f'<text x="{x+22}" y="104" text-anchor="middle" class="xp-m" font-size="8" fill="var(--ground-dim)">P{i+1}</text>')
    return o


def _m_stamp():
    o = ['<rect x="4" y="4" width="92" height="112" fill="currentColor"/>']
    for k in range(12):
        o.append(f'<rect x="{8 + k*7.6:.1f}" y="1" width="4" height="6" fill="var(--ground)"/><rect x="{8 + k*7.6:.1f}" y="113" width="4" height="6" fill="var(--ground)"/>')
    for k in range(14):
        o.append(f'<rect x="1" y="{8 + k*7.6:.1f}" width="6" height="4" fill="var(--ground)"/><rect x="93" y="{8 + k*7.6:.1f}" width="6" height="4" fill="var(--ground)"/>')
    o.append('<rect x="14" y="14" width="72" height="92" fill="none" stroke="var(--ground)" stroke-width="1.5"/>')
    o.append('<g transform="rotate(45 50 50)"><path fill-rule="evenodd" fill="var(--coral)" d="M36 36H64V64H36Z M44 46H54V56H44Z"/></g>')
    o.append('<text x="50" y="98" text-anchor="middle" class="xp-d" font-size="15" fill="var(--ground)">0.09</text>')
    for k in range(5):
        o.append(f'<rect x="70" y="{28 + k*14}" width="130" height="3" fill="currentColor"/>')
    o.append('<rect x="118" y="36" width="70" height="46" fill="var(--ground)" stroke="currentColor" stroke-width="2"/>')
    o.append('<text x="153" y="55" text-anchor="middle" class="xp-m" font-size="9" fill="currentColor">LIS · 04</text>')
    o.append('<text x="153" y="70" text-anchor="middle" class="xp-m" font-size="9" fill="currentColor">17·11·26</text>')
    return o


def _m_dip():
    o = ['<rect x="2" y="2" width="338" height="96" fill="none" stroke="currentColor" stroke-width="1.5"/>',
         '<text x="14" y="18" class="xp-m" font-size="8.5" fill="currentColor">ON ▲</text>',
         '<text x="328" y="18" text-anchor="end" class="xp-m" font-size="8.5" fill="var(--ground-dim)">CFG · 1011 0110</text>']
    states = [1, 0, 1, 1, 0, 1, 1, 0]
    for i, on in enumerate(states):
        x = 26 + i * 38
        o.append(f'<rect x="{x}" y="26" width="24" height="52" fill="var(--ground-3)"/>')
        col = "var(--coral)" if i == 5 else "currentColor"
        o.append(f'<rect x="{x+3}" y="{29 if on else 52}" width="18" height="23" fill="{col}"/>')
        o.append(f'<text x="{x+12}" y="92" text-anchor="middle" class="xp-m" font-size="8" fill="var(--ground-dim)">{i+1}</text>')
    return o


def _m_barbs():
    o = []
    speeds = [10, 15, 25, 35, 50, 30]
    hours = ["14", "15", "16", "17", "18", "19"]
    for i, (v, h) in enumerate(zip(speeds, hours)):
        x = 26 + i * 58
        col = "var(--coral)" if v >= 50 else "currentColor"
        o.append(f'<path d="M{x} 84V20" stroke="{col}" stroke-width="2.5"/>')
        o.append(f'<rect x="{x-4}" y="82" width="8" height="8" fill="{col}"/>')
        y, rem = 20, v
        while rem >= 50:
            o.append(f'<polygon points="{x},{y+14} {x+14},{y} {x},{y}" fill="{col}"/>'); y += 18; rem -= 50
        while rem >= 10:
            o.append(f'<path d="M{x} {y+16}L{x+16} {y}" stroke="{col}" stroke-width="2.5"/>'); y += 8; rem -= 10
        if rem >= 5:
            o.append(f'<path d="M{x} {y+16}L{x+8} {y+8}" stroke="{col}" stroke-width="2.5"/>')
        o.append(f'<text x="{x}" y="106" text-anchor="middle" class="xp-m" font-size="8.5" fill="var(--ground-dim)">{h}:00</text>')
        o.append(f'<text x="{x+12}" y="84" class="xp-m" font-size="8.5" fill="currentColor">{v}</text>')
    return o


def _m_compass():
    o = []
    for ang, L, col in [(0, 34, "var(--coral)"), (90, 30, "currentColor"), (180, 30, "currentColor"), (270, 30, "currentColor"),
                        (45, 18, "var(--ground-dim)"), (135, 18, "var(--ground-dim)"), (225, 18, "var(--ground-dim)"), (315, 18, "var(--ground-dim)")]:
        o.append(f'<g transform="rotate({ang} 40 40)"><polygon points="40,{40-L} 45,40 40,{40+5} 35,40" fill="{col}"/></g>')
    o.append('<text x="40" y="78" text-anchor="middle" class="xp-m" font-size="8" fill="currentColor">N 038°</text>')
    return o


def _m_print():
    o = []
    for i, r in enumerate(range(4, 30, 4)):
        dash = ["40 6", "28 5", "52 7", "34 6", "60 8", "22 5", "70 9"][i % 7]
        o.append(f'<polygon points="{_chamf(30, 32, r * .78, r, r * .35)}" fill="none" stroke="currentColor" stroke-width="1.6" stroke-dasharray="{dash}"/>')
    return o


def _m_flow():
    o = [f'<polygon points="{_chamf(30, 27, 28, 20, 8)}" fill="none" stroke="currentColor" stroke-width="1.5"/>',
         '<text x="30" y="31" text-anchor="middle" class="xp-m" font-size="9" fill="currentColor">4417</text>',
         f'<polygon points="{_chamf(312, 27, 28, 20, 8)}" fill="currentColor"/>',
         '<text x="312" y="32" text-anchor="middle" class="xp-t" font-size="12" fill="var(--ground)">LS</text>']
    for k in range(10):
        x = 76 + k * 19
        col = "var(--coral)" if k == 6 else ("currentColor" if k < 6 else "var(--ground-3)")
        o.append(f'<polygon points="{x+8},18 {x+16},18 {x+8},36 {x},36" fill="{col}"/>')
    o.append('<polygon points="266,20 280,27 266,34" fill="currentColor"/>')
    o.append('<text x="171" y="52" text-anchor="middle" class="xp-m" font-size="8.5" fill="var(--ground-dim)">7 / 10 PACKETS · AES-256</text>')
    return o


def _m_micro():
    o = []
    line = "AXIOM·SIGNAL·0917·" * 8
    for k in range(20):
        o.append(f'<text x="{-(k % 3) * 18}" y="{6 + k*7}" class="xp-m" font-size="4.6" fill="currentColor">{line}</text>')
    return o


def _m_meters():
    o = []
    for c, (lv, lab) in enumerate([(13, "L"), (11, "R")]):
        x = 4 + c * 20
        for k in range(16):
            y = 150 - k * 9
            col = "var(--coral)" if k == lv - 1 and k >= 12 else ("currentColor" if k < lv else "var(--ground-3)")
            o.append(f'<rect x="{x}" y="{y}" width="14" height="6" fill="{col}"/>')
        o.append(f'<text x="{x+7}" y="168" text-anchor="middle" class="xp-m" font-size="8" fill="var(--ground-dim)">{lab}</text>')
    return o


for _k, _vb, _fn in [("m-tumblers", "0 0 342 108", _m_tumblers), ("m-stamp", "0 0 200 120", _m_stamp), ("m-dip", "0 0 342 100", _m_dip),
                     ("m-barbs", "0 0 342 112", _m_barbs), ("m-compass", "0 0 80 82", _m_compass), ("m-print", "0 0 60 64", _m_print),
                     ("m-flow", "0 0 342 56", _m_flow), ("m-micro", "0 0 342 140", _m_micro), ("m-meters", "0 0 38 172", _m_meters)]:
    G[_k] = (_vb, "".join(_fn()))


def _bg_pcb():
    traces = [[(0, 160), (90, 160), (150, 100), (390, 100)], [(0, 300), (40, 300), (120, 220), (260, 220), (300, 180), (390, 180)],
              [(60, 844), (60, 640), (170, 530), (170, 420)], [(390, 520), (300, 520), (240, 580), (240, 844)],
              [(0, 700), (110, 700), (200, 610), (390, 610)], [(330, 0), (330, 60), (280, 110)], [(20, 0), (20, 90), (70, 140), (70, 200)],
              [(390, 760), (330, 760), (290, 800), (290, 844)], [(130, 844), (130, 760), (210, 680), (390, 680)]]
    o = []
    for i, t in enumerate(traces):
        pts = " ".join(f"{x},{y}" for x, y in t)
        o.append(f'<polyline points="{pts}" fill="none" stroke="{"var(--ground-2)" if i % 3 else "var(--ground-3)"}" stroke-width="{5 if i % 3 == 0 else 2}" stroke-linejoin="miter"/>')
        for x, y in (t[0], t[-1]):
            if 0 < x < 390 and 0 < y < 844:
                o.append(f'<rect x="{x-6}" y="{y-6}" width="12" height="12" fill="var(--ground-3)"/><rect x="{x-2}" y="{y-2}" width="4" height="4" fill="var(--ground)"/>')
    for x, y in [(90, 160), (260, 220), (170, 530), (200, 610), (300, 520)]:
        o.append(f'<rect x="{x-4}" y="{y-4}" width="8" height="8" fill="var(--ground-3)"/>')
    return "".join(o)


def _bg_terrace():
    o = []
    for k in range(16):
        base = 900 - k * 46
        pts, x, y = [], -40, base
        pts.append((x, y))
        while x < 430:
            run = 50 + (k * 37 + x) % 70
            x += run; pts.append((x, y))
            rise = 18 + (k * 13 + x) % 30
            x += rise; y -= rise; pts.append((x, y))
        col = "var(--ground-3)" if k % 4 == 0 else "var(--ground-2)"
        o.append(f'<polyline points="{" ".join(f"{a},{b}" for a, b in pts)}" fill="none" stroke="{col}" stroke-width="1.5"/>')
    return "".join(o)


G["bg-pcb"] = ("0 0 390 844", _bg_pcb())
G["bg-terrace"] = ("0 0 390 844", _bg_terrace())



def _bg_tiers():
    o = []
    for k in range(9):
        apex, L = 70 + k * 46, 420
        col = "var(--ground-3)" if k % 3 == 0 else "var(--ground-2)"
        o.append(f'<polyline points="{195-L},{apex+L} 195,{apex} {195+L},{apex+L}" fill="none" stroke="{col}" stroke-width="{10 if k % 3 == 0 else 1.5}"/>')
    return "".join(o)


def _bg_decay():
    o = []
    for i, y in enumerate(range(150, 860, 22)):
        dash, gap = max(2, 60 - i * 2), 2 + i * 2
        o.append(f'<path d="M0 {y}H390" stroke="var(--ground-2)" stroke-width="2" stroke-dasharray="{dash} {gap}"/>')
    o.append('<rect x="24" y="414" width="18" height="2" fill="var(--coral)"/>')
    return "".join(o)


def _bg_relays():
    lines = [[(0, 660), (110, 660), (270, 500), (390, 500)], [(0, 730), (170, 730), (330, 570), (390, 570)], [(0, 820), (230, 820), (390, 660)]]
    o = []
    for t in lines:
        o.append(f'<polyline points="{" ".join(f"{x},{y}" for x, y in t)}" fill="none" stroke="var(--ground-3)" stroke-width="1.5"/>')
        for x, y in t[1:-1]:
            o.append(f'<rect x="{x-6}" y="{y-6}" width="12" height="12" fill="none" stroke="var(--ground-3)" stroke-width="1.5"/>')
    return "".join(o)


def _bg_columns():
    o = [f'<path d="M{x} 0V844" stroke="var(--ground-2)" stroke-width="1"/>' for x in (24, 105, 186, 267, 366)]
    o += [f'<path d="M0 {y}H390" stroke="var(--ground-2)" stroke-width="1"/>' for y in range(300, 844, 22)]
    o += ['<path d="M8 290H18 M24 274V284 M372 290H382 M366 274V284" stroke="var(--ground-dim)" stroke-width="1"/>']
    return "".join(o)


def _bg_airmail():
    o = []
    for y in range(-24, 880, 24):
        for x0 in (0, 378):
            col = "var(--ground-3)" if (y // 24) % 2 else "var(--ground-2)"
            o.append(f'<polygon points="{x0},{y+12} {x0+12},{y} {x0+12},{y+12} {x0},{y+24}" fill="{col}"/>')
    return "".join(o)


G["bg-tiers"] = ("0 0 390 844", _bg_tiers())
G["bg-decay"] = ("0 0 390 844", _bg_decay())
G["bg-relays"] = ("0 0 390 844", _bg_relays())
G["bg-columns"] = ("0 0 390 844", _bg_columns())
G["bg-airmail"] = ("0 0 390 844", _bg_airmail())

# ---------------------------------------------------------------- monoliths (grand backdrops)
sys.path.insert(0, str(ROOT / "tools"))
import monoliths  # noqa: E402
monoliths.SEGS = _segs
for _k in monoliths.MONOLITHS:
    G["bg-" + _k] = ("0 0 390 844", monoliths.svg(_k))


# ---------------------------------------------------------------- constructed type
# Block letters on a 6-unit grid, 1.4-unit strokes, TL/BR cuts only.
_LET = {
    "A": (6, "M1.4 0H6V6H4.6V3.8H1.4V6H0V1.4Z M1.4 1.4H4.6V2.4H1.4Z"),
    "X": (6, "M0 0H2V2.2H0Z M4 0H6V2.2H4Z M1.2 1.9H4.8V4.1H1.2Z M0 3.8H2V6H0Z M4 3.8H6V6H4Z"),
    "I": (4.4, "M0 0H4.4V1.4H2.9V4.6H4.4V6H0V4.6H1.5V1.4H0Z"),
    "O": (6, "M1.4 0H6V4.6L4.6 6H0V1.4Z M1.4 1.4H4.6V4.6H1.4Z"),
    "0": (6, "M1.4 0H6V4.6L4.6 6H0V1.4Z M1.4 1.4H4.6V4.6H1.4Z"),
    "M": (6, "M0 0H6V6H4.6V1.4H3.7V4.2H2.3V1.4H1.4V6H0Z"),
    "S": (6, "M1.4 0H6V1.4H1.4V2.3H6V4.6L4.6 6H0V4.6H4.6V3.7H0V1.4Z"),
    "P": (6, "M1.4 0H6V3.8H1.4V6H0V1.4Z M1.4 1.4H4.6V2.4H1.4Z"),
    "9": (6, "M1.4 0H6V4.6L4.6 6H0V4.6H4.6V3.8H0V1.4Z M1.4 1.4H4.6V2.4H1.4Z"),
    "-": (3, "M0 2.4H3V3.6H0Z"),
}


def constructed(text, unit=10, x=0, y=0, fill="var(--ground-hi)"):
    o, cx = [], 0.0
    for ch in text:
        w, d = _LET[ch]
        o.append(f'<path transform="translate({f(x + cx * unit)} {y}) scale({unit})" d="{d}" fill="{fill}" fill-rule="evenodd"/>')
        cx += w + .8
    return "".join(o), (cx - .8) * unit


def exploded_x(cx, cy, s, h=None, fill="var(--coral)"):
    """The hard X broken into slabs: three on the '/' stroke, two on the other."""
    h = h or s * .34
    def seg(x0, y0, x1, y1):
        return f'<polygon points="{f(x0)},{f(y0)} {f(x0+h)},{f(y0)} {f(x1+h)},{f(y1)} {f(x1)},{f(y1)}" fill="{fill}"/>'
    o, g = [], s * .14
    a = (cx - s - h / 2, cy + s)
    for t0, t1 in [(0, .62), (.62 + g / s, 1.38 - g / s), (1.38, 2)]:
        o.append(seg(a[0] + t0 * s, a[1] - t0 * s, a[0] + t1 * s, a[1] - t1 * s))
    b = (cx - s - h / 2, cy - s)
    for t0, t1 in [(0, .62), (1.38, 2)]:
        o.append(seg(b[0] + t0 * s, b[1] + t0 * s, b[0] + t1 * s, b[1] + t1 * s))
    return "".join(o)



# ---------------------------------------------------------------- relay network diagram
# Routes run level or along "/" only; nodes are cut squares; one route is the signal.
def relay_net(cities, routes, hot=None, label=True, size=12):
    """cities: {name: (x, y, sub)}; routes: [[name or (x, y), ...]]; hot: index of the coral route."""
    def pt(p):
        return cities[p][:2] if isinstance(p, str) else p
    o = []
    for i, r in enumerate(routes):
        pts = " ".join(f"{f(x)},{f(y)}" for x, y in map(pt, r))
        col = "var(--coral)" if i == hot else "var(--ground-hi)"
        w = 3 if i == hot else 1.5
        o.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="miter"/>')
    for name, (x, y, sub) in cities.items():
        h = size / 2
        o.append(f'<polygon points="{f(x-h+3)},{f(y-h)} {f(x+h)},{f(y-h)} {f(x+h)},{f(y+h-3)} {f(x+h-3)},{f(y+h)} {f(x-h)},{f(y+h)} {f(x-h)},{f(y-h+3)}" fill="var(--ground)" stroke="var(--ground-hi)" stroke-width="1.5"/>')
        o.append(f'<rect x="{f(x-2)}" y="{f(y-2)}" width="4" height="4" fill="var(--ground-hi)"/>')
        if label:
            o.append(f'<text x="{f(x+h+6)}" y="{f(y-2)}" class="xp-t" font-size="11" fill="var(--ground-hi)">{name.upper()}</text>'
                     f'<text x="{f(x+h+6)}" y="{f(y+9)}" class="xp-m" font-size="6.5" fill="var(--ground-dim)">{sub}</text>')
    return "".join(o)


NET_CITIES = {"Lisbon": (60, 250, "RELAY 04 · 23 MS"), "Porto": (60, 130, "RELAY 07 · 31 MS"), "Lyon": (170, 100, "RELAY 02 · 48 MS"),
              "Osaka": (250, 30, "RELAY 12 · 212 MS"), "Seoul": (220, 210, "RELAY 09 · 188 MS")}
NET_ROUTES = [["Lisbon", (60, 190), "Porto"], ["Porto", (110, 130), (140, 100), "Lyon"], ["Lyon", (200, 100), (250, 50), "Osaka"],
              ["Lisbon", (130, 250), (170, 210), "Seoul"], ["Seoul", (220, 140), (250, 110), (250, 30)]]


def sprite():
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="position:absolute" aria-hidden="true"><defs>']
    for k, (vb, inner) in G.items():
        out.append(f'<symbol id="g-{k}" viewBox="{vb}">{inner}</symbol>')
    out.append("</defs></svg>")
    return "".join(out)


def export_glyphs():
    d = ROOT / "assets" / "svg"
    d.mkdir(parents=True, exist_ok=True)
    for k, (vb, inner) in G.items():
        if k.startswith(("bg-", "m-")):
            continue
        w, h = vb.split()[2:]
        body = inner.replace("currentColor", "var(--ink)")
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}">{body}</svg>\n'
        if "var(--" in inner:  # multi-colour glyph: one file per appearance
            (d / f"{k}-dark.svg").write_text(resolve(svg, "dark"))
            (d / f"{k}-light.svg").write_text(resolve(svg, "light"))
        else:                  # single colour: use as a template image, tint in code
            (d / f"{k}.svg").write_text(resolve(svg, "dark"))


# ---------------------------------------------------------------- poster
def keyart(mode):
    """Key art: the shirt's print stack + the poster's instrument column, in HTML."""
    return f'''<figure class="mode-{mode}"><div class="ka tex"><div class="ka-in">
      <div class="ka-mast"><span class="u-code">SK·09·LIS</span><span class="sg-display">AXIOM</span></div>
      <div class="slab-cut ka-slab"></div><div class="ka-head brackets"><svg><use href="#g-reg"/></svg></div>
      <div class="yearspan sg-num ka-year">20<i></i>26</div>
      <div class="ka-trio"><div class="sg-label">Signal engineering</div><div class="sg-jp sg-justify">信号工学</div><div class="sg-label">Ingénierie du signal</div></div>
      <div class="ka-side"><div><div class="sg-num">09</div><div class="sg-mono">#bab9ad</div></div>
        <svg viewBox="0 0 100 100"><use href="#g-x-line"/></svg><svg viewBox="0 0 100 100"><use href="#g-x-solid"/></svg>
        <i class="barcode"></i><div class="sg-mono">REF:<br>OPSEC/AHI<br>SP C53</div></div>
      <div class="ka-chev"><svg viewBox="0 0 300 230"><use href="#g-chevrons"/></svg></div>
      <div class="hazard ka-haz"></div>
      <div class="ka-foot"><div><div class="sg-label">Axiom signal systems</div><div class="sg-mono">COMSEC MONITORING · NETWORK OPERATIONS AND DEFENSE</div></div><i class="barcode--v"></i></div>
    </div></div><figcaption class="cap"><b>Key art · {mode}</b><span>{"bone print on ink stripes" if mode == "dark" else "ink print on sage stripes"}</span></figcaption></figure>'''


# ---------------------------------------------------------------- explorations: poster series + motion
def _xp_frame(n, word, jp, line, body):
    """Shared poster frame: masthead, art window (40..470), footer with display word."""
    return (f'<svg class="xp" viewBox="0 0 400 600" role="img" aria-label="Poster {n}: {word}">'
            f'<rect width="400" height="600" fill="var(--ground)"/>{body}'
            f'<text x="24" y="28" class="xp-d" font-size="15" fill="var(--ground-hi)">AXIOM</text>'
            f'<text x="376" y="27" class="xp-m" font-size="9" fill="var(--ground-dim)" text-anchor="end">XP·{n} · SHINGŌ FIELD SERIES</text>'
            f'<rect x="24" y="492" width="352" height="1.5" fill="var(--ground-hi)"/>'
            f'<text x="22" y="554" class="xp-d" font-size="46" fill="var(--ground-hi)">{word}</text>'
            f'<text x="376" y="482" class="xp-j" font-size="18" fill="var(--ground-hi)" text-anchor="end">{jp}</text>'
            f'<text x="24" y="578" class="xp-m" font-size="9" fill="var(--ground-dim)">{line}</text>'
            f'<text x="376" y="578" class="xp-m" font-size="9" fill="var(--ground-dim)" text-anchor="end">{n} / 06</text></svg>')


def _xp_tunnel():
    o = ['<clipPath id="xpc1"><rect x="0" y="44" width="400" height="418"/></clipPath><g clip-path="url(#xpc1)">',
         '<path d="M-200 650 L600 -150" stroke="var(--ground-3)" stroke-width="1" stroke-dasharray="2 6"/>']
    for i, h in enumerate(range(14, 300, 15)):
        col = "var(--ground-hi)" if i < 4 else "var(--ground-3)"
        o.append(f'<polygon points="{_chamf(200, 258, h * 1.15, h * .8, h * .3)}" fill="none" stroke="{col}" stroke-width="1.5"/>')
    o.append(f'<polygon points="{_chamf(200, 258, 12, 8, 3)}" fill="var(--coral)"/></g>')
    return _xp_frame("01", "TUNNEL", "隧道", "THREE RELAYS · ONE SEALED ROUTE", "".join(o))


def _xp_lattice():
    o = []
    for r in range(7):
        for c in range(6):
            x, y = 22 + c * 60, 52 + r * 60
            if (r, c) == (2, 4):
                o.append(f'<path transform="translate({x} {y}) scale(.52)" d="{XS}" fill="var(--coral)"/>')
            elif (r, c) == (4, 1):
                o.append(f'<path transform="translate({x} {y}) scale(.52)" d="{XS}" fill="var(--ground-hi)"/>')
            else:
                o.append(f'<path transform="translate({x} {y}) scale(.52)" d="{XS}" fill="none" stroke="var(--ground-3)" stroke-width="3.5"/>')
    return _xp_frame("02", "LATTICE", "格子", "42 NODES · ONE ACTIVE · ONE FAULT", "".join(o))


def _xp_slash():
    o = ['<clipPath id="xpc3"><rect x="0" y="44" width="400" height="418"/></clipPath><g clip-path="url(#xpc3)">']
    for k in range(-12, 18):
        x = k * 40
        o.append(f'<polygon points="{x},474 {x+22},474 {x+452},44 {x+430},44" fill="var(--ground-hi)"/>')
    o.append('</g>')
    o.append(f'<polygon points="{_chamf(200, 260, 162, 74, 18)}" fill="var(--ground)"/>')
    o.append(f'<polygon points="{_chamf(200, 260, 162, 74, 18)}" fill="none" stroke="var(--ground-hi)" stroke-width="1.5"/>')
    o.append(f'<g transform="translate(66 226)">{seg7("09:41", 68, "2")}</g>')
    o.append('<text x="56" y="210" class="xp-m" font-size="9" fill="var(--ground-dim)">LOCAL TIME · LIS</text>')
    return _xp_frame("03", "SLASH", "斜線", "ONE ANGLE · RISING LEFT TO RIGHT", "".join(o))


def _xp_signal():
    body = ('<use href="#g-chevrons" x="40" y="62" width="320" height="246" style="color:var(--ground-hi)"/>'
            '<text x="24" y="352" class="xp-t" font-size="19" fill="var(--ground-hi)">SIGNAL ENGINEERING</text>'
            '<text x="24" y="382" class="xp-j" font-size="19" fill="var(--ground-hi)" textLength="230" lengthAdjust="spacing">信号工学</text>'
            '<text x="24" y="410" class="xp-t" font-size="19" fill="var(--ground-hi)">INGÉNIERIE DU SIGNAL</text>'
            '<polygon points="400,318 400,462 256,462" fill="var(--coral)"/>'
            '<text x="24" y="450" class="xp-m" font-size="9" fill="var(--ground-dim)">REF: OPSEC/AHI · SP C53</text>')
    return _xp_frame("04", "SIGNAL", "信号", "ENGLISH · 日本語 · FRANÇAIS", body)


def _mo_tunnel():
    rings = "".join(f'<polygon style="--i:{i}" points="{_chamf(150, 90, h * 1.15, h * .8, h * .3)}"/>' for i, h in enumerate(range(10, 130, 12)))
    return (f'<svg class="mo-tunnel" viewBox="0 0 300 180">{rings}'
            f'<polygon points="{_chamf(150, 90, 9, 6, 2)}" fill="var(--coral)" stroke="none"/></svg>')



def _xp_relay():
    o = ['<polygon points="94,170 330,170 330,452 316,466 80,466 80,184" fill="none" stroke="var(--ground-3)" stroke-width="1.5"/>',
         f'<g transform="translate(92 176) scale(.9)">{relay_net(NET_CITIES, NET_ROUTES, hot=3)}</g>',
         '<g stroke="var(--coral)" stroke-width=".8">'
         '<path d="M0 158H400 M0 470H400 M68 44V474 M340 44V474"/></g>',
         '<g fill="var(--coral)"><rect x="64" y="154" width="8" height="8"/><rect x="336" y="466" width="8" height="8"/><rect x="200" y="62" width="5" height="5"/></g>',
         '<path d="M330 120h20 M340 110v20 M60 470h16 M68 462v16" stroke="var(--coral)" stroke-width="1"/>',
         exploded_x(278, 108, 40),
         '<polygon points="38,300 92,300 92,470 24,470 24,314" fill="var(--ground-hi)"/>',
         ''.join(f'<text x="58" y="{344 + i*30}" text-anchor="middle" class="xp-j" font-size="24" fill="var(--ground)">{c}</text>' for i, c in enumerate("中継塔"))
         + '<text x="58" y="458" text-anchor="middle" class="xp-m" font-size="7" fill="var(--ground)">Nº 05</text>',
         '<text x="350" y="60" class="xp-m" font-size="7" fill="var(--coral)" transform="rotate(90 350 60)">2835 × 1890 PX · 200 PPI</text>',
         '<text x="24" y="70" class="xp-m" font-size="7" fill="var(--ground-dim)">ABOVE THE NOISE,</text><text x="24" y="80" class="xp-m" font-size="7" fill="var(--ground-dim)">MACHINES HUM IN SILENCE</text>',
         '<text x="24" y="120" class="xp-d" font-size="11" fill="var(--coral)">2026</text><text x="24" y="134" class="xp-m" font-size="7" fill="var(--coral)">NOV 17</text>']
    return _xp_frame("05", "RELAY", "中継", "SILENT RELAY · FIVE NODES · ONE SIGNAL ROUTE", "".join(o))


def _xp_ops():
    o = ['<clipPath id="xpc6"><rect x="24" y="50" width="352" height="46"/></clipPath><g clip-path="url(#xpc6)">']
    for k in range(-4, 30):
        x = 24 + k * 18
        o.append(f'<polygon points="{x},96 {x+10},96 {x+56},50 {x+46},50" fill="var(--ground-hi)"/>')
    o.append('</g>')
    stat = [(24, 122, "System verified", "Status – active"), (190, 122, "Protocol synced", "Status – stable"),
            (24, 152, "Field unit calibrated", "Status – online"), (190, 152, "Relay certified", "Status – operational")]
    for x, y, a, b in stat:
        o.append(f'<text x="{x}" y="{y}" class="xp-t" font-size="10.5" fill="var(--ground-hi)">{a.upper()}</text>'
                 f'<text x="{x}" y="{y+12}" class="xp-m" font-size="7.5" fill="var(--ground-dim)">{b.upper()}</text>')
    o.append('<text x="376" y="134" text-anchor="end" class="xp-d" font-size="22" fill="var(--ground-hi)">LIS</text>')
    o.append('<rect x="356" y="146" width="20" height="20" fill="none" stroke="var(--ground-hi)" stroke-width="2"/><text x="366" y="160" text-anchor="middle" class="xp-t" font-size="11" fill="var(--ground-hi)">R</text>')
    word, w = constructed("AX-09", unit=11.6, x=24, y=188)
    o.append(word)
    lines = ["AX-09 IS A ████ RELAY DIVISION FOCUSED", "ON SEALED ROUTING AND ███████ ████", "INFRASTRUCTURE. OUR KEYS INTEGRATE", "DIRECTLY INTO ██████ NETWORKS, ENABLING", "QUIET TRANSIT AND ████ EXECUTION."]
    for i, ln in enumerate(lines):
        x = 24
        for j, part in enumerate(ln.split("█")):
            pass
        o.append(f'<text x="24" y="{290 + i*10}" class="xp-m" font-size="6.6" fill="var(--ground-dim)">{ln.replace("█", " ")}</text>')
    # redaction bars over the gaps (positioned by monospace advance ~ .6em)
    adv = 6.6 * (.6 + .04)  # mono advance + .xp-m letter-spacing
    for i, ln in enumerate(lines):
        j = 0
        while j < len(ln):
            if ln[j] == "█":
                k = j
                while k < len(ln) and ln[k] == "█":
                    k += 1
                o.append(f'<rect x="{f(24 + j*adv)}" y="{283 + i*10}" width="{f((k-j)*adv)}" height="8" fill="var(--ground-hi)"/>')
                j = k
            else:
                j += 1
    # id plate
    o.append('<rect x="214" y="276" width="162" height="62" fill="none" stroke="var(--ground-hi)" stroke-width="2"/>'
             '<path d="M260 276V338 M260 306H376 M314 276V306" stroke="var(--ground-hi)" stroke-width="2"/>')
    o.append(f'<path transform="translate(222 290) scale(.36)" d="{XS}" fill="var(--ground-hi)"/>')
    o.append('<text x="287" y="295" text-anchor="middle" class="xp-t" font-size="8.5" fill="var(--ground-hi)">AX-OPS</text>')
    for i, ch in enumerate("LIS"):
        bx = 320 + i * 18
        fill = "var(--coral)" if i == 0 else "none"
        tc = "#0c0c0a" if i == 0 else "var(--ground-hi)"
        o.append(f'<rect x="{bx}" y="281" width="15" height="20" fill="{fill}" stroke="var(--ground-hi)" stroke-width="1.5"/><text x="{bx+7.5}" y="295" text-anchor="middle" class="xp-t" font-size="10" fill="{tc}">{ch}</text>')
    o.append('<text x="268" y="326" class="xp-t" font-size="8.6" fill="var(--ground-hi)">LOG ID: 2611-A-09</text>')
    o.append('<rect x="24" y="360" width="352" height="26" fill="var(--ground-hi)"/>'
             '<text x="34" y="377" class="xp-t" font-size="10.5" fill="var(--ground)">SIGNAL INTEGRATION</text>'
             '<text x="200" y="377" text-anchor="middle" class="xp-m" font-size="10" fill="var(--ground)">----</text>'
             '<text x="366" y="377" text-anchor="end" class="xp-t" font-size="10.5" fill="var(--ground)">RELAY OPERATIONS</text>')
    o.append('<text x="24" y="420" class="xp-t" font-size="9" fill="var(--ground-hi)">INTERNAL USE ONLY / AUTHORIZED PERSONNEL / LIS – 2026</text>')
    o.append('<rect x="24" y="440" width="352" height="1" fill="var(--ground-3)"/>')
    return _xp_frame("06", "OPS", "運用", "STATUS ACTIVE · PROTOCOL SYNCED · EYES ONLY", "".join(o))


def explorations():
    posters = [_xp_tunnel(), _xp_lattice(), _xp_slash(), _xp_signal(), _xp_relay(), _xp_ops()]
    cells = "".join(f'<i style="--i:{i}"></i>' for i in range(12))
    return f'''<section class="sec">
  <div class="sec-h"><span class="sg-num">06</span><h2 class="sg-display">Explorations</h2><span class="sg-mono">a poster series and motion studies · each piece built from one primitive of the alphabet</span></div>
  <div class="xp-grid">{"".join(f'<figure>{p}</figure>' for p in posters)}</div>
  <div class="alpha-h" style="margin-top:36px"><span class="sg-cap">Motion and live behaviour</span><span class="sg-mono">never eased · slides glide, states step · still when reduced motion is on · on the screens above: tap a tab, point at data</span></div>
  <div class="mo-grid">
    <figure><div class="mo">{_mo_tunnel()}</div><figcaption><b>Tunnel pulse</b><span>Connecting. A print frame travels outward ring by ring.</span></figcaption></figure>
    <figure><div class="mo"><div class="cells cells--tall mo-cells">{cells}</div><div class="sg-mono mo-lbl">SYNCING RELAYS</div></div><figcaption><b>Cell fill</b><span>Indeterminate progress. Cells fill in order, then reset.</span></figcaption></figure>
    <figure><div class="mo"><svg class="mo-scope" viewBox="0 0 200 200"><use href="#g-scope"/><g class="mo-sweep"><polygon points="100,100 196,100 190,72" fill="var(--coral)"/></g></svg></div><figcaption><b>Step sweep</b><span>Scanning. The sweep turns in eight 45° steps.</span></figcaption></figure>
    <figure><div class="mo"><div class="hazard hazard--run" style="width:76%"></div><div class="sg-mono mo-lbl">WRITING FIRMWARE<i class="caret"></i></div></div><figcaption><b>March</b><span>Busy. Hazard stripes march along the one diagonal.</span></figcaption></figure>
    <figure><div class="mo mo-wipe" style="position:relative"><div class="mo-view"><div class="sg-display" style="font-size:30px;color:var(--ground-hi)">Protected</div><div class="sg-mono mo-lbl" style="margin-top:8px;color:var(--ground-dim)">SINCE 08:14 · LIS-04</div></div><div class="mo-view" hidden><div class="sg-display" style="font-size:30px;color:var(--ground-hi)">Run log</div><div class="sg-mono mo-lbl" style="margin-top:8px;color:var(--ground-dim)">W46 · 42.6 KM</div></div><div class="mo-view" hidden><div class="sg-display" style="font-size:30px;color:var(--ground-hi)">Wallet</div><div class="sg-mono mo-lbl" style="margin-top:8px;color:var(--ground-dim)">€8,214.60</div></div></div><figcaption><b>Print wipe</b><span>Between views a hazard band slides across on the diagonal, and the new title resolves from glyph noise.</span></figcaption></figure>
    <figure><div class="mo"><div style="display:grid;gap:6px;justify-items:center">{seg7("02:47", 54, "2", cls="live-down")}<span class="sg-mono mo-lbl" style="color:var(--ground-dim)">ROUND 3 · WORK</span></div></div><figcaption><b>Live readout</b><span>Readouts re-render segment by segment: timers count, counters climb, coordinates drift.</span></figcaption></figure>
  </div>
</section>'''



# ---------------------------------------------------------------- patterns + console
_FLEET = [("04", "Lisbon", "23", 4, "ok"), ("07", "Porto", "31", 6, "ok"), ("03", "Lyon", "212", 9, "warn"),
          ("12", "Osaka", "—", 0, "off"), ("09", "Seoul", "188", 7, "busy"), ("02", "Reykjavík", "—", 0, "fault")]
_STATE = {"ok": "nominal", "warn": "caution", "fault": "fault", "off": "offline", "busy": "syncing"}


def _cells(n, on, hot=-1):
    return '<div class="cells" style="padding-left:9px">' + "".join(f'<i class="{"hot" if i == hot else ("on" if i < on else "")}" style="height:10px"></i>' for i in range(n)) + "</div>"


def spec_table(rows, selected=1):
    body = "".join(
        f'<tr aria-selected="{"true" if i == selected else "false"}"><td class="idx">{i+1:02d}</td><td><b class="sg-wordmark" style="font-size:12px">{c}</b><br><span class="sg-mono" style="color:var(--ground-dim)">RELAY {r}</span></td>'
        f'<td class="n">{l}{" ms" if l != "—" else ""}</td><td style="width:34%">{_cells(10, ld, hot=9 if ld >= 9 else -1)}</td><td><span class="state state--{s}">{_STATE[s]}</span></td></tr>'
        for i, (r, c, l, ld, s) in enumerate(rows))
    return ('<div class="stable-wrap"><table class="stable"><thead><tr><th><small>C-01</small>Nº</th><th><small>C-02</small>Relay</th><th class="n"><small>C-03</small>Latency</th>'
            f'<th><small>C-04</small>Load</th><th><small>C-05</small>State</th></tr></thead><tbody>{body}</tbody></table></div>')


def patterns():
    return f'''  <div class="alpha-h" style="margin-top:30px"><span class="sg-cap">Patterns for any app</span><span class="sg-mono">state language · spec tables · form set · telex · skeletons · every one is live</span></div>
  <div class="insts">
    <div class="inst inst--wide"><h3><span>State language</span><span>.state · SGState</span></h3><p>Every system state has one fixed shape, so any app reads the same: nominal is a solid square, caution is hatched, fault is a coral X, offline is a dim X, and busy marches.</p>
      <div class="demo" style="display:block"><div class="spec spec--ground" style="grid-template-columns:120px minmax(0,1fr) minmax(12px,.6fr) auto;row-gap:14px"><span class="state state--ok">Nominal</span><span style="color:var(--ground-dim)">solid square · print</span><i></i><span>running as specified</span><span class="state state--warn">Caution</span><span style="color:var(--ground-dim)">hatched square · print</span><i></i><span>degraded, still working</span><span class="state state--fault">Fault</span><span style="color:var(--ground-dim)">hard X · coral</span><i></i><span>stopped, needs action</span><span class="state state--off">Offline</span><span style="color:var(--ground-dim)">hard X · dim</span><i></i><span>not reporting</span><span class="state state--busy">Syncing</span><span style="color:var(--ground-dim)">marching hatch</span><i></i><span>work in progress</span></div></div></div>
    <div class="inst inst--wide"><h3><span>Spec table</span><span>.stable · SGSpecTable</span></h3><p>Lists as an engineering spec sheet: coded columns, row index, tabular figures, cell-run loads and the state language. The selected row carries the coral bar. Click a row.</p>
      <div class="demo" style="display:block">{spec_table(_FLEET[:4])}</div></div>
    <div class="inst"><h3><span>Form set</span><span>.xcheck .dradio .stepper</span></h3><p>Checkboxes are hard X boxes, radios are diamonds and steppers are cut keys. All of them come from the alphabet.</p>
      <div class="demo" style="display:grid;gap:12px;justify-items:start">
        <label class="optrow"><input class="xcheck" type="checkbox" id="pf-x1" checked>Kill switch</label>
        <label class="optrow"><input class="xcheck" type="checkbox" id="pf-x2">Allow local network</label>
        <div style="display:flex;gap:18px"><label class="optrow"><input class="dradio" type="radio" name="pf-r" id="pf-r1" checked>EU</label><label class="optrow"><input class="dradio" type="radio" name="pf-r" id="pf-r2">Asia</label><label class="optrow"><input class="dradio" type="radio" name="pf-r" id="pf-r3">Any</label></div>
        <div class="stepper" data-min="1" data-max="5"><button type="button" aria-label="Fewer hops">−</button><output id="pf-hops">3</output><button type="button" aria-label="More hops">+</button></div>
      </div></div>
    <div class="inst"><h3><span>Search and select</span><span>.search .selectf</span></h3><p>The search field leads with the scan reticle and a key hint. The select is a cut field with a solid caret. Both take the coral edge on focus.</p>
      <div class="demo" style="display:grid;gap:12px"><label class="search"><svg><use href="#g-i-scan"/></svg><input id="pf-s" placeholder="Search relays, units, logs"><kbd>⌘K</kbd></label>
        <label class="selectf"><select id="pf-sel"><option>WireGuard</option><option>IKEv2</option><option>Sealed relay</option></select></label></div></div>
    <div class="inst"><h3><span>Telex</span><span>.telex · SGTelex</span></h3><p>Notifications type themselves in like a teleprinter, with a state, the message and a timestamp. Faults take the coral edge.</p>
      <div class="demo" style="display:grid;gap:10px"><div class="telex-stack" id="pf-telex" data-telex-feed></div><button class="btn btn--sm" type="button" data-telex-send="pf-telex">Send telex</button></div></div>
    <div class="inst"><h3><span>Skeleton</span><span>.skel · SGSkeleton</span></h3><p>While data loads, blocks print as drafting hatch, sliding steadily rather than shimmering.</p>
      <div class="demo" style="display:grid;gap:10px"><i class="skel skel--t skel--run"></i><i class="skel skel--run"></i><i class="skel skel--run" style="width:80%"></i><i class="skel skel--b skel--run"></i></div></div>
  </div>
'''


def console():
    cur = ' aria-current="page"'
    rail = "".join(f'<a{cur if i == 1 else ""}><svg><use href="#g-i-{g}"/></svg><span>{n:02d}</span></a>' for i, (g, n) in enumerate([("home", 1), ("grid", 2), ("stats", 3), ("scan", 4), ("log", 5), ("me", 6)]))
    return f'''<section class="sec">
  <div class="sec-h"><span class="sg-num">07</span><h2 class="sg-display">Console</h2><span class="sg-mono">the same system beyond the phone · 1240 × 780 desktop layout · every part comes from the kit · point at data, click rows</span></div>
  <div class="con-wrap"><div class="con scr-like tex">
    <svg class="sg-bg" aria-hidden="true" viewBox="0 0 390 844" preserveAspectRatio="xMidYMid slice"><use href="#g-bg-pcb"/></svg>
    <nav class="con-rail"><svg class="con-mark" style="color:var(--coral)"><use href="#g-mark"/></svg>{rail}</nav>
    <header class="con-top">
      <span class="u-code" style="position:static">AX·CON</span>
      <h3 class="sg-display" style="margin:0;font-size:30px;color:var(--ground-hi)">Relay fleet</h3>
      <div class="u-span" style="margin:0;flex:1"><span>Sector 04 · <span class="live-coord">38.71 N 9.14 W</span></span><i></i><span>17 Nov 2026</span></div>
      <label class="search" style="width:260px"><svg><use href="#g-i-scan"/></svg><input id="con-s" placeholder="Search relays"><kbd>⌘K</kbd></label>
    </header>
    <section class="con-kpi">
      <div class="nframe"><b>Uptime</b>{seg7("99.82", 34)}</div>
      <div class="nframe"><b>Threats</b>{seg7("1284", 34, cls="live-up")}</div>
      <div class="nframe"><b>Relays</b><div class="sg-num" style="font-size:28px;color:var(--ground-hi)">4 / 6</div></div>
      <div class="nframe"><b>Rotation</b>{seg7("04:59", 34, "2", cls="live-down")}</div>
      <div class="smx"><div><b>System verified</b><span>Status – active</span></div><div><b>Protocol synced</b><span>Status – stable</span></div><div><b>Keys sealed</b><span>Status – online</span></div><div><b>Relay 02</b><span>Status – fault</span></div></div>
    </section>
    <section class="con-main"><div class="u-label" style="margin-bottom:10px"><span>Fleet</span><span>6 relays</span></div>{spec_table(_FLEET, selected=2)}
      <div class="u-label" style="margin:18px 0 10px"><span>Telex</span><span>live</span></div><div class="telex-stack" data-telex-feed></div></section>
    <aside class="con-side">
      <div class="u-label"><span>Selected · relay 03</span><span>LYON</span></div>
      <div class="chamfer brackets" style="padding:6px;--c:14px"><svg viewBox="0 0 300 280" style="width:100%;height:auto;overflow:visible">{relay_net(NET_CITIES, NET_ROUTES, hot=1)}</svg></div>
      <div class="spec spec--ground"><span>Protocol</span><i></i><span>WireGuard</span><span>Latency</span><i></i><span>212 ms</span><span>Hops</span><i></i><span>3</span></div>
      <label class="selectf"><select id="con-sel"><option>Reroute via Porto</option><option>Reroute via Seoul</option><option>Hold</option></select></label>
      <div style="display:flex;justify-content:space-between;align-items:center"><span class="optrow" style="cursor:default">Hops</span><div class="stepper" data-min="1" data-max="5"><button type="button" aria-label="Fewer hops">−</button><output id="con-hops">3</output><button type="button" aria-label="More hops">+</button></div></div>
      <label class="optrow"><input class="xcheck" type="checkbox" id="con-x1" checked>Kill switch on reroute</label>
      <button class="keycap" type="button" style="margin-top:auto"><span>Reroute</span><small>HOLD 1 S</small><i class="led"></i></button>
    </aside>
    <footer class="con-foot"><div class="u-foot" style="margin:0;border:0;padding:0"><div><b>Axiom signal systems</b><span>Console · build 2611 · eyes only</span></div><i class="barcode--v"></i></div>
      <div class="ticker" style="flex:1"><span>{" ◆ RELAY 04 · 23 MS · <b>AES-256</b> · 1,284 BLOCKED · RELAY 02 LOST · REROUTING VIA PORTO · " * 2}</span></div></footer>
  </div></div>
</section>
'''


FONTS_URL = ("https://fonts.googleapis.com/css2?family=Anybody:ital,wdth,wght@0,50..150,100..900;1,50..150,100..900"
             "&family=Saira+Stencil+One&family=IBM+Plex+Mono:wght@400;500&family=BIZ+UDGothic:wght@700&display=swap")


def seg7_tags(src):
    """<!--@SEG7|text|height|hot[|class]--> → inline seven-segment SVG."""
    return re.sub(r"<!--@SEG7\|([^|]*)\|(\d+)\|([^|>]*?)(?:\|([^>]*?))?-->",
                  lambda m: seg7(m.group(1), int(m.group(2)), m.group(3), cls=m.group(4) or ""), src)


def dtcg():
    """tokens/shingo.tokens.json in the W3C Design Tokens (DTCG) format, generated from tokens.json."""
    t = json.loads((ROOT / "tokens" / "tokens.json").read_text())
    col = t["color"]
    out = {"$description": "Shingō 信号 design tokens (W3C DTCG format). Generated by tools/build.py from tokens/tokens.json; do not edit.",
           "color": {mode: {k: {"$type": "color", "$value": v, "$description": col["roles"].get(k, "")}
                            for k, v in col[mode].items() if not k.startswith("$")} for mode in ("dark", "light")}}
    geo = t.get("geometry", {})
    dims = {k: v for k, v in geo.items() if isinstance(v, (int, float))}
    dims.update({f"cut-{k}": v for k, v in geo.get("cuts", {}).items() if isinstance(v, (int, float))})
    if dims:
        out["dimension"] = {k: {"$type": "dimension", "$value": f"{v}px"} for k, v in dims.items()}
    fam = {}
    for k, v in t.get("font", {}).items():
        if isinstance(v, dict) and "family" in v:
            fam[k] = {"$type": "fontFamily", "$value": v["family"], "$extensions": {"shingo": {x: v[x] for x in ("width", "weight", "ios", "case", "use") if x in v}}}
    if fam:
        out["fontFamily"] = fam
    (ROOT / "tokens" / "shingo.tokens.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")


def kit():
    """Standalone kit for other apps: dist/shingo.css, shingo-live.js, shingo-sprite.svg, starter.html."""
    d = ROOT / "dist"
    css = (ROOT / "web" / "shingo.css").read_text()
    (d / "shingo.css").write_text(f"/* Shingō kit · generated from web/shingo.css */\n@import url(\"{FONTS_URL}\");\n\n" + css)
    (d / "shingo-live.js").write_text((ROOT / "web" / "shingo-live.js").read_text())
    (d / "shingo-sprite.svg").write_text(sprite().replace(' width="0" height="0" style="position:absolute" aria-hidden="true"', "") + "\n")
    st = seg7_tags((ROOT / "templates" / "starter.src.html").read_text()).replace("<!--@SPRITE-->", sprite())
    (d / "starter.html").write_text(st)
    dtcg()
    print("kit: dist/shingo.css, shingo-live.js, shingo-sprite.svg, starter.html; tokens/shingo.tokens.json")


OLD_BG = ["tunnel", "slashes", "terrace", "stack-card", "stack-badge", "plates", "diamonds", "lattice", "bars", "notch", "wedge",
          "ticks", "pcb", "tiers", "decay", "relays", "columns", "airmail"]


def backdrops_gallery(src):
    """Backdrop index, with the screens that use each one (read from the built screens)."""
    use = {}
    for fig in re.findall(r"<figure data-tier=.*?</figure>", src, re.S):
        t = re.search(r"<figcaption><b>[A-Z] · ([^<]+)</b>", fig)
        for name in set(re.findall(r'class="sg-bg"[^>]*><use href="#g-bg-([a-z-]+)"', fig)):
            if t:
                use.setdefault(name, []).append(t.group(1))
    def tile(name, title, sub):
        u = ", ".join(use.get(name, [])) or "free"
        return (f'<div><figure class="tex"><svg viewBox="0 0 390 844" aria-hidden="true"><use href="#g-bg-{name}"/></svg></figure>'
                f'<b>{title}</b><span>{sub}</span><span>{u}</span></div>')
    mono = "".join(tile(n, t, s) for n, (t, s, _) in monoliths.MONOLITHS.items())
    old = "".join(tile(n, n.replace("-", " "), "") for n in OLD_BG if "g-bg-" + n in src or n in use)
    return (f'<div class="alpha-h" style="margin-top:30px"><span class="sg-cap">Monoliths</span><span class="sg-mono">{len(monoliths.MONOLITHS)} grand backdrops · one hard mass per screen · flat tonal ink · bleeds off every edge</span></div>\n'
            f'  <div class="bgs bgs--mono">{mono}</div>\n'
            f'  <div class="alpha-h" style="margin-top:30px"><span class="sg-cap">Line backdrops</span><span class="sg-mono">{len(OLD_BG)} fine compositions · for subjects that need them: audio, mail, circuits, editorial</span></div>\n'
            f'  <div class="bgs">{old}</div>')


def main():
    export_glyphs()
    defs = sprite().split("<defs>")[1].split("</defs>")[0]
    src = (ROOT / "web" / "gallery.src.html").read_text()
    src = seg7_tags(src)
    src = src.replace("<!--@EXPLORE-->", explorations() + "\n" + console())
    src = src.replace("<!--@PATTERNS-->", patterns())
    src = src.replace("<!--@BACKDROPS-->", backdrops_gallery(src))
    (ROOT / "ios" / "Sources" / "ShingoKit" / "SGMonolith.swift").write_text(monoliths.swift())
    src = src.replace("<!--@LIVEJS-->", (ROOT / "web" / "shingo-live.js").read_text())
    src = src.replace("<!--@CONSTRUCT-->", constructed("AXIOM", unit=10, x=2, y=2)[0] + constructed("AX-09", unit=4.2, x=2, y=72)[0])
    src = src.replace("<!--@XEXPL-->", exploded_x(100, 65, 52))
    src = src.replace("<!--@LANGUAGES-->", (ROOT / "web" / "partials" / "languages.html").read_text())
    src = src.replace("<!--@KEYART_DARK-->", keyart("dark")).replace("<!--@KEYART_LIGHT-->", keyart("light"))
    src = src.replace("<!--@SWATCHES-->", "".join(
        f'<div><i style="background:var(--{k})"></i><b>{k}</b><span>{v}<br>dark {PALETTE["dark"][k]} · light {PALETTE["light"][k]}</span></div>'
        for k, v in ROLES.items()))
    # gallery chrome decodes as it scrolls into view (web/shingo-live.js)
    src = re.sub(r'class="(sec-h|alpha-h|inst)(\b[^"]*)"', r'class="\1\2" data-decode-view', src)
    css = (ROOT / "web" / "shingo.css").read_text()
    out = (src.replace("<!--@CSS-->", css).replace("<!--@SPRITE-->", sprite()))
    (ROOT / "dist").mkdir(exist_ok=True)
    (ROOT / "dist" / "index.html").write_text(out)
    print("built dist/index.html", len(out) // 1024, "KB;", len(G), "glyphs")
    kit()
    sys.path.insert(0, str(ROOT / "tools"))
    import check_tokens
    check_tokens.main()


if __name__ == "__main__":
    main()
