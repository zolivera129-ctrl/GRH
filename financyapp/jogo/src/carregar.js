// Carrega o manifesto dos assets, o layout da planta e todas as imagens.

export const CAMINHOS = {
  assets: '../pixel-art-habbo/assets/',
  layout: '../docs/FinancyApp_Layout_12x10_v1.json',
};

async function carregarJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`não carregou ${url} (${r.status})`);
  return r.json();
}

function carregarImagem(url) {
  return new Promise((ok, erro) => {
    const im = new Image();
    im.onload = () => ok(im);
    im.onerror = () => erro(new Error(`não carregou ${url}`));
    im.src = url;
  });
}

/**
 * Os arquivos de uma peça, pela regra de nomes da v2.2: modelo.png com um
 * estado só, modelo__estado.png ou modelo__direcao.png com vários, mais as
 * camadas (modelo__camada.png). É a mesma regra do build.py.
 */
export function arquivos(modelo, e) {
  const tipos = e.estados ?? e.direcoes ?? e.variacoes;
  const nomes = tipos ? tipos.map((t) => `${modelo}__${t}`) : (e.camadas ? [] : [modelo]);
  for (const c of e.camadas ?? []) nomes.push(`${modelo}__${c}`);
  return nomes.map((n) => `${e.pasta}/${n}.png`);
}

/** Devolve { manifesto, layout, imagens }, com imagens indexadas pelo caminho dentro do assets/. */
export async function carregarTudo() {
  const [manifesto, layout] = await Promise.all([
    carregarJSON(`${CAMINHOS.assets}manifest.json`),
    carregarJSON(CAMINHOS.layout),
  ]);
  const caminhos = new Set();
  for (const [modelo, e] of Object.entries(manifesto)) {
    if (e.folha) caminhos.add(e.folha);
    else if (e.pasta) for (const f of arquivos(modelo, e)) caminhos.add(f);
  }
  const imagens = new Map();
  await Promise.all([...caminhos].map(async (c) => {
    imagens.set(c, await carregarImagem(CAMINHOS.assets + c));
  }));
  return { manifesto, layout, imagens };
}
