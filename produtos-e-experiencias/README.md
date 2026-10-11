# Produtos e Experiências · Brandcenter Gestão RH

Página do brandcenter com os símbolos dos eventos, relacionamento, encontros, inteligência e mídia, reconhecimento e ecossistema. Para ver, abra `index.html` no navegador.

## Bloco animado do GRH Experience

O bloco usa o símbolo original do Experience e roda este roteiro em loop (8,3 s):

| Tempo (s) | Cena |
|---|---|
| 0,00 – 0,90 | 1. O símbolo original gira devagar no sentido horário. |
| 0,90 – 1,75 | 2. Ele dá um giro de 360° e vira uma bola de tênis. As costuras se desenham durante o giro. |
| 1,75 – 2,12 | 3. A bola cai, amassa um pouco ao tocar o chão (com uma sombra de contato) e sobe. |
| 2,12 – 2,85 | 4. Subindo, a bola gira 360° e volta a ser o símbolo. |
| 2,85 – 3,35 | 5. O símbolo segue girando na velocidade em que a bola terminou. |
| 3,35 – 6,10 | 6. O símbolo vira volante (as janelas abrem do centro para fora), vira devagar para a direita e depois para a esquerda, como numa curva. |
| 6,10 – 6,85 | 7. O volante volta para a direita acelerando até virar um borrão. |
| 6,85 – 8,30 | 8. No borrão ele volta a ser o símbolo e desacelera até o giro lento da cena 1. |

A velocidade de giro não dá saltos entre as cenas, e o loop termina num ângulo múltiplo de 90°, então a volta para a cena 1 é contínua.

Como nos outros blocos, o gesto roda com o mouse em cima, com o foco do teclado ou com um toque. Ao sair, o bloco volta suave para o símbolo. Ele respeita o botão "Pausar movimento" e a preferência do sistema por menos movimento. Com o atributo `data-autoplay` no botão, o loop roda sempre.

### Formas

- **Símbolo original**: vetorizado do arquivo enviado (4 lados côncavos em curvas cúbicas, pontas arredondadas), com erro máximo de 0,2 px. Ele também entrou no lugar da estrela antiga na faixa "A família" e no cabeçalho da seção GRH Experience.
- **Bola de tênis**: a mesma da versão anterior.
- **Volante**: redesenhado sobre a referência, com as mesmas proporções de aro, travessa e janelas. Para ficar na linha da identidade, os cantos das janelas foram arredondados, como nos outros símbolos, e o cubo ganhou a estrela do Experience no lugar do círculo.

### Borrão

Girando muito rápido, uma forma vira a média dela em volta do centro, e essa média só depende da distância ao centro. O script mede essa média (cobertura por raio) quando a página fica ociosa e desenha um disco com gradiente radial por cima da forma nítida, mais forte quanto maior a velocidade. O aro continua nítido, o miolo vira um véu e a estrela aparece de novo quando o giro diminui.

### Arquivos

- `experience-card.js`: o gesto, sem dependências. A tabela `T` tem os tempos das cenas; `W_SLOW`, `W_BALL` e `W_MAX` são as velocidades de giro (°/s); `DROP`, `APEX` e `squash()` controlam o quique.
- `index.html`: marcação do bloco (`svg.gb-exp`) com os paths do símbolo e das janelas do volante.
- `styles.css`: sem as animações CSS da versão anterior (estrela, bola e raquete).
- `tools/experience_geometry.py`: gera os paths do símbolo e do volante a partir das medidas. Para mudar as proporções do volante, edite as constantes, rode `python3 tools/experience_geometry.py` e troque os paths no `index.html`.
