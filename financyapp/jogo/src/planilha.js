// Lê a planilha "Escritório de Finanças" e aplica as regras da aba Config.
// Tudo aqui é puro e determinístico (CLAUDE.md, regra 1: código decide):
// recebe os valores das abas como o Google Sheets devolve (texto
// formatado) e devolve o modelo de cada mês, a conferência do cartão e os
// eventos de domínio que mudaram desde a última leitura.
//
// Layout, pela Config: cartão Nubank em B:G, conta corrente em I:M, Digio
// em N:Q; cabeçalho na linha que começa com "Histórico"; cada aba é o mês
// de vencimento da fatura. Do cartão só contam os gastos do Guilherme e a
// metade do "2 X"; responsável vazio fica fora da divisão.

const MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto',
  'setembro', 'outubro', 'novembro', 'dezembro'];

const limpar = (s) => String(s ?? '').trim();
const chaveTexto = (s) => limpar(s).toUpperCase().replace(/\s+/g, ' ');

/** " R$  5.612,09 " -> 5612.09; " R$  -   " -> 0; "(835,00)" -> -835; "" -> null */
export function numero(s) {
  let t = limpar(s);
  if (!t) return null;
  const negativo = /^\(.*\)$/.test(t) || t.includes('(');
  t = t.replace(/R\$|\(|\)|\s/g, '');
  if (t === '-' || t === '') return 0;
  t = t.replace(/\./g, '').replace(',', '.');
  const v = Number(t);
  if (!Number.isFinite(v)) return null;
  return negativo ? -Math.abs(v) : v;
}
const verdade = (s) => limpar(s).toUpperCase() === 'TRUE';
const centavos = (v) => Math.round(v * 100);

/** "Outubro" + ano -> "2026-10" (ou null se não for um mês). */
export function competenciaDaAba(titulo, ano) {
  const i = MESES.indexOf(limpar(titulo).toLowerCase());
  return i < 0 ? null : `${ano}-${String(i + 1).padStart(2, '0')}`;
}
export const abaDaCompetencia = (comp) => {
  const m = MESES[Number(comp.slice(5, 7)) - 1];
  return m[0].toUpperCase() + m.slice(1);
};

/** Uma aba de mês: as três tabelas a partir da linha do cabeçalho. */
export function lerMes(valores, titulo, ano) {
  const linhas = valores ?? [];
  const cab = linhas.findIndex((l) => limpar(l?.[1]) === 'Histórico' && limpar(l?.[8]) === 'Histórico');
  const mes = { aba: titulo, competencia: competenciaDaAba(titulo, ano), cartao: [], conta: [], digio: [], legivel: cab >= 0 };
  if (cab < 0) return mes;
  // os totais que a própria planilha calcula, para conferir o leitor
  mes.resumo = {};
  for (const l of linhas.slice(0, cab)) {
    const rot = chaveTexto(l?.[3]);
    if (['GABRIEL', 'GUILHERME', '2 X', 'FORA DA DIVISÃO'].includes(rot)) mes.resumo[rot] = numero(l[4]);
    if (chaveTexto(l?.[8]) === 'A PAGAR') mes.resumo.A_PAGAR = numero(l[9]);
  }
  for (let i = cab + 1; i < linhas.length; i++) {
    const l = linhas[i] ?? [];
    const c = (k) => l[k];
    if (limpar(c(1)) && numero(c(3)) !== null) {
      mes.cartao.push({ linha: i + 1, historico: limpar(c(1)), categoria: limpar(c(2)), valor: numero(c(3)),
        parcelas: limpar(c(4)), responsavel: limpar(c(5)), conferido: verdade(c(6)) });
    }
    if (limpar(c(8))) {
      mes.conta.push({ linha: i + 1, historico: limpar(c(8)), data: limpar(c(9)),
        credito: numero(c(10)) ?? 0, debito: numero(c(11)) ?? 0, pago: verdade(c(12)) });
    }
    if (limpar(c(13))) {
      mes.digio.push({ linha: i + 1, historico: limpar(c(13)), data: limpar(c(14)), valor: numero(c(15)) ?? 0,
        responsavel: limpar(c(16)) });
    }
  }
  return mes;
}

/** As regras do cartão (Config): parte do Guilherme = os gastos dele + metade do 2 X. */
/** O leitor bate com os totais da planilha? (null se a planilha não tem o total) */
export function leitorConfere(mes) {
  const p = partesDoCartao(mes.cartao);
  const gui = mes.resumo?.GUILHERME;
  if (gui == null) return null;
  return Math.abs(centavos(gui) - centavos(p.guilherme)) <= 1;
}

export function partesDoCartao(cartao) {
  let gui = 0;
  let gab = 0;
  let dois = 0;
  let fora = 0;
  for (const r of cartao) {
    const resp = chaveTexto(r.responsavel);
    if (resp === 'GUILHERME') gui += r.valor;
    else if (resp === 'GABRIEL') gab += r.valor;
    else if (resp === '2 X') dois += r.valor;
    else if (!resp) fora += r.valor;
  }
  return { guilherme: gui + dois / 2, gabriel: gab + dois / 2, doisX: dois, fora, total: gui + gab + dois + fora };
}

const linhaDaConta = (mes, nome) => mes.conta.find((r) => chaveTexto(r.historico) === nome);

/**
 * A conferência de um mês: a linha CARTÃO NUBANK da conta bate com a
 * parte do Guilherme no cartão? E a CARTÃO DIGIO com os lançamentos do
 * Guilherme no Digio? Devolve { estado, diferenca, falta }.
 */
export function conferencia(mes) {
  if (!mes.legivel) return { estado: 'sem_fontes', diferenca: null, falta: 'a aba não tem as tabelas no lugar' };
  const falta = [];
  const nubank = linhaDaConta(mes, 'CARTÃO NUBANK');
  let diferenca = 0;
  if (!mes.cartao.length) falta.push('o lote do cartão');
  else if (!nubank || !nubank.debito) falta.push('a linha CARTÃO NUBANK na conta');
  else diferenca += Math.abs(centavos(nubank.debito) - centavos(partesDoCartao(mes.cartao).guilherme));
  const digio = linhaDaConta(mes, 'CARTÃO DIGIO');
  const doDigio = mes.digio.filter((r) => chaveTexto(r.responsavel) === 'GUILHERME').reduce((s, r) => s + r.valor, 0);
  if (digio && mes.digio.length) diferenca += Math.abs(centavos(digio.debito) - centavos(doDigio));
  if (falta.length) return { estado: 'sem_fontes', diferenca: null, falta: `falta ${falta.join(' e ')}` };
  if (diferenca > 1) return { estado: 'divergente', diferenca: diferenca / 100, falta: null };
  return { estado: 'conciliado', diferenca: null, falta: null };
}

/**
 * Gastos do Guilherme (ou 2 X) sem categoria. As duas opções vêm do
 * próprio histórico da planilha: a categoria já usada no mesmo nome e,
 * em seguida, a mais usada no mês (regra PROPOSTA; sem duas opções, a
 * pergunta não é feita).
 */
export function semCategoria(mes) {
  const doEscopo = (r) => ['GUILHERME', '2 X'].includes(chaveTexto(r.responsavel));
  const usadas = new Map();
  for (const r of mes.cartao) if (r.categoria && doEscopo(r)) usadas.set(r.categoria, (usadas.get(r.categoria) ?? 0) + 1);
  const ranking = [...usadas.entries()].sort((a, b) => b[1] - a[1]).map(([c]) => c);
  const out = [];
  for (const r of mes.cartao) {
    if (r.categoria || !doEscopo(r) || !(r.valor > 0)) continue;
    const doNome = mes.cartao.filter((x) => x !== r && x.categoria && chaveTexto(x.historico) === chaveTexto(r.historico))
      .map((x) => x.categoria);
    const opcoes = [...new Set([...doNome, ...ranking])].slice(0, 2).map((c) => c.replace(/^[^\p{L}]+/u, '').trim());
    out.push({ id: `cat:${mes.aba}:${chaveTexto(r.historico)}:${centavos(r.valor)}`, valor: r.valor,
      campos: opcoes.length === 2 ? { descricao_segura: r.historico, categoria_a: opcoes[0], categoria_b: opcoes[1] } : null });
  }
  return out;
}

/** A aba Config: o saldo da reserva e o guardado por mês. */
export function lerConfig(valores) {
  const linhas = valores ?? [];
  const achar = (rotulo) => {
    const l = linhas.find((x) => chaveTexto(x?.[0]) === chaveTexto(rotulo));
    return l ? numero(l[1]) : null;
  };
  return { reserva: achar('Saldo da reserva'), antes: achar('Saldo antes do escritório') };
}

/** O resumo de um mês para o quadro da reunião. Ausência fica null, nunca zero. */
export function relatorioDoMes(mes, config, competencia) {
  if (!mes || !mes.legivel) {
    return { competencia, situacao: 'sem_dados', entradas: null, saidas: null, saidasConta: null, saidasCartao: null,
      resultado: null, compromissos: null, reserva: config?.reserva ?? null, faltando: ['a aba do mês'], sintetico: false };
  }
  const conf = conferencia(mes);
  const ehCartao = (r) => chaveTexto(r.historico).startsWith('CARTÃO ');
  const pagas = mes.conta.filter((r) => r.pago && r.debito > 0);
  const entradas = mes.conta.filter((r) => r.pago && r.credito > 0).reduce((s, r) => s + r.credito, 0);
  const saidasConta = pagas.filter((r) => !ehCartao(r)).reduce((s, r) => s + r.debito, 0);
  const saidasCartao = pagas.filter(ehCartao).reduce((s, r) => s + r.debito, 0);
  const abertas = mes.conta.filter((r) => !r.pago && r.debito > 0);
  const completa = conf.estado === 'conciliado' && !abertas.length;
  const faltando = [];
  if (conf.estado !== 'conciliado') faltando.push(conf.estado === 'divergente' ? 'a fatura do cartão não bate com a conta' : conf.falta);
  if (abertas.length) faltando.push(`${abertas.length} conta${abertas.length > 1 ? 's' : ''} sem Pago`);
  return {
    competencia, situacao: completa ? 'completa' : 'parcial', sintetico: false,
    entradas, saidasConta, saidasCartao, saidas: saidasConta + saidasCartao,
    resultado: completa ? entradas - saidasConta - saidasCartao : null,
    compromissos: abertas.map((r) => ({ item: r.historico, valor: r.debito })),
    reserva: config?.reserva ?? null, faltando,
    foco: completa ? 'as saídas do cartão' : 'o que falta marcar como pago',
  };
}

// ---------------------------------------------------------------------
// O instantâneo da última leitura e os eventos que mudaram desde ele.

const assinatura = (linhas) => {
  let h = 2166136261;
  for (const ch of JSON.stringify(linhas)) h = Math.imul(h ^ ch.charCodeAt(0), 16777619);
  return (h >>> 0).toString(36);
};

/** Chave estável de uma linha da conta (sobrevive a linhas inseridas acima). */
function chavesDaConta(mes) {
  const vistos = new Map();
  return mes.conta.map((r) => {
    const base = `${mes.aba}:${chaveTexto(r.historico)}:${r.data}:${centavos(r.credito)}:${centavos(r.debito)}`;
    const n = (vistos.get(base) ?? 0) + 1;
    vistos.set(base, n);
    return { r, chave: `${base}:${n}` };
  });
}

export function instantaneo(meses) {
  const s = { lotes: {}, contas: {} };
  for (const m of meses) {
    s.lotes[m.aba] = assinatura(m.cartao.map((r) => [r.historico, r.valor, r.responsavel, r.categoria]));
    for (const { r, chave } of chavesDaConta(m)) s.contas[chave] = r.pago;
  }
  return s;
}

/**
 * Os eventos de domínio entre a leitura anterior e esta (§5 da direção).
 * Ids determinísticos: desmarcar e marcar de novo não gera evento novo.
 * Primeira leitura: os lotes que já existem chegam num envelope só,
 * marcado como histórico, e nada da conta vira "pagamento de hoje".
 */
export function eventosDaLeitura({ meses, config }, anterior, { hoje, perfilId = 'guilherme' } = {}) {
  const agora = instantaneo(meses);
  const evs = [];
  const ev = (id, type, payload, competence = null) => ({
    id, type, profileId: perfilId, competence, occurredAt: hoje, payload: { ...payload, sintetico: false },
  });
  const ambiguas = (m) => semCategoria(m).filter((t) => t.campos);
  if (!anterior) {
    const comLote = meses.filter((m) => m.cartao.length);
    if (comLote.length) {
      const confs = comLote.map(conferencia);
      const pior = confs.find((c) => c.estado === 'divergente') ?? confs.find((c) => c.estado === 'sem_fontes') ?? confs[0];
      evs.push(ev(`lote:planilha-inicial`, 'card_batch_imported', {
        lote: 'planilha-inicial', historico: true, conciliacao: { conciliado: 'conciliado', divergente: 'divergente', sem_fontes: 'sem_fontes' }[pior.estado],
        diferenca: confs.reduce((s, c) => s + (c.diferenca ?? 0), 0) || null, falta: pior.falta,
        ambiguas: comLote.flatMap(ambiguas),
      }));
    }
    return { eventos: evs, instantaneo: agora };
  }
  for (const m of meses) {
    if (m.cartao.length && anterior.lotes?.[m.aba] !== agora.lotes[m.aba]) {
      const c = conferencia(m);
      const lote = `fatura-${m.aba.toLowerCase()}-${agora.lotes[m.aba]}`;
      evs.push(ev(`lote:${lote}`, 'card_batch_imported', {
        lote, historico: false, conciliacao: c.estado, diferenca: c.diferenca, falta: c.falta, ambiguas: ambiguas(m),
      }, m.competencia));
    }
    for (const { r, chave } of chavesDaConta(m)) {
      const antes = anterior.contas?.[chave];
      if (r.pago && antes === false) {
        evs.push(ev(`pago:${chave}`, 'payment_confirmed', { conta: r.historico, valor: r.debito || r.credito, entrada: r.credito > 0 }, m.competencia));
      } else if (antes === undefined) {
        evs.push(ev(`novo:${chave}`, 'account_updated', { conta: r.historico, valor: r.debito || r.credito }, m.competencia));
      }
    }
  }
  return { eventos: evs, instantaneo: agora };
}

/** Lê o título "Controle de Gastos 2026" para saber o ano das abas. */
export function anoDaAba(valores, padrao) {
  const m = limpar(valores?.[0]?.[0]).match(/(20\d\d)/);
  return m ? Number(m[1]) : padrao;
}
