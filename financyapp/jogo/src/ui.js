// A camada de HTML por cima do canvas: balões que seguem o sprite, botões
// de escolha, o quadro da reunião e os outros painéis, a legenda e o botão
// de pular. O texto nunca vai pré-renderizado nos quadros (§6): é HTML,
// legível, com foco de teclado e espelhado numa região aria-live.

import { nomeDe, ORIGEM, ehProvisoria } from './roteiro.js';

export function criarUI({ palco, sala, escala, elenco, opcoes }) {
  const camada = document.createElement('div');
  camada.className = 'camada';
  palco.append(camada);
  const vivo = document.getElementById('falas-sr');
  const legendaEl = document.createElement('p');
  legendaEl.className = 'legenda';
  legendaEl.hidden = true;
  palco.append(legendaEl);
  const pular = document.createElement('button');
  pular.type = 'button';
  pular.className = 'pular';
  pular.textContent = 'Pular cena (Esc)';
  pular.hidden = true;
  palco.append(pular);

  const baloes = new Map();     // ator -> { el }
  let aguardando = null;        // { resolve } do balão que espera toque
  let aoPular = null;

  function anunciar(texto) {
    if (vivo) vivo.textContent = texto;
  }

  function posicionar(el, atorId) {
    const a = elenco.get(atorId);
    if (!a) return;
    const [x, y] = sala.cabeca(a);
    const k = escala();
    const largura = palco.clientWidth;
    let left = x * k;
    const meia = el.offsetWidth / 2;
    left = Math.max(meia + 4 + palco.scrollLeft, Math.min(left, palco.scrollLeft + largura - meia - 4));
    el.style.left = `${left}px`;
    el.style.top = `${Math.max(el.offsetHeight + 6, y * k - 4)}px`;
  }

  function fecharBalao(atorId) {
    const b = baloes.get(atorId);
    if (!b) return;
    b.el.remove();
    baloes.delete(atorId);
  }

  function montarBalao(atorId, texto, origem) {
    fecharBalao(atorId);
    const el = document.createElement('div');
    el.className = 'balao';
    const quem = document.createElement('span');
    quem.className = 'quem';
    quem.textContent = nomeDe(atorId);
    const p = document.createElement('p');
    p.className = 'fala';
    p.textContent = texto;
    el.append(quem, p);
    if (origem && ehProvisoria(origem) && opcoes.marcarProvisorias) {
      const o = document.createElement('span');
      o.className = 'origem';
      o.textContent = ORIGEM[origem] ?? origem;
      el.append(o);
      el.classList.add('provisoria');
    }
    camada.append(el);
    baloes.set(atorId, { el });
    posicionar(el, atorId);
    anunciar(`${nomeDe(atorId)}: ${texto}`);
    return el;
  }

  /** Mostra a fala e espera o toque (ou o tempo, nas ambientais). */
  function falar(atorId, texto, { origem, ambiente = false, pulando = false } = {}) {
    if (pulando) return Promise.resolve();
    const el = montarBalao(atorId, texto, origem);
    const seguir = document.createElement('span');
    seguir.className = 'seguir';
    seguir.setAttribute('aria-hidden', 'true');
    seguir.textContent = '▸';
    el.append(seguir);
    return new Promise((resolve) => {
      let timer = null;
      const fim = () => {
        clearTimeout(timer);
        if (aguardando?.resolve === fim) aguardando = null;
        fecharBalao(atorId);
        resolve();
      };
      if (ambiente) timer = setTimeout(fim, 2600 + texto.length * 55);
      aguardando = { resolve: fim };
    });
  }

  /** Balão com botões: devolve o id escolhido. */
  const pendentes = new Set();   // promessas abertas (escolha, painel), resolvidas ao limpar
  function escolher(atorId, texto, choices, { origem } = {}) {
    const el = montarBalao(atorId, texto, origem);
    el.classList.add('com-escolhas');
    const grupo = document.createElement('div');
    grupo.className = 'escolhas';
    grupo.setAttribute('role', 'group');
    grupo.setAttribute('aria-label', 'Escolha');
    return new Promise((resolve0) => {
      const resolve = (v) => { pendentes.delete(resolve); resolve0(v); };
      pendentes.add(resolve);
      for (const ch of choices) {
        const b = document.createElement('button');
        b.type = 'button';
        b.textContent = ch.texto;
        if (ch.origem && ehProvisoria(ch.origem) && opcoes.marcarProvisorias) {
          b.classList.add('provisoria');
          b.title = ORIGEM[ch.origem] ?? ch.origem;
        }
        b.addEventListener('click', (ev) => {
          ev.stopPropagation();
          fecharBalao(atorId);
          anunciar(`Escolhido: ${ch.texto}`);
          resolve(ch.id);
        });
        grupo.append(b);
      }
      el.append(grupo);
      posicionar(el, atorId);
      grupo.querySelector('button')?.focus({ preventScroll: true });
    });
  }

  /** Avança o balão que espera toque. Devolve true se havia um. */
  function avancar() {
    if (!aguardando) return false;
    aguardando.resolve();
    return true;
  }

  function legenda(texto, ms = 5000) {
    legendaEl.textContent = texto;
    legendaEl.hidden = false;
    anunciar(texto);
    clearTimeout(legenda.t);
    legenda.t = setTimeout(() => { legendaEl.hidden = true; }, ms);
  }

  /**
   * Abre um painel por cima da sala. "montar(corpo, fechar)" preenche o
   * conteúdo e chama fechar(valor) para terminar. Devolve o valor.
   */
  function painel({ titulo, sintetico = true, montar, rotuloFechar = 'Continuar' }) {
    return new Promise((resolve0) => {
      const resolve = (v) => { pendentes.delete(resolve); resolve0(v); };
      pendentes.add(resolve);
      const fundo = document.createElement('div');
      fundo.className = 'painel-fundo';
      const caixa = document.createElement('section');
      caixa.className = 'painel';
      caixa.setAttribute('role', 'dialog');
      caixa.setAttribute('aria-modal', 'true');
      const h = document.createElement('h3');
      h.id = `painel-${Date.now()}`;
      h.textContent = titulo;
      caixa.setAttribute('aria-labelledby', h.id);
      const topo = document.createElement('header');
      topo.append(h);
      if (sintetico) {
        const s = document.createElement('span');
        s.className = 'selo-sintetico';
        s.textContent = 'dados sintéticos';
        topo.append(s);
      }
      const corpo = document.createElement('div');
      corpo.className = 'corpo';
      caixa.append(topo, corpo);
      fundo.append(caixa);
      palco.append(fundo);
      const anterior = document.activeElement;
      const fechar = (valor) => {
        fundo.remove();
        anterior?.focus?.({ preventScroll: true });
        resolve(valor);
      };
      const rodape = montar(corpo, fechar);
      if (rodape !== false) {
        const pe = document.createElement('footer');
        const b = document.createElement('button');
        b.type = 'button';
        b.className = 'primario';
        b.textContent = rotuloFechar;
        b.addEventListener('click', () => fechar(undefined));
        pe.append(b);
        caixa.append(pe);
      }
      caixa.addEventListener('keydown', (ev) => { if (ev.key === 'Escape' && rodape !== false) fechar(undefined); });
      (caixa.querySelector('input, select, button.primario, button') ?? caixa).focus({ preventScroll: true });
    });
  }

  function mostrarPular(pode, acao) {
    pular.hidden = !pode;
    aoPular = pode ? acao : null;
  }
  pular.addEventListener('click', (ev) => { ev.stopPropagation(); aoPular?.(); });

  function atualizar() {
    for (const [id, b] of baloes) posicionar(b.el, id);
  }

  function limpar() {
    for (const id of [...baloes.keys()]) fecharBalao(id);
    aguardando?.resolve();
    aguardando = null;
    palco.querySelectorAll('.painel-fundo').forEach((e) => e.remove());
    for (const r of [...pendentes]) r(undefined);
  }

  return {
    falar, escolher, avancar, legenda, painel, mostrarPular, atualizar, anunciar, limpar,
    get esperandoToque() { return Boolean(aguardando); },
    get pularAtivo() { return Boolean(aoPular); },
    pularAgora() { aoPular?.(); },
  };
}
