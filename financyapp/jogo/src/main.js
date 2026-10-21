// Liga a página: carrega os dados, valida o layout, desenha a sala e
// mostra o resultado da validação.

import { carregarTudo } from './carregar.js';
import { desenharSala, tamanhoDaSala } from './sala.js';
import { validar, resumo } from './validacao.js';

// a arte é feita em 1x e ampliada 2x sem suavizar; numa tela estreita,
// como a do celular, fica em 1x
const ESCALA = 2;

function item(texto, classe) {
  const li = document.createElement('li');
  li.textContent = texto;
  if (classe) li.className = classe;
  return li;
}

function mostrarValidacao(layout) {
  const v = validar(layout);
  const lista = document.getElementById('regras');
  lista.replaceChildren();
  for (const r of v.regras) {
    const li = item(`${r.ok ? '✓' : '✗'} ${r.numero}. ${r.texto}`, r.ok ? 'ok' : 'falha');
    if (r.falhas.length) {
      const sub = document.createElement('ul');
      for (const f of r.falhas) sub.append(item(f));
      li.append(sub);
    }
    lista.append(li);
  }
  const r = resumo(layout);
  document.getElementById('veredito').textContent = v.ok
    ? 'O layout passa nas seis regras.'
    : 'O layout não passa: veja as regras marcadas.';
  document.getElementById('veredito').className = v.ok ? 'ok' : 'falha';
  document.getElementById('resumo').replaceChildren(
    item(`${r.livres} tiles livres, ${r.alcancaveis} alcançáveis a partir da entrada`),
    item(`${r.acesso} de acesso: entrada, pontos de uso e frentes de porta`),
    item(`${r.circulacao} de circulação obrigatória`),
    item(`${r.decorar} livres para decorar`),
  );
}

function ajustarEscala(canvas) {
  // mede a largura da página, e não a do palco, que cresce com a sala
  const cabe = document.getElementById('jogo').clientWidth >= canvas.width * ESCALA;
  const escala = cabe ? ESCALA : 1;
  canvas.style.width = `${canvas.width * escala}px`;
  canvas.style.height = `${canvas.height * escala}px`;
}

async function iniciar() {
  const canvas = document.getElementById('sala');
  const { assets, layout } = document.getElementById('jogo').dataset;
  let dados;
  try {
    dados = await carregarTudo({ assets, layout });
  } catch (erro) {
    const aviso = document.getElementById('erro');
    aviso.hidden = false;
    aviso.textContent = `${erro.message}. Abra a página pelo servidor local: na pasta financyapp, rode `
      + '"python3 -m http.server 8000" e acesse http://localhost:8000/jogo/.';
    return;
  }
  const { largura, altura } = tamanhoDaSala(dados.layout, dados.manifesto);
  canvas.width = largura;
  canvas.height = altura;
  ajustarEscala(canvas);
  window.addEventListener('resize', () => ajustarEscala(canvas));
  const ctx = canvas.getContext('2d');
  const planta = document.getElementById('mostrar-planta');
  const desenhar = () => desenharSala(ctx, dados, { planta: planta.checked });
  planta.addEventListener('change', desenhar);
  desenhar();
  mostrarValidacao(dados.layout);
  document.body.dataset.pronto = 'sim';
}

iniciar();
