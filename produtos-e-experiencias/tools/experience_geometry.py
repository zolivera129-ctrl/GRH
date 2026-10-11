"""Geometria do bloco GRH Experience (viewBox 0 0 120 120, centro 60,60).

Gera os paths usados em index.html e em experience-card.js:
- o símbolo original: 4 lados côncavos em cúbicas, com as pontas arredondadas
  pelo traço (stroke-linejoin round). As medidas vêm do ajuste ao arquivo
  original (erro máximo de 0,2 px), na escala em que a ponta fica a 42
  unidades do centro;
- as janelas do volante: aro, travessa e janelas de baixo com as proporções da
  referência, cantos arredondados (raio RH) e a estrela do Experience no cubo.

Uso: python3 tools/experience_geometry.py
"""
import math

CX = CY = 60.0

# Símbolo original: ponta do caminho a A do centro, alças U e V, raio das pontas RHO.
A, U, V, RHO = 38.575, 13.439, 8.049, 3.412

# Volante (proporções da referência, em frações do raio R).
R = 46.0                                  # raio visível do volante
RI = 0.789 * R                            # raio interno do aro
XB_C, XB_R = 1.349 * R, 1.646 * R         # arco de cima da travessa (centro abaixo do cubo)
LO_X, LO_Y, LO_R = 0.551 * R, 0.569 * R, 0.419 * R   # janelas de baixo
RH = 2.4                                  # raio dos cantos das janelas
HUB = 9.4                                 # ponta da estrela do cubo


def num(x):
    s = f'{x:.2f}'.rstrip('0').rstrip('.')
    return '0' if s in ('', '-0') else s


def star_path(a=A, u=U, v=V):
    w = a - u
    pts = [(0, -a), (v, -w), (w, -v), (a, 0), (w, v), (v, w), (0, a),
           (-v, w), (-w, v), (-a, 0), (-w, -v), (-v, -w), (0, -a)]
    p = [(CX + x, CY + y) for x, y in pts]
    d = f'M{num(p[0][0])} {num(p[0][1])}'
    for i in range(1, 13, 3):
        d += 'C' + ' '.join(f'{num(x)} {num(y)}' for x, y in p[i:i + 3])
    return d + 'Z'


def circle_intersections(c1, r1, c2, r2):
    (x1, y1), (x2, y2) = c1, c2
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy)
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(r1 * r1 - a * a, 0.0))
    xm, ym = x1 + a * dx / d, y1 + a * dy / d
    return (xm + h * dy / d, ym - h * dx / d), (xm - h * dy / d, ym + h * dx / d)


def arc_flags(c, p0, p1, through):
    """Flags large-arc e sweep do arco de p0 a p1 (círculo de centro c) que passa por 'through'."""
    ang = lambda p: math.atan2(p[1] - c[1], p[0] - c[0])
    span = lambda a, b: (b - a) % (2 * math.pi)
    a0, a1, at = ang(p0), ang(p1), ang(through)
    pos = span(a0, a1)
    if span(a0, at) < pos:
        return int(pos > math.pi), 1
    return int(2 * math.pi - pos > math.pi), 0


def pt(p):
    return f'{num(CX + p[0])} {num(CY + p[1])}'


def top_window():
    # Desenhada recuada RH e com traço 2*RH em stroke-linejoin round: os cantos ficam com raio RH.
    r1, c2, r2 = RI - RH, (0.0, XB_C), XB_R + RH
    a, b = circle_intersections((0.0, 0.0), r1, c2, r2)
    left, right = (a, b) if a[0] < b[0] else (b, a)
    la1, sw1 = arc_flags((0, 0), left, right, (0, -r1))
    la2, sw2 = arc_flags(c2, right, left, (0, XB_C - r2))
    return (f'M{pt(left)}A{num(r1)} {num(r1)} 0 {la1} {sw1} {pt(right)}'
            f'A{num(r2)} {num(r2)} 0 {la2} {sw2} {pt(left)}Z')


def low_window(side):
    r1, c3, r3 = RI - RH, (side * LO_X, LO_Y), LO_R - RH
    a, b = circle_intersections((0.0, 0.0), r1, c3, r3)
    n = math.hypot(*c3)
    far = (c3[0] / n * r1, c3[1] / n * r1)
    near = (c3[0] - c3[0] / n * r3, c3[1] - c3[1] / n * r3)
    la1, sw1 = arc_flags((0, 0), a, b, far)
    la2, sw2 = arc_flags(c3, b, a, near)
    return (f'M{pt(a)}A{num(r1)} {num(r1)} 0 {la1} {sw1} {pt(b)}'
            f'A{num(r3)} {num(r3)} 0 {la2} {sw2} {pt(a)}Z')


if __name__ == '__main__':
    k = HUB / (A + RHO)
    print('Símbolo (stroke-width %s):' % num(2 * RHO))
    print(' ', star_path())
    print('Janelas do volante (stroke-width %s):' % num(2 * RH))
    print(' ', top_window())
    print(' ', low_window(-1))
    print(' ', low_window(1))
    print('Estrela do cubo (stroke-width %s):' % num(2 * RHO * k))
    print(' ', star_path(A * k, U * k, V * k))
