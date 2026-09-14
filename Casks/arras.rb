cask "arras" do
  version "2.4.7"
  sha256 "3fc25bc82d775e8dccbd6ee4ab51717cfb2928ee0a666d489a326d2b69a74497"

  url "https://github.com/yashashwi-s/Arras/releases/download/v#{version}/Arras.dmg"
  name "Arras"
  desc "Photo widget that preserves each image's original aspect ratio"
  homepage "https://arras.yashashwi.me/"

  livecheck do
    url :url
    strategy :github_latest
  end

  # Arras ships its own updater, which replaces Arras.app in place. Left greedy,
  # `brew upgrade` would race it and reinstall a version the app already applied.
  auto_updates true
  # Published release artifacts are arm64. Intel remains supported from source.
  depends_on arch: :arm64
  depends_on macos: :sonoma

  app "Arras.app"

  # Arras is LSUIElement and stays resident, so an upgrade over a running copy would
  # otherwise leave the old process holding the replaced bundle.
  uninstall quit: "com.yashashwi.tableau"

  zap trash: [
    "~/Library/Application Support/PhotoWidget",
    "~/Library/Caches/com.yashashwi.tableau",
    # Pre-2.0 sandboxed builds kept everything here; see StorageMigration.swift.
    "~/Library/Containers/com.yashashwi.tableau",
    "~/Library/HTTPStorages/com.yashashwi.tableau",
    "~/Library/Preferences/com.yashashwi.tableau.plist",
  ]

  # Arras is ad-hoc signed rather than notarized. Homebrew tap trust verifies the
  # cask source; it does not change macOS Gatekeeper's assessment of the app.
  caveats <<~EOS
    Arras is ad-hoc signed and not notarized. Before opening it, verify that this
    cask came from the official yashashwi-s/tap distribution. Try opening Arras
    normally first. If macOS blocks it, use System Settings > Privacy & Security >
    Open Anyway, or right-click Arras in #{appdir}, choose Open, and confirm.

    If those options are unavailable and you trust the official build, remove the
    quarantine attribute as an explicit fallback:
      xattr -dr com.apple.quarantine "#{appdir}/Arras.app"

    `brew trust yashashwi-s/tap` trusts the Homebrew tap; it does not notarize Arras
    or bypass Gatekeeper.
  EOS
end
