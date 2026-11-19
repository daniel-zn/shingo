import SwiftUI
import UIKit
import CoreText

// MARK: - Color tokens (mirror tokens/tokens.json)
//
// Industrial print system, two modes with the same layering:
//   dark  = ink stripe ground, bone print, sage plates
//   light = sage stripe ground, ink print, paper plates (never white)
// Coral is the signal and is the same in both.

public extension Color {
    init(hex: UInt32, opacity: Double = 1) {
        self.init(.sRGB,
                  red: Double((hex >> 16) & 0xFF) / 255,
                  green: Double((hex >> 8) & 0xFF) / 255,
                  blue: Double(hex & 0xFF) / 255,
                  opacity: opacity)
    }
    /// Resolves per trait collection, so it follows the system appearance
    /// and `.preferredColorScheme(...)` overrides.
    init(light: UInt32, dark: UInt32) {
        self.init(UIColor { traits in
            let hex = traits.userInterfaceStyle == .dark ? dark : light
            return UIColor(red: CGFloat((hex >> 16) & 0xFF) / 255,
                           green: CGFloat((hex >> 8) & 0xFF) / 255,
                           blue: CGFloat(hex & 0xFF) / 255, alpha: 1)
        })
    }
}

public enum SG {
    // ground: the striped background, and the print on it
    public static let ground    = Color(light: 0xBCBFB4, dark: 0x0B0B0A)
    public static let ground2   = Color(light: 0xB0B3A8, dark: 0x1B1C18)   // stripe highlight
    public static let ground3   = Color(light: 0x9FA297, dark: 0x2E2F2A)   // rules, frames, tracks
    public static let onGround  = Color(light: 0x1C1D19, dark: 0xC9CCC2)   // body text on the ground
    public static let groundHi  = Color(light: 0x0F100D, dark: 0xDCDFD5)   // the print: titles, line art
    public static let groundDim = Color(light: 0x4D4F47, dark: 0x8B8D85)   // secondary print
    // plates: solid print with knocked-out text (two-ink screen print, no third tone)
    public static let sage      = Color(light: 0x0F100D, dark: 0xDCDFD5)
    public static let sageHi    = Color(light: 0x0F100D, dark: 0xDCDFD5)
    public static let sageLo    = Color(light: 0x4D4F47, dark: 0x8B8D85)
    public static let sageLine  = Color(light: 0x4D4F47, dark: 0x8B8D85)
    // ink: text knocked out of a plate (= the ground colour)
    public static let ink       = Color(light: 0xBCBFB4, dark: 0x0B0B0A)
    public static let inkDim    = Color(light: 0x8E9187, dark: 0x55574F)
    public static let inkFixed  = Color(hex: 0x0C0C0A)                    // text on coral, both modes
    // signal
    public static let coral     = Color(hex: 0xFF715E)
    public static let coralDeep = Color(hex: 0xE65B48)
    /// Coral used as text: full coral on ink, a deeper coral on sage so small type stays legible.
    public static let signalText = Color(light: 0x8F2B1C, dark: 0xFF715E)
    /// Coral as text inside a print plate, where the ground flips: full coral on ink plates, deep coral on bone plates.
    public static let signalPlate = Color(light: 0xFF715E, dark: 0x8F2B1C)

    // geometry: one angle (45°), three cut sizes
    public static let hair: CGFloat = 1.5
    public static let stripePeriod: CGFloat = 6
    public static let gutter: CGFloat = 24
    public static let cutS: CGFloat = 6
    public static let cutM: CGFloat = 12
    public static let cutL: CGFloat = 24
}

// MARK: - Type: wide, short, hard

public enum SGFont {
    /// Shingo Grid Heavy: display wordmarks and screen titles (18 pt and up). One heavy stroke, 45° cuts.
    public static func display(_ size: CGFloat) -> Font { .custom("ShingoGrid-Heavy", size: size) }
    /// Shingo Signal ExtraBold (Orbitron, completed): subheads and inline wordmarks below 18 pt.
    public static func title(_ size: CGFloat) -> Font { .custom("ShingoSignal-ExtraBold", size: size) }
    /// Shingo Grid Heavy: big figures in text.
    public static func number(_ size: CGFloat) -> Font { .custom("ShingoGrid-Heavy", size: size) }
    /// Shingo Signal SemiBold: labels in caps ("FUTURE ENGINEERING"), buttons, chips.
    public static func cap(_ size: CGFloat) -> Font { .custom("ShingoSignal-SemiBold", size: size) }
    /// Anybody Medium: body and row labels.
    public static func body(_ size: CGFloat = 15) -> Font { .custom("Anybody-Medium", size: size) }
    /// Anybody Expanded Bold: emphasised lines (the trilingual stack).
    public static func bodyBold(_ size: CGFloat = 15) -> Font { .custom("AnybodyExpanded-Bold", size: size) }
    /// IBM Plex Mono Medium: telemetry and metadata.
    public static func mono(_ size: CGFloat = 11) -> Font { .custom("IBMPlexMono-Medium", size: size) }
    /// Saira Stencil One: stamped numerals, serials, stamps. Wide. Once per screen.
    public static func stencil(_ size: CGFloat) -> Font { .custom("SairaStencilOne-Regular", size: size) }

    /// Call once at launch (e.g. in your App init). Registers the bundled OFL fonts
    /// so you don't need UIAppFonts entries in Info.plist.
    public static func register() {
        let names = ["ShingoGrid-Heavy", "ShingoSignal-ExtraBold", "ShingoSignal-SemiBold", "AnybodyExtraExpanded-ExtraBold", "AnybodyExpanded-Bold", "AnybodyExpanded-SemiBold", "Anybody-Medium",
                     "Anybody-MediumItalic", "SairaStencilOne-Regular", "IBMPlexMono-Medium"]
        for name in names {
            guard let url = Bundle.module.url(forResource: name, withExtension: "ttf") else { continue }
            CTFontManagerRegisterFontsForURL(url as CFURL, .process, nil)
        }
    }
}

public extension View {
    /// Wordmark: Shingo Grid Heavy at 18 pt and up (display, titles), Shingo Signal ExtraBold below (inline).
    func sgWordmark(_ size: CGFloat) -> some View {
        font(size >= 18 ? SGFont.display(size) : SGFont.title(size)).textCase(.uppercase).tracking(size * 0.01)
    }
    /// Condensed caps label, tracked out.
    func sgCap(_ size: CGFloat = 12) -> some View {
        font(SGFont.cap(size)).textCase(.uppercase).tracking(size * 0.05)
    }
    func sgLabel(_ size: CGFloat = 15) -> some View { font(SGFont.body(size)) }
    /// Telemetry. Uppercase by default, like the print.
    func sgMono(_ size: CGFloat = 11, upper: Bool = true) -> some View {
        font(SGFont.mono(size)).textCase(upper ? .uppercase : nil).tracking(size * 0.04)
    }
    func sgNumber(_ size: CGFloat) -> some View { font(SGFont.number(size)) }
    func sgStencil(_ size: CGFloat) -> some View { font(SGFont.stencil(size)).textCase(.uppercase).tracking(size * 0.04) }
}
