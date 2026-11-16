import SwiftUI

// Two of the gallery screens rebuilt in SwiftUI from kit parts,
// so you can compare them with dist/index.html (screens A and C).

// MARK: - A · Launch

public struct LaunchExample: View {
    public var progress: Double = 0.64
    public init(progress: Double = 0.64) { self.progress = progress }

    public var body: some View {
        GeometryReader { geo in
            let w = geo.size.width, h = geo.size.height
            ZStack(alignment: .topLeading) {
                StripeField(facets: [
                    .init(angle: .degrees(-16), polygon: [.init(x: 0, y: 0), .init(x: 1, y: 0), .init(x: 1, y: 0.03), .init(x: 0, y: 0.28)]),
                    .init(angle: .degrees(-60), polygon: [.init(x: 0, y: 0.40), .init(x: 0.46, y: 0.33), .init(x: 0, y: 0.72)])
                ])

                // brand row
                HStack(spacing: 10) {
                    Color.clear.frame(width: 22, height: 22).diamondMark()
                    Text("AXIOM").sgWordmark(17).foregroundStyle(SG.groundHi)
                    Text("secure suite").sgLabel(12).foregroundStyle(SG.onGround)
                }
                .offset(x: 24, y: 66)

                // coral wedge + outline X, top right
                UnitPolygon([.init(x: 1, y: 0), .init(x: 1, y: 1), .init(x: 0, y: 1)])
                    .fill(SG.coral).frame(width: 150, height: 150).offset(x: w - 150, y: 60)
                RoundedX().stroke(SG.groundHi, style: StrokeStyle(lineWidth: 7, lineJoin: .round))
                    .frame(width: 96, height: 96).offset(x: w - 114, y: 56)

                NestedPill(height: 118, bleed: .leading).frame(width: w * 0.65).offset(y: 118)
                Crosshair().stroke(SG.groundHi, lineWidth: 1.5).frame(width: 22, height: 22).offset(x: 258, y: 226)
                NestedPill(height: 118, bleed: .trailing, progress: 0.58).frame(width: w - 84).offset(x: 84, y: 262)

                // coral band + sage slab along one diagonal
                UnitPolygon([.init(x: 150/240, y: 0), .init(x: 1, y: 0), .init(x: 0, y: 1), .init(x: 0, y: 246/300)])
                    .fill(SG.coral).frame(width: 240, height: 300).offset(y: 360)
                UnitPolygon([.init(x: 229 / w, y: 0), .init(x: 1, y: 0), .init(x: 1, y: 1), .init(x: 0, y: 1), .init(x: 0, y: 286 / (h - 374))])
                    .fill(SG.sage).frame(width: w, height: h - 374).offset(y: 374)

                RoundedX().stroke(SG.sageHi, style: StrokeStyle(lineWidth: 9, lineJoin: .round))
                    .frame(width: 130, height: 130).offset(x: 150, y: 470)

                VStack(alignment: .trailing, spacing: 8) {
                    HStack(spacing: 10) {
                        Color.clear.frame(width: 26, height: 26).diamondMark()
                        Text("AXIOM").sgWordmark(40)
                    }
                    Text("secure\nworkspace").sgMono(12).multilineTextAlignment(.trailing)
                    Text("09").sgNumber(15).padding(.top, 30)
                    Spacer().frame(height: 50)
                    Text("verifying keys\nsealing tunnel\n\(Int(progress * 100))%").sgMono(12).multilineTextAlignment(.trailing)
                    SGSlot(progress: progress).frame(width: w - 174)
                }
                .foregroundStyle(SG.ink)
                .frame(width: w - 48, alignment: .trailing)
                .offset(x: 24, y: 420)
            }
        }
        .ignoresSafeArea()
    }
}

// MARK: - C · Dashboard

public struct DashboardExample: View {
    @State private var killSwitch = true
    @State private var trackers = true
    @State private var tab = 0
    public init() {}

    public var body: some View {
        ZStack(alignment: .top) {
            StripeField(angle: .degrees(-34)).ignoresSafeArea()

            VStack(spacing: 0) {
                // header
                HStack {
                    Color.clear.frame(width: 22, height: 22).diamondMark()
                    Text("AXIOM").sgWordmark(18).foregroundStyle(SG.groundHi)
                    Spacer()
                    Circle().fill(SG.sageHi).frame(width: 40, height: 40)
                        .overlay(RecordDisc().padding(4))
                }
                .padding(.horizontal, SG.gutter).padding(.top, 12)

                // hero pill + telemetry
                HStack(alignment: .top) {
                    NestedPill(height: 124, bleed: .leading, progress: 0.82).frame(width: 318)
                    Spacer()
                    VStack(alignment: .trailing) {
                        Text("tunnel").sgMono().foregroundStyle(SG.sageLine)
                        Text("lis-04").sgMono().foregroundStyle(SG.onGround)
                        Spacer()
                        Text("23 ms").sgNumber(15).foregroundStyle(SG.groundHi)
                    }
                    .padding(.trailing, 20)
                }
                .frame(height: 124).padding(.top, 18)

                // sage slab
                ZStack(alignment: .topLeading) {
                    SG.sage
                    UnitPolygon([.init(x: 0, y: 0), .init(x: 1, y: 0), .init(x: 0, y: 1)]).fill(SG.coral).frame(width: 110, height: 70)
                    VStack(alignment: .trailing, spacing: 16) {
                        VStack(alignment: .trailing, spacing: 8) {
                            Text("PROTECTED").sgWordmark(34)
                            Text("since 08:14 · 2 h 31 min · wireguard").sgMono()
                        }
                        .frame(maxWidth: .infinity, alignment: .trailing)

                        HStack(spacing: 12) {
                            tile("threats blocked", "1,284") { Barcode(axis: .horizontal).frame(height: 36) }
                            tile("data routed", "4.2 GB") { RingsCoil().frame(height: 60) }
                        }

                        VStack(spacing: 0) {
                            Toggle(isOn: $killSwitch) { Text("Kill switch").sgLabel(15) }.toggleStyle(SGToggleStyle())
                            Rectangle().fill(SG.sageLo).frame(height: SG.hair).padding(.vertical, 12)
                            Toggle(isOn: $trackers) { Text("Block trackers").sgLabel(15) }.toggleStyle(SGToggleStyle())
                        }

                        Button { } label: { HStack { Text("Disconnect"); RoundedX().frame(width: 14, height: 14) } }
                            .buttonStyle(SGButtonStyle(.coral))
                            .frame(maxWidth: .infinity)
                    }
                    .foregroundStyle(SG.ink)
                    .padding(.horizontal, SG.gutter).padding(.top, 24)
                }
                .ignoresSafeArea(edges: .bottom)
            }

            VStack {
                Spacer()
                SGTabBar(selection: $tab, items: [
                    .init(0, "home") { DiamondMark().fill(style: FillStyle(eoFill: true)) },
                    .init(1, "stats") { Barcode(axis: .vertical, color: tab == 1 ? SG.coral : SG.sageLine) },
                    .init(2, "scan") { Circle().strokeBorder(lineWidth: 2) },
                    .init(3, "servers") { Crosshair().stroke(lineWidth: 2) }
                ])
                .padding(.bottom, 8)
            }
        }
    }

    private func tile<V: View>(_ label: String, _ value: String, @ViewBuilder art: () -> V) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(label).sgMono()
            Text(value).sgNumber(28)
            art()
        }
        .padding(16)
        .frame(maxWidth: .infinity, minHeight: 150, alignment: .topLeading)
        .chamferFrame()
    }
}

#Preview("A · Launch · dark") { LaunchExample().preferredColorScheme(.dark).onAppear { SGFont.register() } }
#Preview("A · Launch · light") { LaunchExample().preferredColorScheme(.light).onAppear { SGFont.register() } }
#Preview("C · Dashboard · dark") { DashboardExample().preferredColorScheme(.dark).onAppear { SGFont.register() } }
#Preview("C · Dashboard · light") { DashboardExample().preferredColorScheme(.light).onAppear { SGFont.register() } }
