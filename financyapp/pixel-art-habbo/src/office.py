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
import animacoes  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..', 'assets')
LAYOUT = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'FinancyApp_Layout_12x10_v1.json')
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

    def box_of(self):
        """Retângulo do que foi desenhado, esticado até o losango da base."""
        xs = [p[0] for p in self.px]
        ys = [p[1] for p in self.px]
        return (min(min(xs), self.scr(0, self.b)[0]), min(ys),
                max(max(xs), self.scr(self.a, 0)[0] - 1), max(max(ys), self.scr(self.a, self.b)[1] - 1))

    def image(self, anchor_at=None, frame=None):
        """Devolve (imagem, âncora). Sem anchor_at, recorta no que foi
        desenhado e no losango da base, com a âncora no vértice de baixo do
        losango: numa peça que não passa da base, ela fica em [32 × tiles em
        A, pé da imagem], como pede a v2. Com anchor_at = (s, t, z), recorta
        só no desenho e põe a âncora nesse ponto (objetos sobre a mesa).
        frame força o retângulo (camadas que se encaixam no mesmo recorte)."""
        if frame:
            x0, y0, x1, y1 = frame
        elif anchor_at:
            xs = [p[0] for p in self.px]
            ys = [p[1] for p in self.px]
            x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        else:
            x0, y0, x1, y1 = self.box_of()
        im = Image.new('RGBA', (x1 - x0 + 1, y1 - y0 + 1), (0, 0, 0, 0))
        for (x, y), c in self.px.items():
            im.putpixel((x - x0, y - y0), (c + (255,)) if len(c) == 3 else c)
        bx, by = self.scr(*anchor_at) if anchor_at else self.scr(self.a, self.b)
        return im, [int(round(bx - x0)), int(round(by - y0))]


def same_frame(*canvases):
    """Recorta várias camadas no mesmo retângulo (as direções da cadeira),
    para que todas tenham a mesma âncora."""
    boxes = [cv.box_of() for cv in canvases]
    frame = (min(b[0] for b in boxes), min(b[1] for b in boxes),
             max(b[2] for b in boxes), max(b[3] for b in boxes))
    return [cv.image(frame=frame) for cv in canvases]


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


def window_frame(h=52):
    """Moldura da janela, 32 a 84 px do chão (52 de altura)."""
    w = 60
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
    """Céu de São Paulo com a linha de prédios, um para cada período. Os
    prédios foram desenhados para 42 px de altura e descem junto com a
    janela."""
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
    blds = [(x0, x1, top + h - 42) for x0, x1, top in
            ((3, 8, 27), (8, 12, 22), (12, 17, 30), (17, 21, 19), (21, 26, 25), (31, 35, 23),
             (35, 41, 28), (41, 44, 16), (44, 50, 24), (50, 56, 20))]
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
    for y in range(12 + h - 42, 16 + h - 42):
        if (43, y) in glass:
            px[(43, y)] = rgb(P['b2'])
    if (43, 11 + h - 42) in glass:
        px[(43, 11 + h - 42)] = rgb('#E2453C')
    return px


def whiteboard(state='limpo'):
    """Quadro branco da reunião, 38 a 82 px do chão."""
    w, h = 58, 44
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
    """Calendário, 52 a 80 px do chão."""
    w, h = 22, 28
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
    """Mural de alertas, de cortiça, 40 a 80 px do chão."""
    w, h = 28, 40
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
    """Tela do FECHADO, 48 a 88 px do chão."""
    w, h = 58, 40
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


def _door_frame(w, h):
    fr = Layer(rgb('#F1EEE7'), rgb('#B9B3A6'))
    fr.rect(0, 0, w - 1, h - 1)
    fr.outline()
    return dict(fr.px)


def door_plain(state='fechada'):
    """Porta do Arquivo: folha lisa de madeira escura, sem cadeado, sem
    silhueta e sem plaquinha; só a maçaneta."""
    w, h = 30, 72
    px = _door_frame(w, h)
    leaf = Layer(rgb('#8E6440'), rgb('#5A3C22'))
    leaf.rect(3, 3, w - 4, h - 1)
    leaf.outline(skip='b')
    for y in range(4, h - 1):
        leaf.set(4, y, rgb('#A0744C'))
    px.update(leaf.px)
    for x, y, c in ((22, 37, '#C9CBD0'), (23, 37, '#EEF0F2'), (22, 38, '#8C9098'), (23, 38, '#C9CBD0')):
        px[(x, y)] = rgb(c)
    return px, w, h


# plaquinhas das portas trancadas: o nome não cabe nos 30 px da porta na
# fonte de pixel, então cada sala tem um ícone gravado no latão
PLAQUINHAS = {
    'tesouraria': [".###.", "#####", ".###.", "#####", ".###."],      # pilha de moedas
    'metas': [".###.", "#...#", "#.#.#", "#...#", ".###."],           # alvo
    'auditoria': [".##..", "#..#.", ".##..", "...#.", "....#"],       # lupa
}


def door_locked():
    """Porta trancada: folha de madeira com visor de vidro fosco e cadeado.
    Devolve (folha, silhueta, {sala: plaquinha}, w, h): a silhueta genérica
    atrás do vidro e as plaquinhas são camadas no mesmo recorte."""
    w, h = 30, 72
    px = _door_frame(w, h)
    leaf = Layer(rgb('#A9784A'), rgb('#6E4A2A'))
    leaf.rect(3, 3, w - 4, h - 1)
    leaf.outline(skip='b')
    px.update(leaf.px)
    glass = {(x, y) for x in range(9, 21) for y in range(9, 33)}
    for (x, y) in glass:
        px[(x, y)] = rgb('#CBD6E0') if (x + y) % 7 else rgb('#D8E1E9')
    vis = Layer(rgb('#6E4A2A'))
    frame_rect(vis, 8, 8, 21, 33, rgb('#6E4A2A'))
    px.update(vis.px)
    for k in range(6):
        px[(10 + k, 10 + k)] = rgb('#E8EEF3')
    # maçaneta e cadeado
    for x, y, c in ((22, 38, '#E2B648'), (23, 38, '#F4D47A'), (22, 39, '#B88A28'), (23, 39, '#E2B648')):
        px[(x, y)] = rgb(c)
    lock = {(21, 41): '#5E6168', (22, 40): '#5E6168', (23, 40): '#5E6168', (24, 41): '#5E6168'}
    for x in range(20, 26):
        for y in range(42, 47):
            lock[(x, y)] = '#C99A2E' if x < 23 else '#A87C22'
    lock[(22, 44)] = '#3A2A10'
    lock[(22, 45)] = '#3A2A10'
    px.update({p: rgb(c) for p, c in lock.items()})
    # silhueta genérica: cabeça e ombros de alguém do outro lado do vidro
    sil = {}
    for (x, y) in glass:
        head = ((x - 14.5) / 3.6) ** 2 + ((y - 17) / 4.2) ** 2 <= 1
        body = y >= 22 and abs(x - 14.5) <= 2 + (y - 22) * 0.9
        if head or body:
            sil[(x, y)] = rgb('#7D8CA3')
    # plaquinhas de latão com o ícone de cada sala
    plates = {}
    for name, icon in PLAQUINHAS.items():
        pl = Layer(rgb('#E2B648'), rgb('#8A6A20'))
        pl.rect(9, 50, 20, 58)
        pl.outline()
        for x in range(10, 20):
            pl.set(x, 51, rgb('#F4D47A'))
        for j, row in enumerate(icon):
            for i, v in enumerate(row):
                if v == '#':
                    pl.set(12 + i, 52 + j, rgb('#5E4310'))
        plates[name] = dict(pl.px)
    return px, sil, plates, w, h


def memory_board():
    """Mural de recordações da Vivi, 40 a 82 px do chão: quadro de tecido
    rosa com moldura, e quatro fotos soltas, em camadas no mesmo recorte,
    que o jogo cola por cima. As fotos são genéricas por enquanto."""
    w, h = 58, 42
    fr = Layer(rgb('#D98AA3'), rgb('#9C4F67'))
    fr.rect(0, 0, w - 1, h - 1)
    fr.outline()
    px = dict(fr.px)
    for y in range(2, h - 2):
        for x in range(2, w - 2):
            px[(x, y)] = rgb('#F6DCE4') if (x * 3 + y * 5) % 13 else rgb('#EFCBD6')
    scenes = (('#8FC6EE', '#6DB55A'), ('#F7BC6A', '#E07A86'), ('#BFE1F6', '#E3C48F'), ('#5EA8E2', '#2F6FD0'))
    pins = ('#D9453B', '#2F6FD0', '#3DB64B', '#E2B648')
    photos = []
    for k, ((x0, y0), (sky_c, ground_c)) in enumerate(zip(((5, 5), (19, 9), (33, 4), (45, 10)), scenes)):
        ph = {}
        for y in range(y0, y0 + 14):
            for x in range(x0, x0 + 10):
                ph[(x, y)] = rgb('#FFFFFF')
        for y in range(y0 + 1, y0 + 10):
            for x in range(x0 + 1, x0 + 9):
                ph[(x, y)] = rgb(sky_c) if y < y0 + 6 else rgb(ground_c)
        for x in range(x0, x0 + 10):
            ph[(x, y0 + 13)] = rgb('#D7D2C8')
        ph[(x0 + 4, y0)] = rgb(pins[k])
        ph[(x0 + 5, y0)] = rgb(pins[k])
        photos.append(ph)
    return px, photos, w, h


# ---------------------------------------------------------------- móveis
OAK = (rgb('#DDBD8B'), rgb('#CDA673'), rgb('#AE895A'))
WHITEF = (rgb('#F4F3EF'), rgb('#E6E4DE'), rgb('#CDCAC2'))
METAL = (rgb('#4A4A52'), rgb('#3A3A42'), rgb('#2A2A30'))


NAVY = (rgb('#46568A'), rgb('#36446F'), rgb('#283353'))
WALNUT = (rgb('#9A6A44'), rgb('#83573A'), rgb('#62402A'))
DESK_TOP = 24          # altura do tampo das mesas de trabalho e do fundador


def round_table():
    """Mesa de reunião redonda, 2x2, tampo a 22 px."""
    iso = Iso(2, 2, 40)
    iso.cyl(1, 1, 0.3, 0, 2, *METAL)
    iso.cyl(1, 1, 0.07, 2, 19, *METAL)

    def top_tex(s, t):
        r = math.hypot(s - 1, t - 1)
        if 0.52 < r < 0.56 or 0.3 < r < 0.33:
            return mix(OAK[0], WHITE, 0.15)
        return OAK[0]
    iso.cyl(1, 1, 0.8, 19, 22, OAK[0], OAK[1], OAK[2], tex=top_tex)
    return iso.image()


# direção da cadeira -> (s0, s1, t0, t1) do encosto. Ela olha para onde olha
# quem senta: frente-dir +A, frente-esq +B, costas-dir -B, costas-esq -A.
ENCOSTO = {
    'frente-dir': (0.22, 0.30, 0.26, 0.74),
    'frente-esq': (0.26, 0.74, 0.22, 0.30),
    'costas-dir': (0.26, 0.74, 0.70, 0.78),
    'costas-esq': (0.70, 0.78, 0.26, 0.74),
}


def chairs():
    """A cadeira nas quatro direções, no mesmo recorte: pés de metal,
    assento estofado a 14 px e encosto até 34 px. Nenhuma é espelho de
    outra, para a luz continuar vindo da esquerda."""
    out = {}
    for d, (s0, s1, t0, t1) in ENCOSTO.items():
        iso = Iso(1, 1, 40)
        for (s, t) in ((0.3, 0.3), (0.7, 0.3), (0.3, 0.7), (0.7, 0.7)):
            iso.cyl(s, t, 0.035, 0, 11, *METAL, outline=False)
        iso.box(0.24, 0.76, 0.24, 0.76, 11, 14, *NAVY)
        iso.box(s0, s1, t0, t1, 14, 34, *NAVY)
        out[d] = iso
    return dict(zip(out, same_frame(*out.values())))


def desk(wood, inlay=None):
    """Mesa 2x1 ao longo de A, tampo a 24 px. Quem senta fica do lado -B,
    então a face que dá para +B, a que se vê, é o painel da frente. inlay
    pinta o meio do tampo (a do fundador tem couro verde)."""
    iso = Iso(2, 1, 40)
    iso.box(0.04, 0.14, 0.12, 0.88, 0, DESK_TOP - 3, *wood)
    iso.box(1.86, 1.96, 0.12, 0.88, 0, DESK_TOP - 3, *wood)
    iso.box(0.14, 1.86, 0.74, 0.82, 7, DESK_TOP - 3, wood[1], mul(wood[1], 0.9), mul(wood[2], 0.9))

    def top(face, s, t, z, c):
        if face == 'top' and inlay and 0.2 < s < 1.8 and 0.24 < t < 0.76:
            edge = s < 0.25 or s > 1.75 or t < 0.29 or t > 0.71
            return mix(inlay, WHITE, 0.25) if edge else inlay
        return c
    iso.box(0.0, 2.0, 0.06, 0.94, DESK_TOP - 3, DESK_TOP, *wood, tex=top)
    return iso.image()


# onde cada objeto fica no tampo, em (s, t) da mesa. O monitor fica no meio
# do lado +B, com a tela virada para quem senta; o modelo serve ao Saldanha
# (cadeira em A5) e ao Caio (cadeira em A7), então não dá para pô-lo na
# frente de um só (ver NOTAS).
ENCAIXES = {
    'mesa_trabalho': {'monitor': (1.0, 0.62), 'bandeja': (1.6, 0.48), 'sineta': (0.4, 0.55),
                      'headset': (1.6, 0.4)},
    'mesa_fundador': {'monitor': (1.0, 0.62)},
}


def encaixes(modelo, base):
    """Encaixes em px, a partir da âncora da mesa (o vértice de baixo da base)."""
    iso = Iso(*base, 40)
    bx, by = iso.scr(*base)
    out = {}
    for obj, (s, t) in ENCAIXES[modelo].items():
        x, y = iso.scr(s, t, DESK_TOP)
        out[obj] = [int(round(x - bx)), int(round(y - by))]
    return out


def _halo(iso, pts, c):
    """Borda de luz: um pixel de brilho em volta dos pontos, menos embaixo."""
    for (x, y) in list(pts):
        for dx, dy in ((0, -1), (-1, 0), (1, 0)):
            q = (x + dx, y + dy)
            if q not in iso.px:
                iso.px[q] = c


def monitor(state='ligado'):
    """Monitor ligado, visto de costas: quem senta olha para +B, então a
    tela fica virada para ele e daqui se vê a traseira, com a luz da tela
    vazando pelas bordas. A âncora é o centro do pé, no tampo."""
    iso = Iso(1, 1, 30)
    iso.box(0.36, 0.64, 0.38, 0.62, 0, 1, *METAL)
    iso.box(0.46, 0.54, 0.5, 0.58, 1, 6, *METAL)
    back = iso.box(0.16, 0.84, 0.42, 0.5, 5, 20, rgb('#3A3B44'), rgb('#2E2F37'), rgb('#202128'))
    _halo(iso, back, (178, 222, 255, 170))
    x, y = iso.scr(0.5, 0.5, 14)
    iso.put(x, y, rgb('#4A4C57'))
    iso.put(x + 1, y, rgb('#4A4C57'))
    return iso.image(anchor_at=(0.5, 0.5, 0))


def tray(state='vazia'):
    """Bandeja de entrada, vazia, em cinza claro para as pilhas de papel do
    corte 2 aparecerem por cima."""
    iso = Iso(1, 1, 30)
    grey = (rgb('#D3D7DD'), rgb('#B7BCC4'), rgb('#969BA4'))
    iso.box(0.28, 0.72, 0.3, 0.7, 0, 1, *grey)
    iso.box(0.28, 0.32, 0.3, 0.7, 1, 4, *grey)
    iso.box(0.28, 0.72, 0.3, 0.34, 1, 4, *grey)
    iso.box(0.68, 0.72, 0.3, 0.7, 1, 3, *grey)
    iso.box(0.28, 0.72, 0.66, 0.7, 1, 3, *grey)
    return iso.image(anchor_at=(0.5, 0.5, 0))


def bell(state='parada'):
    """Sineta de balcão, parada."""
    iso = Iso(1, 1, 30)
    bx, by = iso.scr(0.5, 0.5, 0)
    for dx in range(-4, 5):
        iso.put(bx + dx, by, rgb('#2A2A2E'))
    dome = {-1: range(-3, 4), -2: range(-3, 4), -3: range(-2, 3), -4: range(-1, 2)}
    for dy, xs in dome.items():
        for dx in xs:
            iso.put(bx + dx, by + dy, rgb('#E2B648') if dx < 1 else rgb('#C7972F'))
    iso.put(bx - 2, by - 3, rgb('#FFF0B0'))
    iso.put(bx - 1, by - 3, rgb('#FFE08A'))
    iso.put(bx, by - 5, rgb('#8A6A20'))
    return iso.image(anchor_at=(0.5, 0.5, 0))


def headset(state=None):
    """Headset pousado no tampo: as duas conchas deitadas, o arco por cima
    e o microfone para a frente."""
    iso = Iso(1, 1, 30)
    cx, cy = iso.scr(0.5, 0.5, 0)
    dark, mid, hi = rgb('#26272E'), rgb('#3A3B44'), rgb('#5A5C68')
    for ox in (-5, 4):
        for dx in range(-2, 3):
            for dy in (-2, -1, 0):
                if abs(dx) + abs(dy + 1) <= 2:
                    iso.put(cx + ox + dx, cy + dy, mid if dy < 0 else dark)
        iso.put(cx + ox - 1, cy - 2, hi)
    for dx in range(-5, 5):
        iso.put(cx + dx, cy - 4 + (1 if abs(dx + 0.5) > 3 else 0), dark)
    for k in range(4):
        iso.put(cx - 5 - k, cy + 1 + k // 2, dark)
    iso.put(cx - 9, cy + 3, rgb('#5FB0E8'))
    return iso.image(anchor_at=(0.5, 0.5, 0))


def reception_counter():
    """Balcão da recepção, 1x3 ao longo de B, 34 px. A frente de ripas olha
    para +A, para quem chega; a Vivi senta atrás, do lado -A."""
    iso = Iso(1, 3, 50)

    def slats(face, s, t, z, c):
        if face == 'right':
            if z < 3:
                return mul(c, 0.78)
            if int(t * 32) % 4 == 0:
                return mul(c, 0.86)
        return c
    iso.box(0.2, 0.8, 0.04, 2.96, 0, 30, *OAK, tex=slats)
    iso.box(0.12, 0.88, 0.0, 3.0, 30, 34, *WHITEF)
    return iso.image()


def mailbox(state='vazio'):
    """Malote: caixa de correio azul num pé, 30 px, encostada na parede
    esquerda. A abertura olha para +A; a bandeirinha fica do lado +B."""
    iso = Iso(1, 1, 40)
    blue = (rgb('#5B7EAA'), rgb('#4A6C98'), rgb('#36527A'))
    iso.box(0.28, 0.42, 0.42, 0.56, 0, 10, *METAL)
    iso.box(0.22, 0.48, 0.36, 0.62, 0, 2, *METAL)
    iso.box(0.14, 0.62, 0.24, 0.76, 10, 28, *blue)
    iso.box(0.12, 0.64, 0.22, 0.78, 28, 30, mul(blue[0], 0.9), mul(blue[1], 0.9), mul(blue[2], 0.9))

    def front(u, w):
        if 0.25 < u < 0.75 and 0.7 < w < 0.8:
            return rgb('#141A26')
        if abs(w - 0.6) < 0.04 and 0.1 < u < 0.9:
            return rgb('#2A4262')
        if 0.78 < u < 0.84 and 0.3 < w < 0.4:
            return rgb('#D4D6DA')
        return None
    iso.face_paint('right', 0.62, 0.24, 0.76, 10, 28, front)
    iso.box(0.38, 0.58, 0.76, 0.79, 14, 17, rgb('#E24A40'), rgb('#D7352E'), rgb('#A82620'))
    return iso.image()


def plant(state='viva'):
    """Vaso branco com planta de folhas compridas, 40 px."""
    iso = Iso(1, 1, 60)
    pot = (rgb('#F2F0EA'), rgb('#E2DED5'), rgb('#C4BFB4'))
    iso.cyl(0.5, 0.5, 0.2, 0, 12, *pot)
    iso.cyl(0.5, 0.5, 0.16, 12, 12, rgb('#5A4030'), rgb('#5A4030'), rgb('#5A4030'), only_top=True,
            outline=False)
    g, gd, gl = rgb('#3F8A3A'), rgb('#25602A'), rgb('#6DB55A')
    x0, y0 = iso.scr(0.5, 0.5, 12)
    leaves = ((-12, -14, 3), (-7, -24, 3), (1, -28, 3), (8, -22, 3), (13, -13, 3), (-4, -17, 2), (5, -16, 2))
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
    # contorno das folhas
    for (x, y), c in list(iso.px.items()):
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


def _humano(cid):
    """As animações de um humano (animacoes.py): parado e sentado de frente
    e de costas e as duas caminhadas, cada uma uma lista de quadros já na
    tela de 40 × 70, com a sola na linha da âncora."""
    def quadros(nome):
        return lambda: _QUADROS.setdefault(cid, animacoes.quadros(cid))[nome]
    return {nome: quadros(nome) for nome in animacoes.ANIMACOES}


_QUADROS = {}


def _cachorro(fn, k):
    # parado é o cachorro em pé, nas quatro patas
    return {'parado_frente': lambda: dog(fn(k, 'em_pe')), 'sentado_frente': lambda: dog(fn(k))}


# id -> (nome, {animação: desenho}). Todos vão para o assets/; a folha tem
# uma animação por linha, nesta ordem.
PERSONAGENS = {
    'guilherme': ('Guilherme', _humano('guilherme')),
    'saldanha': ('Saldanha', _humano('saldanha')),
    'caio': ('Caio', _humano('caio')),
    'vivi': ('Vivi', _humano('vivi')),
    'flora': ('Flora', _cachorro(chars.flora, FLORA_K)),
    'lupin': ('Lupin', _cachorro(chars.lupin, LUPIN_K)),
    'gabriel': ('Gabriel', _humano('gabriel')),
    'nina': ('Nina', _humano('nina')),
    'otto': ('Otto', _humano('otto')),
    'sr_pra_ontem': ('Sr. Pra Ontem', _humano('sr_pra_ontem')),
    'iris': ('Íris', _humano('iris')),
    'joana': ('Joana', _humano('joana')),
    'malu': ('Malu', _humano('malu')),
    'duda': ('Duda', _humano('duda')),
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

    Humanos: todos os quadros já vêm na tela de 40 × 70 com a sola na linha
    da âncora, então a âncora é a mesma, (20, 66), em todos (manual de
    animações §1; ver a nota 9 de NOTAS_DE_IMPLEMENTACAO.md).
    Cachorros: um quadro por animação; os quadros entram numa tela comum,
    alinhados pela âncora (o em pé é mais largo que o sentado)."""
    frames = {name: fn() for name, fn in anims.items()}
    frames = {name: f if isinstance(f, list) else [f] for name, f in frames.items()}
    if cid in animacoes.HUMANOS:
        w, h = frames['parado_frente'][0].size
        ax, ay = animacoes.ANCORA
        placed = {name: [(f, (0, 0)) for f in fs] for name, fs in frames.items()}
    else:
        firsts = [fs[0] for fs in frames.values()]
        anchors = [anchor_of(cid, f) for f in firsts]
        ax, ay = max(a[0] for a in anchors), max(a[1] for a in anchors)
        w = ax + max(f.width - a[0] for f, a in zip(firsts, anchors))
        h = ay + max(f.height - a[1] for f, a in zip(firsts, anchors))
        placed = {name: [(f, (ax - a[0], ay - a[1])) for f in fs]
                  for (name, fs), a in zip(frames.items(), anchors)}
    ncol = max(len(fs) for fs in frames.values())
    sheet = Image.new('RGBA', (w * ncol, h * len(frames)), (0, 0, 0, 0))
    for i, fs in enumerate(placed.values()):
        for k, (f, (dx, dy)) in enumerate(fs):
            sheet.alpha_composite(f, (w * k + dx, h * i + dy))
    animacoes_ = {}
    for i, (name, fs) in enumerate(frames.items()):
        fps, loop = animacoes.ANIMACOES.get(name, (0, False))
        animacoes_[name] = {'linha': i, 'quadros': len(fs), 'fps': fps, **({'loop': True} if loop else {})}
        if cid in animacoes.HUMANOS:
            animacoes_[name].update(animacoes.campos(cid, name, len(fs)))
    entry = {'pasta': 'personagens', 'folha': save(sheet, f'personagens/{cid}.png'),
             'tela': [w, h], 'ancora': [ax, ay], 'animacoes': animacoes_}
    with open(os.path.join(ROOT, 'personagens', f'{cid}.json'), 'w', encoding='utf-8') as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)
    return entry


def files(modelo, e):
    """Os arquivos de uma peça, pela regra de nomes da v2.2: modelo.png com
    um estado só, modelo__estado.png ou modelo__direcao.png com vários, mais
    as camadas (modelo__camada.png)."""
    kinds = e.get('estados') or e.get('direcoes') or e.get('variacoes')
    if kinds:
        names = [f'{modelo}__{k}' for k in kinds]
    else:
        names = [] if e.get('camadas') else [modelo]
    names += [f'{modelo}__{c}' for c in e.get('camadas', [])]
    return [f"{e['pasta']}/{n}.png" for n in names]


def check(man):
    """Confere o que o manifesto promete: os arquivos existem e as âncoras
    estão onde a regra diz.
    - personagens: a âncora cai no pé de todos os quadros (o sentado pisa
      onde o parado pisa); na caminhada, no quadro em que o pé da frente
      está no ar o mais baixo é o de trás, 1 px acima (a profundidade). As
      linhas do tampo e do rosto são camadas, não pisam no chão;
    - piso e móveis: no vértice de baixo da base, x = 32 × tiles em A;
    - objetos: dentro da imagem;
    - parede: na ponta esquerda da base, e as camadas no mesmo recorte."""
    for modelo, e in man.items():
        if 'folha' in e:
            sheet = Image.open(os.path.join(ROOT, e['folha']))
            w, h = e['tela']
            for name, a in e['animacoes'].items():
                if a.get('sobreposicao') or a.get('camada_de'):
                    continue            # rosto e tampo não pisam no chão
                for k in range(a['quadros']):
                    frame = sheet.crop((w * k, h * a['linha'], w * (k + 1), h * (a['linha'] + 1)))
                    pe = frame.getbbox()[3]
                    no_ar = name.startswith('andando') and pe == e['ancora'][1] - 1
                    assert pe == e['ancora'][1] or no_ar, (modelo, name, k)
            continue
        if 'pasta' not in e:
            continue                    # cores da parede: o jogo desenha
        ims = [Image.open(os.path.join(ROOT, f)) for f in files(modelo, e)]
        assert len({im.size for im in ims}) == 1, modelo
        w, h = ims[0].size
        if e['pasta'] in ('piso', 'moveis'):
            assert e['ancora'] == [32 * e['base'][0], h], modelo
        elif e['pasta'] == 'parede':
            assert e['ancora'][0] == 0 and 0 < e['ancora'][1] <= h, modelo
        else:
            assert 0 <= e['ancora'][0] < w and 0 <= e['ancora'][1] <= h, modelo


def check_layout(man):
    """A ligação planta ↔ arte: todo modelo do layout existe no manifesto,
    com a mesma base (piso), a mesma parede, o mesmo número de tiles e a
    mesma altura (parede), e cada objeto de mesa tem encaixe."""
    with open(LAYOUT, encoding='utf-8') as f:
        lay = json.load(f)
    for p in lay['pecas_piso']:
        e = man[p['modelo']]
        assert e['base'] == p['base'], p['id']
        for obj in p.get('objetos', []):
            assert obj in man and obj in e['encaixes'], (p['id'], obj)
        if p.get('ocupante_padrao') not in (None, 'convidado', 'vaga'):
            assert p['ocupante_padrao'].lower() in man, p['id']
    for p in lay['pecas_parede']:
        e = man[p['modelo']]
        assert (e['parede'], e['tiles'], e['altura']) == (p['parede'], len(p['tiles']), p['altura_px']), p['id']
    return lay


def build():
    """Gera ../assets/ do zero, com o manifest.json, seguindo o "Como
    entregar" da v2.2: o lote do corte 1 inteiro (piso, parede, móveis e
    objetos) e os 14 personagens. As chaves do manifesto são os ids de
    modelo da planta. No fim, confere tudo contra o layout e monta as
    prévias."""
    shutil.rmtree(ROOT, ignore_errors=True)
    man = {cid: character(cid, anims) for cid, (_, anims) in PERSONAGENS.items()}

    # piso e cores da parede
    man['piso_madeira'] = {'pasta': 'piso', 'base': [1, 1], 'ancora': [TW // 2, TH],
                           'variacoes': [str(v + 1) for v in range(3)]}
    for v in range(3):
        save(wood_tile(v), f'piso/piso_madeira__{v + 1}.png')
    man['parede'] = {'altura': WALL_H, 'rodape': BASEBOARD, 'cores': PAREDE,
                     'borda_do_piso': {'altura': 8, 'esquerda': '#B8935F', 'direita': '#9A784C'}}

    # parede: cada peça é (modelo, parede, tiles, altura da base, estados,
    # camadas), com os desenhos planos do mesmo tamanho, no mesmo recorte
    lpx, sil, plates, dw, dh = door_locked()
    frame_px, glass, ww, wh = window_frame()
    board, photos, mw, mh = memory_board()
    wall = (
        ('porta_entrada', 'esquerda', 1, 0, {'fechada': door_entrance()[0]}, {}, 30, 72),
        ('porta_trancada', 'direita', 1, 0, {'trancada': lpx},
         {'silhueta': sil, **{f'plaquinha-{k}': v for k, v in plates.items()}}, dw, dh),
        ('porta_arquivo', 'esquerda', 1, 0, {'fechada': door_plain()[0]}, {}, 30, 72),
        ('janela', 'esquerda', 2, 32, {}, {'ceu-tarde': sky('tarde', glass, ww, wh), 'moldura': frame_px}, ww, wh),
        ('quadro_branco', 'direita', 2, 38, {'limpo': whiteboard()[0]}, {}, *whiteboard()[1:]),
        ('mural_alertas', 'direita', 1, 40, {'vazio': corkboard()[0]}, {}, *corkboard()[1:]),
        ('tela_parede', 'direita', 2, 48, {'apagada': wall_screen()[0]}, {}, *wall_screen()[1:]),
        ('calendario', 'direita', 1, 52, {'normal': calendar()[0]}, {}, *calendar()[1:]),
        ('mural_recordacoes', 'esquerda', 2, 40, {'vazio': board},
         {f'foto-{k + 1}': ph for k, ph in enumerate(photos)}, mw, mh),
    )
    for modelo, side, tiles, hb, estados, camadas, w, h in wall:
        e = {'pasta': 'parede', 'parede': side, 'tiles': tiles, 'altura': [hb, hb + h]}
        for kind, layers in (('estados', estados), ('camadas', camadas)):
            for name, px in layers.items():
                im, e['ancora'] = shear(px, w, h, side, tiles, hb)
                save(im, f'parede/{modelo}__{name}.png')
            if layers:
                e[kind] = list(layers)
        man[modelo] = e

    # móveis
    def movel(modelo, im_anchor, base, estado=None, **extra):
        im, anchor = im_anchor
        save(im, f'moveis/{modelo}__{estado}.png' if estado else f'moveis/{modelo}.png')
        man[modelo] = {'pasta': 'moveis', 'base': base, 'ancora': anchor,
                       **({'estados': [estado]} if estado else {}), **extra}
    movel('mesa_trabalho', desk(OAK), [2, 1], encaixes=encaixes('mesa_trabalho', (2, 1)))
    movel('mesa_fundador', desk(WALNUT, inlay=rgb('#3E6B4A')), [2, 1],
          encaixes=encaixes('mesa_fundador', (2, 1)))
    movel('mesa_reuniao', round_table(), [2, 2])
    movel('balcao_recepcao', reception_counter(), [1, 3])
    movel('malote', mailbox(), [1, 1], 'vazio')
    movel('planta', plant(), [1, 1], 'viva')
    movel('manta_flora', flora_blanket(), [1, 1])
    movel('caminha_lupin', lupin_bed(), [1, 1])
    for d, (im, anchor) in chairs().items():
        save(im, f'moveis/cadeira__{d}.png')
    man['cadeira'] = {'pasta': 'moveis', 'base': [1, 1], 'ancora': anchor, 'assento_px': 14,
                      'direcoes': list(ENCOSTO)}

    # objetos sobre as mesas
    for modelo, fn, estado in (('monitor', monitor, 'ligado'), ('bandeja', tray, 'vazia'),
                               ('sineta', bell, 'parada'), ('headset', headset, None)):
        im, anchor = fn()
        save(im, f'objetos/{modelo}__{estado}.png' if estado else f'objetos/{modelo}.png')
        man[modelo] = {'pasta': 'objetos', 'ancora': anchor, **({'estados': [estado]} if estado else {})}

    check(man)
    layout = check_layout(man)
    with open(os.path.join(ROOT, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(man, f, ensure_ascii=False, indent=2)
    escala(man)
    sala(man, layout)
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


# quem senta olhando para cada lado: o sentado de frente, espelhado ou não
# (frente-dir = +A sem espelhar, frente-esq = +B espelhado)
OLHA_PARA = {'+A': ('frente-dir', False), '+B': ('frente-esq', True),
             '-B': ('costas-dir', False), '-A': ('costas-esq', True)}
CAMA = {'manta_flora': 'flora', 'caminha_lupin': 'lupin'}


def sala(man, lay):
    """A sala parada montada como o jogo vai montar: só com o layout da
    planta e os arquivos e âncoras do assets/. Piso, paredes, peças de
    parede, móveis com os objetos nos encaixes, cada um no seu posto,
    sentado, e os cachorros nas camas. A estação flexível, reservada, sai
    pontilhada. As cadeiras da reunião ficam vazias no corte 1."""
    A, B = lay['sala']['tiles']
    pad = 20
    cx, cy = pad + 32 * B, pad + WALL_H + 4
    W, H = 32 * (A + B) + 2 * pad, cy + 16 * (A + B) + 8 + pad
    im = Image.new('RGBA', (W, H), (24, 30, 52, 255))

    def P(s, t, z=0):
        return cx + 32 * (s - t), cy + 16 * (s + t) - z

    cache = {}

    def put(rel, anchor, x, y, mirror=False):
        if rel not in cache:
            cache[rel] = Image.open(os.path.join(ROOT, rel)).convert('RGBA')
        sp = cache[rel]
        if mirror:
            sp, anchor = sp.transpose(Image.FLIP_LEFT_RIGHT), [sp.width - anchor[0], anchor[1]]
        im.alpha_composite(sp, (int(round(x - anchor[0])), int(round(y - anchor[1]))))

    def frame(cid, anim):
        e = man[cid]
        (w, h), row = e['tela'], e['animacoes'][anim]['linha']
        rel = f"{e['folha']}#{anim}"
        if rel not in cache:
            sheet = Image.open(os.path.join(ROOT, e['folha'])).convert('RGBA')
            cache[rel] = sheet.crop((0, h * row, w, h * (row + 1)))
        return rel, e['ancora']

    # paredes (o jogo desenha com as cores do manifesto)
    par = man['parede']
    cores = {k: rgb(v) for k, v in par['cores'].items()}
    px = im.load()
    for x in range(cx - 32 * B, cx + 32 * A):
        e = wall_edge(x, cx, cy)
        side = 'esquerda' if x < cx else 'direita'
        for y in range(e - par['altura'], e):
            if y < e - par['altura'] + 2:
                c = cores[f'topo_{side}']
            elif y >= e - par['rodape']:
                c = mul(cores[f'rodape_{side}'], 0.85) if y == e - par['rodape'] else cores[f'rodape_{side}']
            else:
                c = cores[side]
            px[x, y] = (mul(c, 0.82) if x == cx else c) + (255,)

    # piso, com a borda da frente
    piso = man['piso_madeira']
    for a in range(A):
        for b in range(B):
            v = piso['variacoes'][(a * 7 + b * 3 + a * b) % 3]
            put(f'piso/piso_madeira__{v}.png', piso['ancora'], *P(a + 1, b + 1))
    borda = par['borda_do_piso']
    for x in range(P(0, B)[0], P(A, 0)[0]):
        side = 'esquerda' if x < P(A, B)[0] else 'direita'
        y0 = (P(0, B)[1] + (x - P(0, B)[0]) // 2) if side == 'esquerda' else (P(A, B)[1] - (x - P(A, B)[0]) // 2)
        for y in range(y0, y0 + borda['altura']):
            px[x, y] = rgb(borda[side]) + (255,)

    # peças de parede: a âncora vai na ponta esquerda (na tela) do vão, na
    # altura da base (parede esquerda: o fim do último tile; direita: o
    # começo do primeiro)
    for p in lay['pecas_parede']:
        e = man[p['modelo']]
        x, y = P(0, p['tiles'][-1] + 1) if e['parede'] == 'esquerda' else P(p['tiles'][0], 0)
        y -= e['altura'][0]
        names = e.get('estados', [])[:1] + [c for c in e.get('camadas', [])
                                             if not c.startswith('plaquinha-')
                                             or c == f"plaquinha-{p.get('plaquinha', '').lower()}"]
        for n in names:
            put(f"parede/{p['modelo']}__{n}.png", e['ancora'], x, y)

    # estação reservada: só a pegada, pontilhada
    for p in lay['pecas_piso']:
        if p['tipo'] != 'reservado':
            continue
        (a, b), (da, db) = p['tile'], p['base']
        corners = [P(a, b), P(a + da, b), P(a + da, b + db), P(a, b + db), P(a, b)]
        for (x0, y0), (x1, y1) in zip(corners, corners[1:]):
            n = max(abs(x1 - x0), abs(y1 - y0))
            for k in range(0, n, 3):
                im.putpixel((x0 + (x1 - x0) * k // n, y0 + (y1 - y0) * k // n), (70, 60, 50, 255))

    # móveis, em ordem de profundidade: quem está atrás num eixo, dividindo
    # a faixa do outro eixo, vai antes
    items = []
    for p in lay['pecas_piso']:
        if p['tipo'] == 'reservado':
            continue
        (a, b), (da, db) = p['tile'], p['base']
        items.append(dict(p=p, fp=(a, a + da, b, b + db)))

    def behind(i, j):
        (a0, a1, b0, b1), (c0, c1, d0, d1) = i['fp'], j['fp']
        return (a1 <= c0 and b0 < d1 and d0 < b1) or (b1 <= d0 and a0 < c1 and c0 < a1)
    order, done = [], set()
    while len(order) < len(items):
        ready = [k for k in range(len(items)) if k not in done
                 and not any(behind(items[j], items[k]) for j in range(len(items)) if j not in done and j != k)]
        k = min(ready or [k for k in range(len(items)) if k not in done], key=lambda k: sum(items[k]['fp']))
        order.append(k)
        done.add(k)

    for k in order:
        p = items[k]['p']
        e = man[p['modelo']]
        (a, b), (da, db) = p['tile'], p['base']
        ax, ay = P(a + da, b + db)
        if p['modelo'] == 'cadeira':
            d, mirror = OLHA_PARA[p['olha_para']]
            put(f'moveis/cadeira__{d}.png', e['ancora'], ax, ay)
            who = p.get('ocupante_padrao', '').lower()
            if p['zona'] != 'reuniao' and who in man:
                put(*frame(who, 'sentado_frente'), *P(a + 0.5, b + 0.5), mirror=mirror)
            continue
        put(files(p['modelo'], e)[0], e['ancora'], ax, ay)
        for obj in p.get('objetos', []):
            o = man[obj]
            ex, ey = e['encaixes'][obj]
            put(files(obj, o)[0], o['ancora'], ax + ex, ay + ey)
        if p['modelo'] in CAMA:
            put(*frame(CAMA[p['modelo']], 'sentado_frente'), *P(a + 0.5, b + 0.5), mirror=True)

    os.makedirs(PREVIA, exist_ok=True)
    im.save(os.path.join(PREVIA, 'sala-parada.png'))
    up(im, 2).save(os.path.join(PREVIA, 'sala-parada@2x.png'))


if __name__ == '__main__':
    build()
    print('ok')
