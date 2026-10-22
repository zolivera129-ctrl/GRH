// O roteiro do primeiro ciclo. As falas, a ordem, as variantes e as
// escolhas vêm do JSON do autor (dados/financyapp_roteiro_falas_v03.json,
// "roteiro de falas completo v0.3"); este arquivo só traduz aquilo para o
// motor do escritório:
//
//  - as animações técnicas do JSON (adjust_badge, tablet_check, nod...) para
//    as do manifesto, com o fallback do contrato (idle, olhar ou nod);
//  - os alvos (mail_drop, saldanha_desk, meeting_board...) para lugares da
//    planta e estados de objeto;
//  - as condições de cada variante (o "when" do JSON) para leituras do
//    contexto que o diretor e os dados entregam;
//  - a semântica das variantes (replace_selected_lines, append_choices...).
//
// Nada aqui escreve fala: o texto sai do JSON, preenchido só com valores
// do contexto. Chave sem valor nunca vai para a tela (a fala é omitida).
// As poucas peças que o JSON não traz estão em COMPLEMENTOS, marcadas.

export const ROTEIRO_URL = 'dados/financyapp_roteiro_falas_v03.json';

export const ator = (nome) => nome.toLowerCase();
const NOMES = { vivi: 'Vivi', saldanha: 'Saldanha', caio: 'Caio', gabriel: 'Gabriel', guilherme: 'Guilherme' };
export const nomeDe = (id) => NOMES[id] ?? id;

// rótulo de origem de cada fala, como o JSON classifica (approvalPolicy)
export const ORIGEM = {
  original_html_base: 'HTML original (base)',
  original_html_selected_direction: 'HTML original (alternativa escolhida)',
  previous_tech_proposal_not_html: 'proposta técnica anterior (provisória)',
  new_provisional_not_author_approved: 'nova, provisória (sem aprovação do autor)',
  complemento_do_motor: 'complemento do motor (não está no JSON)',
};
export const ehProvisoria = (origem) => origem !== 'original_html_base' && origem !== 'original_html_selected_direction';

// o que o JSON não traz e o motor precisou completar
export const COMPLEMENTOS = {
  // c4s3 tem as variantes "confirmou" e "adiou" a prioridade, mas não os botões
  c4s3_escolhas: [
    { action: 'player_confirms_observation_priority', label: 'Acompanhar com clareza' },
    { action: 'player_defers_priority', label: 'Deixar para depois' },
  ],
  // o texto do M0 veio sem acentos no JSON (herdado do v02); só os acentos foram repostos
  acentos: {
    'Comecamos a preparacao do fechamento do periodo anterior. Nossa reuniao e no dia 6.':
      'Começamos a preparação do fechamento do período anterior. Nossa reunião é no dia 6.',
  },
};

// ---------------------------------------------------------------------
// Animações técnicas -> comandos do motor. "fallback: true" marca o que
// ainda não tem arte própria e usa o gesto mais próximo.
const ANIMACAO = {
  idle_blink: (a) => [{ op: 'piscar', actor: a }],
  adjust_badge: (a) => [{ op: 'play', actor: a, animation: 'olhando_para_o_lado_frente', fallback: 'adjust_badge' }],
  face_player: (a) => [{ op: 'face', actor: a, dir: 'frente' }],
  look_at: (a) => [{ op: 'play', actor: a, animation: 'olhando_para_o_lado_frente' }],
  idle_standing: (a) => [{ op: 'repouso', actor: a }],
  tablet_check: (a) => (a === 'saldanha'
    ? [{ op: 'play', actor: a, animation: 'digitando_sentado', loop: true }]
    : [{ op: 'play', actor: a, animation: 'olhando_para_o_lado_frente', fallback: 'tablet_check' }]),
  glasses_adjust: (a) => [{ op: 'play', actor: a, animation: 'assentindo_para_tela_frente', fallback: 'glasses_adjust' }],
  point: (a) => [{ op: 'apontar', actor: a }],
  typing: (a) => [{ op: 'play', actor: a, animation: 'teclando_frente', loop: true }],
  nod: (a) => [{ op: 'play', actor: a, animation: 'assentindo_para_tela_frente' }],
  wave: () => [],
  give_envelope: (a) => [
    { op: 'play', actor: a, animation: 'deixando_envelope_no_malote_costas', wait: true },
    { op: 'soltar', actor: a },
    { op: 'face', actor: a, dir: '+A' },       // vira para a sala para conversar
  ],
  walk_iso: (a, alvo) => [{ op: 'move', actor: a, target: destino(a, alvo) }],
  sit_down: () => [],            // andar até a mesa da reunião já termina sentado
  stand_up: (a) => [{ op: 'levantar', actor: a }],
  turn_tablet: (a) => [
    { op: 'selo', actor: a },
    { op: 'play', actor: a, animation: 'mostrando_tablet', manter: true },
    { op: 'esperar', ms: 2200 },
    { op: 'selo', actor: a, limpar: true },
  ],
};

/** Para onde cada alvo leva cada personagem, na planta 12x10. */
export function destino(a, alvo) {
  switch (alvo) {
    case 'mail_drop': return { ponto: [0.5, 8.1], olhar: '-B' };      // 0,4 tile do centro, rumo ao malote
    case 'exit_door': return 'fora';
    case 'saldanha_desk': return a === 'saldanha' ? 'posto' : { tile: [6, 2], olhar: '-B' };   // p_saldanha
    case 'caio_station': return a === 'caio' ? { tile: [8, 3], olhar: '+A' } : { tile: [6, 5], olhar: '-B' };
    case 'meeting_table': return 'reuniao';
    default: return 'posto';
  }
}

// alvos e estados de objeto do JSON -> estado visual (ou brilho) na sala
const OBJETO = {
  'mail_drop:received_not_reconciled': () => [{ op: 'object', target: 'malote', state: 'com-envelope' }],
  'reconciliation_panel:state_from_reconciliation_engine': (c) => (c.conciliacao === 'divergente'
    ? [{ op: 'object', target: 'malote', state: 'sinalizado' }] : []),
  'monthly_book:highlight_verified_entry': () => [{ op: 'focus', target: ['mesa_saldanha'], ms: 3500 }],
  'saldanha_desk:temporary_hint': () => [{ op: 'focus', target: ['mesa_saldanha'], ms: 9000 }],
  'caio_station:temporary_hint': () => [{ op: 'focus', target: ['mesa_caio'], ms: 9000 }],
  'verified_changed_object:animate_verified_state_only': (c) => (c.objeto
    ? [{ op: 'object', target: c.objeto, state: 'marcado' }, { op: 'focus', target: [c.objeto], ms: 3000 }] : []),
  'category_prompt:awaiting_confirmation': () => [{ op: 'focus', target: ['mesa_saldanha'], ms: 4000 }],
  'payment_calendar:sync_real_state': () => [{ op: 'object', target: 'calendario', state: 'marcado' },
    { op: 'focus', target: ['calendario'], ms: 2500 }],
  'bill_inbox:sync_real_state': () => [{ op: 'focus', target: ['mesa_saldanha'], ms: 2500 }],
  'category_progress_bar:show_confirmed_threshold': (c) => [{ op: 'object', target: 'mural_alertas', state: `teto-${c.limiar}` },
    { op: 'focus', target: ['mural_alertas'], ms: 3500 }],
  'weekly_board:summary_available': () => [{ op: 'object', target: 'quadro', state: 'novo' }],
  'meeting_board:advance_notice_unread': () => [{ op: 'object', target: 'quadro', state: 'aviso-novo' }],
  'meeting_board:advance_notice_seen': () => [{ op: 'object', target: 'quadro', state: 'aviso' }],
  'meeting_board:invitation_due': () => [{ op: 'object', target: 'quadro', state: 'convite' }],
  'meeting_board:page_financial_flow': () => [{ op: 'object', target: 'quadro', state: 'relatorio' }],
  'meeting_board:page_priority': () => [{ op: 'object', target: 'quadro', state: 'relatorio' }],
  'meeting_board:closing_state_from_domain': (c) => (c.situacao === 'completa'
    ? [{ op: 'object', target: 'tela', state: 'fechado' }, { op: 'object', target: 'quadro', state: null }]
    : [{ op: 'object', target: 'quadro', state: null }]),
};

// ---------------------------------------------------------------------
// As condições das variantes (o "when" do JSON), lidas do contexto.
// Contexto: o que o diretor e os dados entregam (§5), mais as escolhas
// feitas durante a cena em c.escolhas.
const QUANDO = {
  c1s1: { intro_before_overdue_meeting: () => false },   // a fala inteira toca e a reunião vem depois (é a ordem da fila)
  c1s2: { missing_history: (c) => !(c.meses_validos > 0) },
  c1s4: { first_exit_without_financial_action: (c) => Boolean(c.saida) && !c.acao },
  c2s1: { no_batch: (c) => !c.lote },
  c2s2: {
    matched: (c) => c.conciliacao === 'conciliado',
    partial: (c) => c.conciliacao === 'sem_fontes',
    different: (c) => c.conciliacao === 'divergente',
  },
  c2s3: {
    no_ambiguity: (c) => !c.transacao,
    category_choices: (c) => Boolean(c.transacao && c.categoria_a && c.categoria_b),
  },
  c2s4: { still_partial: (c) => c.conciliacao !== 'conciliado' },
  c3s1: { no_confirmed_change: (c) => !c.evento },
  c3s2: {
    not_requested: (c) => !c.voluntaria,
    missing_consult_data: (c) => !['verde', 'amarelo', 'vermelho'].includes(c.veredito) || !c.motivo_curto,
  },
  c3s3: {
    no_threshold: (c) => c.teto == null || ![80, 100].includes(c.limiar),
    education_choice: (c) => c.teto != null && c.cardDisponivel !== false,
  },
  c3s4: {
    not_a_weekly_return: (c) => !c.resumoDisponivel,
    no_valid_updates: (c) => c.quantidade_eventos_validos === 0,
  },
  m0: {
    first_eligible_visit_day_2_to_5: (c) => c.tardio,
    no_login_until_due: (c) => c.dia >= 6,
  },
  c4s1: {
    not_yet_eligible: (c) => !c.competencia,
    first_access_exact_day_6: () => false,           // o diretor nunca agenda nesse caso
    eligible_day_6: (c) => c.convite === true,
    overdue_or_already_deferred: (c) => c.convite !== true,
  },
  c4s2: { partial_data: (c) => c.situacao !== 'completa' },
  // estas duas dependem da escolha feita na própria cena: viram guardas
  c4s3: {
    observation_confirmed: (c) => c.escolhas?.c4s3 === 'player_confirms_observation_priority',
    priority_deferred: (c) => c.escolhas?.c4s3 === 'player_defers_priority',
  },
  c4s4: { closing_pending: (c) => c.situacao !== 'completa' },
};
const DURANTE_A_CENA = new Set(['c4s3:observation_confirmed', 'c4s3:priority_deferred']);

// ---------------------------------------------------------------------

/** Preenche as chaves; devolve null se alguma ficar sem valor. */
export function preencher(texto, c) {
  let numero = null;
  const t = COMPLEMENTOS.acentos[texto] ?? texto;
  const cheio = t.replace(/\{(\w+)\}/g, (m, k) => {
    const v = c[k];
    if (v === undefined || v === null || v === '') return m;
    if (typeof v === 'number') numero = v;
    return String(v);
  });
  if (/\{\w+\}/.test(cheio)) return null;
  // "período(s)": singular ou plural certo pelo número da própria fala
  return numero === null ? cheio : cheio.replace(/(\p{L}+)\(s\)/gu, (_, w) => (numero === 1 ? w : `${w}s`));
}

const saudacao = (hora) => (hora < 12 ? 'Bom dia' : hora < 18 ? 'Boa tarde' : 'Boa noite');

function falar(cmd, cena, c) {
  let texto = preencher(cmd.text, c);
  if (texto === null) return null;
  // C2S1: "ajustar 'boa tarde' à hora do dia" (direção v0.2, §4)
  if (cena.sceneId === 'c2s1' && texto.startsWith('Boa tarde')) texto = texto.replace('Boa tarde', saudacao(c.hora ?? 15));
  return {
    op: 'speak', actor: ator(cmd.actor), texto, origem: cmd.source, ref: cmd.sourceRef ?? null,
    advance: 'tap', ambiente: cena.presentationKind.startsWith('ambient'),
  };
}

function escolha(cmd, cena, c, ultimoAtor) {
  const choices = [];
  for (const ch of cmd.choices) {
    const label = preencher(ch.label, c);
    if (label === null) return null;
    choices.push({ id: ch.action, texto: label, origem: ch.origem ?? cmd.source });
  }
  return { op: 'choice', actor: ultimoAtor, choices, cena: cena.sceneId, origem: cmd.source };
}

/** Traduz um comando do JSON para os do motor. */
function traduzir(cmd, cena, c, ultimoAtor) {
  if (cmd.op === 'speak') return [falar(cmd, cena, c)].filter(Boolean);
  if (cmd.op === 'choice') return [escolha(cmd, cena, c, ultimoAtor)].filter(Boolean);
  if (cmd.op === 'object') {
    const f = OBJETO[`${cmd.target}:${cmd.state}`];
    return f ? f(c) : [];
  }
  if (cmd.op === 'play') {
    const f = ANIMACAO[cmd.animation];
    return f ? f(ator(cmd.actor), cmd.target) : [];
  }
  return [];
}

const ehFalaEscolhida = (cmd) => cmd.op === 'speak' && cmd.source === 'original_html_selected_direction';

/**
 * As variantes ativas de uma cena e o roteiro resultante, ainda no formato
 * do JSON. Devolve { pular, script, variantes, guardadas }.
 */
export function resolverVariantes(cena, c) {
  const quando = QUANDO[cena.sceneId] ?? {};
  const ativas = [];
  const guardadas = [];
  for (const v of cena.conditionalVariants) {
    const f = quando[v.variantId];
    if (!f) continue;
    if (DURANTE_A_CENA.has(`${cena.sceneId}:${v.variantId}`)) { guardadas.push(v); continue; }
    if (f(c)) ativas.push(v);
  }
  if (ativas.some((v) => v.behavior === 'skip')) return { pular: true, script: [], variantes: ativas, guardadas };

  let script = cena.script.map((cmd) => ({ ...cmd }));
  for (const v of ativas) {
    switch (v.behavior) {
      case 'replace_selected_lines': {
        // as falas da alternativa escolhida saem; a variante entra no lugar
        // (em c4s2, depois da fala de abertura, como diz a nota do JSON)
        const i = script.findIndex(ehFalaEscolhida);
        script = script.filter((cmd) => !ehFalaEscolhida(cmd));
        const onde = i < 0 ? script.length : i;
        script.splice(onde, 0, ...v.script);
        break;
      }
      case 'show_partial_state_no_false_comparison': {
        const i = script.findIndex((cmd) => cmd.op === 'speak');
        script.splice(i + 1, 0, ...v.script);
        break;
      }
      case 'replace_all_dialogue': {
        const i = script.findIndex((cmd) => cmd.op === 'speak');
        script = script.filter((cmd) => cmd.op !== 'speak');
        script.splice(i < 0 ? script.length : i, 0, ...v.script);
        break;
      }
      case 'replace_verdict_line': {
        const i = script.findIndex((cmd) => cmd.op === 'speak' && cmd.text.includes('{veredito}'));
        script = script.filter((cmd, k) => k !== i && !(cmd.op === 'play' && cmd.animation === 'turn_tablet'));
        script.splice(i < 0 ? script.length : i, 0, ...v.script);
        break;
      }
      case 'replace_all_dialogue_and_start_mandatory':
        // não toca a fala padrão: a reunião entra direto e só esta fala toca
        script = [...v.script];
        break;
      case 'append_choices':
      case 'play_selected_lines_and_present_choice':
      case 'play_selected_dialogue_and_choice':
        script.push(...v.script);
        break;
      default:
        // keep_dialogue_no_success_badge, avoid_closed_seal, show_late_pre_notice_once,
        // play_main_dialogue_then_resume_to_mandatory_meeting: mesmo roteiro; o
        // estado visual já vem do domínio, sem selo falso
        break;
    }
  }
  return { pular: false, script, variantes: ativas, guardadas };
}

/**
 * Os comandos do motor para uma cena do JSON, com o contexto dado.
 * Devolve null se a cena deve ser pulada (variante skip).
 */
export function comandosDaCena(json, sceneId, c) {
  const cena = json.scenes.find((s) => s.sceneId === sceneId);
  if (!cena) throw new Error(`cena ${sceneId} não está no roteiro`);
  const { pular, script, variantes, guardadas } = resolverVariantes(cena, c);
  if (pular) return null;
  const out = [{ op: 'marca', cena: sceneId, titulo: cena.title, variantes: variantes.map((v) => v.variantId) }];
  let ultimo = null;
  for (const cmd of script) {
    if (cmd.op === 'speak') ultimo = ator(cmd.actor);
    out.push(...traduzir(cmd, cena, c, ultimo));
  }
  // c4s3: os botões que o JSON não traz, e a fala da variante pela escolha
  if (sceneId === 'c4s3') {
    out.push({ op: 'choice', actor: 'saldanha', cena: 'c4s3', origem: 'complemento_do_motor',
      choices: COMPLEMENTOS.c4s3_escolhas.map((e) => ({ id: e.action, texto: e.label, origem: 'complemento_do_motor' })) });
    for (const v of guardadas) {
      for (const cmd of v.script) {
        const t = traduzir(cmd, cena, c, 'saldanha');
        out.push(...t.map((x) => ({ ...x, se: (ctx) => QUANDO.c4s3[v.variantId](ctx) })));
      }
    }
  }
  // c4s4 nas reuniões seguintes: a fala "nossa primeira reunião" não vale
  if (sceneId === 'c4s4' && !c.primeira) {
    const i = out.findIndex((x) => x.op === 'speak' && x.texto.startsWith('Nossa primeira reunião'));
    if (i >= 0) out.splice(i, 1);
  }
  return out;
}

// ---------------------------------------------------------------------
// As cenas como o diretor as chama: algumas são uma cena do JSON, outras
// juntam várias (o arco do envelope, a reunião).

const reunir = (atores) => [
  ...atores.map((a) => ({ op: 'move', actor: a, target: 'reuniao', wait: false })),
  { op: 'aguardar', actors: atores },
];
const dispersar = (atores) => atores.map((a) => ({ op: 'move', actor: a, target: 'posto', wait: false, fundo: true }));

export const CENAS = {
  C1S1: { titulo: 'Vivi abre a porta', pulavel: false,
    montar: (j, c) => [{ op: 'entrar', actor: 'guilherme', ate: { tile: [0, 8], olhar: '+A' } },
      ...comandosDaCena(j, 'c1s1', c),
      { op: 'move', actor: 'guilherme', target: 'posto', wait: false, fundo: true }] },
  C1S2: { titulo: 'O contador já viu alguma coisa', pulavel: true, montar: (j, c) => comandosDaCena(j, 'c1s2', c) },
  C1S3: { titulo: 'Quem decide por onde começar?', pulavel: true, ambiente: true, montar: (j, c) => comandosDaCena(j, 'c1s3', c) },
  C1S4: { titulo: 'O escritório percebe você', pulavel: true, ambiente: true, montar: (j, c) => comandosDaCena(j, 'c1s4', c) },
  C2: { titulo: 'O envelope sobre a mesa', pulavel: true,
    montar: (j, c) => {
      const s1 = comandosDaCena(j, 'c2s1', c);
      if (!s1) return null;
      const out = [{ op: 'entrar', actor: 'gabriel', envelope: true }, { op: 'cao', actor: 'flora', animation: 'sentado_frente' }, ...s1];
      out.push(...(comandosDaCena(j, 'c2s2', c) ?? []));
      out.push({ op: 'panel', panel: 'conciliacao', se: (x) => x.escolhas?.c2s2 === 'open_reconciliation_details' });
      for (const t of c.ambiguas_pendentes ?? []) {
        const s3 = comandosDaCena(j, 'c2s3', { ...c, ...t.campos, transacao: t });
        if (s3) out.push({ op: 'contexto', transacao: t }, ...s3, { op: 'resultado', chave: 'categoria', transacao: t.id });
      }
      out.push(...(comandosDaCena(j, 'c2s4', c) ?? []));
      out.push({ op: 'cao', actor: 'flora', animation: 'dormindo_na_cama' });
      return out;
    } },
  C2S3: { titulo: 'Uma despesa sem sobrenome', pulavel: true,
    montar: (j, c) => {
      const s3 = comandosDaCena(j, 'c2s3', c);
      return s3 && [...s3, { op: 'resultado', chave: 'categoria', transacao: c.transacao?.id }];
    } },
  C3S1: { titulo: 'Uma marca no calendário', pulavel: true, ambiente: true,
    montar: (j, c) => {
      const cmds = comandosDaCena(j, 'c3s1', c);
      // a fala da Vivi só aparece se ela estiver visível no posto (encenação do JSON)
      return cmds && cmds.filter((x) => !(x.op === 'speak' && x.actor === 'vivi' && !c.viviNoPosto));
    } },
  C3S2: { titulo: 'Antes de decidir uma compra', pulavel: true,
    montar: (j, c) => {
      // a primeira fala do Caio pede o que a pessoa quer comprar: o formulário
      // entra logo depois dela; sem resposta, a consulta não existe e a cena para
      const cmds = comandosDaCena(j, 'c3s2', { ...c, voluntaria: true, veredito: 'verde', motivo_curto: '-' });
      const i = cmds.findIndex((x) => x.op === 'speak');
      const resto = (ctx) => {
        const todos = comandosDaCena(j, 'c3s2', { ...c, ...ctx.consulta, voluntaria: true });
        return [todos[0], ...todos.slice(i + 1)];   // a marca (com a variante certa) e o que vem depois do formulário
      };
      return [...cmds.slice(1, i + 1), { op: 'panel', panel: 'consulta' }, { op: 'continuar', se: (x) => Boolean(x.consulta), comandos: resto },
        { op: 'move', actor: 'caio', target: 'posto' }];
    } },
  C3S3: { titulo: 'O quadro levanta a mão', pulavel: true,
    montar: (j, c) => {
      const cmds = comandosDaCena(j, 'c3s3', c);
      return cmds && [...cmds, { op: 'panel', panel: 'card', se: (x) => x.escolhas?.c3s3 === 'open_contextual_education_card' }];
    } },
  C3S4: { titulo: 'Uma semana que não precisa ser perfeita', pulavel: true,
    montar: (j, c) => {
      const cmds = comandosDaCena(j, 'c3s4', c);
      return cmds && [...cmds, { op: 'resultado', chave: 'resumo_visto' }];
    } },
  M0: { titulo: 'Aviso de preparação do fechamento', pulavel: true, ambiente: true, montar: (j, c) => comandosDaCena(j, 'm0', c) },
  C4S1: { titulo: 'O convite do dia 6', pulavel: false,
    montar: (j, c) => {
      const cmds = comandosDaCena(j, 'c4s1', { ...c, convite: true });
      return cmds && [...cmds,
        { op: 'move', actor: 'saldanha', target: 'posto', se: (x) => x.escolhas?.c4s1 === 'defer_once_and_persist' },
        { op: 'resultado', chave: 'convite' }];
    } },
  REUNIAO: { titulo: 'A reunião mensal', pulavel: false, reuniao: true,
    montar: (j, c) => {
      const mesa = ['guilherme', 'vivi', 'caio'];
      const out = [];
      if (c.motivo !== 'aceita') {
        // vencida, adiada ou retomada: entra direto na mesa e só a fala da variante toca
        out.push(...reunir([...mesa, 'saldanha']));
        out.push(...comandosDaCena(j, 'c4s1', { ...c, convite: false }).filter((x) => x.op !== 'move'));
      } else {
        out.push(...reunir(mesa));
      }
      out.push(...comandosDaCena(j, 'c4s2', c));
      out.push({ op: 'panel', panel: 'relatorio' });
      out.push(...comandosDaCena(j, 'c4s3', c));
      out.push({ op: 'resultado', chave: 'observacao' });
      out.push(...comandosDaCena(j, 'c4s4', c));
      out.push({ op: 'cao', actor: 'flora', animation: 'dormindo_na_cama' }, { op: 'cao', actor: 'lupin', animation: 'dormindo_na_cama' });
      out.push({ op: 'marco', id: 'reuniao_concluida' });
      out.push(...dispersar(mesa));
      return out;
    } },
};

/** Ids de cena do JSON que o motor usa (para o teste de cobertura). */
export const CENAS_DO_JSON = ['c1s1', 'c1s2', 'c1s3', 'c1s4', 'c2s1', 'c2s2', 'c2s3', 'c2s4',
  'c3s1', 'c3s2', 'c3s3', 'c3s4', 'm0', 'c4s1', 'c4s2', 'c4s3', 'c4s4'];
export { ANIMACAO, OBJETO, QUANDO };
