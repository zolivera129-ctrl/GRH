// Falas de estado: o que o Saldanha diz quando a pessoa fala com ele e
// antes de abrir o quadro da reunião. O texto sai só do que o código já
// calculou (planilha.js); nenhuma fala diz valor em reais, porque o
// roteiro proíbe expor números sensíveis em fala (c4s2, guardrail).
//
// Texto novo, provisório: não está no roteiro v0.3 e ainda não foi
// aprovado pelo autor. Vai marcado com essa origem no balão.

import { nomeDoMes } from './calendario.js';
import { conferencia } from './planilha.js';

export const ORIGEM_NOVA = 'new_provisional_not_author_approved';

const mesDe = (comp) => (comp ? nomeDoMes(comp) : 'este mês');
const contas = (n) => `${n} conta${n === 1 ? '' : 's'}`;

/** O mês de que o Saldanha fala: o do dia, senão o mais recente lido. */
function mesEmFoco(fonte, hoje) {
  const legiveis = fonte.meses.filter((m) => m.legivel && m.competencia);
  return legiveis.find((m) => m.competencia === hoje.slice(0, 7))
    ?? legiveis.sort((a, b) => a.competencia.localeCompare(b.competencia)).at(-1) ?? null;
}

/**
 * Até dois balões: o que ele leu e o que está pendente. Recebe a fonte de
 * dados, o perfil (categorias a confirmar) e a data de hoje.
 */
export function falasDoSaldanha(fonte, perfil, hoje) {
  const semCategoria = Object.values(perfil.categorias ?? {}).filter((c) => !c.categoria).length;
  const nota = semCategoria ? ` E ${semCategoria === 1 ? 'uma despesa espera' : `${semCategoria} despesas esperam`} categoria.` : '';
  if (fonte.nome !== 'planilha') {
    return [`O livro está em dia com o que chegou até agora.${nota}`];
  }
  if (fonte.estado === 'lendo') return ['Estou lendo a planilha agora. Um minuto.'];
  if (fonte.estado !== 'lida') return ['Ainda não consegui ler a planilha. O motivo está na bancada.'];

  const m = mesEmFoco(fonte, hoje);
  if (!m) return ['Li a planilha, mas não achei nenhuma aba de mês no formato que eu conheço.'];
  const nome = mesDe(m.competencia);
  const c = conferencia(m);
  const fatura = {
    conciliado: `A fatura de ${nome} confere com a conta.`,
    divergente: `A fatura de ${nome} não bate com a conta. A diferença está anotada no livro.`,
    sem_fontes: `Em ${nome}, ainda ${c.falta ?? 'falta uma fonte'}.`,
  }[c.estado];
  const abertas = m.conta.filter((r) => !r.pago && r.debito > 0).length;
  const pagas = abertas
    ? `${contas(abertas)} de ${nome} ainda sem Pago.`
    : `Todas as contas de ${nome} estão marcadas como pagas.`;
  const hora = fonte.lidaEm?.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', timeZone: 'America/Sao_Paulo' });
  return [`${hora ? `Li a planilha às ${hora}.` : 'Li a planilha.'} ${fatura}`, `${pagas}${nota}`];
}

/** A fala antes do quadro da reunião: de que mês é e o que falta. */
export function falaDoQuadro(r) {
  const nome = mesDe(r.competencia);
  if (r.situacao === 'sem_dados') return `A planilha não tem a aba de ${nome}. Vou mostrar só o que existe.`;
  if (r.situacao === 'completa') return `${nome[0].toUpperCase()}${nome.slice(1)} está conferido: a fatura bate e as contas estão pagas.`;
  const falta = (r.faltando ?? []).filter(Boolean);
  return falta.length
    ? `Em ${nome}, ${falta.join(' e ')}. Separo o que já foi pago do que ainda é previsto.`
    : `Em ${nome}, separo o que já foi pago do que ainda é previsto.`;
}
