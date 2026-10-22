// Liga tudo: carrega a arte, a planta e o roteiro; monta o escritório vivo
// (sala, elenco, executor, balões); abre a visita do dia; e passa os
// eventos de domínio pelo diretor narrativo até virarem cena.
//
//   dado validado -> evento -> diretor (elegibilidade, prioridade, unicidade)
//     -> fila -> executor no mapa 2D -> registro de visto/pendente/concluído
//
// Os dados vêm da planilha (fonte_planilha.js, pelo conector Google Sheets)
// ou do gerador sintético da bancada (dados.js); os dois geram os mesmos
// eventos de domínio.

import { carregarTudo } from './carregar.js';
import { criarSala, tamanhoDaSala } from './sala.js';
import { validar, resumo } from './validacao.js';
import { criarGrade } from './caminho.js';
import { Ator, sentarJa, config } from './atores.js';
import { criarExecutor } from './executor.js';
import { criarUI } from './ui.js';
import { CENAS, ROTEIRO_URL } from './roteiro.js';
import * as paineis from './paineis.js';
import { criarDados } from './dados.js';
import { criarFontePlanilha } from './fonte_planilha.js';
import { hojeEmSaoPaulo, horaEmSaoPaulo, partes, competenciaDaReuniao, mesmaSemana } from './calendario.js';
import { armazemDoNavegador, carregarPerfil, salvarPerfil, apagarPerfil, carimbo } from './estado.js';
import {
  abrirVisita, planejarEvento, planejarReuniao, registrarInicio, registrarConclusao, registrarEvento,
  ordenar, deduplicar, CHAVES, PRIORIDADE,
} from './diretor.js';
import { criarPainelDeTeste } from './painel.js';

const ESCALA = 2;
const HUMANOS = ['guilherme', 'saldanha', 'caio', 'vivi', 'gabriel'];
const CAES = { flora: 'manta_flora', lupin: 'caminha_lupin' };
// a vida à mesa de quem trabalha no posto (nota 15.5: quem usa é regra do jogo)
const VIDA = {
  saldanha: { bases: ['teclando_frente', 'teclando_frente', 'sentado_frente_idle', 'digitando_sentado'], gestos: ['assentindo_para_tela_frente'] },
  vivi: { bases: ['sentado_frente_idle', 'teclando_frente'], gestos: ['olhando_para_o_lado_frente'] },
  caio: { bases: ['sentado_frente_idle', 'sentado_frente_idle', 'teclando_frente'], gestos: ['olhando_para_o_lado_frente', 'assentindo_para_tela_frente'] },
  guilherme: { bases: ['sentado_frente_idle', 'teclando_frente'], gestos: [] },
};

async function carregarJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`não carregou ${url} (${r.status})`);
  return r.json();
}

function mostrarValidacao(layout) {
  const v = validar(layout);
  const item = (texto, classe) => {
    const li = document.createElement('li');
    li.textContent = texto;
    if (classe) li.className = classe;
    return li;
  };
  const lista = document.getElementById('regras');
  lista.replaceChildren(...v.regras.map((r) => item(`${r.ok ? '✓' : '✗'} ${r.numero}. ${r.texto}`, r.ok ? 'ok' : 'falha')));
  const r = resumo(layout);
  document.getElementById('veredito').textContent = v.ok ? 'O layout passa nas seis regras.' : 'O layout não passa: veja as regras marcadas.';
  document.getElementById('veredito').className = v.ok ? 'ok' : 'falha';
  document.getElementById('resumo').replaceChildren(
    item(`${r.livres} tiles livres, ${r.alcancaveis} alcançáveis a partir da entrada`),
    item(`${r.circulacao} de circulação obrigatória, ${r.decorar} livres para decorar`),
  );
}

async function iniciar() {
  const canvas = document.getElementById('sala');
  const palco = document.getElementById('palco');
  const raiz = document.getElementById('jogo');
  const { assets, layout: urlLayout, roteiro: urlRoteiro } = raiz.dataset;
  let dadosArte;
  let roteiro;
  try {
    [dadosArte, roteiro] = await Promise.all([
      carregarTudo({ assets, layout: urlLayout }),
      carregarJSON(urlRoteiro ?? ROTEIRO_URL),
    ]);
  } catch (erro) {
    const aviso = document.getElementById('erro');
    aviso.hidden = false;
    aviso.textContent = `${erro.message}. Abra a página pelo servidor local: na pasta financyapp, rode `
      + '"python3 -m http.server 8000" e acesse http://localhost:8000/jogo/.';
    return;
  }
  const { manifesto, layout } = dadosArte;

  // ---- a sala
  const sala = criarSala(dadosArte);
  const { largura, altura } = tamanhoDaSala(layout, manifesto);
  canvas.width = largura;
  canvas.height = altura;
  let escala = ESCALA;
  const ajustarEscala = () => {
    escala = raiz.clientWidth >= canvas.width * ESCALA ? ESCALA : 1;
    canvas.style.width = `${canvas.width * escala}px`;
    canvas.style.height = `${canvas.height * escala}px`;
  };
  ajustarEscala();
  window.addEventListener('resize', ajustarEscala);
  const ctx2d = canvas.getContext('2d');

  // ---- opções do teste e relógio simulado
  const { armazem, persistente } = armazemDoNavegador();
  const lerOpcoes = () => {
    try { return JSON.parse(armazem.getItem('financyapp:teste') ?? '{}'); } catch { return {}; }
  };
  const opcoes = {
    data: null, hora: null, base: 'dois_meses', privado: false, regraDia6: null,
    fonte: 'planilha', velocidade: 1.0, marcarProvisorias: true, reduzido: false, planta: false, ...lerOpcoes(),
  };
  const salvarOpcoes = () => { try { armazem.setItem('financyapp:teste', JSON.stringify(opcoes)); } catch { /* segue */ } };
  const reduzidoDoSistema = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  config.velocidade = opcoes.velocidade;
  config.reduzido = opcoes.reduzido || reduzidoDoSistema;
  const relogio = () => ({ data: opcoes.data ?? hojeEmSaoPaulo(), hora: opcoes.hora ?? horaEmSaoPaulo() });

  // a fonte dos dados: a planilha real (padrão) ou o gerador sintético da bancada
  const sinteticos = criarDados();
  sinteticos.base = opcoes.base;
  sinteticos.privado = opcoes.privado;
  const naPlanilha = opcoes.fonte === 'planilha';
  const dados = naPlanilha ? criarFontePlanilha() : sinteticos;
  dados.privado = opcoes.privado;
  // O perfil real começa limpo: até a v3 o perfil "guilherme" guardava o
  // progresso dos dados sintéticos, então ele vira o perfil de teste.
  const perfilId = naPlanilha ? 'guilherme-planilha' : 'guilherme-teste';
  try {
    const velho = armazem.getItem('financyapp:perfil:guilherme');
    if (velho && !armazem.getItem('financyapp:perfil:guilherme-teste')) {
      const p = JSON.parse(velho); p.perfil = 'guilherme-teste';
      armazem.setItem('financyapp:perfil:guilherme-teste', JSON.stringify(p));
    }
    if (velho) armazem.removeItem('financyapp:perfil:guilherme');
  } catch { /* sem armazém: nada a migrar */ }
  paineis.usarDadosReais(naPlanilha);
  // o conector só existe dentro do claude.ai; fora dele, use() devolve null
  const mcpPronto = naPlanilha ? Promise.resolve(window.claude?.use?.('mcp') ?? null).catch(() => null) : Promise.resolve(null);

  // ---- o elenco
  const elenco = new Map();
  for (const id of HUMANOS) elenco.set(id, new Ator(id, manifesto[id]));
  for (const id of Object.keys(CAES)) elenco.set(id, new Ator(id, manifesto[id], { cao: true }));
  const pecas = Object.fromEntries(layout.pecas_piso.map((p) => [p.id, p]));
  const cadeiraDe = (id) => layout.pecas_piso.find((p) => p.tipo === 'cadeira' && p.zona !== 'reuniao'
    && (p.ocupante_padrao ?? '').toLowerCase() === id);
  const cadeiraDaReuniao = (id) => layout.pecas_piso.find((p) => p.tipo === 'cadeira' && p.zona === 'reuniao'
    && (p.ocupante_padrao ?? '').toLowerCase() === id);
  const t0 = performance.now() / 1000;
  const agora = () => performance.now() / 1000 - t0;

  function posicionarElenco({ guilhermeNaPorta = false } = {}) {
    for (const a of elenco.values()) {
      a.caminho?.resolve();
      a.caminho = null;
      a.umaVez = null;
      a.emCena = false;
      a.falando = false;
      a.envelope = false;
      a.selo = null;
      a.base = null;
      if (a.cao) {
        a.cama = pecas[CAES[a.id]];
        a.visivel = true;
        a.base = 'dormindo_na_cama';
        a.definir(a.base, agora());
        continue;
      }
      const c = cadeiraDe(a.id);
      if (c) sentarJa(a, c, agora());
      else { a.visivel = false; a.cadeira = null; }
    }
    if (guilhermeNaPorta) elenco.get('guilherme').visivel = false;
  }

  // ---- estado do jogo
  let perfil = carregarPerfil(armazem, perfilId);
  const salvar = () => salvarPerfil(armazem, perfil);
  let sessao = null;
  const objetosCena = {};
  const brilhos = new Map();

  const jogo = {
    elenco, layout, grade: criarGrade(layout), agora, cadeiraDe, cadeiraDaReuniao,
    ui: null,
    objetoDaCena(alvo, estado) {
      if (estado == null) delete objetosCena[alvo];
      else objetosCena[alvo] = estado;
    },
    brilhar(ids, ms) {
      for (const id of [].concat(ids)) brilhos.set(id, agora() + ms / 1000);
    },
    abrirPainel: async (nome, ctx) => {
      if (nome === 'relatorio') await paineis.relatorio(jogo.ui, ctx.relatorio, ctx);
      if (nome === 'conciliacao') await paineis.conciliacao(jogo.ui, ctx, ctx);
      if (nome === 'card') await paineis.card(jogo.ui, ctx);
      if (nome === 'consulta') {
        ctx.consulta = await paineis.consulta(jogo.ui);
        if (ctx.consulta) emitirSilencioso(sinteticos.consulta(ctx.consulta, relogio().data), ctx);
      }
    },
    aoResultado: (inv, ctx, cmd) => aplicarResultado(inv, ctx, cmd),
    aoMarco: (inv, ctx, id) => marco(inv, ctx, id),
    aoMarcarCena: (inv, cmd) => painel?.registrar(`  ↳ ${cmd.cena} · ${cmd.titulo}${cmd.variantes.length ? ` · variante ${cmd.variantes.join(', ')}` : ''}`),
  };
  const ui = criarUI({ palco, sala, escala: () => escala, elenco, opcoes });
  jogo.ui = ui;
  const executor = criarExecutor(jogo);

  // ---- estados dos objetos que vêm do perfil (o domínio), mais os da cena
  function objetosBase() {
    const { data: hoje } = relogio();
    const o = {};
    const lotes = Object.values(perfil.lotes);
    const ultimo = lotes.at(-1);
    if (ultimo) o.malote = { recebido: 'com-envelope', parcial: 'com-envelope', sinalizado: 'sinalizado', conferido: 'vazio' }[ultimo.estado];
    const mesAtual = hoje.slice(0, 7);
    const eventos = Object.values(perfil.eventos);
    if (eventos.some((e) => e.tipo === 'payment_confirmed' && (e.competencia ?? '') === mesAtual)) o.calendario = 'marcado';
    const tetos = eventos.filter((e) => e.tipo === 'budget_threshold_crossed' && e.payload?.teto != null && e.competencia === mesAtual);
    if (tetos.length) o.mural_alertas = `teto-${Math.max(...tetos.map((e) => e.payload.limiar))}`;
    const concluidas = Object.entries(perfil.reunioes).filter(([, r]) => r.concluida_em).sort();
    if (concluidas.at(-1)?.[1].fechamento === 'fechado') o.tela = 'fechado';
    const venc = `${mesAtual}-06`;
    const comp = competenciaDaReuniao(venc);
    const quadro = [];
    if (perfil.avisos[comp]?.mostrado_em && !perfil.reunioes[comp]?.concluida_em && partes(hoje).dia < 6) quadro.push('aviso');
    if (perfil.resumo_disponivel) quadro.push('novo');
    if (quadro.length) o.quadro = quadro.join(' ');
    return o;
  }

  // ---- contexto de cada cena: o que o roteiro pode ler
  function contextoDa(inv) {
    const { data: hoje, hora } = relogio();
    const c = { ...inv.contexto, hora, privado: dados.privado, dia: partes(hoje).dia, escolhas: {} };
    const hist = perfil.primeiro_acesso ? dados.historico(perfil.primeiro_acesso) : [];
    c.meses_validos = c.meses_validos ?? hist.filter((m) => m.conferido).length;
    switch (inv.cena) {
      case 'C2': {
        c.ambiguas_pendentes = (c.ambiguas ?? []).filter((t) => !perfil.categorias[t.id]?.categoria);
        break;
      }
      case 'C2S3':
        Object.assign(c, c.transacao?.campos ?? {});
        break;
      case 'C3S1': {
        const vivi = elenco.get('vivi');
        c.viviNoPosto = vivi.visivel && vivi.cadeira?.id === 'cad_vivi';
        break;
      }
      case 'C1S4':
        c.acao = Boolean(c.objeto);
        break;
      case 'C3S3':
        c.cardDisponivel = true;
        break;
      case 'C3S4': {
        c.resumoDisponivel = Boolean(perfil.resumo_disponivel);
        const desde = perfil.resumo_visto_em ?? '';
        c.quantidade_eventos_validos = Object.entries(perfil.eventos)
          .filter(([id, e]) => !id.startsWith('historico:') && id !== 'lote:historico-inicial' && (e.recebido_em ?? '') > desde).length;
        break;
      }
      case 'C4S1':
      case 'REUNIAO': {
        c.relatorio = dados.relatorio(c.competencia, perfil);
        c.situacao = c.relatorio.situacao;
        c.foco = c.relatorio.foco;
        c.diferenca = null;
        break;
      }
      default:
    }
    return c;
  }

  // ---- resultados que a cena entrega
  function aplicarResultado(inv, ctx, cmd) {
    const quando = carimbo(relogio());
    if (cmd.chave === 'categoria') {
      const t = ctx.transacao ?? inv.contexto.transacao;
      if (!t) return;
      const e = ctx.escolhas.c2s3;
      const reg = (perfil.categorias[t.id] ??= { descricao: t.campos?.descricao_segura ?? 'Despesa', perguntada_em: quando });
      if (e === 'confirm_category_a') reg.categoria = t.campos.categoria_a;
      if (e === 'confirm_category_b') reg.categoria = t.campos.categoria_b;
      if (reg.categoria) { reg.respondida_em = quando; sessao.houveAcao = true; }
      else reg.adiada_em = quando;
      painel?.registrar(`  categoria de ${reg.descricao}: ${reg.categoria ?? 'deixada para depois'}`);
    }
    if (cmd.chave === 'observacao') ctx.observacao = ctx.escolhas.c4s3 ?? null;
    if (cmd.chave === 'resumo_visto') {
      perfil.resumo_visto_em = quando;
      perfil.resumo_disponivel = null;
    }
    if (cmd.chave === 'convite') ctx.convite_resposta = ctx.escolhas.c4s1;
    salvar();
  }

  function registrarLote(inv, ctx) {
    const estado = { conciliado: 'conferido', divergente: 'sinalizado', sem_fontes: 'parcial' }[ctx.conciliacao] ?? 'recebido';
    perfil.lotes[ctx.lote] = { estado, recebido_em: carimbo(relogio()), historico: Boolean(ctx.historico) };
    for (const t of ctx.ambiguas ?? []) {
      perfil.categorias[t.id] ??= { descricao: t.campos?.descricao_segura ?? 'Despesa', perguntada_em: carimbo(relogio()) };
    }
  }

  function marco(inv, ctx, id) {
    if (id !== 'reuniao_concluida') return;
    ctx.resultadoReuniao = { fechamento: ctx.situacao === 'completa' ? 'fechado' : 'pendente', observacao: ctx.escolhas.c4s3 ?? null };
    perfil = registrarConclusao(perfil, inv, carimbo(relogio()), ctx.resultadoReuniao);
    salvar();
    painel?.registrar(`  reunião de ${ctx.competencia} registrada: fechamento ${ctx.resultadoReuniao.fechamento}`);
  }

  // ---- a fila
  function enfileirar(invs) {
    if (!sessao?.aberta) return;
    sessao.fila.push(...invs);
    rodarFila();
  }

  function aindaValida(inv) {
    const { data: hoje } = relogio();
    if (inv.cena === 'C4S1' || inv.cena === 'REUNIAO') {
      if (inv.contexto.motivo === 'aceita') return true;
      const p = planejarReuniao(perfil, hoje)[0];
      return p && p.chave === inv.chave && p.cena === inv.cena;
    }
    return true;
  }

  async function tocar(inv, s = sessao) {
    const def = CENAS[inv.cena];
    const ctx = contextoDa(inv);
    const cmds = def.montar(roteiro, ctx);
    const quando = carimbo(relogio());
    if (!cmds) {
      // variante "skip" do roteiro: nenhuma cena exibida; o evento fica processado
      perfil = registrarConclusao(perfil, inv, quando, { pulada: true });
      salvar();
      painel?.registrar(`· ${inv.cena} não toca (variante skip): ${inv.motivo}`);
      return;
    }
    painel?.registrar(`▶ ${inv.cena} · ${def.titulo}${inv.motivo ? ` · ${inv.motivo}` : ''}`);
    perfil = registrarInicio(perfil, inv, quando);
    salvar();
    s.atual = inv;
    palco.classList.toggle('bloqueado', inv.bloqueia);
    await executor.executar(inv, cmds, ctx, { pulavel: def.pulavel });
    // o que a cena mostrou nos objetos volta a vir do domínio (o perfil)
    if (s === sessao) for (const k of Object.keys(objetosCena)) delete objetosCena[k];
    // o estado do envelope vem da conciliação (o domínio); vale depois que a cena mostrou a chegada
    if (inv.cena === 'C2' && s.aberta && s === sessao) registrarLote(inv, ctx);
    palco.classList.remove('bloqueado');
    s.atual = null;
    if (!s.aberta || s !== sessao) return;

    const fim = carimbo(relogio());
    const extra = {};
    if (inv.cena === 'C4S1' && ctx.escolhas.c4s1 === 'defer_once_and_persist') extra.adiada = true;
    if (inv.cena === 'REUNIAO') Object.assign(extra, ctx.resultadoReuniao ?? {});
    perfil = registrarConclusao(perfil, inv, fim, extra);
    salvar();
    painel?.atualizar();

    // o que vem depois
    const { data: hoje } = relogio();
    if (inv.cena === 'C4S1' && ctx.escolhas.c4s1 === 'start_monthly_meeting') {
      enfileirar([{ cena: 'REUNIAO', chave: CHAVES.reuniao(perfil.perfil, inv.contexto.competencia), prioridade: PRIORIDADE.REUNIAO_VENCIDA,
        bloqueia: true, obrigatoria: true, motivo: 'aceitou o convite do dia 6',
        contexto: { ...inv.contexto, motivo: 'aceita' } }]);
    }
    if (inv.cena === 'C4S1' && extra.adiada) painel?.registrar('  adiada uma vez: a próxima visita começa pela reunião');
    if (inv.cena === 'REUNIAO') enfileirar(planejarReuniao(perfil, hoje));
  }

  async function rodarFila() {
    const s = sessao;
    if (!s || s.rodando) return;
    s.rodando = true;
    while (s.aberta && s === sessao && s.fila.length) {
      s.fila = ordenar(deduplicar(perfil, s.fila));
      const inv = s.fila.shift();
      if (!inv) break;
      if (!aindaValida(inv)) continue;
      await tocar(inv, s);
    }
    s.rodando = false;
    painel?.atualizar();
  }

  // ---- eventos de domínio
  function emitir(ev) {
    const quando = carimbo(relogio());
    perfil = registrarEvento(perfil, ev, quando);
    salvar();
    if (!sessao?.aberta) {
      painel?.registrar(`○ ${ev.type} guardado: o app está fechado (vai na próxima visita)`);
      painel?.atualizar();
      return;
    }
    let invs = planejarEvento(perfil, ev, { primeiraVisita: perfil.primeiro_acesso === relogio().data, houveAcao: sessao.houveAcao });
    // C3S1 tem limite: uma reação por visita; o resto só muda o objeto
    if (invs[0]?.cena === 'C3S1' && sessao.reacoes >= 1) {
      perfil.eventos[ev.id].processado_em = quando;
      salvar();
      painel?.registrar(`· ${ev.type}: calendário atualizado, sem nova fala (limite de reação da visita)`);
      invs = [];
    }
    if (ev.type === 'payment_confirmed') sessao.houveAcao = true;
    if (invs[0]?.cena === 'C3S1') sessao.reacoes += 1;
    if (invs[0]?.cena === 'C1S4') invs[0].contexto.objeto = 'calendario';
    if (!invs.length && !perfil.eventos[ev.id].processado_em) {
      perfil.eventos[ev.id].processado_em = quando;
      painel?.registrar(`· ${ev.type}: nenhuma cena elegível`);
      salvar();
    }
    painel?.registrar(`● ${ev.type}${invs.length ? ` → ${invs.map((i) => i.cena).join(', ')}` : ''}`);
    enfileirar(invs);
  }
  function emitirSilencioso(ev) {
    perfil = registrarEvento(perfil, ev, carimbo(relogio()));
    perfil.eventos[ev.id].processado_em = carimbo(relogio());
    sessao.houveAcao = true;
    salvar();
  }

  // ---- visitas
  async function lerPlanilha() {
    if (!naPlanilha) return false;
    painel?.atualizar();
    const ok = await dados.ler(await mcpPronto, relogio().data);
    painel?.registrar(ok ? `◆ planilha lida: ${dados.abas.map((a) => `${a.aba} (${a.conferencia})`).join(', ')}`
      : `◆ planilha não lida: ${dados.erro?.texto}`);
    painel?.atualizar();
    return ok;
  }

  /** Lê de novo no meio da visita: o que mudou vira evento, cena a cena. */
  async function relerPlanilha() {
    if (!await lerPlanilha()) return;
    const evs = dados.eventosDeAbertura(perfil, relogio().data);
    salvar();
    if (!evs.length) painel?.registrar('  nada mudou desde a última leitura');
    for (const ev of evs) emitir(ev);
  }

  async function abrirVisitaAgora() {
    const { data: hoje } = relogio();
    executor.cancelar();
    ui.limpar();
    document.getElementById('encerrada').hidden = true;
    if (naPlanilha) await lerPlanilha();
    const r = abrirVisita(perfil, hoje, { regraDia6: opcoes.regraDia6, lerDados: (p) => dados.eventosDeAbertura(p, hoje) });
    perfil = r.perfil;
    salvar();
    posicionarElenco({ guilhermeNaPorta: r.fila.some((i) => i.cena === 'C1S1') });
    for (const k of Object.keys(objetosCena)) delete objetosCena[k];
    sessao = { aberta: true, fila: [], rodando: false, atual: null, houveAcao: false, reacoes: 0, explorou: false, data: hoje };
    painel?.registrar(`━━ visita em ${hoje}${hoje === hojeEmSaoPaulo() ? ' (hoje)' : ' (simulada)'}`);
    for (const n of r.notas) painel?.registrar(`  ${n}`);
    if (!r.fila.length) painel?.registrar('  nada na fila: escritório livre');
    painel?.atualizar();
    enfileirar(r.fila);
  }

  async function encerrarVisita() {
    if (!sessao?.aberta) return;
    const { data: hoje } = relogio();
    const primeira = perfil.primeiro_acesso === hoje;
    if (primeira && !sessao.houveAcao && !perfil.cenas[CHAVES.primeiraAcao(perfil.perfil)]?.concluida_em && !sessao.atual) {
      // C1S4 na saída da primeira visita, sem ação: despedida neutra
      await tocar({ cena: 'C1S4', chave: CHAVES.primeiraAcao(perfil.perfil), prioridade: PRIORIDADE.AMBIENTE,
        bloqueia: false, contexto: { saida: true }, motivo: 'saída da primeira visita sem ação' });
    }
    sessao.aberta = false;
    executor.cancelar();
    ui.limpar();
    document.getElementById('encerrada').hidden = false;
    painel?.registrar(`━━ visita encerrada`);
    painel?.atualizar();
  }

  function zerarPerfil() {
    if (sessao) sessao.aberta = false;
    executor.cancelar();
    apagarPerfil(armazem, perfilId);
    perfil = carregarPerfil(armazem, perfilId);
    painel?.registrar('━━ perfil zerado');
  }

  // ---- cliques no escritório
  function noEscritorio(id) {
    if (!sessao?.aberta || palco.classList.contains('bloqueado')) return;
    const { data: hoje } = relogio();
    const fila = [];
    // C1S3: a primeira exploração voluntária depois da recepção
    if (!sessao.explorou && perfil.cenas[CHAVES.onboarding(perfil.perfil)]?.concluida_em
      && !perfil.cenas[CHAVES.postos(perfil.perfil)]?.concluida_em) {
      sessao.explorou = true;
      fila.push({ cena: 'C1S3', chave: CHAVES.postos(perfil.perfil), prioridade: PRIORIDADE.MICROCENA + 2, bloqueia: false,
        contexto: {}, motivo: 'primeira exploração voluntária' });
    }
    if (id === 'mesa_caio' || id === 'ator:caio') {
      fila.push({ cena: 'C3S2', chave: `consulta:${perfil.perfil}:${hoje}:${Date.now()}`, prioridade: PRIORIDADE.MICROCENA + 5,
        bloqueia: false, contexto: { voluntaria: true }, motivo: 'consulta pedida pela pessoa' });
    } else if ((id === 'mesa_saldanha' || id === 'ator:saldanha') && !perfil.cenas[CHAVES.leitura(perfil.perfil)]?.concluida_em) {
      // sem histórico, a primeira ida ao Saldanha é a C1S2 sem dados
      fila.push({ cena: 'C1S2', chave: CHAVES.leitura(perfil.perfil), prioridade: PRIORIDADE.MICROCENA, bloqueia: false,
        contexto: { meses_validos: 0 }, motivo: 'a pessoa abriu a mesa do Saldanha sem histórico legível' });
    } else if (id === 'mesa_saldanha' || id === 'ator:saldanha') {
      const pend = Object.entries(perfil.categorias).find(([, c]) => !c.categoria);
      const ev = pend && Object.values(perfil.eventos).flatMap((e) => e.payload?.ambiguas ?? []).find((t) => t.id === pend[0]);
      if (ev) {
        fila.push({ cena: 'C2S3', chave: `category_question:${perfil.perfil}:${ev.id}:${Date.now()}`, prioridade: PRIORIDADE.MICROCENA,
          bloqueia: false, contexto: { transacao: ev }, motivo: 'categoria deixada para depois, retomada pela pessoa' });
      } else {
        paineis.livro(ui, perfil, dados);
      }
    } else if (id === 'quadro') {
      if (perfil.resumo_disponivel) {
        fila.push({ cena: 'C3S4', chave: CHAVES.resumo(perfil.perfil, perfil.resumo_disponivel), prioridade: PRIORIDADE.MICROCENA,
          bloqueia: false, contexto: {}, motivo: 'resumo aberto pela pessoa' });
      } else {
        ui.legenda('Sem resumo novo no quadro.', 2500);
      }
    } else if (id === 'ator:flora' || id === 'ator:lupin') {
      const cao = elenco.get(id.slice(5));
      if (!cao.emCena) {
        cao.definir('inquieto', agora());
        setTimeout(() => { if (!cao.emCena) cao.definir(cao.base ?? 'dormindo_na_cama', agora()); }, 2200);
      }
    }
    enfileirar(fila);
  }

  palco.addEventListener('click', (ev) => {
    if (ev.target.closest('.painel-fundo, .escolhas, button')) return;
    if (ui.avancar()) return;
    if ([...elenco.values()].some((a) => a.caminho)) { config.acelerar = 4; return; }
    const r = canvas.getBoundingClientRect();
    const x = (ev.clientX - r.left) / escala;
    const y = (ev.clientY - r.top) / escala;
    const alvo = [...areas].reverse().find((a) => x >= a.x && x <= a.x + a.w && y >= a.y && y <= a.y + a.h);
    noEscritorio(alvo?.id ?? 'piso');
  });
  canvas.addEventListener('mousemove', (ev) => {
    const r = canvas.getBoundingClientRect();
    const x = (ev.clientX - r.left) / escala;
    const y = (ev.clientY - r.top) / escala;
    const alvo = [...areas].reverse().find((a) => x >= a.x && x <= a.x + a.w && y >= a.y && y <= a.y + a.h);
    const clicavel = alvo && ['mesa_caio', 'ator:caio', 'mesa_saldanha', 'ator:saldanha', 'quadro', 'ator:flora', 'ator:lupin'].includes(alvo.id);
    canvas.style.cursor = clicavel ? 'pointer' : 'default';
    canvas.title = clicavel ? { mesa_caio: 'Consulta com o Caio', 'ator:caio': 'Consulta com o Caio', mesa_saldanha: 'Mesa do Saldanha',
      'ator:saldanha': 'Mesa do Saldanha', quadro: 'Quadro', 'ator:flora': 'Flora', 'ator:lupin': 'Lupin' }[alvo.id] : '';
  });
  document.addEventListener('keydown', (ev) => {
    if (ev.target.closest?.('input, select, textarea')) return;
    if ((ev.key === 'Enter' || ev.key === ' ') && !ev.target.closest?.('button') && ui.avancar()) ev.preventDefault();
    if (ev.key === 'Escape' && ui.pularAtivo) ui.pularAgora();
  });

  // ---- a vida no escritório e o laço de desenho
  let areas = [];
  let ultimo = agora();
  const proximaVida = new Map();
  function vida(t) {
    if (config.reduzido) return;
    for (const [id, v] of Object.entries(VIDA)) {
      const a = elenco.get(id);
      if (!a.sentado || a.emCena || a.caminho || a.umaVez || a.cadeira.zona === 'reuniao') continue;
      if (t < (proximaVida.get(id) ?? 0)) continue;
      proximaVida.set(id, t + 5 + Math.random() * 7);
      if (v.gestos.length && Math.random() < 0.3) {
        const g = v.gestos[Math.floor(Math.random() * v.gestos.length)];
        a.tocar(g, t).then(() => { if (!a.emCena && a.anim === g) a.definir(a.repouso(), agora()); });
      } else {
        a.base = v.bases[Math.floor(Math.random() * v.bases.length)];
        a.definir(a.repouso(), t);
      }
    }
  }

  function quadro() {
    const t = agora();
    const dt = Math.min(0.1, t - ultimo);
    ultimo = t;
    for (const a of elenco.values()) a.atualizar(t, dt);
    if (![...elenco.values()].some((a) => a.caminho)) config.acelerar = 1;
    vida(t);
    for (const [id, ate] of brilhos) if (t > ate) brilhos.delete(id);
    areas = sala.desenhar(ctx2d, {
      atores: [...elenco.values()], objetos: { ...objetosBase(), ...objetosCena }, brilhos: [...brilhos.keys()],
      planta: opcoes.planta, t,
    });
    ui.atualizar();
    requestAnimationFrame(quadro);
  }

  // ---- painel de teste
  const painel = criarPainelDeTeste({
    raiz: document.getElementById('teste'), opcoes, salvarOpcoes, persistente, roteiro,
    relogio, dados: sinteticos, fonte: dados, naPlanilha, relerPlanilha,
    perfil: () => perfil,
    sessao: () => sessao,
    abrirVisita: abrirVisitaAgora,
    encerrarVisita,
    zerarPerfil,
    emitir,
    aplicar: () => {
      config.velocidade = opcoes.velocidade;
      config.reduzido = opcoes.reduzido || reduzidoDoSistema;
      sinteticos.base = opcoes.base;
      sinteticos.privado = opcoes.privado;
      dados.privado = opcoes.privado;
    },
  });

  mostrarValidacao(layout);
  requestAnimationFrame(quadro);
  abrirVisitaAgora();
  document.body.dataset.pronto = 'sim';
  window.financy = { jogo, dados, perfil: () => perfil, sessao: () => sessao, elenco, opcoes, clicar: noEscritorio,
    ocupado: () => Boolean(sessao?.atual || sessao?.fila.length || [...elenco.values()].some((a) => a.caminho)) };
}

iniciar();
