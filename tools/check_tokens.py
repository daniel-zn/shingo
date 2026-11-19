"""Verify the three sources of colour truth agree:
tokens/tokens.json  ·  web/shingo.css  ·  ios/Sources/ShingoKit/SGTheme.swift

    python3 tools/check_tokens.py      (also runs at the end of tools/build.py)

Exits non-zero and lists every mismatch. Change a colour in all three places, or not at all.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# CSS custom property → SG Swift name
SWIFT = {"ground": "ground", "ground-2": "ground2", "ground-3": "ground3", "on-ground": "onGround", "ground-hi": "groundHi",
         "ground-dim": "groundDim", "sage": "sage", "sage-hi": "sageHi", "sage-lo": "sageLo", "sage-line": "sageLine",
         "ink": "ink", "ink-dim": "inkDim", "coral": "coral", "coral-deep": "coralDeep", "signal-text": "signalText", "signal-plate": "signalPlate"}


def css_block(css, selector):
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
    return dict(re.findall(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", m.group(1))) if m else {}


def swift_colors(src):
    out = {"dark": {}, "light": {}}
    for name, a, b in re.findall(r"static let (\w+)\s*=\s*Color\(light: 0x([0-9A-Fa-f]{6}), dark: 0x([0-9A-Fa-f]{6})\)", src):
        out["light"][name], out["dark"][name] = "#" + a.lower(), "#" + b.lower()
    for name, h in re.findall(r"static let (\w+)\s*=\s*Color\(hex: 0x([0-9A-Fa-f]{6})\)", src):
        out["light"][name] = out["dark"][name] = "#" + h.lower()
    return out


def main():
    tok = json.loads((ROOT / "tokens" / "tokens.json").read_text())["color"]
    css = (ROOT / "web" / "shingo.css").read_text()
    sw = swift_colors((ROOT / "ios" / "Sources" / "ShingoKit" / "SGTheme.swift").read_text())
    blocks = {"dark": [":root, .mode-dark"], "light": [".mode-light", ':root[data-theme="light"]']}
    errs = []
    for mode in ("dark", "light"):
        for k, v in tok[mode].items():
            if k.startswith("$"):
                continue
            v = v.lower()
            for sel in blocks[mode]:
                got = css_block(css, sel).get(k)
                if got is None and mode == "light" and sel != ".mode-light":
                    continue  # light overrides only restate what changes
                if got is None:
                    errs.append(f"css {sel}: --{k} missing (tokens {v})")
                elif got.lower() != v:
                    errs.append(f"css {sel}: --{k} {got} ≠ tokens {v}")
            name = SWIFT.get(k)
            if name and name in sw[mode] and sw[mode][name] != v:
                errs.append(f"swift SG.{name} ({mode}) {sw[mode][name]} ≠ tokens {v}")
            elif name and name not in sw[mode]:
                errs.append(f"swift SG.{name} missing")
    if errs:
        print("token check FAILED:\n  " + "\n  ".join(errs))
        sys.exit(1)
    print("token check ok: tokens.json = shingo.css = SGTheme.swift")


if __name__ == "__main__":
    main()
