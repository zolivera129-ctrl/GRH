// O histórico narrativo do perfil (direção narrativa v0.2, §2.8 e §5):
// pertence ao perfil e à competência, sobrevive a recarregar a página e
// guarda o que foi visto, o que ficou pendente e o que foi concluído.
//
// Enquanto não há servidor, o estado fica no armazenamento do navegador. Se
// ele não estiver disponível (aba privada, prévia), o jogo segue em memória.
// Os nomes dos campos seguem a "implementação mínima" do §3.1.

export const VERSAO = 1;

export function perfilNovo(id = 'guilherme') {
  return {
    versao: VERSAO,
    perfil: id,
    primeiro_acesso: null,      // first_access_at (dia civil em São Paulo)
    primeira_reuniao: null,     // first_meeting_due_date, ou 'pendente'
    reunioes: {},               // por competência: vencimento, convite_mostrado_em,
                                // adiada_em, iniciada_em, concluida_em, fechamento,
                                // observacao, sem_pre_aviso
    avisos: {},                 // M0 por competência: mostrado_em, nao_entregue_em
    cenas: {},                  // por chave de unicidade: cena, vista_em, concluida_em,
                                // pendente, evento, versao
    eventos: {},                // cada evento de domínio no seu registro
    categorias: {},             // respostas da pergunta de categoria, por transação
    lotes: {},                  // estado do envelope de cada lote: recebido/conferido/sinalizado/parcial
    visitas: [],
    resumo_disponivel: null,   // dia em que o resumo do quadro ficou disponível (C3S4)
    resumo_visto_em: null,
  };
}

export function clonar(perfil) {
  return JSON.parse(JSON.stringify(perfil));
}

/** Um armazém em memória com a mesma cara do localStorage. */
export function armazemEmMemoria() {
  const m = new Map();
  return {
    getItem: (k) => (m.has(k) ? m.get(k) : null),
    setItem: (k, v) => m.set(k, String(v)),
    removeItem: (k) => m.delete(k),
  };
}

/** O localStorage, se der; senão a memória. */
export function armazemDoNavegador() {
  try {
    const ls = globalThis.localStorage;
    const k = '__financyapp_teste__';
    ls.setItem(k, '1');
    ls.removeItem(k);
    return { armazem: ls, persistente: true };
  } catch {
    return { armazem: armazemEmMemoria(), persistente: false };
  }
}

const chaveDoPerfil = (id) => `financyapp:perfil:${id}`;

export function carregarPerfil(armazem, id = 'guilherme') {
  try {
    const bruto = armazem.getItem(chaveDoPerfil(id));
    if (!bruto) return perfilNovo(id);
    const p = JSON.parse(bruto);
    if (p.versao !== VERSAO) return perfilNovo(id);
    return { ...perfilNovo(id), ...p };
  } catch {
    return perfilNovo(id);
  }
}

export function salvarPerfil(armazem, perfil) {
  try {
    armazem.setItem(chaveDoPerfil(perfil.perfil), JSON.stringify(perfil));
    return true;
  } catch {
    return false;
  }
}

export function apagarPerfil(armazem, id = 'guilherme') {
  try { armazem.removeItem(chaveDoPerfil(id)); } catch { /* segue */ }
}

// carimbo simulado: o dia civil e a hora de São Paulo
export const carimbo = (relogio) => `${relogio.data}T${String(relogio.hora).padStart(2, '0')}:00`;
