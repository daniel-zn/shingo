---
name: shingo
description: Apply the Shingō 信号 industrial print design system (sci-fi industrial brutalism, two inks plus one coral signal, wide hard type, one 45° diagonal, seven-segment readouts, EN with JP/FR accents) to a web or iOS interface. Use when building or reviewing any screen, component or page that should look like Shingō.
---

# Shingō 信号

Interfaces are **printed** on a striped ground like a two-ink screen print: wide hard type, one 45° diagonal, hazard bars, chevrons, seven-segment readouts, stencil serials, mono telemetry and one coral signal per screen. Every screen exists in light and dark.

Source of truth, in this order: `README.md` (rules 1–18), `tokens/tokens.json`, `web/shingo.css`, `ios/Sources/ShingoKit/`. The gallery `dist/index.html` shows every piece; `dist/starter.html` is a complete page to copy.

## Set up

**Web.** Link `shingo.css`, inline `shingo-sprite.svg` at the top of `<body>`, add `shingo-live.js` at the end. Put `class="tex"` on the root and `data-sg-live` on regions that get the live layer. Glyphs: `<svg><use href="#g-i-scan"/></svg>`.

**iOS.** Add `ios/` as a local Swift package, call `SGFont.register()` at launch, use `SG.*` colours (dynamic for both modes), `SGFont.*` type and the `SG*` views.

## Rules (hard constraints)

1. Two inks: ground (`--ground*`) and print (`--ground-hi`, `--sage*`). Plates are solid print with text knocked out in `--ink`. No third tone, no gradients, no white, no black.
2. One coral (`--coral`) block or primary action per screen, plus small active/fault states. Coral as text uses `--signal-text`.
3. Every diagonal rises "/" at 45°. Cuts top-left + bottom-right at 6/12/24. No `border-radius`, shadows, tilts, blur, textures or photos.
4. Type: Anybody wide (display 150%/800 40+, titles 125%/800 28, inline 125%/700 14, labels 125%/600 caps), IBM Plex Mono telemetry, Saira Stencil One serials (once per screen), BIZ UDGothic / Hiragino kanji. Big numbers are seven-segment readouts (`seg7()` / `SGSegDisplay`). Never condensed or rounded fonts.
5. Utility screens follow the grammar: masthead `.u-hd` (code, title, ONE tag, span rule) → ONE hero → divider (`.hazard` system, ticks data, slash money/content) → `.u-body` → imprint `.u-foot`. Poster screens (launch, onboarding, lock, empty) compose freely.
6. One backdrop per screen (`<svg class="sg-bg"><use href="#g-bg-…"/></svg>` / `SGMonolith`). Default to a monolith: one oversized flat mass that bleeds off the edges (monolith, bulkhead, giant-x, chevrons, ziggurat, diamond, girder, aperture, segment, massing, ramp, pylon), chosen by subject. Fine line backdrops only where the subject needs detail. A content motif (`#g-m-*`) only if the subject has one.
7. States: `.state--ok` solid square, `--warn` hatch, `--fault` coral X, `--off` dim X, `--busy` marching hatch (`SGState`). Never colour alone.
8. Lists are spec tables (`.stable` / `SGSpecTable`). Checkboxes `.xcheck`, radios `.dradio`, steppers `.stepper`, search `.search`, select `.selectf`.
9. Notifications are telex (`.telex`, `window.shingo.telex()` / `SGTelex`). Loading is hatch (`.skel--run` / `SGSkeleton`). No spinners, no shimmer.
10. Motion is never eased. Slides (tickers, marching hazard/hatch, the wipe band) move continuously and linearly; state changes (blinks, fills, pulses) use `steps()`. Text decodes from class-keeping glyph noise on arrival (titles → labels → data), on change (new values) and on touch (control labels); never paragraphs, inputs or readouts. Respect reduced motion.
11. English runs the UI. At most one Japanese accent (vertical tag `.sg-jp-v` or seal `.hanko`) and one French aside (`.sg-fr`, usually in the span rule) per screen. Use `tokens/lexicon.json`.
12. Larger screens keep the grammar and add a rail (see `.con` in the gallery).

## Build a screen

1. Decide the tier (poster or utility) and the subject.
2. Masthead: short code (`AX·01`), uppercase title, one tag, span rule `value ──── value`.
3. Hero: exactly one form (nested bar, readout, plate, scope, chevrons).
4. Divider by kind, then the body from kit parts only: `.u-label` group headers, `.stable`, `.spec`, `.cells`, `.nframe`, `.smx`, `.chamfer`, `.brackets`, `.btn--*`, `.tgl`, `.seg`, form set.
5. Imprint footer: wide-caps line, mono reference, barcode.
6. Pick the backdrop. Add the coral: one block or the primary action.

## Review checklist

- [ ] Light and dark both checked (`data-theme="light"|"dark"`, `.mode-light`, SwiftUI previews).
- [ ] Exactly one coral block/primary action; coral text legible on light (`--signal-text`).
- [ ] No radius, shadow, gradient, image, tilt or texture; all diagonals "/".
- [ ] Only kit fonts; numbers in seven-segment where they are the hero.
- [ ] Grammar order intact; one tag; one hero; one backdrop.
- [ ] State shapes, spec tables, telex and hatch used where relevant.
- [ ] Slides linear and continuous, state changes stepped, all off under reduced motion; no horizontal scroll at 390 px.

If a need is not covered, extrapolate from the alphabet (cut plate, tag, nested bar, slash, hazard, notch frame, hard X, diamond, chevrons, brackets, cell run, wedge) rather than importing a new style, then add it to `web/shingo.css`, `ShingoKit` and the gallery together.
