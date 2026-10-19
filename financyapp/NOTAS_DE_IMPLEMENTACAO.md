# Notas de implementação

Pontos em que o código mostrou que os documentos não fecham. Cada um diz o que foi, onde e uma sugestão. Nada aqui muda `docs/`.

## Em aberto

### 1. Escala dos cachorros escolhida

- **O que foi:** na prancha `pixel-art-habbo/previa/escala@2x.png`, o Guilherme escolheu a sugestão da v2: Flora com 34 px e Lupin com 24 px. Os assets já estão nessa escala.
- **Onde:** `FinancyApp_Assets_v2.md` (v2.1), seção "Escala", item "Cachorros", e "Em aberto", item 1.
- **Sugestão:** registrar a escolha e fechar o item 1 de "Em aberto".

### 2. Cópia antiga do layout

- **O que foi:** na segunda rodada de documentos veio um `FinancyApp_Layout_12x10_v1.json` com `"versao": "1"`. Ele não tem o campo `modelo` nem a porta do Arquivo. A cópia em `docs/` continua sendo a 1.1, que bate com a planta 1.1 e com a v2.1 dos assets.
- **Onde:** `FinancyApp_Layout_12x10_v1.json` no projeto de design.
- **Sugestão:** conferir que o projeto guarda só a 1.1, ou renomear o arquivo para `_v1_1`, para não circular a versão antiga.

### 3. Cachorros em pé

- **O que foi:** para fechar a escala, a Flora e o Lupin foram desenhados em pé, nas quatro patas, de lado para a direita. Esse desenho não está em nenhum lote: o corte 1 só tem os cachorros sentados, e o corte 2 fala em "andando". Por isso ele aparece só na prancha e não vai para `assets/`.
- **Onde:** `FinancyApp_Assets_v2.md` (v2.1), "Lotes seguintes", corte 2.
- **Sugestão:** pôr no corte 2 um "parado em pé" dos cachorros, que também serve de base para o andar. O desenho já existe no código (`chars.flora(k, 'em_pe')` e `chars.lupin(k, 'em_pe')`).

## Resolvidas na v2.1

1. A âncora do sentado é o chão embaixo do quadril.
2. O manifesto tem o campo `pasta`, fixa por tipo de peça.
3. As folhas de sprites têm uma animação por linha, com o campo `linha`.
4. A altura atual dos cachorros foi corrigida para a dos assets.
5. O lote do corte 1 tem 4 poses novas, não 7. A sobrecamisa do Caio passou para verde-sálvia.
