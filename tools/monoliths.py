"""Monoliths: the grand backdrops.

Single, oversized hard masses that bleed off the screen: slabs, blast doors,
girders, pylons, a giant X, a giant readout. Quiet flat ink only (ground-2 solid
and half-tone, ground knock-outs), level, upright or "/" edges (the X and chevrons are
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


def zones():
    # heart-rate zones at building scale: five plates run in from the right edge, each a different
    # length, each led by a "/" cut; the longest (the zone you lived in) prints solid
    o = []
    for k, (L, role) in enumerate([(150, "g2"), (250, "g3"), (330, "g3"), (230, "g2"), (120, "g2")]):
        y, h = 560 + k * 52, 36
        x0 = 410 - L
        o.append((role, [(x0 + h, y), (420, y), (420, y + h), (x0, y + h)]))
    return o


def diamond_mark():
    return [("g3", [diamond(390, 560, 330), diamond(390, 560, 196)]), ("g2", diamond(390, 560, 92))]


def girder():
    o = [("g2", band(-150 + k * 110, 680, 180, 32)) for k in range(7)]
    o += [("g3", [(-20, 466), (410, 466), (410, 500), (-20, 500)]),
          ("g3", [(-20, 680), (410, 680), (410, 714), (-20, 714)])]
    o += [("g", [(x, 479), (x + 8, 479), (x + 8, 487), (x, 487)]) for x in range(12, 390, 40)]
    return o


def aperture():
    # a bunker wall with one cut window over the hero
    outer = [(-20, -20), (410, -20), (410, 864), (-20, 864)]
    return [("g3", [outer, chamf(36, 128, 354, 560, 64)]), ("g2", [(36, 560), (354, 560), (354, 590), (36, 590)])]


def segment():
    # a giant Shingo Grid 4 (sector 04, the system's recurring unit): stem and bar solid, the 45° diagonal in half-tone
    st, bt, top, bar = 120, 120, 150, 470          # stroke, bar thickness, cap top, bar bottom
    T = st * 2 ** .5
    bar_top = bar - bt
    rise = bar_top - top                           # the diagonal climbs from the bar to the cap line
    x_left = 40
    stem_r = x_left + rise + T
    return [("g3", [(stem_r - st, top), (stem_r, top), (stem_r, 900), (stem_r - st, 900)]),
            ("g3", [(x_left, bar_top), (stem_r + 70, bar_top), (stem_r + 70, bar), (x_left, bar)]),
            ("g2", [(x_left, bar_top), (x_left + T, bar_top), (x_left + T + rise, top), (x_left + rise, top)])]


def massing():
    return [("g2", chamf(-30, 520, 260, 900, 60)), ("g3", chamf(140, 300, 430, 640, 50)), ("g2", chamf(260, 70, 430, 290, 40))]


def ramp():
    return [("g2", [(-20, 900), (420, 460), (420, 900)]), ("g3", band(-60, 830, 480, 26))]


def pylon():
    o = [("g3", [(262, 200), (412, 50), (412, 900), (262, 900)]),
         ("g2", [(210, 358), (238, 330), (238, 900), (210, 900)])]
    # vents sit high on the tower, above where content usually runs
    o += [("g", [(338, y), (412, y), (412, y + 8), (338, y + 8)]) for y in (150, 170, 190)]
    return o


def dam():
    # a gravity dam: a "/" face, a crest, and the spillway as a half-tone channel down the face
    return [("g3", [(180, 360), (420, 360), (420, 900), (-20, 900), (-20, 560)]),
            ("g2", band(-20, 620, 200, 36))]


def hangar():
    # a wall with a tall door opening, the door in three half-tone leaves
    o = [("g3", [[(-20, 300), (410, 300), (410, 900), (-20, 900)], [(110, 420), (320, 420), (320, 900), (70, 900), (70, 460)]])]
    o += [("g2", [(x, 480), (x + 64, 480), (x + 64, 900), (x, 900)]) for x in (88, 166, 244)]
    return o


def switchback():
    # stair flights that all rise "/", joined by level landings
    return [("g3", band(-80, 860, 300, 46)), ("g3", [(220, 560), (420, 560), (420, 604), (220, 604)]),
            ("g2", band(-40, 470, 280, 46)), ("g2", [(-20, 470), (60, 470), (60, 514), (-20, 514)])]


def tag():
    # the print's slab tag at building scale: one cut, one punched hole
    return [("g3", [(-20, 430), (330, 430), (330, 690), (240, 780), (-20, 780)]),
            ("g", [(282, 462), (304, 462), (304, 484), (282, 484)]),
            ("g2", [(-20, 800), (210, 800), (210, 818), (-20, 818)])]


def nested_bar():
    # the hero form, enlarged past the frame: plate, slot, core
    return [("g3", chamf(-40, 540, 440, 740, 80)), ("g", [(40, 628), (360, 628), (360, 652), (40, 652)]),
            ("g2", [(40, 628), (190, 628), (190, 652), (40, 652)])]


def cells():
    # a cell meter at building scale: four filled, three in half-tone
    return [("g3" if k < 4 else "g2", band(-210 + k * 96, 880, 300, 58)) for k in range(7)]


def brackets():
    # the HUD corners, as walls
    return [("g3", [(-20, 96), (220, 96), (220, 146), (30, 146), (30, 420), (-20, 420)]),
            ("g3", [(410, 860), (170, 860), (170, 810), (360, 810), (360, 536), (410, 536)])]


def silo():
    # three columns with "/" cut heads
    def col(x, w, top, role):
        return (role, [(x, top + w), (x + w, top), (x + w, 900), (x, 900)])
    return [col(14, 92, 440, "g2"), col(124, 92, 320, "g3"), col(234, 176, 190, "g3")]


def shutter():
    # a roller shutter, half down
    o = [("g3", [(-20, 440), (410, 440), (410, 480), (60, 480), (20, 440)])]
    o += [("g2", [(-20, y), (410, y), (410, y + 26), (-20, y + 26)]) for y in range(500, 880, 38)]
    return o


def notch_plate():
    # a notch frame as a mass: half-tone plate, solid label tab with a "/" end
    return [("g2", [(-20, 330), (420, 330), (420, 900), (-20, 900)]),
            ("g3", [(-20, 282), (222, 282), (174, 330), (-20, 330)])]


MONOLITHS = {
    "monolith": ("Monolith", "a split slab", monolith),
    "bulkhead": ("Bulkhead", "blast doors on a / seam", bulkhead),
    "giant-x": ("Giant X", "the mark at building scale", giant_x),
    "chevrons": ("Chevrons", "three advancing masses", chevrons),
    "zones": ("Zones", "five plates, one per heart-rate zone", zones),
    "diamond": ("Diamond", "the mark, cropped", diamond_mark),
    "girder": ("Girder", "a truss of / members", girder),
    "aperture": ("Aperture", "a wall with one window", aperture),
    "segment": ("Segment", "a giant Shingo Grid 4", segment),
    "massing": ("Massing", "three cut blocks", massing),
    "ramp": ("Ramp", "a / incline", ramp),
    "pylon": ("Pylon", "a vented tower", pylon),
    "dam": ("Dam", "a / face and a spillway", dam),
    "hangar": ("Hangar", "a wall and a tall door", hangar),
    "switchback": ("Switchback", "flights that all rise /", switchback),
    "tag": ("Tag", "the slab tag, punched", tag),
    "nested-bar": ("Nested bar", "the hero form, enlarged", nested_bar),
    "cells": ("Cells", "a meter at building scale", cells),
    "brackets": ("Brackets", "HUD corners as walls", brackets),
    "silo": ("Silo", "three cut columns", silo),
    "shutter": ("Shutter", "a roller door, half down", shutter),
    "notch-plate": ("Notch plate", "a notch frame as a mass", notch_plate),
}

# Quiet inks. A monolith is the stripe filled in solid: the main mass ("g3" in the data)
# prints in ground-2, the stripe's own highlight; secondary parts ("g2") in a half-tone of it;
# knock-outs ("g") in the ground. No ground-3, so the mass sits under the content, not on it.
ROLE_CSS = {"g3": 'fill="var(--ground-2)"', "g2": 'fill="var(--ground-2)" fill-opacity=".5"', "g": 'fill="var(--ground)"'}
ROLE_SWIFT = {"g3": "SG.ground2", "g2": "SG.ground2.opacity(0.5)", "g": "SG.ground"}


def _f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def rings(pts):
    """A shape is one ring of points, or a list of rings (the later rings are holes)."""
    return pts if isinstance(pts[0], list) else [pts]


def svg(name):
    out = []
    for r, pts in MONOLITHS[name][2]():
        d = " ".join("M" + " L".join(f"{_f(x)} {_f(y)}" for x, y in ring) + " Z" for ring in rings(pts))
        out.append(f'<path d="{d}" fill-rule="evenodd" {ROLE_CSS[r]}/>')
    return "".join(out)


def swift():
    cases = [n.replace("-", "_") for n in MONOLITHS]
    camel = ["".join([w if i == 0 else w.capitalize() for i, w in enumerate(n.split("-"))]) for n in MONOLITHS]
    out = ["// GENERATED by tools/build.py from tools/monoliths.py: do not edit.",
           "import SwiftUI", "",
           "// MARK: - Monoliths",
           "//",
           "// The grand backdrops: one oversized hard mass per screen, bleeding off the edges.",
           "// Quiet flat ink (ground-2, solid and half-tone) with ground knock-outs; same geometry as the",
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
           "    static let shapes: [SGMonolithKind: [(Color, [[CGPoint]])]] = ["]
    for n, c in zip(MONOLITHS, camel):
        polys = []
        for r, pts in MONOLITHS[n][2]():
            rs = ", ".join("[" + ", ".join(f"CGPoint(x: {_f(x)}, y: {_f(y)})" for x, y in ring) + "]" for ring in rings(pts))
            polys.append(f"            ({ROLE_SWIFT[r]}, [{rs}])")
        out.append(f"        .{c}: [\n" + ",\n".join(polys) + "\n        ],")
    out += ["    ]", "",
            "    public var body: some View {",
            "        Canvas { ctx, size in",
            "            let k = size.width / 390",
            "            ctx.scaleBy(x: k, y: k)",
            "            for (color, rings) in Self.shapes[kind] ?? [] {",
            "                let path = Path { p in for r in rings { p.addLines(r); p.closeSubpath() } }",
            "                ctx.fill(path, with: .color(color), style: FillStyle(eoFill: true))   // later rings are holes",
            "            }",
            "        }",
            "        .allowsHitTesting(false)",
            "        .accessibilityHidden(true)",
            "    }",
            "}", ""]
    return "\n".join(out)
