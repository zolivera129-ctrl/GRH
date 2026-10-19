# Fotos do eventface por premiado

Para cada pessoa de `pessoas.csv`, o script acha a foto dela e manda essa foto para a busca por
selfie do [evento no eventface](https://www.eventface.com.br/evento/WO17616LYTGN), a mesma do botão
"Enviar selfie". Depois baixa cada foto encontrada para `Finais\CEOs\<Nome>` ou `Finais\RHs\<Nome>`.
O resultado é o mesmo do "Baixar todas as fotos", só que direto na pasta, com o nome original de
cada arquivo e sem zip.

Não abre navegador: o script conversa direto com o site.

## Antes da primeira vez

1. Instale o Python em <https://www.python.org/downloads/> marcando **Add python.exe to PATH**.
2. Copie esta pasta (`fotos-eventface`) para dentro de `OneDrive_1_19-10-2026`, ao lado de `CEOs`,
   `RHs` e `Finais`.

## Rodando

Dê dois cliques em `rodar.bat`. Na primeira vez ele instala o Pillow sozinho; o Pillow reduz a foto
antes de enviar, como o site faz.

1. **Conferir** mostra qual foto foi escolhida para cada pessoa, sem ir ao site. Olhe as linhas
   `SEM FOTO` e `<- confira`.
2. **Testar com uma pessoa**: faz uma pessoa e para. Confira se a pasta dela em `Finais` ficou certa.
3. **Rodar a lista toda**: faz todo mundo. Cada pessoa leva poucos segundos.

**Ctrl+C** para a qualquer momento. Pode rodar de novo quantas vezes quiser: quem já tem pasta com
fotos em `Finais` é pulado, e quem parou no meio (pasta `Nome (baixando)`) é completado.

No fim sai o `relatorio-eventface.csv` (abre no Excel) com a situação de cada pessoa.

## Se algo não bater

- **Pessoa sem foto ou com a foto errada**: renomeie a foto com o nome da pessoa, ou escreva o
  caminho dela na coluna `foto` do `pessoas.csv` (por exemplo `CEOs\Ana Paula Bogus (SF).jpg`).
  Para refazer quem já foi baixado com a foto errada, apague a pasta da pessoa em `Finais` e rode de
  novo.
- **Pasta com fotos de outra pessoa**: a busca é a do próprio eventface. Se a foto de referência for
  ruim (muito pequena, de lado, com mais gente), troque por outra.
- **"verificar"**: a busca devolveu mais de 400 fotos, e isso é muito para uma pessoa. Nada foi
  baixado. Se estiver certo, rode só essa pessoa com `rodar.bat --so "Nome" --limite 2000`.
- **Lista**: `pessoas.csv` abre no Excel. A coluna `categoria` define a pasta (`CEOs` ou `RHs`).
