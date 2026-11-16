import SwiftUI

// MARK: - Backdrops
//
// Large compositions that sit behind a screen, built only from the shape
// alphabet and the one "/" diagonal. Tonal (ground-2 / ground-3) so content
// stays legible; at most one small coral element. Geometry matches the
// gallery's bg-* symbols, drawn on a 390 x 844 reference and scaled to fit.
//
//   SGUtilityScreen(...) { ... } content: { ... }
//       .background(SGBackdrop(.tunnel).ignoresSafeArea())

public enum SGBackdropKind: CaseIterable {
    case tunnel, slashes, stackCard, stackBadge, plates, diamonds, lattice, bars, notch, wedge, ticks
}

public struct SGBackdrop: View {
    var kind: SGBackdropKind
    public init(_ kind: SGBackdropKind) { self.kind = kind }

    public var body: some View {
        Canvas { ctx, size in
            let k = size.width / 390
            ctx.scaleBy(x: k, y: k)
            let line = StrokeStyle(lineWidth: 1.5, lineCap: .square, lineJoin: .miter)

            func chamf(_ cx: CGFloat, _ cy: CGFloat, _ hw: CGFloat, _ hh: CGFloat, _ c: CGFloat) -> Path {
                Path { p in
                    p.addLines([CGPoint(x: cx - hw + c, y: cy - hh), CGPoint(x: cx + hw, y: cy - hh), CGPoint(x: cx + hw, y: cy + hh - c),
                                CGPoint(x: cx + hw - c, y: cy + hh), CGPoint(x: cx - hw, y: cy + hh), CGPoint(x: cx - hw, y: cy - hh + c)])
                    p.closeSubpath()
                }
            }
            func stack(_ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat, _ c: CGFloat, _ n: Int, _ step: CGFloat) {
                for i in stride(from: n, through: 1, by: -1) {
                    let d = CGFloat(i) * step
                    ctx.stroke(chamf(x + d + w / 2, y - d + h / 2, w / 2, h / 2, c), with: .color(i == n ? SG.ground2 : SG.ground3), style: line)
                }
            }

            switch kind {
            case .tunnel:
                var g = ctx
                g.clip(to: Path(CGRect(x: 0, y: 118, width: 390, height: 214)))
                let cx: CGFloat = 150, cy: CGFloat = 228
                g.stroke(Path { p in p.move(to: CGPoint(x: cx - 520, y: cy + 520)); p.addLine(to: CGPoint(x: cx + 520, y: cy - 520)) },
                         with: .color(SG.ground3), style: StrokeStyle(lineWidth: 1, dash: [2, 6]))
                for (i, h) in stride(from: CGFloat(18), to: 330, by: 18).enumerated() {
                    let col = i < 3 ? SG.groundHi.opacity(0.55) : SG.ground3
                    g.stroke(chamf(cx, cy, h * 1.18, h * 0.78, h * 0.3), with: .color(col), style: line)
                }
                g.fill(chamf(cx, cy, 11, 7, 3), with: .color(SG.coral))
            case .slashes:
                for i in 0..<10 {
                    let x = CGFloat(-150 + i * 64)
                    ctx.fill(Path { p in p.addLines([CGPoint(x: x, y: 560), CGPoint(x: x + 22, y: 560), CGPoint(x: x + 582, y: 0), CGPoint(x: x + 560, y: 0)]); p.closeSubpath() },
                             with: .color(SG.ground2))
                }
            case .stackCard: stack(24, 132, 342, 170, 24, 3, 14)
            case .stackBadge: stack(24, 128, 342, 300, 30, 3, 14)
            case .plates: stack(170, 40, 240, 150, 20, 4, 16)
            case .diamonds:
                for (i, c) in [(20, 560), (150, 430), (280, 300), (410, 170), (540, 40)].enumerated() {
                    let cx = CGFloat(c.0), cy = CGFloat(c.1), s: CGFloat = 96
                    let d = Path { p in p.addLines([CGPoint(x: cx, y: cy - s), CGPoint(x: cx + s, y: cy), CGPoint(x: cx, y: cy + s), CGPoint(x: cx - s, y: cy)]); p.closeSubpath() }
                    if i == 2 { ctx.fill(d, with: .color(SG.ground2)) }
                    ctx.stroke(d, with: .color(SG.ground3), style: line)
                }
            case .lattice:
                for r in 0..<12 {
                    for c in 0..<6 {
                        let x = CGFloat(c * 78 + (r % 2 == 1 ? 39 : 0) - 20), y = CGFloat(r * 78 - 10)
                        let col = (r, c) == (3, 4) ? SG.coral : SG.ground2
                        ctx.stroke(SGHardX().path(in: CGRect(x: x, y: y, width: 56, height: 56)), with: .color(col), style: StrokeStyle(lineWidth: 1.7, lineJoin: .miter))
                    }
                }
            case .bars:
                for i in 0..<20 {
                    let h = 60 + 150 * abs(sin(Double(i) * 0.61) * cos(Double(i) * 0.23 + 0.4))
                    ctx.fill(Path(CGRect(x: CGFloat(i * 20), y: 844 - CGFloat(h), width: 13, height: CGFloat(h))), with: .color(SG.ground2))
                }
            case .notch:
                ctx.stroke(Path(CGRect(x: 40, y: 232, width: 390, height: 668)), with: .color(SG.ground3), style: line)
                ctx.stroke(Path(CGRect(x: 58, y: 250, width: 372, height: 650)), with: .color(SG.ground2), style: line)
                ctx.fill(Path { p in p.addLines([CGPoint(x: 40, y: 204), CGPoint(x: 230, y: 204), CGPoint(x: 202, y: 232), CGPoint(x: 40, y: 232)]); p.closeSubpath() },
                         with: .color(SG.ground2))
            case .wedge:
                let tri = Path { p in p.addLines([CGPoint(x: 390, y: 0), CGPoint(x: 390, y: 300), CGPoint(x: 90, y: 300)]); p.closeSubpath() }
                var g = ctx
                g.clip(to: tri)
                for x in stride(from: CGFloat(96), through: 390, by: 12) { g.fill(Path(CGRect(x: x, y: 0, width: 1, height: 300)), with: .color(SG.ground2)) }
                for y in stride(from: CGFloat(0), through: 300, by: 12) { g.fill(Path(CGRect(x: 90, y: y, width: 300, height: 1)), with: .color(SG.ground2)) }
                ctx.stroke(Path { p in p.move(to: CGPoint(x: 60, y: 330)); p.addLine(to: CGPoint(x: 420, y: -30)) }, with: .color(SG.groundHi.opacity(0.5)), style: line)
                ctx.stroke(tri, with: .color(SG.ground3), style: line)
            case .ticks:
                for side in 0..<2 {
                    for (i, y) in stride(from: 130, to: 844, by: 8).enumerated() {
                        let L: CGFloat = i % 5 == 0 ? 18 : 8
                        let x = side == 0 ? 0 : 390 - L
                        ctx.fill(Path(CGRect(x: x, y: CGFloat(y), width: L, height: 1.5)), with: .color(i % 5 == 0 ? SG.groundDim : SG.ground3))
                    }
                }
                ctx.fill(Path(CGRect(x: 0, y: 434, width: 22, height: 3)), with: .color(SG.coral))
            }
        }
        .accessibilityHidden(true)
        .allowsHitTesting(false)
    }
}
