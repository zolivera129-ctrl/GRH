// Testes da validação da planta. Rodar com: npm test (ou node --test)
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validar, circulacaoObrigatoria, resumo } from '../src/validacao.js';

const LAYOUT = JSON.parse(readFileSync(new URL('../../docs/FinancyApp_Layout_12x10_v1.json', import.meta.url), 'utf8'));

// cópia do layout com mudanças, para quebrar uma regra de cada vez
function com(mudar) {
  const lay = structuredClone(LAYOUT);
  mudar(lay);
  return lay;
}
const peca = (lay, id) => lay.pecas_piso.find((p) => p.id === id);
const falhou = (v) => v.regras.filter((r) => !r.ok).map((r) => r.numero);

test('o layout padrão passa nas seis regras', () => {
  const v = validar(LAYOUT);
  assert.deepEqual(falhou(v), []);
  assert.equal(v.ok, true);
});

test('os números do layout padrão batem com a planta', () => {
  const r = resumo(LAYOUT);
  assert.equal(r.livres, 90);
  assert.equal(r.alcancaveis, 90);          // todos alcançáveis, nenhum bolsão isolado
  assert.equal(r.acesso, 17);               // pontos de uso e frentes de porta
});

test('a circulação obrigatória calculada é a da planta mais A1/B8', () => {
  // A planta lista 10 tiles. A1/B8 também é obrigatório: é o único acesso ao
  // ponto de uso do malote em A1/B7 (ver NOTAS_DE_IMPLEMENTACAO.md).
  const esperado = new Set([...LAYOUT.circulacao_obrigatoria, [1, 8]].map(([a, b]) => `${a},${b}`));
  const calculado = new Set(circulacaoObrigatoria(LAYOUT).map(([a, b]) => `${a},${b}`));
  assert.deepEqual(calculado, esperado);
  assert.equal(resumo(LAYOUT).decorar, 62);
});

test('regra 1: peça fora da sala', () => {
  const v = validar(com((lay) => { peca(lay, 'planta').tile = [12, 0]; }));
  assert.ok(falhou(v).includes(1));
});

test('regra 1: peças sobrepostas', () => {
  const v = validar(com((lay) => { peca(lay, 'planta').tile = [5, 1]; }));    // em cima da mesa do Saldanha
  assert.ok(falhou(v).includes(1));
});

test('regra 2: entrada ocupada', () => {
  const v = validar(com((lay) => { peca(lay, 'malote').tile = [0, 8]; }));
  assert.ok(falhou(v).includes(2));
});

test('regra 3: ponto de uso ocupado', () => {
  const v = validar(com((lay) => { peca(lay, 'planta').tile = [3, 6]; }));    // visitante do balcão
  assert.deepEqual(falhou(v), [3]);
});

test('regra 3: ponto de uso que fica sem caminho', () => {
  const v = validar(com((lay) => {
    lay.pecas_piso.push({ id: 'vaso', tipo: 'movel', tile: [1, 8], base: [1, 1] });
  }));
  assert.deepEqual(falhou(v), [3]);
  assert.match(v.regras[2].falhas[0], /A1\/B7 não é alcançável/);
});

test('regra 4: frente de porta sem caminho', () => {
  // A4/B0 a A4/B2 é o único caminho para a faixa do fundo
  const v = validar(com((lay) => {
    lay.pecas_piso.push({ id: 'estante', tipo: 'movel', tile: [4, 1], base: [1, 1] });
  }));
  assert.ok(falhou(v).includes(4));
});

test('regra 5: cadeira sem vizinho alcançável', () => {
  // A0/B3 é o único acesso à cadeira da reunião em A0/B2
  const v = validar(com((lay) => {
    lay.pecas_piso.push({ id: 'vaso', tipo: 'movel', tile: [0, 3], base: [1, 1] });
  }));
  assert.ok(falhou(v).includes(5));
  assert.ok(v.regras[4].falhas.some((f) => f.startsWith('cad_reuniao_4')));
});

test('regra 5: caminha sem vizinho alcançável', () => {
  // A11/B2 é o único acesso à manta da Flora
  const v = validar(com((lay) => {
    lay.pecas_piso.push({ id: 'vaso', tipo: 'movel', tile: [11, 2], base: [1, 1] });
  }));
  assert.ok(v.regras[4].falhas.some((f) => f.startsWith('manta_flora')));
});

test('regra 6: a estação reservada ocupa os tiles dela', () => {
  const v = validar(LAYOUT);
  assert.equal(v.ocupacao.get('9,6'), 'flex_mesa');
  assert.equal(v.ocupacao.get('10,5'), 'flex_cadeira');
  // um móvel em cima da estação reservada quebra as regras 1 e 6
  const quebrado = validar(com((lay) => {
    lay.pecas_piso.unshift({ id: 'sofa', tipo: 'movel', tile: [9, 6], base: [1, 1] });
  }));
  assert.ok(falhou(quebrado).includes(1));
  assert.ok(falhou(quebrado).includes(6));
});
