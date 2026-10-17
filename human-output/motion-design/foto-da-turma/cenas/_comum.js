/* _comum.js — a turma como bonecos de recorte.
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

  const CAMADAS = {"B1b": [72, 550, 522, 2024], "B2b": [444, 558, 456, 550], "B3b": [880, 598, 474, 578], "B4b": [1212, 602, 418, 456], "B5b": [1536, 568, 496, 1044], "B4a": [1704, 552, 190, 368], "B1h": [366, 334, 258, 302], "B2h": [656, 384, 258, 254], "B3h": [1024, 424, 220, 246], "B4h": [1256, 406, 246, 264], "B5h": [1474, 412, 240, 256], "M5b": [1444, 902, 446, 812], "M5h": [1366, 732, 496, 590], "M4b": [1054, 1004, 532, 1056], "M4h": [1132, 780, 350, 648], "M2b": [662, 912, 358, 1118], "M2h": [658, 770, 308, 382], "M1b": [176, 858, 556, 1202], "M1h": [302, 726, 406, 418], "M3b": [828, 1098, 330, 692], "M3h": [786, 876, 412, 522], "M6b": [1516, 1254, 524, 1244], "M6h": [1438, 1114, 258, 248], "F1b": [208, 1750, 608, 1046], "F3b": [1088, 1778, 818, 1044], "F2b": [520, 1812, 838, 1000], "F1h": [576, 1546, 226, 272], "F3h": [1104, 1630, 390, 278], "F2h": [876, 1586, 292, 304], "F1m": [764, 1802, 162, 216]};
  // a ordem de empilhamento (de trás para a frente) é a mesma em que as camadas foram completadas
  const ORDEM = Object.keys(CAMADAS);
  const ESTRELAS = [["estrela-02", 48, 421, 200, 214, 148, 529], ["estrela-00", 706, 389, 184, 182, 797, 480], ["estrela-01", 1230, 389, 176, 180, 1315, 477], ["estrela-03", 1860, 423, 202, 208, 1959, 528], ["estrela-05", 1936, 925, 158, 164, 2015, 1007], ["estrela-07", 1938, 1813, 152, 158, 2014, 1890], ["estrela-09", 1906, 2705, 182, 186, 1996, 2797], ["estrela-11", 1866, 3121, 198, 206, 1964, 3224], ["estrela-13", 1236, 3203, 160, 166, 1315, 3284], ["estrela-12", 718, 3197, 160, 168, 797, 3280], ["estrela-10", 40, 3121, 200, 208, 139, 3224], ["estrela-08", 26, 2685, 172, 178, 112, 2771], ["estrela-06", 20, 1813, 152, 156, 95, 1890], ["estrela-04", 20, 925, 156, 168, 97, 1008]]; // em volta, no sentido do relógio

  /* Pessoas: n = pescoço (pivô da cabeça), p = pé (pivô do corpo), par = para quem olha na conversa
     (+1 direita, -1 esquerda), risos = [início, duração] em s. */
  const P = {
    B1: { n: [230, 318], p: [190, 1240], fila: 'B', olha: [[0.3, 1, 0], [3.0, 1, 0]], risos: [[1.0, 0.95]] },
    B2: { n: [360, 318], p: [360, 1240], fila: 'B', olha: [[0.4, -1, 0], [2.7, 1, 0]], risos: [[1.05, 0.85]] },
    B3: { n: [562, 335], p: [560, 1240], fila: 'B', olha: [[0.5, 1, 0], [2.4, -1, 0]], risos: [[2.75, 0.6]] },
    B4: { n: [700, 338], p: [700, 1240], fila: 'B', olha: [[0.35, 1, 0]], risos: [[2.55, 0.85]], extra: ['B4a'] },
    B5: { n: [835, 335], p: [880, 1240], fila: 'B', olha: [[0.45, -1, 0]], risos: [[2.5, 0.95]] },
    M1: { n: [262, 480], p: [210, 1300], fila: 'M', olha: [[0.4, 1, 0]], risos: [[3.0, 0.75]] },
    M2: { n: [398, 492], p: [390, 1300], fila: 'M', olha: [[0.5, -1, 0], [2.3, 1, 0], [3.05, -1, 0]], risos: [[3.05, 0.8]] },
    M3: { n: [500, 560], p: [480, 1300], fila: 'M', olha: [[0.3, 1, 0], [2.4, -1, 0]], risos: [[1.5, 0.9]] },
    M4: { n: [612, 510], p: [650, 1300], fila: 'M', olha: [[0.45, -1, 0]], risos: [[1.55, 1.0]] },
    M5: { n: [765, 498], p: [790, 1300], fila: 'M', olha: [[0.35, 1, 1]], risos: [[1.25, 0.8]] },
    M6: { n: [835, 672], p: [880, 1250], fila: 'M', olha: [[0.5, -1, -1]], risos: [[1.3, 0.7]] },
    F1: { n: [335, 905], p: [220, 1385], fila: 'F', olha: [[0.4, 1, 0]], risos: [[2.1, 0.8]], extra: ['F1m'] },
    F2: { n: [505, 935], p: [450, 1385], fila: 'F', olha: [[0.5, -1, 0], [2.45, 1, 0]], risos: [[2.15, 0.9]] },
    F3: { n: [680, 955], p: [790, 1385], fila: 'F', olha: [[0.45, -1, 0]], risos: [[2.25, 0.75]] },
  };
  const NOMES = Object.keys(P);
  const DONO = {}; // camada → pessoa e parte
  for (const k of ORDEM) DONO[k] = { p: k.slice(0, 2), parte: k === 'B4a' || k === 'F1m' ? 'corpo' : k[2] === 'h' ? 'cabeca' : 'corpo' };

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
  const r01 = (i, k) => { const x = Math.sin((i + 1) * 127.1 + k * 311.7) * 43758.5453; return x - Math.floor(x); };
  const sinal = (v) => (v > 0 ? 1 : v < 0 ? -1 : 0);

  /* ─── a coreografia, montada uma vez em chaves ─── */
  const limpar = (ch) => { ch.sort((a, b) => a[0] - b[0]); for (let j = 1; j < ch.length; j++) if (ch[j][0] <= ch[j - 1][0] + 1e-3) ch[j][0] = ch[j - 1][0] + 0.02; return ch; };
  const COREO = {};
  NOMES.forEach((nome, i) => {
    const q = P[nome];
    const lado = q.n[0] - 527; // distância ao centro do grupo
    const dir = sinal(lado);
    const atraso = 0.08 + 0.42 * r01(i, 1);
    const dx0 = lado * 0.095 + (r01(i, 2) - 0.5) * 14;
    const dy0 = q.fila === 'F' ? -24 : q.fila === 'B' ? -5 : 3;
    const conversa = q.olha[0][1];
    const ap = -dir * (1.2 + 1.7 * Math.min(1, Math.abs(lado) / 420)); // "aperta": inclina para o centro
    const alt = i % 2 ? 1 : -1;
    const gotaF = q.fila === 'F' ? { F1: 5.0, F2: 5.125, F3: 5.25 }[nome] : 0;
    COREO[nome] = {
      x: [[0, dx0], [0.15 + atraso, dx0], [2.35 + atraso * 0.6, dx0 * 0.3], [3.9, dx0 * 0.24], [4.55, dx0 * 0.2], [5.2, -lado * 0.02], [6.15, -lado * 0.024], [6.6, lado * 0.008], [7.35, 0]],
      y: q.fila === 'F'
        ? [[0, dy0], [2.35, dy0 + 4], [gotaF - 0.06, dy0 + 2], [gotaF + 0.14, 4], [gotaF + 0.32, 0]]
        : [[0, dy0], [2.4 + atraso * 0.5, 0]],
      sy: q.fila === 'F'
        ? [[0, 1.025], [gotaF - 0.02, 1.025], [gotaF + 0.13, 0.962], [gotaF + 0.38, 1.0]]
        : [[0, 1], [1, 1]],
      r: [[0, 0], [0.6, 1.4 * conversa], [3.9, 1.1 * conversa], [4.6, 0], [5.45, ap * 0.35], [5.75, ap], [6.15, ap * 0.8], [6.45, -ap * 0.35], [6.95, -ap * 0.3], [7.4, 0]],
      // cabeça: yaw (+ vira para a direita), roll (+ inclina para a direita), pitch (- queixo para cima)
      yaw: (() => {
        const ch = [[0, 0]];
        q.olha.forEach(([t0, d], j) => { ch.push([t0, j ? q.olha[j - 1][1] * 22 : 0]); ch.push([t0 + 0.35, d * 22]); });
        const ripple = 3.85 + 0.035 * Math.abs(lado) / 40; // a chamada: viram para a câmera, do centro para fora
        ch.push([ripple, ch[ch.length - 1][1]], [ripple + 0.4, 0], [5.45, 0], [5.75, -dir * 12], [6.15, -dir * 10], [6.35, alt * 4], [6.6, alt * 9], [6.95, alt * 8], [7.3, 0]);
        return limpar(ch);
      })(),
      roll: (() => {
        const ch = [[0, 0]];
        q.olha.forEach(([t0, d, v], j) => { ch.push([t0, j ? q.olha[j - 1][1] * 6 : 0]); ch.push([t0 + 0.35, d * 6 + v * 4]); });
        const ripple = 3.85 + 0.035 * Math.abs(lado) / 40;
        ch.push([ripple, ch[ch.length - 1][1]], [ripple + 0.4, 0], [5.45, 0], [5.75, -dir * 9 - 3], [6.15, -dir * 7 - 2], [6.35, alt * 2], [6.6, alt * 7], [6.95, alt * 6], [7.32, 0]);
        return limpar(ch);
      })(),
      pitch: [[0, 0], [6.3, 0], [6.6, -7], [6.95, -6], [7.3, 0]],
      risos: q.risos,
      fase: r01(i, 3) * 6.28,
      fase2: r01(i, 4) * 6.28,
      passo: r01(i, 5),
    };
    if (q.olha[0][2]) COREO[nome].pitch = [[0, 0], [q.olha[0][0], 0], [q.olha[0][0] + 0.35, q.olha[0][2] * 5], [3.85, q.olha[0][2] * 5], [4.3, 0], [6.3, 0], [6.6, -7], [6.95, -6], [7.3, 0]];
  });

  /* Estado de uma pessoa no tempo do filme (congela no flash: a foto é tirada ali). */
  function estado(nome, t) {
    const c = COREO[nome];
    t = Math.min(t, T_FLASH);
    let x = trilha(c.x, t), y = trilha(c.y, t), r = trilha(c.r, t), sy = trilha(c.sy, t);
    let yaw = trilha(c.yaw, t), roll = trilha(c.roll, t), pitch = trilha(c.pitch, t), hy = 0;
    // andando: quica a cada passo e balança um fio, proporcional à velocidade
    const vel = Math.abs(trilha(c.x, t + 0.04) - trilha(c.x, t - 0.04)) / 0.08 + Math.abs(trilha(c.y, t + 0.04) - trilha(c.y, t - 0.04)) / 0.08 * (P[nome].fila === 'F' ? 0 : 1);
    const W = Math.min(1, vel / 55);
    const fp = 2.1 + 0.3 * c.passo;
    y -= 5 * W * (1 - Math.cos(2 * Math.PI * fp * t + c.fase)) / 2;
    r += 0.9 * W * Math.sin(Math.PI * fp * t + c.fase);
    // risada: ombros sacodem, a cabeça vai para trás, o corpo recua um fio
    for (const [t0, d] of c.risos) {
      const u = (t - t0) / d;
      if (u <= 0 || u >= 1) continue;
      const env = Math.pow(Math.sin(Math.PI * u), 1.3);
      y -= 3.2 * env * (1 - Math.cos(2 * Math.PI * 4.6 * (t - t0))) / 2;
      pitch -= 11 * env;
      hy -= 4 * env;
      roll += 3 * env * Math.sin(2 * Math.PI * 2.3 * (t - t0));
      r += -0.9 * env * sinal(P[nome].n[0] - 527 || 1);
    }
    // respiração e balanço leves (a vida no hold), até o clique
    sy *= 1 + 0.0042 * Math.sin((2 * Math.PI * t) / 3.1 + c.fase);
    r += 0.32 * Math.sin((2 * Math.PI * t) / 4.7 + c.fase2);
    roll += 0.6 * Math.sin((2 * Math.PI * t) / 3.7 + c.fase2);
    return { x, y, r, sy, yaw, roll, pitch, hy };
  }

  /* Câmera: nasce perto, nos rostos, e abre até a foto inteira no clique. */
  function camera(t) {
    if (t < T_FLASH) {
      const zoom = trilha([[0, 1.3], [2.6, 1.14], [4.5, 1.07], [6.6, 1.025], [T_FLASH, 1.0]], t);
      const fy = trilha([[0, 690], [3.0, 715], [5.5, 738], [T_FLASH, 745.5]], t);
      const fx = 527.5 + 8 * Math.sin((2 * Math.PI * t) / 6.5) * Math.min(1, (T_FLASH - t) / 2);
      return { zoom, fx, fy };
    }
    // a foto: push-in vivo, passando por 1,0 quando as estrelas assentam
    return { zoom: 1 + 0.0042 * (t - 10.9), fx: 527.5, fy: 745.5 };
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
      <div class="revela-cinza"></div>
      <div class="revela-branco"></div>
      <div class="brilho-foto"></div>
      <div class="flash"></div>`;
  }

  function montar(el, api) {
    el.palco = el.$('.palco');
    el.camadas = {};
    el.$$('.pessoa').forEach((im) => (el.camadas[im.dataset.id] = im));
    el.moldura = el.$('.moldura');
    el.estrelas = el.$$('.estrela').map((im, i) => ({ el: im, i, cx: ESTRELAS[i][5], cy: ESTRELAS[i][6] }));
    el.brilho = el.$('.brilho-foto');
    el.flash = el.$('.flash');
    el.cinza = el.$('.revela-cinza');
    el.branco = el.$('.revela-branco');
    el.k = api.largura / PW;
  }

  /* Aplica o filme inteiro no tempo global t. */
  function aplicar(t, el, api) {
    const { clamp, prog, ease, lerp } = api;
    // pessoas
    for (const nome of NOMES) {
      const q = P[nome], s = estado(nome, t);
      const px = PX(q.p[0]), py = PY(q.p[1]), nx = PX(q.n[0]), ny = PY(q.n[1]);
      const corpo = `translate(${f(s.x * Z)}px, ${f(s.y * Z)}px) translate(${f(px)}px, ${f(py)}px) rotate(${f(s.r)}deg) scale(1, ${f(s.sy)}) translate(${f(-px)}px, ${f(-py)}px)`;
      const cabeca = `${corpo} translate(${f(nx)}px, ${f(ny + s.hy * Z)}px) perspective(1400px) rotateY(${f(s.yaw)}deg) rotateX(${f(-s.pitch)}deg) rotate(${f(s.roll)}deg) translate(${f(-nx)}px, ${f(-ny)}px)`;
      api.set(el.camadas[`${nome}b`], { pre: corpo });
      api.set(el.camadas[`${nome}h`], { pre: cabeca });
      for (const e of q.extra || []) api.set(el.camadas[e], { pre: corpo });
    }
    // câmera
    const cam = camera(t), k = el.k * cam.zoom;
    const tx = api.largura / 2 - PX(cam.fx) * k, ty = api.altura / 2 - PY(cam.fy) * k;
    // o flash: estoura em 3 quadros e apaga; a foto nasce clara e revela a cor
    const tf = t - T_FLASH;
    const fl = tf < 0 ? 0 : tf < 0.05 ? ease.outCubic(tf / 0.05) : Math.exp(-(tf - 0.05) / 0.16);
    const rev = tf < 0 ? 0 : 1 - ease.outCubic(clamp((tf - 0.02) / 0.95));
    api.set(el.palco, { pre: `translate(${f(tx)}px, ${f(ty)}px) scale(${Math.round(k * 1e6) / 1e6})` });
    api.set(el.flash, { o: 0.96 * fl });
    api.set(el.branco, { o: 0.42 * rev });
    api.set(el.cinza, { o: 0.45 * rev });
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
      const rot = (u <= 0 ? -70 : -70 * Math.exp(-6 * u) * Math.cos(2 * Math.PI * 0.9 * u)) + vivo * 7 * Math.sin((2 * Math.PI * (t - t0)) / (3.3 + 0.37 * (s.i % 4)) + s.i);
      const pul = 1 + vivo * 0.03 * Math.sin((2 * Math.PI * (t - t0)) / (2.1 + 0.29 * (s.i % 3)) + s.i * 1.7);
      api.set(s.el, {
        pre: `translate(${PX(0) + s.cx}px, ${s.cy}px) rotate(${f(rot)}deg) scale(${f(sc * pul)}) translate(${-s.cx}px, ${-s.cy}px)`,
        o: ab,
      });
    }
    // um brilho de papel fotográfico atravessa a foto uma vez
    const pb = prog(t, T_FLASH + 1.7, T_FLASH + 2.6);
    api.set(el.brilho, { x: lerp(-110, 110, ease.inOutSine(pb)), o: Math.sin(Math.PI * pb) * 0.8 });
  }

  window.Turma = { render, montar, aplicar, estado, camera, T_FLASH, P, COREO };
})();
