// Falas de estado do Saldanha: só contagens e estados, nunca valor em reais.
import test from 'node:test';
import assert from 'node:assert/strict';
import { falasDoSaldanha, falaDoQuadro } from '../src/falas.js';

const mes = (pago) => ({
  aba: 'Outubro', competencia: '2026-10', legivel: true,
  cartao: [{ historico: 'A', valor: 40, responsavel: 'Guilherme' }],
  digio: [],
  conta: [
    { historico: 'CARTÃO NUBANK', debito: 40, credito: 0, pago },
    { historico: 'ALUGUEL', debito: 500, credito: 0, pago: false },
  ],
});
const fonte = (m) => ({ nome: 'planilha', estado: 'lida', meses: [m], lidaEm: null });

test('o Saldanha diz o estado da fatura e as contas sem Pago, sem valores', () => {
  const f = falasDoSaldanha(fonte(mes(true)), { categorias: {} }, '2026-10-20');
  assert.equal(f.length, 2);
  assert.match(f[0], /fatura de outubro confere/);
  assert.match(f[1], /1 conta de outubro ainda sem Pago/);
  assert.ok(f.every((t) => !/R\$|\d+,\d{2}/.test(t)));
});

test('sem leitura, ele diz que não leu; com dados sintéticos, fala genérica', () => {
  assert.match(falasDoSaldanha({ nome: 'planilha', estado: 'erro', meses: [] }, { categorias: {} }, '2026-10-20')[0], /não consegui ler/);
  assert.match(falasDoSaldanha({ nome: 'sintetico' }, { categorias: { x: { categoria: null } } }, '2026-10-20')[0], /uma despesa espera categoria/);
});

test('a fala do quadro segue a situação do relatório', () => {
  assert.match(falaDoQuadro({ competencia: '2026-09', situacao: 'sem_dados' }), /não tem a aba de setembro/);
  assert.match(falaDoQuadro({ competencia: '2026-10', situacao: 'completa' }), /^Outubro está conferido/);
  assert.match(falaDoQuadro({ competencia: '2026-10', situacao: 'parcial', faltando: ['2 contas sem Pago'] }), /Em outubro, 2 contas sem Pago/);
});
