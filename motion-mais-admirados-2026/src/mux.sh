#!/bin/bash
# Junta os chunks renderizados e adiciona a trilha (a partir de 5,54 s da faixa, fade in/out).
# Uso: ./mux.sh saida.mp4
HERE="$(cd "$(dirname "$0")" && pwd)"
BUILD="${MOTION_BUILD:-$HERE/../build}"
R="$BUILD/render"
MUSIC="$BUILD/work/music.mp3"
OUTF=$1
DUR=22.5
OFF=5.54
ffmpeg -y -loglevel error -f concat -safe 0 -i "$R/list.txt" -ss $OFF -t $DUR -i "$MUSIC" \
  -filter_complex "[1:a]afade=t=in:st=0:d=1.6,afade=t=out:st=$(python3 -c "print($DUR-2.6)"):d=2.6[a]" \
  -map 0:v -map "[a]" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -profile:v high -movflags +faststart \
  -c:a aac -b:a 256k -ar 48000 -shortest "$OUTF"
