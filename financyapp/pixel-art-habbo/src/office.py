"""FinancyApp: as peças isoladas do jogo, lote do corte 1 (a sala parada).

Segue ../../docs/FinancyApp_Assets_v2.md: isométrico 2:1, tile de 64x32,
luz da esquerda, contorno na versão escura da própria cor, PNG
transparente em 1x, sem sombra e sem etiqueta. As chaves do manifesto são
os ids de modelo da planta (campo `modelo` do layout).

Uso: python3 office.py  (o build.py também chama)
Gera ../assets/ com as peças, os JSON dos personagens e o manifest.json, e
../previa/escala@2x.png, a prancha para fechar a escala.
"""
import json
import math
import os
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from px import Layer, rgb, mul, mix, up  # noqa: E402
import chars  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..', 'assets')
TW, TH = 64, 32
WALL_H = 100
BASEBOARD = 6
WHITE = rgb('#FFFFFF')
# escala dos cachorros no escritório, fechada na v2.2: Flora sentada com
# 34 px e Lupin com 24 px
FLORA_K, LUPIN_K = 0.75, 0.75

PAREDE = {
    'esquerda': '#AEBC9F', 'direita': '#94A386',
    'rodape_esquerda': '#EFEBE3', 'rodape_direita': '#D2CCC0',
    'topo_esquerda': '#CAD5BE', 'topo_direita': '#B1BEA4',
    'canto': '#7F8D72',
}


def hexs(c):
    return '#%02X%02X%02X' % c


# ------------------------------------------------------------ pintor iso
class Iso:
    """Quadro com origem O: o ponto (s, t, z) do chão vai para
    (ox + 32(s - t), oy + 16(s + t) - z). s anda no eixo A, t no eixo B."""

    def __init__(self, a, b, zmax, pad=8):
        self.a, self.b = a, b
        self.ox = pad + 32 * b
        self.oy = pad + zmax
        self.w = 32 * (a + b) + 2 * pad
        self.h = 16 * (a + b) + zmax + 2 * pad
        self.px = {}

    def scr(self, s, t, z=0):
        return self.ox + 32 * (s - t), self.oy + 16 * (s + t) - z

    def st(self, x, y, z):
        u = (x + 0.5 - self.ox) / 32
        v = (y + 0.5 - self.oy + z) / 16
        return (u + v) / 2, (v - u) / 2

    def _bbox(self, pts):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return int(min(xs)) - 1, int(min(ys)) - 1, int(max(xs)) + 1, int(max(ys)) + 1

    def commit(self, local, outline=True, k=0.6, keep=()):
        """Junta uma peça ao quadro, com contorno escuro da própria cor."""
        if outline:
            edge = [p for p in local if any((p[0] + dx, p[1] + dy) not in local
                                            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
            for p in edge:
                if p not in keep:
                    local[p] = mul(local[p], k)
        self.px.update(local)

    def box(self, s0, s1, t0, t1, z0, z1, top, left, right, tex=None, outline=True, hi=True):
        corners = [self.scr(s, t, z) for s in (s0, s1) for t in (t0, t1) for z in (z0, z1)]
        x0, y0, x1, y1 = self._bbox(corners)
        local, faces = {}, {}
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                s, t = self.st(x, y, z1)
                if s0 <= s <= s1 and t0 <= t <= t1:
                    c = tex('top', s, t, z1, top) if tex else top
                    local[(x, y)], faces[(x, y)] = c, 'top'
                    continue
                s = (x + 0.5 - self.ox) / 32 + t1
                z = self.oy + 16 * (s + t1) - (y + 0.5)
                if s0 <= s <= s1 and z0 <= z <= z1:
                    c = tex('left', s, t1, z, left) if tex else left
                    local[(x, y)], faces[(x, y)] = c, 'left'
                    continue
                t = s1 - (x + 0.5 - self.ox) / 32
                z = self.oy + 16 * (s1 + t) - (y + 0.5)
                if t0 <= t <= t1 and z0 <= z <= z1:
                    c = tex('right', s1, t, z, right) if tex else right
                    local[(x, y)], faces[(x, y)] = c, 'right'
        if hi:
            # quina da frente da tampa, mais clara
            for (x, y), f in list(faces.items()):
                if f == 'top' and faces.get((x, y + 1)) in ('left', 'right'):
                    local[(x, y)] = mix(local[(x, y)], WHITE, 0.3)
        self.commit(local, outline)
        return local

    def slab(self, inside, z0, z1, top, left, right, xc=None, tex=None, outline=True,
             bounds=(-0.2, 1.2, -0.2, 1.2), only_top=False):
        """Sólido extrudado: inside(s, t) diz se o ponto está na forma."""
        s0, s1, t0, t1 = bounds
        corners = [self.scr(s, t, z) for s in (s0, s1) for t in (t0, t1) for z in (z0, z1)]
        x0, y0, x1, y1 = self._bbox(corners)
        xc = self.scr((s0 + s1) / 2, (t0 + t1) / 2)[0] if xc is None else xc
        local = {}
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                s, t = self.st(x, y, z1)
                if inside(s, t):
                    local[(x, y)] = tex(s, t) if tex else top
                    continue
                if only_top:
                    continue
                for z in range(int(z1), int(z0) - 1, -1):
                    s, t = self.st(x, y, z)
                    if inside(s, t):
                        d = (x + 0.5 - xc)
                        local[(x, y)] = left if d < -2 else (right if d > 3 else mix(left, right, 0.5))
                        break
        self.commit(local, outline)
        return local

    def cyl(self, sc, tc, r, z0, z1, top, left, right, **kw):
        xc = self.scr(sc, tc)[0]
        return self.slab(lambda s, t: (s - sc) ** 2 + (t - tc) ** 2 <= r * r, z0, z1,
                         top, left, right, xc=xc,
                         bounds=(sc - r - 0.05, sc + r + 0.05, tc - r - 0.05, tc + r + 0.05), **kw)

    def face_paint(self, face, s_or_t, a0, a1, z0, z1, fn):
        """Pinta numa face vertical: face='right' (plano s fixo, olha para +A)
        ou 'left' (plano t fixo, olha para +B). fn(u, w) devolve a cor, com u
        da esquerda para a direita na tela e w de baixo para cima."""
        pts = []
        if face == 'right':
            s1 = s_or_t
            xa, _ = self.scr(s1, a1)
            xb, _ = self.scr(s1, a0)
            for x in range(int(xa), int(xb) + 1):
                t = s1 - (x + 0.5 - self.ox) / 32
                if not a0 <= t <= a1:
                    continue
                for y in range(0, self.h):
                    z = self.oy + 16 * (s1 + t) - (y + 0.5)
                    if z0 <= z <= z1:
                        u = (a1 - t) / (a1 - a0)
                        w = (z - z0) / (z1 - z0)
                        c = fn(u, w)
                        if c:
                            self.px[(x, y)] = c
                            pts.append((x, y))
        else:
            t1 = s_or_t
            xa, _ = self.scr(a0, t1)
            xb, _ = self.scr(a1, t1)
            for x in range(int(xa), int(xb) + 1):
                s = (x + 0.5 - self.ox) / 32 + t1
                if not a0 <= s <= a1:
                    continue
                for y in range(0, self.h):
                    z = self.oy + 16 * (s + t1) - (y + 0.5)
                    if z0 <= z <= z1:
                        u = (s - a0) / (a1 - a0)
                        w = (z - z0) / (z1 - z0)
                        c = fn(u, w)
                        if c:
                            self.px[(x, y)] = c
                            pts.append((x, y))
        return pts

    def put(self, x, y, c):
        self.px[(int(x), int(y))] = c

    def image(self):
        """Recorta no que foi desenhado e no losango da base e devolve
        (imagem, âncora), com a âncora no vértice de baixo do losango. Numa
        peça que não passa da base, a âncora fica em [32 × tiles em A, pé
        da imagem], como pede a v2."""
        xs = [p[0] for p in self.px]
        ys = [p[1] for p in self.px]
        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        x0 = min(x0, self.scr(0, self.b)[0])
        x1 = max(x1, self.scr(self.a, 0)[0] - 1)
        y1 = max(y1, self.scr(self.a, self.b)[1] - 1)
        im = Image.new('RGBA', (x1 - x0 + 1, y1 - y0 + 1), (0, 0, 0, 0))
        for (x, y), c in self.px.items():
            im.putpixel((x - x0, y - y0), (c + (255,)) if len(c) == 3 else c)
        bx, by = self.scr(self.a, self.b)
        return im, [int(bx - x0), int(by - y0)]


def same_frame(*canvases):
    """Recorta várias camadas no mesmo retângulo (ex.: mesa e monitor), para
    que se encaixem coladas no mesmo ponto."""
    xs, ys = [], []
    for cv in canvases:
        xs += [p[0] for p in cv.px]
        ys += [p[1] for p in cv.px]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    out = []
    for cv in canvases:
        im = Image.new('RGBA', (x1 - x0 + 1, y1 - y0 + 1), (0, 0, 0, 0))
        for (x, y), c in cv.px.items():
            im.putpixel((x - x0, y - y0), c + (255,))
        bx, by = cv.scr(cv.a, cv.b)
        out.append((im, [int(bx - x0), int(by - y0)]))
    return out


# ------------------------------------------------------------------ piso
def wood_tile(variant):
    """Tile de madeira clara: quatro tábuas no sentido do eixo A, emendas
    em lugares diferentes em cada variação, e um nó na terceira."""
    im = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
    bands = (rgb('#E3C48F'), rgb('#D9B983'), rgb('#DFBF8A'), rgb('#D5B37D'))
    seam, joint = rgb('#B58E5D'), rgb('#C19A69')
    joints = ({0: 9, 1: 25, 3: 17}, {0: 22, 1: 5, 2: 14}, {1: 16, 2: 28, 3: 7})[variant]
    for y in range(TH):
        for x in range(TW):
            if abs(x + 0.5 - 32) / 2 + abs(y + 0.5 - 16) > 16:
                continue
            u, v = (x + 0.5 - 32) / 32, (y + 0.5) / 16
            s, t = (u + v) / 2, (v - u) / 2
            S, T = int(s * 32), int(t * 32)
            band = min(3, T // 8)
            c = bands[band]
            if T % 8 == 0:
                c = seam
            elif joints.get(band) is not None and S == joints[band]:
                c = joint
            elif T % 8 == 4 and (S * 5 + band * 3 + variant) % 9 < 2:
                c = mul(c, 0.95)
            elif (S * 7 + T * 3 + variant * 5) % 31 == 0:
                c = mul(c, 0.93)
            elif T % 8 == 1:
                c = mix(c, WHITE, 0.12)
            if variant == 2:
                d = ((S - 21) / 3.2) ** 2 + ((T - 13) / 1.6) ** 2
                if d <= 1:
                    c = rgb('#A98454') if d > 0.35 else rgb('#8E6A40')
            im.putpixel((x, y), c + (255,))
    return im


# -------------------------------------------------------- peças de parede
def wall_edge(x, cx, cy):
    """Linha onde a parede encontra o piso (a mesma regra do room)."""
    return cy + abs(x - cx) // 2


def shear(flat_px, w, h, side, tiles, hb):
    """Põe um desenho plano (w x h) na parede, inclinado 2:1. A imagem sai
    com a largura dos tiles (32 por tile) e a âncora na ponta esquerda da
    base (na tela), na altura hb acima do chão. Peças com o mesmo w, h e hb
    saem no mesmo recorte, então as camadas (moldura e céu) se encaixam."""
    span = 32 * tiles
    m = (span - w) // 2
    cx, cy = 2000, 2000
    x_left = cx - span if side == 'esquerda' else cx

    def to_screen(i, j):
        x = x_left + m + i
        return x, wall_edge(x, cx, cy) - hb - h + j
    ys = [to_screen(i, j)[1] for i in (-1, w) for j in (0, h)]
    ys.append(wall_edge(x_left, cx, cy) - hb)
    y0, y1 = min(ys), max(ys)
    im = Image.new('RGBA', (span, y1 - y0 + 1), (0, 0, 0, 0))
    for (i, j), c in flat_px.items():
        x, y = to_screen(i, j)
        im.putpixel((x - x_left, y - y0), (c + (255,)) if len(c) == 3 else c)
    return im, [0, wall_edge(x_left, cx, cy) - hb - y0]


def frame_rect(L, x0, y0, x1, y1, c):
    for x in range(x0, x1 + 1):
        L.set(x, y0, c)
        L.set(x, y1, c)
    for y in range(y0, y1 + 1):
        L.set(x0, y, c)
        L.set(x1, y, c)


def door_entrance(state='fechada'):
    w, h = 30, 72
    px = {}
    fr = Layer(rgb('#F1EEE7'), rgb('#B9B3A6'))
    fr.rect(0, 0, w - 1, h - 1)
    fr.outline()
    px.update(fr.px)
    leaf = Layer(rgb('#A9784A'), rgb('#6E4A2A'))
    leaf.rect(3, 3, w - 4, h - 1)
    leaf.outline(skip='b')
    for (x0, y0, x1, y1) in ((7, 8, 22, 32), (7, 38, 22, 66)):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                edge = x in (x0, x1) or y in (y0, y1)
                leaf.set(x, y, rgb('#94663E') if edge else rgb('#B08050'))
        for x in range(x0 + 1, x1):
            leaf.set(x, y0 + 1, rgb('#C39465'))
    px.update(leaf.px)
    for x, y, c in ((23, 36, '#E2B648'), (24, 36, '#F4D47A'), (23, 37, '#B88A28'), (24, 37, '#E2B648'),
                    (22, 36, '#8A6A20')):
        px[(x, y)] = rgb(c)
    return px, w, h


def window_frame():
    w, h = 60, 42
    L = Layer(rgb('#F4F3EE'), rgb('#B8B5AC'))
    L.rect(0, 0, w - 1, h - 1)
    glass = set()
    for y in range(3, h - 4):
        for x in range(3, w - 3):
            if x in (29, 30):
                continue
            glass.add((x, y))
    for p in glass:
        L.px.pop(p, None)
    L.outline()
    # peitoril
    for x in range(-1, w + 1):
        L.set(x, h - 1, rgb('#FFFFFF'))
        L.set(x, h, rgb('#B8B5AC'))
    for y in range(3, h - 4):
        L.set(29, y, rgb('#E6E4DD'))
        L.set(30, y, rgb('#CFCCC3'))
    px = dict(L.px)
    # reflexo no vidro (semitransparente)
    for pane_x in (5, 33):
        for k in range(10):
            for d in (0, 1):
                x, y = pane_x + 6 + k + d, 5 + k
                if (x, y) in glass:
                    px[(x, y)] = (255, 255, 255, 70)
        for k in range(5):
            x, y = pane_x + 3 + k, 11 + k
            if (x, y) in glass:
                px[(x, y)] = (255, 255, 255, 55)
    return px, glass, w, h


def sky(period, glass, w, h):
    """Céu de São Paulo com a linha de prédios, um para cada período."""
    P = {
        'manha': dict(top='#94CCF1', bot='#DDF1FA', b1='#A9B9C9', b2='#93A6B8', win='#D9E6F0'),
        'tarde': dict(top='#5EA8E2', bot='#BFE1F6', b1='#8FA3B6', b2='#7A90A6', win='#C6D4E0'),
        'fim-de-tarde': dict(top='#5C4C9C', mid='#E07A86', bot='#F7BC6A', b1='#4D3E6E', b2='#3D305C', win='#F6C97A'),
        'noite': dict(top='#0C1331', bot='#26325E', b1='#1B2242', b2='#141A36', win='#F5D27A'),
    }[period]
    px = {}
    for (x, y) in glass:
        f = (y - 3) / (h - 8)
        if period == 'fim-de-tarde':
            c = mix(rgb(P['top']), rgb(P['mid']), f / 0.55) if f < 0.55 else mix(rgb(P['mid']), rgb(P['bot']), (f - 0.55) / 0.45)
        else:
            c = mix(rgb(P['top']), rgb(P['bot']), f)
        px[(x, y)] = c
    # sol, lua, estrelas, nuvens
    if period == 'manha':
        sun = (14, 11, 3.2)
    elif period == 'tarde':
        sun = (53, 7, 2.6)
    elif period == 'fim-de-tarde':
        sun = (40, 27, 4.2)
    else:
        sun = None
    if sun:
        sx, sy, r = sun
        for (x, y) in glass:
            d = math.hypot(x - sx, y - sy)
            if d <= r:
                px[(x, y)] = rgb('#FFF6C8') if period != 'fim-de-tarde' else rgb('#FFB24A')
            elif d <= r + 1.6:
                px[(x, y)] = mix(px[(x, y)], rgb('#FFF3B0') if period != 'fim-de-tarde' else rgb('#FF9A52'), 0.45)
    if period == 'noite':
        for x, y in ((6, 6), (12, 9), (20, 5), (37, 7), (46, 4), (40, 11), (25, 12), (49, 15), (8, 15)):
            if (x, y) in glass:
                px[(x, y)] = rgb('#FFFFFF') if (x + y) % 3 else rgb('#9FB8F0')
        for (x, y) in glass:
            d1 = math.hypot(x - 52, y - 9)
            d2 = math.hypot(x - 53.6, y - 8.2)
            if d1 <= 3.2 and d2 > 2.7:
                px[(x, y)] = rgb('#F4F0D8')
    if period in ('manha', 'tarde'):
        for cx_, cy_ in ((36 if period == 'manha' else 18, 9), (52 if period == 'manha' else 8, 14)):
            for (x, y) in glass:
                if ((x - cx_) / 4.5) ** 2 + ((y - cy_) / 1.6) ** 2 <= 1 or ((x - cx_ - 2) / 3) ** 2 + ((y - cy_ + 1.3) / 1.4) ** 2 <= 1:
                    px[(x, y)] = rgb('#FFFFFF') if y < cy_ else rgb('#E8F2F8')
    # prédios (a mesma silhueta em todos os céus)
    blds = [(3, 8, 27), (8, 12, 22), (12, 17, 30), (17, 21, 19), (21, 26, 25), (31, 35, 23),
            (35, 41, 28), (41, 44, 16), (44, 50, 24), (50, 56, 20)]
    for i, (x0, x1, top) in enumerate(blds):
        col = rgb(P['b1']) if i % 2 else rgb(P['b2'])
        for x in range(x0, x1):
            for y in range(top, h - 4):
                if (x, y) not in glass:
                    continue
                c = col
                lit = (y - top) % 3 == 1 and (x - x0) % 2 == 1 and x not in (x0, x1 - 1)
                if lit:
                    on = period != 'noite' or (x * 7 + y * 3 + i) % 4 == 0
                    c = mix(col, rgb(P['win']), 0.55 if period != 'noite' else 1.0) if on else col
                px[(x, y)] = c
    # antena
    for y in range(12, 16):
        if (43, y) in glass:
            px[(43, y)] = rgb(P['b2'])
    if (43, 11) in glass:
        px[(43, 11)] = rgb('#E2453C')
    return px


def whiteboard(state='limpo'):
    w, h = 58, 34
    fr = Layer(rgb('#C3C8CF'), rgb('#7E848D'))
    fr.rect(0, 0, w - 1, h - 1)
    fr.outline()
    px = dict(fr.px)
    for y in range(2, h - 4):
        for x in range(2, w - 2):
            px[(x, y)] = rgb('#FBFBFA')
    for x, y in ((10, 8), (11, 8), (12, 9), (30, 18), (31, 18), (32, 19), (44, 10), (45, 11)):
        px[(x, y)] = rgb('#EDEFF2')
    # bandeja das canetas
    for x in range(1, w - 1):
        px[(x, h - 4)] = rgb('#A9AFB8')
        px[(x, h - 3)] = rgb('#8C929B')
    for x0, c in ((8, '#D9453B'), (13, '#2F6FD0'), (18, '#2A2A30')):
        for x in range(x0, x0 + 4):
            px[(x, h - 5)] = rgb(c)
    for x in range(44, 52):
        px[(x, h - 5)] = rgb('#3A3A44')
        px[(x, h - 6)] = rgb('#E8E2D0')
    return px, w, h


def calendar(state='normal'):
    w, h = 22, 26
    pg = Layer(rgb('#FAFAF7'), rgb('#B9B6AE'))
    pg.rect(0, 3, w - 1, h - 1)
    pg.outline()
    px = dict(pg.px)
    for y in range(3, 9):
        for x in range(0, w):
            px[(x, y)] = rgb('#D9453B') if y > 3 else rgb('#A6302A')
    for x in range(4, 18):
        px[(x, 6)] = rgb('#F6C4BE') if x % 2 else rgb('#D9453B')
    for x in (5, 16):
        px[(x, 1)] = rgb('#3A3A40')
        px[(x, 2)] = rgb('#3A3A40')
        px[(x, 3)] = rgb('#3A3A40')
    for r in range(5):
        for c in range(6):
            x, y = 2 + c * 3, 11 + r * 3
            px[(x, y)] = rgb('#AEB2BA')
            px[(x + 1, y)] = rgb('#AEB2BA')
    return px, w, h


def corkboard(state='vazio'):
    w, h = 28, 22
    fr = Layer(rgb('#8A5C34'), rgb('#55361C'))
    fr.rect(0, 0, w - 1, h - 1)
    fr.outline()
    px = dict(fr.px)
    for y in range(2, h - 2):
        for x in range(2, w - 2):
            k = (x * 7 + y * 13) % 11
            px[(x, y)] = rgb('#B98B52') if k == 0 else (rgb('#D7AE77') if k == 5 else rgb('#C89C63'))
    for x in range(2, w - 2):
        px[(x, 2)] = rgb('#AE8048')
    return px, w, h


def wall_screen(state='apagada'):
    w, h = 58, 33
    bz = Layer(rgb('#1C1C21'), rgb('#08080A'))
    bz.rect(0, 0, w - 1, h - 1)
    bz.outline()
    px = dict(bz.px)
    for y in range(2, h - 3):
        for x in range(2, w - 2):
            px[(x, y)] = rgb('#252932')
    for k in range(0, 40):
        for d in range(3):
            x, y = 20 + k - (k // 2) + d, 2 + k // 2
            if 2 <= x < w - 2 and 2 <= y < h - 3:
                px[(x, y)] = rgb('#2F3440')
    px[(w - 5, h - 2)] = rgb('#D9453B')
    return px, w, h


# ---------------------------------------------------------------- móveis
OAK = (rgb('#DDBD8B'), rgb('#CDA673'), rgb('#AE895A'))
WHITEF = (rgb('#F4F3EF'), rgb('#E6E4DE'), rgb('#CDCAC2'))
METAL = (rgb('#4A4A52'), rgb('#3A3A42'), rgb('#2A2A30'))
GREEN = (rgb('#93A574'), rgb('#7D8F60'), rgb('#65754B'))
LEATHER = (rgb('#3F404A'), rgb('#33343C'), rgb('#26272E'))


def round_table():
    iso = Iso(2, 2, 40)
    iso.cyl(1, 1, 0.3, 0, 2, *METAL)
    iso.cyl(1, 1, 0.07, 2, 21, *METAL)

    def top_tex(s, t):
        r = math.hypot(s - 1, t - 1)
        if 0.52 < r < 0.56 or 0.3 < r < 0.33:
            return mix(OAK[0], WHITE, 0.15)
        return OAK[0]
    iso.cyl(1, 1, 0.8, 21, 24, OAK[0], OAK[1], OAK[2], tex=top_tex)
    return iso.image()


def meeting_chair(direction):
    iso = Iso(1, 1, 40)
    for (s, t) in ((0.3, 0.3), (0.7, 0.3), (0.3, 0.7), (0.7, 0.7)):
        iso.cyl(s, t, 0.035, 0, 12, *METAL, outline=False)
    iso.box(0.25, 0.75, 0.25, 0.75, 12, 15, *GREEN)
    if direction == 'frente':
        iso.box(0.22, 0.31, 0.27, 0.73, 15, 31, *GREEN)
    else:
        iso.box(0.27, 0.73, 0.69, 0.78, 15, 31, *GREEN)
    return iso.image()


def boss_chair(direction):
    iso = Iso(1, 1, 44)
    c0 = iso.scr(0.5, 0.5, 2)
    for ang in range(5):
        a = ang * 2 * math.pi / 5 + 0.3
        for k in range(1, 12):
            f = k / 11
            x, y = iso.scr(0.5 + 0.32 * f * math.cos(a), 0.5 + 0.32 * f * math.sin(a), 2)
            iso.put(x, y, rgb('#2A2A30'))
        x, y = iso.scr(0.5 + 0.32 * math.cos(a), 0.5 + 0.32 * math.sin(a), 0)
        iso.put(x, y, rgb('#111114'))
        iso.put(x + 1, y, rgb('#111114'))
    iso.put(c0[0], c0[1], rgb('#2A2A30'))
    iso.cyl(0.5, 0.5, 0.035, 2, 13, rgb('#7A7A84'), rgb('#6A6A72'), rgb('#55555C'))
    iso.box(0.27, 0.73, 0.27, 0.73, 13, 17, *LEATHER)
    if direction == 'frente':
        iso.box(0.25, 0.29, 0.47, 0.53, 15, 21, *METAL)
        iso.box(0.22, 0.31, 0.29, 0.71, 20, 38, *LEATHER)
    else:
        iso.box(0.47, 0.53, 0.71, 0.75, 15, 21, *METAL)
        iso.box(0.29, 0.71, 0.69, 0.78, 20, 38, *LEATHER)
    return iso.image()


def boss_desk():
    """Mesa do Contador (2x1) e, em camadas separadas no mesmo recorte, o
    monitor e a bandeja de entrada."""
    desk = Iso(2, 1, 60)

    def drawers(face, s, t, z, c):
        if face == 'left' and s < 0.62:
            if abs(z - 8) < 0.6 or abs(z - 15) < 0.6:
                return mul(c, 0.8)
            if (abs(z - 11.5) < 0.6 or abs(z - 18.5) < 0.6 or abs(z - 4.5) < 0.6) and 0.27 < s < 0.41:
                return rgb('#8A6A40')
        return c
    desk.box(1.84, 1.94, 0.12, 0.88, 0, 22, *OAK)
    desk.box(0.62, 1.84, 0.45, 0.5, 6, 22, OAK[1], mul(OAK[1], 0.85), mul(OAK[2], 0.85))
    desk.box(0.06, 0.62, 0.14, 0.86, 0, 22, *OAK, tex=drawers)
    desk.box(0.0, 2.0, 0.08, 0.92, 22, 25, *OAK)
    # teclado do lado de quem senta
    kb = desk.box(0.78, 1.32, 0.14, 0.32, 25, 26, rgb('#5A5E68'), rgb('#4A4D55'), rgb('#3A3D44'), outline=False)
    for (x, y) in list(kb):
        if (x + y) % 3 == 0:
            desk.px[(x, y)] = rgb('#7A7E88')

    mon = Iso(2, 1, 60)
    mon.box(0.2, 0.45, 0.38, 0.62, 25, 26, *METAL)
    mon.box(0.27, 0.36, 0.45, 0.55, 26, 32, *METAL)
    mon.box(0.36, 0.42, 0.16, 0.84, 30, 50, rgb('#2A2A30'), rgb('#232328'), rgb('#18181C'))

    def screen(u, w):
        if not (0.06 < u < 0.94 and 0.08 < w < 0.92):
            return None
        if w > 0.8:
            return rgb('#3A4A66')
        # painel parado: linhas de tabela e um gráfico baixo e plano
        if 0.45 < w < 0.75 and 0.12 < u < 0.88:
            if abs(w - (0.55 + 0.04 * math.sin(u * 9))) < 0.05:
                return rgb('#5FB0E8')
            return rgb('#1E2A3E')
        if w < 0.4 and (int(w * 30) % 3 == 0) and 0.12 < u < 0.85:
            return rgb('#4A5A78')
        return rgb('#1B2536')
    mon.face_paint('right', 0.42, 0.16, 0.84, 30, 50, screen)

    tray = Iso(2, 1, 60)
    tray.box(1.42, 1.8, 0.42, 0.8, 25, 26, *METAL)
    tray.box(1.42, 1.46, 0.42, 0.8, 26, 30, *METAL)
    tray.box(1.42, 1.8, 0.42, 0.46, 26, 30, *METAL)
    tray.box(1.76, 1.8, 0.42, 0.8, 26, 29, *METAL)
    return same_frame(desk, mon, tray)


def counter():
    """Balcão 3x1: frente de ripas de madeira virada para quem chega (+B),
    tampo branco e um parapeito mais alto na frente. A sineta é outra camada."""
    iso = Iso(3, 1, 60)

    def slats(face, s, t, z, c):
        if face == 'left':
            if z < 3:
                return mul(c, 0.78)
            if int(s * 32) % 4 == 0:
                return mul(c, 0.86)
        return c
    iso.box(0.04, 2.96, 0.18, 0.78, 0, 30, *OAK, tex=slats)
    iso.box(0.0, 3.0, 0.12, 0.84, 30, 33, *WHITEF)
    iso.box(0.0, 3.0, 0.76, 0.9, 33, 39, *WHITEF)

    bell = Iso(3, 1, 60)
    bx, by = bell.scr(1.5, 0.83, 39)
    for dx in range(-4, 5):
        bell.put(bx + dx, by, rgb('#2A2A2E'))
    dome = {-1: range(-3, 4), -2: range(-3, 4), -3: range(-2, 3), -4: range(-1, 2)}
    for dy, xs in dome.items():
        for dx in xs:
            bell.put(bx + dx, by + dy, rgb('#E2B648') if dx < 1 else rgb('#C7972F'))
    bell.put(bx - 2, by - 3, rgb('#FFF0B0'))
    bell.put(bx - 1, by - 3, rgb('#FFE08A'))
    bell.put(bx, by - 5, rgb('#8A6A20'))
    return same_frame(iso, bell)


def mailbox(state='vazio'):
    """Malote: caixa de correio azul num pé, encostada na parede esquerda.
    A abertura olha para +A; a bandeirinha fica do lado que dá para +B."""
    iso = Iso(1, 1, 60)
    blue = (rgb('#5B7EAA'), rgb('#4A6C98'), rgb('#36527A'))
    iso.box(0.28, 0.42, 0.42, 0.56, 0, 16, *METAL)
    iso.box(0.22, 0.48, 0.36, 0.62, 0, 2, *METAL)
    iso.box(0.14, 0.62, 0.24, 0.76, 16, 40, *blue)
    iso.box(0.12, 0.64, 0.22, 0.78, 40, 42, mul(blue[0], 0.9), mul(blue[1], 0.9), mul(blue[2], 0.9))

    def front(u, w):
        if 0.25 < u < 0.75 and 0.72 < w < 0.8:
            return rgb('#141A26')
        if (u < 0.12 or u > 0.88) and w < 0.62:
            return None
        if abs(w - 0.62) < 0.03 and 0.1 < u < 0.9:
            return rgb('#2A4262')
        if 0.78 < u < 0.84 and 0.3 < w < 0.4:
            return rgb('#D4D6DA')
        return None
    iso.face_paint('right', 0.62, 0.24, 0.76, 16, 40, front)
    # bandeirinha abaixada
    iso.box(0.38, 0.58, 0.76, 0.79, 21, 24, rgb('#E24A40'), rgb('#D7352E'), rgb('#A82620'))
    return iso.image()


def plant(state='viva'):
    iso = Iso(1, 1, 70)
    pot = (rgb('#F2F0EA'), rgb('#E2DED5'), rgb('#C4BFB4'))
    iso.cyl(0.5, 0.5, 0.21, 0, 15, *pot)
    iso.cyl(0.5, 0.5, 0.17, 15, 15, rgb('#5A4030'), rgb('#5A4030'), rgb('#5A4030'), only_top=True,
            outline=False)
    g, gd, gl = rgb('#3F8A3A'), rgb('#25602A'), rgb('#6DB55A')
    x0, y0 = iso.scr(0.5, 0.5, 15)
    leaves = ((-14, -20, 3), (-8, -34, 3), (1, -40, 3), (9, -32, 3), (15, -18, 3), (-4, -24, 2), (6, -22, 2))
    for dx, dy, wd in leaves:
        n = max(abs(dx), abs(dy))
        for k in range(n + 1):
            f = k / n
            x = x0 + round(dx * f)
            y = y0 - 1 + round(dy * f)
            ww = round(wd * 4 * f * (1 - f)) if f > 0.2 else 0
            for q in range(-ww, ww + 1):
                c = gd if q == ww else (gl if q == -ww else g)
                iso.put(x + q, y, c)
            iso.put(x, y, gd)
    lp = {p: c for p, c in iso.px.items()}
    # contorno das folhas
    for (x, y), c in list(lp.items()):
        if c in (g, gd, gl):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q not in iso.px:
                    iso.px[q] = rgb('#1C3A18')
    return iso.image()


def flora_blanket():
    iso = Iso(1, 1, 20)
    red = rgb('#CC322D')

    def inside(s, t):
        a, b = abs(s - 0.5), abs(t - 0.5)
        if a > 0.4 or b > 0.4:
            return False
        if a > 0.3 and b > 0.3:
            return (a - 0.3) ** 2 + (b - 0.3) ** 2 <= 0.01
        return True

    def quilt(s, t):
        S, T = int(s * 40), int(t * 40)
        if S % 7 == 0 or T % 7 == 0:
            return rgb('#9B201D')
        if S % 7 == 1 or T % 7 == 1:
            return rgb('#E45246')
        return red
    iso.slab(inside, 0, 2, red, rgb('#B52A26'), rgb('#8E1E1B'), tex=quilt,
             bounds=(0.05, 0.95, 0.05, 0.95))
    return iso.image()


def lupin_bed():
    iso = Iso(1, 1, 24)
    rim = (rgb('#D2AE80'), rgb('#C29C6C'), rgb('#9C7A50'))
    pad = rgb('#F1E3C6')
    in_ring = lambda s, t: 0.27 ** 2 <= (s - 0.5) ** 2 + (t - 0.5) ** 2 <= 0.42 ** 2
    ring = iso.slab(in_ring, 0, 8, *rim, bounds=(0.05, 0.95, 0.05, 0.95))
    top_ring = {p for p in ring if in_ring(*iso.st(p[0], p[1], 8))}
    for y in range(iso.h):
        for x in range(iso.w):
            s, t = iso.st(x, y, 4)
            d = (s - 0.5) ** 2 + (t - 0.5) ** 2
            if d <= 0.28 ** 2 and (x, y) not in top_ring:
                iso.px[(x, y)] = pad if d < 0.2 ** 2 else rgb('#DCC9A4')
    return iso.image()


# ----------------------------------------------------------- personagens
def paw_anchor(im):
    """Âncora no meio das patas: o meio dos pixels das duas linhas de baixo."""
    bb = im.getbbox()
    xs = [x for y in range(bb[3] - 2, bb[3]) for x in range(im.width) if im.getpixel((x, y))[3]]
    return [int(round((min(xs) + max(xs) + 1) / 2)), bb[3]]


def pad(im, l, t, r, b):
    out = Image.new('RGBA', (im.width + l + r, im.height + t + b), (0, 0, 0, 0))
    out.alpha_composite(im, (l, t))
    return out


def dog(im):
    return pad(im, 2, 2, 2, 2)


def _humano(fn):
    return {'parado_frente': lambda: fn('parado'), 'sentado_frente': lambda: fn('sentado')}


def _cachorro(fn, k):
    # parado é o cachorro em pé, nas quatro patas
    return {'parado_frente': lambda: dog(fn(k, 'em_pe')), 'sentado_frente': lambda: dog(fn(k))}


# id -> (nome, {animação: desenho}). Todos vão para o assets/; a folha tem
# uma animação por linha, nesta ordem.
PERSONAGENS = {
    'guilherme': ('Guilherme', _humano(chars.guilherme)),
    'saldanha': ('Saldanha', _humano(chars.saldanha)),
    'caio': ('Caio', _humano(chars.caio)),
    'vivi': ('Vivi', _humano(chars.vivi)),
    'flora': ('Flora', _cachorro(chars.flora, FLORA_K)),
    'lupin': ('Lupin', _cachorro(chars.lupin, LUPIN_K)),
    'gabriel': ('Gabriel', _humano(chars.gabriel)),
    'nina': ('Nina', _humano(chars.nina)),
    'otto': ('Otto', _humano(chars.otto)),
    'sr_pra_ontem': ('Sr. Pra Ontem', _humano(chars.pra_ontem)),
    'iris': ('Íris', _humano(chars.iris)),
    'joana': ('Joana', _humano(chars.joana)),
    'malu': ('Malu', _humano(chars.malu)),
    'duda': ('Duda', _humano(chars.duda)),
}


def anchor_of(cid, im):
    """Cachorros: o meio das patas. Humanos: o meio dos pés, no meio da tela
    e rente à sola (no sentado, o chão embaixo do quadril, no mesmo ponto)."""
    if cid in ('flora', 'lupin'):
        return paw_anchor(im)
    return [im.width // 2, im.getbbox()[3]]


# ------------------------------------------------------------- exportação
def save(im, rel):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)
    return rel


def character(cid, anims):
    """Folha de sprites (uma animação por linha, quadros da esquerda para a
    direita) e a entrada do manifesto, que também vai no JSON do personagem.
    Os quadros entram numa tela comum, alinhados pela âncora (o cachorro em
    pé é mais largo que o sentado)."""
    frames = [fn() for fn in anims.values()]
    anchors = [anchor_of(cid, f) for f in frames]
    ax, ay = max(a[0] for a in anchors), max(a[1] for a in anchors)
    w = ax + max(f.width - a[0] for f, a in zip(frames, anchors))
    h = ay + max(f.height - a[1] for f, a in zip(frames, anchors))
    sheet = Image.new('RGBA', (w, h * len(frames)), (0, 0, 0, 0))
    for i, (f, a) in enumerate(zip(frames, anchors)):
        sheet.alpha_composite(f, (ax - a[0], h * i + ay - a[1]))
    entry = {'pasta': 'personagens', 'folha': save(sheet, f'personagens/{cid}.png'),
             'tela': [w, h], 'ancora': [ax, ay],
             'animacoes': {name: {'linha': i, 'quadros': 1, 'fps': 0}
                           for i, name in enumerate(anims)}}
    with open(os.path.join(ROOT, 'personagens', f'{cid}.json'), 'w', encoding='utf-8') as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)
    return entry


def check(man):
    """Confere o que o manifesto promete: os arquivos existem e a âncora cai
    no pé da imagem. Personagens: em todos os quadros (sentado pisa onde o
    parado pisa). Móveis: no vértice de baixo da base, x = 32 × tiles em A."""
    for modelo, e in man.items():
        if 'folha' in e:
            sheet = Image.open(os.path.join(ROOT, e['folha']))
            w, h = e['tela']
            for name, a in e['animacoes'].items():
                frame = sheet.crop((0, h * a['linha'], w * a['quadros'], h * (a['linha'] + 1)))
                assert frame.getbbox()[3] == e['ancora'][1], (modelo, name)
        else:
            im = Image.open(os.path.join(ROOT, e['pasta'], f'{modelo}.png'))
            assert e['ancora'] == [32 * e['base'][0], im.height], modelo


def build():
    """Gera ../assets/ do zero com o que já está desenhado (todos os
    personagens, a manta e a caminha) e o manifest.json, com os nomes e as
    âncoras do "Como entregar" da v2.2. As chaves do manifesto são os ids de
    modelo da planta. Móveis, objetos, parede e piso entram depois."""
    shutil.rmtree(ROOT, ignore_errors=True)
    man = {cid: character(cid, anims) for cid, (_, anims) in PERSONAGENS.items()}
    for modelo, fn in (('manta_flora', flora_blanket), ('caminha_lupin', lupin_bed)):
        im, anchor = fn()
        save(im, f'moveis/{modelo}.png')
        man[modelo] = {'pasta': 'moveis', 'base': [1, 1], 'ancora': anchor}
    check(man)
    with open(os.path.join(ROOT, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(man, f, ensure_ascii=False, indent=2)
    escala(man)
    return man


# ----------------------------------------------------------------- prévia
PREVIA = os.path.join(os.path.dirname(__file__), '..', 'previa')


def chair_block():
    """Cadeira em bloco no azul da prévia da planta, só para a prancha:
    assento a 14 px e encosto até 34 px do lado -A, pelas alturas de
    referência da v2.1."""
    iso = Iso(1, 1, 34)
    navy = (rgb('#46568A'), rgb('#36446F'), rgb('#283353'))
    iso.box(0.2, 0.8, 0.2, 0.8, 0, 14, *navy)
    iso.box(0.2, 0.3, 0.2, 0.8, 14, 34, *navy)
    return iso.image()


def escala(man):
    """Prancha de escala: os 14 personagens do assets/ lado a lado no piso,
    lidos dos próprios arquivos. Uma faixa em pé (os cachorros nas quatro
    patas) e outra sentada (humanos na cadeira em bloco, cachorros nas
    camas). A linha pontilhada é o queixo do Guilherme. Sai em 2x, a escala
    do jogo."""
    def sprite(cid, anim):
        e = man[cid]
        (w, h), row = e['tela'], e['animacoes'][anim]['linha']
        im = Image.open(os.path.join(ROOT, e['folha'])).convert('RGBA')
        return im.crop((0, h * row, w, h * (row + 1))), e['ancora']

    def bed(modelo):
        im = Image.open(os.path.join(ROOT, 'moveis', f'{modelo}.png')).convert('RGBA')
        return im, man[modelo]['ancora']

    chair = chair_block()
    beds = {'flora': bed('manta_flora'), 'lupin': bed('caminha_lupin')}
    order = ['guilherme', 'saldanha', 'caio', 'vivi', 'flora', 'lupin', None,
             'gabriel', 'nina', 'otto', 'sr_pra_ontem', 'iris', 'joana', 'malu', 'duda']
    # cada faixa: título, se é sentada, colunas (coluna, nome, sprite, peça
    # embaixo: cadeira ou cama), grupos (primeira e última coluna, rótulo) e
    # a coluna vazia onde vai o rótulo do queixo
    strips = []
    for title, sit in (('Em pé (os cachorros nas quatro patas)', False),
                       ('Sentados: humanos na cadeira em bloco (assento a 14 px), cachorros nas camas', True)):
        items = [(c, PERSONAGENS[cid][0], sprite(cid, 'sentado_frente' if sit else 'parado_frente'),
                  (beds.get(cid, chair) if sit else None))
                 for c, cid in enumerate(order) if cid]
        strips.append((title, sit, items, [(0, 5, 'corte 1'), (7, 14, 'cortes seguintes')],
                       order.index(None)))

    ncol, top, band, foot = len(order), 22, 74, 54
    W = 64 * ncol + 32
    strip_h = band + foot
    im = Image.new('RGBA', (W, top + len(strips) * strip_h), (214, 218, 223, 255))
    labels = []     # (texto, x, y, alinhamento, tamanho): posição em 1x, o texto entra no 2x
    for s, (title, sit, items, groups, chin_col) in enumerate(strips):
        cy = top + s * strip_h + band          # centro dos tiles da faixa
        labels.append((title, 8, cy - band - 2, 'l', 20))
        # piso: os tiles da faixa, recortados num retângulo
        floor = Image.new('RGBA', im.size, (0, 0, 0, 0))
        for n in range(-3, 4):
            for m in range(-1, 2 * ncol + 1):
                if (m + n) % 2 == 0:
                    tile = wood_tile((m * 7 + n * 3) % 3)
                    floor.alpha_composite(tile, (32 * m, cy + 16 * n - 16))
        im.alpha_composite(floor.crop((0, cy - 34, W, cy + 20)), (0, cy - 34))
        chin = cy - (63 - 25) + (chars.SIT_DY if sit else 0)
        for x in range(0, W, 3):
            im.putpixel((x, chin), (200, 70, 60, 255))
        labels.append(('queixo do Guilherme', 32 + 64 * chin_col, chin - 9, 'c', 14))
        for c, name, (sp, a), under in items:
            x = 32 + 64 * c
            if under:
                ui, ua = under
                im.alpha_composite(ui, (x - ua[0], cy + 16 - ua[1]))
            im.alpha_composite(sp, (x - a[0], cy - a[1]))
            bb = sp.getbbox()
            labels += [(name, x, cy + 22, 'c', 15), (f'{bb[3] - bb[1]} px', x, cy + 30, 'c', 14)]
        for c0, c1, text in groups:
            labels.append((text, 32 + 32 * (c0 + c1), cy + 38, 'c', 14))

    big = up(im, 2)
    d = ImageDraw.Draw(big)
    for text, x, y, align, size in labels:
        try:
            font = ImageFont.truetype('DejaVuSans.ttf', size - 2)
        except OSError:       # sem a DejaVu, a fonte embutida (perde os acentos)
            font = ImageFont.load_default(size=size)
        shift = {'l': 0, 'c': 0.5, 'r': 1}[align] * d.textlength(text, font=font)
        d.text((2 * x - shift, 2 * y), text, font=font, fill=(52, 58, 66, 255))
    os.makedirs(PREVIA, exist_ok=True)
    big.save(os.path.join(PREVIA, 'escala@2x.png'))


if __name__ == '__main__':
    build()
    print('ok')
