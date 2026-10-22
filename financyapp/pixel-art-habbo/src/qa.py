"""Conferência das animações (fase 7 do manual, §9.2 e §10).

    python3 src/qa.py

Lê o assets/ que o build gerou (o manifesto e as folhas, como o jogo lê) e:

- monta a listagem de todas as animações (personagem, id, direção, quadros,
  FPS, modo, linha, âncora e marcadores) e confere com as tabelas 8.1 e 8.2
  do manual (teste 13);
- roda os testes do pacote (teste_animacoes.py) e os do jogo (npm test) e
  liga cada um aos itens da checklist §9.2;
- gera previa/qa/: animacoes.json (a listagem e a conferência),
  testes.json (o resultado de cada teste) e index.html (a página de
  comparação por personagem e por animação, com a referência original,
  o que mudou em cada quadro, os marcadores e o registro do que é fiel, do
  que foi ajustado e do que precisa de decisão).
"""
import base64
import io
import json
import os
import re
import subprocess
import sys
import unittest

from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, '..')
ASSETS = os.path.join(RAIZ, 'assets')
SAIDA = os.path.join(RAIZ, 'previa', 'qa')
JOGO = os.path.join(RAIZ, '..', 'jogo')

# ------------------------------------------------------------ o manual
# tabela 8.1, para cada um dos 12 humanos: (direção, quadros, FPS, modo)
RESUMO_8_1 = {
    'parado_frente': ('frente', 1, 0, 'estático'),
    'parado_costas': ('costas', 1, 0, 'estático'),
    'andando_frente': ('frente', 4, 8, 'loop'),
    'andando_costas': ('costas', 4, 8, 'loop'),
    'sentado_frente': ('frente', 1, 0, 'estático'),
    'sentado_costas': ('costas', 1, 0, 'estático'),
    'sentado_frente_idle': ('frente', 2, 2, 'loop'),
    'teclando_frente': ('frente', 4, 8, 'loop'),
    'assentindo_para_tela_frente': ('frente', 4, 6, 'uma vez'),
    'piscando_frente': ('frente', 3, 12, 'uma vez'),
    'olhando_para_o_lado_frente': ('frente', 4, 5, 'uma vez'),
    'falando_frente': ('frente', 4, 8, 'loop'),
    'levantando_da_cadeira_frente': ('frente', 6, 8, 'uma vez'),
    'sentando_na_cadeira_frente': ('frente', 6, 8, 'uma vez'),
}
# tabela 8.2: (personagem ou objeto, id) -> (direção, quadros, FPS, modo)
RESUMO_8_2 = {
    ('gabriel', 'deixando_envelope_no_malote'): ('frente', 2, 6, 'uma vez'),
    ('saldanha', 'digitando_sentado'): ('frente', 2, 6, 'loop'),
    ('saldanha', 'alerta'): ('frente', 2, 5, 'uma vez'),
    ('saldanha', 'apresentando_quadro'): ('frente', 2, 5, 'loop'),
    ('saldanha', 'comemorando_tablet'): ('frente', 2, 5, 'uma vez'),
    ('caio', 'mostrando_tablet'): ('frente', 1, 0, 'estático'),
    ('vivi', 'tirando_foto'): ('frente', 2, 6, 'uma vez'),
    ('flora', 'andando'): ('de lado', 4, 8, 'loop'),
    ('flora', 'dormindo_na_cama'): ('de lado', 2, 1, 'loop'),
    ('flora', 'inquieto'): ('de lado', 2, 3, 'loop'),
    ('lupin', 'andando'): ('de lado', 4, 9, 'loop'),
    ('lupin', 'dormindo_na_cama'): ('de lado', 2, 1, 'loop'),
    ('lupin', 'inquieto'): ('de lado', 2, 4, 'loop'),
    ('sineta', 'tocando'): ('não se aplica', 2, 8, 'uma vez'),
}
# linhas que não estão no manual, e por quê
ACRESCIMOS = {
    '_tampo': 'camada do tampo: antebraços e mãos que o jogo cola depois da mesa (nota 11)',
    'deixando_envelope_no_malote_costas': 'a entrega de costas, a da planta (nota 13)',
}
# poses que já existiam (o manual pede para não refazer)
EXISTIAM = {'parado_frente', 'sentado_frente'}
HUMANOS = ['guilherme', 'saldanha', 'caio', 'vivi', 'gabriel', 'nina', 'otto', 'sr_pra_ontem',
           'iris', 'joana', 'malu', 'duda']
CAES = ['flora', 'lupin']
MARCADORES = ('rosto', 'maos', 'mesa', 'tampo', 'camada_de', 'sobreposicao', 'desloca', 'envelope', 'solta',
              'dedo', 'tela', 'selo', 'flash', 'flash_no_quadro', 'no_lugar_do_teclado', 'na_cama', 'toque')


def modo(a):
    if a.get('loop'):
        return 'loop'
    if a['quadros'] == 1 and not a.get('fps'):
        return 'estático'
    return 'uma vez'


def direcao(cid, nome, a, man):
    if 'direcao' in a:
        return a['direcao']
    if cid in CAES:
        return 'de lado'
    if a.get('camada_de'):
        return direcao(cid, a['camada_de'], man[cid]['animacoes'][a['camada_de']], man)
    if nome.endswith('_costas'):
        return 'costas'
    return 'frente'


def acrescimo(nome):
    if nome.endswith('_tampo'):
        return ACRESCIMOS['_tampo']
    return ACRESCIMOS.get(nome)


def listagem(man):
    """Uma linha por animação do manifesto (personagens e a sineta)."""
    out = []
    for cid, e in man.items():
        if 'folha' in e:
            for nome, a in e['animacoes'].items():
                out.append({
                    'personagem': cid, 'animacao': nome, 'direcao': direcao(cid, nome, a, man),
                    'quadros': a['quadros'], 'fps': a.get('fps', 0), 'modo': modo(a), 'linha': a['linha'],
                    'tela': e['tela'], 'ancora': e['ancora'], 'folha': e['folha'],
                    'marcadores': {k: a[k] for k in MARCADORES if k in a},
                })
        for nome, a in e.get('animacoes', {}).items() if 'folha' not in e else ():
            out.append({
                'personagem': cid, 'animacao': nome, 'direcao': 'não se aplica',
                'quadros': a['quadros'], 'fps': a['fps'], 'modo': 'loop' if a.get('loop') else 'uma vez',
                'linha': 0, 'tela': a['tela'], 'ancora': a['ancora'], 'folha': a['folha'],
                'marcadores': {k: a[k] for k in MARCADORES if k in a},
            })
    return out


def conferir(linhas):
    """Confere a listagem com as tabelas 8.1 e 8.2. Devolve (problemas,
    situacao por linha): cada linha ganha 'manual' ('8.1', '8.2', ou None),
    'confere' (bool) e, se não está no manual, 'acrescimo' (o motivo)."""
    problemas = []
    por = {(l['personagem'], l['animacao']): l for l in linhas}
    for l in linhas:
        chave = (l['personagem'], l['animacao'])
        esperado, tabela = None, None
        if l['personagem'] in HUMANOS and l['animacao'] in RESUMO_8_1:
            esperado, tabela = RESUMO_8_1[l['animacao']], '8.1'
        elif chave in RESUMO_8_2:
            esperado, tabela = RESUMO_8_2[chave], '8.2'
        elif l['personagem'] in CAES and l['animacao'] in EXISTIAM:
            # §6: "já existem: em_pe_parado e sentado (não refazer)"
            esperado, tabela = ('de lado', 1, 0, 'estático'), '§6'
        l['manual'] = tabela
        if esperado:
            real = (l['direcao'], l['quadros'], l['fps'], l['modo'])
            l['confere'] = real == esperado
            if not l['confere']:
                problemas.append(f'{chave}: manual {esperado}, assets {real}')
        else:
            l['acrescimo'] = acrescimo(l['animacao'])
            l['confere'] = l['acrescimo'] is not None
            if not l['confere']:
                problemas.append(f'{chave}: não está no manual e não tem motivo registrado')
    # tudo o que o manual pede existe
    for cid in HUMANOS:
        for nome in RESUMO_8_1:
            if (cid, nome) not in por:
                problemas.append(f'falta {cid} {nome} (8.1)')
    for chave in RESUMO_8_2:
        if chave not in por:
            problemas.append(f'falta {chave} (8.2)')
    return problemas


# ------------------------------------------------------------ a checklist
# §9.2, item a item: o que os testes conferem e o que é de olhar
CHECKLIST = [
    (1, 'Todo sprite humano mede 40 × 70 px e usa pixels inteiros; PNG final com transparência e render sem filtro linear.',
     ['test_tela_40x70_sem_meio_tom', 'cada folha tem uma linha por animação e cabe todos os quadros'],
     'A página mostra tudo ampliado sem suavizar.'),
    (2, 'A âncora permanece estável na pose, ao pisar e na transição sentar/levantar. Nada atravessa piso, borda do quadro ou cadeira.',
     ['test_ancora_no_chao', 'test_pe_plantado_nao_mexe', 'test_nada_vaza_da_tela', 'test_cadeira_comeca_e_termina_nas_poses',
      'test_cadeira_sai_para_o_chao'],
     'Na cadeira, conferir na prévia (seção "Na cadeira"): ele sai do assento para o chão.'),
    (3, 'Personagem sentado tem quadril 14 px acima da âncora do chão; pernas e pés dobrados na perspectiva correta.',
     ['test_quadril_sentado', 'test_sentado_de_costas_no_mesmo_assento'],
     'O quadril fica a 14 ou 15 px; na Vivi, na Íris, na Joana e na Duda a cintura da calça sobe mais (pantalona e cintura alta).'),
    (4, 'Frente/costas mostram os ângulos corretos; outros dois sentidos vêm de espelhamento; o deslocamento lógico continua restrito a quatro direções sem diagonal.',
     ['test_de_costas_nao_tem_rosto', 'test_caminhada_quatro_poses_distintas'],
     'Os ângulos são de olhar (prévia, "Na sala"). As quatro direções sem diagonal são regra do jogo, que ainda não anda (corte 1).'),
    (5, 'Os 12 humanos mantêm paleta, roupa, acessórios, cabelo e características originais.',
     ['test_paleta_e_a_do_desenho', 'test_contato_tem_a_cabeca_do_parado', 'test_relogio_do_saldanha_fica_no_braco'],
     'Nenhuma cor nova além das listadas no teste (luz do dorso da mão, boca aberta, adereços). Conferir alça, relógio, crachá, estampas, botões, argolas, óculos e cabelo na comparação, com "O que mudou" ligado.'),
    (6, 'andando_* tem quatro poses visualmente distintas, apoio alternado e loop sem salto; pés não patinam.',
     ['test_caminhada_quatro_poses_distintas', 'test_caminhada_corpo_sobe_so_nas_passagens', 'test_pe_plantado_nao_mexe'],
     'Patinar depende da velocidade do jogo: com passo de 2 px, acima de uns 0,5 tile/s o pé de apoio desliza.'),
    (7, 'teclando_frente não move a mesa; boca e pálpebras podem animar como overlays sem trocar a posição do corpo.',
     ['test_teclando_so_mexe_as_maos', 'test_mesa_parada_quadril_e_pernas_nao_mexem', 'test_sobreposicoes_so_no_rosto',
      'test_rosto_marca_onde_esta_o_olho'],
     'A mesa não está no sprite: é peça do cenário.'),
    (8, 'sentando_* termina exatamente na pose sentada; levantando_* termina exatamente na pose em pé. Não deixar frame intermediário congelado.',
     ['test_cadeira_comeca_e_termina_nas_poses', 'test_cadeira_sem_quadro_congelado'], ''),
    (9, 'Gabriel: envelope permanece na mão durante os quatro passos e sai no Q2 da entrega; marcador permanece sincronizado com a mão.',
     ['test_envelope_na_mao_andando', 'test_envelope_sai_no_q2'], ''),
    (10, 'Caio: selo verde, amarelo e vermelho aparecem dentro da tela, sem cobrir moldura/mão; não requer três imagens separadas.',
     ['test_selo_dentro_da_tela_do_caio'], ''),
    (11, 'Vivi: flash aparece no Q2, sem flash residual; sineta vibra no Q2 e retorna ao normal.',
     ['test_flash_so_no_q2', 'test_sineta_vibra_no_q2'], ''),
    (12, 'Cães preservam tamanhos relativos, características individuais e camas estáticas; animação de dormir mantém olhos fechados.',
     ['test_tamanho_relativo', 'test_caracteristicas', 'test_paleta_dos_caes', 'test_dormindo_de_olhos_fechados',
      'test_dormindo_so_respira', 'test_em_pe_e_o_desenho_original'],
     'As camas são peças à parte e não mudam.'),
    (13, 'Todas as animações têm id, contagem, FPS e modo de loop consistentes com o resumo; gerar relatório/listagem validável.',
     ['test_listagem_bate_com_o_resumo', 'test_resumo_8_2', 'test_lista_de_animacoes',
      'as camadas e as sobreposições apontam para animações que existem'],
     'A listagem fica em previa/qa/animacoes.json e no fim desta página.'),
    (14, 'Gerar visualização ampliada 4× a 8× nearest-neighbor de cada faixa, com nomes e números fora dos sprites; não embutir rótulos nas texturas finais.',
     ['test_paleta_e_a_do_desenho', 'test_paleta_dos_caes'],
     'Esta página: cada quadro a 4×, recortado da folha do assets/, com o nome e o número fora do sprite.'),
]


class _Coleta(unittest.TextTestResult):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.saida = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.saida.append((test._testMethodName, type(test).__name__, 'passou', ''))

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.saida.append((test._testMethodName, type(test).__name__, 'falhou', self._exc_info_to_string(err, test)))

    def addError(self, test, err):
        super().addError(test, err)
        self.saida.append((test._testMethodName, type(test).__name__, 'erro', self._exc_info_to_string(err, test)))


def testes_do_pacote():
    sys.path.insert(0, AQUI)
    import teste_animacoes
    suite = unittest.defaultTestLoader.loadTestsFromModule(teste_animacoes)
    r = unittest.TextTestRunner(stream=io.StringIO(), resultclass=_Coleta).run(suite)
    return [{'nome': n, 'grupo': g, 'resultado': s, 'detalhe': d} for n, g, s, d in r.saida]


def testes_do_jogo():
    """npm test, no formato TAP: cada 'ok' e 'not ok' com o nome."""
    try:
        p = subprocess.run(['node', '--test', '--test-reporter=tap'], cwd=JOGO, capture_output=True, text=True,
                           timeout=300)
    except FileNotFoundError:
        return [{'nome': 'node não encontrado', 'grupo': 'jogo', 'resultado': 'erro', 'detalhe': ''}]
    out = []
    for linha in p.stdout.splitlines():
        m = re.match(r'^\s*(not ok|ok) \d+ - (.+)$', linha)
        if m and not linha.startswith(' ' * 4):
            nome = m.group(2).strip()
            if nome.endswith('.test.js') or nome.startswith('/'):
                continue
            out.append({'nome': nome, 'grupo': 'jogo', 'resultado': 'passou' if m.group(1) == 'ok' else 'falhou',
                        'detalhe': ''})
    return out


# ------------------------------------------------------------ a página
def png64(im):
    buf = io.BytesIO()
    im.save(buf, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def arquivo64(rel):
    return png64(Image.open(os.path.join(ASSETS, rel)).convert('RGBA'))


def referencias():
    """O desenho original de cada um, como está no chars.py (a pose da
    vitrine), na escala do escritório para os cachorros."""
    import chars
    import costas
    import caes
    out = {}
    for cid, (fn, _) in costas.HUMANOS.items():
        out[cid] = png64(fn())
    for cid, (fn, k) in caes.DESENHO.items():
        out[cid] = png64(fn(k, 'em_pe'))
    return out


def pagina(man, linhas, problemas, testes, jogo):
    nomes = {'guilherme': 'Guilherme', 'saldanha': 'Saldanha', 'caio': 'Caio', 'vivi': 'Vivi', 'gabriel': 'Gabriel',
             'nina': 'Nina', 'otto': 'Otto', 'sr_pra_ontem': 'Sr. Pra Ontem', 'iris': 'Íris', 'joana': 'Joana',
             'malu': 'Malu', 'duda': 'Duda', 'flora': 'Flora', 'lupin': 'Lupin'}
    folhas = {cid: arquivo64(man[cid]['folha']) for cid in nomes}
    sin = man['sineta']['animacoes']['tocando']
    dados = {
        'nomes': nomes,
        'manifesto': {cid: man[cid] for cid in nomes},
        'folhas': folhas,
        'referencias': referencias(),
        'sineta': {**sin, 'folha': arquivo64(sin['folha']), 'parada': arquivo64('objetos/sineta__parada.png')},
        'listagem': linhas,
        'problemas': problemas,
        'testes': testes,
        'jogo': jogo,
        'checklist': [{'item': i, 'texto': t, 'testes': ts, 'olho': o} for i, t, ts, o in CHECKLIST],
    }
    modelo = open(os.path.join(AQUI, 'qa.html'), encoding='utf-8').read()
    return modelo.replace('__DADOS__', json.dumps(dados, ensure_ascii=False))


def main():
    os.makedirs(SAIDA, exist_ok=True)
    man = json.load(open(os.path.join(ASSETS, 'manifest.json'), encoding='utf-8'))
    linhas = listagem(man)
    problemas = conferir(linhas)
    with open(os.path.join(SAIDA, 'animacoes.json'), 'w', encoding='utf-8') as f:
        json.dump({'problemas': problemas, 'animacoes': linhas}, f, ensure_ascii=False, indent=1)
    testes = testes_do_pacote()
    jogo = testes_do_jogo()
    with open(os.path.join(SAIDA, 'testes.json'), 'w', encoding='utf-8') as f:
        json.dump({'pacote': testes, 'jogo': jogo}, f, ensure_ascii=False, indent=1)
    with open(os.path.join(SAIDA, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(pagina(man, linhas, problemas, testes, jogo))
    ok = sum(t['resultado'] == 'passou' for t in testes)
    okj = sum(t['resultado'] == 'passou' for t in jogo)
    print(f'animações: {len(linhas)}; problemas na listagem: {len(problemas)}')
    print(f'testes do pacote: {ok}/{len(testes)}; do jogo: {okj}/{len(jogo)}')
    for p in problemas:
        print(' -', p)


if __name__ == '__main__':
    main()
