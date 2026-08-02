cask "arras" do
  version "2.4.4"
  sha256 "589c34b458823f1f2cc6e56bb2c13ace639c39044b4bb82fdca55277c0fb4df6"

  url "https://github.com/yashashwi-s/Arras/releases/download/v#{version}/Arras.dmg"
  name "Arras"
  desc "Menu bar agent that pins photos to the desktop as borderless widgets"
  homepage "https://github.com/yashashwi-s/Arras"

  livecheck do
    url :url
    strategy :github_latest
  end

  # Arras ships its own updater, which replaces Arras.app in place. Left greedy,
  # `brew upgrade` would race it and reinstall a version the app already applied.
  auto_updates true
  # The release build is thin arm64, so an Intel install would drop in an app that
  # cannot launch. Refuse up front instead.
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

  # Arras is ad-hoc signed rather than notarized (Developer ID is $99/year and Arras
  # is free), so macOS quarantines it and blocks the first launch. Homebrew 6 removed
  # --no-quarantine, so clearing the flag after install is the only route left.
  caveats <<~EOS
    Arras is signed to run locally, not notarized, so macOS blocks the first open.
    Clear the quarantine flag once and it opens normally from then on:
      xattr -dr com.apple.quarantine "#{appdir}/Arras.app"

    Or right-click Arras in #{appdir}, choose Open, and confirm once.
  EOS
end
