#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -x "$ROOT/.local/resources/yt-dlp_macos" || ! -x "$ROOT/.local/resources/ffmpeg" ]]; then
  "$ROOT/scripts/download_deps.sh"
fi

export SOUNDCLOUD_DOWNLOADER_RESOURCES="$ROOT/.local/resources"
exec /usr/bin/python3 "$ROOT/src/soundcloud_webapp.py"

