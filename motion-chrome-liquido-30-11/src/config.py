"""Parâmetros do filme: formato, tempo, grade da simulação e layout."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
FONTS = os.path.join(ROOT, "fonts")

FPS = 24
DUR = 20.0
NFRAMES = int(FPS * DUR)

# Base de layout: 1080x1920. O render final escala tudo por SCALE.
BW, BH = 1080, 1920
SCALE = int(os.environ.get("SCALE", "2"))  # 2 = 2160x3840 (4K vertical)
W, H = BW * SCALE, BH * SCALE

# Grade da simulação: 1 célula = 4 px na base 1080.
CELL = 4
NX, NY = BW // CELL, BH // CELL

# Alturas (unidades da simulação) e como viram pixels na superfície.
TEXT_H = 2.8        # altura do relevo das letras
# superfície em px (base): z = ZA (1 - exp(-eta/Z0)) + ZB eta
ZA, Z0, ZB = 14.0, 1.0, 3.0
EPS = 0.004         # filme precursor (invisível)


def sim_path():
    return os.path.join(BUILD, "sim.npz")


def bed_path():
    return os.path.join(BUILD, f"bed_{SCALE}x.npz")
