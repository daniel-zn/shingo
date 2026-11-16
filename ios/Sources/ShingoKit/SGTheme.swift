import SwiftUI
import UIKit
import CoreText

// MARK: - Color tokens (mirror tokens/tokens.json)
//
// Two modes, same layering:
//   dark  = ink stripe ground, sage slabs          (the original poster)
//   light = sage stripe ground, paper slabs        (never white)
// Ink stays ink (buttons, slots, solid X, tab bar) and coral stays coral.

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
    // ground: the striped background and what sits directly on it
    public static let ground    = Color(light: 0xBCBFB4, dark: 0x0C0C0A)
    public static let ground2   = Color(light: 0xADB0A5, dark: 0x1F201B)   // stripe highlight
    public static let ground3   = Color(light: 0xA1A499, dark: 0x2B2C26)   // rules / rings on the ground
    public static let onGround  = Color(light: 0x1C1D19, dark: 0xD9DBD3)   // text on the ground
    public static let groundHi  = Color(light: 0x0F100D, dark: 0xC3C6BD)   // titles & art on the ground
    // slabs: the lighter layer (pills, tiles, panels)
    public static let sage      = Color(light: 0xE3E5DD, dark: 0xB8BBB0)
    public static let sageHi    = Color(light: 0xF0F1EC, dark: 0xC3C6BD)
    public static let sageLo    = Color(light: 0xD2D4CB, dark: 0xA9ACA1)
    public static let sageLine  = Color(light: 0x72746B, dark: 0x8E9089)
    public static let sageGhost = Color(light: 0xF7F8F4, dark: 0xCDD0C7)
    // ink: text on slabs and solid objects, the same in both modes
    public static let ink       = Color(light: 0x10110E, dark: 0x0C0C0A)
    public static let inkRaised = Color(hex: 0x2B2C26)                    // pressed ink, tab-bar edge
    public static let onInk     = Color(hex: 0xC3C6BD)                    // text on ink objects
    // accent
    public static let coral     = Color(hex: 0xFF715E)
    public static let coralDeep = Color(hex: 0xE65B48)

    // geometry
    public static let hair: CGFloat = 1.5
    public static let stripePeriod: CGFloat = 6
    public static let gutter: CGFloat = 24
}

// MARK: - Type

public enum SGFont {
    /// Archivo Expanded Black — wordmarks & titles (always uppercase).
    public static func wordmark(_ size: CGFloat) -> Font { .custom("ArchivoExpanded-Black", size: size) }
    /// Archivo Bold — numerals (use .monospacedDigit()).
    public static func number(_ size: CGFloat) -> Font { .custom("Archivo-Bold", size: size).monospacedDigit() }
    /// Archivo Medium — labels, tracked tight.
    public static func label(_ size: CGFloat) -> Font { .custom("Archivo-Medium", size: size) }
    /// JetBrains Mono — telemetry / metadata.
    public static func mono(_ size: CGFloat = 11) -> Font { .custom("JetBrainsMono-Regular", size: size) }

    /// Call once at launch (e.g. in your App init). Registers the bundled OFL fonts
    /// so you don't need UIAppFonts entries in Info.plist.
    public static func register() {
        let names = ["ArchivoExpanded-Black", "Archivo-Bold", "Archivo-Medium", "JetBrainsMono-Regular", "JetBrainsMono-Bold", "Archivo-MediumItalic"]
        for name in names {
            guard let url = Bundle.module.url(forResource: name, withExtension: "ttf") else { continue }
            CTFontManagerRegisterFontsForURL(url as CFURL, .process, nil)
        }
    }
}

public extension View {
    func sgWordmark(_ size: CGFloat) -> some View {
        font(SGFont.wordmark(size)).textCase(.uppercase).tracking(-size * 0.01).lineSpacing(-size * 0.12)
    }
    func sgLabel(_ size: CGFloat = 15) -> some View {
        font(SGFont.label(size)).tracking(-size * 0.035)
    }
    func sgMono(_ size: CGFloat = 11) -> some View {
        font(SGFont.mono(size))
    }
    func sgNumber(_ size: CGFloat) -> some View {
        font(SGFont.number(size)).tracking(-size * 0.02)
    }
}
