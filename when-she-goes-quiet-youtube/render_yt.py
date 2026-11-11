"""YouTube render: 16:9 visuals over the approved TikTok audio mix, plus a 10 s end screen.

  python3 render_yt.py --preview        # contact sheet
  python3 render_yt.py                  # full render -> when_she_goes_quiet_youtube.mp4 + .srt + thumbnail.png"""
import sys, os, json, subprocess, importlib.util, wave
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import engine
SK = [os.path.join(r, d, "viral-motion-video", "scripts") for r in ["/root/.claude/skills/synced"] for d in os.listdir(r)
      if os.path.isdir(os.path.join(r, d, "viral-motion-video"))][0]
sys.path.append(SK)
import numpy as np

ORIG_TOTAL = 146.866667   # length of the approved vertical video (audio mix ends here)
END_LEN = 10.0

spec = importlib.util.spec_from_file_location("scenes", os.path.join(HERE, "scenes.py")); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
engine.set_theme(m.THEME)
tm = json.load(open(os.path.join(HERE, "timings.json")))
engine.END_AT = ORIG_TOTAL; engine.END_TITLE = "Thank you for listening."
total = ORIG_TOTAL + END_LEN
out = os.path.join(HERE, "when_she_goes_quiet_youtube.mp4")

if "--preview" in sys.argv:
    P = engine.plan(m.SCENES, tm["scenes"], total)
    frames = [int(30 * f) for p in P for f in (p["start"] + p["dur"] * 0.55, p["end"] - 0.3)] + [int(30 * (total - 1))]
    d = "/tmp/claude-0/-home-user-testDh/8a769baf-a6dc-5c8a-9049-6f7dea6da9d3/scratchpad/yt"; os.makedirs(d, exist_ok=True)
    for f in os.listdir(d): os.remove(os.path.join(d, f))
    engine.render(d + "/f", m.SCENES, tm["scenes"], m.build, total, m.LABEL, preview=frames)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-pattern_type", "glob", "-i", d + "/f_*.png", "-vf", "scale=384:-1,tile=5x7",
                    "-frames:v", "1", d + "/preview.png"], check=True)
    print(d + "/preview.png"); sys.exit()

silent = out + ".silent.mp4"
P = engine.render(silent, m.SCENES, tm["scenes"], m.build, total, m.LABEL)
# audio: approved mix, then a soft music tail under the end screen
import sfx
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(HERE, "original_mix.m4a"), "-ac", "1", "-ar", "44100", "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.float32).astype(np.float64)
n = int(total * 44100); mix = np.zeros(n); mix[:len(a)] = a[:n]
mus = sfx.music(END_LEN + 2.0, getattr(m, "MOOD", "tender")); mus = mus / (np.abs(mus).max() + 1e-9) * 0.12
st = int((ORIG_TOTAL - 2.0) * 44100); mix[st:st + len(mus)] += mus[:n - st]
wav = out + ".wav"
with wave.open(wav, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(44100)
    w.writeframes((np.stack([mix, mix], 1).clip(-1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                "-movflags", "+faststart", out], check=True)
sys.path.insert(0, SK); import render as R
R.srt(P, os.path.splitext(out)[0] + ".srt")
os.remove(silent); os.remove(wav)
print("done", out, f"{total:.1f}s")
