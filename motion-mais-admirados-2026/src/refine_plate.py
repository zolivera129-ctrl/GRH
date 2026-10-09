"""Refino do fundo (placa da aura): remove anomalias e deixa a luz consistente.
- fantasmas dos raios/silhueta removidos (textura diferente) -> denoise + limpeza no centro
- lâminas de luz com bordas duras (esquerda, canto inferior direito, risco do canto superior esquerdo) -> transições suaves
- costura vertical herdada do KV (x~500)
A granulação passa a ser só a do render (uniforme e animada)."""
import os as _os
BUILD = _os.environ.get('MOTION_BUILD', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'build')) + '/'
import numpy as np, cv2
A = BUILD + 'assets/'; W = BUILD + 'work/'
raw_path = A + 'plate_raw.npy'
if not _os.path.exists(raw_path): np.save(raw_path, np.load(A + 'plate.npy'))
plate = np.load(raw_path).astype(np.float32)
H, Wd = plate.shape[:2]
yy, xx = np.mgrid[0:H, 0:Wd].astype(np.float32)

# 1) denoise (remove baked static grain; keeps sub-8-bit smooth gradients)
p8 = (np.clip(plate, 0, 1) * 255 + 0.5).astype(np.uint8)
dn8 = cv2.fastNlMeansDenoisingColored(p8[..., ::-1], None, 7, 7, 7, 25)[..., ::-1].astype(np.float32) / 255.
plate = dn8 + cv2.GaussianBlur(plate - dn8, (0, 0), 3.0)

def dir_soft(img, ang_deg, k=151, sigma=38):
    ker = np.zeros((k, k), np.float32); c = k // 2; a = np.deg2rad(ang_deg)
    for i in range(-c, c + 1):
        ker[int(round(c + i * np.sin(a))), int(round(c + i * np.cos(a)))] = 1
    ker /= ker.sum()
    return cv2.GaussianBlur(cv2.filter2D(img, -1, ker, borderType=cv2.BORDER_REFLECT), (0, 0), sigma)
def poly_w(pts, feather, gain=1.25):
    m = np.zeros((H, Wd), np.float32); cv2.fillPoly(m, [np.array(pts, np.int32)], 1.0)
    return np.clip(cv2.GaussianBlur(m, (0, 0), feather) * gain, 0, 1)
def blend(img, soft, w): return img * (1 - w[..., None]) + soft * w[..., None]

# 2) left hard-edged light sheet -> soft falloff (full)
plate = blend(plate, dir_soft(plate, 26), poly_w([[300, 300], [430, 255], [700, 330], [900, 420], [930, 560], [880, 700], [560, 720], [300, 640], [250, 470]], 45))
# 3) bottom-right sheet: keep the glow, lose the razor edges and white streak lines
w_br = poly_w([[1080, 600], [1350, 640], [1760, 790], [1900, 900], [1900, 1080], [1300, 1080], [1120, 900]], 55, 1.1) * 0.85
plate = blend(plate, dir_soft(plate, 22, k=121, sigma=22), w_br)
# 4) top-left: soften the sharp diagonal highlight line along the beam edge
w_tl = poly_w([[250, 0], [380, 0], [640, 200], [600, 260], [430, 160]], 30, 1.0) * 0.75
plate = blend(plate, dir_soft(plate, 36, k=61, sigma=10), w_tl)
# 5) vertical seam inherited from the KV around x~497 (lower half)
seam = np.exp(-((xx - 497) / 70.0) ** 2) * np.clip((yy - 430) / 120.0, 0, 1)
hblur = cv2.GaussianBlur(plate, (0, 0), sigmaX=45, sigmaY=2)
plate = blend(plate, hblur, seam.astype(np.float32))
# 6) centre (behind the logo): erase residual footprints of removed rays / old silhouette
cx, cy = 970.5, 533.5
r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
w_c = np.clip((500 - r) / 120.0, 0, 1)
# keep the two lower-right lens streaks out of the smoothing
g = cv2.GaussianBlur(plate.mean(2), (0, 0), 1.5)
gm = np.sqrt(cv2.Sobel(g, cv2.CV_32F, 1, 0) ** 2 + cv2.Sobel(g, cv2.CV_32F, 0, 1) ** 2)
streak = cv2.GaussianBlur((gm > 0.06).astype(np.float32), (0, 0), 6)
w_c = w_c * (1 - np.clip(streak * 2, 0, 1)) * 0.9
plate = blend(plate, cv2.GaussianBlur(plate, (0, 0), 9), w_c.astype(np.float32))
plate = np.clip(plate, 0, 1).astype(np.float32)
np.save(A + 'plate.npy', plate)
cv2.imwrite(W + 'plate.png', (plate[..., ::-1] * 255 + 0.5).astype(np.uint8))
print('refined plate saved')
