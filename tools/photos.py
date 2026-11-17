#!/usr/bin/env python3
"""Process source photos into Shingō duotones.

  python3 tools/photos.py            # reads assets/photos/src/*.jpg + credits.json

Each photo becomes two print-style duotones that match the palette:
  <name>-dark.jpg   ink #0b0b0a  -> bone #dcdfd5   (dark mode)
  <name>-light.jpg  ink #0f100d  -> sage #bcbfb4   (light mode)
Contrast is pushed so the result reads like a screen print, not a photo filter.
Sources and licenses live in assets/photos/credits.json; keep them with the files.
"""
import json
import pathlib

from PIL import Image, ImageEnhance, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "photos" / "src"
OUT = ROOT / "assets" / "photos"
TONES = {"dark": ((0x0B, 0x0B, 0x0A), (0xDC, 0xDF, 0xD5)), "light": ((0x0F, 0x10, 0x0D), (0xBC, 0xBF, 0xB4))}


def duotone(img, lo, hi):
    g = ImageOps.grayscale(img)
    g = ImageOps.autocontrast(g, cutoff=1.5)
    g = ImageEnhance.Contrast(g).enhance(1.25)
    return ImageOps.colorize(g, black=lo, white=hi)


def main(width=1100):
    credits = json.loads((OUT / "credits.json").read_text())
    for name in credits:
        src = SRC / f"{name}.jpg"
        im = Image.open(src).convert("RGB")
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        for mode, (lo, hi) in TONES.items():
            duotone(im, lo, hi).save(OUT / f"{name}-{mode}.jpg", quality=78, optimize=True, progressive=True)
        print("processed", name, im.size)


if __name__ == "__main__":
    main()
