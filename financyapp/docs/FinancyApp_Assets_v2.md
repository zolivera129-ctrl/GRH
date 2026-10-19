# FinancyApp — Peças para desenhar

**Versão:** 2.2 · **Data:** 19/10/2026
**Substitui:** a lista de peças de 18/10 (v1).
**Segue:** a planta `FinancyApp_Planta_12x10_v1.md` (versão 1.1) e o GDD v2.

O lote do corte 1 está completo. Os lotes seguintes estão resumidos e ganham detalhe quando o corte chegar. Os ids de modelo deste documento são os mesmos do campo `modelo` em `FinancyApp_Layout_12x10_v1.json`.

## O que mudou na versão 2.2

- A escala dos cachorros foi fechada: Flora sentada com 34 px e Lupin com 24 px.
- A sobrecamisa do Caio já está em verde-sálvia no sprite.
- O corte 2 ganhou os cachorros parados em pé, que servem de base para o andar.

## O que mudou na versão 2.1

Entraram as cinco notas da implementação do corte 1:

- A âncora do sentado passou a ser o chão embaixo do quadril, e não o meio dos pés.
- O manifesto ganhou o campo `pasta`, e cada tipo de peça tem pasta fixa.
- As folhas de sprites têm uma animação por linha, com o campo `linha` no manifesto.
- A altura atual dos cachorros foi corrigida para a dos assets, 37 e 23 px.
- Os parados do Saldanha, do Caio e da Vivi já existiam. O lote do corte 1 tem 4 poses novas, e não 7.

## O que mudou da versão 1

- O Contador e o Consultor viraram Saldanha e Caio, e entrou a Vivi.
- O Caio saiu do balcão e ganhou mesa própria, e a sineta foi junto. O balcão agora é da recepção.
- Entraram a mesa do fundador, o mural de recordações, a porta do Arquivo e mais duas cadeiras de reunião.
- **Móveis não são mais espelhados.** Espelhar inverte o lado da luz. Os personagens continuam espelhados, como no Habbo.
- **O monitor fica de costas para quem olha a tela.** Quem senta à mesa olha para +B, então a tela do monitor fica virada para ele. O estado "gráfico subindo" sai; o trabalho aparece pela animação de digitar.
- Os lotes seguem os cortes do GDD §17.2.

## Regras que valem para todas as peças

- **Projeção:** isométrico 2:1. A cada 2 px na horizontal, a linha sobe ou desce 1 px.
- **Tile do piso:** losango de 64×32 px. Uma peça de a×b tiles tem base de (a+b)×32 px de largura e (a+b)×16 px de altura.
- **Parede:** cada tile ocupa 32 px de largura. Altura de uns 100 px, para caber uma porta de uns 72 px.
- **Luz:** vem da esquerda, do lado da janela. A face voltada para a esquerda é mais clara e a voltada para a direita é mais escura.
- **Contorno:** na versão escura da própria cor, como o px.py já faz.
- **Arquivo:** PNG transparente em 1×, sem cenário, sem sombra no chão e sem etiqueta de nome. O jogo amplia sem suavizar, desenha a sombra e escreve a etiqueta.
- **Âncora:**
  - personagens: em pé, o meio dos pés; sentado, o chão embaixo do quadril (ver "Escala");
  - móveis: o vértice de baixo do losango da base. Numa imagem justa, ele fica em x = 32 × (tiles ao longo de A) e y = pé da imagem;
  - peças de parede: a posição em tiles na parede e a altura do chão até a base da peça.
- **Orientação dos móveis:** desenhe cada móvel na orientação que a planta usa. A outra orientação só entra quando a decoração permitir girar (corte 6), e aí é um desenho novo.

### Direções

| Na planta | Nome do arquivo | Como sai |
|---|---|---|
| +A | frente-dir | Desenhada (as artes atuais já estão assim) |
| -B | costas-dir | Desenhada |
| +B | frente-esq | Espelho de frente-dir |
| -A | costas-esq | Espelho de costas-dir |

Isso vale para os personagens. A cadeira é a exceção entre os móveis: a planta usa as quatro direções, então as quatro são desenhadas.

**Cuidado ao espelhar personagens:** o que fica de um lado só aparece invertido. É o caso da bolsa transversal do Guilherme, da estampa da camiseta do Gabriel, do smartwatch do Saldanha e de qualquer detalhe assimétrico na roupa da Vivi. Ou você aceita isso, como o Habbo aceita, ou desenha as quatro direções desses personagens.

## Escala

- **Humanos:** tela de 40×70 px, com uns 63 px de altura em pé, como o Guilherme e o Gabriel já estão.
- **Sentado:** mesma tela e mesmo ponto de âncora do parado, [20, 63]. No sentado, esse ponto é o chão embaixo do quadril, e os pés ficam à frente dele. O jogo põe a âncora no centro do tile da cadeira, e o quadril fica uns 14 px acima, na altura do assento.
- **Cachorros:** Flora sentada com 34 px e Lupin com 24 px, escolhidos na prancha `pixel-art-habbo/previa/escala@2x.png`, ao lado dos humanos. Os assets já estão nessa escala. As artes de vitrine continuam com 45 e 32 px.

### Alturas de referência

São as alturas usadas na prévia da planta, como ponto de partida para o desenho.

| Peça | Altura (px reais) |
|---|---|
| Portas | 0–72 |
| Janela | 32–84 |
| Quadro branco | 38–82 |
| Mural de alertas | 40–80 |
| Mural de recordações | 40–82 |
| Tela de parede | 48–88, acima da cabeça do Saldanha sentado |
| Calendário | 52–80 |
| Mesas | 24 |
| Mesa de reunião | 22 |
| Balcão da recepção | 34 |
| Cadeira | assento 14, encosto até 34 |
| Malote | 30 |
| Planta | 40 |

## Modelos

Cada modelo é desenhado uma vez e o jogo reaproveita onde a planta pedir.

| Modelo | O que é | Onde aparece |
|---|---|---|
| `piso_madeira` | Tile do piso | Sala inteira |
| `porta_entrada` | Porta de entrada | Parede esquerda, B8 |
| `porta_trancada` | Porta com cadeado, silhueta e plaquinha | Parede direita, A3, A9 e A11 |
| `porta_arquivo` | Porta lisa, sem plaquinha | Parede esquerda, B0 |
| `janela` | Moldura e céu | Parede esquerda, B1–B2 |
| `quadro_branco` | Quadro da reunião | Parede direita, A1–A2 |
| `mural_alertas` | Mural de cortiça | Parede direita, A4 |
| `tela_parede` | Tela do FECHADO | Parede direita, A5–A6 |
| `calendario` | Calendário | Parede direita, A7 |
| `mural_recordacoes` | Mural de fotos da Vivi | Parede esquerda, B5–B6 |
| `mesa_trabalho` | Mesa 2×1 | Saldanha, Caio e, depois, a estação flexível |
| `mesa_fundador` | Mesa 2×1 do Guilherme | Fundador |
| `monitor`, `bandeja`, `sineta`, `headset` | Objetos sobre a mesa | Saldanha: monitor e bandeja. Caio: monitor, sineta e headset. Fundador: monitor |
| `cadeira` | Cadeira | As 6 da reunião e as dos postos |
| `mesa_reuniao` | Mesa redonda 2×2 | Reunião |
| `balcao_recepcao` | Balcão 1×3 | Recepção |
| `malote` | Caixa de correio | Ao lado da porta de entrada |
| `planta` | Vaso com planta | Ao lado do Saldanha |
| `manta_flora`, `caminha_lupin` | Camas dos cachorros | Ao lado do fundador |

## Lote do corte 1: a sala parada

O corte 1 é o diorama com todo mundo no lugar, ainda sem dados. Cada personagem aparece no seu posto, sentado, e nada reage ainda.

### Piso e paredes

| Peça | Modelo | O que entregar |
|---|---|---|
| Piso | `piso_madeira` | Losango de 64×32 em madeira clara, mais duas variações para quebrar a repetição |
| Paredes e rodapé | (código) | As cores da parede esquerda (mais clara), da direita (mais escura) e do rodapé. O jogo desenha as paredes |
| Porta de entrada | `porta_entrada` | Fechada |
| Portas trancadas | `porta_trancada` | A folha trancada com o cadeado. Por cima, em camadas separadas, a silhueta genérica e as três plaquinhas: Tesouraria, Metas e Auditoria |
| Porta do Arquivo | `porta_arquivo` | Fechada, sem cadeado, sem silhueta e sem plaquinha. Se a fenda de correspondência for aprovada, ela já vem desenhada |
| Janela | `janela` | Moldura e céu em camadas separadas, com o céu da tarde |
| Quadro branco | `quadro_branco` | Limpo |
| Mural de alertas | `mural_alertas` | Vazio |
| Tela de parede | `tela_parede` | Apagada |
| Calendário | `calendario` | Normal |
| Mural de recordações | `mural_recordacoes` | O mural vazio e três ou quatro fotos soltas, que o jogo cola por cima. Por enquanto as fotos são genéricas; o que vai dentro delas fica para o Diário |

A silhueta da porta trancada é o sprite do próprio agente pintado de uma cor só, então ela só fica pronta quando o agente existir. Até lá, a genérica serve.

### Móveis e objetos

| Peça | Modelo | Base | O que entregar |
|---|---|---|---|
| Mesa de trabalho | `mesa_trabalho` | 2×1 ao longo de A | 1 desenho |
| Mesa do fundador | `mesa_fundador` | 2×1 ao longo de A | 1 desenho. Precisa se diferenciar da de trabalho: madeira mais escura ou outro tampo |
| Monitor | `monitor` | Sobre a mesa | Ligado, visto de costas, com uma borda de luz |
| Bandeja | `bandeja` | Sobre a mesa | Vazia |
| Sineta | `sineta` | Sobre a mesa | Parada |
| Headset | `headset` | Sobre a mesa | Pousado |
| Cadeira | `cadeira` | 1×1 | As quatro direções |
| Mesa de reunião | `mesa_reuniao` | 2×2 | Redonda, 1 desenho |
| Balcão da recepção | `balcao_recepcao` | 1×3 ao longo de B | 1 desenho, já nessa orientação |
| Malote | `malote` | 1×1 | Vazio |
| Planta | `planta` | 1×1 | Viva |
| Manta e caminha | `manta_flora`, `caminha_lupin` | 1×1 | Já existem nas artes da Flora e do Lupin. Basta recortar como peça solta |

Cada mesa marca no manifesto onde os objetos encaixam (ver "Como entregar").

### Personagens

| Personagem | O que entregar | Observação |
|---|---|---|
| Guilherme | Sentado de frente | O parado de frente já existe. Na mesa ele olha +B, então usa o sentado espelhado |
| Saldanha | Sentado de frente | O parado de frente já existe (era o Contador). Uns 50 anos, cabelo grisalho curto, barba aparada, óculos de armação fina, polo de tricô azul-marinho, chino cinza, smartwatch e tablet [F01 §7]. Na mesa olha +B, espelhado |
| Caio | Sentado de frente | O parado de frente já existe (era o Consultor). Uns 30 anos, cabelo escuro cacheado, sobrecamisa verde-sálvia aberta, camiseta branca, calça azul-marinho, tênis branco e crachá [F01 §8]. Na mesa olha +B, espelhado |
| Vivi | Sentado de frente | O parado de frente já existe. Mulher negra, cabelos cacheados, roupas coloridas e salto alto [F01 §9A]. Na recepção olha +A, então usa o sentado sem espelhar |
| Flora e Lupin | Nada novo | Os sentados de frente já existem, na escala de 34 e 24 px. Na cena padrão eles ficam nas camas |

O Gabriel fica fora do corte 1, porque só entra no escritório com um gatilho real da planilha. O Otto não tem sprite até a estreia do Arquivo.

### Conta do lote

- 11 peças de piso e parede, contando as camadas da porta trancada como uma peça só;
- 13 móveis e objetos, dos quais 2 (a manta e a caminha) são recortes do que já existe;
- 4 poses novas de personagem: os sentados do Guilherme, do Saldanha, do Caio e da Vivi. Os parados já existiam.

## Animações de todo humano

Vale para os lotes seguintes. No corte 1 só entram o parado e o sentado de frente.

| Animação | Direções desenhadas | Quadros |
|---|---|---|
| Parado | 2, espelhadas para 4 | 1, ou 2 se quiser que pisque |
| Andando | 2, espelhadas para 4 | 4 |
| Sentado | 2, espelhadas para 4 | 1. Para quem senta: Guilherme, Saldanha, Caio e Vivi, e o Gabriel na reunião |

## Lotes seguintes

| Corte | O que entra |
|---|---|
| 2 — Livro do Saldanha, sinais e malote | Bandeja em mais três estados: pilha baixa (1 ou 2 contas), média (3 a 5) e alta (6 ou mais). Calendário com dia vermelho. Um post-it solto para o mural (o jogo põe de 0 a 3). Planta murcha. Malote com envelope e com bandeirinha vermelha, e o envelope solto. Porta de entrada aberta. Os outros três céus: manhã, fim de tarde e noite. Gabriel parado, andando e deixando o envelope (braço estendido, 2 quadros). Saldanha andando, digitando (sentado, 2 quadros) e em alerta (mão na testa, 2 quadros). Vivi e Guilherme andando. Flora e Lupin parados em pé, de lado, que também servem de base para o andar (o desenho já existe em `chars.flora(k, 'em_pe')` e `chars.lupin(k, 'em_pe')`). Flora e Lupin andando, dormindo na cama (2 quadros) e inquietos (2 quadros). Nos quadros de andar do Gabriel e do Saldanha, a posição da mão marcada no JSON, para o jogo colar o envelope |
| 3 — Consulta ao Caio | Sineta tocando (2 quadros). Caio andando e mostrando o tablet (1 quadro), mais os três selos que o jogo cola na tela do tablet: verde, amarelo e vermelho. Caio com o headset na cabeça, se a ligação de voz entrar (PROD-01) |
| 4 — Reunião do dia 6 | Todos sentados de costas. Saldanha em pé apresentando no quadro e comemorando com o tablet erguido (2 quadros cada). Quadro com o report (rabiscos e um gráfico). Tela com o selo FECHADO. Vivi tirando foto (2 quadros), porque a primeira reunião termina com a foto oficial dela [F01 §16A] |
| 5 — Carteira e recompensas | Nada no cenário. É interface |
| 6 — Loja e decoração | Depende do catálogo (SHOP-02). Cada móvel que puder girar precisa da outra orientação desenhada |
| 7 — XP, marcos, expansão e Diário | Portas trancadas abertas e as salas atrás delas. Fotos de verdade no mural de recordações |
| 8 — Eventos e educação | Sr. Pra Ontem, A Neblina, decoração de datas e aniversários. O Otto e a porta do Arquivo aberta, com plaquinha, no episódio de estreia |
| 9 — Estagiários | Depende do STG-B-01 |

## Como entregar

O repositório já gera tudo em código. O build.py tem uma saída `assets/` com as peças isoladas e um manifesto, ao lado das artes de vitrine que ele já gera.

- **Nome do arquivo:** `modelo.png` quando a peça tem um estado só, `modelo__estado.png` ou `modelo__direcao.png` quando tem vários.
- **Pasta:** fixa por tipo de peça. `piso/` para o piso, `parede/` para tudo que fica na parede, `moveis/` para o que ocupa tile, `objetos/` para o que vai sobre uma mesa e `personagens/` para humanos e cachorros. O manifesto repete a pasta de cada peça no campo `pasta`.
- **Folha de sprites:** cada animação ocupa uma linha da folha, com os quadros da esquerda para a direita. O manifesto diz a linha de cada animação no campo `linha`.

```
assets/
  piso/          piso_madeira__1.png, piso_madeira__2.png, piso_madeira__3.png
  parede/        porta_entrada__fechada.png
                 porta_trancada__trancada.png, porta_trancada__silhueta.png
                 porta_trancada__plaquinha-tesouraria.png …
                 porta_arquivo__fechada.png
                 janela__moldura.png, janela__ceu-tarde.png
                 quadro_branco__limpo.png, mural_alertas__vazio.png, tela_parede__apagada.png
                 calendario__normal.png, mural_recordacoes__vazio.png, mural_recordacoes__foto-1.png …
  moveis/        mesa_trabalho.png, mesa_fundador.png, mesa_reuniao.png, balcao_recepcao.png
                 cadeira__frente-dir.png, cadeira__frente-esq.png, cadeira__costas-dir.png, cadeira__costas-esq.png
                 malote__vazio.png, planta__viva.png, manta_flora.png, caminha_lupin.png
  objetos/       monitor__ligado.png, bandeja__vazia.png, sineta__parada.png, headset.png
  personagens/   guilherme.png + guilherme.json, saldanha.png + saldanha.json, caio.png + caio.json,
                 vivi.png + vivi.json, flora.png + flora.json, lupin.png + lupin.json
  manifest.json
```

Cada personagem vem numa folha de sprites (um PNG com todos os quadros) e num JSON com os quadros, a âncora e a velocidade. O manifesto diz ao jogo o tamanho de cada peça em tiles, onde fica a âncora, quais estados ou direções existem e, nas mesas, onde os objetos encaixam. Os números abaixo são de exemplo:

```json
{
  "cadeira": {
    "pasta": "moveis",
    "base": [1, 1],
    "ancora": [32, 66],
    "assento_px": 14,
    "direcoes": ["frente-dir", "frente-esq", "costas-dir", "costas-esq"]
  },
  "mesa_trabalho": {
    "pasta": "moveis",
    "base": [2, 1],
    "ancora": [64, 72],
    "encaixes": {
      "monitor": [-30, -40],
      "bandeja": [8, -34],
      "sineta": [-20, -30],
      "headset": [10, -30]
    }
  },
  "malote": {
    "pasta": "moveis",
    "base": [1, 1],
    "ancora": [32, 62],
    "estados": ["vazio"]
  },
  "saldanha": {
    "pasta": "personagens",
    "folha": "personagens/saldanha.png",
    "tela": [40, 70],
    "ancora": [20, 63],
    "animacoes": {
      "parado_frente": { "linha": 0, "quadros": 1, "fps": 0 },
      "sentado_frente": { "linha": 1, "quadros": 1, "fps": 0 }
    }
  }
}
```

Os encaixes são medidos a partir da âncora da mesa. O JSON da planta já diz quais objetos vão em cada mesa, no campo `objetos`.

## Em aberto

1. **Espelhamento dos personagens.** Aceitar os detalhes invertidos ou desenhar quatro direções para quem tem detalhe de um lado só.
2. **Fenda de correspondência na porta do Arquivo** [PROPOSTA]. Se entrar, já vai no desenho do corte 1.
3. **Headset na cabeça do Caio.** Depende da ligação de voz (PROD-01).
4. **Girar móveis na decoração.** Cada orientação nova é um desenho a mais, então a lista de móveis giráveis sai junto com o catálogo da loja.
