import SwiftUI
import CoreText

// MARK: - Impressions
//
// One ink prints four ways (README rule 20). Solid is the default. Display type 40 pt and up,
// and figure readouts, may also print SCREENED (the 45° drafting hatch: a tint made the way
// print makes one), as a KEYLINE (a hairline round the letter, nothing inside) or in the
// stripe's own TONE (ground-3, felt before it is read). A poster may stack them; anything that
// must be read at a glance stays solid. Mirrors `.imp-screen`, `.imp-keyline`, `.imp-tone`
// in web/shingo.css.

public enum SGImpression {
    case solid, screen, keyline, tone
}

/// Display type in Shingo Grid Heavy, printed in one of the four impressions.
///
///     SGDisplayText("No", size: 52)
///     SGDisplayText("signal", size: 52, impression: .keyline)
public struct SGDisplayText: View {
    var text: String; var size: CGFloat; var impression: SGImpression; var ink: Color
    public init(_ text: String, size: CGFloat = 40, impression: SGImpression = .solid, ink: Color = SG.groundHi) {
        self.text = text; self.size = size; self.impression = impression; self.ink = ink
    }
    public var body: some View {
        switch impression {
        case .solid:
            label.foregroundStyle(ink)
        case .tone:
            label.foregroundStyle(SG.ground3)
        case .screen:
            // the hatch shows only where the letters are
            label.hidden()
                .overlay { SGScreenFill(ink: ink, line: max(1.5, size * 0.02), period: max(4.5, size * 0.062)) }
                .mask { label }
                .accessibilityLabel(Text(text))
        case .keyline:
            SGKeyline(text: text.uppercased(), size: size)
                .stroke(ink, style: StrokeStyle(lineWidth: max(1.5, size * 0.011), lineJoin: .miter))
                .frame(width: SGKeyline(text: text.uppercased(), size: size).advance, height: size * SGFace.capHeight)
                .accessibilityLabel(Text(text))
        }
    }
    private var label: some View { Text(text).sgWordmark(size) }
}

/// The 45° screen: hairlines rising left to right, `period` apart measured across the line.
public struct SGScreenFill: View {
    var ink: Color; var line: CGFloat; var period: CGFloat
    public init(ink: Color = SG.groundHi, line: CGFloat = 1.5, period: CGFloat = 4.5) {
        self.ink = ink; self.line = line; self.period = period
    }
    public var body: some View {
        Canvas { ctx, size in
            // level pitch and width of a 45° line `period` apart and `line` thick
            let r2 = CGFloat(2).squareRoot()
            let step = period * r2, wide = line * r2
            var x = -size.height
            while x < size.width {
                var p = Path()
                p.move(to: CGPoint(x: x, y: size.height)); p.addLine(to: CGPoint(x: x + wide, y: size.height))
                p.addLine(to: CGPoint(x: x + wide + size.height, y: 0)); p.addLine(to: CGPoint(x: x + size.height, y: 0)); p.closeSubpath()
                ctx.fill(p, with: .color(ink)); x += step
            }
        }
        .accessibilityHidden(true)
    }
}

/// The outlines of a line of Shingo Grid, as a shape to stroke: baseline on the rect's bottom edge.
public struct SGKeyline: Shape {
    var text: String; var size: CGFloat
    public init(text: String, size: CGFloat) { self.text = text; self.size = size }

    private var line: CTLine {
        let font = CTFontCreateWithName("ShingoGrid-Heavy" as CFString, size, nil)
        let attrs: [NSAttributedString.Key: Any] = [
            NSAttributedString.Key(kCTFontAttributeName as String): font,
            NSAttributedString.Key(kCTKernAttributeName as String): SGFace.tracking(size),
        ]
        return CTLineCreateWithAttributedString(NSAttributedString(string: text, attributes: attrs))
    }
    /// The line's advance width at this size.
    public var advance: CGFloat { CGFloat(CTLineGetTypographicBounds(line, nil, nil, nil)) }

    public func path(in rect: CGRect) -> Path {
        let out = CGMutablePath()
        guard let runs = CTLineGetGlyphRuns(line) as? [CTRun] else { return Path(out) }
        for run in runs {
            let attrs = CTRunGetAttributes(run) as NSDictionary
            guard let any = attrs[kCTFontAttributeName as String] else { continue }
            let font = any as! CTFont
            let n = CTRunGetGlyphCount(run)
            var glyphs = [CGGlyph](repeating: 0, count: n)
            var places = [CGPoint](repeating: .zero, count: n)
            CTRunGetGlyphs(run, CFRange(location: 0, length: 0), &glyphs)
            CTRunGetPositions(run, CFRange(location: 0, length: 0), &places)
            for i in 0..<n {
                guard let glyph = CTFontCreatePathForGlyph(font, glyphs[i], nil) else { continue }
                // glyph space is y-up from the baseline: flip it onto the rect's bottom edge
                out.addPath(glyph, transform: CGAffineTransform(a: 1, b: 0, c: 0, d: -1, tx: rect.minX + places[i].x, ty: rect.maxY))
            }
        }
        return Path(out)
    }
}

private struct SGImpressionPreview: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            SGDisplayText("Axiom", size: 64)
            SGDisplayText("Axiom", size: 64, impression: .screen)
            SGDisplayText("Axiom", size: 64, impression: .keyline)
            SGDisplayText("Axiom", size: 64, impression: .tone)
        }
        .padding(SG.gutter)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .background(StripeField())
    }
}

#Preview("Impressions · dark") { SGImpressionPreview().preferredColorScheme(.dark).onAppear { SGFont.register() } }
#Preview("Impressions · light") { SGImpressionPreview().preferredColorScheme(.light).onAppear { SGFont.register() } }
