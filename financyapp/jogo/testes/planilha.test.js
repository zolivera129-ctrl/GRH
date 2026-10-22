// O leitor da planilha com uma planilha de mentira no mesmo formato
// (os valores reais nunca entram no repositório). Rodar com: npm test
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { numero, lerMes, partesDoCartao, conferencia, semCategoria, relatorioDoMes, lerConfig,
  eventosDaLeitura, leitorConfere, competenciaDaAba } from '../src/planilha.js';

const CAB = ['', 'Histórico', 'Categoria', 'Valor', 'Parcelas', 'Responsável', 'Conferido (Gabriel)', '',
  'Histórico', 'Data', 'Crédito', 'Débito', 'Pago', 'Histórico', 'Data', 'Crédito', 'Responsável'];
function aba({ cartao = [], conta = [], digio = [], resumoGui = null }) {
  const n = Math.max(cartao.length, conta.length, digio.length);
  const linhas = [['Controle de Gastos 2026'], [], [],
    ['', '', '', 'Guilherme', resumoGui ?? ''], CAB];
  for (let i = 0; i < n; i++) {
    const l = new Array(17).fill('');
    if (cartao[i]) [l[1], l[2], l[3], l[4], l[5], l[6]] = cartao[i];
    if (conta[i]) [l[8], l[9], l[10], l[11], l[12]] = conta[i];
    if (digio[i]) [l[13], l[14], l[15], l[16]] = digio[i];
    linhas.push(l);
  }
  return linhas;
}
const MES = aba({
  cartao: [
    ['LOJA A', '🛍️ COMPRAS', ' R$  100,00 ', '', 'Guilherme', 'TRUE'],
    ['LOJA B', '🛒 MERCADO', ' R$  80,00 ', '', '2 X', 'TRUE'],
    ['LOJA C', '🛍️ COMPRAS', ' R$  50,00 ', '', 'Gabriel', ''],
    ['LOJA A', '', ' R$  30,00 ', '', 'Guilherme', 'TRUE'],
    ['TAXA', '🏠 MORADIA', ' R$  12,00 ', '', '', 'TRUE'],
    ['ESTORNO', '🏠 MORADIA', ' R$  (20,00)', '', 'Guilherme', 'TRUE'],
  ],
  conta: [
    ['SALÁRIO', '', ' R$  1.000,00 ', ' R$  -   ', 'TRUE'],
    ['CARTÃO NUBANK', '11/10/2026', ' R$  -   ', ' R$  150,00 ', 'TRUE'],
    ['CARTÃO DIGIO', '25/10/2026', ' R$  -   ', ' R$  9,90 ', 'FALSE'],
    ['LUZ', '20/10/2026', ' R$  -   ', ' R$  120,00 ', 'FALSE'],
  ],
  digio: [['ASSINATURA', '', ' R$  9,90 ', ' GUILHERME ']],
  resumoGui: '150,00',
});

test('números como o Sheets devolve: moeda, traço, parênteses e vazio', () => {
  assert.equal(numero(' R$  5.612,09 '), 5612.09);
  assert.equal(numero('  -   '), 0);
  assert.equal(numero(' R$  (835,00)'), -835);
  assert.equal(numero(''), null);
  assert.equal(competenciaDaAba('Novembro', 2026), '2026-11');
});

test('regras da Config: parte do Guilherme = os dele + metade do 2 X; vazio fica fora', () => {
  const m = lerMes(MES, 'Outubro', 2026);
  assert.equal(m.cartao.length, 6);
  const p = partesDoCartao(m.cartao);
  assert.equal(p.guilherme, 100 + 30 - 20 + 40);
  assert.equal(p.fora, 12);
  assert.equal(leitorConfere(m), true);
});

test('conferência: CARTÃO NUBANK e DIGIO batem; mudando um centavo, diverge', () => {
  assert.equal(conferencia(lerMes(MES, 'Outubro', 2026)).estado, 'conciliado');
  const errado = MES.map((l) => (l[8] === 'CARTÃO NUBANK' ? Object.assign([...l], { 11: ' R$  151,00 ' }) : l));
  const c = conferencia(lerMes(errado, 'Outubro', 2026));
  assert.equal(c.estado, 'divergente');
  assert.equal(c.diferenca, 1);
  const semLinha = MES.filter((l) => l[8] !== 'CARTÃO NUBANK');
  assert.equal(conferencia(lerMes(semLinha, 'Outubro', 2026)).estado, 'sem_fontes');
});

test('gasto sem categoria: opções do próprio histórico; Gabriel fica de fora', () => {
  const [t] = semCategoria(lerMes(MES, 'Outubro', 2026));
  assert.deepEqual(t.campos, { descricao_segura: 'LOJA A', categoria_a: 'COMPRAS', categoria_b: 'MERCADO' });
});

test('relatório: conta sem Pago deixa o mês parcial, sem resultado inventado', () => {
  const r = relatorioDoMes(lerMes(MES, 'Outubro', 2026), lerConfig([['Saldo da reserva', ' R$  315,00 ']]), '2026-10');
  assert.equal(r.situacao, 'parcial');
  assert.equal(r.resultado, null);
  assert.equal(r.entradas, 1000);
  assert.deepEqual(r.compromissos.map((c) => c.item), ['CARTÃO DIGIO', 'LUZ']);
  assert.equal(r.reserva, 315);
  assert.equal(relatorioDoMes(null, null, '2026-09').situacao, 'sem_dados');
});

test('eventos: a primeira leitura é histórico; depois, Pago marcado vira pagamento, uma vez só', () => {
  const ler = (v) => ({ meses: [lerMes(v, 'Outubro', 2026)], config: {} });
  const r1 = eventosDaLeitura(ler(MES), null, { hoje: '2026-10-22' });
  assert.deepEqual(r1.eventos.map((e) => e.type), ['card_batch_imported']);
  assert.equal(r1.eventos[0].payload.historico, true);
  const pago = MES.map((l) => (l[8] === 'LUZ' ? Object.assign([...l], { 12: 'TRUE' }) : l));
  const r2 = eventosDaLeitura(ler(pago), r1.instantaneo, { hoje: '2026-10-23' });
  assert.deepEqual(r2.eventos.map((e) => [e.type, e.payload.conta]), [['payment_confirmed', 'LUZ']]);
  const r3 = eventosDaLeitura(ler(pago), r2.instantaneo, { hoje: '2026-10-24' });
  assert.equal(r3.eventos.length, 0);
  // desmarcar e marcar de novo: mesmo id (o registro de eventos não duplica)
  const r4 = eventosDaLeitura(ler(MES), r3.instantaneo, { hoje: '2026-10-25' });
  const r5 = eventosDaLeitura(ler(pago), r4.instantaneo, { hoje: '2026-10-26' });
  assert.equal(r5.eventos[0].id, r2.eventos[0].id);
  // um gasto novo no cartão muda o lote
  const novo = [...MES, Object.assign(new Array(17).fill(''), { 1: 'LOJA D', 2: '🛍️ COMPRAS', 3: ' R$  5,00 ', 5: 'Gabriel' })];
  const r6 = eventosDaLeitura(ler(novo), r5.instantaneo, { hoje: '2026-10-27' });
  assert.ok(r6.eventos.some((e) => e.type === 'card_batch_imported' && !e.payload.historico));
});
