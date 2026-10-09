"""Mais Admirados 2026 - logo reveal motion renderer (frame-by-frame compositor)."""
import os as _os
BUILD = _os.environ.get('MOTION_BUILD', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'build')) + '/'
import numpy as np, cv2, pickle, math, sys
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import rays

BASE = BUILD
A = BASE + 'assets/'
W, H = 1920, 1080
FPS = 30
PIVOT = np.array([970.5, 533.5])          # KV-space pivot (ray burst centre)
SIL_AXIS_X = 955.0                        # silhouette spin axis (KV x)
SIL_MID_Y = 540.0

# ----------------------------------------------------------------- easing helpers
def clamp01(x): return min(1.0, max(0.0, x))
def lin(t, a, b): return clamp01((t - a) / (b - a)) if b != a else float(t >= b)
def smooth(x): x = clamp01(x); return x * x * (3 - 2 * x)
def ease_out_expo(x): x = clamp01(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def ease_out_cubic(x): x = clamp01(x); return 1 - (1 - x) ** 3
def ease_in_out_cubic(x):
    x = clamp01(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def ease_in_out_sine(x): x = clamp01(x); return -(math.cos(math.pi * x) - 1) / 2
def ease_out_back(x, s=1.4):
    x = clamp01(x); return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2
def mix(a, b, t): return a + (b - a) * t

# ----------------------------------------------------------------- timeline (seconds)
BEAT = 0.5557
T_DROP = 13.36
T = dict(
    burst=1.14, burst_end=2.25, slow_end=4.47,
    rays_in=4.30, sil_in=4.75, sil_full=6.30,
    sweep0=6.55, sweep_end=12.25,
    spin_wind=12.20, spin_go=12.62, spin_stop=T_DROP,
    zoom0=T_DROP, zoom1=T_DROP + 1.75,
    text0=T_DROP + 0.45,
    grh0=T_DROP + 7 * BEAT, grh1=T_DROP + 7 * BEAT + 1.2,
    fade_out0=21.15, end=22.50,
)
DURATION = T['end']
Z_CLOSE = 1.36

# ----------------------------------------------------------------- assets
class Assets:
    def __init__(self):
        self.plate = np.load(A + 'plate.npy')
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        rn = np.sqrt(((xx - 965) / 1000.0) ** 2 + ((yy - 540) / 720.0) ** 2)
        tt = np.clip(rn / 1.25, 0, 1)[..., None]
        tt = tt * tt * (3 - 2 * tt)
        c0 = np.array([0.060, 0.092, 0.150], np.float32); c1 = np.array([0.018, 0.022, 0.034], np.float32)
        self.dark = (c0 * (1 - tt) + c1 * tt).astype(np.float32)
        self.light = (self.plate - self.dark).astype(np.float32)
        self.xx, self.yy = xx, yy
        s = np.load(A + 'silhouette_2x.npz')
        self.s_mask = s['mask']; self.s_col = s['col'][..., ::-1].copy(); self.s_dist = s['dist']
        self.s_gx = s['gx']; self.s_gy = s['gy']; self.s_box = s['box']; self.s_S = int(s['S'])
        self.contour = s['contour']
        # glass colour adjusted for transparency so that composite over plate matches KV
        bx0, by0, bx1, by1 = self.s_box
        bgp = cv2.resize(cv2.GaussianBlur(self.plate, (0, 0), 6)[by0:by1, bx0:bx1],
                         (self.s_mask.shape[1], self.s_mask.shape[0]), interpolation=cv2.INTER_LINEAR)
        self.glass_a = 0.62
        adj = (self.s_col - (1 - self.glass_a) * bgp) / self.glass_a
        self.s_coladj = np.clip(adj, 0, 1.2).astype(np.float32)
        # outward normal from distance field (asset space)
        d = cv2.GaussianBlur(self.s_dist, (0, 0), 2.0)
        nx = -cv2.Sobel(d, cv2.CV_32F, 1, 0, ksize=3); ny = -cv2.Sobel(d, cv2.CV_32F, 0, 1, ksize=3)
        nn = np.sqrt(nx * nx + ny * ny) + 1e-6
        self.s_nx = nx / nn; self.s_ny = ny / nn
        # top-edge profile for light path
        P = self.contour
        xs = np.arange(840, 1030, 1.0); ys = []
        for x in xs:
            sel = np.abs(P[:, 0] - x) < 1.2
            ys.append(P[sel, 1].min() if sel.any() else np.nan)
        ys = np.array(ys); ok = ~np.isnan(ys)
        self.top_x = xs[ok]; self.top_y = ys[ok]
        self.glyphs = pickle.load(open(A + 'text_glyphs.pkl', 'rb'))
        self.grh = np.load(A + 'grh_logo_alpha_x8.npy')
        self.grh_meta = np.load(A + 'grh_logo_meta.npy', allow_pickle=True).item()
        rng = np.random.default_rng(11)
        # particles for the aura burst
        n = 340
        lobe = rng.random(n)
        ang = np.where(lobe < 0.36, np.deg2rad(212) + rng.normal(0, 0.30, n),
              np.where(lobe < 0.72, np.deg2rad(28) + rng.normal(0, 0.30, n), rng.uniform(0, 2 * np.pi, n)))
        self.p_ang = ang
        self.p_r0 = rng.uniform(5, 60, n)
        self.p_v = rng.lognormal(0, 0.45, n) * 900.0      # px per "warped second"
        self.p_len = rng.uniform(0.6, 1.4, n)
        self.p_hue = rng.random(n)
        self.p_int = rng.uniform(0.25, 1.0, n)
        self.p_w = rng.choice([1, 1, 1, 2], n)
        # floating dust (slow-motion feel)
        m = 140
        self.d_xy = np.c_[rng.uniform(0, W, m), rng.uniform(0, H, m)]
        self.d_v = rng.normal(0, 1, (m, 2)) * np.array([14, 8])
        self.d_size = rng.uniform(0.8, 2.6, m)
        self.d_int = rng.uniform(0.15, 0.6, m)
        self.d_ph = rng.uniform(0, 2 * np.pi, m)
        # angular noise for the reveal edge
        self.ang_noise = [(rng.uniform(0.3, 1.0), int(f), rng.uniform(0, 2 * np.pi)) for f in [3, 5, 7, 11, 17, 23, 31, 43]]
        self.grain_rng = np.random.default_rng(3)

AS = None
def assets():
    global AS
    if AS is None: AS = Assets()
    return AS

# ----------------------------------------------------------------- camera
def camera(t):
    """Returns (z_logo, centre_screen) for the logo layer and z for the background plate."""
    if t < T['zoom0']:
        # close framing, very slow push while waiting
        z = Z_CLOSE + 0.035 * smooth(lin(t, T['rays_in'], T['zoom0']))
    else:
        u = lin(t, T['zoom0'], T['zoom1'])
        e = 1 - (1 - u) ** 4
        z = mix(Z_CLOSE + 0.035, 1.0, e)
        # afterwards a gentle drift-in during hold
        z += 0.022 * smooth(lin(t, T['zoom1'], T['end']))
    cx = 970.5 - 6.0 * (z - 1.0)   # keep composition centred
    cy = 533.5 + 4.0 * (z - 1.0)
    zb = 1.0 + (z - 1.0) * 0.30
    return z, np.array([cx, cy]), zb

# ----------------------------------------------------------------- background (dark + aura)
def angular_noise(th):
    a = assets(); n = np.zeros_like(th)
    for amp, f, ph in a.ang_noise: n += amp * np.sin(f * th + ph)
    return n / sum(x[0] for x in a.ang_noise)

def aura_state(t):
    """scale of light layer, reveal radius (plate space), intensity multiplier, core glow."""
    tb, te = T['burst'], T['burst_end']
    if t < tb:
        u = lin(t, 0.15, tb)
        return dict(scale=0.82, R=0.0, gain=0.0, core=0.35 * smooth(u) ** 2 + 0.05 * smooth(u), front=0.0)
    if t < te:
        u = (t - tb) / (te - tb)
        R = mix(30, 1500, 1 - (1 - u) ** 4)
        scale = mix(0.82, 1.0, ease_out_cubic(u))
        gain = smooth(lin(u, 0, 0.25)) * (1 + 0.40 * math.exp(-((u - 0.22) / 0.16) ** 2))
        core = 0.3 * math.exp(-u * 3.0) + 0.55 * math.exp(-((u - 0.05) / 0.08) ** 2)
        return dict(scale=scale, R=R, gain=gain, core=core, front=1.0 - smooth(lin(u, 0.35, 1.0)), nblur=9, zblur=0.16 * (1 - ease_out_cubic(u)))
    u = t - te
    scale = 1.0 + 0.030 * (1 - math.exp(-u / 2.5)) + 0.004 * u
    R = 1500 + 500 * (1 - math.exp(-u / 0.9))
    return dict(scale=scale, R=R, gain=1.0 + 0.045 * math.sin(u * 1.1) * math.exp(-u / 6.0), core=0.06 * math.exp(-u / 1.5), front=0.0)

def warp_time(t):
    """Particle time: very fast in the burst, then slows to a crawl (slow-motion)."""
    tb = T['burst']
    if t < tb: return 0.0
    u = t - tb
    fast = 1.10
    if u < fast:
        return u
    # exponential slow-down: speed decays to ~3%
    k = 0.32
    return fast + k * (1 - math.exp(-(u - fast) / k)) + 0.06 * (u - fast)

def render_background(t, zb, cam_c):
    a = assets()
    st = aura_state(t)
    out = a.dark.copy()
    s = st['scale'] * zb
    # light layer warped around aura centre (PIVOT maps to cam_c offset)
    c_src = PIVOT
    c_dst = np.array([960.0, 540.0]) + (PIVOT - [960.0, 540.0]) * 1.0 + (cam_c - PIVOT) * 0.30
    M = np.array([[s, 0, c_dst[0] - s * c_src[0]], [0, s, c_dst[1] - s * c_src[1]]], np.float32)
    if st['gain'] > 0:
        nb = st.get('nblur', 1)
        li = None
        for kb in range(nb):
            sk = s * (1 + st.get('zblur', 0.0) * kb / max(1, nb - 1))
            Mk = np.array([[sk, 0, c_dst[0] - sk * c_src[0]], [0, sk, c_dst[1] - sk * c_src[1]]], np.float32)
            w_ = cv2.warpAffine(a.light, Mk, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            li = w_ if li is None else li + w_
        li = li / nb
        if st['R'] - (0.3 * st['R'] + 40) < 1400:
            dx = a.xx - c_dst[0]; dy = a.yy - c_dst[1]
            r = np.sqrt(dx * dx + dy * dy) / s
            th = np.arctan2(dy, dx)
            reff = r * (1 + 0.22 * angular_noise(th))
            R = st['R']; fe = 0.30 * R + 40
            m = np.clip((R - reff) / fe, 0, 1)
            m = m * m * (3 - 2 * m)
            front = st['front'] * np.exp(-((reff - R * 0.92) / (0.18 * R + 20)) ** 2)
            li = li * m[..., None] + np.maximum(li, 0) * front[..., None] * 0.9
        out = out + li * st['gain']
    if st['core'] > 0.001:
        dx = a.xx - c_dst[0]; dy = a.yy - c_dst[1]
        r2 = dx * dx + dy * dy
        core = st['core'] * (np.exp(-r2 / (2 * 22.0 ** 2)) + 0.35 * np.exp(-r2 / (2 * 120.0 ** 2)) + 0.12 * np.exp(-r2 / (2 * 380.0 ** 2)))
        out = out + core[..., None] * np.array([0.85, 0.92, 1.0], np.float32)
    return out, c_dst

def render_particles(t, c_dst, glow):
    a = assets()
    if t < T['burst'] - 0.05: return
    tw = warp_time(t); tw0 = warp_time(t - 0.075)
    life = 1.0 - smooth(lin(t, T['slow_end'] - 0.6, T['slow_end'] + 0.9))
    if life <= 0.01: return
    acc_g = np.zeros((H, W), np.uint8); acc_c = np.zeros((H, W), np.uint8)
    for i in range(len(a.p_ang)):
        r1 = a.p_r0[i] + a.p_v[i] * tw
        r0 = a.p_r0[i] + a.p_v[i] * tw0 - 6
        r0 = min(r0, r1 - 1.5)
        if r0 > 1500: continue
        ca, sa = math.cos(a.p_ang[i]), math.sin(a.p_ang[i])
        fade_r = clamp01(1 - r1 / 1300.0) ** 0.7 * (0.25 + 0.75 * smooth(r1 / 220.0))
        inten = a.p_int[i] * fade_r * life
        if inten < 0.02: continue
        p0 = (int((c_dst[0] + ca * r0) * 4), int((c_dst[1] + sa * r0) * 4))
        p1 = (int((c_dst[0] + ca * r1) * 4), int((c_dst[1] + sa * r1) * 4))
        v = int(255 * min(1.0, inten))
        tgt = acc_g if a.p_hue[i] < 0.62 else acc_c
        cv2.line(tgt, p0, p1, v, int(a.p_w[i]), cv2.LINE_AA, shift=2)
    g = acc_g.astype(np.float32) / 255.; c = acc_c.astype(np.float32) / 255.
    col = g[..., None] * np.array([1.0, 0.86, 0.45], np.float32) + c[..., None] * np.array([0.65, 0.88, 1.0], np.float32)
    glow += col * 0.6

def render_dust(t, out, zb):
    a = assets()
    vis = smooth(lin(t, T['burst'] + 0.6, T['burst_end'] + 0.5)) * (1 - 0.5 * smooth(lin(t, T['fade_out0'], T['end'])))
    if vis <= 0: return
    tt = max(0.0, t - T['burst'])
    pos = a.d_xy + a.d_v * tt
    pos[:, 0] %= W; pos[:, 1] %= H
    buf = np.zeros((H, W), np.uint8)
    for i in range(len(pos)):
        tw = 0.6 + 0.4 * math.sin(tt * 1.7 + a.d_ph[i])
        v = int(255 * a.d_int[i] * tw * vis)
        cv2.circle(buf, (int(pos[i, 0] * 4), int(pos[i, 1] * 4)), int(a.d_size[i] * 4 * zb), v, -1, cv2.LINE_AA, shift=2)
    b = cv2.GaussianBlur(buf.astype(np.float32) / 255., (0, 0), 1.2)
    out += b[..., None] * np.array([0.95, 0.88, 0.62], np.float32) * 0.55

# ----------------------------------------------------------------- rays
def ray_growth(t):
    """per-ray growth fraction during the arrival; clockwise sweep from the top-left beam."""
    g = np.ones(rays.N)
    t0 = T['rays_in']
    if t >= t0 + 2.2: return g
    k = np.arange(rays.N)
    ang = (np.rad2deg(rays.ARR['th']) - 225.0) % 360.0
    delay = ang / 360.0 * 1.15
    u = np.clip((t - t0 - delay) / 0.75, 0, 1)
    return 1 - (1 - u) ** 3

def render_rays(t, z, c):
    if t < T['rays_in']: return None
    g = ray_growth(t)
    rot = math.radians(-8.0) * (1 - ease_out_cubic(lin(t, T['rays_in'], T['rays_in'] + 2.4)))
    rot += math.radians(10.0) * (1 - ease_out_expo(lin(t, T['zoom0'], T['zoom1'] + 0.4))) * (t >= T['zoom0'])
    alpha = smooth(lin(t, T['rays_in'], T['rays_in'] + 0.6))
    # drop flash brightening
    pulse = 1 + 0.6 * math.exp(-max(0, t - T['zoom0']) / 0.35) * (t >= T['zoom0'])
    rgb, al = rays.render((H, W), c[0], c[1], z, rot=rot, grow=g, alpha=alpha, bar_gain=1.35 * pulse, line_gain=1.15 * pulse)
    return rgb, al

# ----------------------------------------------------------------- silhouette (liquid glass)
def light_path_x(t):
    """x (KV) of the moving light along the top of the silhouette."""
    xl, xr = 846.0, 1004.0
    rest = 998.0
    t0, t1 = T['sweep0'], T['sweep_end']
    if t < T['sil_full'] - 0.4: return xl - 10
    if t < t0: return xl
    if t >= t1: return rest
    n = 3
    seg = (t1 - t0) / n
    i = int((t - t0) // seg); u = ease_in_out_sine((t - t0 - i * seg) / seg)
    if i % 2 == 0: return mix(xl, xr if i < n - 1 else rest, u)
    return mix(xr, xl, u)

def top_y(x):
    a = assets()
    return float(np.interp(x, a.top_x, a.top_y, left=a.top_y[0] + (a.top_x[0] - x) * 0.4, right=a.top_y[-1] + (x - a.top_x[-1]) * 0.9))

def spin_angle(t):
    if t < T['spin_wind']: return 0.0
    if t < T['spin_go']:
        return -math.radians(16) * ease_in_out_sine(lin(t, T['spin_wind'], T['spin_go']))
    if t < T['spin_stop']:
        u = lin(t, T['spin_go'], T['spin_stop'])
        e = ease_in_out_cubic(u)
        return mix(-math.radians(16), 2 * math.pi + math.radians(9), e)
    u = lin(t, T['spin_stop'], T['spin_stop'] + 0.55)
    return 2 * math.pi + math.radians(9) * (1 - ease_out_cubic(u)) * math.cos(u * math.pi * 1.0)

def sil_homography(phi, z, c):
    a = assets()
    S = a.s_S; bx0, by0, bx1, by1 = a.s_box
    ha, wa = a.s_mask.shape
    src = np.float32([[0, 0], [wa, 0], [wa, ha], [0, ha]])
    D = 1500.0
    dst = []
    for (px, py) in src:
        kx = bx0 + px / S; ky = by0 + py / S
        X = kx - SIL_AXIS_X; Y = ky - SIL_MID_Y
        Xr = X * math.cos(phi); Zd = X * math.sin(phi)
        s = D / (D + Zd)
        sx = c[0] + z * ((SIL_AXIS_X - PIVOT[0]) + Xr * s)
        sy = c[1] + z * ((SIL_MID_Y - PIVOT[1]) + Y * s)
        dst.append([sx, sy])
    return cv2.getPerspectiveTransform(src, np.float32(dst)), np.float32(dst)

def warp_layers(Hm, dst, layers):
    x0 = int(max(0, math.floor(dst[:, 0].min()) - 2)); x1 = int(min(W, math.ceil(dst[:, 0].max()) + 2))
    y0 = int(max(0, math.floor(dst[:, 1].min()) - 2)); y1 = int(min(H, math.ceil(dst[:, 1].max()) + 2))
    if x1 - x0 < 2 or y1 - y0 < 2: return None
    Tm = np.array([[1, 0, -x0], [0, 1, -y0], [0, 0, 1]], np.float64)
    Hl = Tm @ Hm
    outs = [cv2.warpPerspective(L, Hl, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0) for L in layers]
    return (x0, y0, x1, y1), outs

def render_silhouette(t, z, c, bg, glow):
    a = assets()
    if t < T['sil_in']: return
    appear = smooth(lin(t, T['sil_in'], T['sil_full']))
    phi = spin_angle(t)
    spinning = T['spin_go'] - 0.05 < t < T['spin_stop'] + 0.1
    nsub = 9 if spinning else 1
    acc = None
    lx = light_path_x(t); ly = top_y(lx) + 2
    for si in range(nsub):
        ts = t + (si / nsub - 0.5) * (0.5 / FPS) if nsub > 1 else t
        ph = spin_angle(ts) if nsub > 1 else phi
        Hm, dst = sil_homography(ph, z, c)
        res = warp_layers(Hm, dst, [a.s_mask, a.s_coladj, a.s_dist, a.s_nx, a.s_ny])
        if res is None: continue
        (x0, y0, x1, y1), (m, col, dist, nx, ny) = res
        cphi = math.cos(ph)
        nx = nx * (1 if cphi >= 0 else -1)
        # appear: liquid wipe from bottom to top + blur-to-sharp
        if appear < 1:
            yy = np.arange(y0, y1, dtype=np.float32)[:, None]
            ytop = c[1] + z * (200 - PIVOT[1]); ybot = c[1] + z * (885 - PIVOT[1])
            front = mix(ybot + 60, ytop - 120, ease_out_cubic(appear))
            xs_ = np.arange(x0, x1, dtype=np.float32)[None, :]
            fr = front + 7.0 * z * np.sin(xs_ * 0.035 / z + t * 9.0) * (1 - appear)
            wipe = np.clip((yy - fr) / (26.0 * z), 0, 1)
            fill_line = np.exp(-((yy - fr) / (5.0 * z)) ** 2) * (1 - smooth(lin(appear, 0.85, 1.0)))
            m = m * np.maximum(wipe, fill_line * 0.9) * smooth(appear * 2.5)
            col = col + fill_line[..., None] * 0.9
        bgr = bg[y0:y1, x0:x1]
        # refraction of what is behind
        hgt = np.clip(dist / (a.s_S * 16.0), 0, 1)
        k = 9.0 * z * (1 - hgt) + 3.0
        gx, gy = np.meshgrid(np.arange(x0, x1, dtype=np.float32), np.arange(y0, y1, dtype=np.float32))
        mapx = gx + nx * k; mapy = gy + ny * k
        refr = cv2.remap(bg, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        ga = a.glass_a
        glass = refr * (1 - ga) + col * ga
        # thickness / edge darkening & lightening
        dsc = dist / a.s_S * z * max(0.08, abs(cphi)) ** 0.5   # screen-ish px from edge
        inner = np.exp(-dsc / 7.0)
        glass = glass * (1 - 0.10 * inner[..., None]) + inner[..., None] * 0.10 * np.array([0.75, 0.92, 1.0], np.float32)
        # rim light
        ldx = (c[0] + z * (lx - PIVOT[0])) - gx; ldy = (c[1] + z * (ly - PIVOT[1])) - gy
        ln = np.sqrt(ldx * ldx + ldy * ldy) + 1e-3
        facing = np.clip((nx * ldx + ny * ldy) / ln, 0, 1)
        rim = np.exp(-dsc / 1.2) * (0.16 + 0.7 * facing ** 2)
        # fixed cool rim along right edges (KV look)
        rim += np.exp(-dsc / 1.1) * 0.14 * np.clip(nx, 0, 1)
        rim_col = np.array([0.80, 0.95, 1.0], np.float32)
        # sheen from moving light: soft glow on glass near light
        light_on = smooth(lin(t, T['sil_full'] - 0.5, T['sil_full'] + 0.3))
        sig = 50.0 * z
        sheen = np.exp(-(ldx * ldx + ldy * ldy) / (2 * sig * sig)) * 0.20 * light_on
        # spin sheen: band sweeping across the glass as it turns
        spin_sh = 0.0
        if T['spin_wind'] < t < T['spin_stop'] + 0.6:
            om = abs(spin_angle(ts + 0.01) - spin_angle(ts - 0.01)) / 0.02
            band_pos = math.sin(ph * 1.0) * 120 * z
            u = (gx - (c[0] + z * (SIL_AXIS_X - PIVOT[0])) - band_pos) * 0.8 + (gy - c[1]) * 0.35
            spin_sh = np.exp(-(u / (38 * z)) ** 2) * 0.50 * abs(cphi) ** 0.5 * clamp01(om / 9.0)
        lsx = c[0] + z * (lx - PIVOT[0])
        ub = (gx - lsx) + 0.30 * (gy - (c[1] + z * (ly - PIVOT[1])))
        sweeping = light_on * (1 - smooth(lin(t, T['sweep_end'] - 0.3, T['sweep_end'] + 0.6)))
        band = np.exp(-(ub / (34.0 * z)) ** 2) * 0.16 * sweeping * np.exp(-np.maximum(gy - (c[1] + z * (ly - PIVOT[1])), 0) / (520.0 * z))
        sh = sheen + spin_sh + band
        glass = glass + rim[..., None] * rim_col + np.asarray(sh, np.float32)[..., None] * np.array([0.95, 0.98, 1.0], np.float32)
        # edge-on brightening (glass edge catching light)
        edge_on = (1 - abs(cphi)) ** 6
        glass = glass + edge_on * 0.6
        if nsub == 1:
            bg[y0:y1, x0:x1] = bgr * (1 - m[..., None]) + glass * m[..., None]
        else:
            if acc is None:
                acc = np.zeros_like(bg); wacc = np.zeros((H, W, 1), np.float32)
            acc[y0:y1, x0:x1] += glass * m[..., None]; wacc[y0:y1, x0:x1] += m[..., None]
    if nsub > 1 and acc is not None:
        mavg = wacc / nsub
        gl = acc / np.maximum(wacc, 1e-6)
        np.copyto(bg, bg * (1 - mavg) + gl * mavg)
    # flare + glints into glow buffer
    if t >= T['sil_full'] - 0.6:
        fl = smooth(lin(t, T['sil_full'] - 0.6, T['sil_full'] + 0.2))
        if T['spin_wind'] <= t <= T['spin_stop'] + 0.15:
            fl *= 0.35 + 0.65 * abs(math.cos(phi)) ** 4
        # light intensity higher over the glass, dimmer outside
        on_glass = smooth(lin(lx, 840, 860)) * smooth(lin(lx, 1018, 1004))
        fl *= 0.55 + 0.45 * on_glass
        if t > T['zoom0']:
            fl *= 1 + 1.6 * math.exp(-(t - T['zoom0']) / 0.3)
        # project light position through current spin
        X = lx - SIL_AXIS_X; Xr = X * math.cos(phi); Zd = X * math.sin(phi); s = 1500 / (1500 + Zd)
        px = c[0] + z * ((SIL_AXIS_X - PIVOT[0]) + Xr * s); py = c[1] + z * ((ly - PIVOT[1]) * s + (SIL_MID_Y - PIVOT[1]) * (1 - s))
        draw_flare(glow, px, py, fl * appear, z, t)
        # lower-left static glint (KV detail)
        gxk, gyk = 909.0, 703.0
        X = gxk - SIL_AXIS_X; Xr = X * math.cos(phi); Zd = X * math.sin(phi); s = 1500 / (1500 + Zd)
        qx = c[0] + z * ((SIL_AXIS_X - PIVOT[0]) + Xr * s); qy = c[1] + z * ((gyk - PIVOT[1]) * s + (SIL_MID_Y - PIVOT[1]) * (1 - s))
        gi = appear * (0.75 + 0.25 * math.sin(t * 2.1)) * (abs(math.cos(phi)) ** 3)
        draw_glint(glow, qx, qy, gi, z)

def draw_flare(glow, px, py, inten, z, t):
    if inten <= 0.005: return
    R = int(260 * z)
    x0, x1 = int(max(0, px - R)), int(min(W, px + R)); y0, y1 = int(max(0, py - R)), int(min(H, py + R))
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx = (xx - px) / z; dy = (yy - py) / z
    r2 = dx * dx + dy * dy
    core = np.exp(-r2 / (2 * 3.0 ** 2)) * 1.5 + np.exp(-r2 / (2 * 10.0 ** 2)) * 0.75
    halo = np.exp(-np.sqrt(r2) / 20.0) * 0.32 + np.exp(-np.sqrt(r2) / 50.0) * 0.06
    spikes = np.zeros_like(r2)
    rot = 0.10 * math.sin(t * 0.7)
    for ang, length, wdt, amp in [(-0.30, 150, 1.1, 0.65), (1.27, 95, 1.0, 0.45), (0.55, 60, 0.9, 0.30), (2.35, 55, 0.9, 0.25)]:
        a_ = ang + rot
        ca, sa = math.cos(a_), math.sin(a_)
        u = dx * ca + dy * sa; v = -dx * sa + dy * ca
        spikes += amp * np.exp(-(v / wdt) ** 2) * np.exp(-np.abs(u) / (length * 0.33))
    f = (core + halo + spikes) * inten
    glow[y0:y1, x0:x1] += f[..., None] * np.array([0.92, 0.97, 1.0], np.float32)

def draw_glint(glow, px, py, inten, z):
    if inten <= 0.01: return
    R = int(70 * z)
    x0, x1 = int(max(0, px - R)), int(min(W, px + R)); y0, y1 = int(max(0, py - R)), int(min(H, py + R))
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx = (xx - px) / z; dy = (yy - py) / z
    f = np.exp(-(dx / 2.2) ** 2 - (dy / 16.0) ** 2) * 1.1 + np.exp(-(dx / 8.0) ** 2 - (dy / 34.0) ** 2) * 0.28
    glow[y0:y1, x0:x1] += (f * inten)[..., None] * np.array([0.9, 0.97, 1.0], np.float32)

# ----------------------------------------------------------------- text & grh logo
SILVER = np.array([0.70, 0.715, 0.735], np.float32); WHITE = np.array([0.99, 1.0, 1.0], np.float32)
def glyph_color(line, gx):
    a = assets(); spec = a.glyphs[line]['color']
    if spec == 'grad':
        u = clamp01((gx - 850.0) / 175.0); u = u * u * (3 - 2 * u)
        return SILVER * (1 - u) + WHITE * u
    return np.array(spec, np.float32) / 255.

def paste_alpha(out, alpha_src, SS, kvx, kvy, z, c, color, opacity, dx=0.0, dy=0.0, scale=1.0, blur=0.0, glow=None, glow_amt=0.0):
    if opacity <= 0.003: return
    f = z * scale / SS
    h, w = alpha_src.shape
    nw, nh = max(1, int(round(w * f))), max(1, int(round(h * f)))
    a = cv2.resize(alpha_src, (nw, nh), interpolation=cv2.INTER_AREA)
    if blur > 0.3:
        pad = int(blur * 3) + 2
        a = cv2.copyMakeBorder(a, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
        a = cv2.GaussianBlur(a, (0, 0), blur)
    else:
        pad = 0
    sx = c[0] + z * (kvx + dx - PIVOT[0]) - pad
    sy = c[1] + z * (kvy + dy - PIVOT[1]) - pad
    # centre scaling about glyph centre
    if scale != 1.0:
        sx -= (nw - w * z / SS) / 2; sy -= (nh - h * z / SS) / 2
    ix, iy = int(math.floor(sx)), int(math.floor(sy)); fx, fy = sx - ix, sy - iy
    hh, ww = a.shape
    Mt = np.float32([[1, 0, fx], [0, 1, fy]])
    a = cv2.warpAffine(a, Mt, (ww + 1, hh + 1), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    hh, ww = a.shape
    x0, y0 = max(0, ix), max(0, iy); x1, y1 = min(W, ix + ww), min(H, iy + hh)
    if x1 <= x0 or y1 <= y0: return
    sub = a[y0 - iy:y1 - iy, x0 - ix:x1 - ix] * opacity
    out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - sub[..., None]) + sub[..., None] * color
    if glow is not None and glow_amt > 0:
        glow[y0:y1, x0:x1] += sub[..., None] * color * glow_amt

def render_text(t, z, c, out, glow):
    a = assets()
    t0 = T['text0']
    plan = [('prem', 0.00, 0.040, 'track'), ('ceos', 0.20, 0.045, 'track'), ('mais', 0.38, 0.045, 'rise'), ('year', 0.80, 0.10, 'rise')]
    for line, d0, stag, style in plan:
        gl = a.glyphs[line]['glyphs']
        n = len(gl)
        cxl = np.mean([g['x'] + g['alpha'].shape[1] / g['SS'] / 2 for g in gl])
        for i, g in enumerate(gl):
            # stagger from the centre outwards for tracking lines, left-to-right for others
            order = abs(i - (n - 1) / 2) / ((n - 1) / 2 + 1e-6)
            st = t0 + d0 + order * stag * n * 0.5
            u = lin(t, st, st + 0.85)
            if u <= 0: continue
            e = ease_out_expo(u)
            op = smooth(lin(t, st, st + 0.45))
            gcx = g['x'] + g['alpha'].shape[1] / g['SS'] / 2
            if style == 'track':
                dx = (gcx - cxl) * 0.35 * (1 - e); dy = 0.0
            else:
                dx = 0.0; dy = 14.0 * (1 - e)
            blur = 4.0 * (1 - e) * z
            col = glyph_color(line, gcx)
            paste_alpha(out, g['alpha'], g['SS'], g['x'], g['y'], z, c, col, op, dx=dx, dy=dy, blur=blur, glow=glow, glow_amt=0.35 * (1 - e))
    # shine pass over MAIS ADMIRADOS after it settles
    # grh logo
    if t >= T['grh0']:
        op = smooth(lin(t, T['grh0'], T['grh1']))
        m = a.grh_meta
        SR = m['SR']; sc = m['scale']
        kvx = m['dst_circle_lt'][0] + (m['src_origin'][0] - m['tr_circle_lt'][0]) * sc
        kvy = m['dst_circle_lt'][1] + (m['src_origin'][1] - m['tr_circle_lt'][1]) * sc
        blur = 3.0 * (1 - op)
        paste_alpha(out, a.grh, SR / sc, kvx, kvy, z, c, WHITE, op, blur=blur)

# ----------------------------------------------------------------- frame
def render_frame(t, preview_scale=1.0):
    a = assets()
    z, c, zb = camera(t)
    bg, c_aura = render_background(t, zb, c)
    glow = np.zeros((H, W, 3), np.float32)
    render_particles(t, c_aura, glow)
    r = render_rays(t, z, c)
    if r is not None:
        rgb, al = r
        bg = bg * (1 - al[..., None]) + rgb
    render_silhouette(t, z, c, bg, glow)
    render_text(t, z, c, bg, glow)
    render_dust(t, bg, zb)
    # glow / bloom
    if glow.max() > 0:
        small = cv2.resize(glow, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        b1 = cv2.resize(cv2.GaussianBlur(small, (0, 0), 3), (W, H), interpolation=cv2.INTER_LINEAR)
        b2 = cv2.resize(cv2.GaussianBlur(small, (0, 0), 12), (W, H), interpolation=cv2.INTER_LINEAR)
        bg = bg + glow + b1 * 0.45 + b2 * 0.30
    # drop flash
    if t >= T['zoom0']:
        fl = math.exp(-(t - T['zoom0']) / 0.25) * 0.16
        if fl > 0.002:
            rr2 = ((a.xx - c[0]) / 900.0) ** 2 + ((a.yy - c[1]) / 650.0) ** 2
            bg = bg + (fl * np.exp(-rr2))[..., None] * np.array([0.8, 0.9, 1.0], np.float32)
    # filmic soft clip
    bg = np.maximum(bg, 0)
    bg = 1 - np.exp(-bg * 1.08) if False else np.where(bg < 0.8, bg, 0.8 + 0.2 * np.tanh((bg - 0.8) / 0.2))
    # grain
    g = a.grain_rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
    bg = bg + g[..., None] * 0.010
    # vignette (subtle) & fades
    fade = smooth(lin(t, 0.0, 0.7)) * (1 - smooth(lin(t, T['fade_out0'], T['end'] - 0.05)))
    bg = bg * fade
    return np.clip(bg, 0, 1)

def to8(img):
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
