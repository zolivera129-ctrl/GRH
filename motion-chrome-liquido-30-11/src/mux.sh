#!/usr/bin/env bash
# Junta o vídeo 4K com o som e gera a versão 1080 para redes.
set -euo pipefail
cd "$(dirname "$0")/.."
ffmpeg -y -loglevel error -i build/video_2x.mp4 -i build/som.wav \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart \
  encerra-amanha-cromo-liquido-9x16-4k.mp4
ffmpeg -y -loglevel error -i build/video_2x.mp4 -i build/som.wav \
  -map 0:v -map 1:a -vf "scale=1080:1920:flags=lanczos" \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -tune film \
  -c:a aac -b:a 192k -shortest -movflags +faststart \
  encerra-amanha-cromo-liquido-9x16-1080.mp4
ls -la encerra-amanha-cromo-liquido-9x16-*.mp4
