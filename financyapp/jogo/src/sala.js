// Desenha a sala parada no canvas, em 1x: paredes, piso, peças de parede,
// móveis com os objetos nos encaixes, cada um no seu posto, sentado, e os
// cachorros nas camas. Tudo vem do layout da planta e do manifesto dos
// assets. A página amplia 2x sem suavizar (image-rendering: pixelated).

import { arquivos } from './carregar.js';
import { circulacaoObrigatoria, tilesDeAcesso } from './validacao.js';

const MARGEM = 20;

// quem senta olhando para cada lado: a direção da cadeira e se o sentado de
// frente sai espelhado (frente-dir = +A sem espelhar, frente-esq = +B espelhado)
const OLHA_PARA = {
  '+A': ['frente-dir', false],
  '+B': ['frente-esq', true],
  '-B': ['costas-dir', false],
  '-A': ['costas-esq', true],
};
const CAMA = { manta_flora: 'flora', caminha_lupin: 'lupin' };

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

export function desenharSala(ctx, { manifesto, layout, imagens }, { planta = false } = {}) {
  const [A, B] = layout.sala.tiles;
  const { largura, altura, cx, cy } = tamanhoDaSala(layout, manifesto);
  const P = (s, t, z = 0) => [cx + 32 * (s - t), cy + 16 * (s + t) - z];
  const bordaDoPiso = (x) => cy + Math.floor(Math.abs(x - cx) / 2);

  const pixel = (x, y, cor) => {
    ctx.fillStyle = cor;
    ctx.fillRect(x, y, 1, 1);
  };

  // cola uma imagem (ou um quadro dela) com a âncora no ponto (x, y)
  const colar = (img, ancora, x, y, { espelhar = false, recorte = null } = {}) => {
    const [sx, sy, w, h] = recorte ?? [0, 0, img.width, img.height];
    const ax = espelhar ? w - ancora[0] : ancora[0];
    const dx = Math.round(x - ax);
    const dy = Math.round(y - ancora[1]);
    if (!espelhar) {
      ctx.drawImage(img, sx, sy, w, h, dx, dy, w, h);
      return;
    }
    ctx.save();
    ctx.translate(dx + w, dy);
    ctx.scale(-1, 1);
    ctx.drawImage(img, sx, sy, w, h, 0, 0, w, h);
    ctx.restore();
  };
  const colarArquivo = (caminho, ancora, x, y, opcoes) => colar(imagens.get(caminho), ancora, x, y, opcoes);
  const colarPersonagem = (id, animacao, x, y, opcoes = {}) => {
    const e = manifesto[id];
    const [w, h] = e.tela;
    const linha = e.animacoes[animacao].linha;
    colar(imagens.get(e.folha), e.ancora, x, y, { ...opcoes, recorte: [0, h * linha, w, h] });
  };

  ctx.imageSmoothingEnabled = false;
  ctx.fillStyle = css([24, 30, 52]);
  ctx.fillRect(0, 0, largura, altura);

  // paredes: o jogo desenha com as cores do manifesto
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

  // piso, com a borda da frente
  const piso = manifesto.piso_madeira;
  for (let a = 0; a < A; a++) {
    for (let b = 0; b < B; b++) {
      const v = piso.variacoes[(a * 7 + b * 3 + a * b) % 3];
      colarArquivo(`piso/piso_madeira__${v}.png`, piso.ancora, ...P(a + 1, b + 1));
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

  // peças de parede: a âncora vai na ponta esquerda (na tela) do vão, na
  // altura da base (parede esquerda: o fim do último tile; direita: o
  // começo do primeiro)
  for (const p of layout.pecas_parede) {
    const e = manifesto[p.modelo];
    let [x, y] = e.parede === 'esquerda' ? P(0, p.tiles.at(-1) + 1) : P(p.tiles[0], 0);
    y -= e.altura[0];
    const plaquinha = `plaquinha-${(p.plaquinha ?? '').toLowerCase()}`;
    const nomes = [...(e.estados ?? []).slice(0, 1),
      ...(e.camadas ?? []).filter((c) => !c.startsWith('plaquinha-') || c === plaquinha)];
    for (const n of nomes) colarArquivo(`parede/${p.modelo}__${n}.png`, e.ancora, x, y);
  }

  // a planta por cima do piso: acesso, circulação e a estação reservada
  if (planta) desenharPlanta(ctx, layout, P);

  // estação reservada: só a pegada, pontilhada
  for (const p of layout.pecas_piso.filter((p) => p.tipo === 'reservado')) {
    const [[a, b], [da, db]] = [p.tile, p.base];
    const cantos = [P(a, b), P(a + da, b), P(a + da, b + db), P(a, b + db), P(a, b)];
    for (let i = 0; i < 4; i++) {
      const [[x0, y0], [x1, y1]] = [cantos[i], cantos[i + 1]];
      const n = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0));
      for (let k = 0; k < n; k += 3) {
        pixel(x0 + Math.floor((x1 - x0) * k / n), y0 + Math.floor((y1 - y0) * k / n), css([70, 60, 50]));
      }
    }
  }

  // móveis em ordem de profundidade: quem está atrás num eixo, dividindo a
  // faixa do outro eixo, vai antes
  const itens = layout.pecas_piso.filter((p) => p.tipo !== 'reservado').map((p) => {
    const [[a, b], [da, db]] = [p.tile, p.base];
    return { p, fp: [a, a + da, b, b + db] };
  });
  const atras = (i, j) => {
    const [a0, a1, b0, b1] = i.fp;
    const [c0, c1, d0, d1] = j.fp;
    return (a1 <= c0 && b0 < d1 && d0 < b1) || (b1 <= d0 && a0 < c1 && c0 < a1);
  };
  const soma = (k) => itens[k].fp.reduce((s, v) => s + v, 0);
  const ordem = [];
  const feitos = new Set();
  while (ordem.length < itens.length) {
    const restantes = itens.map((_, k) => k).filter((k) => !feitos.has(k));
    const prontos = restantes.filter((k) => !restantes.some((j) => j !== k && atras(itens[j], itens[k])));
    let escolhido = null;
    for (const k of (prontos.length ? prontos : restantes)) {
      if (escolhido === null || soma(k) < soma(escolhido)) escolhido = k;
    }
    ordem.push(escolhido);
    feitos.add(escolhido);
  }

  for (const k of ordem) {
    const { p } = itens[k];
    const e = manifesto[p.modelo];
    const [[a, b], [da, db]] = [p.tile, p.base];
    const [ax, ay] = P(a + da, b + db);
    if (p.modelo === 'cadeira') {
      const [direcao, espelhar] = OLHA_PARA[p.olha_para];
      colarArquivo(`moveis/cadeira__${direcao}.png`, e.ancora, ax, ay);
      const quem = (p.ocupante_padrao ?? '').toLowerCase();
      // no corte 1 cada um está no seu posto; as cadeiras da reunião ficam vazias
      if (p.zona !== 'reuniao' && manifesto[quem]?.folha) {
        colarPersonagem(quem, 'sentado_frente', ...P(a + 0.5, b + 0.5), { espelhar });
      }
      continue;
    }
    colarArquivo(arquivos(p.modelo, e)[0], e.ancora, ax, ay);
    for (const obj of p.objetos ?? []) {
      const o = manifesto[obj];
      const [ex, ey] = e.encaixes[obj];
      colarArquivo(arquivos(obj, o)[0], o.ancora, ax + ex, ay + ey);
    }
    if (CAMA[p.modelo]) colarPersonagem(CAMA[p.modelo], 'sentado_frente', ...P(a + 0.5, b + 0.5), { espelhar: true });
  }
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
