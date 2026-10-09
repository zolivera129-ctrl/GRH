import os as _os
BUILD = _os.environ.get('MOTION_BUILD', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'build')) + '/'
import cv2, numpy as np, sys
from scipy.interpolate import CubicSpline, splprep, splev
W=BUILD + 'work/'
im=cv2.imread(W+'kv.png').astype(np.float32)
mx=cv2.GaussianBlur(im.max(2),(0,0),1.2)

top=[(848,218),(849,208),(853,202),(860,200),(870,200),(880,201),(900,206),(920,214),(940,224),(957,230),(973,236),(990,243),(1003,251)]
right=[(1012,257),(1018,270),(1024,285),(1029,300),(1034,320),(1038,340),(1040,352),(1040,380),(1036,410),(1026,425),(1023,440),(1025,460),(1028,472),(1033,484),(1042,505),(1055,520),(1063,535),(1070,555),(1072,572),(1069,586),(1055,592),(1035,597),(1023,601),(1019,606),(1012,630),(1000,665),(988,700),(975,725),(965,750),(960,800),(960,840),(957,860),(950,872),(942,880)]
bottom=[(936,881),(930,873)]
left=[(925,860),(920,840),(915,800),(912,750),(911,700),(913,665),(913,640),(914,606),(918,586),(925,579),(937,573),(957,567),(970,557),(980,545),(989,535),(975,520),(948,500),(935,484),(922,472),(908,455),(893,440),(883,425),(872,400),(862,370),(856,345),(855,330),(857,310),(862,290),(864,270),(862,250),(853,230)]
pts=np.array(top+right+bottom+left,float)

occ_boxes=[(928,352,1100,412),(870,444,1062,471),(832,486,1088,519),(665,538,1268,584),(858,606,1070,662)]
def occluded(p):
    x,y=p
    if (x-869)**2+(y-380)**2 < 47**2: return True
    for a,b,c,d in occ_boxes:
        if a-3<=x<=c+3 and b-3<=y<=d+3: return True
    # flare zone
    if (x-1000)**2+(y-250)**2 < 30**2 or (930<=x<=1012 and 218<=y<=262): return True
    return False

def resample(P,step=1.5):
    P=np.vstack([P,P[:1]])
    d=np.r_[0,np.cumsum(np.hypot(*np.diff(P,axis=0).T))]
    n=int(d[-1]/step)
    s=np.linspace(0,d[-1],n,endpoint=False)
    return np.c_[np.interp(s,d,P[:,0]),np.interp(s,d,P[:,1])]

def smooth(P,sig):
    n=len(P); k=int(3*sig)+1
    w=np.exp(-0.5*(np.arange(-k,k+1)/sig)**2); w/=w.sum()
    Q=np.zeros_like(P)
    for i,wi in zip(range(-k,k+1),w): Q+=wi*np.roll(P,i,axis=0)
    return Q

P=resample(pts)
P=smooth(P,3)
for it in range(4):
    n=len(P)
    T=np.roll(P,-1,0)-np.roll(P,1,0); T/=np.linalg.norm(T,axis=1,keepdims=True)+1e-9
    N=np.c_[T[:,1],-T[:,0]]  # outward? check sign using centroid
    c=P.mean(0)
    if np.mean(np.sum((P-c)*N,1))<0: N=-N
    occ=np.array([occluded(p) for p in P])
    newP=P.copy()
    for i in range(n):
        if occ[i]: continue
        ts=np.arange(-5,5.01,0.25)
        q=P[i][None]+ts[:,None]*N[i][None]
        v=cv2.remap(mx,q[:,0:1].astype(np.float32),q[:,1:2].astype(np.float32),cv2.INTER_LINEAR)[:,0]
        dv=np.gradient(v)
        j=np.argmin(dv)  # strongest falling (inside->outside)
        if dv[j]<-1.0: newP[i]=q[j]
    # re-interpolate occluded runs from visible neighbours via arc-length spline
    vis=~occ
    d=np.r_[0,np.cumsum(np.hypot(*np.diff(newP,axis=0).T))]
    idx=np.where(vis)[0]
    # periodic extension
    L=d[-1]+np.hypot(*(newP[0]-newP[-1]))
    dd=np.r_[d[idx]-L,d[idx],d[idx]+L]; xx=np.r_[newP[idx,0]]*1; 
    X=np.r_[newP[idx,0],newP[idx,0],newP[idx,0]]; Y=np.r_[newP[idx,1],newP[idx,1],newP[idx,1]]
    # thin the samples near gaps to avoid noisy ends: use smoothing spline
    from scipy.interpolate import UnivariateSpline
    o=np.argsort(dd)
    sx=UnivariateSpline(dd[o],X[o],s=len(dd)*0.6); sy=UnivariateSpline(dd[o],Y[o],s=len(dd)*0.6)
    newP[occ,0]=sx(d[occ]); newP[occ,1]=sy(d[occ])
    P=smooth(resample(newP),2.0)
np.save(W+'sil_contour.npy',P)
# overlay
S=3; x0,y0=820,190
crop=cv2.resize(im[y0:900,x0:1090].astype(np.uint8),None,fx=S,fy=S,interpolation=cv2.INTER_CUBIC)
Q=((P-[x0,y0])*S).astype(np.int32)
cv2.polylines(crop,[Q],True,(0,0,255),1,cv2.LINE_AA)
h=crop.shape[0]
for k,(a,b) in enumerate([(0,h//3),(h//3,2*h//3),(2*h//3,h)]):
    cv2.imwrite(W+f'ov{k}.png',crop[a:b])
print(len(P))
