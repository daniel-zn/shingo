import SwiftUI

// MARK: - Rounded X (union of two crossed stadiums)

/// The poster's X. Fill it for the solid version, `.stroke(lineWidth:lineJoin: .round)` for the outline.
/// Proportions match tools/build.py: halfWidth 12.5 / armLength 32 in a 100-unit box.
public struct RoundedX: Shape {
    public var halfWidth: CGFloat = 12.5
    public var armLength: CGFloat = 32
    public init(halfWidth: CGFloat = 12.5, armLength: CGFloat = 32) {
        self.halfWidth = halfWidth; self.armLength = armLength
    }

    public func path(in rect: CGRect) -> Path {
        let s = min(rect.width, rect.height) / 100
        let c = CGPoint(x: rect.midX, y: rect.midY)
        let h = halfWidth * s, L = armLength * s
        let r2 = CGFloat(0.5).squareRoot()
        let inner = h * CGFloat(2).squareRoot()

        // rotate a local offset by k * 90° clockwise (y-down)
        func rot(_ p: CGPoint, _ k: Int) -> CGPoint {
            var x = p.x, y = p.y
            for _ in 0..<(k % 4) { (x, y) = (-y, x) }
            return CGPoint(x: c.x + x, y: c.y + y)
        }
        let d = CGPoint(x: r2, y: -r2), n = CGPoint(x: r2, y: r2)      // NE arm
        let capCentre = CGPoint(x: L * d.x, y: L * d.y)
        let a1 = CGPoint(x: capCentre.x - h * n.x, y: capCentre.y - h * n.y)

        var p = Path()
        p.move(to: rot(CGPoint(x: 0, y: -inner), 0))
        for k in 0..<4 {
            p.addLine(to: rot(a1, k))
            // semicircular cap: starts at 225° (+90° per arm), sweeps +180° through the arm tip
            p.addRelativeArc(center: rot(capCentre, k), radius: h,
                             startAngle: .degrees(225 + Double(k) * 90), delta: .degrees(180))
            p.addLine(to: rot(CGPoint(x: inner, y: 0), k))
        }
        p.closeSubpath()
        return p
    }
}

// MARK: - Diamond mark (rounded rhombus with an off-centre hole)

public struct DiamondMark: Shape {
    public init() {}
    public func path(in rect: CGRect) -> Path {
        let s = min(rect.width, rect.height) / 100
        let ox = rect.midX - 50 * s, oy = rect.midY - 50 * s
        var p = Path()
        p.addRoundedRect(in: CGRect(x: ox + 19 * s, y: oy + 19 * s, width: 62 * s, height: 62 * s), cornerSize: CGSize(width: 17 * s, height: 17 * s))
        p.addRoundedRect(in: CGRect(x: ox + 37 * s, y: oy + 41 * s, width: 20 * s, height: 20 * s), cornerSize: CGSize(width: 6 * s, height: 6 * s))
        let t = CGAffineTransform(translationX: rect.midX, y: rect.midY).rotated(by: .pi / 4).translatedBy(x: -rect.midX, y: -rect.midY)
        return p.applying(t)
    }
}

public extension View {
    /// The brand mark, filled with even-odd so the hole is transparent.
    func diamondMark(_ color: Color = SG.coral) -> some View {
        overlay(DiamondMark().fill(color, style: FillStyle(eoFill: true)))
    }
}

// MARK: - Chamfer frame (cut top-trailing & bottom-leading corners)

public struct ChamferRect: InsettableShape {
    public var cut: CGFloat = 16
    var inset: CGFloat = 0
    public init(cut: CGFloat = 16) { self.cut = cut }

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

public extension View {
    /// Hairline chamfer frame behind the content (fields, groups, tiles, ID cards).
    func chamferFrame(cut: CGFloat = 16, fill: Color = SG.sageHi, line: Color = SG.sageLine) -> some View {
        background(
            ChamferRect(cut: cut).fill(fill)
                .overlay(ChamferRect(cut: cut).strokeBorder(line, lineWidth: SG.hair))
        )
    }
}

// MARK: - Polygon slab (sage ground / coral band cut on a diagonal)

/// Polygon in unit coordinates (0...1). Use for slabs, coral bands and wedges.
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
        // shaft as a thick parallelogram
        path.move(to: p(13, 77)); path.addLine(to: p(57, 33)); path.addLine(to: p(67, 43)); path.addLine(to: p(23, 87)); path.closeSubpath()
        return path
    }
}
