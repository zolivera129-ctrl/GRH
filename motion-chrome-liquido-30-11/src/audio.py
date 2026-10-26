"""Desenho de som sintetizado a partir da própria simulação.

Camadas, todas baixas e discretas:
- corpo viscoso: ruído grave filtrado que segue o quanto o líquido se move;
- estiramento: ruído médio ressonante, com varreduras lentas;
- ressonâncias de prata: parciais inarmônicas com cauda longa, nos momentos-chave;
- gotas: estalos molhados curtos onde as pontas dos lóbulos aceleram;
- cintilância: agudos muito leves acompanhando as passagens de luz.
O panorama estéreo segue o lado da tela onde o líquido está se mexendo.
Sem música, sem impacto, sem efeito de terror.
"""
import os
import numpy as np
from scipy import signal

import config as C

SR = 48000


def env_from_frames(v, n):
    x = np.arange(len(v)) / C.FPS
    return np.interp(np.arange(n) / SR, x, v)


def bandnoise(n, lo, hi, rng, order=2):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, rng.standard_normal(n))


def lowpass(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="low", fs=SR, output="sos"), x)


def bell(n, t0, f0, dur, amp, rng, ratios=(1.0, 2.76, 4.07, 5.43, 6.8)):
    out = np.zeros(n)
    i0 = int(t0 * SR)
    m = min(n - i0, int(dur * SR))
    if m <= 0:
        return out
    tt = np.arange(m) / SR
    att = 1 - np.exp(-tt / 0.012)
    s = np.zeros(m)
    for k, r in enumerate(ratios):
        dec = dur / (1 + 0.9 * k)
        det = 1 + rng.uniform(-0.002, 0.002)
        s += (0.6 ** k) * np.sin(2 * np.pi * f0 * r * det * tt + rng.uniform(0, 6.28)) * np.exp(-tt / dec)
    tail = np.clip((m - np.arange(m)) / (0.35 * m), 0, 1)  # cauda que some, sem corte
    out[i0:i0 + m] = amp * att * s * tail
    return out


def drop(n, t0, f0, amp):
    out = np.zeros(n)
    i0 = int(t0 * SR)
    m = min(n - i0, int(0.09 * SR))
    if m <= 0:
        return out
    tt = np.arange(m) / SR
    f = f0 * (0.45 + 0.55 * np.exp(-tt / 0.012))
    ph = 2 * np.pi * np.cumsum(f) / SR
    out[i0:i0 + m] = amp * np.sin(ph) * np.exp(-tt / 0.022) * (1 - np.exp(-tt / 0.0015))
    return out


def main():
    h = np.load(os.path.join(C.BUILD, "sim_h.npy"))
    nf = len(h)
    n = int(C.DUR * SR)
    rng = np.random.default_rng(3)

    d = np.abs(np.diff(h, axis=0, prepend=h[:1]))
    act = d.mean(axis=(1, 2))
    act = act / (np.percentile(act, 90) + 1e-9)
    act = np.tanh(act)  # a abertura final mexe muito, mas o som não pode dar um salto
    act = np.convolve(act, np.ones(9) / 9, mode="same")
    xs = np.arange(h.shape[2])[None, :]
    colw = d.sum(axis=1)
    pan = ((colw * xs).sum(1) / (colw.sum(1) + 1e-9)) / h.shape[2]  # 0 esq .. 1 dir
    pan = np.convolve(np.nan_to_num(pan, nan=0.5), np.ones(9) / 9, mode="same")
    cover = (h > 0.1).mean(axis=(1, 2))

    A = env_from_frames(act, n)
    P = env_from_frames(pan, n)
    Cv = env_from_frames(cover, n)
    t = np.arange(n) / SR

    # corpo viscoso
    body = lowpass(rng.standard_normal(n), 140, 4) * 6.0
    body *= (0.15 + 0.85 * np.clip(A, 0, 1.5)) * (0.4 + 0.6 * Cv)
    sub = 0.05 * np.sin(2 * np.pi * 43 * t + 0.6 * np.sin(2 * np.pi * 0.21 * t)) * np.clip(Cv * 1.6, 0, 1)
    # estiramento: ruído médio com ressonância que desliza devagar
    stretch = np.zeros(n)
    for fc, ph in ((320, 0.0), (520, 1.7), (760, 3.1)):
        # três bandas fixas que trocam de peso devagar: ressonância que desliza sem cliques
        lo = bandnoise(n, fc * 0.75, fc * 0.95, rng)
        hi = bandnoise(n, fc * 1.05, fc * 1.3, rng)
        k = 0.5 + 0.5 * np.sin(2 * np.pi * 0.17 * t + ph)
        stretch += lo * (1 - k) + hi * k
    stretch *= 0.5 * np.clip(A, 0, 1.4) ** 1.3
    # cintilância (agudo muito leve)
    shim = bandnoise(n, 6500, 12000, rng) * 0.035
    sweep = np.exp(-((t - 1.75) / 0.45) ** 2) + np.exp(-((t - 14.3) / 0.5) ** 2) + 0.25 * Cv
    shim *= sweep * (0.6 + 0.4 * np.sin(2 * np.pi * 7.3 * t) ** 2)

    # ressonâncias de prata nos momentos-chave
    bells = np.zeros(n)
    for t0, f0, dur, amp in ((1.05, 880, 3.0, 0.050), (2.05, 660, 2.4, 0.030), (4.6, 990, 2.0, 0.020),
                             (6.3, 740, 2.2, 0.020), (10.3, 554, 2.6, 0.025), (12.3, 440, 3.0, 0.040),
                             (13.15, 587, 2.4, 0.035), (13.95, 880, 1.05, 0.055), (14.05, 1318, 0.95, 0.025)):
        bells += bell(n, t0, f0, dur, amp, rng)

    # gotas: onde a frente avança mais rápido (pontas dos lóbulos)
    drops = np.zeros(n)
    front = np.array([(fr > 0.1).sum() for fr in h], float)
    grow = np.diff(front, prepend=front[0])
    cand = [f for f in range(int(2.4 * C.FPS), int(9.5 * C.FPS)) if grow[f] > np.percentile(grow[48:230], 80)]
    rng.shuffle(cand)
    for f in sorted(cand[:14]):
        drops += drop(n, f / C.FPS + rng.uniform(0, 0.03), rng.uniform(900, 1700), rng.uniform(0.04, 0.08))

    mono_low = body + sub
    mid = stretch + bells + drops + shim
    pl = np.cos(P * np.pi / 2) * 1.2
    pr = np.sin(P * np.pi / 2) * 1.2
    L = mono_low + mid * pl
    Rr = mono_low + mid * pr
    # largura: um eco curto e escuro no lado oposto
    dl = int(0.017 * SR)
    L[dl:] += 0.25 * lowpass(Rr[:-dl], 3000)
    Rr[dl:] += 0.25 * lowpass(L[:-dl], 3000)
    st = np.stack([L, Rr], 1)
    fade = np.clip(t / 0.4, 0, 1) * np.clip((C.DUR - t) / 0.35, 0, 1)
    st *= fade[:, None]
    rms = np.sqrt((st ** 2).mean())
    st *= 10 ** (-24 / 20) / (rms + 1e-9)          # nível médio baixo e elegante
    st = 0.6 * np.tanh(st / 0.6)                   # limitador suave
    st *= 10 ** (-3 / 20) / max(np.abs(st).max(), 10 ** (-3 / 20))
    from scipy.io import wavfile
    out = os.path.join(C.BUILD, "som.wav")
    wavfile.write(out, SR, (st * 32767).astype(np.int16))
    print("ok", out, nf)


if __name__ == "__main__":
    main()
