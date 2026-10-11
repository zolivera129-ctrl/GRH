/*
 * GRH Experience · bloco animado de "Símbolos dos eventos"
 *
 * Roteiro (em loop):
 *   1. O símbolo original gira devagar no sentido horário.
 *   2. Ele dá um giro de 360° e vira uma bola de tênis.
 *   3. A bola quica rápido: amassa um pouco ao tocar o chão e sobe.
 *   4. Enquanto sobe, a bola gira 360° e volta a ser o símbolo.
 *   5. O símbolo segue girando na mesma velocidade da bola.
 *   6. O símbolo vira um volante, que vira devagar para a direita e depois
 *      para a esquerda, como numa curva.
 *   7. O volante volta para a direita muito rápido, até virar um borrão.
 *   8. Do borrão até parar, ele volta a ser o símbolo, que segue girando
 *      devagar no sentido horário (e a cena 1 recomeça).
 *
 * Marcação: <button class="gb gb-experience"> com o <svg class="gb-exp"> do index.html.
 * Como os outros blocos, o gesto roda com o mouse em cima, com o foco do
 * teclado ou com um toque. Com data-autoplay no botão, roda sempre.
 * Respeita "Pausar movimento" (.grh-paused) e prefers-reduced-motion.
 */
(function () {
  'use strict';

  // ---- Geometria (viewBox 0 0 120 120, centro 60,60) -----------------------

  // Símbolo original: 4 lados côncavos em cúbicas + pontas arredondadas pelo
  // traço (stroke-linejoin round, raio RHO). Medido no arquivo original.
  var RHO = 3.41;
  var KAPPA = 0.5522847498;
  var BALL_R = 36;   // raio da bola
  var WHEEL_R = 46;  // raio do volante

  function starPts(a, u, v) {
    var w = a - u;
    return [0, -a, v, -w, w, -v, a, 0, w, v, v, w, 0, a, -v, w, -w, v, -a, 0, -w, -v, -v, -w, 0, -a];
  }
  function circlePts(r) {
    var k = KAPPA * r;
    return [0, -r, k, -r, r, -k, r, 0, r, k, k, r, 0, r, -k, r, -r, k, -r, 0, -r, -k, -k, -r, 0, -r];
  }
  var P_STAR = starPts(38.575, 13.439, 8.049);
  var P_BALL = circlePts(BALL_R - RHO);
  var P_WHEEL = circlePts(WHEEL_R - RHO);

  function bodyPath(mb, mw) {
    var d = '';
    for (var i = 0; i < 26; i += 2) {
      var x = 60 + P_STAR[i] + mb * (P_BALL[i] - P_STAR[i]) + mw * (P_WHEEL[i] - P_STAR[i]);
      var y = 60 + P_STAR[i + 1] + mb * (P_BALL[i + 1] - P_STAR[i + 1]) + mw * (P_WHEEL[i + 1] - P_STAR[i + 1]);
      d += (i === 0 ? 'M' : i % 6 === 2 ? 'C' : ' ') + x.toFixed(2) + ' ' + y.toFixed(2);
    }
    return d + 'Z';
  }

  // ---- Linha do tempo (segundos) --------------------------------------------

  var T = {
    s2: 0.9,      // cena 2: giro de 360° e vira bola
    s3: 1.75,     // cena 3: a bola cai
    hit: 2.02,    // toca o chão
    up: 2.12,     // cena 4: sobe girando e volta a ser o símbolo
    s5: 2.85,     // cena 5: segue girando
    s6: 3.35,     // cena 6: vira volante
    wheel: 4.1,   // volante pronto, reto
    right: 4.95,  // virou para a direita
    left: 5.85,   // virou para a esquerda (curva)
    s7: 6.1,      // cena 7: volta para a direita muito rápido
    s8: 6.85,     // cena 8: borrão, desacelera e vira o símbolo
    end: 8.3
  };
  var SCENES = [0, T.s2, T.s3, T.up, T.s5, T.s6, T.s7, T.s8];

  var W_SLOW = 40;    // °/s, giro leve das cenas 1 e 8
  var W_BALL = 710;   // °/s, giro da bola que o símbolo mantém na cena 5
  var W_MAX = 1440;   // °/s, pico do borrão

  // Rotação: trechos de Hermite com velocidade contínua [t, ângulo, °/s].
  var KEYS = (function () {
    var k = [[0, 0, W_SLOW], [T.s2, W_SLOW * T.s2, W_SLOW]];
    var a = k[1][1] + 360;
    k.push([T.s3, a, 90]);
    a += 25; k.push([T.up, a, 60]);
    a += 360; k.push([T.s5, a, W_BALL]);
    a += W_BALL * (T.s6 - T.s5); k.push([T.s6, a, W_BALL]);
    a += W_BALL * (T.wheel - T.s6) / 3; k.push([T.wheel, a, 0]);   // freia até o volante ficar reto
    var up = a;
    k.push([T.right - 0.08, up + 40, 0], [T.right, up + 40, 0]);
    k.push([T.left, up - 95, 0], [T.s7, up - 100, 0]);
    a = up - 100 + W_MAX * (T.s8 - T.s7) / 3; k.push([T.s8, a, W_MAX]); // acelera do zero
    // Platô no pico: duração escolhida para o loop fechar num múltiplo de 90°
    // (o símbolo tem simetria de 90°, então a volta para a cena 1 não tem salto).
    var q = W_SLOW + (W_MAX - W_SLOW) / 3;
    var base = a + (T.end - T.s8) * q;
    var p = 0.2, gain = W_MAX - q;
    var rest = ((base + p * gain) % 90 + 90) % 90;
    p += (90 - rest) % 90 / gain;
    a += W_MAX * p; k.push([T.s8 + p, a, W_MAX]);
    a += (T.end - T.s8 - p) * q; k.push([T.end, Math.round(a / 90) * 90, W_SLOW]);
    return { list: k, wheelUp: up };
  })();

  function rotation(t) {
    var k = KEYS.list;
    for (var i = 1; i < k.length; i++) {
      if (t <= k[i][0] || i === k.length - 1) {
        var a = k[i - 1], b = k[i], dt = b[0] - a[0];
        var s = Math.min(Math.max((t - a[0]) / dt, 0), 1), s2 = s * s, s3 = s2 * s;
        var th = (2 * s3 - 3 * s2 + 1) * a[1] + (s3 - 2 * s2 + s) * dt * a[2] + (-2 * s3 + 3 * s2) * b[1] + (s3 - s2) * dt * b[2];
        var w = ((6 * s2 - 6 * s) * a[1] + (3 * s2 - 4 * s + 1) * dt * a[2] + (-6 * s2 + 6 * s) * b[1] + (3 * s2 - 2 * s) * dt * b[2]) / dt;
        return [th, w];
      }
    }
    return [0, W_SLOW];
  }

  function clamp01(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }
  function seg(t, a, b) { return clamp01((t - a) / (b - a)); }
  function smooth(x) { return x * x * (3 - 2 * x); }
  function inOut(x) { return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }
  function outCubic(x) { return 1 - Math.pow(1 - x, 3); }
  function outBack(x) { var y = x - 1; return 1 + 1.8 * y * y * y + 0.8 * y * y; }

  // Quique: queda com gravidade, contato, subida balística e assentamento.
  var DROP = 16;
  var G = 2 * DROP / Math.pow(T.hit - T.s3, 2);
  var APEX = -6;
  var V_UP = Math.sqrt(2 * G * (DROP - APEX));
  var T_APEX = V_UP / G;
  var SETTLE = 0.5;
  var GROUND = 60 + DROP + BALL_R;

  function posY(t) {
    if (t < T.s3) return 0;
    if (t < T.hit) { var u = (t - T.s3) / (T.hit - T.s3); return DROP * u * u; }
    if (t < T.up) return DROP;
    var tu = t - T.up;
    if (tu < T_APEX) return DROP - V_UP * tu + 0.5 * G * tu * tu;
    return APEX * (1 - smooth(seg(tu, T_APEX, T_APEX + SETTLE)));
  }

  // > 0 amassa (achata contra o chão), < 0 estica no ar.
  function squash(t) {
    if (t > T.s3 && t < T.hit) return -0.05 * Math.pow(seg(t, T.s3 + 0.1, T.hit), 2);
    if (t >= T.hit && t <= T.up) { var u = seg(t, T.hit, T.up); return 0.14 * Math.sin(Math.PI * u) - 0.05 * (1 - u) * (1 - u); }
    if (t > T.up && t < T.up + 0.2) return -0.06 * Math.sin(Math.PI * seg(t, T.up, T.up + 0.2));
    return 0;
  }

  function sample(t) {
    var r = rotation(t);
    var mb = t < T.s3 ? inOut(seg(t, T.s2 + 0.1, T.s3 - 0.02)) : 1 - inOut(seg(t, T.up + 0.1, T.s5 - 0.05));
    return {
      th: r[0],
      w: r[1],
      mb: mb,
      mw: inOut(seg(t, T.s6, T.s6 + 0.45)) * (1 - inOut(seg(t, T.s8 + 0.02, T.s8 + 0.4))),
      se: smooth(seg(t, T.s3 - 0.4, T.s3 - 0.02)) * (1 - smooth(seg(t, T.up + 0.02, T.up + 0.3))),
      ho: (t < T.s8 ? outBack(seg(t, T.s6 + 0.25, T.wheel)) : 1) * (1 - inOut(seg(t, T.s8, T.s8 + 0.32))),
      y: posY(t),
      sq: squash(t),
      sh: smooth(seg(t, T.s3 - 0.3, T.s3)) * (1 - smooth(seg(t, T.up + 0.1, T.up + 0.45)))
    };
  }
  var SEAMS_ROT = -rotation(T.hit)[0];   // costuras na vertical quando a bola toca o chão
  var HOLES_ROT = -KEYS.wheelUp;         // volante reto no fim da cena 6
  var REST = { th: 0, w: 0, mb: 0, mw: 0, se: 0, ho: 0, y: 0, sq: 0, sh: 0 };

  function mix(a, b, e) {
    var o = {};
    for (var key in REST) o[key] = a[key] + (b[key] - a[key]) * e;
    return o;
  }

  // ---- Borrão de rotação ------------------------------------------------------
  // Girando muito rápido, a forma vira a sua média em volta do centro, que só
  // depende da distância ao centro. Essa média é medida uma vez (cobertura por
  // raio) e desenhada como um disco com gradiente radial por cima da forma
  // nítida, com opacidade crescendo com a velocidade.

  var PR = 50;            // raio do disco do borrão
  var RES = 2;            // amostras por unidade de raio
  var NB = PR * RES;      // última amostra (raio PR)
  var BODY_STEPS = 10;    // perfis do corpo para mw = 0; 0,1 ... 1
  var profiles = null;

  function blurAmount(w) {
    return smooth(clamp01((Math.abs(w) - 800) / 600));
  }

  function radialProfile(draw) {
    var S = 3, size = 2 * PR * S;
    var cv = document.createElement('canvas');
    cv.width = cv.height = size;
    var ctx = cv.getContext && cv.getContext('2d', { willReadFrequently: true });
    if (!ctx) return null;
    ctx.setTransform(S, 0, 0, S, size / 2 - 60 * S, size / 2 - 60 * S);
    draw(ctx);
    var px = ctx.getImageData(0, 0, size, size).data;
    var sum = new Float64Array(NB + 1), cnt = new Float64Array(NB + 1);
    for (var y = 0; y < size; y++) {
      for (var x = 0; x < size; x++) {
        var dx = x + 0.5 - size / 2, dy = y + 0.5 - size / 2;
        var i = Math.round(Math.sqrt(dx * dx + dy * dy) / S * RES);
        if (i > NB) continue;
        sum[i] += px[(y * size + x) * 4 + 3] / 255;
        cnt[i]++;
      }
    }
    var out = [];
    for (var k = 0; k <= NB; k++) out.push(cnt[k] ? sum[k] / cnt[k] : 0);
    return out;
  }

  function buildProfiles(card) {
    if (profiles !== null) return;
    profiles = false;
    if (typeof Path2D !== 'function') return;
    var bodyW = parseFloat(card.body.getAttribute('stroke-width')) || 2 * RHO;
    var holes = Array.prototype.map.call(card.holes.querySelectorAll('path'), function (p) {
      return { path: new Path2D(p.getAttribute('d')), w: parseFloat(p.getAttribute('stroke-width')) || 0 };
    });
    var fillStroke = function (ctx, path, w) {
      ctx.fill(path);
      if (w > 0) { ctx.lineWidth = w; ctx.lineJoin = 'round'; ctx.stroke(path); }
    };
    var body = [];
    for (var i = 0; i <= BODY_STEPS; i++) {
      var shape = new Path2D(bodyPath(0, i / BODY_STEPS));
      var prof = radialProfile(function (ctx) { fillStroke(ctx, shape, bodyW); });
      if (!prof) return;
      body.push(prof);
    }
    var hole = radialProfile(function (ctx) { holes.forEach(function (h) { fillStroke(ctx, h.path, h.w); }); });
    if (hole) profiles = { body: body, holes: hole };
  }

  // Cobertura média por raio (amostras 0..NB) para o corpo mw com as janelas na escala ho.
  function blurProfile(mw, ho) {
    var f = clamp01(mw) * BODY_STEPS, i0 = Math.floor(f), i1 = Math.min(BODY_STEPS, i0 + 1), u = f - i0;
    var A = profiles.body[i0], B = profiles.body[i1], H = profiles.holes, out = [];
    for (var k = 0; k <= NB; k++) {
      var c = A[k] + (B[k] - A[k]) * u;
      if (ho > 0.001) {
        var rr = k / ho;
        if (rr < NB) { var j = Math.floor(rr), v = rr - j; c -= H[j] + (H[j + 1] - H[j]) * v; }
      }
      out.push(c < 0 ? 0 : c > 1 ? 1 : c);
    }
    return out;
  }

  function rgb(str) {
    var m = /^#([0-9a-f]{6})$/i.exec(str.trim());
    if (m) { var n = parseInt(m[1], 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
    m = /rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)/.exec(str);
    return m ? [+m[1], +m[2], +m[3]] : [0, 0, 0];
  }

  // ---- Um bloco --------------------------------------------------------------

  var SVG_NS = 'http://www.w3.org/2000/svg';
  var reduce = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  var cards = [];
  var uid = 0;

  function Card(btn) {
    var svg = btn.querySelector('svg.gb-exp');
    this.btn = btn;
    this.pos = svg.querySelector('.gb-exp-pos');
    this.squashEl = svg.querySelector('.gb-exp-squash');
    this.sym = svg.querySelector('.gb-exp-sym');
    this.body = svg.querySelector('.gb-exp-body');
    this.seams = svg.querySelector('.gb-exp-seams');
    this.seamPaths = svg.querySelectorAll('.gb-exp-seams path');
    this.holes = svg.querySelector('.gb-exp-holes');
    this.shadow = svg.querySelector('.gb-exp-shadow');

    // Disco do borrão (gradiente radial com um stop a cada meia unidade de raio).
    var id = 'gbExpBlur' + (++uid);
    var defs = document.createElementNS(SVG_NS, 'defs');
    var grad = document.createElementNS(SVG_NS, 'radialGradient');
    grad.setAttribute('id', id);
    grad.setAttribute('gradientUnits', 'userSpaceOnUse');
    grad.setAttribute('cx', '60'); grad.setAttribute('cy', '60'); grad.setAttribute('r', String(PR));
    this.stops = [];
    for (var k = 0; k <= NB; k++) {
      var st = document.createElementNS(SVG_NS, 'stop');
      st.setAttribute('offset', (k / NB).toFixed(4));
      grad.appendChild(st);
      this.stops.push(st);
    }
    defs.appendChild(grad);
    svg.insertBefore(defs, svg.firstChild);
    this.blurDisc = document.createElementNS(SVG_NS, 'circle');
    this.blurDisc.setAttribute('class', 'gb-exp-blur');
    this.blurDisc.setAttribute('cx', '60'); this.blurDisc.setAttribute('cy', '60'); this.blurDisc.setAttribute('r', String(PR));
    this.blurDisc.setAttribute('fill', 'url(#' + id + ')');
    this.blurDisc.setAttribute('display', 'none');
    this.pos.appendChild(this.blurDisc);
    this.fg = rgb(getComputedStyle(svg).color);
    this.bg = rgb(this.holes.getAttribute('fill') || '#8F74B1');

    this.last = {};
    this.t = 0;
    this.mode = 'rest';
    this.want = { hover: false, key: false, touch: false, auto: btn.hasAttribute('data-autoplay') };
    this.state = REST;
    this.base = 0;
    this.speed = 1;
    this.bind();
    this.render(REST);
  }

  Card.prototype.bind = function () {
    var self = this, btn = this.btn;
    var isMouse = function (e) { return e.pointerType === 'mouse' || e.pointerType === 'pen'; };
    btn.addEventListener('pointerenter', function (e) { if (isMouse(e)) self.set('hover', true); });
    btn.addEventListener('pointerleave', function (e) { if (isMouse(e)) self.set('hover', false); });
    btn.addEventListener('pointerup', function (e) { if (e.pointerType === 'touch') self.set('touch', !self.want.touch); });
    document.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'touch' && !btn.contains(e.target)) self.set('touch', false);
    });
    btn.addEventListener('focus', function () {
      var visible = true;
      try { visible = btn.matches(':focus-visible'); } catch (err) { /* navegador antigo */ }
      if (visible) self.set('key', true);
    });
    btn.addEventListener('blur', function () { self.set('key', false); });
  };

  Card.prototype.set = function (key, on) {
    this.want[key] = on;
    this.update();
  };

  Card.prototype.active = function () {
    var w = this.want;
    return !reduce.matches && (w.hover || w.key || w.touch || w.auto);
  };

  Card.prototype.update = function () {
    if (this.active()) {
      if (this.mode === 'play') return;
      // Começa na cena 1. Se ainda estava parando, faz a ponte a partir de onde está.
      this.from = this.mode === 'rest' ? null : this.state;
      this.base = Math.ceil((this.state.th - 0.5) / 90) * 90;
      this.t = 0;
      this.blend = 0;
      this.mode = 'play';
    } else {
      if (this.mode !== 'play') return;
      // Para com suavidade: volta a ser o símbolo e assenta no próximo ângulo de 90°.
      this.from = this.state;
      this.target = Math.ceil(this.state.th / 90) * 90;
      this.blend = 0;
      this.mode = 'settle';
    }
    wake();
  };

  Card.prototype.paused = function () {
    return !!this.btn.closest('.grh-paused');
  };

  // Avança dt segundos. Devolve true se ainda precisa de quadros.
  Card.prototype.step = function (dt) {
    if (this.mode === 'rest') return false;
    if (reduce.matches) {
      this.mode = 'rest';
      this.render(REST);
      return false;
    }
    if (this.paused() || this.frozen) return true;
    dt *= this.speed;
    if (this.mode === 'play') {
      this.t += dt;
      if (this.t >= T.end) { // nova volta do loop: o ângulo segue de onde parou
        this.t -= T.end;
        this.base += KEYS.list[KEYS.list.length - 1][1];
      }
      var s = sample(this.t);
      s.th += this.base;
      if (this.from) {
        this.blend = Math.min(1, this.blend + dt / 0.3);
        s = mix(this.from, s, inOut(this.blend));
        if (this.blend >= 1) this.from = null;
      }
      this.render(s);
      return true;
    }
    // settle
    this.blend = Math.min(1, this.blend + dt / 0.6);
    var e = this.blend;
    var st = mix(this.from, Object.assign({}, REST, { th: this.target }), inOut(e));
    st.th = this.from.th + (this.target - this.from.th) * outCubic(e);
    st.w = this.from.w * (1 - outCubic(e));
    this.render(st);
    if (e >= 1) {
      this.mode = 'rest';
      this.render(Object.assign({}, REST, { th: this.target }));
      return false;
    }
    return true;
  };

  // Mostra o quadro do instante t do loop (usado pela prévia).
  Card.prototype.seek = function (t) {
    this.t = ((t % T.end) + T.end) % T.end;
    this.base = 0;
    this.from = null;
    this.render(sample(this.t));
  };

  Card.prototype.attr = function (el, key, name, value) {
    if (this.last[key] === value) return;
    this.last[key] = value;
    el.setAttribute(name, value);
  };

  Card.prototype.render = function (s) {
    this.state = s;
    var seamsOn = s.se > 0.01, holesOn = s.ho > 0.001;
    this.attr(this.sym, 'rot', 'transform', 'rotate(' + s.th.toFixed(3) + ' 60 60)');
    this.attr(this.body, 'd', 'd', bodyPath(clamp01(s.mb), clamp01(s.mw)));
    this.attr(this.seams, 'seams', 'display', seamsOn ? 'inline' : 'none');
    if (seamsOn) {
      var dash = (1 - clamp01(s.se)).toFixed(3);
      this.attr(this.seams, 'seamsRot', 'transform', 'rotate(' + SEAMS_ROT.toFixed(2) + ' 60 60)');
      this.attr(this.seamPaths[0], 'dash0', 'stroke-dashoffset', dash);
      this.attr(this.seamPaths[1], 'dash1', 'stroke-dashoffset', dash);
    }
    this.attr(this.holes, 'holes', 'display', holesOn ? 'inline' : 'none');
    if (holesOn) {
      this.attr(this.holes, 'holesT', 'transform', 'rotate(' + HOLES_ROT.toFixed(2) + ' 60 60) translate(60 60) scale(' + s.ho.toFixed(4) + ') translate(-60 -60)');
    }

    var sx = 1 + 0.9 * s.sq, sy = 1 - s.sq;
    this.attr(this.pos, 'pos', 'transform', 'translate(0 ' + s.y.toFixed(3) + ')');
    this.attr(this.squashEl, 'sq', 'transform', 'translate(60 96) scale(' + sx.toFixed(4) + ' ' + sy.toFixed(4) + ') translate(-60 -96)');

    // Borrão
    var b = blurAmount(s.w);
    if (b > 0.002 && profiles === null) buildProfiles(this);
    var blurOn = b > 0.002 && !!profiles;
    this.attr(this.blurDisc, 'blur', 'display', blurOn ? 'inline' : 'none');
    if (blurOn) {
      var prof = blurProfile(s.mw, s.ho), fg = this.fg, bg = this.bg;
      for (var k = 0; k <= NB; k++) {
        var c = prof[k];
        this.attr(this.stops[k], 'stop' + k, 'stop-color', 'rgb(' +
          Math.round(bg[0] + (fg[0] - bg[0]) * c) + ',' +
          Math.round(bg[1] + (fg[1] - bg[1]) * c) + ',' +
          Math.round(bg[2] + (fg[2] - bg[2]) * c) + ')');
      }
      this.attr(this.blurDisc, 'blurOp', 'opacity', b.toFixed(3));
    }

    // Sombra no chão: cresce e escurece quando a bola chega perto.
    var h = clamp01((GROUND - (60 + s.y + BALL_R)) / 30);
    var shadowOn = s.sh * s.mb > 0.01;
    this.attr(this.shadow, 'shadow', 'display', shadowOn ? 'inline' : 'none');
    if (shadowOn) {
      this.attr(this.shadow, 'shadowOp', 'opacity', (0.22 * s.sh * clamp01(s.mb) * (1 - 0.75 * h)).toFixed(3));
      this.attr(this.shadow, 'shadowRx', 'rx', (22 * (1 - 0.45 * h) * sx).toFixed(2));
    }
  };

  // ---- Laço de quadros compartilhado ------------------------------------------

  var running = false, last = 0;
  function frame(now) {
    var dt = Math.min(0.05, Math.max(0, (now - last) / 1000));
    last = now;
    var more = false;
    for (var i = 0; i < cards.length; i++) if (cards[i].step(dt)) more = true;
    if (more) requestAnimationFrame(frame);
    else running = false;
  }
  function wake() {
    if (running) return;
    running = true;
    last = performance.now();
    requestAnimationFrame(frame);
  }

  function start() {
    var list = document.querySelectorAll('.gb-experience');
    for (var i = 0; i < list.length; i++) {
      if (list[i].gbExperience || !list[i].querySelector('svg.gb-exp')) continue;
      var card = new Card(list[i]);
      list[i].gbExperience = card;
      cards.push(card);
      card.update();
    }
    // Mede o borrão com o navegador ocioso, antes de ele ser preciso.
    if (cards.length && profiles === null) {
      var first = cards[0];
      var later = window.requestIdleCallback || function (fn) { return setTimeout(fn, 200); };
      later(function () { buildProfiles(first); });
    }
    if (reduce.addEventListener) reduce.addEventListener('change', function () { cards.forEach(function (c) { c.update(); }); wake(); });
  }

  window.GBExperience = { duration: T.end, scenes: SCENES, sample: sample, start: start };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
