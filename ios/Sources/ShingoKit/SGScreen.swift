import SwiftUI

// MARK: - Screen grammar (industrial print)
//
// Two tiers:
//  • UTILITY screens (most of an app) use SGUtilityScreen. Content prints
//    straight onto the striped ground:
//      masthead  vertical code + title (26) + ONE tag (vertical Japanese, a hanko,
//                short meta or one action), then a span rule "value ──── value"
//      hero      at most ONE form: a bar, a number, a plate, a scope, chevrons
//      divider   a hazard bar on the gutter
//      body      rows and frames; labels in condensed caps, telemetry in mono
//  • POSTER screens (launch, onboarding, lock screen, empty state) compose freely.
// One angle (45°). Type: display 44 · title 26 · inline 15.
// Coral: one signal block or one primary action per screen, plus small states.
// Languages: Japanese in the masthead tag or a seal; French in the span rule.

public enum SGMetrics {
    public static let display: CGFloat = 40
    public static let title: CGFloat = 28
    public static let inline: CGFloat = 14
}

/// What goes in the masthead's single right-hand slot.
public enum SGHeaderTag {
    case none
    case meta(String)                 // short mono, right-aligned (use "\n" for two lines)
    case japanese(String)             // vertical caption
    case hanko(String)                // coral seal
    case action(systemImage: String, label: String, action: () -> Void)
}

/// Vertical micro-code beside a title ("AX·09"), like the shirt's tiny side text.
public struct SGCode: View {
    var text: String
    public init(_ text: String) { self.text = text }
    public var body: some View {
        SGScrambleText(text, weight: .label).sgMono(7).tracking(1.6).foregroundStyle(SG.groundDim)
            .fixedSize()
            .rotationEffect(.degrees(-90))
            .frame(width: 9, height: CGFloat(text.count) * 6.5)
    }
}

public struct SGUtilityScreen<Hero: View, Content: View>: View {
    let title: String
    let code: String
    let spanLeading: Text
    let spanTrailing: Text
    let tag: SGHeaderTag
    let hero: Hero
    let content: Content
    let backdrop: SGBackdropKind?

    /// Span texts are `Text` so a French aside can be mixed in:
    /// `Text("journal de course").font(SGFont.fr(12))`
    public init(_ title: String, code: String = "AX·09",
                span: (Text, Text), tag: SGHeaderTag = .none, backdrop: SGBackdropKind? = nil,
                @ViewBuilder hero: () -> Hero, @ViewBuilder content: () -> Content) {
        self.title = title; self.code = code
        self.spanLeading = span.0; self.spanTrailing = span.1
        self.tag = tag; self.backdrop = backdrop; self.hero = hero(); self.content = content()
    }

    public var body: some View {
        ZStack {
            StripeField().ignoresSafeArea()
            if let b = backdrop { SGBackdrop(b).ignoresSafeArea() }
            VStack(spacing: 0) {
                masthead
                hero.padding(.top, 20).padding(.bottom, 18)
                HazardBar().padding(.horizontal, SG.gutter)
                VStack(alignment: .leading, spacing: 14) { content }
                    .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
                    .padding(.horizontal, SG.gutter)
                    .padding(.top, 18)
                    .foregroundStyle(SG.onGround)
            }
        }
    }

    private var masthead: some View {
        VStack(spacing: 12) {
            HStack(alignment: .bottom, spacing: 10) {
                SGCode(code)
                SGScrambleText(title).sgWordmark(SGMetrics.title).foregroundStyle(SG.groundHi)
                Spacer(minLength: 0)
                tagView
            }
            HStack(spacing: 10) {
                spanLeading
                Rectangle().fill(SG.groundDim).frame(height: SG.hair)
                spanTrailing
            }
            .sgMono(11)
            .foregroundStyle(SG.onGround)
        }
        .padding(.horizontal, SG.gutter)
        .padding(.top, 8)
    }

    @ViewBuilder private var tagView: some View {
        switch tag {
        case .none: EmptyView()
        case .meta(let s): Text(s).sgMono(11).multilineTextAlignment(.trailing).foregroundStyle(SG.groundDim)
        case .japanese(let s): VerticalText(s, size: 11).foregroundStyle(SG.groundDim)
        case .hanko(let s): Hanko(s)
        case .action(let img, let label, let action):
            Button(action: action) { Image(systemName: img) }
                .buttonStyle(SGButtonStyle(.plate))
                .accessibilityLabel(label)
        }
    }
}

/// The imprint that closes a screen, like a garment print's footer:
/// print rule, wide-caps line, mono reference, barcode.
public struct SGFooter: View {
    var line: String; var ref: String
    public init(_ line: String = "Axiom signal systems", ref: String) { self.line = line; self.ref = ref }
    public var body: some View {
        VStack(spacing: 12) {
            Rectangle().fill(SG.groundHi).frame(height: SG.hair)
            HStack(alignment: .bottom, spacing: 16) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(line).sgWordmark(12).foregroundStyle(SG.groundHi)
                    Text(ref).sgMono(9.5).foregroundStyle(SG.groundDim)
                }
                Spacer(minLength: 0)
                Barcode(axis: .horizontal, color: SG.groundHi).frame(width: 112, height: 26)
            }
        }
    }
}
