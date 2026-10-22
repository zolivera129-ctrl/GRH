"""As animações de cada humano, prontas para a folha de sprites.

A ordem das linhas mantém o que o jogo já usa (parado e sentado de frente
nas linhas 0 e 1) e acrescenta as do manual:

- fase 2 (§3): parado e sentado de costas e as duas caminhadas;
- fase 3 (§4): a vida à mesa (respirar, teclar, assentir, olhar para o
  lado), cada uma com a sua camada do tampo, e as sobreposições do rosto
  (piscar e falar);
- fase 4 (§4.7 e §4.8): levantar da cadeira e sentar nela.

Todos os quadros ficam na tela de 40 × 70 com a sola na linha anim.PE, então
a âncora é a mesma em todos: (20, anim.PE).

Campos que o manifesto ganha por animação (além de linha, quadros e fps):
- loop: true quando repete enquanto o estado durar;
- rosto: onde o rosto está em cada quadro, em relação ao parado de frente;
  as sobreposições de olhos e boca vão nesse deslocamento;
- tampo: o nome da linha com os antebraços e as mãos daquela animação, que
  o jogo cola depois da mesa e antes dos objetos sobre ela;
- maos: os pontos das duas mãos em cada quadro, [frente, trás];
- mesa: em que móvel as mãos pousam ('mesa', 24 px, ou 'balcao', 34 px);
- sobreposicao: true nas linhas do rosto, que não são um corpo inteiro;
- desloca: em levantar e sentar, quanto o personagem anda em cada quadro,
  na tela, a partir do centro do tile da cadeira (para quem olha +A;
  espelhado, o x troca de sinal). Em pé, ele fica meio tile à frente da
  cadeira, pisando no chão.
"""
import anim
import cadeira
import chars
import costas
import escritorio

ANCORA = (20, anim.PE)

# nome: (quadros por segundo, repete?)
ANIMACOES = {
    'parado_frente': (0, False),
    'sentado_frente': (0, False),
    'parado_costas': (0, False),
    'sentado_costas': (0, False),
    'andando_frente': (8, True),
    'andando_costas': (8, True),
    'sentado_frente_idle': (2, True),
    'teclando_frente': (8, True),
    'assentindo_para_tela_frente': (6, False),
    'olhando_para_o_lado_frente': (5, False),
    'sentado_frente_idle_tampo': (2, True),
    'teclando_frente_tampo': (8, True),
    'assentindo_para_tela_frente_tampo': (6, False),
    'olhando_para_o_lado_frente_tampo': (5, False),
    'piscando_frente': (12, False),
    'falando_frente': (8, True),
    'levantando_da_cadeira_frente': (8, False),
    'sentando_na_cadeira_frente': (8, False),
}
CADEIRA = list(cadeira.ROTEIROS)
ESCRITORIO = list(escritorio.CICLOS)
SOBREPOSICOES = ('piscando_frente', 'falando_frente')


def quadros(cid):
    """{animação: [quadros]} de um humano, pelo id do assets/."""
    frente, _ = costas.HUMANOS[cid]
    n = anim.folga(frente)
    ops_costas = costas.ops(cid, 'parado')
    out = {
        'parado_frente': [anim.descer(frente('parado'), n)],
        'sentado_frente': [anim.descer(frente('sentado'), n)],
        'parado_costas': [costas.imagem(cid, 'parado')],
        'sentado_costas': [costas.imagem(cid, 'sentado')],
        'andando_frente': anim.andando(frente),
        'andando_costas': [anim.montar(ops_costas, q, n) for q in anim.ANDANDO],
    }
    for nome in ESCRITORIO:
        out[nome] = escritorio.quadros(cid, nome)
    for nome in ESCRITORIO:
        out[f'{nome}_tampo'] = escritorio.quadros(cid, nome, so_tampo_=True)
    out['piscando_frente'] = escritorio.piscando(cid)
    out['falando_frente'] = escritorio.falando(cid)
    for nome, roteiro in cadeira.ROTEIROS.items():
        out[nome] = cadeira.quadros(cid, roteiro)
    return out


def campos(cid, nome, nquadros):
    """Os campos extras da animação no manifesto (ver o começo do arquivo)."""
    e = {}
    if nome == 'parado_frente':
        e['rosto'] = [[0, 0]]
    elif nome == 'sentado_frente':
        e['rosto'] = [[0, chars.SIT_DY]]
    elif nome == 'andando_frente':
        e['rosto'] = [[0, q.get('corpo', {}).get('dy', 0)] for q in anim.ANDANDO]
    elif nome in CADEIRA:
        e['rosto'] = cadeira.rosto(nome)
        e['desloca'] = cadeira.desloca(nome)
    elif nome in ESCRITORIO:
        e['rosto'] = escritorio.rosto(nome)
        e['tampo'] = f'{nome}_tampo'
        e['maos'] = escritorio.maos_marcadas(cid, nome)
        e['mesa'] = escritorio.TAMPO.get(cid, 'mesa')
    elif nome.endswith('_tampo'):
        e['camada_de'] = nome[:-len('_tampo')]
    elif nome in SOBREPOSICOES:
        e['sobreposicao'] = True
    return e


HUMANOS = list(costas.HUMANOS)
