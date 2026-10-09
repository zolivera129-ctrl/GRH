"""Suaviza a 'lâmina' de luz com bordas duras do lado esquerdo da aura (degrau escuro + risco branco do KV)."""
import os as _os
BUILD = _os.environ.get('MOTION_BUILD', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'build')) + '/'
import numpy as np, cv2
A = BUILD + 'assets/'; W = BUILD + 'work/'
plate = np.load(A + 'plate_raw.npy') if _os.path.exists(A + 'plate_raw.npy') else np.load(A + 'plate.npy')
np.save(A + 'plate_raw.npy', plate)
H, Wd = plate.shape[:2]
# region covering the hard-edged light sheet left of the logo
poly = np.array([[300, 300], [430, 255], [700, 330], [900, 420], [930, 560], [880, 700], [560, 720], [300, 640], [250, 470]], np.int32)
m = np.zeros((H, Wd), np.float32); cv2.fillPoly(m, [poly], 1.0)
w = cv2.GaussianBlur(m, (0, 0), 45)
w = np.clip(w * 1.25, 0, 1)
# smooth field: directional blur along the beam + strong isotropic blur
k = 151; ker = np.zeros((k, k), np.float32); ang = np.deg2rad(26)
c = k // 2
for i in range(-c, c + 1):
    x = int(round(c + i * np.cos(ang))); y = int(round(c + i * np.sin(ang)))
    ker[y, x] = 1
ker /= ker.sum()
soft = cv2.filter2D(plate, -1, ker, borderType=cv2.BORDER_REFLECT)
soft = cv2.GaussianBlur(soft, (0, 0), 38)
out = plate * (1 - w[..., None]) + soft * w[..., None]
# matching grain where softened
rng = np.random.default_rng(5)
n = cv2.GaussianBlur(rng.normal(0, 1, (H, Wd)).astype(np.float32), (0, 0), 0.6) * 1.6
lum = out.mean(2, keepdims=True)
out = out + (n[..., None] * (0.006 + 0.03 * lum)) * w[..., None]
out = np.clip(out, 0, 1).astype(np.float32)
np.save(A + 'plate.npy', out)
cv2.imwrite(W + 'plate.png', (out[..., ::-1] * 255).astype(np.uint8))
print('ok')
