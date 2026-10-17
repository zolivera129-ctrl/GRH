import sys, os, json, numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
from seeds import SEEDS
from skimage.segmentation import watershed
im = cv2.cvtColor(cv2.imread(sys.argv[1]), cv2.COLOR_BGR2RGB)
H, W = im.shape[:2]
names = ['bg'] + list(SEEDS.keys())
mk = np.zeros((H, W), np.int32)
f = im.astype(np.float32)
def near(c, d): return np.linalg.norm(f - np.array(c, np.float32), axis=2) < d
pinks = near((243,110,168), 22) | near((248,135,185), 18) | near((240,100,160), 18)
green = near((56,109,37), 35)
star = near((244,163,26), 40) & (cv2.dilate(green.astype(np.uint8), np.ones((31,31))) > 0)
bg = (pinks | green | star).astype(np.uint8)
bg = cv2.erode(bg, np.ones((9,9)))
mk[bg > 0] = 1
for i, (k, lst) in enumerate(SEEDS.items()):
    lab = i + 2
    for s in lst:
        if isinstance(s, list):
            cv2.polylines(mk_u := mk.view(np.int32), [np.array(s, np.int32)], False, int(lab), 5)
        else:
            cv2.circle(mk, s, 4, int(lab), -1)
sm = cv2.bilateralFilter(im, 7, 30, 5)
lab_im = cv2.cvtColor(sm, cv2.COLOR_RGB2LAB).astype(np.float32)
g = np.zeros((H, W), np.float32)
for c in range(3):
    gx = cv2.Sobel(lab_im[..., c], cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(lab_im[..., c], cv2.CV_32F, 0, 1, ksize=3)
    g = np.maximum(g, np.hypot(gx, gy))
seg = watershed(g, mk)
np.save(sys.argv[2], seg - 1)  # -1... bg=0
json.dump(names, open(sys.argv[2].replace('.npy', '.json'), 'w'))
# overlay
rng = np.random.RandomState(3)
cols = rng.randint(40, 255, (len(names) + 2, 3)); cols[1] = (0, 0, 0)
ov = (im * 0.45 + cols[seg] * 0.55).astype(np.uint8)
edges = cv2.Canny((seg * 7 % 255).astype(np.uint8), 1, 1) > 0
ov[edges] = (255, 255, 255)
for i, k in enumerate(names[1:]):
    ys, xs = np.where(seg == i + 2)
    if len(xs): cv2.putText(ov, k, (int(np.median(xs)) - 12, int(np.median(ys))), 0, 0.45, (255, 255, 255), 2); cv2.putText(ov, k, (int(np.median(xs)) - 12, int(np.median(ys))), 0, 0.45, (0, 0, 0), 1)
cv2.imwrite(sys.argv[3], cv2.cvtColor(ov, cv2.COLOR_RGB2BGR))
