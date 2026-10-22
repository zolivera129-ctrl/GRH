"""Animações dos personagens a partir das camadas do desenho original.

O desenho de cada personagem (chars.py) é feito camada por camada. Aqui ele
é desenhado de novo com um Sprite que grava cada camada e cada pixel solto
na ordem em que entraram. Cada operação ganha um grupo (corpo, perna da
frente, perna de trás, braço da frente, braço de trás) e um quadro de
animação é o mesmo desenho remontado, na mesma ordem, com cada grupo
deslocado. Nada é redesenhado: roupa, cabelo, rosto e paleta são os do
original, pixel por pixel.

Convenção do manual (FinancyApp_Manual_Animacoes, v1.0):
- tela de 40 × 70, origem no canto de cima à esquerda, x para a direita e
  y para baixo;
- "da frente" é o membro mais perto da câmera, "de trás" o mais escondido;
- deslocamentos de 1 a 3 px, sempre inteiros.
"""
import math

from PIL import Image

import chars
import px


# ------------------------------------------------------------ gravação
class Gravador(px.Sprite):
    """Sprite que lembra cada camada e cada pixel solto, na ordem."""
    ultimo = None

    def __init__(self, w, h, dy=0):
        super().__init__(w, h, dy)
        self.ops = []
        Gravador.ultimo = self

    def add(self, layer, dx=0, dy=0):
        pts = {(x + dx + self.dx, y + dy + self.dy): c for (x, y), c in layer.px.items()}
        self.ops.append(['camada', pts, None])
        self.px.update(pts)

    def set(self, x, y, c):
        p = (x + self.dx, y + self.dy)
        self.ops.append(['pixel', {p: c}, None])
        self.px[p] = c


def gravar(fn, *args, **kw):
    """Desenha fn(*args) com o Gravador no lugar do Sprite e devolve as
    operações gravadas."""
    antes = chars.Sprite
    chars.Sprite = Gravador
    try:
        fn(*args, **kw)
    finally:
        chars.Sprite = antes
    return Gravador.ultimo.ops


def _caixa(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def agrupar(ops, regra):
    """Dá um grupo a cada operação. As camadas são classificadas pela regra;
    um pixel solto vai com a camada de cima que já ocupava aquele ponto
    (o relógio vai com o braço, a faixa do tênis com a perna). Cada
    operação também guarda, no fim, o índice da camada dona (a própria
    camada, ou a camada em que o pixel solto caiu; None se caiu no vazio)."""
    dono = {}
    for i, op in enumerate(ops):
        kind, pts = op[0], op[1]
        if kind == 'camada':
            op[2] = regra(_caixa(pts))
            op[3:] = [i]
            for p in pts:
                dono[p] = (op[2], i)
        else:
            (p,) = pts
            g, d = dono.get(p, ('corpo', None))
            op[2] = g
            op[3:] = [d]
            dono[p] = (g, d)
    return ops


def regra_humano(caixa):
    """Grupos de um humano em pé, de frente (olhando para a direita da tela).
    A perna e o tênis da frente ficam à esquerda (x < 19); os de trás, à
    direita. O braço da frente fica todo à esquerda do tronco; o de trás,
    à direita."""
    x0, y0, x1, y1 = caixa
    cx = (x0 + x1) / 2
    if y0 >= 43 and y1 >= 55:
        return 'perna_frente' if cx < 19 else 'perna_tras'
    if y0 >= 28 and y1 <= 52:
        if cx <= 11.5:
            return 'braco_frente'
        if cx >= 26:
            return 'braco_tras'
    return 'corpo'


# ------------------------------------------------------------ montagem
# Linha do chão (a âncora em y) de todos os quadros animados: (20, 66), a
# provisória do manual. Os desenhos originais pisam em 62 ou 63 e cinco
# deles encostam o cabelo na linha 0; sem folga em cima, o corpo subindo
# 1 px nas passagens cortaria a primeira linha do cabelo. Cada personagem
# desce até a sola cair em 66.
PE = 66


def folga(fn):
    """Quantos px o personagem desce para a sola cair na linha PE."""
    return PE - fn('parado').getbbox()[3]


def descer(im, n):
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.alpha_composite(im, (0, n))
    return out


def _arred(v):
    return int(math.floor(abs(v) + 0.5)) * (1 if v >= 0 else -1)


def _limites(ops):
    lim = {}
    for op in ops:
        pts, g = op[1], op[2]
        for (x, y) in pts:
            a = lim.setdefault(g, [y, y])
            a[0] = min(a[0], y)
            a[1] = max(a[1], y)
    return lim


def montar(ops, mov, desce=0, w=40, h=70):
    """Remonta o desenho com cada grupo deslocado.

    mov[grupo] = dict com:
      dx, dy: deslocamento inteiro do grupo inteiro;
      ponta: deslocamento horizontal da ponta (pé ou mão), com o topo do
             grupo preso (quadril ou ombro) e o meio em degraus;
      ergue: px que o pé sobe (só a parte de baixo da perna).
    """
    lim = _limites(ops)
    S = px.Sprite(w, h)
    for op in ops:
        pts, g = op[1], op[2]
        m = mov.get(g, {})
        top, bot = lim[g]
        pe = bot - 4                 # do cano do tênis para baixo, ponta cheia
        for (x, y), c in pts.items():
            nx, ny = x + m.get('dx', 0), y + m.get('dy', 0)
            ponta = m.get('ponta', 0)
            if ponta:
                if g.startswith('perna'):
                    t = (y - top) / max(1, pe - top)
                else:
                    t = (y - top) / max(1, bot - top)
                nx += _arred(ponta * max(0.0, min(1.0, t)))
            if m.get('ergue') and y >= bot - 7:
                ny -= m['ergue']
            S.px[(nx, ny + desce)] = c
    return S.image()


# ------------------------------------------------------------ ciclos
# Tabela 3.1 do manual (andando_frente, 4 quadros, 8 FPS, loop). Braços e
# pernas em oposição; o corpo sobe 1 px nas passagens e os pés ficam no chão.
ANDANDO = [
    # Q1, contato A: a perna da frente pisa adiante, a de trás recua;
    # o braço da frente recua 2 px e o de trás avança 2 px.
    {'perna_frente': {'ponta': 2}, 'perna_tras': {'ponta': -1},
     'braco_frente': {'ponta': -2}, 'braco_tras': {'ponta': 2}},
    # Q2, passagem A: corpo y-1; a da frente volta (x+1, levantada 1 px),
    # a de trás fica plantada; braços perto do neutro.
    {'corpo': {'dy': -1},
     'perna_frente': {'ponta': 1, 'ergue': 1}, 'perna_tras': {},
     'braco_frente': {'dy': -1, 'ponta': -1}, 'braco_tras': {'dy': -1, 'ponta': 1}},
    # Q3, contato B: a de trás pisa adiante, a da frente recua.
    {'perna_tras': {'ponta': 2}, 'perna_frente': {'ponta': -1},
     'braco_frente': {'ponta': 2}, 'braco_tras': {'ponta': -2}},
    # Q4, passagem B: corpo y-1; a de trás em x+1, levantada; a da frente
    # plantada; braços no neutro, invertidos em relação ao Q2.
    {'corpo': {'dy': -1},
     'perna_tras': {'ponta': 1, 'ergue': 1}, 'perna_frente': {},
     'braco_frente': {'dy': -1, 'ponta': 1}, 'braco_tras': {'dy': -1, 'ponta': -1}},
]


def andando(fn, regra=regra_humano, ciclo=ANDANDO):
    ops = agrupar(gravar(fn, 'parado'), regra)
    n = folga(fn)
    return [montar(ops, q, n) for q in ciclo]
