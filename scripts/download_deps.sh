#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESOURCES="$ROOT/.local/resources"
mkdir -p "$RESOURCES"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This alpha installer currently supports macOS only." >&2
  exit 1
fi

ARCH="$(uname -m)"
case "$ARCH" in
  arm64)
    FFMPEG_URL="https://github.com/eugeneware/ffmpeg-static/releases/download/b6.0/ffmpeg-darwin-arm64.gz"
    ;;
  x86_64)
    FFMPEG_URL="https://github.com/eugeneware/ffmpeg-static/releases/download/b6.0/ffmpeg-darwin-x64.gz"
    ;;
  *)
    echo "Unsupported Mac architecture: $ARCH" >&2
    exit 1
    ;;
esac

YTDLP_URL="https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos"

echo "Downloading yt-dlp..."
curl -L --fail --progress-bar -o "$RESOURCES/yt-dlp_macos" "$YTDLP_URL"
chmod +x "$RESOURCES/yt-dlp_macos"

echo "Downloading ffmpeg..."
tmp="$(mktemp -t soundcloud-ffmpeg.XXXXXX.gz)"
curl -L --fail --progress-bar -o "$tmp" "$FFMPEG_URL"
gunzip -c "$tmp" > "$RESOURCES/ffmpeg"
rm -f "$tmp"
chmod +x "$RESOURCES/ffmpeg"

xattr -d com.apple.quarantine "$RESOURCES/yt-dlp_macos" 2>/dev/null || true
xattr -d com.apple.quarantine "$RESOURCES/ffmpeg" 2>/dev/null || true

echo "Dependencies ready in $RESOURCES"

