#!/usr/bin/env bash
# Renderiza o Reels e masteriza o áudio (+4 dB com limitador em -2 dBFS, ~-15 LUFS, nível comum no Instagram).
# Argumentos extras vão para o `remotion render` (ex.: --browser-executable=/caminho/do/chromium).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p out
npx remotion render src/index.ts CastawayApplyReel out/render.mp4 --codec=h264 --crf=18 "$@"
ffmpeg -v error -y -i out/render.mp4 -c:v copy \
  -af "volume=4dB,alimiter=limit=0.8:attack=3:release=60:level=disabled" \
  -c:a aac -b:a 192k -movflags +faststart castaway-como-aplicar-reels.mp4
echo "ok: castaway-como-aplicar-reels.mp4"
