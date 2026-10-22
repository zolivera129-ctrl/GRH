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

### 4. Um encaixe por modelo não serve às duas mesas de trabalho

- **O que foi:** a `mesa_trabalho` atende o Saldanha e o Caio, mas cada um senta numa ponta. O Saldanha fica na frente da metade A5 da mesa dele, e o Caio na frente da metade A7 da dele. Como os encaixes são por modelo, o monitor não consegue ficar na frente dos dois. Ficou no meio da mesa, meio tile fora da linha de cada um.
- **Onde:** `FinancyApp_Assets_v2.md` (v2.2), "Como entregar" (`encaixes`); `FinancyApp_Layout_12x10_v1.json`, `mesa_saldanha` e `mesa_caio`.
- **Sugestão:** deixar o layout escolher o encaixe de cada instância. Por exemplo, a mesa ganha dois encaixes de monitor (`monitor_a5` e `monitor_a6`, um em cada metade), e o campo `objetos` da planta diz qual usar.

### 5. Nome das salas nas plaquinhas

- **O que foi:** a porta tem 30 px de largura. Na fonte de pixel, "TESOURARIA" e "AUDITORIA" não cabem. Cada plaquinha ganhou um ícone gravado no latão: pilha de moedas (Tesouraria), alvo (Metas) e lupa (Auditoria).
- **Onde:** `FinancyApp_Assets_v2.md` (v2.2), "Piso e paredes", porta trancada.
- **Sugestão:** confirmar os ícones, e o nome por extenso fica na etiqueta que o jogo escreve ao passar o mouse.

### 6. Cadeira de costas precisa do encosto em outra camada

- **O que foi:** quando alguém senta olhando para -A ou -B, o encosto fica entre a pessoa e quem olha a tela, então precisa ser desenhado por cima dela. Com a cadeira num desenho só, o jogo não consegue pôr a pessoa entre o assento e o encosto. No corte 1 isso não aparece, porque as cadeiras da reunião ficam vazias, mas aparece no corte 4.
- **Onde:** `FinancyApp_Assets_v2.md` (v2.2), "Móveis e objetos", cadeira; "Lotes seguintes", corte 4.
- **Sugestão:** nas direções de costas, entregar o encosto como camada separada (`cadeira__costas-dir-encosto.png`), ou definir que o jogo desenha a pessoa antes da cadeira nessas direções.

### 7. A1/B8 também é circulação obrigatória

- **O que foi:** a função de validação calcula a circulação obrigatória testando, tile a tile, o que quebra alguma regra se for ocupado. Saíram 11 tiles: os 10 da planta e mais A1/B8. O ponto de uso do malote em A1/B7 está cercado pelo malote (A0/B7), pelo balcão (A2/B7) e pela cadeira da Vivi (A1/B6). O único caminho até ele é A1/B8. Se A1/B8 for decorado, a regra 3 quebra.
- **Onde:** `FinancyApp_Planta_12x10_v1.md`, seções "Grade" (A1/B8 aparece como `·`, livre para decorar) e "Validação" (circulação obrigatória e resultado); `FinancyApp_Layout_12x10_v1.json`, `circulacao_obrigatoria`.
- **Como ficou:** o jogo usa o cálculo, então não deixa decorar A1/B8. Os números do layout padrão passam a ser 11 de circulação obrigatória e 62 livres para decorar, em vez de 10 e 63. O teste da validação aceita a lista da planta mais A1/B8.
- **Sugestão:** pôr A1/B8 na circulação obrigatória da planta e do JSON (marcado `+` na grade) e corrigir o resultado para 11 e 62.

### 8. Campos e âncoras que o documento não define

O documento não diz como resolver os pontos abaixo. Fiz assim, e vale registrar:

- **Peça de parede:** a âncora é a ponta esquerda (na tela) do vão, na altura da base. Na parede esquerda, essa ponta é o fim do último tile; na direita, o começo do primeiro. O manifesto repete a altura em `altura: [base, topo]`, que o build confere contra o `altura_px` do layout.
- **Camadas:** ficam no campo `camadas`, na ordem de desenho, no mesmo recorte e com a mesma âncora da peça. São o céu e a moldura da janela, a silhueta e as plaquinhas da porta trancada, e as fotos do mural de recordações.
- **Objeto de mesa:** a âncora é o centro da base do objeto, no tampo. O jogo cola o objeto em `âncora da mesa + encaixe - âncora do objeto`.
- **Piso:** as três variações ficam em `variacoes`, e a âncora segue a regra dos móveis (vértice de baixo, [32, 32]).
- **Cores da parede:** ficam na chave `parede` do manifesto (altura, rodapé, cores e borda do piso), que não é um modelo da planta.

### 9. Âncora dos humanos e o pé nas passagens (animações)

- **O que foi:** os humanos pisam em y 62 ou 63 da tela de 40×70, e cinco (Guilherme, Nina, Sr. Pra Ontem, Íris e Duda) encostam o cabelo na linha 0. Na caminhada o corpo sobe 1 px nas passagens e cortaria a primeira linha do cabelo; o `comemorando_tablet` do Saldanha também precisa de espaço acima da cabeça. Além disso, de frente o pé de trás fica 1 px acima do da frente, então, no quadro em que o da frente levanta, o ponto mais baixo do quadro sobe 1 px sem a âncora mexer.
- **Onde:** Manual de sprites e animações v1.0, §1 (âncora "(20,66) provisoriamente") e §9.2 (testes 2 e 6); `office.py`, `anchor_of` e `check`, que hoje pegam a âncora do pé de cada quadro e exigem o pé na linha da âncora em todos.
- **Como ficou:** a âncora dos 12 humanos é (20, 66): cada um desce até a sola cair em 66 (3 ou 4 px), em todas as animações, e o manifesto traz a âncora nova (o jogo já lê de lá; a sala ficou idêntica, pixel por pixel). A conferência do build exige o pé na âncora em todo quadro, com uma exceção: na caminhada, o quadro em que o pé da frente está no ar pode terminar 1 px acima.
- **Sugestão:** registrar a âncora (20, 66) dos humanos no "Como entregar" da Assets e no manual, e a exceção do pé no ar nos testes do §9.2.

### 10. Animações da fase 2 já no assets/

- **O que foi:** a pedido do Guilherme, os 12 humanos ganharam `parado_costas`, `sentado_costas`, `andando_frente` e `andando_costas` (4 quadros, 8 FPS, `loop`), nas linhas 2 a 5 da folha. As linhas 0 e 1 continuam o parado e o sentado de frente. No manifesto, cada animação animada traz `quadros`, `fps` e `loop: true`. Isso adianta o andar dos cortes 2 a 4, como a passagem do corte 1 já registrava ("pedido para já"). O jogo ainda não usa nada disso.
- **Onde:** `FinancyApp_Assets_v2.md`, "Animações de todo humano" (a tabela tem só frente-dir e costas-dir; o manual tem as mesmas) e "Lotes seguintes"; manual de sprites e animações v1.0, §3 e §10 (fase 2).
- **Sugestão:** na Assets, marcar as quatro animações como entregues para os 12 e tirar o andar dos lotes dos cortes 2 a 4; registrar o formato do manifesto (`quadros`, `fps`, `loop`).

### 11. Vida à mesa (fase 3): onde ficam as mãos e o que o jogo cola por cima

- **O que foi:** a pedido do Guilherme, os 12 humanos ganharam a fase 3 do manual: `sentado_frente_idle`, `teclando_frente`, `assentindo_para_tela_frente` e `olhando_para_o_lado_frente`, e as sobreposições `piscando_frente` e `falando_frente`. Três pontos não fecham com o manual e com a planta:
  - **Mãos:** o manual sugere as mãos em (28, 44) e (19, 43). Pela planta, quem senta olhando +B à mesa de 24 px tem a borda do tampo passando por (20, 58) no sprite, subindo meio pixel a cada pixel para a direita. As mãos ficaram em torno de (27, 56) e (34, 52), logo depois da borda. As coordenadas do manual só batem com o balcão da recepção (34 px), e a Vivi ficou assim.
  - **Camada do tampo:** a mesa fica mais perto da câmera que a cadeira e o jogo a desenha depois do personagem, então ela cobre as mãos. Cada animação à mesa ganhou uma linha `..._tampo` só com antebraços e mãos. A ordem é: cadeira, personagem, rosto, mesa, camada do tampo e só então os objetos sobre a mesa (o monitor fica mais perto da câmera que as mãos).
  - **Rosto:** piscar e falar são sobreposições na tela do parado de frente, como o manual pede. Cada quadro com rosto visível traz no manifesto o deslocamento `rosto`, para o jogo colar olhos e boca no lugar certo (sentado é [0, 3]; nas passagens da caminhada, [0, -1]). No olhar para o lado as pupilas andam 1 px, e o piscar não combina com esses dois quadros.
- **Onde:** manual de sprites e animações v1.0, §1.1 (camadas), §4 (pose-base, mãos, tabelas 4.1 a 4.6) e §9 (marcadores); `FinancyApp_Assets_v2.md`, "Animações de todo humano"; planta 1.1 (altura das mesas e do balcão).
- **Ajustes pedidos pelo Guilherme depois da primeira versão:**
  - **Teclando:** sem o movimento de cabeça e ombros da tabela 4.2 (parecia que a pessoa dançava). Só os punhos alternam 1 px.
  - **Dentes ao falar:** quem mostra os dentes na boca de repouso (Guilherme, Caio, Vivi e Gabriel) fica com a metade do meio dos dentes na abertura de 1 px e sem dentes na de 2 px.
  - **Teclado:** novo objeto `teclado`, em duas direções (`frente-esq` para quem olha +B nas mesas; `frente-dir` para o balcão). O campo `objetos` da planta não tem teclado, então ele vai pela âncora de quem senta: `no_personagem` traz o deslocamento por móvel. A ordem fica: mesa, teclado, camada do tampo, objetos. No Saldanha, o monitor (encaixe único da mesa de trabalho, ponto 4 da passagem do corte 1) cobre o teclado.
- **Sugestão:** registrar no manual as mãos por móvel (mesa e balcão), a camada do tampo com a ordem de desenho e os dois ajustes de teclar e falar; registrar na Assets os campos `rosto`, `tampo`, `maos`, `mesa`, `camada_de` e `sobreposicao` e o teclado (se entra no `objetos` da planta, com encaixe por metade da mesa, ou se fica preso ao personagem). Quem usa a vida à mesa no jogo continua sendo regra do GDD (o manual pede para não transformar o Gabriel em funcionário).

## Resolvidas

- **Na v2.2:** a escala dos cachorros foi fechada em 34 e 24 px; o Caio está em verde-sálvia; os cachorros parados em pé entraram no corte 2.
- **Na v2.1:** a âncora do sentado é o chão embaixo do quadril; o manifesto tem o campo `pasta`, fixa por tipo; as folhas têm uma animação por linha, com o campo `linha`; a altura dos cachorros foi corrigida; o lote do corte 1 tem 4 poses novas, não 7.
