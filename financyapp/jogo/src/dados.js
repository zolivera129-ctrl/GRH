// Dados financeiros SINTÉTICOS, só para testar as cenas (CLAUDE.md, regra 2:
// dado de teste só existe marcado como sintético). O módulo de dados de
// verdade (planilha, conciliação, regras do Caio) ainda não existe; quando
// existir, ele gera os mesmos eventos de domínio (§5) e este arquivo sai.
//
// Nada aqui decide veredito, fechamento ou recompensa: os valores servem
// para as falas e o quadro terem o que mostrar, sempre com o selo de
// sintético.

import { data, partes, competenciaDaReuniao } from './calendario.js';

export const BASES = {
  nenhuma: 'Sem histórico (usuário novo, sem dados)',
  dois_meses: 'Dois meses conciliados antes da primeira visita',
  parcial: 'Base parcial: o último mês sem o cartão',
};

const brl = (v) => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
export { brl };

// números estáveis por competência (o mesmo mês sempre dá o mesmo valor)
function semente(s) {
  let h = 2166136261;
  for (const ch of s) h = Math.imul(h ^ ch.charCodeAt(0), 16777619);
  return () => {
    h = Math.imul(h ^ (h >>> 15), 2246822507);
    h = Math.imul(h ^ (h >>> 13), 3266489909);
    return ((h ^= h >>> 16) >>> 0) / 4294967296;
  };
}
const redondo = (v) => Math.round(v / 10) * 10;

const mesesAntes = (dia, n) => {
  const { ano, mes } = partes(dia);
  return Array.from({ length: n }, (_, i) => data(ano, mes - n + i, 1).slice(0, 7));
};

export function criarDados() {
  const d = { base: 'dois_meses', privado: false, contador: 0 };

  /** Os meses que existiam antes da primeira visita, conforme a base. */
  d.historico = (primeiroAcesso) => {
    if (d.base === 'nenhuma') return [];
    const [m1, m2] = mesesAntes(primeiroAcesso, 2);
    if (d.base === 'parcial') return [{ competencia: m1, conferido: true }, { competencia: m2, conferido: false, falta: 'o cartão' }];
    return [{ competencia: m1, conferido: true }, { competencia: m2, conferido: true }];
  };

  /** A competência da reunião, como o quadro vai mostrar. */
  d.situacaoDe = (competencia, perfil) => {
    if (d.base === 'nenhuma') return 'sem_dados';
    if (d.base === 'parcial') return 'parcial';
    return competencia ? 'completa' : 'completa';
  };

  d.relatorio = (competencia, perfil) => {
    const situacao = d.situacaoDe(competencia, perfil);
    const r = semente(`relatorio:${competencia}`);
    const entradas = redondo(6800 + r() * 2400);
    const saidasConta = redondo(3200 + r() * 1400);
    const saidasCartao = redondo(2100 + r() * 1600);
    const compromissos = [
      { item: 'Fatura do cartão do próximo mês', valor: redondo(1800 + r() * 900) },
      { item: 'Parcelas em andamento', valor: redondo(300 + r() * 500) },
      { item: 'Contas fixas', valor: redondo(900 + r() * 400) },
    ];
    const reserva = redondo(1400 + r() * 3000);
    const base = { competencia, situacao, sintetico: true };
    if (situacao === 'sem_dados') {
      return { ...base, entradas: null, saidas: null, resultado: null, compromissos: null, reserva: null,
        faltando: ['planilha da conta', 'lote do cartão'] };
    }
    if (situacao === 'parcial') {
      return { ...base, entradas, saidas: null, saidasConta, saidasCartao: null, resultado: null,
        compromissos: compromissos.filter((c) => !c.item.startsWith('Fatura')), reserva,
        faltando: ['lote do cartão'], foco: 'o que falta chegar' };
    }
    return { ...base, entradas, saidas: saidasConta + saidasCartao, saidasConta, saidasCartao,
      resultado: entradas - saidasConta - saidasCartao, compromissos, reserva, faltando: [],
      foco: 'as saídas do cartão' };
  };

  // ---- eventos de domínio sintéticos (formato do §5)
  const evento = (type, payload, competence = null) => ({
    id: `${type}:${Date.now().toString(36)}:${(d.contador++).toString(36)}`,
    type, profileId: 'guilherme', competence, occurredAt: new Date().toISOString(),
    payload: { ...payload, sintetico: true },
  });

  /** O que o módulo de dados lê ao abrir a visita, uma vez por perfil. */
  d.eventosDeAbertura = (perfil) => {
    const out = [];
    const hist = d.historico(perfil.primeiro_acesso);
    // sem histórico legível não há "primeira leitura": a C1S2 sem dados
    // toca quando a pessoa abre a mesa do Saldanha (variante missing_history)
    if (!perfil.eventos['historico:leitura'] && hist.some((m) => m.conferido)) {
      out.push({ id: 'historico:leitura', type: 'historical_data_ready', profileId: perfil.perfil, competence: null,
        occurredAt: perfil.primeiro_acesso,
        payload: { meses_validos: hist.filter((m) => m.conferido).length, meses: hist,
          meses_fora: hist.filter((m) => !m.conferido).length, sintetico: true } });
    }
    // os dois meses importados chegam num envelope simbólico só
    // (qual lote representa o histórico é a questão 2 do §10, pendente)
    if (hist.length && !perfil.eventos['lote:historico-inicial']) {
      out.push({ id: 'lote:historico-inicial', type: 'card_batch_imported', profileId: perfil.perfil, competence: null,
        occurredAt: perfil.primeiro_acesso,
        payload: { lote: 'historico-inicial', historico: true,
          conciliacao: d.base === 'parcial' ? 'sem_fontes' : 'conciliado',
          falta: d.base === 'parcial' ? 'falta o cartão do último mês' : null, ambiguas: [], sintetico: true } });
    }
    return out;
  };

  d.lote = (tipo, hoje) => {
    const comp = hoje.slice(0, 7);
    const r = semente(`lote:${hoje}:${d.contador}`);
    const lote = `nubank-${hoje}-${d.contador}`;
    // a transação ambígua chega com o rótulo seguro e as duas categorias que
    // o motor de categorização ofereceria (template do roteiro v0.3)
    const ambiguas = tipo === 'ambiguo'
      ? [{ id: `tx-${lote}-1`, valor: redondo(120 + r() * 160) - 0.1,
        campos: { descricao_segura: 'Uma compra em loja online', categoria_a: 'Compras', categoria_b: 'Casa' } }]
      : [];
    return evento('card_batch_imported', {
      lote, historico: false,
      conciliacao: tipo === 'divergente' ? 'divergente' : (tipo === 'sem_fontes' ? 'sem_fontes' : 'conciliado'),
      diferenca: tipo === 'divergente' ? redondo(40 + r() * 120) - 0.5 : null,
      falta: tipo === 'sem_fontes' ? 'falta a planilha do mês' : null,
      ambiguas,
    }, comp);
  };

  d.pagamento = (hoje) => {
    const contas = ['Conta de luz', 'Internet', 'Condomínio', 'Plano do celular'];
    const conta = contas[d.contador % contas.length];
    return evento('payment_confirmed', { conta, valor: redondo(90 + (d.contador * 37) % 200) }, hoje.slice(0, 7));
  };

  d.teto = (limiar, comTeto, hoje) => evento('budget_threshold_crossed', {
    categoria: comTeto ? 'Delivery' : 'Lazer', limiar, teto: comTeto ? 400 : null, competencia: hoje.slice(0, 7),
  }, hoje.slice(0, 7));

  d.consulta = ({ valor, parcelas, veredito, regra }, hoje) => evento('purchase_consult_requested', {
    voluntaria: true, valor, parcelas, veredito, regra,
  }, hoje.slice(0, 7));

  d.competenciaDaReuniao = competenciaDaReuniao;
  return d;
}
