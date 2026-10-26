"""Render do cromo: superfície (relevo + líquido) iluminada por um estúdio.

Cada pixel calcula a normal da superfície real (letras + espessura do
líquido simulado), reflete o raio da câmera e busca o ambiente: softboxes
grandes, filetes laterais, rebatimento carmim de baixo e, nas bordas
rasantes, o próprio veludo vermelho refletido no metal.
"""
import os
import sys
import subprocess
import numpy as np
import cv2
from multiprocessing import Pool

import config as C
import roteiro as R

S = C.SCALE
W, H = C.W, C.H
SRC = os.path.dirname(os.path.abspath(__file__))

G = {}


def ss(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def fbm(shape, seed, octaves=6, base=6, persist=0.55):
    rng = np.random.default_rng(seed)
    hh, ww = shape
    acc = np.zeros(shape, np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        n = base * 2 ** o
        r = rng.random((max(2, int(n * hh / ww)) + 1, n + 1)).astype(np.float32)
        acc += amp * cv2.resize(r, (ww, hh), interpolation=cv2.INTER_CUBIC)
        tot += amp
        amp *= persist
    acc /= tot
    return (acc - acc.mean()) / (acc.std() + 1e-6)


def init():
    bed = np.load(C.bed_path())
    G["b1"], G["b2"] = bed["b1"], bed["b2"]
    bsim = np.load(os.path.join(C.BUILD, "bed_sim.npz"))
    G["bs1"], G["bs2"] = bsim["b1"].astype(np.float32), bsim["b2"].astype(np.float32)
    G["h"] = np.load(os.environ.get("SIM_H", os.path.join(C.BUILD, "sim_h.npy")), mmap_mode="r")
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    G["xx"], G["yy"] = xx, yy
    # veludo: duas camadas de manchas que derivam devagar (margem para deslocar)
    G["vel1"] = fbm((H + 64 * S, W + 64 * S), 11, base=5)
    G["vel2"] = fbm((H + 64 * S, W + 64 * S), 23, base=9, persist=0.6)
    G["fib"] = fbm((H, W), 5, octaves=3, base=180, persist=0.5)
    # ondulação de superfície em células da simulação
    G["wav1"] = fbm((H + 600 * S, W // 2 + 300 * S), 31, octaves=2, base=3, persist=0.45)
    G["wav2"] = fbm((H + 600 * S, W // 2 + 300 * S), 47, octaves=2, base=5, persist=0.45)
    G["wav3"] = fbm((H + 600 * S, W // 2 + 300 * S), 59, octaves=2, base=11, persist=0.5)
    G["grain_rng"] = None
    G["win_in"] = np.clip((0.93 - R.window_shape(C.NX, C.NY)) / 0.08, 0, 1).astype(np.float32)


def velvet(t):
    o1 = 32 * S + 18 * S * np.array([np.sin(0.21 * t), np.cos(0.17 * t)])
    o2 = 32 * S + 24 * S * np.array([np.cos(0.13 * t + 1), np.sin(0.19 * t + 2)])
    n1 = G["vel1"][int(o1[1]):int(o1[1]) + H, int(o1[0]):int(o1[0]) + W]
    n2 = G["vel2"][int(o2[1]):int(o2[1]) + H, int(o2[0]):int(o2[0]) + W]
    xx, yy = G["xx"] / W, G["yy"] / H
    cx = 0.5 + 0.03 * np.sin(0.3 * t)
    cy = 0.45 + 0.02 * np.cos(0.23 * t)
    rr = ((xx - cx) / 0.75) ** 2 + ((yy - cy) / 0.62) ** 2
    glow = np.exp(-rr * 1.6)
    mott = np.clip(0.80 + 0.17 * n1 + 0.09 * n2 + 0.04 * G["fib"], 0.2, 1.5)
    lum = (0.05 + 0.75 * glow) * mott
    # dobras mais escuras, como veludo amassado
    dark = ss(0.4, -1.6, n1 * 0.7 + n2 * 0.5)
    lum = lum * (1 - 0.45 * dark)
    bg = np.empty((H, W, 3), np.float32)
    bg[..., 0] = lum * 0.010 + 0.002 * glow   # B
    bg[..., 1] = lum * 0.008
    bg[..., 2] = lum * 0.200                  # R
    return bg


def env(rx, ry, rz, t, sweep):
    """Ambiente HDR do estúdio, por direção refletida (x dir., y baixo, z para a câmera)."""
    out = np.zeros(rx.shape + (3,), np.float32)

    def box(cx, cy, cz, su, sv, inten, col, tilt=0.0):
        n = np.sqrt(cx * cx + cy * cy + cz * cz)
        cx, cy, cz = cx / n, cy / n, cz / n
        dx, dy = rx - cx, ry - cy
        ct, st = np.cos(tilt), np.sin(tilt)
        u = (dx * ct + dy * st) / su
        v = (-dx * st + dy * ct) / sv
        facing = ss(0.0, 0.3, rx * cx + ry * cy + rz * cz)
        k = (1 - ss(0.78, 1.0, np.abs(u))) * (1 - ss(0.72, 1.0, np.abs(v))) * facing
        for c in range(3):
            out[..., c] += k * inten * col[c]

    # frente (atrás da câmera): teto claro que escurece para baixo, com réguas de luz
    face = ss(-0.2, 0.6, rz)
    front = 0.03 + 0.24 * ss(0.12, -0.40, ry) ** 2
    front += 1.4 * np.exp(-((ry + 0.13 + 0.015 * np.sin(0.5 * t)) / 0.026) ** 2)
    front += 0.5 * np.exp(-((ry - 0.17) / 0.032) ** 2)
    front += 0.5 * np.exp(-((ry + 0.30) / 0.05) ** 2)
    front *= 0.55 + 0.45 * np.cos(rx * 9.0 + 0.4 * np.sin(0.3 * t)) ** 2
    # duas réguas largas atrás da câmera: o metal quase plano ganha massas de luz com borda nítida
    front += 0.75 * (1 - ss(0.82, 1.0, np.abs(rx + 0.17 - 0.015 * np.sin(0.4 * t)) / 0.055)) * ss(0.35, 0.0, ry)
    front += 0.55 * (1 - ss(0.82, 1.0, np.abs(ry - 0.06) / 0.035)) * (1 - ss(0.25, 0.45, np.abs(rx)))
    front *= face
    # rebatimento carmim de baixo e das laterais
    red = 0.26 * ss(0.25, 0.85, ry) + 0.08 * ss(0.5, 0.95, np.abs(rx))
    out[..., 0] += front * 1.00 + red * 0.010
    out[..., 1] += front * 0.98 + red * 0.008
    out[..., 2] += front * 0.96 + red * 0.90

    sx = 0.32 * np.sin(0.33 * t + 0.6)
    box(sx, -0.60, 0.80, 0.62, 0.16, 7.0, (1.0, 0.99, 0.97))
    box(0.0, -0.14, 0.99, 0.55, 0.10, 0.38, (1.0, 0.99, 0.98))          # chapa frontal suave            # softbox de cima, varrendo
    box(-0.78, -0.10, 0.62, 0.10, 0.75, 4.2, (1.0, 0.98, 0.96), 0.12)   # filete esquerdo
    box(0.74, 0.05, 0.67, 0.12, 0.62, 3.0, (0.96, 0.98, 1.0), -0.10)   # filete direito
    box(0.0 - sx * 0.5, 0.42, 0.90, 0.30, 0.05, 1.6, (0.92, 0.92, 1.0))  # régua baixa
    box(0.0, 0.88, 0.48, 0.85, 0.25, 0.8, (0.02, 0.02, 0.95))           # carmim de baixo
    if sweep is not None:
        pos, inten = sweep
        band = rx * 0.6 + ry * 0.8
        k = np.exp(-((band - pos) / 0.07) ** 2) * ss(0.0, 0.4, rz)
        for c in range(3):
            out[..., c] += k * inten
    return out


def sweep_at(t):
    """Faixa de luz que passa pelas letras na revelação de cada mensagem."""
    if 0.9 < t < 2.6:
        u = (t - 0.9) / 1.7
        return (-0.9 + 1.8 * u, 3.5 * np.sin(np.pi * u))
    if 13.75 < t < 15.0:
        u = (t - 13.75) / 1.25
        return (-0.9 + 1.8 * u, 3.2 * np.sin(np.pi * min(u, 1.0)))
    return None


def frame(f):
    t = f / C.FPS
    hs = np.array(G["h"][min(f, len(G["h"]) - 1)], np.float32)
    # borda de cima: o líquido chega de fora do quadro, sem as marcas das bicas
    k = np.linspace(0, 1, 18, dtype=np.float32)[:, None] ** 1.5
    hs[:18] = hs[18] * (1 - k) + hs[:18] * k
    w = float(R.bed_mix(t))
    rise = float(ss(0.9, 1.9, t))
    b = G["b1"] * (1 - w) + G["b2"] * w
    b = b * (0.25 + 0.75 * rise)
    bs = G["bs1"] * (1 - w) + G["bs2"] * w
    # superfície livre da simulação (relevo + líquido); o alisamento vai nela,
    # não na espessura, para um lençol nivelado continuar plano sobre as letras
    es = bs + hs
    wet_s = ss(0.06, 0.35, hs)
    thick = (ss(1.2, 2.6, es) * wet_s).astype(np.float32)
    es = es + (cv2.GaussianBlur(es, (0, 0), 1.6) - es) * thick
    es = cv2.GaussianBlur(es, (0, 0), 0.6)
    # cobertura total: o lençol grosso esconde o relevo de baixo (sem marca de letra)
    hide = float(ss(11.9, 12.3, t) * (1 - ss(12.95, 13.4, t)))
    if hide > 0:
        es = es + (cv2.GaussianBlur(es, (0, 0), 3.5) - es) * (hide * thick)
    hs = cv2.GaussianBlur(hs, (0, 0), 0.6)
    h = np.maximum(cv2.resize(hs, (W, H), interpolation=cv2.INTER_CUBIC), 0)
    eta_sim = cv2.resize(es.astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    # o cromo amplifica qualquer quina de curvatura: alisa o que veio da grade
    eta_sim = cv2.GaussianBlur(eta_sim, (0, 0), 0.6 * C.CELL * S)
    text_a = float(ss(0.85, 1.55, t))

    hd = np.maximum(h - 0.05, 0)
    a = ss(0.06, 0.14, h)
    # o véu residual dentro da janela termina de se recolher
    kr = float(ss(13.5, 14.3, t))
    if kr > 0:
        ins = cv2.resize(G["win_in"], (W, H), interpolation=cv2.INTER_LINEAR)
        lift = kr * ins
        a = a * (1 - lift) + ss(0.6, 1.4, h) * lift
    # uma só curva de altura para relevo e líquido: íngreme perto de zero (lóbulos
    # redondos), comprimida no lençol grosso. Lençol nivelado = superfície plana.
    # seco: relevo nítido das letras; molhado: a superfície da própria simulação
    wet = ss(0.06, 0.35, h)
    th = cv2.resize(thick, (W, H), interpolation=cv2.INTER_LINEAR)
    if hide > 0:
        wet = np.maximum(wet, hide * ss(0.2, 0.6, th))
    eta = b * (1 - wet) + np.maximum(eta_sim, b) * wet
    z = (C.ZA * (1 - np.exp(-eta / C.Z0)) + C.ZB * eta) * S
    # ondulação viva do lençol grosso: ondas largas que respiram e escorrem
    if th.max() > 0:
        amp = 0.6 + 0.9 * ss(10.4, 12.0, t) - 0.7 * ss(13.2, 14.2, t)
        oy = float((t * 60 * S) % (H * 0.9))
        ox = float(40 * S * np.sin(0.4 * t))
        w1 = cv2.remap(G["wav1"], G["xx"] * 0.5 + 64 * S + ox, G["yy"] * 0.5 + 32 * S + (H * 0.45 - oy * 0.5),
                       cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        w2 = cv2.remap(G["wav2"], G["xx"] * 0.5 + 200 * S - ox, G["yy"] * 0.5 + 400 * S + (H * 0.72 - oy * 0.8),
                       cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        w3 = cv2.remap(G["wav3"], G["xx"] * 0.5 + 100 * S + ox * 0.5, G["yy"] * 0.5 + 200 * S + (H * 0.6 - oy * 1.1),
                       cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        z = z + th * (5.5 * w1 + 2.8 * w2 + 0.7 * w3) * amp * S
    z = z.astype(np.float32)
    z = z + (cv2.GaussianBlur(z, (0, 0), 1.2 * S) - z) * wet
    gx = cv2.Sobel(z, cv2.CV_32F, 1, 0, ksize=3) / 8.0
    gy = cv2.Sobel(z, cv2.CV_32F, 0, 1, ksize=3) / 8.0
    inv = 1.0 / np.sqrt(gx * gx + gy * gy + 1.0)
    nx, ny, nz = -gx * inv, -gy * inv, inv

    # câmera em perspectiva, frontal e travada
    fcam = 2.4 * H
    vx, vy, vz = (G["xx"] - W / 2), (G["yy"] - H / 2), np.full((H, W), -fcam, np.float32)
    vl = 1.0 / np.sqrt(vx * vx + vy * vy + vz * vz)
    vx, vy, vz = vx * vl, vy * vl, vz * vl
    d = vx * nx + vy * ny + vz * nz
    rx, ry, rz = vx - 2 * d * nx, vy - 2 * d * ny, vz - 2 * d * nz

    bg = velvet(t)
    mt = ss(0.02, 0.25, b / C.TEXT_H) * text_a
    m = np.maximum(mt, a)

    # sombras de contato no veludo
    sm = cv2.resize(m, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    sh1 = cv2.GaussianBlur(sm, (0, 0), 2.0 * S)
    sh2 = cv2.GaussianBlur(sm, (0, 0), 7.0 * S)
    M = np.float32([[1, 0, 0], [0, 1, 2.0 * S]])
    sh = cv2.warpAffine(0.6 * sh1 + 0.5 * sh2, M, (W // 4, H // 4), borderMode=cv2.BORDER_REPLICATE)
    sh = cv2.resize(sh, (W, H), interpolation=cv2.INTER_LINEAR)
    bg *= (1 - np.clip(sh, 0, 0.85))[..., None]

    e = env(rx, ry, rz, t, sweep_at(t))
    # reflexo do próprio veludo nas bordas rasantes (SSR barato)
    vis = cv2.resize(bg * (1 - m)[..., None], (W // 8, H // 8), interpolation=cv2.INTER_AREA)
    vis = cv2.GaussianBlur(vis, (0, 0), 3.0 * S)
    q = 1.0 / 8
    mapx = ((G["xx"] + rx * 90 * S) * q).astype(np.float32)
    mapy = ((G["yy"] + ry * 90 * S) * q).astype(np.float32)
    ssr = cv2.remap(vis, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    graze = ss(0.95, 0.35, rz)
    e += ssr * (2.2 * graze)[..., None]

    # Fresnel do metal (prata levemente quente) e oclusão nas dobras
    cos = np.clip(-d, 0, 1)
    fr = (1 - cos) ** 5
    f0 = np.array([0.90, 0.92, 0.95], np.float32)  # BGR
    spec = e * (f0 + (1 - f0) * fr[..., None])
    lap = cv2.Laplacian(cv2.resize(z, (W // 2, H // 2)), cv2.CV_32F, ksize=5)
    lap = cv2.resize(lap, (W, H))
    occ = 1 - 0.55 * ss(0.0, 2.5 * S, lap / S)
    spec *= occ[..., None]

    img = bg * (1 - m)[..., None] + spec * m[..., None]

    # brilho (bloom) das luzes no metal
    small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    br = np.maximum(small - 1.2, 0)
    bloom = cv2.GaussianBlur(br, (0, 0), 2 * S) * 0.22 + cv2.GaussianBlur(br, (0, 0), 10 * S) * 0.10
    img += cv2.resize(bloom, (W, H), interpolation=cv2.INTER_LINEAR)

    # ACES (aprox.) e vinheta
    x = img * 1.15
    img = np.clip((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0, 1)
    vig = 1 - 0.35 * ss(0.35, 1.05, np.sqrt(((G["xx"] / W - 0.5) / 0.6) ** 2 + ((G["yy"] / H - 0.5) / 0.75) ** 2))
    img *= vig[..., None]
    img *= float(ss(0.0, 0.55, t))  # entrada do preto
    out = np.power(img, 1 / 2.2)
    rng = np.random.default_rng(1000 + f)
    grain = rng.standard_normal((H // 2, W // 2)).astype(np.float32)
    grain = cv2.resize(grain, (W, H), interpolation=cv2.INTER_LINEAR)
    out = out + grain[..., None] * 0.006
    return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)


def main():
    args = sys.argv[1:]
    if args and args[0] == "still":
        init()
        for tt in args[1:]:
            f = int(round(float(tt) * C.FPS))
            cv2.imwrite(os.path.join(C.BUILD, f"still_{float(tt):05.2f}.png"), frame(f))
        return
    out = args[0] if args else os.path.join(C.BUILD, f"video_{S}x.mp4")
    f0 = int(args[1]) if len(args) > 1 else 0
    f1 = int(args[2]) if len(args) > 2 else C.NFRAMES
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
           "-s", f"{W}x{H}", "-r", str(C.FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", os.environ.get("CRF", "16"),
           "-pix_fmt", "yuv420p", "-tune", "film", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(int(os.environ.get("JOBS", "4")), initializer=init) as pool:
        for i, img in enumerate(pool.imap(frame, range(f0, f1), chunksize=1)):
            p.stdin.write(img.tobytes())
            if i % 24 == 0:
                print(f"quadro {f0 + i}/{f1}", flush=True)
    p.stdin.close()
    p.wait()
    print("ok", out)


if __name__ == "__main__":
    main()
