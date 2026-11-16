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
import math, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Colours are CSS variables so the same SVG renders in light and dark mode
# (the page resolves them). Exports resolve them to literal hex per mode.
C = dict(ink="var(--ink)", sage="var(--sage)", hi="var(--sage-hi)", lo="var(--sage-lo)",
         line="var(--sage-line)", ghost="var(--sage-ghost)", coral="var(--coral)",
         oninc="var(--on-ground)", ghi="var(--ground-hi)", ground="var(--ground)", ground2="var(--ground-2)")
PALETTE = {
    "dark":  {"ground": "#0b0b0a", "ground-2": "#1b1c18", "ground-3": "#2e2f2a", "on-ground": "#c9ccc2", "ground-hi": "#dcdfd5", "ground-dim": "#8b8d85",
              "sage": "#b8bbb0", "sage-hi": "#c9ccc2", "sage-lo": "#a9aca1", "sage-line": "#8e9089", "sage-ghost": "#cdd0c7",
              "ink": "#0c0c0a", "ink-dim": "#4d4f49", "coral": "#ff715e", "coral-deep": "#e65b48"},
    "light": {"ground": "#bcbfb4", "ground-2": "#b0b3a8", "ground-3": "#9fa297", "on-ground": "#1c1d19", "ground-hi": "#0f100d", "ground-dim": "#4d4f47",
              "sage": "#e3e5dd", "sage-hi": "#eceee7", "sage-lo": "#d2d4cb", "sage-line": "#72746b", "sage-ghost": "#f7f8f4",
              "ink": "#10110e", "ink-dim": "#5a5c54", "coral": "#ff715e", "coral-deep": "#e65b48"},
}
ROLES = {"ground": "striped background", "ground-2": "stripe highlight", "ground-3": "rules, frames, tracks",
         "on-ground": "body text on the ground", "ground-hi": "the print: titles, line art, plates of text", "ground-dim": "secondary print",
         "sage": "plates, outer bar", "sage-hi": "plates you press or carry", "sage-lo": "pressed plates", "sage-line": "hairlines on plates",
         "sage-ghost": "faint marks on plates", "ink": "text on plates, solid objects", "ink-dim": "secondary text on plates",
         "coral": "the signal", "coral-deep": "pressed signal"}


def resolve(svg, mode):
    """Replace var(--x) with the literal colour for one mode (for standalone files)."""
    fonts = {"f-display": "Archivo, 'Archivo Expanded', sans-serif", "f-sans": "Archivo, sans-serif",
             "f-mono": "'JetBrains Mono', monospace", "f-jp": "'Hiragino Sans', 'Noto Sans JP', sans-serif"}
    return re.sub(r"var\(--([a-z0-9-]+)\)", lambda m: PALETTE[mode].get(m.group(1)) or fonts[m.group(1)], svg)


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- geometry
def x_path(h=14.0, L=30.0, c=50.0):
    """Outline of two crossed stadiums (the poster's rounded X).
    h = half arm width, L = centre-to-cap-centre distance. 100x100 box."""
    s = h * math.sqrt(2)
    r2 = math.sqrt(0.5)

    def rot(p, k):  # rotate k*90deg clockwise (y down)
        x, y = p
        for _ in range(k):
            x, y = -y, x
        return x, y
    # NE arm, local coords around 0,0
    d = (r2, -r2); n = (r2, r2)
    a1 = (L * d[0] - h * n[0], L * d[1] - h * n[1])
    a2 = (L * d[0] + h * n[0], L * d[1] + h * n[1])
    inner_top, inner_right = (0, -s), (s, 0)
    pts = []
    for k in range(4):
        pts.append((rot(inner_top, k), rot(a1, k), rot(a2, k)))
    d_ = f"M{f(c+pts[0][0][0])} {f(c+pts[0][0][1])}"
    for (it, p1, p2) in pts:
        d_ += f" L{f(c+p1[0])} {f(c+p1[1])} A{f(h)} {f(h)} 0 0 1 {f(c+p2[0])} {f(c+p2[1])}"
        d_ += f" L{f(c+rot(inner_right, pts.index((it,p1,p2)))[0])} {f(c+rot(inner_right, pts.index((it,p1,p2)))[1])}"
    return d_ + " Z"


def rrect(x, y, w, h, r):
    return (f"M{f(x+r)} {f(y)} H{f(x+w-r)} A{f(r)} {f(r)} 0 0 1 {f(x+w)} {f(y+r)} V{f(y+h-r)} "
            f"A{f(r)} {f(r)} 0 0 1 {f(x+w-r)} {f(y+h)} H{f(x+r)} A{f(r)} {f(r)} 0 0 1 {f(x)} {f(y+h-r)} "
            f"V{f(y+r)} A{f(r)} {f(r)} 0 0 1 {f(x+r)} {f(y)} Z")


def blob(cx, cy, r, seed, amp=0.07, n=72):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        rr = r * (1 + amp * math.sin(3 * t + seed) + amp * .6 * math.sin(5 * t + seed * 1.7) + amp * .3 * math.sin(8 * t + seed * .3))
        pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t)))
    return "M" + " L".join(f"{f(x)} {f(y)}" for x, y in pts) + " Z"


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


def _segs(w=36, h=64, t=7, g=1.6):
    def hseg(x0, x1, yc):
        return [(x0, yc), (x0 + t / 2, yc - t / 2), (x1 - t / 2, yc - t / 2), (x1, yc), (x1 - t / 2, yc + t / 2), (x0 + t / 2, yc + t / 2)]
    def vseg(xc, y0, y1):
        return [(xc, y0), (xc + t / 2, y0 + t / 2), (xc + t / 2, y1 - t / 2), (xc, y1), (xc - t / 2, y1 - t / 2), (xc - t / 2, y0 + t / 2)]
    x0, x1, m = t / 2 + g, w - t / 2 - g, h / 2
    return {"a": hseg(x0, x1, t / 2), "g": hseg(x0, x1, m), "d": hseg(x0, x1, h - t / 2),
            "f": vseg(t / 2, t / 2 + g, m - g), "b": vseg(w - t / 2, t / 2 + g, m - g),
            "e": vseg(t / 2, m + g, h - t / 2 - g), "c": vseg(w - t / 2, m + g, h - t / 2 - g)}


def seg7(text, height=48, hot="", ghost=True, cls=""):
    """Inline SVG seven-segment readout. Characters in `hot` (indexes) light coral.
    Unlit segments draw in --off unless ghost=False. Supports 0-9 - . : and a few letters."""
    w, h, gap = 36, 64, 8
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
    W = x - gap + 10
    return (f'<svg class="seg7 {cls}" viewBox="0 0 {W} {h}" height="{height}" width="{f(height * W / h)}" role="img" aria-label="{text}">'
            f'<g transform="translate(9 0) skewX(-8)">{"".join(parts)}</g></svg>')


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


XP = x_path(12.5, 32)   # rounded X: origins poster only
XS = x_sharp()          # sharp X: the interface

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
G["globe"] = ("0 0 100 64", '<g fill="none" stroke="currentColor" stroke-width="3.2"><ellipse cx="50" cy="32" rx="46" ry="28"/><ellipse cx="50" cy="32" rx="24" ry="28"/><ellipse cx="50" cy="32" rx="8" ry="28"/><path d="M4 32H96M9 18H91M9 46H91"/></g>')
G["rings"] = ("0 0 240 120", '<g fill="none" stroke="currentColor" stroke-width="1.3">' + "".join(f'<circle cx="{60+i*8}" cy="60" r="56"/>' for i in range(16)) + "</g>")
G["disc"] = ("0 0 100 100", '<g fill="none" stroke="currentColor" stroke-width=".9">' + "".join(f'<circle cx="50" cy="50" r="{r}"/>' for r in range(14, 49, 3)) + '</g><circle cx="50" cy="50" r="3" fill="currentColor"/>')
G["bars"] = ("0 0 100 100", '<g fill="currentColor"><rect x="12" y="20" width="76" height="8" rx="4"/><rect x="12" y="46" width="52" height="8" rx="4"/><rect x="12" y="72" width="64" height="8" rx="4"/></g>')
G["play"] = ("0 0 100 100", '<path d="M30 18 L84 50 L30 82Z" fill="currentColor" stroke="currentColor" stroke-width="8" stroke-linejoin="round"/>')
G["skip"] = ("0 0 100 100", '<path d="M18 22 L58 50 L18 78Z M50 22 L90 50 L50 78Z" fill="currentColor"/>')
G["chev"] = ("0 0 100 100", '<path d="M36 18 L68 50 L36 82" fill="none" stroke="currentColor" stroke-width="11"/>')
G["user"] = ("0 0 100 100", '<circle cx="50" cy="32" r="18" fill="currentColor"/><path d="M14 90 A36 30 0 0 1 86 90 Z" fill="currentColor"/>')
# --- motifs from the trilingual print reference ---
G["head"] = ("0 0 100 100", '<g fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M32 94 C32 82 27 76 26 66 C17 54 17 30 33 18 C47 7 70 11 76 29 C79 37 79 43 83 50 L78 54 C80 58 78 62 76 64 C74 70 68 73 62 73 L62 94"/>'
    '<path d="M40 15 C47 29 47 39 44 47"/><path d="M44 47 C51 44 54 55 46 57"/><path d="M26 66 C36 64 44 60 46 57"/></g>')
_chev = []
for _ay, _d1 in zip([18, 82, 146, 210], [70, 150, 40, 112]):
    _chev.append(f'<path d="M-30 {_ay+180} L150 {_ay} L330 {_ay+180}" fill="none" stroke="currentColor" stroke-width="26" stroke-linejoin="miter" stroke-dasharray="{_d1} 16 9999"/>')
_chev.append('<path d="M0 0 H62 L0 62Z" fill="currentColor"/><path d="M300 0 V44 L256 0Z" fill="currentColor"/>')
G["chevrons"] = ("0 0 300 230", "".join(_chev))
G["warn"] = ("0 0 100 100", '<path fill-rule="evenodd" fill="currentColor" d="M50 6 L96 90 H4 Z M44 34 H56 V64 H44 Z M44 70 H56 V80 H44 Z"/>')
G["reg"] = ("0 0 100 100", '<path d="M50 4V96 M4 50H96" stroke="currentColor" stroke-width="4"/><path d="M26 26H74V74H26Z" fill="none" stroke="currentColor" stroke-width="4"/><path d="M40 40H60V60H40Z" fill="currentColor"/>')
G["matrix"] = ("0 0 21 21", f'<g fill="currentColor">{_matrix()}</g>')
G["wave"] = ("0 0 240 60", '<polyline fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="miter" points="0,30 20,30 26,8 34,52 42,8 50,52 56,30 90,30 96,18 102,42 108,30 140,30 146,4 154,56 162,4 170,56 176,30 210,30 216,22 222,38 228,30 240,30"/>')
G["slash"] = ("0 0 100 100", '<path d="M20 80 L80 20" stroke="currentColor" stroke-width="3"/>')

topo = [f'<circle cx="50" cy="50" r="47" fill="none" stroke="{C["ink"]}" stroke-width="1.4"/>',
        f'<circle cx="50" cy="50" r="43" fill="none" stroke="{C["ink"]}" stroke-width=".7"/>']
for i, r in enumerate([36, 31, 26, 21, 16]):
    topo.append(f'<path d="{blob(52 + i*.6, 51 + i*.4, r, i*1.3)}" fill="none" stroke="{C["ink"]}" stroke-width=".8" opacity=".75"/>')
topo.append(f'<path d="{blob(53, 52, 10.5, 2.2, .14)}" fill="{C["coral"]}"/>')
topo.append(f'<path d="{rrect(49,47,5,5,1.6)}" fill="{C["ink"]}" transform="rotate(45 51.5 49.5)"/>')
G["topo"] = ("0 0 100 100", "".join(topo))

fan = [f'<path d="M50 50 L{f(50+40*math.cos(math.radians(-8)))} {f(50+40*math.sin(math.radians(-8)))} A40 40 0 1 1 {f(50+40*math.cos(math.radians(-62)))} {f(50+40*math.sin(math.radians(-62)))} Z" fill="{C["hi"]}"/>']
for a in range(150, 262, 5):
    t = math.radians(a)
    fan.append(f'<path d="M50 50 L{f(50+40*math.cos(t))} {f(50+40*math.sin(t))}" stroke="{C["line"]}" stroke-width=".9"/>')
fan.append(f'<path d="M50 44 L58 92 L53 92 L50 62 L47 92 L42 92Z" fill="{C["ink"]}"/>')
G["radar-fan"] = ("0 0 100 100", "".join(fan))


def sprite():
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="position:absolute" aria-hidden="true"><defs>']
    for k, (vb, inner) in G.items():
        out.append(f'<symbol id="g-{k}" viewBox="{vb}">{inner}</symbol>')
    # worn screen-print: knocks pinholes out of whatever it is applied to (CSS filter:url(#wear))
    out.append('<filter id="wear" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.95" numOctaves="2" seed="7" result="n"/>'
               '<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -3.4 0 0 0 2.6" result="m"/>'
               '<feComposite in="SourceGraphic" in2="m" operator="in"/></filter>')
    out.append("</defs></svg>")
    return "".join(out)


def export_glyphs():
    d = ROOT / "assets" / "svg"
    d.mkdir(parents=True, exist_ok=True)
    for k, (vb, inner) in G.items():
        w, h = vb.split()[2:]
        body = inner.replace("currentColor", "var(--ink)")
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}">{body}</svg>\n'
        if "var(--" in inner:  # multi-colour glyph: one file per appearance
            (d / f"{k}-dark.svg").write_text(resolve(svg, "dark"))
            (d / f"{k}-light.svg").write_text(resolve(svg, "light"))
        else:                  # single colour: use as a template image, tint in code
            (d / f"{k}.svg").write_text(resolve(svg, "dark"))


# ---------------------------------------------------------------- poster
def use(gid, x, y, w, h=None, color=None, extra=""):
    h = w if h is None else h
    st = f' style="color:{color}"' if color else ""
    return f'<use href="#g-{gid}" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"{st} {extra}/>'


def poster(sfx="d"):
    W, H = 1333, 2000
    o = [f'<svg class="poster" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Poster study rebuilt from Shingō primitives">']
    o.append(f'''<defs>
<linearGradient id="pgr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--ground)"/><stop offset=".5" stop-color="var(--ground-2)"/><stop offset="1" stop-color="var(--ground)"/></linearGradient>
{''.join(f'<pattern id="pst{i}" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate({a})"><rect width="14" height="14" fill="url(#pgr)"/></pattern>' for i, a in enumerate([-36, -18, -58, -47]))}
<clipPath id="pc-l"><rect x="32" y="0" width="1400" height="2000"/></clipPath>
<clipPath id="pc-r"><rect x="0" y="0" width="1300" height="2000"/></clipPath>
<clipPath id="pc-rdark"><rect x="960" y="372" width="340" height="150"/></clipPath>
<clipPath id="pc-rcoral"><polygon points="915,522 1300,135 1300,522"/></clipPath>
<clipPath id="pc-rsage"><rect x="960" y="522" width="340" height="96"/></clipPath>
<clipPath id="pc-xsolid"><path transform="translate(900 1119) scale(1.9)" d="{XP}"/></clipPath>
<clipPath id="pc-x2"><rect x="1060" y="270" width="240" height="200"/></clipPath>
</defs>''')
    o.append(f'<style>svg.poster .pw{{font-family:var(--f-display);font-stretch:125%;font-weight:900}} svg.poster .ps{{font-family:var(--f-sans);font-weight:500;letter-spacing:-.04em}} svg.poster .pm{{font-family:var(--f-mono);font-size:19.5px}} svg.poster .pn{{font-family:var(--f-display);font-weight:700;font-stretch:105%}}</style>')
    # ground + facets
    o.append(f'<rect width="{W}" height="{H}" fill="url(#pst0)"/>')
    o.append('<polygon points="0,0 1333,0 1333,40 0,560" fill="url(#pst1)"/>')
    o.append('<polygon points="0,880 230,690 600,860 32,1420 0,1440" fill="url(#pst2)"/>')
    o.append('<polygon points="760,0 1333,0 1333,120 930,520 820,330" fill="url(#pst3)"/>')
    # coral band + sage ground
    o.append(f'<polygon points="32,1400 582,850 750,850 32,1495" fill="{C["coral"]}"/>')
    o.append(f'<polygon points="725,860 1300,860 1300,1965 32,1965 32,1495" fill="{C["sage"]}"/>')
    # coral wedge top right, solid X behind rings
    o.append(f'<polygon points="915,522 1300,135 1300,522" fill="{C["coral"]}"/>')
    o.append(f'<g clip-path="url(#pc-x2)"><path transform="translate(1072 272) scale(2)" d="{XP}" fill="{C["hi"]}"/></g>')
    # rings coil across three zones
    def coil(stroke, clip):
        return f'<g clip-path="url(#{clip})" fill="none" stroke="{stroke}" stroke-width="2.2">' + "".join(f'<circle cx="{1110+i*11}" cy="497" r="118"/>' for i in range(22)) + "</g>"
    o.append(coil(C["coral"], "pc-rdark"))
    o.append(coil(C["line"], "pc-rcoral"))
    # pill 1 (bleeds left)
    o.append(f'''<g clip-path="url(#pc-l)">
<rect x="-200" y="125" width="922" height="350" rx="175" fill="{C["sage"]}"/>
<rect x="-200" y="187" width="860" height="226" rx="113" fill="{C["hi"]}"/>
<rect x="-200" y="275" width="775" height="50" rx="25" fill="{C["sage"]}"/>
<rect x="-200" y="295.5" width="753" height="9" rx="4.5" fill="{C["ink"]}"/></g>''')
    o.append(f'<circle cx="107" cy="233" r="3" fill="{C["line"]}"/>')
    # pill 2 (bleeds right)
    o.append(f'''<g clip-path="url(#pc-r)">
<rect x="205" y="522" width="1300" height="350" rx="175" fill="{C["sage"]}"/>
<rect x="268" y="585" width="1200" height="224" rx="112" fill="{C["hi"]}"/>
<rect x="355" y="652" width="650" height="90" rx="45" fill="{C["sage"]}"/>
<rect x="375" y="692.5" width="555" height="9" rx="4.5" fill="{C["ink"]}"/>
<rect x="740" y="692.5" width="190" height="9" rx="4.5" fill="{C["coral"]}"/></g>''')
    o.append(coil(C["line"], "pc-rsage"))
    o.append(f'<circle cx="627" cy="633" r="3" fill="{C["line"]}"/><circle cx="1007" cy="633" r="3" fill="{C["line"]}"/>')
    # right column
    o.append(f'<rect x="1165" y="698" width="135" height="1267" fill="{C["sage"]}"/><rect x="1165" y="668" width="135" height="30" fill="{C["ink"]}"/>')
    o.append(use("topo", 1180, 722, 106))
    o.append(f'<rect x="1165" y="846" width="135" height="5" fill="{C["ink"]}"/><rect x="1165" y="860" width="135" height="2.5" fill="{C["ink"]}"/>')
    y, bars = 876, [2,2,2,6,2,2,2,2,5,2,2,2,2,2,2,6,2,2,2,2,2,2,2,2]
    for i, t in enumerate(bars):
        o.append(f'<rect x="1165" y="{y}" width="135" height="{t}" fill="{C["ink"]}"/>'); y += t + (4 if i % 5 else 9)
    # frames
    o.append(f'<polygon points="935,220 1130,220 1150,262 1150,697 1015,697 935,615" fill="none" stroke="{C["line"]}" stroke-width="2.6"/>')
    o.append(f'<polygon points="788,657 937,657 975,697 742,928 625,928 572,873" fill="none" stroke="{C["line"]}" stroke-width="2.6"/>')
    # X family
    o.append(f'<path transform="translate(1072 58) scale(2)" d="{XP}" fill="none" stroke="{C["ghi"]}" stroke-width="13" stroke-linejoin="round"/>')
    o.append(f'<path transform="translate(900 900) scale(1.9)" d="{XP}" fill="none" stroke="{C["hi"]}" stroke-width="11" stroke-linejoin="round"/>')
    o.append(f'<path transform="translate(683 1119) scale(1.9)" d="{XP}" fill="none" stroke="{C["ink"]}" stroke-width="7.5" stroke-linejoin="round"/>')
    o.append(f'<path transform="translate(900 1119) scale(1.9)" d="{XP}" fill="{C["ink"]}"/>')
    o.append(f'<path d="M925 1283 L1062 1146" stroke="{C["line"]}" stroke-width="1.6"/>')
    # glyphs
    o.append(use("mark", 60, 62, 46, color=C["coral"]) + use("mark", 803, 763, 46, color=C["coral"]))
    o.append(use("globe", 62, 586, 60, 38, color=C["oninc"]))
    o.append(use("plus", 877, 474, 26, color=C["oninc"]) + use("plus", 975, 725, 26, color=C["line"]))
    o.append(use("arrow", 846, 1010, 26, color=C["coral"]) + use("arrow", 1236, 533, 26, color=C["coral"]))
    o.append(f'<g transform="rotate(90 1097 598)">{use("arrow", 1084, 585, 26, color=C["ink"])}</g>')
    o.append(f'<g transform="rotate(-90 1141 1849)">{use("arrow", 1128, 1836, 26, color=C["line"])}</g>')
    # badges bottom right
    o.append(f'<circle cx="1233" cy="1681" r="47" fill="{C["hi"]}" stroke="{C["coral"]}" stroke-width="10"/>' + use("disc", 1203, 1651, 60, color=C["ink"]))
    o.append(f'<rect x="1165" y="1741" width="135" height="224" fill="{C["coral"]}"/>' + use("radar-fan", 1172, 1745, 120))
    o.append(f'<rect x="1183" y="1932" width="100" height="3" fill="{C["lo"]}"/><rect x="1183" y="1942" width="100" height="3" fill="{C["lo"]}"/>')
    o.append(f'<path d="M888 1465 H1155" stroke="{C["line"]}" stroke-width="2"/><rect x="1124" y="1465" width="31" height="9" fill="{C["line"]}"/>')
    # type
    T = lambda x, y, s, cls, fill, anchor="start", size=None: f'<text x="{x}" y="{y}" class="{cls}" fill="{fill}" text-anchor="{anchor}"' + (f' font-size="{size}"' if size else "") + f'>{s}</text>'
    o.append(T(128, 100, "AXIOM", "pw", C["ghi"], size=36) + T(320, 96, "signal systems", "ps", C["oninc"], size=20) + T(495, 96, "2019–2026", "ps", C["oninc"], size=20))
    o.append(T(62, 535, "200 ppi", "ps", C["oninc"], size=20) + T(62, 562, "1890 x 2835 px", "ps", C["oninc"], size=20))
    o.append(T(1270, 476, "09", "pn", C["ink"], "end", 31) + T(1270, 501, "#bab9ad", "ps", C["ink"], "end", 18))
    o.append(T(1157, 805, "AXIOM", "pw", C["ink"], "end", 52))
    mono = [(830, "signal"), (852, "integrity"), (1012, "ref:"), (1032, "opsec/AHI"), (1052, "sp c53"),
            (1165, "Field telemetry"), (1187, "response program"), (1229, "(FTRP)"),
            (1755, "COMSEC  monitoring,"), (1777, "network operations"), (1799, "and defense")]
    for yy, s in mono:
        o.append(T(1155, yy, s, "pm", C["ink"], "end"))
    o.append(f'<g clip-path="url(#pc-xsolid)">' + "".join(T(1155, yy, s, "pm", C["line"], "end") for yy, s in mono[5:7]) + "</g>")
    o.append(T(1155, 917, "09", "pn", C["ink"], "end", 22) + T(1155, 1455, "09", "pn", C["ink"], "end", 22))
    o.append(T(398, 1755, "#ff715e", "ps", C["ink"], size=18))
    for yy, s in [(1892, "2019 - 2026"), (1914, "Interface study · Shingō"), (1936, "Screen collection entry No. 09")]:
        o.append(T(1155, yy, s, "pm", C["ghost"], "end"))
    o.append("</svg>")
    out = "".join(o)
    # unique ids per instance: patterns and clips resolve colours where they are defined
    out = re.sub(r'id="(pgr|pst\d|pc-[a-z0-9]+)"', lambda m: f'id="{m.group(1)}-{sfx}"', out)
    out = re.sub(r'url\(#(pgr|pst\d|pc-[a-z0-9]+)\)', lambda m: f'url(#{m.group(1)}-{sfx})', out)
    return out


def keyart(mode):
    """Key art: the shirt's print stack + the poster's instrument column, in HTML."""
    return f'''<figure class="mode-{mode}"><div class="ka tex"><div class="ka-in">
      <div class="ka-mast"><span class="u-code">SK·09·LIS</span><span class="sg-display wear">AXIOM</span></div>
      <div class="slab-cut ka-slab wear"></div><div class="ka-head brackets"><svg><use href="#g-head"/></svg></div>
      <div class="yearspan sg-num ka-year">20<i></i>26</div>
      <div class="ka-trio"><div class="sg-label">Signal engineering</div><div class="sg-jp sg-justify">信号工学</div><div class="sg-label">Ingénierie du signal</div></div>
      <div class="ka-side"><div><div class="sg-num">09</div><div class="sg-mono">#bab9ad</div></div>
        <svg viewBox="0 0 100 100"><use href="#g-x-line"/></svg><svg viewBox="0 0 100 100"><use href="#g-x-solid"/></svg>
        <i class="barcode"></i><div class="sg-mono">REF:<br>OPSEC/AHI<br>SP C53</div></div>
      <div class="ka-chev"><svg class="wear" viewBox="0 0 300 230"><use href="#g-chevrons"/></svg></div>
      <div class="hazard ka-haz wear"></div>
      <div class="ka-foot"><div><div class="sg-label">Axiom signal systems</div><div class="sg-mono">COMSEC MONITORING · NETWORK OPERATIONS AND DEFENSE</div></div><i class="barcode--v"></i></div>
    </div></div><figcaption class="cap"><b>Key art · {mode}</b><span>{"bone print on ink stripes" if mode == "dark" else "ink print on sage stripes"}</span></figcaption></figure>'''


def main():
    export_glyphs()
    defs = sprite().split("<defs>")[1].split("</defs>")[0]
    for mode in ("dark", "light"):
        svg = poster(mode[0]).replace("<defs>", "<defs>" + defs, 1)
        (ROOT / "assets" / "svg" / f"poster-{mode}.svg").write_text(resolve(svg, mode) + "\n")
    src = (ROOT / "web" / "gallery.src.html").read_text()
    src = re.sub(r"<!--@SEG7\|([^|]*)\|(\d+)\|([^>]*?)-->", lambda m: seg7(m.group(1), int(m.group(2)), m.group(3)), src)
    src = src.replace("<!--@LANGUAGES-->", (ROOT / "web" / "partials" / "languages.html").read_text())
    src = src.replace("<!--@KEYART_DARK-->", keyart("dark")).replace("<!--@KEYART_LIGHT-->", keyart("light"))
    src = src.replace("<!--@SWATCHES-->", "".join(
        f'<div><i style="background:var(--{k})"></i><b>{k}</b><span>{v}<br>dark {PALETTE["dark"][k]} · light {PALETTE["light"][k]}</span></div>'
        for k, v in ROLES.items()))
    css = (ROOT / "web" / "shingo.css").read_text()
    out = (src.replace("<!--@CSS-->", css).replace("<!--@SPRITE-->", sprite())
              .replace("<!--@POSTER_DARK-->", poster("d")).replace("<!--@POSTER_LIGHT-->", poster("l")))
    (ROOT / "dist").mkdir(exist_ok=True)
    (ROOT / "dist" / "index.html").write_text(out)
    print("built dist/index.html", len(out) // 1024, "KB;", len(G), "glyphs")


if __name__ == "__main__":
    main()
