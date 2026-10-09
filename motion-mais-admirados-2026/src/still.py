import os as _os
BUILD = _os.environ.get('MOTION_BUILD', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'build')) + '/'
import sys, time, cv2
sys.path.insert(0,_os.path.dirname(_os.path.abspath(__file__)))
import motion
out=BUILD + 'stills/'
import os; os.makedirs(out,exist_ok=True)
for ts in sys.argv[1:]:
    t=float(ts); t0=time.time()
    f=motion.render_frame(t)
    cv2.imwrite(out+f't{t:06.2f}.png',motion.to8(f)[...,::-1])
    print(ts,'%.2fs'%(time.time()-t0),flush=True)
