import SwiftUI

// MARK: - Stripe field (the poster's dark ground)

/// Soft-edged diagonal stripes. Add `facets` to rotate stripes inside polygons,
/// like the folded-paper ground in the poster.
public struct StripeField: View {
    public struct Facet {
        public var angle: Angle
        public var polygon: [UnitPoint]
        public init(angle: Angle, polygon: [UnitPoint]) { self.angle = angle; self.polygon = polygon }
    }
    public var angle: Angle = .degrees(-36)
    public var period: CGFloat = SG.stripePeriod
    public var facets: [Facet] = []

    public init(angle: Angle = .degrees(-36), period: CGFloat = SG.stripePeriod, facets: [Facet] = []) {
        self.angle = angle; self.period = period; self.facets = facets
    }

    public var body: some View {
        Canvas { ctx, size in
            ctx.fill(Path(CGRect(origin: .zero, size: size)), with: .color(SG.ink))
            Self.stripes(in: &ctx, size: size, angle: angle, period: period)
            for f in facets {
                var sub = ctx
                sub.clip(to: UnitPolygon(f.polygon).path(in: CGRect(origin: .zero, size: size)))
                sub.fill(Path(CGRect(origin: .zero, size: size)), with: .color(SG.ink))
                Self.stripes(in: &sub, size: size, angle: f.angle, period: period)
            }
        }
        .drawingGroup()
        .accessibilityHidden(true)
    }

    static func stripes(in ctx: inout GraphicsContext, size: CGSize, angle: Angle, period: CGFloat) {
        var g = ctx
        let diag = (size.width * size.width + size.height * size.height).squareRoot()
        g.translateBy(x: size.width / 2, y: size.height / 2)
        g.rotate(by: angle)
        let grad = Gradient(colors: [SG.ink, SG.ink2, SG.ink])
        var y = -diag / 2
        while y < diag / 2 {
            let r = CGRect(x: -diag / 2, y: y, width: diag, height: period)
            g.fill(Path(r), with: .linearGradient(grad, startPoint: CGPoint(x: 0, y: r.minY), endPoint: CGPoint(x: 0, y: r.maxY)))
            y += period
        }
    }
}

// MARK: - Barcode (horizontal or vertical line groups)

public struct Barcode: View {
    public var axis: Axis = .vertical
    public var color: Color = SG.ink
    public init(axis: Axis = .vertical, color: Color = SG.ink) { self.axis = axis; self.color = color }
    public var body: some View {
        Canvas { ctx, size in
            let pattern: [(CGFloat, CGFloat)] = [(2, 3), (1, 3), (1, 5), (2, 2), (3, 2), (1, 4)] // (line, gap)
            var pos: CGFloat = 0, i = 0
            let length = axis == .vertical ? size.height : size.width
            while pos < length {
                let (w, gap) = pattern[i % pattern.count]
                let r = axis == .vertical ? CGRect(x: 0, y: pos, width: size.width, height: w)
                                          : CGRect(x: pos, y: 0, width: w, height: size.height)
                ctx.fill(Path(r), with: .color(color))
                pos += w + gap; i += 1
            }
        }
        .accessibilityHidden(true)
    }
}

// MARK: - Rings coil / record disc / radar

/// Row of overlapping circles (the poster's tube of rings).
public struct RingsCoil: View {
    public var color: Color = SG.coral
    public var count = 16
    public init(color: Color = SG.coral, count: Int = 16) { self.color = color; self.count = count }
    public var body: some View {
        Canvas { ctx, size in
            let r = size.height / 2 - 1
            let step = (size.width - 2 * r) / CGFloat(max(count - 1, 1))
            for i in 0..<count {
                let c = CGPoint(x: r + CGFloat(i) * step, y: size.height / 2)
                ctx.stroke(Path(ellipseIn: CGRect(x: c.x - r, y: c.y - r, width: 2 * r, height: 2 * r)), with: .color(color), lineWidth: 1.2)
            }
        }
        .accessibilityHidden(true)
    }
}

public struct RecordDisc: View {
    public var label: Color = SG.coral
    public init(label: Color = SG.coral) { self.label = label }
    public var body: some View {
        Canvas { ctx, size in
            let s = min(size.width, size.height), c = CGPoint(x: size.width / 2, y: size.height / 2)
            ctx.fill(Path(ellipseIn: CGRect(x: c.x - s / 2, y: c.y - s / 2, width: s, height: s)), with: .color(SG.sage))
            let inner = s / 2 - s * 0.055
            ctx.fill(Path(ellipseIn: CGRect(x: c.x - inner, y: c.y - inner, width: 2 * inner, height: 2 * inner)), with: .color(SG.sageHi))
            var r = inner * 0.92
            while r > s * 0.16 {
                ctx.stroke(Path(ellipseIn: CGRect(x: c.x - r, y: c.y - r, width: 2 * r, height: 2 * r)), with: .color(SG.ink), lineWidth: 0.9)
                r -= s * 0.028
            }
            let lr = s * 0.15
            ctx.fill(Path(ellipseIn: CGRect(x: c.x - lr, y: c.y - lr, width: 2 * lr, height: 2 * lr)), with: .color(label))
        }
        .aspectRatio(1, contentMode: .fit)
        .accessibilityHidden(true)
    }
}

/// Concentric radar with a coral angular sweep. Animate `sweep` for a live scan.
public struct RadarScope: View {
    public var sweep: Angle = .degrees(20)
    public init(sweep: Angle = .degrees(20)) { self.sweep = sweep }
    public var body: some View {
        ZStack {
            ForEach(1..<5) { i in
                Circle().stroke(SG.ink3, lineWidth: 2).scaleEffect(CGFloat(i) / 4)
            }
            Circle().fill(AngularGradient(colors: [SG.coral.opacity(0.55), SG.coral.opacity(0), .clear, .clear],
                                          center: .center, startAngle: sweep - .degrees(90), endAngle: sweep + .degrees(270)))
            Crosshair().stroke(SG.ink3, lineWidth: SG.hair)
        }
        .aspectRatio(1, contentMode: .fit)
    }
}
