# FinancyApp: o jogo

A tela do jogo: uma página estática com Canvas 2D e JavaScript puro em
módulos, sem framework e sem etapa de build. Ela lê direto o
`manifest.json` dos assets (`../pixel-art-habbo/assets/`) e o layout da
planta (`../docs/FinancyApp_Layout_12x10_v1.json`).

Hoje ela mostra o escritório vivo com o primeiro ciclo narrativo: as 17
cenas do roteiro de falas v0.3 acontecendo no mesmo cenário (Vivi na
recepção, o envelope do Gabriel, a consulta ao Caio, o pré-aviso do dia 1º e
a reunião do dia 6), com uma bancada de teste ao lado para simular datas e
eventos com dados sintéticos.

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

- `index.html` e `estilo.css`: a página, com o palco (canvas, balões e
  painéis) e a bancada de teste.
- `dados/financyapp_roteiro_falas_v03.json`: o roteiro de falas do autor,
  sem alteração. É a fonte das falas, das variantes e das escolhas.
- `src/carregar.js`: manifesto, layout e imagens (regra de nomes da v2.2).
- `src/sala.js`: desenha a sala quadro a quadro, com móveis e pessoas em
  ordem de profundidade, a camada do tampo à mesa e os estados dos objetos.
- `src/atores.js` e `src/caminho.js`: o elenco (animação, caminhada,
  sentar e levantar) e os caminhos na planta.
- `src/calendario.js`: o ciclo mensal (primeira reunião, convite do dia 6,
  pré-aviso M0), puro e testado.
- `src/diretor.js`: o diretor narrativo (fila, prioridade, unicidade,
  condensação) e os registros de visto, pendente e concluído.
- `src/estado.js`: o perfil persistido no navegador.
- `src/roteiro.js`: traduz o JSON do roteiro para os comandos do motor.
- `src/executor.js`: encena os comandos (andar, falar, escolher, objetos,
  painéis); pular uma cena mantém os registros.
- `src/ui.js` e `src/paineis.js`: balões, escolhas, o quadro da reunião, a
  consulta ao Caio e o livro do mês.
- `src/dados.js`: dados financeiros SINTÉTICOS e os eventos de domínio,
  até o módulo da planilha existir.
- `src/painel.js`: a bancada de teste (data, casos de aceite, eventos).
- `src/main.js`: liga tudo.
- `src/validacao.js`: as seis regras da planta.
- `testes/`: validação da planta, animações, ciclo mensal e diretor
  (`ciclo.test.js`) e o roteiro (`roteiro.test.js`).

O desenho segue a mesma montagem da prévia `sala-parada.png` que o
`build.py` gera. Na conferência, o canvas saiu igual à prévia; só 192
pixels semitransparentes diferem, em 1 unidade de cor.

## Fonte dos dados

Por padrão o jogo lê a planilha real pelo conector Google Sheets do claude.ai (só leitura, só funciona aberto no claude.ai). Na bancada, "Fonte dos dados" troca para os dados sintéticos de teste; cada fonte tem o seu perfil salvo. "Ler a planilha agora" relê no meio da visita: o que mudou (fatura nova, Pago marcado, linha nova na conta) vira evento.
