import os as _os
BUILD = _os.environ.get('MOTION_BUILD', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'build')) + '/'
import cv2, numpy as np
W=BUILD + 'work/'
im=cv2.imread(W+'kv.png').astype(np.float32)/255.
P=np.load(W+'sil_contour.npy')
H,Wd=im.shape[:2]
def poly_mask(P,scale=1,shape=(1080,1920),ss=4):
    h,w=shape
    m=np.zeros((h*ss,w*ss),np.uint8)
    cv2.fillPoly(m,[np.round(P*scale*ss).astype(np.int32)],255,cv2.LINE_8)
    return cv2.resize(m.astype(np.float32)/255.,(w,h),interpolation=cv2.INTER_AREA)
M=poly_mask(P)
np.save(W+'sil_mask1x.npy',M)
inside=M>0.99
# text pixel detection inside bands
occ=np.zeros((H,Wd),bool)
yy,xx=np.mgrid[0:H,0:Wd]
occ|=((xx-869)**2+(yy-380)**2)<46**2
bands=[(350,414),(442,473),(484,521),(536,586),(604,664)]
lum=im.mean(2)
for a,b in bands:
    sub=im[a-15:b+15]
    med=cv2.medianBlur((sub*255).astype(np.uint8),25).astype(np.float32)/255.
    dev=np.abs(sub-med).max(2)
    t=(dev>0.07)
    t=cv2.dilate(t.astype(np.uint8),np.ones((5,5),np.uint8)).astype(bool)
    occ[a-15:b+15]|=t & (np.arange(a-15,b+15)[:,None]>=a-2)&(np.arange(a-15,b+15)[:,None]<=b+2)
# flare zone
occ|=((xx-998)**2+(yy-250)**2)<48**2
occ|=(xx>=898)&(xx<=932)&(yy>=588)&(yy<=664)
# left lower glint
occ|=((xx-910)/16.)**2+((yy-702)/42.)**2<1
inside_er=cv2.erode(inside.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))).astype(bool)
known=inside_er & ~occ
# push-pull fill
def pushpull(img,w,levels=9):
    if levels==0 or min(img.shape[:2])<4:
        s=w.sum(); 
        return np.broadcast_to((img*w[...,None]).sum((0,1))/max(s,1e-6),img.shape).copy()
    wi=img*w[...,None]
    h,ww=w.shape
    sm_w=cv2.resize(cv2.GaussianBlur(w,(0,0),1.0),(ww//2,h//2),interpolation=cv2.INTER_AREA)
    sm_i=cv2.resize(cv2.GaussianBlur(wi,(0,0),1.0),(ww//2,h//2),interpolation=cv2.INTER_AREA)
    low=pushpull(sm_i/np.maximum(sm_w,1e-6)[...,None],np.clip(sm_w*4,0,1),levels-1)
    up=cv2.resize(low,(ww,h),interpolation=cv2.INTER_LINEAR)
    return img*w[...,None]+up*(1-w[...,None])
x0,y0,x1,y1=780,170,1110,910
sub=im[y0:y1,x0:x1]; kw=known[y0:y1,x0:x1].astype(np.float32)
filled=pushpull(sub,kw)
# normalized blur to remove rays, inside only (filled everywhere so plain blur ok)
col=cv2.GaussianBlur(filled,(0,0),4.0)
full=np.zeros_like(im); full[y0:y1,x0:x1]=col
np.save(W+'sil_color1x.npy',full.astype(np.float32))
vis=np.concatenate([im[y0:y1,x0:x1],filled,col,col*M[y0:y1,x0:x1,None]],1)
o=np.zeros_like(sub); o[...,2]=occ[y0:y1,x0:x1]
vis=np.concatenate([vis,sub*0.6+o*0.4],1)
cv2.imwrite(W+'silcol_vis.png',(np.clip(vis,0,1)*255).astype(np.uint8))
