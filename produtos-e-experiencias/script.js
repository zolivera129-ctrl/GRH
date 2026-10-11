/*
 * Universo Visual · Brandcenter Gestão RH
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

// Página Produtos e Experiências: menu lateral e pausa de movimento
class Produtos extends UVComponent {
  renderVals() {
    const s = this.state || {};
    const active = s.active || 'simbolos';
    const paused = !!s.paused;
    const ids = ['simbolos', 'relacionamento', 'encontros', 'midia', 'reconhecimento', 'ecossistema'];
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

// 04 Inteligência e mídia
class ProdutosMidia extends UVComponent {
  lum(hex) {
    const n = parseInt(hex.slice(1), 16);
    const ch = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => {
      const x = v / 255;
      return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2];
  }
  ratio(a, b) {
    const la = this.lum(a);
    const lb = this.lum(b);
    const x = (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
    return '✓ ' + x.toFixed(1).replace('.', ',') + ':1';
  }
  copy(text) {
    const done = (ok) => {
      this.setState({ copied: true, ok: ok });
      clearTimeout(this._t);
      this._t = setTimeout(() => this.setState({ copied: false }), 1800);
    };
    try {
      navigator.clipboard.writeText(text).then(() => done(true), () => done(false));
    } catch (e) {
      done(false);
    }
  }
  componentWillUnmount() {
    clearTimeout(this._t);
  }
  renderVals() {
    const s = this.state || {};
    const sel = s.filter || 'Todos';
    const subject = '[Tema da semana]: o que as lideranças de RH estão discutindo';
    const filters = ['Todos', 'Conversas', 'Pesquisas', 'Experiências'].map((f) => {
      const on = f === sel;
      return { label: f, pressed: on ? 'true' : 'false', bg: on ? '#061718' : 'transparent', fg: on ? '#FFFFFF' : '#061718', pick: () => this.setState({ filter: f }) };
    });
    const cards = [
      ['Conversas', '[Frase de liderança que resume o debate]'],
      ['Pesquisas', '[Dado que muda a leitura do mercado]'],
      ['Experiências', '[Aprendizado de um encontro]'],
      ['Pesquisas', '[Tendência identificada na pesquisa]']
    ].map((k) => ({ theme: k[0], text: k[1], opacity: sel === 'Todos' || sel === k[0] ? 1 : 0.25 }));
    return {
      filters: filters,
      cards: cards,
      subjectLabel: s.copied ? (s.ok ? 'Copiado' : 'Selecione o assunto acima') : 'Copiar modelo de assunto',
      copySubject: () => this.copy(subject),
      r: {
        portal: this.ratio('#061718', '#FFFFFF'),
        revista: this.ratio('#451531', '#FFFFFF'),
        tv: this.ratio('#8198FF', '#061718'),
        news: this.ratio('#B1DAE5', '#061718'),
        insights: this.ratio('#F498B1', '#061718')
      }
    };
  }
}

// 03 Encontros e experiências
class ProdutosEncontros extends UVComponent {
  lum(hex) {
    const n = parseInt(hex.slice(1), 16);
    const ch = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => {
      const x = v / 255;
      return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2];
  }
  ratio(a, b) {
    const la = this.lum(a);
    const lb = this.lum(b);
    const x = (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
    return '✓ ' + x.toFixed(1).replace('.', ',') + ':1';
  }
  renderVals() {
    const s = this.state || {};
    const sel = s.city || 0;
    const data = [
      ['Curitiba', '50.9%', '82.6%', 'img/regional-curitiba.jpg'],
      ['Porto Alegre', '43.1%', '97%', 'img/regional-porto-alegre.jpg'],
      ['Rio de Janeiro', '75.3%', '74.7%', 'img/regional-rio-de-janeiro.jpg'],
      ['Belo Horizonte', '72.2%', '62%', 'img/regional-belo-horizonte.jpg'],
      ['Fortaleza', '93.9%', '14.8%', 'img/regional-fortaleza.jpg'],
      ['Manaus', '7.9%', '12.9%', 'img/regional-manaus.jpg']
    ];
    const cities = data.map((c, i) => {
      const on = i === sel;
      return {
        name: c[0],
        x: c[1],
        y: c[2],
        img: c[3],
        alt: on ? 'Vista de ' + c[0] : '',
        pressed: on ? 'true' : 'false',
        size: on ? '24px' : '14px',
        dot: on ? '#E83363' : '#4287C7',
        opacity: on ? 1 : 0,
        bg: on ? '#061718' : 'transparent',
        fg: on ? '#FFFFFF' : '#061718',
        pick: () => this.setState({ city: i })
      };
    });
    return {
      cities: cities,
      city: data[sel][0],
      r: {
        connection: this.ratio('#7ABDD0', '#061718'),
        private: this.ratio('#7ABDD0', '#451531'),
        experience: this.ratio('#8F74B1', '#061718'),
        forum: this.ratio('#CAD63C', '#061718'),
        regional: this.ratio('#4287C7', '#061718'),
        roadshow: this.ratio('#E47A39', '#451531'),
        celebration: this.ratio('#061718', '#FFFFFF')
      }
    };
  }
}

  const registry = { Produtos, ProdutosMidia, ProdutosEncontros };

  function start() {
    let page = null;
    document.querySelectorAll('[data-component]').forEach((root) => {
      const Component = registry[root.getAttribute('data-component')];
      if (!Component) return;
      const instance = new Component(root);
      instance.mount();
      if (!page && root.querySelector('main')) page = instance;
    });

    // O menu lateral acompanha a seção que está na tela.
    if (page && 'IntersectionObserver' in window) {
      const spy = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) page.setState({ active: entry.target.id });
        });
      }, { rootMargin: '-30% 0px -65% 0px' });
      document.querySelectorAll('main section[id]').forEach((section) => spy.observe(section));
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
