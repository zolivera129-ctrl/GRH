"""Silhueta nova: forma exata do vetor (.ai) + cor/brilho do render oficial do card (sem textos por cima)."""
import os as _os
BUILD = _os.environ.get('MOTION_BUILD', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'build')) + '/'
import numpy as np, cv2, sys
from scipy.spatial import cKDTree
W = BUILD + 'work/'; A = BUILD + 'assets/'

# ---------------- vector contour (.ai) -> KV space
def bezier_contour(path_items, n=220):
    pts = []
    for p0, p1, p2, p3 in path_items:
        p0, p1, p2, p3 = map(np.array, (p0, p1, p2, p3))
        for t in np.linspace(0, 1, n, endpoint=False):
            pts.append((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3)
    return np.array(pts)
AI_PATH = [((786.7, 211.0), (781.5, 198.2), (792.8, 184.6), (806.4, 187.6)), ((806.4, 187.6), (826.8, 192.2), (856.2, 201.1), (892.1, 218.5)),
    ((892.1, 218.5), (910.2, 227.4), (926.6, 233.4), (939.5, 237.3)), ((939.5, 237.3), (958.8, 243.3), (974.1, 258.1), (980.7, 277.2)),
    ((980.7, 277.2), (989.1, 301.4), (999.6, 334.6), (1003.8, 360.4)), ((1003.8, 360.4), (1011.4, 406.5), (953.0, 439.3), (992.1, 503.6)),
    ((992.1, 503.6), (1031.1, 567.9), (1054.2, 604.8), (1023.3, 615.5)), ((1023.3, 615.5), (986.2, 628.4), (975.8, 608.5), (962.6, 669.7)),
    ((962.6, 669.7), (949.4, 730.8), (906.7, 786.9), (908.0, 849.3)), ((908.0, 849.3), (909.0, 902.7), (908.6, 921.4), (891.3, 935.1)),
    ((891.3, 935.1), (886.4, 939.0), (879.1, 936.6), (877.2, 930.6)), ((877.2, 930.6), (869.6, 907.0), (853.8, 846.2), (857.8, 756.4)),
    ((857.8, 756.4), (863.1, 638.9), (851.7, 604.6), (881.6, 601.3)), ((881.6, 601.3), (909.1, 598.2), (972.8, 581.9), (935.7, 547.7)),
    ((935.7, 547.7), (897.3, 512.3), (798.5, 437.1), (793.1, 351.9)), ((793.1, 351.9), (788.3, 275.7), (826.3, 307.5), (786.7, 211.0))]
AI2KV_S, AI2KV_T = 0.9044873, np.array([135.92863, 30.46312])   # fitted to the logo lockup in the KV
def ai2kv(P): return P * AI2KV_S + AI2KV_T
PK = ai2kv(bezier_contour(AI_PATH))

# ---------------- card render (official glass look of the new silhouette)
card = cv2.imread(W + 'card_glass.png')[..., ::-1].astype(np.float32) / 255.
mx = card.max(2)
seg = (cv2.GaussianBlur(mx, (0, 0), 1.5) > np.percentile(mx, 50) + 22 / 255.).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(seg)
i = 1 + np.argmax(st[1:, 4]); segm = (lab == i).astype(np.uint8)
segm = cv2.morphologyEx(segm, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
_do = cv2.distanceTransform(1 - segm, cv2.DIST_L2, 5)
bgc = np.median(card[(_do > 18) & (_do < 45)].reshape(-1, 3), 0)
print('card bg', bgc * 255)
cs, _ = cv2.findContours(segm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
PC = max(cs, key=cv2.contourArea)[:, 0, :].astype(np.float64)

# similarity (with rotation) card -> KV, ICP
def umeyama(X, Y):
    mx_, my_ = X.mean(0), Y.mean(0); Xc, Yc = X - mx_, Y - my_
    U, S, Vt = np.linalg.svd(Yc.T @ Xc / len(X))
    D = np.eye(2); D[1, 1] = np.sign(np.linalg.det(U @ Vt))
    R = U @ D @ Vt; s = np.trace(np.diag(S) @ D) / Xc.var(0).sum()
    return s, R, my_ - s * R @ mx_
s0 = np.ptp(PK[:, 1]) / np.ptp(PC[:, 1])
R = np.eye(2); s = s0; t = PK.min(0) - s * PC.min(0)
tree = cKDTree(PK)
for it in range(120):
    Q = (s * (R @ PC.T)).T + t
    d, idx = tree.query(Q)
    keep = d <= np.percentile(d, 100 if it < 20 else 65)
    s, R, t = umeyama(PC[keep], PK[idx[keep]])
Q = (s * (R @ PC.T)).T + t; d, idx = tree.query(Q); d = np.sort(d)[:int(len(d) * 0.65)]
print('card->KV: scale %.4f rot %.3f deg resid mean %.2f max %.2f' % (s, np.degrees(np.arctan2(R[1, 0], R[0, 0])), d.mean(), d.max()))

# prep card colours: interior known (eroded), flare & glint removed, push-pull extrapolate
known = cv2.erode(segm, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))).astype(bool)
# locate baked flare (brightest blob near top) and glint (bright blob lower-left)
lum = card.mean(2)
H_, W_ = lum.shape
yy, xx = np.mgrid[0:H_, 0:W_]
ys, xs = np.where(segm > 0); ytop, ybot = ys.min(), ys.max()
upper = (yy < ytop + 0.3 * (ybot - ytop)); lower = (yy > ytop + 0.55 * (ybot - ytop))
def brightest(region):
    l = np.where(region, cv2.GaussianBlur(lum, (0, 0), 3), -1); y, x = np.unravel_index(np.argmax(l), l.shape); return x, y
fx, fy = brightest(upper); gxp, gyp = brightest(lower & (xx < xs.mean()))
print('card flare', fx, fy, 'glint', gxp, gyp)
known &= ((xx - fx) ** 2 + (yy - fy) ** 2) > 34 ** 2
known &= (((xx - gxp) / 14.0) ** 2 + ((yy - gyp) / 40.0) ** 2) > 1
def pushpull(img, w, levels=9):
    if levels == 0 or min(img.shape[:2]) < 4:
        return np.broadcast_to((img * w[..., None]).sum((0, 1)) / max(w.sum(), 1e-6), img.shape).copy()
    h, ww = w.shape
    sw = cv2.resize(cv2.GaussianBlur(w, (0, 0), 1.0), (ww // 2, h // 2), interpolation=cv2.INTER_AREA)
    si = cv2.resize(cv2.GaussianBlur(img * w[..., None], (0, 0), 1.0), (ww // 2, h // 2), interpolation=cv2.INTER_AREA)
    low = pushpull(si / np.maximum(sw, 1e-6)[..., None], np.clip(sw * 4, 0, 1), levels - 1)
    return img * w[..., None] + cv2.resize(low, (ww, h), interpolation=cv2.INTER_LINEAR) * (1 - w[..., None])
colc = pushpull(cv2.GaussianBlur(card, (0, 0), 0.7), known.astype(np.float32))
colc = cv2.GaussianBlur(colc, (0, 0), 1.2) * (1 - known[..., None]) + colc * known[..., None]

# rim profile along card contour: brightness just inside the edge above interior colour
dist_c = cv2.distanceTransform(segm, cv2.DIST_L2, 5)
band = (dist_c > 0) & (dist_c < 3.2)
rim_raw = np.clip((card - colc).max(2), 0, 1) * band
rim_raw[~known & ~band] = 0
bys, bxs = np.where(band)
treeC = cKDTree(PC)
_, bi = treeC.query(np.c_[bxs, bys])
rim_c = np.zeros(len(PC)); cnt = np.zeros(len(PC))
np.maximum.at(rim_c, bi, rim_raw[bys, bxs])
# remove flare/glint influence & smooth along contour
near_f = np.hypot(PC[:, 0] - fx, PC[:, 1] - fy) < 40
near_g = np.hypot(PC[:, 0] - gxp, PC[:, 1] - gyp) < 46
rim_c[near_f | near_g] = np.nan
ok = ~np.isnan(rim_c); idxs = np.arange(len(PC))
rim_c = np.interp(idxs, idxs[ok], rim_c[ok], period=len(PC))
k = 9; ker = np.ones(k) / k
rim_c = np.convolve(np.r_[rim_c[-k:], rim_c, rim_c[:k]], ker, mode='same')[k:-k]
rim_c = np.clip(rim_c / max(np.percentile(rim_c, 97), 1e-3), 0, 1)

# ---------------- asset grid in KV space
S = 3
bx0, by0, bx1, by1 = 800, 170, 1100, 910
Wa, Ha = (bx1 - bx0) * S, (by1 - by0) * S
ss = 4
m = np.zeros((Ha * ss, Wa * ss), np.uint8)
cv2.fillPoly(m, [np.round((PK - [bx0, by0]) * S * ss).astype(np.int32)], 255)
mask = cv2.resize(m.astype(np.float32) / 255., (Wa, Ha), interpolation=cv2.INTER_AREA)
# KV coords of asset pixels -> card coords
ay, ax = np.mgrid[0:Ha, 0:Wa].astype(np.float64)
kx = bx0 + (ax + 0.5) / S; ky = by0 + (ay + 0.5) / S
Ri = R.T
cx_ = (Ri[0, 0] * (kx - t[0]) + Ri[0, 1] * (ky - t[1])) / s
cy_ = (Ri[1, 0] * (kx - t[0]) + Ri[1, 1] * (ky - t[1])) / s
col = cv2.remap(colc, (cx_ - 0.5).astype(np.float32), (cy_ - 0.5).astype(np.float32), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
col = np.clip(col, 0, 1)
dist = cv2.distanceTransform((mask > 0.5).astype(np.uint8), cv2.DIST_L2, 5).astype(np.float32)
h = np.sqrt(np.clip(dist / (S * 14.0), 0, 1)); h = cv2.GaussianBlur(h, (0, 0), 3)
gx = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3)
# rim strength map from card rim profile (nearest contour point)
PCk = (s * (R @ PC.T)).T + t
treeK = cKDTree(PCk)
edge = dist < 8 * S
ey, ex = np.where(edge)
_, ei = treeK.query(np.c_[bx0 + (ex + 0.5) / S, by0 + (ey + 0.5) / S])
rim = np.zeros((Ha, Wa), np.float32); rim[ey, ex] = rim_c[ei]
flare_kv = s * (R @ np.array([fx, fy])) + t; glint_kv = s * (R @ np.array([gxp, gyp])) + t
print('flare KV', flare_kv, 'glint KV', glint_kv)
np.savez_compressed(A + 'silhouette_v2.npz', mask=mask.astype(np.float32), col=col.astype(np.float32), dist=dist, gx=gx, gy=gy,
                    rim=rim, box=np.array([bx0, by0, bx1, by1]), S=S, contour=PK, flare=flare_kv, glint=glint_kv,
                    card_bg=bgc.astype(np.float32))
# preview
pv = (np.clip(col * mask[..., None] + (1 - mask[..., None]) * bgc, 0, 1) * 255).astype(np.uint8)[..., ::-1]
cv2.imwrite(W + 'sil_v2_preview.png', cv2.resize(pv, None, fx=1 / S * 1.5, fy=1 / S * 1.5, interpolation=cv2.INTER_AREA))
cv2.imwrite(W + 'sil_v2_rim.png', (np.clip(rim * (mask > 0.01), 0, 1) * 255).astype(np.uint8)[::3, ::3])
