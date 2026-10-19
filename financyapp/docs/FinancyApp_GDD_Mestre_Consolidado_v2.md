---
title: "FinancyApp — Game Design Document Mestre"
version: "2.0 — consolidação integral dos sete arquivos-fonte"
date: "2026-10-19"
status: "Regras conceituais consolidadas; balanceamentos e algumas especificações em aberto"
---

# FinancyApp

## Game Design Document Mestre — versão 2.0

**Data-base:** 19 de outubro de 2026  
**Cobertura:** Capítulos 01–08 organizados em **sete documentos recebidos** (Universo/Identidade e Personagens no primeiro arquivo, Economia no segundo, mais os Capítulos 04–08).  
**Tipo:** experiência individual 2D de navegador, gestão financeira pessoal baseada em dados reais, escritório isométrico e narrativa interativa.  
**Natureza desta revisão:** consolidação documental e tradução para requisitos; **não equivale a aprovação de parâmetros pendentes nem a produto implementado**.

> **Política de integridade editorial.** A expressão **APROVADO** identifica regras expressamente decididas ou inequívocas nos arquivos-fonte. **BASE** identifica um requisito dos documentos-base anterior aos capítulos posteriores, preservado salvo revisão explícita. **PROPOSTA** é conteúdo criativo ou solução técnica sujeita a validação. **PENDENTE** é definição que o jogador ainda não aprovou ou que depende de verificação dos dados reais. Uma opção escolhida (A, B, C, D) nunca autoriza inventar seu conteúdo.


---

# 1. Fontes, escopo e precedência

## 1.1. Mapeamento dos sete arquivos recebidos

| Código | Capítulos / domínio | Documento-fonte | Papel no GDD |
|---|---|---|---|
| F01 | 01–02, universo, elenco e narrativa | `escritorio-universo-identidade-biblia-personagens.md` | Bíblia de identidade; inclui decisões, propostas e pontos a validar, distinguíveis por etiquetas internas |
| F03 | 03, economia | `financyapp-economia-v1.md` | Tabela de moedas e operações aprovadas |
| F04 | 04, personalização | `FinancyApp_Capitulo_04_Loja_e_Personalizacao.md` | 11 decisões estruturais e quatro conflitos resolvidos |
| F05 | 05, progressão | `FinancyApp_Capitulo_05_Progressao_e_Escritorios.md` | Dez perguntas e nove conflitos resolvidos |
| F06 | 06, conquistas | `capitulo-06-conquistas-e-marcos.md` | Dez perguntas e dez conflitos resolvidos |
| F07 | 07, rotinas | `FinancyApp_Capitulo_07_Rotinas_e_Eventos.md` | Dez perguntas e oito conflitos resolvidos |
| F08 | 08, educação | `FinancyApp_Capitulo_08_Educacao_Financeira.md` | Dez perguntas e oito conflitos resolvidos |

**Diagnóstico documental:** a hipótese de que os Capítulos 01 e 02 foram unidos é **compatível com o conteúdo de F01** (universo, identidade, elenco, relações, roteiros), mas F01 não traz duas seções formais intituladas “Capítulo 01” e “Capítulo 02”. O vínculo 01–02 é uma classificação editorial desta consolidação, não a reprodução de dois arquivos autônomos.

Os arquivos `escritorio-regras-do-jogo.md` e `escritorio-personagens-e-espacos.md` são **documentos-base históricos citados por F01**, e parte de seu conteúdo foi preservada em F01. O GDD 1.1, anteriormente gerado, foi usado como referência técnica auxiliar, **não como fonte superior às sete consolidações entregues**. O conjunto integral e sem cortes das sete fontes acompanha esta revisão no arquivo `FinancyApp_Anexo_Integral_Fontes_01a08.md`.

## 1.2. Regras de precedência

- Decisões posteriores **explícitas e específicas** ajustam regras gerais mais antigas. Exemplo: revenda com reembolso integral permanece para itens comercializáveis; **nenhuma roupa pode ser vendida** [F03 §4; F04 §04.10].
- O elenco da Bíblia não substitui condições posteriores de desbloqueio, propriedade ou XP. Ideias de contratação por CE e promoção de personagens em F01 mantêm a etiqueta **PROPOSTA/DEPENDÊNCIA**, respeitando as regras expressas de F05 [F01 §3.3; F05 P04–P05].
- Propostas de biografia, roteiros, nome de novos profissionais, catálogo ilustrativo, cronologia de episódios e ações de personagens não se tornam automaticamente conteúdo fechado [F01].
- Valores **explícitos** da tabela econômica F03 substituem antigas observações de que moedas “ficariam para depois”. Faixas de preço não definem SKUs finais [F03 §§2–3].
- Correções da planilha atualizam fatos e indicadores, mas não apagam automaticamente XP, espaços, itens, memórias ou conquistas históricos reconhecidos [F05 C07; F06 C01/C03/C07].
- **A modalidade B dos estágios** foi selecionada na conversa do projeto, mas o texto completo dessa modalidade **não integra os sete arquivos**. Mantém-se registrada sem inferir requisitos adicionais.

# 2. Visão, princípios e ciclo de jogo

## 2.1. Fantasia central

**APROVADO [F01 §1].** Guilherme funda uma firma que o ajuda a manter uma vida financeira saudável. Planilhas reais determinam os acontecimentos financeiros; uma equipe de personagens transforma marcos, dúvidas e rotinas em convivência, histórias, escolhas e lembranças. O objetivo não é competir por patrimônio nem comprar progresso, e sim desenvolver segurança, clareza, liberdade de escolha e capacidade de realização.

**Tom:** comédia observacional brasileira com drama humano e conflitos temporários, sem humilhação por dificuldades econômicas. A história pode mostrar situações ficcionais, mas nunca disfarça gastos, consultas, viagens, sincronizações ou pagamentos inventados como fatos reais. O jogo é individual e não exige multiplayer, ranking público ou mundo aberto [F01 §§1–2].

## 2.2. Princípios imutáveis

1. **Registrar não pune:** valores de um gasto não alteram a recompensa pelo ato válido de registrá-lo. Alertas refletem dados, não culpa.
2. **Realidade antes de cliques:** acesso repetido, desfazer/refazer ações e reimportação não produzem ganhos adicionais.
3. **Código decide, IA explica:** valores, regras financeiras, elegibilidade, recompensas, conquistas e desbloqueios são determinísticos.
4. **Dinheiro real separado de moeda de jogo:** compras cosméticas não modificam registros financeiros, análises ou vereditos.
5. **Permanência de progressão:** uma dificuldade financeira futura não retira níveis, salas, conquistas ou narrativas legítimas.
6. **Ajuda financeira sempre acessível:** salas opcionais, roupas e relações não podem bloquear ferramentas essenciais.
7. **Privacidade contextual:** cada pessoa/personagem conhece só o necessário e o autorizado.
8. **A ausência não destrói a história:** eventos importantes recuperáveis permanecem disponíveis.
9. **O avatar não decide pelo usuário:** nenhuma compra, contratação, meta, compromisso ou consentimento é automático.

## 2.3. Loop principal

`Planilha atualizada → leitura/validação → sinais ambientais → consulta e pequenas ações → reunião/fechamento → conquistas e eventos → progressão/decoração → novo ciclo.`

| Camada | Frequência ou gatilho | Regra |
|---|---|---|
| Mundo | Ao abrir ou navegar | Reagir aos dados efetivamente conhecidos; permitir observar e conversar sem obrigação |
| Ações financeiras | Quando há fato legítimo | Registrar, categorizar, pagar, planejar e consultar, com recompensa quando elegível |
| Semanal | Segunda-feira, quando aplicável | Relatório, sugestão de prioridades e ação semanal válida |
| Mensal | Dia **6** ou próximo acesso posterior | Convocação de reunião sobre competência anterior, com possibilidade de um adiamento |
| Progresso | XP/nível, marcos reais, missões e narrativa | Desbloquear oportunidades sem vender ferramentas essenciais |
| Eventos | Calendário/estado narrativo/fatos validados | Rotinas orgânicas, capítulos recuperáveis e celebrações proporcionais |
| Educação | Conteúdo geral ou contexto autorizado | Diálogos, desafios, biblioteca e simulações isoladas do financeiro real |

Sessões curtas são o padrão desejado. Atividades facultativas de carinho nos cães, decoração, microcenas e pílulas não devem ser cobranças diárias ou a base de penalidades [F01 §§4, A; F07 P04].

# 3. Mundo, dioramas, interface e ambientação

## 3.1. Direção de arte

**APROVADO/BASE [F01 §2].** Pixel art isométrica inspirada em Habbo, projeção **2:1**, tiles **64 × 32 px**, contornos escuros por objeto. Moderno, arejado, iluminado; madeira clara, off-white, verde-sálvia, azul-marinho e plantas. Tablets, monitores e teclado refletem o trabalho financeiro atual. O escritório inicial tem **12 × 10 tiles** e permanece acessível após expansões [F01 §§2–3; F05 P01].

**APROVADO [F01 §§2–4].** O usuário vê Guilherme fisicamente em cada diorama acessado; avatar anda e interage autonomamente quando ocioso, mas cliques e decisões do jogador têm prioridade. Consultas financeiras abrem rapidamente, sem esperar o fim da animação. Cenas longas usam painel de diálogo com nome/retrato e pequenas movimentações no diorama. Há um hub para troca rápida de unidades, sem obrigatoriedade de percorrer uma cidade.

## 3.2. Planta inicial e ocupação

- **Vivi — recepção:** posto de acolhimento independente da consultoria.
- **Caio — consultoria:** posto próprio e sineta de chamada. Em F07, consultas ocorrem por ligação de voz; a cena física não pode ser confundida com obrigação de recepção.
- **Saldanha — contabilidade:** mesa, monitor, calendário, bandeja, mural, planta e painel de fechamento.
- **Guilherme — direção:** mesa do fundador e assento da reunião; não é vaga de contratação.
- **Flora e Lupin:** espaço de descanso, circulação e interações não obrigatórias.
- **Futuras áreas:** portas/unidades para Tesouraria, Metas, Auditoria e especiais, conforme desbloqueios.

**Conflito de layout a verificar:** F01 apresenta dois postos técnicos fixos (Saldanha e Caio), terceira estação flexível desbloqueável **além do posto de recepção de Vivi**. A ocupação real de 12 × 10 tiles deve ser validada em uma planta navegável; não presumir espaço físico para todas as mesas [F01 §§3.1, 9A].

## 3.3. Linguagem ambiental

| Objeto | Estado verificável | Cuidado de implementação |
|---|---|---|
| Bandeja | Contas a pagar | Não exibir conta fictícia |
| Calendário | Vencimento não quitado em até três dias | Distinguir data confiável e ausência de dados |
| Malote | Sincronização de cartão registrada; envelope de Gabriel | Recebido não significa conciliado; mostrar erro/divergência quando houver |
| Planta | Saldo final projetado acima/abaixo de **R$ 1.000** | A planta é feedback, não punição por lançar gasto |
| Mural | Tetos, faturas e erros pertinentes | Comentário ao passar de 80%; destaque ao passar de 100% do teto |
| Quadro branco | Relatório e barras de categorias | Dados conferidos versus estimados diferenciados |
| Tela “FECHADO” | Conciliação real concluída | Nunca marcar período incompleto como fechado |
| Janela | Horário local pertinente | A referência original é São Paulo; política por jogador/fuso deve ser especificada |
| A Neblina | Dados inconclusivos, contraditórios ou pendentes | Nunca representar pobreza ou dívidas como defeito moral |

**PROPOSTA técnica:** redundância textual para sinais por cor e suporte a teclado/leitores de tela. Não atribuir estados apenas por animação/verde-vermelho.

## 3.4. Sede permanente, múltiplos espaços

**APROVADO [F05 P01, P04, P06].** Uma sede principal cresce por salas/ambientes/andares, conservando propriedade, itens e layouts. F01 também estabelece hub de dioramas independentes e descreve imóveis alternativos e sedes de prestígio; essa direção pode coexistir com sede principal única, **desde que** o modelo de navegação, instâncias e critérios de desbloqueio seja reconciliado antes de implementação [PENDENTE de arquitetura]. Os marcos de reserva da base (1/3/6 meses de saídas) continuam vigentes até uma revisão expressa [F01 §3.2; F05 §4].

# 4. Elenco, relações e direção narrativa

## 4.1. Papéis oficiais

| Personagem | Papel e identidade | Limite obrigatório |
|---|---|---|
| **Guilherme** | Fundador, diretor e avatar do jogador | Nunca compra, contrata, define meta ou dá consentimento por conta própria |
| **Vivi** | Recepcionista, amiga de infância, acolhimento, visitantes e eventos | Não substitui Caio ou Saldanha; intervenção excepcional sobre hábitos é pendente de critérios |
| **Saldanha** | Contador: leituras, categorias, pendências, projeções e reunião mensal | Não decide compras no lugar do motor consultivo de Caio |
| **Caio** | Referência na orientação financeira e análise de compras | Não atua como recepcionista; veredito calculado por regra, não por IA |
| **Gabriel** | Visitante com vínculos reais à sincronização de seu cartão | Aparições operacionais devem ter gatilho verdadeiro; não é funcionário fixo |
| **Flora** | Labrador preta, coleira/manta vermelha, afetuosa e preguiçosa | Carinho é opcional; sem indicador punitivo de cuidado diário |
| **Lupin** | Cão pequeno, pelagem dura/características caramelo, brincalhão e cauteloso | Afeição de novas pessoas se constrói naturalmente, sem obrigação |
| **Otto** | Responsável invisível por Diário e memórias | Não ganha sprite/presença física antes do arco de estreia do Arquivo |
| **Sr. Pra Ontem** | Pressão e urgências artificiais, humor teatral | Não gera boletos, crises ou dívidas fictícias |
| **A Neblina** | Incerteza decorrente de dados não verificados | Não surge apenas porque a situação financeira está difícil |

**Vivi [F01 §9A].** Mulher negra de cabelos cacheados, roupas coloridas e salto alto; recebe visitantes, usa expressões ocasionais em inglês e conhece Guilherme desde a infância. Direções de sua vida social e familiar descritas na Bíblia são contexto narrativo fornecido ou criativo conforme a etiqueta original; não inventar lembranças reais específicas. Sua possível conversa delicada sobre consumo **não pode ser ativada** sem limiares, consentimento, tom e frequência aprovados.

**Caio e Saldanha [F01 §§7–8].** A dinâmica contrasta rigor numérico e acolhimento; ambos trabalham em conjunto, sem que um invalide o outro. Caio pode falar em voz com o jogador no fluxo de F07. Saldanha tem participação eventual inesperada em levantamentos, sujeita a cadência e não intrusão ainda pendentes.

**Gabriel e narrativa pessoal [F01 §§9, 9A].** Sua presença é motivada por sincronização, conferência, reunião ou fechamento pertinentes; vínculo afetivo/romântico foi descrito como **direção narrativa**, nunca como confirmação de sentimentos, consentimento ou fatos da vida real. Escolhas pessoais do jogador prevalecem.

## 4.2. Histórias e memória

**APROVADO [F01 §§4, 12, 14; F05 P07/P09; F07 P10].** Personagens evoluem por hábitos, relações e lembranças; há conflitos temporários e reconciliações, sem bloquear serviços nem permitir que a relação cause punição econômica. O Diário armazena **fatos comprovados** separados de **memórias ficcionais**, além de escolhas e capítulos efetivamente vistos. Pode recuperar capítulos importantes e apresentar variantes coerentes com a cronologia.

**PROPOSTAS DE ROTEIRO [F01 §§15–18].** A temporada “A Firma Abriu”, o arco “Dois jeitos de cuidar” (A1 a A5), as biografias ficcionais e os futuros funcionários Lia, Tito, Duda, Malu, Joana, Íris e Nina são material de pré-produção, não lista final de conteúdo obrigatoriamente aprovado. Podem servir à escrita, mas aprovação de personagem, sprite, episódio, custo ou recompensa exige rastreabilidade. A condição de Otto “invisível até a estreia” é definida.

## 4.3. Presença orgânica

**APROVADO [F07 P01–P03/C01–C03].** Rotinas refletem calendário e hora reais, inclusive possibilidade de escritório vazio de madrugada. Vivi acolhe quando está presente **e há algo pertinente**, senão a entrada é livre. Após um dia de ausência, há mensagem especial de retorno, entregue pessoalmente ou por canal digital segundo presença; não é necessário fazê-la comparecer em horário impróprio. Saldanha pode aparecer de surpresa em contexto pertinente, sem impedir uso financeiro normal.

---
# 5. Planilha, dados financeiros e regras de verdade

## 5.1. Fontes e escopo

**BASE [F01 §5, Apêndice A].** A planilha do usuário é a fonte principal dos lançamentos, contas, cartões e reservas. Para o orçamento de Guilherme, o cartão compartilhado inclui **sua parte e metade dos lançamentos “2 X”**, sem tomar como próprios gastos de terceiros. A base descreve conta corrente, lançamentos `Pago`, parcelas e linhas de `POUPANÇA`; somente dados efetivamente disponíveis e autorizados alimentam o jogo.

Estados obrigatórios de informação: **previsto / registrado / sincronizado / conferido / concluído / corrigido / indisponível**. A interface não confunde sincronização com conferência nem confirmação com evidência de pontualidade. Os cartões originais não possuíam necessariamente **data por compra**; não fabricar precisão diária inexistente [F01 §5].

**BASE de tetos [F01 Apêndice A].** Categorias: Delivery, Lazer, Assinaturas, Compras. Teto inicial = média dos três meses anteriores menos **10%**, quando existe histórico adequado. Proposta de revisão na primeira segunda do primeiro mês de cada trimestre, aprovada ou alterada pelo jogador. Alertas após **80%** e **100%** de consumo do teto. Moradia, contas e saúde ficam de fora dessa regra inicial.

## 5.2. Reserva, colchão e projeções

- **Colchão operacional:** **R$ 1.000** de saldo final projetado em cada mês afetado por uma compra. Não confundir com reserva de emergência [F01 Apêndice A].
- **Reserva reconhecida:** saldo anterior à implantação, informado pelo usuário, somado às transferências `POUPANÇA` marcadas `Pago` conforme a base; cada mês deve integrar a série. **Retiradas da reserva permanecem sem regra de lançamento** [F01 §5 e Apêndice A].
- **Marcos de reserva:** 1, 3 e 6 meses equivalentes de saídas reais, com reconhecimento histórico permanente [F01 Apêndice A; F05 §4].
- **Projeção:** distinguir mês atual e meses afetados por parcelas; não prometer saldo futuro garantido quando há valores incertos ou faltantes.
- **Qualidade de prova:** `Pago = true` sem data confiável **não demonstra** pagamento antes do vencimento. Ausência de compra na planilha **não demonstra**, por si só, adesão ao conselho do Caio [F01 Apêndice A; F03 §2].

## 5.3. Proibições de inferência financeira

- O registro de um gasto de passagem/hotel não prova que uma viagem aconteceu; eventos de experiência requerem confirmação expressa ou evidência apropriada [F01 §5].
- Reuniões com histórico zero, um, dois ou muitos meses só falam do histórico presente. **Dois meses** referem-se ao histórico inicial informado pelo criador, não a um requisito universal [F07 P05/C08].
- Reprocessar, corrigir ou reconciliar um lançamento **não é nova ação econômica** só porque a planilha mudou novamente [F03 §2; F06 C02].
- Falta de informação produz estado de **incerteza**, não fato, punição nem análise fabricada.

# 6. Consulta financeira de Caio

## 6.1. Entrada e função

**BASE [F01 Apêndice A; F07 P02].** O usuário informa item, valor, pagamento à vista/parcelado, parcelas, juros e descontos. A IA pode transformar linguagem livre em campos revisáveis, mas é o motor determinístico que consulta dados ao Saldanha, projeta compromissos e retorna **verde / amarelo / vermelho**, evidências e alternativas. Caio é a referência educativa sobre compras; o atendimento por **ligação de voz** integra a direção aprovada do Capítulo 07, com fluxo técnico ainda a detalhar.

## 6.2. Ordem aprovada do veredito

| Etapa | Restrição | Se violada |
|---|---|---|
| 1 | Nenhum mês afetado fecha abaixo do colchão de **R$ 1.000** | Vermelho; indicar quando a compra passaria a caber quando houver dado suficiente |
| 2 | Soma das parcelas comprometidas, com a nova, não ultrapassa **15% da renda** do mês | Amarelo; mostrar quando libera capacidade |
| 3 | Consumo imediato (delivery, restaurante, lazer de um dia) **não é parcelado** | À vista se couber; caso contrário, vermelho |
| 4 | Compras parceladas **com juros** não são aprovadas | Recomendar à vista se couber ou esperar |
| 5 | Limite de **10 parcelas**, nunca acima da vida útil do bem | Amarelo; sugerir prazo permitido |

**BASE:** a primeira restrição reprovada determina a cor, preservada a semântica particular das regras de consumo imediato e juros. Após a validação, desconto à vista que cabe favorece à vista; sem juros e sem desconto, avaliar o maior prazo permitido mantendo liquidez. O prazo de uma meta existente é informado, **não se torna veto automático** [F01 Apêndice A].

**Ciclo dos cartões da base:** Nubank fecha dia 4 ou 5 e vence dia 11; Digio fecha dia 23 ou 24 e vence dia 25. Em dias de fechamento ambíguos, escolher a fatura mais próxima por prudência. Essas datas são parâmetros associados aos cartões da fonte e precisam de verificação se suas condições mudarem [F01 Apêndice A].

**PROPOSTA de resposta técnica:** `{status, regra_determinante, premissas, meses_afetados, dados_insuficientes, alternativas}`. Não exibir um “verde” definitivo com base em renda, fatura ou parcela desconhecida.

# 7. Calendário, rotinas e reuniões

## 7.1. Tempo real e visita

**APROVADO [F07 P01–P04, P09].** O calendário do escritório acompanha o tempo real, enquanto a narrativa pode usar cenas e transições contextualizadas. O espaço pode ficar vazio de madrugada. Atividades diárias são facultativas; a ausência de visita não destrói conquistas, não gera punição arbitrária nem impede o acesso posterior a acontecimentos importantes.

**BASE [F01 Apêndice A].** Atividades: atualizar planilha, registrar pagamento, confirmar categoria ambígua, responder pílula educativa, consultar Caio, interagir com Flora e Lupin. Reunião de segunda apresenta análise/prioridades quando aplicável. “Planilha viva” é sequência **semanal**, com proposta-base de **uma semana congelável por mês**, cuja mecânica operacional ainda deve ser detalhada.

## 7.2. Reunião mensal do dia 6

**APROVADO [F01 §16A; F05 §4; F07 §3].** No primeiro acesso **no dia 6 ou depois**, para a competência anterior ainda não tratada, Saldanha convoca o jogador.

1. **Primeira convocação:** aceitar agora ou **adiar para a próxima visita**.
2. **Visita seguinte após adiar:** a reunião é apresentada obrigatoriamente; não se oferece novo adiamento pela mesma regra. Ferramentas financeiras de uso emergencial permanecem acessíveis.
3. **Conferência incompleta:** ocorre reunião **de pendências**, que mostra apenas o verificável; nenhum selo “FECHADO” é concedido sem efetiva conciliação.
4. **Reunião efetivamente concluída:** registrar competência, resultado, fatos validados, escolhas narrativas e recompensas elegíveis **uma única vez**.
5. **Primeira reunião:** introdutória, retrospectiva, usando até os **dois meses** de conciliação inicialmente disponíveis **quando de fato existirem**. Nenhum mês histórico vira automaticamente “fechado no jogo”. Outros usuários podem ter mais, menos ou nenhum mês.
6. **Da segunda em diante:** narrativa progressiva com relatórios, reservas, gastos, decisões e personagens pertinentes; nenhuma cena opcional pode bloquear o rito.

**Papéis:** Vivi acolhe se disponível, Saldanha apresenta números e conduz, Caio explica e participa segundo sua especialidade; Gabriel comparece **apenas com gatilho real pertinente**. Otto arquiva separadamente fatos e memórias [F01 §16A].

## 7.3. Ausência longa e reuniões acumuladas

**APROVADO [F07 C06].** Após múltiplas competências pendentes, Saldanha **pode conduzir uma apresentação consolidada**, preservando análises e resultados **separáveis por mês**. Consolidação não apaga obrigações nem mistura fatos de meses distintos. A cronologia, participação da equipe e tratamento de períodos sem dados são preservados.

**PENDENTE:** a quantidade de meses necessária para consolidar, o fluxo de retomada, a ordenação dos períodos e a validação individual de cada fechamento. Não implementar “resolver todos os meses com um único carimbo” por presunção.

## 7.4. Educação nas reuniões

**APROVADO [F08 P08/C04].** Explicações essenciais fazem parte da reunião sem se converter em testes obrigatórios extras. Desafios e simulações complementares podem ficar disponíveis para depois, sem impedir o encerramento do rito financeiro quando há dados conciliados. Educação não altera a convocação do dia 6 nem as regras de reunião acumulada.

# 8. Economia virtual

## 8.1. Princípios e saldo

**APROVADO [F03 §§1–3].** Moedas são virtuais, obtidas de **ações reais verificáveis**. Não são compradas por dinheiro real, não expiram, não possuem teto máximo de saldo e não existe **teto diário geral de emissão**. Há limitações **por ação**. O crédito inicial é de **100 moedas, uma única vez** por perfil/economia.

## 8.2. Tabela completa de premiação aprovada

| Ação válida | Moedas | Janela e regra |
|---|---:|---|
| Atualizar a planilha | **5** | Alteração financeira real, não revertida, distinta de fato premiado; até 1/dia |
| Registrar pagamento | **10** | Um ou vários pagamentos válidos, **10 no total por dia** |
| Confirmar categoria | **5** | Pelo menos uma pendência real de categorização; até 1/dia |
| Acertar pílula financeira | **5** | Resposta correta validada; até 1/dia |
| Consultar Caio | **10** | Primeira consulta completa com veredito; até 1/dia, qualquer cor |
| Concluir prioridade semanal | **25** | Conclusão comprovada, até 1/semana |
| Fechamento mensal com Saldanha | **50** | Conciliação efetiva, até 1/competência |
| Conquista financeira | **100** | Primeira concessão de marco/conquista elegível identificável |

**APROVADO [F03 §2]:** a virada das recompensas diárias usa `America/Sao_Paulo`. O fechamento usa **competência**, mesmo quando ocorre em data posterior ao dia 6. Repetir, desfazer/reaplicar, recarregar a página ou sincronizar novamente não gera crédito adicional.

**Exceção de duplicidade:** quando um mesmo fato gera “atualizar planilha” e “registrar pagamento” como ações meramente consequentes, não se concedem ambos automaticamente pelo **mesmo evento**. Em contrapartida, uma **conquista distinta** e a ação que a originou podem ser recompensadas independentemente se forem eventos elegíveis e identificados de forma própria [F03 §2; F06 C02].

## 8.3. Preços, carteira e balanceamento

Faixas **de referência**, não SKUs finais, [F03 §3]: decorações pequenas **40–100**; brinquedos/camas/acessórios dos cães **80–180**; móveis/roupas **150–350**; cosméticos especiais **500–1.000** moedas. Uma projeção de aproximadamente 500 moedas por mês na fonte é **somente cenário ilustrativo**, não renda garantida. É necessário simular pelo menos três meses antes de ajustar preços, sempre preservando a regra de recompensas aprovada.

**Saldo virtual:** `100 + recompensas válidas + reembolsos válidos − compras`, nunca negativo. Cada débito/crédito precisa de identificador estável, período quando aplicável e trilha auditável. Regras finais de estorno administrativo por correção financeira permanecem pendentes [F03 §§7–9; F06 C01].

# 9. Loja, inventário, roupas, coleções e decoração

## 9.1. Loja integrada

**APROVADO [F03 §4; F04 04.1–04.4].** A loja é catálogo digital acessível pelo escritório; estoque da loja **ilimitado**; compras podem conter **múltiplas unidades do mesmo item**. Itens adquiridos viram **instâncias individuais** no inventário. Catálogo básico inicial, novos produtos e coleções desbloqueados por requisitos de progresso; desbloquear compra **não** significa receber grátis.

**Raridades:** **Comum, Incomum, Raro, Épico, Lendário**. Indicam exclusividade/condição de desbloqueio, nunca capacidade de influenciar finanças. Estilos podem ser combinados; exemplos de estilo são ilustrações de direção visual, não catálogo aprovado [F04 04.3–04.4]. Não existem caixas-surpresa pagas [F04 §1].

## 9.2. Compra e revenda

- **Compras comerciais:** saldo suficiente, subtrair o preço **efetivamente pago** e entregar a unidade no **mesmo ato transacional**; quantidades podem ser maiores que um [F03 §4].
- **Revenda comercial elegível:** devolver **100% do preço pago por aquela unidade**, não o preço atual do catálogo; remover a unidade do cômodo/inventário na mesma operação [F03 §4; F04 §3].
- **Roupas e acessórios vestíveis:** **nunca revendáveis**, mesmo fora de uso, e não devem mostrar botão de venda [F04 04.10]. Jogador pode equipar; funcionários preservam a própria identidade e **decidem autonomamente se e quando vestir** peças adquiridas para eles [F04 04.6].
- **Construções/salas adquiridas:** propriedade permanente **não revendável**, não há devolução do custo de construção. Salas podem ser armazenadas/restauradas gratuitamente; **acabamentos comerciais** podem seguir revenda integral quando elegíveis [F05 C01].
- **Objetos concedidos diretamente por conquistas:** guardáveis, expostos e reposicionáveis, **não vendáveis, não trocáveis e não conversíveis em moedas** [F06 C04].
- **Móvel especial grátis por coleção:** entregue uma vez por coleção completa; F04 deixava sua política de revenda em aberto e F06 protege objetos dados diretamente por conquistas. **Aplicação ao prêmio de coleção exige classificar formalmente se integra o inventário comemorativo protegido**, sem inventar valor de revenda [F04 04.5/§3; F06 C04].

## 9.3. Coleções

**APROVADO [F04 04.5 e 04.8].** Completar uma coleção requer ter adquirido **ao menos uma vez cada item distinto exigido**. A conclusão registrada e sua conquista permanecem **permanentes**, inclusive quando unidades compradas são posteriormente revendidas. Conclusão concede **uma única vez** um móvel interativo exclusivo **gratuito**. Recomprar itens não rende novo móvel; interações do prêmio são cosméticas e não geram moedas ou vantagens financeiras.

Catálogo completo de coleções, tamanho, requisitos, mobiliário entregue e classificação definitiva de cada prêmio **pendentes**. **Exemplos** de cadeira de massagem, tapete de cachorro e máquina de pipoca não constituem o catálogo final [F04 §2].

## 9.4. Decoração ao vivo e móveis

**APROVADO [F03 §5; F04 04.7, 04.9, 04.11; F05 C02].** Decoração acontece **sem pausar** os personagens. Todos os móveis, inclusive funcionais, podem ser movidos **somente se continuarem acessíveis/utilizáveis**: portas, circulação, balcões, mesas de reunião, malote, quadro e pontos de interação não podem ficar obstruídos. Uma movimentação inválida é recusada preservando a posição anterior.

Móvel ocupado: personagem termina/encerra a interação, levanta/afasta-se naturalmente e libera o item; a simulação global não congela. Móveis especiais são usados **organicamente**, influenciados por personalidade, proximidade, contexto e disponibilidade, **sem frequência fixa ou obrigação de uso**. O item precisa estar colocado e acessível. Layouts podem ser salvos/restaurados gradualmente, após verificação de posse dos itens, rotas, colisões e ocupação; jamais duplicam unidades [F05 P06/C02].

## 9.5. Inventários especiais

**APROVADO [F06 C04/C09–C10].** Inventário comemorativo é **ilimitado em lembranças armazenadas**, independentemente da área de exposição. Não substituir a decoração existente por prêmio sem o jogador pedir. Quantidade de cópias de uma mesma lembrança ainda está indefinida. Recompensas de níveis evolutivos, quando elegíveis, são concedidas **uma única vez por nível** e os objetos de níveis anteriores são preservados.

---
# 10. Progressão, salas, XP e expansão

## 10.1. Dois eixos e permanência

**APROVADO [F05 §§1–2].** O desenvolvimento combina:

- **XP e nível geral:** participação legítima, ações financeiras comprovadas, bônus de marcos elegíveis e algumas missões pontuais. Comprar item cosmético **não dá XP** por si só. Repetição, recriação e edição artificial não criam XP infinito.
- **Marcos financeiros reais:** reserva, pagamentos, metas ou hábitos validados, independentes do volume de XP. Situação financeira atual pode mudar; a memória do que foi realmente alcançado permanece.

**Não há** recurso obrigatório adicional chamado “pontos de expansão”. Níveis habilitam ambientes comuns; salas especiais podem exigir marco, missão ou acontecimento narrativo; entre ambientes **já elegíveis** o jogador escolhe a ordem de expansão. Funções essenciais não exigem pagamento nem construção opcional. **Salas essenciais são gratuitas após desbloqueio**; salas/espaços opcionais e melhorias cosméticas **podem custar moedas**; preços individuais permanecem pendentes [F05 P04–P05].

## 10.2. Progressão de longo prazo

**APROVADO [F05 P08–P10].** Ambientes podem ser funcionais, sociais ou especiais, com novas funções e diálogos evolutivos. A jornada apresenta **fundação, crescimento, maturidade e continuidade**, sem datas fixas para as fases, sem reset obrigatório e sem crescimento físico infinito. História principal e fechamento do dia 6 podem ser apresentados mesmo sem sala opcional. Eventos dependentes de uma sala guardada aguardam sua restauração, enquanto os eventos já vividos e as memórias não desaparecem [F05 C05].

## 10.3. Marcos originais de ambientes

| Marco documentado na base | Referência de desbloqueio | Status |
|---|---|---|
| Disciplina: três meses com pagamentos em dia confirmados | Tesouraria / Tesoureiro | BASE mantida; depende de prova de pontualidade |
| Hábito: três meses com poupança registrada | Sala de Metas / Planejador | BASE mantida |
| Delivery dentro do teto por dois meses válidos | Auditoria / Auditor de cortes | BASE mantida |
| Reserva de **1 mês** de saídas | Ampliação / sede maior | BASE mantida |
| Reserva de **3 meses** de saídas | Andar inteiro | BASE mantida |
| Reserva de **6 meses** de saídas | Cobertura/terraço | BASE mantida |

**Atenção de compatibilidade [F01 §3.3; F05 §4]:** a Bíblia inicialmente propõe contratação direta por créditos virtuais e promoções alternativas. F05 afirma que salas essenciais são gratuitas após desbloqueio e que marcos financeiros não são comprados. Assim, **não transformar automaticamente contratações pagas em requisito de funções essenciais nem substituir os marcos por moedas**. A contratação antecipada de presença narrativa/promoção precisa de definição própria.

## 10.4. Salvar/restaurar e circulação

**APROVADO [F05 P06/C01–C02/C06].** Layouts podem ser salvos e restaurados; móveis ocupados são liberados organicamente; não há duplicação de itens. Construções compradas são permanentes e não revendáveis, mas podem ser **ocultadas/armazenadas** e retornam sem pagar novamente. Ao armazenar uma sala, validar portas, ligações e dependências; oferecer reconexão, armazenamento conjunto de dependentes ou cancelamento e **pedir confirmação** para mudança estrutural relevante. Nunca prender personagens nem tornar inacessível função financeira.

## 10.5. História, recuperação e retroatividade

**APROVADO [F05 C03–C05/C07–C09].** Moedas e XP têm controles separados. Evento legítimo pode contar para ação e missão **distintas** quando as duas elegibilidades são comprovadas. Histórias sazonais importantes permanecem recuperáveis; revê-las não duplica recompensa. Correções financeiras posteriores não retiram salas, XP ou memórias anteriores; próximos desbloqueios usam dados corrigidos.

O histórico inicial do projeto contém **dois meses de conciliação**. Na primeira integração pode haver **reconhecimento único de XP inicial**, com validação e identificador próprio, **sem multiplicar XP por cada transação histórica**. Marcos históricos comprováveis são reconhecidos separadamente. **Valor exato e condições técnicas do bônus ficam pendentes** [F05 C08].

**Arquivo narrativo inteligente [F05 C09].** Eventos simples podem ser recuperados; histórias adaptáveis usam versões compatíveis; histórias que dependem de futuros acontecimentos **esperam sem spoiler**, nunca são inventadas para preencher cronologia.

# 11. Conquistas, reconhecimento e Diário

## 11.1. Como uma conquista é identificada

**APROVADO [F06 P01–P10].** Conquistas têm categorias temáticas, gradação de importância e possíveis níveis evolutivos. Marcos comuns recebem aviso discreto; reconhecimentos relevantes podem gerar reação; grandes marcos têm celebração narrativa. Critérios financeiros e hábitos são **transparentes**, com progresso e requisitos restantes visíveis. Segredos podem existir **somente para exploração e histórias opcionais**; nenhum agente, sala, escritório ou função principal fica travado por segredo.

A conquista possui identificação, validação, data/competência conhecida, ocorrências, sequência atual e melhor sequência. **Detectar** no decorrer do mês não é o mesmo que **confirmar** depois da verificação. Conquista recorrente pode registrar novo episódio válido, **sem premiação nova automática**. Recompensas, quando elegíveis, podem incluir moedas, XP, cosméticos protegidos e narrativa, mas sempre exigem regra específica [F06 P03/P06/P08].

## 11.2. Exemplos documentados na base

| Grupo | Conquista | Regra de referência / limitação |
|---|---|---|
| Mensal | **Em dia** | Todas as saídas no prazo; exige **data confiável**, não apenas campo `Pago` |
| Mensal | **No azul** | Saldo final acima do colchão de R$ 1.000 |
| Mensal | **Guardou** | Valor guardado do mês maior que zero |
| Mensal | **Dentro do teto** | Categoria mensal dentro do respectivo teto |
| Mensal | **Mês redondo** | Combinação das condições mensais previstas na base |
| Sequência | **Hábito** | Três meses seguidos com “Guardou” |
| Sequência | **Disciplina** | Três meses seguidos com “Em dia”, com prova temporal |
| Sequência | **Planilha viva** | Quatro semanas com atualização genuína; possível semana congelada conforme regra-base |
| Marco | **Primeira consulta** | Consulta válida ao Caio |
| Marco | **Ouviu o Caio** | Fonte-base tratava ausência de compra como indício; requer prova melhor antes de afirmação categórica |
| Marco | **Reserva de 1 mês** | Saldo de reserva cobre um mês de saídas reconhecidas |
| Marco | **Fim de parcela longa** | Quitação de compra parcelada em dez vezes ou mais |

**Importante:** F06 §5 chama essa lista de **referências a conferir**, e não de catálogo final com todos os requisitos. Não inventar data, valor ou histórico para um marco só porque há campo sem confirmação.

## 11.3. Correções, recorrência e reversibilidade

**APROVADO [F06 C01–C03/C07/C10].** Ao corrigir a planilha:

- Manter a **memória do reconhecimento histórico**, distinguindo o que foi corrigido do que continua comprovado.
- **Recalcular cronologicamente** indicadores, sequências e melhores sequências válidas. Guardar referência do recorde anteriormente mostrado sem tratá-lo como recorde atual legítimo.
- **Não revogar automaticamente** conquistas, recompensas já entregues, XP, ambientes e personagens previamente desbloqueados.
- Para **novos** desbloqueios e indicadores, usar a informação válida corrigida.
- Premiar cada nível evolutivo elegível **apenas uma vez**; voltar ao mesmo nível não remultiplica a recompensa.

Retroatividade anterior ao início do jogo pode gerar reconhecimento e **celebração contextualizada no presente**, distinguindo **data do fato** e **data da comemoração**. Não encenar falso acontecimento passado nem conceder XP/moedas retroativos não previstos [F06 C05].

## 11.4. Celebração e exposição

**APROVADO [F06 C04/C06/C08–C09].** Celebrações simultâneas podem ser **agrupadas por prioridade**, preservando cada prêmio e conquista, e grandes marcos ficam aptos a cenas especiais. Celebrações não assistidas permanecem em fila, conciliadas com o dia 6. Galeria digital completa; exposição física de lembranças elegíveis **voluntária**; retirá-las da exposição não altera a conquista. Lembranças de conquistas não são moeda e não podem ser vendidas/trocadas. Armazenamento comemorativo ilimitado; capacidade visual depende da área disponível.

## 11.5. Diário permanente — Otto

**APROVADO [F01 §12; F06 P09–P10; F07 P10].** O Diário combina marcos verificáveis, datas disponíveis, escolhas, episódios vistos, conquistas, fotografias permitidas, correções e narrativas ficcionais identificadas. Registros individuais não vazam automaticamente para memória coletiva. O nome Otto pode surgir desde o primeiro dia, mas sua estreia em cena física exige episódio próprio [F01 §12].

# 12. Eventos, ausências, temporadas e privacidade narrativa

## 12.1. Tipos e ocorrência

**APROVADO [F07 P06–P10].** Há eventos ambientais, interativos e contextuais com **aleatoriedade controlada**, relações orgânicas e continuidade. Datas comemorativas alteram temporariamente clima do escritório, permitem histórias ou objetos elegíveis e retornam em futuras temporadas; personagens **terão aniversários**, mas **nenhuma data foi aprovada**. Os aniversários podem ter rituais e eventos aleatórios pré-programados, ainda sem catálogo final.

**APROVADO [F05 C04/C09; F07 C05].** Ambientações temporárias seguem calendário, mas eventos importantes marcados como recuperáveis podem ser revistos/retomados de modo contextual, mesmo após a data. Histórias não assistidas não podem criar recompensas por duplicidade. Nem todo detalhe ambiental precisa ser recuperável; o sistema distingue **recuperável / resumível / puramente passageiro** com critérios futuros.

## 12.2. Exceções de rotina

- Escritório vazio na madrugada não anula reunião obrigatória; presença excepcional, cena contextual ou remota pode representar situações especiais, com modalidade por caso ainda pendente [F07 C01].
- Vivi entrega mensagem de retorno pessoalmente **se presente** ou digitalmente **se ausente**; encontro posterior pode reconhecer retorno sem duplicar aviso [F07 C02].
- Saldanha pode aparecer inesperadamente em levantamento financeiro pertinente, com variedade e sem interromper tarefas essenciais; **frequência e intervalo** são pendentes [F07 C03].
- Após ausência, o usuário pode encontrar resumo, episódios importantes recuperáveis e reuniões ainda pendentes. Ausência não gera perda artificial de propriedade ou de histórias significativas [F07 P09/C05–C06].

## 12.3. Recompensa de eventos

**APROVADO [F07 C04].** Parte dos eventos é só narrativa; alguns podem recompensar ações válidas com limite por ação; estreias podem receber recompensa única **se a elegibilidade estiver definida**. A regra de 100 moedas de conquista financeira **não autoriza** atribuir esse valor a qualquer evento. Não existe teto global diário de moedas; repetir o mesmo evento remunerado **não** cria créditos diários ilimitados [F03 §2; F07 §4].

## 12.4. Memória e acesso

**APROVADO [F07 C07].** Acesso a fatos é **contextual e proporcional à função**. Atendimento particular de Caio permanece reservado, exceto compartilhamento legítimo e autorizado; lembrança coletiva não dá a todos acesso a conversas privadas ou linha por linha da planilha. Uma reunião revela somente informações pertinentes aos participantes autorizados. Matriz de permissão/consentimento, retenção e revogação **não está tecnicamente fechada** [F07 §5].

# 13. Educação financeira

## 13.1. Princípios aprovados [F08 P01–P10]

| Domínio | Solução aprovada | Limite/documentação ainda aberta |
|---|---|---|
| Formatos | Diálogos, desafios, simulações e contexto real autorizado | Currículo, temas e sequência |
| Orientador | **Caio** como referência; outros participam por função | Vivi não se torna consultora |
| Desbloqueio | Combina XP/nível, narrativa, competências e fatos financeiros | Gatilhos específicos; conteúdo geral não deve exigir planilha |
| Desafios | Perguntas, narrativa, hipóteses e prática | Tentativas, conclusão, identidade do desafio |
| Simulação | Livre, narrativa ou com dados autorizados | Fórmulas, catálogo, salvamento e avisos |
| Revisão | Biblioteca por tema, Diário e explicações reapresentáveis | Busca/favoritos não aprovados como obrigatórios |
| Progresso cognitivo | Evolução por tema, separada de riqueza/XP/moedas | Indicadores e escala |
| Reuniões | Explicações essenciais e atividades complementares adiáveis | Separação exata por atividade |
| Contextos difíceis | Linguagem respeitosa, exemplos e alternativas | Critério de detecção e intervenção |
| Reconhecimento | Conquistas, narrativa, cosméticos e eventuais moedas/XP elegíveis | Valores e elegibilidade não aprovados |

## 13.2. Soluções dos oito conflitos [F08 C01–C08]

1. **Atividade inédita versus repetição:** primeira conclusão válida pode ser remunerada se houver regra; estudar a mesma atividade novamente não duplica prêmio. Outra atividade só conta separadamente com identidade real e validação própria.
2. **Privacidade:** dados específicos só quando necessários e autorizados; espaços coletivos usam agregado, desidentificado ou cenário fictício. Nenhum personagem ganha permissão geral por oferecer ensino.
3. **Progressão educativa versus narrativa:** temas gerais não exigem escritório evoluído; desafios especializados podem exigir pré-requisito; reconhecer depois um aprendizado não gera XP retroativo automaticamente nem substitui marco financeiro real.
4. **Ensino versus reunião obrigatória:** explicação essencial integra o rito; exercícios opcionais podem ser feitos depois. Reuniões acumuladas continuam sujeitas à própria lógica.
5. **Simulações persistentes versus planilha real:** cenários temporários ou salvos **não alteram** registros bancários, saldos, conquistas financeiras ou desbloqueios por fatos reais.
6. **Correção de dados versus Diário educativo:** análises antigas podem ser assinaladas como desatualizadas; reavaliação usa dados corrigidos, sem duplicar recompensa ou apagar conquista histórica válida.
7. **Avaliação justa:** distinguir participação, conhecimento demonstrado e uso prático; renda/patrimônio não são medidores de competência.
8. **Reconhecimento versus loja:** conquistas educativas podem ser permanentes, liberar item à compra e eventualmente render cosmético especial; não conceder automaticamente itens/recompensas não aprovados. Conquistas de coleção anteriores permanecem permanentes.

## 13.3. Pílula e simuladores

**BASE/F03 [F01 Apêndice A; F03 §2].** Pílula cotidiana curta, acompanhada de pergunta. **Acerto genuíno validado** pode conceder **5 moedas por dia**, segundo a tabela aprovada. **Não significa** que qualquer repetição ou qualquer modalidade educativa dá 5 moedas. O domínio financeiro real e a simulação virtual ficam tecnicamente separados [F08 P04–P05/C05].

# 14. Missões longas e sistema de estagiários

**Contexto da conversa do projeto, não especificação dos sete arquivos.** O usuário propôs missões que ocupam aproximadamente um mês: candidatos variáveis fazem entrevistas, o jogador escolhe quem acredita ser melhor e o estagiário selecionado altera temporariamente as relações e rotinas do escritório, com eventos recorrentes e arco narrativo durante sua permanência, podendo existir recompensa de conclusão. O usuário selecionou **modalidade B** para desenvolver esse sistema.

**CONFIRMADO:** intenção de estágios temporários mensais, entrevistas, decisão do jogador, arco e impacto social temporário. **NÃO RECUPERADO:** enunciado integral da alternativa B e suas possíveis exigências adicionais. Portanto **não atribuir** números de candidatos, duração exata em dias, critérios de seleção, probabilidades, cargos, acesso a dados, calendário automático, consequências ou recompensas.

**Invariantes herdados (não decidem a modalidade):** estagiários não podem alterar planilha/consultoria por livre interpretação; consultas privadas não são compartilhadas sem permissão; eventos não geram moedas/XP sem elegibilidade; ausência não apaga arcos recuperáveis; personagens permanentes preservam seu papel; jogador escolhe quando houver escolha real. **Bloqueio de implementação STG-B-01:** recuperar a descrição da modalidade B ou submeter seu conteúdo a decisão futura, sem refazer os capítulos já fechados.

# 15. IA, acessibilidade e proteção de dados

## 15.1. IA: comunicação, não autoridade

**BASE [F01 §§5, 20 e Apêndice A].** IA pode analisar texto livre e devolver campos revisáveis, explicar vereditos já calculados, sugerir categorização, redigir relatórios sobre valores autorizados e variar diálogos/pílulas. **Não pode** calcular saldo como fonte da verdade, conceder moedas/XP, entregar conquista, alterar desbloqueio, determinar privacidade, afirmar fato financeiro sem evidência ou aprovar compra em lugar do motor. Se indisponível, usar mensagens predefinidas sem bloquear o jogo. Referências históricas a fornecedor de IA não constituem decisão obrigatória de contratação.

## 15.2. Privacidade contextual

**APROVADO em princípio [F07 C07; F08 C02/C06].** Consultas reservadas são confidenciais; memória de personagem só contém fatos a que teve acesso legítimo; reunião só compartilha conteúdo autorizado; bibliotecas e diários educativos respeitam os mesmos controles; cenários fictícios e dados reais devem ser distinguíveis. Dados enviados a serviços externos devem ser **mínimos e proporcionais**. Fotos e redes sociais na história de Vivi são elementos **internos ficcionais**, não publicação automática de dados pessoais [F01 §9A].

**PENDENTE de engenharia e decisão:** autenticação, modelo detalhado de permissões por personagem, conceder/revogar compartilhamento, retenção, exclusão, anonimização, logs e políticas de IA. Antes da exposição em domínio público, a proteção de dados e o login são requisitos da documentação-base.

## 15.3. Acessibilidade e feedback (PROPOSTA técnica)

Contraste, navegação por teclado, texto equivalente a cores, estados de processamento, legendas de voz, opção de ler falas, controles de velocidade e desativação de efeitos repetitivos. Não confundir esses critérios recomendados com aprovação prévia de um pacote técnico de acessibilidade.

---
# 16. Contratos técnicos e critérios de aceite

> **Status desta seção:** **PROPOSTAS DE IMPLEMENTAÇÃO** derivadas das regras aprovadas; nomes de tabelas, APIs, eventos, chaves e filas ainda não foram aprovados como decisões de produto. Os invariantes de comportamento são obrigatórios onde sua fonte é marcada APROVADO/BASE.

## 16.1. Domínios e fonte da verdade

| Domínio técnico sugerido | Origem confiável | Proibições/invariantes |
|---|---|---|
| Dados financeiros | Planilha validada e sincronizações autorizadas | Não escrever dado fictício; não exibir conciliação sem prova |
| Consultoria | Motor de regras + projeções | IA não muda cor, limite ou parcela |
| Economia virtual | Carteira + extrato imutável de eventos | Sem saldo negativo, sem duplicar, sem teto geral inventado |
| Inventário | Instâncias individuais + preço histórico por unidade | Sem revenda de roupa/lembrança protegida, sem item duplicado |
| XP e níveis | Eventos de progresso validados | Sem XP por compras cosméticas ou reimportação |
| Conquistas e coleção | Requisitos + evidências + histórico de correções | Não apagar reconhecimento histórico nem repetição remunerada |
| Reuniões | Competência + estado de convocação + validação | Não fechar mês incompleto ou liberar novo adiamento indevido |
| Narrativa/Diário | Eventos verdadeiros e cenas vistas como objetos distintos | Não narrar fato pessoal jamais confirmado |
| Educação | Atividades identificadas e simulações isoladas | Simulação não altera finanças reais |
| Privacidade | Permissões explícitas/contextuais | Memória de personagem não é autorização irrestrita |

## 16.2. Modelo lógico sugerido

- `FinancialSource(id, owner_id, source_type, permissions, last_checked_at, integrity_status)`.
- `FinancialEntry(id, source_id, competence, effective_date?, due_date?, paid_mark, paid_at?, amount, category, share_ratio, revision)`.
- `Reconciliation(id, competence, source_revision, status, verified_at?, discrepancies)`.
- `FinancialSnapshot(id, competence, revision, values, missing_fields, calculated_at)`.
- `PurchaseConsultation(id, source_revision, inputs, outcome, decisive_rule, alternatives, timestamp)`.
- `RewardGrant(id, event_key, action_kind, period_key, amount, eligibility_version, origin_revision)`.
- `VirtualWallet(owner_id, balance, journal)`.
- `ShopProduct(sku, type, unlock_rule_id, rarity, sale_policy, status)`.
- `OwnedUnit(unit_id, sku, acquisition_kind, paid_price?, room_id?, position?, is_worn)`.
- `CollectionCompletion(id, collection_id, first_valid_at, reward_grant_id, corrected_context?)`.
- `RoomOwnership(id, kind, unlock_origin, purchased_price?, visibility, layout_ids)`.
- `Achievement(id, level?, first_recognized_at, valid_occurrences, corrected_history, unlocks)`.
- `Meeting(id, competence, eligibility, invited_at, deferred_once, status, reconciliation_id?, viewed_scene_ids)`.
- `StoryMemory(id, kind:factual|fictional, visibility_scope, source_event_id?, occurred_at?, shown_at?, version, state)`.
- `EducationAttempt(id, activity_identity, scenario_mode, result, reward_key?, snapshot_revision?)`.

**Dados insuficientes:** datas não presentes permanecem `null`/“desconhecido”; não usar hora de importação como data de pagamento, nem horário de cena como data do fato. Campos como `paid_at` só existem se a fonte realmente os fornece.

## 16.3. Transações e idempotência

**Recompensa de ação [F03/F06]:** obter evento validado → identificar tipo + janela + identidade econômica do fato → verificar se já premiado → registrar `RewardGrant` e crédito juntos. Recompensa de **conquista distinta** pode ter chave de concessão própria; a mera consequência de atualizar planilha ao pagar uma conta não constitui segunda ação premiável. Período diário usa São Paulo; semanal e competência mensal requerem regras de calendário confirmadas.

**Compra:** verificar saldo e desbloqueio de catálogo → debitar preço total → criar `N` unidades com seus preços individuais → commit conjunto. **Venda:** verificar unidade e política; remover do cenário e propriedade → reembolsar o preço gravado daquela unidade → commit conjunto. Repetir a mesma solicitação não processa duas vezes.

**Correção financeira [F05/F06]:** aplicar nova revisão dos fatos → recalcular indicadores e critérios futuros → **manter acesso a progressão já concedida** → registrar contexto corrigido no Diário → não gerar premiação retroativa ou estorno automático sem regra aprovada.

**Mudança de sala/layout [F04/F05]:** simular colisão e caminhos → pedir confirmação quando houver dependentes → liberar móveis usados com animação orgânica → mover/armazenar sem copiar itens → gravar configuração somente quando válida.

## 16.4. Máquina conceitual de reunião (PROPOSTA)

`não_elegível → convite_disponível → {aceita | adia_uma_vez} → apresentação_obrigatória → {conferência_pendente | concluída_validada}`.

Ao entrar novamente depois do adiamento, o estado conduz à **apresentação obrigatória**, mas não força afirmar fechamento. Se os dados continuam incompletos, o estado passa a **conferência pendente**, com roteiro de lacunas. Reuniões de várias competências preservam identificadores distintos mesmo quando são vistas em sessão consolidada [F01 §16A; F07 C06]. O desenho de transições após várias reuniões acumuladas requer definição separada.

## 16.5. Casos de aceite prioritários

| ID | Cenário | Resultado esperado | Fonte |
|---|---|---|---|
| FIN-01 | Projeção mensal fica abaixo de R$ 1.000 após compra | Caio não emite verde | F01 Apêndice A |
| FIN-02 | Parcelas totais passam de 15% da renda | Proposta parcelada reprova na regra 2 | F01 Apêndice A |
| FIN-03 | Delivery pedido em três parcelas | Não aprovar o parcelamento de consumo imediato | F01 Apêndice A |
| FIN-04 | Compra em onze parcelas | Não aceitar prazo maior que dez | F01 Apêndice A |
| DATA-01 | Cartão recebido, mas divergente | Não exibir envelope como conferido nem mês como fechado | F01 §5 |
| DATA-02 | `Pago` sem timestamp, vencimento passado | Não declarar conquista “Em dia” sem evidência | F01 Apêndice A; F03 |
| ECON-01 | Novo perfil | Crédito inicial **100** uma vez | F03 |
| ECON-02 | Três contas pagas no mesmo dia | **10 moedas totais** por “registrar pagamento” | F03 |
| ECON-03 | Pílula certa duas vezes no mesmo dia | **5 moedas no máximo** pelo tipo de ação | F03 |
| ECON-04 | Consulta completa Caio com veredito vermelho | **10 moedas** na primeira consulta válida do dia | F03 |
| ECON-05 | Prioridade semanal comprovada | Crédito **25** uma vez na semana | F03 |
| ECON-06 | Reunião com competência antiga, conciliada hoje | Crédito **50** uma vez pela competência | F03 |
| ECON-07 | Ação independente e conquista financeira própria | Créditos distintos quando ambas elegíveis; nenhum replay extra | F03; F06 C02 |
| SHOP-01 | Compra duas unidades do mesmo móvel | Debita 2 preços e cria 2 unidades físicas | F03/F04 |
| SHOP-02 | Revenda após mudança de preço da loja | Crédito igual ao preço pago **da unidade** | F03 |
| SHOP-03 | Tentativa de vender qualquer roupa | Recusa sem alterar saldo/guarda-roupa | F04 04.10 |
| SHOP-04 | Completa coleção e revende item comercial da coleção | Conquista e prêmio **não se apagam** | F04 04.8 |
| SHOP-05 | Móvel ocupado é movido | Reação orgânica; sem pausar simulação; validar acesso | F04 04.9 |
| ROOM-01 | Sala com dependentes é armazenada | Validar ligações, oferecer alternativas e confirmação | F05 C06 |
| ROOM-02 | Salva e restaura layout contendo item vendido | Não duplicar; sinalizar configuração não executável | F05 C02 |
| XP-01 | Reimporta conciliações históricas | Não multiplica XP inicial por lançamento | F05 C08 |
| ACH-01 | Correção altera sequência | Recalcular recorde válido; manter memória do recorde anterior corrigido | F06 C07 |
| ACH-02 | Correção invalida marco que já liberou sala | Sala permanece disponível; critérios futuros usam dado corrigido | F06 C03 |
| ACH-03 | Ganha prêmio comemorativo sem local de exposição | Vai para inventário protegido ilimitado | F06 C04/C09 |
| MEET-01 | Primeira visita a partir do dia 6 | Saldanha convida, permite um adiamento | F01 §16A |
| MEET-02 | Jogador adiou e volta | Reunião apresentada, sem segundo adiamento | F01 §16A |
| MEET-03 | Planilha do período sem conciliação | Reunião de pendências, **sem** selo fechado ou prêmio de fechamento | F01 §16A; F03 |
| MEET-04 | Três meses atrasados e apresentados juntos | Resultados permanecem separados por mês; operacionalizar segundo regra futura | F07 C06 |
| EVENT-01 | Aniversário recuperável não foi visto na data | Ritual pode ser retomado contextualmente, não a decoração temporária fora da época | F07 C05 |
| EVENT-02 | Visita noturna sem Vivi | Mensagem de retorno por canal digital/contextual | F07 C02 |
| PRIV-01 | Personagem que não participou de consulta Caio | Não pode relatar dados privados sem permissão | F07 C07 |
| EDU-01 | Usuário repete desafio já premiado | Aprendizado permitido, nova recompensa não emitida | F08 C01 |
| EDU-02 | Cenário simulado com economia maior | Planilha e conquistas de fatos reais não mudam | F08 C05 |
| EDU-03 | Patrimônio menor, respostas educativas corretas | Não rebaixar competência por patrimônio | F08 C07 |
| AI-01 | Provedor de IA indisponível | Motor financeiro e ações reais seguem operando | F01 §20 |

**Aceite ainda não executável de forma definitiva:** classificação/revenda de prêmios de coleção, número de cópias de lembranças, fórmulas/ritmos de XP, permissão granular de Vivi, gatilhos de aniversários, agrupamento exato de reuniões atrasadas, identidade técnica de desafios novos, cronograma de estágios B.

# 17. Backlog e pendências que exigem decisão

## 17.1. Itens bloqueadores de especificação (não reabrir decisões já tomadas)

| ID | Prioridade | Tema | O que falta definir | Restrições já aprovadas |
|---|---|---|---|---|
| DATA-01 | Alta | Esquema real e auditoria da planilha | Amostra anonimizada, significado de datas, semântica de `Pago`, precisão das atualizações e conciliações | Não inventar pontualidade ou transações |
| RES-01 | Alta | Retiradas de reserva | Como registrar, recalcular e comprovar saques/retiradas | Manter marcos históricos e não regredir escritório |
| SEC-01 | Alta | Privacidade | Quem pode ver o quê, consentimentos, revogação, armazenamento e acesso a histórico | Consultas privadas e permissões contextuais |
| MEET-01 | Alta | Reunião incompleta | Retorno para concluir pendências e prova de fechamento | Convocação dia 6, um adiamento, sem falso “FECHADO” |
| MEET-02 | Alta | Reuniões acumuladas | Critérios de agregação, apresentação e histórico de meses | Competências individualizadas e obrigatoriedade preservada |
| STG-B-01 | Alta | Estagiários | Texto da modalidade B e parâmetros efetivos | Não inventar duração, candidatos ou recompensas |
| XP-01 | Alta | Curva de XP | Tabela por ação, limites, níveis e bônus único inicial | Emissão independente das moedas, anti-duplicação |
| ACH-01 | Alta | Prova de conquista | Catálogo final, estados, datas e validação de “Em dia”, “Ouviu o Caio” | Transparência, sem inferências falsas |
| SHOP-01 | Média | Prêmio de coleção | Classificação do item gratuito para política de revenda/proteção e quantidade de cópias | Concessão única e conclusão permanente |
| SHOP-02 | Média | Catálogo e valores | SKUs, requisitos, preços por raridade, conjunto das coleções, peças de roupas | Raridades fixadas; referência de preços não é catálogo |
| ROOM-01 | Média | Arquitetura de espaços | Planta 12 × 10 com Vivi e posto técnico, hub/dioramas/andares, salas essenciais e opcionais | Sede permanente, serviços essenciais livres, acessibilidade |
| ROOM-02 | Média | Layouts | Quantidade de layouts, regras de restauração sem itens e prioridades de animação | Sem duplicar/proibir acesso, comportamento orgânico |
| EVENT-01 | Média | Temporadas | Datas de aniversários, eventos pré-programados, probabilidades e janelas | Eventos importantes recuperáveis |
| EVENT-02 | Média | Personagens | Presença por horário, mensagens de Vivi, surpresa de Saldanha e ligação de voz do Caio | Sem bloquear tarefas, sem aparição indevida |
| NARR-01 | Média | Conteúdo narrativo | Aceite de biografias propostas, futuros nomes, roteiros e ordem de episódios | Fatos financeiros reais e escolha do jogador |
| EDU-01 | Média | Currículo | Temas, desbloqueios, biblioteca, diario educativo, conteúdo inicial | Conteúdo geral sem bloqueio indevido |
| EDU-02 | Média | Simulação e avaliação | Fórmulas, versão de cenários, métricas de conhecimento | Simulações isoladas; renda não mede aprendizagem |
| EDU-03 | Média | Recompensas educativas | Valores elegíveis, catálogo de itens especiais, identidade de desafios | Limites por ação, sem duplicar ou inventar XP |
| HIST-01 | Média | Diário corrigido | Política de versionamento, retenção e marcações de desatualização | Reconhecimento histórico preservado |
| PROD-01 | Média | Infraestrutura | Fornecedor IA/voz, segurança, persistência e custos | Código decide; IA degrada sem bloquear |
| UX-01 | Média | Acessibilidade | Padrões, legendas, leitura por teclado e controles | Conteúdo deve permanecer verificável |

## 17.2. Cortes verticais recomendados (PROPOSTA, não cronograma aprovado)

| Ordem indicativa | Entrega que demonstra valor | Dependência para ativação com dados reais |
|---|---|---|
| 0 | Leitura de planilha de demonstração, auditoria e proteção de acesso | DATA-01 e SEC-01 |
| 1 | Diorama 12 × 10 com Vivi, Caio, Saldanha, Guilherme e cães | ROOM-01 |
| 2 | Livro do Saldanha, sinais visuais e malote sincronizado | Fontes financeiras verificadas |
| 3 | Motor determinístico de consulta ao Caio | Projeção e cartões conferidos |
| 4 | Reunião dia 6, adiamento único e fechamento sem falsos positivos | MEET-01, dados de conciliação |
| 5 | Carteira de 100 moedas, tabela de recompensas e inventário transacional | Critérios de validação por evento |
| 6 | Loja, roupas, coleções e decoração orgânica | SHOP-01/02 e ROOM-02 |
| 7 | XP, marcos, expansão e Diário histórico | XP-01 e ACH-01 |
| 8 | Eventos recuperáveis, reuniões acumuladas, privacidade contextual e ensino híbrido | MEET-02, EVENT-01/02, EDU-01/02/03 |
| 9 | Missões de estágios com entrevistas e arcos | STG-B-01 e catálogo de conteúdo |

## 17.3. Condição de lançamento por funcionalidades

O FinancyApp tem **decisões conceituais consolidadas dos Capítulos 01–08**, mas não está “100% pronto para programar sem perguntas” em todos os sistemas. Recursos marcados com pendências precisam de especificações próprias antes de serem anunciados como fechados. É permitido prototipar com dados sintéticos **identificados como sintéticos**, nunca fingir que demonstrativos correspondem aos dados do jogador.

# 18. Mapa de rastreabilidade, exceções e histórico

## 18.1. Índice de decisões por capítulo

| Capítulo | Escopo documentado | Cobertura de decisões | Status da consolidação |
|---|---|---|---|
| 01–02 | Universo, identidade, elenco, relações, tom, cenas e reunião | Bíblia reunida em F01; elementos marcados como DEFINIDO/PROPOSTA/A VALIDAR | Incorporado com diferenciação explícita de status |
| 03 | Economia | 8 recompensas com valores, preços de referência, loja, inventário e regras monetárias | Incorporado integralmente em regras transversais |
| 04 | Personalização | 11 regras estruturais, 4 conflitos | Incorporado; prêmio de coleção exige classificação comercial |
| 05 | Progressão | 10 perguntas, 9 conflitos | Incorporado; XP, custo e arquitetura fina permanecem pendentes |
| 06 | Conquistas | 10 perguntas, 10 conflitos | Incorporado; histórico e proteção de lembranças preservados |
| 07 | Rotinas | 10 perguntas (9 D, 1 C), 8 conflitos | Incorporado; horários, eventos e agregação de reuniões pendentes |
| 08 | Educação | 10 perguntas D, 8 conflitos D | Incorporado; fórmulas, métricas e catálogo ainda pendentes |
| Transversal | Estagiários | Escolha **B** referenciada na conversa, não documentada nos sete MD | **Pendente de especificação textual** |

## 18.2. Exceções decisivas contra versões antigas

| Antes / regra geral | Atualização aprovada | Origem |
|---|---|---|
| Caio associado à recepção | **Vivi recebe**, Caio faz consultoria em posto próprio/voz | F01 Adendo; F07 P02 |
| Moedas deixadas para depois | Tabela completa: 5/10/5/5/10/25/50/100, sem teto geral | F03 §2 |
| Revenda integral indistinta | Roupas **não vendáveis**; construções **não vendáveis**; objetos comemorativos protegidos | F04 04.10; F05 C01; F06 C04 |
| Escritório melhora apenas por mudança de sede | Sede permanente, salas anexadas, opcionais pagáveis, marcos de reserva reconhecidos | F05 P01/P04–P06 |
| Marco corrigido poderia revogar recompensa | Corrigir indicadores e preservar reconhecimentos e desbloqueios históricos | F05 C07; F06 C01–C03 |
| Fechamento “no fim do mês” sem ritual | Convocação real dia **6**, adiamento único, reunião pendente se dados incompletos | F01 §16A; F07 §3 |
| Reunião de vários meses seria “um único mês” | Apresentação pode agrupar, mas competência permanece individual | F07 C06 |
| Repetir desafio poderia gerar prêmio | Estudo repetível, mas ganho único por atividade distinta e elegível | F08 C01 |
| Cenário de simulação afeta saldo | Simulação salva/temporária é isolada de planilha e marcos | F08 C05 |

## 18.3. Questões sensíveis à classificação documental

- A atribuição “F01 = Capítulos 01–02” é **organização inferida do material entregue**, não arquivo original nomeado por capítulos.
- “Contratar funcionário com CE” em F01 tem enquadramentos de direção/proposta e **não substitui** salas essenciais gratuitas e marcos do F05.
- F01 prevê dioramas independentes e hub; F05 estabelece sede principal única e permanente. O modelo final de navegação deve preservar **ambas as decisões compatíveis** ou solicitar decisão onde a implementação produzir conflito real.
- O item grátis de coleção de F04 é recompensa por conquista de coleção; F06 protege brindes **diretamente** concedidos por conquistas. Fazer o elo de classificação no catálogo exige definição — **não presumir que reembolso integral se aplica**.
- O primeiro histórico de dois meses é caso concreto inicial, não mínimo obrigatório para futuros jogadores.
- Referência a nomes de agentes futuros, passado ficcional, arcos completos, preços de contratação/CE e cenários de progressão ilustrativos **não são decisões definitivas de catálogo**.

## 18.4. Changelog da versão 2.0

- Substituídas as lacunas artificiais do GDD 1.1 com base nos **sete arquivos efetivamente recebidos**.
- Reintegrada a **tabela econômica de oito ações** e as exceções completas de loja, construção e inventário comemorativo.
- Incorporadas as resoluções dos **9 conflitos de progressão**, **10 de conquistas**, **8 de rotinas** e **8 de educação**, além de **4 conflitos de loja**.
- Restaurado o conteúdo completo dos princípios de educação híbrida, estados do Diário, narrativa orgânica e recuperação de eventos.
- Mantidos bloqueios verdadeiros: prova temporal da planilha, retirada da reserva, políticas técnicas de dados, configurações de XP, classificação de prêmios de coleção, detalhes de reuniões acumuladas e **texto da modalidade B dos estágios**.
- Criado anexo de fontes integrais para preservação literal e rastreabilidade sem reabrir decisões já aprovadas.

