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
  - **Braços à mesa:** redesenhados no estilo do braço que segura o tablet no desenho original (braço de cima reto, antebraço em faixa de 4 px, mão em bloco), com a pele tirada do rosto: antes, em quem tem braço de 4 px, a cor mais frequente do braço solto era o contorno, e o antebraço saía mais escuro que a pele.
  - **Teclado:** novo objeto `teclado`, em duas direções (`frente-esq` para quem olha +B nas mesas; `frente-dir` para o balcão). O campo `objetos` da planta não tem teclado, então ele vai pela âncora de quem senta: `no_personagem` traz o deslocamento por móvel. A ordem fica: mesa, teclado, camada do tampo, objetos. No Saldanha, o monitor (encaixe único da mesa de trabalho, ponto 4 da passagem do corte 1) cobre o teclado.
- **Sugestão:** registrar no manual as mãos por móvel (mesa e balcão), a camada do tampo com a ordem de desenho e os dois ajustes de teclar e falar; registrar na Assets os campos `rosto`, `tampo`, `maos`, `mesa`, `camada_de` e `sobreposicao` e o teclado (se entra no `objetos` da planta, com encaixe por metade da mesa, ou se fica preso ao personagem). Quem usa a vida à mesa no jogo continua sendo regra do GDD (o manual pede para não transformar o Gabriel em funcionário).

### 12. Levantar e sentar (fase 4) na escala do nosso sentado

- **O que foi:** a pedido do Guilherme, os 12 humanos ganharam `levantando_da_cadeira_frente` e `sentando_na_cadeira_frente`, com 6 quadros a 8 FPS, uma vez. Dois pontos não fecham com o manual:
  - **Altura:** o manual descreve o quadril e a cabeça subindo 9 px. No nosso desenho, o sentado fica só 3 px abaixo do em pé (`SIT_DY`, no estilo do Habbo). Os 3 px se distribuem pelos quadros do meio; o tronco inclina 1 px e a cabeça 2 px para a frente, e as pernas passam por duas poses meio dobradas, desenhadas com as cores da calça e os sapatos de cada um. O primeiro e o último quadro são exatamente o sentado e o parado de frente, e a âncora não mexe.
  - **À mesa:** o sentar termina no sentado de braços soltos, como o manual pede. À mesa, o jogo emenda o `sentado_frente_idle`, que já começa com as mãos no tampo (decisão do Guilherme).
  - **Sair da cadeira:** em pé no mesmo ponto do assento, o personagem parecia flutuar dentro da cadeira (apontado pelo Guilherme). Ao levantar, o corpo vai para a frente por cima dos pés e termina meio tile à frente do centro da cadeira, pisando no chão; ao sentar, o caminho de volta. O manifesto traz `desloca`, quanto o personagem anda em cada quadro, na tela, a partir do centro do tile da cadeira, para quem olha +A (espelhado, o x troca de sinal): de (0, 0) a (16, 8). A planta não diz por onde se sai de cada cadeira (a regra 5 só pede um vizinho livre), e nas estações a frente é a mesa: ali ele fica em pé entre a cadeira e a mesa, e o jogo o leva andando até um vizinho livre.
- **Onde:** manual de sprites e animações v1.0, §4.7, §4.8 e §9.2 (teste 8).
- **Sugestão:** registrar no manual a escala de 3 px entre sentado e em pé, a emenda com a vida à mesa e o `desloca`; decidir na planta por onde se sai de cada cadeira.

### 13. Ações especiais (fase 5): lado do gesto, Gabriel de costas, tela do Caio e adereços

- **O que foi:** a pedido do Guilherme, entraram as ações da §5 do manual, só na folha de quem faz: Gabriel `deixando_envelope_no_malote`; Saldanha `digitando_sentado` (com a linha `_tampo`), `alerta`, `apresentando_quadro` e `comemorando_tablet`; Caio `mostrando_tablet`; Vivi `tirando_foto`; e a sineta `tocando` (§7). Adereços novos, todos peças à parte que o jogo cola: `envelope`, `malote__com-envelope`, `tablet` (deitado no tampo) e `selo_tablet` (verde, amarelo e vermelho). Pontos que não fecham com o manual ou com a planta:
  - **Lado do gesto:** o manual põe as mãos do gesto à direita do quadro (x de 32 a 38), para onde o personagem olha, e chama esse braço de "da frente". No nosso desenho de frente, o braço desse lado é o de trás; o da frente fica à esquerda, perto da câmera, e estendê-lo até lá cruzaria o peito. Valem os pontos do manual: quem entrega, aponta e leva a mão à testa é o braço da direita da tela.
  - **Gabriel de costas no malote:** a abertura do malote olha para +A e os pontos de uso da planta (`p_malote`, tiles (0, 8) e (1, 7)) ficam em +B e +A dele, então quem deixa o envelope fica de costas para a câmera. O manual só pede a entrega de frente. Fiz as duas: `deixando_envelope_no_malote` (frente, a do manual) e `deixando_envelope_no_malote_costas`, pelo mesmo critério que o manual usa para levantar e sentar de costas ("se o enquadramento real exigir"). O malote ganhou `abertura` no manifesto, o ponto da fenda na imagem; a mão do Q2 de cada entrega está no campo `envelope`, e o jogo aproxima o Gabriel (na prévia, 0,4 tile a partir do centro do tile, em direção ao malote).
  - **Tela do Caio:** o manual estima a tela útil em (26, 28)–(36, 42), à direita, mas pede para conferir a imagem original, em que o tablet fica erguido ao lado do rosto, no braço da frente. Usei a pose original com a tela em branco: área útil (1, 18)–(9, 27) e centro do selo (5, 22), nos campos `tela` e `selo`. O selo é um adereço de 7 × 7, com um sinal além da cor (check, exclamação e x).
  - **Saldanha digitando:** "braços apoiados, tablet firme" virou a pose da mesa (fase 3) com o tablet deitado no tampo, no lugar do teclado (`no_lugar_do_teclado: "tablet"`). Na mesa dele, o tablet fica atrás do monitor, como o teclado (ponto 4 da passagem do corte 1).
  - **Envelope andando:** a lista do corte 2 nos Assets pede a mão marcada nos quadros de andar do Gabriel e do Saldanha; o manual dá pontos de partida só para o Gabriel. Os dois ganharam `envelope` nas duas caminhadas, lido do desenho (a mão da direita da tela; de costas, é o braço da frente). Os pontos do manual (y em torno de 43) não batem com a mão do nosso desenho (y em torno de 50), que o manual manda seguir.
  - **Malote com envelope:** desenhei só o envelope saindo da abertura. A bandeirinha levantada, que a lista do corte 2 também cita, ficou para quando o corte chegar.
  - **Rosto:** `rosto` só vai nas ações em que o rosto fica livre (entrega de frente, digitando, apresentando, mostrando o tablet e a foto). Alerta e comemorando têm a expressão desenhada no próprio quadro (sobrancelha, boca em "o", sorriso aberto).
- **Corrigido de passagem (fase 3):** relógios e pulseiras desenhados dentro da camada do braço não eram lidos, e o braço à mesa saía sem eles: o smartwatch do Saldanha, a pulseira azul do Guilherme e os relógios e pulseiras de Nina, Otto, Sr. Pra Ontem, Joana e Malu. Agora aparecem no antebraço, inclusive na camada do tampo. Na Íris, na Duda e na Vivi, a manga comprida cobre o pulso de trás e a pulseira não aparece à mesa.
- **Onde:** manual de sprites e animações v1.0, §5, §7, §8.2 e §9 (marcadores e testes 9 a 11); `FinancyApp_Assets_v2.md`, "Lotes seguintes" (cortes 2, 3 e 4); planta 1.1 (`p_malote`, `p_quadro`, malote em (0, 7)).
- **Sugestão:** no manual, trocar "braço da frente" por "braço do lado para onde ele olha" nas ações, registrar a entrega de costas e a tela do Caio pela pose original; na Assets, registrar os adereços (`envelope`, `tablet`, `selo_tablet`, `malote__com-envelope`, a `abertura` do malote e a tira `sineta__tocando`) e os campos `direcao`, `envelope`, `solta`, `dedo`, `tela`, `selo`, `flash`, `flash_no_quadro` e `no_lugar_do_teclado`.

### 14. Cachorros (fase 6): deitados é pose nova e trote em diagonal

- **O que foi:** a pedido do Guilherme, a Flora e o Lupin ganharam a §6 do manual: `andando` (4 quadros; Flora a 8 FPS, Lupin a 9), `dormindo_na_cama` (2 quadros, 1 FPS) e `inquieto` (2 quadros; Flora a 3 FPS, Lupin a 4), todos em loop, nas linhas 2 a 4 da folha. A tela e a âncora não mudaram: os quadros novos ficam na tela do em pé e pisam na linha dele. O outro sentido é o espelho, como o manual pede. Pontos que não fecham com o manual:
  - **Deitados:** o manual diz que só o em pé e o sentado já existem; não havia desenho deitado. Fiz uma pose nova, de lado, como esfinge: o tronco e a coxa do em pé baixados até o chão, as patas da frente esticadas, a cabeça de sempre com o queixo nas patas, olhos fechados e o rabo no chão. Na Flora a coleira aparece por baixo da orelha, com a plaquinha. A respiração do Q2 sobe as costas 1 px; cabeça, orelhas e patas não mexem.
  - **Cama:** o deitado não traz a cama. O jogo cola na âncora da cama (o centro do tile), espelhado como o sentado da sala; o manifesto diz qual cama em `na_cama`. A cama não muda.
  - **Andar:** o manual descreve uma pata por vez; fiz o trote em pares cruzados (a da frente de perto com a de trás de longe), no mesmo esquema da caminhada dos humanos: 2 px no contato, o corpo 1 px acima na passagem, com a pata que passa 1 px no ar. O rabo da Flora desce e sobe 1 px; no Lupin a cabeça vai 1 px à frente e a orelha dobrada fica para trás.
  - **Inquieto:** o Q1 é o em pé, exatamente; no Q2 a cabeça sobe, a pata da frente de perto sai do chão e o rabo mexe, nos px do manual.
- **Onde:** manual de sprites e animações v1.0, §6, §8.2 e §9.2 (teste 12); `FinancyApp_Assets_v2.md`, lista do corte 2.
- **Sugestão:** registrar no manual a pose deitada (e que ela não traz a cama) e o trote em pares; na Assets, o campo `na_cama` e as três animações como entregues.

### 15. Conferência (fase 7): o que ficou para decidir

- **O que foi:** a fase 7 do manual. `src/qa.py` lê o `assets/` como o jogo lê, monta a listagem de todas as animações (236 linhas, em `previa/qa/animacoes.json`) e confere com as tabelas 8.1 e 8.2: nenhuma divergência; as 50 linhas que não estão no manual (as camadas do tampo e a entrega de costas do Gabriel) têm o motivo registrado. Os testes cobrem os 14 itens da §9.2: 45 no pacote de arte (`teste_animacoes.py`, com três novos: paleta, quadril sentado e listagem) e 6 novos do lado do jogo (`jogo/testes/animacoes.test.js`), que leem o manifesto e os PNGs pela regra de nomes do jogo. O jogo do corte 1 continua desenhando só o parado e o sentado de frente, nas linhas 0 e 1, e a sala ficou igual pixel a pixel em todas as fases. A página `previa/qa/index.html` junta a comparação por personagem e por animação (recortada das folhas, ao lado do desenho original, com o que mudou e os marcadores), a checklist com o resultado de cada teste e o registro do que é fiel, do que foi ajustado e do que precisa de decisão.
- **Diferenças que os testes mostraram e ficaram assim:**
  - **Quadril sentado:** o manual pede 14 px acima da âncora. O alto das pernas sentadas fica a 14 ou 15 px; em quem tem cintura alta (Vivi, Íris, Joana e Duda) a calça começa até 18 px acima. Bate com o "uns 14 px" da Assets.
  - **Cores novas:** só a luz no dorso da mão à mesa (a pele clareada), a boca aberta ao falar e os adereços (tablet erguido, celular, flash). Roupa, cabelo e pele usam só as cores das poses-base.
- **Para decidir (junta o que está em aberto nas notas 4, 6 e 11 a 14):**
  1. o monitor cobre o teclado e o tablet na mesa do Saldanha (nota 4);
  2. teclado e tablet no campo `objetos` da planta ou presos a quem senta (nota 11);
  3. por onde se sai de cada cadeira (nota 12);
  4. a velocidade de andar do jogo (o pé desliza acima de uns 0,5 tile/s);
  5. quem usa a vida à mesa (o Gabriel não vira funcionário);
  6. piscar nos quadros 2 e 3 do olhar para o lado;
  7. a entrega de costas como oficial e quanto o Gabriel se aproxima do malote (nota 13);
  8. a bandeirinha do malote como estado à parte (nota 13);
  9. o encosto da cadeira de costas em outra camada (nota 6);
  10. levar ao manual e à Assets os campos novos do manifesto e os ajustes das notas 9 a 14.
- **Onde:** manual de sprites e animações v1.0, §9.2, §10 (fase 7) e §12.
- **Sugestão:** levar os dez pontos ao projeto de design; a página de conferência mostra cada um no quadro.

### 16. Primeiro ciclo narrativo: a direção v0.2 e o roteiro de falas v0.3 no jogo

- **O que foi:** a pedido do Guilherme, o jogo ganhou a narrativa do primeiro ciclo, adiantando a parte de cena dos cortes 2 a 4: o diretor narrativo (fila, prioridade, unicidade), o executor de cenas no mesmo mapa 2D, as 17 cenas do `financyapp_roteiro_falas_completo_para_claude_v03.json` (copiado sem alteração para `jogo/dados/`), o ciclo mensal (§3.1 da direção) e uma bancada de teste com dados sintéticos. O módulo financeiro de verdade ainda não existe: `jogo/src/dados.js` gera os eventos de domínio (§5) marcados como sintéticos, e sai quando a planilha entrar.
- **Onde:** `jogo/src/calendario.js`, `diretor.js`, `estado.js`, `roteiro.js`, `executor.js`, `atores.js`, `caminho.js`, `ui.js`, `paineis.js`, `painel.js`, `dados.js`, `sala.js` e `main.js`; testes em `jogo/testes/ciclo.test.js` (os exemplos de aceitação da direção) e `roteiro.test.js` (as variantes do JSON).
- **Como o JSON é lido:** as falas, a ordem, as variantes e as escolhas saem do JSON; `roteiro.js` só traduz as animações técnicas (com o fallback do contrato: olhar, nod ou idle), os alvos (malote, mesa do Saldanha, quadro) e o "when" de cada variante para o contexto do jogo. Chave sem valor nunca vai para a tela: a fala é omitida.
- **Decidido no código, para confirmar no projeto de design:**
  1. **GDD §7.2 contra a direção v0.2.** O GDD diz que o primeiro acesso "no dia 6 ou depois" recebe convite adiável; a direção v0.2 (aprovada em 22/10) diz que depois do dia 6 a reunião abre direto, sem adiar. Segui a v0.2. Sugestão: atualizar o §7.2 e a máquina do §16.4.
  2. **Primeiro acesso no dia 6:** nenhuma reunião é agendada, e o estado mostra "pendente". As duas leituras existem só na bancada, para teste.
  3. **Reuniões acumuladas:** uma por competência, a mais antiga primeiro, em sequência na mesma visita. A consolidação do GDD §7.3 continua pendente e não foi feita.
  4. **Gatilhos que o JSON descreve em texto:** C1S3 toca no primeiro clique no escritório depois da C1S1 (`first_voluntary_exploration`); a C1S2 sem histórico toca quando a pessoa abre a mesa do Saldanha (`user_opens_saldanha`); a C3S4 fica disponível no quadro na primeira visita de uma semana nova, ou quando mais de 3 eventos se acumulam fora do app (a síntese do §5), e conta os eventos registrados desde o último resumo visto; a C3S1 fala uma vez por visita e os outros pagamentos só marcam o calendário (`per_financial_event_with_throttle`, sem número no JSON).
  5. **Texto completado:** a C4S3 tem as variantes "confirmou" e "adiou" a prioridade, mas não os botões; ficaram "Acompanhar com clareza" e "Deixar para depois", marcados como complemento do motor. O M0 veio sem acentos no JSON e só os acentos foram repostos. "Período(s)" e "registro(s)" viram singular ou plural pelo número da fala (direção §4). O "Boa tarde" do Gabriel segue a hora (direção §4). A fala "Nossa primeira reunião terminou" sai nas reuniões seguintes.
  6. **Consulta ao Caio:** o formulário da compra entra logo depois da primeira fala dele ("me diz o que você está pensando em comprar"). O veredito e o motivo vêm de um seletor sintético, porque o motor de regras do Caio não existe.
  7. **Card de 30 s (C3S3):** sem conteúdo, que ainda não foi escrito; o painel mostra o lugar dele.
  8. **Reunião em cena:** Guilherme, Vivi e Caio vão às cadeiras de reunião deles e o Saldanha senta na cadeira 5; o Gabriel não vai. Nas cadeiras de costas, a pessoa é desenhada antes da cadeira (nota 6, segunda opção).
  9. **Histórico inicial:** os dois meses importados chegam num envelope simbólico só, o lote `historico-inicial` (questão 2 do §10 da direção, ainda aberta).
  10. **Andar:** velocidade padrão de 1,0 tile/s, ajustável na bancada (nota 15.4). A saída das cadeiras de frente é pela borda até o tile livre ao lado (nota 15.3).
  11. **Persistência:** o perfil fica no armazenamento do navegador até existir servidor; reabrir não repete cena concluída nem duplica evento.
  12. **Placeholders em blocos:** recado "6" no quadro (pré-aviso e convite), marca no calendário, barra de teto no mural, selo FECHADO na tela e bandeirinha no malote.
- **Escopo:** o CLAUDE.md ainda diz "Corte atual: 1". Sugestão: registrar que a narrativa do primeiro ciclo entrou antes dos dados, por decisão do Guilherme.

## Resolvidas

- **Na v2.2:** a escala dos cachorros foi fechada em 34 e 24 px; o Caio está em verde-sálvia; os cachorros parados em pé entraram no corte 2.
- **Na v2.1:** a âncora do sentado é o chão embaixo do quadril; o manifesto tem o campo `pasta`, fixa por tipo; as folhas têm uma animação por linha, com o campo `linha`; a altura dos cachorros foi corrigida; o lote do corte 1 tem 4 poses novas, não 7.

## 17. Leitura da planilha real (Google Sheets)

- **O que foi:** o jogo passou a ler a planilha "Escritório de Finanças" pelo conector Google Sheets do claude.ai (`jogo/src/fonte_planilha.js`, contas em `jogo/src/planilha.js`). Só funciona com o jogo aberto no claude.ai; na primeira leitura o claude.ai pede permissão. Só leitura: nada é escrito na planilha.
- **Privacidade:** nenhum valor real fica no código, no pacote publicado ou no repositório. Os testes usam uma planilha falsa. Os valores existem só na tela, no momento da leitura, e o instantâneo para comparar leituras fica no navegador (perfil `guilherme`, separado do perfil sintético `guilherme-teste`).
- **Decisões que tomei e precisam da sua confirmação:**
  1. A primeira leitura vira um único lote histórico (C1S2), sem cenas de fatura ou pagamento para o que já estava lá.
  2. A planilha não guarda quando o "Pago" foi marcado: a data do evento é a da leitura.
  3. Despesa sem categoria: as opções da C2S3 são a categoria de outra linha com o mesmo histórico e, depois, a mais usada no mês. Isso é **PROPOSTA** minha; a resposta escolhida no jogo não volta para a planilha.
  4. A conferência da fatura compara o débito "CARTÃO NUBANK"/"CARTÃO DIGIO" da conta com a parte do Guilherme (as linhas dele mais metade das "2 X"). Linha sem responsável fica fora da divisão.
  5. Mês só fica "completo" no relatório se a fatura conferir e não houver conta sem "Pago".
- **Falta na spec / na planilha:** não há tetos de categoria na Config, então a C3S3 (80%/100% do teto) nunca dispara com dados reais. **Sugestão:** um bloco "Tetos" na Config (categoria, valor), quando a regra sair de PENDENTE.
