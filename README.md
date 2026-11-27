# Shingō 信号

*Shingō* is Japanese for "signal". It's an industrial interface system for iOS and the web. Interfaces are **printed** on a striped ground, like a two-ink screen print: wide hard type, one 45° diagonal, hazard stripes, chevrons, big hard figures, stencil serials and mono telemetry, with one coral signal per screen. English leads, with Japanese and French as accents. Every screen ships in light and dark.

![key art in both modes](docs/keyart.png)

Open `dist/index.html` in a browser for the full gallery: key art, the shape alphabet, content motifs, backdrops, 28 iPhone screens, widgets, components, instruments, the poster series, motion studies, patterns for any app, a desktop console and language rules. Use the switch in the corner to flip modes.

## Art direction

One spec. Everything in the repo follows it, and anything new must too.

**Color**
1. **Two inks.** Print on ground, nothing else. Solid shapes (keys, cards, badges, tickets, bars, plates) are print ink with the text knocked out. There is no third tone.
2. **One signal.** Coral is the only extra ink: one block or one primary action per screen, plus the latest or active state. Switches turn on in print. Coral used as text takes `--signal-text`, a deeper coral on sage so small type stays legible. Inside a print plate (tickets, data plates, `[data-plate]`) the ground flips, so it takes `--signal-plate` instead; those plates set it for you. Coral never draws guides, dashed outlines, frames or annotations: construction marks and notes print in the dim ink (`--ground-dim`), and warnings are framed in print with a hazard spine.

   **Multi-series telemetry (optional extension).** When a dense telemetry panel must distinguish 2–4 simultaneous series in one meter or readout group (volumes, channels, multi-band load), Shingō adds four matte industrial inks harmonized to Shingo Coral (`#ff715e`): **Jade** (`--series-1`, split-complement of coral), **Cerulean** (`--series-2`, cool architectural counterpoint), **Marigold** (`--series-3`, warm ochre sibling) and **Iris** (`--series-4`, spaced fourth hue). On dark ground (`#0b0b0a` / `#000000`), all four sit at matched perceptual lightness (OKLCH L ≈ 0.72–0.83) with warm-balanced matte chroma so they read cleanly without neon clash or competing with coral; on light sage ground (`#bcbfb4`), each steps down to an ink-matched print density (OKLCH L ≈ 0.42–0.44, ≈ 4.45:1 contrast, matching `--signal-text` `#8f2b1c`). Use them only for multi-series telemetry bars and 5×5 square legend pips (`.cells-split` + `.pip-legend` / `SGSplitCellMeter`) — never for UI chrome. Coral remains strictly reserved for alerts, thresholds and the single primary signal; when a series crosses a threshold, tint only its readout text in `--signal-text` while keeping its bar and pip distinct. System states still rely on shapes and position, never colour alone.

**Shape**

3. **One angle, one direction.** Every diagonal rises left to right at 45°. Corner cuts sit top-left and bottom-right at 6, 12 or 24 pt. Nothing is tilted, textured, shadowed or rounded; device chrome is the only exception.
4. **The alphabet.** Twelve primitives make everything: cut plate, tag, nested bar (a solid bar with a slot), slash, hazard, notch frame, hard X, diamond, chevrons, brackets, cell run and wedge.
5. **Content motifs.** Where a screen has a subject, its shape comes from that subject, drawn by the same rules: lock tumblers, postage stamp, DIP switches, wind barbs, packet flow, cut fingerprint, compass rose, level meters and security microtext.
6. **Icons.** One family on a 24-unit grid with 2-unit strokes, square caps and miter joins.

**Type**

7. **Wide, short, hard.** One face of our own sets everything that is not body text or telemetry. **Shingo Grid** is a cut-plate grotesque: the square, wide-shouldered skeleton Orbitron made familiar, with the system's own corners. Wherever a stroke turns a corner a round letter would curve through, the corner is cut at 45° the way every plate is cut: top-left and bottom-right only, so every cut in a line of type rises left to right. The other two corners, and every terminal, stay square. Diagonals run at 45° and end level on a short upright facet; B, 3 and 8 take a sawtooth waist (the same cut, the same direction); and the rule survives a half turn, so 6/9, b/q, d/p, n/u and M/W are each other rotated. It comes in three weights from one set of drawings, and a stencil:
   - **Heavy** (stems a quarter of the cap height) sets display 40+, screen titles 32 and big figures.
   - **Bold** sets subheads and inline wordmarks.
   - **Medium** sets labels, buttons, chips and tabs, in caps, tracked out as they get small.
   - **Stencil** is the Heavy, bridged, for serials and stamps (once per screen). Every bridge is a slit on the same diagonal. The two corners the plate rule leaves square, top-right and bottom-left, are exactly the two a mitre can open "/", so where the plate is not cut the stencil opens it.

   Letters are about a tenth wider than tall, the cap height is 0.7 em, and bars are a shade lighter than stems so three-bar letters stay open. Body text is Anybody, telemetry IBM Plex Mono and kanji BIZ UDGothic (Hiragino Sans on iOS). Nothing prints below 10 pt (tab labels 11 pt). Big numbers are Shingo Grid figures: proportional by default, tabular (`tnum`, `.sg-num--tab`) for columns, and readouts that tick give each digit a fixed cell. Never condensed, never rounded.

![Shingo Grid Heavy: the wordmark, the S on its construction guides and the specimen column](docs/dark/masthead.png)

**Layout**

8. **Two tiers.** Poster screens (launch, onboarding, lock screen, empty state, relay city, live activity) compose freely. Every other screen follows the grammar: masthead (micro-code, title, one tag, span rule) → one hero → divider → body → imprint footer (rule, wide-caps line, mono reference, barcode).
9. **Dividers by kind.** Hazard for system and safety screens, a tick ruler for data, a slash run for money and content.
10. **One backdrop per screen: a quiet monument.** Behind the content sits one oversized hard mass that bleeds off the edges: a **monolith**. It prints only in the stripe's own tone: the mass is the stripe filled in solid (ground-2), secondary parts in its half-tone, openings are real holes that show the stripes, and small cuts knock out to the ground. It should be felt before it is seen. No outlines, no ground-3, no layering beyond the mass and its cuts. Chosen by subject from 22: monolith, bulkhead, giant X, chevrons, zones, diamond, girder, aperture, segment, massing, ramp, pylon, dam, hangar, switchback, tag, nested bar, cells, brackets, silo, shutter and notch plate. The finer line compositions (tunnel, circuit traces, relays and the rest) survive only as heroes and insets, such as the dashboard tunnel and the briefing's traces, never as a screen backdrop. The same monoliths sit behind the console and the starter page.

**Imagery and motion**

11. **No pictorial scenes.** There is no photography and no illustrated or generated cities. Imagery comes from the shape system itself: backdrops, motifs and diagrams such as the relay network.
12. **Slides glide, states step.** Nothing is ever eased. Anything that travels sideways (tickers, marching hazard and hatch, the wipe band) moves continuously at an even, linear speed. Changes of state (blinks, cell fills, pulses, the radar sweep, text decode) step. Everything stays still when reduced motion is on.
13. **Live behaviour.** The interface behaves like a machine:
    - Information decodes from glyph noise. Each character locks in at its own random moment, the flicker is irregular, and no two decodes take the same time. Noise keeps each character's class (digits flicker through digits, capitals through hard capitals, kanji through kanji); punctuation and spaces never scramble, so the structure of a line holds while it resolves.
    - Decoding has three triggers. **Arrival:** a screen or section decodes top to bottom in three weights: titles (0.32–0.72 s), then labels, codes, column heads and buttons (0.16–0.38 s), then data such as span rules, spec values, table figures, states and imprint lines (0.2–0.52 s), staggered 18 ms apart. **Change:** a new value decodes (stepper, selected row, telex timestamp, HUD callout). **Touch:** buttons, keys, tabs and chips re-decode their label under the pointer (0.12–0.26 s).
    - Paragraphs, inputs, tickers, telex messages (they type instead) and figure readouts never decode.
    - Figure readouts re-render in place: timers count, counters climb, coordinates drift. Live readouts give each digit a fixed cell, so nothing jumps; static ones set on the figures' own widths.
    - Views change behind a hazard band that slides across on the diagonal at an even speed.
    - A HUD reticle snaps coral brackets and a callout to data under the pointer (on iOS, press and hold).
    - Tickers, marching hazard bars, busy states and loading hatch slide smoothly and loop without a seam.

    On iOS each shape has a feel: a hard tick for switches and tabs, a double tick for keycaps, a heavy throw for the rocker, rising steps for cell meters, an error pattern for alerts and a success pattern for sealed. Web: `web/shingo-live.js`. iOS: `SGLive.swift` (`SGHaptics`, `SGScrambleText`, `SGLiveCountdown`, `.sgHazardWipe`, `.sgHUD`).

**Language**

14. **English runs the interface.** Japanese (a vertical tag or a seal) and French (the span rule or fine print) appear at most once each per screen. All three stack only once per app, on the lock screen.

**Patterns**

15. **States have shapes.** Every system state has one fixed mark, in every app: nominal is a solid square, caution is hatched, fault is a coral X, offline is a dim X and syncing is a marching hatch. Never signal state by colour alone.
16. **Data is a spec sheet.** Lists are spec tables: coded columns (C-01…), a row index, tabular figures and the coral bar on the selected row. Form controls come from the alphabet: checkboxes are hard X boxes, radios are diamonds and steppers are cut keys.
17. **The machine reports.** Notifications type in like a telex (state, message, timestamp; faults take a coral edge). Loading prints as drafting hatch that slides steadily, never a shimmer or a spinner.
18. **Beyond the phone.** Larger screens keep the grammar and add a rail: masthead across the top, readouts as the hero, the spec table as the body, a side panel for the selection, and the imprint plus ticker as the footer (see the Console section of the gallery).

**Print furniture**

19. **Every sheet is a technical print.** Around the content sits the furniture of a printed spec sheet: crosshairs pinning frames and rules, vertical spec rails, word-spaced microtext, a coordinate stack in the display face, version stamps, the coral mark tile, data callouts, a specimen column and the giant glyph construction on grid paper. Furniture prints in the print or dim ink; coral only fills the mark tile and at most one stamp per view. Poster screens and the gallery use it freely; utility screens carry it on the imprint rule and in heroes. Generators: `tools/print_kit.py`; SwiftUI: `SGPrint.swift`.

**Impressions**

20. **One ink, four impressions.** The print ink lands four ways. **Solid** is the default. Display type 40 pt and up, and figure readouts, may also print **screened** (`.imp-screen`: the 45° drafting hatch, a tint made the way print makes one), as a **keyline** (`.imp-keyline`: a hairline round the letter and nothing inside) or in the stripe's own **tone** (`.imp-tone`: ground-3, felt before it is read). The key art stacks the wordmark in the first three. A screen takes at most one line that is not solid, and uses it to mean something: the empty state prints the missing SIGNAL as a keyline. Anything that must be read at a glance, and all body text, labels and controls, stays solid. SwiftUI: `SGDisplayText(_:size:impression:)`.

| dashboard | interval timer | transfer | device |
|---|---|---|---|
| ![](docs/dark/screen-c.png) | ![](docs/dark/screen-r.png) | ![](docs/dark/screen-s.png) | ![](docs/light/screen-q.png) |

![instruments](docs/dark/instruments.png)

![patterns](docs/light/patterns.png)

![console](docs/dark/console.png)

## Light and dark

| | ground (striped) | print | plates | signal |
|---|---|---|---|---|
| **Dark** | ink `#0b0b0a` | bone `#dcdfd5` | bone, text knocked out | coral `#ff715e` (text `#ff715e`) |
| **Light** | sage `#bcbfb4` | ink `#0f100d` | ink, text knocked out | coral `#ff715e` (text `#8f2b1c`) |

Multi-series telemetry inks (opt-in, harmonized to coral `#ff715e`):

| token | hue | dark (`#0b0b0a`) | light (`#bcbfb4`) | relationship to coral |
|---|---|---|---|---|
| `--series-1` / `SG.series1` | **Jade** | `#5cd6a0` | `#15593e` | split-complement |
| `--series-2` / `SG.series2` | **Cerulean** | `#5ba8ff` | `#184e8e` | cool architectural counterpoint |
| `--series-3` / `SG.series3` | **Marigold** | `#f2c14e` | `#694808` | warm ochre sibling |
| `--series-4` / `SG.series4` | **Iris** | `#b388ff` | `#5b3a9b` | spaced fourth hue |

Use role tokens, never raw hex. Things printed on the ground use `--ground-*`: `--ground-hi` is the print and `--ground-dim` is secondary print. Things on plates use `--sage-*` and `--ink`. Force a mode on any web subtree with `.mode-light` or `.mode-dark`. On iOS, every `SG` colour is dynamic and follows the system appearance or `.preferredColorScheme`.

| dark | light |
|---|---|
| ![](docs/dark/screen-c.png) | ![](docs/light/screen-c.png) |
| ![](docs/dark/screen-j.png) | ![](docs/light/screen-j.png) |

## What's here

```
tokens/tokens.json            colours (both modes), type, geometry, screen grammar, rules
tokens/lexicon.json           EN / 日本語 / FR phrase list with readings
web/shingo.css                tokens + components + screen grammar (.u-*)
web/shingo-live.js            live layer: scramble, live readouts, hazard wipe, HUD reticle, telex, steppers, table rows
templates/starter.src.html    a complete app page built only from the kit (source of dist/starter.html)
web/gallery.src.html          gallery source
web/partials/languages.html   the language section
tools/screens.py              regenerates the gallery screens from the grammar
tools/font.py                 draws Shingo Grid (Heavy, Bold, Medium and the Stencil) from one set of drawings: unions of bars and 45° strokes with the plate cuts taken out; TTF for iOS, WOFF2 for the web
web/fonts/                    ShingoGrid-Heavy, -Bold, -Medium, -Stencil (WOFF2)
tools/print_kit.py            print furniture generators: crosshairs, rails, spaced microtext, coords, stamps, callouts
tools/posters.py              the second poster series (XP·07–12)
tools/monoliths.py            the monolith backdrops as polygon data (web symbols and SwiftUI are generated from it)
tools/build.py                glyphs, motifs, backdrops, key art, posters; builds dist/
tools/check_tokens.py         fails the build if tokens.json, shingo.css and SGTheme.swift disagree
tools/screenshot.js           renders every screen in both modes (preinstalled Playwright)
dist/index.html               the built, self-contained gallery
dist/shingo.css               the kit stylesheet for other apps (Shingo Grid from dist/fonts/, the rest from Google Fonts)
dist/fonts/                   the Shingo Grid WOFF2 files
dist/shingo-live.js           the live layer, standalone
dist/shingo-sprite.svg        every glyph, icon, motif and backdrop as <symbol id="g-…">
dist/starter.html             the starter page, built (open it next to shingo.css)
tokens/shingo.tokens.json     the colour, dimension and font tokens in W3C DTCG format (generated)
skills/shingo/SKILL.md        instructions for an AI agent applying Shingō to a new app
CLAUDE.md                     repo conventions for agents working in this repo
assets/svg/*.svg              glyphs and icons (multi-colour ones as -dark/-light pairs)
ios/                          Swift package "ShingoKit" (iOS 17+), all colours dynamic
  Sources/ShingoKit/SGTheme.swift       SG colour tokens, SGFont, SGFace (the title face's metrics), font registration
  Sources/ShingoKit/SGImpression.swift  SGDisplayText: display type solid, screened, keyline or tone; SGScreenFill, SGKeyline
  Sources/ShingoKit/SGShapes.swift      SGHardX, DiamondMark, ChamferRect, TagCut, Brackets, UnitPolygon, SignalBars
  Sources/ShingoKit/SGTextures.swift    StripeField, Barcode, Spectrum, Scope
  Sources/ShingoKit/SGComponents.swift  SGBar, SGButtonStyle, SGToggleStyle, SGSegmented, SGChip, SGSlot, SGGroupLabel, SGTabBar
  Sources/ShingoKit/SGBackdrop.swift     SGBackdrop: eleven of the line backdrops
  Sources/ShingoKit/SGMonolith.swift     SGMonolith: all 22 monoliths (generated, do not edit)
  Sources/ShingoKit/SGLive.swift        SGHaptics, SGScrambleText, SGLiveCountdown, sgHazardWipe transition, sgHUD readout
  Sources/ShingoKit/SGScreen.swift      SGUtilityScreen, SGCode: the screen grammar
  Sources/ShingoKit/SGInstruments.swift  SGSegDisplay, SGCellMeter, SGSplitCellMeter, SGSeriesPip, SGRuler, SGSteps, SGIndexTabs, SGCaution, SGStamp, SGTicket, SGKeycapStyle, SGRockerStyle, SGDataPlate, SGSpecRow, SGMatrixCode, .printMarks(), SGColorBar, SGTicker, SGBootLog, SGLamps, SGBlueprint, SGCallout, SGWave
  Sources/ShingoKit/SGPatterns.swift    SGState, SGSpecTable, SGXCheckboxStyle, SGDiamondRadio, SGStepper, SGSearchField, SGTelex, SGSkeleton
  Sources/ShingoKit/SGLanguage.swift    VerticalText, Hanko, HazardBar, ChevronStack, YearSpan, ManifestoExample
  Sources/ShingoKit/Examples/           LaunchExample, DashboardExample, IntervalExample with light/dark #Previews
  Sources/ShingoKit/Resources/Fonts/    Shingo Grid (4 cuts, MIT); Anybody (3 widths + italic) and IBM Plex Mono (SIL OFL)
docs/                         screenshots of every screen in docs/dark and docs/light
```

## Build the gallery

```bash
python3 tools/screens.py
```

```bash
python3 tools/build.py
```

```bash
node tools/screenshot.js docs
```

`build.py` also writes the standalone kit in `dist/`, regenerates `tokens/shingo.tokens.json` and runs the token check. `npm run build` does all of it in one go.

## Apply Shingō to another app

The repo is built to be lifted into anything. Pick the route that fits.

**A web app**

1. Copy `dist/shingo.css`, `dist/fonts/`, `dist/shingo-live.js` and `dist/shingo-sprite.svg` into the app, keeping `fonts/` next to the stylesheet. Anybody, Plex Mono and BIZ UDGothic come from Google Fonts; self-host them if you need to.
2. Inline the sprite once at the top of `<body>` (or fetch it and inject it), then use any glyph with `<svg><use href="#g-i-scan"/></svg>`.
3. Put `class="tex"` on the page or app root for the striped ground, and `data-sg-live` on any region that should get the live layer (decode, readouts, HUD, wipe). Phone screens use `.scr`, desktop consoles `.con`. `data-decode-view` decodes any other element when it scrolls into view, `data-decode-change` decodes a value whenever its text changes, and `data-no-decode` opts a node out.
4. Start from `dist/starter.html`: a masthead, readout hero, hazard divider, spec table, telex feed, form set and imprint, in both modes, responsive down to 390 px.
5. Script hooks: `window.shingo.telex(stack, state, message, time)`, `window.shingo.wipe(el, fn)`, `window.shingo.scramble(region)` (the arrival decode), `window.shingo.decode(el, 'title'|'label'|'data'|'touch')` and `window.shingo.decodeOnChange(el)`. States are `ok`, `warn`, `fault`, `off` and `busy`.

**Another design tool or platform**

Import `tokens/shingo.tokens.json` (W3C DTCG) into Figma Tokens/Tokens Studio, Style Dictionary or similar. `tokens/tokens.json` has the full spec beyond colour: type scale, geometry, grammar, motion and rules.

**An iOS app**

Add `ios/` as a local Swift package (see below). Every web pattern has a SwiftUI counterpart in the map.

**An AI agent**

Point the agent at `skills/shingo/SKILL.md`. It holds the rules in checklist form, the component vocabulary and the review steps.

**Make it yours**

- **Brand.** The examples use the placeholder brand AXIOM (marks `AX·09`, "Axiom signal systems"). Replace the name, the masthead codes and the imprint line. Keep the format: a short code, a wide-caps line and a mono reference.
- **Signal colour.** Coral is the one extra ink. To rebrand it, change `--coral`, `--coral-deep`, `--signal-text` and `--signal-plate` in `tokens/tokens.json`, `web/shingo.css` and `SGTheme.swift`, then run the build; the token check fails until all three agree. Keep it a single warm, saturated ink that reads on both grounds.
- **Content.** Pick a backdrop, a divider and (if the subject has one) a motif for each screen from the lists in the rules. Write English first, then add at most one Japanese and one French accent per screen from `tokens/lexicon.json`.

**Checklist for any new screen**

- [ ] Works in light and dark (`data-theme`, `.mode-light` / `.mode-dark`, or SwiftUI appearance).
- [ ] One coral block or primary action; coral text uses `--signal-text`.
- [ ] Every diagonal is "/"; cuts top-left and bottom-right; no radius, shadow, tilt or texture.
- [ ] Wide type only; big numbers are Shingo Grid figure readouts; at most one display line that is not solid.
- [ ] Utility screens follow the grammar: masthead → hero → divider → body → imprint.
- [ ] States use the state shapes; lists are spec tables; loading is hatch.
- [ ] Slides are continuous and linear, state changes step, nothing eases, and everything stops under reduced motion.

## Use in an iOS app

1. In Xcode, go to File › Add Package Dependencies › Add Local… and pick the `ios/` folder.
2. Register the fonts once at launch:
   ```swift
   import ShingoKit
   @main struct MyApp: App {
       init() { SGFont.register() }
       var body: some Scene { WindowGroup { DashboardExample() } }
   }
   ```
3. Build screens on the grammar:
   ```swift
   SGUtilityScreen("Protected", span: (Text("since 08:14"), Text("lis-04")), tag: .japanese("保護中")) {
       SGBar(height: 100, bleed: .leading, progress: 0.82).frame(width: 270)
   } content: {
       Toggle("Kill switch", isOn: $on).toggleStyle(SGToggleStyle())
       Button("Disconnect") {}.buttonStyle(SGButtonStyle(.print))
   }
   ```
4. For static art, drag `assets/svg/*.svg` into an asset catalog and tick **Preserve Vector Data**. Single-colour glyphs render as template images, so tint them in code. For multi-colour ones (`scope`), set Appearances to Any/Dark and drop the `-light` file into Any and the `-dark` file into Dark.

> The Swift sources were written against the iOS 17 SwiftUI API but have **not been compiled yet**. The build environment had no Swift toolchain. Expect a few small fixes on the first Xcode build.

## Web → SwiftUI map

| Web | SwiftUI | Notes |
|---|---|---|
| `.tex`, `.facet` | `StripeField(facets:)` | 45° stripes, 6 pt period |
| `.sg-bg` + `#g-bg-{monolith}` | `SGMonolith(.bulkhead)` | generated from `tools/monoliths.py` |
| `.u`, `.u-hd`, `.u-hero`, `.hazard`, `.u-body` | `SGUtilityScreen` | the screen grammar |
| `.bar` (+ `--bleed-r`) | `SGBar(height:bleed:progress:)` | band 16%, cut 42% of height |
| `#g-x-line` / `#g-x-solid` | `SGHardX()` stroke / fill | square-cut ends |
| `#g-mark` | `DiamondMark()` with `eoFill` | |
| `.chamfer`, `.cut` | `.chamferFrame()`, `ChamferRect` | cuts 6 / 12 / 24 |
| `.brackets` | `.brackets()`, `Brackets` | HUD corners |
| `.slab-cut` | `TagCut` | the coral tag slab |
| `.hazard` | `HazardBar` | |
| `.btn--*` | `SGButtonStyle(.print/.signal/.plate/.ink/.ghost)` | 48 pt, cut 10 |
| `.tgl` | `SGToggleStyle()` | |
| `.seg` | `SGSegmented` | |
| `.slot`, `.yearspan`, `.barcode` | `SGSlot`, `YearSpan`, `Barcode` | |
| `#g-spectrum`, `#g-scope` | `Spectrum`, `Scope` | |
| `seg7()` → `.sg-fig` (`.live-down` / `.live-up` fixed cells), `.cells`, `.ruler` | `SGReadout` (`tabular:`), `SGCellMeter`, `SGRuler` | readouts and levels |
| `.cells-split` + `.cells--slim.cells--s1..4`, `.pip-legend` + `.pip--s1..4` | `SGSplitCellMeter`, `SGSeriesPip`, `SGSeries` | up to 4 multi-series 45° tracks + 5×5 square pips; `.pip-item--hot` (`isAlert`) for coral threshold text |
| `.steps`, `.itabs`, `.caution`, `.stamp` | `SGSteps`, `SGIndexTabs`, `SGCaution`, `SGStamp` | |
| `.ticket`, `.keycap`, `.rocker`, `.dataplate` | `SGTicket`, `SGKeycapStyle`, `SGRockerStyle`, `SGDataPlate` | |
| `.marks`, `.colorbar`, `.ticker`, `.bootlog`, `.lamps` | `.printMarks()`, `SGColorBar`, `SGTicker`, `SGBootLog`, `SGLamps` | |
| `.callout`, `.blueprint`, `#g-wave`, `#g-matrix` | `SGCallout`, `SGBlueprint`, `SGWave`, `SGMatrixCode` | |
| `.xh`, `.techframe`, `.rail`, `.spaced` | `SGCrosshair`, `.sgTechFrame()`, `SGRail`, `SGSpacedText` | print furniture |
| `.coords`, `.vstamp`, `.marktile`, `.dcall`, `.specgrid`, `.gbuild` | `SGCoordStack`, `SGVersionStamp`, `SGMarkTile`, `SGDataCallout`, `SGSpecGrid`, `SGGlyphBuild` | print furniture |
| `.imp-screen`, `.imp-keyline`, `.imp-tone` | `SGDisplayText(_:size:impression:)` (`SGScreenFill`, `SGKeyline`) | the four impressions; display type 40 pt+ |
| `.state--ok/warn/fault/off/busy` | `SGState(.nominal/.caution/.fault/.offline/.syncing)` | one shape per state |
| `.stable` | `SGSpecTable` | coded columns, coral bar on selection |
| `.xcheck`, `.dradio`, `.stepper` | `SGXCheckboxStyle`, `SGDiamondRadio`, `SGStepper` | the form set |
| `.search`, `.selectf` | `SGSearchField`, `Picker` in a `ChamferRect` frame | |
| `.telex`, `window.shingo.telex()` | `SGTelex` | types in; faults buzz |
| `.skel` | `SGSkeleton` | drafting hatch |
| decode (`data-decode-view`, `data-decode-change`, `data-no-decode`), `.live-*`, `.sg-wipe`, `.sg-hud` | `SGScrambleText(_:weight:delay:)`, `SGLiveCountdown`, `.sgHazardWipe`, `.sgHUD` | the live layer |

## Three languages

- **English** runs the interface: every action, label and number.
- **日本語** adds texture: vertical captions (`.sg-jp-v` / `VerticalText`), hanko seals (`.hanko` / `Hanko`) and display kanji. At most one per screen, and never the only label on a control.
- **Français** is the aside: italic notes in the span rule, dates, pull quotes and fine print (`.sg-fr` / `.sgFR()`). At most one per screen.

Every phrase, with its Japanese reading, is in `tokens/lexicon.json`. These are drafts: have native speakers check them before release.

## Origins

Shingō started from two references: a sage and coral poster (palette, striped ground, layered forms, right-aligned telemetry) and a trilingual technical print (wide industrial type, hazard bars, chevrons, barcodes, three languages). Later references added field-operations print (status matrices, redaction, ID plates) and a construction-guide poster (an exploded X, guides, city data over a photo). Earlier rounded forms from the first poster have been retired. The first title face, a light, very wide octagonal design, has been retired too: Shingo Grid was drawn again as the cut-plate face above, so the type finally obeys the system's own first shape rule. Orbitron (as Shingo Signal) and Saira Stencil One, which set subheads, labels and serials until then, gave way to the new face's lighter weights and its stencil, so the system now speaks in one voice; both remain in the history if you want them back.

## SwiftUI coverage

ShingoKit covers the tokens, type and its four impressions, alphabet shapes, components, instruments, icons, the screen grammar, all 22 monoliths, eleven line backdrops, the live layer (scramble, countdowns, wipe, HUD, haptics) and the patterns (states, spec table, form set, search, telex, skeleton). Web-only so far: the motifs, six of the backdrops, the ops furniture, constructed type, the relay network diagram, the posters and the console layout. The Swift code hasn't been compiled yet.

## Fonts

- **Shingo Grid** is drawn in this repo by `tools/font.py`, MIT licensed with the rest of the repo. Every glyph is a union of bars, stems and 45° strokes with the plate cuts taken out (skia-pathops), on whole font units, so every edge is level, upright or exactly 45°. One set of drawings makes every weight: positions are shared, strokes come from the weight's row in `WEIGHTS`, and details that follow the stroke (notches, points, accents) scale with it.

  | | stem | bar | diagonal | the O | bearing | web weights it answers | iOS name |
  |---|---|---|---|---|---|---|---|
  | **Heavy** | 170 | 148 | 158 | 770 | 52 | 850–900 | `ShingoGrid-Heavy` |
  | **Bold** | 142 | 128 | 134 | 760 | 60 | 650–849 | `ShingoGrid-Bold` |
  | **Medium** | 120 | 112 | 116 | 750 | 68 | 100–649 | `ShingoGrid-Medium` |
  | **Stencil** | the Heavy, bridged by 84-unit slits | | | | | its own family, `Shingo Grid Stencil` | `ShingoGrid-Stencil` |

  1000 units per em, cap height 700, x-height 540, ascenders 740, descenders −190. The plate cut is 150 deep in the Heavy (142 and 134 in the lighter weights), with the inner corner cut to match so a stroke keeps its weight round the turn. The Medium sets caps at 10 to 13 px, so its bars stay close to its stems. Stems stand about a stem apart in the Heavy and open up as the weight drops; spacing is optical (each side gets the base bearing minus part of the white it already holds), and the few pairs that cannot reach are kerned (LT, LY, TJ, P., 3/8…). Being square-shouldered, the face needs none of the classic diagonal pairs.
- Each weight covers A–Z and a full lowercase (a two-storey a; n, u, m and w cut like the capitals), figures, common punctuation, arrows (← ↑ → ↓), ◆, №, primes, guillemets, € $ % and the accented capitals and lowercase for English, French and Portuguese; anything else (Æ, Œ, ß, ™) falls through to Anybody. The figures share one body width and the capitals' rules: a slashed zero whose slash runs between the two square corners, a 1 with a flag cut right through, a closed 4 on a 45° stroke, a straight 7. The S and the 5 are cut at their extremes and square at the waist; the 2 is square at its extremes and cut at both waist turns, so its neck runs "/". Tabular alternates (`tnum`) share one advance, and the tabular 1 stands on a foot so it fills its cell. The gallery's Components section has an audit card with the weights and every character, read from the font file.
- **The stencil** carries capitals and figures; lowercase sets in the capitals. A square corner where a bar and a stem join is opened by a mitre slit through its inner corner; a glyph no mitre reaches is bridged once (across the H's crossbar, the stem of I K T Y, the falling stroke of M N V W X, a bar of F Z 4 7); the zero's slash floats clear of its frame. Letters keep the Heavy's spacing, so a bridge never shifts a line.
- Anybody and IBM Plex Mono are licensed under the SIL Open Font License 1.1 (licence texts next to the fonts in `ios/Sources/ShingoKit/Resources/Fonts/OFL-*.txt`). You may bundle them in an app; keep the licence texts with them.
- Japanese uses Hiragino Sans, which ships with iOS, and BIZ UDGothic on the web. BIZ UDGothic isn't bundled because it's 4 MB.
- Rebuilding the fonts needs `pip install fonttools brotli skia-pathops`.


## Licence

The code, tokens, artwork and docs are MIT licensed (see `LICENSE`). The bundled fonts keep their own SIL Open Font License.
