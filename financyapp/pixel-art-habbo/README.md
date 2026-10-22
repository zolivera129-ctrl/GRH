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

Peças isoladas para o jogo, seguindo `../docs/FinancyApp_Assets_v2.md` (v2.2):
isométrico 2:1, tile de 64x32, luz da esquerda, PNG transparente em 1x,
sem sombra e sem etiqueta. As chaves do `manifest.json` são os ids de
modelo da planta (campo `modelo` de `../docs/FinancyApp_Layout_12x10_v1.json`).

O `build.py` apaga e refaz o `assets/` a cada rodada, com o lote do corte 1
inteiro e os 14 personagens. No fim, confere o manifesto contra o layout:
todo modelo existe, com a mesma base, parede, tiles e altura, e os objetos
de cada mesa têm encaixe.

```
assets/
  piso/          piso_madeira__1.png, __2, __3
  parede/        porta_entrada__fechada, porta_trancada__trancada (+ silhueta e
                 plaquinha-tesouraria, -metas, -auditoria), porta_arquivo__fechada,
                 janela__ceu-tarde + janela__moldura, quadro_branco__limpo,
                 mural_alertas__vazio, tela_parede__apagada, calendario__normal,
                 mural_recordacoes__vazio (+ foto-1 a foto-4)
  moveis/        mesa_trabalho, mesa_fundador, mesa_reuniao, balcao_recepcao,
                 cadeira__frente-dir, __frente-esq, __costas-dir, __costas-esq,
                 malote__vazio, planta__viva, manta_flora, caminha_lupin
  objetos/       monitor__ligado, bandeja__vazia, sineta__parada, headset,
                 teclado__frente-esq e __frente-dir
  personagens/   guilherme, saldanha, caio, vivi, flora, lupin, gabriel,
                 nina, otto, sr_pra_ontem, iris, joana, malu, duda
                 (folha PNG + JSON com tela, âncora e animações)
  manifest.json  por modelo: pasta, base, âncora, estados, direções,
                 variações, camadas e encaixes; a chave parede traz as cores
```

Âncoras:

- Piso e móveis: o vértice de baixo do losango da base. A imagem é justa
  na base, então a âncora fica em [32 × tiles em A, pé da imagem].
- Peças de parede: a ponta esquerda (na tela) do vão, na altura da base.
  Na parede esquerda, é o fim do último tile; na direita, o começo do
  primeiro. As camadas vêm no mesmo recorte, com a mesma âncora.
- Objetos de mesa: o centro da base, no tampo. O objeto vai em
  `âncora da mesa + encaixe - âncora do objeto`. O teclado é a exceção:
  vai pela âncora de quem senta (`no_personagem`, por móvel), entre a mesa
  e a camada do tampo.
- Personagens: o meio dos pés (cachorros: das patas). No sentado, é o chão
  embaixo do quadril, no mesmo ponto da tela do parado. Nos 12 humanos é
  (20, 66) em todos os quadros: cada um desce até a sola cair na linha 66,
  o que deixa folga em cima para o corpo subir na caminhada.

Detalhes:

- Personagens: uma animação por linha da folha, quadros da esquerda para a
  direita. Todos têm `parado_frente` (linha 0) e `sentado_frente`
  (linha 1); nos cachorros, o parado é em pé, nas quatro patas. Os quadros
  de uma folha ficam numa tela comum, alinhados pela âncora.
- Humanos, fase 2 do manual de animações: `parado_costas` (linha 2),
  `sentado_costas` (3), `andando_frente` (4) e `andando_costas` (5), as
  caminhadas com 4 quadros a 8 FPS e `loop`. As direções que faltam são o
  espelho destas, como no jogo.
- Humanos, fase 3 (vida à mesa), linhas 6 a 15: `sentado_frente_idle`,
  `teclando_frente`, `assentindo_para_tela_frente` e
  `olhando_para_o_lado_frente`, com as mãos no tampo; para cada uma, uma
  linha `..._tampo` só com antebraços e mãos, que o jogo cola depois da
  mesa e antes dos objetos sobre ela; e as sobreposições do rosto,
  `piscando_frente` e `falando_frente`, na tela do parado de frente. No
  manifesto, cada quadro com rosto traz `rosto` (onde colar olhos e boca),
  e as animações à mesa trazem `tampo`, `maos` e `mesa` (`mesa` ou
  `balcao`).
- Humanos, fase 4, linhas 16 e 17: `levantando_da_cadeira_frente` e
  `sentando_na_cadeira_frente`, 6 quadros a 8 FPS, uma vez. O primeiro e o
  último quadro são o sentado e o parado de frente.
- Humanos, fase 5 (`especiais.py`), a partir da linha 18, só na folha de
  quem faz: Gabriel `deixando_envelope_no_malote` (e a variante
  `_costas`, a da planta); Saldanha `digitando_sentado` (e `_tampo`),
  `alerta`, `apresentando_quadro` e `comemorando_tablet`; Caio
  `mostrando_tablet`; Vivi `tirando_foto`. Cada uma traz `direcao` e os
  marcadores dela: `envelope` e `solta` (o Gabriel e o Saldanha também
  têm `envelope` nas caminhadas), `dedo`, `tela` e `selo`, `flash` e
  `flash_no_quadro`, `no_lugar_do_teclado`.
- Adereços da fase 5 em `objetos/`: `envelope.png`, `tablet__frente-esq`
  e `__frente-dir` (deitado no tampo, no lugar do teclado) e
  `selo_tablet__verde`, `__amarelo` e `__vermelho`; em `moveis/`,
  `malote__com-envelope.png` (o malote ganhou `abertura`); e a sineta
  tocando, `objetos/sineta__tocando.png`, 2 quadros lado a lado, no campo
  `animacoes` da sineta.
- Móveis não são espelhados: a cadeira tem as quatro direções desenhadas.
- A pose sentada sai do mesmo desenho do parado: o corpo desce 3 px
  (`SIT_DY`, no `chars.py`) até o assento, a 14 px do chão, e as pernas
  dobram para a frente.
- Cachorros na escala da v2.2: Flora sentada com 34 px e Lupin com 24 px
  (`FLORA_K` e `LUPIN_K`, no `office.py`).

Prévias (`previa/`):

- `sala-parada.png` e `@2x`: a sala montada só com o layout e os arquivos
  do `assets/`, como o jogo vai montar. Cada um fica no seu posto, sentado,
  e a estação flexível, reservada, sai pontilhada.
- `escala@2x.png`: os 14 personagens lado a lado no piso, em pé e sentados.

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
  exportação do `assets/`, a conferência contra o layout e as prévias.
- `anim.py`: grava o desenho de um personagem camada por camada e remonta
  com pernas e braços deslocados; é daí que saem as caminhadas, sem
  redesenhar ninguém.
- `costas.py`: os 12 humanos de costas. Braços, pernas, tronco e pescoço
  vêm do desenho de frente; a nuca, o cabelo e os detalhes de trás de cada
  um são desenhados ali.
- `escritorio.py`: a vida à mesa. Os braços dobrados com as mãos na borda
  do tampo (calibrados pela planta), os ciclos da fase 3, as pupilas de
  lado, piscar e falar, e as estações de trabalho montadas com as peças
  do jogo, para conferir.
- `cadeira.py`: levantar e sentar, com as pernas meio dobradas desenhadas
  com as cores e os sapatos de cada um.
- `especiais.py`: as ações especiais da fase 5 (só os braços do gesto e
  o adereço são desenhados; o resto é o desenho original), o envelope, os
  selos e os marcadores de cada uma.
- `animacoes.py`: a lista de animações de cada humano, com quadros por
  segundo e os campos do manifesto, na ordem das linhas da folha.
- `previa_animacoes.py`: a página de prévia (`previa/animacoes/`), com os
  ciclos tocando nas quatro direções, e as faixas ampliadas.
- `teste_animacoes.py`: os testes do manual (§9.2) para os 12 e para as
  ações especiais: `python3 src/teste_animacoes.py`.

Para gerar tudo de novo (o `build.py` também gera o `assets/` e as prévias):

```
pip install pillow
python src/build.py
python src/scene16.py
```
