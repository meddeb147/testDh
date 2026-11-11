"""Find the best moments of a video and cut them into stand-alone vertical clips."""
import re, subprocess, os

EMO = set("""never always nobody everything nothing gone dead alone love hate scared afraid lie lied truth secret why
until suddenly finally only last first heart cry tears blood dark silent silence warning danger""".split())


def scene_scores(plan):
    n = len(plan); out = []
    for i, sc in enumerate(plan):
        words = [re.sub(r"\W", "", w.lower()) for w in sc["words"]]
        s = len(sc["beats"]) + 0.6 * len(sc["hl"]) + 0.4 * sum(w in EMO for w in words)
        s += 1.5 * sc["question"] + 1.0 * (sc["neg"] is not None) + 1.5 * bool(sc["numbers"])
        s += 2.5 if i == 0 else 0                       # the hook
        s += 1.5 if i >= n - 3 and not sc["cta"] else 0  # the payoff
        s -= 6 if sc["cta"] else 0
        out.append(s)
    return out


def pick(plan, timings, n_clips=3, lo=15.0, hi=45.0):
    """Non-overlapping windows of consecutive scenes, lo..hi seconds, ranked by mean score (+ a bonus for starting
    on a strong line, because a clip lives or dies on its first second)."""
    sc = scene_scores(plan); spans = [s["span"] for s in timings["scenes"]]
    cands = []
    for a in range(len(plan)):
        for b in range(a, len(plan)):
            d = spans[b][1] - spans[a][0]
            if d > hi: break
            if d < lo or plan[b]["cta"]: continue
            score = sum(sc[a:b + 1]) / (b - a + 1) + 0.5 * sc[a] + 0.02 * d
            cands.append((score, a, b))
    chosen = []
    for score, a, b in sorted(cands, reverse=True):
        if all(b < x or a > y for _, x, y in chosen): chosen.append((score, a, b))
        if len(chosen) == n_clips: break
    out = []
    for s, a, b in sorted(chosen, key=lambda c: c[1]):
        end = spans[b][1] + 0.6
        if b + 1 < len(spans): end = min(end, spans[b + 1][0] - 0.05)     # never bleed into the next line
        out.append(dict(start=max(0, spans[a][0] - 0.15), end=end, scenes=[a, b], score=round(s, 2),
                        hook=" ".join(plan[a]["words"][:8])))
    return out


def cut(src_mp4, clips, out_dir, bg_hex="#000000"):
    paths = []
    for k, c in enumerate(clips, 1):
        d = c["end"] - c["start"]; out = os.path.join(out_dir, f"clip_{k}.mp4")
        vf = f"drawbox=x=0:y=0:w=iw:h=12:color={bg_hex}:t=fill,fade=t=in:st=0:d=0.25,fade=t=out:st={d - 0.35:.2f}:d=0.35"
        af = f"afade=t=in:st=0:d=0.15,afade=t=out:st={d - 0.4:.2f}:d=0.4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{c['start']:.2f}", "-t", f"{d:.2f}", "-i", src_mp4,
                        "-vf", vf, "-af", af, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac",
                        "-b:a", "160k", "-movflags", "+faststart", out], check=True)
        paths.append(out)
    return paths
