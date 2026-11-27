"""Print furniture: the technical-print layer from the references, as HTML generators.

Crosshairs, spec rails, word-spaced microtext, coordinate stacks, version stamps, the coral
mark tile, data callouts, specimen columns, glyph constructions and tech frames. Styles live
in web/shingo.css ("print furniture"); SwiftUI counterparts in SGPrint.swift.

Used by tools/build.py (gallery chrome, the print-furniture card) and tools/screens.py.
"""
import html


def xh(dim=False, style=""):
    """A registration crosshair with an open centre."""
    s = f' style="{style}"' if style else ""
    return f'<i class="xh{" xh--dim" if dim else ""}{" xh--abs" if style else ""}" aria-hidden="true"{s}></i>'


def rail(text, up=False, style=""):
    """Vertical mono spec text that runs on as a hairline."""
    s = f' style="{style}"' if style else ""
    return f'<span class="rail{" rail--up" if up else ""}" aria-hidden="true"{s}>{html.escape(text)}</span>'


def spaced(text, style="", hot=()):
    """Microtext justified to the full measure on every line. Words in `hot` print in the main ink."""
    words = [f"<b>{w}</b>" if w.strip(".,;:") in hot else w for w in text.split()]
    s = f' style="{style}"' if style else ""
    return f'<p class="spaced"{s}>{" ".join(words)}</p>'


def coords(lines, dim=(), style=""):
    """The coordinate stack: short lines in the display face (indexes in `dim` print dim)."""
    s = f' style="{style}"' if style else ""
    return f'<div class="coords"{s}>' + "".join(
        ('<span class="co-dim">' if i in dim else "<span>") + f"{l}</span>" for i, l in enumerate(lines)) + "</div>"


def vstamp(text, small="", sig=False, style=""):
    """A version / test stamp in a cut hairline box."""
    s = f' style="{style}"' if style else ""
    sm = f"<small>{small}</small>" if small else ""
    return f'<span class="vstamp{" vstamp--sig" if sig else ""}"{s}>{text}{sm}</span>'


def marktile(size=34, style=""):
    """The brand mark knocked out of a coral tile."""
    return (f'<span class="marktile" aria-hidden="true" style="width:{size}px;height:{size}px;{style}">'
            f'<svg viewBox="0 0 100 100"><use href="#g-mark"/></svg></span>')


def dcall(name, rows, style=""):
    """A data callout: node, display-face name, key/value rows."""
    s = f' style="{style}"' if style else ""
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
    return f'<div class="dcall"{s}><b>{name}</b><dl>{dl}</dl></div>'


def specgrid(chars, cols=4, style=""):
    """A specimen column; figures take the signal accent."""
    s = f' style="--cols:{cols};{style}"'
    return f'<div class="specgrid"{s}>' + "".join(
        f'<span{" class=fig" if c.isdigit() else ""}>{html.escape(c)}</span>' for c in chars) + "</div>"


_FONT = {}


def _face():
    """Shingo Grid's own numbers, read from the font file once: cap height, x-height and advances per em."""
    if not _FONT:
        import pathlib
        from fontTools.ttLib import TTFont
        f = TTFont(pathlib.Path(__file__).resolve().parent.parent / "ios" / "Sources" / "ShingoKit" / "Resources" / "Fonts" / "ShingoGrid-Heavy.ttf")
        _FONT.update(cap=f["OS/2"].sCapHeight, x=f["OS/2"].sxHeight, upm=f["head"].unitsPerEm, cmap=f.getBestCmap(), hmtx=f["hmtx"])
    return _FONT


# the glyph-construction sheet (.gbuild): 1.8:1, the glyph set at 54cqw from 8% in, baseline at 84%
GB_SIZE, GB_LEFT, GB_BASE, GB_RATIO = 54, 0.08, 0.84, 1.8


def gbuild(ch, guides=None, verticals=None, values=False, style="", cls=""):
    """A giant tonal glyph on grid paper with labelled construction guides. The guides are true:
    cap line, x-height, baseline, origin and advance come from the font file (values=True prints
    the numbers in font units)."""
    f = _face()
    em = GB_SIZE * GB_RATIO / 100                    # one em as a fraction of the sheet's height
    if guides is None:
        lab = (lambda n, k: f"{n} {f[k]}") if values else (lambda n, k: n)
        guides = ((lab("cap", "cap"), GB_BASE - em * f["cap"] / f["upm"]), (lab("x-height", "x"), GB_BASE - em * f["x"] / f["upm"]), ("baseline", GB_BASE))
    if verticals is None:
        adv = f["hmtx"][f["cmap"][ord(ch)]][0] / f["upm"]
        verticals = (GB_LEFT, GB_LEFT + GB_SIZE / 100 * adv)
    s = f' style="{style}"' if style else ""
    g = "".join(f'<i class="gb-l" style="top:{y * 100:.1f}%"><span>{n}</span></i>' for n, y in guides)
    v = "".join(f'<i class="gb-v" style="left:{x * 100:.1f}%"></i>' for x in verticals)
    return f'<div class="gbuild blueprint {cls}"{s} aria-hidden="true"><span class="gb-g">{html.escape(ch)}</span>{g}{v}</div>'


def techframe(inner, style="", cls=""):
    """Wrap content in a frame with crosshairs on its four corners."""
    s = f' style="{style}"' if style else ""
    return f'<div class="techframe {cls}"{s}>{xh()}{xh()}{xh()}{xh()}{inner}</div>'
