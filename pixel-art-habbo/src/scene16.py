"""Cenários da versão em grade: salas vistas de cima (3/4, como RPG), em
tiles de 16x16. Cada sala tem 9x11 tiles (144x176 px); o personagem de
16x32 fica em pé no tile do meio. Tudo que é fixo (parede, piso e mobis)
cai certinho na grade, e o tileset de cada sala sai fatiando o fundo.

Uso: python3 scene16.py  (gera ../out/grade16/)
"""
import math
import os
import random
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from px import rgb, mul, mix, up  # noqa: E402
from scene import FONT, MINI, text_width  # noqa: E402
import sprites16  # noqa: E402

T = 16
COLS, ROWS = 9, 11
W, H = COLS * T, ROWS * T
WALL_ROWS = 3
SIDE = 4                       # espessura das paredes laterais vistas de cima
CHAR_COL, FEET_ROW = 4, 7      # o personagem ocupa as linhas 6 e 7 da coluna 4
OUT = os.path.join(os.path.dirname(__file__), '..', 'out', 'grade16')
WHITE = rgb('#FFFFFF')


# ----------------------------------------------------------------- base
class Canvas:
    def __init__(self, w, h):
        self.im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        self.w, self.h = w, h

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.im.putpixel((x, y), c + (255,) if len(c) == 3 else c)

    def get(self, x, y):
        return self.im.getpixel((x, y))[:3]

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c)

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def paste(self, im, x, y):
        self.im.alpha_composite(im, (x, y))


def outlined(cv, c):
    """Contorno de 1 px por fora de tudo que foi desenhado."""
    im = cv.im
    px = im.load()
    filled = {(x, y) for y in range(im.height) for x in range(im.width) if px[x, y][3]}
    for y in range(im.height):
        for x in range(im.width):
            if (x, y) in filled:
                continue
            if any((x + dx, y + dy) in filled for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = c + (255,)
    return im


def text(cv, s, x, y, c, font=FONT, gap=1):
    for ch in s:
        g = font[ch]
        for j, row in enumerate(g):
            for i, v in enumerate(row):
                if v == '#':
                    cv.set(x + i, y + j, c)
        x += len(g[0]) + gap


def room(cv, wall, floor, top_col, base_col):
    """wall(x, y) e floor(x, y) recebem coordenadas da tela; os padrões
    repetem a cada 16 px para casar com a grade."""
    wall_h = WALL_ROWS * T
    for y in range(H):
        for x in range(W):
            if x < SIDE or x >= W - SIDE:
                c = top_col
                if x in (SIDE - 1, W - SIDE):
                    c = mul(top_col, 0.7)
            elif y < 4:
                c = top_col if y < 3 else mul(top_col, 0.7)
            elif y < wall_h - 4:
                c = wall(x, y)
            elif y < wall_h:
                c = base_col if y < wall_h - 1 else mul(base_col, 0.75)
            else:
                c = floor(x, y)
                # sombra que a parede joga no chão
                if y < wall_h + 3:
                    c = mul(c, (0.78, 0.86, 0.94)[y - wall_h])
                if x < SIDE + 2:
                    c = mul(c, 0.86 if x == SIDE else 0.93)
                if x >= W - SIDE - 2:
                    c = mul(c, 0.86 if x == W - SIDE - 1 else 0.93)
            cv.set(x, y, c)


def shadow(cv, cx, cy, rx, ry, k=0.7):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if ((x - cx) / (rx + 0.5)) ** 2 + ((y - cy) / (ry + 0.5)) ** 2 <= 1:
                cv.set(x, y, mul(cv.get(x, y), k))


def nametag(cv, name, cx, bottom):
    tw = text_width(name)
    h = 12 if 'p' in name else 10
    w = tw + 6
    x0, y0 = cx - w // 2, bottom - h - 3
    bg = rgb('#141414')
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if not ((x in (x0, x0 + w - 1)) and (y in (y0, y0 + h - 1))):
                cv.set(x, y, bg)
    for x in range(x0 + 1, x0 + w - 1):
        cv.set(x, y0, rgb('#3A3A3A'))
    for i, half in enumerate((2, 1, 0)):
        for x in range(cx - half, cx + half + 1):
            cv.set(x, y0 + h + i, bg)
    text(cv, name, x0 + 3, y0 + 2, WHITE)


def tx(col):
    return col * T


def ty(row):
    return row * T


# ------------------------------------------------------------------ mobis
def prop(w, h):
    return Canvas(w, h)


def window_sea():
    p = prop(32, 24)
    wood, woodd = rgb('#9A6A40'), rgb('#6E4828')
    p.rect(0, 0, 31, 23, wood)
    for y in range(2, 22):
        for x in range(2, 30):
            if y < 9:
                c = mix(rgb('#A9DDF4'), rgb('#D3F0FA'), (y - 2) / 7)
            elif y < 13:
                c = rgb('#5C9440') if (x * 3 + y) % 7 else rgb('#3F7030')
                if y == 9 and not (8 <= x <= 22):
                    c = rgb('#CFEFFA')
                if y == 10 and not (5 <= x <= 25):
                    c = rgb('#CFEFFA')
            elif y == 13:
                c = rgb('#C9B48A')
            else:
                c = rgb('#30C7CC') if y < 17 else rgb('#21B4BE')
                if (x * 5 + y * 3) % 13 == 0:
                    c = rgb('#B8F3F0')
            p.set(x, y, c)
    for x, y in ((6, 4), (7, 4), (8, 4), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (21, 3), (22, 3), (20, 4), (21, 4), (22, 4), (23, 4)):
        p.set(x, y, WHITE)
    p.vline(15, 2, 21, wood)
    p.vline(16, 2, 21, woodd)
    p.hline(2, 29, 11, wood)
    p.hline(0, 31, 23, woodd)
    p.hline(1, 30, 1, mix(wood, WHITE, 0.25))
    return outlined(p, rgb('#3A2614'))


def window_city():
    p = prop(32, 24)
    fr, frd = rgb('#E2E2DE'), rgb('#B4B4AE')
    p.rect(0, 0, 31, 23, fr)
    for y in range(2, 22):
        for x in range(2, 30):
            p.set(x, y, mix(rgb('#D3E9F5'), rgb('#9CC6E2'), (y - 2) / 20))
    for x0, x1, top, col in ((2, 6, 9, '#8EA3B5'), (7, 11, 5, '#A9B8C6'), (12, 17, 11, '#7F95A8'),
                             (18, 22, 6, '#B4C2CF'), (23, 29, 10, '#91A5B7')):
        for x in range(x0, x1 + 1):
            for y in range(top, 22):
                c = rgb(col)
                if y > top and (y - top) % 2 == 0 and x not in (x0, x1) and (x - x0) % 2:
                    c = mix(c, WHITE, 0.5)
                p.set(x, y, c)
    p.vline(15, 2, 21, fr)
    p.vline(16, 2, 21, frd)
    p.hline(2, 29, 11, fr)
    p.hline(0, 31, 23, frd)
    return outlined(p, rgb('#55554F'))


def ring16(colfn, r_out=6.6, r_in=3.2):
    p = prop(16, 16)
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if r_in <= d <= r_out:
                p.set(x, y, colfn(x - 7.5, y - 7.5, d))
    return p


def lifebuoy():
    red, white = rgb('#E2452F'), rgb('#F6F4EE')

    def col(dx, dy, d):
        a = math.atan2(dy, dx)
        seg = int(((a + math.pi) / (math.pi / 2)) + 0.5) % 4
        c = red if seg % 2 == 0 else white
        return mix(c, WHITE, 0.3) if dy < -2 and d > 4.6 else c
    return outlined(ring16(col, 6.4, 3.0), rgb('#6E2014'))


def framed(art_fn, wood, inner, size=(16, 16)):
    w, h = size
    p = prop(w, h)
    p.rect(0, 0, w - 1, h - 1, wood)
    p.hline(1, w - 2, 1, mix(wood, WHITE, 0.3))
    p.rect(2, 2, w - 3, h - 3, inner)
    p.hline(2, w - 3, 2, mul(inner, 0.86))
    art_fn(p)
    return outlined(p, mul(wood, 0.45))


def art_bone(p, c=rgb('#F3EEE2')):
    d = mul(c, 0.7)
    for x in range(5, 11):
        p.set(x, 8, c)
        p.set(x, 9, d)
    for ex in (4, 11):
        for dx, dy in ((0, 7), (0, 10), (-1, 7), (-1, 10), (0, 8), (0, 9), (-1, 8), (-1, 9)):
            p.set(ex + (dx if ex == 4 else -dx), dy, c)
    p.set(3, 8, c)
    p.set(3, 9, c)
    p.set(12, 8, c)
    p.set(12, 9, c)


def art_heart(p, c=rgb('#E2453C')):
    rows = {5: [(4, 6), (9, 11)], 6: (3, 12), 7: (3, 12), 8: (4, 11), 9: (5, 10), 10: (6, 9), 11: (7, 8)}
    for y, segs in rows.items():
        if isinstance(segs[0], int):
            segs = [segs]
        for x0, x1 in segs:
            for x in range(x0, x1 + 1):
                p.set(x, y, c)
    p.set(5, 6, mix(c, WHITE, 0.6))


def art_paw(p, c=rgb('#2A2A33')):
    toes = ((4, 6), (6, 4), (9, 4), (11, 6))
    for tx_, ty_ in toes:
        for dx in (0, 1):
            for dy in (0, 1):
                p.set(tx_ + dx - 1 if tx_ > 7 else tx_ + dx, ty_ + dy, c)
    for y, (x0, x1) in {9: (6, 9), 10: (5, 10), 11: (5, 10), 12: (6, 9)}.items():
        for x in range(x0, x1 + 1):
            p.set(x, y, c)


def art_record(p):
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.0)
            if d <= 5.2:
                c = rgb('#D9B04C') if int(d * 2) % 2 else rgb('#B48E35')
                if d <= 1.6:
                    c = rgb('#F0CE6A')
                if 2.5 < d < 4 and x < 7 and y < 7:
                    c = rgb('#F7E2A0')
                p.set(x, y, c)


def art_chart(p):
    for i, h in enumerate((2, 4, 3, 6)):
        x0 = 3 + i * 3
        for x in (x0, x0 + 1):
            for y in range(12 - h, 12):
                p.set(x, y, rgb('#3DB64B') if x == x0 else rgb('#2C9440'))
    p.hline(2, 13, 12, rgb('#8A8D94'))
    for x, y in ((11, 4), (12, 3), (12, 4), (13, 4), (12, 5)):
        p.set(x, y, rgb('#E2453C'))


def art_check(p):
    for x, y in ((3, 8), (4, 9), (5, 10), (6, 11), (7, 10), (8, 9), (9, 8), (10, 7), (11, 6), (12, 5)):
        p.set(x, y, WHITE)
        p.set(x, y - 1, WHITE)


def neon_on_air():
    p = prop(32, 13)
    p.rect(0, 0, 31, 12, rgb('#17121C'))
    p.hline(1, 30, 1, rgb('#2A2032'))
    pink, glow, hot = rgb('#FF6AD5'), rgb('#7E2D74'), rgb('#FFD3F4')
    tmp = Canvas(32, 13)
    x0 = (32 - text_width('ON AIR', MINI)) // 2
    text(tmp, 'ON AIR', x0, 4, pink, MINI)
    pts = [(x, y) for y in range(13) for x in range(32) if tmp.im.getpixel((x, y))[3]]
    for x, y in pts:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in pts and 0 < x + dx < 31 and 0 < y + dy < 12:
                p.set(x + dx, y + dy, glow)
    for x, y in pts:
        p.set(x, y, pink)
    p.set(*pts[0], hot)
    return outlined(p, rgb('#3A2C46'))


def palm():
    """Palmeira no vaso: 16x32, o vaso apoiado na linha de baixo."""
    p = prop(16, 32)
    pot, potd, potl = rgb('#C4673A'), rgb('#9A4E2A'), rgb('#DA8655')
    for y in range(21, 31):
        inset = (y - 21) // 4
        for x in range(3 + inset, 13 - inset):
            p.set(x, y, potd if x >= 10 - inset else pot)
    p.hline(2, 13, 20, potl)
    p.hline(2, 13, 21, potd)
    p.hline(4, 11, 20, rgb('#3B2416'))
    for k in range(10):
        p.set(7 + (k // 5), 19 - k, rgb('#8A6238') if k % 3 else rgb('#5E4126'))
        p.set(8 + (k // 5), 19 - k, rgb('#A97C4A'))
    leaf, leafd, leafl = rgb('#4E9A34'), rgb('#2F6A21'), rgb('#7CC24E')
    cx, cy = 8, 9
    for fx, fy in ((-7, 3), (-6, -3), (-2, -7), (3, -7), (6, -3), (7, 3), (-4, 6), (5, 6)):
        n = max(abs(fx), abs(fy))
        for t in range(n + 1):
            x = cx + round(fx * t / n)
            y = cy + round(fy * t / n + (t / n) ** 2 * 2)
            p.set(x, y, leaf)
            p.set(x, y + 1, leafd)
            if t % 2:
                p.set(x, y - 1, leafl)
    return outlined(p, rgb('#1E3A16'))


def big_leaf():
    p = prop(16, 32)
    pot, potd = rgb('#D6D3CC'), rgb('#A8A49C')
    for y in range(21, 31):
        for x in range(3, 13):
            p.set(x, y, potd if x >= 10 else pot)
    p.hline(2, 13, 20, rgb('#ECEAE5'))
    p.hline(3, 12, 21, rgb('#5A4030'))
    g, gd, gl = rgb('#3F8A3A'), rgb('#25602A'), rgb('#6DB55A')
    for (x0, y0, dx, dy) in ((7, 20, -6, -12), (8, 20, -2, -18), (8, 20, 3, -16), (9, 20, 6, -10), (8, 20, -5, -6)):
        n = max(abs(dx), abs(dy))
        for t in range(n + 1):
            f = t / n
            x = x0 + round(dx * f)
            y = y0 + round(dy * f)
            w = round(2.2 * 4 * f * (1 - f)) if f > 0.2 else 0
            for k in range(-w, w + 1):
                p.set(x + k, y, gd if k == w else (gl if k == -w else g))
            p.set(x, y, gd)
    return outlined(p, rgb('#1C3A18'))


def ficus():
    p = prop(16, 32)
    pot, potd = rgb('#8F9396'), rgb('#6C7073')
    for y in range(22, 31):
        for x in range(4, 12):
            p.set(x, y, potd if x >= 9 else pot)
    p.hline(3, 12, 21, rgb('#B4B8BA'))
    for k in range(9):
        p.set(8 if k % 5 < 3 else 7, 20 - k, rgb('#7A5A3A'))
    rnd = random.Random(3)
    g, gd, gl = rgb('#3E8C3C'), rgb('#265F28'), rgb('#74C05E')
    for _ in range(170):
        x = 8 + rnd.randint(-7, 6)
        y = 8 + rnd.randint(-7, 6)
        if ((x - 7.5) / 7) ** 2 + ((y - 7.5) / 7.5) ** 2 <= 1:
            p.set(x, y, rnd.choice([g, g, gd, gl]))
    return outlined(p, rgb('#1A3A18'))


def speaker():
    p = prop(16, 32)
    p.rect(1, 2, 14, 30, rgb('#2A2A32'))
    p.hline(1, 14, 2, rgb('#4A4A55'))
    p.hline(1, 14, 3, rgb('#3A3A44'))
    p.vline(14, 3, 30, rgb('#1E1E24'))
    for cy, r in ((10, 3.6), (21, 5.0)):
        for y in range(32):
            for x in range(16):
                d = math.hypot(x - 7.5, y - cy)
                if d <= r:
                    p.set(x, y, rgb('#0F0F12') if d > r - 1 else (rgb('#5A5A66') if d < 1.3 else rgb('#24242A')))
    p.set(12, 5, rgb('#7CE38A'))
    return outlined(p, rgb('#0A0A0C'))


def dj_table():
    p = prop(32, 24)
    top, front, frontd = rgb('#3A3540'), rgb('#26222B'), rgb('#1C1920')
    p.rect(0, 0, 31, 11, top)
    p.hline(0, 31, 0, rgb('#544C5E'))
    p.rect(0, 12, 31, 20, front)
    p.hline(0, 31, 12, mix(top, WHITE, 0.15))
    p.rect(1, 21, 3, 23, frontd)
    p.rect(28, 21, 30, 23, frontd)
    for (cx, cy) in ((8.5, 5.5), (23.5, 5.5)):
        for y in range(12):
            for x in range(32):
                d = math.hypot(x - cx, (y - cy) * 1.25)
                if d <= 5:
                    c = rgb('#0E0E10')
                    if d < 1.6:
                        c = rgb('#B13FD0')
                    elif 2.8 < d < 3.4:
                        c = rgb('#2A2A30')
                    p.set(x, y, c)
    for x in range(14, 18):
        for y in range(3, 9):
            p.set(x, y, rgb('#4A4452'))
    p.set(15, 4, rgb('#F4C04F'))
    p.set(16, 6, rgb('#7CE38A'))
    p.set(15, 7, rgb('#FF6AD5'))
    return outlined(p, rgb('#0A080C'))


def desk():
    p = prop(32, 24)
    top, topd, front, frontd = rgb('#DDBE8E'), rgb('#C9A878'), rgb('#C29A68'), rgb('#A27E50')
    p.rect(0, 0, 31, 9, top)
    p.hline(0, 31, 0, mix(top, WHITE, 0.3))
    p.rect(0, 10, 31, 20, front)
    p.hline(0, 31, 10, topd)
    p.rect(2, 12, 13, 18, frontd)
    p.hline(6, 9, 15, rgb('#D9C7A8'))
    p.rect(1, 21, 2, 23, frontd)
    p.rect(29, 21, 30, 23, frontd)
    # caderno, porta-canetas
    p.rect(4, 2, 13, 7, rgb('#2A3140'))
    p.hline(4, 13, 2, rgb('#3E4860'))
    p.rect(22, 1, 25, 6, rgb('#1C1C20'))
    p.set(22, 0, rgb('#D04040'))
    p.set(23, 0, rgb('#3070D0'))
    p.set(24, 0, rgb('#F0C040'))
    return outlined(p, rgb('#4A3418'))


def counter():
    p = prop(48, 24)
    top, oak, oakd = rgb('#F4F4F2'), rgb('#D9B786'), rgb('#C29E6C')
    p.rect(0, 0, 47, 9, top)
    p.hline(0, 47, 9, rgb('#D6D6D3'))
    p.rect(0, 10, 47, 22, oak)
    for x in range(1, 47, 3):
        p.vline(x, 11, 21, oakd)
    p.hline(0, 47, 22, rgb('#E8E8E6'))
    p.hline(0, 47, 23, rgb('#BDBDBA'))
    # campainha dourada
    p.hline(34, 40, 6, rgb('#2A2A2E'))
    for x, y in ((35, 5), (36, 5), (37, 5), (38, 5), (39, 5), (36, 4), (37, 4), (38, 4), (37, 3)):
        p.set(x, y, rgb('#E2B648'))
    p.set(36, 4, rgb('#FFF0B0'))
    # monitor de lado e papéis
    p.rect(6, 2, 15, 6, rgb('#FAFAF8'))
    p.hline(7, 13, 3, rgb('#C9CBD0'))
    p.hline(7, 11, 5, rgb('#C9CBD0'))
    return outlined(p, rgb('#5A4A30'))


def bowl():
    p = prop(16, 16)
    for y in range(16):
        for x in range(16):
            d = ((x - 7.5) / 6.5) ** 2 + ((y - 10) / 3.6) ** 2
            if d <= 1:
                p.set(x, y, rgb('#D83A33') if y > 9 else rgb('#EE5A50'))
    for y in range(16):
        for x in range(16):
            d = ((x - 7.5) / 5) ** 2 + ((y - 8.5) / 2.2) ** 2
            if d <= 1:
                p.set(x, y, rgb('#6E3A1E'))
    for i, (x, y) in enumerate(((5, 8), (7, 7), (9, 8), (10, 9), (6, 9), (8, 9))):
        p.set(x, y, rgb('#C27C40') if i % 2 else rgb('#9A5C2E'))
    return outlined(p, rgb('#6E1612'))


def ball():
    p = prop(8, 8)
    for y in range(8):
        for x in range(8):
            d = math.hypot(x - 3.5, y - 3.5)
            if d <= 3.2:
                p.set(x, y, rgb('#D7EA3A') if d < 2.4 else rgb('#A9BC22'))
    for x, y in ((1, 2), (2, 3), (3, 3), (4, 4), (5, 5)):
        p.set(x, y, rgb('#F7F7EE'))
    p.set(2, 1, rgb('#F2FBA0'))
    return outlined(p, rgb('#5A6410'))


def bone_toy():
    p = prop(16, 8)
    c, d = rgb('#F3EEE2'), rgb('#C7BFA9')
    p.rect(4, 3, 11, 4, c)
    p.hline(4, 11, 4, d)
    for ex in (2, 13):
        p.rect(ex - 1, 1, ex, 2, c)
        p.rect(ex - 1, 5, ex, 6, d)
        p.rect(ex - 1, 3, ex, 4, c)
    return outlined(p, rgb('#6E6450'))


def dog_bed():
    p = prop(48, 24)
    rim, rimd, rimh = rgb('#C9A57A'), rgb('#9C7A50'), rgb('#E3C79F')
    pad, padd = rgb('#F1E3C6'), rgb('#D8C49E')
    for y in range(24):
        for x in range(48):
            d = ((x - 23.5) / 23) ** 2 + ((y - 11.5) / 11) ** 2
            if d <= 1:
                p.set(x, y, rimd if y > 14 else rim)
    for y in range(24):
        for x in range(48):
            d = ((x - 23.5) / 17) ** 2 + ((y - 10) / 6.5) ** 2
            if d <= 1:
                p.set(x, y, padd if y < 7 else pad)
    for x in range(12, 36):
        p.set(x, 2, rimh)
    return outlined(p, rgb('#5E4426'))


# ---------------------------------------------------------------- salas
def deck(x, y):
    """Deck de barco: duas tábuas por tile (uma inteira, outra emendada),
    com veio no sentido do comprimento."""
    plank = (y // 8) % 2
    base = (rgb('#BF8B58'), rgb('#B2804F'))[plank]
    yy = y % 8
    if yy == 7:
        return rgb('#86593A')
    if yy == 0:
        return mix(base, rgb('#FFFFFF'), 0.1)
    if plank == 0 and x % 16 == 0:
        return rgb('#93653E')
    if (yy == 3 and (x * 3) % 7 < 3) or (yy == 5 and (x * 5 + 2) % 9 < 2):
        return mul(base, 0.93)
    return base


def sala_guilherme():
    cv = Canvas(W, H)

    def wall(x, y):
        if 32 <= y <= 37:
            return rgb('#36BFC2') if y > 32 else rgb('#5ED0D2')
        if y == 38:
            return rgb('#2795A0')
        return rgb('#F3EFE6') if (x // 2 + y) % 9 else rgb('#ECE7DC')

    room(cv, wall, deck, rgb('#6E4A2C'), rgb('#E6E0D2'))
    cv.paste(window_sea(), tx(1), 6)
    cv.paste(lifebuoy(), tx(6), 12)
    cv.paste(palm(), tx(1), ty(3) - 8)
    return cv, 'Guilherme'


def sala_gabriel():
    cv = Canvas(W, H)

    def wall(x, y):
        base = rgb('#45306E')
        return mul(base, 1.12) if ((x // 4) + (y // 4)) % 2 else mul(base, 0.92)

    def tiles(x, y):
        if x % 16 == 0 or y % 16 == 0:
            return rgb('#262D30')
        return rgb('#3E494C') if ((x // 16) + (y // 16)) % 2 else rgb('#353F42')

    room(cv, wall, tiles, rgb('#1E1530'), rgb('#2A1E44'))
    # luz roxa no chão
    for y in range(ty(WALL_ROWS), H):
        for x in range(SIDE, W - SIDE):
            d = ((x - (tx(CHAR_COL) + 8)) / 52) ** 2 + ((y - ty(FEET_ROW + 1)) / 34) ** 2
            if d < 1:
                cv.set(x, y, mix(cv.get(x, y), rgb('#8A4FD8'), 0.3 * (1 - d)))
    cv.paste(neon_on_air(), tx(1), 14)
    cv.paste(framed(art_record, rgb('#C9A24A'), rgb('#2B2433')), tx(6), 12)
    cv.paste(dj_table(), tx(1), ty(3))
    cv.paste(speaker(), tx(7), ty(2) + 8)
    return cv, 'Gabriel'


def sala_flora():
    cv = Canvas(W, H)

    def wall(x, y):
        if y >= 28:
            if x % 16 == 0:
                return rgb('#A98762')
            return rgb('#C9A57E') if y != 28 else rgb('#E0C49E')
        return rgb('#F5E9D6') if (x // 2 + y // 2) % 7 else rgb('#EADCC6')

    def blanket(x, y):
        a, b = (x + y) % 16, (x - y) % 16
        if a == 0 or b == 0:
            return rgb('#9B201D')
        if a == 1 or b == 1:
            return rgb('#E45246')
        return rgb('#CC322D')

    room(cv, wall, blanket, rgb('#7A5232'), rgb('#9C7A54'))
    cv.paste(framed(art_bone, rgb('#7A5232'), rgb('#9ED2EE')), tx(2), 8)
    cv.paste(framed(art_heart, rgb('#7A5232'), rgb('#FBF3E6')), tx(6), 8)
    cv.paste(bowl(), tx(2), ty(6))
    cv.paste(ball(), tx(6) + 4, ty(8) + 4)
    return cv, 'Flora'


def sala_lupin():
    cv = Canvas(W, H)

    def wall(x, y):
        return rgb('#B6CDE0') if x % 8 == 0 else rgb('#D3E7F5')

    def plaid(x, y):
        navy, mid, light, line = rgb('#1E2C5C'), rgb('#2F4383'), rgb('#4462AE'), rgb('#DCE3F2')
        a, b = x % 16, y % 16
        ca = 2 if a < 4 else (1 if a < 6 else 0)
        cb = 2 if b < 4 else (1 if b < 6 else 0)
        c = [navy, mid, light][max(ca, cb)] if ca != cb else [navy, light, light][ca]
        if a == 10 or b == 10:
            c = mix(line, c, 0.55)
        return c

    room(cv, wall, plaid, rgb('#2F4383'), rgb('#9DB6CC'))
    cv.paste(framed(art_paw, rgb('#7A5232'), rgb('#F6E9C9')), tx(2), 8)
    cv.paste(framed(lambda p: art_bone(p), rgb('#2F4383'), rgb('#F3C64E')), tx(6), 8)
    cv.paste(dog_bed(), tx(3), ty(6) + 14)
    cv.paste(bone_toy(), tx(1), ty(8) + 4)
    return cv, 'Lupin'


def sala_saldanha():
    cv = Canvas(W, H)
    rug = (tx(2), ty(6), tx(7) - 1, ty(10) - 1)

    def wall(x, y):
        return rgb('#8D9C7D') if (x * 3 + y * 7) % 23 else rgb('#86957A')

    def stone(x, y):
        if rug[0] <= x <= rug[2] and rug[1] <= y <= rug[3]:
            if x in (rug[0], rug[0] + 1, rug[2], rug[2] - 1) or y in (rug[1], rug[1] + 1, rug[3], rug[3] - 1):
                return rgb('#7E7F80')
            return rgb('#9C9D9B') if (x * 13 + y * 7) % 29 == 0 else rgb('#A9AAA8')
        if x % 16 == 0 or y % 16 == 0:
            return rgb('#A39E95')
        return rgb('#C9C4BB') if ((x // 16) + (y // 16)) % 2 else rgb('#C1BCB3')

    room(cv, wall, stone, rgb('#4E5A44'), rgb('#F0EEE8'))
    cv.paste(window_city(), tx(1), 6)
    cv.paste(framed(art_chart, rgb('#3A3A40'), rgb('#FAFAF7')), tx(6), 10)
    cv.paste(big_leaf(), tx(1), ty(3) - 6)
    cv.paste(desk(), tx(6), ty(3))
    return cv, 'Saldanha'


def sala_caio():
    cv = Canvas(W, H)

    def slats(x, y):
        if x % 4 == 0:
            return rgb('#9C7646')
        return rgb('#D7B585') if (x // 4) % 2 else rgb('#CBA877')

    def tiles(x, y):
        if x % 16 == 0 or y % 16 == 0:
            return rgb('#A7A9AB')
        k = ((x // 16) * 3 + (y // 16)) % 4
        return (rgb('#CACCCD'), rgb('#C2C4C5'), rgb('#C6C8C9'), rgb('#BEC0C1'))[k]

    room(cv, slats, tiles, rgb('#6E5434'), rgb('#F2F2F0'))

    def sign(p):
        p.rect(1, 1, 14, 14, rgb('#3DB64B'))
        p.hline(2, 13, 1, rgb('#6ACF72'))
        art_check(p)
    cv.paste(framed(sign, rgb('#25803A'), rgb('#3DB64B')), tx(2), 10)
    cv.paste(ficus(), tx(1), ty(3) - 6)
    cv.paste(counter(), tx(5), ty(3))
    return cv, 'Caio'


SALAS = [('01-guilherme', sala_guilherme, 'guilherme'), ('02-gabriel', sala_gabriel, 'gabriel'),
         ('03-flora', sala_flora, 'flora'), ('04-lupin', sala_lupin, 'lupin'),
         ('05-saldanha', sala_saldanha, 'saldanha'), ('06-caio', sala_caio, 'caio')]


def tileset(im, cols=8):
    """Fatia o fundo em tiles de 16x16 e junta os diferentes numa folha."""
    seen, tiles = set(), []
    for r in range(ROWS):
        for c in range(COLS):
            t = im.crop((c * T, r * T, c * T + T, r * T + T))
            key = t.tobytes()
            if key not in seen:
                seen.add(key)
                tiles.append(t)
    rows_ = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * T, rows_ * T), (0, 0, 0, 0))
    for i, t in enumerate(tiles):
        sheet.alpha_composite(t, ((i % cols) * T, (i // cols) * T))
    return sheet, len(tiles)


def grid_overlay(im, k):
    big = up(im, k).convert('RGBA')
    px = big.load()
    for y in range(big.height):
        for x in range(big.width):
            if x % (T * k) == 0 or y % (T * k) == 0:
                r, g, b, a = px[x, y]
                px[x, y] = (min(255, r + 70), min(255, g + 70), min(255, b + 90), 255)
    return big


def build():
    sprites = dict((n, f()) for n, f in sprites16.ALL16)
    dirs = {k: os.path.join(OUT, k) for k in ('personagens', 'cenas', 'tilesets')}
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)

    # sprites soltos, fundo transparente
    for name, im in sprites.items():
        im.save(os.path.join(dirs['personagens'], f'{name}-16x32.png'))
        for k in (3, 4):
            up(im, k).save(os.path.join(dirs['personagens'], f'{name}-16x32@{k}x.png'))
    sheet = Image.new('RGBA', (T * len(sprites), 2 * T), (0, 0, 0, 0))
    for i, im in enumerate(sprites.values()):
        sheet.alpha_composite(im, (i * T, 0))
    sheet.save(os.path.join(dirs['personagens'], 'todos-spritesheet.png'))
    for k in (3, 4):
        up(sheet, k).save(os.path.join(dirs['personagens'], f'todos-spritesheet@{k}x.png'))

    scenes = []
    for fname, fn, who in SALAS:
        cv, label = fn()
        bg = cv.im.copy()
        ts, n = tileset(bg)
        ts.save(os.path.join(dirs['tilesets'], f'{fname}-tileset.png'))
        sp = sprites[who]
        x0, y0 = tx(CHAR_COL), ty(FEET_ROW + 1) - 2 * T
        top = sp.getbbox()[1]
        shadow(cv, x0 + 8, y0 + 31, 6, 2)
        cv.paste(sp, x0, y0)
        nametag(cv, label, x0 + 8, y0 + top - 1)
        cv.im.save(os.path.join(dirs['cenas'], f'{fname}.png'))
        for k in (3, 4):
            up(cv.im, k).save(os.path.join(dirs['cenas'], f'{fname}@{k}x.png'))
        grid_overlay(cv.im, 4).save(os.path.join(dirs['cenas'], f'{fname}-grade@4x.png'))
        scenes.append(cv.im)
        print(f'{fname}: {n} tiles únicos')

    gap, cols = 4, 3
    rows_ = (len(scenes) + cols - 1) // cols
    allsheet = Image.new('RGBA', (W * cols + gap * (cols + 1), H * rows_ + gap * (rows_ + 1)),
                         (11, 17, 38, 255))
    for i, im in enumerate(scenes):
        allsheet.alpha_composite(im, (gap + (i % cols) * (W + gap), gap + (i // cols) * (H + gap)))
    up(allsheet, 3).save(os.path.join(OUT, '00-todos-grade16@3x.png'))


if __name__ == '__main__':
    build()
