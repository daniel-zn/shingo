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
    // multi-series telemetry: coral-harmonized inks for dense multi-series meters and pips
    // (Coral stays reserved for alerts, thresholds and the single primary signal.)
    public static let series1   = Color(light: 0x15593E, dark: 0x5CD6A0)   // jade (split-complement of coral)
    public static let series2   = Color(light: 0x184E8E, dark: 0x5BA8FF)   // cerulean (cool architectural counterpoint)
    public static let series3   = Color(light: 0x694808, dark: 0xF2C14E)   // marigold (warm ochre sibling)
    public static let series4   = Color(light: 0x5B3A9B, dark: 0xB388FF)   // iris (spaced 4th hue)

    // geometry: one angle (45°), three cut sizes
    public static let hair: CGFloat = 1.5
    public static let stripePeriod: CGFloat = 6
    public static let gutter: CGFloat = 24
    public static let cutS: CGFloat = 6
    public static let cutM: CGFloat = 12
    public static let cutL: CGFloat = 24
}

// MARK: - Type: wide, short, hard

/// Shingo Grid's own numbers (tools/font.py), per em. The three weights share them.
public enum SGFace {
    public static let capHeight: CGFloat = 0.70
    public static let xHeight: CGFloat = 0.54
    /// One tabular figure's advance; readouts that tick give each digit a cell this wide.
    public static let figureCell: CGFloat = 0.84
    /// Heavy's tracking by size, in points.
    public static func tracking(_ size: CGFloat) -> CGFloat {
        min(max(1.32 - 0.03 * size, -0.012 * size), 0.07 * size)
    }
    /// Bold and Medium caps: about +.11 em at 11 pt, +.08 em at 14, +.03 em at 24
    /// (the web's `clamp(.02em, 1.8px - .05em, .12em)`).
    public static func capTracking(_ size: CGFloat) -> CGFloat {
        min(max(1.8 - 0.05 * size, 0.02 * size), 0.12 * size)
    }
}

public enum SGFont {
    /// Shingo Grid Heavy: display wordmarks and screen titles (18 pt and up). A cut-plate grotesque:
    /// one heavy weight, cap height 0.7 em, corners cut at 45° top-left and bottom-right only.
    public static func display(_ size: CGFloat) -> Font { .custom("ShingoGrid-Heavy", size: size) }
    /// Shingo Grid Bold: subheads and inline wordmarks below 18 pt.
    public static func title(_ size: CGFloat) -> Font { .custom("ShingoGrid-Bold", size: size) }
    /// Shingo Grid Heavy: big figures in text (proportional; `.monospacedDigit()` gives the tabular set).
    public static func number(_ size: CGFloat) -> Font { .custom("ShingoGrid-Heavy", size: size) }
    /// Shingo Grid Medium: labels in caps ("FUTURE ENGINEERING"), buttons, chips, tabs.
    public static func cap(_ size: CGFloat) -> Font { .custom("ShingoGrid-Medium", size: size) }
    /// Anybody Medium: body and row labels.
    public static func body(_ size: CGFloat = 15) -> Font { .custom("Anybody-Medium", size: size) }
    /// Anybody Expanded Bold: emphasised lines (the trilingual stack).
    public static func bodyBold(_ size: CGFloat = 15) -> Font { .custom("AnybodyExpanded-Bold", size: size) }
    /// IBM Plex Mono Medium: telemetry and metadata.
    public static func mono(_ size: CGFloat = 11) -> Font { .custom("IBMPlexMono-Medium", size: size) }
    /// Shingo Grid Stencil: the Heavy, bridged on the system's diagonal. Stamped numerals, serials,
    /// stamps; capitals and figures (lowercase sets in capitals). Once per screen.
    public static func stencil(_ size: CGFloat) -> Font { .custom("ShingoGrid-Stencil", size: size) }

    /// Call once at launch (e.g. in your App init). Registers the bundled OFL fonts
    /// so you don't need UIAppFonts entries in Info.plist.
    public static func register() {
        let names = ["ShingoGrid-Heavy", "ShingoGrid-Bold", "ShingoGrid-Medium", "AnybodyExtraExpanded-ExtraBold", "AnybodyExpanded-Bold", "AnybodyExpanded-SemiBold", "Anybody-Medium",
                     "Anybody-MediumItalic", "ShingoGrid-Stencil", "IBMPlexMono-Medium"]
        for name in names {
            guard let url = Bundle.module.url(forResource: name, withExtension: "ttf") else { continue }
            CTFontManagerRegisterFontsForURL(url as CFURL, .process, nil)
        }
    }
}

public extension View {
    /// Wordmark: Shingo Grid Heavy at 18 pt and up (display, titles), Shingo Grid Bold below (inline).
    /// The face is drawn tight, so it opens up as it gets small and closes up when huge
    /// (the web's `clamp(-.012em, 1.32px - .03em, .07em)` for Heavy, `SGFace.capTracking` below 18 pt).
    func sgWordmark(_ size: CGFloat) -> some View {
        font(size >= 18 ? SGFont.display(size) : SGFont.title(size)).textCase(.uppercase)
            .tracking(size >= 18 ? SGFace.tracking(size) : SGFace.capTracking(size))
    }
    /// Caps label in Shingo Grid Medium, tracked out by size.
    func sgCap(_ size: CGFloat = 12) -> some View {
        font(SGFont.cap(size)).textCase(.uppercase).tracking(SGFace.capTracking(size))
    }
    func sgLabel(_ size: CGFloat = 15) -> some View { font(SGFont.body(size)) }
    /// Telemetry. Uppercase by default, like the print.
    func sgMono(_ size: CGFloat = 11, upper: Bool = true) -> some View {
        font(SGFont.mono(size)).textCase(upper ? .uppercase : nil).tracking(size * 0.04)
    }
    func sgNumber(_ size: CGFloat) -> some View { font(SGFont.number(size)) }
    func sgStencil(_ size: CGFloat) -> some View { font(SGFont.stencil(size)).textCase(.uppercase).tracking(size * 0.02) }
}
