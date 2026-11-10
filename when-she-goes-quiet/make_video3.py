"""Video #2 'When She Goes Quiet' — timed to the ElevenLabs voice-over."""
import math, sys, json, re, subprocess
import numpy as np
import cairo
sys.path.insert(0, ".")
import make_video as B
import make_video2 as M
from make_video import (W, H, FPS, INK, RED, GREY, clamp, ease_io, ease_out, ease_back, arc, bez, join,
                        heart_pts, man, woman, head_profile, heart, broken_heart, bolt, cloud, arrow, qmark,
                        eye, bubble, crossx, stroke_partial, fill_poly, El, parse, make_bg)
from make_video2 import S, F, E_, cue, rain, rings, slide, shake, dots_bubble, draw_caption
from vo_script3 import VO3

AUDIO_END = 145.08
TOTAL = AUDIO_END + 1.8
LABEL = "WHEN SHE GOES QUIET"
LIGHT = (0.78, 0.75, 0.73)

# ------------------------------------------------------------- icons / custom draws
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
        stroke_partial(ctx, [B.wobble(arc(cx, cy, 110, -90, 270))], ease_io(p), INK, 4)
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
            ctx.push_group(); fill_poly(ctx, [(x - cx, y - cy) for x, y in B.flame(cx, cy, 0.6)], (0.35, 0.5, 0.75)); ctx.pop_group_to_source(); ctx.paint_with_alpha(max(a, 0))
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

# ------------------------------------------------------------- scenes
def build(i, w, words):
    def wf(word, n=1):
        c = 0
        for k, x in enumerate(words):
            if re.sub(r"[^a-z']", "", x.lower().replace("’", "'")) == word:
                c += 1
                if c == n: return w(k)
        raise KeyError(word)
    E = []
    if i == 0:
        fade_fight = wf("stops") + 0.2
        E += [S(woman(330, 1000), 0.05), S(man(750, 1000), 0.2),
              S(bubble(420, 700, 120, 70) + [[(385, 700), (400, 685), (415, 712), (430, 688), (445, 710), (455, 698)]], 0.3, color=RED, te=fade_fight, sfx="buzz", g=0.25),
              S(bubble(660, 660, 120, 70) + [[(625, 660), (640, 645), (655, 672), (670, 648), (685, 670), (695, 658)]], 0.55, color=RED, te=fade_fight),
              F(heart_pts(330, 760, 30), wf("peace") - 0.4, (330, 760), beat=True, sfx="heartbeat", g=0.4,
                anim=lambda t: (0, 0, 1, 1 - 0.75 * ease_io((t - wf("giving")) / 1.5)), pivot=(330, 760)),
              S(flag(470, 1000), wf("giving"), width=4, sfx="whoosh", g=0.35,
                anim=lambda t: (0, 90 * (1 - ease_out((t - wf("giving") - 0.3) / 1.3)) if t > wf("giving") + 0.3 else 90, 1, 1,
                                0.03 * math.sin(t * 3)), pivot=(470, 1000))]
    elif i == 1:
        E += [S(man(330, 1030), 0.05),
              S([[(260, 760), (300, 800), (380, 700)]], wf("okay"), color=RED, width=6, sfx="tick", g=0.6)]
        for k, (yy, nm) in enumerate([(560, "arguments"), (720, "complaints"), (880, "difficult")]):
            E += [S(bubble(700, yy, 260, 90) + [[(610, yy - 10), (790, yy - 10)], [(610, yy + 15), (740, yy + 15)]], 0.4 + 0.25 * k, g=0.12),
                  S([[(560, yy - 50), (840, yy + 50)]], wf(nm), color=RED, width=6, sfx="scribble", g=0.5)]
    elif i == 2:
        msg = wf("simple")
        flip = lambda t: (0, 0, 1, 1)
        def flip_bubble(ctx, p, t):
            k = clamp((t - msg) / 0.5); sx = abs(math.cos(k * math.pi)) + 1e-3
            ctx.save(); ctx.translate(540, 900); ctx.scale(sx, 1); ctx.translate(-540, -900)
            stroke_partial(ctx, [bubble(540, 900, 230, 120)[0]], ease_io(p), INK, 4)
            if k < 0.5:
                stroke_partial(ctx, [[(460, 900), (485, 875), (510, 925), (535, 875), (560, 925), (585, 875), (610, 900)]], ease_io(p), RED, 4)
            else:
                ctx.save(); ctx.translate(540, 895); s = 1 + 0.06 * max(0, math.sin(t * 6)) ** 8; ctx.scale(s, s); ctx.translate(-540, -895)
                fill_poly(ctx, heart_pts(540, 895, 36), RED); ctx.restore()
            ctx.restore()
        E += [F(heart_pts(540, 600, 40), wf("save") - 0.6, (540, 600), beat=True, sfx="heartbeat", g=0.4, te=msg - 1.6),
              E_(wf("save"), lifebuoy(540, 600), 0.5, sfx="pop", g=0.5, te=msg - 1.6),
              S(woman(330, 760, 0.8), wf("woman"), te=msg - 1.6),
              rings(540, 600, wf("relationship"), t_off=msg - 1.6),
              E_(wf("complaint"), flip_bubble, 0.6, sfx="buzz", g=0.3), cue(msg, "whoosh", 0.4), cue(msg + 0.25, "chime", 0.4)]
    elif i == 3:
        E += [S(eye(300, 760, 1.1), wf("see"), sfx="pop", g=0.5),
              S(ear(540, 760, 1.3), wf("hear"), sfx="pop", g=0.5),
              F(heart_pts(790, 760, 60), wf("matter"), (790, 760), beat=True, sfx="heartbeat", g=0.6),
              E_(wf("make"), sound_waves(580, 740, wf("hear")), 0.01)]
    elif i == 4:
        hope = wf("hoping")
        E += [S(woman(300, 1030), 0.05), S(man(800, 1030), 0.2),
              S(dots_bubble(420, 760), wf("gently"), sfx="pop", g=0.3),
              S(bubble(470, 610, 160, 80) + [[(415, 600), (525, 600)], [(415, 622), (490, 622)]], wf("again"), sfx="pop", g=0.35),
              S(bubble(540, 450, 220, 90) + [[(455, 440), (625, 440)], [(455, 462), (600, 462)]], wf("explain"), sfx="pop", g=0.4)]
        def tears(ctx, p, t):
            for k in range(4):
                f = ((t - wf("cries")) * 0.9 + k / 4) % 1
                ctx.set_source_rgba(0.35, 0.5, 0.75, 0.9 * (1 - f))
                ctx.arc(318, 870 + 90 * f, 5, 0, 2 * math.pi); ctx.fill()
        E += [E_(wf("cries"), tears, 0.01, te=wf("angry"), sfx="tick", g=0.2),
              S([[(230, 820), (215, 800)], [(265, 800), (262, 776)], [(370, 820), (385, 800)], [(335, 800), (338, 776)]],
                wf("angry"), color=RED, width=5, sfx="buzz", g=0.4, te=hope - 0.2),
              S(candle(560, 1030), hope, sfx="scribble", g=0.2),
              F(B.flame(560, 920, 0.45), hope + 0.4, (560, 920), flicker=True, sfx="fire", g=0.3),
              E_(wf("change"), lambda ctx, p, t: (ctx.set_source(_glow(560, 900, 140, 0.25 * ease_out((t - wf("change")) / 0.6))), ctx.paint()), 0.01)]
    elif i == 5:
        hz = [wf("overreacting"), wf("now"), wf("later")]
        hl = lambda t: (0, 0, 1, 1 - 0.28 * sum(t > h for h in hz))
        E += [S(woman(300, 1030), 0.05), S(man(780, 1030), 0.2),
              F(heart_pts(300, 760, 34), 0.3, (300, 760), beat=True, sfx="heartbeat", g=0.4, anim=hl, pivot=(300, 760))]
        for k, (h, yy) in enumerate(zip(hz, [800, 650, 500])):
            E += [S(bubble(720, yy, 190, 80) + [[(650, yy - 8), (790, yy - 8)], [(650, yy + 14), (740, yy + 14)]], h, color=INK, sfx="buzz", g=0.3),
                  cue(h + 0.05, "thud", 0.25)]
    elif i == 6:
        ch = wf("changes")
        E += [S([[(420, 520), (660, 520), (660, 690), (420, 690), (420, 520)], [(420, 560), (660, 560)], [(470, 500), (470, 540)], [(610, 500), (610, 540)]],
                0.05, te=ch - 0.3, sfx="scribble", g=0.2),
              cue(wf("day") - 0.1, "tear", 0.5),
              E_(wf("day"), lambda ctx, p, t: _cal_page(ctx, t - wf("day")), 0.01, te=ch - 0.3),
              S(woman(330, 1050), 0.2),
              E_(ch, _heart_emptying(330, 790, 36, ch), 0.4, sfx="heartbeat", g=0.35),
              E_(wf("expecting") - 0.3, toggle(700, 780, wf("adjusting")), 0.5, sfx="pop", g=0.4),
              cue(wf("adjusting"), "switch", 0.6)]
    elif i == 7:
        sh = wf("shower")
        E += [S(woman(320, 1040), 0.05, te=sh - 0.6),
              S(toolbox(640, 1030), wf("solve"), te=sh - 0.6, sfx="thud", g=0.3),
              S([[(600, 900), (690, 810)], arc(700, 800, 18, 135, 405)], wf("deal"), color=RED, width=5, te=sh - 0.6),
              S(shower(560, 560), sh - 0.4, sfx="scribble", g=0.25),
              rain(500, 620, 500, 1020, sh, n=18, speed=800, color=(0.35, 0.5, 0.75), alpha=0.6),
              cue(sh, "rain", 0.55),
              S(woman(560, 1050), sh - 0.1),
              F(B.flame(588, 870, 0.18), wf("nobody"), (588, 870), color=(0.35, 0.5, 0.75), sfx="pop", g=0.2,
                anim=lambda t: (0, 50 * clamp((t - wf("nobody")) / 1.6), 1, 1, math.pi), pivot=(588, 870))]
    elif i == 8:
        E += [E_(0.1, phone_typing(540, 760, "Today was so hard, I wanted to tell you that", wf("telling"), wf("nothing")), 0.5, sfx="pop", g=0.4),
              cue(wf("telling"), "typing", 0.5), cue(wf("nothing"), "erase", 0.5),
              S(ear(880, 520, 0.9), wf("listen") - 0.2, color=INK),
              S(crossx(880, 520, 40), wf("listen"), color=RED, width=6, sfx="buzz", g=0.4)]
    elif i == 9:
        rev = wf("silence")
        E += [S(warning(540, 640), 0.05, color=RED, width=5, te=wf("outside") - 0.3, sfx="buzz", g=0.4,
                anim=lambda t: (0, 0, 1 + 0.05 * math.sin(t * 10), 1), pivot=(540, 640)),
              E_(wf("outside"), mask_face(540, 760, rev), 0.6, sfx="scribble", g=0.25),
              cue(rev, "whoosh", 0.4), cue(wf("happiness"), "heartbeat", 0.25)]
    elif i == 10:
        gb = wf("goodbye")
        E += [E_(0.1, battery(540, 650, 0.6, gb - 0.4), 0.5, te=gb - 0.3, sfx="pop", g=0.3),
              cue(wf("exhaustion"), "powerdown", 0.6),
              E_(gb, hourglass(540, 720, gb + 0.3, wf("time") + 0.6), 0.5, sfx="pop", g=0.4),
              cue(gb + 0.3, "sand", 0.5)]
    elif i == 11:
        gone = wf("gone")
        E += [S(man(760, 1030), 0.05),
              S([[(760, 780), (760, 830)]] + [arc(760, 852, 4, 0, 360, 8)], wf("notices"), color=RED, width=6, sfx="pop", g=0.4),
              S(woman(330, 1030), 0.0, dur=0.01, anim=lambda t: (0, 0, 1, 1 - 0.85 * ease_io((t - gone) / 0.9))),
              S(suitcase(330, 760), wf("suitcase") - 0.2, color=GREY, te=wf("heart", 1) - 0.3, sfx="thud", g=0.3),
              F(heart_pts(330, 820, 30), wf("heart") - 0.15, (330, 820), sfx="whoosh", g=0.6,
                anim=lambda t: (-200 * ease_in_((t - wf("heart")) / 1.2), -500 * ease_in_((t - wf("heart")) / 1.2), 1, 1, -0.4 * clamp((t - wf("heart")) / 1.2)),
                pivot=(330, 820))]
    elif i == 12:
        E += [S(man(800, 1030), 0.05),
              S(bubble(700, 700, 230, 100), wf("she", 1), sfx="pop", g=0.3),
              S(qmark(700, 705, 1.0), wf("nowhere"), color=RED),
              S([[(150, 1060), (930, 1060)]], wf("didn't"), color=LIGHT, width=3)]
        for k in range(6):
            x = 200 + k * 95
            E.append(S(bubble(x, 900 - 40 * (k % 2), 70, 44), wf("tell") + 0.3 + k * 0.22, color=RED, sfx="pop", g=0.2, te=wf("walking") - 0.2))
        E += [E_(wf("walking"), footprints(640, 1050, 150, 1050, wf("walking"), 1.8), 0.01, sfx=None),
              cue(wf("walking"), "steps", 0.5),
              S(woman(150, 1030, 0.7), wf("years"), anim=lambda t: (0, 0, 1, 0.6)),
              S(closed_eye(800, 780), wf("noticed") - 0.2, sfx="scribble", g=0.2)]
    elif i == 13:
        fr = wf("relationship")
        E += [S(woman(330, 1030), 0.05), S(man(750, 1030), 0.2),
              S(dots_bubble(420, 720), wf("complaining"), te=fr - 0.5),
              S([[(650, 760), (650, 680)]] + [[(640 + 12 * k, 690), (640 + 12 * k, 740)] for k in range(3)], wf("shut") - 0.2, te=wf("treat") - 0.3),
              S(crossx(660, 720, 45), wf("down"), color=RED, width=6, sfx="buzz", g=0.4, te=wf("treat") - 0.3),
              S(B.shield(650, 720, 0.9), wf("attack") - 0.3, te=fr - 0.5),
              S(crossx(650, 720, 50), wf("attack"), color=RED, width=6, sfx="buzz", g=0.4, te=fr - 0.5),
              S(arrow(420, 580, 650, 580, 16), wf("against") - 0.1, color=INK, te=fr - 0.5, sfx="whoosh", g=0.3),
              S(crossx(535, 580, 26), wf("against") + 0.25, color=RED, width=5, te=fr - 0.5),
              F(heart_pts(540, 820, 40), fr, (540, 820), beat=True, sfx="heartbeat", g=0.6),
              rings(540, 820, fr + 0.3), S(arrow(380, 820, 480, 820, 14), fr + 0.1, color=RED, width=4)]
    elif i == 14:
        stop = wf("stop")
        E += [S(ear(400, 640, 1.2), wf("listen"), te=wf("because") - 0.3),
              E_(wf("talking") - 0.2, sound_waves(450, 620, wf("talking")), 0.01, te=wf("because") - 0.3),
              S(woman(700, 760, 0.8), wf("attention"), te=wf("because") - 0.3),
              S(bubble(790, 520, 130, 70), wf("explain") - 0.2, te=wf("because") - 0.3, sfx="pop", g=0.3),
              E_(wf("heartbreaking"), monitor(140, 940, 740, wf("heartbreaking"), wf("shouting"), stop), 0.01, sfx=None),
              cue(wf("heartbreaking"), "beeps", 0.45), cue(stop, "flatline", 0.55),
              F(heart_pts(540, 560, 34), wf("relationship") - 0.2, (540, 560), beat=True, sfx=None,
                anim=lambda t: (0, 0, 1, 1 - 0.8 * ease_io((t - stop) / 1.2)), pivot=(540, 560))]
    elif i == 15:
        fly = lambda t: (260 * ease_io((t - wf("it")) / 0.9), -200 * ease_io((t - wf("it")) / 0.9), 1, 1 - clamp((t - wf("it") - 0.5) / 0.4))
        fol = wf("follow")
        E += [S(B.plane(540, 620, 1.3), 0.05, color=RED, anim=fly), cue(wf("it"), "whoosh", 0.6)]
        def btn(ctx, p, t):
            s = max(ease_back(p), 1e-3)
            if t > fol: s *= 1 - 0.07 * math.sin(clamp((t - fol) / 0.25) * math.pi)
            ctx.save(); ctx.translate(540, 820); ctx.scale(s, s)
            bw, r = 330, 52
            ctx.new_sub_path(); ctx.arc(-bw / 2 + r, 0, r, math.pi / 2, 3 * math.pi / 2); ctx.arc(bw / 2 - r, 0, r, -math.pi / 2, math.pi / 2)
            ctx.close_path(); ctx.set_source_rgb(*RED); ctx.fill()
            ctx.select_font_face("Inter SemiBold", 0, 0); ctx.set_source_rgb(1, 1, 1)
            lab = "+ Follow" if t < fol + 0.5 else "✓ Following"; ctx.set_font_size(46 if t < fol + 0.5 else 40)
            ext = ctx.text_extents(lab); ctx.move_to(-ext.x_advance / 2, 15); ctx.show_text(lab); ctx.restore()
            if t > fol:
                ph = clamp((t - fol) / 0.7); ctx.set_source_rgba(*RED, 0.5 * (1 - ph)); ctx.set_line_width(4)
                ctx.arc(600, 840, 20 + 90 * ph, 0, 2 * math.pi); ctx.stroke()
        def hand_tap(ctx, p, t):
            k = ease_out((t - (fol - 0.5)) / 0.5); press = math.sin(clamp((t - fol) / 0.25) * math.pi) * 8
            x, y = 640 + 120 * (1 - k), 880 + 140 * (1 - k) + press
            stroke_partial(ctx, [join([(x - 12, y + 70)], [(x - 12, y)], arc(x, y, 12, 180, 360), [(x + 12, y + 30)]),
                                 [(x + 12, y + 30), (x + 34, y + 36), (x + 36, y + 80)]], 1.0, INK, 4)
        E += [E_(wf("and") - 0.15, btn, 0.5, sfx="pop", g=0.6), E_(fol - 0.5, hand_tap, 0.01), cue(fol + 0.02, "click", 0.7)]
    return E

def _glow(x, y, r, a):
    g = cairo.RadialGradient(x, y, 5, x, y, r); g.add_color_stop_rgba(0, 1, 0.75, 0.4, a); g.add_color_stop_rgba(1, 1, 0.75, 0.4, 0); return g

def _cal_page(ctx, dt):
    if dt < 0: return
    k = ease_in_(dt / 0.7); a = 1 - clamp(dt / 0.7)
    ctx.save(); ctx.translate(540, 560 + 300 * k); ctx.rotate(0.6 * k)
    ctx.set_source_rgba(*INK, a); ctx.set_line_width(4); ctx.rectangle(-120, 0, 240, 130); ctx.stroke()
    ctx.select_font_face("Inter SemiBold", 0, 0); ctx.set_font_size(60); ctx.set_source_rgba(*RED, a)
    e = ctx.text_extents("1"); ctx.move_to(-e.x_advance / 2, 90); ctx.show_text("1")
    ctx.restore()

def _heart_emptying(x, y, size, t0):
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

# ------------------------------------------------------------- plan + render
def plan():
    al = json.load(open("vo2/scene_words.json")); P = []
    for i, ((span, txt), A) in enumerate(zip(VO3, al)):
        cards = parse(txt); abs_t = [x[1] for x in A["words"]]
        start = 0.0 if i == 0 else (al[i - 1]["span"][1] + min(span[0], abs_t[0])) / 2
        P.append(dict(i=i, cards=cards, abs_t=abs_t, start=start, words=[w for c in cards for w, _ in c]))
    for i, p in enumerate(P):
        p["end"] = P[i + 1]["start"] if i + 1 < len(P) else TOTAL
        p["dur"] = p["end"] - p["start"]; p["times"] = [x - p["start"] for x in p["abs_t"]]
    return P

def render(out_video, preview=None):
    P = plan(); events = []
    for p in P:
        B._seed[0] = p["i"] * 100 + 7
        p["els"] = build(p["i"], lambda k, ts=p["times"]: ts[min(k, len(ts) - 1)], p["words"])
        for e in p["els"]:
            sf = getattr(e, "sfx", None)
            if sf and sf[0]: events.append((p["start"] + e.t0, sf[0], sf[1]))
        if p["i"] > 0: events.append((p["start"] - 0.12, "transition", 0.35))
        # punch-in moments: highlighted words that start a highlight run
        flat = [hl for c in p["cards"] for _, hl in c]
        p["punch"] = [p["times"][k] for k in range(len(flat)) if flat[k] and (k == 0 or not flat[k - 1])]
    json.dump(events, open("sfx_events3.json", "w"))
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
        ext = ctx.text_extents(LABEL); ctx.set_source_rgba(*GREY, 0.9); ctx.move_to(W / 2 - ext.x_advance / 2, 200); ctx.show_text(LABEL)
        last = p["i"] == len(P) - 1; fo = 0.22
        out_a = 1 if last else 1 - clamp((t - (p["dur"] - fo)) / fo)
        in_a = ease_out(t / 0.2) if p["i"] > 0 else 1
        punch = sum(0.035 * math.sin(math.pi * clamp((t - pt) / 0.35)) for pt in p["punch"] if 0 < t - pt < 0.35)
        zoom = 1 + 0.03 * t / p["dur"] + punch + (0.03 * clamp((t - (p["dur"] - fo)) / fo) if not last else 0)
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
