import SwiftUI

// MARK: - Stripe field (the ground everything is printed on)

/// Soft-edged stripes at the system's one 45° angle. Add `facets` to rotate
/// stripes inside polygons for a folded-paper ground on poster screens.
public struct StripeField: View {
    public struct Facet {
        public var angle: Angle
        public var polygon: [UnitPoint]
        public init(angle: Angle, polygon: [UnitPoint]) { self.angle = angle; self.polygon = polygon }
    }
    public var angle: Angle = .degrees(45)
    public var period: CGFloat = SG.stripePeriod
    public var facets: [Facet] = []

    public init(angle: Angle = .degrees(45), period: CGFloat = SG.stripePeriod, facets: [Facet] = []) {
        self.angle = angle; self.period = period; self.facets = facets
    }

    public var body: some View {
        Canvas { ctx, size in
            ctx.fill(Path(CGRect(origin: .zero, size: size)), with: .color(SG.ground))
            Self.stripes(in: &ctx, size: size, angle: angle, period: period)
            for f in facets {
                var sub = ctx
                sub.clip(to: UnitPolygon(f.polygon).path(in: CGRect(origin: .zero, size: size)))
                sub.fill(Path(CGRect(origin: .zero, size: size)), with: .color(SG.ground))
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
        let grad = Gradient(colors: [SG.ground, SG.ground2, SG.ground])
        var y = -diag / 2
        while y < diag / 2 {
            let r = CGRect(x: -diag / 2, y: y, width: diag, height: period)
            g.fill(Path(r), with: .linearGradient(grad, startPoint: CGPoint(x: 0, y: r.minY), endPoint: CGPoint(x: 0, y: r.maxY)))
            y += period
        }
    }
}

// MARK: - Barcode

public struct Barcode: View {
    public var axis: Axis = .vertical
    public var color: Color = SG.groundHi
    public init(axis: Axis = .vertical, color: Color = SG.groundHi) { self.axis = axis; self.color = color }
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

// MARK: - Spectrum (music hero)

/// 40 printed bars, same heights as assets/svg/spectrum.svg. `playhead` 0...1 draws a coral line.
public struct Spectrum: View {
    public var playhead: Double?
    public init(playhead: Double? = 0.4) { self.playhead = playhead }
    public var body: some View {
        Canvas { ctx, size in
            let n = 40, step = size.width / CGFloat(n)
            for i in 0..<n {
                let k = abs(sin(Double(i) * 0.53) * cos(Double(i) * 0.21 + 1.1))
                let h = size.height * CGFloat((10 + 62 * k) / 80)
                ctx.fill(Path(CGRect(x: CGFloat(i) * step, y: size.height - h, width: step * 0.58, height: h)), with: .color(SG.groundHi))
            }
            if let ph = playhead {
                ctx.fill(Path(CGRect(x: size.width * ph, y: 0, width: 2, height: size.height)), with: .color(SG.coral))
            }
        }
        .accessibilityHidden(true)
    }
}

// MARK: - Scope (radar hero): octagons, crosshair, coral sweep

public struct Scope: View {
    public var sweep: Angle = .degrees(-30)
    public init(sweep: Angle = .degrees(-30)) { self.sweep = sweep }
    public var body: some View {
        Canvas { ctx, size in
            let c = CGPoint(x: size.width / 2, y: size.height / 2)
            let R = min(size.width, size.height) / 2 - 2
            func octagon(_ r: CGFloat) -> Path {
                var p = Path()
                for k in 0..<8 {
                    let a = Double.pi / 8 + Double(k) * Double.pi / 4
                    let pt = CGPoint(x: c.x + r * CGFloat(cos(a)), y: c.y + r * CGFloat(sin(a)))
                    if k == 0 { p.move(to: pt) } else { p.addLine(to: pt) }
                }
                p.closeSubpath(); return p
            }
            for f in [1.0, 0.76, 0.52, 0.28] {
                ctx.stroke(octagon(R * CGFloat(f)), with: .color(SG.groundHi.opacity(0.55)), lineWidth: 1.2)
            }
            var cross = Path()
            cross.move(to: CGPoint(x: c.x, y: c.y - R)); cross.addLine(to: CGPoint(x: c.x, y: c.y + R))
            cross.move(to: CGPoint(x: c.x - R, y: c.y)); cross.addLine(to: CGPoint(x: c.x + R, y: c.y))
            ctx.stroke(cross, with: .color(SG.groundHi.opacity(0.35)), lineWidth: 1)
            var wedge = Path()
            wedge.move(to: c)
            wedge.addLine(to: CGPoint(x: c.x + R * CGFloat(cos(sweep.radians - 0.2)), y: c.y + R * CGFloat(sin(sweep.radians - 0.2))))
            wedge.addLine(to: CGPoint(x: c.x + R * CGFloat(cos(sweep.radians + 0.2)), y: c.y + R * CGFloat(sin(sweep.radians + 0.2))))
            wedge.closeSubpath()
            ctx.fill(wedge, with: .color(SG.coral.opacity(0.5)))
        }
        .aspectRatio(1, contentMode: .fit)
        .accessibilityHidden(true)
    }
}
