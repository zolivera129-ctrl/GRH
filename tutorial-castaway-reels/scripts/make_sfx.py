"""Gera os efeitos sonoros do tutorial (sintetizados, sem licença de terceiros).

Uso: python3 scripts/make_sfx.py  (grava em public/sfx/)
"""
import os
import wave

import numpy as np

SR = 48000
OUT = os.path.join(os.path.dirname(__file__), "..", "public", "sfx")
rng = np.random.default_rng(7)


def t(d):
    return np.arange(int(SR * d)) / SR


def env(n, attack=0.002, decay=0.05):
    x = np.arange(n) / SR
    a = np.clip(x / attack, 0, 1)
    return a * np.exp(-x / decay)


def lowpass(x, cutoff):
    # filtro de um polo, suficiente para "amaciar" ruído
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def save(name, x, gain=0.8):
    x = x / (np.max(np.abs(x)) + 1e-9) * gain
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    stereo = np.repeat(pcm[:, None], 2, axis=1)
    with wave.open(os.path.join(OUT, name), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(stereo.tobytes())


os.makedirs(OUT, exist_ok=True)

# toque na tela: clique curto e seco
d = t(0.06)
x = np.sin(2 * np.pi * 1900 * d) * env(len(d), 0.0005, 0.008)
x += highpass(rng.standard_normal(len(d)), 2500) * env(len(d), 0.0003, 0.004) * 0.6
save("tap.wav", x, 0.55)

# tecla do teclado do iPhone
d = t(0.035)
x = highpass(rng.standard_normal(len(d)), 3000) * env(len(d), 0.0002, 0.003)
x += np.sin(2 * np.pi * 3200 * d) * env(len(d), 0.0002, 0.002) * 0.4
save("key.wav", x, 0.35)

# pop (entrada de elementos)
d = t(0.12)
f = 900 * np.exp(-d * 28) + 260
x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(d), 0.001, 0.035)
save("pop.wav", x, 0.6)

# whoosh (transições e rolagem rápida)
d = t(0.55)
n = rng.standard_normal(len(d))
cut = 300 + 3500 * np.sin(np.pi * d / d[-1]) ** 2
y = np.zeros_like(n)
acc = 0.0
for i, v in enumerate(n):
    a = np.exp(-2 * np.pi * cut[i] / SR)
    acc = (1 - a) * v + a * acc
    y[i] = acc
x = y * np.sin(np.pi * d / d[-1]) ** 1.5
save("whoosh.wav", x, 0.5)

# sucesso: dois sinos (C6 -> G6)
def bell(freq, dur):
    d = t(dur)
    s = sum(np.sin(2 * np.pi * freq * k * d) * (0.6 ** i) for i, k in enumerate([1, 2.0, 3.01]))
    return s * env(len(d), 0.003, 0.35)

a = bell(1046.5, 0.9)
b = bell(1568.0, 1.1)
x = np.zeros(int(SR * 1.3))
x[: len(a)] += a
off = int(SR * 0.12)
x[off: off + len(b)] += b
save("success.wav", x, 0.55)

# impacto (destaque do código de campanha)
d = t(1.1)
f = 120 * np.exp(-d * 6) + 42
x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(d), 0.002, 0.28)
x += lowpass(rng.standard_normal(len(d)), 900) * env(len(d), 0.001, 0.06) * 0.8
shimmer = t(1.1)
x += sum(np.sin(2 * np.pi * fr * shimmer) for fr in (2093, 2637, 3136)) * env(len(d), 0.01, 0.25) * 0.05
save("impact.wav", x, 0.7)

# chegada do código no campo: "ding" curto
d = t(0.5)
x = (np.sin(2 * np.pi * 1318.5 * d) + 0.4 * np.sin(2 * np.pi * 2637 * d)) * env(len(d), 0.002, 0.12)
save("ding.wav", x, 0.45)
print("ok", sorted(os.listdir(OUT)))
