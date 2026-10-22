// O conteúdo dos painéis que as cenas abrem: o quadro da reunião (três
// cartões), o detalhe da conciliação, a consulta ao Caio, o card de 30 s e
// o livro do mês do Saldanha. Os números vêm do módulo de dados (hoje,
// sintéticos e marcados assim). Ausência aparece como ausência, nunca zero.

import { brl } from './dados.js';
import { nomeDoMes } from './calendario.js';
import { partesDoCartao, conferencia } from './planilha.js';

// Com a planilha como fonte, os painéis não levam o selo de sintético.
let real = false;
export const usarDadosReais = (v) => { real = Boolean(v); };

const el = (tag, attrs = {}, ...filhos) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') e.className = v;
    else if (k === 'text') e.textContent = v;
    else e.setAttribute(k, v);
  }
  for (const f of filhos) if (f) e.append(f);
  return e;
};
const valor = (v, privado) => (v == null ? 'sem informação' : (privado ? '•••' : brl(v)));
const Mes = (c) => { const m = nomeDoMes(c); return `${m[0].toUpperCase()}${m.slice(1)} de ${c.slice(0, 4)}`; };

function linhas(pares, privado) {
  const dl = el('dl', { class: 'linhas' });
  for (const [rotulo, v, nota] of pares) {
    const dd = el('dd', { text: typeof v === 'string' ? v : valor(v, privado) });
    if (v == null) dd.classList.add('ausente');
    dl.append(el('dt', { text: rotulo }), dd);
    if (nota) dl.append(el('dd', { class: 'nota', text: nota }));
  }
  return dl;
}

/** O quadro da reunião: fluxo, compromissos e reserva, um cartão por vez. */
export function relatorio(ui, r, { privado }) {
  const parcial = r.situacao !== 'completa';
  const cartoes = [
    { titulo: '1. O que entrou e saiu?', corpo: () => linhas([
      ['Entrou', r.entradas],
      ['Saiu da conta', r.saidasConta],
      ['Saiu no cartão', r.saidasCartao, r.saidasCartao == null && r.situacao === 'parcial' ? 'o lote do cartão ainda não chegou' : null],
      ['Resultado do mês', r.resultado, r.resultado == null ? 'só com a base completa' : null],
    ], privado) },
    { titulo: '2. O que ainda está comprometido?', corpo: () => (r.compromissos
      ? linhas(r.compromissos.map((c) => [c.item, c.valor]).concat(parcial ? [['Fatura do cartão', null, 'pendente: falta o lote']] : []), privado)
      : el('p', { class: 'ausente', text: 'Sem informação suficiente para listar compromissos.' })) },
    { titulo: '3. Como está a reserva?', corpo: () => linhas([
      ['Reserva conferida', r.reserva],
      ['Colchão de caixa (regra aprovada)', 1000],
    ], privado) },
  ];
  return ui.painel({
    sintetico: !real,
    titulo: `Reunião de ${Mes(r.competencia)}`,
    rotuloFechar: 'Fechar o quadro',
    montar: (corpo, fechar) => {
      let i = 0;
      const situacao = el('p', { class: `situacao ${r.situacao}`,
        text: { completa: 'Base completa', parcial: 'Base parcial: o que falta fica marcado como pendente', sem_dados: 'Sem informação suficiente: estado legítimo, sem número inventado' }[r.situacao] });
      const area = el('div', { class: 'cartao-quadro', 'aria-live': 'polite' });
      const anterior = el('button', { type: 'button', text: '◀ Anterior' });
      const proximo = el('button', { type: 'button', class: 'primario', text: 'Próximo ▶' });
      const pos = el('span', { class: 'pos' });
      const desenhar = () => {
        area.replaceChildren(el('h4', { text: cartoes[i].titulo }), cartoes[i].corpo());
        anterior.disabled = i === 0;
        pos.textContent = `${i + 1} de ${cartoes.length}`;
        proximo.textContent = i === cartoes.length - 1 ? 'Concluir o quadro' : 'Próximo ▶';
      };
      anterior.addEventListener('click', () => { i = Math.max(0, i - 1); desenhar(); });
      proximo.addEventListener('click', () => { if (i === cartoes.length - 1) fechar(); else { i += 1; desenhar(); } });
      corpo.append(situacao, area, el('nav', { class: 'navegar' }, anterior, pos, proximo));
      desenhar();
      return false;
    },
  });
}

export function conciliacao(ui, c, { privado }) {
  return ui.painel({
    sintetico: !real,
    titulo: 'Conferência do lote',
    montar: (corpo) => {
      corpo.append(linhas([
        ['Lote', c.lote ?? '—'],
        ['Fontes comparadas', 'lote do cartão × planilha'],
        ['Diferença calculada', c.diferenca ?? null],
        ['Estado', 'divergente, sinalizado para depois'],
      ], privado), el('p', { class: 'nota', text: 'A diferença vem do cálculo da conciliação, não da conversa. Ela continua visível até as fontes baterem.' }));
    },
  });
}

/** A consulta ao Caio: o que comprar e como pagar; o veredito é do motor. */
export function consulta(ui) {
  const motivos = {
    verde: 'Cabe no mês sem tocar no colchão de R$ 1.000',
    amarelo: 'As parcelas chegam perto de 15% da renda',
    vermelho: 'O saldo projetado fica abaixo do colchão de R$ 1.000',
    insuficiente: '',
  };
  return ui.painel({
    sintetico: true,
    titulo: 'Consulta ao Caio',
    montar: (corpo, fechar) => {
      const form = el('form', { class: 'form' });
      const item = el('input', { id: 'c-item', type: 'text', placeholder: 'Ex.: cadeira de escritório', required: '' });
      const val = el('input', { id: 'c-valor', type: 'number', min: '1', step: '0.01', placeholder: '0,00', required: '' });
      const forma = el('select', { id: 'c-forma' },
        ...['à vista', '2x', '3x', '6x', '10x', '12x'].map((f) => el('option', { value: f, text: f })));
      const ver = el('select', { id: 'c-veredito' },
        el('option', { value: 'verde', text: 'verde' }), el('option', { value: 'amarelo', text: 'amarelo' }),
        el('option', { value: 'vermelho', text: 'vermelho' }), el('option', { value: 'insuficiente', text: 'dados insuficientes' }));
      const motivo = el('input', { id: 'c-motivo', type: 'text', value: motivos.verde });
      ver.addEventListener('change', () => { motivo.value = motivos[ver.value]; });
      const campo = (rotulo, input) => el('label', {}, el('span', { text: rotulo }), input);
      const teste = el('fieldset', { class: 'teste' }, el('legend', { text: 'Veredito sintético (o motor de regras do Caio ainda não existe)' }),
        campo('Veredito', ver), campo('Motivo curto', motivo));
      const cancelar = el('button', { type: 'button', text: 'Agora não' });
      const enviar = el('button', { type: 'submit', class: 'primario', text: 'Perguntar ao Caio' });
      cancelar.addEventListener('click', () => fechar(null));
      form.addEventListener('submit', (ev) => {
        ev.preventDefault();
        const v = ver.value === 'insuficiente' ? null : ver.value;
        fechar({ item: item.value.trim(), valor: Number(val.value), forma: forma.value,
          veredito: v, motivo_curto: v ? motivo.value.trim().replace(/\.$/, '') : null });
      });
      form.append(campo('O que você está pensando em comprar?', item), campo('Valor (R$)', val),
        campo('Como pretende pagar?', forma), teste, el('footer', {}, cancelar, enviar));
      corpo.append(form);
      return false;
    },
  });
}

export function card(ui, c) {
  return ui.painel({
    sintetico: !real,
    titulo: 'Explicação de 30 segundos',
    montar: (corpo) => {
      corpo.append(linhas([
        ['Categoria', c.categoria],
        ['Limiar alcançado', `${c.limiar}% do teto`],
        ['Teto registrado', c.teto],
      ], c.privado), el('p', { class: 'nota', text: 'O texto educativo deste card ainda não foi escrito (GDD, educação nas reuniões e pílulas). Aqui fica o lugar dele.' }));
    },
  });
}

/** O livro do mês do Saldanha: só o que está registrado. */
export function livro(ui, perfil, dados) {
  return ui.painel({
    sintetico: !real,
    titulo: 'Livro do mês',
    rotuloFechar: 'Fechar o livro',
    montar: (corpo) => {
      const hist = perfil.primeiro_acesso ? dados.historico(perfil.primeiro_acesso) : [];
      const privado = dados.privado;
      const lista = (titulo, itens, vazio) => el('section', {}, el('h4', { text: titulo }),
        itens.length ? el('ul', {}, ...itens.map((t) => el('li', { text: t }))) : el('p', { class: 'ausente', text: vazio }));
      const rotuloLote = { recebido: 'recebido, não conferido', conferido: 'conferido', sinalizado: 'divergente, sinalizado', parcial: 'parcial: falta fonte' };
      if (dados.nome === 'planilha') corpo.append(...daPlanilha(dados, privado));
      corpo.append(
        lista('Períodos do histórico', hist.map((m) => `${Mes(m.competencia)}: ${m.conferido ? 'conferido' : `pendente (falta ${m.falta})`}`), 'Nenhum histórico importado.'),
        lista('Lotes do cartão', Object.entries(perfil.lotes).map(([id, l]) => `${id}: ${rotuloLote[l.estado] ?? l.estado}`), 'Nenhum lote recebido.'),
        lista('Categorias a confirmar', Object.values(perfil.categorias).filter((c) => !c.categoria)
          .map((c) => `${c.descricao}: aguardando sua resposta`), 'Nada a confirmar.'),
        lista('Reuniões', Object.entries(perfil.reunioes).map(([comp, r]) => `${Mes(comp)}: ${r.concluida_em ? `realizada, fechamento ${r.fechamento === 'fechado' ? 'confirmado' : 'pendente'}` : (r.adiada_em ? 'adiada uma vez' : 'devida')}`), 'Nenhuma reunião ainda.'),
      );
    },
  });
}

/** O que o Saldanha leu da planilha: um bloco por aba de mês e a reserva. */
function daPlanilha(fonte, privado) {
  const v = (x) => valor(x, privado);
  if (fonte.estado !== 'lida') {
    return [el('section', {}, el('h4', { text: 'Planilha' }),
      el('p', { class: 'ausente', text: fonte.estado === 'lendo' ? 'Lendo a planilha…' : (fonte.erro?.texto ?? 'A planilha ainda não foi lida.') }))];
  }
  const rotulo = { conciliado: 'confere com a conta', divergente: 'não bate com a conta', sem_fontes: 'incompleta' };
  const blocos = fonte.meses.map((m) => {
    const titulo = m.competencia ? `${Mes(m.competencia)} (aba ${m.aba})` : `Aba ${m.aba}`;
    if (!m.legivel) return el('section', {}, el('h4', { text: titulo }), el('p', { class: 'ausente', text: 'As tabelas desta aba não estão no lugar esperado.' }));
    const c = conferencia(m);
    const partes = partesDoCartao(m.cartao);
    const comDebito = m.conta.filter((r) => r.debito > 0);
    const pagas = comDebito.filter((r) => r.pago).length;
    const entradas = m.conta.filter((r) => r.credito > 0).reduce((s, r) => s + r.credito, 0);
    const saidas = comDebito.reduce((s, r) => s + r.debito, 0);
    return el('section', {}, el('h4', { text: titulo }), linhas([
      ['Fatura do cartão', `${m.cartao.length} lançamentos, ${rotulo[c.estado]}`,
        c.estado === 'divergente' ? `diferença de ${v(c.diferenca)}` : (c.falta ?? null)],
      ['Sua parte no cartão', partes.guilherme, 'seus lançamentos mais metade dos "2 X"'],
      ['Entradas previstas na conta', entradas],
      ['Saídas previstas na conta', saidas],
      ['Contas pagas', `${pagas} de ${comDebito.length}`],
    ], privado));
  });
  blocos.push(el('section', {}, el('h4', { text: 'Reserva' }), linhas([['Saldo da reserva (Config)', fonte.config?.reserva ?? null]], privado)));
  const hora = fonte.lidaEm?.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', timeZone: 'America/Sao_Paulo' });
  blocos.unshift(el('p', { class: 'nota', text: `Lido da planilha às ${hora}. Só leitura: nada é escrito nela.` }));
  return blocos;
}
