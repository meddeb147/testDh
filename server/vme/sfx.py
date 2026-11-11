"""Synthesized sound effects + mood music bed, mixed under the voice-over (no downloads needed).

  python3 sfx.py VO.mp3 events.json TOTAL_SECONDS out.wav [--mood tender|dark|playful|uplifting]

events.json is written by render.py: [[time, sound_name, gain], ...]. Sound names: see BANK at the bottom."""
import json, sys, wave, subprocess
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

def load_vo(path, total):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    v = np.frombuffer(raw, np.float32).astype(np.float64)
    out = np.zeros(int(total * SR)); out[:min(len(v), len(out))] = v[:len(out)]
    return out

BANK = dict(scribble=scribble, pop=pop, heartbeat=heartbeat, whoosh=whoosh, transition=transition, thunder=thunder,
            rumble=rumble, crack=crack, chime=chime, tick=tick, click=click, glass=glass, crackle=crackle, fire=fire,
            shield=shield, water=water, rain=rain, buzz=buzz, squeeze=squeeze, thud=thud, tear=tear, switch=switch,
            typing=typing, erase=erase, powerdown=powerdown, sand=sand, steps=steps, beeps=beeps, flatline=flatline)
VOL = dict(scribble=0.55, pop=0.5, heartbeat=0.9, whoosh=0.55, transition=0.45, thunder=0.8, rumble=0.8, crack=0.5,
           chime=0.35, tick=0.4, click=0.6, glass=0.55, crackle=0.45, fire=0.6, shield=0.45, water=0.55, rain=0.35,
           buzz=0.35, squeeze=0.35, thud=0.8, tear=0.5, switch=0.6, typing=0.45, erase=0.4, powerdown=0.45, sand=0.3,
           steps=0.6, beeps=0.22, flatline=0.2)

MOODS = {   # chord progression (Hz), seconds per chord, piano notes on/off, pad brightness, piano note gap
    "tender":    ([[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [130.81, 196.0, 261.63], [196.0, 246.94, 293.66]], 4.8, True, 2200, 1.2),
    "dark":      ([[110.0, 130.81, 155.56], [103.83, 123.47, 155.56], [110.0, 130.81, 164.81], [98.0, 116.54, 146.83]], 6.0, True, 900, 2.4),
    "playful":   ([[261.63, 329.63, 392.0], [349.23, 440.0, 523.25], [293.66, 349.23, 440.0], [392.0, 493.88, 587.33]], 2.4, True, 3500, 0.3),
    "uplifting": ([[261.63, 329.63, 392.0], [220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [196.0, 246.94, 293.66]], 4.0, True, 3000, 0.6),
}

def music(total, mood="tender"):
    chords, L, piano, bright, gap = MOODS[mood]
    n = int(total * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for k in range(int(total / L) + 1):
        s0 = k * L; ch = chords[k % 4]
        i0 = int(max(0, s0 - 1.0) * SR); i1 = min(n, int((s0 + L + 1.0) * SR)); tl = t[i0:i1] - (s0 - 1.0)
        e = np.clip(np.minimum(tl / 1.5, (L + 2.0 - tl) / 1.5), 0, 1) ** 2
        for f in ch:
            for det in (-0.4, 0.4):
                out[i0:i1] += e * (np.sin(2 * np.pi * (f + det) * t[i0:i1]) + 0.25 * np.sin(4 * np.pi * (f + det) * t[i0:i1])) / 6
        out[i0:i1] += 0.5 * e * np.sin(2 * np.pi * ch[0] / 2 * t[i0:i1])
        if piano:
            notes = [ch[2] * 2, ch[1] * 2, ch[0] * 2, ch[1] * 2]
            for j in range(int(L / gap)):
                f = notes[j % 4]; st = int((s0 + j * gap + 0.05) * SR)
                if st >= n: break
                d = min(2.4, (n - st) / SR); tn = np.arange(int(d * SR)) / SR
                nt = (np.sin(2 * np.pi * f * tn) + 0.35 * np.sin(4 * np.pi * f * tn) + 0.12 * np.sin(6 * np.pi * f * tn))
                out[st:st + len(nt)] += nt * np.minimum(1, tn / 0.004) * np.exp(-tn / (0.25 if mood == "playful" else 0.6)) * 0.28
    if mood == "dark":   # slow heartbeat-like pulse
        for s0 in np.arange(0, total, 1.6):
            st = int(s0 * SR); th = thump(0.3, 45)
            if st + len(th) < n: out[st:st + len(th)] += 0.5 * th
    out = lp(out, bright)
    return out * np.minimum(1, t / 1.5) * np.minimum(1, (total - t) / 1.8)

def main(vo_path, events_path, total, out_wav, mood="tender"):
    total = float(total)
    vo = load_vo(vo_path, total); vo = vo / np.max(np.abs(vo)) * 0.9
    sfx = np.zeros_like(vo); cache = {}; last = {}
    for t0, name, g in sorted(json.load(open(events_path))):
        if name not in BANK: print("unknown sound", name); continue
        if name == "scribble" and t0 - last.get(name, -9) < 0.12: continue
        last[name] = t0
        if name not in cache: cache[name] = BANK[name]()
        x = cache[name] if name != "scribble" else scribble()
        i = int(max(0, t0) * SR); j = min(len(sfx), i + len(x)); sfx[i:j] += x[:j - i] * g * VOL[name]
    sfx *= 0.32
    mus = music(total, mood)
    venv = lp(np.abs(vo), 4); venv /= venv.max(); duck = 1 - 0.55 * np.clip(venv * 4, 0, 1)
    vo_rms = np.sqrt(np.mean(vo[np.abs(vo) > 0.02] ** 2))
    mus = mus / (np.sqrt(np.mean(mus ** 2)) + 1e-9) * vo_rms * 0.16 * duck
    mix = np.tanh((vo + sfx + mus) * 1.1) / 1.1
    data = (np.stack([mix, mix], 1) * 32767 * 0.95).astype(np.int16)
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mood = sys.argv[sys.argv.index("--mood") + 1] if "--mood" in sys.argv else "tender"
    if mood in args: args.remove(mood)
    main(*args[:4], mood=mood)
