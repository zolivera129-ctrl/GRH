"""Parametric reconstruction of the 90-ray spiral sunburst of the 'Mais Admirados' logo (KV units)."""
import numpy as np

CENTER=np.array([970.5,533.5])
N=90
TH0=3.1   # deg, image coords (0=east, 90=south)
STEP=4.0
R_TIP=150.0
BAR_W=8.0
LINE_W=1.7

def _A(k):
    th=TH0+STEP*k
    if 12<=k<=54: return 462-0.89*(th-51)
    t=th if th>=223 else th+360
    return 470-0.89*(t-223)

def _has_line(k): return (12<=k<=34) or (55<=k<=78)

# measured visibility of bar ends (alpha), from KV sampling; interpolated over occluded rays
_bar_alpha_pts={0:0.18,4:0.21,7:0.27,8:0.42,11:0.55,12:0.55,14:0.5,16:0.38,18:0.26,20:0.18,21:0.15,24:0.10,26:0.06,30:0.04,35:0.07,
 38:0.10,41:0.14,44:0.20,47:0.28,49:0.36,51:0.58,54:0.6,55:0.52,56:0.50,58:0.42,60:0.36,63:0.33,67:0.30,70:0.22,72:0.05,75:0.03,
 78:0.05,79:0.09,81:0.14,83:0.18,86:0.21,89:0.18}
_line_alpha_pts={12:0.85,13:0.88,14:0.8,15:0.78,16:0.8,17:0.78,18:0.72,19:0.6,20:0.55,21:0.42,22:0.32,24:0.2,26:0.12,28:0.08,30:0.07,34:0.06,
 55:0.55,56:0.62,57:0.64,58:0.62,59:0.55,60:0.58,61:0.52,62:0.52,63:0.46,64:0.45,65:0.42,66:0.36,67:0.34,68:0.33,69:0.24,70:0.18,71:0.13,72:0.08,74:0.07,78:0.07}
WHITE=np.array([0.90,0.93,0.94]); GOLD=np.array([0.95,0.86,0.42]); CREAM=np.array([0.92,0.89,0.74]); COOL=np.array([0.80,0.86,0.92])
_line_col_pts={12:WHITE,13:WHITE*0.6+GOLD*0.4,15:GOLD,20:GOLD,21:CREAM,23:COOL,34:COOL,55:WHITE,60:WHITE,61:CREAM,63:GOLD,70:GOLD,72:COOL,78:COOL}
_bar_col_pts={0:COOL,6:CREAM*0.5+COOL*0.5,10:CREAM,20:CREAM,24:COOL,44:COOL,48:CREAM,50:np.array([0.94,0.90,0.66]),56:np.array([0.94,0.90,0.68]),62:CREAM,70:COOL,89:COOL}

def _interp_circ(pts,k,vec=False):
    ks=sorted(pts)
    ext=[(a-N,pts[a]) for a in ks]+[(a,pts[a]) for a in ks]+[(a+N,pts[a]) for a in ks]
    xs=[e[0] for e in ext]
    if vec:
        vals=np.array([e[1] for e in ext]); return np.array([np.interp(k,xs,vals[:,c]) for c in range(3)])
    return float(np.interp(k,xs,[e[1] for e in ext]))

def ray_table():
    rows=[]
    for k in range(N):
        A=_A(k); hl=_has_line(k)
        Bend=A-(161 if k<=54 else 169) if hl else A
        la=_interp_circ(_line_alpha_pts,k) if hl else 0.0
        if hl:
            # line rays only between first/last listed
            pass
        rows.append(dict(k=k,th=np.deg2rad(TH0+STEP*k),A=A,B=Bend,line=hl,
            a_bar=_interp_circ(_bar_alpha_pts,k),a_line=la,
            c_bar=_interp_circ(_bar_col_pts,k,True),c_line=_interp_circ(_line_col_pts,k,True)))
    return rows
TABLE=ray_table()
ARR={key:np.array([r[key] for r in TABLE]) for key in ['th','A','B','a_bar','a_line']}
ARR['line']=np.array([r['line'] for r in TABLE],bool)
ARR['c_bar']=np.array([r['c_bar'] for r in TABLE]); ARR['c_line']=np.array([r['c_line'] for r in TABLE])

def render(shape,cx,cy,z,rot=0.0,grow=None,alpha=1.0,bar_gain=1.0,line_gain=1.0,width_gain=1.0,rmax_out=None):
    """Return premultiplied RGB (H,W,3) and alpha (H,W) of the ray burst.
    cx,cy: screen position of burst centre; z: scale (screen px per KV px); rot: radians (clockwise).
    grow: array(N) in [0,1]: fraction of each ray's outer radius drawn (from R_TIP outward)."""
    H,W=shape
    if grow is None: grow=np.ones(N)
    rmax=(max(ARR['A'])+6)*z
    x0=int(max(0,np.floor(cx-rmax))); x1=int(min(W,np.ceil(cx+rmax)))
    y0=int(max(0,np.floor(cy-rmax))); y1=int(min(H,np.ceil(cy+rmax)))
    rgb=np.zeros((H,W,3),np.float32); al=np.zeros((H,W),np.float32)
    if x1<=x0 or y1<=y0: return rgb,al
    yy,xx=np.mgrid[y0:y1,x0:x1].astype(np.float32)
    dx=(xx+0.5-cx)/z; dy=(yy+0.5-cy)/z
    r=np.sqrt(dx*dx+dy*dy)+1e-6
    th=np.arctan2(dy,dx)-rot
    kf=(np.rad2deg(th)-TH0)/STEP
    k=np.round(kf).astype(np.int32)%N
    dth=(kf-np.round(kf))*np.deg2rad(STEP)
    dperp=r*np.sin(dth)*z            # screen px
    rpar=r*np.cos(dth)               # KV px
    A=ARR['A'][k]; Bn=ARR['B'][k]; g=grow[k]
    rcur=R_TIP+(A-R_TIP)*g           # current outer extent
    # bar
    bend=np.minimum(Bn,rcur)
    t=np.clip((rpar-R_TIP)/(Bn-R_TIP),0,1)
    hw=0.5*BAR_W*width_gain*t*z
    cov=np.clip(hw-np.abs(dperp)+0.5,0,1)*np.minimum(1,2*hw+0.15)
    cov*=np.clip((bend-rpar)*z+0.5,0,1)*(rpar>R_TIP)
    ab=ARR['a_bar'][k]*bar_gain*t*t*cov
    # line
    hwl=0.5*LINE_W*width_gain*max(z,0.6)
    covl=np.clip(hwl-np.abs(dperp)+0.5,0,1)
    seg=np.clip((rpar-Bn)*z+0.5,0,1)*np.clip((rcur-rpar)*z+0.5,0,1)
    L=np.maximum(A-Bn,1)
    u=np.clip((rpar-Bn)/L,0,1)
    fade=np.clip(u/0.04,0,1)*np.clip((1-u)/0.12,0.35,1)
    alin=ARR['a_line'][k]*line_gain*covl*seg*fade*ARR['line'][k]
    a_tot=1-(1-ab)*(1-alin)
    col=(ARR['c_bar'][k]*ab[...,None]+ARR['c_line'][k]*alin[...,None])
    rgb[y0:y1,x0:x1]=col*alpha
    al[y0:y1,x0:x1]=a_tot*alpha
    return rgb,al
