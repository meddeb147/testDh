import sys; sys.path.insert(0, ".")
import numpy as np, sfx
from sfx import SR, tt, noise, norm, lp, hp, bp, env, sine_sweep, crackle, thud, tick, BANK, VOL
rng = np.random.default_rng(11)
def tear():
    d = 0.45; x = bp(noise(d), 800, 5000) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 37 * tt(d)))) * np.sin(np.pi * tt(d) / d)
    return norm(x)
def switch(): return norm(np.concatenate([tick(), np.zeros(int(0.06 * SR)), 0.7 * tick()]))
def typing(d=1.4):
    x = np.zeros(int(d * SR))
    for k in range(int(d * 9)):
        o = int((k / 9 + rng.uniform(0, 0.04)) * SR); b = bp(noise(0.03), 1500, 6000) * env(int(0.03 * SR), 0.0005, 0.008)
        x[o:o + len(b)] += b * rng.uniform(0.6, 1)
    return norm(x)
def erase(): return norm(typing(0.9) * np.linspace(1, 0.5, int(0.9 * SR)))
def powerdown():
    return norm(sine_sweep(600, 70, 1.0, 0.5) + 0.2 * sine_sweep(1200, 140, 1.0, 0.4))
def sand(d=4.0):
    t = tt(d); return norm(bp(noise(d), 2500, 9000) * 0.5 * np.minimum(1, t / 0.5) * np.minimum(1, (d - t) / 1.0) + 0.4 * crackle(d) * 0.3)
def steps(n=8, gap=0.22):
    x = np.zeros(int((n * gap + 0.3) * SR)); s = thud()
    for k in range(n):
        o = int(k * gap * SR); x[o:o + len(s)] += s * (0.6 if k % 2 else 0.8) * (1 - k / (n + 2))
    return norm(lp(x, 900))
def beep(f=1000, d=0.14):
    t = tt(d); return np.sin(2 * np.pi * f * t) * np.minimum(1, t / 0.005) * np.minimum(1, (d - t) / 0.02)
def beeps():
    x = np.zeros(int(3.5 * SR))
    for k in range(4):
        b = beep(); o = int(k * 0.85 * SR); x[o:o + len(b)] += b
    return norm(x)
def flatline(d=2.6):
    t = tt(d); return norm(np.sin(2 * np.pi * 1000 * t) * np.minimum(1, t / 0.01) * np.minimum(1, (d - t) / 0.8))
for k, f, v in [("tear", tear, 0.5), ("switch", switch, 0.6), ("typing", typing, 0.45), ("erase", erase, 0.4),
                ("powerdown", powerdown, 0.45), ("sand", sand, 0.3), ("steps", steps, 0.6), ("beeps", beeps, 0.22),
                ("flatline", flatline, 0.2)]:
    BANK[k] = f; VOL[k] = v
if __name__ == "__main__":
    sfx.main(*sys.argv[1:])
