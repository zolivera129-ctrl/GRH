// Validação da planta: as seis regras da seção "Validação" de
// docs/FinancyApp_Planta_12x10_v1.md. Roda ao carregar o layout e, mais
// tarde, a cada vez que um móvel for movido. Função pura: não mexe na página.

export const REGRAS = [
  'Nenhuma peça fora da sala ou sobreposta a outra.',
  'O tile de entrada está livre.',
  'Todo ponto de uso está livre e é alcançável a partir da entrada.',
  'A frente de toda porta está livre e é alcançável.',
  'Toda cadeira, caminha e estação reservada tem pelo menos um vizinho alcançável.',
  'A estação reservada conta como ocupada desde já.',
];

// peças que precisam de um vizinho alcançável (regra 5)
const PRECISA_DE_VIZINHO = new Set(['cadeira', 'caminha_pet', 'reservado']);
// caminhos em quatro direções, sem diagonal
const VIZINHOS = [[1, 0], [-1, 0], [0, 1], [0, -1]];

const chave = (a, b) => `${a},${b}`;
export const nomeDoTile = (a, b) => `A${a}/B${b}`;

function tilesDaPeca(p) {
  const [a0, b0] = p.tile;
  const [da, db] = p.base;
  const out = [];
  for (let a = a0; a < a0 + da; a++) {
    for (let b = b0; b < b0 + db; b++) out.push([a, b]);
  }
  return out;
}

/**
 * Confere o layout contra as seis regras.
 * Devolve { ok, regras: [{numero, texto, ok, falhas}], ocupacao, alcance, resumo }.
 * ocupacao: Map "a,b" -> id da peça; alcance: Set "a,b" dos tiles livres
 * alcançáveis a partir da entrada.
 */
export function validar(layout) {
  const [A, B] = layout.sala.tiles;
  const falhas = REGRAS.map(() => []);
  const dentro = (a, b) => a >= 0 && a < A && b >= 0 && b < B;

  // regras 1 e 6: a ocupação inclui a estação reservada
  const ocupacao = new Map();
  for (const p of layout.pecas_piso) {
    for (const [a, b] of tilesDaPeca(p)) {
      if (!dentro(a, b)) {
        falhas[0].push(`${p.id} sai da sala em ${nomeDoTile(a, b)}`);
      } else if (ocupacao.has(chave(a, b))) {
        falhas[0].push(`${p.id} fica em cima de ${ocupacao.get(chave(a, b))} em ${nomeDoTile(a, b)}`);
      } else {
        ocupacao.set(chave(a, b), p.id);
      }
    }
  }
  for (const p of layout.pecas_piso.filter((p) => p.tipo === 'reservado')) {
    for (const [a, b] of tilesDaPeca(p)) {
      if (dentro(a, b) && ocupacao.get(chave(a, b)) !== p.id) {
        falhas[5].push(`${p.id} não está ocupando ${nomeDoTile(a, b)}`);
      }
    }
  }
  const livre = (a, b) => dentro(a, b) && !ocupacao.has(chave(a, b));

  // regra 2 e o alcance a partir da entrada
  const [ea, eb] = layout.entrada;
  const alcance = new Set();
  if (!livre(ea, eb)) {
    falhas[1].push(`a entrada ${nomeDoTile(ea, eb)} está ocupada por ${ocupacao.get(chave(ea, eb)) ?? 'fora da sala'}`);
  } else {
    const fila = [[ea, eb]];
    alcance.add(chave(ea, eb));
    while (fila.length) {
      const [a, b] = fila.shift();
      for (const [da, db] of VIZINHOS) {
        const [na, nb] = [a + da, b + db];
        if (livre(na, nb) && !alcance.has(chave(na, nb))) {
          alcance.add(chave(na, nb));
          fila.push([na, nb]);
        }
      }
    }
  }
  const conferirAcesso = (regra, rotulo, a, b) => {
    if (!livre(a, b)) {
      falhas[regra].push(`${rotulo}: ${nomeDoTile(a, b)} está ocupado por ${ocupacao.get(chave(a, b)) ?? 'fora da sala'}`);
    } else if (!alcance.has(chave(a, b))) {
      falhas[regra].push(`${rotulo}: ${nomeDoTile(a, b)} não é alcançável a partir da entrada`);
    }
  };

  // regra 3: pontos de uso
  for (const ponto of layout.pontos_de_uso) {
    for (const [a, b] of ponto.tiles) conferirAcesso(2, ponto.nome, a, b);
  }

  // regra 4: frentes de porta
  for (const [porta, [a, b]] of Object.entries(layout.frentes_de_porta)) {
    conferirAcesso(3, `frente de ${porta}`, a, b);
  }

  // regra 5: cadeiras, camas e estação reservada
  for (const p of layout.pecas_piso.filter((p) => PRECISA_DE_VIZINHO.has(p.tipo))) {
    const proprios = new Set(tilesDaPeca(p).map(([a, b]) => chave(a, b)));
    const algum = tilesDaPeca(p).some(([a, b]) => VIZINHOS.some(([da, db]) => {
      const k = chave(a + da, b + db);
      return !proprios.has(k) && alcance.has(k);
    }));
    if (!algum) falhas[4].push(`${p.id} não tem vizinho alcançável`);
  }

  let livres = 0;
  for (let a = 0; a < A; a++) {
    for (let b = 0; b < B; b++) if (livre(a, b)) livres++;
  }
  const regras = REGRAS.map((texto, i) => ({ numero: i + 1, texto, ok: falhas[i].length === 0, falhas: falhas[i] }));
  return {
    ok: regras.every((r) => r.ok),
    regras,
    ocupacao,
    alcance,
    resumo: { livres, alcancaveis: alcance.size },
  };
}

/** Tiles que precisam ficar livres pelas regras 2 a 4: entrada, pontos de uso e frentes de porta. */
export function tilesDeAcesso(layout) {
  const out = new Set([chave(...layout.entrada)]);
  for (const ponto of layout.pontos_de_uso) for (const [a, b] of ponto.tiles) out.add(chave(a, b));
  for (const [a, b] of Object.values(layout.frentes_de_porta)) out.add(chave(a, b));
  return out;
}

/**
 * Circulação obrigatória: tiles livres, fora dos de acesso, que quebram
 * alguma regra se forem ocupados. É o que o jogo não deixa decorar.
 * Devolve uma lista de [a, b] em ordem.
 */
export function circulacaoObrigatoria(layout) {
  const base = validar(layout);
  if (!base.ok) return null;
  const acesso = tilesDeAcesso(layout);
  const [A, B] = layout.sala.tiles;
  const out = [];
  for (let a = 0; a < A; a++) {
    for (let b = 0; b < B; b++) {
      if (base.ocupacao.has(chave(a, b)) || acesso.has(chave(a, b))) continue;
      const teste = { id: 'teste', tipo: 'movel', tile: [a, b], base: [1, 1] };
      if (!validar({ ...layout, pecas_piso: [...layout.pecas_piso, teste] }).ok) out.push([a, b]);
    }
  }
  return out;
}

/** O resumo da planta: livres, alcançáveis, circulação, acesso e livres para decorar. */
export function resumo(layout) {
  const v = validar(layout);
  const circulacao = circulacaoObrigatoria(layout) ?? [];
  const acesso = [...tilesDeAcesso(layout)].filter((k) => !v.ocupacao.has(k));
  return {
    ...v.resumo,
    circulacao: circulacao.length,
    acesso: acesso.length,
    decorar: v.resumo.livres - circulacao.length - acesso.length,
  };
}
