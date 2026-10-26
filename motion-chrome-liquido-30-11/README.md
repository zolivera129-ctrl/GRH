# Motion: cromo líquido "30/11 23h → Encerra amanhã a venda de ingressos"

Vídeo: `encerra-amanha-cromo-liquido-9x16-4k.mp4` (2160×3840, 9:16, 24 qps, H.264 + AAC, 15 s)
Versão leve para redes: `encerra-amanha-cromo-liquido-9x16-1080.mp4` (1080×1920)

Um plano único, com câmera frontal travada. O cromo é uma simulação física de fluido viscoso de verdade:
nada é interpolação entre imagens, nada é máscara 2D, crossfade ou transição. A passagem da primeira
mensagem para a segunda acontece dentro da própria simulação.

## Roteiro

| Tempo (s) | O que acontece |
|---|---|
| 0,0 – 1,0 | O veludo carmim aparece do preto, com as manchas derivando devagar. |
| 1,0 – 2,0 | "30/11 · 23h" sobe em relevo de prata polida; uma faixa de luz atravessa as letras. |
| 2,0 – 4,0 | O cromo começa a descer pelo topo em bicas irregulares, com cabeças redondas e pesadas. |
| 4,0 – 7,0 | Os lóbulos descem em velocidades diferentes, encontram as letras e se dividem em volta delas. As letras continuam secas e legíveis. |
| 7,0 – 10,0 | O líquido domina: cortinas laterais chegam ao fundo e escorrem para fora; acima das letras ele represa e abraça o relevo. |
| 10,0 – 12,0 | O fundo fecha e o cromo acumula: o bolsão carmim embaixo das letras encolhe e o nível sobe até passar por cima das letras, que afundam sob o lençol. |
| 12,0 – 13,0 | Cobertura total: o lençol de cromo continua respirando com ondas largas. |
| 13,0 – 13,6 | O cromo se afasta do centro e se acumula numa borda grossa e irregular, abrindo a janela carmim. |
| 13,6 – 15,0 | "ENCERRA AMANHÃ · A VENDA DE INGRESSOS" em relevo de prata dentro da janela; uma faixa de luz passa pelas letras. |

## Como foi feito

Tudo é gerado por código (Python, NumPy, SciPy, Numba e OpenCV, com encode no ffmpeg).

- **Relevo das letras** (`src/bed.py`): a tipografia (Playfair Display, algarismos alinhados) vira um mapa de
  altura com chanfro arredondado e face levemente abaulada. As letras são obstáculo físico na simulação.
- **Simulação** (`src/sim.py`): equação de filme fino (lubrificação) numa grade de 270×480, com gravidade no
  plano, pressão hidrostática, tensão superficial e mobilidade de líquido viscoso (mel / mercúrio). As
  cabeças redondas das gotas, os lóbulos e o represamento atrás das letras saem da física. O líquido só
  sobe numa letra quando a própria superfície já está acima dela, por isso ele contorna o relevo e só o
  engole depois de acumular volume. A tensão superficial e o nivelamento são resolvidos de forma
  semi-implícita (DCT), o que permite um líquido espesso sem passo de tempo minúsculo.
- **Roteiro físico** (`src/roteiro.py`): as condições ao longo do tempo (de onde o cromo entra, quando o
  fundo fecha, a inclinação do painel, a troca do relevo de baixo durante a cobertura total e o campo
  que afasta o líquido do centro para abrir a janela).
- **Render** (`src/render.py`): cada pixel calcula a normal da superfície real (letras + líquido), reflete
  o raio de uma câmera em perspectiva e busca um estúdio HDR (softbox varrendo no alto, filetes laterais,
  réguas de luz, rebatimento carmim de baixo). Nas bordas rasantes o metal reflete o próprio veludo
  vermelho. Fresnel de prata, oclusão nas dobras, sombras de contato, bloom e tone mapping ACES.
- **Som** (`src/audio.py`): sintetizado a partir da simulação: corpo viscoso grave que segue o quanto o
  líquido se move, estiramento médio ressonante, gotas molhadas nas pontas dos lóbulos, ressonâncias de
  prata nos momentos-chave e cintilância leve nas passagens de luz. O estéreo segue o lado da tela onde
  o líquido se mexe. Sem música.

## Como renderizar de novo

```bash
pip install numpy scipy numba pillow opencv-python-headless   # e ffmpeg instalado
cd src
SCALE=1 python3 bed.py && SCALE=2 python3 bed.py   # relevo (grade da simulação e 4K)
python3 sim.py                                      # simulação inteira (~15 min em 4 núcleos)
python3 audio.py                                    # som
SCALE=2 python3 render.py ../build/video_2x.mp4     # render 4K (~30 min em 4 núcleos)
bash mux.sh                                         # junta vídeo e som nos MP4 finais
```

`python3 preview_sim.py 0.5` gera uma folha de contato rápida da simulação, e
`SCALE=1 python3 render.py still 4.0 11.0 14.5` renderiza quadros soltos para conferir.
