// O executor de cenas (§9, passo 1): recebe a lista de comandos que o
// roteiro montou e encena no escritório, com os mesmos sprites. Não decide
// nada de dado: o que precisa ser gravado ele entrega ao jogo (resultado e
// marco). Pular uma cena encena tudo na hora, sem falas, com a escolha
// segura de cada pergunta: os estados e os registros continuam valendo.

import { irAte, levantar, config } from './atores.js';
import { deFrente } from './caminho.js';

// a escolha que vale quando a pessoa pula a cena (nunca grava categoria
// nem abre card sem pedido)
const AO_PULAR = {
  c2s2: 'keep_reconciliation_pending',
  c2s3: 'defer_classification',
  c3s3: 'dismiss_education_card',
  c4s3: 'player_defers_priority',
};

// animações que pedem a pessoa sentada de frente, à mesa, e as que pedem em pé
const DE_PE = new Set(['mostrando_tablet', 'apresentando_quadro', 'deixando_envelope_no_malote',
  'deixando_envelope_no_malote_costas', 'alerta', 'comemorando_tablet', 'tirando_foto']);

export function criarExecutor(jogo) {
  const ex = { pulando: false, corrida: { cancelado: false }, movimentos: new Map(), log: [], ultima: {}, origemUltima: {} };

  const ator = (id) => jogo.elenco.get(id);
  const agora = () => jogo.agora();
  const espera = (ms) => (ex.pulando || config.reduzido ? Promise.resolve()
    : new Promise((r) => setTimeout(r, ms)));

  function podeTocar(a, nome) {
    const anim = a.animacao(nome);
    if (!anim) return false;
    if (DE_PE.has(nome)) return !a.sentado;
    if (anim.tampo || nome.startsWith('sentado_frente') || nome === 'digitando_sentado') {
      return a.sentado && deFrente(a.cadeira.olha_para);
    }
    return true;
  }

  function destinoDo(a, alvo) {
    if (alvo === 'posto') return { cadeira: jogo.cadeiraDe(a.id) };
    if (alvo === 'reuniao') return { cadeira: jogo.cadeiraDaReuniao(a.id) };
    if (alvo === 'fora') return { fora: true };
    if (typeof alvo === 'string') return { cadeira: jogo.layout.pecas_piso.find((p) => p.id === alvo) };
    return alvo;
  }

  async function mover(cmd) {
    const a = ator(cmd.actor);
    a.emCena = true;
    const dest = destinoDo(a, cmd.target);
    if (cmd.olhar) dest.olhar = cmd.olhar;
    if (dest.cadeira === undefined && !dest.tile && !dest.ponto && !dest.fora) return;
    const p = irAte(a, dest, { grade: jogo.grade, layout: jogo.layout, agora });
    // "fundo": a caminhada segue depois do fim da cena (voltar ao posto)
    if (cmd.fundo) ex.movimentos.delete(a.id);
    else ex.movimentos.set(a.id, p);
    if (cmd.wait !== false) await p;
  }

  async function comando(cmd, ctx, inv) {
    const a = cmd.actor ? ator(cmd.actor) : null;
    if (cmd.actor && !a) return;
    if (a) a.emCena = true;
    switch (cmd.op) {
      case 'marca':
        ex.log.push({ cena: cmd.cena, titulo: cmd.titulo, variantes: cmd.variantes });
        jogo.aoMarcarCena?.(inv, cmd);
        return;
      case 'entrar': {
        a.cadeira = null;
        a.visivel = true;
        a.alfa = 1;
        a.envelope = Boolean(cmd.envelope);
        a.pos = [jogo.layout.entrada[0] - 0.6, jogo.layout.entrada[1] + 0.5];
        a.dir = '+A';
        a.definir(a.repouso(), agora());
        const ate = cmd.ate ?? { tile: jogo.layout.entrada };
        await mover({ actor: a.id, target: ate, olhar: ate.olhar });
        return;
      }
      case 'move':
        await mover(cmd);
        return;
      case 'aguardar':
        await Promise.all(cmd.actors.map((id) => ex.movimentos.get(id)).filter(Boolean));
        return;
      case 'levantar':
        if (a.sentado) await levantar(a, { grade: jogo.grade, agora });
        return;
      case 'face':
        if (cmd.dir === 'frente') {
          if (!a.sentado && (a.dir === '-A' || a.dir === '-B')) a.dir = '+A';
        } else if (!a.sentado) a.dir = cmd.dir;
        if (!a.sentado) a.definir(a.repouso(), agora());
        return;
      case 'play': {
        if (!podeTocar(a, cmd.animation)) return;
        if (cmd.loop || a.animacao(cmd.animation).loop) {
          if (a.sentado) a.base = cmd.animation;
          a.definir(cmd.animation, agora());
          return;
        }
        const p = a.tocar(cmd.animation, agora()).then(() => {
          if (!cmd.manter && a.anim === cmd.animation) a.definir(a.repouso(), agora());
        });
        if (cmd.wait || cmd.manter) await p;
        return;
      }
      case 'apontar':
        if (!a.sentado && a.animacao('apresentando_quadro')) {
          a.definir('apresentando_quadro', agora());
          await espera(1600);
          a.definir(a.repouso(), agora());
        } else if (podeTocar(a, 'olhando_para_o_lado_frente')) {
          a.tocar('olhando_para_o_lado_frente', agora()).then(() => a.definir(a.repouso(), agora()));
        }
        return;
      case 'piscar':
        a.piscar.proximo = agora();
        return;
      case 'repouso':
        a.definir(a.repouso(), agora());
        return;
      case 'soltar':
        a.envelope = false;
        return;
      case 'selo':
        a.selo = cmd.limpar ? null : (['verde', 'amarelo', 'vermelho'].includes(ctx.consulta?.veredito ?? ctx.veredito)
          ? (ctx.consulta?.veredito ?? ctx.veredito) : null);
        return;
      case 'cao':
        a.base = cmd.animation;
        a.definir(cmd.animation, agora());
        return;
      case 'speak':
        ex.ultima[a.id] = cmd.texto;
        if (cmd.vaiParaEscolha) return;      // a fala fica no balão dos botões
        a.falando = !ex.pulando;
        await jogo.ui.falar(a.id, cmd.texto, { origem: cmd.origem, ambiente: cmd.ambiente, pulando: ex.pulando });
        a.falando = false;
        return;
      case 'choice': {
        const id = ex.pulando && AO_PULAR[cmd.cena]
          ? AO_PULAR[cmd.cena]
          : await jogo.ui.escolher(cmd.actor ?? 'saldanha', ex.ultima[cmd.actor] ?? '',
            cmd.choices, { origem: ex.origemUltima?.[cmd.actor] ?? cmd.origem });
        ctx.escolhas[cmd.cena] = id;
        return;
      }
      case 'object':
        jogo.objetoDaCena(cmd.target, cmd.state);
        return;
      case 'focus':
        jogo.brilhar(cmd.target, ex.pulando ? 0 : (cmd.ms ?? 3000));
        if (cmd.wait) await espera(cmd.ms ?? 3000);
        return;
      case 'legenda':
        if (!ex.pulando) jogo.ui.legenda(cmd.texto, cmd.ms);
        return;
      case 'panel':
        if (ex.pulando && cmd.panel !== 'consulta') return;
        if (ex.pulando) { ctx.consulta = null; return; }
        await jogo.abrirPainel(cmd.panel, ctx, inv);
        return;
      case 'esperar':
        await espera(cmd.ms);
        return;
      case 'contexto':
        ctx.transacao = cmd.transacao;
        Object.assign(ctx, cmd.transacao?.campos ?? {});
        return;
      case 'continuar':
        await executarLista(cmd.comandos(ctx), ctx, inv);
        return;
      case 'resultado':
        jogo.aoResultado(inv, ctx, cmd);
        return;
      case 'marco':
        jogo.aoMarco(inv, ctx, cmd.id);
        return;
      default:
    }
  }

  // a última fala antes de uma escolha do mesmo personagem não espera
  // toque: ela aparece junto com os botões, no mesmo balão
  function vaiParaEscolha(cmds, i, ctx) {
    const atual = cmds[i];
    for (let k = i + 1; k < cmds.length; k++) {
      const c = cmds[k];
      if (c.se && !c.se(ctx)) continue;
      if (c.op === 'choice') return c.actor === atual.actor;
      if (['speak', 'panel', 'move', 'aguardar', 'continuar', 'esperar', 'levantar'].includes(c.op)) return false;
    }
    return false;
  }

  async function executarLista(cmds, ctx, inv) {
    const corrida = ex.corrida;
    for (let i = 0; i < cmds.length; i++) {
      const cmd = cmds[i];
      if (corrida.cancelado) return;
      if (cmd.se && !cmd.se(ctx)) continue;
      if (cmd.op === 'speak' && !ex.pulando && vaiParaEscolha(cmds, i, ctx)) {
        ex.origemUltima[cmd.actor] = cmd.origem;
        await comando({ ...cmd, vaiParaEscolha: true }, ctx, inv);
        continue;
      }
      await comando(cmd, ctx, inv);
    }
  }

  /** Encena a lista de comandos. Devolve o contexto com as escolhas. */
  ex.executar = async (inv, cmds, ctx, { pulavel = false } = {}) => {
    const corrida = { cancelado: false };
    ex.corrida = corrida;
    ex.pulando = false;
    ex.movimentos = new Map();
    ex.log = [];
    ex.ultima = {};
    ex.origemUltima = {};
    jogo.ui.mostrarPular(pulavel, () => {
      ex.pulando = true;
      jogo.ui.limpar();
      config.acelerar = 30;
    });
    try {
      await executarLista(cmds, ctx, inv);
      await Promise.all([...ex.movimentos.values()]);
    } finally {
      // uma cena cancelada não mexe no elenco de quem já está em cena depois dela
      if (ex.corrida !== corrida) return ctx;
      jogo.ui.mostrarPular(false);
      config.acelerar = 1;
      for (const a of jogo.elenco.values()) {
        if (!a.emCena) continue;
        a.emCena = false;
        a.falando = false;
        a.selo = null;
        if (!a.caminho && !a.umaVez && !a.cao) {
          if (a.sentado && a.base && !a.animacao(a.base)?.loop) a.base = null;
          a.definir(a.repouso(), agora());
        }
      }
    }
    return ctx;
  };

  ex.cancelar = () => {
    if (ex.corrida) ex.corrida.cancelado = true;
    ex.pulando = false;
    jogo.ui.limpar();
    jogo.ui.mostrarPular(false);
    config.acelerar = 1;
    for (const a of jogo.elenco.values()) { a.emCena = false; a.falando = false; a.selo = null; }
  };

  return ex;
}
