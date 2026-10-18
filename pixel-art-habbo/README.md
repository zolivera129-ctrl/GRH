# Pixel art estilo Habbo

Quatro artes em pixel art no estilo Habbo Hotel, cada uma num cantinho de
quarto isométrico, com a etiqueta de nome em cima da cabeça.

| Arte | Quem | Cenário |
|---|---|---|
| `out/01-guilherme.png` | Guilherme: cabelo cacheado, óculos redondos, camiseta branca com o boneco azul, bolsa transversal preta | piso de deck de barco, janela para o mar de Arraial, boia |
| `out/02-gabriel.png` | Gabriel: boné preto, óculos meio-aro, barba, alargador, camiseta Tone Death, jogger e Vans | estúdio roxo, letreiro ON AIR, disco de ouro, toca-discos, caixa de som |
| `out/03-flora.png` | Flora: labrador preta com coleira vermelha | manta vermelha, potinho de ração, bolinha de tênis |
| `out/04-lupin.png` | Lupin: vira-lata pequeno, pelo duro, barba e sobrancelhas caramelo | manta xadrez azul, caminha, ossinho |

`out/00-todos.png` junta as quatro lado a lado.

Cada arte tem 96x120 pixels de verdade, ampliados 10x sem suavização
(960x1200). Os personagens são desenhados pixel a pixel em código, em
`src/chars.py`; os cenários ficam em `src/scene.py` e `src/build.py`.

Para gerar de novo:

```
python3 src/build.py
```
