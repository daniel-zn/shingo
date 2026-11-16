import SwiftUI

// One angle: every cut and diagonal is 45°. Chamfers sit on the
// top-trailing / bottom-leading axis. Nothing is rounded.

// MARK: - Hard X (two crossed bars with square-cut ends)

public struct SGHardX: Shape {
    public var halfWidth: CGFloat = 9.5
    public var armLength: CGFloat = 34
    public init(halfWidth: CGFloat = 9.5, armLength: CGFloat = 34) {
        self.halfWidth = halfWidth; self.armLength = armLength
    }
    public func path(in rect: CGRect) -> Path {
        let s = min(rect.width, rect.height) / 100
        let c = CGPoint(x: rect.midX, y: rect.midY)
        let h = halfWidth * s, L = armLength * s
        let r2 = CGFloat(0.5).squareRoot()
        let inner = h * CGFloat(2).squareRoot()
        func rot(_ p: CGPoint, _ k: Int) -> CGPoint {
            var x = p.x, y = p.y
            for _ in 0..<(k % 4) { (x, y) = (-y, x) }
            return CGPoint(x: c.x + x, y: c.y + y)
        }
        let d = CGPoint(x: r2, y: -r2), n = CGPoint(x: r2, y: r2)
        let a1 = CGPoint(x: L * d.x - h * n.x, y: L * d.y - h * n.y)
        let a2 = CGPoint(x: L * d.x + h * n.x, y: L * d.y + h * n.y)
        var p = Path()
        p.move(to: rot(CGPoint(x: 0, y: -inner), 0))
        for k in 0..<4 {
            p.addLine(to: rot(a1, k))
            p.addLine(to: rot(a2, k))
            p.addLine(to: rot(CGPoint(x: inner, y: 0), k))
        }
        p.closeSubpath()
        return p
    }
}

// MARK: - Diamond mark (sharp rhombus with an off-centre square hole)

public struct DiamondMark: Shape {
    public init() {}
    public func path(in rect: CGRect) -> Path {
        let s = min(rect.width, rect.height) / 100
        let ox = rect.midX - 50 * s, oy = rect.midY - 50 * s
        var p = Path()
        p.addRect(CGRect(x: ox + 20 * s, y: oy + 20 * s, width: 60 * s, height: 60 * s))
        p.addRect(CGRect(x: ox + 38 * s, y: oy + 42 * s, width: 20 * s, height: 20 * s))
        let t = CGAffineTransform(translationX: rect.midX, y: rect.midY).rotated(by: .pi / 4).translatedBy(x: -rect.midX, y: -rect.midY)
        return p.applying(t)
    }
}

// MARK: - Chamfer (cut top-trailing & bottom-leading corners)

public struct ChamferRect: InsettableShape {
    public var cut: CGFloat = SG.cutM
    var inset: CGFloat = 0
    public init(cut: CGFloat = SG.cutM) { self.cut = cut }
    public func path(in rect: CGRect) -> Path {
        let r = rect.insetBy(dx: inset, dy: inset)
        let c = max(0, cut - inset * 0.41)
        var p = Path()
        p.move(to: CGPoint(x: r.minX, y: r.minY))
        p.addLine(to: CGPoint(x: r.maxX - c, y: r.minY))
        p.addLine(to: CGPoint(x: r.maxX, y: r.minY + c))
        p.addLine(to: CGPoint(x: r.maxX, y: r.maxY))
        p.addLine(to: CGPoint(x: r.minX + c, y: r.maxY))
        p.addLine(to: CGPoint(x: r.minX, y: r.maxY - c))
        p.closeSubpath()
        return p
    }
    public func inset(by amount: CGFloat) -> ChamferRect { var s = self; s.inset += amount; return s }
}

/// A single 45° cut on one bottom corner (the shirt's tag slab, the bar's end).
public struct TagCut: Shape {
    public enum Corner { case bottomTrailing, bottomLeading }
    public var cut: CGFloat
    public var corner: Corner
    public init(cut: CGFloat = 16, corner: Corner = .bottomTrailing) { self.cut = cut; self.corner = corner }
    public func path(in rect: CGRect) -> Path {
        let c = min(cut, rect.height, rect.width)
        var p = Path()
        p.move(to: CGPoint(x: rect.minX, y: rect.minY))
        p.addLine(to: CGPoint(x: rect.maxX, y: rect.minY))
        switch corner {
        case .bottomTrailing:
            p.addLine(to: CGPoint(x: rect.maxX, y: rect.maxY - c))
            p.addLine(to: CGPoint(x: rect.maxX - c, y: rect.maxY))
            p.addLine(to: CGPoint(x: rect.minX, y: rect.maxY))
        case .bottomLeading:
            p.addLine(to: CGPoint(x: rect.maxX, y: rect.maxY))
            p.addLine(to: CGPoint(x: rect.minX + c, y: rect.maxY))
            p.addLine(to: CGPoint(x: rect.minX, y: rect.maxY - c))
        }
        p.closeSubpath()
        return p
    }
}

/// HUD corner brackets. Stroke it.
public struct Brackets: Shape {
    public var length: CGFloat = 12
    public init(length: CGFloat = 12) { self.length = length }
    public func path(in r: CGRect) -> Path {
        let l = length
        var p = Path()
        p.move(to: CGPoint(x: r.minX, y: r.minY + l)); p.addLine(to: CGPoint(x: r.minX, y: r.minY)); p.addLine(to: CGPoint(x: r.minX + l, y: r.minY))
        p.move(to: CGPoint(x: r.maxX - l, y: r.minY)); p.addLine(to: CGPoint(x: r.maxX, y: r.minY)); p.addLine(to: CGPoint(x: r.maxX, y: r.minY + l))
        p.move(to: CGPoint(x: r.maxX, y: r.maxY - l)); p.addLine(to: CGPoint(x: r.maxX, y: r.maxY)); p.addLine(to: CGPoint(x: r.maxX - l, y: r.maxY))
        p.move(to: CGPoint(x: r.minX + l, y: r.maxY)); p.addLine(to: CGPoint(x: r.minX, y: r.maxY)); p.addLine(to: CGPoint(x: r.minX, y: r.maxY - l))
        return p
    }
}

public extension View {
    /// Hairline chamfer frame behind the content (tiles, fields, scopes).
    func chamferFrame(cut: CGFloat = SG.cutM, fill: Color = SG.ground, line: Color = SG.ground3) -> some View {
        background(
            ChamferRect(cut: cut).fill(fill)
                .overlay(ChamferRect(cut: cut).strokeBorder(line, lineWidth: SG.hair))
        )
    }
    /// A filled plate with a chamfer (keys, cards, badges).
    func plate(cut: CGFloat = SG.cutM) -> some View {
        foregroundStyle(SG.ink).background(ChamferRect(cut: cut).fill(SG.sageHi))
    }
    /// HUD brackets around the content.
    func brackets(_ color: Color = SG.groundHi, length: CGFloat = 12) -> some View {
        overlay(Brackets(length: length).stroke(color, lineWidth: SG.hair))
    }
}

// MARK: - Polygon in unit coordinates (bands, wedges)

public struct UnitPolygon: Shape {
    public var points: [UnitPoint]
    public init(_ points: [UnitPoint]) { self.points = points }
    public func path(in rect: CGRect) -> Path {
        var p = Path()
        guard let first = points.first else { return p }
        func pt(_ u: UnitPoint) -> CGPoint { CGPoint(x: rect.minX + u.x * rect.width, y: rect.minY + u.y * rect.height) }
        p.move(to: pt(first))
        points.dropFirst().forEach { p.addLine(to: pt($0)) }
        p.closeSubpath()
        return p
    }
}

// MARK: - Small glyphs

public struct Crosshair: Shape {
    public init() {}
    public func path(in rect: CGRect) -> Path {
        var p = Path()
        p.move(to: CGPoint(x: rect.midX, y: rect.minY)); p.addLine(to: CGPoint(x: rect.midX, y: rect.maxY))
        p.move(to: CGPoint(x: rect.minX, y: rect.midY)); p.addLine(to: CGPoint(x: rect.maxX, y: rect.midY))
        return p
    }
}

/// Filled north-east arrow. Rotate for other directions (90° = south-east).
public struct ArrowNE: Shape {
    public init() {}
    public func path(in rect: CGRect) -> Path {
        let s = min(rect.width, rect.height) / 100
        func p(_ x: CGFloat, _ y: CGFloat) -> CGPoint { CGPoint(x: rect.minX + x * s, y: rect.minY + y * s) }
        var path = Path()
        path.move(to: p(36, 18)); path.addLine(to: p(82, 18)); path.addLine(to: p(82, 64)); path.closeSubpath()
        path.move(to: p(13, 77)); path.addLine(to: p(57, 33)); path.addLine(to: p(67, 43)); path.addLine(to: p(23, 87)); path.closeSubpath()
        return path
    }
}

/// Four stepped bars (signal strength). `level` 0...4 controls how many are drawn solid.
public struct SignalBars: View {
    public var level: Int
    public init(level: Int = 4) { self.level = level }
    public var body: some View {
        HStack(alignment: .bottom, spacing: 2) {
            ForEach(0..<4) { i in
                Rectangle().opacity(i < level ? 1 : 0.25).frame(height: CGFloat(i + 1) * 4.5)
            }
        }
        .frame(width: 20, height: 18, alignment: .bottom)
    }
}
