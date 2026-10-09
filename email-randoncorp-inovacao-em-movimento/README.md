# E-mail: Inovação em movimento (Randoncorp)

HTML de e-mail marketing feito a partir do layout `input/layout-original.webp`, pronto para colar no RD Station.

- **Arquivo para colar:** `email-inovacao-em-movimento.html`
- **Botão:** leva para https://www.youtube.com/@Randoncorp
- **Prévia:** `preview/desktop.png` (600 px) e `preview/celular.png` (375 px)

## Como usar no RD Station

1. Abra `email-inovacao-em-movimento.html`, copie todo o código e cole no editor de HTML do RD Station.
2. Envie um e-mail de teste para Gmail e Outlook antes do disparo.

As 4 imagens já apontam para links públicos deste repositório (`raw.githubusercontent.com`), então o e-mail funciona assim que é colado. Para o disparo oficial, recomendo hospedar as imagens no próprio RD Station:

1. Suba os arquivos da pasta `img/` no gerenciador de arquivos do RD Station.
2. No HTML, troque cada link `https://raw.githubusercontent.com/.../img/<arquivo>.png` pelo link que o RD gerar para o mesmo arquivo.

Assim as imagens não dependem do GitHub, e o e-mail não leva links de um domínio que alguns filtros de spam olham com desconfiança.

| Arquivo | Onde aparece | Tamanho no e-mail |
|---|---|---|
| `img/deco-estrada-direita.png` | linhas de estrada à direita do texto | 144 × 692 |
| `img/deco-seta-topo.png` | seta do rodapé, ao lado do botão | 102 × 72 |
| `img/deco-seta-base.png` | seta do rodapé, ao lado do logo | 114 × 131 |
| `img/logo-randoncorp.png` | logo | 290 × 32 |

As imagens foram recortadas do layout (cerca de 1,5× o tamanho exibido). Se o time de criação puder exportar as mesmas peças do arquivo original em 2×, com os mesmos nomes e proporções, o logo e as linhas ficam mais nítidos em telas retina.

## Como o HTML foi montado

- **Todo o texto é texto de verdade**, não imagem. Ele aparece mesmo quando o leitor bloqueia imagens (o Outlook bloqueia por padrão), conta a favor na entrega e pode ser lido por leitores de tela. Só as linhas decorativas e o logo são imagens; o logo tem texto alternativo.
- **Estrutura em tabelas com estilos inline**, que é o que Outlook, Gmail, Yahoo e Apple Mail entendem igual.
- **Fonte:** Inter (Google Fonts) onde o leitor aceita fonte web (Apple Mail, iPhone, Outlook para Mac). Nos outros (Gmail, Outlook para Windows, Yahoo), entra Arial. As quebras de linha do layout estão fixas no desktop, então o texto quebra nos mesmos pontos com qualquer uma das duas fontes.
- **Outlook para Windows:** o botão é desenhado em VML, então fica arredondado e clicável. O selo "Inovação em movimento" e a faixa "E o resultado?" aparecem com cantos retos, porque esse Outlook não faz cantos arredondados em HTML.
- **Celular (até 620 px):** as linhas decorativas laterais somem, o texto ocupa a largura toda com margem de 24 px, as quebras fixas são desligadas e o título, o selo e o botão diminuem. Leitores sem suporte a media query (ex.: app do Gmail com conta que não é Gmail) mostram a versão de 600 px reduzida.
- **Texto de pré-visualização** (o que aparece ao lado do assunto na caixa de entrada): "Conheça o projeto que levou uma carreta por mais de 10 mil km pelas estradas do Brasil." Ele fica logo no começo do `<body>` e pode ser editado lá.

## Como gerar as imagens de novo

```bash
pip install numpy pillow
python3 src/build_images.py   # dentro desta pasta; grava em img/
```

O script recorta as peças de `input/layout-original.webp` e salva em PNG transparente (cor fixa e transparência calculada a partir do azul do fundo). Assim o recorte não forma uma caixa de outro tom de azul em volta.
