#!/usr/bin/env python3
"""Synchronize the Arras cask with the latest stable, tagged release metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


REPOSITORY = "yashashwi-s/Arras"
REPOSITORY_URL = f"https://github.com/{REPOSITORY}"
RELEASE_API = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
RAW_METADATA = (
    f"https://raw.githubusercontent.com/{REPOSITORY}/{{tag}}/product-metadata.json"
)
USER_AGENT = "homebrew-tap-arras-sync/1"
ROOT = Path(__file__).resolve().parents[1]
CASK_PATH = ROOT / "Casks" / "arras.rb"
README_PATH = ROOT / "README.md"
VERSION_RE = re.compile(
    r"v(?P<version>(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*))\Z"
)
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")

MACOS_SYMBOLS = {
    "14.0": "sonoma",
    "15.0": "sequoia",
    "26.0": "tahoe",
}

EXPECTED_COMMANDS = [
    "brew tap yashashwi-s/tap",
    "brew trust yashashwi-s/tap",
    "brew install --cask arras",
]


class SyncError(RuntimeError):
    pass


def request(url: str):
    return Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )


def fetch_json(url: str) -> dict[str, Any]:
    try:
        with urlopen(request(url), timeout=30) as response:
            value = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise SyncError(f"could not fetch valid JSON from {url}: {error}") from error
    if not isinstance(value, dict):
        raise SyncError(f"expected a JSON object from {url}")
    return value


def sha256_for_asset(asset: dict[str, Any]) -> str:
    digest = asset.get("digest")
    if isinstance(digest, str) and digest.startswith("sha256:"):
        sha256 = digest.removeprefix("sha256:").lower()
        if SHA256_RE.fullmatch(sha256):
            return sha256

    download_url = asset.get("browser_download_url")
    if not valid_https_url(download_url):
        raise SyncError("Arras.dmg has neither a valid SHA-256 digest nor download URL")

    hasher = hashlib.sha256()
    try:
        with urlopen(request(download_url), timeout=120) as response:
            while chunk := response.read(1024 * 1024):
                hasher.update(chunk)
    except (HTTPError, URLError, TimeoutError) as error:
        raise SyncError(f"could not download Arras.dmg to calculate SHA-256: {error}") from error
    return hasher.hexdigest()


def valid_https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username


def require_string(metadata: dict[str, Any], key: str) -> str:
    value = metadata.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SyncError(f"product metadata field {key!r} must be a non-empty string")
    return value


def validate_metadata(metadata: dict[str, Any]) -> None:
    if metadata.get("schemaVersion") != 1:
        raise SyncError("unsupported product metadata schemaVersion (expected 1)")
    if metadata.get("name") != "Arras":
        raise SyncError("product metadata name must be Arras")
    if metadata.get("repositoryUrl") != REPOSITORY_URL:
        raise SyncError(f"repositoryUrl must be {REPOSITORY_URL}")
    if not valid_https_url(metadata.get("canonicalUrl")):
        raise SyncError("canonicalUrl must be a valid HTTPS URL")
    publisher = metadata.get("publisher")
    if not isinstance(publisher, dict) or not isinstance(publisher.get("name"), str):
        raise SyncError("publisher must contain a name")
    if not valid_https_url(publisher.get("url")):
        raise SyncError("publisher.url must be a valid HTTPS URL")
    require_string(metadata, "category")
    require_string(metadata, "shortDescription")
    require_string(metadata, "repositoryDescription")
    require_string(metadata, "bundleIdentifier")
    historical_names = metadata.get("historicalNames")
    if not isinstance(historical_names, list) or not all(
        isinstance(name, str) and name for name in historical_names
    ):
        raise SyncError("historicalNames must be an array of non-empty strings")

    minimum_macos = require_string(metadata, "minimumMacOS")
    if minimum_macos not in MACOS_SYMBOLS:
        raise SyncError(
            f"minimumMacOS {minimum_macos!r} has no Homebrew symbol mapping; "
            "update MACOS_SYMBOLS explicitly"
        )

    public_release = metadata.get("publicRelease")
    if not isinstance(public_release, dict):
        raise SyncError("publicRelease must be an object")
    if public_release.get("architectures") != ["arm64"]:
        raise SyncError("the Arras cask currently supports exactly the arm64 public artifact")
    if not isinstance(public_release.get("notarized"), bool):
        raise SyncError("publicRelease.notarized must be boolean")
    source_build = metadata.get("sourceBuild")
    if not isinstance(source_build, dict) or not isinstance(
        source_build.get("intelSupported"), bool
    ):
        raise SyncError("sourceBuild.intelSupported must be boolean")
    license_metadata = metadata.get("license")
    if not isinstance(license_metadata, dict) or not isinstance(
        license_metadata.get("spdx"), str
    ):
        raise SyncError("license must contain an SPDX identifier")
    if not valid_https_url(license_metadata.get("url")):
        raise SyncError("license.url must be a valid HTTPS URL")
    if not isinstance(metadata.get("telemetry"), bool):
        raise SyncError("telemetry must be boolean")
    require_string(metadata, "featureContractPath")

    homebrew = metadata.get("homebrew")
    if not isinstance(homebrew, dict):
        raise SyncError("homebrew must be an object")
    expected_homebrew = {
        "tap": "yashashwi-s/tap",
        "tapRepository": "https://github.com/yashashwi-s/homebrew-tap",
        "cask": "arras",
        "trustScope": "tap",
        "commands": EXPECTED_COMMANDS,
    }
    for key, expected in expected_homebrew.items():
        if homebrew.get(key) != expected:
            raise SyncError(f"homebrew.{key} must be {expected!r}")
    if any("brew trust --cask" in command for command in homebrew["commands"]):
        raise SyncError("canonical Homebrew commands must not use cask-level trust")


def replace_section(text: str, begin: str, end: str, body: str, path: Path) -> str:
    pattern = re.compile(
        rf"(?P<indent>^[ \t]*){re.escape(begin)}\n.*?^(?P=indent){re.escape(end)}",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise SyncError(f"missing or duplicated sync markers {begin!r} in {path}")
    if pattern.search(text, match.end()):
        raise SyncError(f"duplicated sync markers {begin!r} in {path}")
    indent = match.group("indent")
    indented_body = "\n".join(indent + line if line else "" for line in body.splitlines())
    replacement = f"{indent}{begin}\n{indented_body}\n{indent}{end}"
    return text[: match.start()] + replacement + text[match.end() :]


def replace_unique(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, flags=re.MULTILINE)
    if count != 1:
        raise SyncError(f"expected exactly one {label} section, found {count}")
    return updated


def render_files(
    metadata: dict[str, Any], version: str, sha256: str, asset_url: str
) -> dict[Path, str]:
    expected_asset_url = f"{REPOSITORY_URL}/releases/download/v{version}/Arras.dmg"
    if asset_url != expected_asset_url:
        raise SyncError(f"unexpected Arras.dmg URL: {asset_url}")

    description = metadata["shortDescription"].removesuffix(".")
    cask_description = re.sub(r"^Native macOS ", "", description, flags=re.IGNORECASE)
    cask_description = cask_description[:1].upper() + cask_description[1:]
    homepage = metadata["canonicalUrl"]
    bundle_identifier = metadata["bundleIdentifier"]
    macos_symbol = MACOS_SYMBOLS[metadata["minimumMacOS"]]

    cask = CASK_PATH.read_text()
    cask = replace_unique(
        cask,
        r'^  version ".*?"\n  sha256 "[0-9a-f]+"\n',
        f'  version "{version}"\n  sha256 "{sha256}"\n',
        "Arras version/checksum",
    )
    cask = replace_unique(
        cask,
        r'^  url ".*?"\n  name ".*?"\n  desc ".*?"\n  homepage ".*?"$',
        "\n".join(
            [
                f'  url "{REPOSITORY_URL}/releases/download/v#{{version}}/Arras.dmg"',
                '  name "Arras"',
                f'  desc "{cask_description}"',
                f'  homepage "{homepage}"',
            ]
        ),
        "Arras identity",
    )
    cask = replace_unique(
        cask,
        r"^  # Published release artifacts are .*?\n  depends_on arch: .*?\n  depends_on macos: .*?$",
        "\n".join(
            [
                "  # Published release artifacts are arm64. Intel remains supported from source.",
                "  depends_on arch: :arm64",
                f"  depends_on macos: :{macos_symbol}",
            ]
        ),
        "Arras platform",
    )
    cask = replace_unique(
        cask,
        r'^  uninstall quit: ".*?"$',
        f'  uninstall quit: "{bundle_identifier}"',
        "Arras bundle identifier",
    )

    readme = README_PATH.read_text()
    readme_row = (
        f"| `arras` | [Arras]({homepage}) ([source]({REPOSITORY_URL})) | "
        f"{description} |"
    )
    section_pattern = re.compile(
        r"(?s)(?<=<!-- BEGIN ARRAS PRODUCT METADATA -->\n).*?(?=<!-- END ARRAS PRODUCT METADATA -->)"
    )
    section_match = section_pattern.search(readme)
    if not section_match:
        raise SyncError("README is missing the Arras product metadata section")
    section = replace_unique(
        section_match.group(),
        r"^\| `arras` \|.*$",
        readme_row,
        "Arras README row",
    )
    readme = replace_section(
        readme,
        "<!-- BEGIN ARRAS PRODUCT METADATA -->",
        "<!-- END ARRAS PRODUCT METADATA -->",
        section.rstrip("\n"),
        README_PATH,
    )
    if "brew trust --cask" in readme:
        raise SyncError("README uses forbidden cask-level trust")
    command_positions = [readme.find(command) for command in EXPECTED_COMMANDS]
    if any(position < 0 for position in command_positions):
        raise SyncError("README is missing a canonical Arras Homebrew command")
    if command_positions != sorted(command_positions):
        raise SyncError("README Arras Homebrew commands are not in canonical order")

    return {CASK_PATH: cask, README_PATH: readme}


def synchronize(check: bool) -> int:
    release = fetch_json(RELEASE_API)
    if release.get("draft") or release.get("prerelease"):
        raise SyncError("GitHub releases/latest did not return a stable release")
    tag = release.get("tag_name")
    if not isinstance(tag, str) or not (match := VERSION_RE.fullmatch(tag)):
        raise SyncError(f"malformed stable release tag: {tag!r}")
    version = match.group("version")

    assets = release.get("assets")
    if not isinstance(assets, list):
        raise SyncError("latest release assets must be an array")
    dmg_assets = [asset for asset in assets if isinstance(asset, dict) and asset.get("name") == "Arras.dmg"]
    if len(dmg_assets) != 1:
        raise SyncError(f"expected exactly one Arras.dmg asset, found {len(dmg_assets)}")
    asset = dmg_assets[0]
    sha256 = sha256_for_asset(asset)
    asset_url = asset.get("browser_download_url")
    if not isinstance(asset_url, str):
        raise SyncError("Arras.dmg is missing browser_download_url")

    metadata_url = RAW_METADATA.format(tag=quote(tag, safe=""))
    metadata = fetch_json(metadata_url)
    validate_metadata(metadata)
    rendered = render_files(metadata, version, sha256, asset_url)

    changed = [path for path, content in rendered.items() if path.read_text() != content]
    if check:
        if changed:
            for path in changed:
                print(f"out of sync: {path.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print(f"Arras Homebrew metadata is synchronized with {tag}.")
        return 0

    for path in changed:
        path.write_text(rendered[path])
        print(f"updated {path.relative_to(ROOT)}")
    if not changed:
        print(f"Arras Homebrew metadata is already synchronized with {tag}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="report drift without modifying files",
    )
    args = parser.parse_args()
    try:
        return synchronize(args.check)
    except (OSError, SyncError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
