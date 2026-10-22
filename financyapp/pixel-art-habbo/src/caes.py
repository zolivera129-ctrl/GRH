"""Os cachorros (fase 6 do manual, §6): Flora e Lupin andando, dormindo na
cama e inquietos.

Como nos humanos, o desenho de cada um (chars.flora e chars.lupin, em pé,
na escala do escritório) é gravado camada por camada e remontado com as
patas, o corpo, a cabeça e o rabo deslocados. Nada é redesenhado no andar e
no inquieto. Só o deitado é pose nova (não existia): o corpo e a coxa vêm
do em pé, baixados até o chão, com as patas da frente esticadas, a cabeça
apoiada nelas e os olhos fechados.

Tela e âncora: as do em pé (o desenho de 56 × 47, ou 44 × 34, na escala do
escritório, com a margem de 2 px do assets/). Todos os quadros novos ficam
nessa tela e pisam na mesma linha do em pé, então a âncora é a dele.

Direção: o desenho olha para a direita; o outro sentido é o espelho, como
o manual pede (§6, "Espelhamento dos cães").
"""
import math

import anim
import chars
import costas
from px import Layer, mix, rgb

MARGEM = 2          # a margem do office.dog


class GravaCao(chars._SSprite):
    """O _SSprite que lembra cada camada e cada pixel solto, já na escala."""
    ultimo = None

    def __init__(self, k, w, h):
        super().__init__(k, w, h)
        self.ops = []
        GravaCao.ultimo = self

    def add(self, layer, dx=0, dy=0):
        pts = {(x + dx + self.dx, y + dy + self.dy): c for (x, y), c in layer.px.items()}
        self.ops.append(['camada', pts, None, None])
        self.px.update(pts)

    def set(self, x, y, c):
        m = lambda v: int(math.floor(v * self.k + 0.5))
        p = (m(x) + self.dx, m(y) + self.dy)
        self.ops.append(['pixel', {p: c}, None, None])
        self.px[p] = c


def gravar(fn, k, pose='em_pe'):
    antes = chars._SSprite
    chars._SSprite = GravaCao
    try:
        fn(k, pose)
    finally:
        chars._SSprite = antes
    S = GravaCao.ultimo
    ops = [[a, costas.mover(p, MARGEM, MARGEM), g, d] for a, p, g, d in S.ops]
    return ops, (S.w + 2 * MARGEM, S.h + 2 * MARGEM)


# ------------------------------------------------------------ grupos
# a ordem das camadas do em pé (chars._flora_standing / _lupin_standing e
# a cabeça): rabo, pata de trás de longe, pata da frente de longe, corpo,
# coxa, pata de trás de perto, pata da frente de perto, e a cabeça. Pixel
# solto vai com a camada de antes dele.
EM_PE = {
    'flora': ['rabo', 'perna_tl', 'perna_fl', 'corpo', 'corpo', 'perna_tp', 'perna_fp',
              'cabeca', 'cabeca', 'orelha'],
    'lupin': ['rabo', 'perna_tl', 'perna_fl', 'corpo', 'corpo', 'perna_tp', 'perna_fp',
              'cabeca', 'cabeca', 'cabeca', 'orelha', 'orelha_longe'],
}
CARAMELO = {rgb('#70462A'), rgb('#94603A')}
DESENHO = {'flora': (chars.flora, 0.75), 'lupin': (chars.lupin, 0.75)}


def agrupar(cid, ops):
    nomes = iter(EM_PE[cid])
    g = None
    out = []
    for o in ops:
        if o[0] == 'camada':
            g = next(nomes)
        grupo = g
        if cid == 'lupin' and o[0] == 'pixel' and g == 'cabeca':
            (p, c), = o[1].items()
            if c in CARAMELO and p[1] <= 8:
                grupo = 'sobrancelha'
        out.append([o[0], o[1], grupo, None])
    return out


def em_pe(cid):
    fn, k = DESENHO[cid]
    ops, tela = gravar(fn, k)
    return agrupar(cid, ops), tela


# ------------------------------------------------------------ andando
# trote em diagonal: o par A é a pata da frente de perto com a de trás de
# longe; o par B, a da frente de longe com a de trás de perto. Como na
# caminhada dos humanos: no contato um par vai 2 px à frente e o outro
# recua 1; na passagem o corpo sobe 1 px e o par que avança passa com a
# pata 1 px no ar, enquanto o outro fica plantado.
def _par(a, b, **m):
    return {a: dict(m), b: dict(m)}


A_ = ('perna_fp', 'perna_tl')
B_ = ('perna_fl', 'perna_tp')
SOBE = ('corpo', 'cabeca', 'orelha', 'orelha_longe', 'sobrancelha')


def _ciclo(extra):
    base = [
        {**_par(*A_, ponta=2), **_par(*B_, ponta=-1)},
        {**{g: {'dy': -1} for g in SOBE}, **_par(*B_, ponta=1, ergue=1)},
        {**_par(*B_, ponta=2), **_par(*A_, ponta=-1)},
        {**{g: {'dy': -1} for g in SOBE}, **_par(*A_, ponta=1, ergue=1)},
    ]
    for q, e in zip(base, extra):
        for g, m in e.items():
            q[g] = {**q.get(g, {}), **m}
    return base


ANDANDO = {
    # manual §6.1: Q2 focinho sobe com o corpo e o rabo desce 1 px; Q4 o
    # rabo sobe 1 px
    'flora': _ciclo([{}, {'rabo': {'dy': 1}}, {}, {'rabo': {'dy': -1}}]),
    # manual §6.4: Q2 cabeça x+1 e a orelha dobrada fica 1 px para trás
    # (balança); Q4 o rabo vai 1 px para o lado
    'lupin': _ciclo([{}, {'cabeca': {'dx': 1}, 'sobrancelha': {'dx': 1}, 'orelha_longe': {'dx': 1}},
                     {}, {'rabo': {'dx': -1}}]),
}

# ------------------------------------------------------------ inquieto
# manual §6.3 e §6.6: Q1 é o em pé; Q2 levanta a cabeça, o corpo (só a
# Flora) e a pata da frente de perto, e mexe o rabo
INQUIETO = {
    'flora': [{}, {'cabeca': {'dx': 1, 'dy': -2}, 'orelha': {'dx': 1, 'dy': -3},
                   'corpo': {'dy': -1}, 'perna_fp': {'dy': -1}, 'rabo': {'dy': -2}}],
    'lupin': [{}, {'cabeca': {'dx': 2, 'dy': -1}, 'orelha': {'dx': 2, 'dy': -1}, 'orelha_longe': {'dx': 2, 'dy': -1},
                   'sobrancelha': {'dx': 2, 'dy': -2}, 'perna_fp': {'dy': -1}, 'rabo': {'dx': -2}}],
}


def quadros_em_pe(cid, ciclo):
    ops, (w, h) = em_pe(cid)
    return [anim.montar(ops, m, w=w, h=h) for m in ciclo]


# ------------------------------------------------------------ dormindo
# Pose nova: deitada de lado para a direita, como a esfinge, no mesmo
# desenho e na mesma escala do em pé (as coordenadas são as do desenho
# original, antes da escala). O tronco é o do em pé baixado até o chão; a
# coxa de trás dobrada, com a pata para a frente; as patas da frente
# esticadas no chão; a cabeça baixada, com o queixo nas patas; o rabo no
# chão; olhos fechados. Cada parte é uma camada com o seu grupo: 'tronco'
# respira (Q2: as costas sobem 1 px), o resto não mexe.
def _flora_deitada(S, L, fur, furd, furl, furll, line):
    grupos = []

    def add(layer, g):
        S.add(layer)
        grupos.append(g)
    # rabo deitado no chão, atrás
    tl = L(fur, line)
    tl.rows({41: (2, 8), 42: (0, 10), 43: (0, 11), 44: (2, 10)})
    tl.outline()
    for x in (3, 4, 5):
        tl.set(x, 42, furl)
    add(tl, 'corpo')
    # pata da frente de longe, esticada (1 px acima da de perto)
    fl = L(fur, line)
    fl.rows({39: (34, 47), 40: (34, 48), 41: (34, 48), 42: (35, 49), 43: (36, 49)})
    fl.shade_side('l', 1, furd)
    fl.outline()
    add(fl, 'corpo')
    # tronco: as costas do em pé, baixadas até o chão
    bd = L(fur, line)
    bd.rows({30: (16, 34), 31: (11, 37), 32: (9, 38)})
    bd.rows({y: (7, 39) for y in range(33, 43)})
    bd.rows({43: (8, 39), 44: (9, 38)})
    bd.outline()
    for x in range(13, 33):
        bd.set(x, 32, furl)
    for x in range(17, 30):
        bd.set(x, 31, furll if x % 5 == 0 else furl)
    for x in range(11, 38):
        bd.set(x, 43, furd)
    add(bd, 'tronco')
    # coxa de trás dobrada e a pata de trás de perto, para a frente, no chão
    hp = L(fur, line)
    hp.rows({33: (10, 17), 34: (8, 19), 35: (7, 20), 36: (7, 21), 37: (7, 21), 38: (7, 21),
             39: (7, 21), 40: (8, 21), 41: (9, 20)})
    hp.outline()
    for x, y in ((11, 34), (12, 34), (13, 34), (10, 35)):
        hp.set(x, y, furl)
    add(hp, 'corpo')
    pt = L(fur, line)
    pt.rows({41: (12, 24), 42: (11, 25), 43: (11, 26), 44: (12, 26)})
    pt.shade_side('l', 1, furd)
    pt.outline()
    add(pt, 'corpo')
    # pata da frente de perto, esticada até embaixo do focinho
    fp = L(fur, line)
    fp.rows({41: (31, 47), 42: (31, 48), 43: (31, 49), 44: (32, 49), 45: (33, 49)})
    fp.shade_side('l', 1, furd)
    fp.outline()
    for x in range(35, 46):
        fp.set(x, 42, furl)
    add(fp, 'corpo')
    return grupos


def _lupin_deitado(S, L, fur, furd, furl, line):
    grupos = []

    def add(layer, g):
        S.add(layer)
        grupos.append(g)
    tl = L(fur, line)
    tl.rows({29: (1, 6), 30: (0, 7), 31: (1, 7)})
    chars._tufts(tl, 1, line, 3)
    tl.outline()
    add(tl, 'corpo')
    fl = L(fur, line)
    fl.rows({28: (25, 33), 29: (25, 34), 30: (26, 34)})
    fl.outline()
    add(fl, 'corpo')
    bd = L(fur, line)
    bd.rows({21: (11, 26), 22: (8, 28), 23: (7, 29)})
    bd.rows({y: (6, 29) for y in range(24, 30)})
    bd.rows({30: (7, 29), 31: (8, 28)})
    bd.shade_side('l', 1, furd)
    bd.outline()
    chars._tufts(bd, 2, line)
    for x in range(10, 24):
        bd.set(x, 22 if x > 11 else 23, furl)
    for x in range(9, 28):
        bd.set(x, 30, furd)
    add(bd, 'tronco')
    hp = L(fur, line)
    hp.rows({24: (8, 13), 25: (7, 14), 26: (7, 14), 27: (7, 14), 28: (8, 14)})
    hp.outline()
    hp.set(9, 25, furl)
    add(hp, 'corpo')
    pt = L(fur, line)
    pt.rows({29: (10, 17), 30: (10, 18), 31: (11, 18)})
    pt.outline()
    add(pt, 'corpo')
    fp = L(fur, line)
    fp.rows({29: (23, 33), 30: (23, 34), 31: (24, 34), 32: (25, 34)})
    fp.outline()
    add(fp, 'corpo')
    return grupos


# onde a cabeça vai, deitada (o deslocamento do desenho da cabeça, em px do
# desenho original): baixada até o queixo encostar nas patas
CABECA_DEITADA = {'flora': (8, 25), 'lupin': (5, 13)}
# olhos fechados: os pixels do olho, no desenho da cabeça, viram pelo, e um
# traço curvo fica no lugar (no desenho da cabeça, antes do deslocamento)
OLHOS = {
    'flora': {'apaga': [(x, y) for x in range(27, 30) for y in range(5, 9)] + [(x, y) for x in (34, 35) for y in range(5, 9)],
              'traco': [(27, 7), (28, 8), (29, 7), (34, 7), (35, 8)]},
    'lupin': {'apaga': [(20, 7), (21, 7), (20, 8), (21, 8), (26, 7), (27, 7), (26, 8), (27, 8)],
              'traco': [(20, 8), (21, 8), (26, 8), (27, 8)]},
}


def gravar_deitado(cid):
    fn, k = DESENHO[cid]
    L = lambda base, line=None: chars._SLayer(k, base, line)
    if cid == 'flora':
        cores = (rgb('#2A2A31'), rgb('#141418'), rgb('#434552'), rgb('#666A7D'))
        linha = rgb('#09090B')
        S = GravaCao(k, 56, 47)
        grupos = _flora_deitada(S, L, *cores, linha)
        cabeca = chars._flora_head
        args = cores + (linha,)
        pelo = cores[0]
    else:
        cores = (rgb('#25242A'), rgb('#121115'), rgb('#403E4A'))
        linha = rgb('#070708')
        S = GravaCao(k, 44, 34)
        grupos = _lupin_deitado(S, L, *cores, linha)
        cabeca = chars._lupin_head
        args = cores + (linha,)
        pelo = cores[0]
    if cid == 'flora':
        # a coleira, no pescoço, embaixo da cabeça baixada: só um pedaço
        # aparece entre a orelha e as patas, com a plaquinha (a coleira da
        # cabeça em pé fica de fora)
        col = L(rgb('#D7352E'), rgb('#8E1C18'))
        col.rows({41: (25, 33), 42: (25, 33)})
        col.outline()
        for x in range(27, 32):
            col.set(x, 41, rgb('#EF5A50'))
        S.add(col)
        grupos.append('corpo')
        for x, y, c in ((31, 43, rgb('#F4C04F')), (32, 43, rgb('#C99A2E'))):
            S.set(x, y, c)
    n_corpo = len(S.ops)
    S.dx, S.dy = (round(v * k) for v in CABECA_DEITADA[cid])
    cabeca(S, L, *args)
    if cid == 'flora':
        # tira a coleira e a plaquinha que a cabeça desenha (a primeira
        # camada e os quatro pixels seguintes)
        del S.ops[n_corpo:n_corpo + 5]
    for x, y in OLHOS[cid]['apaga']:
        S.set(x, y, pelo)
    for x, y in OLHOS[cid]['traco']:
        S.set(x, y, linha)
    ops = []
    gi = iter(grupos)
    g = None
    for i, o in enumerate(S.ops):
        if i < n_corpo:
            g = next(gi) if o[0] == 'camada' else g
            ops.append([o[0], costas.mover(o[1], MARGEM, MARGEM), g, None])
        else:
            ops.append([o[0], costas.mover(o[1], MARGEM, MARGEM), 'cabeca', None])
    return ops, (S.w + 2 * MARGEM, S.h + 2 * MARGEM)


# respiração: no Q2 as costas sobem 1 px (o tronco estica para cima acima
# da metade); cabeça, orelhas e patas ficam
def dormindo(cid):
    ops, (w, h) = gravar_deitado(cid)
    lim = anim._limites(ops)['tronco']
    meio = (lim[0] + lim[1]) // 2
    return [anim.montar(ops, {}, w=w, h=h),
            anim.montar(ops, {'tronco': {'dy': -1, 'acima_de': meio}}, w=w, h=h)]


# ------------------------------------------------------------ o registro
# manual §8.2: nome -> (quadros por segundo, repete?)
ANIMACOES = {
    'flora': {'andando': (8, True), 'dormindo_na_cama': (1, True), 'inquieto': (3, True)},
    'lupin': {'andando': (9, True), 'dormindo_na_cama': (1, True), 'inquieto': (4, True)},
}
CAMA = {'flora': 'manta_flora', 'lupin': 'caminha_lupin'}


def quadros(cid):
    """{animação: [quadros]} das animações novas, na tela do em pé (com a
    margem do assets/), pisando na linha dele."""
    return {
        'andando': quadros_em_pe(cid, ANDANDO[cid]),
        'dormindo_na_cama': dormindo(cid),
        'inquieto': quadros_em_pe(cid, INQUIETO[cid]),
    }


def campos(cid, nome):
    """Campos do manifesto além de linha, quadros, fps e loop."""
    if nome == 'dormindo_na_cama':
        # deitado, na cama: o jogo cola na âncora da cama (o centro do tile)
        return {'na_cama': CAMA[cid]}
    return {}
