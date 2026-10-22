// O painel de teste, ao lado do escritório: simula a data, a base de dados
// e os eventos de domínio (sintéticos), roda os casos de aceite do roteiro
// e mostra o estado persistido e o registro do diretor. Não é o jogo: é a
// bancada para conferir as regras antes do módulo de dados real existir.

import { somarDias, primeiraReuniao, situacaoDaReuniao, situacaoDoPreAviso, hojeEmSaoPaulo } from './calendario.js';
import { BASES } from './dados.js';

const h = (tag, attrs = {}, ...filhos) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') e.className = v;
    else if (k === 'text') e.textContent = v;
    else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
    else if (v !== false && v != null) e.setAttribute(k, v === true ? '' : v);
  }
  for (const f of filhos) if (f != null) e.append(f);
  return e;
};
const botao = (texto, aoClicar, extra = {}) => h('button', { type: 'button', onclick: aoClicar, ...extra }, texto);
const dataBR = (d) => d.split('-').reverse().join('/');
const HORAS = [[9, 'manhã (9h)'], [15, 'tarde (15h)'], [20, 'noite (20h)']];

// casos de aceite: os do JSON v0.3 e mais três de ausência e adiamento
const CASOS = [
  { nome: '1º acesso 3/out, volta 17/out', passos: ['2026-10-03', '2026-10-17'],
    espera: 'Vivi na primeira visita; na volta, a reunião de 6/out abre direto, sem convite.' },
  { nome: '1º acesso 9/out, volta 17/out', passos: ['2026-10-09', '2026-10-17'],
    espera: 'Sem reunião de outubro; a primeira vence em 6/nov.' },
  { nome: '1º acesso 5/out, volta 6/out', passos: ['2026-10-05', '2026-10-06'],
    espera: 'Convite no dia 6, com a opção de adiar uma vez.' },
  { nome: '1º acesso 5/out, volta 8/out', passos: ['2026-10-05', '2026-10-08'],
    espera: 'Sem acesso no dia 6: a reunião pendente abre direto em 8/out.' },
  { nome: '1º acesso 6/out (pendente)', passos: ['2026-10-06', '2026-10-06'],
    espera: 'Pendência do autor: Vivi recebe, nenhuma reunião é assumida.' },
  { nome: '1º acesso 9/out, volta 1º/nov', passos: ['2026-10-09', '2026-11-01'],
    espera: 'Pré-aviso M0 para a reunião de 6/nov; nada inventado em outubro.' },
  { nome: 'Adiar no dia 6 e voltar no mesmo dia', passos: ['2026-10-05', '2026-10-06', '2026-10-06'],
    espera: 'No dia 6, escolha "Na próxima visita"; a volta abre a reunião direto, sem botão de adiar.' },
  { nome: 'Dia 1º sem visita, volta dia 3', passos: ['2026-10-09', '2026-11-03', '2026-11-06'],
    espera: 'Pré-aviso tardio no dia 3 (sem fingir o dia 1º); convite no dia 6.' },
  { nome: 'Ausência longa (3 reuniões)', passos: ['2026-10-03', '2026-12-10'],
    espera: 'A reunião mais antiga (setembro) abre direto; as outras vêm em seguida, uma por competência.' },
];

export function criarPainelDeTeste(api) {
  const { raiz, opcoes, salvarOpcoes, persistente } = api;
  let caso = null;
  let passo = 0;

  const registro = h('ol', { class: 'registro', 'aria-live': 'polite' });
  const estado = h('dl', { class: 'estado' });
  const dataInput = h('input', { type: 'date', id: 't-data', value: opcoes.data ?? hojeEmSaoPaulo() });
  const horaSel = h('select', { id: 't-hora' }, ...HORAS.map(([v, r]) => h('option', { value: v, text: r })));
  const casoInfo = h('p', { class: 'caso', hidden: true });
  const proximoBtn = botao('Próximo passo do caso', () => avancarCaso(), { class: 'primario', hidden: true });
  const visitaBtn = botao('Encerrar visita', () => (api.sessao()?.aberta ? api.encerrarVisita() : abrirNaData()));

  function definirData(d) {
    opcoes.data = d === hojeEmSaoPaulo() ? null : d;
    dataInput.value = d;
    salvarOpcoes();
  }
  function abrirNaData() {
    definirData(dataInput.value);
    opcoes.hora = Number(horaSel.value);
    salvarOpcoes();
    api.aplicar();
    api.abrirVisita();
  }
  async function visitarEm(d) {
    if (api.sessao()?.aberta) await api.encerrarVisita();
    definirData(d);
    opcoes.hora = Number(horaSel.value);
    salvarOpcoes();
    api.aplicar();
    api.abrirVisita();
  }
  function rodarCaso(c) {
    caso = c;
    passo = 0;
    api.zerarPerfil();
    visitarEm(c.passos[0]);
    mostrarCaso();
  }
  function avancarCaso() {
    if (!caso) return;
    passo += 1;
    if (passo >= caso.passos.length) { caso = null; mostrarCaso(); return; }
    visitarEm(caso.passos[passo]);
    mostrarCaso();
  }
  function mostrarCaso() {
    casoInfo.hidden = !caso;
    proximoBtn.hidden = !caso || passo >= caso.passos.length - 1;
    if (!caso) return;
    casoInfo.replaceChildren(h('strong', { text: caso.nome }), h('br'),
      h('span', { text: `Visita ${passo + 1} de ${caso.passos.length}: ${dataBR(caso.passos[passo])}.` }), h('br'),
      h('span', { class: 'espera', text: `Esperado: ${caso.espera}` }));
    if (!proximoBtn.hidden) proximoBtn.textContent = `Ir para ${dataBR(caso.passos[passo + 1])}`;
  }

  const lote = (tipo) => () => api.emitir(api.dados.lote(tipo, api.relogio().data));
  const statusPlanilha = h('p', { class: 'status-planilha', 'aria-live': 'polite' });
  const lerBtn = botao('Ler a planilha agora', () => api.relerPlanilha(), { class: 'primario' });
  const fonteSel = h('select', { id: 't-fonte', onchange: (e) => { opcoes.fonte = e.target.value; salvarOpcoes(); location.reload(); } },
    h('option', { value: 'planilha', text: 'Planilha do escritório (Google Sheets)', selected: opcoes.fonte === 'planilha' }),
    h('option', { value: 'sintetica', text: 'Dados sintéticos de teste', selected: opcoes.fonte !== 'planilha' }));

  const secao = (titulo, aberta, ...filhos) => h('details', { open: aberta }, h('summary', { text: titulo }), ...filhos);
  const campo = (rotulo, input) => h('label', { class: 'campo' }, h('span', { text: rotulo }), input);

  const baseSel = h('select', { id: 't-base', onchange: (e) => { opcoes.base = e.target.value; salvarOpcoes(); api.aplicar(); atualizar(); } },
    ...Object.entries(BASES).map(([k, v]) => h('option', { value: k, text: v, selected: opcoes.base === k })));
  const dia6Sel = h('select', { id: 't-dia6', onchange: (e) => { opcoes.regraDia6 = e.target.value || null; salvarOpcoes(); atualizar(); } },
    h('option', { value: '', text: 'pendente (não agenda reunião)', selected: !opcoes.regraDia6 }),
    h('option', { value: 'mesmo_mes', text: 'teste: vence no mesmo dia 6', selected: opcoes.regraDia6 === 'mesmo_mes' }),
    h('option', { value: 'mes_seguinte', text: 'teste: vence no mês seguinte', selected: opcoes.regraDia6 === 'mes_seguinte' }));
  const vel = h('input', { type: 'range', min: '0.4', max: '1.6', step: '0.1', value: String(opcoes.velocidade),
    oninput: (e) => { opcoes.velocidade = Number(e.target.value); salvarOpcoes(); api.aplicar(); velRot.textContent = `${opcoes.velocidade.toFixed(1)} tile/s`; } });
  const velRot = h('span', { class: 'mini', text: `${Number(opcoes.velocidade).toFixed(1)} tile/s` });
  const marcar = (rotulo, chave) => h('label', { class: 'check' },
    h('input', { type: 'checkbox', checked: Boolean(opcoes[chave]), onchange: (e) => { opcoes[chave] = e.target.checked; salvarOpcoes(); api.aplicar(); } }),
    h('span', { text: rotulo }));

  raiz.replaceChildren(
    h('h2', { text: 'Bancada de teste' }),
    h('p', { class: 'aviso-sintetico', text: api.naPlanilha
      ? 'Lendo a planilha real pelo conector Google Sheets, só leitura. Cada fonte tem o seu perfil salvo.'
      : 'Dados sintéticos: os eventos daqui fazem o papel da planilha. O perfil de teste é separado do real.' }),
    campo('Fonte dos dados', fonteSel),
    api.naPlanilha ? secao('Planilha', true, statusPlanilha, h('div', { class: 'botoes' }, lerBtn),
      h('p', { class: 'mini', text: 'Marque Pago, mude o cartão ou a Config na planilha e leia de novo: o que mudou vira cena. A planilha não guarda quando o Pago foi marcado, então a data é a da leitura.' })) : null,
    secao('Visita e data', true,
      h('div', { class: 'linha' }, campo('Data (São Paulo)', dataInput), campo('Hora', horaSel)),
      h('div', { class: 'botoes' },
        botao('Abrir visita nesta data', () => { if (api.sessao()?.aberta) api.encerrarVisita().then(abrirNaData); else abrirNaData(); }, { class: 'primario' }),
        visitaBtn,
        botao('+1 dia', () => { dataInput.value = somarDias(dataInput.value, 1); }),
        botao('+7 dias', () => { dataInput.value = somarDias(dataInput.value, 7); }),
        botao('Dia real', () => { dataInput.value = hojeEmSaoPaulo(); })),
      h('p', { class: 'mini', text: 'A data vale na próxima visita. Encerrar a visita no primeiro dia sem ação toca a despedida da C1S4.' })),
    secao('Casos de aceite', true,
      h('div', { class: 'casos' }, ...CASOS.map((c) => botao(c.nome, () => rodarCaso(c)))),
      casoInfo, proximoBtn),
    api.naPlanilha ? null : secao('Eventos de domínio', true,
      h('p', { class: 'mini', text: 'Com a visita aberta, a cena entra na fila; com o app fechado, o evento espera a próxima visita.' }),
      h('div', { class: 'botoes' },
        botao('Lote do cartão: confere', lote('conciliado')),
        botao('Lote: diferença', lote('divergente')),
        botao('Lote: gasto ambíguo', lote('ambiguo')),
        botao('Lote: falta fonte', lote('sem_fontes')),
        botao('Pagamento confirmado', () => api.emitir(api.dados.pagamento(api.relogio().data))),
        botao('Teto em 80%', () => api.emitir(api.dados.teto(80, true, api.relogio().data))),
        botao('Teto em 100%', () => api.emitir(api.dados.teto(100, true, api.relogio().data))),
        botao('Categoria sem teto', () => api.emitir(api.dados.teto(80, false, api.relogio().data)))),
      h('p', { class: 'mini', text: 'A consulta ao Caio e o resumo da semana são da pessoa: clique na mesa do Caio ou no quadro.' })),
    secao('Perfil e regras', false,
      api.naPlanilha ? null : campo('Base de dados', baseSel),
      campo('Primeiro acesso no dia 6', dia6Sel),
      h('p', { class: 'mini', text: 'A regra do dia 6 está pendente com o autor. As duas leituras aqui são só para testar.' }),
      campo('Velocidade de andar (nota 15.4)', h('span', { class: 'linha' }, vel, velRot)),
      marcar('Marcar falas provisórias no balão', 'marcarProvisorias'),
      marcar('Perfil sem permissão a dados (sem valores)', 'privado'),
      marcar('Movimento reduzido', 'reduzido'),
      marcar('Mostrar a planta no piso', 'planta'),
      h('div', { class: 'botoes' }, botao('Zerar perfil e abrir', () => { api.zerarPerfil(); abrirNaData(); }, { class: 'perigo' })),
      h('p', { class: 'mini', text: persistente ? 'O estado fica salvo neste navegador.' : 'Este navegador não deixa salvar: o estado dura até recarregar.' })),
    secao('Estado do perfil', true, estado),
    secao('Registro do diretor', true, registro),
    secao('Validação da planta', false,
      h('p', { id: 'veredito' }), h('ol', { id: 'regras' }), h('ul', { id: 'resumo' })),
  );
  horaSel.value = String(opcoes.hora ?? 15);

  function atualizar() {
    const p = api.perfil();
    const { data: hoje } = api.relogio();
    const s = api.sessao();
    visitaBtn.textContent = s?.aberta ? 'Encerrar visita' : 'Reabrir visita';
    const reuniao = situacaoDaReuniao(p, hoje);
    const aviso = situacaoDoPreAviso(p, hoje);
    const dia6 = p.primeiro_acesso ? primeiraReuniao(p.primeiro_acesso, opcoes.regraDia6) : null;
    const linhas = [
      ['Hoje', `${dataBR(hoje)}${opcoes.data ? ' (simulado)' : ''}`],
      ['Primeiro acesso', p.primeiro_acesso ? dataBR(p.primeiro_acesso) : '—'],
      ['Primeira reunião', p.primeira_reuniao === 'pendente' ? 'pendente (dia 6, decisão do autor)' : (p.primeira_reuniao ? dataBR(p.primeira_reuniao) : '—')
        + (dia6?.provisoria ? ' (regra de teste)' : '')],
      ['Reunião hoje', { nenhuma: `nenhuma (${reuniao.motivo})`, convite: `convite de ${reuniao.competencia}`,
        obrigatoria: `obrigatória: ${reuniao.competencia} (${reuniao.motivo}${reuniao.acumuladas > 1 ? `, ${reuniao.acumuladas} devidas` : ''})` }[reuniao.tipo]],
      ['Pré-aviso M0', { nenhum: '—', no_dia: `dia 1º (${aviso.competencia})`, tardio: `tardio (${aviso.competencia})`, nao_entregue: `não entregue (${aviso.competencia})` }[aviso.tipo]],
      ...Object.entries(p.reunioes).map(([c, r]) => [`Reunião ${c}`,
        [r.convite_mostrado_em && 'convite visto', r.adiada_em && 'adiada uma vez', r.iniciada_em && 'iniciada',
          r.concluida_em && `realizada; fechamento ${r.fechamento === 'fechado' ? 'confirmado' : 'pendente'}`,
          r.observacao && `intenção: ${r.observacao === 'player_confirms_observation_priority' ? 'acompanhar' : 'sem prioridade'}`]
          .filter(Boolean).join(' · ') || 'devida']),
      ['Cenas concluídas', Object.values(p.cenas).filter((c) => c.concluida_em).map((c) => c.cena).join(', ') || '—'],
      ['Eventos', `${Object.keys(p.eventos).length} registrados, ${Object.values(p.eventos).filter((e) => !e.processado_em).length} pendentes`],
      ['Resumo no quadro', p.resumo_disponivel ? `disponível desde ${dataBR(p.resumo_disponivel)}` : '—'],
      ['Visita', s?.aberta ? (s.atual ? `em cena: ${s.atual.cena}` : 'aberta, livre') : 'encerrada'],
    ];
    if (api.naPlanilha) {
      const f = api.fonte;
      const rot = { conciliado: 'confere', divergente: 'não bate', sem_fontes: 'incompleta' };
      statusPlanilha.textContent = {
        nao_lida: 'Ainda não lida.',
        lendo: 'Lendo a planilha…',
        erro: f.erro?.texto ?? 'A leitura falhou.',
        lida: `Lida às ${f.lidaEm?.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}. `
          + f.abas.map((a) => `${a.aba}: fatura ${rot[a.conferencia]}${a.leitorConfere === false ? ' (o cálculo do jogo difere do total da planilha)' : ''}`).join('; ')
          + (f.config?.reserva != null ? `. Reserva na Config: R$ ${f.config.reserva.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}.` : '. Reserva vazia na Config.'),
      }[f.estado];
      statusPlanilha.className = `status-planilha ${f.estado}`;
      lerBtn.disabled = f.estado === 'lendo';
    }
    estado.replaceChildren(...linhas.flatMap(([k, v]) => [h('dt', { text: k }), h('dd', { text: v })]));
  }

  function registrar(texto) {
    registro.append(h('li', { text: texto, class: texto.startsWith('━━') ? 'marco' : '' }));
    while (registro.children.length > 120) registro.firstChild.remove();
    registro.scrollTop = registro.scrollHeight;
  }

  return { atualizar, registrar };
}
