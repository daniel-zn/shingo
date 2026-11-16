import SwiftUI

// MARK: - Nested stadium pill (hero form)

/// Three stacked capsules plus a slot line. Proportions are measured off the poster:
/// band 18% of height, core 15%, slot 3%. `bleed` squares off a side that runs off-screen.
/// The slot doubles as a progress bar: `progress` = share drawn in `slotA`, the rest in `slotB`.
public struct NestedPill: View {
    public enum Bleed { case none, leading, trailing }
    public var height: CGFloat
    public var bleed: Bleed
    public var progress: Double
    public var slotA: Color
    public var slotB: Color
    public var dark: Bool

    public init(height: CGFloat = 150, bleed: Bleed = .none, progress: Double = 1,
                slotA: Color = SG.ink, slotB: Color = SG.coral, dark: Bool = false) {
        self.height = height; self.bleed = bleed; self.progress = progress
        self.slotA = slotA; self.slotB = slotB; self.dark = dark
    }

    private func shape(_ r: CGFloat) -> UnevenRoundedRectangle {
        let l = bleed == .leading ? 0 : r, t = bleed == .trailing ? 0 : r
        return UnevenRoundedRectangle(topLeadingRadius: l, bottomLeadingRadius: l, bottomTrailingRadius: t, topTrailingRadius: t)
    }

    public var body: some View {
        let band = height * 0.18
        let midH = height - band * 2
        let coreH = height * 0.15
        let slotH = max(3, height * 0.03)
        let outer = dark ? SG.ink3 : SG.sage
        let mid = dark ? SG.ink2 : SG.sageHi

        shape(height / 2).fill(outer)
            .overlay {
                shape(midH / 2).fill(mid)
                    .overlay {
                        shape(coreH / 2).fill(outer)
                            .overlay {
                                GeometryReader { g in
                                    HStack(spacing: 0) {
                                        Rectangle().fill(slotA).frame(width: g.size.width * progress)
                                        Rectangle().fill(slotB)
                                    }
                                    .clipShape(shape(slotH / 2))
                                }
                                .frame(height: slotH)
                                .padding(.leading, bleed == .leading ? 0 : height * 0.06)
                                .padding(.trailing, bleed == .trailing ? 0 : height * 0.06)
                            }
                            .frame(height: coreH)
                            .padding(.leading, bleed == .leading ? 0 : height * 0.24)
                            .padding(.trailing, bleed == .trailing ? 0 : height * 0.24)
                    }
                    .padding(.vertical, band)
                    .padding(.leading, bleed == .leading ? 0 : band)
                    .padding(.trailing, bleed == .trailing ? 0 : band)
            }
            .frame(height: height)
            .accessibilityHidden(true)
    }
}

// MARK: - Buttons

public struct SignalButtonStyle: ButtonStyle {
    public enum Kind { case ink, coral, sage, ghost }
    public var kind: Kind
    public var compact: Bool
    /// Line + text colour for `.ghost` (use SG.sageHi on ink screens).
    public var ghostColor: Color
    public init(_ kind: Kind = .ink, compact: Bool = false, ghostColor: Color = SG.ink) {
        self.kind = kind; self.compact = compact; self.ghostColor = ghostColor
    }

    public func makeBody(configuration: Configuration) -> some View {
        let pressed = configuration.isPressed
        configuration.label
            .font(SGFont.wordmark(compact ? 11 : 13))
            .textCase(.uppercase)
            .padding(.horizontal, compact ? 16 : 24)
            .frame(minHeight: compact ? 36 : 52)
            .foregroundStyle(fg)
            .background {
                switch kind {
                case .ink:   Capsule().fill(pressed ? SG.ink3 : SG.ink)
                case .coral: Capsule().fill(pressed ? SG.coralDeep : SG.coral)
                case .sage:  Capsule().fill(pressed ? SG.sage : SG.sageHi).overlay(Capsule().strokeBorder(SG.sageLo, lineWidth: 6))
                case .ghost: Capsule().strokeBorder(fg, lineWidth: SG.hair).background(Capsule().fill(pressed ? fg.opacity(0.08) : .clear))
                }
            }
            .contentShape(Capsule())
    }
    private var fg: Color {
        switch kind { case .ink: SG.sageHi; case .coral, .sage: SG.ink; case .ghost: ghostColor }
    }
}

// MARK: - Toggle

public struct SignalToggleStyle: ToggleStyle {
    public init() {}
    public func makeBody(configuration: Configuration) -> some View {
        HStack {
            configuration.label
            Spacer(minLength: 12)
            ZStack(alignment: configuration.isOn ? .trailing : .leading) {
                Capsule().fill(configuration.isOn ? SG.coral : SG.sageLo)
                    .overlay(Capsule().strokeBorder(configuration.isOn ? SG.coralDeep : SG.sage, lineWidth: 5))
                Capsule().fill(SG.ink.opacity(0.35)).frame(height: 3).padding(.horizontal, 11)
                Circle().fill(SG.ink).frame(width: 22, height: 22).padding(5)
            }
            .frame(width: 60, height: 32)
            .onTapGesture { withAnimation(.snappy(duration: 0.18)) { configuration.isOn.toggle() } }
            .accessibilityAddTraits(.isButton)
        }
    }
}

// MARK: - Segmented control

public struct SignalSegmented<T: Hashable>: View {
    @Binding var selection: T
    let options: [(T, String)]
    var onInk: Bool
    @Namespace private var ns

    public init(selection: Binding<T>, options: [(T, String)], onInk: Bool = false) {
        _selection = selection; self.options = options; self.onInk = onInk
    }

    public var body: some View {
        HStack(spacing: 2) {
            ForEach(options, id: \.0) { option in
                let (value, title) = option
                let on = value == selection
                Text(title).sgMono(11)
                    .frame(maxWidth: .infinity, minHeight: 32)
                    .foregroundStyle(on ? (onInk ? SG.ink : SG.sageHi) : (onInk ? SG.onInk : SG.ink))
                    .background {
                        if on { Capsule().fill(onInk ? SG.sageHi : SG.ink).matchedGeometryEffect(id: "seg", in: ns) }
                    }
                    .contentShape(Capsule())
                    .onTapGesture { withAnimation(.snappy(duration: 0.2)) { selection = value } }
                    .accessibilityAddTraits(on ? [.isButton, .isSelected] : .isButton)
            }
        }
        .padding(4)
        .background(Capsule().fill(onInk ? SG.ink3 : SG.sageLo))
    }
}

// MARK: - Chip, rule, slot

public struct SignalChip: View {
    public enum Kind { case outline, on, coral }
    var text: String; var kind: Kind
    public init(_ text: String, kind: Kind = .outline) { self.text = text; self.kind = kind }
    public var body: some View {
        Text(text).sgMono(10.5)
            .padding(.horizontal, 11).frame(height: 26)
            .foregroundStyle(kind == .on ? SG.sageHi : SG.ink)
            .background {
                switch kind {
                case .outline: Capsule().strokeBorder(SG.sageLine, lineWidth: SG.hair)
                case .on: Capsule().fill(SG.ink)
                case .coral: Capsule().fill(SG.coral)
                }
            }
    }
}

/// Hairline that ends in a small block (the poster's "09 ———▬").
public struct SignalRule: View {
    public var color: Color = SG.sageLine
    public init(color: Color = SG.sageLine) { self.color = color }
    public var body: some View {
        HStack(spacing: 0) {
            Rectangle().fill(color).frame(height: 1.5)
            Rectangle().fill(color).frame(width: 26, height: 8)
        }.frame(height: 8)
    }
}

/// Thin capsule progress bar: coral fill on an ink track.
public struct SignalSlot: View {
    public var progress: Double
    public var fill: Color = SG.coral
    public var track: Color = SG.ink
    public init(progress: Double, fill: Color = SG.coral, track: Color = SG.ink) {
        self.progress = progress; self.fill = fill; self.track = track
    }
    public var body: some View {
        GeometryReader { g in
            HStack(spacing: 0) {
                Rectangle().fill(fill).frame(width: g.size.width * progress)
                Rectangle().fill(track)
            }
        }
        .frame(height: 6)
        .clipShape(Capsule())
        .accessibilityValue(Text("\(Int(progress * 100)) percent"))
    }
}

// MARK: - Tab bar

public struct SignalTabBar<Tab: Hashable>: View {
    public struct Item { public let tab: Tab; public let title: String; public let icon: AnyView
        public init<V: View>(_ tab: Tab, _ title: String, @ViewBuilder icon: () -> V) { self.tab = tab; self.title = title; self.icon = AnyView(icon()) }
    }
    @Binding var selection: Tab
    let items: [Item]
    public init(selection: Binding<Tab>, items: [Item]) { _selection = selection; self.items = items }

    public var body: some View {
        HStack {
            ForEach(items.indices, id: \.self) { i in
                let item = items[i], on = item.tab == selection
                VStack(spacing: 4) {
                    item.icon.frame(width: 22, height: 22)
                    Text(item.title).sgMono(9)
                }
                .foregroundStyle(on ? SG.coral : SG.sageLine)
                .frame(maxWidth: .infinity)
                .contentShape(Rectangle())
                .onTapGesture { selection = item.tab }
                .accessibilityAddTraits(on ? [.isButton, .isSelected] : .isButton)
            }
        }
        .frame(height: 64)
        .background(Capsule().fill(SG.ink).overlay(Capsule().strokeBorder(SG.ink3, lineWidth: SG.hair)))
        .padding(.horizontal, 16)
    }
}
