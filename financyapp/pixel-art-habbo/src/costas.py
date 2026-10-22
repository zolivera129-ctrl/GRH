"""Os humanos de costas (direção costas-dir: olhando para cima e para a
direita da tela, no sentido de -B).

De costas, o personagem continua virado para a direita: os tênis apontam
para a direita e a silhueta é a mesma do parado de frente. O que muda é o
lado que fica perto da câmera. De frente, o braço e a perna da frente ficam
à esquerda da tela; de costas, ficam à direita. Por isso:

- os braços trocam de lado (espelhados em torno do meio do tronco, x = 19)
  e de ordem: o da esquerda vai atrás do tronco, o da direita na frente;
- as pernas não espelham (o bico do tênis segue para a direita): a da
  direita passa a ser a da frente, com o pé 1 px mais baixo e desenhada por
  cima, e a da esquerda sobe 1 px e vai para trás;
- o rosto some: a nuca e o cabelo cobrem a cabeça e a orelha passa para a
  direita;
- a estampa, a gola em V e tudo o que é da frente da roupa saem; o que se
  vê por trás (alça, bolsa, cinto, barra do blazer) fica.

As peças vêm do desenho de frente gravado pelo anim.Gravador (mesmas
camadas, mesmos pixels, mesma paleta); só a nuca, o cabelo de trás e os
detalhes de costas de cada um são desenhados aqui.
"""
from collections import Counter

import anim
import chars
from px import Layer, Sprite, mix, mul

EIXO = 38          # espelho dos braços: x -> 38 - x (o meio do tronco, x = 19)


# ------------------------------------------------------------ ferramentas
def espelho(pts, eixo=EIXO):
    return {(eixo - x, y): c for (x, y), c in pts.items()}


def mover(pts, dx=0, dy=0):
    return {(x + dx, y + dy): c for (x, y), c in pts.items()}


def esticar(pts, corte, n):
    """Muda a altura de um membro a partir da linha corte: n > 0 alonga para
    baixo (a linha de cima do corte se repete), n < 0 encolhe para cima."""
    out = {}
    for (x, y), c in pts.items():
        if y < corte:
            out[(x, y)] = c
    for (x, y), c in pts.items():
        if y >= corte:
            out[(x, y + n)] = c
        elif n > 0 and y == corte - 1:
            for k in range(1, n + 1):
                out.setdefault((x, y + k), c)
    return out


def cor_mais_comum(pts):
    return Counter(pts.values()).most_common(1)[0][0]


class Frente:
    """O parado (ou o sentado) de frente, gravado e agrupado."""

    def __init__(self, fn, pose='parado'):
        self.ops = anim.agrupar(anim.gravar(fn, pose), anim.regra_humano)

    def grupo(self, g):
        """Todas as operações de um grupo, na ordem, juntas num dict."""
        out = {}
        for op in self.ops:
            if op[2] == g:
                out.update(op[1])
        return out

    def camada(self, cond):
        """Índice da primeira camada que satisfaz cond(caixa, pts)."""
        for i, op in enumerate(self.ops):
            if op[0] == 'camada' and cond(anim._caixa(op[1]), op[1]):
                return i
        raise LookupError('camada não encontrada')

    def com_detalhes(self, i):
        """A camada i e os pixels soltos que caíram nela, juntos."""
        out = dict(self.ops[i][1])
        for op in self.ops[i + 1:]:
            if op[0] == 'pixel' and op[3] == i:
                out.update(op[1])
        return out

    def so(self, i):
        return dict(self.ops[i][1])

    def entre(self, i0, i1):
        """Tudo o que foi desenhado entre as operações i0 e i1 (exclusive)."""
        out = {}
        for op in self.ops[i0 + 1:i1]:
            out.update(op[1])
        return out


def camada_de(pts, base, line=None):
    L = Layer(base, line)
    L.px = dict(pts)
    return L


def pernas_de_costas(F):
    """A perna da frente (esquerda, de frente) vira a de trás: sobe 1 px.
    A de trás (direita) vira a da frente: desce 1 px e vai por cima."""
    tras = esticar(F.grupo('perna_frente'), 56, -1)
    frente = esticar(F.grupo('perna_tras'), 56, 1)
    return tras, frente


def bracos_de_costas(F):
    """O braço de trás (direita, de frente) vai para a esquerda, atrás do
    tronco; o da frente vai para a direita, por cima."""
    return espelho(F.grupo('braco_tras')), espelho(F.grupo('braco_frente'))


def nuca(F, P, dy=0, sem_nariz_de=28):
    """A cabeça vista por trás: a mesma silhueta da de frente, sem o nariz,
    na cor da pele, luz da esquerda e sombra de 2 px à direita."""
    i = F.camada(lambda c, p: c[1] <= 10 + dy and c[3] >= 24 + dy and c[2] - c[0] >= 15
                 and cor_mais_comum(p) == P['sk'])
    hd = Layer(P['sk'], P['skline'])
    hd.px = {p: P['sk'] for p in F.so(i) if p[0] < sem_nariz_de}
    # tira o contorno antigo de baixo do queixo: de costas o queixo vira nuca
    hd.shade_side('r', 2, P['sks'])
    hd.outline()
    return hd


def pescoco(F, P, dy=0):
    i = F.camada(lambda c, p: c == (15, 22 + dy, 21, 28 + dy))
    return F.so(i)


def orelha_direita(P):
    """A orelha de frente, espelhada para o lado direito da cabeça."""
    ear = Layer(P['sk'], P['skline'])
    ear.rows({15: (24, 25), 16: (23, 26), 17: (23, 26), 18: (23, 26), 19: (24, 25)})
    ear.outline()
    ear.set(24, 17, P['sks'])
    ear.set(25, 17, P['sks'])
    ear.set(24, 16, P['sks'])
    return ear


# ------------------------------------------------------------ Guilherme
GUI = dict(sk=(0xC9, 0x8D, 0x5F), sks=(0xAD, 0x72, 0x49), skline=(0x7A, 0x4A, 0x2C),
           tee=(0xF7, 0xF7, 0xF3), tees=(0xDC, 0xDD, 0xE3), teeline=(0x9A, 0x9C, 0xA9),
           hair=(0x33, 0x23, 0x1A), haird=(0x1B, 0x12, 0x0D), hairl=(0x62, 0x43, 0x2F))


def _degrade(S, hd, P, dy, ate_x=27):
    """Laterais e nuca na régua: escuro logo abaixo dos cachos, clareando
    até a pele. As faixas sobem para a direita (a linha do cabelo fica mais
    alta perto da orelha) e se misturam em xadrez nas passagens."""
    tons = [mix(P['sks'], P['haird'], t) for t in (0.62, 0.48, 0.32)]
    pele = None
    for (x, y), c in hd.px.items():
        if x > ate_x:
            continue
        v = (y - dy - 10) + 0.35 * (x - 11)
        xad = (x + y) % 2
        if v < 4:
            t = tons[0]
        elif v < 5.5:
            t = tons[0] if xad else tons[1]
        elif v < 7.5:
            t = tons[1]
        elif v < 9:
            t = tons[1] if xad else tons[2]
        elif v < 10.5:
            t = tons[2]
        elif v < 11.5 and xad:
            t = tons[2]
        else:
            t = pele
        if t is None:
            continue
        S[(x, y)] = mul(t, 0.68) if c == P['skline'] else t


def guilherme_ops(pose='parado'):
    """Guilherme de costas, como lista de operações agrupadas (as mesmas do
    anim.montar): cachos em cima, laterais e nuca na régua, alça cruzando
    as costas do ombro esquerdo até a bolsa no quadril direito."""
    P = GUI
    F = Frente(chars.guilherme, pose)
    dy = chars.SIT_DY if pose == 'sentado' else 0
    ops = []

    def op(pts, g='corpo'):
        ops.append(['camada', dict(pts), g, None])

    braco_esq, braco_dir = bracos_de_costas(F)
    tronco = F.camada(lambda c, p: c[1] == 27 + dy and c[3] >= 44 + dy and c[2] - c[0] >= 15)
    op(braco_esq, 'braco_tras')
    if pose == 'sentado':
        # sentado, as pernas são as mesmas de frente (quadril no assento e
        # coxas para a direita), por baixo do tronco
        ult = max(i for i, o in enumerate(F.ops[:tronco]) if o[2] == 'braco_tras')
        op(F.entre(ult, tronco), 'pernas')
    else:
        perna_esq, perna_dir = pernas_de_costas(F)
        op(perna_esq, 'perna_tras')
        op(perna_dir, 'perna_frente')

    # tronco: a mesma camiseta, sem a estampa e sem a gola em V
    op(F.so(tronco))

    # alça e bolsa, espelhadas: a alça sai do ombro esquerdo e desce pelas
    # costas até a bolsa, no quadril direito
    preto = (0x1E, 0x1E, 0x23)
    alca = F.camada(lambda c, p: c[0] >= 14 and c[2] >= 24 and c[3] <= 41 + dy
                    and cor_mais_comum(p) == preto)
    bolsa = F.camada(lambda c, p: c[0] <= 10 and c[3] >= 46 + dy and cor_mais_comum(p) == preto)
    op(espelho(F.com_detalhes(alca)))
    op(espelho(F.so(bolsa)))

    op(braco_dir, 'braco_frente')

    # pescoço e a gola de trás, mais alta que a da frente
    op(pescoco(F, P, dy))
    gola = {(x, 27 + dy): P['teeline'] for x in range(15, 22)}
    gola[(14, 28 + dy)] = gola[(22, 28 + dy)] = P['teeline']
    op(gola)

    # cabeça por trás, com o degradê
    hd = nuca(F, P, dy)
    cab = dict(hd.px)
    _degrade(cab, hd, P, dy)
    op(cab)
    op(mover(orelha_direita(P).px, 0, dy))

    # cachos: o mesmo volume de cima, até a linha 10, com a borda de baixo
    # irregular na nuca
    i = F.camada(lambda c, p: c[1] <= 1 + dy and c[2] - c[0] >= 20)
    cachos = {p: c for p, c in F.so(i).items() if p[1] - dy <= 10}
    L = camada_de(cachos, P['hair'], P['haird'])
    L.outline()
    for x in (12, 13, 19, 24, 25, 29):
        L.px.pop((x, 10 + dy), None)
    op(L.px)
    return ops


def guilherme(pose='parado'):
    return anim.montar(guilherme_ops(pose), {}, anim.folga(chars.guilherme))
