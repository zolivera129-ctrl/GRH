"""Roteiro físico: o que muda no mundo a cada instante.

Nada aqui desenha imagem. São as condições da simulação ao longo do tempo:
de onde o cromo entra, quanto pesa a gravidade no plano e na normal
(a inclinação do painel), quando o relevo de baixo é trocado e o campo
que abre a janela final.
"""
import numpy as np

import config as C


def ss(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# Bicas de entrada no topo: (x em células, largura, início, altura, pulso Hz, fase)
SPOUTS = [
    (9, 15, 2.00, 1.75, 0.7, 0.0),
    (47, 8, 2.55, 1.05, 1.1, 1.3),
    (80, 11, 2.20, 1.30, 0.9, 2.1),
    (118, 7, 2.85, 0.95, 1.3, 0.4),
    (146, 11, 2.35, 1.35, 0.8, 3.0),
    (181, 8, 2.70, 1.05, 1.0, 1.7),
    (212, 11, 2.15, 1.30, 1.2, 0.9),
    (240, 7, 2.80, 1.00, 0.75, 2.6),
    (262, 15, 2.05, 1.75, 0.85, 1.1),
]


def top_profile(t, rng_noise):
    """Espessura imposta na borda de cima (linha 0..1), por coluna."""
    x = np.arange(C.NX, dtype=np.float64)
    h = np.zeros(C.NX)
    for x0, w, t0, a, hz, ph in SPOUTS:
        if t < t0:
            continue
        grow = ss(t0, t0 + 0.6, t)
        drift = 3.0 * np.sin(0.5 * t + ph)
        puls = 0.82 + 0.18 * np.sin(2 * np.pi * hz * t + ph)
        wid = w * (0.55 + 0.45 * grow)
        h = np.maximum(h, a * grow * puls * np.exp(-((x - x0 - drift) / wid) ** 2))
    # lençol contínuo que engrossa na fase de acúmulo
    sheet = 1.1 * ss(8.0, 9.8, t) + 1.7 * ss(9.8, 11.6, t)
    if sheet > 0:
        wav = 0.85 + 0.15 * np.sin(x * 0.07 + 3.1 * t) * np.sin(x * 0.023 - 1.7 * t)
        h = np.maximum(h, sheet * wav)
    h = h * (1 + 0.06 * rng_noise)
    return h * (1 - ss(12.5, 12.9, t))  # a fonte de cima seca antes da janela abrir


def edge_level(t):
    """Nível imposto nas bordas laterais e de baixo (o cromo que entra pela moldura)."""
    return (1.4 * ss(8.6, 10.2, t) + 2.6 * ss(10.2, 12.0, t)) * (1 - ss(12.5, 12.9, t))


def gravity(t):
    """(G no plano, Gn na normal). O painel 'deita': escorre, depois nivela."""
    g = 110.0 * (1 - ss(8.5, 11.0, t)) + 8.0
    gn = 60.0 + 340.0 * ss(8.5, 11.5, t) - 240.0 * ss(12.85, 13.2, t)
    return g, gn


SIGMA = 2500.0
DT_MAX = 0.004
HC = 1.2


def bottom_open(t):
    """Até ~9 s o líquido escorre para fora por baixo; depois o fundo fecha e acumula."""
    return 1.0 - ss(8.8, 9.6, t)


def slip(t):
    return 2.0 * ss(12.9, 13.3, t)


def swell(t):
    """Engrossamento do lençol na fase de acúmulo (espessura por segundo onde já há cromo)."""
    return 1.25 * ss(9.4, 10.2, t) * (1 - ss(12.1, 12.4, t))


def bed_mix(t):
    """0 = 30/11 23h ; 1 = ENCERRA AMANHÃ (trocado só sob cobertura total)."""
    return ss(12.45, 12.85, t)


def window_shape(nx, ny, scale=1.0):
    """Forma irregular da janela final, em coordenadas de células (ou px * scale)."""
    yy, xx = np.mgrid[0:ny, 0:nx].astype(np.float64)
    cx, cy = nx * 0.5, ny * 0.49
    rx, ry = nx * 0.475, ny * 0.405
    dx, dy = (xx - cx) / rx, (yy - cy) / ry
    ang = np.arctan2(dy, dx)
    wob = (1 + 0.055 * np.sin(3 * ang + 0.7) + 0.04 * np.sin(5 * ang + 2.1)
           + 0.03 * np.sin(8 * ang + 4.0) + 0.02 * np.sin(11 * ang + 1.3))
    r = np.sqrt(dx * dx + dy * dy) / wob
    # superelipse suave: mais "quadrada" que um oval
    r = (np.abs(dx / wob) ** 2.6 + np.abs(dy / wob) ** 2.6) ** (1 / 2.6) * 0.5 + r * 0.5
    return r


def gate_open(t):
    """Na abertura, o empurrão leva o véu por cima das letras novas (sem ficar preso atrás delas)."""
    return float(ss(12.9, 13.1, t))


def retract(t):
    """Recolhimento do filme residual dentro da janela (o véu fino se retrai e some)."""
    return 4.0 * ss(13.0, 13.15, t) + 30.0 * ss(13.15, 13.35, t)


def phi_amp(t):
    return 60000.0 * ss(12.9, 13.35, t)
