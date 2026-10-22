// O lado do jogo das animações (fase 7 do manual): o manifesto e as folhas
// que o pacote de arte gera, lidos como o jogo lê. O jogo do corte 1 só
// desenha o parado e o sentado de frente; estes testes garantem que o resto
// já chega inteiro e coerente para quando os cortes seguintes usarem.
// Rodar com: npm test (ou node --test)
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { arquivos } from '../src/carregar.js';

const ASSETS = new URL('../../pixel-art-habbo/assets/', import.meta.url);
const MAN = JSON.parse(readFileSync(new URL('manifest.json', ASSETS), 'utf8'));

// largura e altura de um PNG, lidas do cabeçalho (IHDR)
function tamanho(rel) {
  const b = readFileSync(new URL(rel, ASSETS));
  assert.equal(b.toString('ascii', 1, 4), 'PNG', rel);
  return [b.readUInt32BE(16), b.readUInt32BE(20)];
}
const personagens = Object.entries(MAN).filter(([, e]) => e.folha);
const dentro = ([x, y], [w, h]) => x >= 0 && y >= 0 && x < w && y < h;

test('a sala de hoje: o parado e o sentado de frente continuam nas linhas 0 e 1', () => {
  for (const [id, e] of personagens) {
    assert.equal(e.animacoes.parado_frente.linha, 0, id);
    assert.equal(e.animacoes.sentado_frente.linha, 1, id);
  }
});

test('cada folha tem uma linha por animação e cabe todos os quadros', () => {
  for (const [id, e] of personagens) {
    const [W, H] = tamanho(e.folha);
    const [w, h] = e.tela;
    const anims = Object.values(e.animacoes);
    const linhas = anims.map((a) => a.linha);
    assert.equal(new Set(linhas).size, linhas.length, `${id}: linha repetida`);
    assert.equal(H, h * (Math.max(...linhas) + 1), `${id}: altura da folha`);
    assert.equal(W, w * Math.max(...anims.map((a) => a.quadros)), `${id}: largura da folha`);
    assert.ok(dentro(e.ancora, [w, h + 1]), `${id}: âncora fora da tela`);
    for (const [nome, a] of Object.entries(e.animacoes)) {
      assert.ok(Number.isInteger(a.quadros) && a.quadros >= 1, `${id} ${nome}: quadros`);
      assert.ok(typeof a.fps === 'number' && a.fps >= 0, `${id} ${nome}: fps`);
      assert.ok(a.quadros === 1 || a.fps > 0, `${id} ${nome}: animação sem fps`);
    }
  }
});

test('as camadas e as sobreposições apontam para animações que existem', () => {
  for (const [id, e] of personagens) {
    for (const [nome, a] of Object.entries(e.animacoes)) {
      if (a.tampo) {
        assert.ok(e.animacoes[a.tampo], `${id} ${nome}: tampo ${a.tampo}`);
        assert.equal(e.animacoes[a.tampo].quadros, a.quadros, `${id} ${nome}: tampo com outro número de quadros`);
        assert.equal(e.animacoes[a.tampo].camada_de, nome, `${id} ${nome}: o tampo não volta para ela`);
      }
      if (a.camada_de) assert.ok(e.animacoes[a.camada_de], `${id} ${nome}: camada_de`);
      for (const campo of ['rosto', 'maos', 'envelope', 'dedo', 'desloca']) {
        if (a[campo]) assert.equal(a[campo].length, a.quadros, `${id} ${nome}: ${campo} por quadro`);
      }
    }
  }
});

test('os marcadores caem dentro da tela do personagem', () => {
  for (const [id, e] of personagens) {
    for (const [nome, a] of Object.entries(e.animacoes)) {
      for (const p of a.envelope ?? []) assert.ok(dentro(p, e.tela), `${id} ${nome}: envelope ${p}`);
      for (const p of a.dedo ?? []) assert.ok(dentro(p, e.tela), `${id} ${nome}: dedo ${p}`);
      for (const q of a.maos ?? []) for (const p of q) assert.ok(dentro(p, e.tela), `${id} ${nome}: mão ${p}`);
      if (a.flash) assert.ok(dentro(a.flash, e.tela), `${id} ${nome}: flash`);
      if (a.tela) {
        const [x0, y0, x1, y1] = a.tela;
        assert.ok(dentro([x0, y0], e.tela) && dentro([x1, y1], e.tela) && x0 <= x1 && y0 <= y1, `${id} ${nome}: tela`);
        const [sx, sy] = a.selo;
        assert.ok(sx >= x0 && sx <= x1 && sy >= y0 && sy <= y1, `${id} ${nome}: selo fora da tela`);
      }
      for (const campo of ['solta', 'flash_no_quadro']) {
        if (campo in a) assert.ok(a[campo] >= 0 && a[campo] < a.quadros, `${id} ${nome}: ${campo}`);
      }
    }
  }
});

test('os adereços e as camas que as animações citam existem no manifesto', () => {
  for (const [id, e] of personagens) {
    for (const [nome, a] of Object.entries(e.animacoes)) {
      if (a.no_lugar_do_teclado) {
        const t = MAN[a.no_lugar_do_teclado];
        assert.ok(t?.no_personagem && t.direcoes, `${id} ${nome}: ${a.no_lugar_do_teclado}`);
      }
      if (a.na_cama) assert.equal(MAN[a.na_cama]?.pasta, 'moveis', `${id} ${nome}: ${a.na_cama}`);
      if (a.envelope) assert.ok(MAN.envelope, `${id} ${nome}: envelope`);
      if (a.selo) assert.ok(MAN.selo_tablet?.estados?.length === 3, `${id} ${nome}: selos`);
    }
  }
  assert.ok(MAN.malote.estados.includes('com-envelope'));
  assert.ok(dentro(MAN.malote.abertura, tamanho('moveis/malote__vazio.png')));
});

test('todo arquivo de peça existe, pela regra de nomes do jogo', () => {
  for (const [modelo, e] of Object.entries(MAN)) {
    if (!e.pasta || e.folha) continue;
    const fs = arquivos(modelo, e);
    const tamanhos = new Set();
    for (const f of fs) {
      assert.ok(existsSync(new URL(f, ASSETS)), `${modelo}: falta ${f}`);
      tamanhos.add(tamanho(f).join('x'));
    }
    assert.equal(tamanhos.size, 1, `${modelo}: estados de tamanhos diferentes`);
    for (const [nome, a] of Object.entries(e.animacoes ?? {})) {
      const [W, H] = tamanho(a.folha);
      assert.deepEqual([W, H], [a.tela[0] * a.quadros, a.tela[1]], `${modelo} ${nome}`);
      assert.ok(a.toque >= 0 && a.toque < a.quadros, `${modelo} ${nome}: toque`);
    }
  }
});
