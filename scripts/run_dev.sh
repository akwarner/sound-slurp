#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -x "$ROOT/.local/resources/yt-dlp_macos" || ! -x "$ROOT/.local/resources/ffmpeg" ]]; then
  "$ROOT/scripts/download_deps.sh"
fi

export SOUND_SLURP_RESOURCES="$ROOT/.local/resources"
export SOUND_SLURP_ASSETS="$ROOT/assets"
exec /usr/bin/python3 "$ROOT/src/sound_slurp_webapp.py"
