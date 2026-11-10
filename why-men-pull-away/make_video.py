"""Motion-graphics explainer: 'Why men pull away' (English remake).
Renders 1080x1920 @30fps line-art animation with word-by-word captions."""
import math, subprocess, sys, json
import cairo
import numpy as np

W, H, FPS = 1080, 1920, 30
BG = (0.937, 0.914, 0.898)
INK = (0.11, 0.09, 0.09)
RED = (0.55, 0.05, 0.10)
GREY = (0.55, 0.52, 0.50)

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_io(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_back(x):
    x = clamp(x); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

# ---------------------------------------------------------------- geometry
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

_seed = [0]
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

# ---------------------------------------------------------------- elements
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

def S(polys, t0, dur=None, color=INK, width=4.0, wob=True, **kw):
    polys = [wobble(q) if wob else densify(q) for q in polys]
    if dur is None:
        dur = clamp(sum(math.dist(a, b) for q in polys for a, b in zip(q, q[1:])) / 900, 0.35, 1.3)
    return El(t0, lambda ctx, p, t: stroke_partial(ctx, polys, ease_io(p), color, width), dur, **kw)

def fill_poly(ctx, poly, color):
    ctx.set_source_rgb(*color); ctx.move_to(*poly[0])
    for q in poly[1:]: ctx.line_to(*q)
    ctx.close_path(); ctx.fill()

def F(poly, t0, center, color=RED, beat=False, flicker=False, **kw):
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

# ---------------------------------------------------------------- icons (return polylines)
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

# ---------------------------------------------------------------- script
# '|' splits caption cards; *word* = highlighted in red
SCENES = [
 ("Why does a man pull *away* | from the woman he loves… | right when his life is at its *hardest?*"),
 ("From the outside, it's confusing. | If he loves her… | why would he *leave?*"),
 ("Because what a man *feels…* | and how he *handles* it… | are not always the same thing."),
 ("When everything inside him | starts to *collapse…* | when he feels lost, drained, | and out of control…"),
 ("he's not thinking about | how to keep her close. | He's thinking about how not to | *drag her down* with him."),
 ("His logic becomes simple: | If I'm on *fire…* | I have to *protect the ones I love* | from the flames."),
 ("His life has become | a *burning ship.* | So the first thing he does… | is push her away."),
 ("And he stays on deck. | Because it's his ship. | His responsibility. | He either *saves it…* | or *sinks with it.*"),
 ("The problem is, in these moments… | he *forgets how to love.* | He goes quiet. | Closed off."),
 ("Not because his feelings *disappeared…* | but because he believes | this is something he has to face | *alone.*"),
 ("And that's exactly where | men *lose everything.*"),
 ("So many relationships | end right here. | Not because the love was *gone…*"),
 ("but because she saw his distance | as *rejection…* | and he saw her closeness | as *pressure.*"),
 ("If each of them understood | what the other was going through… | they would have *made it* together."),
 ("So if he pulls away… | don't chase him. | And don't disappear. | Just let him know: | *I'm not going anywhere.*"),
 ("Because the right kind of closeness | doesn't add pressure… | it makes the storm *smaller.*"),
 ("Send this to someone | who *needs to hear it.* | And follow for more."),
]

def parse(text):
    cards, hl = [], False
    for card in text.split("|"):
        words = []
        for tok in card.split():
            start = tok.startswith("*"); tok = tok.lstrip("*")
            if start: hl = True
            end = tok.endswith("*") or tok.rstrip("…?.,:").endswith("*")
            clean = tok.replace("*", "")
            words.append((clean, hl or start))
            if end: hl = False
        cards.append(words)
    return cards

def word_times(cards, lead=0.3):
    t = lead; times = []
    for ci, card in enumerate(cards):
        for wi, (w, _) in enumerate(card):
            times.append(t)
            letters = sum(c.isalnum() for c in w)
            t += 0.085 + 0.044 * letters
            if w.endswith("…"): t += 0.34
            elif w[-1] in ".?!": t += 0.30
            elif w[-1] in ",:": t += 0.13
    return times, t + 0.45

# ---------------------------------------------------------------- scene visuals
def slide(t0, dx, dur=0.9, dy=0):
    return lambda t: (dx * ease_io((t - t0) / dur), dy * ease_io((t - t0) / dur))

def shake(t0, amp=6, dur=0.6):
    return lambda t: (amp * math.sin(t * 60) * (1 - clamp((t - t0) / dur)) if t > t0 else 0, 0)

def build(i, w, T):
    """w(k) -> time of k-th word in the scene. T = scene duration."""
    E = []
    if i == 0:
        mv = slide(w(11), 150)
        E += [S(man(560, 900), 0.05, anim=mv),
              S(cloud(600, 610), w(13), color=RED, anim=mv),
              S(bolt(630, 672, 0.45), w(18), color=RED, width=3.5, dur=0.25,
                anim=lambda t: (mv(t)[0], 0, 1, 0.5 + 0.5 * (math.sin(t * 25) > -0.3))),
              S(woman(320, 900), w(7)),
              S(arrow(470, 690, 600, 690), w(4), color=RED, width=3.5, anim=mv)]
    elif i == 1:
        E += [S(head_profile(540, 760, 1.6), 0.05),
              S(qmark(540, 520, 1.4), w(6), color=RED, anim=lambda t: (0, 0, 1, 1, 0.12 * math.sin(t * 4))),
              S(arrow(380, 990, 700, 990), w(11), color=RED, width=3.5)]
    elif i == 2:
        tilt = lambda t: 0.22 * math.sin((t - w(11)) * 2.2) if t > w(11) else 0
        def scale_draw(ctx, p, t):
            a = tilt(t); cx, cy = 540, 640
            stroke_partial(ctx, [[(cx, cy), (cx, cy + 130)], [(cx - 40, cy + 130), (cx + 40, cy + 130)]], ease_io(p))
            ctx.save(); ctx.translate(cx, cy); ctx.rotate(a); ctx.translate(-cx, -cy)
            stroke_partial(ctx, [[(cx - 110, cy), (cx + 110, cy)],
                                 [(cx - 110, cy), (cx - 135, cy + 50), (cx - 85, cy + 50), (cx - 110, cy)],
                                 [(cx + 110, cy), (cx + 85, cy + 50), (cx + 135, cy + 50), (cx + 110, cy)]],
                           ease_io(p))
            ctx.restore()
        E += [F(heart_pts(330, 500, 60), w(4), (330, 500), beat=True),
              S(man(780, 960), w(6)),
              S(arrow(720, 760, 850, 760), w(8), color=RED, width=3.5),
              El(w(10), scale_draw, 0.9)]
    elif i == 3:
        sh = shake(w(13), 9, 1.4)
        E += [S(head_profile(540, 780, 1.6), 0.05, anim=sh),
              S([[(560, 640), (530, 690), (575, 720), (535, 770), (565, 810)]], w(5), color=RED, width=3.5, anim=sh),
              S(qmark(560, 560, 1.1), w(9), color=RED, anim=sh),
              S(bolt(330, 700, 0.8), w(11), color=RED, width=3.5),
              S(bolt(760, 720, 0.8), w(13), color=RED, width=3.5)]
    elif i == 4:
        sink = lambda t: (0, 22 * ease_io((t - w(16)) / 1.0))
        E += [S(pit(540, 900), 0.05),
              S(man(560, 990, 0.6), 0.3, anim=sink),
              S(woman(380, 900, 0.85), w(5)),
              F(heart_pts(380, 700, 26), w(7), (380, 700), beat=True),
              S(arrow(560, 600, 560, 780, 22), w(15), color=RED, width=4)]
    elif i == 5:
        E += [S(gear(760, 520, 24), w(1), color=INK, width=3.5,
                anim=lambda t: (0, 0, 1, 1, (t - w(1)) * 1.2)) ,
              F(flame(400, 790, 1.4), w(7), (400, 790), flicker=True),
              S(shield(700, 790, 1.5), w(10)),
              F(heart_pts(670, 790, 15), w(13), (670, 790)),
              F(heart_pts(700, 815, 15), w(13) + 0.1, (700, 815)),
              F(heart_pts(730, 790, 15), w(13) + 0.2, (730, 790))]
    elif i == 6:
        E += [S(boat(620, 900), 0.05),
              S(waves(620, 930, 170, 9, 3), w(2), anim=lambda t: (6 * math.sin(t * 2), 0)),
              F(flame(626, 760, 0.75), w(5), (626, 760), flicker=True),
              S(man(640, 900, 0.5), w(8)),
              S(woman(320, 920, 0.7), w(10), anim=slide(w(14) + 0.2, -60)),
              S(arrow(520, 840, 400, 840), w(14), color=RED, width=4)]
    elif i == 7:
        out = w(13) - 0.1
        E += [S(boat(620, 900), 0.0, dur=0.01, te=out),
              S(waves(620, 930, 170, 9, 3), 0.0, dur=0.01, te=out, anim=lambda t: (6 * math.sin(t * 2), 0)),
              F(flame(626, 760, 0.75), 0.0, (626, 760), flicker=True, te=out),
              S(man(640, 900, 0.5), 0.0, dur=0.01, te=out),
              S(shield(640, 790, 1.1), w(9), color=RED, te=out),
              S(target(400, 760), w(13)),
              F(heart_pts(400, 760, 22), w(14), (400, 760), beat=True),
              S(hand(700, 800), w(16), anim=lambda t: (0, 40 * ease_io((t - w(17)) / 1.2))),
              S(waves(700, 820, 150, 10, 2, rows=2), w(16), anim=lambda t: (8 * math.sin(t * 2.4), 0))]
    elif i == 8:
        empty = w(7)
        def fade_heart(ctx, p, t):
            k = 1 - clamp((t - empty) / 0.8)
            ctx.save(); ctx.translate(540, 560); s = ease_back(p); ctx.scale(s, s); ctx.translate(-540, -560)
            if k > 0:
                ctx.push_group(); fill_poly(ctx, heart_pts(540, 560, 62), RED); ctx.pop_group_to_source(); ctx.paint_with_alpha(k)
            ctx.restore()
        E += [El(0.1, fade_heart, 0.45),
              S(heart(540, 560, 62), w(6), color=RED, width=3.5),
              S(man(620, 990), w(11)),
              S(moon(780, 560), w(12), color=INK),
              S(door(370, 990), w(14))]
    elif i == 9:
        alone = w(15)
        E += [S(door(370, 990), 0.0, dur=0.01, te=alone),
              S(moon(780, 560), 0.0, dur=0.01, te=alone),
              S(heart(540, 560, 62), 0.0, dur=0.01, color=RED, width=3.5, te=alone),
              F(heart_pts(540, 560, 30), w(3), (540, 560), beat=True, te=alone),
              S(eye(330, 600, 0.8), w(7), te=alone),
              S(man(620, 990), 0.0, dur=0.01, anim=lambda t: (-80 * ease_io((t - alone) / 0.9), 0)),
              S([arc(540, 1000, 22, 0, 360, rx=110)], alone, color=GREY, width=3)]
    elif i == 10:
        sh = shake(w(5), 10, 1.0)
        E += [S(man(540, 960), 0.05, anim=sh),
              S(bolt(380, 640, 0.9), w(4), color=RED, width=3.5),
              S(bolt(700, 660, 0.9), w(5), color=RED, width=3.5),
              S([[(470, 990), (500, 1000), (530, 985), (560, 1002), (610, 990)]], w(6), color=RED, width=3)]
    elif i == 11:
        xs = [340, 440, 540, 640, 740]
        for k, x in enumerate(xs):
            h, cr = broken_heart(x, 620, 34)
            E.append(S(h, 0.05 + k * 0.18, color=INK, width=3))
            if k < 3: E.append(S(cr, w(3) + k * 0.15, color=RED, width=3))
        E.append(F(heart_pts(540, 850, 70), w(8), (540, 850), beat=True))
    elif i == 12:
        E += [S(woman(360, 1000), 0.05), S(man(720, 1000), 0.25),
              S(bubble(360, 700), w(4)), S(crossx(360, 700, 16), w(7), color=RED, width=3.5),
              S(bubble(720, 700), w(9)),
              S(arrow(680, 700, 710, 700, 10) + arrow(760, 700, 730, 700, 10), w(14), color=RED, width=3.5)]
    elif i == 13:
        E += [S(eye(340, 650), 0.05), S(eye(740, 650), 0.2),
              S(arrow(420, 630, 660, 630, 14), w(4), color=RED, width=3.5),
              S(arrow(660, 672, 420, 672, 14), w(7), color=RED, width=3.5),
              F(heart_pts(540, 860, 60), w(13), (540, 860), beat=True)]
    elif i == 14:
        E += [S(woman(340, 1000), 0.05),
              S(man(740, 1000), 0.2, anim=slide(w(3), 50)),
              S(arrow(430, 760, 620, 760, 16), w(5), color=INK, width=3.5, te=w(8)),
              S(crossx(525, 760, 30), w(6), color=RED, width=4.5, te=w(8)),
              F(heart_pts(540, 740, 36), w(12), (540, 740), beat=True)]
        def rings(ctx, p, t):
            for k in range(3):
                ph = ((t - w(15)) * 0.6 + k / 3) % 1.0
                ctx.set_source_rgba(*RED, 0.6 * (1 - ph)); ctx.set_line_width(3)
                ctx.arc(540, 740, 45 + 110 * ph, 0, 2 * math.pi); ctx.stroke()
        E.append(El(w(15), rings, 0.01))
    elif i == 15:
        shrink = lambda t: (0, 0, 1 - 0.55 * ease_io((t - w(10)) / 1.6), 1 - 0.7 * ease_io((t - w(11)) / 1.6))
        E += [S(cloud(540, 560, 2.4), 0.05, color=INK, anim=shrink, pivot=(540, 560)),
              S(bolt(520, 700, 0.9), 0.4, color=RED, width=3.5, anim=shrink, pivot=(540, 560)),
              S(woman(400, 1010, 0.85), w(2)), S(man(680, 1010, 0.85), w(2) + 0.2),
              F(heart_pts(540, 820, 30), w(5), (540, 820), beat=True)]
    elif i == 16:
        fly = lambda t: (260 * ease_io((t - w(8)) / 0.9), -200 * ease_io((t - w(8)) / 0.9), 1,
                         1 - clamp((t - w(8) - 0.5) / 0.4))
        E += [S(plane(540, 620, 1.3), 0.05, color=RED, anim=fly)]
        def btn(ctx, p, t):
            s = ease_back(p)
            if t > w(10): s *= 1 - 0.07 * math.sin(clamp((t - w(10)) / 0.25) * math.pi)
            ctx.save(); ctx.translate(540, 820); ctx.scale(s, s)
            bw, bh, r = 330, 104, 52
            ctx.new_sub_path(); ctx.arc(-bw/2 + r, 0, r, math.pi/2, 3*math.pi/2); ctx.arc(bw/2 - r, 0, r, -math.pi/2, math.pi/2)
            ctx.close_path(); ctx.set_source_rgb(*RED); ctx.fill()
            ctx.select_font_face("Inter SemiBold", 0, 0); ctx.set_font_size(46); ctx.set_source_rgb(1, 1, 1)
            ext = ctx.text_extents("+ Follow"); ctx.move_to(-ext.x_advance/2, 16); ctx.show_text("+ Follow")
            ctx.restore()
            if t > w(10):
                ph = clamp((t - w(10)) / 0.7)
                ctx.set_source_rgba(*RED, 0.5 * (1 - ph)); ctx.set_line_width(4)
                ctx.arc(600, 840, 20 + 90 * ph, 0, 2 * math.pi); ctx.stroke()
        E.append(El(w(9) - 0.2, btn, 0.5))
    return E

# ---------------------------------------------------------------- captions
CAP_Y, CAP_LH, CAP_FS, CAP_MAXW = 1240, 74, 56, 880

def draw_caption(ctx, card, times, t, alpha=1.0):
    ctx.select_font_face("Inter SemiBold", 0, 0); ctx.set_font_size(CAP_FS)
    sp = ctx.text_extents(" ").x_advance
    lines, cur, cw = [], [], 0
    for k, (wd, hl) in enumerate(card):
        wlen = ctx.text_extents(wd).x_advance
        if cur and cw + sp + wlen > CAP_MAXW: lines.append((cur, cw)); cur, cw = [], 0
        cur.append((wd, hl, wlen, times[k])); cw += (sp if cw else 0) + wlen
    lines.append((cur, cw))
    y0 = CAP_Y - (len(lines) - 1) * CAP_LH / 2
    for li, (ws, lw) in enumerate(lines):
        x = W / 2 - lw / 2; y = y0 + li * CAP_LH
        for wd, hl, wlen, wt in ws:
            p = clamp((t - wt) / 0.18)
            if p > 0:
                col = RED if hl else INK
                ctx.set_source_rgba(*col, p * alpha)
                ctx.move_to(x, y + 14 * (1 - ease_out(p))); ctx.show_text(wd)
            x += wlen + sp

# ---------------------------------------------------------------- background
def make_bg():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(surf)
    c.set_source_rgb(*BG); c.paint()
    g = cairo.RadialGradient(W/2, H*0.45, 200, W/2, H*0.45, 1300)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.25); g.add_color_stop_rgba(1, 0.6, 0.55, 0.52, 0.28)
    c.set_source(g); c.paint()
    rng = np.random.default_rng(3)
    noise = (rng.normal(0, 1, (H, W)) * 6).astype(np.int16)
    buf = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    for ch in range(3): buf[:, :, ch] = np.clip(buf[:, :, ch].astype(np.int16) + noise, 0, 255)
    surf.mark_dirty(); return surf

# ---------------------------------------------------------------- main render
def main(out, preview=None):
    plan = []; t_acc = 0.0
    for i, text in enumerate(SCENES):
        cards = parse(text); times, dur = word_times(cards)
        plan.append(dict(i=i, cards=cards, times=times, dur=dur, start=t_acc)); t_acc += dur
    total = t_acc
    json.dump([dict(i=p["i"], start=p["start"], dur=p["dur"], cards=[" ".join(w for w, _ in c) for c in p["cards"]],
                    card_times=[p["times"][sum(len(c) for c in p["cards"][:k])] for k in range(len(p["cards"]))])
               for p in plan], open(out + ".timing.json", "w"), indent=1)
    for p in plan:
        _seed[0] = p["i"] * 100
        p["els"] = build(p["i"], lambda k, ts=p["times"]: ts[min(k, len(ts) - 1)], p["dur"])
    bg = make_bg()
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    frames = range(int(total * FPS) + 1) if preview is None else preview
    proc = None
    if preview is None:
        proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra",
                                 "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                 "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                                 "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for fi in frames:
        T = fi / FPS
        p = next(q for q in reversed(plan) if q["start"] <= T + 1e-9)
        t = T - p["start"]
        ctx.set_source_surface(bg); ctx.paint()
        # progress bar + series label
        ctx.set_source_rgb(*RED); ctx.rectangle(0, 0, W * T / total, 10); ctx.fill()
        ctx.select_font_face("Inter SemiBold", 0, 0); ctx.set_font_size(30)
        lab = "WHY MEN PULL AWAY"; ext = ctx.text_extents(lab)
        ctx.set_source_rgba(*GREY, 0.9); ctx.move_to(W/2 - ext.x_advance/2, 200); ctx.show_text(lab)
        # scene layer (fade out at end, gentle push-in)
        out_a = 1 - clamp((t - (p["dur"] - 0.28)) / 0.28) if p["i"] < len(plan) - 1 else 1
        zoom = 1 + 0.025 * t / p["dur"]
        ctx.push_group()
        ctx.save(); ctx.translate(W/2, 800); ctx.scale(zoom, zoom); ctx.translate(-W/2, -800)
        for e in p["els"]: e.render(ctx, t)
        ctx.restore()
        # caption card
        idx = 0; starts = []
        for c in p["cards"]: starts.append(idx); idx += len(c)
        k = max(j for j in range(len(starts)) if j == 0 or p["times"][starts[j]] <= t)
        draw_caption(ctx, p["cards"][k], p["times"][starts[k]:starts[k] + len(p["cards"][k])], t)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(out_a)
        if proc: proc.stdin.write(surf.get_data())
        else: surf.write_to_png(f"{out}_{fi:05d}.png")
    if proc: proc.stdin.close(); proc.wait()
    print("total seconds", round(total, 2))

if __name__ == "__main__":
    if len(sys.argv) > 2: main(sys.argv[1], [int(x) for x in sys.argv[2:]])
    else: main(sys.argv[1])
