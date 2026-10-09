"""Build static assets: gestaorh logo alpha (hi-res), text layers (hi-res), silhouette asset (2x)."""
import os as _os
BUILD = _os.environ.get('MOTION_BUILD', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'build')) + '/'
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
B=BUILD
W=B+'work/'; A=B+'assets/'; F=B+'fonts/'
import os; os.makedirs(A,exist_ok=True)
kv=cv2.imread(W+'kv.png').astype(np.float32)[...,::-1]/255.

def smoothstep(e0,e1,x):
    t=np.clip((x-e0)/(e1-e0),0,1); return t*t*(3-2*t)

# ---------- gestaorh logo: from top-right of KV, superresolve x8 ----------
x0,y0,x1,y1=1606,56,1846,144
sub=kv[y0:y1,x0:x1].min(2)
bg=np.median(kv[y0:y1,1850:1900].min(2))
alpha=np.clip((sub-bg)/(0.97-bg),0,1)
SR=8
up=cv2.resize(alpha,None,fx=SR,fy=SR,interpolation=cv2.INTER_CUBIC)
up=cv2.GaussianBlur(up,(0,0),SR*0.35)
up=smoothstep(0.35,0.65,up)
np.save(A+'grh_logo_alpha_x8.npy',up.astype(np.float32))
# placement: TR logo circle left 1617, top 66 -> central lockup circle left 828, top 336, scale 1.24
meta=dict(src_origin=(x0,y0),SR=SR,tr_circle_lt=(1617,66),dst_circle_lt=(828,336.5),scale=1.245)
np.save(A+'grh_logo_meta.npy',meta)

# ---------- silhouette asset (2x) ----------
P=np.load(W+'sil_contour.npy')
C=np.load(W+'sil_color1x.npy')
S2=2
bx0,by0,bx1,by1=800,180,1100,900   # KV-space box
Wd,Hd=(bx1-bx0)*S2,(by1-by0)*S2
ss=4
m=np.zeros((Hd*ss,Wd*ss),np.uint8)
Q=np.round((P-[bx0,by0])*S2*ss).astype(np.int32)
cv2.fillPoly(m,[Q],255)
mask=cv2.resize(m.astype(np.float32)/255.,(Wd,Hd),interpolation=cv2.INTER_AREA)
col=cv2.resize(C[by0:by1,bx0:bx1],(Wd,Hd),interpolation=cv2.INTER_CUBIC)
col=np.clip(col,0,1)
# distance inside (in 2x px)
dist=cv2.distanceTransform((mask>0.5).astype(np.uint8),cv2.DIST_L2,5).astype(np.float32)
# smooth pseudo-height for normals
h=np.sqrt(np.clip(dist/ (S2*14.0),0,1))
h=cv2.GaussianBlur(h,(0,0),3)
gx=cv2.Sobel(h,cv2.CV_32F,1,0,ksize=3); gy=cv2.Sobel(h,cv2.CV_32F,0,1,ksize=3)
np.savez_compressed(A+'silhouette_2x.npz',mask=mask.astype(np.float32),col=col.astype(np.float32),dist=dist,gx=gx,gy=gy,box=np.array([bx0,by0,bx1,by1]),S=S2,contour=P)
print('sil asset',mask.shape)

# ---------- text layers: rendered at 4x in KV space, per-glyph alpha with boxes ----------
def font(w,cap,SS):
    return ImageFont.truetype(F+f'Montserrat-{w}.ttf',int(round(cap/0.70*SS)))
def ink_bbox(ch,f):
    im=Image.new('L',(f.size*3,f.size*3),0); d=ImageDraw.Draw(im); d.text((f.size,f.size*2),ch,font=f,fill=255,anchor='ls')
    a=np.array(im); ys,xs=np.where(a>20)
    return xs.min()-f.size, xs.max()-f.size  # ink left/right relative to origin
def render_line(text,weight,cap,baseline_y,glyph_left_xs,SS=4,name=''):
    f=font(weight,cap,SS)
    glyphs=[]
    for ch,lx in zip(text,glyph_left_xs):
        if ch==' ': continue
        il,ir=ink_bbox(ch,f)
        pad=int(cap*SS*1.2)
        size=f.size*3
        im=Image.new('L',(size,size),0); d=ImageDraw.Draw(im)
        ox=size//3; oy=size*2//3
        d.text((ox,oy),ch,font=f,fill=255,anchor='ls')
        a=np.array(im).astype(np.float32)/255.
        ys,xs=np.where(a>0.004)
        ya,yb,xa,xb=ys.min(),ys.max()+1,xs.min(),xs.max()+1
        crop=a[ya:yb,xa:xb]
        # KV-space position of crop top-left: glyph ink left = lx ; baseline = baseline_y
        kvx=lx-(ox+il-xa)/SS + (xa-xa)/SS
        kvx=lx+(xa-(ox+il))/SS
        kvy=baseline_y+(ya-oy)/SS
        glyphs.append(dict(ch=ch,alpha=crop,x=kvx,y=kvy,SS=SS))
    return glyphs

def render_glyphs(text,weight,cap,baseline,centers,SS=4):
    f=font(weight,cap,SS)
    out=[]
    ci=0
    for ch in text:
        if ch==' ': continue
        size=f.size*3
        im=Image.new('L',(size,size),0); d=ImageDraw.Draw(im)
        ox=size//3; oy=size*2//3
        d.text((ox,oy),ch,font=f,fill=255,anchor='ls')
        a=np.array(im).astype(np.float32)/255.
        ys,xs=np.where(a>0.002)
        ya,yb,xa,xb=ys.min()-2,ys.max()+3,xs.min()-2,xs.max()+3
        crop=a[ya:yb,xa:xb]
        inkc=(xs.min()+xs.max()+1)/2
        cx=centers[ci]; ci+=1
        kvx=cx+(xa-inkc)/SS
        kvy=baseline+(ya-oy)/SS
        out.append(dict(ch=ch,alpha=crop.astype(np.float32),x=float(kvx),y=float(kvy),SS=SS))
    return out
lines={}
lines['prem']=dict(glyphs=render_glyphs('PREMIAÇÃO',700,14.2,464.0,[880.5,902,922.5,945.5,965.5,983.5,1004.5,1027.5,1049.5]),color=(252,254,255))
lines['ceos']=dict(glyphs=render_glyphs('CEOs E RHs',400,16.0,510.0,[844.5,875.5,904.5,932.5,975.5,1020.5,1049.5,1076.5]),color=(212,190,112))
lines['mais']=dict(glyphs=render_glyphs('MAIS ADMIRADOS',600,29.6,576.0,[685.5,736,774,809.5,879.5,927.5,978,1019,1056,1101.5,1150.5,1199,1245.5]),color='grad')
lines['year']=dict(glyphs=render_glyphs('2026',300,40.0,654.0,[874,932,989,1046.5]),color=(230,208,138))
import pickle
pickle.dump(lines,open(A+'text_glyphs.pkl','wb'))
print('glyphs',{k:len(v['glyphs']) for k,v in lines.items()})
