"""Render a video from a scenes file + timings.

  python3 render.py scenes.py timings.json OUT.mp4 --preview          # contact sheet PNG of every scene (fast check)
  python3 render.py scenes.py timings.json OUT.mp4 --frames 120 450   # specific frames as PNGs
  python3 render.py scenes.py timings.json OUT.mp4 --vo VO.mp3        # full render + SFX + music + mux + .srt

scenes.py defines SCENES, build(i, w, wf) and optionally THEME, MOOD, LABEL, TAIL (see references/scene-authoring.md)."""
import sys, os, json, subprocess, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import engine, sfx

def load(p):
    sys.path.insert(0, os.path.dirname(os.path.abspath(p)))
    spec = importlib.util.spec_from_file_location("scenes", p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def srt(P, path):
    def ts(s): mm, sec = divmod(s, 60); return f"00:{int(mm):02d}:{int(sec):02d},{int(round((sec % 1) * 1000)) % 1000:03d}"
    out, n = [], 1
    for p in P:
        idx = 0
        for c in p["cards"]:
            a = p["abs_t"][idx]; idx += len(c)
            b = p["abs_t"][idx] - 0.05 if idx < len(p["abs_t"]) else p["end"] - 0.05
            out.append(f"{n}\n{ts(a)} --> {ts(b)}\n{' '.join(w for w, _ in c)}\n"); n += 1
    open(path, "w").write("\n".join(out))

def main():
    a = sys.argv[1:]; scenes_py, timings_js, out = a[:3]
    m = load(scenes_py); tm = json.load(open(timings_js))
    engine.set_theme(getattr(m, "THEME", "romance"))
    total = tm["audio_duration"] + getattr(m, "TAIL", 1.8)
    label = getattr(m, "LABEL", ""); base = os.path.splitext(out)[0]
    if "--preview" in a or "--frames" in a:
        P = engine.plan(m.SCENES, tm["scenes"], total)
        if "--frames" in a: frames = [int(x) for x in a[a.index("--frames") + 1:] if x.isdigit()]
        else: frames = [int(engine.FPS * f) for p in P for f in (p["start"] + p["dur"] * 0.55, p["end"] - 0.3)]
        os.makedirs(base + "_frames", exist_ok=True)
        engine.render(base + "_frames/f", m.SCENES, tm["scenes"], m.build, total, label, preview=frames)
        if "--preview" in a:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-pattern_type", "glob", "-i", base + "_frames/f_*.png", "-vf",
                            "crop=1080:1250:0:250,scale=190:-1,tile=8x" + str((len(frames) + 7) // 8), "-frames:v", "1",
                            base + "_preview.png"], check=True)
            print("preview:", base + "_preview.png")
        return
    vo = a[a.index("--vo") + 1]
    ev = base + "_sfx_events.json"; silent = base + "_silent.mp4"; wav = base + "_mix.wav"
    P = engine.render(silent, m.SCENES, tm["scenes"], m.build, total, label, events_out=ev)
    sfx.main(vo, ev, total, wav, getattr(m, "MOOD", "tender"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest",
                    "-movflags", "+faststart", out], check=True)
    srt(P, base + ".srt")
    for f in (silent, wav): os.remove(f)
    print("done:", out, "and", base + ".srt", f"({total:.1f}s)")

if __name__ == "__main__":
    main()
