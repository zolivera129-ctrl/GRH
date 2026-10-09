#!/bin/bash
# Pipeline completo. Requer: python3 (numpy, opencv-python-headless, scipy, pillow), ffmpeg.
# Coloque a trilha em build/work/music.mp3 antes de rodar (não versionada).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
export MOTION_BUILD="${MOTION_BUILD:-$HERE/../build}"
mkdir -p "$MOTION_BUILD"/{work,assets,fonts,render,stills}
cp "$HERE/../input/kv.png" "$MOTION_BUILD/work/kv.png"
cp "$HERE/../input/card_glass.png" "$MOTION_BUILD/work/card_glass.png"
cp "$HERE/../fonts/"*.ttf "$MOTION_BUILD/fonts/"
cd "$HERE"
python3 trace_sil.py        # contorno da silhueta
python3 sil_color.py        # cor do vidro (sem textos/brilhos)
python3 build_assets.py     # textos, logo gestãorh
python3 build_silhouette_v2.py  # silhueta oficial (vetor .ai + cor do card)
python3 build_plate.py      # placa da aura (KV limpo)
python3 refine_plate.py     # refino do fundo (anomalias, luzes duras, granulação)
python3 render_video.py 4   # quadros -> chunks ffv1
./mux.sh "$HERE/../mais-admirados-2026-logo-motion.mp4"
