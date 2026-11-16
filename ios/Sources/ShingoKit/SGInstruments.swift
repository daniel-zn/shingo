import SwiftUI

// Instruments: useful, decorative parts extrapolated from the system.
// Each one is built from existing motifs: the 45° cut, the hazard stripe,
// ticks, plates and the coral signal. Mirrors the "instruments" section of
// web/shingo.css and the gallery's section 05.

// MARK: - Seven-segment readout

public struct SGSegDisplay: View {
    public var text: String
    public var height: CGFloat
    /// Character indexes drawn in coral.
    public var hot: Set<Int>
    public var ghost: Bool
    public init(_ text: String, height: CGFloat = 48, hot: Set<Int> = [], ghost: Bool = true) {
        self.text = text; self.height = height; self.hot = hot; self.ghost = ghost
    }

    static let map: [Character: String] = ["0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd",
                                           "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg", "-": "g", " ": ""]

    private var unitWidth: CGFloat {
        text.reduce(CGFloat(0)) { $0 + (($1 == "." || $1 == ":") ? 15 : 44) } - 8 + 10
    }

    public var body: some View {
        Canvas { ctx, size in
            let s = size.height / 64
            ctx.translateBy(x: 9 * s, y: 0)
            ctx.concatenate(CGAffineTransform(a: 1, b: 0, c: -0.1405, d: 1, tx: 0, ty: 0)) // skewX(-8°)
            ctx.scaleBy(x: s, y: s)
            let t: CGFloat = 7, w: CGFloat = 36, h: CGFloat = 64, g: CGFloat = 1.6
            func hseg(_ x0: CGFloat, _ x1: CGFloat, _ yc: CGFloat) -> Path {
                Path { p in p.addLines([CGPoint(x: x0, y: yc), CGPoint(x: x0 + t/2, y: yc - t/2), CGPoint(x: x1 - t/2, y: yc - t/2),
                                        CGPoint(x: x1, y: yc), CGPoint(x: x1 - t/2, y: yc + t/2), CGPoint(x: x0 + t/2, y: yc + t/2)]); p.closeSubpath() }
            }
            func vseg(_ xc: CGFloat, _ y0: CGFloat, _ y1: CGFloat) -> Path {
                Path { p in p.addLines([CGPoint(x: xc, y: y0), CGPoint(x: xc + t/2, y: y0 + t/2), CGPoint(x: xc + t/2, y: y1 - t/2),
                                        CGPoint(x: xc, y: y1), CGPoint(x: xc - t/2, y: y1 - t/2), CGPoint(x: xc - t/2, y: y0 + t/2)]); p.closeSubpath() }
            }
            let x0 = t/2 + g, x1 = w - t/2 - g, m = h/2
            let segs: [Character: Path] = ["a": hseg(x0, x1, t/2), "g": hseg(x0, x1, m), "d": hseg(x0, x1, h - t/2),
                                           "f": vseg(t/2, t/2 + g, m - g), "b": vseg(w - t/2, t/2 + g, m - g),
                                           "e": vseg(t/2, m + g, h - t/2 - g), "c": vseg(w - t/2, m + g, h - t/2 - g)]
            var x: CGFloat = 0
            for (i, ch) in text.enumerated() {
                let lit: Color = hot.contains(i) ? SG.coral : SG.groundHi
                if ch == "." {
                    ctx.fill(Path(CGRect(x: x, y: h - 7, width: 7, height: 7)), with: .color(lit)); x += 15; continue
                }
                if ch == ":" {
                    ctx.fill(Path(CGRect(x: x, y: h * 0.28, width: 7, height: 7)), with: .color(lit))
                    ctx.fill(Path(CGRect(x: x, y: h * 0.64, width: 7, height: 7)), with: .color(lit)); x += 15; continue
                }
                let on = Self.map[ch] ?? ""
                for (k, path) in segs where on.contains(k) || ghost {
                    ctx.fill(path.offsetBy(dx: x, dy: 0), with: .color(on.contains(k) ? lit : SG.ground3))
                }
                x += 44
            }
        }
        .frame(width: height * unitWidth / 64, height: height)
        .accessibilityLabel(Text(text))
    }
}

// MARK: - Cell meter

public struct SGCellMeter: View {
    public var count: Int, filled: Int, hot: Int?, tall: Bool
    public init(count: Int = 12, filled: Int, hot: Int? = nil, tall: Bool = false) {
        self.count = count; self.filled = filled; self.hot = hot; self.tall = tall
    }
    public var body: some View {
        HStack(spacing: 3) {
            ForEach(0..<count, id: \.self) { i in
                Rectangle()
                    .fill(i == hot ? SG.coral : (i < filled ? SG.groundHi : SG.ground3))
                    .frame(height: tall ? 22 : 14)
                    .transformEffect(CGAffineTransform(a: 1, b: 0, c: -0.577, d: 1, tx: (tall ? 22 : 14) * 0.577, ty: 0)) // skewX(-30°)
            }
        }
        .accessibilityValue(Text("\(filled) of \(count)"))
    }
}

// MARK: - Ruler slider

public struct SGRuler: View {
    @Binding var value: Double          // 0...1
    var labels: [String]
    public init(value: Binding<Double>, labels: [String] = ["0", "20", "40", "60", "80", "100"]) {
        _value = value; self.labels = labels
    }
    public var body: some View {
        VStack(spacing: 5) {
            GeometryReader { g in
                let w = g.size.width
                ZStack(alignment: .topLeading) {
                    Canvas { ctx, size in
                        for i in 0...50 {
                            let x = min(size.width - 1.5, size.width * CGFloat(i) / 50)
                            let major = i % 5 == 0
                            ctx.fill(Path(CGRect(x: x, y: major ? 12 : 24, width: major ? 1.5 : 1, height: major ? 22 : 10)),
                                     with: .color(major ? SG.groundHi : SG.groundDim))
                        }
                    }
                    Path { p in p.move(to: CGPoint(x: -6, y: 0)); p.addLine(to: CGPoint(x: 6, y: 0)); p.addLine(to: CGPoint(x: 0, y: 10)); p.closeSubpath() }
                        .fill(SG.coral).offset(x: w * value)
                    Rectangle().fill(SG.coral).frame(width: 2, height: 24).offset(x: w * value - 1, y: 10)
                }
                .contentShape(Rectangle())
                .gesture(DragGesture(minimumDistance: 0).onChanged { value = min(1, max(0, $0.location.x / w)) })
            }
            .frame(height: 34)
            HStack { ForEach(labels.indices, id: \.self) { i in Text(labels[i]); if i < labels.count - 1 { Spacer() } } }
                .sgMono(10).foregroundStyle(SG.groundDim)
        }
        .accessibilityElement()
        .accessibilityValue(Text("\(Int(value * 100))"))
        .accessibilityAdjustableAction { dir in value = min(1, max(0, value + (dir == .increment ? 0.05 : -0.05))) }
    }
}

// MARK: - Chevron steps

public struct SGSteps: View {
    public var steps: [String]; public var current: Int
    public init(_ steps: [String], current: Int) { self.steps = steps; self.current = current }
    public var body: some View {
        HStack(spacing: 3) {
            ForEach(steps.indices, id: \.self) { i in
                Text(steps[i]).sgCap(11)
                    .frame(maxWidth: .infinity, minHeight: 30)
                    .foregroundStyle(i < current ? SG.ground : (i == current ? SG.inkFixed : SG.groundDim))
                    .background(ChevronShape(notch: i > 0).fill(i < current ? SG.groundHi : (i == current ? SG.coral : SG.ground3)))
            }
        }
    }
    struct ChevronShape: Shape {
        var notch: Bool
        func path(in r: CGRect) -> Path {
            Path { p in
                p.move(to: CGPoint(x: r.minX, y: r.minY)); p.addLine(to: CGPoint(x: r.maxX - 11, y: r.minY))
                p.addLine(to: CGPoint(x: r.maxX, y: r.midY)); p.addLine(to: CGPoint(x: r.maxX - 11, y: r.maxY))
                p.addLine(to: CGPoint(x: r.minX, y: r.maxY))
                if notch { p.addLine(to: CGPoint(x: r.minX + 11, y: r.midY)) }
                p.closeSubpath()
            }
        }
    }
}

// MARK: - Index tabs

public struct SGIndexTabs: View {
    @Binding var selection: Int
    var titles: [String]
    public init(selection: Binding<Int>, titles: [String]) { _selection = selection; self.titles = titles }
    public var body: some View {
        VStack(spacing: 0) {
            HStack(spacing: 4) {
                ForEach(titles.indices, id: \.self) { i in
                    let on = i == selection
                    Text(titles[i]).sgCap(11)
                        .padding(.leading, 12).padding(.trailing, 18).padding(.vertical, 7)
                        .foregroundStyle(on ? SG.ground : SG.groundDim)
                        .background(TabShape().fill(on ? SG.groundHi : SG.ground3))
                        .onTapGesture { selection = i }
                        .accessibilityAddTraits(on ? [.isButton, .isSelected] : .isButton)
                }
                Spacer(minLength: 0)
            }
            Rectangle().fill(SG.groundHi).frame(height: 2)
        }
    }
    struct TabShape: Shape {
        func path(in r: CGRect) -> Path {
            Path { p in
                p.move(to: CGPoint(x: r.minX, y: r.minY)); p.addLine(to: CGPoint(x: r.maxX - 10, y: r.minY))
                p.addLine(to: CGPoint(x: r.maxX, y: r.minY + 10)); p.addLine(to: CGPoint(x: r.maxX, y: r.maxY))
                p.addLine(to: CGPoint(x: r.minX, y: r.maxY)); p.closeSubpath()
            }
        }
    }
}

// MARK: - Caution tag

/// Hazard stripes in coral and ink, used as a frame.
public struct HazardFill: View {
    public var a: Color = SG.coral, b: Color = SG.inkFixed, period: CGFloat = 16
    public init(a: Color = SG.coral, b: Color = SG.inkFixed, period: CGFloat = 16) { self.a = a; self.b = b; self.period = period }
    public var body: some View {
        Canvas { ctx, size in
            ctx.fill(Path(CGRect(origin: .zero, size: size)), with: .color(b))
            var x = -size.height
            while x < size.width + size.height {
                var p = Path()
                p.move(to: CGPoint(x: x, y: size.height)); p.addLine(to: CGPoint(x: x + period / 2, y: size.height))
                p.addLine(to: CGPoint(x: x + period / 2 + size.height, y: 0)); p.addLine(to: CGPoint(x: x + size.height, y: 0)); p.closeSubpath()
                ctx.fill(p, with: .color(a)); x += period
            }
        }
    }
}

public struct SGCaution: View {
    var title: String; var message: String
    public init(_ title: String, message: String) { self.title = title; self.message = message }
    public var body: some View {
        HStack(alignment: .top, spacing: 12) {
            WarnShape().fill(SG.coral, style: FillStyle(eoFill: true)).frame(width: 30, height: 30)
            VStack(alignment: .leading, spacing: 3) {
                Text(title).sgCap(13).foregroundStyle(SG.groundHi)
                Text(message).sgMono(11).foregroundStyle(SG.onGround)
            }
            Spacer(minLength: 0)
        }
        .padding(.horizontal, 14).padding(.vertical, 12)
        .background(SG.ground)
        .padding(5)
        .background(HazardFill())
    }
}

/// Sharp warning triangle with a bar and a square dot (use eoFill).
public struct WarnShape: Shape {
    public init() {}
    public func path(in r: CGRect) -> Path {
        let s = min(r.width, r.height) / 100
        func pt(_ x: CGFloat, _ y: CGFloat) -> CGPoint { CGPoint(x: r.minX + x * s, y: r.minY + y * s) }
        var p = Path()
        p.addLines([pt(50, 6), pt(96, 90), pt(4, 90)]); p.closeSubpath()
        p.addRect(CGRect(origin: pt(44, 34), size: CGSize(width: 12 * s, height: 30 * s)))
        p.addRect(CGRect(origin: pt(44, 70), size: CGSize(width: 12 * s, height: 10 * s)))
        return p
    }
}

// MARK: - Rubber stamp

public struct SGStamp: View {
    var text: String; var color: Color; var gap: Color; var angle: Double
    public init(_ text: String, color: Color = SG.coral, gap: Color = SG.ground, angle: Double = -8) {
        self.text = text; self.color = color; self.gap = gap; self.angle = angle
    }
    public var body: some View {
        Text(text).sgStencil(19)
            .padding(.horizontal, 12).padding(.vertical, 5)
            .foregroundStyle(color)
            .overlay(Rectangle().strokeBorder(color, lineWidth: 2.5))
            .overlay(Rectangle().inset(by: 4.5).strokeBorder(color, lineWidth: 1.5))
            .rotationEffect(.degrees(angle))
            .opacity(0.92)
    }
}

// MARK: - Ticket stub

public struct TicketShape: Shape {
    public var stub: CGFloat = 92, notch: CGFloat = 7
    public init(stub: CGFloat = 92, notch: CGFloat = 7) { self.stub = stub; self.notch = notch }
    public func path(in r: CGRect) -> Path {
        let x = r.maxX - stub, n = notch
        return Path { p in
            p.addLines([CGPoint(x: r.minX, y: r.minY), CGPoint(x: x - n, y: r.minY), CGPoint(x: x - n, y: r.minY + n), CGPoint(x: x + n, y: r.minY + n),
                        CGPoint(x: x + n, y: r.minY), CGPoint(x: r.maxX, y: r.minY), CGPoint(x: r.maxX, y: r.maxY), CGPoint(x: x + n, y: r.maxY),
                        CGPoint(x: x + n, y: r.maxY - n), CGPoint(x: x - n, y: r.maxY - n), CGPoint(x: x - n, y: r.maxY), CGPoint(x: r.minX, y: r.maxY)])
            p.closeSubpath()
        }
    }
}

public struct SGTicket<Main: View, Stub: View>: View {
    var stubWidth: CGFloat; let main: Main; let stub: Stub
    public init(stubWidth: CGFloat = 92, @ViewBuilder main: () -> Main, @ViewBuilder stub: () -> Stub) {
        self.stubWidth = stubWidth; self.main = main(); self.stub = stub()
    }
    public var body: some View {
        HStack(spacing: 0) {
            main.padding(.horizontal, 16).padding(.vertical, 14).frame(maxWidth: .infinity, alignment: .leading)
            Path { p in p.move(to: .zero); p.addLine(to: CGPoint(x: 0, y: 200)) }
                .stroke(SG.sageLo, style: StrokeStyle(lineWidth: 2, dash: [5, 4])).frame(width: 2)
            stub.padding(14).frame(width: stubWidth - 2, alignment: .trailing)
        }
        .foregroundStyle(SG.ink)
        .background(SG.sageHi)
        .clipShape(TicketShape(stub: stubWidth))
    }
}

// MARK: - Keycap and rocker

public struct SGKeycapStyle: ButtonStyle {
    var print: Bool; var hint: String
    public init(print: Bool = false, hint: String = "") { self.print = print; self.hint = hint }
    public func makeBody(configuration: Configuration) -> some View {
        let pressed = configuration.isPressed
        ZStack {
            ChamferRect(cut: 14).fill(print ? SG.groundDim : SG.coralDeep).padding(.top, 6)
            HStack {
                configuration.label.font(SGFont.title(21)).textCase(.uppercase).tracking(1.2)
                Spacer()
                if !hint.isEmpty { Text(hint).sgMono(10) }
                Rectangle().fill(SG.inkFixed).frame(width: 10, height: 10)
            }
            .padding(.horizontal, 22)
            .frame(maxHeight: .infinity)
            .background(ChamferRect(cut: 14).fill(print ? SG.groundHi : SG.coral))
            .padding(.bottom, 6)
            .offset(y: pressed ? 4 : 0)
        }
        .foregroundStyle(print ? SG.ground : SG.inkFixed)
        .frame(height: 76)
        .animation(.easeOut(duration: 0.08), value: pressed)
    }
}

public struct SGRockerStyle: ToggleStyle {
    public init() {}
    public func makeBody(configuration: Configuration) -> some View {
        HStack {
            configuration.label
            Spacer(minLength: 12)
            HStack(spacing: 0) {
                Text("I").frame(width: 36, height: 28).background(configuration.isOn ? SG.coral : .clear)
                    .foregroundStyle(configuration.isOn ? SG.inkFixed : SG.groundDim)
                Text("O").frame(width: 36, height: 28).background(configuration.isOn ? .clear : SG.groundHi)
                    .foregroundStyle(configuration.isOn ? SG.groundDim : SG.ground)
            }
            .font(SGFont.mono(14))
            .padding(4)
            .background(ChamferRect(cut: 7).fill(SG.ground3))
            .onTapGesture { configuration.isOn.toggle() }
            .accessibilityAddTraits(.isButton)
        }
    }
}

// MARK: - Data plate, spec rows, matrix code

public struct SGDataPlate<Content: View>: View {
    let content: Content
    public init(@ViewBuilder content: () -> Content) { self.content = content() }
    public var body: some View {
        VStack(alignment: .leading, spacing: 10) { content }
            .padding(.horizontal, 20).padding(.vertical, 18)
            .foregroundStyle(SG.ink)
            .background(ChamferRect(cut: 14).fill(SG.sageHi))
            .overlay(alignment: .topLeading) { rivet.padding(7) }
            .overlay(alignment: .bottomTrailing) { rivet.padding(7) }
            .overlay(alignment: .topTrailing) { rivet.padding(.top, 7).padding(.trailing, 22) }
            .overlay(alignment: .bottomLeading) { rivet.padding(.bottom, 7).padding(.leading, 22) }
    }
    private var rivet: some View { Rectangle().fill(SG.inkDim).frame(width: 6, height: 6) }
}

/// "SERIAL ........ 0917-C53"
public struct SGSpecRow: View {
    var label: String; var value: String; var onGround: Bool
    public init(_ label: String, _ value: String, onGround: Bool = false) { self.label = label; self.value = value; self.onGround = onGround }
    public var body: some View {
        HStack(alignment: .lastTextBaseline, spacing: 8) {
            Text(label)
            Line().stroke(onGround ? SG.groundDim : SG.inkDim, style: StrokeStyle(lineWidth: 1.5, dash: [1.5, 3])).frame(height: 1.5)
            Text(value)
        }
        .sgMono(11)
    }
    struct Line: Shape { func path(in r: CGRect) -> Path { Path { p in p.move(to: CGPoint(x: r.minX, y: r.midY)); p.addLine(to: CGPoint(x: r.maxX, y: r.midY)) } } }
}

/// A decorative QR-style matrix with three finder squares. Same look as assets/svg/matrix.svg.
public struct SGMatrixCode: View {
    var seed: UInt64
    public init(seed: UInt64 = 7) { self.seed = seed }
    public var body: some View {
        Canvas { ctx, size in
            let n = 21, c = min(size.width, size.height) / CGFloat(n)
            var rng = seed &* 6364136223846793005 &+ 1442695040888963407
            func next() -> Double { rng = rng &* 6364136223846793005 &+ 1442695040888963407; return Double(rng >> 33) / Double(1 << 31) }
            func cell(_ x: Int, _ y: Int) { ctx.fill(Path(CGRect(x: CGFloat(x) * c, y: CGFloat(y) * c, width: c, height: c)), with: .foreground) }
            for (fx, fy) in [(0, 0), (n - 7, 0), (0, n - 7)] {
                for y in 0..<7 { for x in 0..<7 where x == 0 || x == 6 || y == 0 || y == 6 || ((2...4).contains(x) && (2...4).contains(y)) { cell(fx + x, fy + y) } }
            }
            for y in 0..<n { for x in 0..<n {
                let reserved = (x < 8 && y < 8) || (x >= n - 8 && y < 8) || (x < 8 && y >= n - 8)
                if !reserved && next() < 0.48 { cell(x, y) }
            } }
        }
        .aspectRatio(1, contentMode: .fit)
        .accessibilityHidden(true)
    }
}

// MARK: - Print marks and colour bar

public extension View {
    /// Crop marks outside the corners, like a print proof.
    func printMarks(_ color: Color = SG.groundDim) -> some View {
        overlay(CropMarks().stroke(color, lineWidth: 1).padding(-14))
    }
}

struct CropMarks: Shape {
    func path(in r: CGRect) -> Path {
        let o: CGFloat = 14, l: CGFloat = 9
        return Path { p in
            let corners: [(CGFloat, CGFloat, CGFloat, CGFloat)] = [(r.minX, r.minY, 1, 1), (r.maxX, r.minY, -1, 1), (r.minX, r.maxY, 1, -1), (r.maxX, r.maxY, -1, -1)]
            for (cx, cy, sx, sy) in corners {
                p.move(to: CGPoint(x: cx, y: cy + o * sy)); p.addLine(to: CGPoint(x: cx + l * sx, y: cy + o * sy))
                p.move(to: CGPoint(x: cx + o * sx, y: cy)); p.addLine(to: CGPoint(x: cx + o * sx, y: cy + l * sy))
            }
        }
    }
}

public struct SGColorBar: View {
    public init() {}
    let swatches: [(String, Color)] = [("gnd", SG.ground), ("g-3", SG.ground3), ("print", SG.groundHi), ("sage", SG.sage),
                                       ("plate", SG.sageHi), ("ink", SG.ink), ("coral", SG.coral)]
    public var body: some View {
        HStack(spacing: 2) {
            ForEach(swatches, id: \.0) { item in
                let (name, color) = item
                VStack(alignment: .leading, spacing: 4) {
                    Rectangle().fill(color).frame(height: 14).overlay(Rectangle().strokeBorder(SG.ground3, lineWidth: 1))
                    Text(name).sgMono(8.5).foregroundStyle(SG.groundDim)
                }
            }
        }
    }
}

// MARK: - Ticker, boot log, lamps

public struct SGTicker: View {
    var text: String
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    public init(_ text: String) { self.text = text }
    public var body: some View {
        TimelineView(.animation(paused: reduceMotion)) { tl in
            GeometryReader { g in
                let line = Text(text + "   ◆   ").sgMono(11).foregroundStyle(SG.groundHi).fixedSize()
                let speed = 30.0, width = CGFloat(text.count + 7) * 6.6
                let x = reduceMotion ? 0 : -CGFloat(tl.date.timeIntervalSinceReferenceDate * speed).truncatingRemainder(dividingBy: width)
                HStack(spacing: 0) { line; line; line }.offset(x: x).frame(width: g.size.width, alignment: .leading).clipped()
            }
        }
        .frame(height: 26)
        .overlay(alignment: .top) { Rectangle().fill(SG.ground3).frame(height: 1) }
        .overlay(alignment: .bottom) { Rectangle().fill(SG.ground3).frame(height: 1) }
        .accessibilityLabel(Text(text))
    }
}

public struct SGBootLog: View {
    var done: [String]; var running: String?
    public init(done: [String], running: String? = nil) { self.done = done; self.running = running }
    public var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            ForEach(done, id: \.self) { line in (Text("[ OK ] ").foregroundStyle(SG.groundHi) + Text(line)) }
            if let r = running {
                HStack(spacing: 3) {
                    Text("[ .. ] ").foregroundStyle(SG.coral) + Text(r)
                    Rectangle().fill(SG.coral).frame(width: 7, height: 11)
                }
            }
        }
        .sgMono(11).foregroundStyle(SG.onGround)
    }
}

public struct SGLamps: View {
    public enum State { case off, on, fault }
    var lamps: [(String, State)]
    public init(_ lamps: [(String, State)]) { self.lamps = lamps }
    public var body: some View {
        HStack(spacing: 6) {
            ForEach(lamps.indices, id: \.self) { i in
                let (name, st) = lamps[i]
                VStack(alignment: .leading, spacing: 6) {
                    Rectangle().fill(st == .fault ? SG.coral : (st == .on ? SG.groundHi : SG.ground3)).frame(height: 10)
                    Text(name).sgMono(10).foregroundStyle(st == .fault ? SG.coral : (st == .on ? SG.groundHi : SG.groundDim))
                }
            }
        }
    }
}

// MARK: - Blueprint ground, callout, wave

public struct SGBlueprint: View {
    public init() {}
    public var body: some View {
        Canvas { ctx, size in
            ctx.fill(Path(CGRect(origin: .zero, size: size)), with: .color(SG.ground))
            for (step, color) in [(6.0, SG.ground2), (24.0, SG.ground3)] {
                var x: CGFloat = 0
                while x < size.width { ctx.fill(Path(CGRect(x: x, y: 0, width: 1, height: size.height)), with: .color(color)); x += step }
                var y: CGFloat = 0
                while y < size.height { ctx.fill(Path(CGRect(x: 0, y: y, width: size.width, height: 1)), with: .color(color)); y += step }
            }
        }
        .accessibilityHidden(true)
    }
}

/// Technical-drawing leader. Place it with `.position` at the point to annotate.
public struct SGCallout: View {
    var label: String; var length: CGFloat
    public init(_ label: String, length: CGFloat = 34) { self.label = label; self.length = length }
    public var body: some View {
        let d = length * 0.7071
        ZStack(alignment: .topLeading) {
            Path { p in p.move(to: CGPoint(x: 0, y: d)); p.addLine(to: CGPoint(x: d, y: 0)) }.stroke(SG.groundHi, lineWidth: 1.5)
            Rectangle().fill(SG.coral).frame(width: 6, height: 6).offset(x: -3, y: d - 3)
            Text(label).sgMono(10).foregroundStyle(SG.groundHi)
                .padding(.leading, 4).padding(.bottom, 2)
                .overlay(alignment: .bottom) { Rectangle().fill(SG.groundHi).frame(height: 1.5) }
                .fixedSize()
                .offset(x: d - 1, y: -15)
        }
        .frame(width: d, height: d, alignment: .topLeading)
    }
}

/// Angular oscilloscope trace (same points as assets/svg/wave.svg, 240 x 60).
public struct SGWave: Shape {
    public init() {}
    static let pts: [CGPoint] = [(0,30),(20,30),(26,8),(34,52),(42,8),(50,52),(56,30),(90,30),(96,18),(102,42),(108,30),(140,30),(146,4),
                                 (154,56),(162,4),(170,56),(176,30),(210,30),(216,22),(222,38),(228,30),(240,30)].map { CGPoint(x: $0.0, y: $0.1) }
    public func path(in r: CGRect) -> Path {
        Path { p in p.addLines(Self.pts.map { CGPoint(x: r.minX + $0.x / 240 * r.width, y: r.minY + $0.y / 60 * r.height) }) }
    }
}
