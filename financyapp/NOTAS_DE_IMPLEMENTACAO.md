# Notas de implementação

Pontos em que o código mostrou que os documentos não fecham. Cada um diz o que foi, onde e uma sugestão. Nada aqui muda `docs/`.

## Em aberto

### 1. Os 14 personagens no assets/

- **O que foi:** a pedido do Guilherme, o `assets/` traz os 14 personagens prontos para uso, cada um com o parado e o sentado de frente. Os documentos ainda falam em seis:
  - o "Como entregar" da v2.2 lista só Guilherme, Saldanha, Caio, Vivi, Flora e Lupin em `personagens/`;
  - a v2.2 diz que "o Otto não tem sprite até a estreia do Arquivo", e o GDD §4.1 diz que ele "não ganha sprite/presença física" antes disso;
  - o GDD §4.2 diz que o sprite de Nina, Íris, Joana, Malu e Duda exige aprovação.
- **Ids escolhidos para os oito novos:** `gabriel`, `nina`, `otto`, `sr_pra_ontem`, `iris`, `joana`, `malu` e `duda`, em minúsculas e com sublinhado, como os ids de modelo.
- **Onde:** `FinancyApp_Assets_v2.md` (v2.2), "Personagens" e "Como entregar"; `FinancyApp_GDD_Mestre_Consolidado_v2.md`, §4.1 e §4.2.
- **Sugestão:**
  - pôr os 14 e os ids no "Como entregar";
  - trocar a regra do Otto para "não aparece em cena antes da estreia do Arquivo", já que o sprite existe;
  - registrar no §4.2 que os sprites existem por decisão do Guilherme, e que o que depende de aprovação é o personagem entrar em cena.

### 2. Cachorros parados, em pé, já no assets/

- **O que foi:** a v2.2 põe os cachorros parados em pé no corte 2. Como o desenho já existia, eles entraram agora. A folha da Flora e a do Lupin têm `parado_frente` (em pé, linha 0) e `sentado_frente` (linha 1), como os humanos. A tela de cada folha cresceu para caber o em pé, que é mais largo: Flora com 47×41 e Lupin com 38×32, os dois quadros alinhados pela âncora.
- **Onde:** `FinancyApp_Assets_v2.md` (v2.2), "Personagens" (Flora e Lupin) e "Lotes seguintes", corte 2.
- **Sugestão:** tirar o parado em pé da lista do corte 2 e registrar que, nos cachorros, `parado_frente` é o em pé.

### 3. Cópia antiga do layout

- **O que foi:** na segunda rodada de documentos veio um `FinancyApp_Layout_12x10_v1.json` com `"versao": "1"`, sem o campo `modelo` e sem a porta do Arquivo. A cópia em `docs/` continua sendo a 1.1.
- **Onde:** `FinancyApp_Layout_12x10_v1.json` no projeto de design.
- **Sugestão:** conferir que o projeto guarda só a 1.1, ou renomear o arquivo para `_v1_1`.

## Resolvidas

- **Na v2.2:** a escala dos cachorros foi fechada em 34 e 24 px; o Caio está em verde-sálvia; os cachorros parados em pé entraram no corte 2.
- **Na v2.1:** a âncora do sentado é o chão embaixo do quadril; o manifesto tem o campo `pasta`, fixa por tipo; as folhas têm uma animação por linha, com o campo `linha`; a altura dos cachorros foi corrigida; o lote do corte 1 tem 4 poses novas, não 7.
