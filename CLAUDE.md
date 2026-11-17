# Shingō repo conventions

Shingō 信号 is an industrial print design system for iOS and the web. The art direction in `README.md` (rules 1–18) is binding for every change. `skills/shingo/SKILL.md` is the condensed version for applying it.

## Layout

- `web/shingo.css` — tokens + every component. `web/shingo-live.js` — the live layer.
- `web/gallery.src.html` + `web/partials/` — gallery source with `<!--@…-->` placeholders.
- `tools/screens.py` — writes the 26 phone screens into the gallery source.
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
- After a visual change, rebuild, screenshot both modes and look at the result before committing.
- The Swift sources have not been compiled in CI (no toolchain here); keep to iOS 17 SwiftUI API.
