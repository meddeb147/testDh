"""Synthesize SFX + soft music bed, mix with the voice-over."""
import json, subprocess, sys
import numpy as np

SR = 44100
rng = np.random.default_rng(7)

def tt(d): return np.arange(int(d * SR)) / SR
def noise(d): return rng.standard_normal(int(d * SR))
def norm(x): return x / (np.max(np.abs(x)) + 1e-9)

def lp(x, fc):
    """one-pole lowpass; fc may be array (time-varying)."""
    fc = np.broadcast_to(np.asarray(fc, float), x.shape)
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y

def hp(x, fc): return x - lp(x, fc)
def bp(x, lo, hi): return hp(lp(x, hi), lo)
def env(n, a, d):  # attack/decay (seconds) exponential-ish envelope
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)

def sine_sweep(f0, f1, d, decay):
    t = tt(d); f = f0 * (f1 / f0) ** (t / d); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(len(t), 0.002, decay)

def scribble():
    d = 0.38; x = bp(noise(d), 1800, 6500)
    flutter = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 15 * tt(d) + rng.uniform(0, 6)))
    return norm(x * flutter * np.sin(np.pi * tt(d) / d) ** 0.6)

def pop():
    return norm(sine_sweep(950, 260, 0.12, 0.05) + 0.3 * bp(noise(0.12), 2000, 6000) * env(int(0.12 * SR), 0.001, 0.01))

def thump(d=0.18, f=55):
    t = tt(d); return np.sin(2 * np.pi * (f + 40 * np.exp(-t * 30)) * t) * env(len(t), 0.004, 0.06)

def heartbeat():
    x = np.zeros(int(0.55 * SR)); a = thump(); b = thump(f=50) * 0.7
    x[:len(a)] += a; o = int(0.22 * SR); x[o:o + len(b)] += b
    return norm(lp(x, 300))

def whoosh(d=0.55, peak=2600):
    t = tt(d); shape = np.sin(np.pi * t / d) ** 2
    return norm(lp(noise(d), 250 + peak * shape) * shape)

def transition(): return whoosh(0.42, 1800)

def thunder():
    crack = hp(noise(0.08), 1500) * env(int(0.08 * SR), 0.001, 0.02)
    d = 2.2; rum = lp(lp(noise(d), 180), 180) * env(int(d * SR), 0.05, 0.7)
    rum *= 0.6 + 0.4 * lp(np.abs(noise(d)), 6) * 3
    x = np.zeros(int(d * SR)); x += norm(rum); x[:len(crack)] += 0.8 * norm(crack)
    return norm(x)

def rumble():
    d = 1.6; return norm(lp(lp(noise(d), 120), 120) * env(int(d * SR), 0.15, 0.6))

def crack():
    x = np.zeros(int(0.25 * SR))
    for k in range(4):
        o = int(rng.uniform(0, 0.15) * SR); b = hp(noise(0.03), 2500) * env(int(0.03 * SR), 0.0005, 0.006)
        x[o:o + len(b)] += b * rng.uniform(0.5, 1)
    return norm(x)

def bell(freqs, d=1.6, decay=0.5):
    t = tt(d); x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / (decay * (1 + 0.3 * k))) / (k + 1)
                       for k, f in enumerate(freqs))
    return norm(x * np.minimum(1, t / 0.003))

def chime(): return bell([1318.5, 1975.5, 2637 * 1.003, 3951], 1.8, 0.45)
def tick(): return norm(sine_sweep(1500, 1100, 0.05, 0.012))
def click(): return norm(np.concatenate([tick(), np.zeros(1000)]) + 0.5 * np.pad(pop(), (0, 0))[:len(tick()) + 1000])

def glass():
    c = crack(); r = bell([2489, 3720, 5130, 6620], 0.9, 0.12)
    x = np.zeros(max(len(c), len(r))); x[:len(c)] += c; x[:len(r)] += 0.5 * r
    return norm(x)

def crackle(d=1.1):
    x = np.zeros(int(d * SR))
    for _ in range(int(d * 28)):
        o = int(rng.uniform(0, d - 0.02) * SR); b = hp(noise(0.012), 1200) * env(int(0.012 * SR), 0.0003, 0.003)
        x[o:o + len(b)] += b * rng.uniform(0.2, 1)
    return norm(x * np.sin(np.pi * tt(d) / d) ** 0.4)

def fire():
    d = 1.3; base = lp(noise(d), 500) * env(int(d * SR), 0.12, 0.5)
    return norm(norm(base) + 0.6 * crackle(d))

def shield():
    s = bell([2093, 3135, 4186], 0.7, 0.15); w = whoosh(0.3, 3500)
    x = np.zeros(len(s)); x[:len(w)] += 0.5 * w; x += 0.6 * s
    return norm(x)

def water(d=2.0):
    base = lp(lp(noise(d), 600), 600) * np.sin(np.pi * tt(d) / d)
    x = norm(base)
    for _ in range(14):   # bubbles
        o = int(rng.uniform(0, d - 0.08) * SR); b = sine_sweep(rng.uniform(300, 600), rng.uniform(900, 1500), 0.06, 0.025)
        x[o:o + len(b)] += 0.25 * b
    return norm(x)

def rain(d=3.5):
    t = tt(d); fade = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 1.2)
    return norm(bp(noise(d), 1500, 8000) * fade * 0.6 + 0.5 * crackle(d) * fade)

def buzz():
    t = tt(0.28); x = np.sign(np.sin(2 * np.pi * 140 * t)) * env(len(t), 0.005, 0.12)
    return norm(lp(x, 900))

def squeeze():
    t = tt(0.35); f = 220 + 260 * t / 0.35 + 15 * np.sin(2 * np.pi * 18 * t)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.35))

def thud():
    t = tt(0.4); x = np.sin(2 * np.pi * (65 + 60 * np.exp(-t * 25)) * t) * env(len(t), 0.002, 0.09)
    x += 0.4 * lp(noise(0.4), 400) * env(len(t), 0.001, 0.04)
    return norm(x)

BANK = dict(scribble=scribble, pop=pop, heartbeat=heartbeat, whoosh=whoosh, transition=transition, thunder=thunder,
            rumble=rumble, crack=crack, chime=chime, tick=tick, click=click, glass=glass, crackle=crackle, fire=fire,
            shield=shield, water=water, rain=rain, buzz=buzz, squeeze=squeeze, thud=thud)
VOL = dict(scribble=0.55, pop=0.5, heartbeat=0.9, whoosh=0.55, transition=0.45, thunder=0.8, rumble=0.8, crack=0.5,
           chime=0.35, tick=0.4, click=0.6, glass=0.55, crackle=0.45, fire=0.6, shield=0.45, water=0.55,
           rain=0.35, buzz=0.35, squeeze=0.35, thud=0.8)

def music(total):
    """Soft, slow A-minor pad + sparse piano notes."""
    n = int(total * SR); t = np.arange(n) / SR; out = np.zeros(n)
    chords = [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [130.81, 196.0, 261.63], [196.0, 246.94, 293.66]]
    L = 4.8
    for k in range(int(total / L) + 1):
        s0 = k * L; ch = chords[k % 4]
        i0 = int(max(0, s0 - 1.0) * SR); i1 = min(n, int((s0 + L + 1.0) * SR))
        tl = t[i0:i1] - (s0 - 1.0)
        e = np.clip(np.minimum(tl / 1.5, (L + 2.0 - tl) / 1.5), 0, 1) ** 2
        for f in ch:
            for det in (-0.4, 0.4):
                out[i0:i1] += e * (np.sin(2 * np.pi * (f + det) * t[i0:i1]) + 0.25 * np.sin(4 * np.pi * (f + det) * t[i0:i1])) / 6
        bass = ch[0] / 2
        out[i0:i1] += 0.5 * e * np.sin(2 * np.pi * bass * t[i0:i1])
        # piano notes
        for j, f in enumerate([ch[2] * 2, ch[1] * 2, ch[0] * 2, ch[1] * 2]):
            st = int((s0 + j * 1.2 + 0.05) * SR)
            if st >= n: break
            d = min(2.4, (n - st) / SR); tn = np.arange(int(d * SR)) / SR
            note = (np.sin(2 * np.pi * f * tn) + 0.35 * np.sin(4 * np.pi * f * tn) + 0.12 * np.sin(6 * np.pi * f * tn))
            note *= np.minimum(1, tn / 0.004) * np.exp(-tn / 0.6) * 0.28
            out[st:st + len(note)] += note
    out = lp(out, 2200)
    fade = np.minimum(1, t / 1.5) * np.minimum(1, (total - t) / 1.8)
    return out * fade

def load_vo(path, total):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    v = np.frombuffer(raw, np.float32).astype(np.float64)
    out = np.zeros(int(total * SR)); out[:min(len(v), len(out))] = v[:len(out)]
    return out

def main(vo_path, events_path, total, out_wav):
    total = float(total)
    vo = load_vo(vo_path, total); vo = vo / np.max(np.abs(vo)) * 0.9
    sfx = np.zeros_like(vo); cache = {}
    events = json.load(open(events_path))
    last = {}
    for t0, name, g in sorted(events):
        if name == "scribble" and t0 - last.get(name, -9) < 0.12: continue   # avoid machine-gun scribbles
        last[name] = t0
        if name not in cache: cache[name] = BANK[name]()
        x = cache[name] if name != "scribble" else scribble()
        i = int(max(0, t0) * SR); j = min(len(sfx), i + len(x))
        sfx[i:j] += x[:j - i] * g * VOL[name]
    sfx *= 0.32
    mus = music(total)
    # sidechain duck: music dips while the voice is speaking
    venv = lp(np.abs(vo), 4); venv /= venv.max()
    duck = 1 - 0.55 * np.clip(venv * 4, 0, 1)
    vo_rms = np.sqrt(np.mean(vo[np.abs(vo) > 0.02] ** 2))
    mus = mus / (np.sqrt(np.mean(mus ** 2)) + 1e-9) * vo_rms * 0.16 * duck
    mix = vo + sfx + mus
    mix = np.tanh(mix * 1.1) / 1.1
    L = mix; R = mix.copy()
    data = (np.stack([L, R], 1) * 32767 * 0.95).astype(np.int16)
    import wave
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())
    print("events", len(events), "mixed", out_wav)

if __name__ == "__main__":
    main(*sys.argv[1:])
