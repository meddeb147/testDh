"""Hand-drawn motion-graphics engine for vertical (1080x1920) voice-over videos.

Scene files do `from engine import *` and define SCENES / build(); see references/scene-authoring.md.
Colors are mutable lists so set_theme() recolors everything, including function defaults."""
import math, json, subprocess
import numpy as np
import cairo

W, H, FPS = 1920, 1080, 30
# YouTube (16:9) build: scenes are authored in the 1080x1920 coordinate space and mapped into this frame
MAP_C, MAP_S, MAP_SRC = (960, 470), 1.2, (540, 765)

THEMES = {
    # name: (background, ink/lines/text, accent, label grey, light/disabled)
    "romance":    ((0.937, 0.914, 0.898), (0.11, 0.09, 0.09), (0.55, 0.05, 0.10), (0.55, 0.52, 0.50), (0.78, 0.75, 0.73)),
    "horror":     ((0.065, 0.065, 0.075), (0.86, 0.85, 0.82), (0.78, 0.06, 0.08), (0.45, 0.45, 0.47), (0.30, 0.30, 0.32)),
    "comedy":     ((0.99, 0.95, 0.80), (0.12, 0.12, 0.16), (0.95, 0.40, 0.10), (0.55, 0.50, 0.40), (0.82, 0.78, 0.65)),
    "motivation": ((0.96, 0.95, 0.93), (0.10, 0.11, 0.14), (0.85, 0.60, 0.10), (0.55, 0.55, 0.55), (0.80, 0.80, 0.78)),
    "mystery":    ((0.07, 0.10, 0.16), (0.88, 0.90, 0.94), (0.20, 0.75, 0.75), (0.45, 0.50, 0.58), (0.28, 0.32, 0.40)),
    "facts":      ((0.94, 0.96, 0.98), (0.08, 0.12, 0.20), (0.10, 0.45, 0.90), (0.50, 0.55, 0.62), (0.78, 0.82, 0.88)),
}
THEMES["relationships"] = THEMES["romance"]
BG, INK, RED, GREY, LIGHT = (list(c) for c in THEMES["romance"])   # RED = the accent color

def set_theme(theme):
    """theme: preset name or a dict {bg, ink, accent, grey, light} of RGB 0-1 triples."""
    vals = THEMES[theme] if isinstance(theme, str) else (theme["bg"], theme["ink"], theme["accent"], theme["grey"], theme["light"])
    for dst, src in zip((BG, INK, RED, GREY, LIGHT), vals): dst[:] = list(src)

_seed = [0]
CAP_Y, CAP_LH, CAP_FS, CAP_MAXW = 958, 64, 50, 1500


# ------------------------------------------------------------- drawing primitives, icons, effects

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))

def ease_io(x): x = clamp(x); return x * x * (3 - 2 * x)

def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3

def ease_back(x):
    x = clamp(x); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def arc(cx, cy, r, a0, a1, n=None, rx=None):
    rx = r if rx is None else rx
    n = n or max(12, int(abs(a1 - a0) / 4))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

def bez(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        out.append((u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
                    u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]))
    return out

def join(*parts):
    out = []
    for p in parts:
        out += p if not out else p[1:] if out[-1] == p[0] else p
    return out

def densify(poly, step=5.0):
    out = [poly[0]]
    for a, b in zip(poly, poly[1:]):
        d = math.dist(a, b); n = max(1, int(d / step))
        for i in range(1, n + 1):
            out.append((a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n))
    return out

def wobble(poly, amp=1.1):
    _seed[0] += 1; s = _seed[0] * 1.7
    pts = densify(poly); out = []; L = 0.0
    for i, p in enumerate(pts):
        if i: L += math.dist(pts[i - 1], p)
        out.append((p[0] + amp * math.sin(L * 0.045 + s), p[1] + amp * math.cos(L * 0.037 + s * 1.3)))
    return out

def heart_pts(cx, cy, size, n=80):
    k = size / 17.0
    return [(cx + k * 16 * math.sin(t) ** 3,
             cy - k * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)))
            for t in [2 * math.pi * i / n for i in range(n + 1)]]

class El:
    """Generic timed element. draw(ctx, p, t): p = reveal 0..1, t = scene time."""
    def __init__(self, t0, draw, dur=0.8, te=None, fade=0.35, anim=None, pivot=(540, 800)):
        self.t0, self.draw, self.dur, self.te, self.fade = t0, draw, dur, te, fade
        self.anim, self.pivot = anim, pivot

    def render(self, ctx, t):
        if t < self.t0: return
        p = clamp((t - self.t0) / self.dur)
        a = 1.0
        if self.te is not None:
            a = 1 - clamp((t - self.te) / self.fade)
            if a <= 0: return
        dx = dy = 0.0; sc = 1.0; rot = 0.0
        if self.anim:
            r = self.anim(t)
            dx, dy = r[0], r[1]
            if len(r) > 2: sc = r[2]
            if len(r) > 3: a *= r[3]
            if len(r) > 4: rot = r[4]
        ctx.save()
        ctx.push_group()
        px, py = self.pivot
        ctx.translate(px + dx, py + dy); ctx.rotate(rot); ctx.scale(sc, sc); ctx.translate(-px, -py)
        self.draw(ctx, p, t)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
        ctx.restore()

def stroke_partial(ctx, polys, p, color=INK, width=4.0):
    lens = [sum(math.dist(a, b) for a, b in zip(q, q[1:])) for q in polys]
    total = sum(lens) or 1; remain = total * p
    ctx.set_source_rgb(*color); ctx.set_line_width(width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    for q, L in zip(polys, lens):
        if remain <= 0: break
        ctx.move_to(*q[0]); acc = 0.0
        for a, b in zip(q, q[1:]):
            d = math.dist(a, b)
            if acc + d >= remain:
                f = (remain - acc) / d if d else 0
                ctx.line_to(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f); break
            ctx.line_to(*b); acc += d
        ctx.stroke(); remain -= L

def _S(polys, t0, dur=None, color=INK, width=4.0, wob=True, **kw):
    polys = [wobble(q) if wob else densify(q) for q in polys]
    if dur is None:
        dur = clamp(sum(math.dist(a, b) for q in polys for a, b in zip(q, q[1:])) / 900, 0.35, 1.3)
    return El(t0, lambda ctx, p, t: stroke_partial(ctx, polys, ease_io(p), color, width), dur, **kw)

def fill_poly(ctx, poly, color):
    ctx.set_source_rgb(*color); ctx.move_to(*poly[0])
    for q in poly[1:]: ctx.line_to(*q)
    ctx.close_path(); ctx.fill()

def _F(poly, t0, center, color=RED, beat=False, flicker=False, **kw):
    """Filled shape that pops in with overshoot."""
    cx, cy = center
    def d(ctx, p, t):
        s = max(ease_back(p), 1e-3)
        if beat: s *= 1 + 0.06 * max(0, math.sin((t - t0) * 6.0)) ** 8
        sy = s
        if flicker: sy *= 1 + 0.05 * math.sin(t * 13) + 0.03 * math.sin(t * 21)
        ay = poly_bottom if flicker else cy
        ctx.save(); ctx.translate(cx, ay); ctx.scale(s, sy); ctx.translate(-cx, -ay)
        fill_poly(ctx, poly, color); ctx.restore()
    poly_bottom = max(q[1] for q in poly)
    return El(t0, d, 0.45, **kw)

def man(x, y, s=1.0):
    hr = 26 * s; hy = y - 150 * s
    head = arc(x, hy, hr, -90, 270)
    L = join([(x - 8*s, hy + hr)], [(x - 8*s, y - 108*s)],
             bez((x - 8*s, y - 108*s), (x - 8*s, y - 70*s), (x - 52*s, y - 55*s), (x - 52*s, y)))
    R = [(2*x - px, py) for px, py in L]
    return [head, L, R]

def woman(x, y, s=1.0):
    hr = 24 * s; hy = y - 150 * s
    head = arc(x, hy, hr, -90, 270)
    hair = join(bez((x - 34*s, y - 98*s), (x - 40*s, y - 140*s), (x - 40*s, hy - 30*s), (x, hy - 34*s)),
                bez((x, hy - 34*s), (x + 40*s, hy - 30*s), (x + 40*s, y - 140*s), (x + 34*s, y - 98*s)))
    L = bez((x - 10*s, y - 118*s), (x - 18*s, y - 70*s), (x - 50*s, y - 60*s), (x - 48*s, y))
    R = [(2*x - px, py) for px, py in L]
    return [head, hair, L, R]

def head_profile(x, y, s=1.0):
    P = lambda a, b: (x + a*s, y + b*s)
    return [join(bez(P(-55, 115), P(-55, 60), P(-90, 30), P(-90, -15)),
                 bez(P(-90, -15), P(-90, -75), P(-45, -110), P(5, -110)),
                 bez(P(5, -110), P(60, -110), P(85, -60), P(80, -10)),
                 [P(80, -10), P(96, 22), P(82, 28), P(86, 44), P(78, 50), P(80, 60)],
                 bez(P(80, 60), P(78, 78), P(60, 82), P(48, 80)),
                 [P(48, 80), P(46, 115)])]

def heart(x, y, size): return [heart_pts(x, y, size)]

def broken_heart(x, y, size):
    k = size / 17
    crack = [(x, y - 5*k), (x - 4*k, y + 1*k), (x + 3*k, y + 5*k), (x - 2*k, y + 10*k), (x, y + 15*k)]
    return heart(x, y, size), [crack]

def bolt(x, y, s=1.0):
    pts = [(0, -45), (-20, 6), (-2, 6), (-12, 45), (20, -8), (2, -8), (12, -45), (0, -45)]
    return [[(x + a*s, y + b*s) for a, b in pts]]

def cloud(x, y, s=1.0):
    P = lambda a, b: (x + a*s, y + b*s)
    return [join([P(58, 24), P(-52, 24)]),
            arc(x - 46*s, y + 6*s, 18*s, 90, 270),
            arc(x - 4*s, y - 8*s, 30*s, 195, 345),
            arc(x + 44*s, y + 5*s, 19*s, 250, 450)]

def arrow(x0, y0, x1, y1, head=18):
    a = math.atan2(y1 - y0, x1 - x0)
    h1 = (x1 - head * math.cos(a - 0.5), y1 - head * math.sin(a - 0.5))
    h2 = (x1 - head * math.cos(a + 0.5), y1 - head * math.sin(a + 0.5))
    return [[(x0, y0), (x1, y1)], [h1, (x1, y1), h2]]

def qmark(x, y, s=1.0):
    return [join(arc(x, y - 18*s, 16*s, 190, 395), [(x + 6*s, y + 0*s), (x, y + 6*s), (x, y + 16*s)]),
            arc(x, y + 30*s, 2.5*s, 0, 360, 10)]

def gear(x, y, r=22):
    out = [arc(x, y, r, 0, 360), arc(x, y, r * 0.38, 0, 360)]
    for i in range(8):
        a = math.radians(i * 45)
        out.append([(x + r * math.cos(a), y + r * math.sin(a)),
                    (x + (r + 9) * math.cos(a), y + (r + 9) * math.sin(a))])
    return out

def flame(x, y, s=1.0):
    P = lambda a, b: (x + a*s, y + b*s)
    return join(bez(P(0, -70), P(14, -38), P(36, -18), P(36, 18)),
                bez(P(36, 18), P(36, 50), P(-36, 50), P(-36, 18)),
                bez(P(-36, 18), P(-36, -14), P(-6, -36), P(0, -70)))

def shield(x, y, s=1.0):
    P = lambda a, b: (x + a*s, y + b*s)
    return [join([P(-42, -40), P(0, -54), P(42, -40), P(42, 2)],
                 bez(P(42, 2), P(42, 34), P(18, 52), P(0, 60)),
                 bez(P(0, 60), P(-18, 52), P(-42, 34), P(-42, 2)), [P(-42, 2), P(-42, -40)])]

def boat(x, y, s=1.0):
    P = lambda a, b: (x + a*s, y + b*s)
    return [[P(-110, 0), P(110, 0), P(82, 52), P(-82, 52), P(-110, 0)],
            [P(0, 0), P(0, -150)],
            [P(6, -140), P(70, -20), P(6, -20), P(6, -140)]]

def waves(x, y, w, amp=10, n=3, rows=1, gap=26):
    out = []
    for r in range(rows):
        out.append([(x - w/2 + w * i / 80, y + r*gap + amp * math.sin(2 * math.pi * n * i / 80 + r))
                    for i in range(81)])
    return out

def target(x, y):
    return [arc(x, y, 50, 0, 360), arc(x, y, 34, 0, 360),
            [(x, y - 64), (x, y - 50)], [(x, y + 50), (x, y + 64)],
            [(x - 64, y), (x - 50, y)], [(x + 50, y), (x + 64, y)]]

def hand(x, y):
    out = []
    for i, (dx, h) in enumerate([(-27, 44), (-9, 56), (9, 56), (27, 46)]):
        fx = x + dx
        out.append(join([(fx - 7, y)], [(fx - 7, y - h)], arc(fx, y - h, 7, 180, 360), [(fx + 7, y)]))
    return out

def moon(x, y, r=26):
    return [join(arc(x, y, r, 70, 290), arc(x + r * 0.45, y - r * 0.1, r * 0.82, 250, 110))]

def door(x, y, w=70, h=125):
    return [[(x - w/2, y), (x - w/2, y - h), (x + w/2, y - h), (x + w/2, y), (x - w/2, y)],
            arc(x + w/2 - 12, y - h/2, 2.5, 0, 360, 8)]

def eye(x, y, s=1.0):
    P = lambda a, b: (x + a*s, y + b*s)
    return [join(bez(P(-55, 0), P(-25, -32), P(25, -32), P(55, 0)),
                 bez(P(55, 0), P(25, 32), P(-25, 32), P(-55, 0))),
            arc(x, y, 17*s, 0, 360), arc(x, y, 5*s, 0, 360, 10)]

def bubble(x, y, w=110, h=64):
    l, r, t, b = x - w/2, x + w/2, y - h/2, y + h/2
    return [[(l + 10, b), (l, b), (l, t), (r, t), (r, b), (l + 34, b), (l + 14, b + 20), (l + 14, b)]]

def ground(x, y, w):
    return [[(x - w/2, y), (x + w/2, y)]]

def pit(x, y):
    return [join([(x - 230, y), (x - 70, y), (x - 70, y + 70)],
                 bez((x - 70, y + 70), (x - 70, y + 100), (x + 70, y + 100), (x + 70, y + 70)),
                 [(x + 70, y + 70), (x + 70, y), (x + 230, y)])]

def plane(x, y, s=1.0):
    P = lambda a, b: (x + a*s, y + b*s)
    return [[P(-60, 0), P(60, -45), P(25, 50), P(5, 15), P(-60, 0)], [P(60, -45), P(5, 15)],
            [P(5, 15), P(0, 42), P(25, 50)]]

def crossx(x, y, r=26):
    return [[(x - r, y - r), (x + r, y + r)], [(x + r, y - r), (x - r, y + r)]]

def parse(text):
    cards, hl = [], False
    for card in text.split("|"):
        words = []
        for tok in card.split():
            start = tok.startswith("*"); tok = tok.lstrip("*")
            if start: hl = True
            end = tok.endswith("*") or tok.rstrip("…?.,:”\"").endswith("*")
            clean = tok.replace("*", "")
            words.append((clean, hl or start))
            if end: hl = False
        cards.append(words)
    return cards

def S(polys, t0, sfx="scribble", g=0.16, **kw):
    e = _S(polys, t0, **kw); e.sfx = (sfx, g) if kw.get("dur", 1) > 0.05 else None; return e

def F(poly, t0, center, sfx="pop", g=0.5, **kw):
    e = _F(poly, t0, center, **kw); e.sfx = (sfx, g); return e

def E_(t0, draw, dur=0.8, sfx=None, g=0.5, **kw):
    e = El(t0, draw, dur, **kw); e.sfx = (sfx, g) if sfx else None; return e

def cue(t, name, g=0.5):
    e = El(t, lambda c, p, tt: None, 0.01); e.sfx = (name, g); return e

def bulb(x, y):
    return [join(arc(x, y, 62, 130, 410)),
            [(x - 40, y + 47), (x - 30, y + 95), (x + 30, y + 95), (x + 40, y + 47)],
            [(x - 28, y + 110), (x + 28, y + 110)], [(x - 20, y + 125), (x + 20, y + 125)],
            [(x - 14, y + 40), (x - 8, y - 5), (x, y + 15), (x + 8, y - 5), (x + 14, y + 40)]]

def rays(x, y, r0, r1, n=10, a0=0):
    return [[(x + r0 * math.cos(a0 + 2 * math.pi * k / n), y + r0 * math.sin(a0 + 2 * math.pi * k / n)),
             (x + r1 * math.cos(a0 + 2 * math.pi * k / n), y + r1 * math.sin(a0 + 2 * math.pi * k / n))] for k in range(n)]

def umbrella(x, y, r=150):
    scallops = []
    for k in range(4):
        cx = x - r + r / 4 + k * r / 2
        scallops += arc(cx, y, r / 4, 180, 360)[::-1] if False else arc(cx, y, r / 4, 180, 360)
    return [arc(x, y, r, 180, 360), [(x - r, y)] + scallops,
            join([(x, y - r), (x, y + 150)], arc(x - 14, y + 150, 14, 0, 180))]

def anchor(x, y, s=1.0):
    P = lambda a, b: (x + a * s, y + b * s)
    return [arc(x, y - 62 * s, 12 * s, 0, 360), [P(0, -50), P(0, 52)], [P(-28, -30), P(28, -30)],
            arc(x, y + 2 * s, 50 * s, 20, 160), [P(36, 14), P(47, 19), P(52, 6)], [P(-36, 14), P(-47, 19), P(-52, 6)]]

def sun(x, y, r=42): return [arc(x, y, r, 0, 360)]

def dots_bubble(x, y):
    return bubble(x, y, 120, 70) + [arc(x - 25 + 25 * k, y, 4, 0, 360, 10) for k in range(3)]

def rain(x0, x1, y0, y1, t_on, t_off=None, n=26, speed=650, color=INK, alpha=0.45):
    rng = np.random.default_rng(int(x0 + y0))
    xs, ph = rng.uniform(x0, x1, n), rng.uniform(0, 1, n)
    def d(ctx, p, t):
        a = clamp((t - t_on) / 0.5) * (1 - clamp((t - t_off) / 0.8) if t_off else 1)
        if a <= 0: return
        ctx.set_line_width(2.5); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for x, f in zip(xs, ph):
            yy = y0 + ((t * speed / (y1 - y0) + f) % 1.0) * (y1 - y0)
            ctx.set_source_rgba(*color, alpha * a * min(1, (y1 - yy) / 60))
            ctx.move_to(x - 4, yy); ctx.line_to(x - 9, yy + 22); ctx.stroke()
    return El(t_on, d, 0.01)

def sparks(x0, y0, x1, y1, t_on, t_off, n=7):
    def d(ctx, p, t):
        if t > t_off + 0.6: return
        for k in range(n):
            f = ((t - t_on) * 1.3 + k / n) % 1.0
            if t > t_off and f < (t - t_off) * 1.3: continue
            x = x0 + (x1 - x0) * f; y = y0 + (y1 - y0) * f - 60 * math.sin(f * math.pi)
            ctx.set_source_rgba(*RED, 0.9 * (1 - f)); ctx.arc(x, y, 5 * (1 - f) + 2, 0, 2 * math.pi); ctx.fill()
    return El(t_on, d, 0.01)

def rings(x, y, t_on, color=RED, r0=45, span=110, t_off=None):
    def d(ctx, p, t):
        a = 1 - clamp((t - t_off) / 0.4) if t_off else 1
        for k in range(3):
            ph = ((t - t_on) * 0.6 + k / 3) % 1.0
            ctx.set_source_rgba(*color, 0.55 * (1 - ph) * a); ctx.set_line_width(3)
            ctx.arc(x, y, r0 + span * ph, 0, 2 * math.pi); ctx.stroke()
    return El(t_on, d, 0.01)

def slide(t0, dx, dur=0.9, dy=0.0):
    return lambda t: (dx * ease_io((t - t0) / dur), dy * ease_io((t - t0) / dur))

def shake(t0, amp=6, dur=0.6):
    return lambda t: (amp * math.sin(t * 60) * (1 - clamp((t - t0) / dur)) if t > t0 else 0, 0)

def beat_heart(x, y, size, t0, **kw):
    return F(heart_pts(x, y, size), t0, (x, y), beat=True, sfx="heartbeat", g=0.55, **kw)

def draw_caption(ctx, card, times, t, alpha=1.0):
    ctx.select_font_face("Inter SemiBold", 0, 0); ctx.set_font_size(CAP_FS)
    sp = ctx.text_extents(" ").x_advance
    lines, cur, cw = [], [], 0
    for k, (wd, hl) in enumerate(card):
        wl = ctx.text_extents(wd).x_advance
        if cur and cw + sp + wl > CAP_MAXW: lines.append((cur, cw)); cur, cw = [], 0
        cur.append((wd, hl, wl, times[k])); cw += (sp if cw else 0) + wl
    lines.append((cur, cw))
    y0 = CAP_Y - (len(lines) - 1) * CAP_LH / 2
    pw = max(lw for _, lw in lines) + 70
    ctx.new_sub_path(); r = 18; x0p, y0p, hp = W / 2 - pw / 2, y0 - 52, CAP_LH * (len(lines) - 1) + 82
    ctx.arc(x0p + pw - r, y0p + r, r, -math.pi / 2, 0); ctx.arc(x0p + pw - r, y0p + hp - r, r, 0, math.pi / 2)
    ctx.arc(x0p + r, y0p + hp - r, r, math.pi / 2, math.pi); ctx.arc(x0p + r, y0p + r, r, math.pi, 1.5 * math.pi); ctx.close_path()
    ctx.set_source_rgba(*INK, 0.06 * alpha * clamp((t - times[0] + 0.1) / 0.2)); ctx.fill()
    for li, (ws, lw) in enumerate(lines):
        x = W / 2 - lw / 2; y = y0 + li * CAP_LH
        for j, (wd, hl, wl, wt) in enumerate(ws):
            p = clamp((t - wt) / 0.16)
            if p > 0:
                ctx.save()
                s = 1 + (0.18 * (1 - ease_out(clamp((t - wt) / 0.3))) if hl else 0)
                ctx.translate(x + wl / 2, y - 18); ctx.scale(s, s); ctx.translate(-(x + wl / 2), -(y - 18))
                ctx.set_source_rgba(*(RED if hl else INK), p * alpha)
                ctx.move_to(x, y + 14 * (1 - ease_out(p))); ctx.show_text(wd); ctx.restore()
                if hl:   # hand-drawn underline sweeping under highlighted words
                    u = ease_io((t - wt - 0.05) / 0.3)
                    ext = wl + (sp if j + 1 < len(ws) and ws[j + 1][1] else 0)
                    if u > 0:
                        ctx.set_source_rgba(*RED, 0.85 * alpha); ctx.set_line_width(4.5); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                        ctx.move_to(x, y + 16)
                        n = 12
                        for q in range(1, n + 1):
                            f = q / n * u
                            ctx.line_to(x + ext * f, y + 16 + 2.5 * math.sin(f * 7 + li))
                        ctx.stroke()
            x += wl + sp

def flag(x, y):
    pole = [(x, y), (x, y - 230)]
    top = [(x + 4 + 110 * i / 30, y - 225 + 7 * math.sin(i / 30 * 2 * math.pi)) for i in range(31)]
    bot = [(x + 4 + 110 * i / 30, y - 160 + 7 * math.sin(i / 30 * 2 * math.pi)) for i in range(31)][::-1]
    return [pole, top + [top[-1], bot[0]] + bot + [(x + 4, y - 225)]]

def lifebuoy(cx, cy, R=95, r=55):
    def d(ctx, p, t):
        s = max(ease_back(p), 1e-3)
        ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s); ctx.rotate(0.25 * math.sin(t * 1.5))
        for k in range(4):
            a0 = k * math.pi / 2 + math.pi / 8; a1 = a0 + math.pi / 4
            ctx.new_path(); ctx.arc(0, 0, R, a0, a1); ctx.arc_negative(0, 0, r, a1, a0); ctx.close_path()
            ctx.set_source_rgb(*RED); ctx.fill()
        ctx.set_source_rgb(*INK); ctx.set_line_width(4)
        ctx.new_path(); ctx.arc(0, 0, R, 0, 2 * math.pi); ctx.stroke()
        ctx.new_path(); ctx.arc(0, 0, r, 0, 2 * math.pi); ctx.stroke()
        ctx.restore()
    return d

def ear(x, y, s=1.0):
    P = lambda a, b: (x + a * s, y + b * s)
    return [join(bez(P(-30, 10), P(-40, -60), P(40, -70), P(35, 0)),
                 bez(P(35, 0), P(32, 30), P(5, 35), P(5, 60)), bez(P(5, 60), P(5, 80), P(-20, 85), P(-25, 70))),
            bez(P(-12, 0), P(-15, -30), P(20, -35), P(15, 5))]

def candle(x, y):
    return [[(x - 18, y), (x - 18, y - 90), (x + 18, y - 90), (x + 18, y), (x - 18, y)], [(x, y - 90), (x, y - 102)]]

def toggle(cx, cy, t_flip):
    def d(ctx, p, t):
        k = ease_io((t - t_flip) / 0.45); s = max(ease_back(p), 1e-3)
        ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s)
        w, h = 170, 84; r = h / 2
        col = tuple(RED[i] * (1 - k) + LIGHT[i] * k for i in range(3))
        ctx.new_path(); ctx.arc(-w / 2 + r, 0, r, math.pi / 2, 3 * math.pi / 2); ctx.arc(w / 2 - r, 0, r, -math.pi / 2, math.pi / 2)
        ctx.close_path(); ctx.set_source_rgb(*col); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke()
        kx = (w / 2 - r) * (1 - 2 * k)
        ctx.new_path(); ctx.arc(kx, 0, r - 9, 0, 2 * math.pi); ctx.set_source_rgb(1, 1, 1); ctx.fill_preserve()
        ctx.set_source_rgb(*INK); ctx.set_line_width(3); ctx.stroke(); ctx.restore()
    return d

def toolbox(x, y):
    return [[(x - 70, y), (x - 70, y - 70), (x + 70, y - 70), (x + 70, y), (x - 70, y)],
            [(x - 25, y - 70), (x - 25, y - 92), (x + 25, y - 92), (x + 25, y - 70)], [(x - 70, y - 42), (x + 70, y - 42)]]

def shower(x, y):
    return [[(x - 120, y - 140), (x - 120, y - 110), (x - 20, y - 110)], arc(x, y - 92, 26, 180, 360),
            [(x - 26, y - 92), (x + 26, y - 92)]]

def phone_typing(cx, cy, msg, t_type, t_del, t_send=None):
    def d(ctx, p, t):
        s = max(ease_back(p), 1e-3)
        ctx.save(); ctx.translate(cx, cy); ctx.scale(s * 1.35, s * 1.35)
        w, h, r = 260, 440, 34
        ctx.new_path(); ctx.arc(-w / 2 + r, -h / 2 + r, r, math.pi, 1.5 * math.pi); ctx.arc(w / 2 - r, -h / 2 + r, r, 1.5 * math.pi, 2 * math.pi)
        ctx.arc(w / 2 - r, h / 2 - r, r, 0, 0.5 * math.pi); ctx.arc(-w / 2 + r, h / 2 - r, r, 0.5 * math.pi, math.pi); ctx.close_path()
        ctx.set_source_rgb(1, 1, 1); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke()
        ctx.move_to(-30, -h / 2 + 22); ctx.line_to(30, -h / 2 + 22); ctx.stroke()
        n = int(len(msg) * clamp((t - t_type) / 1.3))
        if t > t_del: n = int(n * (1 - clamp((t - t_del) / 0.9)))
        txt = msg[:n]
        ctx.select_font_face("Inter Medium", 0, 0); ctx.set_font_size(24)
        lines, cur = [], ""
        for wd in txt.split(" "):
            if ctx.text_extents(cur + " " + wd).x_advance > 190 and cur: lines.append(cur); cur = wd
            else: cur = (cur + " " + wd).strip()
        lines.append(cur)
        y0 = h / 2 - 70 - 34 * (len(lines) - 1)
        if txt:
            bw = max(ctx.text_extents(l).x_advance for l in lines) + 30
            ctx.set_source_rgba(*RED, 0.12); ctx.rectangle(w / 2 - 22 - bw, y0 - 34, bw, 34 * len(lines) + 18); ctx.fill()
        ctx.set_source_rgb(*INK)
        for k, l in enumerate(lines):
            ctx.move_to(w / 2 - 37 - ctx.text_extents(l).x_advance, y0 + 34 * k); ctx.show_text(l)
        if (t * 2) % 1 < 0.5:   # blinking cursor
            ctx.rectangle(w / 2 - 34, y0 + 34 * (len(lines) - 1) - 24, 3, 28); ctx.fill()
        ctx.restore()
    return d

def warning(x, y):
    return [[(x, y - 80), (x + 85, y + 65), (x - 85, y + 65), (x, y - 80)], [(x, y - 25), (x, y + 20)], arc(x, y + 42, 4, 0, 360, 10)]

def mask_face(cx, cy, t_reveal):
    def d(ctx, p, t):
        k = ease_io((t - t_reveal) / 0.9)
        stroke_partial(ctx, [wobble(arc(cx, cy, 110, -90, 270))], ease_io(p), INK, 4)
        if p < 1: return
        # eyes
        for ex in (-38, 38):
            ctx.set_source_rgb(*INK); ctx.arc(cx + ex, cy - 25, 6, 0, 2 * math.pi); ctx.fill()
        # mouth morph: smile -> frown
        my = cy + 45; bend = 28 * (1 - 2 * k)
        ctx.set_line_width(4.5); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(cx - 40, my); ctx.curve_to(cx - 15, my + bend, cx + 15, my + bend, cx + 40, my); ctx.stroke()
        if k > 0.6:   # tear
            ty = cy - 5 + 70 * ease_in((t - t_reveal - 0.6) / 1.2) if False else cy - 5 + 70 * clamp((t - t_reveal - 0.55) / 1.4)
            a = 1 - clamp((t - t_reveal - 1.6) / 0.4)
            ctx.save(); ctx.translate(cx + 38, ty); ctx.scale(0.35, 0.35)
            ctx.push_group(); fill_poly(ctx, [(x - cx, y - cy) for x, y in flame(cx, cy, 0.6)], (0.35, 0.5, 0.75)); ctx.pop_group_to_source(); ctx.paint_with_alpha(max(a, 0))
            ctx.restore()
        # mask sliding off (smiling paper mask)
        mx = cx + 420 * ease_in_(k); ma = 1 - k
        if ma > 0:
            ctx.save(); ctx.translate(mx - cx, 30 * k); ctx.rotate(0.3 * k)
            ctx.new_path(); ctx.arc(cx, cy, 104, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, ma); ctx.fill()
            ctx.set_source_rgba(*RED, ma); ctx.set_line_width(4); ctx.arc(cx, cy, 104, 0, 2 * math.pi); ctx.stroke()
            for ex in (-38, 38):
                ctx.move_to(cx + ex - 16, cy - 22); ctx.curve_to(cx + ex - 8, cy - 36, cx + ex + 8, cy - 36, cx + ex + 16, cy - 22); ctx.stroke()
            ctx.move_to(cx - 50, cy + 35); ctx.curve_to(cx - 20, cy + 75, cx + 20, cy + 75, cx + 50, cy + 35); ctx.stroke()
            ctx.restore()
    return d

def ease_in_(x): x = clamp(x); return x * x

def battery(cx, cy, t_drain, t_end):
    def d(ctx, p, t):
        s = max(ease_back(p), 1e-3); ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s)
        ctx.set_source_rgb(*INK); ctx.set_line_width(4.5)
        ctx.rectangle(-110, -50, 200, 100); ctx.stroke(); ctx.rectangle(92, -18, 16, 36); ctx.fill()
        level = 1 - clamp((t - t_drain) / (t_end - t_drain))
        bars = math.ceil(level * 4 - 1e-6)
        for b in range(bars):
            col = RED if bars == 1 else INK
            ctx.set_source_rgb(*col)
            if bars == 1 and (t * 3) % 1 < 0.5: continue
            ctx.rectangle(-98 + b * 47, -38, 38, 76); ctx.fill()
        ctx.restore()
    return d

def hourglass(cx, cy, t0, t1):
    def d(ctx, p, t):
        s = max(ease_back(p), 1e-3); ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s)
        f = clamp((t - t0) / (t1 - t0))
        ctx.set_source_rgb(*RED)
        ht = 90 * (1 - f) ** 0.8   # top sand height
        if ht > 1:
            ctx.move_to(-70 * ht / 90 * 0.95, -ht - 5 + 0); ctx.line_to(70 * ht / 90 * 0.95, -ht - 5); ctx.line_to(0, -5); ctx.close_path()
            ctx.fill()
        hb = 90 * f ** 0.8
        if hb > 1:
            ctx.move_to(-70, 95); ctx.line_to(70, 95); ctx.line_to(70 * (1 - hb / 95), 95 - hb); ctx.line_to(-70 * (1 - hb / 95), 95 - hb); ctx.close_path(); ctx.fill()
        if 0 < f < 1:
            ctx.set_line_width(3); ctx.move_to(0, -5); ctx.line_to(0, 95 - hb); ctx.stroke()
        ctx.set_source_rgb(*INK); ctx.set_line_width(4.5)
        ctx.move_to(-85, -105); ctx.line_to(85, -105); ctx.move_to(-85, 105); ctx.line_to(85, 105); ctx.stroke()
        ctx.move_to(-75, -105); ctx.line_to(-6, 0); ctx.line_to(-75, 105); ctx.move_to(75, -105); ctx.line_to(6, 0); ctx.line_to(75, 105); ctx.stroke()
        ctx.restore()
    return d

def suitcase(x, y):
    return [[(x - 80, y), (x - 80, y - 110), (x + 80, y - 110), (x + 80, y), (x - 80, y)],
            [(x - 28, y - 110), (x - 28, y - 135), (x + 28, y - 135), (x + 28, y - 110)], [(x - 35, y - 110), (x - 35, y)], [(x + 35, y - 110), (x + 35, y)]]

def footprints(x0, y0, x1, y1, t0, dur, n=9):
    def d(ctx, p, t):
        for k in range(n):
            tk = t0 + dur * k / n
            if t < tk: break
            f = k / (n - 1); x = x0 + (x1 - x0) * f; y = y0 + (y1 - y0) * f + (10 if k % 2 else -10)
            a = clamp((t - tk) / 0.2) * (0.35 + 0.65 * (1 - f) * 0 + 0.65)
            ctx.save(); ctx.translate(x, y); ctx.scale(1.0, 0.55)
            ctx.set_source_rgba(*INK, a * 0.75); ctx.arc(0, 0, 11, 0, 2 * math.pi); ctx.fill(); ctx.restore()
    return d

def closed_eye(x, y):
    return [bez((x - 50, y), (x - 20, y + 25), (x + 20, y + 25), (x + 50, y))] + \
           [[(x + dx, y + 16), (x + dx * 1.3, y + 32)] for dx in (-25, 0, 25)]

def monitor(x0, x1, cy, t_on, t_loud, t_flat):
    rng = np.random.default_rng(5)
    ph = rng.uniform(0, 6, 8); fr = rng.uniform(1.5, 9, 8)
    def d(ctx, p, t):
        rev = clamp((t - t_on) / 0.6)
        xs = np.linspace(x0, x0 + (x1 - x0) * rev, 160)
        u = (xs - x0) / (x1 - x0)
        loud = 1 + 2.2 * ease_io((t - t_loud) / 0.5)
        flat = ease_io((t - t_flat) / 0.35)
        amp = np.zeros_like(u)
        for a, b in zip(ph, fr): amp += np.sin(u * b * 6 + t * b * 2 + a)
        env_ = np.abs(np.sin(u * 7 + t * 3)) * 0.6 + 0.4
        ys = cy + amp * 9 * loud * env_ * (1 - flat)
        ctx.set_source_rgb(*RED); ctx.set_line_width(4.5); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.move_to(xs[0], ys[0])
        for xx, yy in zip(xs[1:], ys[1:]): ctx.line_to(xx, yy)
        ctx.stroke()
        if t > t_flat:   # glowing dot at the end
            g = 0.5 + 0.5 * math.sin(t * 8)
            ctx.set_source_rgba(*RED, 0.5 + 0.5 * g); ctx.arc(x1, cy, 8, 0, 2 * math.pi); ctx.fill()
    return d

def sound_waves(x, y, t0):
    def d(ctx, p, t):
        for k in range(3):
            ph = ((t - t0) * 0.8 + k / 3) % 1
            ctx.set_source_rgba(*RED, 0.8 * (1 - ph)); ctx.set_line_width(4)
            ctx.new_path(); ctx.arc(x, y, 40 + 70 * ph, -0.6, 0.6); ctx.stroke()
    return d

def glow(x, y, r, a):
    g = cairo.RadialGradient(x, y, 5, x, y, r); g.add_color_stop_rgba(0, 1, 0.75, 0.4, a); g.add_color_stop_rgba(1, 1, 0.75, 0.4, 0); return g

def cal_page(ctx, dt):
    if dt < 0: return
    k = ease_in_(dt / 0.7); a = 1 - clamp(dt / 0.7)
    ctx.save(); ctx.translate(540, 560 + 300 * k); ctx.rotate(0.6 * k)
    ctx.set_source_rgba(*INK, a); ctx.set_line_width(4); ctx.rectangle(-120, 0, 240, 130); ctx.stroke()
    ctx.select_font_face("Inter SemiBold", 0, 0); ctx.set_font_size(60); ctx.set_source_rgba(*RED, a)
    e = ctx.text_extents("1"); ctx.move_to(-e.x_advance / 2, 90); ctx.show_text("1")
    ctx.restore()

def heart_emptying(x, y, size, t0):
    def d(ctx, p, t):
        k = clamp((t - t0) / 1.4)
        pts = heart_pts(x, y, size)
        ctx.save()
        ctx.move_to(*pts[0]); [ctx.line_to(*q) for q in pts[1:]]; ctx.close_path(); ctx.clip()
        top = y - size * 0.9 + (size * 2.0) * k
        ctx.set_source_rgb(*RED); ctx.rectangle(x - size * 1.5, top, size * 3, size * 3); ctx.fill()
        ctx.restore()
        stroke_partial(ctx, [pts], 1.0, RED, 3.5)
    return d

# ------------------------------------------------------------- background / plan / render
def make_bg():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(surf)
    c.set_source_rgb(*BG); c.paint()
    lum = sum(BG) / 3; hi = [min(1, x + 0.06) for x in BG]; lo = [x * (0.55 if lum < 0.3 else 0.8) for x in BG]
    g = cairo.RadialGradient(W / 2, H * 0.45, 200, W / 2, H * 0.45, 1300)
    g.add_color_stop_rgba(0, *hi, 0.6); g.add_color_stop_rgba(1, *lo, 0.6)
    c.set_source(g); c.paint()
    rng = np.random.default_rng(3)
    noise = (rng.normal(0, 1, (H, W)) * 6).astype(np.int16)
    buf = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    for ch in range(3): buf[:, :, ch] = np.clip(buf[:, :, ch].astype(np.int16) + noise, 0, 255)
    surf.mark_dirty(); return surf

def norm_word(x): import re; return re.sub(r"[^a-z']", "", x.lower().replace("’", "'"))

def plan(scenes, timings, total):
    """scenes: list of caption texts; timings: align.py output (one entry per scene)."""
    P = []
    for i, (txt, A) in enumerate(zip(scenes, timings)):
        cards = parse(txt); abs_t = [x[1] for x in A["words"]]
        start = 0.0 if i == 0 else (timings[i - 1]["span"][1] + min(A["span"][0], abs_t[0])) / 2
        P.append(dict(i=i, cards=cards, abs_t=abs_t, start=start, words=[w for c in cards for w, _ in c]))
    for i, p in enumerate(P):
        p["end"] = P[i + 1]["start"] if i + 1 < len(P) else total
        p["dur"] = p["end"] - p["start"]; p["times"] = [x - p["start"] for x in p["abs_t"]]
    return P

def make_wf(words, w):
    """wf('word', n=1) -> scene-local time of the n-th time that word is spoken."""
    def wf(word, n=1):
        c = 0
        for k, x in enumerate(words):
            if norm_word(x) == norm_word(word):
                c += 1
                if c == n: return w(k)
        raise KeyError(f"word '{word}' (#{n}) not in scene: {' '.join(words)}")
    return wf

def render(out_video, scenes, timings, build, total, label="", events_out=None, preview=None, punch=True):
    P = plan(scenes, timings, total); events = []
    for p in P:
        _seed[0] = p["i"] * 100 + 7
        w = lambda k, ts=p["times"]: ts[min(k, len(ts) - 1)]
        p["els"] = build(p["i"], w, make_wf(p["words"], w))
        for e in p["els"]:
            sf = getattr(e, "sfx", None)
            if sf and sf[0]: events.append((p["start"] + e.t0, sf[0], sf[1]))
        if p["i"] > 0: events.append((p["start"] - 0.12, "transition", 0.35))
        flat = [hl for c in p["cards"] for _, hl in c]
        p["punch"] = [p["times"][k] for k in range(len(flat)) if flat[k] and (k == 0 or not flat[k - 1])] if punch else []
    if events_out: json.dump(events, open(events_out, "w"))
    bg = make_bg()
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    frames = range(int(total * FPS)) if preview is None else preview
    proc = None
    if preview is None:
        proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                                 "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                                 "-pix_fmt", "yuv420p", out_video], stdin=subprocess.PIPE)
    for fi in frames:
        T = fi / FPS
        p = next(q for q in reversed(P) if q["start"] <= T + 1e-9); t = T - p["start"]
        ctx.set_source_surface(bg); ctx.paint()
        if label:
            ctx.select_font_face("Inter SemiBold", 0, 0); ctx.set_font_size(28)
            ctx.set_source_rgb(*RED); ctx.rectangle(80, 62, 6, 34); ctx.fill()
            ctx.set_source_rgba(*GREY, 0.95); ctx.move_to(100, 90); ctx.show_text(label)

        last = p["i"] == len(P) - 1; fo = 0.22
        out_a = 1 if last else 1 - clamp((t - (p["dur"] - fo)) / fo)
        in_a = ease_out(t / 0.2) if p["i"] > 0 else 1
        pz = sum(0.035 * math.sin(math.pi * clamp((t - pt) / 0.35)) for pt in p["punch"] if 0 < t - pt < 0.35)
        zoom = 1 + 0.03 * t / p["dur"] + pz + (0.03 * clamp((t - (p["dur"] - fo)) / fo) if not last else 0)
        ctx.push_group()
        ctx.save(); ctx.translate(*MAP_C); ctx.scale(zoom * MAP_S, zoom * MAP_S)
        ctx.translate(-MAP_SRC[0] + 4 * math.sin(T * 0.7), -MAP_SRC[1] + 3 * math.sin(T * 0.53))
        for e in p["els"]: e.render(ctx, t)
        ctx.restore()
        starts = []; idx = 0
        for c in p["cards"]: starts.append(idx); idx += len(c)
        k = max(j for j in range(len(starts)) if j == 0 or p["times"][starts[j]] - 0.05 <= t)
        draw_caption(ctx, p["cards"][k], p["times"][starts[k]:starts[k] + len(p["cards"][k])], t)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(out_a * in_a)
        if T >= END_AT:
            ctx.push_group(); ctx.set_source_surface(bg); ctx.paint()
            end_screen(ctx, T - END_AT); ctx.pop_group_to_source(); ctx.paint_with_alpha(ease_out((T - END_AT) / 0.6))
        if proc: proc.stdin.write(surf.get_data())
        else: surf.write_to_png(f"{out_video}_{fi:05d}.png")
    if proc: proc.stdin.close(); proc.wait()
    return P


# ------------------------------------------------------------- YouTube end screen (last seconds, room for end-screen elements)
END_AT = 1e9          # set by render_yt.py
END_TITLE = ""

def end_screen(ctx, dt):
    """Calm end card: two 'watch next' slots (where YouTube end-screen videos go) and a subscribe circle."""
    ctx.select_font_face("Inter SemiBold", 0, 0)
    ctx.set_font_size(54); e = ctx.text_extents(END_TITLE)
    ctx.set_source_rgba(*INK, ease_out(dt / 0.8)); ctx.move_to(W / 2 - e.x_advance / 2, 190); ctx.show_text(END_TITLE)
    for k, x in enumerate((250, 1010)):
        a = ease_out((dt - 0.3 - 0.2 * k) / 0.6)
        ctx.set_source_rgba(*LIGHT, 0.55 * a); ctx.set_line_width(4); ctx.rectangle(x, 300, 660, 371); ctx.stroke()
        ctx.set_font_size(30); lab = "Watch next" if k == 0 else "Part 2: his side"
        e = ctx.text_extents(lab); ctx.set_source_rgba(*GREY, a); ctx.move_to(x + 330 - e.x_advance / 2, 720); ctx.show_text(lab)
    a = ease_out((dt - 0.7) / 0.6)
    ctx.set_source_rgba(*RED, a); ctx.arc(W / 2, 860, 80, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, a); ctx.move_to(W / 2 - 22, 825); ctx.line_to(W / 2 + 34, 860); ctx.line_to(W / 2 - 22, 895); ctx.close_path(); ctx.fill()
    ctx.set_font_size(30); e = ctx.text_extents("Subscribe"); ctx.set_source_rgba(*INK, a)
    ctx.move_to(W / 2 - e.x_advance / 2, 990); ctx.show_text("Subscribe")
