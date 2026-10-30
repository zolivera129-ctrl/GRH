# PATI · vídeo de demonstração (Remotion)

Vídeo 16:9, 1920×1080, 30 fps, 38 s. Composição: **`PatiDemo`**.
Prévia renderizada: [`pati-demo-preview.mp4`](pati-demo-preview.mp4) · frames de verificação em [`verificacao/`](verificacao/) (2, 7, 13, 21, 30 e 37 s).

> As imagens `public/luis-justo-story.png` e `public/mockup-pausa.png` desta versão são **provisórias**
> (geradas por `scripts/make_placeholders.py`). Troque pelas originais antes de publicar.

## Rodar

```bash
npm install
npm run dev          # Remotion Studio, para ver e ajustar
```

## Trocar as duas imagens

1. Copie as imagens reais para `public/` com os mesmos nomes:
   `luis-justo-story.png` (story do slide) e `mockup-pausa.png` (arte da fogueira).
   Se preferir outros nomes, altere `ASSETS.storyImage` e `ASSETS.artImage` em `src/config.ts`.
2. Se a proporção for diferente, ajuste `ASSETS.storyAspect` / `ASSETS.artAspect` (largura ÷ altura).
3. Confira as áreas desfocadas do story em `STORY_PRIVACY_MASKS` (`src/config.ts`), em % da imagem.
   Por padrão cobrem o topo (foto, @ e barra de progresso) e a base (campo de resposta).
   Se o nome ou a foto estiverem em outro ponto, acrescente um retângulo.

## Alterar textos, cores e tempos

Tudo fica em `src/config.ts`:

- `TEXTS`: todos os textos (prompts completos, respostas, legendas dos testes, encerramento).
  `userMarks` define os trechos destacados no prompt do teste 1; `recoEmphasis`, as palavras em verde.
- `COLORS`: paleta (destaque da PATI em `accent`).
- `TIMING`: segundos em que cada coisa entra. Os scrolls são calculados sozinhos a partir das
  posições medidas das mensagens, então mudar um texto não exige refazer o scroll.
- `CAMERA`: zoom e foco por segundo.
- `LAYOUT`: medidas da interface. Balões longos reduzem a fonte automaticamente (de `userFont`
  até `userFontMin`) para o prompt completo caber em `userBubbleMaxHeightRatio` da área visível.
- `VOLUME`: volume da trilha e dos sons.

## Renderizar de novo

```bash
npx remotion render src/index.ts PatiDemo out/pati-demo.mp4 --crf=18
```

Frames de verificação (saem em `out/frames/`):

```bash
node scripts/check-frames.mjs 2 7 13 21 30 37
```

No ambiente em nuvem do Claude, acrescente o navegador local:
`--browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`
no render, ou `REMOTION_BROWSER=<mesmo caminho>` antes do script de frames.

## Estrutura

| Arquivo | O quê |
| --- | --- |
| `src/PatiDemo.tsx` | Composição principal: câmera, scroll, áudio |
| `src/scenes/Scene1Intro.tsx` | 0–3 s · Conheça a PATI → cabeçalho |
| `src/scenes/Scene2WhatSheDoes.tsx` | 3–9 s · o que ela faz + três critérios |
| `src/scenes/Scene3Palestra.tsx` | 9–17 s · teste 1, story da palestra |
| `src/scenes/Scene4Email.tsx` | 17–25 s · teste 2, assunto de e-mail |
| `src/scenes/Scene5Arte.tsx` | 25–35 s · teste 3, arte da fogueira |
| `src/scenes/Scene6Closing.tsx` | 35–38 s · encerramento (estático a partir de 36,5 s) |
| `src/components/` | Navegador, composer, mensagens, cursor, legendas, medição do chat |
| `scripts/make_audio.py` | Sintetiza a trilha e os sons de interface (`public/audio/`) |
| `scripts/make_placeholders.py` | Gera as imagens provisórias |

Fonte: Inter (SIL Open Font License), servida de `public/fonts/`. Trilha e sons são sintetizados
pelo próprio script, sem samples de terceiros.
