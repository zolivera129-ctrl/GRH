# FinancyApp: o jogo

A tela do jogo: uma página estática com Canvas 2D e JavaScript puro em
módulos, sem framework e sem etapa de build. Ela lê direto o
`manifest.json` dos assets (`../pixel-art-habbo/assets/`) e o layout da
planta (`../docs/FinancyApp_Layout_12x10_v1.json`).

Hoje ela mostra o corte 1, a sala parada: o escritório 12×10 com todo mundo
no seu posto e a validação da planta rodando ao carregar.

## Abrir

O navegador não carrega os JSON abrindo o arquivo direto, então a página
precisa de um servidor local. Na pasta `financyapp`:

```
python3 -m http.server 8000
```

e acesse `http://localhost:8000/jogo/`.

## Testar

Na pasta `jogo`, com o Node 22 ou mais novo (sem instalar nada):

```
npm test
```

## Arquivos

- `index.html` e `estilo.css`: a página. A arte é desenhada em 1× no canvas
  e ampliada 2× sem suavizar (`image-rendering: pixelated`).
- `src/carregar.js`: carrega o manifesto, o layout e as imagens, e aplica a
  regra de nomes de arquivo da v2.2 (a mesma do `build.py`).
- `src/sala.js`: desenha a sala: paredes, piso, peças de parede, móveis em
  ordem de profundidade, objetos nos encaixes, personagens sentados nos
  postos e cachorros nas camas. Com a opção `planta`, marca no piso o
  acesso (azul) e a circulação obrigatória (laranja).
- `src/validacao.js`: as seis regras da seção "Validação" da planta, numa
  função pura (`validar`), e o cálculo da circulação obrigatória.
- `src/main.js`: liga tudo e mostra o resultado da validação ao lado da
  sala.
- `testes/validacao.test.js`: o layout padrão passa, e layouts quebrados
  de propósito falham na regra certa.

O desenho segue a mesma montagem da prévia `sala-parada.png` que o
`build.py` gera. Na conferência, o canvas saiu igual à prévia; só 192
pixels semitransparentes diferem, em 1 unidade de cor.
