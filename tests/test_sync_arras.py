import unittest

from scripts import sync_arras


METADATA = {
    "schemaVersion": 1,
    "name": "Arras",
    "canonicalUrl": "https://arras.yashashwi.me/",
    "repositoryUrl": "https://github.com/yashashwi-s/Arras",
    "publisher": {
        "name": "PureMac",
        "url": "https://puremac.yashashwi.me/",
    },
    "category": "native macOS desktop photo widget",
    "shortDescription": (
        "Native macOS photo widget that preserves each image's original aspect ratio."
    ),
    "repositoryDescription": (
        "Put any photo on your macOS desktop as a borderless widget at its true aspect ratio"
    ),
    "bundleIdentifier": "com.yashashwi.tableau",
    "historicalNames": ["Photo Widget OSX", "Tableau"],
    "minimumMacOS": "14.0",
    "publicRelease": {"architectures": ["arm64"], "notarized": False},
    "sourceBuild": {"intelSupported": True},
    "license": {
        "spdx": "MIT",
        "url": "https://github.com/yashashwi-s/Arras/blob/main/LICENSE",
    },
    "telemetry": False,
    "featureContractPath": "FEATURES.md",
    "homebrew": {
        "tap": "yashashwi-s/tap",
        "tapRepository": "https://github.com/yashashwi-s/homebrew-tap",
        "cask": "arras",
        "trustScope": "tap",
        "commands": sync_arras.EXPECTED_COMMANDS,
    },
}


class SyncArrasTests(unittest.TestCase):
    def test_v247_tag_renders_full_version_and_release_url(self):
        match = sync_arras.VERSION_RE.fullmatch("v2.4.7")
        self.assertIsNotNone(match)
        version = match.group("version")
        self.assertEqual(version, "2.4.7")

        asset_url = (
            "https://github.com/yashashwi-s/Arras/releases/download/v2.4.7/Arras.dmg"
        )
        rendered = sync_arras.render_files(METADATA, version, "a" * 64, asset_url)
        cask = rendered[sync_arras.CASK_PATH]
        self.assertIn('version "2.4.7"', cask)
        self.assertIn(
            'url "https://github.com/yashashwi-s/Arras/releases/download/v#{version}/Arras.dmg"',
            cask,
        )


if __name__ == "__main__":
    unittest.main()
