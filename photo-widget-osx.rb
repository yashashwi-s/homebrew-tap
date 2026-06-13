cask "photo-widget-osx" do
  version "1.0.0"
  sha256 "ea693e5fd66a10ff9e59f47b6190883ce4486b7f3794365d7683a310657f3a13"

  url "https://github.com/yashashwi-s/PhotoWidgetOSX/releases/download/v#{version}/PhotoWidgetOSX-#{version}.dmg"
  name "Photo Widget OSX"
  desc "Place any photo on your macOS desktop as a borderless widget with perfect aspect ratio"
  homepage "https://github.com/yashashwi-s/PhotoWidgetOSX"

  app "Photo Widget OSX.app"

  zap trash: [
    "~/Library/Application Support/PhotoWidget",
    "~/Library/Preferences/com.yashashwi.photowidgetosx.plist",
  ]
end

