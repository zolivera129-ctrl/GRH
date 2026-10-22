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

## Publicar

A página também fica publicada como Artifact no claude.ai, para abrir sem
instalar nada. O Artifact serve só os arquivos publicados junto com a
página, então o `empacotar.py` monta em `pacote/` (fora do git) a página, o
estilo, os scripts, os assets e o layout, com os caminhos dos dados trocados
para dentro do pacote:

```
python3 empacotar.py
```

Depois, publique `pacote/index.html` com os arquivos do pacote, sempre na
mesma URL (está no CLAUDE.md).

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
- `src/main.js`: liga tudo, amplia a sala 2× (ou 1× numa tela estreita) e
  mostra o resultado da validação ao lado. Os caminhos dos dados vêm dos
  atributos `data-assets` e `data-layout` do HTML.
- `empacotar.py`: monta o pacote para publicar como Artifact.
- `testes/validacao.test.js`: o layout padrão passa, e layouts quebrados
  de propósito falham na regra certa.
- `testes/animacoes.test.js`: o manifesto e as folhas do pacote de arte,
  lidos como o jogo lê: o parado e o sentado de frente continuam nas linhas
  0 e 1, cada folha cabe as linhas e os quadros, as camadas, os marcadores
  e os adereços citados existem. O jogo do corte 1 ainda não toca as
  animações; o teste garante que elas chegam inteiras.

O desenho segue a mesma montagem da prévia `sala-parada.png` que o
`build.py` gera. Na conferência, o canvas saiu igual à prévia; só 192
pixels semitransparentes diferem, em 1 unidade de cor.
