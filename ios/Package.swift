// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "SignalKit",
    platforms: [.iOS(.v17)],
    products: [.library(name: "SignalKit", targets: ["SignalKit"])],
    targets: [
        .target(
            name: "SignalKit",
            resources: [.process("Resources")]
        )
    ]
)
