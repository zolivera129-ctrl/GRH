// O roteiro do JSON v0.3 traduzido para o motor: as 17 cenas existem, as
// variantes trocam as falas certas e nenhuma chave crua vai para a tela.
// Rodar com: npm test
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { comandosDaCena, CENAS, CENAS_DO_JSON, ANIMACAO, OBJETO, preencher, COMPLEMENTOS } from '../src/roteiro.js';

const JSON_ = JSON.parse(readFileSync(new URL('../dados/financyapp_roteiro_falas_v03.json', import.meta.url), 'utf8'));
const MAN = JSON.parse(readFileSync(new URL('../../pixel-art-habbo/assets/manifest.json', import.meta.url), 'utf8'));
const falas = (cmds) => (cmds ?? []).filter((c) => c.op === 'speak').map((c) => c.texto);
const base = { hora: 15, privado: false, primeira: true, escolhas: {} };

test('as 17 cenas do JSON estão no motor, e todas as animações e objetos têm tradução', () => {
  assert.deepEqual(JSON_.scenes.map((s) => s.sceneId).sort(), [...CENAS_DO_JSON].sort());
  for (const s of JSON_.scenes) {
    for (const c of [...s.script, ...s.conditionalVariants.flatMap((v) => v.script)]) {
      if (c.op === 'play') assert.ok(ANIMACAO[c.animation], `${s.sceneId}: animação ${c.animation}`);
      if (c.op === 'object') assert.ok(OBJETO[`${c.target}:${c.state}`], `${s.sceneId}: objeto ${c.target}:${c.state}`);
    }
  }
});

test('as animações que o motor pede existem no manifesto de quem faz', () => {
  const quem = { saldanha: 'saldanha', vivi: 'vivi', caio: 'caio', gabriel: 'gabriel', guilherme: 'guilherme' };
  for (const s of JSON_.scenes) {
    for (const c of s.script.filter((x) => x.op === 'play')) {
      for (const cmd of ANIMACAO[c.animation](c.actor.toLowerCase(), c.target)) {
        if (cmd.op === 'play') assert.ok(MAN[quem[cmd.actor]].animacoes[cmd.animation], `${cmd.actor}: ${cmd.animation}`);
      }
    }
  }
});

test('C1S1: as três falas do HTML original, na ordem, para todo usuário', () => {
  const cmds = CENAS.C1S1.montar(JSON_, base);
  assert.deepEqual(falas(cmds), [
    'Bem-vindo ao escritório. Pode entrar — sua mesa já está por aqui.',
    'Chegou na hora certa. Ainda tem café e ninguém perdeu a calculadora.',
    'Brincadeira. Aqui a gente prefere números conferidos — o Saldanha pode mostrar.',
  ]);
  assert.ok(cmds.filter((c) => c.op === 'speak').every((c) => c.actor === 'vivi'));
  assert.ok(!cmds.some((c) => c.op === 'choice'), 'sem escolha A/B/C para o jogador');
});

test('C1S2: plural certo e, sem histórico, a variante sem número', () => {
  assert.ok(falas(comandosDaCena(JSON_, 'c1s2', { ...base, meses_validos: 2 })).includes('Encontrei 2 períodos com informações conferíveis.'));
  assert.ok(falas(comandosDaCena(JSON_, 'c1s2', { ...base, meses_validos: 1 })).includes('Encontrei 1 período com informações conferíveis.'));
  const sem = falas(comandosDaCena(JSON_, 'c1s2', { ...base, meses_validos: 0 }));
  assert.equal(sem[0], 'Sou o Saldanha. Vou conferir o que está registrado. Só afirmo aquilo que consigo verificar.');
  assert.ok(sem[1].startsWith('Ainda não tenho informações suficientes'));
  assert.ok(!sem.some((f) => /\d/.test(f)), 'nenhum número inventado');
});

test('C1S4: na saída sem ação, não diz que houve atualização', () => {
  const sem = falas(comandosDaCena(JSON_, 'c1s4', { ...base, saida: true, acao: false }));
  assert.deepEqual(sem, ['Quando você registrar alguma coisa, o escritório vai refletir o que mudou.']);
  const com = falas(comandosDaCena(JSON_, 'c1s4', { ...base, acao: true, objeto: 'calendario' }));
  assert.ok(com.includes('Atualização confirmada. O meu livro já reflete a mudança.'));
});

test('C2S2: conciliado nunca fala em diferença; divergente pergunta; parcial diz parcial', () => {
  const ok = comandosDaCena(JSON_, 'c2s2', { ...base, conciliacao: 'conciliado' });
  assert.ok(!falas(ok).some((f) => f.toLowerCase().includes('diferença')));
  assert.ok(!ok.some((c) => c.op === 'choice'));
  const div = comandosDaCena(JSON_, 'c2s2', { ...base, conciliacao: 'divergente' });
  assert.ok(falas(div).includes('Encontrei uma diferença entre as fontes.'));
  assert.deepEqual(div.find((c) => c.op === 'choice').choices.map((c) => c.texto), ['Ver agora', 'Deixar para depois']);
  const parcial = falas(comandosDaCena(JSON_, 'c2s2', { ...base, conciliacao: 'sem_fontes' }));
  assert.ok(parcial.some((f) => f.includes('estado parcial')));
  assert.ok(!parcial.some((f) => f.includes('diferença')));
});

test('C2S1: o "boa tarde" segue a hora; sem lote, a cena não existe', () => {
  const manha = falas(comandosDaCena(JSON_, 'c2s1', { ...base, lote: 'x', hora: 9 }));
  assert.ok(manha.includes('Bom dia, equipe. Hoje tem envelope.'));
  assert.equal(comandosDaCena(JSON_, 'c2s1', { ...base, lote: null }), null);
});

test('C2S3: categorias do motor nos botões; sem ambiguidade, pula', () => {
  const t = { id: 't1', campos: { descricao_segura: 'Loja online', categoria_a: 'Compras', categoria_b: 'Casa' } };
  const cmds = comandosDaCena(JSON_, 'c2s3', { ...base, transacao: t, ...t.campos });
  assert.ok(falas(cmds).includes('Loja online entra em Compras ou Casa?'));
  assert.deepEqual(cmds.find((c) => c.op === 'choice').choices.map((c) => c.texto), ['Compras', 'Casa', 'Não sei / depois']);
  assert.equal(comandosDaCena(JSON_, 'c2s3', { ...base, transacao: null }), null);
});

test('C3S2: só com consulta pedida; sem veredito calculável, sem selo', () => {
  assert.equal(comandosDaCena(JSON_, 'c3s2', { ...base, voluntaria: false }), null);
  const ok = comandosDaCena(JSON_, 'c3s2', { ...base, voluntaria: true, veredito: 'amarelo', motivo_curto: 'A parcela passa de 15% da renda' });
  assert.ok(falas(ok).includes('Com isso, a orientação é: amarelo. A parcela passa de 15% da renda.'));
  assert.ok(ok.some((c) => c.op === 'selo'));
  const falta = comandosDaCena(JSON_, 'c3s2', { ...base, voluntaria: true, veredito: null });
  assert.ok(!falta.some((c) => c.op === 'selo'), 'sem selo verde/amarelo/vermelho');
  assert.ok(falas(falta).some((f) => f.startsWith('Ainda faltam dados')));
});

test('C3S3: sem teto, nenhum alerta', () => {
  assert.equal(comandosDaCena(JSON_, 'c3s3', { ...base, teto: null, limiar: 80 }), null);
  assert.ok(comandosDaCena(JSON_, 'c3s3', { ...base, teto: 400, limiar: 80 }).some((c) => c.op === 'choice'));
});

test('C3S4: só com retorno semanal; com zero, a variante sem novidade', () => {
  assert.equal(comandosDaCena(JSON_, 'c3s4', { ...base, resumoDisponivel: false }), null);
  assert.ok(falas(comandosDaCena(JSON_, 'c3s4', { ...base, resumoDisponivel: true, quantidade_eventos_validos: 3 }))
    .includes('Nesta semana, 3 registros mudaram de estado.'));
  const zero = falas(comandosDaCena(JSON_, 'c3s4', { ...base, resumoDisponivel: true, quantidade_eventos_validos: 0 }));
  assert.ok(zero.includes('Ainda não apareceu uma nova alteração confirmada desde sua última visita.'));
  assert.ok(!zero.some((f) => f.includes('{')));
});

test('M0: acentos repostos, nada mais mudado; não toca do dia 6 em diante', () => {
  const m0 = falas(comandosDaCena(JSON_, 'm0', { ...base, dia: 1 }));
  assert.deepEqual(m0, ['Começamos a preparação do fechamento do período anterior. Nossa reunião é no dia 6.']);
  assert.equal(Object.keys(COMPLEMENTOS.acentos).length, 1);
  assert.equal(comandosDaCena(JSON_, 'm0', { ...base, dia: 6 }), null);
});

test('C4S1: no dia 6, falas e os dois botões; vencida, só a fala da variante', () => {
  const convite = comandosDaCena(JSON_, 'c4s1', { ...base, competencia: '2026-09', convite: true });
  assert.equal(falas(convite).length, 4);
  assert.deepEqual(convite.find((c) => c.op === 'choice').choices.map((c) => c.texto), ['Entrar na reunião', 'Na próxima visita']);
  const vencida = comandosDaCena(JSON_, 'c4s1', { ...base, competencia: '2026-09', convite: false });
  assert.deepEqual(falas(vencida), ['Temos uma reunião mensal pendente. Vamos começar pelo que está registrado.']);
  assert.ok(!vencida.some((c) => c.op === 'choice'), 'sem novo adiamento');
});

test('reunião: base parcial avisa logo depois da abertura e nunca põe o selo FECHADO', () => {
  const ctx = { ...base, competencia: '2026-09', motivo: 'vencida', situacao: 'parcial' };
  const cmds = CENAS.REUNIAO.montar(JSON_, ctx);
  const f = falas(cmds);
  const i = f.indexOf('Antes de comparar os meses, vou separar o que está confirmado do que está pendente.');
  assert.ok(f[i + 1].startsWith('Há informações que ainda não permitem comparação'));
  assert.ok(!cmds.some((c) => c.op === 'object' && c.state === 'fechado'));
  const completa = CENAS.REUNIAO.montar(JSON_, { ...ctx, situacao: 'completa' });
  assert.ok(completa.some((c) => c.op === 'object' && c.target === 'tela' && c.state === 'fechado'));
  assert.ok(!falas(completa).some((f2) => f2.startsWith('Há informações')));
});

test('reunião: a fala "nossa primeira reunião" só na primeira', () => {
  const ctx = { ...base, competencia: '2026-10', motivo: 'aceita', situacao: 'completa' };
  assert.ok(falas(CENAS.REUNIAO.montar(JSON_, ctx)).some((f) => f.startsWith('Nossa primeira reunião')));
  assert.ok(!falas(CENAS.REUNIAO.montar(JSON_, { ...ctx, primeira: false })).some((f) => f.startsWith('Nossa primeira reunião')));
});

test('nenhuma cena deixa chave crua: sem valor, a fala sai', () => {
  assert.equal(preencher('Encontrei {meses_validos} período(s).', {}), null);
  for (const id of CENAS_DO_JSON) {
    const cmds = comandosDaCena(JSON_, id, { ...base, convite: true, competencia: '2026-09', meses_validos: 2, lote: 'l',
      conciliacao: 'conciliado', voluntaria: true, veredito: 'verde', motivo_curto: 'cabe', teto: 400, limiar: 80,
      resumoDisponivel: true, quantidade_eventos_validos: 2, dia: 2, situacao: 'completa',
      transacao: { id: 't' }, descricao_segura: 'X', categoria_a: 'A', categoria_b: 'B' }) ?? [];
    for (const c of cmds) {
      if (c.op === 'speak') assert.ok(!/[{}]/.test(c.texto), `${id}: ${c.texto}`);
    }
  }
});
