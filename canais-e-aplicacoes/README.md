# Canais e Aplicações · Brandcenter Gestão RH

Página do brandcenter que traduz a marca para os pontos de contato: redes, e-mails, site, apresentações, materiais comerciais, eventos e audiovisual. Para ver, abra `index.html` no navegador.

Segue a mesma ID da página Produtos e Experiências: cabeçalho, menu lateral, hero escuro, seções alternando branco e cinza, fechamento escuro com a faixa vermelha e o mesmo rodapé.

## Estrutura

| Seção | Canal | Módulo ("como codar depois") |
|---|---|---|
| 01 Canais digitais | LinkedIn | Post por intenção: perspectiva, registro, convite, reconhecimento, repertório |
| | Instagram | Grid de cards de captação: pessoas, ambiente, detalhe, bastidor, palco, depoimento |
| | E-mail marketing | Régua por momento: convite, confirmação, lembrete, agradecimento, devolutiva, próximo passo |
| | Portal e site | Mapa do ecossistema com entrada por produto, público, objetivo e momento |
| | Insights no LinkedIn | Edição com editorias fixas: tema, pergunta, especialista, aprendizado, próxima conversa |
| 02 Materiais e formatos | Apresentações | Template de slide: tese, contexto, prova, aplicação, CTA |
| | Materiais comerciais | Checklist: oferta, contrapartida, público, limite, prova, responsável |
| 03 Experiências presenciais | Eventos e cenografia | Planta da jornada: chegada, credenciamento, ponto instagramável, palco, networking, depoimentos |
| 04 Produção audiovisual | Fotografia e audiovisual | Visor de formato e matriz de captação: foto horizontal, foto vertical, reels, aftermovie, depoimento, capa, bastidor |
| 05 Mesmo núcleo | | Os quatro grupos ligados à faixa "Relacionamento qualificado entre lideranças de RH" |

Cada canal tem o mesmo esqueleto: rubrica, título, frase em destaque na cor do canal, texto de apoio, o módulo e uma faixa **USE / EVITE** tirada do próprio texto do canal.

## Cores dos canais

A frase em destaque de cada canal usa uma cor da paleta. Todos os pares passam de 4,5:1.

| Canal | Fundo + texto | Contraste |
|---|---|---|
| LinkedIn | #CC003D + branco | 5,8:1 |
| Instagram | #C0CBFF + Vinho | 9,4:1 |
| E-mail marketing | Azul de apoio #B1DAE5 + Petróleo | 12,3:1 |
| Portal e site | Petróleo #061718 + branco | 18,4:1 |
| Insights no LinkedIn | Rosa de apoio #F498B1 + Petróleo | 8,7:1 |
| Apresentações | Vinho #451531 + branco | 15,0:1 |
| Materiais comerciais | Petróleo #061718 + branco | 18,4:1 |
| Eventos e cenografia | #CC003D + branco | 5,8:1 |
| Fotografia e audiovisual | Lavanda #8198FF + Petróleo | 6,9:1 |

Portal e Insights repetem as cores do Portal Gestão RH e do Insights Gestão RH; Fotografia e audiovisual usa a Lavanda da TV GRH.

## Para validar com a equipe

Estes conteúdos são proposta e estão marcados na página:

- **Portal e site**: os agrupamentos de produtos em cada entrada (público, objetivo e momento).
- **Fotografia e audiovisual**: a matriz de usos (principal e apoio) de cada formato.
- Os modelos de texto (posts, assuntos de e-mail, editorias) usam `[colchetes]` onde entra o conteúdo real.

## Arquivos

- `index.html`: a página pronta no estado inicial.
- `styles.css`: base compartilhada com as outras páginas e os padrões desta (`ca-*`).
- `script.js`: um componente por módulo interativo (`CanaisLinkedin`, `CanaisEmail`, `CanaisPortal`, `CanaisSlides`, `CanaisChecklist`, `CanaisJornada`, `CanaisCaptacao`). Os textos que mudam com o clique ficam nos arrays de cada classe; o HTML já traz o primeiro estado.
- `img/`: fotos reaproveitadas da página Produtos e Experiências.

Os módulos respeitam o botão "Pausar movimento" e a preferência do sistema por menos movimento. O menu lateral acompanha o canal que está na tela.
