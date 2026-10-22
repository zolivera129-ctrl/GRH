// O diretor narrativo (direção narrativa v0.2, §5): decide quais cenas
// entram na fila, com que prioridade e com que chave de unicidade. É puro:
// recebe o perfil, o dia e os eventos, e devolve o perfil atualizado e a
// fila. Não depende de a cena anterior do capítulo ter sido concluída, e
// nunca mexe em resultado financeiro: só lê o que o módulo de dados validou.

import { clonar } from './estado.js';
import {
  primeiraReuniao, situacaoDaReuniao, situacaoDoPreAviso, partes, mesmaSemana,
} from './calendario.js';

// a fila sugerida no §5: Vivi > reunião vencida > reunião adiada > convite
// do dia 6 > microcenas > resumos e reações
export const PRIORIDADE = {
  C1S1: 100,
  REUNIAO_VENCIDA: 90,
  REUNIAO_ADIADA: 85,
  CONVITE: 70,
  MICROCENA: 50,
  AVISO: 30,
  AMBIENTE: 20,
};

// a partir de quantos eventos acumulados a abertura condensa num resumo
export const LIMITE_SEM_CONDENSAR = 3;

const chaves = {
  onboarding: (p) => `onboarding:vivi:${p}`,
  leitura: (p) => `primeira_leitura:${p}`,
  postos: (p) => `postos:${p}`,
  primeiraAcao: (p) => `primeira_acao:${p}`,
  reuniao: (p, c) => `monthly_meeting:${p}:${c}`,
  convite: (p, c) => `convite:${p}:${c}`,
  preAviso: (p, c) => `pre_aviso:${p}:${c}`,
  lote: (p, l) => `card_arrival:${p}:${l}`,
  categoria: (p, t) => `category_question:${p}:${t}`,
  atualizacao: (p, e) => `atualizacao:${p}:${e}`,
  consulta: (p, e) => `consulta:${p}:${e}`,
  teto: (p, c, cat, l) => `budget_alert:${p}:${c}:${cat}:${l}`,
  resumo: (p, d) => `resumo:${p}:${d}`,
};
export { chaves as CHAVES };

const concluida = (perfil, chave) => Boolean(perfil.cenas[chave]?.concluida_em);

function invocacao(cena, chave, prioridade, extra = {}) {
  return { cena, chave, prioridade, bloqueia: false, obrigatoria: false, contexto: {}, motivo: '', ...extra };
}

/** Ordena por prioridade, mantendo a ordem de chegada entre iguais. */
export function ordenar(fila) {
  return fila.map((inv, i) => [inv, i])
    .sort(([a, i], [b, j]) => b.prioridade - a.prioridade || i - j)
    .map(([inv]) => inv);
}

/** Tira da fila o que já foi concluído ou já está na fila (mesma chave). */
export function deduplicar(perfil, fila, emCurso = []) {
  const vistas = new Set(emCurso);
  return fila.filter((inv) => {
    if (concluida(perfil, inv.chave) || vistas.has(inv.chave)) return false;
    vistas.add(inv.chave);
    return true;
  });
}

/**
 * Abertura de uma visita (§3.1, "na abertura do aplicativo"):
 * registra o primeiro acesso, põe a recepção da Vivi na frente de tudo,
 * resolve a reunião (obrigatória ou convite), o pré-aviso M0 e os eventos
 * que chegaram com o app fechado. Devolve { perfil, fila, notas }.
 */
export function abrirVisita(perfilAntes, hoje, { regraDia6 = null, eventosPendentes = [], lerDados = null } = {}) {
  const perfil = clonar(perfilAntes);
  const id = perfil.perfil;
  const fila = [];
  const notas = [];

  if (!perfil.primeiro_acesso) {
    perfil.primeiro_acesso = hoje;
    const r = primeiraReuniao(hoje, regraDia6);
    perfil.primeira_reuniao = r.vencimento ?? 'pendente';
    notas.push(r.vencimento
      ? `Primeiro acesso em ${hoje}: primeira reunião vence em ${r.vencimento}${r.provisoria ? ' (regra do dia 6 escolhida só para teste)' : ''}.`
      : `Primeiro acesso no dia 6 (${hoje}): regra pendente de decisão do autor; nenhuma reunião agendada.`);
  } else if (perfil.primeira_reuniao === 'pendente' && regraDia6) {
    // o painel de teste escolheu uma leitura depois: recalcula a partir do primeiro acesso
    const r = primeiraReuniao(perfil.primeiro_acesso, regraDia6);
    perfil.primeira_reuniao = r.vencimento;
    notas.push(`Regra do dia 6 para teste (${regraDia6}): primeira reunião em ${r.vencimento}.`);
  }
  if (!concluida(perfil, chaves.onboarding(id))) {
    fila.push(invocacao('C1S1', chaves.onboarding(id), PRIORIDADE.C1S1,
      { bloqueia: true, obrigatoria: true, motivo: 'primeira entrada autenticada' }));
  }
  // retorno semanal (C3S4): a primeira visita numa semana nova deixa o
  // resumo disponível no quadro, sem interromper ninguém
  const anterior = perfil.visitas.filter((v) => v < hoje).at(-1);
  if (anterior && !mesmaSemana(anterior, hoje) && !perfil.resumo_disponivel) {
    perfil.resumo_disponivel = hoje;
    notas.push(`Retorno numa semana nova (última visita em ${anterior}): resumo disponível no quadro.`);
  }
  if (perfil.visitas.at(-1) !== hoje) perfil.visitas.push(hoje);
  perfil.visitas = perfil.visitas.slice(-60);

  // o módulo de dados lê o que já existe (histórico importado) depois que
  // o primeiro acesso está registrado
  const lidos = lerDados ? lerDados(perfil) : [];
  for (const ev of lidos) {
    if (!perfil.eventos[ev.id]) {
      perfil.eventos[ev.id] = { tipo: ev.type, recebido_em: ev.occurredAt ?? hoje, competencia: ev.competence ?? null,
        payload: ev.payload, processado_em: null };
    }
  }
  const pendentes = new Map(eventosPendentes.map((e) => [e.id, e]));
  for (const e of eventosNaoProcessados(perfil)) if (!pendentes.has(e.id)) pendentes.set(e.id, e);

  fila.push(...planejarReuniao(perfil, hoje));

  const aviso = situacaoDoPreAviso(perfil, hoje);
  if (aviso.tipo === 'no_dia' || aviso.tipo === 'tardio') {
    fila.push(invocacao('M0', chaves.preAviso(id, aviso.competencia), PRIORIDADE.AVISO,
      { contexto: { competencia: aviso.competencia, tardio: aviso.tipo === 'tardio' },
        motivo: aviso.tipo === 'no_dia' ? 'dia 1º com fechamento por anunciar' : 'pré-aviso pendente, entrega antes do dia 6' }));
  } else if (aviso.tipo === 'nao_entregue') {
    const a = (perfil.avisos[aviso.competencia] ??= {});
    if (!a.nao_entregue_em) {
      a.nao_entregue_em = hoje;
      notas.push(`Sem visita entre o dia 1 e o dia 5: o pré-aviso de ${aviso.competencia} não foi mostrado e fica registrado assim.`);
    }
  }

  const doEventos = [];
  for (const ev of pendentes.values()) doEventos.push(...planejarEvento(perfil, ev, { abertura: true }));
  const { fila: eventos, condensados } = condensar(perfil, doEventos, hoje);
  if (condensados.length) {
    // cada evento continua no seu registro; a síntese fica no quadro (C3S4)
    for (const id of condensados) {
      const e = perfil.eventos[id];
      if (e) { e.processado_em ??= hoje; e.condensado = true; }
    }
    perfil.resumo_disponivel ??= hoje;
    notas.push(`${condensados.length} eventos acumulados não viram cascata de falas: ficam no resumo do quadro.`);
  }
  fila.push(...eventos);

  return { perfil, fila: ordenar(deduplicar(perfil, fila)), notas };
}

/** A reunião que vale hoje, como invocação (ou nada). */
export function planejarReuniao(perfil, hoje) {
  const id = perfil.perfil;
  const s = situacaoDaReuniao(perfil, hoje);
  if (s.tipo === 'nenhuma') return [];
  const semPreAviso = !perfil.avisos[s.competencia]?.mostrado_em;
  const primeira = !Object.values(perfil.reunioes).some((r) => r.concluida_em);
  const contexto = { competencia: s.competencia, vencimento: s.vencimento, semPreAviso, primeira,
    acumuladas: s.acumuladas };
  if (s.tipo === 'convite') {
    return [invocacao('C4S1', chaves.convite(id, s.competencia), PRIORIDADE.CONVITE,
      { bloqueia: true, contexto, motivo: 'dia 6, perfil elegível presente' })];
  }
  const prioridade = s.motivo === 'adiada' ? PRIORIDADE.REUNIAO_ADIADA : PRIORIDADE.REUNIAO_VENCIDA;
  const motivo = { vencida: 'reunião vencida desde um dia 6 anterior, sem adiamento',
    adiada: 'reunião adiada no dia 6: obrigatória, sem novo adiamento',
    retomada: 'reunião começada e não concluída: recomeça' }[s.motivo];
  return [invocacao('REUNIAO', chaves.reuniao(id, s.competencia), prioridade,
    { bloqueia: true, obrigatoria: true, contexto: { ...contexto, motivo: s.motivo, semConvite: s.semConvite }, motivo })];
}

/**
 * As cenas que um evento de domínio pede. ctx.primeiraVisita e
 * ctx.houveAcao vêm da sessão; ctx.abertura marca o que chegou com o app
 * fechado.
 */
export function planejarEvento(perfil, ev, ctx = {}) {
  const id = perfil.perfil;
  const p = ev.payload ?? {};
  const base = { evento: ev.id, contexto: { ...p, evento: ev.id } };
  switch (ev.type) {
    case 'historical_data_ready': {
      const out = [];
      if (!concluida(perfil, chaves.leitura(id))) {
        out.push(invocacao('C1S2', chaves.leitura(id), PRIORIDADE.MICROCENA,
          { ...base, importante: true, motivo: 'primeira leitura dos dados existentes' }));
      }
      // C1S3 não vem daqui: o gatilho dela é a primeira exploração voluntária (roteiro v0.3)
      return out;
    }
    case 'card_batch_imported': {
      const primeiroLote = !Object.keys(perfil.lotes).length;
      return [invocacao('C2', chaves.lote(id, p.lote), PRIORIDADE.MICROCENA,
        { ...base, importante: primeiroLote, motivo: `lote ${p.lote}${p.historico ? ' (histórico importado)' : ''}` })];
    }
    case 'expense_needs_category': {
      const t = p.transacao;
      if (!t || perfil.categorias[t.id]?.respondida_em) return [];
      return [invocacao('C2S3', chaves.categoria(id, t.id), PRIORIDADE.MICROCENA,
        { ...base, motivo: 'gasto ambíguo de verdade' })];
    }
    case 'payment_confirmed': {
      if (ctx.primeiraVisita && !ctx.houveAcao && !concluida(perfil, chaves.primeiraAcao(id))) {
        return [invocacao('C1S4', chaves.primeiraAcao(id), PRIORIDADE.AMBIENTE,
          { ...base, contexto: { ...base.contexto, objeto: 'calendario' }, motivo: 'primeira ação da primeira visita' })];
      }
      return [invocacao('C3S1', chaves.atualizacao(id, ev.id), PRIORIDADE.AMBIENTE,
        { ...base, motivo: 'atualização real' })];
    }
    case 'purchase_consult_requested': {
      // só com pergunta voluntária: nunca para cumprir história
      if (!p.voluntaria) return [];
      return [invocacao('C3S2', chaves.consulta(id, ev.id), PRIORIDADE.MICROCENA + 5,
        { ...base, motivo: 'consulta pedida pela pessoa' })];
    }
    case 'budget_threshold_crossed': {
      if (p.teto == null || ![80, 100].includes(p.limiar)) return [];
      return [invocacao('C3S3', chaves.teto(id, p.competencia, p.categoria, p.limiar), PRIORIDADE.MICROCENA,
        { ...base, motivo: `teto de ${p.categoria} em ${p.limiar}%` })];
    }
    default:
      return [];
  }
}

/**
 * Muitos eventos de uma vez (ausência) não viram uma cascata de falas: o
 * que é importante (a primeira leitura e o primeiro lote) segue, e o resto,
 * acima do limite, sai da fila. Quem chama marca esses eventos como
 * condensados e deixa o resumo no quadro.
 */
export function condensar(perfil, fila) {
  const unicas = deduplicar(perfil, fila);
  const comuns = unicas.filter((inv) => !inv.importante);
  if (comuns.length <= LIMITE_SEM_CONDENSAR) return { fila: unicas, condensados: [] };
  return { fila: unicas.filter((inv) => inv.importante), condensados: comuns.map((i) => i.evento).filter(Boolean) };
}

// ---------------------------------------------------------------------
// Registros. Cada função devolve um perfil novo; nada é marcado como visto
// ou concluído sem a cena ter de fato acontecido na visita.

export function registrarInicio(perfilAntes, inv, quando) {
  const perfil = clonar(perfilAntes);
  const c = (perfil.cenas[inv.chave] ??= { cena: inv.cena, versao: 1 });
  c.vista_em ??= quando;
  if (inv.evento) c.evento = inv.evento;
  c.pendente = true;
  if (inv.cena === 'REUNIAO') {
    const r = (perfil.reunioes[inv.contexto.competencia] ??= { vencimento: inv.contexto.vencimento });
    r.iniciada_em ??= quando;
    if (inv.contexto.semPreAviso) r.sem_pre_aviso = true;
  }
  if (inv.cena === 'C4S1') {
    const r = (perfil.reunioes[inv.contexto.competencia] ??= { vencimento: inv.contexto.vencimento });
    r.convite_mostrado_em ??= quando;
  }
  if (inv.cena === 'M0') {
    (perfil.avisos[inv.contexto.competencia] ??= {}).mostrado_em ??= quando;
  }
  return perfil;
}

export function registrarConclusao(perfilAntes, inv, quando, resultado = {}) {
  const perfil = clonar(perfilAntes);
  const c = (perfil.cenas[inv.chave] ??= { cena: inv.cena, versao: 1 });
  c.concluida_em = quando;
  c.pendente = false;
  if (resultado.adiada) {
    // o convite foi visto e adiado: a chave do convite fica concluída, a reunião não
    const r = perfil.reunioes[inv.contexto.competencia];
    r.adiada_em = quando;
  }
  if (inv.cena === 'REUNIAO') {
    const r = perfil.reunioes[inv.contexto.competencia];
    r.concluida_em = quando;
    r.fechamento = resultado.fechamento ?? 'pendente';   // reunião feita não é mês fechado
    r.observacao = resultado.observacao ?? null;
  }
  for (const ev of resultado.eventos ?? (inv.evento ? [inv.evento] : [])) {
    if (perfil.eventos[ev]) perfil.eventos[ev].processado_em ??= quando;
  }
  return perfil;
}

/** Guarda um evento de domínio no seu registro (idempotente pelo id). */
export function registrarEvento(perfilAntes, ev, quando) {
  if (perfilAntes.eventos[ev.id]) return perfilAntes;
  const perfil = clonar(perfilAntes);
  perfil.eventos[ev.id] = { tipo: ev.type, recebido_em: quando, competencia: ev.competence ?? null,
    payload: ev.payload, processado_em: null };
  return perfil;
}

export function eventosNaoProcessados(perfil) {
  return Object.entries(perfil.eventos)
    .filter(([, e]) => !e.processado_em)
    .map(([id, e]) => ({ id, type: e.tipo, profileId: perfil.perfil, competence: e.competencia,
      occurredAt: e.recebido_em, payload: e.payload }));
}

/** Primeira visita = o dia do primeiro acesso. */
export function ehPrimeiraVisita(perfil, hoje) {
  return perfil.primeiro_acesso === hoje && perfil.visitas.filter((v) => v === hoje).length <= 1;
}

export function diaDoMes(hoje) {
  return partes(hoje).dia;
}
