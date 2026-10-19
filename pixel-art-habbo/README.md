# Pixel art: estilo Habbo e Escritório de Finanças

Seis personagens em duas versões: cartões no estilo Habbo Hotel e uma
versão de jogo em grade, com tiles de 16x16 e personagens de 16x32.

| # | Quem | Cenário |
|---|---|---|
| 01 | Guilherme: cabelo cacheado, óculos redondos, camiseta branca com o boneco azul, bolsa transversal preta | deck de barco, janela para o mar de Arraial, boia, palmeira |
| 02 | Gabriel: boné preto, óculos meio-aro, barba, alargador, camiseta Tone Death, jogger e Vans | estúdio roxo, letreiro ON AIR, disco de ouro, toca-discos, caixa de som |
| 03 | Flora: labrador preta com coleira vermelha | manta vermelha, potinho de ração, bolinha de tênis |
| 04 | Lupin: vira-lata pequeno, pelo duro, barba e sobrancelhas caramelo | manta xadrez azul, caminha, ossinho |
| 05 | Saldanha (contador): grisalho, óculos, barba branca, polo marinho, cinto marrom, chino cinza, tablet | escritório: parede verde, janela para a cidade, quadro com gráfico, mesa, planta |
| 06 | Caio (consultor): cachos curtos, sorrisão, camisa verde-oliva aberta, crachá, tablet com check verde | recepção: ripado de madeira, placa de check, balcão com campainha, ficus |

## Estilo Habbo (`out/`)

`out/01-guilherme.png` a `out/06-caio.png`, mais `out/00-todos.png` com
os seis juntos. Cada arte tem 96x120 pixels ampliados 10x (960x1200).

## Escritório de Finanças (`assets/`)

Peças isoladas para o jogo, seguindo o documento "Escritório de Finanças:
peças para desenhar" (v1, 18/10/2026): isométrico 2:1, tile de 64x32,
parede de 100 px, luz da esquerda, PNG transparente em 1x, sem sombra e
sem etiqueta. Lote entregue até agora: **Sala parada**.

```
assets/
  piso/          madeira-1.png, madeira-2.png, madeira-3.png
  parede/        porta-entrada, janela (moldura + 4 céus), quadro-branco,
                 calendario, mural, tela-parede
  moveis/        mesa-redonda, cadeira-reuniao (frente, costas), mesa-contador
                 (+ monitor em camada), bandeja, cadeira-contador (frente,
                 costas), balcao, sineta, malote, planta, manta-flora,
                 caminha-lupin
  personagens/   guilherme, gabriel, contador, consultor, flora, lupin
                 (folha PNG + JSON com quadros, âncora e fps)
  manifest.json  tamanho em tiles, âncora, estados e posição de cada peça
  previa/        a sala montada a partir desses arquivos e a prancha de escala
```

As regras de âncora e de espelhamento estão em `manifest.json`, na chave
`convencoes`. O que ainda falta de cada peça está na chave `falta`.

- Contador = Saldanha, Consultor = Caio.
- Cachorros na escala do escritório: Flora sentada com ~37 px (a cabeça na
  altura do queixo do Guilherme) e Lupin com ~23 px. Os números ficam em
  `FLORA_K` e `LUPIN_K`, no `office.py`.
- O monitor da mesa do Contador fica virado para +A, para quem olha a tela
  ver o gráfico.

## Grade 16x16 (`out/grade16/`)

Saiu do plano do jogo (o escritório segue a medida do Habbo). Fica aqui
só como arte.

- Tiles de 16x16 px; personagens de 16x32 px (um tile de largura, dois
  de altura), vistos de frente.
- Cada sala tem 9x11 tiles (144x176 px) e o personagem fica no tile do
  meio.
- Na tela, use 3x ou 4x, sempre sem suavização (nearest neighbor).

Pastas:

- `personagens/`: cada sprite em 16x32 (1x, para o motor do jogo), `@3x`
  e `@4x`, todos com fundo transparente; `todos-spritesheet` junta os seis
  lado a lado (96x32).
- `cenas/`: cada sala em 1x, `@3x` e `@4x`, e uma `-grade@4x` com as
  linhas da grade desenhadas por cima, para conferir o alinhamento.
- `tilesets/`: os tiles 16x16 diferentes de cada sala, fatiados do fundo
  (sem o personagem e sem a etiqueta).
- `00-todos-grade16@3x.png`: as seis salas juntas.

## Código (`src/`)

Tudo é desenhado pixel a pixel em Python, só com Pillow.

- `px.py`: motorzinho de camadas com contorno automático.
- `chars.py`: personagens do estilo Habbo.
- `scene.py` e `build.py`: quartos isométricos e mobis do estilo Habbo.
- `sprites16.py`: os sprites 16x32, um desenho em texto por personagem.
- `scene16.py`: as salas em tiles 16x16, os tilesets e as exportações.
- `office.py`: o Escritório de Finanças: pintor isométrico, peças,
  manifest e prévia.

Para gerar tudo de novo (o `build.py` já gera o `assets/` também):

```
pip install pillow
python src/build.py
python src/scene16.py
```
