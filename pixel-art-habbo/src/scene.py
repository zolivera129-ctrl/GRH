"""Cenários: um canto de quarto do Habbo para cada personagem.

Piso em losangos 2:1 (64x32, a medida do Habbo), duas paredes que se
encontram no meio, fundo estrelado como o quarto da referência, mobis
temáticos e a etiqueta de nome preta em cima da cabeça.
"""
import random
from PIL import Image
from px import Layer, Sprite, rgb, mul, mix, up

W, H = 96, 120
CX, YC, WH = 48, 60, 52          # canto do piso, altura da parede
SCALE = 10


# ------------------------------------------------------------- fonte pixel
FONT = {  # fonte pequena no espírito da Volter do Habbo
    'G': [".##.", "#..#", "#...", "#.##", "#..#", ".###"],
    'F': ["####", "#...", "###.", "#...", "#...", "#..."],
    'S': [".###", "#...", ".##.", "...#", "...#", "###."],
    'C': [".###", "#...", "#...", "#...", "#...", ".###"],
    'd': ["...#", "...#", ".###", "#..#", "#..#", ".###"],
    'V': ["#...#", "#...#", "#...#", ".#.#.", ".#.#.", "..#.."],
    'N': ["#..#", "##.#", "#.##", "#..#", "#..#", "#..#"],
    'O': [".##.", "#..#", "#..#", "#..#", "#..#", ".##."],
    'v': [".....", ".....", "#...#", "#...#", ".#.#.", "..#.."],
    't': [".#.", ".#.", "###", ".#.", ".#.", "..#"],
    'P': ["###.", "#..#", "#..#", "###.", "#...", "#..."],
    'J': ["..##", "...#", "...#", "...#", "#..#", ".##."],
    'M': ["#...#", "##.##", "#.#.#", "#...#", "#...#", "#...#"],
    'D': ["###.", "#..#", "#..#", "#..#", "#..#", "###."],
    'Í': ["..#", "###", ".#.", ".#.", ".#.", ".#.", "###"],
    's': ["....", "....", ".###", "##..", "..##", "###."],
    '.': [".", ".", ".", ".", ".", "#"],
    ' ': ["..", "..", "..", "..", "..", ".."],
    'L': ["#...", "#...", "#...", "#...", "#...", "####"],
    'a': ["....", "....", ".###", "#..#", "#..#", ".###"],
    'b': ["#...", "#...", "###.", "#..#", "#..#", "###."],
    'e': ["....", "....", ".##.", "####", "#...", ".###"],
    'h': ["#...", "#...", "###.", "#..#", "#..#", "#..#"],
    'i': ["#", ".", "#", "#", "#", "#"],
    'l': ["#", "#", "#", "#", "#", "#"],
    'm': [".....", ".....", "####.", "#.#.#", "#.#.#", "#.#.#"],
    'n': ["....", "....", "###.", "#..#", "#..#", "#..#"],
    'o': ["....", "....", ".##.", "#..#", "#..#", ".##."],
    'p': ["....", "....", "###.", "#..#", "#..#", "###.", "#...", "#..."],
    'r': ["...", "...", "#.#", "##.", "#..", "#.."],
    'u': ["....", "....", "#..#", "#..#", "#..#", ".###"],
}

MINI = {  # 3x5 para letreiros
    'O': ["###", "#.#", "#.#", "#.#", "###"],
    'N': ["#..#", "##.#", "#.##", "#..#", "#..#"],
    'A': [".#.", "#.#", "###", "#.#", "#.#"],
    'I': ["###", ".#.", ".#.", ".#.", "###"],
    'R': ["##.", "#.#", "##.", "#.#", "#.#"],
    'U': ["#.#", "#.#", "#.#", "#.#", "###"],
    'G': ["###", "#..", "#.#", "#.#", "###"],
    'E': ["###", "#..", "##.", "#..", "###"],
    'T': ["###", ".#.", ".#.", ".#.", ".#."],
    'D': ["##.", "#.#", "#.#", "#.#", "##."],
    ' ': ["..", "..", "..", "..", ".."],
}


def text_width(s, font=FONT, gap=1):
    return sum(len(font[ch][0]) for ch in s) + gap * (len(s) - 1)


ACCENT_UP = {'Í'}


def draw_text(S, s, x, y, c, font=FONT, gap=1):
    for ch in s:
        g = font[ch]
        dy = -1 if ch in ACCENT_UP else 0
        for j, row in enumerate(g):
            for i, v in enumerate(row):
                if v == '#':
                    S.set(x + i, y + j + dy, c)
        x += len(g[0]) + gap


# -------------------------------------------------------------- geometria
def floor_edge(x):
    return YC + abs(x - CX) // 2


def iso_ab(x, y):
    """Coordenadas do piso: A cresce para a direita-baixo, B para a esquerda-baixo.
    Um losango de 64x32 tem 64 unidades em cada eixo."""
    dx, dy = x - CX, y - YC
    return dx + 2 * dy, 2 * dy - dx


def stars(S, seed, top_color):
    rnd = random.Random(seed)
    for y in range(H):
        for x in range(W):
            if y < floor_edge(x) - WH - 1:
                S.set(x, y, top_color)
    for _ in range(46):
        x, y = rnd.randrange(W), rnd.randrange(40)
        if y < floor_edge(x) - WH - 2:
            S.set(x, y, rnd.choice([rgb('#FFFFFF'), rgb('#9FC4FF'), rgb('#5A6C9E'), rgb('#5A6C9E')]))
    for _ in range(3):
        x, y = rnd.randrange(4, W - 4), rnd.randrange(3, 22)
        if y < floor_edge(x) - WH - 4:
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                S.set(x + dx, y + dy, rgb('#FFFFFF') if (dx, dy) == (0, 0) else rgb('#8FB0F0'))


def room(S, wall_l, wall_r, floor):
    """wall_l/wall_r(u, v) -> cor; floor(A, B) -> cor."""
    for y in range(H):
        for x in range(W):
            e = floor_edge(x)
            if y >= e:
                A, B = iso_ab(x, y)
                c = floor(A, B)
                # sombrinha onde o piso encosta na parede
                if y - e < 2:
                    c = mul(c, 0.82 if y - e == 0 else 0.92)
                S.set(x, y, c)
            elif y >= e - WH:
                u, v = abs(x - CX), e - y
                c = wall_l(u, v) if x < CX else wall_r(u, v)
                if y == e - WH:
                    c = mix(c, rgb('#FFFFFF'), 0.45)
                elif y == e - WH + 1:
                    c = mul(c, 1.06)
                if x == CX:
                    c = mul(c, 0.8)
                S.set(x, y, c)


def on_wall(S, im, side, x0, vtop):
    """Cola uma imagem plana na parede, inclinada 2:1 como no Habbo."""
    for i in range(im.width):
        x = x0 + i
        e = floor_edge(x)
        for j in range(im.height):
            p = im.getpixel((i, j))
            if p[3]:
                S.set(x, e - vtop + j, p[:3])


def paste(S, im, x, y):
    for j in range(im.height):
        for i in range(im.width):
            p = im.getpixel((i, j))
            if p[3]:
                S.set(x + i, y + j, p[:3])


def shadow(S, cx, cy, rx, ry, k=0.72):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 and (x, y) in S.px:
                S.px[(x, y)] = mul(S.px[(x, y)], k)


def nametag(S, name, cx, bottom):
    tw = text_width(name)
    desc = any(ch in 'p' for ch in name)
    h = 10 if not desc else 12
    w = tw + 6
    x0, y0 = cx - w // 2, bottom - h - 3
    bg, edge = rgb('#141414'), rgb('#3A3A3A')
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            corner = (x in (x0, x0 + w - 1)) and (y in (y0, y0 + h - 1))
            if not corner:
                S.set(x, y, bg)
    for x in range(x0 + 1, x0 + w - 1):
        S.set(x, y0, edge)
    # setinha
    for i, half in enumerate((2, 1, 0)):
        for x in range(cx - half, cx + half + 1):
            S.set(x, y0 + h + i, bg)
    draw_text(S, name, x0 + 3, y0 + 2, rgb('#FFFFFF'))


def finish(S, path):
    im = S.image()
    up(im, SCALE).save(path)
    return im


# ---------------------------------------------------------------- mobis
def flat(w, h):
    return Sprite(w, h)


def box(L, x0, y0, w, h, c):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            L.set(x, y, c)


def iso_block(S, x, y, h, height, top, left, right, line=None):
    """Bloco isométrico. (x, y) é o vértice de baixo do losango da base,
    que tem 4h de largura e 2h de altura."""
    line = line or mul(right, 0.55)
    for i in range(-2 * h, 2 * h + 1):
        yb = y - abs(i) // 2
        c = left if i < 0 else right
        for k in range(height + 1):
            S.set(x + i, yb - k, c)
        S.set(x + i, yb, line)
    cy = y - h - height
    for yy in range(cy - h, cy + h + 1):
        for i in range(-2 * h, 2 * h + 1):
            if abs(i) / 2 + abs(yy - cy) <= h:
                S.set(x + i, yy, top)
    for i in range(-2 * h, 2 * h + 1):
        S.set(x + i, cy + h - abs(i) // 2, mix(top, rgb('#FFFFFF'), 0.3))
        S.set(x + i, cy - h + abs(i) // 2, line)
    for k in range(height + 1):
        S.set(x - 2 * h, y - h - k, line)
        S.set(x + 2 * h, y - h - k, line)
        S.set(x, y - k, mul(right, 0.85))
    return cy


def iso_box(S, x, y, a, b, height, top, left, right, line=None):
    """Caixa isométrica com base a x b (a ao longo da parede da direita,
    b ao longo da parede da esquerda). (x, y) é o canto da frente, no chão.
    Devolve uma função que, para um pixel da tampa, dá (s, t): a posição
    nela em unidades de 0..a e 0..b (fora da tampa devolve None)."""
    line = line or mul(right, 0.55)
    for xi in range(x - 2 * b, x + 2 * a + 1):
        if xi <= x:
            yb = y - (x - xi) // 2
            c = left
        else:
            yb = y - (xi - x) // 2
            c = right
        for k in range(height + 1):
            S.set(xi, yb - k, c)
        S.set(xi, yb, line)
    ty = y - height

    def on_top(xi, yi):
        dx, dy = xi - x, yi - ty
        s4, t4 = dx - 2 * dy, -dx - 2 * dy
        if 0 <= s4 <= 4 * a and 0 <= t4 <= 4 * b:
            return s4 / 4, t4 / 4
        return None
    for yi in range(ty - a - b - 1, ty + 1):
        for xi in range(x - 2 * b, x + 2 * a + 1):
            if on_top(xi, yi):
                S.set(xi, yi, top)
    hi = mix(top, rgb('#FFFFFF'), 0.35)
    for xi in range(x - 2 * b, x + 2 * a + 1):
        yy = ty - abs(xi - x) // 2
        S.set(xi, yy, hi)
    for k in range(height + 1):
        S.set(x - 2 * b, y - b - k, line)
        S.set(x + 2 * a, y - a - k, line)
        S.set(x, y - k, mix(left, right, 0.5))
    return on_top
