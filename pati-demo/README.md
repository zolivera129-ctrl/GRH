# PATI · vídeo de demonstração (Remotion)

Vídeo 16:9, 1920×1080, 30 fps, cerca de 83 s (a duração sai do ritmo de leitura, ver abaixo). Composição: **`PatiDemo`**.
Prévia renderizada: [`pati-demo-preview.mp4`](pati-demo-preview.mp4) · frames de verificação em [`verificacao/`](verificacao/).

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
- `READING`: ritmo de leitura. Os tempos dos três testes são calculados pelo número de palavras de
  cada texto: a mensagem do usuário fica na tela `palavras ÷ userWordsPerSecond` antes da PATI
  responder, e cada bloco da PATI fica `palavras ÷ patiWordsPerSecond` antes do próximo entrar.
  **Para deixar mais lento ou mais rápido, mude só esses dois números**; a duração total, os scrolls,
  a câmera, as marcações e a trilha se ajustam sozinhos. Trocar um texto também recalcula tudo.
- `TIMING`: tempos fixos da apresentação (0–9 s) e a linha do tempo calculada dos testes.
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
node scripts/check-frames.mjs 2 7 12 20 32 48 60 71 78 82
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
| `src/scenes/Scene3Palestra.tsx` | teste 1, slide da palestra (a partir de 9 s) |
| `src/scenes/Scene4Email.tsx` | teste 2, assunto de e-mail |
| `src/scenes/Scene5Arte.tsx` | teste 3, mockup do post do evento |
| `src/scenes/Scene6Closing.tsx` | encerramento, últimos 3 s (o último 1,5 s fica estático) |
| `src/components/` | Navegador, composer, mensagens, cursor, legendas, medição do chat |
| `scripts/make_audio.py` | Sintetiza a trilha (base longa + acorde final) e os sons de interface (`public/audio/`). A base dura ~167 s; o vídeo a corta no encerramento, então não precisa regerar quando a duração muda |

Fonte: Inter (SIL Open Font License), servida de `public/fonts/`. Trilha e sons são sintetizados
pelo próprio script, sem samples de terceiros.
