// A fonte de dados real: a planilha "Escritório de Finanças", lida pelo
// conector Google Sheets do claude.ai com o login de quem abre o jogo (a
// página nunca vê token). Só lê: nada é escrito na planilha.
//
// Tem a mesma cara do módulo sintético (dados.js) para o resto do jogo:
// historico, relatorio, situacaoDe e eventosDeAbertura. As contas saem de
// planilha.js; aqui fica só a leitura e o estado dela.

import {
  lerMes, lerConfig, relatorioDoMes, conferencia, eventosDaLeitura, anoDaAba, competenciaDaAba,
  abaDaCompetencia, leitorConfere,
} from './planilha.js';

export const PLANILHA_ID = '1c46Q28p-T75jL5YNMtMAco1ZXog1D8RMA1omOg-CxIU';
export const SERVIDOR = 'Google Sheets';

// o que cada código de erro do conector pede de quem está vendo
const COMO_RESOLVER = {
  needs_reauth: 'O login do Google Sheets expirou. Reconecte em claude.ai, Configurações, Conectores.',
  server_not_connected: 'O Google Sheets não está conectado nesta conta. Adicione em claude.ai, Configurações, Conectores.',
  selection_required: 'Há mais de um conector do Google Sheets: escolha qual usar no aviso do claude.ai.',
  not_in_manifest: 'A leitura da planilha não foi permitida para esta página. Libere no menu de permissões do artifact.',
  approval_required: 'A leitura da planilha precisa da sua aprovação. Use "Ler a planilha agora" e aprove.',
  blocked_by_policy: 'A organização bloqueou o Google Sheets para esta página.',
  server_unavailable: 'O Google Sheets não respondeu. Tente de novo em alguns segundos.',
  tool_error: 'O Google Sheets recusou a leitura (a planilha mudou de nome ou de permissão?).',
  sem_conector: 'Esta visualização não tem acesso a conectores: abra o jogo no claude.ai.',
};

export function criarFontePlanilha() {
  const f = {
    nome: 'planilha', base: 'planilha', privado: false,
    estado: 'nao_lida',   // nao_lida | lendo | lida | erro
    erro: null, lidaEm: null, meses: [], config: null, abas: [],
  };

  async function valores(mcp, range) {
    const r = await mcp.callTool(SERVIDOR, 'get_values', { spreadsheetId: PLANILHA_ID, range }, { cache: false });
    return r.payload?.values ?? [];
  }

  /** Lê as abas de mês e a Config. Resolve true se leu. */
  f.ler = async (mcp, hoje) => {
    if (!mcp) {
      f.estado = 'erro';
      f.erro = { code: 'sem_conector', texto: COMO_RESOLVER.sem_conector };
      return false;
    }
    f.estado = 'lendo';
    try {
      const info = await mcp.callTool(SERVIDOR, 'get_spreadsheet',
        { spreadsheetId: PLANILHA_ID, fields: ['sheets.properties.title'] }, { cache: false });
      const titulos = (info.payload?.sheets ?? []).map((s) => s.properties?.title).filter(Boolean);
      const abasMes = titulos.filter((t) => competenciaDaAba(t, 2000));
      const lidas = await Promise.all([...abasMes.map((t) => valores(mcp, `${t}!A1:Q600`)),
        titulos.includes('Config') ? valores(mcp, 'Config!A1:F80') : Promise.resolve([])]);
      const config = lidas.pop();
      const anoPadrao = Number(hoje.slice(0, 4));
      f.meses = abasMes.map((t, i) => lerMes(lidas[i], t, anoDaAba(lidas[i], anoPadrao)));
      f.config = lerConfig(config);
      f.abas = f.meses.map((m) => ({ aba: m.aba, competencia: m.competencia, legivel: m.legivel,
        conferencia: conferencia(m).estado, leitorConfere: leitorConfere(m), linhas: m.cartao.length + m.conta.length }));
      f.estado = 'lida';
      f.erro = null;
      f.lidaEm = new Date();
      return true;
    } catch (e) {
      f.estado = 'erro';
      const code = e?.code ?? 'upstream_error';
      f.erro = { code, texto: COMO_RESOLVER[code] ?? `A leitura falhou (${code}).`, retryable: Boolean(e?.retryable) };
      return false;
    }
  };

  const mesDa = (comp) => f.meses.find((m) => m.competencia === comp);

  /** Os meses que já existiam antes do primeiro acesso, com o estado de cada um. */
  f.historico = (primeiroAcesso) => {
    if (!primeiroAcesso || f.estado !== 'lida') return [];
    const mesDoAcesso = primeiroAcesso.slice(0, 7);
    return f.meses.filter((m) => m.competencia && m.competencia < mesDoAcesso).map((m) => {
      const r = relatorioDoMes(m, f.config, m.competencia);
      return { competencia: m.competencia, conferido: r.situacao === 'completa', falta: r.faltando.join(', ') };
    });
  };

  f.relatorio = (comp) => relatorioDoMes(mesDa(comp) ?? null, f.config, comp);
  f.situacaoDe = (comp) => f.relatorio(comp).situacao;

  /**
   * Os eventos desde a última leitura guardada no perfil. Atualiza o
   * instantâneo no próprio perfil (o diretor passa o perfil da visita).
   */
  f.eventosDeAbertura = (perfil, hoje = new Date().toISOString().slice(0, 10)) => {
    if (f.estado !== 'lida') return [];
    const anterior = perfil.planilha?.instantaneo ?? null;
    const { eventos, instantaneo } = eventosDaLeitura({ meses: f.meses, config: f.config }, anterior,
      { hoje: perfil.visitas?.at(-1) ?? hoje, perfilId: perfil.perfil });
    perfil.planilha = { instantaneo, lida_em: hoje };
    const hist = f.historico(perfil.primeiro_acesso);
    if (!perfil.eventos['historico:leitura'] && hist.some((m) => m.conferido)) {
      eventos.unshift({ id: 'historico:leitura', type: 'historical_data_ready', profileId: perfil.perfil, competence: null,
        occurredAt: perfil.primeiro_acesso,
        payload: { meses_validos: hist.filter((m) => m.conferido).length, meses: hist,
          meses_fora: hist.filter((m) => !m.conferido).length, sintetico: false } });
    }
    return eventos;
  };

  f.abaDaCompetencia = abaDaCompetencia;
  return f;
}
