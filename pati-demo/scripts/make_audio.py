"""Sintetiza a trilha instrumental e os sons de interface usados no vídeo (sem samples externos).

Saída em public/audio/: trilha.wav, clique.wav, envio.wav, revela.wav
Uso: python3 scripts/make_audio.py
"""
from pathlib import Path
import wave

import numpy as np

SR = 48000
OUT = Path(__file__).resolve().parent.parent / "public" / "audio"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(3)

DURATION = 39.0  # 38 s de vídeo + cauda
BPM = 92
BEAT = 60 / BPM
BAR = 4 * BEAT
# Marcos do vídeo (s): testes começam em 9, encerramento em 35.
TESTS_START, CLOSING = 9.0, 35.0


def write(name, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    data = (x * 32767).astype("<i2")
    with wave.open(str(OUT / name), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print("gerado:", OUT / name)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def lowpass(x, cutoff):
    # filtro de um polo, suficiente para amaciar o timbre
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def ep_note(freq, dur, vel=1.0):
    """Timbre de piano elétrico discreto: senoides com harmônicos que decaem rápido."""
    t = np.arange(int(dur * SR)) / SR
    env = np.exp(-t * 1.6) * (1 - np.exp(-t * 200))
    tone = (np.sin(2 * np.pi * freq * t)
            + 0.28 * np.exp(-t * 6) * np.sin(2 * np.pi * 2 * freq * t)
            + 0.08 * np.exp(-t * 12) * np.sin(2 * np.pi * 3.01 * freq * t))
    trem = 1 + 0.06 * np.sin(2 * np.pi * 4.2 * t)
    return vel * env * tone * trem


def place(buf, start, sig, pan=0.0):
    i = int(start * SR)
    if i >= len(buf):
        return
    sig = sig[: len(buf) - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(sig), 0] += sig * l
    buf[i:i + len(sig), 1] += sig * r


n = int(DURATION * SR)
music = np.zeros((n, 2))

# Am9 – Fmaj7 – Cmaj7 – G6, voicings fechados no registro médio
chords = [
    [57, 60, 64, 67, 71],
    [53, 57, 60, 64, 69],
    [48, 55, 59, 64, 67],
    [55, 59, 62, 64, 67],
]
roots = [45, 41, 48, 43]

t = 0.0
bar = 0
while t < CLOSING + BAR:
    ci = bar % 4
    final = t >= CLOSING - 0.01
    length = BAR * (2.2 if final else 1.25)
    for k, note in enumerate(chords[ci]):
        place(music, t + k * 0.012, ep_note(midi(note), length, 0.11), pan=(k - 2) * 0.18)
    # baixo suave
    tb = np.arange(int(length * SR)) / SR
    bass = 0.16 * np.sin(2 * np.pi * midi(roots[ci] - 12) * tb) * np.exp(-tb * 0.9) * (1 - np.exp(-tb * 60))
    place(music, t, bass)
    if final:
        break
    # pulso em colcheias durante os testes, crescendo aos poucos
    if t + BAR > TESTS_START:
        for b in range(8):
            tp = t + b * BEAT / 2
            if tp < TESTS_START or tp >= CLOSING:
                continue
            grow = min(1.0, (tp - TESTS_START) / (CLOSING - TESTS_START) * 1.4)
            note = chords[ci][[1, 3, 2, 4][b % 4]] + 12
            tt = np.arange(int(0.25 * SR)) / SR
            pluck = np.sin(2 * np.pi * midi(note) * tt) * np.exp(-tt * 18) * (1 - np.exp(-tt * 400))
            place(music, tp, (0.025 + 0.035 * grow) * pluck, pan=0.35 if b % 2 else -0.35)
            # shaker bem baixo a partir do segundo teste
            if tp >= 17.0:
                nn = int(0.06 * SR)
                sh = rng.standard_normal(nn) * np.exp(-np.arange(nn) / SR * 70)
                sh = sh - lowpass(sh, 5000)
                place(music, tp, 0.018 * grow * sh * (1.0 if b % 2 else 0.6), pan=0.2)
    t += BAR
    bar += 1

# envelope geral: entra suave, cresce nos testes, desacelera no encerramento
tt = np.arange(n) / SR
env = np.interp(tt, [0, 1.5, TESTS_START, CLOSING, CLOSING + 2.5, DURATION], [0, 0.75, 0.8, 1.0, 0.7, 0])
music *= env[:, None]
music = np.stack([lowpass(music[:, 0], 7000), lowpass(music[:, 1], 7000)], axis=1)
music *= 0.5 / np.max(np.abs(music))  # pico em -6 dBFS; o volume final é ajustado no Remotion
write("trilha.wav", music)

# clique de mouse: ruído curto filtrado + tique agudo
m = int(0.05 * SR)
tm = np.arange(m) / SR
click = rng.standard_normal(m) * np.exp(-tm * 260)
click = lowpass(click, 3500) * 0.9 + 0.25 * np.sin(2 * np.pi * 2300 * tm) * np.exp(-tm * 400)
write("clique.wav", 0.6 * click / np.max(np.abs(click)))

# envio de mensagem: varredura curta e macia
m = int(0.22 * SR)
tm = np.arange(m) / SR
f = np.interp(tm, [0, 0.22], [420, 880])
send = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * np.clip(tm / 0.22, 0, 1)) ** 2
write("envio.wav", 0.35 * send)

# revelação de recomendação: duas notas suaves
m = int(1.2 * SR)
tm = np.arange(m) / SR
chime = np.zeros(m)
for delay, note in ((0.0, 81), (0.09, 88)):
    d = int(delay * SR)
    tt = tm[: m - d]
    chime[d:] += np.sin(2 * np.pi * midi(note) * tt) * np.exp(-tt * 5) * (1 - np.exp(-tt * 300))
write("revela.wav", 0.28 * chime / np.max(np.abs(chime)))
