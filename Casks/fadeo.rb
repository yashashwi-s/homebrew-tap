cask "fadeo" do
  version "0.3.0"
  sha256 "05333b6607c71cf5303a311c93583a7e385c9e5cdc35b7f7354415f1ed3203ae"

  url "https://github.com/yashashwi-s/Fadeo/releases/download/v#{version}/Fadeo.dmg"
  name "Fadeo"
  desc "Plays, fades, and switches audio automatically based on what you're doing"
  homepage "https://github.com/yashashwi-s/Fadeo"

  app "Fadeo.app"

  # Fadeo is open source and ad-hoc signed (no paid Apple Developer ID yet), so macOS
  # Gatekeeper warns on first launch.
  caveats <<~EOS
    Fadeo is signed to run locally, not notarized, so macOS warns on first open.
    Right-click Fadeo in Applications and choose Open (then confirm once), or run:
      xattr -dr com.apple.quarantine "/Applications/Fadeo.app"
  EOS

  zap trash: [
    "~/Library/Application Support/Fadeo",
    "~/Library/Preferences/com.fadeo.Fadeo.plist",
  ]
end
