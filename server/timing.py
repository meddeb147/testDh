"""Word timings for a voice-over.

English: offline forced alignment (pocketsphinx) of the exact script; words missing from the pronunciation
dictionary (names, numbers like 3:17) are interpolated between their neighbours.
Other languages (or if alignment fails): pause-aware proportional timing. Speech stretches between pauses are
detected with ffmpeg and the words are spread over speech time by character length, snapping sentence ends to pauses."""
import os, sys, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vme"))
import align as A


def _interp(words, found):
    """found: {index: (start, end)} -> full list of (start, end) with gaps filled linearly."""
    n = len(words); out = [None] * n
    for k, v in found.items(): out[k] = v
    known = sorted(found)
    for k in range(n):
        if out[k]: continue
        prev = max([j for j in known if j < k], default=None); nxt = min([j for j in known if j > k], default=None)
        a = found[prev][1] if prev is not None else (found[nxt][0] - 0.3 * (nxt - k) if nxt is not None else 0)
        b = found[nxt][0] if nxt is not None else a + 0.3 * (k - prev)
        lo = prev if prev is not None else k - 1; hi = nxt if nxt is not None else k + 1
        f0 = (k - lo - 1) / max(1, hi - lo - 1); f1 = (k - lo) / max(1, hi - lo - 1)
        out[k] = (a + (b - a) * f0, a + (b - a) * min(1, f1))
    return out


def english(path, words):
    audio = A.raw16k(path)
    normed = [A.norm(w) for w in words]
    keep = [k for k, w in enumerate(normed) if w and w in A.DICT]
    if len(keep) < 0.7 * len(words): return None
    seg = A.force(A.aligner(), audio, [normed[k] for k in keep])
    if seg is None: return None
    return _interp(words, {k: (s[1], s[2]) for k, s in zip(keep, seg)})


def proportional(path, words):
    """Fit words to the speech stretches between pauses: dynamic programming picks where each stretch starts so that
    (a) each stretch's length matches the text it holds at a steady speaking rate and (b) stretches tend to end on
    punctuation. Inside a stretch, words get time by character length."""
    dur = A.duration(path)
    ph = A.phrases(path, dur, noise="-38dB", min_sil=0.18) or [(0.0, dur)]
    ph = [(s, e) for s, e in ph if e - s > 0.12] or [(0.0, dur)]
    weight = [max(2, len(re.sub(r"\W", "", w))) + 1.0 for w in words]
    N, P = len(words), len(ph)
    if P > N: ph = ph[:N]; P = N
    rate = sum(weight) / sum(e - s for s, e in ph)
    cum = [0.0]
    for x in weight: cum.append(cum[-1] + x)
    punct = [bool(re.search(r"[.!?…,;:]['”\"]?$", w)) for w in words]
    INF = float("inf"); MAXW = 40
    best = [[INF] * (N + 1) for _ in range(P + 1)]; back = [[0] * (N + 1) for _ in range(P + 1)]
    best[0][0] = 0.0
    for p in range(1, P + 1):
        d = ph[p - 1][1] - ph[p - 1][0]
        for j in range(p, N - (P - p) + 1):
            for i in range(max(p - 1, j - MAXW), j):
                if best[p - 1][i] == INF: continue
                c = best[p - 1][i] + ((cum[j] - cum[i]) / rate - d) ** 2 / max(d, 0.3) + (0 if punct[j - 1] or j == N else 0.35)
                if c < best[p][j]: best[p][j] = c; back[p][j] = i
    bounds, j = [N], N
    for p in range(P, 0, -1): j = back[p][j]; bounds.append(j)
    bounds = bounds[::-1]
    out = []
    for p in range(P):
        i, j = bounds[p], bounds[p + 1]; s, e = ph[p]; tot = cum[j] - cum[i]
        for k in range(i, j):
            a = s + (e - s) * (cum[k] - cum[i]) / tot; b = s + (e - s) * (cum[k + 1] - cum[i]) / tot
            out.append((a, b))
    return out


def word_times(path, words, language="English"):
    """Returns (list of (start, end) per word, method)."""
    if language.lower().startswith("en"):
        try:
            r = english(path, words)
            if r: return r, "aligned"
        except Exception as e:  # noqa: BLE001 - fall back to pause timing
            print("alignment failed:", e)
    return proportional(path, words), "estimated"


def scene_timings(path, plan, language="English"):
    words = [w for sc in plan for w in sc["words"]]
    times, method = word_times(path, words, language)
    res, k = [], 0
    for sc in plan:
        n = len(sc["words"]); seg = times[k:k + n]
        res.append(dict(span=[seg[0][0], seg[-1][1]], words=[[w, round(a, 3), round(b, 3)] for w, (a, b) in zip(sc["words"], seg)]))
        k += n
    return dict(audio_duration=A.duration(path), scenes=res, method=method)
