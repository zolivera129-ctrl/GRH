"""Motorzinho de pixel art: camadas com contorno automático no estilo Habbo.

Cada parte do corpo é uma camada. Depois de preenchida, a camada recebe
um contorno na versão escura da própria cor (é isso que dá a cara de
Habbo), e só então ganha os detalhes internos, que não mexem no contorno.
"""
from PIL import Image


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mul(c, f):
    return tuple(max(0, min(255, round(v * f))) for v in c)


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Layer:
    def __init__(self, base, line=None):
        self.base = base
        self.line = line or mul(base, 0.62)
        self.px = {}

    def set(self, x, y, c=None):
        self.px[(x, y)] = c or self.base

    def rows(self, spec, c=None):
        """spec = {y: (x0, x1)} ou {y: [(x0, x1), ...]}, intervalos inclusivos."""
        for y, segs in spec.items():
            if isinstance(segs[0], int):
                segs = [segs]
            for x0, x1 in segs:
                for x in range(x0, x1 + 1):
                    self.px[(x, y)] = c or self.base

    def rect(self, x0, y0, x1, y1, c=None):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px[(x, y)] = c or self.base

    def line_(self, x0, y0, x1, y1, c=None, w=1):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            x = round(x0 + (x1 - x0) * i / n)
            y = round(y0 + (y1 - y0) * i / n)
            for k in range(w):
                self.px[(x + k, y)] = c or self.base

    def paint(self, pts, c):
        """Pinta só onde a camada já existe (para sombra e brilho)."""
        for p in pts:
            if p in self.px:
                self.px[p] = c

    def recolor(self, fn):
        for p in list(self.px):
            c = fn(p[0], p[1], self.px[p])
            if c is not None:
                self.px[p] = c

    def edges(self, skip=''):
        out = []
        for (x, y) in self.px:
            for dx, dy, side in ((1, 0, 'r'), (-1, 0, 'l'), (0, 1, 'b'), (0, -1, 't')):
                if side in skip:
                    continue
                if (x + dx, y + dy) not in self.px:
                    out.append((x, y))
                    break
        return out

    def outline(self, skip='', c=None):
        for p in self.edges(skip):
            self.px[p] = c or self.line
        return self

    def shade_side(self, side, n, c):
        """Sombra nos n pixels de um dos lados de cada linha ('l' ou 'r')."""
        ys = {}
        for (x, y) in self.px:
            ys.setdefault(y, []).append(x)
        for y, xs in ys.items():
            xs.sort()
            pick = xs[:n] if side == 'l' else xs[-n:]
            for x in pick:
                self.px[(x, y)] = c
        return self


class Sprite:
    def __init__(self, w, h, dy=0):
        """dx e dy deslocam tudo o que for desenhado dali em diante (a pose
        sentada desce o corpo até o assento; o cachorro em pé leva a cabeça
        para a frente), sem redesenhar cada parte."""
        self.w, self.h = w, h
        self.dx, self.dy = 0, dy
        self.px = {}

    def add(self, layer, dx=0, dy=0):
        for (x, y), c in layer.px.items():
            self.px[(x + dx + self.dx, y + dy + self.dy)] = c

    def set(self, x, y, c):
        self.px[(x + self.dx, y + self.dy)] = c

    def image(self):
        im = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))
        for (x, y), c in self.px.items():
            if 0 <= x < self.w and 0 <= y < self.h:
                im.putpixel((x, y), c + (255,) if len(c) == 3 else c)
        return im


def up(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)
