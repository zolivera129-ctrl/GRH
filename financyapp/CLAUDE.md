# FinancyApp

Jogo de navegador, individual: um escritório em pixel art isométrico, no estilo Habbo, que cuida das finanças pessoais do Guilherme a partir da planilha dele. Só o Guilherme usa o app.

## Documentos

Os documentos de design ficam em `docs/`. Eles são cópias do projeto de design no claude.ai, que é a fonte da verdade. **Não edite nada em `docs/`.**

| Arquivo | Para que serve |
|---|---|
| `docs/FinancyApp_GDD_Mestre_Consolidado_v2.md` | Visão geral, regras e a ordem dos cortes (§17.2). Comece por aqui. |
| `docs/FinancyApp_Anexo_Integral_Fontes_01a08.md` | Texto original de cada capítulo. Antes de implementar uma regra, confira a fonte aqui. |
| `docs/FinancyApp_Planta_12x10_v1.md` | Planta do escritório: zonas, pontos de uso e regras de validação. |
| `docs/FinancyApp_Layout_12x10_v1.json` | A mesma planta em dados. É a fonte das posições. |
| `docs/FinancyApp_Assets_v2.md` | O que desenhar, as medidas e como entregar os assets. |
| `docs/FinancyApp_Planta_12x10_previa.png` | Prévia em blocos. Referência visual, não arte final. |
| `docs/FinancyApp_Matriz_Rastreabilidade_v2.md` | Rastreio das decisões. Não é fonte de regra. |

Leia só o que a tarefa pede. Os documentos são longos.

## Etiquetas dos documentos

- **APROVADO** e **BASE**: pode implementar.
- **PROPOSTA**: só com a minha confirmação.
- **PENDENTE** e **A VALIDAR**: não implemente e não invente valor. Pergunte.

## Escopo

- O trabalho segue os cortes do GDD §17.2, um de cada vez.
- **Corte atual: 1, a sala parada.** O diorama 12×10 com todo mundo no lugar, sem dados.
- Não adiante nada de outro corte.
- Cada sessão termina com algo que dá para ver rodando.
- **Stack da tela:** página estática com Canvas 2D e JavaScript puro em módulos, sem framework e sem etapa de build, em `jogo/`. Testes com `node:test`.
- **Servidor** (planilha, regras, carteira, IA e login): ainda não definido. A recomendação é Python com SQLite, a decidir quando o jogo chegar aos dados.
- Não adicione framework ou biblioteca nova sem perguntar.

## Regras que valem sempre

1. **Código decide, IA explica.** Contas, regras, vereditos, recompensas e desbloqueios são determinísticos. A IA nunca produz um número que o jogo usa como verdade.
2. **Nunca inventar dado financeiro.** Dado de teste só pode existir marcado como sintético.
3. **Login de um usuário só**, antes de qualquer coisa ir para um domínio público.
4. **Fuso:** America/Sao_Paulo.

## Convenções do escritório

- **Coordenadas:** cada tile é A/B. A0/B0 é o canto do fundo. A cresce ao longo da parede direita; B cresce ao longo da parede esquerda.
- **Projeção:** isométrico 2:1, tile de 64×32. A arte é feita em 1× e ampliada 2× sem suavizar (`image-rendering: pixelated`).
- **Ligação planta ↔ arte:** o campo `modelo` do JSON da planta é a chave do mesmo modelo no `manifest.json` dos assets. O campo `objetos` diz o que vai em cima de cada mesa.
- **Validação da planta:** as seis regras da seção "Validação" da planta são a função `validar` de `jogo/src/validacao.js`. Ela roda ao carregar o layout e, mais tarde, vai rodar a cada vez que um móvel for movido.
- **Espelhamento:** personagens são espelhados; móveis não.
- **Arte que ainda não existe:** use blocos como placeholder, no estilo da prévia, com as mesmas âncoras.

## Jogo

A tela fica em `jogo/` e lê direto o `manifest.json` dos assets e o layout em `docs/`.

- Para abrir: na pasta `financyapp`, rode `python3 -m http.server 8000` e acesse `http://localhost:8000/jogo/`.
- Para testar: na pasta `jogo`, rode `npm test`.

## Arte

A arte é gerada em código, no pacote pixel-art-habbo. O `build.py` gera a pasta `assets/` e o `manifest.json` seguindo `docs/FinancyApp_Assets_v2.md`: nomes de arquivo, âncoras e encaixes.

## Quando a spec não fecha

Se o código mostrar que algo nos documentos não funciona ou está faltando, não decida sozinho e não mude `docs/`. Anote em `NOTAS_DE_IMPLEMENTACAO.md` o que foi, onde e uma sugestão, e me avise. Eu levo de volta para o projeto de design.

## Idioma

Responda em português.
