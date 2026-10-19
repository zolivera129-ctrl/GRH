# Notas de implementação

Pontos em que o código mostrou que os documentos não fecham. Cada um diz o que foi, onde e uma sugestão. Nada aqui muda `docs/`.

## 1. Âncora da pose sentada

- **O que foi:** a v2 diz que o sentado usa "a mesma âncora (meio dos pés, no chão)" e que o jogo põe essa âncora no centro do tile da cadeira. Com as coxas para a frente, os pés ficam uns 9 px à frente do quadril. Se a âncora fosse o meio dos pés, o quadril cairia atrás do centro da cadeira, em cima do encosto.
- **Onde:** `FinancyApp_Assets_v2.md`, seção "Escala", item "Sentado".
- **Como ficou:** a âncora do sentado é o mesmo ponto da tela do parado, [20, 63]. No sentado, esse ponto é o chão embaixo do quadril; os pés vão para a frente.
- **Sugestão:** escrever "Sentado: mesma tela e mesma âncora do parado. No sentado, a âncora é o chão embaixo do quadril, e os pés ficam à frente dela."

## 2. Pasta de cada peça no manifesto

- **O que foi:** o exemplo do manifesto diz os estados e as direções, mas não em que pasta fica o arquivo (`moveis/`, `objetos/`, `parede/`, `piso/`).
- **Onde:** `FinancyApp_Assets_v2.md`, "Como entregar".
- **Como ficou:** cada peça leva um campo `pasta`. O nome do arquivo segue a regra do documento: `modelo.png`, `modelo__estado.png` ou `modelo__direcao.png`.
- **Sugestão:** pôr `pasta` no exemplo, ou fixar a pasta de cada tipo de peça.

## 3. Onde cada animação fica na folha de sprites

- **O que foi:** o exemplo dá `quadros` e `fps`, mas não diz em que parte da folha está cada animação.
- **Onde:** `FinancyApp_Assets_v2.md`, "Como entregar", entrada `saldanha` do exemplo.
- **Como ficou:** uma animação por linha, quadros da esquerda para a direita, e o campo `linha` em cada animação.
- **Sugestão:** pôr `linha` no exemplo.

## 4. Altura atual dos cachorros

- **O que foi:** a v2 diz "hoje a Flora tem 45 px e o Lupin 32 px". Essa é a altura das artes de vitrine. Nos assets da v1 os dois já estavam reduzidos: Flora com 37 px e Lupin com 23 px.
- **Onde:** `FinancyApp_Assets_v2.md`, seção "Escala", item "Cachorros", e "Em aberto", item 1.
- **Como ficou:** os assets continuam com 37 e 23 px até a escala fechar. A prancha `pixel-art-habbo/previa/escala@2x.png` mostra essa escala ao lado da sugestão da v2 (34 e 24 px).
- **Sugestão:** corrigir o "hoje" para 37 e 23 px e registrar a escala escolhida.

## 5. Poses que já existiam

- **O que foi:** a conta do lote fala em 7 poses novas, incluindo o parado do Saldanha, do Caio e da Vivi. Os três parados já existiam no repositório (os dois primeiros como Contador e Consultor) e batem com as descrições da v2. Foram reaproveitados, então as poses novas foram 4: os sentados do Guilherme, do Saldanha, do Caio e da Vivi.
- **Onde:** `FinancyApp_Assets_v2.md`, "Personagens" e "Conta do lote".
- **Diferença pequena:** a v2 pede a sobrecamisa do Caio verde-sálvia; a atual é verde-oliva. Se quiser o tom mais claro, é só trocar a cor.
- **Sugestão:** atualizar a conta do lote.
