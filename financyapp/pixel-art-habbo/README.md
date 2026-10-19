# Pixel art: estilo Habbo e FinancyApp

Catorze personagens em cartões no estilo Habbo Hotel, as peças do FinancyApp
para o jogo (`assets/`) e, dos seis primeiros, uma versão em grade com
tiles de 16x16 e personagens de 16x32.

| # | Quem | Cenário |
|---|---|---|
| 01 | Guilherme: cabelo cacheado, óculos redondos, camiseta branca com o boneco azul, bolsa transversal preta | deck de barco, janela para o mar de Arraial, boia, palmeira |
| 02 | Gabriel: boné preto, óculos meio-aro, barba, alargador, camiseta Tone Death, jogger e Vans | estúdio roxo, letreiro ON AIR, disco de ouro, toca-discos, caixa de som |
| 03 | Flora: labrador preta com coleira vermelha | manta vermelha, potinho de ração, bolinha de tênis |
| 04 | Lupin: vira-lata pequeno, pelo duro, barba e sobrancelhas caramelo | manta xadrez azul, caminha, ossinho |
| 05 | Saldanha (contador): grisalho, óculos, barba branca, polo marinho, cinto marrom, chino cinza, tablet | escritório: parede verde, janela para a cidade, quadro com gráfico, mesa, planta |
| 06 | Caio (consultor): cachos curtos, barba por fazer, sorrisão, camisa verde-oliva aberta, crachá, tablet com check verde | recepção: ripado de madeira, placa de check, balcão com campainha, ficus |
| 07 | Vivi: cachos volumosos com luzes caramelo, argolas e colar dourados, blusa laranja canelada, pantalona creme, scarpin | agência de viagens: quadro do Pão de Açúcar, prateleira com a torre Eiffel e o globo, balcão de ripas com câmera antiga, mala |
| 08 | Nina: coque bagunçado, argolas, blazer verde-oliva com a manga puxada, regata creme, cinto marrom, calça creme | estúdio de arquitetura: moodboard, estante com livros, mesa com planta impressa, amostras e maquete, ficus |
| 09 | Otto: calvo no alto, lados brancos e fofos, barba branca cheia, óculos redondos de tartaruga, camisa branca, colete de tricô oliva, gravata listrada | arquivo da memória: parede de madeira, gravura antiga, retratos sépia, fichário de gavetinhas, mesa com luminária verde e chá |
| 10 | Sr. Pra Ontem (Departamento das Urgências): cabelo escuro com as têmporas grisalhas e topete espetado, óculos pretos, bigode e cavanhaque escuros, terno grafite, gravata verde, fone vermelho no ouvido | relógio de parede, placa URGENTE, mesa com pilhas de papel etiquetadas, telefone vermelho, despertador e ampulheta |
| 11 | Íris (Analista de Cenários Financeiros): black power, óculos gatinho de tartaruga, blazer verde-escuro | quadro de gráfico, janela de fim de tarde, mesa com notebook, papéis e ampulheta, globo de chão |
| 12 | Joana (Negociadora de Resultados): careca, argolas grandes e piercings dourados, delineado e batom vinho, blazer bege com botões dourados | quadro de alvo, estante de livros, mesa com notebook, caneca e livros, planta |
| 13 | Malu (Experiências, Viagens e Histórias): cabelo longo, liso e preto-azulado, óculos de sol na cabeça, camisa de linho creme, jeans | mapa-múndi com polaroides, janela para o Pão de Açúcar, mesa com notebook, passaporte e câmera, mala com chapéu de palha |
| 14 | Duda (Auditoria e Clareza Financeira): coque alto com dois cachos caindo na testa, blazer verde-oliva com botões dourados | letreiro DUDA, quadro com o relatório (pizza e barras), mesa com notebook, papéis, lupa e ampulheta |

## Estilo Habbo (`out/`)

`out/01-guilherme.png` a `out/14-duda.png`, mais `out/00-todos.png` com
todos juntos. Cada arte tem 96x120 pixels ampliados 10x (960x1200).

## FinancyApp (`assets/`)

Peças isoladas para o jogo, seguindo `../docs/FinancyApp_Assets_v2.md` (v2.1):
isométrico 2:1, tile de 64x32, luz da esquerda, PNG transparente em 1x,
sem sombra e sem etiqueta. As chaves do `manifest.json` são os ids de
modelo da planta (campo `modelo` de `../docs/FinancyApp_Layout_12x10_v1.json`).

O `build.py` apaga e refaz o `assets/` a cada rodada. Por enquanto ele traz
do lote do corte 1 só os personagens, a manta e a caminha; móveis, objetos,
parede e piso entram depois. Os outros oito personagens (Gabriel, Nina,
Otto, Sr. Pra Ontem, Íris, Joana, Malu e Duda) já têm o sentado desenhado,
mas só aparecem na prancha: estão fora do corte 1, e o GDD ainda não aprova
o sprite deles (§4.1 e §4.2). A lista do que é exportado é `CORTE_1`, no
`office.py`.

```
assets/
  moveis/        manta_flora.png, caminha_lupin.png
  personagens/   guilherme, saldanha, caio, vivi, flora, lupin
                 (folha PNG + JSON com tela, âncora e animações)
  manifest.json  por modelo: pasta, base em tiles e âncora (peças);
                 folha, tela, âncora e animações (personagens)
```

- Personagens: uma animação por linha da folha, quadros da esquerda para a
  direita. Os humanos têm `parado_frente` e `sentado_frente`; a Flora e o
  Lupin, `sentado_frente`. A âncora é o meio dos pés (cachorros: das patas);
  no sentado, é o chão embaixo do quadril, no mesmo ponto da tela do parado.
- Móveis: âncora no vértice de baixo do losango da base. A imagem é justa
  na base, então a âncora fica em [32 × tiles em A, pé da imagem].
- O `build.py` confere as âncoras antes de gravar o manifesto.
- A pose sentada sai do mesmo desenho do parado: o corpo desce 3 px
  (`SIT_DY`, no `chars.py`) até o assento, a 14 px do chão, e as pernas
  dobram para a frente.
- Cachorros na escala da v2, escolhida na prancha: Flora sentada com 34 px
  e Lupin com 24 px (`FLORA_K` e `LUPIN_K`, no `office.py`; a da v1 fica em
  `FLORA_K_V1` e `LUPIN_K_V1`).
- Os cachorros também têm um desenho em pé, nas quatro patas
  (`chars.flora(k, 'em_pe')` e `chars.lupin(k, 'em_pe')`). Ele ainda não
  está em nenhum lote, então só aparece na prancha.
- A prancha `previa/escala@2x.png` mostra os 14 lado a lado no piso, em pé
  e sentados, e os cachorros em pé nas escalas da v2 e da v1.

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
- `office.py`: as peças do FinancyApp: pintor isométrico, peças, a
  exportação do `assets/` e a prancha de escala.

Para gerar tudo de novo (o `build.py` também gera o `assets/` e a prancha):

```
pip install pillow
python src/build.py
python src/scene16.py
```
