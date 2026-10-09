"""Recorta do layout original as imagens usadas no e-mail.

As imagens saem em PNG transparente: a cor de cada traço é fixa (verde-água
ou branco) e a transparência vem da mistura com o azul do fundo. Assim o
recorte não deixa "caixa" de outro tom de azul em volta e continua certo
mesmo que algum leitor escureça o fundo no modo escuro.

Uso: python3 src/build_images.py   (dentro de email-randoncorp-inovacao-em-movimento/)
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "input" / "layout-original.webp"
OUT = ROOT / "img"

BLUE = np.array([5, 58, 181], dtype=float)    # fundo #053AB5
TEAL = np.array([16, 178, 166], dtype=float)  # verde-água #10B2A6
WHITE = np.array([255, 255, 255], dtype=float)


def alpha_toward(px, color, floor=0.06):
    """Quanto de `color` existe em cada pixel misturado com o azul do fundo."""
    axis = color - BLUE
    a = ((px - BLUE) @ axis) / (axis @ axis)
    a = np.clip(a, 0.0, 1.0)
    a[a < floor] = 0.0
    return a


def round_cap(alpha, center, direction, radius, window=25):
    """Termina uma linha com ponta redonda em `center`.

    `direction` aponta da ponta para dentro da linha; o que fica atrás da
    ponta (fora do círculo de raio `radius`) é apagado.
    """
    cx, cy = center
    ux, uy = np.array(direction, dtype=float) / np.hypot(*direction)
    h, w = alpha.shape
    y0, y1 = max(0, cy - window), min(h, cy + window)
    x0, x1 = max(0, cx - window), min(w, cx + window)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    behind = (xx - cx) * ux + (yy - cy) * uy < 0
    keep = np.clip(radius + 0.5 - np.hypot(xx - cx, yy - cy), 0.0, 1.0)
    alpha[y0:y1, x0:x1] = np.where(behind, alpha[y0:y1, x0:x1] * keep, alpha[y0:y1, x0:x1])


def save_rgba(color, alpha, name):
    h, w = alpha.shape
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[..., :3] = color.astype(np.uint8)
    rgba[..., 3] = np.round(alpha * 255).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(OUT / name, optimize=True)
    print(f"{name}: {w}x{h}")


def main():
    OUT.mkdir(exist_ok=True)
    im = np.asarray(Image.open(SRC).convert("RGB")).astype(float)

    # Linhas de estrada da direita (coluna de 144 px no e-mail; o texto
    # ao lado ocupa 392 px, a mesma medida do layout).
    x0, x1, y0, y1 = 698, 919, 410, 1470
    crop = im[y0:y1, x0:x1]
    a = alpha_toward(crop, TEAL)
    # A ponta de algumas linhas de texto entra nesta faixa: apaga o branco.
    # Branco misturado ao azul sobe o vermelho junto com o verde; o verde-água
    # quase não tem vermelho, nem nas bordas comprimidas do webp.
    r, g = crop[..., 0] - BLUE[0], crop[..., 1] - BLUE[1]
    text = (r > 40) & (r > 0.5 * g)
    text[:, 715 - x0:] = False
    # Engorda a máscara 2 px para levar junto o antisserrilhado das letras.
    text = Image.fromarray(text.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(5))
    text = np.asarray(text) > 0
    a[text] = 0.0
    # As duas pontas em "V" das linhas ficam um pouco antes do corte da
    # coluna; em vez de um corte reto, as linhas terminam com ponta redonda.
    round_cap(a, (12, 199), (0.69, 0.72), 5.5)
    round_cap(a, (8, 882), (0.64, -0.77), 5.5)
    save_rgba(TEAL, a, "deco-estrada-direita.png")

    # Seta do rodapé, em duas fatias (linha do botão e linha do logo).
    # A fatia de cima termina em x=156, onde começa o botão.
    for name, (x0, x1, y0, y1) in {
        "deco-seta-topo.png": (0, 156, 1690, 1800),
        "deco-seta-base.png": (0, 175, 1800, 2000),
    }.items():
        crop = im[y0:y1, x0:x1]
        save_rgba(TEAL, alpha_toward(crop, TEAL), name)

    # Logo Randoncorp (branco).
    crop = im[1870:1919, 238:683]
    save_rgba(WHITE, alpha_toward(crop, WHITE, floor=0.04), "logo-randoncorp.png")


if __name__ == "__main__":
    main()
