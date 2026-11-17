import SwiftUI
import UIKit

// MARK: - Live layer
//
// Machine behaviour for the print system, matching web/shingo-live.js:
// haptics designed with the shapes, scrambling titles, live readouts,
// a hazard-band transition and a HUD readout. Everything is stepped
// (no easing) and stands still when Reduce Motion is on.

// MARK: Haptics

/// One vocabulary of feel, paired with the shapes.
public enum SGHaptics {
    /// Switches and tabs: one hard tick.
    public static func tick() { UIImpactFeedbackGenerator(style: .rigid).impactOccurred(intensity: 0.9) }
    /// Keycaps: a double tick, press and seat.
    public static func key() {
        let g = UIImpactFeedbackGenerator(style: .rigid)
        g.impactOccurred(intensity: 1)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.06) { g.impactOccurred(intensity: 0.55) }
    }
    /// Cell meters: a step whose weight rises with the level (0...1).
    public static func step(_ level: Double) { UIImpactFeedbackGenerator(style: .light).impactOccurred(intensity: 0.35 + 0.6 * min(1, max(0, level))) }
    /// Rocker: a heavier throw.
    public static func throwSwitch() { UIImpactFeedbackGenerator(style: .heavy).impactOccurred() }
    /// Alerts: the coral signal.
    public static func alarm() { UINotificationFeedbackGenerator().notificationOccurred(.error) }
    /// Completion: sealed, sent, verified.
    public static func sealed() { UINotificationFeedbackGenerator().notificationOccurred(.success) }
}

// MARK: Scramble

/// How long a decode takes. Titles are slowest, then labels, then data; touch is a quick re-decode.
public enum SGDecodeWeight {
    case title, label, data, touch
    var range: ClosedRange<Double> {
        switch self { case .title: 0.32...0.72; case .label: 0.16...0.38; case .data: 0.20...0.52; case .touch: 0.12...0.26 }
    }
}

/// Glyph noise that keeps each character's class: digits through digits, capitals through hard
/// capitals, kanji through kanji. Punctuation and spaces never scramble, so structure holds.
enum SGNoise {
    static let digits = Array("0123456789"), upper = Array("XKZNRVHEW#/"), lower = Array("xkznrvhew#/"), kanji = Array("信号経路保護暗中封鎖")
    static func pool(_ c: Character) -> [Character]? {
        if c.isNumber && c.isASCII { return digits }
        if c.isUppercase { return upper }
        if c.isLowercase { return lower }
        if let u = c.unicodeScalars.first?.value, (0x3040...0x30FF).contains(u) || (0x4E00...0x9FFF).contains(u) { return kanji }
        return nil
    }
    static func glyph(_ c: Character) -> Character { pool(c)?.randomElement() ?? c }
}

/// Text that decodes from glyph noise when it appears and whenever it changes,
/// each character locking at its own random moment.
///
///     SGScrambleText("Relay fleet")                       // title
///     SGScrambleText(label, weight: .label, delay: 0.09)  // staggered down the screen
///     SGScrambleText("\(hops)", weight: .touch)            // a value that changes
public struct SGScrambleText: View {
    var text: String; var weight: SGDecodeWeight; var delay: Double
    @State private var shown: String
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    public init(_ text: String, weight: SGDecodeWeight = .title, delay: Double = 0) {
        self.text = text; self.weight = weight; self.delay = delay; _shown = State(initialValue: text)
    }

    public var body: some View {
        Text(shown)
            .accessibilityLabel(Text(text))
            .task(id: text) { await run() }
    }

    /// Frames land every 28–80 ms; each character flickers irregularly until it locks.
    private func run() async {
        guard !reduceMotion else { shown = text; return }
        let src = Array(text)
        let total = Double.random(in: weight.range)
        let lock = src.map { _ in total * (0.15 + 0.85 * pow(Double.random(in: 0...1), 0.8)) }
        var cur = src.map { SGNoise.glyph($0) }
        shown = String(cur)                       // hold the noise through the stagger delay
        if delay > 0 { try? await Task.sleep(nanoseconds: UInt64(delay * 1e9)) }
        let t0 = Date()
        while !Task.isCancelled {
            let t = Date().timeIntervalSince(t0)
            var done = true
            for k in src.indices where SGNoise.pool(src[k]) != nil && t < lock[k] {
                done = false
                if Double.random(in: 0...1) < 0.45 { cur[k] = SGNoise.glyph(src[k]) }
            }
            shown = String(src.indices.map { k in (SGNoise.pool(src[k]) == nil || t >= lock[k]) ? src[k] : cur[k] })
            if done { break }
            try? await Task.sleep(nanoseconds: UInt64.random(in: 28_000_000...80_000_000))
        }
        shown = text
    }
}

// MARK: Live readouts

/// A seven-segment countdown that re-renders every second and loops.
public struct SGLiveCountdown: View {
    var seconds: Int; var height: CGFloat; var hot: Set<Int>
    @State private var start = Date()
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    public init(seconds: Int, height: CGFloat = 48, hot: Set<Int> = [2]) { self.seconds = seconds; self.height = height; self.hot = hot }
    public var body: some View {
        TimelineView(.periodic(from: start, by: 1)) { tl in
            let elapsed = reduceMotion ? 0 : Int(tl.date.timeIntervalSince(start))
            let t = seconds - elapsed % (seconds + 1)
            SGSegDisplay(String(format: "%02d:%02d", t / 60, t % 60), height: height, hot: hot)
        }
    }
}

// MARK: Transition: hazard wipe

/// A hazard band crosses the view along the one diagonal in eight steps.
public struct SGHazardWipe: ViewModifier {
    var progress: CGFloat   // 0...1, quantised to 8 steps
    public func body(content: Content) -> some View {
        content.overlay {
            GeometryReader { g in
                let p = (progress * 8).rounded(.down) / 8
                if p > 0 && p < 1 {
                    HazardFill(a: SG.groundHi, b: SG.ground, period: 28)
                        .frame(width: g.size.width * 0.7, height: g.size.height * 1.4)
                        .overlay(alignment: .leading) { Rectangle().fill(SG.coral).frame(width: 6) }
                        .transformEffect(CGAffineTransform(a: 1, b: 0, c: -1, d: 1, tx: g.size.height * 0.7, ty: 0))
                        .offset(x: -g.size.width * 0.8 + p * g.size.width * 2.2, y: -g.size.height * 0.2)
                        .allowsHitTesting(false)
                }
            }
        }
    }
}

public extension AnyTransition {
    /// Use with `.animation(.linear(duration: 0.52), value:)`; the band itself is quantised to 8 steps.
    static var sgHazardWipe: AnyTransition {
        .modifier(active: SGHazardWipe(progress: 0.5), identity: SGHazardWipe(progress: 0))
    }
}

// MARK: HUD readout

/// Coral brackets and a callout snap to a view while it is pressed.
public struct SGHUDReadout: ViewModifier {
    var label: String
    @GestureState private var pressed = false
    public func body(content: Content) -> some View {
        content
            .overlay {
                if pressed {
                    Brackets(length: 9).stroke(SG.coral, lineWidth: SG.hair).padding(-4)
                        .overlay(alignment: .topTrailing) {
                            SGScrambleText("▸ " + label.uppercased(), weight: .touch).sgMono(9.5).foregroundStyle(SG.inkFixed)
                                .padding(.horizontal, 6).padding(.vertical, 2)
                                .background(SG.coral).fixedSize().offset(y: -18)
                        }
                }
            }
            .simultaneousGesture(LongPressGesture(minimumDuration: 0.15).sequenced(before: DragGesture(minimumDistance: 0))
                .updating($pressed) { v, s, _ in if case .second = v { if !s { SGHaptics.tick() }; s = true } })
    }
}

public extension View {
    /// Press and hold to read this value through the HUD reticle.
    func sgHUD(_ label: String) -> some View { modifier(SGHUDReadout(label: label)) }
}
