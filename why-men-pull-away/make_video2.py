"""v2: video timed to the ElevenLabs voice-over (word-level forced alignment),
more animation, synthesized sound effects + soft music bed."""
import math, sys, json, subprocess, wave
import numpy as np
import cairo
sys.path.insert(0, ".")
import make_video as B
from make_video import (W, H, FPS, INK, RED, GREY, clamp, ease_io, ease_out, ease_back, arc, bez, join,
                        heart_pts, man, woman, head_profile, heart, broken_heart, bolt, cloud, arrow, qmark,
                        gear, flame, shield, boat, waves, target, hand, moon, door, eye, bubble, pit, plane,
                        crossx, stroke_partial, fill_poly, wobble, El, parse, make_bg)
from vo_script import VO

AUDIO_END = 114.83
TOTAL = AUDIO_END + 1.6

# ------------------------------------------------------------- element wrappers with sound
def S(polys, t0, sfx="scribble", g=0.16, **kw):
    e = B.S(polys, t0, **kw); e.sfx = (sfx, g) if kw.get("dur", 1) > 0.05 else None; return e

def F(poly, t0, center, sfx="pop", g=0.5, **kw):
    e = B.F(poly, t0, center, **kw); e.sfx = (sfx, g); return e

def E_(t0, draw, dur=0.8, sfx=None, g=0.5, **kw):
    e = El(t0, draw, dur, **kw); e.sfx = (sfx, g) if sfx else None; return e

def cue(t, name, g=0.5):
    e = El(t, lambda c, p, tt: None, 0.01); e.sfx = (name, g); return e

# ------------------------------------------------------------- new icons
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

# ------------------------------------------------------------- particle effects
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

# ------------------------------------------------------------- scenes
def build(i, w):
    E = []
    if i == 0:   # Why does a man pull away ... right when life gets hardest?
        mv = slide(w(5), 150)
        E += [S(man(560, 960), 0.05, anim=mv),
              S(arrow(470, 750, 600, 750), w(4), color=RED, width=3.5, anim=mv, sfx="whoosh", g=0.35),
              S(woman(320, 960), w(8)),
              S(cloud(600, 640), w(12), color=RED, anim=mv),
              S(bolt(630, 705, 0.45), w(15), color=RED, width=3.5, dur=0.2, sfx="thunder", g=0.6,
                anim=lambda t: (mv(t)[0], 0, 1, 0.45 + 0.55 * (math.sin(t * 25) > -0.3))),
              rain(670, 820, 690, 820, w(15))]
    elif i == 1:  # From the outside, it makes no sense. If he loves her, why would he push her away?
        push = lambda t: (180 * ease_io((t - w(14)) / 0.8), 0, 1, 1 - clamp((t - w(15)) / 0.8))
        E += [S(head_profile(500, 780, 1.6), 0.05),
              S(qmark(500, 540, 1.4), w(5), color=RED, sfx="pop", g=0.3,
                anim=lambda t: (0, 0, 1, 1, 0.12 * math.sin(t * 4)), pivot=(500, 540)),
              F(heart_pts(760, 640, 40), w(9), (760, 640), beat=True, sfx="heartbeat", g=0.5, anim=push),
              S(arrow(640, 760, 780, 760), w(14), color=RED, width=3.5, sfx="whoosh", g=0.4)]
    elif i == 2:  # But here's something most people don't understand.
        lit = w(5)
        def glow(ctx, p, t):
            a = ease_out((t - lit) / 0.5)
            g = cairo.RadialGradient(540, 690, 10, 540, 690, 190)
            g.add_color_stop_rgba(0, *RED, 0.28 * a); g.add_color_stop_rgba(1, *RED, 0)
            ctx.set_source(g); ctx.arc(540, 690, 190, 0, 2 * math.pi); ctx.fill()
        E += [E_(lit, glow, 0.5),
              S(bulb(540, 690), 0.05, sfx="scribble", g=0.2),
              S(rays(540, 690, 95, 130, 10, -math.pi / 2), lit, color=RED, width=4, sfx="chime", g=0.5,
                anim=lambda t: (0, 0, 1 + 0.04 * math.sin((t - lit) * 5)), pivot=(540, 690))]
    elif i == 3:  # What a man feels and how he deals with those feelings are two very different things.
        tilt = lambda t: (0.12 * math.sin((t - w(11)) * 2.2) if t < w(14) else 0.28) if t > w(11) else 0
        tilt_s = lambda t: tilt(t) if t < w(14) else 0.12 * math.sin((w(14) - w(11)) * 2.2) * (1 - ease_out((t - w(14)) / 0.5)) + 0.28 * ease_out((t - w(14)) / 0.5)
        def scale_draw(ctx, p, t):
            a = tilt_s(t); cx, cy = 540, 660
            stroke_partial(ctx, [[(cx, cy), (cx, cy + 130)], [(cx - 40, cy + 130), (cx + 40, cy + 130)]], ease_io(p))
            ctx.save(); ctx.translate(cx, cy); ctx.rotate(a); ctx.translate(-cx, -cy)
            stroke_partial(ctx, [[(cx - 110, cy), (cx + 110, cy)],
                                 [(cx - 110, cy), (cx - 135, cy + 50), (cx - 85, cy + 50), (cx - 110, cy)],
                                 [(cx + 110, cy), (cx + 85, cy + 50), (cx + 135, cy + 50), (cx + 110, cy)]], ease_io(p))
            ctx.restore()
        E += [F(heart_pts(320, 520, 60), w(3), (320, 520), beat=True, sfx="heartbeat"),
              S(man(790, 990), w(4)),
              S(arrow(730, 790, 860, 790), w(7), color=RED, width=3.5, sfx="whoosh", g=0.3),
              E_(w(11), scale_draw, 0.9, sfx="scribble", g=0.2), cue(w(14), "tick", 0.5)]
    elif i == 4:  # When everything in his life starts falling apart, lost, exhausted, out of control
        sh = shake(w(15), 10, 1.6)
        E += [S(head_profile(540, 790, 1.6), 0.05, anim=sh),
              S([[(560, 650), (530, 700), (575, 730), (535, 780), (565, 820)]], w(6), color=RED, width=3.5,
                anim=sh, sfx="crack", g=0.55),
              S([[(500, 700), (470, 735), (490, 760)], [(610, 690), (640, 720), (625, 750)]], w(7), color=RED,
                width=3, anim=sh, sfx="crack", g=0.35),
              S(qmark(560, 570, 1.1), w(11), color=RED, anim=sh, sfx="pop", g=0.3),
              S(bolt(320, 720, 0.8), w(12), color=RED, width=3.5, sfx="thunder", g=0.35),
              S(bolt(770, 740, 0.8), w(14), color=RED, width=3.5, sfx="thunder", g=0.45),
              cue(w(15), "rumble", 0.5)]
    elif i == 5:  # he isn't thinking about how to keep her close... his problems from reaching her
        E += [S(pit(560, 920), 0.05),
              S(man(600, 1010, 0.6), 0.3),
              S(woman(350, 920, 0.85), w(4)),
              F(heart_pts(350, 720, 26), w(7), (350, 720), beat=True, sfx="heartbeat", g=0.4),
              S(cloud(600, 760, 1.0), w(15), color=INK),
              rain(560, 650, 780, 990, w(16), n=12),
              S(shield(480, 840, 0.85), w(18), color=RED, sfx="shield", g=0.5)]
    elif i == 6:  # In his mind, it's simple: If I'm on fire, protect the people I love from getting burned.
        E += [S(gear(540, 520, 26), w(1), width=3.5, anim=lambda t: (0, 0, 1, 1, (t - w(1)) * 1.4), pivot=(540, 520)),
              F(flame(380, 800, 1.4), w(8), (380, 800), flicker=True, sfx="fire", g=0.55),
              S(shield(720, 800, 1.5), w(12), sfx="shield", g=0.45),
              F(heart_pts(690, 800, 15), w(14), (690, 800), sfx="pop", g=0.3),
              F(heart_pts(720, 825, 15), w(14) + 0.1, (720, 825), sfx="pop", g=0.3),
              F(heart_pts(750, 800, 15), w(14) + 0.2, (750, 800), sfx="pop", g=0.3),
              sparks(410, 760, 640, 780, w(18), w(19) + 0.8), cue(w(18), "crackle", 0.4)]
    elif i == 7:  # Imagine his life as a sinking ship. Instead of asking her for help, he pushes her away.
        sinkm = lambda t: (0, 45 * ease_io((t - w(5)) / 2.0), 1, 1, 0.14 * ease_io((t - w(5)) / 2.0))
        E += [S(boat(640, 920), 0.05, anim=sinkm, pivot=(640, 940)),
              S(man(650, 920, 0.5), 0.4, anim=sinkm, pivot=(640, 940)),
              S(waves(640, 960, 300, 10, 4, rows=2, gap=24), 0.2, anim=lambda t: (8 * math.sin(t * 2), 0)),
              cue(w(5), "water", 0.6),
              S(woman(300, 960, 0.75), w(10), anim=slide(w(14) + 0.15, -70)),
              S(arrow(520, 850, 400, 850), w(14), color=RED, width=4, sfx="whoosh", g=0.5)]
    elif i == 8:  # And he stays on board ... He believes he has to save it, or sink with it.
        out = w(15)
        sunk = lambda t: (0, 45, 1, 1, 0.14)
        E += [S(boat(640, 920), 0.0, dur=0.01, te=out, anim=sunk, pivot=(640, 940)),
              S(man(650, 920, 0.5), 0.0, dur=0.01, te=out, anim=sunk, pivot=(640, 940)),
              S(waves(640, 960, 300, 10, 4, rows=2, gap=24), 0.0, dur=0.01, te=out, anim=lambda t: (8 * math.sin(t * 2), 0)),
              S(shield(660, 820, 1.0), w(9), color=RED, te=out, sfx="shield", g=0.45),
              S(target(380, 760), w(16), sfx="scribble", g=0.2),
              F(heart_pts(380, 760, 22), w(17), (380, 760), beat=True, sfx="heartbeat", g=0.5),
              S(hand(710, 820), w(19), anim=lambda t: (0, 50 * ease_io((t - w(19) - 0.3) / 1.3))),
              S(waves(710, 840, 170, 10, 2, rows=2), w(19), anim=lambda t: (8 * math.sin(t * 2.4), 0), sfx="water", g=0.5)]
    elif i == 9:  # Here's where things go wrong ... forgets how to let her love him ... distant ... shuts down
        empty = w(11)
        def fade_heart(ctx, p, t):
            k = 1 - clamp((t - empty) / 0.9)
            s = max(ease_back(p), 1e-3) * (1 + 0.05 * max(0, math.sin(t * 6)) ** 8 * k)
            ctx.save(); ctx.translate(540, 560); ctx.scale(s, s); ctx.translate(-540, -560)
            if k > 0:
                ctx.push_group(); fill_poly(ctx, heart_pts(540, 560, 62), RED); ctx.pop_group_to_source(); ctx.paint_with_alpha(k)
            ctx.restore()
        mv = slide(w(19), 110)
        E += [E_(0.1, fade_heart, 0.45, sfx="heartbeat", g=0.5),
              S(bolt(400, 520, 0.6), w(4), color=RED, width=3.5, sfx="thunder", g=0.3),
              S(heart(540, 560, 62), w(10), color=RED, width=3.5),
              S(woman(330, 1010), w(9)),
              S(man(690, 1010), 0.3, anim=mv),
              S(dots_bubble(780, 790), w(22), anim=mv, sfx="pop", g=0.3),
              S(crossx(780, 790, 22), w(23), color=RED, width=4, anim=mv, sfx="scribble", g=0.3)]
        def door_close(ctx, p, t):
            k = ease_out((t - w(25)) / 0.35)   # door swings shut
            x, y, h = 500, 1010, 150; wdt = 80 * (0.15 + 0.85 * k)
            stroke_partial(ctx, [[(x, y), (x, y - h)], [(x, y - h), (x + wdt, y - h), (x + wdt, y), (x, y)]], 1.0, INK, 4)
            if k > 0.9:
                ctx.set_source_rgb(*INK); ctx.arc(x + wdt - 12, y - h / 2, 3, 0, 2 * math.pi); ctx.fill()
        E.append(E_(w(25), door_close, 0.35, sfx="thud", g=0.7))
    elif i == 10:  # Not necessarily because his feelings are gone ... face everything alone.
        alone = w(18)
        hm = lambda t: (0, 330 * ease_io((t - w(8)) / 1.2), 1 - 0.6 * ease_io((t - w(8)) / 1.2))
        E += [S(man(540, 1010), 0.05),
              S(heart(540, 590, 60), w(3), color=RED, width=3.5, te=w(8) - 0.2),
              F(heart_pts(540, 590, 34), w(4), (540, 590), beat=True, sfx="heartbeat", g=0.5, anim=hm, pivot=(540, 590)),
              S(moon(780, 520), w(10), te=alone),
              S([arc(540, 1020, 22, 0, 360, rx=120)], alone, color=GREY, width=3, sfx="whoosh", g=0.3)]
        def dark(ctx, p, t):
            a = 0.18 * ease_io((t - alone) / 0.8)
            g = cairo.RadialGradient(540, 900, 160, 540, 900, 900)
            g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0.1, 0.05, 0.05, a)
            ctx.set_source(g); ctx.paint()
        E.append(E_(alone, dark, 0.01))
    elif i == 11:  # And that's where so many men lose the very thing they're trying to protect.
        land = w(6) + 0.7
        fall = lambda t: (0, 230 * clamp((t - w(6)) / 0.7) ** 2, 1, 1 - clamp((t - land) / 0.05), 0.9 * clamp((t - w(6)) / 0.7))
        E += [S(man(450, 900), 0.05, anim=shake(w(6), 8, 0.8)),
              F(heart_pts(640, 610, 34), 0.2, (640, 610), beat=True, sfx="heartbeat", g=0.4, anim=fall, pivot=(640, 610)),
              S(bolt(380, 620, 0.85), w(4), color=RED, width=3.5, sfx="thunder", g=0.4),
              S(bolt(700, 640, 0.85), w(5), color=RED, width=3.5),
              S(broken_heart(640, 860, 30)[0] + broken_heart(640, 860, 30)[1], land, dur=0.25, color=RED, width=3.5,
                sfx="glass", g=0.6),
              S([[(330, 905), (750, 905)]], 0.05, sfx=None)]
    elif i == 12:  # So many relationships end like this. Not because the love disappeared,
        xs = [340, 440, 540, 640, 740]
        for k, x in enumerate(xs):
            h, cr = broken_heart(x, 620, 34)
            E.append(S(h, 0.05 + k * 0.15, color=INK, width=3, g=0.08))
            if k < 3: E.append(S(cr, w(3) + k * 0.18, color=RED, width=3, sfx="crack", g=0.4))
        E.append(F(heart_pts(540, 850, 70), w(9), (540, 850), beat=True, sfx="heartbeat", g=0.6))
    elif i == 13:  # she sees his silence as rejection, he sees her attempts ... as more pressure, instead of support
        squeeze = lambda t: (0, 0, 1 - 0.35 * ease_io((t - w(18)) / 0.5), 1 - clamp((t - w(20)) / 0.6))
        E += [S(woman(360, 1010), 0.05), S(man(720, 1010), 0.25),
              S(bubble(360, 700), w(4), g=0.2), S(crossx(360, 700, 16), w(7), color=RED, width=3.5, sfx="buzz", g=0.4),
              S(bubble(720, 700), w(12), g=0.2),
              S(arrow(680, 700, 710, 700, 10) + arrow(760, 700, 730, 700, 10), w(18), color=RED, width=3.5, sfx="squeeze", g=0.4),
              F(heart_pts(540, 870, 26), w(13), (540, 870), sfx="pop", g=0.3, anim=squeeze, pivot=(540, 870))]
    elif i == 14:  # If they could only understand ... made it through the storm together.
        out = w(12)
        E += [S(eye(340, 600), 0.05, te=out), S(eye(740, 600), 0.2, te=out),
              S(arrow(420, 580, 660, 580, 14), w(4), color=RED, width=3.5, te=out, sfx="whoosh", g=0.3),
              S(arrow(660, 622, 420, 622, 14), w(9), color=RED, width=3.5, te=out, sfx="whoosh", g=0.3),
              S(woman(460, 1030, 0.8), w(12)), S(man(620, 1030, 0.8), w(12) + 0.15),
              S(umbrella(540, 800, 160), w(16), color=RED, width=4, sfx="whoosh", g=0.4),
              rain(250, 830, 420, 1040, w(17), n=40),
              cue(w(17), "rain", 0.5),
              F(heart_pts(540, 900, 18), w(19), (540, 900), beat=True, sfx="heartbeat", g=0.5)]
    elif i == 15:  # So if he starts pulling away, don't chase him. Don't disappear either.
        E += [S(woman(340, 1010), 0.05),
              S(man(740, 1010), 0.2, anim=slide(w(3), 60)),
              S(arrow(430, 760, 620, 760, 16), w(6), width=3.5, te=w(9), sfx="whoosh", g=0.3),
              S(crossx(525, 760, 30), w(7), color=RED, width=4.5, te=w(9), sfx="buzz", g=0.4),
              S(anchor(340, 1110, 0.8), w(10), color=RED, width=4, sfx="thud", g=0.4)]
    elif i == 16:  # Just let him know: I'm not here to add to your problems. I'm here because I love you...
        E += [S(woman(340, 1010), 0.05, anim=slide(w(18), 70)),
              S(man(740, 1010), 0.2, anim=slide(w(18), -70)),
              S(cloud(740, 640, 0.9), w(9), te=w(13)),
              F(heart_pts(540, 740, 36), w(12), (540, 740), beat=True, sfx="heartbeat", g=0.6),
              rings(540, 740, w(15)), cue(w(15), "chime", 0.35)]
    elif i == 17:  # Because the right kind of closeness doesn't make the storm heavier; it makes it easier to survive.
        grow = lambda t: (0, 0, (1 + 0.15 * ease_io((t - w(9)) / 0.8)) * (1 - 0.6 * ease_io((t - w(13)) / 1.5)),
                          1 - 0.85 * ease_io((t - w(13)) / 1.5))
        E += [S(cloud(540, 560, 2.4), 0.05, anim=grow, pivot=(540, 560)),
              S(bolt(520, 690, 0.9), w(9), color=RED, width=3.5, anim=grow, pivot=(540, 560), sfx="thunder", g=0.6),
              rain(330, 750, 640, 1010, 0.3, t_off=w(13), n=30),
              S(woman(440, 1010, 0.85), w(2)), S(man(640, 1010, 0.85), w(2) + 0.2),
              F(heart_pts(540, 830, 30), w(5), (540, 830), beat=True, sfx="heartbeat", g=0.5),
              S(sun(800, 470, 40), w(14), color=RED, width=4, sfx="chime", g=0.5),
              S(rays(800, 470, 55, 80, 12), w(15), color=RED, width=3.5, g=0.1,
                anim=lambda t: (0, 0, 1, 1, (t - w(15)) * 0.4), pivot=(800, 470))]
    elif i == 18:  # Send this to someone who needs to hear it. And follow for more.
        fly = lambda t: (260 * ease_io((t - w(8)) / 0.9), -200 * ease_io((t - w(8)) / 0.9), 1, 1 - clamp((t - w(8) - 0.5) / 0.4))
        E += [S(plane(540, 620, 1.3), 0.05, color=RED, anim=fly), cue(w(8), "whoosh", 0.6)]
        def btn(ctx, p, t):
            s = max(ease_back(p), 1e-3)
            if t > w(10): s *= 1 - 0.07 * math.sin(clamp((t - w(10)) / 0.25) * math.pi)
            ctx.save(); ctx.translate(540, 820); ctx.scale(s, s)
            bw, bh, r = 330, 104, 52
            ctx.new_sub_path(); ctx.arc(-bw / 2 + r, 0, r, math.pi / 2, 3 * math.pi / 2); ctx.arc(bw / 2 - r, 0, r, -math.pi / 2, math.pi / 2)
            ctx.close_path(); ctx.set_source_rgb(*RED); ctx.fill()
            ctx.select_font_face("Inter SemiBold", 0, 0); ctx.set_font_size(46); ctx.set_source_rgb(1, 1, 1)
            lab = "+ Follow" if t < w(10) + 0.5 else "✓ Following"
            if t >= w(10) + 0.5: ctx.set_font_size(40)
            ext = ctx.text_extents(lab); ctx.move_to(-ext.x_advance / 2, 15); ctx.show_text(lab)
            ctx.restore()
            if t > w(10):
                ph = clamp((t - w(10)) / 0.7)
                ctx.set_source_rgba(*RED, 0.5 * (1 - ph)); ctx.set_line_width(4)
                ctx.arc(600, 840, 20 + 90 * ph, 0, 2 * math.pi); ctx.stroke()
        E += [E_(w(9) - 0.15, btn, 0.5, sfx="pop", g=0.6), cue(w(10) + 0.02, "click", 0.7)]
        def hand_tap(ctx, p, t):  # pointer finger tapping the button
            k = ease_out((t - (w(10) - 0.5)) / 0.5); press = math.sin(clamp((t - w(10)) / 0.25) * math.pi) * 8
            x, y = 640 + 120 * (1 - k), 880 + 140 * (1 - k) + press
            stroke_partial(ctx, [join([(x - 12, y + 70)], [(x - 12, y)], arc(x, y, 12, 180, 360), [(x + 12, y + 30)]),
                                 [(x + 12, y + 30), (x + 34, y + 36), (x + 36, y + 80)]], 1.0, INK, 4)
        E.append(E_(w(10) - 0.5, hand_tap, 0.01))
    return E

# ------------------------------------------------------------- captions (with animated underline)
CAP_Y, CAP_LH, CAP_FS, CAP_MAXW = 1250, 76, 58, 880

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

# ------------------------------------------------------------- render plan
def plan():
    al = json.load(open("vo/scene_words.json"))
    # small correction: 'gone' sits right before the pause at 66.21
    w10 = al[10]["words"]
    for k, (wd, a, b) in enumerate(w10):
        if wd == "gone": w10[k][1] = 65.85
    P = []
    for i, ((span, txt), A) in enumerate(zip(VO, al)):
        cards = parse(txt)
        abs_t = [x[1] for x in A["words"]]
        start = 0.0 if i == 0 else (al[i - 1]["span"][1] + min(span[0], abs_t[0])) / 2
        P.append(dict(i=i, cards=cards, abs_t=abs_t, start=start))
    for i, p in enumerate(P):
        p["end"] = P[i + 1]["start"] if i + 1 < len(P) else TOTAL
        p["dur"] = p["end"] - p["start"]
        p["times"] = [x - p["start"] for x in p["abs_t"]]
    return P

def render(out_video, preview=None):
    P = plan(); events = []
    for p in P:
        B._seed[0] = p["i"] * 100
        p["els"] = build(p["i"], lambda k, ts=p["times"]: ts[min(k, len(ts) - 1)])
        for e in p["els"]:
            sf = getattr(e, "sfx", None)
            if sf and sf[0]: events.append((p["start"] + e.t0, sf[0], sf[1]))
        if p["i"] > 0: events.append((p["start"] - 0.12, "transition", 0.35))
    json.dump(events, open("sfx_events.json", "w"))
    bg = make_bg()
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    frames = range(int(TOTAL * FPS)) if preview is None else preview
    proc = None
    if preview is None:
        proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                                 "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                                 "-pix_fmt", "yuv420p", out_video], stdin=subprocess.PIPE)
    for fi in frames:
        T = fi / FPS
        p = next(q for q in reversed(P) if q["start"] <= T + 1e-9); t = T - p["start"]
        ctx.set_source_surface(bg); ctx.paint()
        ctx.set_source_rgb(*RED); ctx.rectangle(0, 0, W * T / TOTAL, 10); ctx.fill()
        ctx.select_font_face("Inter SemiBold", 0, 0); ctx.set_font_size(30)
        lab = "WHY MEN PULL AWAY"; ext = ctx.text_extents(lab)
        ctx.set_source_rgba(*GREY, 0.9); ctx.move_to(W / 2 - ext.x_advance / 2, 200); ctx.show_text(lab)
        last = p["i"] == len(P) - 1
        fo = 0.22
        out_a = 1 if last else 1 - clamp((t - (p["dur"] - fo)) / fo)
        in_a = ease_out(t / 0.2) if p["i"] > 0 else 1
        zoom = 1 + 0.03 * t / p["dur"] + (0.03 * clamp((t - (p["dur"] - fo)) / fo) if not last else 0)
        ctx.push_group()
        ctx.save(); ctx.translate(W / 2, 800); ctx.scale(zoom, zoom)
        ctx.translate(-W / 2 + 4 * math.sin(T * 0.7), -800 + 3 * math.sin(T * 0.53))
        for e in p["els"]: e.render(ctx, t)
        ctx.restore()
        starts = []; idx = 0
        for c in p["cards"]: starts.append(idx); idx += len(c)
        k = max(j for j in range(len(starts)) if j == 0 or p["times"][starts[j]] - 0.05 <= t)
        draw_caption(ctx, p["cards"][k], p["times"][starts[k]:starts[k] + len(p["cards"][k])], t)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(out_a * in_a)
        if proc: proc.stdin.write(surf.get_data())
        else: surf.write_to_png(f"{out_video}_{fi:05d}.png")
    if proc: proc.stdin.close(); proc.wait()
    return P

if __name__ == "__main__":
    if len(sys.argv) > 2: render(sys.argv[1], [int(x) for x in sys.argv[2:]])
    else: render(sys.argv[1])
