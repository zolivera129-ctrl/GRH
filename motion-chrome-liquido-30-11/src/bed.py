"""Relevo das letras: tipografia em mapa de altura (chanfro arredondado).

Gera dois relevos, o do começo (30/11, divisória, 23h) e o do fim
(ENCERRA AMANHÃ, divisória, A VENDA DE INGRESSOS), na resolução do render
e na grade da simulação.
"""
import os
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

import config as C

SS = 2  # supersample do desenho das letras
FEAT = ["lnum"]  # algarismos alinhados, como no KV


def font(weight, size):
    return ImageFont.truetype(os.path.join(C.FONTS, f"PlayfairDisplay-{weight}.ttf"), size)


def text_mask(lines, w, h, s):
    """lines: (texto, peso, largura alvo em px base, centro y em px base, achatamento x)."""
    m = Image.new("L", (w * SS, h * SS), 0)
    for txt, weight, width, cy, sx in lines:
        probe = font(weight, 200)
        x0, y0, x1, y1 = probe.getbbox(txt, features=FEAT)
        size = int(200 * width * s * SS / ((x1 - x0) * sx))
        f = font(weight, size)
        x0, y0, x1, y1 = f.getbbox(txt, features=FEAT)
        tw, th = x1 - x0, y1 - y0
        layer = Image.new("L", (tw + 8, th + 8), 0)
        ImageDraw.Draw(layer).text((4 - x0, 4 - y0), txt, font=f, fill=255, features=FEAT)
        layer = layer.resize((max(1, int((tw + 8) * sx)), th + 8), Image.LANCZOS)
        px = int(w * SS / 2 - layer.width / 2)
        py = int(cy * s * SS - layer.height / 2)
        m.paste(255, (px, py), layer)
    return np.asarray(m, np.float32) / 255.0


def divider_mask(w, h, s, cy, half, gap=34, star=26):
    """Filete fino com uma estrela de quatro pontas no centro."""
    m = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(m)
    k = s * SS
    cx, cyy = w * SS / 2, cy * k
    t = 2.2 * k
    for side in (-1, 1):
        a, b = cx + side * gap * k, cx + side * half * k
        xa, xb = sorted((a, b))
        # filete afinando para a ponta
        d.polygon([(xa, cyy - t), (xb, cyy - t), (xb, cyy + t), (xa, cyy + t)], fill=255)
    r, q = star * k, star * k * 0.22
    pts = []
    for i in range(8):
        ang = np.pi / 2 * (i // 2) + (np.pi / 4 if i % 2 else 0)
        rad = r if i % 2 == 0 else q
        pts.append((cx + rad * np.cos(ang - np.pi / 2), cyy + rad * np.sin(ang - np.pi / 2)))
    d.polygon(pts, fill=255)
    arr = np.asarray(m, np.float32) / 255.0
    # afina as pontas do filete
    xs = (np.arange(w * SS) - cx) / k
    taper = np.clip((half - np.abs(xs)) / 120.0, 0, 1) ** 0.6
    band = np.abs(np.arange(h * SS)[:, None] - cyy) < 3 * k
    arr = np.where(band, arr * np.maximum(taper[None, :], (np.abs(xs) < gap)[None, :]), arr)
    return arr


def height_from_mask(mask, s, bevel=13.0, dome=0.30, low=1.0):
    """Altura com chanfro de quarto de círculo e leve abaulado no topo."""
    hard = (mask > 0.5).astype(np.uint8)
    dist = cv2.distanceTransform(hard, cv2.DIST_L2, 5) / (s * SS)  # px base
    dist = dist + (mask - 0.5) * (1.0 / s / SS)  # sub-pixel pelo antialias
    u = np.clip(dist / bevel, 0, 1)
    prof = np.sqrt(np.clip(1 - (1 - u) ** 2, 0, 1))
    # almofada: a face sobe devagar até o meio do traço e pega as luzes do estúdio
    pil = np.clip(dist / (bevel * 3.5), 0, 1)
    prof = prof * (1 - dome) + dome * pil * (2 - pil)
    hgt = C.TEXT_H * low * prof * (mask > 0.02)
    hgt = cv2.resize(hgt, (mask.shape[1] // SS, mask.shape[0] // SS), interpolation=cv2.INTER_AREA)
    return hgt


def build_bed(s):
    w, h = C.BW * s, C.BH * s
    start_txt = [
        ("30/11", 600, 745, 790, 1.0),
        ("23h", 600, 500, 1235, 1.0),
    ]
    end_txt = [
        ("ENCERRA", 600, 790, 610, 0.82),
        ("AMANHÃ", 600, 810, 820, 0.82),
        ("A VENDA DE", 600, 560, 1170, 0.84),
        ("INGRESSOS", 600, 540, 1300, 0.84),
    ]
    b1 = height_from_mask(text_mask(start_txt, w, h, s), s)
    b1 = np.maximum(b1, height_from_mask(divider_mask(w, h, s, 1012, 270), s, bevel=4, low=0.55))
    b2 = height_from_mask(text_mask(end_txt, w, h, s), s, bevel=11)
    b2 = np.maximum(b2, height_from_mask(divider_mask(w, h, s, 1010, 250), s, bevel=4, low=0.55))
    return b1.astype(np.float32), b2.astype(np.float32)


def to_sim(b):
    return cv2.resize(b, (C.NX, C.NY), interpolation=cv2.INTER_AREA).astype(np.float64)


if __name__ == "__main__":
    os.makedirs(C.BUILD, exist_ok=True)
    b1, b2 = build_bed(C.SCALE)
    np.savez_compressed(C.bed_path(), b1=b1, b2=b2)
    if not os.path.exists(os.path.join(C.BUILD, "bed_sim.npz")) or C.SCALE == 1:
        bb1, bb2 = build_bed(1)
        np.savez_compressed(os.path.join(C.BUILD, "bed_sim.npz"), b1=to_sim(bb1), b2=to_sim(bb2))
    prev = np.concatenate([b1, b2], 1) / C.TEXT_H
    cv2.imwrite(os.path.join(C.BUILD, "bed_preview.png"),
                cv2.resize((prev * 255).astype(np.uint8), (prev.shape[1] // (2 * C.SCALE), prev.shape[0] // (2 * C.SCALE))))
    print("ok", b1.shape)
