# Signal Kit

A UI kit that rebuilds the sage, coral and stripe poster style in code, for the web and for SwiftUI.

![poster study](docs/poster.png)

## Why this isn't built on `open-design/brutalist-skill`

That skill (`nexu-io/open-design/skills/brutalist-skill/SKILL.md`) is a 9 KB text prompt. It has no assets, components or code, and three of its rules contradict this poster:

| Skill says | Poster does |
|---|---|
| "Absolute rejection of border-radius" | Built on stadium pills, circles and rounded X marks |
| One substrate per project, "never mix light and dark" | Sage slabs on an ink stripe ground on every screen |
| Accent `#E61919` hazard red | Accent `#ff715e` coral, on a sage `#bab9ad` palette |

It is useful for tone: mono telemetry, technical framing, barcodes and crosshairs. It can't reproduce this look, so this kit was built from scratch with measurements taken from the reference image.

## What's here

```
tokens/tokens.json            colours, type, geometry ratios, usage rules
web/signal.css                tokens + components (.pill .btn .tgl .seg .chamfer .slot .barcode .tex)
web/gallery.src.html          gallery source: poster study, 13 screens, widgets, component sheet
tools/build.py                generates glyphs + poster SVG, exports assets, builds dist/
tools/screenshot.js           renders every screen to PNG with the preinstalled Playwright
dist/index.html               the built, self-contained gallery (open in a browser)
assets/svg/*.svg              16 vector glyphs + poster-study.svg, ready for Xcode asset catalogs
ios/                          Swift package "SignalKit" (iOS 17+)
  Sources/SignalKit/SignalTheme.swift       SG colour tokens, SGFont, font registration
  Sources/SignalKit/SignalShapes.swift      RoundedX, DiamondMark, ChamferRect, UnitPolygon, Crosshair, ArrowNE
  Sources/SignalKit/SignalTextures.swift    StripeField (Canvas), Barcode, RingsCoil, RecordDisc, RadarScope
  Sources/SignalKit/SignalComponents.swift  NestedPill, SignalButtonStyle, SignalToggleStyle, SignalSegmented, SignalChip, SignalRule, SignalSlot, SignalTabBar
  Sources/SignalKit/Examples/               LaunchExample + DashboardExample with #Previews
  Sources/SignalKit/Resources/Fonts/        Archivo + JetBrains Mono TTFs (SIL OFL)
docs/                         screenshots of every screen
```

## Build the gallery

```bash
python3 tools/build.py
```

```bash
node tools/screenshot.js docs
```

## Use in an iOS app

1. In Xcode, go to File › Add Package Dependencies › Add Local… and pick the `ios/` folder.
2. Register the fonts once at launch:
   ```swift
   import SignalKit
   @main struct MyApp: App {
       init() { SGFont.register() }
       var body: some Scene { WindowGroup { DashboardExample() } }
   }
   ```
3. Build screens from the parts:
   ```swift
   ZStack {
       StripeField()
       NestedPill(height: 124, bleed: .leading, progress: 0.8)
       RoundedX().stroke(SG.sageHi, style: .init(lineWidth: 7, lineJoin: .round))
   }
   Button("Disconnect") {}.buttonStyle(SignalButtonStyle(.coral))
   Toggle("Kill switch", isOn: $on).toggleStyle(SignalToggleStyle())
   ```
4. For static art, drag `assets/svg/*.svg` into an asset catalog and tick **Preserve Vector Data**. Single-colour glyphs can be set to render as template images.

> The Swift sources were written against the iOS 17 SwiftUI API but have **not been compiled yet**. The build environment had no Swift toolchain. Expect a few small fixes on the first Xcode build.

## Web → SwiftUI map

| Web | SwiftUI | Notes |
|---|---|---|
| `.tex`, `.facet` | `StripeField(angle:facets:)` | 6 pt soft stripes, facets are clipped polygons |
| `.pill` (+ `--bleed-l/r`) | `NestedPill(height:bleed:progress:)` | band 18%, core 15%, slot 3% of height |
| `#g-x-line` / `#g-x-solid` | `RoundedX()` stroke / fill | halfWidth 12.5, armLength 32 |
| `#g-mark` | `DiamondMark()` with `eoFill` | brand mark with a hole |
| `.chamfer` | `.chamferFrame()` / `ChamferRect` | cut 16 |
| `.slab`, `.band` | `UnitPolygon([...]).fill(...)` | the diagonal split |
| `.btn--*` | `SignalButtonStyle(.ink/.coral/.sage/.ghost)` | 52 pt capsule |
| `.tgl` | `SignalToggleStyle()` | |
| `.seg` | `SignalSegmented` | |
| `.slot`, `.rule`, `.barcode` | `SignalSlot`, `SignalRule`, `Barcode` | |

## Fonts

Archivo (Omnibus-Type) and JetBrains Mono (JetBrains) are both licensed under the SIL Open Font License 1.1. You may bundle them in an app.
