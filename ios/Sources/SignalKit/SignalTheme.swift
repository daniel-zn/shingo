import SwiftUI
import CoreText

// MARK: - Color tokens (mirror tokens/tokens.json)

public extension Color {
    init(hex: UInt32, opacity: Double = 1) {
        self.init(.sRGB,
                  red: Double((hex >> 16) & 0xFF) / 255,
                  green: Double((hex >> 8) & 0xFF) / 255,
                  blue: Double(hex & 0xFF) / 255,
                  opacity: opacity)
    }
}

public enum SG {
    // ground
    public static let ink       = Color(hex: 0x0C0C0A)
    public static let ink2      = Color(hex: 0x1F201B)   // stripe highlight
    public static let ink3      = Color(hex: 0x2B2C26)   // raised ink
    // slabs
    public static let sage      = Color(hex: 0xB8BBB0)
    public static let sageHi    = Color(hex: 0xC3C6BD)
    public static let sageLo    = Color(hex: 0xA9ACA1)
    public static let sageLine  = Color(hex: 0x8E9089)
    public static let sageGhost = Color(hex: 0xCDD0C7)
    // accent
    public static let coral     = Color(hex: 0xFF715E)
    public static let coralDeep = Color(hex: 0xE65B48)
    public static let onInk     = Color(hex: 0xD9DBD3)

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
