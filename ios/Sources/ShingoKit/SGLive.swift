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

/// Text that resolves from glyph noise when it appears or changes. Stepped, 9 frames at 45 ms.
public struct SGScrambleText: View {
    var text: String
    @State private var shown: String
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    private static let noise = Array("/X#▮▚09-+")

    public init(_ text: String) { self.text = text; _shown = State(initialValue: text) }

    public var body: some View {
        Text(shown)
            .accessibilityLabel(Text(text))
            .task(id: text) { await run() }
    }

    private func run() async {
        guard !reduceMotion else { shown = text; return }
        let src = Array(text), steps = 9
        for i in 1...steps {
            let keep = src.count * i / steps
            shown = String(src.enumerated().map { k, c in (k < keep || c == " ") ? c : Self.noise[(k * 7 + i * 3) % Self.noise.count] })
            try? await Task.sleep(nanoseconds: 45_000_000)
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
                            Text("▸ " + label.uppercased()).sgMono(9.5).foregroundStyle(SG.inkFixed)
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
