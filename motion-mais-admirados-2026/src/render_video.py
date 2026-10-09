import os as _os
BUILD = _os.environ.get('MOTION_BUILD', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'build')) + '/'
import sys, os, subprocess, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

OUT = BUILD + 'render/'
os.makedirs(OUT, exist_ok=True)

def worker(idx, f0, f1):
    import motion
    motion.assets().grain_rng = np.random.default_rng(1000 + idx)
    fn = OUT + f'chunk_{idx:02d}.mkv'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{motion.W}x{motion.H}',
           '-r', str(motion.FPS), '-i', '-', '-c:v', 'ffv1', '-level', '3', '-pix_fmt', 'rgb24', fn]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for f in range(f0, f1):
        t = f / motion.FPS
        img = motion.to8(motion.render_frame(t))
        p.stdin.write(img.tobytes())
        if (f - f0) % 20 == 0:
            print(f'[w{idx}] frame {f} ({f - f0 + 1}/{f1 - f0}) {time.time() - t0:.0f}s', flush=True)
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'worker':
        worker(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])); sys.exit(0)
    import motion
    nfr = int(round(motion.DURATION * motion.FPS))
    nw = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    nchunks = nw * 3
    bounds = [round(i * nfr / nchunks) for i in range(nchunks + 1)]
    jobs = [(i, bounds[i], bounds[i + 1]) for i in range(nchunks)]
    running = []
    while jobs or running:
        while jobs and len(running) < nw:
            i, a, b = jobs.pop(0)
            running.append(subprocess.Popen(['python3', __file__, 'worker', str(i), str(a), str(b)]))
        time.sleep(1)
        running = [r for r in running if r.poll() is None]
    with open(OUT + 'list.txt', 'w') as fh:
        for i in range(nchunks): fh.write(f"file 'chunk_{i:02d}.mkv'\n")
    print('frames', nfr, 'chunks done')
