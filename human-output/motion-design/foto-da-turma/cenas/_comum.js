/* _comum.js — a turma em camadas recortadas da ilustração.
   A ilustração foi separada em camadas (corpo e cabeça de cada pessoa, mais o braço de quem abraça
   e a mão no ombro), com as partes escondidas completadas por trás. Aqui mora o palco (fundo
   xadrez, moldura, estrelas, pessoas, flash), a coreografia inteira como função pura do tempo do
   filme e a câmera. As três cenas chamam Turma.aplicar(tGlobal): o estado é contínuo entre elas.

   Unidades: px da ilustração original (1055 × 1491). As camadas estão em 2× e moram num palco de
   2110 × 3760 (a ilustração no meio, com 389 px de sobra em cima e embaixo para o 9:16). */
(function () {
  const Z = 2, OY = 389, PW = 2110, PH = 3760;
  const CX = PW / 2, CY = OY + 1491; // centro da ilustração no palco
  const T_FLASH = 8.0;

  const CAMADAS = {"B1b": [72, 550, 522, 2024], "B2b": [444, 558, 456, 540], "B3b": [880, 598, 474, 568], "B4b": [1212, 602, 418, 450], "B5b": [1536, 568, 496, 1040], "B4a": [1704, 552, 190, 368], "B1h": [366, 334, 258, 302], "B2h": [656, 384, 258, 254], "B3h": [1024, 424, 220, 246], "B4h": [1256, 406, 242, 264], "B5h": [1474, 412, 240, 256], "M5b": [1444, 902, 446, 804], "M5h": [1372, 732, 490, 588], "M4b": [1054, 1004, 532, 1052], "M4h": [1134, 780, 348, 648], "M2b": [662, 912, 358, 1112], "M2h": [664, 770, 296, 382], "M1b": [188, 858, 544, 1200], "M1a": [176, 1100, 132, 630], "M1h": [302, 726, 406, 418], "M3b": [828, 1098, 228, 686], "M3a": [1010, 1176, 148, 424], "M3h": [786, 876, 412, 522], "M6b": [1516, 1254, 524, 1244], "M6h": [1438, 1114, 258, 248], "F1b": [208, 1750, 608, 1046], "F1a": [388, 2064, 308, 294], "F3b": [1088, 1778, 818, 1044], "F3m": [1344, 2198, 446, 470], "F2b": [520, 1812, 838, 1000], "F1h": [576, 1546, 226, 272], "F3h": [1104, 1630, 390, 278], "F2h": [878, 1586, 290, 304], "F2v": [948, 1896, 340, 506], "F1m": [764, 1802, 162, 216]};
  // a ordem de empilhamento (de trás para a frente) é a mesma em que as camadas foram completadas
  const ORDEM = Object.keys(CAMADAS);
  const ESTRELAS = [["estrela-02", 48, 421, 200, 214, 148, 529], ["estrela-00", 706, 389, 184, 182, 797, 480], ["estrela-01", 1230, 389, 176, 180, 1315, 477], ["estrela-03", 1860, 423, 202, 208, 1959, 528], ["estrela-05", 1936, 925, 158, 164, 2015, 1007], ["estrela-07", 1938, 1813, 152, 158, 2014, 1890], ["estrela-09", 1906, 2705, 182, 186, 1996, 2797], ["estrela-11", 1866, 3121, 198, 206, 1964, 3224], ["estrela-13", 1236, 3203, 160, 166, 1315, 3284], ["estrela-12", 718, 3197, 160, 168, 797, 3280], ["estrela-10", 40, 3121, 200, 208, 139, 3224], ["estrela-08", 26, 2685, 172, 178, 112, 2771], ["estrela-06", 20, 1813, 152, 156, 95, 1890], ["estrela-04", 20, 925, 156, 168, 97, 1008]]; // em volta, no sentido do relógio

  /* Pessoas. Só o que uma pessoa faz: os corpos ficam parados; a cabeça inclina a partir do pescoço
     e se desloca um fio, os braços fazem um gesto lento de cada vez. Nada gira em 3D, nada estica,
     nada balança sozinho.
     n = pescoço (pivô da cabeça), em px da ilustração original.
     olha = [quando, inclinação em graus (+ para a direita), deslocamento em px]: para quem a cabeça
     pende na conversa. risos e acenos = [início, duração]. */
  const P = {
    B1: { n: [230, 318], olha: [[0, 5, 2]], risos: [[1.0, 1.1]], acenos: [[2.4, 0.8]] },
    B2: { n: [360, 318], olha: [[0, -5, -2], [2.7, 4, 1.5]], risos: [[1.1, 1.0]], acenos: [] },
    B3: { n: [562, 335], olha: [[0, 4, 1.5], [2.35, -4, -1.5]], risos: [[2.85, 0.9]], acenos: [[1.35, 0.8]] },
    B4: { n: [700, 338], olha: [[0, 6, 2]], risos: [[2.55, 1.0]], acenos: [[1.55, 0.7]] },
    B5: { n: [835, 335], olha: [[0, -6, -2]], risos: [[2.6, 1.05]], acenos: [] },
    M1: { n: [262, 480], olha: [[0, 4, 1.5]], risos: [[3.05, 0.95]], acenos: [[1.7, 0.8]] },
    M2: { n: [398, 492], olha: [[0, -5, -2], [2.25, 3.5, 1.5], [3.0, -5, -2]], risos: [[3.15, 0.9]], acenos: [] },
    M3: { n: [500, 560], olha: [[0, 5, 2], [2.45, -3.5, -1.5]], risos: [[1.5, 1.05]], acenos: [] },
    M4: { n: [612, 510], olha: [[0, -5, -2]], risos: [[1.6, 1.1]], acenos: [[2.8, 0.8]] },
    M5: { n: [765, 498], olha: [[0, 6, 2]], risos: [[1.25, 0.95]], acenos: [[2.45, 0.8]] },
    M6: { n: [835, 672], olha: [[0, -5, -2]], risos: [[1.4, 0.9]], acenos: [] },
    F1: { n: [335, 905], olha: [[0, 5, 2]], risos: [[2.1, 0.95]], acenos: [[1.0, 0.7]] },
    F2: { n: [505, 935], olha: [[0, -4, -1.5], [2.5, 4, 1.5]], risos: [[2.2, 1.05]], acenos: [] },
    F3: { n: [680, 955], olha: [[0, -6, -2]], risos: [[2.3, 0.9]], acenos: [[1.2, 0.7]] },
  };
  const NOMES = Object.keys(P);

  /* Membros: pivô (cotovelo ou ombro) e dono. Só três gestos, lentos, um de cada vez. */
  const MEMBROS = {
    B4a: { dono: 'B4', piv: [872, 292] },  // o braço que abraça: puxa o amigo para perto na pose 1
    F1m: { dono: 'F1', piv: [392, 925] },  // a mão no ombro: aperta o amigo na pose 1
    F2v: { dono: 'F2', piv: [610, 1175] }, // o "V": sobe do peito até o queixo para a foto
    F1a: { dono: 'F1', piv: [198, 1072] }, M1a: { dono: 'M1', piv: [125, 552] }, // parados
    M3a: { dono: 'M3', piv: [545, 588] }, F3m: { dono: 'F3', piv: [878, 1135] },
  };
  const MEMBROS_DE = {};
  for (const [k, m] of Object.entries(MEMBROS)) (MEMBROS_DE[m.dono] = MEMBROS_DE[m.dono] || []).push(k);

  /* ─── curvas: Hermite monotônica por chaves (velocidade contínua, sem passar do valor) ─── */
  function trilha(ch, t) {
    const n = ch.length;
    if (t <= ch[0][0]) return ch[0][1];
    if (t >= ch[n - 1][0]) return ch[n - 1][1];
    let i = 0;
    while (t > ch[i + 1][0]) i++;
    const [t0, p0] = ch[i], [t1, p1] = ch[i + 1];
    const tan = (j) => {
      if (j <= 0 || j >= n - 1) return 0;
      const a = (ch[j][1] - ch[j - 1][1]) / (ch[j][0] - ch[j - 1][0]);
      const b = (ch[j + 1][1] - ch[j][1]) / (ch[j + 1][0] - ch[j][0]);
      if (a * b <= 0) return 0;
      return (2 * a * b) / (a + b);
    };
    const d = t1 - t0, u = (t - t0) / d, u2 = u * u, u3 = u2 * u;
    return (2 * u3 - 3 * u2 + 1) * p0 + (u3 - 2 * u2 + u) * tan(i) * d + (-2 * u3 + 3 * u2) * p1 + (u3 - u2) * tan(i + 1) * d;
  }
  const limpar = (ch) => { ch.sort((a, b) => a[0] - b[0]); for (let j = 1; j < ch.length; j++) if (ch[j][0] <= ch[j - 1][0] + 1e-3) ch[j][0] = ch[j - 1][0] + 0.02; return ch; };
  const r01 = (i, k) => { const x = Math.sin((i + 1) * 127.1 + k * 311.7) * 43758.5453; return x - Math.floor(x); };
  const sinal = (v) => (v > 0 ? 1 : v < 0 ? -1 : 0);
  const suave = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));

  /* ─── a coreografia das cabeças, montada uma vez em chaves ─── */
  const COREO = {};
  NOMES.forEach((nome, i) => {
    const q = P[nome];
    const lado = q.n[0] - 527, dir = sinal(lado);
    const alt = i % 2 ? 1 : -1;
    const rea = 0.16 * r01(i, 1);                       // cada um reage no seu tempo
    const dm = 0.55 + 0.15 * r01(i, 2);                 // e leva o seu tempo para mexer a cabeça
    const virada = 3.85 + 0.03 * Math.abs(lado) / 40 + rea; // a chamada: olham para a câmera, do centro para as pontas
    const trilhas = {};
    ['roll', 'hx'].forEach((eixo, e) => {
      const ch = [];
      q.olha.forEach((o, j) => {
        if (j === 0) ch.push([0, o[1 + e]]);
        else { ch.push([o[0] + rea, q.olha[j - 1][1 + e]]); ch.push([o[0] + rea + dm, o[1 + e]]); }
      });
      const ult = q.olha[q.olha.length - 1][1 + e];
      // pose 1 "aperta!": encostam a cabeça para o centro; pose 2: cabeças pendendo para lados alternados
      const p1 = [-dir * (4 + 3 * Math.min(1, Math.abs(lado) / 420)), -dir * 2.5][e];
      const p2 = [alt * 4, alt * 1.5][e];
      ch.push([virada, ult], [virada + dm, 0], [5.0 + rea, 0], [5.0 + rea + dm, p1], [5.9 + rea, p1], [5.9 + rea + dm, p2], [6.85 + rea, p2], [6.85 + rea + dm, 0]);
      trilhas[eixo] = limpar(ch);
    });
    // pose 2 também levanta um pouco o queixo: a cabeça sobe um fio
    trilhas.hy = limpar([[0, 0], [5.9 + rea, 0], [5.9 + rea + dm, -1.5], [6.85 + rea, -1.5], [6.85 + rea + dm, 0]]);
    COREO[nome] = trilhas;
  });

  /* Estado de uma cabeça no tempo do filme (congela no flash: a foto é tirada ali). */
  function estado(nome, t) {
    const c = COREO[nome], q = P[nome];
    t = Math.min(t, T_FLASH);
    let roll = trilha(c.roll, t), hx = trilha(c.hx, t), hy = trilha(c.hy, t);
    const lado = sinal(q.olha[0][1]);
    // risada: a cabeça vai para trás e para o lado do amigo, dá duas ou três sacudidas que diminuem e volta
    for (const [t0, d] of q.risos) {
      const u = (t - t0) / d;
      if (u <= 0 || u >= 1) continue;
      const sobe = suave(u / 0.25) * (1 - suave((u - 0.6) / 0.4)); // vai, segura, volta
      const ha = Math.sin(Math.PI * 2 * 3.2 * (t - t0)) * (1 - u);   // "ha-ha-ha", cada vez mais fraco
      hy += -3.2 * sobe + 0.9 * ha * sobe;
      roll += lado * 2.5 * sobe;
    }
    // aceno de "uhum": a cabeça desce e sobe duas vezes, devagar
    for (const [t0, d] of q.acenos) {
      const u = (t - t0) / d;
      if (u <= 0 || u >= 1) continue;
      hy += 1.4 * Math.pow(Math.sin(Math.PI * 2 * u), 2);
    }
    return { roll, hx, hy };
  }

  /* Ângulo de cada membro no tempo do filme: só gestos lentos, sem oscilar. */
  function membro(k, t) {
    t = Math.min(t, T_FLASH);
    switch (k) {
      case 'F2v': return trilha([[0, -6], [6.1, -6], [6.95, 0]], t);                       // o V sobe até o queixo
      case 'F1m': return trilha([[0, 0], [5.05, 0], [5.6, 2.5], [6.0, 2.5], [6.6, 0]], t);   // aperta o ombro
      case 'B4a': return trilha([[0, 0], [5.05, 0], [5.6, -1.8], [6.0, -1.8], [6.6, 0]], t); // puxa o amigo
    }
    return 0;
  }

  /* Câmera: nasce perto dos rostos e abre até a foto inteira no clique. */
  function camera(t) {
    if (t < T_FLASH) {
      const zoom = trilha([[0, 1.3], [2.6, 1.15], [4.5, 1.07], [6.6, 1.025], [T_FLASH, 1.0]], t);
      const fy = trilha([[0, 690], [3.0, 715], [5.5, 738], [T_FLASH, 745.5]], t);
      const fx = 527.5 + 8 * Math.sin((2 * Math.PI * t) / 6.5) * Math.min(1, (T_FLASH - t) / 2);
      return { zoom, fx, fy };
    }
    // a foto: parada no enquadramento exato enquanto a moldura chega; depois um push-in vivo e lento
    return { zoom: 1 + 0.003 * Math.max(0, t - 9.4) ** 1.5, fx: 527.5, fy: 745.5 };
  }

  const f = (v) => (Math.round(v * 1000) / 1000).toString();
  const PX = (x) => x * Z, PY = (y) => y * Z + OY; // ilustração → palco

  function render(c) {
    const img = (nome, x, y, w, h, cls, extra = '') =>
      `<img class="tc ${cls}" data-id="${nome}" src="${c.ativo(nome)}" style="left:${x}px;top:${y}px;width:${w}px;height:${h}px;transform-origin:${-x}px ${-y}px" alt="" draggable="false"${extra}>`;
    const pessoas = ORDEM.map((k) => {
      const [x, y, w, h] = CAMADAS[k];
      return img(k, x, y + OY, w, h, 'pessoa');
    }).join('');
    const estrelas = ESTRELAS.map(([k, x, y, w, h]) => img(k, x, y, w, h, 'estrela')).join('');
    return `
      <div class="palco">
        <img class="fundo" src="${c.ativo('fundo')}" alt="" draggable="false">
        <div class="moldura-grupo">
          <img class="moldura" src="${c.ativo('moldura')}" alt="" draggable="false">
          ${estrelas}
        </div>
        <div class="turma">${pessoas}</div>
      </div>
      <div class="brilho-foto"></div>
      <div class="flash"></div>`;
  }

  function montar(el, api) {
    el.palco = el.$('.palco');
    el.camadas = {};
    el.$$('.pessoa').forEach((im) => (el.camadas[im.dataset.id] = im));
    el.moldura = el.$('.moldura');
    api.pintura.camada(el.moldura); // camada própria: a escala da moldura não re-rasteriza no meio do gesto
    el.estrelas = el.$$('.estrela').map((im, i) => ({ el: im, i, cx: ESTRELAS[i][5], cy: ESTRELAS[i][6] }));
    el.brilho = el.$('.brilho-foto');
    el.flash = el.$('.flash');
    api.pintura.filtroFixo(el.palco); // a revelação é um filtro contínuo, ligado a cena toda
    el.k = api.largura / PW;
  }

  /* Aplica o filme inteiro no tempo global t. */
  function aplicar(t, el, api) {
    const { clamp, prog, ease, lerp } = api;
    // pessoas: os corpos ficam como na arte; a cabeça inclina no pescoço; os braços giram na junta
    for (const nome of NOMES) {
      const q = P[nome], s = estado(nome, t);
      const nx = PX(q.n[0]), ny = PY(q.n[1]);
      api.set(el.camadas[`${nome}h`], { pre: `translate(${f(nx + s.hx * Z)}px, ${f(ny + s.hy * Z)}px) rotate(${f(s.roll)}deg) translate(${f(-nx)}px, ${f(-ny)}px)` });
      for (const k of MEMBROS_DE[nome] || []) {
        const [mx, my] = MEMBROS[k].piv;
        api.set(el.camadas[k], { pre: `translate(${f(PX(mx))}px, ${f(PY(my))}px) rotate(${f(membro(k, t))}deg) translate(${f(-PX(mx))}px, ${f(-PY(my))}px)` });
      }
    }
    // câmera
    const cam = camera(t), k = el.k * cam.zoom;
    const tx = api.largura / 2 - PX(cam.fx) * k, ty = api.altura / 2 - PY(cam.fy) * k;
    // o flash: estoura em 3 quadros e apaga até zero em 0,6 s; a foto nasce clara e revela a cor
    const tf = t - T_FLASH;
    const fl = tf < 0 ? 0 : tf < 0.05 ? ease.outCubic(tf / 0.05) : Math.exp(-(tf - 0.05) / 0.15) * (1 - api.suave(prog(tf, 0.3, 0.6)));
    const rev = tf < 0 ? 0 : 1 - ease.outCubic(clamp((tf - 0.02) / 0.95));
    api.set(el.palco, {
      pre: `translate(${f(tx)}px, ${f(ty)}px) scale(${Math.round(k * 1e6) / 1e6})`,
      bright: 1 + 0.5 * rev,
      sat: 1 - 0.4 * rev,
    });
    api.set(el.flash, { o: 0.96 * fl });
    // a moldura chega de fora para dentro, elástica, e assenta (antes do clique ela não existe)
    const tm = t - (T_FLASH + 0.28);
    const ent = ease.inOutSine(clamp(tm / 0.14));
    const m = tm <= 0 ? 0 : ent * (1 - Math.exp(-6.2 * tm) * Math.cos(2 * Math.PI * 1.15 * tm));
    api.set(el.moldura, {
      pre: `translate(${CX}px, ${CY}px) scale(${f(1 + 0.32 * (1 - m))}, ${f(1 + 0.52 * (1 - m))}) translate(${-CX}px, ${-CY}px)`,
      o: t < T_FLASH ? 0 : 1,
    });
    // estrelas: uma a uma em volta, com mola; no hold giram e cintilam devagar
    for (const s of el.estrelas) {
      const t0 = T_FLASH + 1.0 + s.i * 0.045;
      const u = t - t0;
      const ab = clamp(u / 0.07);
      const sc = u <= 0 ? 0.5 : 1 - 0.5 * Math.exp(-7 * u) * Math.cos(2 * Math.PI * 1.7 * u);
      const vivo = Math.max(0, Math.min(1, (t - t0 - 0.5) / 1.2));
      const rot = (u <= 0 ? -70 : -70 * Math.exp(-6 * u) * Math.cos(2 * Math.PI * 0.9 * u)) + vivo * 11 * Math.sin((2 * Math.PI * (t - t0)) / (3.3 + 0.37 * (s.i % 4)) + s.i);
      const pul = 1 + vivo * 0.05 * Math.sin((2 * Math.PI * (t - t0)) / (2.1 + 0.29 * (s.i % 3)) + s.i * 1.7);
      api.set(s.el, {
        pre: `translate(${PX(0) + s.cx}px, ${s.cy}px) rotate(${f(rot)}deg) scale(${f(sc * pul)}) translate(${-s.cx}px, ${-s.cy}px)`,
        o: ab,
      });
    }
    // um brilho de papel fotográfico atravessa a foto uma vez
    const pb = prog(t, T_FLASH + 1.7, T_FLASH + 2.6);
    api.set(el.brilho, { x: lerp(-110, 110, ease.inOutSine(pb)), o: Math.sin(Math.PI * pb) * 0.8 });
  }

  window.Turma = { render, montar, aplicar, estado, membro, camera, T_FLASH, P, COREO };
})();
