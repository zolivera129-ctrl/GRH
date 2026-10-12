/*
 * Canais e Aplicações · Brandcenter Gestão RH
 *
 * O index.html já vem pronto no estado inicial. Este arquivo só atualiza os
 * trechos interativos, marcados no HTML com:
 *   data-component="Nome"       raiz de um bloco interativo (classe abaixo)
 *   data-click="caminho"        função de renderVals() chamada no clique
 *   data-bind-text="{{caminho}}"            texto
 *   data-bind-style="prop: {{caminho}}"     propriedades de estilo
 *   data-bind-class / data-bind-show / data-bind-<atributo>
 * Cada classe guarda seu estado em this.state e devolve os valores em renderVals().
 */
(function () {
  'use strict';

  const get = (obj, path) => path.split('.').reduce((o, k) => (o == null ? undefined : o[k]), obj);
  const fill = (tpl, vals) => tpl.replace(/\{\{\s*([^}]+?)\s*\}\}/g, (_, p) => {
    const v = get(vals, p);
    return v == null ? '' : String(v);
  });

  class UVComponent {
    constructor(root) {
      this.root = root;
      this.state = {};
    }

    setState(patch) {
      this.state = Object.assign({}, this.state, patch);
      this.update();
    }

    owns(el) {
      return el.closest('[data-component]') === this.root;
    }

    mount() {
      this.bound = Array.from(this.root.querySelectorAll('[data-bind]')).filter((el) => this.owns(el));
      if (this.root.hasAttribute('data-bind')) this.bound.unshift(this.root);
      this.root.addEventListener('click', (event) => {
        const el = event.target.closest('[data-click]');
        if (!el || !this.owns(el)) return;
        const fn = get(this.vals, el.getAttribute('data-click'));
        if (typeof fn === 'function') fn(event);
      });
      this.update();
    }

    update() {
      const vals = (this.vals = this.renderVals());
      this.bound.forEach((el) => {
        Array.from(el.attributes).forEach((attr) => {
          if (!attr.name.startsWith('data-bind-')) return;
          const key = attr.name.slice(10);
          if (key === 'style') {
            attr.value.split(';').forEach((decl) => {
              const i = decl.indexOf(':');
              if (i > 0) el.style.setProperty(decl.slice(0, i).trim(), fill(decl.slice(i + 1).trim(), vals));
            });
          } else if (key === 'text') {
            const text = fill(attr.value, vals);
            if (el.textContent !== text) el.textContent = text;
          } else if (key === 'class') {
            const next = fill(attr.value, vals);
            if (el.__uvClass && el.__uvClass !== next) el.classList.remove(el.__uvClass);
            if (next) el.classList.add(next);
            el.__uvClass = next;
          } else if (key === 'show') {
            el.style.display = get(vals, attr.value) ? 'contents' : 'none';
          } else {
            el.setAttribute(key, fill(attr.value, vals));
          }
        });
      });
    }
  }

  const pad = (n) => (n < 10 ? '0' : '') + n;

  // Lista de abas: devolve { pressed, pick } para cada item
  const tabs = (component, key, count, sel) => {
    const out = [];
    for (let i = 0; i < count; i++) {
      out.push({ pressed: i === sel ? 'true' : 'false', on: i === sel, pick: () => component.setState({ [key]: i }) });
    }
    return out;
  };

// Página Canais e Aplicações: menu lateral e pausa de movimento
class Canais extends UVComponent {
  renderVals() {
    const s = this.state || {};
    const active = s.active || 'linkedin';
    const paused = !!s.paused;
    const ids = ['linkedin', 'instagram', 'email', 'portal', 'insights', 'apresentacoes', 'comerciais', 'eventos', 'audiovisual'];
    const nav = {};
    ids.forEach((id) => {
      const on = id === active;
      nav[id] = {
        color: on ? '#CC003D' : '#535E5E',
        bg: on ? '#FCE9EE' : 'transparent',
        pick: () => this.setState({ active: id })
      };
    });
    return {
      nav: nav,
      rootClass: paused ? 'grh-paused' : 'grh-live',
      motionLabel: paused ? 'Retomar movimento' : 'Pausar movimento',
      motionPressed: paused ? 'true' : 'false',
      toggleMotion: () => this.setState({ paused: !paused })
    };
  }
}

// 01 LinkedIn: exemplos de post por intenção
class CanaisLinkedin extends UVComponent {
  renderVals() {
    const sel = (this.state || {}).intent || 0;
    const data = [
      {
        answers: 'Por que o tema importa agora.',
        attach: 'slides',
        text: '[Tema] entrou na agenda das lideranças de RH. Nos últimos encontros, três sinais se repetiram: [sinal 1], [sinal 2] e [sinal 3]. A pergunta que fica para o mercado: [pergunta]?'
      },
      {
        answers: 'Quem esteve na conversa e o que ficou dela.',
        attach: 'photo',
        img: 'img/forum.jpg',
        alt: 'Plateia em uma edição do Fórum GRH',
        tag: '[FOTO] ENCONTRO',
        text: '[Número] lideranças de RH se reuniram no [evento], em [cidade], para discutir [tema]. Mais do que a programação, ficou a qualidade da conversa: [aprendizado em uma frase]. Obrigado a [parceiros] por construírem este encontro com a gente.'
      },
      {
        answers: 'O que vai estar em discussão, e para quem.',
        attach: 'invite',
        text: 'Em [data], o [evento] reúne lideranças de RH em [cidade] para discutir [tema]. A conversa parte de uma pergunta: [pergunta central]. [Condição de participação]. Saiba como participar: [link].'
      },
      {
        answers: 'Quem se destaca e por quê.',
        attach: 'photo',
        img: 'img/mais-admirados.jpg',
        alt: 'Palco do prêmio CEOs e RHs Mais Admirados',
        tag: '[FOTO] PREMIAÇÃO',
        text: '[Nome], [cargo] na [empresa], está entre os [reconhecidos] de [ano]. Um reconhecimento à trajetória e às práticas que [Nome] construiu em [área]. Parabéns a todos os [finalistas].'
      },
      {
        answers: 'Qual visão a marca ajuda a circular.',
        attach: 'data',
        text: 'O que [número] lideranças de RH responderam sobre [tema]: [dado principal]. No Insights desta semana, [especialista] interpreta o que isso muda na prática. Leia a análise completa: [link].'
      }
    ];
    const post = data[sel];
    return {
      intents: tabs(this, 'intent', data.length, sel),
      post: post,
      photo: {
        img: post.img || data[1].img,
        alt: post.alt || '',
        tag: post.tag || ''
      },
      show: {
        slides: post.attach === 'slides',
        photo: post.attach === 'photo',
        invite: post.attach === 'invite',
        data: post.attach === 'data'
      }
    };
  }
}

// 01 E-mail marketing: régua por momento da jornada
class CanaisEmail extends UVComponent {
  renderVals() {
    const sel = (this.state || {}).step || 0;
    const data = [
      { subject: '[Nome], uma conversa sobre [tema] em [data]', to: 'Lideranças com perfil para o encontro', why: 'O tema, quem estará na mesa e por que a pessoa foi lembrada.', value: 'Acesso a uma conversa qualificada entre pares.', cta: 'Confirmar presença' },
      { subject: 'Presença confirmada: [evento], [data]', to: 'Quem aceitou o convite', why: 'Tudo o que a pessoa precisa para se organizar, em uma mensagem só.', value: 'Clareza e cuidado antes do encontro.', cta: 'Salvar na agenda' },
      { subject: '[Evento] é [amanhã]: local, horário e acesso', to: 'Confirmados', why: 'Logística sem atrito: endereço, horário, acesso e contato da equipe.', value: 'Hospitalidade desde antes da chegada.', cta: 'Ver como chegar' },
      { subject: 'Obrigado por estar no [evento]', to: 'Quem participou', why: 'Reconhecer a presença e o que cada pessoa trouxe para a conversa.', value: 'Memória e pertencimento.', cta: 'Ver fotos do encontro' },
      { subject: 'O que ficou da conversa sobre [tema]', to: 'Participantes e lideranças interessadas no tema', why: 'Os aprendizados organizados, com falas e dados do encontro.', value: 'Repertório para levar para a empresa.', cta: 'Ler a síntese' },
      { subject: 'A próxima conversa: [tema], em [cidade]', to: 'Quem participou e quem tem afinidade com o tema', why: 'A relação continua: há um próximo encontro ou conteúdo à espera da pessoa.', value: 'Relacionamento ao longo do ano, não só no dia do evento.', cta: 'Garantir meu lugar' }
    ];
    const labels = ['Convite', 'Confirmação', 'Lembrete', 'Agradecimento', 'Devolutiva', 'Próximo passo'];
    const steps = tabs(this, 'step', data.length, sel).map((t, i) => Object.assign(t, { state: i < sel ? 'done' : i === sel ? 'current' : 'next' }));
    return {
      steps: steps,
      mail: data[sel],
      moment: pad(sel + 1) + ' de 06 · ' + labels[sel],
      fill: (sel / (data.length - 1)) * 100 + '%'
    };
  }
}

// 01 Portal e site: mapa do ecossistema por tipo de entrada
class CanaisPortal extends UVComponent {
  renderVals() {
    const sel = (this.state || {}).lens || 0;
    const notes = [
      'Por produto: as quatro frentes do ecossistema e o que cada uma reúne.',
      'Por público: quem chega ao site e onde encontra seu lugar.',
      'Por objetivo: o que a pessoa quer resolver e qual frente responde.',
      'Por momento da relação: da descoberta ao reconhecimento.'
    ];
    return {
      lenses: tabs(this, 'lens', notes.length, sel),
      note: notes[sel]
    };
  }
}

// 02 Apresentações: template de slide por bloco
class CanaisSlides extends UVComponent {
  renderVals() {
    const sel = (this.state || {}).slide || 0;
    const data = [
      ['Tese', 'Uma frase que a sala consegue repetir. Abre a apresentação e volta no fim.'],
      ['Contexto', 'Por que o tema importa agora e para quem está na sala. Três pontos, no máximo.'],
      ['Prova', 'Um dado, um caso ou uma imagem por slide, sempre com fonte.'],
      ['Aplicação', 'Como a tese vira prática: etapas, formatos e entregas.'],
      ['CTA', 'Um próximo passo claro, com responsável e prazo.']
    ];
    return {
      slides: tabs(this, 'slide', data.length, sel),
      counter: pad(sel + 1) + ' / 05 · ' + data[sel][0].toUpperCase(),
      guide: data[sel][1]
    };
  }
}

// 02 Materiais comerciais: checklist antes de enviar
class CanaisChecklist extends UVComponent {
  renderVals() {
    const done = (this.state || {}).done || [false, false, false, false, false, false];
    const count = done.filter(Boolean).length;
    const total = done.length;
    const items = done.map((on, i) => ({
      pressed: on ? 'true' : 'false',
      toggle: () => {
        const next = done.slice();
        next[i] = !next[i];
        this.setState({ done: next });
      }
    }));
    const left = total - count;
    return {
      items: items,
      count: count + ' de ' + total,
      width: (count / total) * 100 + '%',
      color: count === total ? '#061718' : '#CC003D',
      status: count === total ? 'Pronto para enviar.' : left === 1 ? 'Falta 1 item antes de enviar.' : 'Faltam ' + left + ' itens antes de enviar.',
      reset: () => this.setState({ done: [false, false, false, false, false, false] })
    };
  }
}

// 03 Eventos e cenografia: planta da jornada
class CanaisJornada extends UVComponent {
  renderVals() {
    const sel = (this.state || {}).stop || 0;
    const data = [
      { name: 'Chegada', role: 'ACOLHER', x: 52, y: 226, text: 'A marca recebe antes de informar. Sinalização clara desde o acesso e equipe visível na entrada.' },
      { name: 'Credenciamento', role: 'ORIENTAR', x: 52, y: 136, text: 'Rápido e nominal. É o primeiro contato pessoal com a anfitriã e o momento de apresentar o percurso.' },
      { name: 'Ponto instagramável', role: 'REGISTRAR', x: 52, y: 62, text: 'Cenário com a marca e o tema da edição, com luz própria e enquadramento para foto vertical e horizontal.' },
      { name: 'Palco', role: 'COMUNICAR', x: 322, y: 90, text: 'Fundo limpo, com produto e tema legíveis na foto e no vídeo. O palco diz onde a pessoa está.' },
      { name: 'Networking', role: 'CONECTAR', x: 205, y: 185, text: 'Mesas altas, circulação livre e som baixo o bastante para conversar. É onde o relacionamento acontece.' },
      { name: 'Depoimentos', role: 'PROVAR', x: 338, y: 224, text: 'Canto reservado e silencioso para gravar falas curtas de convidados ainda durante o evento.' }
    ];
    const stops = tabs(this, 'stop', data.length, sel).map((t) => Object.assign(t, {
      fill: t.on ? '#CC003D' : '#FFFFFF',
      ink: t.on ? '#FFFFFF' : '#061718'
    }));
    const cur = data[sel];
    return {
      stops: stops,
      cur: cur,
      title: pad(sel + 1) + ' · ' + cur.name,
      role: 'FUNÇÃO · ' + cur.role
    };
  }
}

// 04 Fotografia e audiovisual: visor e matriz de captação
class CanaisCaptacao extends UVComponent {
  renderVals() {
    const sel = (this.state || {}).format || 0;
    const uses = ['Redes', 'Site', 'Revista', 'Capas', 'Apresentações', 'Pós-evento', 'Comercial'];
    // 2 = uso principal, 1 = apoio, 0 = não indicado (mesma ordem de uses)
    const data = [
      { name: 'Foto horizontal', ratio: '3 / 2', w: '100%', spec: '3:2 · 16:9', img: 'img/forum.jpg', pos: '50% 50%', alt: 'Plateia em uma edição do Fórum GRH', tip: 'Plano aberto: palco, público e marca no mesmo quadro.', uses: [1, 2, 2, 1, 2, 2, 2] },
      { name: 'Foto vertical', ratio: '4 / 5', w: '64%', spec: '4:5', img: 'img/experience-esportes.jpg', pos: '50% 50%', alt: 'GRH Experience de esportes', tip: 'Pessoas em primeiro plano, com a marca legível ao fundo.', uses: [2, 1, 2, 2, 1, 2, 1] },
      { name: 'Reels', ratio: '9 / 16', w: '50%', spec: '9:16', img: 'img/experience-experiencias.jpg', pos: '62% 50%', alt: 'GRH Experience de experiências', tip: 'Movimento e som ambiente. Os primeiros segundos mostram onde a pessoa está.', uses: [2, 0, 0, 0, 0, 2, 1] },
      { name: 'Aftermovie', ratio: '16 / 9', w: '100%', spec: '16:9', img: 'img/celebration.jpg', pos: '50% 50%', alt: 'Convidados no GRH Celebration', tip: 'A narrativa do encontro: chegada, conteúdo, troca e encerramento.', uses: [1, 2, 0, 0, 2, 2, 2] },
      { name: 'Depoimento', ratio: '9 / 16', w: '50%', spec: '9:16 · 16:9', img: 'img/connection.jpg', pos: '54% 40%', alt: 'Palco de uma edição do GRH Connection', tip: 'Fala curta, em local silencioso, com nome e cargo na tela.', uses: [2, 2, 1, 0, 2, 1, 2] },
      { name: 'Capa', ratio: '3 / 4', w: '60%', spec: '3:4', img: 'img/excelencia.jpg', pos: '50% 50%', alt: 'Palco da premiação Excelência em Gestão de Pessoas', tip: 'Área livre para título e marca. Foco no rosto ou no palco.', uses: [1, 2, 2, 2, 2, 0, 1] },
      { name: 'Bastidor', ratio: '1 / 1', w: '76%', spec: 'livre', img: 'img/roadshow.jpg', pos: '80% 50%', alt: 'Visita em uma parada do Roadshow GRH', tip: 'Conversas fora do palco e preparação da equipe, sem pose.', uses: [2, 0, 1, 0, 0, 2, 0] }
    ];
    const cur = data[sel];
    const main = uses.filter((u, i) => cur.uses[i] === 2);
    return {
      formats: tabs(this, 'format', data.length, sel),
      cur: cur,
      main: 'USO PRINCIPAL · ' + main.join(', ')
    };
  }
}

  const registry = { Canais, CanaisLinkedin, CanaisEmail, CanaisPortal, CanaisSlides, CanaisChecklist, CanaisJornada, CanaisCaptacao };

  function start() {
    let page = null;
    document.querySelectorAll('[data-component]').forEach((root) => {
      const Component = registry[root.getAttribute('data-component')];
      if (!Component) return;
      const instance = new Component(root);
      instance.mount();
      if (!page && root.querySelector('main')) page = instance;
    });

    // O menu lateral acompanha o canal que está na tela.
    if (page && 'IntersectionObserver' in window) {
      const spy = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) page.setState({ active: entry.target.id });
        });
      }, { rootMargin: '-30% 0px -65% 0px' });
      document.querySelectorAll('main article[id]').forEach((article) => spy.observe(article));
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
