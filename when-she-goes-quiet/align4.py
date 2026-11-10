import json, re, sys
sys.path.insert(0, ".")
from pocketsphinx import Decoder
from make_video import parse
from vo_script3 import VO3 as VO
a = open("vo2/vo.raw", "rb").read()
d = Decoder(samprate=16000, bestpath=False, beam=1e-120, wbeam=1e-100, pbeam=1e-120)
out = []
for i, ((s, e), txt) in enumerate(VO):
    words = [w for c in parse(txt) for w, _ in c]
    norm = [re.sub(r"[^a-z']", "", w.lower()) for w in words]
    s0, e0 = max(0, s - 0.15), min(145.08, e + 0.15)
    d.set_align_text(" ".join(norm)); d.start_utt()
    d.process_raw(a[int(s0 * 16000) * 2:int(e0 * 16000) * 2], full_utt=True); d.end_utt()
    segs = [(re.sub(r"\(\d+\)$", "", g.word), s0 + g.start_frame / 100, s0 + (g.end_frame + 1) / 100)
            for g in (d.seg() or []) if g.word not in ("<s>", "</s>", "<sil>", "[NOISE]")]
    ok = [x[0] for x in segs] == norm
    if not ok:  # fallback: spread by letters
        L = [len(w) + 2 for w in norm]; tot = sum(L); t = s; segs = []
        for w, l in zip(norm, L): segs.append((w, t, t + (e - s) * l / tot)); t += (e - s) * l / tot
    print(i, "aligned" if ok else "FALLBACK", " ".join(f"{w}@{a_:.2f}" for w, a_, _ in segs))
    out.append(dict(span=[s, e], words=[[w, round(a_, 3), round(b_, 3)] for w, a_, b_ in segs]))
json.dump(out, open("vo2/scene_words.json", "w"), indent=0)
