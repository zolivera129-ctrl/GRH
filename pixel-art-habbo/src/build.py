"""Monta as quatro artes. Uso: python3 build.py  (gera ../out/*.png)"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from px import Sprite, Layer, rgb, mul, mix  # noqa: E402
from scene import (W, H, CX, YC, room, stars, on_wall, paste, shadow, nametag,  # noqa: E402
                   finish, iso_block, iso_box, draw_text, MINI, text_width, floor_edge)
import chars  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), '..', 'out')
WHITE = rgb('#FFFFFF')
FEET_Y = 108


def place(S, sprite, feet_x, feet_y=FEET_Y, sh=(13, 4)):
    """Põe o personagem com o meio dos pés em (feet_x, feet_y)."""
    bbox = sprite.getbbox()
    cx = (bbox[0] + bbox[2]) // 2
    shadow(S, feet_x, feet_y - 1, *sh)
    x0, y0 = feet_x - cx, feet_y - bbox[3]
    paste(S, sprite, x0, y0)
    return y0 + bbox[1]       # topo do personagem


def ring(w, cx, cy, r0, r1, colfn):
    sp = Sprite(w, w)
    for y in range(w):
        for x in range(w):
            d = math.hypot(x - cx, y - cy)
            if r0 <= d <= r1:
                sp.set(x, y, colfn(x - cx, y - cy, d))
    return sp


def frame(w, h, wood, inner):
    sp = Sprite(w, h)
    L = Layer(wood, mul(wood, 0.6))
    L.rect(0, 0, w - 1, h - 1)
    L.outline()
    for x in range(1, w - 1):
        L.set(x, 1, mix(wood, WHITE, 0.25))
    L.rect(2, 2, w - 3, h - 3, inner)
    for x in range(2, w - 2):
        L.set(x, 2, mul(inner, 0.85))
    sp.add(L)
    return sp


# ------------------------------------------------------------------ mobis
def potted_palm(S, x, y):
    shadow(S, x, y - 3, 9, 4)
    top = iso_block(S, x, y, 3, 6, rgb('#7A4A2C'), rgb('#C4673A'), rgb('#A9532D'))
    for i in range(-4, 5):
        S.set(x + i, top - 1 + abs(i) // 3, rgb('#3B2416'))
    # tronco
    for k in range(14):
        S.set(x + (k // 6), top - 2 - k, rgb('#8A6238') if k % 3 else rgb('#5E4126'))
        S.set(x + 1 + (k // 6), top - 2 - k, rgb('#A97C4A'))
    # folhas
    leaf, leafd, leafl = rgb('#4E9A34'), rgb('#2F6A21'), rgb('#7CC24E')
    cx, cy = x + 2, top - 16
    fronds = [(-10, 4), (-8, -3), (-3, -7), (4, -7), (9, -3), (11, 4), (-5, 6), (6, 6)]
    for fx, fy in fronds:
        n = max(abs(fx), abs(fy))
        for t in range(n + 1):
            px = cx + round(fx * t / n)
            py = cy + round(fy * t / n + (t / n) ** 2 * 3)
            S.set(px, py, leaf)
            S.set(px, py + 1, leafd)
            if t % 2:
                S.set(px, py - 1, leafl)
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (1, 1)):
        S.set(cx + dx, cy + dy, leafd)


def window_sea():
    sp = frame(26, 21, rgb('#9A6A40'), rgb('#A9DDF4'))
    sky2 = rgb('#CFEFFA')
    for y in range(3, 9):
        for x in range(2, 24):
            if y > 5:
                sp.set(x, y, sky2)
    for x, y in ((5, 4), (6, 4), (7, 4), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5),
                 (16, 3), (17, 3), (15, 4), (16, 4), (17, 4), (18, 4)):
        sp.set(x, y, rgb('#FFFFFF'))
    hill = {7: (10, 15), 8: (7, 19), 9: (4, 22), 10: (2, 23), 11: (2, 23)}
    for y, (x0, x1) in hill.items():
        for x in range(x0, x1 + 1):
            sp.set(x, y, rgb('#5C9440') if (x + y) % 5 else rgb('#3F7030'))
    for x in range(2, 24):
        sp.set(x, 12, rgb('#C9B48A') if x % 3 else rgb('#9C8A66'))
    for y in range(13, 19):
        for x in range(2, 24):
            c = rgb('#30C7CC') if y < 16 else rgb('#21B4BE')
            if (x * 3 + y * 5) % 11 == 0:
                c = rgb('#B8F3F0')
            sp.set(x, y, c)
    # cruzeta da janela
    for y in range(2, 19):
        sp.set(12, y, rgb('#9A6A40'))
        sp.set(13, y, rgb('#7A5030'))
    for x in range(2, 24):
        sp.set(x, 10, rgb('#9A6A40'))
    return sp.image()


def lifebuoy():
    red, white = rgb('#E2452F'), rgb('#F6F4EE')

    def col(dx, dy, d):
        if d > 5.6 or d < 3.2:
            return rgb('#7E2418') if d > 5.6 else rgb('#8E8A80')
        a = math.atan2(dy, dx)
        seg = int(((a + math.pi) / (math.pi / 2)) + 0.5) % 4
        c = red if seg % 2 == 0 else white
        return mix(c, WHITE, 0.25) if dy < -1 and d > 4.5 else c
    sp = ring(14, 6.5, 6.5, 2.6, 6.4, col)
    return sp.image()


def neon_on_air(S, x0, vtop):
    """Letreiro ON AIR na parede da esquerda. A caixa segue a inclinação da
    parede; cada letra sobe inteira (sem se deformar) para continuar legível."""
    w, h = 27, 11
    box = Sprite(w, h)
    L = Layer(rgb('#17121C'), rgb('#3A2C46'))
    L.rect(0, 0, w - 1, h - 1)
    L.outline()
    box.add(L)
    on_wall(S, box.image(), 'l', x0, vtop)
    pink, glow, hot = rgb('#FF6AD5'), rgb('#7E2D74'), rgb('#FFD3F4')
    gx = x0 + 3
    for ch in 'ON AIR':
        g = MINI[ch]
        gw = len(g[0])
        mid = gx + gw // 2
        top = floor_edge(mid) - vtop + 3
        pts = [(gx + i, top + j) for j, row in enumerate(g) for i, v in enumerate(row) if v == '#']
        for (x, y) in pts:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q not in pts:
                    S.set(*q, glow)
        for (x, y) in pts:
            S.set(x, y, pink)
        if pts:
            S.set(*pts[0], hot)
        gx += gw + 1


def gold_record():
    sp = frame(16, 19, rgb('#C9A24A'), rgb('#2B2433'))

    def col(dx, dy, d):
        if d <= 1.6:
            return rgb('#E9C35B')
        if d <= 2.4:
            return rgb('#B8902F')
        c = rgb('#D9B04C') if (int(d * 2) % 2) else rgb('#B48E35')
        return mix(c, WHITE, 0.4) if (dx < 0 and dy < 0 and 3 < d < 4.5) else c
    disc = ring(13, 6, 6, 0, 5.5, col)
    for (x, y), c in disc.px.items():
        sp.set(x + 2, y + 2, c)
    for x in range(4, 12):
        sp.set(x, 15, rgb('#E9DDB8'))
    return sp.image()


def speaker(S, x, y):
    shadow(S, x, y - 2, 8, 3)
    h, hh = 3, 15
    iso_block(S, x, y, h, hh, rgb('#4A4A55'), rgb('#2E2E36'), rgb('#23232A'))
    # cones na face da direita
    for (ck, r) in ((4, 2.2), (10, 1.4)):
        for i in range(0, 2 * h + 1):
            for k in range(hh):
                d = math.hypot(i - h, k - ck)
                if d <= r:
                    c = rgb('#0F0F12') if d > r - 0.8 else rgb('#5A5A66')
                    S.set(x + i, y - i // 2 - k - 1, c)
    S.set(x + 4, y - 2 - 13, rgb('#7CE38A'))


def turntable(S, x, y):
    shadow(S, x, y - 2, 12, 4)
    top = iso_block(S, x, y, 5, 4, rgb('#3A3540'), rgb('#26222B'), rgb('#1C1920'))
    for yy in range(top - 4, top + 4):
        for xx in range(x - 9, x + 7):
            d = ((xx - (x - 1)) / 7) ** 2 + ((yy - top) / 3.4) ** 2
            if d <= 1:
                c = rgb('#0E0E10') if d > 0.25 else rgb('#B13FD0')
                if 0.45 < d < 0.6:
                    c = rgb('#2A2A30')
                S.set(xx, yy, c)
    for k in range(5):
        S.set(x + 6, top - 3 + k // 2 + k, rgb('#C9C9D2'))
    S.set(x + 7, top - 3, rgb('#FFFFFF'))


def bowl(S, x, y, rim, inside):
    shadow(S, x, y, 8, 3)
    for yy in range(y - 6, y + 2):
        for xx in range(x - 8, x + 9):
            body = ((xx - x) / 7.5) ** 2 + ((yy - (y - 1)) / 2.6) ** 2 <= 1 or \
                (abs(xx - x) <= 7 - (yy - (y - 4)) * 0.4 and y - 4 <= yy <= y)
            if body:
                S.set(xx, yy, rim if xx < x + 3 else mul(rim, 0.8))
    for yy in range(y - 7, y - 2):
        for xx in range(x - 8, x + 9):
            d = ((xx - x) / 7.5) ** 2 + ((yy - (y - 5)) / 2.4) ** 2
            if d <= 1:
                S.set(xx, yy, mix(rim, WHITE, 0.35) if d > 0.55 else inside)
    for i, (dx, dy) in enumerate(((-3, -5), (-1, -6), (1, -5), (3, -6), (0, -4), (-2, -4), (2, -4))):
        S.set(x + dx, y + dy, rgb('#9A5C2E') if i % 2 else rgb('#C27C40'))


def ball(S, x, y):
    shadow(S, x, y, 3, 1)
    for yy in range(y - 5, y + 1):
        for xx in range(x - 3, x + 4):
            d = math.hypot(xx - x, (yy - (y - 2.5)))
            if d <= 3.1:
                c = rgb('#D7EA3A') if d < 2.3 else rgb('#A9BC22')
                S.set(xx, yy, c)
    for xx, yy in ((x - 2, y - 4), (x - 1, y - 3), (x, y - 3), (x + 1, y - 2), (x + 2, y - 1)):
        S.set(xx, yy, rgb('#F7F7EE'))
    S.set(x - 1, y - 5, rgb('#F2FBA0'))


def bone_sprite(c=rgb('#F3EEE2')):
    sp = Sprite(13, 7)
    L = Layer(c, mul(c, 0.65))
    L.rows({0: [(0, 1), (11, 12)], 1: [(0, 2), (10, 12)], 2: (1, 11), 3: (1, 11), 4: (1, 11),
            5: [(0, 2), (10, 12)], 6: [(0, 1), (11, 12)]})
    L.outline()
    for x in range(3, 10):
        L.set(x, 2, mix(c, WHITE, 0.5))
    sp.add(L)
    return sp.image()


def floor_bone(S, x, y):
    """Osso deitado no chão, na diagonal do piso."""
    shadow(S, x + 1, y, 7, 2)
    c, d = rgb('#F3EEE2'), rgb('#B5AC98')
    pts = [(i, -i // 2) for i in range(-5, 6)]
    for (i, j) in pts:
        S.set(x + i, y + j - 1, c)
        S.set(x + i, y + j, mix(c, d, 0.5))
    for ex, ey in ((x - 6, y + 2), (x + 6, y - 3)):
        for dx, dy in ((0, 0), (1, 0), (0, -1), (-1, -1), (0, 1), (-1, 0), (1, -1)):
            S.set(ex + dx, ey + dy - 1, c)
        S.set(ex, ey, d)
        S.set(ex + 1, ey, d)


def dog_bed(S, x, y):
    """Caminha oval de pet: borda fofinha com lateral aparente e almofada
    afundada no meio."""
    top, side, sided, hi = rgb('#D2AE80'), rgb('#A9814F'), rgb('#86623A'), rgb('#EBD2A8')
    pad, padd = rgb('#F0E2C4'), rgb('#CDB78F')
    rx, ry, lift = 20, 8, 4
    cy = y - lift
    shadow(S, x, y + 1, rx + 1, ry)

    def inside(xx, yy, cx_, cy_, a, b):
        return ((xx - cx_) / a) ** 2 + ((yy - cy_) / b) ** 2 <= 1
    for yy in range(cy - ry - 1, y + ry + 2):
        for xx in range(x - rx - 1, x + rx + 2):
            t = inside(xx, yy, x, cy, rx, ry)
            sd = inside(xx, yy, x, y, rx, ry)
            if t:
                S.set(xx, yy, top)
            elif sd and yy > cy:
                S.set(xx, yy, side if xx < x + rx // 2 else sided)
    # contorno de baixo da lateral
    for xx in range(x - rx, x + rx + 1):
        yy = y + round(ry * (1 - ((xx - x) / rx) ** 2) ** 0.5)
        S.set(xx, yy, mul(sided, 0.75))
    # brilho na borda da frente
    for xx in range(x - rx + 4, x + rx - 3):
        yy = cy + round(ry * (1 - ((xx - x) / rx) ** 2) ** 0.5) - 1
        S.set(xx, yy, hi)
    # almofada afundada
    for yy in range(cy - ry, cy + ry):
        for xx in range(x - rx, x + rx + 1):
            if inside(xx, yy, x, cy, rx - 5, ry - 3):
                edge = not inside(xx, yy - 2, x, cy, rx - 5, ry - 3)
                S.set(xx, yy, padd if edge else pad)


def paw_print(c):
    rows = ["...##.##...",
            "...##.##...",
            ".##.....##.",
            ".##.###.##.",
            "...#####...",
            "..#######..",
            "..#######..",
            "...##.##..."]
    sp = Sprite(len(rows[0]), len(rows))
    for y, row in enumerate(rows):
        for x, v in enumerate(row):
            if v == '#':
                sp.set(x, y, c)
    return sp.image()


def heart(c):
    sp = Sprite(9, 8)
    rows = {0: [(1, 2), (6, 7)], 1: (0, 8), 2: (0, 8), 3: (1, 7), 4: (2, 6), 5: (3, 5), 6: (4, 4)}
    L = Layer(c, mul(c, 0.6))
    L.rows(rows)
    L.outline()
    L.set(2, 1, mix(c, WHITE, 0.6))
    sp.add(L)
    return sp.image()


def framed(art, w, h, wood, inner):
    sp = frame(w, h, wood, inner)
    im = sp.image()
    im.alpha_composite(art, ((w - art.width) // 2, (h - art.height) // 2 + 1))
    return im


def window_city():
    sp = frame(24, 22, rgb('#DADAD6'), rgb('#BFD9EA'))
    for y in range(2, 20):
        for x in range(2, 22):
            sp.set(x, y, mix(rgb('#D3E9F5'), rgb('#9CC6E2'), (y - 2) / 18))
    for x0, x1, top, col in ((2, 5, 9, '#8EA3B5'), (6, 9, 6, '#A9B8C6'), (10, 13, 11, '#7F95A8'),
                             (14, 17, 7, '#B4C2CF'), (18, 21, 10, '#91A5B7')):
        for x in range(x0, x1 + 1):
            for y in range(top, 20):
                c = rgb(col)
                if y > top and (y - top) % 2 == 0 and x not in (x0, x1) and (x - x0) % 2:
                    c = mix(c, rgb('#FFFFFF'), 0.45)
                sp.set(x, y, c)
    for y in range(2, 20):
        sp.set(11, y, rgb('#DADAD6'))
        sp.set(12, y, rgb('#B9B9B4'))
    for x in range(2, 22):
        sp.set(x, 11, rgb('#DADAD6'))
    return sp.image()


def chart_frame():
    """Quadro com gráfico de barras subindo (o contador gosta)."""
    sp = frame(19, 16, rgb('#3A3A40'), rgb('#FAFAF7'))
    for x in range(3, 11):
        sp.set(x, 3, rgb('#B9BCC2'))
    for x in range(3, 8):
        sp.set(x, 4, rgb('#D5D7DB'))
    for i, h in enumerate((2, 4, 3, 6, 8)):
        x0 = 3 + i * 3
        for x in (x0, x0 + 1):
            for y in range(13 - h, 13):
                sp.set(x, y, rgb('#3DB64B') if x == x0 else rgb('#2C9440'))
    for x in range(2, 17):
        sp.set(x, 13, rgb('#8A8D94'))
    for x, y in ((13, 6), (14, 5), (15, 4), (15, 5), (14, 4)):
        sp.set(x, y, rgb('#E2453C'))
    return sp.image()


def check_badge():
    """Placa verde com check branco (quadrado de canto arredondado: inclinado
    na parede continua lendo como placa)."""
    green, dark, light = rgb('#3DB64B'), rgb('#25803A'), rgb('#6ACF72')
    sp = Sprite(16, 16)
    L = Layer(green, dark)
    L.rect(0, 0, 15, 15)
    for p in ((0, 0), (15, 0), (0, 15), (15, 15)):
        L.px.pop(p)
    L.outline()
    for x in range(2, 14):
        L.set(x, 1, light)
    sp.add(L)
    for x, y in ((3, 8), (4, 9), (5, 10), (6, 11), (7, 10), (8, 9), (9, 8), (10, 7),
                 (11, 6), (12, 5)):
        for k in (0, 1):
            sp.set(x, y + k, rgb('#FFFFFF'))
    return sp.image()


def leaf(S, x0, y0, dx, dy, width, c, cd, cl):
    n = max(abs(dx), abs(dy))
    for t in range(n + 1):
        f = t / n
        x = x0 + round(dx * f)
        y = y0 + round(dy * f)
        w = round(width * (4 * f * (1 - f))) if f > 0.25 else 0
        for k in range(-w, w + 1):
            S.set(x + k, y, cd if k == w else (cl if k == -w else c))
        S.set(x, y, cd)


def big_leaf_plant(S, x, y):
    """Planta de folhas largas num vaso redondo cimento."""
    shadow(S, x, y - 1, 9, 3)
    pot, potd, potl = rgb('#D6D3CC'), rgb('#A8A49C'), rgb('#ECEAE5')
    for yy in range(y - 10, y + 1):
        for xx in range(x - 7, x + 8):
            if abs(xx - x) <= 7 - max(0, yy - (y - 3)):
                S.set(xx, yy, pot if xx < x + 3 else potd)
    for xx in range(x - 7, x + 8):
        S.set(xx, y - 10, potl)
        S.set(xx, y - 11, potd)
    g, gd, gl = rgb('#3F8A3A'), rgb('#25602A'), rgb('#6DB55A')
    for dx, dy, w in ((-12, -14, 3), (-6, -22, 3), (2, -26, 3), (9, -20, 3), (13, -11, 2), (-3, -16, 2)):
        leaf(S, x + (1 if dx > 0 else -1), y - 11, dx, dy, w, g, gd, gl)


def desk(S, x, y):
    shadow(S, x + 4, y - 4, 14, 5)
    top = iso_box(S, x, y, 7, 3, 10, rgb('#DDBE8E'), rgb('#C79F6C'), rgb('#AE8858'))
    # caderno e porta-canetas em cima
    for yy in range(y - 24, y - 8):
        for xx in range(x - 8, x + 16):
            st = top(xx, yy)
            if st and 1.0 <= st[0] <= 4.0 and 0.6 <= st[1] <= 2.4:
                edge = st[0] < 1.4 or st[1] < 0.9
                S.set(xx, yy, rgb('#1F2633') if not edge else rgb('#3A4560'))
    px_, py_ = x + 11, y - 18
    for k in range(5):
        S.set(px_, py_ - k, rgb('#1C1C20'))
        S.set(px_ + 1, py_ - k, rgb('#2E2E34'))
    for dx, h, c in ((0, 3, '#D04040'), (1, 4, '#3070D0'), (1, 2, '#F0C040')):
        for k in range(h):
            S.set(px_ + dx, py_ - 5 - k, rgb(c))
    # gaveta
    for i in range(0, 6):
        S.set(x - 5 + i, y - 6 + (5 - i) // 2 - 2, rgb('#9C7849'))


def ficus(S, x, y):
    shadow(S, x, y - 1, 8, 3)
    pot, potd = rgb('#8F9396'), rgb('#6C7073')
    for yy in range(y - 9, y + 1):
        for xx in range(x - 6, x + 7):
            if abs(xx - x) <= 6 - max(0, yy - (y - 3)):
                S.set(xx, yy, pot if xx < x + 2 else potd)
    for xx in range(x - 6, x + 7):
        S.set(xx, y - 9, rgb('#B4B8BA'))
    for k in range(30):
        S.set(x + (1 if k % 9 < 4 else 0), y - 10 - k, rgb('#7A5A3A'))
    g, gd, gl = rgb('#3E8C3C'), rgb('#265F28'), rgb('#74C05E')
    import random
    rnd = random.Random(7)
    for _ in range(320):
        cx_ = x + rnd.randint(-12, 12)
        cy_ = y - 31 + rnd.randint(-13, 11)
        if ((cx_ - x) / 12) ** 2 + ((cy_ - (y - 30)) / 15) ** 2 <= 1:
            c = rnd.choice([g, g, gd, gl])
            S.set(cx_, cy_, c)
            S.set(cx_ + 1, cy_, c)
            S.set(cx_, cy_ + 1, gd)


def counter(S, x, y):
    """Balcão de recepção: frente de madeira clara, tampo branco e a campainha."""
    shadow(S, x + 8, y - 5, 20, 6)
    oak, oakd = rgb('#D9B786'), rgb('#C29E6C')
    top = iso_box(S, x, y, 10, 4, 13, rgb('#F4F4F2'), oak, oakd)
    # rodapé branco
    for xi in range(x - 8, x + 21):
        yb = y - (abs(xi - x)) // 2
        S.set(xi, yb - 1, rgb('#E8E8E6'))
    # veio da madeira
    for xi in range(x - 7, x + 20, 3):
        yb = y - abs(xi - x) // 2
        for k in range(3, 12, 2):
            S.set(xi, yb - k, mul(oak if xi < x else oakd, 0.94))
    # campainha dourada
    bx, by = x + 9, y - 18
    for dx in range(-3, 4):
        S.set(bx + dx, by, rgb('#2A2A2E'))
    for dx, dy in ((-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1), (-1, -2), (0, -2), (1, -2)):
        S.set(bx + dx, by + dy, rgb('#E2B648'))
    S.set(bx - 1, by - 2, rgb('#FFF0B0'))
    S.set(bx, by - 3, rgb('#B88A28'))


# ---------------------------------------------------------------- cenas
def scene_guilherme():
    S = Sprite(W, H)
    stars(S, 11, rgb('#0B1126'))
    cream_l, cream_r = rgb('#F3EFE6'), rgb('#DED8CB')
    tq_l, tq_r = rgb('#36BFC2'), rgb('#2BA2A6')

    def wall(base, tq):
        def f(u, v):
            if 7 <= v <= 10:
                return tq
            if v == 11:
                return mul(tq, 0.8)
            if v < 7:
                return mix(base, rgb('#FFFFFF'), 0.3)
            return base
        return f

    def deck(A, B):
        plank = B // 12
        shade = (rgb('#BE8854'), rgb('#AE7849'), rgb('#C8935E'))[plank % 3]
        if B % 12 in (0, 1):
            return rgb('#704828')
        if (A + plank * 26) % 64 in (0, 1):
            return rgb('#80522E')
        if (A * 3 + B) % 37 == 0:
            return mul(shade, 0.9)
        return shade

    room(S, wall(cream_l, tq_l), wall(cream_r, tq_r), deck)
    on_wall(S, window_sea(), 'l', 9, 46)
    on_wall(S, lifebuoy(), 'r', 70, 38)
    potted_palm(S, 16, 96)
    top = place(S, chars.guilherme(), CX + 2)
    nametag(S, 'Guilherme', CX + 2, top - 1)
    return finish(S, os.path.join(OUT, '01-guilherme.png'))


def scene_gabriel():
    S = Sprite(W, H)
    stars(S, 22, rgb('#0B0A1E'))

    def wall(base):
        def f(u, v):
            k = ((u // 4) + (v // 4)) % 2
            c = mul(base, 1.1) if k else mul(base, 0.92)
            if v < 4:
                c = mul(base, 0.75)
            return c
        return f

    def tiles(A, B):
        if A % 32 in (0, 1) or B % 32 in (0, 1):
            return rgb('#262D30')
        k = (A // 32 + B // 32) % 2
        return rgb('#3E494C') if k else rgb('#353F42')

    room(S, wall(rgb('#45306E')), wall(rgb('#36265A')), tiles)
    neon_on_air(S, 10, 46)
    on_wall(S, gold_record(), 'r', 66, 44)
    # brilho roxo da luz no chão
    for (x, y), c in list(S.px.items()):
        if y >= floor_edge(x):
            d = ((x - CX) / 34) ** 2 + ((y - 104) / 15) ** 2
            if d < 1:
                S.px[(x, y)] = mix(c, rgb('#8A4FD8'), 0.28 * (1 - d))
    turntable(S, 17, 98)
    speaker(S, 80, 90)
    top = place(S, chars.gabriel(), CX - 1)
    nametag(S, 'Gabriel', CX - 1, top - 1)
    return finish(S, os.path.join(OUT, '02-gabriel.png'))


def scene_flora():
    S = Sprite(W, H)
    stars(S, 33, rgb('#0D0F24'))

    def wall(base, wood):
        def f(u, v):
            if v < 15:
                if u % 8 == 0:
                    return mul(wood, 0.82)
                return wood if v != 14 else mix(wood, rgb('#FFFFFF'), 0.25)
            if v == 15:
                return mul(wood, 0.7)
            return base if (u // 2 + v // 2) % 7 else mul(base, 0.96)
        return f

    def blanket(A, B):
        base, dark, light = rgb('#CC322D'), rgb('#9B201D'), rgb('#E45246')
        if A % 32 in (0, 1) or B % 32 in (0, 1):
            return dark
        if A % 32 in (2, 3) or B % 32 in (2, 3):
            return light
        return base if (A + B) % 4 else mul(base, 0.95)

    room(S, wall(rgb('#F5E9D6'), rgb('#C9A57E')), wall(rgb('#E4D5BE'), rgb('#B68F69')), blanket)
    on_wall(S, framed(bone_sprite(), 19, 13, rgb('#7A5232'), rgb('#9ED2EE')), 'l', 12, 42)
    on_wall(S, framed(heart(rgb('#E2453C')), 15, 14, rgb('#7A5232'), rgb('#FBF3E6')), 'r', 68, 41)
    bowl(S, 17, 100, rgb('#D83A33'), rgb('#6E3A1E'))
    ball(S, 76, 112)
    top = place(S, chars.flora(), CX + 1, sh=(18, 5))
    nametag(S, 'Flora', CX + 3, top - 1)
    return finish(S, os.path.join(OUT, '03-flora.png'))


def scene_lupin():
    S = Sprite(W, H)
    stars(S, 44, rgb('#0B1126'))

    def wall(base):
        def f(u, v):
            if u % 10 in (0,):
                return mul(base, 0.88)
            return base if v > 3 else mul(base, 0.85)
        return f

    def plaid(A, B):
        navy, mid, light, line = rgb('#1E2C5C'), rgb('#2F4383'), rgb('#4462AE'), rgb('#DCE3F2')
        a, b = A % 48, B % 48
        ca = 2 if a < 12 else (1 if a < 18 else 0)
        cb = 2 if b < 12 else (1 if b < 18 else 0)
        c = [navy, mid, light][max(ca, cb)] if ca != cb else [navy, mid, light][min(2, ca + 1) if ca else 0]
        if a in (30, 31) or b in (30, 31):
            c = line if (A + B) % 4 < 2 else mix(line, c, 0.5)
        return c

    room(S, wall(rgb('#D3E7F5')), wall(rgb('#BCD3E7')), plaid)
    on_wall(S, framed(paw_print(rgb('#2A2A33')), 17, 14, rgb('#7A5232'), rgb('#F6E9C9')), 'l', 14, 42)
    on_wall(S, framed(bone_sprite(rgb('#F3EEE2')), 19, 13, rgb('#2F4383'), rgb('#F3C64E')), 'r', 63, 40)
    dog_bed(S, CX + 1, FEET_Y + 1)
    floor_bone(S, 18, 104)
    top = place(S, chars.lupin(), CX + 1, FEET_Y - 1, sh=(11, 3))
    nametag(S, 'Lupin', CX + 3, top - 1)
    return finish(S, os.path.join(OUT, '04-lupin.png'))


def scene_saldanha():
    S = Sprite(W, H)
    stars(S, 55, rgb('#0B1126'))

    def wall(base):
        def f(u, v):
            return base if (u * 3 + v * 7) % 23 else mul(base, 0.97)
        return f

    def stone(A, B):
        # piso de porcelanato e o tapete cinza debaixo dele
        if 50 <= A <= 140 and 50 <= B <= 140:
            if A in (50, 51, 139, 140) or B in (50, 51, 139, 140):
                return rgb('#7E7F80')
            return rgb('#9C9D9B') if (A * 13 + B * 7) % 29 == 0 else rgb('#A9AAA8')
        if A % 64 in (0, 1) or B % 64 in (0, 1):
            return rgb('#A39E95')
        return rgb('#C9C4BB') if (A // 64 + B // 64) % 2 else rgb('#C1BCB3')

    room(S, wall(rgb('#F2F0EA')), wall(rgb('#8D9C7D')), stone)
    on_wall(S, window_city(), 'l', 8, 46)
    on_wall(S, chart_frame(), 'r', 60, 43)
    big_leaf_plant(S, 15, 98)
    desk(S, 66, 92)
    top = place(S, chars.saldanha(), CX - 1)
    nametag(S, 'Saldanha', CX - 1, top - 1)
    return finish(S, os.path.join(OUT, '05-saldanha.png'))


def scene_caio():
    S = Sprite(W, H)
    stars(S, 66, rgb('#0B1126'))

    def white(u, v):
        return rgb('#F3F3F1') if v > 3 else rgb('#E2E2E0')

    def slats(u, v):
        if u % 3 == 0:
            return rgb('#9C7646')
        return rgb('#D7B585') if (u // 3) % 2 else rgb('#CBA877')

    def tiles(A, B):
        if A % 32 in (0, 1) or B % 32 in (0, 1):
            return rgb('#A7A9AB')
        k = (A // 32 * 3 + B // 32) % 4
        return (rgb('#CACCCD'), rgb('#C2C4C5'), rgb('#C6C8C9'), rgb('#BEC0C1'))[k]

    room(S, white, slats, tiles)
    on_wall(S, check_badge(), 'l', 16, 44)
    ficus(S, 15, 100)
    counter(S, 66, 100)
    top = place(S, chars.caio(), CX - 2)
    nametag(S, 'Caio', CX - 1, top - 1)
    return finish(S, os.path.join(OUT, '06-caio.png'))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    ims = [scene_guilherme(), scene_gabriel(), scene_flora(), scene_lupin(),
           scene_saldanha(), scene_caio()]
    # prancha com os seis em grade 3x2
    from PIL import Image
    from px import up
    gap, cols = 4, 3
    rows_ = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGBA', (W * cols + gap * (cols + 1), H * rows_ + gap * (rows_ + 1)),
                      (11, 17, 38, 255))
    for i, im in enumerate(ims):
        sheet.alpha_composite(im, (gap + (i % cols) * (W + gap), gap + (i // cols) * (H + gap)))
    up(sheet, 6).save(os.path.join(OUT, '00-todos.png'))
    print('ok')
