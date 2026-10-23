// O elenco em cena: posição na planta, para onde olha, a animação que está
// tocando e o que está fazendo (sentado, andando, falando, piscando). O
// desenho fica em sala.js; aqui só o estado e o tempo.
//
// Animações e espelhamento seguem o manifesto: de frente, quem olha +A usa
// o desenho sem espelhar e quem olha +B, espelhado; de costas, -B sem
// espelhar e -A espelhado.

import {
  buscar, centro, tileDe, acessoDaCadeira, deFrente, direcaoDoPasso,
} from './caminho.js';

export const ESPELHA = { '+A': false, '+B': true, '-B': false, '-A': true };
export const LADO = { '+A': 'frente', '+B': 'frente', '-A': 'costas', '-B': 'costas' };

// velocidade de andar (tiles por segundo). A nota 15.4 deixa a decisão com
// o jogo: acima de uns 0,5 o pé desliza; aqui a caminhada acelera junto.
export const config = { velocidade: 1.0, reduzido: false, acelerar: 1 };

export class Ator {
  constructor(id, entrada, { cao = false } = {}) {
    this.id = id;
    this.e = entrada;
    this.cao = cao;
    this.pos = [0.5, 0.5];
    this.dir = '+A';
    this.cadeira = null;     // peça da planta em que está sentado
    this.cama = null;        // peça da cama (cachorros)
    this.visivel = true;
    this.alfa = 1;
    this.anim = cao ? 'sentado_frente' : 'parado_frente';
    this.t0 = 0;
    this.ritmo = 1;
    this.base = null;        // repouso escolhido (vida à mesa, sono dos cachorros)
    this.umaVez = null;      // { fim, resolve } da animação que toca uma vez
    this.caminho = null;     // { pontos, resolve }
    this.falando = false;
    this.piscar = { proximo: 2 + Math.random() * 4, inicio: -9 };
    this.envelope = false;   // envelope na mão
    this.selo = null;        // cor do selo na tela do tablet
    this.emCena = false;     // o executor está no controle
    this.foraDaCama = false; // cachorro andando pela sala
    this.rotina = 0;         // ficha da rotina de ambiente (uma nova cancela a anterior)
  }

  animacao(nome = this.anim) { return this.e.animacoes[nome]; }
  // o cachorro na cama olha para a sala (espelhado); andando, o desenho
  // sem espelhar olha para a direita da tela, como o dos humanos
  get espelhar() { return this.cao && !this.foraDaCama ? true : ESPELHA[this.dir]; }
  get sentado() { return Boolean(this.cadeira); }

  /** Repouso: sentado (com a vida à mesa, se houver), em pé ou na cama. */
  repouso() {
    if (this.cao) return this.foraDaCama ? 'parado_frente' : (this.base ?? 'sentado_frente');
    if (this.cadeira) {
      if (!deFrente(this.cadeira.olha_para)) return 'sentado_costas';
      return this.base && this.animacao(this.base) ? this.base : 'sentado_frente';
    }
    return `parado_${LADO[this.dir]}`;
  }

  definir(nome, t) {
    if (!this.animacao(nome)) nome = this.repouso();
    if (this.anim !== nome) {
      this.anim = nome;
      this.t0 = t;
    }
  }

  quadro(t, nome = this.anim, t0 = this.t0) {
    const a = this.animacao(nome);
    if (!a || a.quadros <= 1 || !a.fps) return 0;
    const k = Math.floor((t - t0) * a.fps * (nome.startsWith('andando') ? this.ritmo : 1));
    return a.loop ? ((k % a.quadros) + a.quadros) % a.quadros : Math.min(a.quadros - 1, Math.max(0, k));
  }

  /** Toca uma animação uma vez e resolve no fim (as de laço resolvem logo). */
  tocar(nome, t) {
    const a = this.animacao(nome);
    if (!a) return Promise.resolve();
    this.umaVez?.resolve();
    this.anim = nome;
    this.t0 = t;
    if (a.loop || !a.fps || a.quadros <= 1 || config.reduzido) {
      this.umaVez = null;
      return Promise.resolve();
    }
    return new Promise((resolve) => {
      this.umaVez = { fim: t + a.quadros / a.fps, resolve, voltar: true };
    });
  }

  /** Anda pelos pontos (posições contínuas) e resolve ao chegar. */
  andar(pontos) {
    this.caminho?.resolve();
    if (!pontos.length) return Promise.resolve();
    if (config.reduzido) {
      const ultimo = pontos.at(-1);
      const penultimo = pontos.at(-2) ?? this.pos;
      this.dir = direcaoDoPasso(penultimo, ultimo);
      this.pos = [...ultimo];
      return Promise.resolve();
    }
    return new Promise((resolve) => { this.caminho = { pontos: pontos.map((p) => [...p]), resolve }; });
  }

  atualizar(t, dt) {
    if (this.caminho) {
      let passo = config.velocidade * config.acelerar * dt;
      this.ritmo = Math.min(1.6, Math.max(1, config.velocidade / 0.5));
      while (passo > 0 && this.caminho) {
        const alvo = this.caminho.pontos[0];
        const da = alvo[0] - this.pos[0];
        const db = alvo[1] - this.pos[1];
        const d = Math.hypot(da, db);
        if (d > 1e-4) this.dir = direcaoDoPasso(this.pos, alvo);
        if (d <= passo) {
          this.pos = [...alvo];
          passo -= d;
          this.caminho.pontos.shift();
          if (!this.caminho.pontos.length) {
            const { resolve } = this.caminho;
            this.caminho = null;
            this.definir(this.repouso(), t);
            resolve();
          }
        } else {
          this.pos = [this.pos[0] + (da / d) * passo, this.pos[1] + (db / d) * passo];
          passo = 0;
        }
      }
      if (this.caminho) this.definir(this.cao ? 'andando' : `andando_${LADO[this.dir]}`, t);
    }
    if (this.umaVez && t >= this.umaVez.fim) {
      const { resolve } = this.umaVez;
      this.umaVez = null;
      resolve();
    }
    // piscar de vez em quando, só de frente e fora do olhar para o lado
    if (!this.cao && t >= this.piscar.proximo) {
      this.piscar.inicio = t;
      this.piscar.proximo = t + 2.5 + Math.random() * 4;
    }
  }

  /** As sobreposições do quadro de agora: olhos e boca no lugar do rosto. */
  sobreposicoes(t) {
    const a = this.animacao();
    if (this.cao || !a?.rosto || config.reduzido) return [];
    const k = this.quadro(t);
    const rosto = a.rosto[Math.min(k, a.rosto.length - 1)];
    const out = [];
    const piscando = this.animacao('piscando_frente');
    if (piscando && !this.anim.startsWith('olhando')) {
      const kp = Math.floor((t - this.piscar.inicio) * piscando.fps);
      if (kp >= 0 && kp < piscando.quadros) out.push({ nome: 'piscando_frente', quadro: kp, rosto });
    }
    if (this.falando && this.animacao('falando_frente')) {
      out.push({ nome: 'falando_frente', quadro: this.quadro(t, 'falando_frente', 0), rosto });
    }
    return out;
  }
}

/**
 * Leva o ator de onde está até o destino, pelos tiles livres:
 *   { cadeira }   senta na cadeira (levanta antes, se estiver sentado)
 *   { tile }      fica em pé no centro do tile
 *   { ponto }     fica em pé no ponto contínuo (chegando pelo tile dele)
 *   { fora }      sai pela porta de entrada (some)
 * 'olhar' vira o ator no fim.
 */
export async function irAte(ator, destino, { grade, layout, agora }) {
  if (ator.cadeira && destino.cadeira?.id === ator.cadeira.id) return;
  // uma viagem nova substitui a anterior: a antiga para onde estiver
  const viagem = (ator.viagem = (ator.viagem ?? 0) + 1);
  const valendo = () => ator.viagem === viagem;
  if (ator.cadeira) await levantar(ator, { grade, agora });
  if (!valendo()) return;

  let alvoTile;
  let finais = [];
  if (destino.cadeira) {
    const acc = acessoDaCadeira(grade, destino.cadeira);
    alvoTile = acc.entrada;
    finais = acc.frente ? [acc.lateral, acc.frente] : [acc.centro];
  } else if (destino.tile) {
    alvoTile = destino.tile;
  } else if (destino.ponto) {
    alvoTile = tileDe(destino.ponto);
    finais = [destino.ponto];
  } else if (destino.fora) {
    alvoTile = layout.entrada;
    finais = [[layout.entrada[0] - 0.6, layout.entrada[1] + 0.5]];
  }
  const tiles = buscar(grade, tileDe(ator.pos), alvoTile) ?? [alvoTile];
  const pontos = tiles.slice(1).map(centro);
  if (!pontos.length) pontos.push(centro(alvoTile));
  await ator.andar([...pontos, ...finais]);
  if (!valendo()) return;

  if (destino.cadeira) await sentar(ator, destino.cadeira, agora);
  if (destino.fora) ator.visivel = false;
  if (destino.olhar) ator.dir = destino.olhar;
  if (!ator.cadeira) ator.definir(ator.repouso(), agora());
}

export async function levantar(ator, { grade, agora }) {
  const c = ator.cadeira;
  if (!c) return;
  const acc = acessoDaCadeira(grade, c);
  ator.dir = c.olha_para;
  if (acc.frente && ator.animacao('levantando_da_cadeira_frente')) {
    await ator.tocar('levantando_da_cadeira_frente', agora());
    ator.cadeira = null;
    ator.pos = [...acc.frente];
    ator.definir(ator.repouso(), agora());
    await ator.andar([acc.lateral, centro(acc.entrada)]);
  } else {
    ator.cadeira = null;
    ator.pos = [...acc.centro];
    await ator.andar([centro(acc.entrada)]);
  }
}

export async function sentar(ator, cadeira, agora) {
  ator.dir = cadeira.olha_para;
  const acc = { centro: [cadeira.tile[0] + 0.5, cadeira.tile[1] + 0.5] };
  ator.pos = acc.centro;
  ator.cadeira = cadeira;
  if (deFrente(cadeira.olha_para) && ator.animacao('sentando_na_cadeira_frente')) {
    await ator.tocar('sentando_na_cadeira_frente', agora());
  }
  ator.definir(ator.repouso(), agora());
}

/** Coloca o ator sentado na cadeira, sem andar (abertura da cena). */
export function sentarJa(ator, cadeira, t) {
  ator.cadeira = cadeira;
  ator.dir = cadeira.olha_para;
  ator.pos = [cadeira.tile[0] + 0.5, cadeira.tile[1] + 0.5];
  ator.visivel = true;
  ator.definir(ator.repouso(), t);
}
