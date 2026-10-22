// Desenha a sala no canvas, em 1x, quadro a quadro: paredes e piso (feitos
// uma vez), peças de parede com o estado de cada uma, e móveis e pessoas em
// ordem de profundidade. Quem está sentado é desenhado junto da cadeira; à
// mesa, a ordem é cadeira, pessoa (com olhos e boca), mesa, teclado, camada
// do tampo e objetos (nota 11). A página amplia 2x sem suavizar.
//
// O que ainda não tem arte (selo FECHADO, recado no quadro, marca no
// calendário, bandeirinha do malote) vai em blocos, como manda o CLAUDE.md.

import { arquivos } from './carregar.js';
import { circulacaoObrigatoria, tilesDeAcesso } from './validacao.js';
import { deFrente } from './caminho.js';

const MARGEM = 20;

// quem senta olhando para cada lado: a direção da cadeira e se o sentado de
// frente sai espelhado (frente-dir = +A sem espelhar, frente-esq = +B espelhado)
export const OLHA_PARA = {
  '+A': ['frente-dir', false],
  '+B': ['frente-esq', true],
  '-B': ['costas-dir', false],
  '-A': ['costas-esq', true],
};
const CAMA = { manta_flora: 'flora', caminha_lupin: 'lupin' };
const MESAS = new Set(['mesa_trabalho', 'mesa_fundador', 'balcao_recepcao']);

/** Tamanho do canvas em 1x e a origem: o canto A0/B0 do piso fica em (cx, cy). */
export function tamanhoDaSala(layout, manifesto) {
  const [A, B] = layout.sala.tiles;
  const cx = MARGEM + 32 * B;
  const cy = MARGEM + manifesto.parede.altura + 4;
  return { largura: 32 * (A + B) + 2 * MARGEM, altura: cy + 16 * (A + B) + 8 + MARGEM, cx, cy };
}

// arredonda como o Python (meio para o par), para as cores saírem iguais às do build
function arredondar(v) {
  const f = Math.floor(v);
  const d = v - f;
  if (d !== 0.5) return d > 0.5 ? f + 1 : f;
  return f % 2 === 0 ? f : f + 1;
}
const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
const escurecer = (c, f) => c.map((v) => Math.max(0, Math.min(255, arredondar(v * f))));
const css = ([r, g, b], a = 1) => `rgba(${r},${g},${b},${a})`;

// letras 3x5 para os blocos com texto (selo FECHADO, "DIA 6")
const LETRAS = {
  F: ['111', '100', '110', '100', '100'], E: ['111', '100', '110', '100', '111'],
  C: ['111', '100', '100', '100', '111'], H: ['101', '101', '111', '101', '101'],
  A: ['010', '101', '111', '101', '101'], D: ['110', '101', '101', '101', '110'],
  O: ['111', '101', '101', '101', '111'], I: ['111', '010', '010', '010', '111'],
  6: ['111', '100', '111', '101', '111'], ' ': ['000', '000', '000', '000', '000'],
};

/** Os assentos de mesa: cadeira -> móvel à frente (mesma zona, fora da reunião). */
function mesasDasCadeiras(layout) {
  const out = new Map();
  for (const c of layout.pecas_piso.filter((p) => p.tipo === 'cadeira' && p.zona !== 'reuniao')) {
    const m = layout.pecas_piso.find((p) => p.zona === c.zona && MESAS.has(p.modelo) && p.tipo !== 'reservado');
    if (m) out.set(m.id, c.id);
  }
  return out;
}

export function criarSala({ manifesto, layout, imagens }) {
  const [A, B] = layout.sala.tiles;
  const geo = tamanhoDaSala(layout, manifesto);
  const { largura, altura, cx, cy } = geo;
  const P = (s, t, z = 0) => [cx + 32 * (s - t), cy + 16 * (s + t) - z];
  const bordaDoPiso = (x) => cy + Math.floor(Math.abs(x - cx) / 2);
  const cadeiraDaMesa = mesasDasCadeiras(layout);
  const pecas = Object.fromEntries([...layout.pecas_piso, ...layout.pecas_parede].map((p) => [p.id, p]));

  // cola uma imagem (ou um recorte dela) com a âncora no ponto (x, y)
  const colar = (ctx, img, ancora, x, y, { espelhar = false, recorte = null, alfa = 1 } = {}) => {
    if (!img) return;
    const [sx, sy, w, h] = recorte ?? [0, 0, img.width, img.height];
    const ax = espelhar ? w - ancora[0] : ancora[0];
    const dx = Math.round(x - ax);
    const dy = Math.round(y - ancora[1]);
    if (alfa < 1) { ctx.save(); ctx.globalAlpha = alfa; }
    if (!espelhar) {
      ctx.drawImage(img, sx, sy, w, h, dx, dy, w, h);
    } else {
      ctx.save();
      ctx.translate(dx + w, dy);
      ctx.scale(-1, 1);
      ctx.drawImage(img, sx, sy, w, h, 0, 0, w, h);
      ctx.restore();
    }
    if (alfa < 1) ctx.restore();
  };
  const arquivo = (c) => imagens.get(c);
  const quadroDaFolha = (id, nome, k) => {
    const e = manifesto[id];
    const [w, h] = e.tela;
    return [k * w, h * e.animacoes[nome].linha, w, h];
  };

  // ---- fundo: paredes, piso e a borda da frente, uma vez só
  const fundo = document.createElement('canvas');
  fundo.width = largura;
  fundo.height = altura;
  {
    const ctx = fundo.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    ctx.fillStyle = css([24, 30, 52]);
    ctx.fillRect(0, 0, largura, altura);
    const par = manifesto.parede;
    const cor = Object.fromEntries(Object.entries(par.cores).map(([k, v]) => [k, rgb(v)]));
    for (let x = cx - 32 * B; x < cx + 32 * A; x++) {
      const e = bordaDoPiso(x);
      const lado = x < cx ? 'esquerda' : 'direita';
      const faixas = [
        [e - par.altura, 2, cor[`topo_${lado}`]],
        [e - par.altura + 2, par.altura - 2 - par.rodape, cor[lado]],
        [e - par.rodape, 1, escurecer(cor[`rodape_${lado}`], 0.85)],
        [e - par.rodape + 1, par.rodape - 1, cor[`rodape_${lado}`]],
      ];
      for (const [y, h, c] of faixas) {
        ctx.fillStyle = css(x === cx ? escurecer(c, 0.82) : c);
        ctx.fillRect(x, y, 1, h);
      }
    }
    const piso = manifesto.piso_madeira;
    for (let a = 0; a < A; a++) {
      for (let b = 0; b < B; b++) {
        const v = piso.variacoes[(a * 7 + b * 3 + a * b) % 3];
        colar(ctx, arquivo(`piso/piso_madeira__${v}.png`), piso.ancora, ...P(a + 1, b + 1));
      }
    }
    const borda = par.borda_do_piso;
    const [xEsq, yEsq] = P(0, B);
    const [xFrente, yFrente] = P(A, B);
    for (let x = xEsq; x < P(A, 0)[0]; x++) {
      const esquerda = x < xFrente;
      const y0 = esquerda ? yEsq + Math.floor((x - xEsq) / 2) : yFrente - Math.floor((x - xFrente) / 2);
      ctx.fillStyle = borda[esquerda ? 'esquerda' : 'direita'];
      ctx.fillRect(x, y0, 1, borda.altura);
    }
  }

  // onde fica cada peça de parede: a âncora vai na ponta esquerda (na tela)
  // do vão, na altura da base
  const naParede = (p) => {
    const e = manifesto[p.modelo];
    const [x, y] = e.parede === 'esquerda' ? P(0, p.tiles.at(-1) + 1) : P(p.tiles[0], 0);
    return [x, y - e.altura[0]];
  };
  // a caixa de uma peça de parede na tela (para clique e brilho)
  const caixaDaParede = (p) => {
    const e = manifesto[p.modelo];
    const [x, y] = naParede(p);
    const w = 32 * p.tiles.length;
    const h = e.altura[1] - e.altura[0];
    const queda = 16 * p.tiles.length;   // a direita desce para a direita; a esquerda sobe
    return e.parede === 'direita'
      ? { x, y: y - h, w, h: h + queda, parede: e.parede }
      : { x, y: y - h - queda, w, h: h + queda, parede: e.parede };
  };

  // desenho preso à parede direita: (dx, dy) a partir da ponta esquerda da
  // peça, dx ao longo da parede (que desce 1 px a cada 2 para a direita) e
  // dy acima da base
  function bloco(ctx, x, yb, dx, dy, w, h, cor) {
    ctx.fillStyle = cor;
    for (let i = 0; i < w; i++) ctx.fillRect(x + dx + i, yb + Math.floor((dx + i) / 2) - dy - h, 1, h);
  }
  function letreiro(ctx, s, x, yb, dx, dy, cor) {
    ctx.fillStyle = cor;
    [...s].forEach((ch, k) => {
      const g = LETRAS[ch] ?? LETRAS[' '];
      g.forEach((linha, j) => [...linha].forEach((bit, i) => {
        const c = dx + 4 * k + i;
        if (bit === '1') ctx.fillRect(x + c, yb + Math.floor(c / 2) - dy - 5 + j, 1, 1);
      }));
    });
  }

  function desenharParede(ctx, objetos, t) {
    for (const p of layout.pecas_parede) {
      const e = manifesto[p.modelo];
      const [x, y] = naParede(p);
      const plaquinha = `plaquinha-${(p.plaquinha ?? '').toLowerCase()}`;
      const nomes = [...(e.estados ?? []).slice(0, 1),
        ...(e.camadas ?? []).filter((c) => !c.startsWith('plaquinha-') || c === plaquinha)];
      for (const n of nomes) colar(ctx, arquivo(`parede/${p.modelo}__${n}.png`), e.ancora, x, y);
      const estado = objetos[p.id];
      if (!estado || e.parede !== 'direita') continue;
      // placeholders em blocos (a arte destes estados ainda não existe)
      const pulso = 0.55 + 0.45 * Math.sin(t * 4);
      if (p.id === 'tela' && estado === 'fechado') {
        bloco(ctx, x, y, 10, 13, 44, 14, '#2f7d4a');
        bloco(ctx, x, y, 11, 14, 42, 12, '#3f9a5d');
        letreiro(ctx, 'FECHADO', x, y, 18, 17, '#eaf7ec');
      }
      if (p.id === 'quadro') {
        const marcas = estado.split(' ');
        const aviso = marcas.find((m) => m.startsWith('aviso') || m === 'convite');
        if (aviso) {
          // recado com "6": pré-aviso (amarelo) e convite (laranja)
          bloco(ctx, x, y, 42, 20, 14, 13, aviso === 'convite' ? '#f2a03d' : '#f2cf57');
          letreiro(ctx, '6', x, y, 47, 24, '#6b4b10');
          if (aviso === 'aviso-novo' || aviso === 'convite') bloco(ctx, x, y, 55, 33, 3, 3, `rgba(214,69,58,${pulso})`);
        }
        if (marcas.includes('novo')) {
          // resumo disponível: um ponto que pulsa e três linhas
          bloco(ctx, x, y, 6, 32, 3, 3, `rgba(214,150,30,${pulso})`);
          bloco(ctx, x, y, 12, 30, 22, 1, '#7a8aa8');
          bloco(ctx, x, y, 12, 25, 16, 1, '#7a8aa8');
          bloco(ctx, x, y, 12, 20, 19, 1, '#7a8aa8');
        }
        if (marcas.includes('relatorio')) {
          for (let i = 0; i < 3; i++) bloco(ctx, x, y, 8 + 6 * i, 6, 3, 6 + 5 * i, '#4b6fb3');
          bloco(ctx, x, y, 32, 30, 22, 1, '#c0503f');
          bloco(ctx, x, y, 32, 24, 16, 1, '#555c6e');
          bloco(ctx, x, y, 32, 18, 20, 1, '#555c6e');
        }
      }
      if (p.id === 'mural_alertas' && estado.startsWith('teto-')) {
        // barra do teto da categoria: 80% âmbar, 100% vermelho
        const cheio = estado === 'teto-100' ? 1 : 0.8;
        bloco(ctx, x, y, 6, 16, 20, 4, '#e8e2d4');
        bloco(ctx, x, y, 6, 16, Math.round(20 * cheio), 4, cheio >= 1 ? '#d6453a' : '#e0a33a');
      }
      if (p.id === 'calendario' && estado === 'marcado') {
        bloco(ctx, x, y, 11, 7, 5, 4, '#3f9a5d');
      }
    }
  }

  // ---- personagens
  function desenharAtor(ctx, ator, t, { x, y }) {
    if (!ator.visivel) return;
    const e = ator.e;
    const nome = ator.animacao() ? ator.anim : ator.repouso();
    const k = ator.quadro(t, nome);
    const espelhar = ator.espelhar;
    const folha = arquivo(e.folha);
    let [px, py] = [x, y];
    const a = e.animacoes[nome];
    if (a.desloca && ator.cadeira) {
      const [dx, dy] = a.desloca[k];
      px += espelhar ? -dx : dx;
      py += dy;
    }
    colar(ctx, folha, e.ancora, px, py, { espelhar, recorte: quadroDaFolha(ator.id, nome, k), alfa: ator.alfa });
    for (const s of ator.sobreposicoes(t)) {
      const [rx, ry] = s.rosto;
      colar(ctx, folha, e.ancora, px + (espelhar ? -rx : rx), py + ry,
        { espelhar, recorte: quadroDaFolha(ator.id, s.nome, s.quadro), alfa: ator.alfa });
    }
    // adereços: o envelope na mão e o selo na tela do tablet
    const mao = (ator.envelope && a.envelope) ? a.envelope[k] : null;
    if (mao && !(a.solta !== undefined && k >= a.solta)) {
      const env = manifesto.envelope;
      const ax = e.ancora[0];
      const mx = espelhar ? px - (mao[0] - ax) : px + (mao[0] - ax);
      colar(ctx, arquivo('objetos/envelope.png'), env.ancora, mx, py + (mao[1] - e.ancora[1]), { espelhar });
    }
    if (ator.selo && a.selo) {
      const s = manifesto.selo_tablet;
      const ax = e.ancora[0];
      const sx = espelhar ? px - (a.selo[0] - ax) : px + (a.selo[0] - ax);
      colar(ctx, arquivo(`objetos/selo_tablet__${ator.selo}.png`), s.ancora, sx, py + (a.selo[1] - e.ancora[1]));
    }
    return { x: px, y: py };
  }

  // a camada do tampo e o teclado de quem está à mesa
  function desenharMaosNaMesa(ctx, ator, t, [x, y]) {
    const a = ator.animacao();
    if (!a?.tampo || !ator.cadeira) return;
    const k = ator.quadro(t);
    const espelhar = ator.espelhar;
    const objeto = a.no_lugar_do_teclado ?? 'teclado';
    const o = manifesto[objeto];
    if (o?.no_personagem?.[a.mesa]) {
      const [ox, oy] = o.no_personagem[a.mesa];
      const dir = a.mesa === 'balcao' ? 'frente-dir' : 'frente-esq';
      colar(ctx, arquivo(`objetos/${objeto}__${dir}.png`), o.ancora, x + ox, y + oy);
    }
    colar(ctx, arquivo(ator.e.folha), ator.e.ancora, x, y,
      { espelhar, recorte: quadroDaFolha(ator.id, a.tampo, k) });
  }

  // ---- ordem de profundidade: quem está atrás num eixo, dividindo a faixa
  // do outro eixo, vai antes; empate pela soma
  const atras = (i, j) => {
    const [a0, a1, b0, b1] = i.fp;
    const [c0, c1, d0, d1] = j.fp;
    return (a1 <= c0 && b0 < d1 && d0 < b1) || (b1 <= d0 && a0 < c1 && c0 < a1);
  };
  function ordenar(itens) {
    const soma = (it) => it.fp.reduce((s, v) => s + v, 0) + (it.ator ? 0.01 : 0);
    const ordem = [];
    const feitos = new Set();
    while (ordem.length < itens.length) {
      const restantes = itens.filter((it) => !feitos.has(it));
      const prontos = restantes.filter((it) => !restantes.some((j) => j !== it && atras(j, it)));
      let escolhido = null;
      for (const it of (prontos.length ? prontos : restantes)) {
        if (!escolhido || soma(it) < soma(escolhido)) escolhido = it;
      }
      ordem.push(escolhido);
      feitos.add(escolhido);
    }
    return ordem;
  }

  const moveis = layout.pecas_piso.filter((p) => p.tipo !== 'reservado').map((p) => {
    const [[a, b], [da, db]] = [p.tile, p.base];
    return { p, fp: [a, a + da, b, b + db] };
  });

  // brilho de foco: o losango do piso pulsando em volta da peça
  function brilho(ctx, ids, t) {
    const pulso = 0.35 + 0.35 * Math.sin(t * 3.2);
    ctx.save();
    ctx.lineWidth = 1;
    for (const id of ids) {
      const p = pecas[id];
      if (!p) continue;
      ctx.strokeStyle = `rgba(244,192,79,${0.5 + pulso})`;
      ctx.fillStyle = `rgba(244,192,79,${pulso * 0.35})`;
      if (p.pecas_parede || p.parede) {
        const c = caixaDaParede(p);
        ctx.strokeRect(c.x + 0.5, c.y + 0.5, c.w, c.h);
        continue;
      }
      const [[a, b], [da, db]] = [p.tile, p.base];
      ctx.beginPath();
      ctx.moveTo(...P(a - 0.15, b - 0.15));
      ctx.lineTo(...P(a + da + 0.15, b - 0.15));
      ctx.lineTo(...P(a + da + 0.15, b + db + 0.15));
      ctx.lineTo(...P(a - 0.15, b + db + 0.15));
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    }
    ctx.restore();
  }

  /**
   * Desenha um quadro. cena = { atores (lista), objetos (estado por id),
   * brilhos (ids), planta (bool), t (segundos) }. Devolve as áreas de clique.
   */
  function desenhar(ctx, cena) {
    const { atores, objetos = {}, brilhos = [], planta = false, t = 0 } = cena;
    const areas = [];
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(fundo, 0, 0);
    desenharParede(ctx, objetos, t);
    for (const p of layout.pecas_parede) {
      if (['quadro', 'calendario', 'tela', 'mural_alertas'].includes(p.id)) areas.push({ id: p.id, ...caixaDaParede(p) });
    }
    if (planta) desenharPlanta(ctx, layout, P);

    // estação reservada: só a pegada, pontilhada
    for (const p of layout.pecas_piso.filter((q) => q.tipo === 'reservado')) {
      const [[a, b], [da, db]] = [p.tile, p.base];
      const cantos = [P(a, b), P(a + da, b), P(a + da, b + db), P(a, b + db), P(a, b)];
      ctx.fillStyle = css([70, 60, 50]);
      for (let i = 0; i < 4; i++) {
        const [[x0, y0], [x1, y1]] = [cantos[i], cantos[i + 1]];
        const n = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0));
        for (let k = 0; k < n; k += 3) ctx.fillRect(x0 + Math.floor((x1 - x0) * k / n), y0 + Math.floor((y1 - y0) * k / n), 1, 1);
      }
    }
    if (brilhos.length) brilho(ctx, brilhos.filter((id) => pecas[id] && !pecas[id].parede), t);

    // quem está sentado, por cadeira; quem está em pé entra na ordem pelo tile
    const sentados = new Map();
    const emPe = [];
    for (const at of atores) {
      if (!at.visivel || at.cao) continue;
      if (at.cadeira) sentados.set(at.cadeira.id, at);
      else {
        const [a, b] = [Math.floor(at.pos[0] - 1e-3), Math.floor(at.pos[1] - 1e-3)];
        emPe.push({ ator: at, fp: [a, a + 1, b, b + 1] });
      }
    }
    const caes = new Map(atores.filter((a) => a.cao).map((a) => [a.id, a]));
    const posDoSentado = new Map();

    for (const it of ordenar([...moveis, ...emPe])) {
      if (it.ator) {
        const [x, y] = P(...it.ator.pos);
        desenharAtor(ctx, it.ator, t, { x, y });
        areas.push({ id: `ator:${it.ator.id}`, x: x - 14, y: y - 66, w: 28, h: 66 });
        continue;
      }
      const { p } = it;
      const e = manifesto[p.modelo];
      const [[a, b], [da, db]] = [p.tile, p.base];
      const [ax, ay] = P(a + da, b + db);
      if (p.modelo === 'cadeira') {
        const [direcao] = OLHA_PARA[p.olha_para];
        const quem = sentados.get(p.id);
        const pos = P(a + 0.5, b + 0.5);
        const cadeira = () => colar(ctx, arquivo(`moveis/cadeira__${direcao}.png`), e.ancora, ax, ay);
        // de costas, o encosto fica entre a pessoa e a câmera: a pessoa vem antes (nota 6)
        if (quem && !deFrente(p.olha_para)) {
          desenharAtor(ctx, quem, t, { x: pos[0], y: pos[1] });
          cadeira();
        } else {
          cadeira();
          if (quem) desenharAtor(ctx, quem, t, { x: pos[0], y: pos[1] });
        }
        if (quem) {
          posDoSentado.set(p.id, pos);
          areas.push({ id: `ator:${quem.id}`, x: pos[0] - 14, y: pos[1] - 64, w: 28, h: 60 });
        }
        continue;
      }
      let estado = null;
      if (p.modelo === 'malote') estado = objetos.malote === 'com-envelope' || objetos.malote === 'sinalizado' ? 'com-envelope' : 'vazio';
      const caminhoImg = estado ? `moveis/${p.modelo}__${estado}.png` : arquivos(p.modelo, e)[0];
      colar(ctx, arquivo(caminhoImg), e.ancora, ax, ay);
      if (p.modelo === 'malote' && objetos.malote === 'sinalizado') {
        // bandeirinha vermelha (sem arte ainda)
        ctx.fillStyle = '#5a4632';
        ctx.fillRect(ax - 4, ay - 46, 1, 14);
        ctx.fillStyle = '#d6453a';
        ctx.fillRect(ax - 3, ay - 46, 6, 4);
      }
      // à mesa: teclado e camada do tampo de quem senta nela
      const cid = cadeiraDaMesa.get(p.id);
      const quem = cid && sentados.get(cid);
      if (quem && posDoSentado.has(cid)) desenharMaosNaMesa(ctx, quem, t, posDoSentado.get(cid));
      for (const obj of p.objetos ?? []) {
        const o = manifesto[obj];
        const [ex, ey] = e.encaixes[obj];
        if (obj === 'sineta' && objetos.sineta === 'tocando') {
          const s = o.animacoes.tocando;
          const k = Math.floor(t * s.fps) % s.quadros;
          colar(ctx, arquivo(s.folha), s.ancora, ax + ex, ay + ey, { recorte: [k * s.tela[0], 0, s.tela[0], s.tela[1]] });
        } else {
          colar(ctx, arquivo(arquivos(obj, o)[0]), o.ancora, ax + ex, ay + ey);
        }
      }
      if (CAMA[p.modelo]) {
        const cao = caes.get(CAMA[p.modelo]);
        if (cao?.visivel) {
          const [x, y] = P(a + 0.5, b + 0.5);
          const nome = cao.animacao() ? cao.anim : 'sentado_frente';
          colar(ctx, arquivo(cao.e.folha), cao.e.ancora, x, y,
            { espelhar: true, recorte: quadroDaFolha(cao.id, nome, cao.quadro(t, nome)) });
          areas.push({ id: `ator:${cao.id}`, x: x - 20, y: y - 34, w: 40, h: 36 });
        }
      }
      if (MESAS.has(p.modelo) || p.modelo === 'malote') {
        const img = arquivo(caminhoImg);
        areas.push({ id: p.id, x: ax - e.ancora[0], y: ay - e.ancora[1], w: img.width, h: img.height });
      }
    }
    // o brilho das peças de parede vai por cima
    const naParedeBrilho = brilhos.filter((id) => pecas[id]?.parede);
    if (naParedeBrilho.length) brilho(ctx, naParedeBrilho, t);
    return areas;
  }

  /** Ponto da cabeça de um ator na tela (para o balão). */
  function cabeca(ator) {
    if (ator.cao) {
      const p = layout.pecas_piso.find((q) => CAMA[q.modelo] === ator.id);
      const [x, y] = P(p.tile[0] + 0.5, p.tile[1] + 0.5);
      return [x, y - 30];
    }
    if (ator.cadeira) {
      const [x, y] = P(ator.cadeira.tile[0] + 0.5, ator.cadeira.tile[1] + 0.5);
      return [x, y - 66];
    }
    const [x, y] = P(...ator.pos);
    return [x, y - 70];
  }

  return { geo, P, desenhar, cabeca, pecas, caixaDaParede };
}

// marcas da planta no piso: entrada, pontos de uso e frentes de porta em
// azul, circulação obrigatória em laranja
function desenharPlanta(ctx, layout, P) {
  const losango = ([a, b], preencher, contorno) => {
    ctx.beginPath();
    ctx.moveTo(...P(a, b));
    ctx.lineTo(...P(a + 1, b));
    ctx.lineTo(...P(a + 1, b + 1));
    ctx.lineTo(...P(a, b + 1));
    ctx.closePath();
    ctx.fillStyle = preencher;
    ctx.fill();
    ctx.strokeStyle = contorno;
    ctx.stroke();
  };
  for (const k of tilesDeAcesso(layout)) losango(k.split(',').map(Number), 'rgba(70,120,220,0.35)', 'rgba(40,80,180,0.9)');
  for (const t of circulacaoObrigatoria(layout) ?? []) losango(t, 'rgba(240,140,40,0.35)', 'rgba(200,100,20,0.9)');
}
