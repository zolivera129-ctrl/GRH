import os as _os
BUILD = _os.environ.get('MOTION_BUILD', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'build')) + '/'
import cv2, numpy as np, sys, pickle
sys.path.insert(0,_os.path.dirname(_os.path.abspath(__file__)))
import rays
B=BUILD
W=B+'work/'; A=B+'assets/'
kv=cv2.imread(W+'kv.png').astype(np.float32)[...,::-1]/255.
H,Wd=kv.shape[:2]
yy,xx=np.mgrid[0:H,0:Wd].astype(np.float32)

# --- ray geometry mask (generous, geometric)
dxr=xx-rays.CENTER[0]; dyr=yy-rays.CENTER[1]
rr=np.hypot(dxr,dyr)+1e-6
kf=(np.rad2deg(np.arctan2(dyr,dxr))-rays.TH0)/rays.STEP
kk=np.round(kf).astype(int)%rays.N
dperp=np.abs(rr*np.sin((kf-np.round(kf))*np.deg2rad(rays.STEP)))
Bk=rays.ARR['B'][kk]; Ak=rays.ARR['A'][kk]
barm=(rr>100)&(rr<Ak+8)&(dperp<3.0+6.5*np.clip((rr-100)/(Bk-100),0,1))
linem=(rr>=Bk-2)&(rr<Ak+7)&(dperp<2.6)
raymask=(barm|linem).astype(np.uint8)
ring=np.zeros_like(raymask)
# --- silhouette
M=np.load(W+'sil_mask1x.npy')
sil=cv2.dilate((M>0.02).astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(13,13)))
flare=(((xx-998)**2+(yy-250)**2)<75**2).astype(np.uint8)
glint=((((xx-908)/30.)**2+((yy-705)/60.)**2)<1).astype(np.uint8)
# --- text & central logo
txt=np.zeros((H,Wd),np.uint8)
for (x0,y0,x1,y1) in [(860,440,1066,476),(830,486,1090,516),(660,540,1272,582),(855,608,1066,660)]:
    sub=kv[y0:y1,x0:x1]
    med=cv2.medianBlur((sub*255).astype(np.uint8),21).astype(np.float32)/255.
    d=np.abs(sub-med).max(2)>0.05
    txt[y0:y1,x0:x1]|=d.astype(np.uint8)
txt=cv2.dilate(txt,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
logo=((((xx-870)**2+(yy-379)**2)<49**2)|((xx>922)&(xx<1102)&(yy>350)&(yy<410))).astype(np.uint8)
badge=((xx>108)&(xx<446)&(yy>98)&(yy<466)).astype(np.uint8)
tr=((xx>1600)&(xx<1846)&(yy>52)&(yy<146)).astype(np.uint8)
foot=((xx>36)&(xx<492)&(yy>945)&(yy<1048)).astype(np.uint8)

# step 1: thin inpaint (rays+text+ring) with Telea
thin=((raymask|txt|ring|tr|foot)>0).astype(np.uint8)
big=((sil|flare|glint|logo)>0).astype(np.uint8)
img8=(np.clip(kv,0,1)*255).astype(np.uint8)
bgr=img8[...,::-1].copy()
f1=cv2.inpaint(bgr,((thin|big|badge)>0).astype(np.uint8)*255,6,cv2.INPAINT_TELEA)
f1=f1[...,::-1].astype(np.float32)/255.

def directional_fill(img,hole,angle_deg,blur=2.5):
    """Fill hole by linear interpolation along lines at angle_deg (image coords)."""
    Hh,Ww=hole.shape
    src=cv2.GaussianBlur(img,(0,0),blur)
    c=(Ww/2,Hh/2)
    Rm=cv2.getRotationMatrix2D(c,angle_deg,1.0)  # rotates image so that direction angle becomes horizontal
    diag=int(np.hypot(Hh,Ww))+4
    Rm[0,2]+=(diag-Ww)/2; Rm[1,2]+=(diag-Hh)/2
    rs=cv2.warpAffine(src,Rm,(diag,diag),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(-1,-1,-1))
    rh=cv2.warpAffine(hole.astype(np.float32),Rm,(diag,diag),flags=cv2.INTER_LINEAR,borderValue=1)
    valid=cv2.warpAffine(np.ones((Hh,Ww),np.float32),Rm,(diag,diag),flags=cv2.INTER_NEAREST,borderValue=0)
    known=(rh<0.01)&(valid>0.5)
    out=rs.copy()
    xs=np.arange(diag)
    for y in range(diag):
        kn=known[y]
        need=(rh[y]>=0.01)&(valid[y]>0.5)
        if not need.any() or kn.sum()<2: continue
        for ch in range(3):
            out[y,need,ch]=np.interp(xs[need],xs[kn],rs[y,kn,ch])
    Ri=cv2.invertAffineTransform(Rm)
    back=cv2.warpAffine(out,Ri,(Ww,Hh),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
    return back

def polar_fill(img,hole,F,rmax=1400,nth=2880,blur=2.0):
    src=cv2.GaussianBlur(img,(0,0),blur)
    th=np.linspace(0,2*np.pi,nth,endpoint=False); r=np.arange(0,rmax,1.0)
    TH,RR=np.meshgrid(th,r)
    mx=(F[0]+RR*np.cos(TH)).astype(np.float32); my=(F[1]+RR*np.sin(TH)).astype(np.float32)
    P=cv2.remap(src,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(-1,-1,-1))
    Hm=cv2.remap(hole.astype(np.float32),mx,my,cv2.INTER_LINEAR,borderValue=0)
    valid=(mx>=0)&(mx<img.shape[1]-1)&(my>=0)&(my<img.shape[0]-1)
    out=P.copy()
    for j in range(nth):
        need=(Hm[:,j]>0.01)&valid[:,j]
        if not need.any(): continue
        kn=(Hm[:,j]<0.01)&valid[:,j]
        if kn.sum()<2: continue
        for ch in range(3): out[need,j,ch]=np.interp(r[need],r[kn],P[kn,j,ch])
    # back to cartesian
    Hh,Ww=hole.shape
    yy,xx=np.mgrid[0:Hh,0:Ww].astype(np.float32)
    rr=np.hypot(xx-F[0],yy-F[1]); tt=(np.arctan2(yy-F[1],xx-F[0])%(2*np.pi))/(2*np.pi)*nth
    back=cv2.remap(out,tt.astype(np.float32),rr.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_WRAP)
    return back

plate=f1.copy()
# badge: polar fill around streak focal point
bd=cv2.dilate(badge,np.ones((5,5),np.uint8))
pf=polar_fill(f1,bd,(603,317))
plate[bd>0]=pf[bd>0]
# big central holes: directional fill along the beam
bg_hole=cv2.dilate(big,np.ones((5,5),np.uint8))
df=directional_fill(plate,bg_hole,28.0)
plate[bg_hole>0]=df[bg_hole>0]
# soften seams: feathered blend of filled regions
filled=((bd|bg_hole)>0).astype(np.float32)
fe=cv2.GaussianBlur(filled,(0,0),3)
plate_s=cv2.GaussianBlur(plate,(0,0),1.5)
# grain on filled/inpainted regions
rng=np.random.default_rng(7)
anyfill=((thin|big|badge|bd|bg_hole)>0).astype(np.float32)
anyfill=cv2.GaussianBlur(anyfill,(0,0),2)
lum=plate.mean(2,keepdims=True)
noise=rng.normal(0,1,(H,Wd,1)).astype(np.float32)
noise=cv2.GaussianBlur(noise,(0,0),0.6)[...,None]*1.6
plate=plate+noise*(0.006+0.03*lum)*anyfill[...,None]
plate=np.clip(plate,0,1)
np.save(A+'plate.npy',plate.astype(np.float32))
cv2.imwrite(W+'plate.png',(plate[...,::-1]*255).astype(np.uint8))
cv2.imwrite(W+'plate_small.jpg',cv2.resize((plate[...,::-1]*255).astype(np.uint8),(960,540),interpolation=cv2.INTER_AREA))
print('done')
