// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "ShingoKit",
    platforms: [.iOS(.v17)],
    products: [.library(name: "ShingoKit", targets: ["ShingoKit"])],
    targets: [
        .target(
            name: "ShingoKit",
            resources: [.process("Resources")]
        )
    ]
)
