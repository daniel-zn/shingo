import SwiftUI

// Three languages: English runs the interface, Japanese adds texture,
// French is the aside. See the "Three languages" section of the gallery
// and tokens/lexicon.json for the phrase list.

public extension SGFont {
    /// Japanese gothic. Hiragino Sans ships with iOS, so nothing to bundle.
    static func jp(_ size: CGFloat, bold: Bool = true) -> Font {
        .custom(bold ? "HiraginoSans-W6" : "HiraginoSans-W3", size: size)
    }
    /// French asides: Archivo Medium Italic (bundled).
    static func fr(_ size: CGFloat) -> Font { .custom("Archivo-MediumItalic", size: size) }
}

public extension View {
    func sgJP(_ size: CGFloat, bold: Bool = true) -> some View { font(SGFont.jp(size, bold: bold)).tracking(size * 0.04) }
    func sgFR(_ size: CGFloat = 13) -> some View { font(SGFont.fr(size)).tracking(-size * 0.02) }
}

// MARK: - Vertical Japanese (tategaki)

/// SwiftUI has no vertical writing mode. Stacking glyphs works for kanji and kana;
/// the long-vowel mark ー is swapped for its vertical form ｜.
public struct VerticalText: View {
    var text: String; var size: CGFloat; var spacing: CGFloat; var bold: Bool
    public init(_ text: String, size: CGFloat = 11, spacing: CGFloat = 0.32, bold: Bool = false) {
        self.text = text; self.size = size; self.spacing = spacing; self.bold = bold
    }
    public var body: some View {
        VStack(spacing: size * spacing) {
            ForEach(Array(text.enumerated()), id: \.offset) { _, ch in
                Text(ch == "ー" ? "｜" : String(ch)).font(SGFont.jp(size, bold: bold))
            }
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(Text(text))
    }
}

// MARK: - Hanko seal

public struct Hanko: View {
    var text: String; var size: CGFloat; var color: Color
    public init(_ text: String, size: CGFloat = 56, color: Color = SG.coral) {
        self.text = text; self.size = size; self.color = color
    }
    public var body: some View {
        VerticalText(text, size: size * 0.3, spacing: 0.1, bold: true)
            .foregroundStyle(color)
            .frame(width: size, height: size)
            .overlay(RoundedRectangle(cornerRadius: 4).strokeBorder(color, lineWidth: 2.5))
            .rotationEffect(.degrees(-4))
    }
}

// MARK: - Print motifs

/// Diagonal hazard stripes between two hairlines.
public struct HazardBar: View {
    public var color: Color = SG.sageHi
    public init(color: Color = SG.sageHi) { self.color = color }
    public var body: some View {
        Canvas { ctx, size in
            ctx.fill(Path(CGRect(x: 0, y: 0, width: size.width, height: 1.5)), with: .color(color))
            ctx.fill(Path(CGRect(x: 0, y: size.height - 1.5, width: size.width, height: 1.5)), with: .color(color))
            let top: CGFloat = 5.5, h = size.height - 11
            var inner = ctx
            inner.clip(to: Path(CGRect(x: 0, y: top, width: size.width, height: h)))
            var x: CGFloat = -h
            while x < size.width + h {
                var p = Path()
                p.move(to: CGPoint(x: x, y: top + h)); p.addLine(to: CGPoint(x: x + 15.5, y: top + h))
                p.addLine(to: CGPoint(x: x + 15.5 + h, y: top)); p.addLine(to: CGPoint(x: x + h, y: top)); p.closeSubpath()
                inner.fill(p, with: .color(color))
                x += 31
            }
        }
        .frame(height: 26)
        .accessibilityHidden(true)
    }
}

/// Nested chevrons with broken left arms (same geometry as assets/svg/chevrons.svg, 300 x 230).
public struct ChevronStack: View {
    public var color: Color = SG.sageHi
    public init(color: Color = SG.sageHi) { self.color = color }
    public var body: some View {
        Canvas { ctx, size in
            let s = min(size.width / 300, size.height / 230)
            ctx.translateBy(x: (size.width - 300 * s) / 2, y: (size.height - 230 * s) / 2)
            ctx.scaleBy(x: s, y: s)
            ctx.clip(to: Path(CGRect(x: 0, y: 0, width: 300, height: 230)))
            for (ay, gap) in zip([18.0, 82, 146, 210], [70.0, 150, 40, 112]) {
                var p = Path()
                p.move(to: CGPoint(x: -30, y: ay + 180)); p.addLine(to: CGPoint(x: 150, y: ay)); p.addLine(to: CGPoint(x: 330, y: ay + 180))
                ctx.stroke(p, with: .color(color), style: StrokeStyle(lineWidth: 26, lineJoin: .miter, dash: [gap, 16, 9999]))
            }
            var tl = Path(); tl.move(to: .zero); tl.addLine(to: CGPoint(x: 62, y: 0)); tl.addLine(to: CGPoint(x: 0, y: 62)); tl.closeSubpath()
            var tr = Path(); tr.move(to: CGPoint(x: 300, y: 0)); tr.addLine(to: CGPoint(x: 300, y: 44)); tr.addLine(to: CGPoint(x: 256, y: 0)); tr.closeSubpath()
            ctx.fill(tl, with: .color(color)); ctx.fill(tr, with: .color(color))
        }
        .aspectRatio(300 / 230, contentMode: .fit)
        .accessibilityHidden(true)
    }
}

/// Line-art head in profile (stroke it).
public struct HeadProfile: Shape {
    public init() {}
    public func path(in rect: CGRect) -> Path {
        let s = min(rect.width, rect.height) / 100
        func p(_ x: CGFloat, _ y: CGFloat) -> CGPoint { CGPoint(x: rect.minX + x * s, y: rect.minY + y * s) }
        var path = Path()
        path.move(to: p(32, 94))
        path.addCurve(to: p(26, 66), control1: p(32, 82), control2: p(27, 76))
        path.addCurve(to: p(33, 18), control1: p(17, 54), control2: p(17, 30))
        path.addCurve(to: p(76, 29), control1: p(47, 7), control2: p(70, 11))
        path.addCurve(to: p(83, 50), control1: p(79, 37), control2: p(79, 43))
        path.addLine(to: p(78, 54))
        path.addCurve(to: p(76, 64), control1: p(80, 58), control2: p(78, 62))
        path.addCurve(to: p(62, 73), control1: p(74, 70), control2: p(68, 73))
        path.addLine(to: p(62, 94))
        path.move(to: p(40, 15)); path.addCurve(to: p(44, 47), control1: p(47, 29), control2: p(47, 39))
        path.addCurve(to: p(46, 57), control1: p(51, 44), control2: p(54, 55))
        path.move(to: p(26, 66)); path.addCurve(to: p(46, 57), control1: p(36, 64), control2: p(44, 60))
        return path
    }
}

/// "20 ———— 26"
public struct YearSpan: View {
    var from: String; var to: String; var size: CGFloat
    public init(_ from: String = "20", _ to: String = "26", size: CGFloat = 21) { self.from = from; self.to = to; self.size = size }
    public var body: some View {
        HStack(spacing: 12) {
            Text(from).sgNumber(size)
            Rectangle().frame(height: 1.5)
            Text(to).sgNumber(size)
        }
    }
}

// MARK: - Example: manifesto lock screen (gallery screen N)

public struct ManifestoExample: View {
    public init() {}
    public var body: some View {
        ZStack {
            Color(hex: 0x121210).ignoresSafeArea()
            StripeField(angle: .degrees(-38)).opacity(0.55).ignoresSafeArea()
            VStack(alignment: .leading, spacing: 11) {
                Text("AXIOM").sgWordmark(54)
                HStack {
                    Text("lundi 16 novembre").sgFR(14)
                    Spacer()
                    Text("9:41").sgNumber(14)
                }
                HStack(spacing: 14) {
                    UnitPolygon([.init(x: 0, y: 0), .init(x: 1, y: 0), .init(x: 1, y: 0.71), .init(x: 0.95, y: 1), .init(x: 0, y: 1)])
                        .fill(SG.coral).frame(height: 56)
                    HeadProfile().stroke(SG.sageHi, style: StrokeStyle(lineWidth: 1.6, lineCap: .round, lineJoin: .round))
                        .frame(width: 60, height: 60)
                }
                YearSpan()
                VStack(alignment: .leading, spacing: 3) {
                    Text("SIGNAL ENGINEERING").font(.custom("Archivo-Bold", size: 23))
                    HStack { ForEach(Array("信号工学"), id: \.self) { Text(String($0)).sgJP(22); if $0 != "学" { Spacer() } } }
                    Text("INGÉNIERIE DU SIGNAL").font(.custom("Archivo-Bold", size: 23))
                }
                ChevronStack().padding(.horizontal, 24)
                HazardBar()
                Text("AXIOM SIGNAL SYSTEMS").font(.custom("Archivo-Bold", size: 15))
                Barcode(axis: .horizontal, color: SG.sageHi).frame(height: 30)
            }
            .foregroundStyle(SG.sageHi)
            .padding(.horizontal, 28)
        }
    }
}

#Preview("N · Manifesto") { ManifestoExample().onAppear { SGFont.register() } }
