"""Voice-over tools (offline, pocketsphinx; `pip install pocketsphinx`).

  python3 align.py check  VO.mp3                       # split on pauses + rough transcript of each phrase
  python3 align.py score  VO.mp3 12.1-14.2 "cand a" "cand b" ...   # which wording fits that stretch best
  python3 align.py align  VO.mp3 scenes.py timings.json # word-level timings for every scene in scenes.SCENES

The rough transcript is noisy (it's a small offline model): use it to spot where the recording differs
from the script, then confirm wording with `score`. `align` assumes SCENES matches the audio exactly."""
import sys, os, re, json, subprocess, importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pocketsphinx import Decoder

def raw16k(path):
    return subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                          capture_output=True, check=True).stdout

def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout)

def phrases(path, dur, noise="-40dB", min_sil=0.18):
    out = subprocess.run(["ffmpeg", "-i", path, "-af", f"silencedetect=n={noise}:d={min_sil}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", out)]
    b = [0.0] + en; e = st + [dur]
    return [(x, y) for x, y in zip(b, e) if y - x > 0.1]

def norm(w): return re.sub(r"[^a-z']", "", w.lower().replace("’", "'"))

def aligner(): return Decoder(samprate=16000, bestpath=False, beam=1e-120, wbeam=1e-100, pbeam=1e-120)

def force(dec, audio, words, offset=0.0):
    dec.set_align_text(" ".join(words)); dec.start_utt(); dec.process_raw(audio, full_utt=True); dec.end_utt()
    segs = [(re.sub(r"\(\d+\)$", "", g.word), offset + g.start_frame / 100, offset + (g.end_frame + 1) / 100)
            for g in (dec.seg() or []) if g.word not in ("<s>", "</s>", "<sil>", "[NOISE]")]
    return segs if [s[0] for s in segs] == words else None

def cut(audio, s, e): return audio[int(s * 16000) * 2:int(e * 16000) * 2]

def cmd_check(path):
    a = raw16k(path); d = Decoder(samprate=16000)
    for s, e in phrases(path, duration(path)):
        d.start_utt(); d.process_raw(cut(a, s, e), full_utt=True); d.end_utt()
        print(f"{s:7.2f}-{e:7.2f}  {d.hyp().hypstr if d.hyp() else ''}")

def cmd_score(path, rng, cands):
    a = raw16k(path); s, e = map(float, rng.split("-")); d = aligner(); res = []
    for c in cands:
        d.set_align_text(" ".join(norm(w) for w in c.split())); d.start_utt(); d.process_raw(cut(a, s, e), full_utt=True); d.end_utt()
        res.append((d.hyp().best_score if d.hyp() else -1e12, c))
    for sc, c in sorted(res, reverse=True): print(f"{sc:10.4f}  {c}")

def load_scenes(p):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.abspath(p)))
    spec = importlib.util.spec_from_file_location("scenes", p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def cmd_align(path, scenes_py, out):
    from engine import parse
    m = load_scenes(scenes_py); a = raw16k(path); dur = duration(path)
    scene_words = [[w for c in parse(t) for w, _ in c] for t in m.SCENES]
    normed = [[norm(w) for w in ws] for ws in scene_words]
    missing = sorted({w for ws in normed for w in ws if w and w not in DICT})
    if missing: print("WARNING: not in pronunciation dictionary (alignment may fail):", missing)
    full = force(aligner(), a, [w for ws in normed for w in ws])
    if full is None: sys.exit("Full alignment failed: the text in SCENES probably differs from the recording. Run `check` and fix SCENES.")
    res, k = [], 0
    for i, ws in enumerate(normed):
        seg = full[k:k + len(ws)]; k += len(ws)
        s0, e0 = max(0, seg[0][1] - 0.2), min(dur, seg[-1][2] + 0.2)
        fine = force(aligner(), cut(a, s0, e0), ws, s0) or seg      # refine scene by scene
        span = [fine[0][1], fine[-1][2]]; rate = len(ws) / max(0.3, span[1] - span[0])
        flag = "  <-- CHECK (speaking rate looks off; text may not match audio)" if not 0.8 < rate < 5.5 else ""
        print(f"scene {i:2d}  {span[0]:7.2f}-{span[1]:7.2f}  {rate:4.1f} w/s{flag}")
        res.append(dict(span=span, words=[[w, round(s, 3), round(e, 3)] for w, s, e in fine]))
    json.dump(dict(audio_duration=dur, scenes=res), open(out, "w"), indent=0)
    print("wrote", out)

import pocketsphinx
DICT = {l.split()[0] for l in open(os.path.join(pocketsphinx.get_model_path(), "en-us", "cmudict-en-us.dict"))}

if __name__ == "__main__":
    c = sys.argv[1]
    if c == "check": cmd_check(sys.argv[2])
    elif c == "score": cmd_score(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif c == "align": cmd_align(*sys.argv[2:5])
    else: print(__doc__)
