// O calendário do ciclo mensal (direção narrativa v0.2, §2 e §3.1). Tudo
// aqui é puro: recebe o estado persistido do perfil e o dia de hoje e diz o
// que vale. As datas são dias civis em São Paulo, no formato AAAA-MM-DD, e
// a competência é AAAA-MM.
//
// Regra aprovada da primeira reunião: primeiro acesso do dia 1 ao 5 vence no
// dia 6 do mesmo mês; do dia 7 em diante, no dia 6 do mês seguinte. O
// primeiro acesso no próprio dia 6 está PENDENTE de decisão do autor: sem a
// decisão, nenhuma reunião é agendada e o estado diz que está pendente.

export const FUSO = 'America/Sao_Paulo';
export const DIA_DA_REUNIAO = 6;

// as duas leituras possíveis para o primeiro acesso no dia 6; nenhuma é a
// padrão (null = pendente)
export const REGRAS_DIA_6 = ['mesmo_mes', 'mes_seguinte'];

const dois = (n) => String(n).padStart(2, '0');

export function partes(d) {
  const [ano, mes, dia] = d.split('-').map(Number);
  return { ano, mes, dia };
}

/** Monta uma data AAAA-MM-DD, aceitando mês fora de 1..12 (vira o ano). */
export function data(ano, mes, dia) {
  const a = ano + Math.floor((mes - 1) / 12);
  const m = ((mes - 1) % 12 + 12) % 12 + 1;
  return `${a}-${dois(m)}-${dois(dia)}`;
}

export function somarDias(d, n) {
  const { ano, mes, dia } = partes(d);
  const t = new Date(Date.UTC(ano, mes - 1, dia + n));
  return `${t.getUTCFullYear()}-${dois(t.getUTCMonth() + 1)}-${dois(t.getUTCDate())}`;
}

export function diasEntre(a, b) {
  const pa = partes(a);
  const pb = partes(b);
  return Math.round((Date.UTC(pb.ano, pb.mes - 1, pb.dia) - Date.UTC(pa.ano, pa.mes - 1, pa.dia)) / 864e5);
}

/** O dia civil de agora em São Paulo. */
export function hojeEmSaoPaulo(agora = new Date()) {
  return new Intl.DateTimeFormat('en-CA', { timeZone: FUSO, year: 'numeric', month: '2-digit', day: '2-digit' })
    .format(agora);
}

export function horaEmSaoPaulo(agora = new Date()) {
  return Number(new Intl.DateTimeFormat('en-GB', { timeZone: FUSO, hour: '2-digit', hourCycle: 'h23' }).format(agora));
}

/** A competência que a reunião de um dia 6 revisa: o mês anterior. */
export function competenciaDaReuniao(vencimento) {
  const { ano, mes } = partes(vencimento);
  return data(ano, mes - 1, 1).slice(0, 7);
}

const MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto',
  'setembro', 'outubro', 'novembro', 'dezembro'];

export function nomeDoMes(competencia) {
  return MESES[Number(competencia.slice(5, 7)) - 1];
}

/**
 * Primeira data de reunião a partir do primeiro acesso.
 * Devolve { vencimento } ou { pendente: 'primeiro-acesso-no-dia-6' }.
 * regraDia6 só existe para o painel de teste simular as duas leituras.
 */
export function primeiraReuniao(primeiroAcesso, regraDia6 = null) {
  const { ano, mes, dia } = partes(primeiroAcesso);
  if (dia < DIA_DA_REUNIAO) return { vencimento: data(ano, mes, DIA_DA_REUNIAO) };
  if (dia > DIA_DA_REUNIAO) return { vencimento: data(ano, mes + 1, DIA_DA_REUNIAO) };
  if (regraDia6 === 'mesmo_mes') return { vencimento: data(ano, mes, DIA_DA_REUNIAO), provisoria: true };
  if (regraDia6 === 'mes_seguinte') return { vencimento: data(ano, mes + 1, DIA_DA_REUNIAO), provisoria: true };
  return { pendente: 'primeiro-acesso-no-dia-6' };
}

/** Todos os dias 6 de reunião, do primeiro vencimento até hoje (inclusive). */
export function vencimentosAte(primeiro, hoje) {
  const out = [];
  if (!primeiro || primeiro > hoje) return out;
  let { ano, mes } = partes(primeiro);
  for (let v = primeiro; v <= hoje; v = data(ano, ++mes, DIA_DA_REUNIAO)) out.push(v);
  return out;
}

/**
 * O que vale hoje para a reunião mensal (§3.1, passos 2 a 5):
 *  - { tipo: 'nenhuma', motivo }               nada a impor
 *  - { tipo: 'convite', vencimento, competencia }   hoje é o dia 6 devido
 *  - { tipo: 'obrigatoria', vencimento, competencia, motivo, semConvite, acumuladas }
 * A mais antiga não concluída vem primeiro. "motivo" da obrigatória:
 * 'vencida' (hoje depois do dia 6), 'adiada' (adiou no dia 6) ou
 * 'retomada' (começou e não terminou: recarregou no meio).
 */
export function situacaoDaReuniao(perfil, hoje) {
  const primeiro = perfil.primeira_reuniao;
  if (!primeiro) return { tipo: 'nenhuma', motivo: 'sem-primeiro-acesso' };
  if (primeiro === 'pendente') return { tipo: 'nenhuma', motivo: 'regra-do-dia-6-pendente' };
  const reunioes = perfil.reunioes ?? {};
  const devidas = vencimentosAte(primeiro, hoje)
    .filter((v) => !reunioes[competenciaDaReuniao(v)]?.concluida_em);
  if (!devidas.length) {
    return { tipo: 'nenhuma', motivo: primeiro > hoje ? 'primeira-ainda-nao-venceu' : 'em-dia', proxima: primeiro > hoje ? primeiro : null };
  }
  const vencimento = devidas[0];
  const competencia = competenciaDaReuniao(vencimento);
  const r = reunioes[competencia] ?? {};
  const base = { vencimento, competencia, acumuladas: devidas.length };
  if (hoje > vencimento) {
    return { tipo: 'obrigatoria', motivo: r.adiada_em ? 'adiada' : (r.iniciada_em ? 'retomada' : 'vencida'),
      semConvite: !r.convite_mostrado_em, ...base };
  }
  // hoje é o próprio dia 6
  if (r.adiada_em) return { tipo: 'obrigatoria', motivo: 'adiada', semConvite: false, ...base };
  if (r.iniciada_em) return { tipo: 'obrigatoria', motivo: 'retomada', semConvite: !r.convite_mostrado_em, ...base };
  return { tipo: 'convite', ...base };
}

/** Só o convite do próprio dia 6 pode ser adiado, e uma vez. */
export function podeAdiar(perfil, hoje) {
  const s = situacaoDaReuniao(perfil, hoje);
  return s.tipo === 'convite' && !perfil.reunioes?.[s.competencia]?.adiada_em;
}

/**
 * O pré-aviso M0 (§2.7 e §3): do dia 1 ao 5 de um mês cujo dia 6 é de
 * reunião, se ainda não foi mostrado. No dia 1 é 'no_dia'; do 2 ao 5 é a
 * entrega tardia legítima ('tardio'). Do dia 6 em diante, sem aviso
 * mostrado, é 'nao_entregue': a reunião reconhece que não houve pré-aviso,
 * sem fingir uma visita que não aconteceu.
 */
export function situacaoDoPreAviso(perfil, hoje) {
  const primeiro = perfil.primeira_reuniao;
  if (!primeiro || primeiro === 'pendente') return { tipo: 'nenhum' };
  const { ano, mes, dia } = partes(hoje);
  const vencimento = data(ano, mes, DIA_DA_REUNIAO);
  if (vencimento < primeiro) return { tipo: 'nenhum' };
  const competencia = competenciaDaReuniao(vencimento);
  if (perfil.reunioes?.[competencia]?.concluida_em) return { tipo: 'nenhum' };
  const mostrado = perfil.avisos?.[competencia]?.mostrado_em;
  if (dia < DIA_DA_REUNIAO) {
    if (mostrado) return { tipo: 'nenhum' };
    return { tipo: dia === 1 ? 'no_dia' : 'tardio', competencia, vencimento };
  }
  return mostrado ? { tipo: 'nenhum' } : { tipo: 'nao_entregue', competencia, vencimento };
}

/** Mesma semana (segunda a domingo) em São Paulo? */
export function mesmaSemana(a, b) {
  const seg = (d) => {
    const { ano, mes, dia } = partes(d);
    const dow = (new Date(Date.UTC(ano, mes - 1, dia)).getUTCDay() + 6) % 7;
    return somarDias(d, -dow);
  };
  return seg(a) === seg(b);
}
