cask "fadeo" do
  version "0.4.0"
  sha256 "2129b6ef771b7e990cbd93a79ef25686760a9f35c0e8eb9e861c516bd1aa8e5e"

  url "https://github.com/yashashwi-s/Fadeo/releases/download/v#{version}/Fadeo.dmg"
  name "Fadeo"
  desc "Plays, fades, and switches audio automatically based on what you're doing"
  homepage "https://github.com/yashashwi-s/Fadeo"

  livecheck do
    url :url
    strategy :github_latest
  end

  # The release build is thin arm64, so an Intel install would drop in an app that
  # cannot launch. Refuse up front instead.
  depends_on arch: :arm64
  depends_on macos: :sonoma

  app "Fadeo.app"

  zap trash: [
    "~/Library/Application Support/Fadeo",
    "~/Library/Preferences/com.fadeo.Fadeo.plist",
  ]

  # Fadeo is open source and ad-hoc signed (no paid Apple Developer ID yet), so macOS
  # Gatekeeper warns on first launch.
  caveats <<~EOS
    Fadeo is signed to run locally, not notarized, so macOS warns on first open.
    Right-click Fadeo in Applications and choose Open (then confirm once), or run:
      xattr -dr com.apple.quarantine "/Applications/Fadeo.app"
  EOS
end
