"""Monoliths: the grand backdrops.

Single, oversized hard masses that bleed off the screen: slabs, blast doors,
girders, pylons, a giant X, a giant readout. Flat ink only (ground-2 / ground-3
fills, ground knock-outs), level, upright or "/" edges (the X and chevrons are
the alphabet's own exceptions), no outlines, no layering beyond one mass and
its cuts. Drawn on the 390 x 844 phone reference and bled past it.

Each monolith is a list of (role, [points]) polygons, so the web symbols
(tools/build.py) and the SwiftUI view (ios/.../SGMonolith.swift) are generated
from the same data. Roles: g2 / g3 = tonal ink, g = knock-out to the ground.
"""
import math

R2 = math.sqrt(0.5)


def band(x, y, L, w):
    """A "/" band: bottom-left at (x, y), horizontal thickness w, rising L."""
    return [(x, y), (x + w, y), (x + w + L, y - L), (x + L, y - L)]


def chamf(x0, y0, x1, y1, c):
    """Plate with the system cuts: top-left and bottom-right."""
    return [(x0 + c, y0), (x1, y0), (x1, y1 - c), (x1 - c, y1), (x0, y1), (x0, y0 + c)]


def xbar(cx, cy, L, h, rising=True):
    """One bar of the hard X: square-cut ends, half-length L, half-width h."""
    d = (R2, -R2) if rising else (R2, R2)
    n = (R2, R2) if rising else (-R2, R2)
    return [(cx + sa * d[0] * L + sb * n[0] * h, cy + sa * d[1] * L + sb * n[1] * h)
            for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def diamond(cx, cy, s):
    return [(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)]


SEGS = None   # set by tools/build.py to its seven-segment geometry (_segs)


def _seg_digit(segs, k, ox, oy):
    S = SEGS()
    return [[(ox + x * k, oy + y * k) for x, y in S[s]] for s in segs]


def monolith():
    return [("g3", [(150, 250), (330, 250), (330, 900), (-30, 900), (-30, 430)]),
            ("g", band(-30, 760, 326, 34)),
            ("g2", [(346, 120), (420, 120), (420, 900), (346, 900)])]


def bulkhead():
    # two blast doors meeting on a "/" seam, locked by one bar
    return [("g2", [(-20, -20), (410, -20), (410, 460), (6, 864), (-20, 864)]),
            ("g3", [(410, 520), (410, 864), (66, 864)]),
            ("g3", [(-20, 560), (310, 560), (270, 600), (-20, 600)]),
            ("g3", [(370, 560), (410, 560), (410, 600), (330, 600)])]


def giant_x():
    return [("g3", xbar(300, 610, 470, 56, True)), ("g3", xbar(300, 610, 470, 56, False))]


def chevrons():
    o = []
    for k, role in enumerate(("g2", "g2", "g3")):
        ax, t, a = 120 + k * 112, 62, 270
        o.append((role, [(ax - a, 600 - a), (ax - a + t, 600 - a), (ax + t, 600), (ax - a + t, 600 + a), (ax - a, 600 + a), (ax, 600)]))
    return o


def ziggurat():
    def steps(x, y, run, top):
        pts = [(x, 900)]
        while y > top:
            pts += [(x, y), (x + run, y)]
            x += run; y -= run
        pts += [(x, y), (430, y), (430, 900)]
        return pts
    return [("g2", steps(-20, 760, 72, 300)), ("g3", steps(-20, 880, 72, 560))]


def diamond_mark():
    return [("g2", diamond(390, 560, 330)), ("g", diamond(390, 560, 196)), ("g3", diamond(390, 560, 92))]


def girder():
    o = [("g2", band(-150 + k * 110, 680, 180, 32)) for k in range(7)]
    o += [("g3", [(-20, 466), (410, 466), (410, 500), (-20, 500)]),
          ("g3", [(-20, 680), (410, 680), (410, 714), (-20, 714)])]
    o += [("g", [(x, 479), (x + 8, 479), (x + 8, 487), (x, 487)]) for x in range(12, 390, 40)]
    return o


def aperture():
    # a bunker wall with one cut window over the hero
    outer = [(-20, -20), (410, -20), (410, 864), (-20, 864)]
    return [("g2", outer), ("g", chamf(36, 128, 354, 560, 64)), ("g3", [(36, 560), (290, 560), (354, 560), (354, 590), (36, 590)])]


def segment():
    # a giant seven-segment 4: sector 04, the system's recurring unit
    k = 8.4
    return [("g3" if s == "g" else "g2", p) for s, p in zip("fgbc", _seg_digit("fgbc", k, 22, 236))]


def massing():
    return [("g2", chamf(-30, 520, 260, 900, 60)), ("g3", chamf(140, 300, 430, 640, 50)), ("g2", chamf(260, 70, 430, 290, 40))]


def ramp():
    return [("g2", [(-20, 900), (420, 460), (420, 900)]), ("g3", band(-60, 830, 480, 26))]


def pylon():
    o = [("g3", [(262, 200), (412, 50), (412, 900), (262, 900)]),
         ("g2", [(210, 358), (238, 330), (238, 900), (210, 900)])]
    o += [("g", [(282, y), (412, y), (412, y + 10), (282, y + 10)]) for y in range(640, 720, 26)]
    return o


MONOLITHS = {
    "monolith": ("Monolith", "a split slab", monolith),
    "bulkhead": ("Bulkhead", "blast doors on a / seam", bulkhead),
    "giant-x": ("Giant X", "the mark at building scale", giant_x),
    "chevrons": ("Chevrons", "three advancing masses", chevrons),
    "ziggurat": ("Ziggurat", "stepped mass rising /", ziggurat),
    "diamond": ("Diamond", "the mark, cropped", diamond_mark),
    "girder": ("Girder", "a truss of / members", girder),
    "aperture": ("Aperture", "a wall with one window", aperture),
    "segment": ("Segment", "a giant readout 4", segment),
    "massing": ("Massing", "three cut blocks", massing),
    "ramp": ("Ramp", "a / incline", ramp),
    "pylon": ("Pylon", "a vented tower", pylon),
}

ROLE_CSS = {"g2": "var(--ground-2)", "g3": "var(--ground-3)", "g": "var(--ground)"}
ROLE_SWIFT = {"g2": "SG.ground2", "g3": "SG.ground3", "g": "SG.ground"}


def _f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def svg(name):
    return "".join(f'<polygon points="{" ".join(f"{_f(x)},{_f(y)}" for x, y in pts)}" fill="{ROLE_CSS[r]}"/>'
                   for r, pts in MONOLITHS[name][2]())


def swift():
    cases = [n.replace("-", "_") for n in MONOLITHS]
    camel = ["".join([w if i == 0 else w.capitalize() for i, w in enumerate(n.split("-"))]) for n in MONOLITHS]
    out = ["// GENERATED by tools/build.py from tools/monoliths.py: do not edit.",
           "import SwiftUI", "",
           "// MARK: - Monoliths",
           "//",
           "// The grand backdrops: one oversized hard mass per screen, bleeding off the edges.",
           "// Flat tonal ink (ground-2 / ground-3) with ground knock-outs; same geometry as the",
           "// gallery's bg-* monolith symbols, on the 390 x 844 reference, scaled to the width.",
           "//",
           "//     SGUtilityScreen(...) { ... } content: { ... }",
           "//         .background(SGMonolith(.bulkhead).ignoresSafeArea())", "",
           "public enum SGMonolithKind: String, CaseIterable {",
           "    case " + ", ".join(camel), "}", "",
           "public struct SGMonolith: View {",
           "    var kind: SGMonolithKind",
           "    public init(_ kind: SGMonolithKind) { self.kind = kind }",
           "",
           "    static let shapes: [SGMonolithKind: [(Color, [CGPoint])]] = ["]
    for n, c in zip(MONOLITHS, camel):
        polys = []
        for r, pts in MONOLITHS[n][2]():
            p = ", ".join(f"CGPoint(x: {_f(x)}, y: {_f(y)})" for x, y in pts)
            polys.append(f"            ({ROLE_SWIFT[r]}, [{p}])")
        out.append(f"        .{c}: [\n" + ",\n".join(polys) + "\n        ],")
    out += ["    ]", "",
            "    public var body: some View {",
            "        Canvas { ctx, size in",
            "            let k = size.width / 390",
            "            ctx.scaleBy(x: k, y: k)",
            "            for (color, pts) in Self.shapes[kind] ?? [] {",
            "                ctx.fill(Path { p in p.addLines(pts); p.closeSubpath() }, with: .color(color))",
            "            }",
            "        }",
            "        .allowsHitTesting(false)",
            "        .accessibilityHidden(true)",
            "    }",
            "}", ""]
    return "\n".join(out)
