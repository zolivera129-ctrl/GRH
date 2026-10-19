# FinancyApp — Planta do escritório 12×10

**Versão:** 1.1 · **Data:** 19/10/2026
**Status:** PROPOSTA de layout padrão, já validada por código (circulação, pontos de uso e portas). Resolve a parte "planta 12 × 10 com Vivi e posto técnico" do ROOM-01. Hub, andares e as salas atrás das portas continuam pendentes.
**Arquivos de apoio no projeto:** `FinancyApp_Layout_12x10_v1.json` (o mesmo layout em dados, com o modelo de sprite de cada peça) e `FinancyApp_Planta_12x10_previa.png` (prévia isométrica em blocos). As medidas e o que desenhar estão em `FinancyApp_Assets_v2.md`.

**Mudanças da versão 1:** entrou a porta do Arquivo na parede esquerda, em B0. A cabeceira da reunião fica como estava, com o Guilherme de costas para quem olha a tela.

## Como ler

- **Coordenadas:** cada tile é A/B. A0/B0 é o canto do fundo, onde as duas paredes se encontram. A cresce ao longo da parede direita; B cresce ao longo da parede esquerda. A parede direita fica na linha B0 e a esquerda na coluna A0.
- **Layout padrão:** é a posição inicial. Todos os móveis, inclusive os funcionais, podem ser movidos pelo jogador desde que a validação abaixo continue passando [APROVADO, F03 §5; F04 04.7].
- **Quem olha para onde:** "olha +B" é de frente para a esquerda de quem vê a tela; "olha +A" é de frente para a direita. Os dois são vistas de frente. "-A" e "-B" são vistas de costas.

## Grade

```
         A →  0   1   2   3   4   5   6   7   8   9  10  11
      B  0    o   o   o   o   +   s   P   ·   ·   o   ·   o
         1    r   R   R   r   +   S   S   ·   ·   ·   ·   +
         2    r   R   R   r   +   o   o   ·   ·   ·   g   +
         3    +   r   r   ·   ·   ·   ·   c   ·   G   G   F
         4    +   +   +   +   ·   ·   C   C   ·   o   o   L
         5    ·   ·   V   ·   ·   ·   o   o   ·   ·   X   ·
         6    ·   v   V   o   ·   ·   ·   ·   ·   X   X   ·
         7    M   o   V   ·   ·   ·   ·   ·   ·   o   o   ·
         8    E   ·   ·   ·   ·   ·   ·   ·   ·   ·   ·   ·
         9    ·   ·   ·   ·   ·   ·   ·   ·   ·   ·   ·   ·
```

| Letra | Peça | Letra | Peça |
|---|---|---|---|
| R | Mesa de reunião | r | Cadeira da reunião |
| S | Mesa do Saldanha | s | Cadeira do Saldanha |
| C | Mesa do Caio | c | Cadeira do Caio |
| G | Mesa do fundador | g | Cadeira do fundador |
| V | Balcão da recepção | v | Cadeira da Vivi |
| P | Planta | M | Malote |
| F | Manta da Flora | L | Caminha do Lupin |
| X | Estação flexível (reservada) | E | Entrada (frente da porta) |
| o | Ponto de uso ou frente de porta | + | Circulação obrigatória |
| · | Livre para decorar | | |

## Zonas

**Reunião, no fundo (A0–A3, B0–B4).** Mesa 2×2 com seis cadeiras e o quadro branco na parede direita, logo atrás da mesa. Quem apresenta fica em pé em A1/B0 ou A2/B0, de frente para a mesa. A cabeceira é A1/B3, do lado oposto ao quadro, e o Guilherme senta ali de costas para quem olha a tela. A janela fica na parede esquerda, sobre as cadeiras do lado esquerdo, e a porta do Arquivo fica no canto, em B0.

**Saldanha, no centro da parede direita (A4–A7, B0–B2).** Tudo o que o GDD põe na conta dele fica junto: mesa com monitor e bandeja, cadeira encostada na parede, planta ao lado, e na parede atrás dele o mural de alertas, a tela do FECHADO e o calendário. Quem vai falar com ele para em A5/B2 ou A6/B2.

**Caio, no meio da sala (A6–A7, B3–B5).** Posto próprio, fora da recepção. A sineta e o headset ficam na mesa. Ele senta de costas para a mesa do Saldanha, a dois passos dela, então o "vai até o Saldanha e volta" das consultas é curto. Quem é atendido para em A6/B5 ou A7/B5.

**Fundador, no fundo à direita (A9–A11, B0–B4).** Mesa do Guilherme entre as portas de Metas e Auditoria, com a Flora e o Lupin ao lado. Fica um corredor de dois tiles atrás da cadeira para chegar às duas portas sem passar por cima dele.

**Recepção, junto da porta de entrada (A0–A3, B5–B8).** O balcão da Vivi corre ao longo da parede esquerda, com ela sentada de frente para a sala e o mural de recordações na parede atrás dela. O malote fica entre ela e a porta: o Gabriel entra, deixa o envelope e não precisa contornar o balcão. O visitante para em A3/B6.

**Flora e Lupin (A11, B3–B4).** Manta e caminha juntas, ao lado da mesa do fundador e longe da porta, porque o Lupin desconfia de quem chega. Os dois andam pela sala livremente; essas são só as camas.

**Estação flexível (A9–A10, B5–B7).** Pegada reservada desde já, desenhada pontilhada até ser liberada. Ela já conta como ocupada na validação, então a decoração nunca toma o espaço dela.

**Frente livre (de B5 a B9, quase toda).** São 63 tiles livres para decorar, a maioria na metade da frente. É o espaço da loja e das lembranças.

## Porta do Arquivo

[DEFINIDO nesta versão] Fica na parede esquerda, em B0, escondida no canto da reunião. Existe desde o primeiro dia, fechada, sem plaquinha e sem cadeado, e não leva silhueta, porque o Otto é invisível até a estreia do Arquivo [F01 §12]. No episódio de estreia ela ganha a plaquinha "Arquivo" e abre.

[PROPOSTA] Uma fenda de correspondência na porta. Quando alguém diz que vai "mandar para o Otto", pode ir até ela e passar um papel pela fenda. É uma cena de ambiente, sem efeito em dado nenhum.

## Peças de piso

| Peça | Tiles | Base | Olha para | Observação |
|---|---|---|---|---|
| Mesa de reunião | A1–A2 / B1–B2 | 2×2 | — | |
| Cadeira — cabeceira (Guilherme) | A1/B3 | 1×1 | -B | De frente para o quadro, de costas para a tela |
| Cadeira — Vivi | A2/B3 | 1×1 | -B | |
| Cadeira — Caio | A0/B1 | 1×1 | +A | |
| Cadeira — convidado ou Gabriel | A0/B2 | 1×1 | +A | |
| Cadeira — Saldanha | A3/B1 | 1×1 | -A | Ao lado de onde ele apresenta |
| Cadeira — vaga | A3/B2 | 1×1 | -A | Para o próximo agente |
| Cadeira do Saldanha | A5/B0 | 1×1 | +B | Encostada na parede, sob a tela |
| Mesa do Saldanha | A5–A6 / B1 | 2×1 | — | Monitor e bandeja em cima |
| Planta | A6/B0 | 1×1 | — | Viva ou murcha |
| Cadeira do Caio | A7/B3 | 1×1 | +B | |
| Mesa do Caio | A6–A7 / B4 | 2×1 | — | Monitor, sineta e headset |
| Cadeira do fundador | A10/B2 | 1×1 | +B | |
| Mesa do fundador | A9–A10 / B3 | 2×1 | — | |
| Manta da Flora | A11/B3 | 1×1 | — | Só cachorro entra |
| Caminha do Lupin | A11/B4 | 1×1 | — | Só cachorro entra |
| Balcão da recepção | A2 / B5–B7 | 1×3 | — | Corre ao longo de B |
| Cadeira da Vivi | A1/B6 | 1×1 | +A | |
| Malote | A0/B7 | 1×1 | — | Ao lado da porta |
| Estação flexível — mesa | A9–A10 / B6 | 2×1 | — | Reservada |
| Estação flexível — cadeira | A10/B5 | 1×1 | +B | Reservada |

## Peças de parede

Parede direita (linha B0), de A0 a A11:

| Posição | Peça |
|---|---|
| A1–A2 | Quadro branco |
| A3 | Porta trancada — Tesouraria |
| A4 | Mural de alertas |
| A5–A6 | Tela de parede (selo FECHADO) |
| A7 | Calendário |
| A9 | Porta trancada — Metas |
| A11 | Porta trancada — Auditoria |
| A0, A8, A10 | Livres. A10, atrás da cadeira do fundador, é um bom lugar para expor lembranças. |

Parede esquerda (coluna A0), de B0 a B9:

| Posição | Peça |
|---|---|
| B0 | Porta do Arquivo |
| B1–B2 | Janela (céu por horário) |
| B5–B6 | Mural de recordações da Vivi |
| B8 | Porta de entrada |
| B3, B4, B7, B9 | Livres para decorar |

As plaquinhas das três portas trancadas seguem os desbloqueios da base (Disciplina → Tesouraria, Hábito → Metas, Delivery no teto → Auditoria) [BASE, GDD §10.3]. Tesouraria fica do lado do Saldanha e Metas do lado do fundador.

## Pontos de uso

Onde um personagem fica em pé para usar ou atender cada peça. Precisam estar livres e alcançáveis a partir da entrada.

| Ponto | Tiles |
|---|---|
| Entrada | A0/B8 |
| Quem apresenta no quadro | A1/B0, A2/B0 |
| Visita à mesa do Saldanha | A5/B2, A6/B2 |
| Atendimento do Caio | A6/B5, A7/B5 |
| Visita à mesa do fundador | A9/B4, A10/B4 |
| Visitante no balcão da Vivi | A3/B6 |
| Malote (Gabriel deixa, Saldanha pega) | A0/B8, A1/B7 |
| Visita à estação flexível | A9/B7, A10/B7 |
| Frente do Arquivo | A0/B0 |
| Frente da Tesouraria | A3/B0 |
| Frente de Metas | A9/B0 |
| Frente da Auditoria | A11/B0 |

## Validação

O motor roda estas checagens antes de aceitar qualquer posição nova de móvel [APROVADO, F03 §5; GDD §9.4]. O layout padrão passa em todas.

1. Nenhuma peça fora da sala ou sobreposta a outra.
2. O tile de entrada está livre.
3. Todo ponto de uso está livre e é alcançável a partir da entrada.
4. A frente de toda porta está livre e é alcançável.
5. Toda cadeira, caminha e estação reservada tem pelo menos um vizinho alcançável.
6. A estação reservada conta como ocupada desde já.

Caminhos em quatro direções, sem diagonal, para a validação ficar do lado seguro.

**Circulação obrigatória.** Estes tiles estão livres, mas se forem ocupados alguma regra acima quebra. O jogo não deixa decorar em cima deles:

- A0/B3: o único acesso à cadeira da reunião em A0/B2. A de A0/B1 é acessada pela frente da porta do Arquivo.
- A0–A3 / B4: o corredor que liga a recepção ao fundo da sala e dá acesso à cabeceira.
- A4 / B0–B2: o único caminho para a faixa do fundo, onde ficam quem apresenta no quadro, a porta da Tesouraria, a porta do Arquivo e a cadeira do Saldanha.
- A11/B1–B2: o único acesso à manta da Flora.

Resultado da validação do layout padrão: 90 tiles livres, todos alcançáveis, nenhum bolsão isolado, 10 de circulação obrigatória, 17 entre pontos de uso e frentes de porta, e 63 livres para decorar.

## Decisões

- [x] Cabeceira da reunião em A1/B3, com o Guilherme de costas para a tela
- [x] Porta do Arquivo na parede esquerda, em B0
- [ ] Fenda de correspondência na porta do Arquivo (proposta)

## Em aberto

1. **Estagiário.** A estação flexível é o lugar natural para o estagiário do mês se a modalidade B pedir um posto. Depende do STG-B-01.
2. **Salas atrás das portas.** As portas são os pontos de ligação com as salas anexas da sede [F05 P01]. A planta dessas salas, o hub e os andares ficam para a próxima parte do ROOM-01.
3. **Ligação de voz do Caio** [PENDENTE, PROD-01]. O posto já tem o headset. A sineta continua sendo o clique que abre a consulta, e a caminhada do Guilherme até o ponto de atendimento acontece em paralelo, sem segurar a interface [F01 §2].
