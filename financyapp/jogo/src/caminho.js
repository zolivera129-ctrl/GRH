// Caminhos na planta: quais tiles estão livres, o caminho mais curto entre
// dois tiles (busca em largura, 4 direções, como a validação) e como se
// chega e se sai de cada cadeira.
//
// Posições contínuas: o tile (a, b) vai de a a a+1 e de b a b+1; o centro
// é (a + 0,5, b + 0,5).

export const VETOR = { '+A': [1, 0], '-A': [-1, 0], '+B': [0, 1], '-B': [0, -1] };
const VIZINHOS = [[1, 0], [-1, 0], [0, 1], [0, -1]];

export function criarGrade(layout) {
  const [A, B] = layout.sala.tiles;
  const ocupado = new Set();
  for (const p of layout.pecas_piso) {
    const [[a, b], [da, db]] = [p.tile, p.base];
    for (let i = a; i < a + da; i++) for (let j = b; j < b + db; j++) ocupado.add(`${i},${j}`);
  }
  const dentro = (a, b) => a >= 0 && b >= 0 && a < A && b < B;
  const livre = (a, b) => dentro(a, b) && !ocupado.has(`${a},${b}`);
  return { A, B, livre, dentro };
}

/** Caminho de tiles livres de 'de' até 'para' (inclusive), ou null. */
export function buscar(grade, de, para) {
  const k = ([a, b]) => `${a},${b}`;
  if (!grade.livre(...para)) return null;
  const veio = new Map([[k(de), null]]);
  const fila = [de];
  while (fila.length) {
    const t = fila.shift();
    if (t[0] === para[0] && t[1] === para[1]) {
      const out = [];
      for (let c = t; c; c = veio.get(k(c))) out.unshift(c);
      return out;
    }
    for (const [da, db] of VIZINHOS) {
      const n = [t[0] + da, t[1] + db];
      if (veio.has(k(n)) || !grade.livre(...n)) continue;
      veio.set(k(n), t);
      fila.push(n);
    }
  }
  return null;
}

export const centro = ([a, b]) => [a + 0.5, b + 0.5];

/** O tile em que está uma posição contínua (na borda, conta o de trás). */
export const tileDe = ([a, b]) => [Math.floor(a - 1e-3), Math.floor(b - 1e-3)];

/** Quem olha +A e +B senta de frente (com as animações de sentar). */
export const deFrente = (olha) => olha === '+A' || olha === '+B';

/**
 * Como se chega a uma cadeira e se sai dela.
 *  - de frente: o personagem fica em pé meio tile à frente do centro
 *    (ponto F, o fim do `desloca` de levantar). Entre F e um tile livre ao
 *    lado, ele anda pela borda (ponto L), sem atravessar a mesa.
 *  - de costas: não há animação de sentar de costas; chega pelo vizinho
 *    livre ao centro e senta direto.
 * Devolve { centro, frente, lateral, entrada } ou null se não há entrada.
 */
export function acessoDaCadeira(grade, cadeira) {
  const [a, b] = cadeira.tile;
  const C = [a + 0.5, b + 0.5];
  const [va, vb] = VETOR[cadeira.olha_para];
  if (!deFrente(cadeira.olha_para)) {
    for (const [da, db] of VIZINHOS) {
      if (grade.livre(a + da, b + db)) return { centro: C, frente: null, lateral: null, entrada: [a + da, b + db] };
    }
    return null;
  }
  const F = [C[0] + 0.5 * va, C[1] + 0.5 * vb];
  const perp = va ? [0, 1] : [1, 0];
  let melhor = null;
  for (const s of [-1, 1]) {
    const L = [F[0] + s * perp[0], F[1] + s * perp[1]];
    const t1 = [a + s * perp[0], b + s * perp[1]];             // ao lado da cadeira
    const t2 = [a + va + s * perp[0], b + vb + s * perp[1]];   // ao lado do que está à frente
    const livres = [t1, t2].filter((t) => grade.livre(...t));
    if (livres.length && (!melhor || livres.length > melhor.n)) melhor = { L, entrada: livres[0], n: livres.length };
  }
  return melhor ? { centro: C, frente: F, lateral: melhor.L, entrada: melhor.entrada } : null;
}

/** A direção de um passo (o eixo que mais muda). */
export function direcaoDoPasso([a0, b0], [a1, b1]) {
  const da = a1 - a0;
  const db = b1 - b0;
  if (Math.abs(da) >= Math.abs(db)) return da >= 0 ? '+A' : '-A';
  return db >= 0 ? '+B' : '-B';
}

/** Para onde olhar de 'de' até 'alvo'. */
export const olharPara = direcaoDoPasso;
