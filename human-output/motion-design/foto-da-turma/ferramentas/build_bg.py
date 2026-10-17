# Background plaid (full 9:16 canvas), frame (green, wavy window) and stars, at 2x.
import sys, os, json, numpy as np, cv2
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import gaussian_filter1d
work, out = sys.argv[1], sys.argv[2]
W1, H1, Z = 1055, 1491, 2
im = cv2.cvtColor(cv2.imread(os.path.join(work, 'orig.jpg')), cv2.COLOR_BGR2RGB).astype(np.float32)
seg = np.load(os.path.join(work, 'seg.npy'))
W2, H2 = W1 * Z, H1 * Z
# canvas for 9:16 at poster width: height = W2*16/9
CH = int(np.ceil(W2 * 16 / 9)) + 8
OY = (CH - H2) // 2          # poster top inside canvas
rng = np.random.RandomState(11)
# ---- plaid colors measured from the original
bgmask = (seg == 0) & (np.linalg.norm(im - [243, 110, 168], axis=2) < 40)
base = np.median(im[bgmask], axis=0)
vx = [20, 80, 141, 206, 262, 322, 395, 466, 525, 587, 661, 731, 790, 847, 910, 973, 1035]
hy_meas = [95, 149, 213, 269, 313, 625, 878, 1064, 1244, 1295, 1349, 1405]
# fill gaps with near-even spacing (~57)
hy = []
for a, b in zip(hy_meas[:-1], hy_meas[1:]):
    n = max(1, round((b - a) / 58)); hy += list(np.linspace(a, b, n + 1)[:-1])
hy.append(hy_meas[-1])
while hy[0] > -OY / Z - 60: hy.insert(0, hy[0] - 57)
while hy[-1] < (CH - OY) / Z + 60: hy.append(hy[-1] + 57)
# line color: sample on a measured line
lm = np.zeros_like(bgmask); 
for x in [395, 466, 525]: lm[90:170, x - 1:x + 2] = True
lc = np.median(im[lm & bgmask], axis=0)
amp = (lc - base)
print('base', base, 'line', lc)
yy = (np.arange(CH)[:, None] - OY) / Z; xx = np.arange(W2)[None, :] / Z
def lines(coord, pos, sig):
    v = np.zeros(np.broadcast_shapes(coord.shape), np.float32)
    for p in pos: v = np.maximum(v, np.exp(-0.5 * ((coord - p) / sig) ** 2))
    return v
LV = lines(np.broadcast_to(xx, (CH, W2)), vx, 2.3)
LH = lines(np.broadcast_to(yy, (CH, W2)), hy, 2.3)
L = np.clip(LV + LH, 0, 1.35)
# low-frequency mottling + fine grain
mot = cv2.GaussianBlur(rng.normal(0, 1, (CH // 8 + 1, W2 // 8 + 1)).astype(np.float32), (0, 0), 6)
mot = cv2.resize(mot, (W2, CH), interpolation=cv2.INTER_CUBIC); mot /= mot.std() + 1e-6
grain = rng.normal(0, 1, (CH, W2)).astype(np.float32)
bg = base[None, None] + L[..., None] * amp[None, None] * 1.05 + mot[..., None] * 1.6 + grain[..., None] * 2.0
cv2.imwrite(os.path.join(out, 'fundo.jpg'), cv2.cvtColor(np.clip(bg, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
# ---- window shape from traced edges, occlusions filled by left/right symmetry + smooth interpolation
E = json.load(open(os.path.join(work, 'edges.json')))
def side(arr, valid_range, cheio):
    a = np.array([[t, v, p] for t, v, p in arr], float)
    t, v, p = a[:, 0], a[:, 1], a[:, 2] > 0
    ext = (v == cheio)                     # whole row/column is frame: no window there
    ok = ((~p) & (v > valid_range[0]) & (v < valid_range[1])) | ext
    v = np.where(ext, 4000 if cheio > 0 else -2000, v)
    return t, v, ok
yL, vL, okL = side(E['L'], (5, 400), W1); yR, vR, okR = side(E['R'], (650, 1050), -1)
vRm = (W1 - 1) - vR
# combine: left edge estimate from left where ok, else mirrored right
comb = np.where(okL, vL, np.where(okR, np.where(vR <= -1000, 4000, vRm), np.nan))
okc = ~np.isnan(comb)
# only rows where the side edge is meaningful (between the top and bottom waves)
rows = np.arange(H1)
fL = PchipInterpolator(rows[okc], comb[okc])(rows)
fL = gaussian_filter1d(fL, 2)
xT, vT, okT = side(E['T'], (5, 400), H1); xB, vB, okB = side(E['B'], (1000, 1490), -1)
vBm = vB
fT = PchipInterpolator(xT[okT], vT[okT])(np.arange(W1)); fT = gaussian_filter1d(fT, 2)
fB = PchipInterpolator(xB[okB], vB[okB])(np.arange(W1)); fB = gaussian_filter1d(fB, 2)
# supersampled window mask on the 2x poster grid, embedded in the canvas
SS = 2
gy = (np.arange(CH * SS) + 0.5) / SS; gx = (np.arange(W2 * SS) + 0.5) / SS
py = (gy - OY) / Z; px = gx / Z
Lx = np.interp(py, rows, fL, left=1e9, right=1e9); Rx = (W1 - 1) - Lx
Ty = np.interp(px, np.arange(W1), fT); By = np.interp(px, np.arange(W1), fB)
win = (px[None, :] > Lx[:, None]) & (px[None, :] < Rx[:, None]) & (py[:, None] > Ty[None, :]) & (py[:, None] < By[None, :])
win &= (py[:, None] > 28) & (py[:, None] < 1466) & (px[None, :] > 4) & (px[None, :] < 1051)
win = cv2.resize(win.astype(np.float32), (W2, CH), interpolation=cv2.INTER_AREA)
# ---- frame: green with subtle texture, alpha = 1 - window
gm = (np.linalg.norm(im - [56, 109, 37], axis=2) < 30)
green = np.median(im[gm], axis=0)
mot2 = cv2.resize(cv2.GaussianBlur(rng.normal(0, 1, (CH // 8 + 1, W2 // 8 + 1)).astype(np.float32), (0, 0), 5), (W2, CH)); mot2 /= mot2.std() + 1e-6
fr = green[None, None] + mot2[..., None] * 1.4 + rng.normal(0, 1.6, (CH, W2, 1))
fa = 1 - win
rgba = np.dstack([np.clip(fr, 0, 255), fa * 255]).astype(np.uint8)
cv2.imwrite(os.path.join(out, 'moldura.png'), cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA), [cv2.IMWRITE_PNG_COMPRESSION, 9])
# ---- stars: unmix star color against green
sc = np.array([244, 163, 26], np.float32)
d = (im - green); u = sc - green
al = np.clip((d @ u) / (u @ u), 0, 1)
starm = (al > 0.5) & (seg == 0)
n, cc, st, cen = cv2.connectedComponentsWithStats(starm.astype(np.uint8))
stars = []
al2 = cv2.resize(al, (W2, H2), interpolation=cv2.INTER_CUBIC)
for j in range(1, n):
    if st[j, 4] < 150 or st[j, 2] > 120 or st[j, 3] > 120: continue
    if win[int(cen[j, 1] * Z + OY), int(cen[j, 0] * Z)] > 0.3: continue
    x, y, w, h = st[j, :4]; m = 8
    x0, y0, x1, y1 = max(0, x - m), max(0, y - m), min(W1, x + w + m), min(H1, y + h + m)
    a = np.clip(al2[y0 * Z:y1 * Z, x0 * Z:x1 * Z], 0, 1)
    # keep only this star's component (dilated)
    cm = cv2.dilate((cc[y0:y1, x0:x1] == j).astype(np.uint8), np.ones((5, 5)))
    a *= cv2.resize(cm.astype(np.float32), (a.shape[1], a.shape[0]), interpolation=cv2.INTER_LINEAR)
    col = np.ones(a.shape + (3,), np.float32) * sc
    col += rng.normal(0, 1.4, col.shape)
    img = np.dstack([np.clip(col, 0, 255), a * 255]).astype(np.uint8)
    nm = f'estrela-{len(stars):02d}.png'
    cv2.imwrite(os.path.join(out, nm), cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA))
    stars.append({'id': nm[:-4], 'x': int(x0 * Z), 'y': int(y0 * Z + OY), 'w': int(a.shape[1]), 'h': int(a.shape[0]), 'cx': float(cen[j, 0] * Z), 'cy': float(cen[j, 1] * Z + OY)})
json.dump({'largura': W2, 'altura': CH, 'posterTopo': OY, 'posterAltura': H2, 'estrelas': stars}, open(os.path.join(out, 'cenario.json'), 'w'), indent=1)
print('canvas', W2, CH, 'OY', OY, 'stars', len(stars))
