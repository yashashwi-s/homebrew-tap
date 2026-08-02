# yashashwi-s/tap

Homebrew casks for my macOS apps.

```bash
brew tap yashashwi-s/tap
```

## Casks

| Cask | App | Description |
| --- | --- | --- |
| `arras` | [Arras](https://github.com/yashashwi-s/Arras) | Pins photos to the desktop as borderless widgets |
| `fadeo` | [Fadeo](https://github.com/yashashwi-s/Fadeo) | Plays, fades, and switches audio based on what you're doing |

## Install

```bash
brew install --cask arras
brew install --cask fadeo
```

Both apps are ad-hoc signed rather than notarized, so macOS quarantines them and blocks
the first launch. Homebrew 6 removed the `--no-quarantine` flag that used to skip this,
so clear the flag once after installing:

```bash
xattr -dr com.apple.quarantine "/Applications/Arras.app"
```

Or right-click the app in Applications, choose **Open**, and confirm once. Either way it
is a one-time step.

## Notes

- **Arras requires Apple Silicon.** The release build is thin arm64; the cask declares
  `depends_on arch: :arm64` so Intel Macs get a clear error instead of an app that
  cannot launch.
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
