# yashashwi-s/tap

[Homebrew](https://brew.sh/) casks for [PureMac](https://puremac.yashashwi.me/)
native macOS apps.

```bash
brew tap yashashwi-s/tap
brew trust yashashwi-s/tap
```

This intentionally trusts the whole `yashashwi-s/tap`. Homebrew tap trust and
macOS Gatekeeper are separate systems: trusting the tap does not notarize an app
or bypass Gatekeeper.

<!-- BEGIN ARRAS PRODUCT METADATA -->
## Casks

| Cask | App | Description |
| --- | --- | --- |
| `arras` | [Arras](https://arras.yashashwi.me/) ([source](https://github.com/yashashwi-s/Arras)) | Native macOS photo widget that preserves each image's original aspect ratio |
| `fadeo` | [Fadeo](https://github.com/yashashwi-s/Fadeo) | Plays, fades, and switches audio based on what you're doing |
<!-- END ARRAS PRODUCT METADATA -->

## Install

```bash
brew install --cask arras
brew install --cask fadeo
```

Both apps are ad-hoc signed rather than notarized. Verify that an app came from
the official distribution, then try opening it normally. If macOS blocks it, use
**System Settings → Privacy & Security → Open Anyway**, or right-click the app in
Applications, choose **Open**, and confirm once.

If those options are unavailable and you trust the official build, removing the
quarantine attribute is an explicit fallback:

```bash
xattr -dr com.apple.quarantine "/Applications/Arras.app"
```

## Notes

- **Arras's published Homebrew cask is Apple Silicon.** The public release artifact
  is arm64, so the cask refuses incompatible installs. Arras supports Intel when
  built from [source](https://github.com/yashashwi-s/Arras).
- **Arras updates itself.** It has a built-in updater that replaces `Arras.app` in place,
  so the cask sets `auto_updates true` and `brew upgrade` leaves it alone unless you pass
  `--greedy`.
- `photo-widget-osx` was renamed to `arras`. `cask_renames.json` migrates existing
  installs on the next `brew upgrade`. If the old `Photo Widget OSX.app` was already
  deleted by hand, that migration cannot uninstall what is not there — run
  `brew install --cask --force arras` once to move past it.

## Removing an app and its data

```bash
brew uninstall --cask --zap arras
```

`--zap` also deletes `~/Library/Application Support/PhotoWidget`, which is where Arras
stores every widget and its photos. Without it, reinstalling restores your layout.
