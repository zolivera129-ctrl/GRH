// O ciclo mensal e o diretor narrativo contra os exemplos de aceitação da
// direção narrativa v0.2 (§3.1 e §8). Rodar com: npm test
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  primeiraReuniao, situacaoDaReuniao, situacaoDoPreAviso, competenciaDaReuniao, vencimentosAte, podeAdiar,
} from '../src/calendario.js';
import { perfilNovo } from '../src/estado.js';
import {
  abrirVisita, registrarInicio, registrarConclusao, registrarEvento, planejarEvento, eventosNaoProcessados,
  PRIORIDADE, LIMITE_SEM_CONDENSAR,
} from '../src/diretor.js';

// uma visita completa: abre, "assiste" a tudo o que bloqueia e conclui
function visitar(perfil, hoje, { adiar = false, regraDia6 = null, eventos = [] } = {}) {
  let { perfil: p, fila } = abrirVisita(perfil, hoje, { regraDia6, eventosPendentes: eventos });
  const vistas = [];
  for (const inv of fila) {
    vistas.push(inv);
    p = registrarInicio(p, inv, `${hoje}T10:00`);
    if (inv.cena === 'C4S1' && adiar) {
      p = registrarConclusao(p, inv, `${hoje}T10:00`, { adiada: true });
      continue;
    }
    if (inv.cena === 'C4S1') {
      // aceitou: a reunião entra na hora
      p = registrarConclusao(p, inv, `${hoje}T10:00`);
      const r = { ...inv, cena: 'REUNIAO', chave: `monthly_meeting:${p.perfil}:${inv.contexto.competencia}` };
      vistas.push(r);
      p = registrarInicio(p, r, `${hoje}T10:01`);
      p = registrarConclusao(p, r, `${hoje}T10:30`, { fechamento: 'pendente' });
      continue;
    }
    p = registrarConclusao(p, inv, `${hoje}T10:05`);
  }
  return { perfil: p, vistas, cenas: vistas.map((v) => v.cena) };
}

test('primeira reunião: dia 1 a 5 vence no mesmo mês; 7 em diante, no seguinte', () => {
  for (const d of ['01', '03', '05']) assert.equal(primeiraReuniao(`2026-10-${d}`).vencimento, '2026-10-06');
  for (const d of ['07', '09', '31']) assert.equal(primeiraReuniao(`2026-10-${d}`).vencimento, '2026-11-06');
  assert.equal(primeiraReuniao('2026-12-20').vencimento, '2027-01-06');
});

test('primeiro acesso exatamente no dia 6 fica pendente: nenhuma regra assumida', () => {
  const r = primeiraReuniao('2026-10-06');
  assert.equal(r.vencimento, undefined);
  assert.equal(r.pendente, 'primeiro-acesso-no-dia-6');
  // Vivi continua sendo a primeira cena, e nada de reunião
  const v = visitar(perfilNovo(), '2026-10-06');
  assert.equal(v.cenas[0], 'C1S1');
  assert.ok(!v.cenas.includes('C4S1') && !v.cenas.includes('REUNIAO'));
  assert.equal(v.perfil.primeira_reuniao, 'pendente');
  // e continua sem reunião dias depois
  const depois = visitar(v.perfil, '2026-10-20');
  assert.ok(!depois.cenas.includes('REUNIAO'));
});

test('competência é o mês anterior ao dia 6', () => {
  assert.equal(competenciaDaReuniao('2026-10-06'), '2026-09');
  assert.equal(competenciaDaReuniao('2027-01-06'), '2026-12');
  assert.deepEqual(vencimentosAte('2026-10-06', '2026-12-05'), ['2026-10-06', '2026-11-06']);
});

test('aceite: primeiro acesso em 3/out e volta em 17/out abre a reunião de 6/out direto', () => {
  const v1 = visitar(perfilNovo(), '2026-10-03');
  assert.equal(v1.cenas[0], 'C1S1');
  assert.equal(v1.perfil.primeira_reuniao, '2026-10-06');
  const { perfil, fila } = abrirVisita(v1.perfil, '2026-10-17');
  assert.equal(fila[0].cena, 'REUNIAO');
  assert.equal(fila[0].obrigatoria, true);
  assert.equal(fila[0].contexto.competencia, '2026-09');
  assert.equal(fila[0].contexto.semConvite, true);
  assert.ok(!fila.some((i) => i.cena === 'C4S1'), 'sem convite adiável');
  assert.equal(podeAdiar(perfil, '2026-10-17'), false);
});

test('aceite: primeiro acesso em 9/out não convoca; a primeira vence em 6/nov', () => {
  const v1 = visitar(perfilNovo(), '2026-10-09');
  assert.equal(v1.perfil.primeira_reuniao, '2026-11-06');
  assert.ok(!v1.cenas.includes('REUNIAO') && !v1.cenas.includes('C4S1'));
  const v2 = visitar(v1.perfil, '2026-10-30');
  assert.ok(!v2.cenas.includes('REUNIAO'), 'nenhuma reunião antiga');
  const s = situacaoDaReuniao(v2.perfil, '2026-11-06');
  assert.equal(s.tipo, 'convite');
  assert.equal(s.competencia, '2026-10');
});

test('aceite: primeiro acesso em 5/out, volta em 6/out: convite adiável uma vez', () => {
  const v1 = visitar(perfilNovo(), '2026-10-05');
  const { fila } = abrirVisita(v1.perfil, '2026-10-06');
  const convite = fila.find((i) => i.cena === 'C4S1');
  assert.ok(convite);
  assert.equal(convite.prioridade, PRIORIDADE.CONVITE);
  // adia
  const v2 = visitar(v1.perfil, '2026-10-06', { adiar: true });
  assert.equal(v2.perfil.reunioes['2026-09'].adiada_em, '2026-10-06T10:00');
  assert.ok(!v2.perfil.reunioes['2026-09'].concluida_em);
  // volta no mesmo dia: obrigatória, sem segundo adiamento
  const mesmoDia = abrirVisita(v2.perfil, '2026-10-06');
  assert.equal(mesmoDia.fila[0].cena, 'REUNIAO');
  assert.equal(mesmoDia.fila[0].contexto.motivo, 'adiada');
  assert.ok(!mesmoDia.fila.some((i) => i.cena === 'C4S1'));
  // volta no dia 8: obrigatória
  const dia8 = abrirVisita(v2.perfil, '2026-10-08');
  assert.equal(dia8.fila[0].cena, 'REUNIAO');
  assert.equal(dia8.fila[0].prioridade, PRIORIDADE.REUNIAO_ADIADA);
});

test('aceite: sem adiar e sem concluir no dia 6, depois do dia 6 é obrigatória', () => {
  const v1 = visitar(perfilNovo(), '2026-10-05');
  // viu o convite e fechou o app sem escolher
  let { perfil, fila } = abrirVisita(v1.perfil, '2026-10-06');
  perfil = registrarInicio(perfil, fila.find((i) => i.cena === 'C4S1'), '2026-10-06T09:00');
  assert.equal(situacaoDaReuniao(perfil, '2026-10-06').tipo, 'convite', 'mesmo dia: convite de novo');
  const s = situacaoDaReuniao(perfil, '2026-10-08');
  assert.equal(s.tipo, 'obrigatoria');
  assert.equal(s.semConvite, false);
});

test('reunião concluída não volta; a próxima só no dia 6 seguinte', () => {
  const v1 = visitar(perfilNovo(), '2026-10-03');
  const v2 = visitar(v1.perfil, '2026-10-17');
  assert.ok(v2.cenas.includes('REUNIAO'));
  assert.ok(v2.perfil.reunioes['2026-09'].concluida_em);
  assert.equal(v2.perfil.reunioes['2026-09'].fechamento, 'pendente', 'reunião feita não fecha o mês sozinha');
  const v3 = visitar(v2.perfil, '2026-10-20');
  assert.ok(!v3.cenas.includes('REUNIAO'));
  assert.equal(situacaoDaReuniao(v3.perfil, '2026-11-06').tipo, 'convite');
});

test('recarregar no meio da reunião recomeça a mesma reunião, sem duplicar', () => {
  const v1 = visitar(perfilNovo(), '2026-10-03');
  let { perfil, fila } = abrirVisita(v1.perfil, '2026-10-17');
  perfil = registrarInicio(perfil, fila[0], '2026-10-17T10:00');
  const de_novo = abrirVisita(perfil, '2026-10-17');
  const reunioes = de_novo.fila.filter((i) => i.cena === 'REUNIAO');
  assert.equal(reunioes.length, 1);
  assert.equal(reunioes[0].contexto.motivo, 'retomada');
});

test('reuniões acumuladas: a mais antiga primeiro, uma por competência', () => {
  const v1 = visitar(perfilNovo(), '2026-10-03');
  const { fila } = abrirVisita(v1.perfil, '2026-12-10');
  const r = fila.find((i) => i.cena === 'REUNIAO');
  assert.equal(r.contexto.competencia, '2026-09');
  assert.equal(r.contexto.acumuladas, 3);
});

test('M0: dia 1º mostra o pré-aviso; dia 1º sem visita não marca como mostrado', () => {
  const v1 = visitar(perfilNovo(), '2026-10-09');      // primeira reunião em 6/nov
  // dia 1º de novembro com visita
  const d1 = abrirVisita(v1.perfil, '2026-11-01');
  const m0 = d1.fila.find((i) => i.cena === 'M0');
  assert.ok(m0);
  assert.equal(m0.contexto.competencia, '2026-10');
  assert.equal(m0.contexto.tardio, false);
  assert.equal(m0.bloqueia, false, 'não toma a tela');
  // sem visita no dia 1º: entrega tardia legítima no dia 3
  const d3 = abrirVisita(v1.perfil, '2026-11-03');
  assert.equal(d3.fila.find((i) => i.cena === 'M0').contexto.tardio, true);
  assert.equal(situacaoDoPreAviso(v1.perfil, '2026-11-03').tipo, 'tardio');
  // depois de mostrado, não repete
  const visto = visitar(v1.perfil, '2026-11-01');
  assert.ok(visto.perfil.avisos['2026-10'].mostrado_em);
  assert.ok(!abrirVisita(visto.perfil, '2026-11-04').fila.some((i) => i.cena === 'M0'));
});

test('M0: só volta no dia 6 ou depois: reconhece que não houve pré-aviso, sem fingir', () => {
  const v1 = visitar(perfilNovo(), '2026-10-09');
  const d6 = abrirVisita(v1.perfil, '2026-11-06');
  assert.ok(!d6.fila.some((i) => i.cena === 'M0'));
  assert.equal(d6.perfil.avisos['2026-10'].mostrado_em, undefined, 'shown continua falso');
  assert.equal(d6.perfil.avisos['2026-10'].nao_entregue_em, '2026-11-06');
  const convite = d6.fila.find((i) => i.cena === 'C4S1');
  assert.equal(convite.contexto.semPreAviso, true);
});

test('M0 não antecipa a reunião para o dia 1º', () => {
  const v1 = visitar(perfilNovo(), '2026-10-09');
  const d1 = abrirVisita(v1.perfil, '2026-11-01');
  assert.ok(!d1.fila.some((i) => i.cena === 'REUNIAO' || i.cena === 'C4S1'));
});

test('primeiro acesso entre o dia 1 e o 5: Vivi primeiro, depois o pré-aviso', () => {
  const { fila } = abrirVisita(perfilNovo(), '2026-11-02');
  assert.equal(fila[0].cena, 'C1S1');
  assert.ok(fila.some((i) => i.cena === 'M0'));
});

test('C1S1 uma vez por perfil; recarregar antes de concluir repete', () => {
  let { perfil, fila } = abrirVisita(perfilNovo(), '2026-10-22');
  assert.equal(fila[0].cena, 'C1S1');
  perfil = registrarInicio(perfil, fila[0], 'x');
  assert.equal(abrirVisita(perfil, '2026-10-22').fila[0].cena, 'C1S1');
  perfil = registrarConclusao(perfil, fila[0], 'y');
  assert.ok(!abrirVisita(perfil, '2026-10-22').fila.some((i) => i.cena === 'C1S1'));
  assert.ok(!abrirVisita(perfil, '2026-10-30').fila.some((i) => i.cena === 'C1S1'));
});

test('consulta ao Caio só com pergunta voluntária; teto só com teto', () => {
  const p = perfilNovo();
  assert.deepEqual(planejarEvento(p, { id: 'e1', type: 'purchase_consult_requested', payload: { voluntaria: false } }), []);
  assert.equal(planejarEvento(p, { id: 'e2', type: 'purchase_consult_requested', payload: { voluntaria: true } })[0].cena, 'C3S2');
  assert.deepEqual(planejarEvento(p, { id: 'e3', type: 'budget_threshold_crossed',
    payload: { categoria: 'Lazer', limiar: 80, teto: null, competencia: '2026-10' } }), []);
  assert.equal(planejarEvento(p, { id: 'e4', type: 'budget_threshold_crossed',
    payload: { categoria: 'Delivery', limiar: 100, teto: 400, competencia: '2026-10' } })[0].chave,
  'budget_alert:guilherme:2026-10:Delivery:100');
});

test('primeira ação da primeira visita é C1S4; depois, C3S1', () => {
  const p = perfilNovo();
  const ev = { id: 'pg1', type: 'payment_confirmed', payload: {} };
  assert.equal(planejarEvento(p, ev, { primeiraVisita: true, houveAcao: false })[0].cena, 'C1S4');
  assert.equal(planejarEvento(p, ev, { primeiraVisita: true, houveAcao: true })[0].cena, 'C3S1');
  assert.equal(planejarEvento(p, ev, { primeiraVisita: false })[0].cena, 'C3S1');
});

test('semana sem visita: eventos acumulados não viram cascata; ficam no resumo do quadro', () => {
  let p = visitar(perfilNovo(), '2026-10-09').perfil;
  for (let i = 0; i < 8; i++) {
    p = registrarEvento(p, { id: `pg${i}`, type: 'payment_confirmed', payload: { conta: `Conta ${i}` } }, '2026-10-12');
  }
  assert.equal(eventosNaoProcessados(p).length, 8);
  const { perfil, fila, notas } = abrirVisita(p, '2026-10-18');
  assert.ok(!fila.some((i) => i.cena === 'C3S1'), 'sem cascata de 8 falas');
  assert.equal(perfil.resumo_disponivel, '2026-10-18');
  assert.equal(eventosNaoProcessados(perfil).length, 0, 'cada evento no seu registro, processado uma vez');
  assert.ok(Object.values(perfil.eventos).every((e) => e.condensado));
  assert.ok(notas.some((n) => n.includes('8 eventos')));
  assert.ok(LIMITE_SEM_CONDENSAR < 8);
});

test('retorno numa semana nova deixa o resumo disponível; mesma semana não', () => {
  const v1 = visitar(perfilNovo(), '2026-10-12');          // segunda-feira
  assert.equal(abrirVisita(v1.perfil, '2026-10-16').perfil.resumo_disponivel, null);
  assert.equal(abrirVisita(v1.perfil, '2026-10-20').perfil.resumo_disponivel, '2026-10-20');
});

test('a leitura dos dados acontece depois do primeiro acesso registrado', () => {
  const lerDados = (p) => [{ id: 'historico:leitura', type: 'historical_data_ready', occurredAt: p.primeiro_acesso,
    payload: { meses_validos: 2 } }];
  const { perfil, fila } = abrirVisita(perfilNovo(), '2026-10-22', { lerDados });
  assert.equal(perfil.eventos['historico:leitura'].recebido_em, '2026-10-22');
  assert.deepEqual(fila.map((i) => i.cena), ['C1S1', 'C1S2']);
});

test('o mesmo lote não encena duas vezes', () => {
  let p = perfilNovo();
  const ev = { id: 'lote-1', type: 'card_batch_imported', payload: { lote: 'nubank-2026-10' } };
  const [inv] = planejarEvento(p, ev);
  assert.equal(inv.chave, 'card_arrival:guilherme:nubank-2026-10');
  p = registrarConclusao(registrarInicio(p, inv, 'a'), inv, 'b');
  assert.equal(abrirVisita(p, '2026-10-22', { eventosPendentes: [ev] }).fila.filter((i) => i.cena === 'C2').length, 0);
});
