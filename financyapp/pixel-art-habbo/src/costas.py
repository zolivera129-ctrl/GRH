"""Os humanos de costas (direção costas-dir: olhando para cima e para a
direita da tela, no sentido de -B).

De costas, o personagem continua virado para a direita: os sapatos apontam
para a direita e a silhueta é a mesma do parado de frente. O que muda é o
lado que fica perto da câmera. De frente, o braço e a perna da frente ficam
à esquerda da tela; de costas, ficam à direita. Por isso:

- os braços trocam de lado (espelhados em torno do meio do tronco, x = 19)
  e de ordem: o da esquerda vai atrás do tronco, o da direita na frente;
- as pernas não espelham (o bico do sapato segue para a direita): a da
  direita passa a ser a da frente, com o pé 1 px mais baixo e desenhada por
  cima, e a da esquerda sobe 1 px e vai para trás;
- o rosto some: a nuca e o cabelo cobrem a cabeça, a orelha passa para a
  direita e, de quem usa óculos, aparece a haste;
- a estampa, a frente aberta do blazer e tudo o que é da frente da roupa
  saem; o que se vê por trás (alça, bolsa, cinto, gola) fica.

As peças vêm do desenho de frente gravado pelo anim.Gravador (mesmas
camadas, mesmos pixels, mesma paleta); só a nuca, o cabelo de trás e os
detalhes de costas de cada um são desenhados aqui. As cores do cabelo e
das roupas repetem as do chars.py.

Coordenadas: as do desenho de frente, antes de descer até a âncora; a pose
sentada soma chars.SIT_DY em y, como no chars.py.
"""
from collections import Counter

import anim
import chars
from chars import GOLD, GOLDD, curls, strands
from px import Layer, mix, mul, rgb

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


def linhas(spec):
    """{y: (x0, x1)} ou {y: [(x0, x1), ...]} -> conjunto de pontos."""
    pts = set()
    for y, segs in spec.items():
        if isinstance(segs[0], int):
            segs = [segs]
        for x0, x1 in segs:
            pts.update((x, y) for x in range(x0, x1 + 1))
    return pts


class Frente:
    """O parado (ou o sentado) de frente, gravado e agrupado."""

    def __init__(self, fn, pose='parado'):
        self.ops = anim.agrupar(anim.gravar(fn, pose), anim.regra_humano)

    def grupo(self, g):
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
        out = {}
        for op in self.ops[i0 + 1:i1]:
            out.update(op[1])
        return out


# ------------------------------------------------------------ o boneco
class Costas:
    """Monta um humano de costas. Uso:

        C = Costas(chars.saldanha, pose)
        C.corpo(gola=...)           # braços, pernas, tronco, pescoço, gola
        cab = C.cabeca()            # a cabeça por trás, para o cabelo pintar
        ...                         # cabelo, orelha, detalhes
        return C.ops

    Cada operação é ['camada', pts, grupo, None], o mesmo formato que o
    anim.montar remonta (e anima)."""

    def __init__(self, fn, pose='parado'):
        self.fn, self.pose = fn, pose
        self.F = Frente(fn, pose)
        self.dy = chars.SIT_DY if pose == 'sentado' else 0
        self.ops = []
        d = self.dy
        hd = self.F.so(self.F.camada(lambda c, p: c == (10, 9 + d, 28, 25 + d)))
        self.P = {'sk': cor_mais_comum(hd), 'skline': hd[(14, 9 + d)], 'sks': hd[(11, 15 + d)]}
        self._cabeca = hd

    # coordenadas do desenho de frente -> as desta pose
    def p(self, x, y):
        return (x, y + self.dy)

    def pts(self, conj, cor):
        return {(x, y + self.dy): cor for (x, y) in conj}

    def op(self, pts, g='corpo'):
        if pts:
            self.ops.append(['camada', dict(pts), g, None])

    def tronco_idx(self):
        d = self.dy
        return self.F.camada(lambda c, p: c[1] == 27 + d and c[3] >= 40 + d and c[2] - c[0] >= 15)

    def corpo(self, gola=None, por_cima_do_tronco=(), sem_braco_frente=False):
        """Braço esquerdo atrás, pernas, tronco, o que vai por cima do tronco
        (alça, cinto), braço direito na frente, pescoço e gola.
        gola = (cor da gola, cor do contorno) ou None."""
        F = self.F
        tronco = self.tronco_idx()
        self.op(espelho(F.grupo('braco_tras')), 'braco_tras')
        if self.pose == 'sentado':
            # sentado, as pernas são as de frente (quadril no assento e coxas
            # para a direita), por baixo do tronco
            ult = max(i for i, o in enumerate(F.ops[:tronco]) if o[2] == 'braco_tras')
            self.op(F.entre(ult, tronco), 'pernas')
        else:
            self.op(esticar(F.grupo('perna_frente'), 56, -1), 'perna_tras')
            self.op(esticar(F.grupo('perna_tras'), 56, 1), 'perna_frente')
        self.op(F.so(tronco))
        for pts in por_cima_do_tronco:
            self.op(pts)
        if not sem_braco_frente:
            self.braco_frente()
        self.op(F.so(F.camada(lambda c, p: c == (15, 22 + self.dy, 21, 28 + self.dy))))
        if gola:
            cor, linha = gola
            g = self.pts(linhas({27: (15, 21)}), cor)
            g.update(self.pts({(14, 27), (22, 27), (14, 28), (22, 28)}, linha))
            self.op(g)

    def braco_frente(self):
        self.op(espelho(self.F.grupo('braco_frente')), 'braco_frente')

    def cabeca(self, sem_nariz_de=28):
        """A cabeça vista por trás: a silhueta da de frente sem o nariz, na
        cor da pele, luz da esquerda e sombra de 2 px à direita. Devolve o
        dict de pixels para o cabelo pintar por cima; entra com C.op()."""
        P = self.P
        hd = Layer(P['sk'], P['skline'])
        hd.px = {p: P['sk'] for p in self._cabeca if p[0] < sem_nariz_de}
        hd.shade_side('r', 2, P['sks'])
        hd.outline()
        self.contorno_cabeca = {p for p, c in hd.px.items() if c == P['skline']}
        return dict(hd.px)

    def orelha(self):
        """A orelha de frente, espelhada para o lado direito da cabeça."""
        P = self.P
        ear = Layer(P['sk'], P['skline'])
        ear.rows({15: (24, 25), 16: (23, 26), 17: (23, 26), 18: (23, 26), 19: (24, 25)})
        ear.outline()
        ear.set(24, 17, P['sks'])
        ear.set(25, 17, P['sks'])
        ear.set(24, 16, P['sks'])
        self.op(mover(ear.px, 0, self.dy))

    def haste(self, cor):
        """A haste dos óculos, saindo da orelha para a frente do rosto."""
        self.op(self.pts({(26, 15), (27, 15)}, cor))

    def argola(self, x=24, y=20, ouro=GOLD, escuro=GOLDD):
        """A argola da orelha direita (a de frente, espelhada)."""
        pts = {}
        for dx, dy in ((0, 0), (1, 1), (1, 2), (0, 3), (-1, 2), (-1, 1)):
            pts[self.p(x + dx, y + dy)] = ouro if dy < 2 else escuro
        self.op(pts)

    def cabelo(self, cab, regiao, base, linha, tex=None, contorno=True, tirar=()):
        """Pinta o cabelo: regiao é o conjunto de pontos (coordenadas de
        frente) que o cabelo cobre, dentro ou fora da cabeça. Devolve a
        camada, já posta na lista."""
        L = Layer(base, linha)
        for (x, y) in regiao:
            L.set(x, y + self.dy)
        if tex:
            L.recolor(lambda x, y, c: tex(x, y - self.dy, c))
        if contorno:
            L.outline()
        for p in tirar:
            L.px.pop(self.p(*p), None)
        for p in list(L.px):
            cab.pop(p, None)
        self.op(cab)
        self.op(L.px)
        return L


def cobre_cabeca(C, nuca_y, orelha_y=14, meio=None):
    """Os pontos da cabeça que o cabelo cobre: tudo até a linha da nuca à
    esquerda (atrás) e até em cima da orelha à direita, com um degrau no
    meio. nuca_y e orelha_y em coordenadas de frente."""
    meio = meio if meio is not None else (nuca_y + orelha_y) // 2
    out = set()
    for (x, y) in C._cabeca:
        y0 = y - C.dy
        if x >= 28:
            continue
        lim = nuca_y if x <= 20 else (meio if x <= 22 else orelha_y)
        if y0 <= lim:
            out.add((x, y0))
    return out


def degrade(C, cab, haird, ate_x=27, v0=10):
    """Laterais e nuca na régua: escuro logo abaixo do cabelo, clareando até
    a pele. As faixas sobem para a direita (a linha do cabelo fica mais alta
    perto da orelha) e se misturam em xadrez nas passagens."""
    P = C.P
    tons = [mix(P['sks'], haird, t) for t in (0.62, 0.48, 0.32)]
    for (x, y), c in list(cab.items()):
        if x > ate_x:
            continue
        v = (y - C.dy - v0) + 0.35 * (x - 11)
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
            continue
        cab[(x, y)] = mul(t, 0.68) if c == P['skline'] else t


def barba_lateral(C, linhas_, base, escura, rala=False):
    """A barba vista por trás: só a borda do maxilar, à direita, abaixo da
    orelha."""
    pts = {}
    for (x, y) in linhas(linhas_):
        p = C.p(x, y)
        if rala:
            if (x + y) % 2:
                pts[p] = mix(C.P['sks'], escura, 0.35)
        else:
            pts[p] = escura if (x * 3 + y) % 5 == 0 else base
    C.op(pts)


def gola(cor, linha):
    return (cor, linha)


# ------------------------------------------------------------ os doze
def guilherme(pose='parado'):
    """Cachos em cima, laterais e nuca na régua, haste dos óculos, alça
    cruzando as costas do ombro esquerdo até a bolsa no quadril direito."""
    C = Costas(chars.guilherme, pose)
    F, d = C.F, C.dy
    hair, haird = rgb('#33231A'), rgb('#1B120D')
    preto = rgb('#1E1E23')
    alca = F.camada(lambda c, p: c[0] >= 14 and c[2] >= 24 and c[3] <= 41 + d
                    and cor_mais_comum(p) == preto)
    bolsa = F.camada(lambda c, p: c[0] <= 10 and c[3] >= 46 + d and cor_mais_comum(p) == preto)
    C.corpo(gola=gola(rgb('#9A9CA9'), rgb('#9A9CA9')),
            por_cima_do_tronco=(espelho(F.com_detalhes(alca)), espelho(F.so(bolsa))))
    cab = C.cabeca()
    degrade(C, cab, haird)
    C.op(cab)
    C.orelha()
    C.haste(rgb('#26262B'))
    # cachos: o mesmo volume de cima, até a linha 10, com a borda de baixo
    # irregular na nuca
    i = F.camada(lambda c, p: c[1] <= 1 + d and c[2] - c[0] >= 20)
    cachos = {p: c for p, c in F.so(i).items() if p[1] - d <= 10}
    L = Layer(hair, haird)
    L.px = cachos
    L.outline()
    for x in (12, 13, 19, 24, 25, 29):
        L.px.pop((x, 10 + d), None)
    C.op(L.px)
    return C.ops


def gabriel(pose='parado'):
    """Boné de costas, com a abertura do snapback e a ponta da aba
    aparecendo à direita; nuca curta, barba no maxilar e o alargador."""
    C = Costas(chars.gabriel, pose)
    cap, capd, capl = rgb('#202024'), rgb('#0E0E10'), rgb('#3C3C45')
    beard, beardd = rgb('#3E2819'), rgb('#26170E')
    C.corpo(gola=gola(rgb('#221E20'), rgb('#221E20')))
    cab = C.cabeca()
    degrade(C, cab, beardd, v0=11)
    C.op(cab)
    C.orelha()
    barba_lateral(C, {20: (26, 27), 21: (25, 27), 22: (24, 26), 23: (24, 26), 24: (23, 25), 25: (22, 24)},
                  beard, beardd)
    alarg = {C.p(24, 19): rgb('#1A1214'), C.p(25, 19): rgb('#8A2A30'),
             C.p(24, 20): rgb('#1A1214'), C.p(25, 20): rgb('#1A1214')}
    C.op(alarg)
    C.haste(rgb('#141416'))
    # a ponta da aba, para a frente (à direita), atrás da copa
    aba = Layer(cap, capd)
    aba.rows({10 + C.dy: (26, 31), 11 + C.dy: (26, 32)})
    aba.outline()
    C.op(aba.px)
    # a copa de seis gomos, com a costura do meio e o fecho atrás
    cp = Layer(cap, capd)
    cp.rows({y + C.dy: s for y, s in {3: (14, 23), 4: (12, 25), 5: (11, 26), 6: (10, 27), 7: (10, 27),
                                       8: (9, 27), 9: (9, 27), 10: (9, 27), 11: (9, 26)}.items()})
    cp.recolor(lambda x, y, c: capl if (y - C.dy in (4, 5) and 13 <= x <= 19) else None)
    cp.outline()
    for y in range(4, 10):
        cp.set(18, y + C.dy, capd)
    cp.set(18, 2 + C.dy, capd)              # botão
    for x, y in ((14, 9), (15, 9), (16, 9), (17, 9), (14, 10), (17, 10)):
        cp.set(x, y + C.dy, capd)          # o arco da abertura
    for x in (15, 16):
        cp.set(x, 10 + C.dy, beardd)        # cabelo aparecendo no fecho
    for x in range(13, 19):
        cp.set(x, 11 + C.dy, capl)          # a tira do snapback
    cp.set(16, 11 + C.dy, rgb('#9A9AA0'))
    C.op(cp.px)
    return C.ops


def saldanha(pose='parado'):
    """Grisalho penteado para trás, gola da polo, cinto marrom sem a fivela,
    haste dos óculos e a barba branca curta no maxilar."""
    C = Costas(chars.saldanha, pose)
    grey, greyd, greyl = rgb('#8E8E93'), rgb('#5E5E65'), rgb('#C9C9CD')
    navy, navy_l = rgb('#0A0F1E'), rgb('#34446D')
    cinto = {}
    for x in range(11, 28):
        cinto[C.p(x, 44)] = rgb('#8A5533')
        cinto[C.p(x, 45)] = rgb('#5E3820')
    for x in (13, 19, 25):
        cinto[C.p(x, 44)] = rgb('#A5A8AD') if x != 19 else rgb('#6E4026')
    C.corpo(gola=gola(navy_l, navy), por_cima_do_tronco=(cinto,))
    cab = C.cabeca()
    reg = cobre_cabeca(C, 20, 13) | linhas({6: (15, 23), 7: (13, 25), 8: (11, 26), 9: (10, 27),
                                             10: (10, 26), 11: (10, 26)})

    def pentes(x, y, c):
        # penteado para trás: fios na vertical, mais claros no alto
        if (x * 2 + y // 3) % 5 == 0:
            return greyl
        if (x + y // 2) % 4 == 0:
            return greyd
        return None
    C.cabelo(cab, reg, grey, greyd, pentes, tirar=((10, 20), (20, 21)))
    C.orelha()
    barba_lateral(C, {20: (25, 26), 21: (25, 26), 22: (24, 25), 23: (23, 25)},
                  mix(rgb('#BE8763'), greyl, 0.5), mix(rgb('#BE8763'), greyl, 0.3))
    C.haste(rgb('#1C1C20'))
    return C.ops


def caio(pose='parado'):
    """Cachos curtos com a nuca acertada, gola da sobrecamisa, cordão do
    crachá passando atrás do pescoço e a barba por fazer no maxilar."""
    C = Costas(chars.caio, pose)
    hair, haird, hairl = rgb('#2B1D16'), rgb('#160F0B'), rgb('#55392A')
    C.corpo(gola=gola(rgb('#A3B79D'), rgb('#465843')))
    C.op(C.pts(linhas({26: (15, 21)}), rgb('#1D2A4C')))       # cordão do crachá
    cab = C.cabeca()
    degrade(C, cab, haird, v0=14)
    reg = cobre_cabeca(C, 15, 12) | linhas({4: [(14, 16), (18, 21), (23, 25)], 5: (12, 26),
                                             6: (11, 27), 7: (10, 27), 8: (10, 27), 9: (10, 27),
                                             10: (10, 27), 11: (10, 27), 12: (10, 26)})
    C.cabelo(cab, reg, hair, haird, curls(hair, haird, hairl), tirar=((10, 15), (14, 16), (18, 16)))
    C.orelha()
    barba_lateral(C, {20: (25, 27), 21: (24, 27), 22: (24, 26), 23: (23, 26), 24: (22, 25)},
                  None, haird, rala=True)
    return C.ops


def vivi(pose='parado'):
    """O volume de cachos cobre a cabeça e desce pelas costas até a
    cintura; a mão direita aparece abaixo dele. Cós alto da pantalona."""
    C = Costas(chars.vivi, pose)
    hair, haird, hairl, hairll = rgb('#3B2417'), rgb('#21130B'), rgb('#7E5130'), rgb('#B07A42')
    cream = (rgb('#F0E8D9'), rgb('#D6CBB8'))
    cos = {}
    for x in range(12, 27):
        cos[C.p(x, 41)] = cream[0]
        cos[C.p(x, 42)] = cream[1]
    C.corpo(gola=None, por_cima_do_tronco=(cos,))
    cab = C.cabeca()
    tex = curls(hair, haird, hairl)
    reg = linhas({1: (12, 24), 2: (9, 27), 3: (7, 29), 4: (6, 30)})
    reg |= linhas({y: (5, 31) for y in range(5, 9)})
    reg |= linhas({y: (4, 31) for y in range(9, 15)})
    reg |= linhas({y: (3, 30) for y in range(15, 23)})
    reg |= linhas({y: (3, 29) for y in range(23, 29)})
    reg |= linhas({y: (4, 28) for y in range(29, 35)})
    reg |= linhas({y: (5, 27) for y in range(35, 39)})
    reg |= linhas({39: (6, 25), 40: (7, 24), 41: [(8, 13), (15, 22)], 42: [(9, 11), (17, 20)]})
    C.cabelo(cab, reg, hair, haird,
             lambda x, y, c: hairll if (x * 5 + y * 3) % 17 == 0 else tex(x, y, c),
             tirar=((3, 16), (3, 21), (4, 27), (4, 33), (31, 12), (30, 19), (28, 31), (5, 37)))
    return C.ops


def nina(pose='parado'):
    """Coque alto bagunçado, o cabelo puxado subindo para ele, mechas soltas
    na nuca, gola do blazer e a argola."""
    C = Costas(chars.nina, pose)
    hair, haird, hairl = rgb('#3A2418'), rgb('#21140C'), rgb('#6A4430')
    C.corpo(gola=gola(rgb('#76824A'), rgb('#2A3018')))
    cab = C.cabeca()
    reg = cobre_cabeca(C, 18, 13) | linhas({0: (14, 19), 1: (12, 21), 2: (11, 22), 3: (11, 23),
                                             4: (11, 23), 5: (12, 23), 6: (12, 24), 7: (11, 26),
                                             8: (10, 27), 9: (10, 27), 10: (10, 26)})

    def puxado(x, y, c):
        # fios subindo para o coque (o coque, em cima, tem textura própria)
        if y <= 6:
            return strands(hair, haird, hairl)(x, y, c)
        k = x * 2 + (y if x < 17 else -y)
        return hairl if k % 7 == 0 else (haird if k % 5 == 0 else None)
    L = C.cabelo(cab, reg, hair, haird, puxado, tirar=((10, 18), (20, 19)))
    for x, y in ((13, 2), (16, 1), (19, 3), (14, 4), (20, 5)):
        L.px[C.p(x, y)] = hairl
    for x, y in ((12, 6), (11, 7), (17, 6), (18, 7), (19, 6)):
        L.px[C.p(x, y)] = haird         # a base do coque
    C.orelha()
    soltas = {}
    for x, y in ((11, 19), (12, 20), (11, 21), (13, 20), (14, 21), (27, 12), (27, 13), (26, 14),
                 (10, 4), (24, 2), (25, 3)):
        soltas[C.p(x, y)] = haird
    C.op(soltas)
    C.argola(24, 20)
    return C.ops


def otto(pose='parado'):
    """Calvo no alto com brilho, a coroa de cabelo branco e fofo de orelha a
    orelha, a barba branca no maxilar, a haste de tartaruga e a gola da
    camisa por cima do colete."""
    C = Costas(chars.otto, pose)
    grey, greyd, greyl = rgb('#E6E5E2'), rgb('#A8A6A0'), rgb('#FFFFFF')
    C.corpo(gola=gola(rgb('#F6F5F0'), rgb('#9C9EA6')))
    cab = C.cabeca()
    for x, y in ((15, 10), (16, 10), (17, 10), (14, 11), (15, 11), (13, 12)):
        cab[C.p(x, y)] = rgb('#E6B894')
    cab[C.p(16, 10)] = rgb('#F6D2B4')
    C.op(cab)
    C.orelha()
    barba_lateral(C, {20: (26, 27), 21: (25, 27), 22: (25, 27), 23: (24, 26), 24: (24, 26),
                      25: (23, 25), 26: (22, 24)},
                  rgb('#E8E6E2'), rgb('#A9A6A0'))
    # a coroa: fina acima da orelha, engrossando atrás e embaixo
    reg = linhas({13: (8, 14), 14: (7, 16), 15: (7, 18), 16: (7, 20), 17: (7, 21), 18: (7, 22),
                  19: (7, 22), 20: (8, 22), 21: (9, 21), 22: (10, 19)})
    reg |= linhas({13: (22, 26), 14: (21, 27)})

    def fofo(x, y, c):
        if (x * 3 + y * 2) % 7 == 0:
            return greyd
        if (x + y) % 3 == 0:
            return greyl
        return None
    hr = Layer(grey, greyd)
    for (x, y) in reg:
        hr.set(x, y + C.dy)
    hr.recolor(lambda x, y, c: fofo(x, y - C.dy, c))
    hr.outline()
    for (x, y) in hr.edges():
        if (x * 5 + y * 3) % 4 == 0 and (x < 22 or y - C.dy == 13):
            hr.px.pop((x, y), None)
    C.op(hr.px)
    C.haste(rgb('#5A3418'))
    return C.ops


def pra_ontem(pose='parado'):
    """Topete espetado escuro, a nuca e a têmpora perto da orelha
    grisalhas, haste dos óculos pretos e a gola branca da camisa por cima
    do paletó."""
    C = Costas(chars.pra_ontem, pose)
    grey, greyd, greyl = rgb('#34343A'), rgb('#1C1C20'), rgb('#56565E')
    silver, silverd = rgb('#C2C2C8'), rgb('#8E8E96')
    C.corpo(gola=gola(rgb('#F6F5F0'), rgb('#17171B')))
    cab = C.cabeca()
    reg = cobre_cabeca(C, 20, 13) | linhas({0: [(16, 17), (22, 23)], 1: [(15, 18), (21, 24), (26, 27)],
                                             2: [(14, 19), (20, 28)], 3: (13, 28), 4: (12, 28),
                                             5: (11, 28), 6: (10, 28), 7: (10, 28), 8: (9, 27),
                                             9: (9, 27), 10: (9, 26), 11: (9, 26)})
    reg |= linhas({y: (9, 11) for y in range(12, 21)})

    def grisalho(x, y, c):
        # escuro no alto e atrás; prata na nuca (de baixo para cima, em
        # xadrez na passagem) e na têmpora, acima da orelha
        prata = silverd if (x * 3 + y) % 7 == 0 else silver
        if y >= 18 or (y == 17 and (x + y) % 2):
            return prata
        if x >= 21 and y >= 10:
            return prata
        if x >= 20 and y == 9 and (x + y) % 2:
            return prata
        if (x + y * 2) % 5 == 0:
            return greyl
        return None
    C.cabelo(cab, reg, grey, greyd, grisalho, tirar=((9, 20), (21, 21)))
    C.orelha()
    C.haste(rgb('#141416'))
    return C.ops


def iris(pose='parado'):
    """O black power inteiro, redondo, cobrindo a cabeça e as orelhas; a gola
    do blazer aparece embaixo."""
    C = Costas(chars.iris, pose)
    hair, haird, hairl, hairll = rgb('#2B1A10'), rgb('#160D07'), rgb('#5A3A22'), rgb('#8A5A30')
    tex = curls(hair, haird, hairl)
    C.corpo(gola=gola(rgb('#466A50'), rgb('#13221A')))
    cab = C.cabeca()
    reg = {(x, y) for y in range(0, 26) for x in range(4, 36)
           if ((x - 19.5) / 14.5) ** 2 + ((y - 11.5) / 12.5) ** 2 <= 1}
    L = C.cabelo(cab, reg, hair, haird,
                 lambda x, y, c: hairll if (x * 5 + y * 3) % 19 == 0 else tex(x, y, c))
    for (x, y) in L.edges():
        if (x * 7 + y * 3) % 5 == 0:
            L.px.pop((x, y), None)
    return C.ops


def joana(pose='parado'):
    """A cabeça raspada com o brilho no alto, à esquerda (de onde vem a
    luz), a orelha com os piercings e a argola grande, gola do blazer."""
    C = Costas(chars.joana, pose)
    C.corpo(gola=gola(rgb('#EAD8BA'), rgb('#8A7350')))
    cab = C.cabeca()
    shine, shine2 = rgb('#B8784C'), rgb('#DCA27A')
    for x, y in ((15, 10), (16, 10), (17, 10), (14, 11), (15, 11), (13, 12)):
        cab[C.p(x, y)] = shine
    cab[C.p(16, 10)] = shine2
    cab[C.p(17, 10)] = shine2
    C.op(cab)
    C.orelha()
    furos = {C.p(26, 15): GOLD, C.p(26, 17): GOLD, C.p(25, 15): GOLDD}
    for x, y in ((14, 20), (13, 21), (12, 22), (12, 23), (12, 24), (13, 25), (14, 26), (15, 25),
                 (16, 24), (16, 23), (16, 22), (15, 21)):
        furos[C.p(EIXO - x, y)] = GOLD if y < 23 else GOLDD
    C.op(furos)
    return C.ops


def malu(pose='parado'):
    """Cabelo liso, preto-azulado, cobrindo a cabeça e descendo reto pelas
    costas; a haste âmbar dos óculos de sol aparece à direita."""
    C = Costas(chars.malu, pose)
    hair, haird = rgb('#151A28'), rgb('#07090F')
    blue, sheen = rgb('#2A3656'), rgb('#4A5C8E')

    def sleek(x, y, c):
        if y < 10 and (x + y) % 4 == 0:
            return sheen
        if x % 4 == 1:
            return blue
        if x % 4 == 3:
            return haird
        return None
    C.corpo(gola=None)
    cab = C.cabeca()
    reg = linhas({4: (14, 24), 5: (11, 27)})
    reg |= linhas({y: (9, 29) for y in range(6, 10)})
    reg |= linhas({y: (7, 30) for y in range(10, 31)})
    reg |= linhas({y: (8, 29) for y in range(31, 38)})
    reg |= linhas({y: (9, 28) for y in range(38, 41)})
    reg |= linhas({41: (10, 27)})
    C.cabelo(cab, reg, hair, haird, sleek)
    amber = rgb('#C9853E')
    C.op(C.pts(linhas({7: (26, 30)}), amber))
    return C.ops


def duda(pose='parado'):
    """O cabelo liso puxado para o coque alto de cachos, a nuca à mostra,
    gola do blazer e a argola."""
    C = Costas(chars.duda, pose)
    hair, haird, hairl = rgb('#24160E'), rgb('#120A05'), rgb('#5A3A22')
    C.corpo(gola=gola(rgb('#66704A'), rgb('#22271A')))
    cab = C.cabeca()
    reg = cobre_cabeca(C, 19, 13) | linhas({5: (13, 24), 6: (11, 26), 7: (10, 27), 8: (9, 27),
                                             9: (9, 27), 10: (9, 26)})
    reg |= linhas({y: (9, 11) for y in range(11, 19)})

    def puxado(x, y, c):
        k = x * 2 + (y if x < 18 else -y)
        return hairl if k % 7 == 0 else None
    C.cabelo(cab, reg, hair, haird, puxado, tirar=((10, 19), (20, 20)))
    C.orelha()
    bun = Layer(hair, haird)
    bun.rows({y + C.dy: s for y, s in {0: (15, 21), 1: (13, 23), 2: (12, 24), 3: (12, 24),
                                        4: (13, 23), 5: (14, 22)}.items()})
    bun.recolor(lambda x, y, c: curls(hair, haird, hairl)(x, y - C.dy, c))
    bun.outline()
    C.op(bun.px)
    C.argola(23, 19)
    return C.ops


HUMANOS = {
    'guilherme': (chars.guilherme, guilherme),
    'saldanha': (chars.saldanha, saldanha),
    'caio': (chars.caio, caio),
    'vivi': (chars.vivi, vivi),
    'gabriel': (chars.gabriel, gabriel),
    'nina': (chars.nina, nina),
    'otto': (chars.otto, otto),
    'sr_pra_ontem': (chars.pra_ontem, pra_ontem),
    'iris': (chars.iris, iris),
    'joana': (chars.joana, joana),
    'malu': (chars.malu, malu),
    'duda': (chars.duda, duda),
}


def ops(cid, pose='parado'):
    return HUMANOS[cid][1](pose)


def imagem(cid, pose='parado'):
    """O de costas pronto, já na linha da âncora (anim.PE)."""
    frente, costas = HUMANOS[cid]
    return anim.montar(costas(pose), {}, anim.folga(frente))
