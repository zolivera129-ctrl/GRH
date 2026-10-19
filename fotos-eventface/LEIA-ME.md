# Fotos do eventface por premiado

Para cada pessoa de `pessoas.csv`, o script acha a foto dela, envia essa foto no "Enviar selfie" do
[evento no eventface](https://www.eventface.com.br/evento/WO17616LYTGN), baixa o resultado em
"Baixar todas as fotos" e descompacta em `Finais\CEOs\<Nome>` ou `Finais\RHs\<Nome>`.

## Antes da primeira vez

1. Instale o Python em <https://www.python.org/downloads/> marcando **Add python.exe to PATH**.
2. Copie esta pasta (`fotos-eventface`) para dentro de `OneDrive_1_19-10-2026`, ao lado de `CEOs`,
   `RHs` e `Finais`.

## Rodando

Dê dois cliques em `rodar.bat`. Na primeira vez ele instala o Playwright sozinho.

1. **Conferir** mostra qual foto foi escolhida para cada pessoa, sem abrir o site. Olhe as linhas
   `SEM FOTO` e `<- confira`.
2. **Testar com uma pessoa**: abre o Edge, faz uma pessoa e para. Confira se a pasta dela em `Finais`
   ficou certa.
3. **Rodar a lista toda**: faz todo mundo.

Enquanto roda, deixe a janela do Edge aberta e acompanhe o console:

- Quando ele não souber o que clicar, ele avisa no console. Aí é só clicar você mesmo na janela. A
  foto da pessoa é escolhida sozinha quando abrir a janela de escolher arquivo.
- **Enter** pula a pessoa da vez, e **Ctrl+C** para tudo.
- Pode rodar de novo quantas vezes quiser: quem já tem pasta com fotos em `Finais` é pulado.

No fim sai o `relatorio-eventface.csv` (abre no Excel) com a situação de cada pessoa.

## Se algo não bater

- **Pessoa sem foto ou com a foto errada**: renomeie a foto com o nome da pessoa, ou escreva o
  caminho dela na coluna `foto` do `pessoas.csv` (por exemplo `CEOs\Ana Paula Bogus (SF).jpg`).
- **Pergunta "o 'Baixar todas as fotos' agora baixa só as fotos desta pessoa?"**: ela aparece quando o
  site não cria um botão novo depois da selfie. Olhe a janela: se as fotos mostradas são só as da
  pessoa, responda `s` e ele passa a clicar sozinho.
- **"parece o evento inteiro"**: o zip veio com mais de 400 fotos. O script não descompacta sem você
  confirmar e deixa o download em `_eventface`.
- **Lista**: `pessoas.csv` abre no Excel. A coluna `categoria` define a pasta (`CEOs` ou `RHs`).
