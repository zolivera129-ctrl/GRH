# Motion: apresentação do logo "CEOs e RHs Mais Admirados 2026"

Vídeo: `mais-admirados-2026-logo-motion.mp4` (1920×1080, 30 fps, H.264 + AAC, cerca de 22,5 s)

Trilha: *Moon Party*, de Alex MakeMusic (licença Artlist). O vídeo usa o trecho a partir de 0:05,5, com fade in de 1,6 s e fade out de 2,6 s.

## Roteiro das cenas

| Tempo (s) | Cena |
|---|---|
| 0,0 – 1,1 | Fundo escuro. Um ponto de luz se acende no centro. |
| 1,1 – 2,3 | A aura amarela do KV nasce do centro e se expande rápido (desfoque radial e partículas de luz) até ocupar a tela como no KV. |
| 2,3 – 4,5 | Câmera lenta: a expansão desacelera, as partículas quase param e a poeira de luz flutua. |
| 4,3 – 6,3 | O logo chega sem textos: os raios crescem num giro horário e a silhueta de vidro líquido "enche" de baixo para cima. |
| 6,5 – 12,3 | A luz da silhueta percorre o topo de um lado para o outro (3 passagens), com reflexo no vidro. |
| 12,2 – 13,4 | Giro rápido de 360° como porta giratória (antecipação, motion blur e perspectiva). Ele para no drop da música. |
| 13,4 – 15,1 | Zoom out que abre a visão. Os textos da premiação entram (PREMIAÇÃO / CEOs E RHs / MAIS ADMIRADOS / 2026). |
| 17,3 – 18,5 | Cerca de 2 s depois, o logo gestãorh entra em fade in. |
| 18,5 – 22,5 | O logo completo fica em tela e o vídeo termina em fade out. |

O giro de 360° termina no drop da música (18,9 s da faixa), por isso a revelação do logo completo acontece junto com a entrada do grave.

## Como foi feito

Tudo é gerado por código (Python, NumPy e OpenCV, com encode no ffmpeg), a partir do KV e do print do logo:

- **Aura**: é a própria aura do KV. O selo, os logos, o rodapé e o logo central foram removidos e o fundo atrás deles foi reconstruído, para animar só a luz. No lado esquerdo, a lâmina de luz de bordas duras (degrau escuro e risco branco) foi suavizada (`src/soften_plate.py`).
- **Raios**: foram reconstruídos em vetor a partir do KV (90 raios a cada 4°, espiral de 2 braços, barras e linhas com as cores medidas), por isso continuam nítidos no zoom.
- **Silhueta**: a forma é o vetor oficial (`input/silhoueta_trofeu.ai`). A cor e o brilho do vidro vêm do render do card "Quem você admira?" (`input/card_glass.png`), alinhado ao vetor com erro médio abaixo de 1 px. O shader de vidro líquido adiciona refração, borda de luz, brilho móvel e flare.
- **Textos**: em Montserrat, com o mesmo peso, a mesma posição de cada letra e o degradê prata→branco de "MAIS ADMIRADOS".
- **Logo gestãorh**: extraído do KV e vetorizado por super-resolução.

## Como renderizar de novo

```bash
pip install numpy scipy pillow opencv-python-headless   # e ffmpeg instalado
# dentro de motion-mais-admirados-2026/
mkdir -p build/work && cp /caminho/Alex_MakeMusic_-_Moon_Party.mp3 build/work/music.mp3
./src/run_all.sh
```

- `src/motion.py`: compositor e linha do tempo. A tabela `T` define os tempos de cada cena e `T_DROP` marca o drop da música.
- `src/rays.py`: raios do logo em vetor.
- `src/build_silhouette_v2.py`: silhueta oficial (vetor + cor do card).
- `src/trace_sil.py`, `src/sil_color.py`, `src/build_assets.py` e `src/build_plate.py`: preparação dos outros elementos a partir de `input/kv.png`.
- `src/still.py 13.5 20`: renderiza quadros avulsos para conferência.

A trilha não está versionada no repositório por causa da licença da Artlist.
