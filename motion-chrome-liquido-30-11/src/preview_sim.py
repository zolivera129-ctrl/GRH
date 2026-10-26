"""Folha de contato rápida da simulação (sem render): espessura e relevo."""
import os
import sys
import numpy as np
import cv2

import config as C
import roteiro as R

h = np.load(os.path.join(C.BUILD, "sim_h.npy"), mmap_mode="r")
bed = np.load(os.path.join(C.BUILD, "bed_sim.npz"))
step = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
tiles = []
t = 0.0
while t < C.DUR - 1e-6:
    f = min(int(round(t * C.FPS)), len(h) - 1)
    hh = np.asarray(h[f], np.float32)
    w = R.bed_mix(f / C.FPS)
    b = bed["b1"] * (1 - w) + bed["b2"] * w
    z = (hh + b).astype(np.float32)
    gx = cv2.Sobel(z, cv2.CV_32F, 1, 0) * 0.5
    gy = cv2.Sobel(z, cv2.CV_32F, 0, 1) * 0.5
    shade = np.clip(0.55 - 0.35 * gx - 0.35 * gy, 0, 1)
    a = np.clip((hh - 0.04) / 0.08, 0, 1)
    img = np.zeros((C.NY, C.NX, 3), np.float32)
    img[..., 2] = 0.45
    img[..., 1] = 0.03
    txt = np.clip(b / 0.3, 0, 1)
    for c in range(3):
        img[..., c] = img[..., c] * (1 - txt) + txt * (0.75 * shade)
        img[..., c] = img[..., c] * (1 - a) + a * (shade * (0.7 + 0.12 * np.clip(hh, 0, 3)))
    img = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    cv2.putText(img, f"{t:.1f}s", (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    tiles.append(img)
    t += step
cols = 8
while len(tiles) % cols:
    tiles.append(np.zeros_like(tiles[0]))
rows = [np.concatenate(tiles[i:i + cols], 1) for i in range(0, len(tiles), cols)]
out = os.path.join(C.BUILD, "sim_sheet.png")
cv2.imwrite(out, np.concatenate(rows, 0))
print(out)
