import SwiftUI

// MARK: - Patterns for any app
//
// State language, spec table, the form set, telex and skeletons.
// Mirrors the "patterns" block of web/shingo.css.

// MARK: State language

/// Every system state has one fixed shape.
public enum SGStateKind: String, CaseIterable {
    case nominal, caution, fault, offline, syncing
}

public struct SGState: View {
    var kind: SGStateKind; var label: String?
    public init(_ kind: SGStateKind, label: String? = nil) { self.kind = kind; self.label = label }
    public var body: some View {
        HStack(spacing: 8) {
            mark.frame(width: kind == .syncing ? 22 : 11, height: 11)
            Text(label ?? kind.rawValue).sgMono(10.5)
        }
        .foregroundStyle(kind == .fault ? SG.signalText : (kind == .offline ? SG.groundDim : SG.groundHi))
        .accessibilityElement(children: .combine)
    }
    @ViewBuilder private var mark: some View {
        switch kind {
        case .nominal: Rectangle().fill(SG.groundHi)
        case .caution: HazardFill(a: SG.groundHi, b: .clear, period: 4).overlay(Rectangle().strokeBorder(SG.groundHi, lineWidth: SG.hair))
        case .fault: SGHardX().fill(SG.coral)
        case .offline: SGHardX().fill(SG.groundDim)
        case .syncing: HazardFill(a: SG.groundHi, b: .clear, period: 5)
        }
    }
}

// MARK: Spec table

/// A list as an engineering spec sheet: coded columns, row index, tabular figures,
/// and the coral bar on the selected row.
public struct SGSpecTable<Row: Identifiable, Cells: View>: View {
    public struct Column { public let code: String; public let title: String; public let trailing: Bool
        public init(_ code: String, _ title: String, trailing: Bool = false) { self.code = code; self.title = title; self.trailing = trailing } }
    let columns: [Column]; let rows: [Row]
    @Binding var selection: Row.ID?
    let cells: (Row) -> Cells

    public init(columns: [Column], rows: [Row], selection: Binding<Row.ID?>, @ViewBuilder cells: @escaping (Row) -> Cells) {
        self.columns = columns; self.rows = rows; _selection = selection; self.cells = cells
    }

    public var body: some View {
        VStack(spacing: 0) {
            HStack(alignment: .bottom) {
                Text("Nº").frame(width: 28, alignment: .leading)
                ForEach(columns.indices, id: \.self) { i in
                    VStack(alignment: columns[i].trailing ? .trailing : .leading, spacing: 2) {
                        Text(columns[i].code).sgMono(8.5).foregroundStyle(SG.groundDim)
                        Text(columns[i].title)
                    }
                    .frame(maxWidth: .infinity, alignment: columns[i].trailing ? .trailing : .leading)
                }
            }
            .sgCap(10).foregroundStyle(SG.groundHi)
            .padding(.horizontal, 14).padding(.bottom, 7)
            .overlay(alignment: .bottom) { Rectangle().fill(SG.groundHi).frame(height: SG.hair) }
            ForEach(Array(rows.enumerated()), id: \.element.id) { i, row in
                let on = row.id == selection
                HStack {
                    Text(String(format: "%02d", i + 1)).sgMono(10).foregroundStyle(SG.groundDim).frame(width: 28, alignment: .leading)
                    cells(row)
                }
                .padding(.horizontal, 14).padding(.vertical, 9)
                .background(on ? SG.ground2 : .clear)
                .overlay(alignment: .leading) { if on { Rectangle().fill(SG.coral).frame(width: 4) } }
                .overlay(alignment: .bottom) { Rectangle().fill(SG.ground3).frame(height: 1) }
                .contentShape(Rectangle())
                .onTapGesture { selection = row.id; SGHaptics.tick() }
                .accessibilityAddTraits(on ? [.isButton, .isSelected] : .isButton)
            }
        }
    }
}

// MARK: Form set

/// Checkbox as a hard X in a square.
public struct SGXCheckboxStyle: ToggleStyle {
    public init() {}
    public func makeBody(configuration: Configuration) -> some View {
        HStack(spacing: 10) {
            ZStack {
                Rectangle().strokeBorder(SG.groundHi, lineWidth: SG.hair)
                if configuration.isOn { SGHardX().fill(SG.groundHi).padding(4) }
            }
            .frame(width: 20, height: 20)
            configuration.label.sgCap(11.5).foregroundStyle(SG.groundHi)
        }
        .contentShape(Rectangle())
        .onTapGesture { configuration.isOn.toggle(); SGHaptics.tick() }
        .accessibilityAddTraits(.isButton)
    }
}

/// Radio as a diamond. Use one per option, bound to a shared selection.
public struct SGDiamondRadio<Value: Hashable>: View {
    var title: String; var value: Value; @Binding var selection: Value
    public init(_ title: String, value: Value, selection: Binding<Value>) { self.title = title; self.value = value; _selection = selection }
    public var body: some View {
        let on = value == selection
        HStack(spacing: 10) {
            ZStack {
                Diamond().stroke(SG.groundHi, lineWidth: 2.2)
                if on { Diamond().fill(SG.groundHi).padding(6) }
            }
            .frame(width: 20, height: 20)
            Text(title).sgCap(11.5).foregroundStyle(SG.groundHi)
        }
        .contentShape(Rectangle())
        .onTapGesture { selection = value; SGHaptics.tick() }
        .accessibilityAddTraits(on ? [.isButton, .isSelected] : .isButton)
    }
    struct Diamond: Shape {
        func path(in r: CGRect) -> Path { Path { p in p.addLines([CGPoint(x: r.midX, y: r.minY), CGPoint(x: r.maxX, y: r.midY), CGPoint(x: r.midX, y: r.maxY), CGPoint(x: r.minX, y: r.midY)]); p.closeSubpath() } }
    }
}

/// Stepper as two cut keys around a wide numeral.
public struct SGStepper: View {
    @Binding var value: Int; var range: ClosedRange<Int>
    public init(value: Binding<Int>, in range: ClosedRange<Int>) { _value = value; self.range = range }
    public var body: some View {
        HStack(spacing: 4) {
            key("−") { value = max(range.lowerBound, value - 1) }
            Text("\(value)").font(SGFont.title(22)).monospacedDigit().foregroundStyle(SG.groundHi).frame(minWidth: 64)
            key("+") { value = min(range.upperBound, value + 1) }
        }
        .accessibilityElement()
        .accessibilityValue(Text("\(value)"))
        .accessibilityAdjustableAction { d in value = d == .increment ? min(range.upperBound, value + 1) : max(range.lowerBound, value - 1) }
    }
    private func key(_ s: String, _ action: @escaping () -> Void) -> some View {
        Button { action(); SGHaptics.tick() } label: {
            Text(s).font(SGFont.mono(18)).foregroundStyle(SG.ground).frame(width: 40, height: 40).background(ChamferRect(cut: 7).fill(SG.groundHi))
        }.buttonStyle(.plain)
    }
}

/// Search field with the scan reticle and a key hint.
public struct SGSearchField: View {
    @Binding var text: String; var prompt: String
    @FocusState private var focused: Bool
    public init(text: Binding<String>, prompt: String = "Search") { _text = text; self.prompt = prompt }
    public var body: some View {
        HStack(spacing: 10) {
            SGIcon(.scan).frame(width: 18, height: 18).foregroundStyle(SG.groundHi)
            TextField("", text: $text, prompt: Text(prompt.uppercased()).font(SGFont.mono(11)).foregroundStyle(SG.groundDim))
                .font(SGFont.body(14)).foregroundStyle(SG.groundHi).focused($focused)
        }
        .padding(.horizontal, 12).frame(height: 44)
        .background(ChamferRect(cut: 10).strokeBorder(focused ? SG.coral : SG.groundDim, lineWidth: SG.hair))
    }
}

// MARK: Telex

/// A notification that types itself in like a teleprinter.
public struct SGTelex: View {
    var state: SGStateKind; var message: String; var time: String
    @State private var typed = ""
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    public init(_ state: SGStateKind, _ message: String, time: String) { self.state = state; self.message = message; self.time = time }
    public var body: some View {
        HStack(spacing: 12) {
            SGState(state)
            Text(typed.isEmpty && reduceMotion ? message : typed).lineLimit(1).frame(maxWidth: .infinity, alignment: .leading)
            Text(time).foregroundStyle(SG.groundDim)
        }
        .sgMono(11).foregroundStyle(SG.groundHi)
        .padding(.horizontal, 14).padding(.vertical, 11)
        .overlay(Rectangle().strokeBorder(SG.groundHi, lineWidth: SG.hair))
        .overlay(alignment: .leading) { if state == .fault { Rectangle().fill(SG.coral).frame(width: 5) } }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(Text("\(state.rawValue), \(message), \(time)"))
        .task(id: message) {
            if state == .fault { SGHaptics.alarm() }
            guard !reduceMotion else { typed = message; return }
            for i in 1...max(1, message.count) {
                typed = String(message.prefix(i)) + (i < message.count ? "▮" : "")
                try? await Task.sleep(nanoseconds: UInt64.random(in: 14_000_000...44_000_000))
            }
        }
    }
}

// MARK: Skeleton

/// Drafting hatch while data loads.
public struct SGSkeleton: View {
    public init() {}
    public var body: some View {
        HazardFill(a: SG.ground3, b: .clear, period: 6)
            .overlay(Rectangle().strokeBorder(SG.ground3, lineWidth: 1))
            .accessibilityLabel(Text("Loading"))
    }
}
