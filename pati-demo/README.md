# PATI · vídeo de demonstração (Remotion)

Vídeo 16:9, 1920×1080, 30 fps, 45 s. Composição: **`PatiDemo`**.
Prévia renderizada: [`pati-demo-preview.mp4`](pati-demo-preview.mp4) · frames de verificação em [`verificacao/`](verificacao/) (2, 7, 13, 17, 27, 34, 40 e 44 s).

Imagens usadas: `public/luis-justo-story.png` (slide da palestra, recortado só para tirar a moldura
cinza do print) e `public/mockup-evento.png` (mockup do post do evento).

## Rodar

```bash
npm install
npm run dev          # Remotion Studio, para ver e ajustar
```

## Trocar as duas imagens

1. Copie as imagens para `public/` com os mesmos nomes:
   `luis-justo-story.png` (teste 1) e `mockup-evento.png` (teste 3).
   Se preferir outros nomes, altere `ASSETS.storyImage` e `ASSETS.artImage` em `src/config.ts`.
2. Se a proporção for diferente, ajuste `ASSETS.storyAspect` / `ASSETS.artAspect` (largura ÷ altura).
3. Se a imagem do teste 1 for um print de story com nome, foto ou @ de quem postou, cubra essas
   áreas em `STORY_PRIVACY_MASKS` (`src/config.ts`), em % da imagem. Há um exemplo comentado lá.
   O slide atual não tem identificadores, então a lista está vazia.

## Alterar textos, cores e tempos

Tudo fica em `src/config.ts`:

- `TEXTS`: todos os textos (prompts completos, respostas, legendas dos testes, encerramento).
  `userMarks` define os trechos destacados no prompt do teste 1; `recoEmphasis`, as palavras em verde.
- `COLORS`: paleta (destaque da PATI em `accent`).
- `TIMING`: segundos em que cada coisa entra. Para dar mais ou menos tempo de leitura a uma
  resposta, afaste o tempo do bloco seguinte (e o `start` do próximo teste). Os scrolls e a câmera
  acompanham sozinhos. Se mudar a duração total, ajuste `VIDEO.durationInSeconds` e as constantes
  `DURATION`/`CLOSING` em `scripts/make_audio.py`, e rode o script de novo.
- `CAMERA`: zoom e foco, montados a partir de `TIMING`.
- `LAYOUT`: medidas da interface. Balões longos reduzem a fonte automaticamente (de `userFont`
  até `userFontMin`) para o prompt completo caber em `userBubbleMaxHeightRatio` da área visível.
- `VOLUME`: volume da trilha e dos sons.

## Renderizar de novo

```bash
npx remotion render src/index.ts PatiDemo out/pati-demo.mp4 --crf=18
```

Frames de verificação (saem em `out/frames/`):

```bash
node scripts/check-frames.mjs 2 7 13 17 27 34 40 44
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
| `src/scenes/Scene3Palestra.tsx` | 9–19 s · teste 1, slide da palestra |
| `src/scenes/Scene4Email.tsx` | 19–29,5 s · teste 2, assunto de e-mail |
| `src/scenes/Scene5Arte.tsx` | 29,5–42 s · teste 3, mockup da arte |
| `src/scenes/Scene6Closing.tsx` | 42–45 s · encerramento (estático a partir de 43,5 s) |
| `src/components/` | Navegador, composer, mensagens, cursor, legendas, medição do chat |
| `scripts/make_audio.py` | Sintetiza a trilha e os sons de interface (`public/audio/`) |

Fonte: Inter (SIL Open Font License), servida de `public/fonts/`. Trilha e sons são sintetizados
pelo próprio script, sem samples de terceiros.
