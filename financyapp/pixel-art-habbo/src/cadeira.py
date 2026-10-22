"""Levantar e sentar (fase 4 do manual, §4.7 e §4.8).

No nosso desenho, o sentado fica só 3 px abaixo do em pé (chars.SIT_DY, como
no Habbo): o corpo desce até o assento, a 14 px do chão, e as pernas dobram
para a frente. O manual fala do quadril subindo 9 px; aqui os 3 px se
distribuem pelos quadros do meio, e as pernas passam por duas poses meio
dobradas, desenhadas com as cores da calça e os sapatos de cada um.

O primeiro e o último quadro são exatamente o sentado e o parado de frente;
a âncora não mexe.

Coordenadas: as do desenho de frente em pé (sem SIT_DY), antes de descer
até a âncora (anim.folga).
"""
import math
from collections import Counter

import anim
import chars
import costas
from px import Layer

# por quadro: (quanto o corpo está abaixo do em pé, inclinação da cabeça,
# inclinação do tronco, pernas: 0 = sentado, 1 = em pé)
LEVANTANDO = [
    (3, 0, 0, 0.0),     # Q1 sentado
    (3, 2, 1, 0.0),     # Q2 tronco vai à frente, quadril ainda no assento
    (2, 2, 1, 0.35),    # Q3 quadril sobe, joelhos começam a esticar
    (1, 1, 1, 0.7),     # Q4 pernas quase retas, tronco menos inclinado
    (0, 1, 0, 1.0),     # Q5 de pé, a cabeça termina de voltar
    (0, 0, 0, 1.0),     # Q6 parado
]
SENTANDO = [
    (0, 0, 0, 1.0),     # Q1 parado
    (0, 1, 1, 0.85),    # Q2 tronco à frente, joelhos começam a dobrar
    (1, 2, 1, 0.6),     # Q3 quadril desce
    (2, 2, 1, 0.3),     # Q4 pernas avançam dobradas
    (3, 1, 0, 0.0),     # Q5 no assento
    (3, 0, 0, 0.0),     # Q6 sentado
]
CINTURA = 45            # o tronco inclina acima desta linha (desenho de frente)


def _cores(pts):
    base = Counter(pts.values()).most_common(1)[0][0]
    topo = min(y for _, y in pts)
    linha = pts[min((p for p in pts if p[1] == topo), key=lambda p: p[0])]
    meio = sorted({y for _, y in pts})[len({y for _, y in pts}) // 2]
    xs = sorted(x for x, y in pts if y == meio)
    sombra = pts[(xs[-2], meio)]
    return base, sombra, linha


def _capsula(p0, p1, r):
    (x0, y0), (x1, y1) = p0, p1
    pts = set()
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy or 1e-9
    for y in range(math.floor(min(y0, y1) - r) - 1, math.ceil(max(y0, y1) + r) + 2):
        for x in range(math.floor(min(x0, x1) - r) - 1, math.ceil(max(x0, x1) + r) + 2):
            t = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / L2))
            if (x - (x0 + t * dx)) ** 2 + (y - (y0 + t * dy)) ** 2 <= r * r:
                pts.add((x, y))
    return pts


def _lerp(a, b, s):
    return tuple(a[i] + (b[i] - a[i]) * s for i in range(len(a)))


class Pernas:
    """As pernas de um personagem em qualquer ponto entre sentado (s = 0) e
    em pé (s = 1): calça com as cores da perna em pé, sapatos copiados do
    desenho em pé e levados até onde pisam no sentado."""

    def __init__(self, fn):
        F = costas.Frente(fn, 'parado')
        S = anim.agrupar(anim.gravar(fn, 'sentado'), anim.regra_humano)
        self.topo = min(y for op in F.ops if op[2].startswith('perna') for _, y in op[1])
        self.calca = {}
        self.sapato = {}
        for lado, g in (('frente', 'perna_frente'), ('tras', 'perna_tras')):
            ops = [op for op in F.ops if op[2] == g]
            camadas = [op for op in ops if op[0] == 'camada']
            calca = max(camadas, key=lambda op: len(op[1]))
            self.calca[lado] = _cores(calca[1])
            sap = {}
            for op in ops:
                if op is calca:
                    continue
                if op[0] == 'camada' or op[3] != calca[3]:
                    for p, c in op[1].items():
                        if p[1] >= 56:
                            sap[p] = c
            self.sapato[lado] = sap
        # onde os sapatos pisam no sentado: o deslocamento em x do sapato
        sx = {}
        for lado in ('frente', 'tras'):
            x_em_pe = min(x for x, _ in self.sapato[lado])
            sx[lado] = x_em_pe
        pes_sentado = sorted({min(x for x, _ in op[1]) for op in S
                              if op[0] == 'camada' and op[2].startswith('perna') and min(y for _, y in op[1]) >= 56})
        # no sentado o de trás pisa mais à direita
        self.dx_sentado = {'frente': pes_sentado[0] - sx['frente'], 'tras': pes_sentado[-1] - sx['tras']}
        self.largo = 'vivi' in fn.__name__

    def desenhar(self, s):
        """Operações [('camada', pts, 'pernas', None)] das pernas em s."""
        topo = self.topo
        hip_y = round(topo + (49 - topo) * (1 - s))  # no sentado, o quadril fica em 46 + SIT_DY
        geo = {
            'tras': {'quadril': ((22.5, topo + 3), (20.0, 50.0)), 'joelho': ((22.5, 51.0), (30.0, 50.5)),
                     'tornozelo': ((22.5, 55.5), (30.0, 55.5))},
            'frente': {'quadril': ((15.5, topo + 3), (16.0, 51.0)), 'joelho': ((15.5, 52.0), (25.0, 52.5)),
                       'tornozelo': ((15.5, 56.5), (25.0, 56.5))},
        }
        ops = []
        for lado in ('tras', 'frente'):
            g = geo[lado]
            q = _lerp(g['quadril'][1], g['quadril'][0], s)
            j = _lerp(g['joelho'][1], g['joelho'][0], s)
            t = _lerp(g['tornozelo'][1], g['tornozelo'][0], s)
            base, sombra, linha = self.calca[lado]
            L = Layer(base, linha)
            pts = _capsula(q, j, 3.6) | _capsula(j, t, 3.4 if self.largo else 3.1)
            if lado == 'tras':
                # o quadril, ligando as duas coxas por baixo do tronco
                for y in range(hip_y, hip_y + 3):
                    for x in range(11, 28):
                        pts.add((x, y))
            for p in pts:
                L.set(*p)
            L.shade_side('r', 2, sombra)
            L.outline()
            ops.append(['camada', L.px, 'pernas', None])
            dx = round(self.dx_sentado[lado] * (1 - s))
            ops.append(['camada', costas.mover(self.sapato[lado], dx, 0), 'pernas', None])
        return ops


def _corpo_separado(F):
    """As operações do desenho em pé sem as pernas, com o corpo dividido em
    cabeça (o que começa acima do pescoço, e os pixels soltos em cima disso),
    tronco de cima (acima da cintura, que inclina) e tronco de baixo. Devolve
    (operações, onde as pernas estavam)."""
    cabeca = {i for i, op in enumerate(F)
              if op[0] == 'camada' and op[2] == 'corpo' and anim._caixa(op[1])[1] < 22}
    out, onde = [], None
    for i, op in enumerate(F):
        k, pts, g, d = op[0], op[1], op[2], op[3]
        if g.startswith('perna'):
            onde = len(out) if onde is None else onde
            continue
        if g == 'corpo' and (i in cabeca or d in cabeca):
            out.append([k, pts, 'cabeca', d])
        elif g == 'corpo':
            cima = {p: c for p, c in pts.items() if p[1] < CINTURA}
            baixo = {p: c for p, c in pts.items() if p[1] >= CINTURA}
            if cima:
                out.append([k, cima, 'corpo', d])
            if baixo:
                out.append([k, baixo, 'corpo_baixo', d])
        else:
            out.append([k, pts, g, d])
    return out, onde


def _pernas_do_sentado(fn):
    """As pernas do sentado de verdade (quadril, coxas, canelas e sapatos),
    na ordem em que foram desenhadas."""
    S = anim.agrupar(anim.gravar(fn, 'sentado'), anim.regra_humano)
    quadril = {i for i, op in enumerate(S) if op[0] == 'camada' and anim._caixa(op[1])[3] == 51
               and anim._caixa(op[1])[2] - anim._caixa(op[1])[0] >= 15}
    return [['camada', op[1], 'pernas', None] for i, op in enumerate(S)
            if op[2].startswith('perna') or i in quadril or op[3] in quadril]


def quadros(cid, roteiro):
    """Os 6 quadros de levantar (roteiro LEVANTANDO) ou sentar (SENTANDO),
    na tela de 40 × 70, com a sola na linha anim.PE. O primeiro e o último
    são exatamente o sentado ou o parado de frente."""
    fn = costas.HUMANOS[cid][0]
    n = anim.folga(fn)
    F = anim.agrupar(anim.gravar(fn, 'parado'), anim.regra_humano)
    corpo, onde = _corpo_separado(F)
    pernas = Pernas(fn)
    sentado = _pernas_do_sentado(fn)
    out = []
    for k, (desce, cab, tronco, s) in enumerate(roteiro):
        if k in (0, len(roteiro) - 1):
            out.append(anim.descer(fn('sentado' if s == 0.0 else 'parado'), n))
            continue
        novas = sentado if s == 0.0 else pernas.desenhar(s)
        ops = corpo[:onde] + novas + corpo[onde:]
        mov = {'cabeca': {'dx': cab, 'dy': desce}, 'corpo': {'dx': tronco, 'dy': desce},
               'corpo_baixo': {'dy': desce},
               'braco_frente': {'dx': tronco, 'dy': desce}, 'braco_tras': {'dx': tronco, 'dy': desce}}
        out.append(anim.montar(ops, mov, n))
    return out


ROTEIROS = {'levantando_da_cadeira_frente': LEVANTANDO, 'sentando_na_cadeira_frente': SENTANDO}


def rosto(nome):
    """Onde está o rosto em cada quadro, em relação ao parado de frente."""
    return [[cab, desce] for desce, cab, _, _ in ROTEIROS[nome]]
