# Builds person layers (with hidden-part completion), background plaid, frame and stars at 2x.
import sys, os, json, numpy as np, cv2
from scipy.interpolate import PchipInterpolator
W1, H1 = 1055, 1491
Z = 2
work, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
im = cv2.cvtColor(cv2.imread(os.path.join(work, 'orig.jpg')), cv2.COLOR_BGR2RGB)
seg = np.load(os.path.join(work, 'seg_l.npy')); names = json.load(open(os.path.join(work, 'seg_l.json')))
idx = {k: i for i, k in enumerate(names)}
sys.path.insert(0, os.path.dirname(__file__)); from seeds import SEEDS
labim = cv2.cvtColor(cv2.GaussianBlur(im, (0, 0), 1.0), cv2.COLOR_RGB2LAB).astype(np.float32)
ORDER = ['B1b','B2b','B3b','B4b','B5b','B4a','B1h','B2h','B3h','B4h','B5h',
         'M5b','M5h','M4b','M4h','M2b','M2h','M1b','M1a','M1h','M3b','M3a','M3h','M6b','M6h',
         'F1b','F1a','F3b','F3m','F2b','F1h','F3h','F2h','F2v','F1m']
LIMBS = {'B4a', 'F1m', 'F2v', 'F3m', 'F1a', 'M1a', 'M3a'}
def params(k):
    if k in LIMBS: return dict(R=10, D=0)
    row, part = k[0], k[2]
    if part == 'h': return dict(R={'B': 30, 'M': 45, 'F': 26}[row], D=0)
    return dict(R={'B': 120, 'M': 95, 'F': 72}[row], D={'B': 650, 'M': 320, 'F': 0}[row])
orig2 = cv2.resize(im, (W1 * Z, H1 * Z), interpolation=cv2.INTER_LANCZOS4)
rng = np.random.RandomState(7)
grain1 = rng.normal(0, 1, (H1 * Z, W1 * Z, 1)).astype(np.float32)
meta = {'escala': Z, 'largura': W1 * Z, 'altura': H1 * Z, 'camadas': []}
masks = {k: (seg == idx[k]) for k in ORDER}
above = np.zeros((H1, W1), bool)
front = {}
for k in reversed(ORDER):
    front[k] = above.copy(); above |= masks[k]
for k in ORDER:
    M0 = masks[k].astype(np.uint8); p = params(k)
    # the rim touching layers in front keeps their anti-aliased fringe: treat it as hidden too
    band = (M0 > 0) & (cv2.dilate(front[k].astype(np.uint8), np.ones((5, 5))) > 0)
    M = ((M0 > 0) & ~band).astype(np.uint8)
    if M.sum() < 50: M = M0
    pts = cv2.findNonZero(M)
    hull_src = M.copy()
    if p['D'] > 0:
        sh = np.zeros_like(M); sh[p['D']:] = M[:-p['D']]; hull_src = hull_src | sh
        # also extrude in steps so the hull is a solid sweep
        for d in range(40, p['D'], 40):
            s2 = np.zeros_like(M); s2[d:] = M[:-d]; hull_src |= s2
    hull = np.zeros_like(M)
    cv2.fillPoly(hull, [cv2.convexHull(cv2.findNonZero(hull_src))], 1)
    if k[-1] == 'h': hull = cv2.dilate(hull, np.ones((7, 7)))
    dist = cv2.distanceTransform(1 - M, cv2.DIST_L2, 5)
    zone = ((dist <= p['R']) & front[k] & (hull > 0)) | (band & (M0 > 0) & (M != M0))
    # keep only zone components touching the mask
    n, cc = cv2.connectedComponents((zone | (M > 0)).astype(np.uint8))
    keep = np.unique(cc[M > 0]); zone &= np.isin(cc, keep)
    src = cv2.erode(M, np.ones((5, 5))) if M.sum() > 400 else M
    if src.sum() < 20: src = M
    # completion sources only from this layer's own palette (sampled at its seeds)
    pal = []
    for s in SEEDS.get(k, []):
        for (sx, sy) in (s if isinstance(s, list) else [s]):
            if seg[sy, sx] == idx[k]: pal.append(labim[max(0,sy-2):sy+3, max(0,sx-2):sx+3].reshape(-1, 3).mean(0))
    pal = np.array(pal, np.float32) if pal else None
    ys_, xs_ = np.where(src > 0)
    d = np.zeros(len(ys_)) if pal is None else np.min(np.linalg.norm(labim[ys_, xs_][:, None, :] - pal[None], axis=2), axis=1)
    ok = d < 22
    src2 = np.zeros_like(src); src2[ys_[ok], xs_[ok]] = 1
    if src2.sum() > 50: src = src2
    _, lab = cv2.distanceTransformWithLabels(1 - src, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    ys, xs = np.where(src > 0)
    lut = np.zeros((lab.max() + 1, 3), np.float32)
    lut[lab[ys, xs]] = im[ys, xs]
    fill = lut[lab]
    # normalized blur inside zone to soften voronoi streaks
    wz = (zone | (src > 0)).astype(np.float32)
    bl = cv2.GaussianBlur(fill * wz[..., None], (0, 0), 2.2) / np.maximum(cv2.GaussianBlur(wz, (0, 0), 2.2), 1e-3)[..., None]
    comp = np.where(zone[..., None], bl, im.astype(np.float32))
    if k in ('F2b', 'F3b'):
        # patterned shirts: continue the stripes into the hidden area by copying along them
        I = im.astype(np.int32)
        if k == 'F2b':
            shirt = (src > 0) & (I[..., 0] > 190) & (I[..., 2] > 115) & (I[..., 0] - I[..., 1] > 45)
        else:
            shirt = (src > 0) & (I[..., 0] > 170) & (I[..., 1] < 130)
        # stripe direction: the shift along which the shirt repeats itself best
        gm = im.astype(np.float32).mean(2)
        best = None
        for adeg in range(-60, 61, 2):
            a = np.radians(adeg); dx, dy = np.sin(a) * 7, np.cos(a) * 7
            M2 = np.float32([[1, 0, dx], [0, 1, dy]])
            sh = cv2.warpAffine(gm, M2, (W1, H1)); ms = cv2.warpAffine(shirt.astype(np.uint8), M2, (W1, H1)) > 0
            both = shirt & ms
            if both.sum() < 500: continue
            e = np.abs(sh - gm)[both].mean()
            if best is None or e < best[0]: best = (e, a)
        th = best[1]
        d = np.array([np.sin(th), np.cos(th)])              # along the stripes
        nearest_is_shirt = shirt.reshape(-1)[lab.reshape(-1)].reshape(lab.shape) if False else None
        zy, zx = np.where(zone)
        # which source pixel is nearest: use the label image to look up its coords
        src_y = np.zeros(lab.max() + 1, np.int32); src_x = np.zeros(lab.max() + 1, np.int32)
        sy_, sx_ = np.where(src > 0); src_y[lab[sy_, sx_]] = sy_; src_x[lab[sy_, sx_]] = sx_
        ny_, nx_ = src_y[lab[zy, zx]], src_x[lab[zy, zx]]
        want = shirt[ny_, nx_] if k == 'F3b' else (I[ny_, nx_, 2] > 112) & (I[ny_, nx_].sum(1) > 300)
        zy, zx = zy[want], zx[want]
        fillc = np.full((len(zy), 3), np.nan, np.float32)
        for sgn in (1, -1):
            todo = np.isnan(fillc[:, 0])
            for s in range(1, 260):
                if not todo.any(): break
                qy = np.round(zy[todo] + sgn * s * d[1]).astype(int); qx = np.round(zx[todo] + sgn * s * d[0]).astype(int)
                ok = (qy >= 0) & (qy < H1) & (qx >= 0) & (qx < W1)
                hit = np.zeros(todo.sum(), bool); hit[ok] = shirt[qy[ok], qx[ok]]
                idxs = np.where(todo)[0][hit]
                fillc[idxs] = im[qy[hit], qx[hit]]
                todo[idxs] = False
        good = ~np.isnan(fillc[:, 0])
        comp[zy[good], zx[good]] = fillc[good]
        print('  stripes', k, round(float(np.degrees(th)), 1), round(float(best[0]), 2), int(good.sum()), '/', len(zy))
    alpha1 = ((M > 0) | zone).astype(np.float32)
    # soft fade at the far end of the zone
    fade = np.clip((p['R'] - dist) / 8.0, 0, 1)
    alpha1 = np.where(zone, np.minimum(alpha1, np.maximum(fade, 0)), alpha1)
    ys, xs = np.where(alpha1 > 0)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    x0, y0 = max(0, x0 - 2), max(0, y0 - 2); x1, y1 = min(W1, x1 + 2), min(H1, y1 + 2)
    X0, Y0, X1, Y1 = x0 * Z, y0 * Z, x1 * Z, y1 * Z
    comp2 = cv2.resize(comp[y0:y1, x0:x1], ((x1 - x0) * Z, (y1 - y0) * Z), interpolation=cv2.INTER_CUBIC)
    vis2 = cv2.resize(M[y0:y1, x0:x1].astype(np.float32), ((x1 - x0) * Z, (y1 - y0) * Z), interpolation=cv2.INTER_LINEAR)
    zone2 = cv2.resize(zone[y0:y1, x0:x1].astype(np.float32), ((x1 - x0) * Z, (y1 - y0) * Z), interpolation=cv2.INTER_LINEAR)
    col = np.where(vis2[..., None] > 0.5, orig2[Y0:Y1, X0:X1].astype(np.float32), comp2 + grain1[Y0:Y1, X0:X1] * 2.2 * (zone2[..., None] > 0.5))
    a2 = cv2.resize(alpha1[y0:y1, x0:x1], ((x1 - x0) * Z, (y1 - y0) * Z), interpolation=cv2.INTER_LINEAR)
    # frame-green fringe near the poster edges does not belong to the person
    g = col[..., 1] - np.maximum(col[..., 0], col[..., 2])
    xs2 = np.arange(X0, X1)[None, :] / Z
    nearedge = (xs2 < 160) | (xs2 > 895)
    a2 = np.where((g > 12) & nearedge & (vis2 > 0), a2 * np.clip(1 - (g - 12) / 10, 0, 1), a2)
    rgba = np.dstack([np.clip(col, 0, 255), np.clip(a2 * 255, 0, 255)]).astype(np.uint8)
    cv2.imwrite(os.path.join(out, f'{k}.png'), cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA), [cv2.IMWRITE_PNG_COMPRESSION, 9])
    meta['camadas'].append({'id': k, 'x': int(X0), 'y': int(Y0), 'w': int(X1 - X0), 'h': int(Y1 - Y0)})
    print(k, X0, Y0, X1 - X0, Y1 - Y0, int(zone.sum()))
json.dump(meta, open(os.path.join(out, 'camadas.json'), 'w'), indent=1)
