import SwiftUI

// MARK: - Nested bar (hero form)

/// Three plates and a slot with one 45° cut at the free end: the industrial
/// descendant of the nested pill. `bleed` is the side that runs off-screen.
/// The slot doubles as progress: `progress` drawn in `slotA`, the rest in `slotB`.
public struct SGBar: View {
    public enum Bleed { case leading, trailing }
    public var height: CGFloat
    public var bleed: Bleed
    public var progress: Double
    public var slotA: Color
    public var slotB: Color

    public init(height: CGFloat = 120, bleed: Bleed = .leading, progress: Double = 1,
                slotA: Color = SG.ground, slotB: Color = SG.coral) {
        self.height = height; self.bleed = bleed; self.progress = progress
        self.slotA = slotA; self.slotB = slotB
    }

    public var body: some View {
        let k = height * 0.42
        let corner: TagCut.Corner = bleed == .leading ? .bottomTrailing : .topLeading
        let freeEnd: Edge.Set = bleed == .leading ? .trailing : .leading

        TagCut(cut: k, corner: corner).fill(SG.groundHi)
            .overlay {
                TagCut(cut: k * 0.62, corner: corner).fill(SG.groundHi)
                    .overlay {
                        Rectangle().fill(SG.groundHi)
                            .overlay {
                                GeometryReader { g in
                                    HStack(spacing: 0) {
                                        Rectangle().fill(slotA).frame(width: g.size.width * progress)
                                        Rectangle().fill(slotB)
                                    }
                                }
                                .frame(height: max(3, height * 0.05))
                                .padding(freeEnd, height * 0.06)
                            }
                            .frame(height: height * 0.2)
                            .padding(freeEnd, height * 0.3)
                    }
                    .padding(.vertical, height * 0.12)
                    .padding(freeEnd, height * 0.12)
            }
            .frame(height: height)
            .accessibilityHidden(true)
    }
}

// MARK: - Buttons

public struct SGButtonStyle: ButtonStyle {
    public enum Kind { case print, signal, plate, ink, ghost }
    public var kind: Kind
    public var compact: Bool
    /// Line + text colour for `.ghost`.
    public var ghostColor: Color

    public init(_ kind: Kind = .print, compact: Bool = false, ghostColor: Color = SG.groundHi) {
        self.kind = kind; self.compact = compact; self.ghostColor = ghostColor
    }

    public func makeBody(configuration: Configuration) -> some View {
        let shape = ChamferRect(cut: compact ? 7 : 10)
        configuration.label
            .font(SGFont.cap(compact ? 12 : 14)).textCase(.uppercase).tracking(compact ? 1.4 : 1.7)
            .padding(.horizontal, compact ? 14 : 22)
            .frame(minHeight: compact ? 32 : 48)
            .foregroundStyle(fg)
            .background {
                switch kind {
                case .ghost: shape.strokeBorder(ghostColor, lineWidth: SG.hair)
                default: shape.fill(bg)
                }
            }
            .opacity(configuration.isPressed ? 0.8 : 1)
            .contentShape(shape)
    }
    private var bg: Color {
        switch kind {
        case .print: SG.groundHi
        case .signal: SG.coral
        case .plate: SG.sageHi
        case .ink: SG.inkFixed
        case .ghost: .clear
        }
    }
    private var fg: Color {
        switch kind {
        case .print: SG.ground
        case .signal: SG.inkFixed
        case .plate: SG.ink
        case .ink: Color(hex: 0xDCDFD5)
        case .ghost: ghostColor
        }
    }
}

// MARK: - Toggle (cut plate with a sliding block)

public struct SGToggleStyle: ToggleStyle {
    public init() {}
    public func makeBody(configuration: Configuration) -> some View {
        HStack {
            configuration.label.font(SGFont.cap(12.5)).textCase(.uppercase).foregroundStyle(SG.groundHi)
            Spacer(minLength: 12)
            ZStack(alignment: configuration.isOn ? .trailing : .leading) {
                ChamferRect(cut: 7).fill(configuration.isOn ? SG.groundHi : SG.ground3)
                ChamferRect(cut: 5).fill(configuration.isOn ? SG.ground : SG.groundDim)
                    .frame(width: 22, height: 20).padding(4)
            }
            .frame(width: 58, height: 28)
            .onTapGesture { withAnimation(.snappy(duration: 0.16)) { configuration.isOn.toggle() } }
            .accessibilityAddTraits(.isButton)
        }
    }
}

// MARK: - Segmented control

public struct SGSegmented<T: Hashable>: View {
    @Binding var selection: T
    let options: [(T, String)]
    @Namespace private var ns

    public init(selection: Binding<T>, options: [(T, String)]) {
        _selection = selection; self.options = options
    }

    public var body: some View {
        HStack(spacing: 3) {
            ForEach(options, id: \.0) { option in
                let (value, title) = option
                let on = value == selection
                Text(title).sgMono(11)
                    .frame(maxWidth: .infinity, minHeight: 30)
                    .foregroundStyle(on ? SG.ground : SG.onGround)
                    .background {
                        if on { Rectangle().fill(SG.groundHi).matchedGeometryEffect(id: "seg", in: ns) }
                    }
                    .contentShape(Rectangle())
                    .onTapGesture { withAnimation(.snappy(duration: 0.2)) { selection = value } }
                    .accessibilityAddTraits(on ? [.isButton, .isSelected] : .isButton)
            }
        }
        .padding(3)
        .background(ChamferRect(cut: 8).fill(SG.ground3))
    }
}

// MARK: - Chip, slot, group label

public struct SGChip: View {
    public enum Kind { case outline, on, signal }
    var text: String; var kind: Kind
    public init(_ text: String, kind: Kind = .outline) { self.text = text; self.kind = kind }
    public var body: some View {
        let shape = ChamferRect(cut: 5)
        Text(text).sgMono(10.5)
            .padding(.horizontal, 9).frame(height: 22)
            .foregroundStyle(kind == .on ? SG.ground : (kind == .signal ? SG.inkFixed : SG.groundHi))
            .background {
                switch kind {
                case .outline: shape.strokeBorder(SG.groundDim, lineWidth: SG.hair)
                case .on: shape.fill(SG.groundHi)
                case .signal: shape.fill(SG.coral)
                }
            }
    }
}

/// Flat progress bar: coral fill on a ground-3 track. No rounding.
public struct SGSlot: View {
    public var progress: Double
    public var fill: Color = SG.groundHi
    public var track: Color = SG.ground3
    public init(progress: Double, fill: Color = SG.groundHi, track: Color = SG.ground3) {
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
        .accessibilityValue(Text("\(Int(progress * 100)) percent"))
    }
}

/// Condensed-caps group label over a print hairline: "PRIVACY ———— 01".
public struct SGGroupLabel: View {
    var label: String; var index: String
    public init(_ label: String, _ index: String = "") { self.label = label; self.index = index }
    public var body: some View {
        VStack(spacing: 6) {
            HStack(alignment: .firstTextBaseline) {
                Text(label).sgCap(12).foregroundStyle(SG.groundHi)
                Spacer()
                Text(index).sgMono(11).foregroundStyle(SG.groundDim)
            }
            Rectangle().fill(SG.groundHi).frame(height: SG.hair)
        }
    }
}

// MARK: - Tab bar (cut dock)

public struct SGTabBar<Tab: Hashable>: View {
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
                    Rectangle().fill(on ? SG.coral : .clear).frame(width: 18, height: 3)
                    item.icon.frame(width: 20, height: 20)
                    Text(item.title).sgCap(10)
                }
                .foregroundStyle(on ? SG.signalText : SG.groundDim)
                .frame(maxWidth: .infinity)
                .contentShape(Rectangle())
                .onTapGesture { selection = item.tab }
                .accessibilityAddTraits(on ? [.isButton, .isSelected] : .isButton)
            }
        }
        .frame(height: 60)
        .chamferFrame(cut: SG.cutM)
        .padding(.horizontal, 16)
    }
}
