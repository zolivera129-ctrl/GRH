# Splits movable limbs off their body labels (polygon ∩ owner ∩ skin-ish colors). Writes seg_l.npy/json.
import sys, os, json, numpy as np, cv2
work = sys.argv[1]
im = cv2.cvtColor(cv2.imread(os.path.join(work, 'orig.jpg')), cv2.COLOR_BGR2RGB).astype(np.int32)
seg = np.load(os.path.join(work, 'seg.npy')); names = json.load(open(os.path.join(work, 'seg.json')))
idx = {k: i for i, k in enumerate(names)}
R, G, B = im[..., 0], im[..., 1], im[..., 2]
skin = (R > 150) & (G > 75) & (G < 200) & (B < 135) & (R - B > 70)
tattoo = (abs(R - G) < 40) & (abs(G - B) < 40) & (R < 170) & (R > 60)  # grey ink on skin
LIMBS = {
  'F2v': dict(dono=['F2b', 'F2h'], poly=[(485,955),(522,950),(548,982),(568,1000),(572,1040),(590,1078),(602,1108),(642,1148),(644,1186),(612,1198),(584,1182),(560,1152),(544,1112),(528,1082),(503,1066),(484,1040),(476,1000)], cor='pele'),
  'F3m': dict(dono=['F3b'], poly=[(896,1100),(902,1162),(862,1186),(802,1202),(762,1232),(738,1266),(744,1302),(730,1334),(688,1338),(668,1300),(678,1258),(698,1232),(738,1202),(788,1168),(838,1132),(868,1104)], cor='pele'),
  'F1a': dict(dono=['F1b'], poly=[(198,1034),(232,1044),(268,1060),(292,1068),(320,1088),(347,1114),(354,1150),(347,1180),(318,1183),(298,1162),(280,1137),(262,1114),(230,1114),(196,1108)], cor='pele+tinta', relogio=(254, 1066, 298, 1110)),
  'M1a': dict(dono=['M1b'], poly=[(98,552),(152,552),(154,640),(147,700),(142,760),(152,800),(150,842),(131,862),(103,863),(90,832),(93,780),(90,700),(93,620)], cor='pele'),
  'M3a': dict(dono=['M3b'], poly=[(512,572),(568,566),(578,620),(573,700),(563,760),(553,804),(518,804),(510,742),(507,660)], cor='pele+tinta'),
}
for k, L in LIMBS.items():
    pm = np.zeros(seg.shape, np.uint8); cv2.fillPoly(pm, [np.array(L['poly'], np.int32)], 1)
    own = np.isin(seg, [idx[d] for d in L['dono']])
    col = skin | (tattoo if 'tinta' in L['cor'] else False)
    m = (pm > 0) & own & col
    if 'relogio' in L:
        x0, y0, x1, y1 = L['relogio']; box = np.zeros_like(m); box[y0:y1, x0:x1] = True
        m |= box & (pm > 0) & own
    # clean: close small holes (tattoo lines), keep largest component
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5))) & (pm > 0) & own
    n, cc, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8))
    if n > 1:
        j = 1 + np.argmax(st[1:, 4]); m = cc == j
    # take the anti-aliased rim with the limb, so the body keeps no skin-coloured outline
    m = (cv2.dilate(m.astype(np.uint8), np.ones((5, 5))) > 0) & (pm > 0) & own
    names.append(k); seg[m] = len(names) - 1
    print(k, int(m.sum()))
np.save(os.path.join(work, 'seg_l.npy'), seg); json.dump(names, open(os.path.join(work, 'seg_l.json'), 'w'))
