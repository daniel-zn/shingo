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
    // plates: filled blocks for things you press or carry
    public static let sage      = Color(light: 0xE3E5DD, dark: 0xB8BBB0)
    public static let sageHi    = Color(light: 0xECEEE7, dark: 0xC9CCC2)
    public static let sageLo    = Color(light: 0xD2D4CB, dark: 0xA9ACA1)
    public static let sageLine  = Color(light: 0x72746B, dark: 0x8E9089)
    // ink: text on plates and solid objects
    public static let ink       = Color(light: 0x10110E, dark: 0x0C0C0A)
    public static let inkDim    = Color(light: 0x5A5C54, dark: 0x4D4F49)
    public static let inkFixed  = Color(hex: 0x0C0C0A)                    // text on coral, both modes
    // signal
    public static let coral     = Color(hex: 0xFF715E)
    public static let coralDeep = Color(hex: 0xE65B48)

    // geometry: one angle (45°), three cut sizes
    public static let hair: CGFloat = 1.5
    public static let stripePeriod: CGFloat = 6
    public static let gutter: CGFloat = 24
    public static let cutS: CGFloat = 6
    public static let cutM: CGFloat = 12
    public static let cutL: CGFloat = 24
}

// MARK: - Type: hard, chamfered, industrial

public enum SGFont {
    /// Tektur Black: wordmarks, titles, display (uppercase). Cut-corner letterforms.
    public static func display(_ size: CGFloat) -> Font { .custom("Tektur-Black", size: size) }
    /// Tektur ExtraBold: numerals in text.
    public static func number(_ size: CGFloat) -> Font { .custom("Tektur-ExtraBold", size: size).monospacedDigit() }
    /// Tektur Condensed SemiBold: labels in caps ("FUTURE ENGINEERING").
    public static func cap(_ size: CGFloat) -> Font { .custom("TekturCondensed-SemiBold", size: size) }
    /// Tektur Medium: body and row labels.
    public static func body(_ size: CGFloat = 15) -> Font { .custom("Tektur-Medium", size: size) }
    /// Tektur Bold: emphasised body (the trilingual stack).
    public static func bodyBold(_ size: CGFloat = 15) -> Font { .custom("Tektur-Bold", size: size) }
    /// Kode Mono: telemetry and metadata.
    public static func mono(_ size: CGFloat = 11) -> Font { .custom("KodeMono-Regular", size: size) }
    /// Big Shoulders Stencil: stamped numerals, serials, stamps. Once per screen.
    public static func stencil(_ size: CGFloat) -> Font { .custom("BigShouldersStencilDisplay-ExtraBold", size: size) }

    /// Call once at launch (e.g. in your App init). Registers the bundled OFL fonts
    /// so you don't need UIAppFonts entries in Info.plist.
    public static func register() {
        let names = ["Tektur-Black", "Tektur-ExtraBold", "Tektur-Bold", "Tektur-Medium", "TekturCondensed-SemiBold",
                     "KodeMono-Regular", "BigShouldersStencilDisplay-ExtraBold", "ChakraPetch-MediumItalic", "DotGothic16-Regular"]
        for name in names {
            guard let url = Bundle.module.url(forResource: name, withExtension: "ttf") else { continue }
            CTFontManagerRegisterFontsForURL(url as CFURL, .process, nil)
        }
    }
}

public extension View {
    /// Display / title / inline wordmark. Sizes: 44, 26, 15.
    func sgWordmark(_ size: CGFloat) -> some View {
        font(SGFont.display(size)).textCase(.uppercase)
    }
    /// Condensed caps label, tracked out.
    func sgCap(_ size: CGFloat = 12) -> some View {
        font(SGFont.cap(size)).textCase(.uppercase).tracking(size * 0.12)
    }
    func sgLabel(_ size: CGFloat = 15) -> some View { font(SGFont.body(size)) }
    /// Telemetry. Uppercase by default, like the print.
    func sgMono(_ size: CGFloat = 11, upper: Bool = true) -> some View {
        font(SGFont.mono(size)).textCase(upper ? .uppercase : nil).tracking(size * 0.04)
    }
    func sgNumber(_ size: CGFloat) -> some View { font(SGFont.number(size)) }
    func sgStencil(_ size: CGFloat) -> some View { font(SGFont.stencil(size)).textCase(.uppercase).tracking(size * 0.04) }
}
