"""Simulação do cromo líquido: equação de filme fino (lubrificação).

    dh/dt = -div q
    q = gate * M(h) [ -grad p + G y ]
    p = Gn (h + b) - sigma lap(h + b) + phi
    M(h) = h^3 / (1 + (h/hc)^2) + slip h

h é a espessura do líquido, b o relevo das letras (obstáculo físico).
G puxa o líquido para baixo no plano, Gn nivela (pressão hidrostática),
sigma é a tensão superficial (cabeças arredondadas nas gotas, lóbulos) e
phi é o campo que, no fim, afasta o líquido do centro e abre a janela.
'gate' é a barreira de subida: o líquido só entra numa célula de letra
quando a sua própria superfície já está acima daquela letra, então ele
contorna o relevo e só o engole depois de acumular altura.

Passo semi-implícito: os termos de difusão (tensão superficial e
nivelamento) são estabilizados por uma resolução em cossenos (DCT), o que
permite tensão superficial alta sem passo de tempo minúsculo.
"""
import os
import time
import numpy as np
from numba import njit, prange
from scipy import fft as sfft

import config as C
import roteiro as R


@njit(cache=True, inline="always")
def mob(h, hc, sl):
    return h * h * h / (1.0 + (h / hc) ** 2) + sl * h


@njit(cache=True, inline="always")
def gate(eta_from, b_to):
    x = (eta_from - b_to + 0.05) / 0.3
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    return x * x * (3.0 - 2.0 * x)


@njit(parallel=True, cache=True)
def rate(h, b, phi, G, Gn, sig, hc, sl, openb, gopen, out):
    """-div q (explícito). Devolve a maior velocidade e a maior mobilidade."""
    ny, nx = h.shape
    M = np.empty_like(h)
    eta = np.empty_like(h)
    p = np.empty_like(h)
    for j in prange(ny):
        for i in range(nx):
            M[j, i] = mob(h[j, i], hc, sl)
            eta[j, i] = h[j, i] + b[j, i]
    for j in prange(ny):
        jm = max(j - 1, 0)
        jp = min(j + 1, ny - 1)
        for i in range(nx):
            im = max(i - 1, 0)
            ip = min(i + 1, nx - 1)
            lh = h[j, im] + h[j, ip] + h[jm, i] + h[jp, i] - 4.0 * h[j, i]
            lb = b[j, im] + b[j, ip] + b[jm, i] + b[jp, i] - 4.0 * b[j, i]
            wb = h[j, i] / (h[j, i] + 0.25)  # o relevo só curva a superfície sob líquido
            p[j, i] = Gn * eta[j, i] - sig * (lh + wb * lb) + phi[j, i]
    qx = np.zeros((ny, nx + 1))
    qy = np.zeros((ny + 1, nx))
    vrow = np.zeros(ny)
    for j in prange(ny):
        vm = 0.0
        for i in range(1, nx):
            q = -0.5 * (M[j, i - 1] + M[j, i]) * (p[j, i] - p[j, i - 1])
            if q > 0:
                q *= max(gate(eta[j, i - 1], b[j, i]), gopen)
                v = q / max(h[j, i - 1], 0.05)
            else:
                q *= max(gate(eta[j, i], b[j, i - 1]), gopen)
                v = -q / max(h[j, i], 0.05)
            qx[j, i] = q
            if v > vm:
                vm = v
        vrow[j] = vm
    for j in prange(1, ny):
        vm = vrow[j]
        for i in range(nx):
            q = -0.5 * (M[j - 1, i] + M[j, i]) * (p[j, i] - p[j - 1, i]) + G * M[j - 1, i]
            if q > 0:
                q *= max(gate(eta[j - 1, i], b[j, i]), gopen)
                v = q / max(h[j - 1, i], 0.05)
            else:
                q *= max(gate(eta[j, i], b[j - 1, i]), gopen)
                v = -q / max(h[j, i], 0.05)
            qy[j, i] = q
            if v > vm:
                vm = v
        vrow[j] = vm
    for i in range(nx):
        qy[ny, i] = G * M[ny - 1, i] * openb  # borda de baixo aberta: escorre para fora do quadro
    mm = 0.0
    for j in range(ny):
        for i in range(nx):
            out[j, i] = -(qx[j, i + 1] - qx[j, i] + qy[j + 1, i] - qy[j, i])
            if M[j, i] > mm:
                mm = M[j, i]
    return vrow.max(), mm


class Solver:
    def __init__(self):
        kx = np.pi * np.arange(C.NX) / C.NX
        ky = np.pi * np.arange(C.NY) / C.NY
        lam = (2 * np.cos(kx)[None, :] - 2) + (2 * np.cos(ky)[:, None] - 2)  # <= 0
        self.lam = lam
        self.out = np.zeros((C.NY, C.NX))

    def step(self, h, b, phi, G, Gn, sig, sl, openb, gopen, dt_max):
        vmax, mmax = rate(h, b, phi, G, Gn, sig, R.HC, sl, openb, gopen, self.out)
        dt = min(dt_max, 0.35 / (vmax + 1e-6))
        a4 = 0.6 * sig * mmax
        a2 = 0.6 * Gn * mmax
        L = 1.0 + dt * (a4 * self.lam ** 2 - a2 * self.lam)
        dh = sfft.dctn(dt * self.out, type=2, norm="ortho", workers=4)
        dh = sfft.idctn(dh / L, type=2, norm="ortho", workers=4)
        # a estabilização não pode vazar líquido para cima de letra seca
        dry = (b > 0.15) & (h < 0.12) & (gopen < 0.5)
        dh[dry] = dt * self.out[dry]
        np.add(h, dh, out=h)
        np.maximum(h, C.EPS, out=h)
        return dt


def run(t_end=C.DUR, t_resume=None):
    os.makedirs(C.BUILD, exist_ok=True)
    bed = np.load(os.path.join(C.BUILD, "bed_sim.npz"))
    b1, b2 = bed["b1"], bed["b2"]
    rng = np.random.default_rng(7)
    h = np.full((C.NY, C.NX), C.EPS)
    rwin = R.window_shape(C.NX, C.NY)
    dome = np.clip(1 - rwin, 0, None)  # cone: empurrão constante para fora
    inside = np.clip((1.0 - rwin) / 0.08, 0, 1)
    frames = np.zeros((C.NFRAMES, C.NY, C.NX), np.float32)
    noise = rng.standard_normal(C.NX)
    solver = Solver()
    nf = min(C.NFRAMES, int(round(t_end * C.FPS)))
    out = os.path.join(C.BUILD, "sim_h.npy")
    t0 = time.time()
    steps = 0
    t = 0.0
    f_start = 0
    if t_resume is not None:
        prev = np.load(out)
        f_start = int(round(t_resume * C.FPS))
        frames[:f_start] = prev[:f_start]
        h[:] = prev[f_start - 1]
        t = f_start / C.FPS
    yrow = np.arange(C.NY)
    xcol = np.arange(C.NX)
    for f in range(f_start, nf):
        t_next = (f + 1) / C.FPS
        while t < t_next - 1e-9:
            noise = 0.97 * noise + 0.24 * rng.standard_normal(C.NX)
            top = R.top_profile(t, noise)
            h[0:2, :] = np.maximum(h[0:2, :], top[None, :])
            e = R.edge_level(t)
            if e > 0.01:
                prof = e * (0.85 + 0.15 * np.sin(yrow * 0.05 + 2.3 * t))
                h[:, 0] = np.maximum(h[:, 0], prof)
                h[:, -1] = np.maximum(h[:, -1], prof[::-1])
                h[-1, :] = np.maximum(h[-1, :], e * (0.9 + 0.1 * np.sin(xcol * 0.09 - 1.9 * t)))
            w = R.bed_mix(t)
            b = b1 * (1 - w) + b2 * w
            G, Gn = R.gravity(t)
            phi = R.phi_amp(t) * dome
            dt = solver.step(h, b, phi, G, Gn, R.SIGMA, R.slip(t), R.bottom_open(t), R.gate_open(t),
                             min(R.DT_MAX, t_next - t))
            k = R.retract(t)
            if k > 0:
                thin = np.clip((2.5 - h) / 1.0, 0, 1)
                h -= dt * k * h * thin * inside
                np.maximum(h, C.EPS, out=h)
            sw = R.swell(t)
            if sw > 0:
                h += dt * sw * np.clip((h - 0.2) / 0.4, 0, 1)
            t += dt
            steps += 1
        frames[f] = h
        if f % 24 == 23:
            np.save(out, frames[:f + 1])
        if f % 12 == 0:
            print(f"t={t:5.2f}s passos={steps} hmax={h.max():.2f} vol={h.sum():.0f} "
                  f"{time.time() - t0:.0f}s", flush=True)
    np.save(out, frames[:nf])
    print("sim ok", time.time() - t0)


if __name__ == "__main__":
    import sys
    run(float(sys.argv[1]) if len(sys.argv) > 1 else C.DUR,
        float(sys.argv[2]) if len(sys.argv) > 2 else None)
