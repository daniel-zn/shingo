import SwiftUI

// Gallery screens rebuilt in SwiftUI from kit parts, so you can compare
// them with dist/index.html (screens A and C). N lives in SGLanguage.swift.

// MARK: - A · Launch (poster tier: reference 1 made industrial)

public struct LaunchExample: View {
    public var progress: Double = 0.64
    public init(progress: Double = 0.64) { self.progress = progress }

    public var body: some View {
        GeometryReader { geo in
            let w = geo.size.width
            ZStack(alignment: .topLeading) {
                StripeField(facets: [
                    .init(angle: .degrees(-45), polygon: [.init(x: 0, y: 0), .init(x: 1, y: 0), .init(x: 1, y: 0.06), .init(x: 0, y: 0.34)])
                ])

                // masthead
                HStack(alignment: .bottom, spacing: 8) {
                    SGCode("SK·09·LIS")
                    Text("AXIOM").sgWordmark(SGMetrics.display)
                }
                .foregroundStyle(SG.groundHi)
                .offset(x: 22, y: 64)
                Text("Secure workspace").sgCap(12).foregroundStyle(SG.groundDim).offset(x: 42, y: 116)

                // 45° coral wedge + hard X
                UnitPolygon([.init(x: 1, y: 0), .init(x: 1, y: 1), .init(x: 0, y: 1)])
                    .fill(SG.coral).frame(width: 120, height: 120).offset(x: w - 120, y: 56)
                SGHardX().stroke(SG.groundHi, style: StrokeStyle(lineWidth: 5.5, lineJoin: .miter))
                    .frame(width: 84, height: 84).offset(x: w - 104, y: 150)

                // two cut bars
                SGBar(height: 104, bleed: .leading).frame(width: 260).offset(y: 164)
                VerticalText("安全な作業空間", size: 11).foregroundStyle(SG.groundDim).offset(x: 28, y: 296)
                SGBar(height: 104, bleed: .trailing, progress: 0.58).frame(width: w - 72).offset(x: 72, y: 290)

                // 45° band
                UnitPolygon([.init(x: 150 / 240, y: 0), .init(x: 1, y: 0), .init(x: 0, y: 1), .init(x: 0, y: 150 / 240)])
                    .fill(SG.coral).frame(width: 240, height: 240).offset(y: 420)

                // instrument column
                VStack(alignment: .trailing, spacing: 8) {
                    Text("09").sgNumber(28)
                    Text("REF:\nOPSEC/AHI\nSP C53").sgMono(12).multilineTextAlignment(.trailing)
                    Barcode(axis: .vertical).frame(width: 96, height: 80).padding(.top, 20)
                }
                .foregroundStyle(SG.groundHi)
                .frame(width: w - 48, alignment: .trailing)
                .offset(x: 24, y: 430)

                // boot status
                VStack(spacing: 10) {
                    HazardBar()
                    HStack { Text("Sealing tunnel"); Spacer(); Text("\(Int(progress * 100))%") }
                        .sgMono(11).foregroundStyle(SG.groundHi).padding(.top, 14)
                    SGSlot(progress: progress)
                }
                .frame(width: w - 48)
                .offset(x: 24, y: 690)
            }
        }
        .ignoresSafeArea()
    }
}

// MARK: - C · Dashboard (utility grammar)

public struct DashboardExample: View {
    @State private var killSwitch = true
    @State private var trackers = true
    @State private var tab = 0
    public init() {}

    public var body: some View {
        SGUtilityScreen("Protected",
                        span: (Text("since 08:14"), Text("lis-04")),
                        tag: .japanese("保護中"), backdrop: .tunnel) {
            // the tunnel backdrop is the hero; uptime is set large beside it
            VStack(alignment: .trailing, spacing: 6) {
                Text("Tunnel uptime").sgCap(11).foregroundStyle(SG.groundDim)
                Text("82%").sgWordmark(52).foregroundStyle(SG.groundHi)
            }
            .frame(maxWidth: .infinity, minHeight: 172, alignment: .bottomTrailing)
            .padding(.horizontal, SG.gutter)
        } content: {
            HStack(spacing: 12) {
                SGNotchFrame("Threats") { SGReadout("1284", height: 30) }
                SGNotchFrame("Data") {
                    Text("4.2 / 10 GB").sgNumber(22).foregroundStyle(SG.groundHi).padding(.bottom, 10)
                    SGCellMeter(count: 10, filled: 4)
                }
            }
            VStack(spacing: 0) {
                Toggle(isOn: $killSwitch) { Text("Kill switch").sgLabel(15) }.toggleStyle(SGToggleStyle())
                Rectangle().fill(SG.ground3).frame(height: 1).padding(.vertical, 11)
                Toggle(isOn: $trackers) { Text("Block trackers").sgLabel(15) }.toggleStyle(SGToggleStyle())
            }
            Button { } label: {
                HStack { Text("Disconnect"); SGHardX().frame(width: 12, height: 12) }
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(SGButtonStyle(.print))
        }
        .overlay(alignment: .bottom) {
            SGTabBar(selection: $tab, items: [
                .init(0, "home") { SGIcon(.home) },
                .init(1, "stats") { SGIcon(.stats) },
                .init(2, "scan") { SGIcon(.scan) },
                .init(3, "servers") { SGIcon(.grid) }
            ])
            .padding(.bottom, 8)
        }
    }

    private func tile<V: View>(_ label: String, _ value: String, @ViewBuilder art: () -> V) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(label).sgCap(11).foregroundStyle(SG.groundDim)
            Text(value).sgNumber(28).foregroundStyle(SG.groundHi)
            art()
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .topLeading)
        .chamferFrame()
    }
}

// MARK: - R · Interval timer (instruments on the utility grammar)

public struct IntervalExample: View {
    @State private var intensity = 0.7
    public init() {}
    public var body: some View {
        SGUtilityScreen("Interval", span: (Text("round 3"), Text("of 8")), tag: .japanese("計時"), monolith: .cells) {
            VStack(spacing: 10) {
                SGReadout("02:47", height: 92, hot: [2], tabular: true)
                Text("Work 45 s · rest 15 s · next: rest").sgMono(11).foregroundStyle(SG.groundDim)
            }
            .frame(maxWidth: .infinity)
        } content: {
            SGGroupLabel("Rounds", "3 / 8")
            SGCellMeter(count: 8, filled: 2, hot: 2, tall: true)
            SGGroupLabel("Intensity", "7")
            SGRuler(value: $intensity, labels: ["0", "2", "4", "6", "8", "10"])
            Button("Pause") { }.buttonStyle(SGKeycapStyle(hint: "Hold 1 s to end"))
        }
    }
}

#Preview("R · Interval · dark") { IntervalExample().preferredColorScheme(.dark).onAppear { SGFont.register() } }
#Preview("R · Interval · light") { IntervalExample().preferredColorScheme(.light).onAppear { SGFont.register() } }
#Preview("A · Launch · dark") { LaunchExample().preferredColorScheme(.dark).onAppear { SGFont.register() } }
#Preview("A · Launch · light") { LaunchExample().preferredColorScheme(.light).onAppear { SGFont.register() } }
#Preview("C · Dashboard · dark") { DashboardExample().preferredColorScheme(.dark).onAppear { SGFont.register() } }
#Preview("C · Dashboard · light") { DashboardExample().preferredColorScheme(.light).onAppear { SGFont.register() } }
