"""Trilha original do tutorial (tropical house, 120 BPM, Lá menor), sintetizada por código.

Não usa samples nem trechos de terceiros, então não depende de licença.
A grade de compassos está presa à linha do tempo do vídeo:
  - 0,0–3,2 s: introdução (gancho), com subida que leva à entrada do celular
  - 3,2 s: entra o groove (passo 1)
  - 27,2–29,2 s: preparação
  - 29,2 s: refrão com melodia, junto com o "DON'T SKIP IT" do código de campanha
  - 45,2 s: acorde final, que soa até o fim (48,3 s)

Uso: python3 scripts/make_music.py   (gera public/music/castaway-tropical.m4a; precisa de ffmpeg)
"""
import os
import subprocess
import wave

import numpy as np

SR = 48000
BPM = 120
BEAT = 60 / BPM
BAR = 4 * BEAT
STEP = BAR / 16
T0 = 877 / 30 - 14 * BAR  # 1º tempo do compasso 0; o compasso 14 cai no frame 877 (código de campanha)
LENGTH = 48.4

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "public", "music")
TMP_WAV = os.path.join(HERE, "..", "out", "castaway-tropical.wav")

rng = np.random.default_rng(2026)
N = int(LENGTH * SR)
mix = np.zeros((N, 2))
send = np.zeros((N, 2))  # envio para o reverb


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def bar_t(k, step=0):
    return T0 + k * BAR + step * STEP


def place(sig, t, gain=1.0, pan=0.0, rev=0.0):
    """Soma `sig` (mono) em `t` segundos, com pan (-1..1) e envio de reverb."""
    i = int(round(t * SR))
    if i >= N or i + len(sig) <= 0:
        return
    s = sig
    if i < 0:
        s = s[-i:]
        i = 0
    s = s[: N - i]
    left = np.cos((pan + 1) * np.pi / 4)
    right = np.sin((pan + 1) * np.pi / 4)
    mix[i : i + len(s), 0] += s * gain * left
    mix[i : i + len(s), 1] += s * gain * right
    if rev:
        send[i : i + len(s), 0] += s * gain * rev * left
        send[i : i + len(s), 1] += s * gain * rev * right


def tt(d):
    return np.arange(int(d * SR)) / SR


def fft_filter(x, lo=None, hi=None):
    """Filtro estático (passa-altas `lo` / passa-baixas `hi`) no domínio da frequência."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if lo:
        g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1)) ** 4)
    if hi:
        g *= 1 / np.sqrt(1 + (f / hi) ** 4)
    return np.fft.irfft(X * g, len(x))


# ---------------------------------------------------------------------------
# Instrumentos
# ---------------------------------------------------------------------------
def marimba(m, dur=0.6):
    f = midi(m)
    t = tt(dur)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.32)
    s += 0.11 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t / 0.05)
    s += 0.025 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t / 0.02)
    s *= np.clip(t / 0.002, 0, 1)
    return s


def steelpan(m, dur=0.9):
    f = midi(m)
    t = tt(dur)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.12) / 0.2, 0, 1)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    s = np.sin(ph) + 0.45 * np.sin(2.01 * ph) * np.exp(-t / 0.25) + 0.18 * np.sin(3.0 * ph) * np.exp(-t / 0.12)
    s *= np.exp(-t / 0.55) * np.clip(t / 0.004, 0, 1)
    return s


def bass(m, dur=0.42):
    f = midi(m)
    t = tt(dur)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t)
    s = np.tanh(1.6 * s) / np.tanh(1.6)
    env = np.clip(t / 0.006, 0, 1) * np.exp(-t / 0.3) * np.clip((dur - t) / 0.03, 0, 1)
    return s * env


def kick():
    t = tt(0.4)
    f = 125 * np.exp(-t * 32) + 46
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
    s += 0.25 * fft_filter(rng.standard_normal(len(t)), lo=1500) * np.exp(-t / 0.004)
    return s


def clap():
    t = tt(0.3)
    n = fft_filter(rng.standard_normal(len(t)), lo=900, hi=5000)
    env = np.zeros_like(t)
    for k, d in enumerate([0.0, 0.011, 0.022]):
        env += (t >= d) * np.exp(-np.clip(t - d, 0, None) / (0.008 if k < 2 else 0.12))
    return n * env * 0.6


def shaker(acc=1.0):
    t = tt(0.09)
    n = fft_filter(rng.standard_normal(len(t)), lo=6000)
    return n * np.clip(t / 0.006, 0, 1) * np.exp(-t / 0.03) * acc


def hat_open():
    t = tt(0.25)
    n = fft_filter(rng.standard_normal(len(t)), lo=7000)
    return n * np.exp(-t / 0.08)


def pad_chord(notes, dur):
    t = tt(dur)
    s = np.zeros((len(t), 2))
    for m in notes:
        for ch, det in enumerate((-7, 7)):
            for det2 in (0, det * 0.4):
                f = midi(m) * 2 ** ((det + det2) / 1200)
                for h in range(1, 7):
                    s[:, ch] += np.sin(2 * np.pi * f * h * t + h * ch) / h
    env = np.clip(t / 0.35, 0, 1) * np.clip((dur - t) / 0.45, 0, 1)
    s *= env[:, None] / (len(notes) * 4)
    for ch in range(2):
        s[:, ch] = fft_filter(s[:, ch], lo=150, hi=1800)
    return s


def riser(dur):
    t = tt(dur)
    n = rng.standard_normal(len(t))
    y = np.zeros_like(n)
    acc = 0.0
    cut = 300 + 7000 * (t / dur) ** 2
    a = np.exp(-2 * np.pi * cut / SR)
    for i in range(len(n)):
        acc = (1 - a[i]) * n[i] + a[i] * acc
        y[i] = acc
    sweep = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (2.5 * t / dur)) / SR) * 0.25
    return (y * 1.6 + sweep) * (t / dur) ** 2


# ---------------------------------------------------------------------------
# Arranjo
# ---------------------------------------------------------------------------
CHORDS = [  # Am – F – C – G
    {"pad": [57, 60, 64, 69], "mar": [69, 72, 76], "bass": 45},
    {"pad": [53, 57, 60, 65], "mar": [65, 69, 72], "bass": 41},
    {"pad": [55, 60, 64, 67], "mar": [67, 72, 76], "bass": 48},
    {"pad": [55, 59, 62, 67], "mar": [67, 71, 74], "bass": 43},
]
MELODY = [  # (passo, nota) por compasso do refrão
    [(0, 76), (3, 74), (6, 72), (10, 69), (12, 72), (14, 74)],
    [(0, 72), (3, 69), (6, 72), (8, 77), (12, 76)],
    [(0, 79), (3, 76), (6, 74), (8, 72), (11, 74), (14, 76)],
    [(0, 74), (3, 71), (6, 67), (8, 71), (12, 74)],
]
TRES = [0, 3, 6, 8, 11, 14]  # ritmo 3-3-2 típico do tropical house

KICK, CLAP = kick(), clap()
duck = np.ones(N)  # sidechain (bombeado) aplicado no pad e no baixo


def add_kick(t, g=0.95):
    place(KICK, t, g)
    i = int(t * SR)
    d = 1 - 0.55 * np.exp(-tt(0.35) / 0.09)
    j = min(N, i + len(d))
    if i < N:
        duck[i:j] = np.minimum(duck[i:j], d[: j - i])


pad_bus = np.zeros((N, 2))
bass_bus = np.zeros(N)


def add_pad(chord, t, dur, g=1.0):
    p = pad_chord(chord, dur)
    i = int(t * SR)
    j = min(N, i + len(p))
    if i < N:
        pad_bus[i:j] += p[: j - i] * g


def add_bass(m, t, dur=0.42, g=1.0):
    b = bass(m, dur)
    i = int(t * SR)
    j = min(N, i + len(b))
    if i < N:
        bass_bus[i:j] += b[: j - i] * g


# introdução (antes do compasso 0): pad de Lá menor surgindo
add_pad(CHORDS[0]["pad"], 0.0, T0 + 0.2, 0.8)
for s, m in [(10, 69), (12, 72), (14, 76)]:
    place(marimba(m), T0 - BAR + s * STEP, 0.18, 0.2, rev=0.5)

for k in range(22):
    ch = CHORDS[k % 4]
    t = bar_t(k)
    intro = k == 0
    verse_a = 1 <= k <= 4
    build = k == 13
    chorus = 14 <= k <= 17
    outro = k == 21

    add_pad(ch["pad"], t, BAR + 0.3, 1.25 if chorus else 1.0)

    # marimba 3-3-2
    for n, s in enumerate(TRES):
        if intro and s not in (0, 8):
            continue
        notes = ch["mar"] if s in (0, 8) else ch["mar"][1:]
        for m in notes:
            place(marimba(m), bar_t(k, s), 0.16 if not build else 0.11, -0.25 if n % 2 else 0.25, rev=0.35)

    if intro or build:
        if build:  # palmas acelerando + shaker em crescendo
            for s in list(range(0, 8, 2)) + list(range(8, 16)):
                place(CLAP, bar_t(k, s), 0.12 + 0.25 * s / 16, 0.0, rev=0.3)
            for s in range(16):
                place(shaker(0.4 + s / 16), bar_t(k, s), 0.16, 0.4)
        continue

    # bateria
    if verse_a:
        for b in (0, 2):
            add_kick(t + b * BEAT)
    elif outro:
        add_kick(t)
        add_kick(t + 2 * BEAT, 0.7)
    else:
        for b in range(4):
            add_kick(t + b * BEAT)
        for b in (1, 3):
            place(CLAP, t + b * BEAT, 0.42, 0.0, rev=0.25)
    for s in range(16):
        place(shaker(1.0 if s % 2 else 0.5), bar_t(k, s), 0.13, 0.45)
    if chorus or (5 <= k <= 12 and k % 2):
        for b in range(4):
            place(hat_open(), t + b * BEAT + BEAT / 2, 0.09, -0.4)

    # baixo
    for s, dur in [(0, 0.5), (6, 0.3), (10, 0.42)]:
        add_bass(ch["bass"], bar_t(k, s), dur, 0.95 if not outro else 0.7)

    # melodia do refrão
    if chorus:
        for s, m in MELODY[k - 14]:
            place(steelpan(m), bar_t(k, s), 0.3, 0.0, rev=0.45)

# subidas
place(riser(BAR), bar_t(0), 0.22)
place(riser(BAR), bar_t(13), 0.28)

# final: Dó maior soando até o fim
tf = bar_t(22)
add_kick(tf, 0.8)
add_pad([48, 55, 60, 64, 67], tf, LENGTH - tf, 1.2)
add_bass(36, tf, 1.6, 0.6)
for n, m in enumerate([60, 64, 67, 72, 76, 79, 84]):
    place(marimba(m, 1.5), tf + n * STEP * 0.75, 0.15, -0.5 + n / 6, rev=0.6)
place(steelpan(84, 2.5), tf + 0.6, 0.2, 0.0, rev=0.7)

# ---------------------------------------------------------------------------
# Mixagem
# ---------------------------------------------------------------------------
mix += pad_bus * duck[:, None] * 0.55
bass_bus = fft_filter(bass_bus, hi=900)
mix += np.stack([bass_bus, bass_bus], 1) * duck[:, None] * 0.42

# reverb: convolução com ruído em decaimento (um IR por canal, para abrir o estéreo)
ir_t = tt(1.8)
for ch in range(2):
    ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.45)
    ir = fft_filter(ir, lo=250, hi=6000)
    ir /= np.sqrt(np.sum(ir**2))
    L = N + len(ir)
    wet = np.fft.irfft(np.fft.rfft(send[:, ch], L) * np.fft.rfft(ir, L), L)[:N]
    mix[:, ch] += wet * 0.5

# fades e master
fade_in = np.clip(np.arange(N) / (0.6 * SR), 0, 1)
fade_out = np.clip((LENGTH - 0.15 - np.arange(N) / SR) / 2.2, 0, 1)
mix *= (fade_in * fade_out)[:, None]
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
mix /= np.max(np.abs(mix)) / 0.89

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(TMP_WAV), exist_ok=True)
pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
with wave.open(TMP_WAV, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
out = os.path.join(OUT_DIR, "castaway-tropical.m4a")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", TMP_WAV, "-c:a", "aac", "-b:a", "192k", out], check=True)
print("ok", out, f"T0={T0:.3f}s")
