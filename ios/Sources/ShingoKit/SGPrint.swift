import SwiftUI

// MARK: - Print furniture
//
// The technical-print layer from the references: what a printed spec sheet carries around
// its content. Crosshairs, spec rails, word-spaced microtext, coordinate stacks, version
// stamps, the coral mark tile, data callouts, specimen columns, glyph constructions and
// tech frames. All of it prints in the print or dim ink; coral is reserved for the mark tile
// and one signal stamp per view. Mirrors the "print furniture" block of web/shingo.css
// (generators: tools/print_kit.py).

// MARK: Crosshair

/// A registration crosshair: a "+" of hairlines with an open centre (`.xh`).
/// `dim` prints it in the secondary ink (`.xh--dim`).
public struct SGCrosshair: View {
    var dim: Bool; var size: CGFloat
    public init(dim: Bool = false, size: CGFloat = 14) { self.dim = dim; self.size = size }
    public var body: some View {
        SGPrintOpenCross(line: SG.hair)
            .fill(dim ? SG.groundDim : SG.groundHi)
            .frame(width: size, height: size)
            .accessibilityHidden(true)
    }
}

/// Four arms, each 35% of the box, leaving the middle 30% open.
private struct SGPrintOpenCross: Shape {
    var line: CGFloat
    func path(in r: CGRect) -> Path {
        let ax = r.width * 0.35, ay = r.height * 0.35, t = line
        var p = Path()
        p.addRect(CGRect(x: r.minX, y: r.midY - t / 2, width: ax, height: t))
        p.addRect(CGRect(x: r.maxX - ax, y: r.midY - t / 2, width: ax, height: t))
        p.addRect(CGRect(x: r.midX - t / 2, y: r.minY, width: t, height: ay))
        p.addRect(CGRect(x: r.midX - t / 2, y: r.maxY - ay, width: t, height: ay))
        return p
    }
}

// MARK: Spec rail

/// A vertical line of mono spec text, reading upward, that runs on as a hairline (`.rail`).
/// The hairline fills the height it is given and runs down from the text; `up` puts it above
/// the text instead (`.rail--up`).
public struct SGRail: View {
    var text: String; var up: Bool
    public init(_ text: String, up: Bool = false) { self.text = text; self.up = up }
    public var body: some View {
        VStack(spacing: 8) {
            if up { hairline }
            SGPrintQuarterTurn {
                Text(text).font(SGFont.mono(10)).tracking(10 * 0.14)
                    .textCase(.uppercase)
                    .lineLimit(1)
                    .fixedSize()
                    .rotationEffect(.degrees(-90))
            }
            if !up { hairline }
        }
        .foregroundStyle(SG.groundDim)
        .accessibilityHidden(true)
    }
    private var hairline: some View {
        Rectangle().frame(width: 1).frame(minHeight: 16, maxHeight: .infinity).opacity(0.7)
    }
}

/// Lays out its one subview at its ideal size and reports that size turned a quarter, so a
/// `.rotationEffect(±90°)` child takes the space it visibly covers.
private struct SGPrintQuarterTurn: Layout {
    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        guard let s = subviews.first?.sizeThatFits(.unspecified) else { return .zero }
        return CGSize(width: s.height, height: s.width)
    }
    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        guard let v = subviews.first else { return }
        v.place(at: CGPoint(x: bounds.midX, y: bounds.midY), anchor: .center, proposal: .unspecified)
    }
}

// MARK: Spaced microtext

/// Mono microtext whose words spread to the full measure on every line, the last line
/// included, like the posters' captions (`.spaced`). Words in `hot` (compared without
/// trailing `.,;:`) print in the main ink.
public struct SGSpacedText: View {
    var text: String; var hot: Set<String>; var size: CGFloat
    public init(_ text: String, hot: Set<String> = [], size: CGFloat = 10) {
        self.text = text; self.hot = hot; self.size = size
    }
    private static let punctuation = CharacterSet(charactersIn: ".,;:")
    public var body: some View {
        let words = text.split(whereSeparator: \.isWhitespace).map(String.init)
        // a space is 0.6 em in Plex Mono, plus the 0.08 em tracking; lines pitch at 1.55 em (the face sets 1.3 em)
        SGPrintJustifyLayout(minGap: size * 0.68, lineSpacing: size * 0.25) {
            ForEach(Array(words.enumerated()), id: \.offset) { _, word in
                Text(word)
                    .foregroundStyle(hot.contains(word.trimmingCharacters(in: Self.punctuation)) ? SG.groundHi : SG.groundDim)
            }
        }
        .font(SGFont.mono(size))
        .tracking(size * 0.08)
        .textCase(.uppercase)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(Text(text))
    }
}

/// Wraps its subviews (one per word) into lines, then spreads each line's spare width evenly
/// between its words. A line holding a single word sits at the leading edge.
private struct SGPrintJustifyLayout: Layout {
    var minGap: CGFloat
    var lineSpacing: CGFloat

    struct Line { var range: Range<Int>; var width: CGFloat; var height: CGFloat }

    func makeCache(subviews: Subviews) -> [CGSize] {
        subviews.map { $0.sizeThatFits(.unspecified) }
    }

    func updateCache(_ cache: inout [CGSize], subviews: Subviews) {
        cache = makeCache(subviews: subviews)
    }

    private func lines(_ sizes: [CGSize], width: CGFloat) -> [Line] {
        var out: [Line] = []
        var start = 0
        var w: CGFloat = 0, h: CGFloat = 0
        for (i, s) in sizes.enumerated() {
            if i > start && w + minGap + s.width > width + 0.01 {
                out.append(Line(range: start..<i, width: w, height: h))
                start = i; w = 0; h = 0
            }
            w += (i > start ? minGap : 0) + s.width
            h = max(h, s.height)
        }
        if start < sizes.count { out.append(Line(range: start..<sizes.count, width: w, height: h)) }
        return out
    }

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout [CGSize]) -> CGSize {
        let natural = cache.reduce(CGFloat(0)) { $0 + $1.width } + minGap * CGFloat(max(0, cache.count - 1))
        var width = natural
        if let proposed = proposal.width, proposed.isFinite { width = proposed }
        let ls = lines(cache, width: width)
        let widest = ls.map(\.width).max() ?? 0
        let height = ls.reduce(CGFloat(0)) { $0 + $1.height } + lineSpacing * CGFloat(max(0, ls.count - 1))
        return CGSize(width: max(width, widest), height: height)
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout [CGSize]) {
        var y = bounds.minY
        for line in lines(cache, width: bounds.width) {
            let n = line.range.count
            let inked = line.range.reduce(CGFloat(0)) { $0 + cache[$1].width }
            let gap = n > 1 ? max(minGap, (bounds.width - inked) / CGFloat(n - 1)) : 0
            var x = bounds.minX
            for i in line.range {
                subviews[i].place(at: CGPoint(x: x, y: y), anchor: .topLeading, proposal: ProposedViewSize(cache[i]))
                x += cache[i].width + gap
            }
            y += line.height + lineSpacing
        }
    }
}

// MARK: Coordinate stack

/// The RADAR data block: short lines set tight in the display face (`.coords`). Lines whose
/// index is in `dim` print in the secondary ink. Case is the author's.
public struct SGCoordStack: View {
    var lines: [String]; var dim: Set<Int>; var size: CGFloat
    public init(_ lines: [String], dim: Set<Int> = [], size: CGFloat = 22) {
        self.lines = lines; self.dim = dim; self.size = size
    }
    public var body: some View {
        // the web pitches lines at 1 em (0.9 line + 0.1 gap); a Shingo Grid line box is 1.18 em
        VStack(alignment: .leading, spacing: size * -0.18) {
            ForEach(lines.indices, id: \.self) { i in
                Text(lines[i])
                    .foregroundStyle(dim.contains(i) ? SG.groundDim : SG.groundHi)
                    .lineLimit(1)
                    .fixedSize(horizontal: true, vertical: false)
            }
        }
        .font(SGFont.display(size))
        .tracking(size * 0.01)
        .accessibilityElement(children: .combine)
    }
}

// MARK: Version stamp

/// A version / test stamp: display-face text in a hairline box with its top-leading corner cut
/// (`.vstamp`), with an optional small mono suffix. `signal` makes it the view's one coral
/// stamp (`.vstamp--sig`).
public struct SGVersionStamp: View {
    var text: String; var small: String?; var signal: Bool
    public init(_ text: String, small: String? = nil, signal: Bool = false) {
        self.text = text; self.small = small; self.signal = signal
    }
    public var body: some View {
        let ink = signal ? SG.signalText : SG.groundHi
        HStack(spacing: 8) {
            Text(text).font(SGFont.display(13)).tracking(13 * 0.06)
            if let small {
                Text(small).font(SGFont.mono(10)).tracking(1).opacity(0.8)
            }
        }
        .textCase(.uppercase)
        .lineLimit(1)
        .padding(.leading, 12).padding(.trailing, 10).padding(.vertical, 4)
        .foregroundStyle(ink)
        .background(SGPrintCutFrame(cut: 8, line: SG.hair).fill(ink, style: FillStyle(eoFill: true)))
        .fixedSize()
        .accessibilityElement(children: .combine)
    }
}

/// A hairline frame with a 45° cut on the top-leading corner (the `.vstamp` clip path).
/// Fill it even-odd.
private struct SGPrintCutFrame: Shape {
    var cut: CGFloat; var line: CGFloat
    func path(in r: CGRect) -> Path {
        func pt(_ x: CGFloat, _ y: CGFloat) -> CGPoint { CGPoint(x: r.minX + x, y: r.minY + y) }
        let w = r.width, h = r.height, c = min(cut, w, h), t = line
        var p = Path()
        p.addLines([pt(c, 0), pt(w, 0), pt(w, h), pt(0, h), pt(0, c)])
        p.closeSubpath()
        p.addLines([pt(c + t, t), pt(w - t, t), pt(w - t, h - t), pt(t, h - t), pt(t, c + t)])
        p.closeSubpath()
        return p
    }
}

// MARK: Mark tile

/// The brand mark knocked out of a coral square with its bottom-trailing corner cut, like the
/// references' logo tiles (`.marktile`). The mark prints in the fixed ink, as text on coral does.
public struct SGMarkTile: View {
    var size: CGFloat
    public init(size: CGFloat = 34) { self.size = size }
    public var body: some View {
        DiamondMark()
            .fill(SG.inkFixed, style: FillStyle(eoFill: true))
            .frame(width: size * 0.6, height: size * 0.6)
            .frame(width: size, height: size)
            .background(TagCut(cut: 7, corner: .bottomTrailing).fill(SG.coral))
            .accessibilityHidden(true)
    }
}

// MARK: Data callout

/// A data callout, the posters' city labels (`.dcall`): a square node with a centre dot, a
/// name in the display face and key/value rows in mono, keys in the secondary ink.
public struct SGDataCallout: View {
    var name: String; var rows: [(String, String)]
    public init(_ name: String, rows: [(String, String)]) { self.name = name; self.rows = rows }
    public var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(spacing: 7) {
                SGPrintNode().frame(width: 9, height: 9)
                Text(name).font(SGFont.display(15)).tracking(15 * 0.03).textCase(.uppercase)
            }
            if !rows.isEmpty {
                Grid(alignment: .leading, horizontalSpacing: 10, verticalSpacing: 1) {
                    ForEach(rows.indices, id: \.self) { i in
                        GridRow {
                            Text(rows[i].0).foregroundStyle(SG.groundDim)
                            Text(rows[i].1)
                        }
                    }
                }
                .font(SGFont.mono(10))
                .tracking(9 * 0.06)
                .textCase(.uppercase)
                .padding(.leading, 16)
            }
        }
        .foregroundStyle(SG.groundHi)
        .accessibilityElement(children: .combine)
    }
}

/// The callout node: a hairline square with a square centre dot (nothing round).
private struct SGPrintNode: View {
    var body: some View {
        Rectangle().strokeBorder(SG.groundHi, lineWidth: SG.hair)
            .overlay(Rectangle().fill(SG.groundHi).frame(width: 3, height: 3))
            .accessibilityHidden(true)
    }
}

// MARK: Specimen grid

/// A specimen column: a grid of glyphs in the display face, `columns` wide (`.specgrid`).
/// Figures print in signal text as the one accent.
public struct SGSpecGrid: View {
    var chars: [Character]; var columns: Int; var size: CGFloat
    public init(_ chars: String, columns: Int = 4, size: CGFloat = 22) {
        self.chars = Array(chars); self.columns = columns; self.size = size
    }
    public var body: some View {
        LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 6), count: max(1, columns)), spacing: 0) {
            ForEach(chars.indices, id: \.self) { i in
                Text(String(chars[i]))
                    .foregroundStyle(chars[i].isWholeNumber ? SG.signalText : SG.groundHi)
            }
        }
        .font(SGFont.display(size))
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(Text(String(chars)))
    }
}

// MARK: Glyph construction

/// One giant glyph in tonal ink (ground-3) on grid paper, with labelled horizontal guides and
/// plain vertical guides, each given as a fraction of the sheet's height or width (`.gbuild`).
/// The sheet is fixed at 1.8:1 and the glyph is set at 54% of its width, so the baseline sits
/// at 84% and the cap line at 16%; the default guides follow the face (`SGFace`), and the
/// default verticals mark the glyph's origin and advance.
public struct SGGlyphBuild: View {
    var glyph: String; var guides: [(String, CGFloat)]; var verticals: [CGFloat]?
    public init(_ glyph: String,
                guides: [(String, CGFloat)] = [("cap", 0.84 - 0.972 * SGFace.capHeight), ("x-height", 0.84 - 0.972 * SGFace.xHeight), ("baseline", 0.84)],
                verticals: [CGFloat]? = nil) {
        self.glyph = glyph; self.guides = guides; self.verticals = verticals
    }
    public var body: some View {
        Canvas { ctx, size in
            let w = size.width, h = size.height
            guard w > 0, h > 0 else { return }
            // the glyph: 54% of the width, from 8% in, its baseline on 84% of the height
            let g = ctx.resolve(Text(glyph).font(SGFont.display(w * 0.54)).foregroundStyle(SG.ground3))
            let gs = g.measure(in: CGSize(width: CGFloat.infinity, height: CGFloat.infinity))
            let base = g.firstBaseline(in: gs)
            ctx.draw(g, in: CGRect(x: w * 0.08, y: h * 0.84 - base, width: gs.width, height: gs.height))
            // guides in the dim ink, labels sitting just above their line at the trailing edge
            for (label, f) in guides {
                let y = (h * f).rounded()
                ctx.fill(Path(CGRect(x: 0, y: y, width: w, height: 1)), with: .color(SG.groundDim))
                let t = ctx.resolve(Text(label.uppercased()).font(SGFont.mono(10)).tracking(10 * 0.08).foregroundStyle(SG.groundDim))
                ctx.draw(t, at: CGPoint(x: w - 8, y: y - 14), anchor: .topTrailing)
            }
            for f in verticals ?? [0.08, 0.08 + gs.width / w] {
                ctx.fill(Path(CGRect(x: (w * f).rounded(), y: 0, width: 1, height: h)), with: .color(SG.groundDim))
            }
        }
        .background(SGBlueprint())
        .aspectRatio(1.8, contentMode: .fit)
        .clipped()
        .accessibilityHidden(true)
    }
}

// MARK: Tech frame

public extension View {
    /// A tech frame (`.techframe`): registration crosshairs on the four corners, each centred on
    /// its corner so half of it sits outside the content.
    func sgTechFrame(dim: Bool = false, size: CGFloat = 14) -> some View {
        let o = size / 2
        return self
            .overlay(alignment: .topLeading) { SGCrosshair(dim: dim, size: size).offset(x: -o, y: -o) }
            .overlay(alignment: .topTrailing) { SGCrosshair(dim: dim, size: size).offset(x: o, y: -o) }
            .overlay(alignment: .bottomLeading) { SGCrosshair(dim: dim, size: size).offset(x: -o, y: o) }
            .overlay(alignment: .bottomTrailing) { SGCrosshair(dim: dim, size: size).offset(x: o, y: o) }
    }
}

// MARK: - Preview

private struct SGPrintFurniturePreview: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 28) {
                HStack(spacing: 14) {
                    SGMarkTile()
                    SGCrosshair()
                    SGCrosshair(dim: true)
                    SGVersionStamp("V2.4", small: "rev c")
                    SGVersionStamp("Test", signal: true)
                }
                HStack(alignment: .top, spacing: 16) {
                    SGRail("SHG-04 · 2/6")
                    SGSpacedText("Printed on the stripe in two inks. Every diagonal rises at 45 degrees; corners cut at 6, 12 or 24 pt. Signal reserved for one block per view.",
                                 hot: ["Signal", "two"])
                    SGRail("Tol ±0.2 mm", up: true)
                }
                .frame(height: 170)
                HStack(alignment: .top, spacing: 24) {
                    SGCoordStack(["N 35.6812", "E 139.7671", "ALT 040 M"], dim: [2])
                    SGDataCallout("Tokyo", rows: [("lat", "35.68 N"), ("lon", "139.77 E"), ("grid", "TK-07")])
                }
                SGSpecGrid("ABCDEFGHIJKL0123", columns: 4)
                SGGlyphBuild("A")
                VStack(alignment: .leading, spacing: 6) {
                    Text("Panel 01").sgCap(11).foregroundStyle(SG.groundHi)
                    Text("Crosshairs centred on each corner").sgMono(10).foregroundStyle(SG.groundDim)
                }
                .padding(16)
                .frame(maxWidth: .infinity, alignment: .leading)
                .overlay(Rectangle().strokeBorder(SG.ground3, lineWidth: SG.hair))
                .sgTechFrame()
            }
            .padding(24)
        }
        .background { StripeField().ignoresSafeArea() }
    }
}

#Preview("Print furniture · dark") { SGPrintFurniturePreview().preferredColorScheme(.dark).onAppear { SGFont.register() } }
#Preview("Print furniture · light") { SGPrintFurniturePreview().preferredColorScheme(.light).onAppear { SGFont.register() } }
