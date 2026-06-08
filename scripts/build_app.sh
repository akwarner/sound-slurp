#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_PATH="${APP_PATH:-/Applications/Sound Slurp.app}"
RESOURCES="$ROOT/.local/resources"
OPEN_AFTER_BUILD=0
DOWNLOAD=0

for arg in "$@"; do
  case "$arg" in
    --download) DOWNLOAD=1 ;;
    --open) OPEN_AFTER_BUILD=1 ;;
    *)
      echo "Unknown option: $arg" >&2
      echo "Usage: scripts/build_app.sh [--download] [--open]" >&2
      exit 1
      ;;
  esac
done

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This app wrapper currently supports macOS only." >&2
  exit 1
fi

if [[ "$DOWNLOAD" -eq 1 ]]; then
  "$ROOT/scripts/download_deps.sh"
fi

for path in "$ROOT/src/sound_slurp_webapp.py" "$ROOT/packaging/SoundSlurp.applescript" "$ROOT/assets/sound-slurp-logo.svg" "$ROOT/assets/sound-slurp.icns" "$RESOURCES/yt-dlp_macos" "$RESOURCES/ffmpeg"; do
  if [[ ! -e "$path" ]]; then
    echo "Missing required file: $path" >&2
    echo "Run: scripts/build_app.sh --download" >&2
    exit 1
  fi
done

echo "Building $APP_PATH..."
rm -rf "$APP_PATH"
osacompile -o "$APP_PATH" "$ROOT/packaging/SoundSlurp.applescript"

mkdir -p "$APP_PATH/Contents/Resources"
cp "$ROOT/src/sound_slurp_webapp.py" "$APP_PATH/Contents/Resources/sound_slurp_webapp.py"
cp "$ROOT/assets/sound-slurp-logo.svg" "$APP_PATH/Contents/Resources/sound-slurp-logo.svg"
cp "$ROOT/assets/sound-slurp.icns" "$APP_PATH/Contents/Resources/sound-slurp.icns"
cp "$RESOURCES/yt-dlp_macos" "$APP_PATH/Contents/Resources/yt-dlp_macos"
cp "$RESOURCES/ffmpeg" "$APP_PATH/Contents/Resources/ffmpeg"

plutil -replace CFBundleIconFile -string sound-slurp "$APP_PATH/Contents/Info.plist"
/usr/bin/touch "$APP_PATH"

chmod +x "$APP_PATH/Contents/Resources/yt-dlp_macos" "$APP_PATH/Contents/Resources/ffmpeg"
xattr -dr com.apple.quarantine "$APP_PATH" 2>/dev/null || true

echo "Installed: $APP_PATH"
echo "Local UI: http://127.0.0.1:8765/"

if [[ "$OPEN_AFTER_BUILD" -eq 1 ]]; then
  open "$APP_PATH"
fi
