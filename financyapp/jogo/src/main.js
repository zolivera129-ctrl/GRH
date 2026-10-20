// Liga a página: carrega os dados, valida o layout, desenha a sala e
// mostra o resultado da validação.

import { carregarTudo } from './carregar.js';
import { desenharSala, tamanhoDaSala } from './sala.js';
import { validar, resumo } from './validacao.js';

const ESCALA = 2;   // a arte é feita em 1x e ampliada 2x sem suavizar

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

async function iniciar() {
  const canvas = document.getElementById('sala');
  let dados;
  try {
    dados = await carregarTudo();
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
  canvas.style.width = `${largura * ESCALA}px`;
  canvas.style.height = `${altura * ESCALA}px`;
  const ctx = canvas.getContext('2d');
  const planta = document.getElementById('mostrar-planta');
  const desenhar = () => desenharSala(ctx, dados, { planta: planta.checked });
  planta.addEventListener('change', desenhar);
  desenhar();
  mostrarValidacao(dados.layout);
  document.body.dataset.pronto = 'sim';
}

iniciar();
