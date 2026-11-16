import SwiftUI

// MARK: - Screen grammar
//
// Two tiers:
//  • UTILITY screens (most of an app) use SGUtilityScreen:
//      header  title (28) + mono subline + ONE tag (vertical Japanese, a hanko, short meta or an action)
//      hero    at most ONE form on the stripes: a pill, a number, a card, a disc or a scope
//      cut     the slab edge: always a 28 pt rise with a 12 pt coral strip
//      slab    content on a 24 pt gutter, ink on sage
//  • POSTER screens (launch, onboarding, lock screen, empty state) compose freely
//    and are the only place for the 45° coral band and stacked pills.
// Type: display 44 · title 28 · inline 15. Numbers: 88 · 40 · 28 · 15.
// Coral: the cut, plus at most one action and small state markers.

public enum SGMetrics {
    public static let cutRise: CGFloat = 28
    public static let cutStrip: CGFloat = 12
    public static let display: CGFloat = 44
    public static let title: CGFloat = 28
    public static let inline: CGFloat = 15
}

/// Slab shape whose top edge rises `rise` points from leading to trailing.
public struct SGCut: Shape {
    public var rise: CGFloat = SGMetrics.cutRise
    public init(rise: CGFloat = SGMetrics.cutRise) { self.rise = rise }
    public func path(in rect: CGRect) -> Path {
        var p = Path()
        p.move(to: CGPoint(x: rect.minX, y: rect.minY + rise))
        p.addLine(to: CGPoint(x: rect.maxX, y: rect.minY))
        p.addLine(to: CGPoint(x: rect.maxX, y: rect.maxY))
        p.addLine(to: CGPoint(x: rect.minX, y: rect.maxY))
        p.closeSubpath()
        return p
    }
}

/// The coral strip that sits on top of every slab.
public struct SGCutStrip: Shape {
    public init() {}
    public func path(in rect: CGRect) -> Path {
        let r = SGMetrics.cutRise, s = SGMetrics.cutStrip
        var p = Path()
        p.move(to: CGPoint(x: rect.minX, y: rect.minY + r))
        p.addLine(to: CGPoint(x: rect.maxX, y: rect.minY))
        p.addLine(to: CGPoint(x: rect.maxX, y: rect.minY + s))
        p.addLine(to: CGPoint(x: rect.minX, y: rect.minY + r + s))
        p.closeSubpath()
        return p
    }
}

/// What goes in the header's single right-hand slot.
public enum SGHeaderTag {
    case none
    case meta(String)                 // short mono, right-aligned (use "\n" for two lines)
    case japanese(String)             // vertical caption
    case hanko(String)                // coral seal
    case action(systemImage: String, label: String, action: () -> Void)
}

public struct SGUtilityScreen<Hero: View, Content: View>: View {
    let title: String
    let subline: Text
    let tag: SGHeaderTag
    let hero: Hero
    let content: Content

    /// `subline` is a Text so you can mix mono with a French italic aside:
    /// `Text("journal de course").font(SGFont.fr(12)) + Text(" · week 46")`
    public init(_ title: String, subline: Text, tag: SGHeaderTag = .none,
                @ViewBuilder hero: () -> Hero, @ViewBuilder content: () -> Content) {
        self.title = title; self.subline = subline; self.tag = tag
        self.hero = hero(); self.content = content()
    }

    public var body: some View {
        ZStack {
            StripeField().ignoresSafeArea()
            VStack(spacing: 0) {
                header
                hero.padding(.top, 22).padding(.bottom, 18)
                ZStack(alignment: .top) {
                    SGCut().fill(SG.sage)
                        .padding(.top, SGMetrics.cutStrip)
                        .ignoresSafeArea(edges: .bottom)
                    SGCutStrip().fill(SG.coral).frame(height: SGMetrics.cutRise + SGMetrics.cutStrip)
                    VStack(alignment: .leading, spacing: 16) { content }
                        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
                        .padding(.horizontal, SG.gutter)
                        .padding(.top, SGMetrics.cutRise + SGMetrics.cutStrip + 18)
                        .foregroundStyle(SG.ink)
                }
            }
        }
    }

    private var header: some View {
        HStack(alignment: .top, spacing: 16) {
            VStack(alignment: .leading, spacing: 7) {
                Text(title).sgWordmark(SGMetrics.title).foregroundStyle(SG.groundHi)
                subline.sgMono(11).foregroundStyle(SG.groundDim)
            }
            Spacer(minLength: 0)
            switch tag {
            case .none: EmptyView()
            case .meta(let s): Text(s).sgMono(11).multilineTextAlignment(.trailing).foregroundStyle(SG.groundDim)
            case .japanese(let s): VerticalText(s, size: 11).foregroundStyle(SG.groundDim)
            case .hanko(let s): Hanko(s)
            case .action(let img, let label, let action):
                Button(action: action) { Image(systemName: img) }
                    .buttonStyle(SGButtonStyle(.sage))
                    .accessibilityLabel(label)
            }
        }
        .padding(.horizontal, SG.gutter)
        .padding(.top, 10)
    }
}

/// Group label with a hairline: "privacy ———— 01".
public struct SGGroupLabel: View {
    var label: String; var index: String
    public init(_ label: String, _ index: String = "") { self.label = label; self.index = index }
    public var body: some View {
        VStack(spacing: 8) {
            HStack { Text(label); Spacer(); Text(index) }.sgMono(11).foregroundStyle(SG.inkDim)
            Rectangle().fill(SG.sageLo).frame(height: SG.hair)
        }
    }
}
