# Shingō repo conventions

Shingō 信号 is an industrial print design system for iOS and the web. The art direction in `README.md` (rules 1–20) is binding for every change. `skills/shingo/SKILL.md` is the condensed version for applying it.

## Layout

- `web/shingo.css` — tokens + every component. `web/shingo-live.js` — the live layer.
- `web/gallery.src.html` + `web/partials/` — gallery source with `<!--@…-->` placeholders.
- `tools/screens.py` — writes the 28 phone screens into the gallery source.
- `tools/font.py` — draws Shingo Grid Heavy, the title face (a cut-plate grotesque: cuts top-left and bottom-right only; capitals, lowercase, figures and punctuation in one file, built with skia-pathops). Its numbers (cap height, stems, cut) are constants at the top; `tools/print_kit.py` and `tools/posters.py` read them, so guides stay true. `tools/signal_font.py` — builds Shingo Signal (Orbitron plus missing glyphs) for subheads and labels. Run them after changing a glyph, then the build.
- `tools/print_kit.py` — print furniture generators (used by build.py and screens.py). `tools/posters.py` — poster series XP·07–12.
- `tools/monoliths.py` — the monolith backdrops as polygon data; build.py turns it into `#g-bg-*` symbols and `SGMonolith.swift` (generated).
- `tools/build.py` — glyphs, backdrops, motifs, posters, patterns, console; writes `dist/` (gallery + standalone kit) and `tokens/shingo.tokens.json`; runs `tools/check_tokens.py`.
- `templates/starter.src.html` — the starter page (built to `dist/starter.html`).
- `ios/Sources/ShingoKit/` — SwiftUI package; mirrors the web kit (see the Web → SwiftUI map).
- `tokens/tokens.json` — the spec in data form. `tokens/lexicon.json` — EN/JP/FR phrases.

## Commands

```bash
python3 tools/screens.py && python3 tools/build.py
```

```bash
node tools/screenshot.js docs 1
```

`dist/` and `docs/` are generated: rebuild, never hand-edit. Playwright and Chromium are preinstalled in cloud sessions.

## Rules for changes

- Colours live in three places: `tokens/tokens.json`, `web/shingo.css`, `ios/Sources/ShingoKit/SGTheme.swift`. Change all three; the build fails otherwise.
- New pieces go into CSS, SwiftUI and the gallery together, and must work in light and dark.
- Keep CSS braces balanced; one broken `@media` swallows everything after it.
- Never ease. Slides are continuous and linear, state changes are stepped; respect `prefers-reduced-motion` / `accessibilityReduceMotion`.
- Type cuts follow the plates: top-left and bottom-right only. A new glyph that needs a curve gets that cut or a square corner, never a cut that runs the other way.
- Display type may print screened, keyline or tone (`.imp-*`, rule 20); at most one such line per screen, never for text that must be read at a glance.
- After a visual change, rebuild, screenshot both modes and look at the result before committing.
- The Swift sources have not been compiled in CI (no toolchain here); keep to iOS 17 SwiftUI API.
