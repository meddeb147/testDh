"""Scenes for "3:17 AM" (horror, dark mood). Text matches the ElevenLabs recording word for word."""
from engine import *

THEME = "horror"
MOOD = "dark"
LABEL = "3:17 AM"
TAIL = 1.8

SCENES = [
    # 0  hook
    "If you ever get a *text message* | from your *own number* | at three seventeen in the morning… | do *exactly* what it says.",
    # 1
    "Last night, | my phone *lit up.* | *Three seventeen a.m.*",
    # 2
    "The sender… | was *me.* | One message: | *“Don't go downstairs.”*",
    # 3
    "I thought it was a *glitch.* | Maybe a *prank.* | I almost went back to sleep.",
    # 4
    "And I heard *something.* | Fridge door. | *Downstairs.* | Opening… | and *closing.*",
    # 5
    "My phone *buzzed* again: | “It's in the *kitchen.* | Stay in bed.” | Another message: | “Don't *answer* | when *Mom* calls you.”",
    # 6
    "And right then… | from the *bottom of the stairs…* | I heard my *mom's voice.* | *“Honey?* | Come down here a second.”",
    # 7
    "I swear, | I *almost went.* | My foot was already | *on the floor.*",
    # 8
    "Then my phone buzzed | *one last time.* | This time… | the message *wasn't from me.* | It was from *Mom.*",
    # 9
    "*“Are you awake?* | Don't make a *sound.* | I'm hiding in my *closet.* | *Someone's in the kitchen.”*",
    # 10
    "I *froze.* | I didn't move. | I didn't even *breathe.* | I stayed in that bed | until *sunrise.*",
    # 11
    "When I finally went downstairs, | the kitchen was *empty.* | Every cabinet… | *wide open.* | Every chair… | turned to *face the stairs.*",
    # 12
    "I still don't know | who sent those *first messages.* | But I know *one thing.*",
    # 13
    "Whatever was in that kitchen | can *copy any voice* it hears. | It just *can't text.*",
    # 14
    "So if you hear someone | *calling your name* tonight… | *don't answer.* | Check your *phone* first.",
    # 15
    "You might be getting | a *warning…* | from someone who's | *already seen* what's downstairs.",
    # 16  CTA
    "Send this to someone | who sleeps with their phone | next to their bed. | And *follow* for part two.",
]

# ------------------------------------------------------------------ helpers (colors read at draw time: theme is set after import)
COLD = (0.72, 0.80, 0.98)        # screen light
SCREEN = (0.17, 0.19, 0.24)
PW, PH = 320, 600                # phone size before scaling


def dark(f=0.55): return [c * f for c in BG]


def rr(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def txt(ctx, s, x, y, size, color, a=1.0, font="Inter SemiBold", anchor="c"):
    ctx.select_font_face(font, 0, 0); ctx.set_font_size(size)
    adv = ctx.text_extents(s).x_advance
    ctx.move_to(x + {"c": -adv / 2, "l": 0, "r": -adv}[anchor], y); ctx.set_source_rgba(*color, a); ctx.show_text(s)
    return adv


def wrap(ctx, s, size, maxw, font="Inter Medium"):
    ctx.select_font_face(font, 0, 0); ctx.set_font_size(size)
    lines, cur = [], ""
    for wd in s.split():
        test = (cur + " " + wd).strip()
        if cur and ctx.text_extents(test).x_advance > maxw: lines.append(cur); cur = wd
        else: cur = test
    return lines + [cur] if cur else lines


def pick(seq, t):
    """seq: [(t, ...)] -> the last entry whose time has passed, or None."""
    cur = None
    for e in seq:
        if t >= e[0]: cur = e
    return cur


def phone(cx, cy, s=1.0, lit=0.0, buzz=(), clock=None, header=None, notes=(), bubbles=(), dim=None, glitch=None,
          flash=None, bfs=24):
    """Draw fn for a phone. lit: time the screen turns on (None = dark). clock: (t, "3:17").
    header: [(t, name, color)] chat contact. notes: [(t, [(t, sender, color, struck)], body)] lock-screen cards.
    bubbles: [(t0, t1, text, accent)] incoming chat bubbles typed in between t0 and t1.
    buzz: vibration times. dim: screen fades out. glitch: (t0, t1). flash: time the first card's border flashes red."""
    def content(ctx, t, sx, sy, sw, sh):
        y = sy + 60
        if clock and t >= clock[0]:
            a = ease_out((t - clock[0]) / 0.35); sc = 1 + 0.25 * (1 - ease_out((t - clock[0]) / 0.45))
            ctx.save(); ctx.translate(0, sy + 140); ctx.scale(sc, sc)
            txt(ctx, clock[1], 0, 0, 96, INK, a); ctx.restore()
            txt(ctx, "Tuesday, November 10", 0, sy + 180, 20, GREY, a, "Inter Medium")
            y = sy + 215
        hd = pick(header or [], t)
        if hd:
            a = ease_out((t - header[0][0]) / 0.3)
            ctx.set_source_rgba(*INK, 0.22 * a); ctx.arc(0, sy + 64, 28, 0, 2 * math.pi); ctx.fill()
            txt(ctx, hd[1][0], 0, sy + 74, 28, INK, a)
            na = ease_out((t - hd[0]) / 0.25)
            txt(ctx, hd[1], 0, sy + 124, 25, hd[2], a * na)
            ctx.set_source_rgba(*INK, 0.15 * a); ctx.rectangle(sx, sy + 142, sw, 2); ctx.fill()
            y = sy + 160
        for k, (nt, senders, body) in enumerate(notes):
            if t < nt: continue
            a = ease_out((t - nt) / 0.35); yy = y - 26 * (1 - a)
            lines = wrap(ctx, body, 23, sw - 64)
            h = 74 + 30 * (len(lines) - 1) + 22
            x0, w0 = sx + 12, sw - 24
            rr(ctx, x0, yy, w0, h, 20); ctx.set_source_rgba(*INK, 0.13 * a); ctx.fill()
            if flash is not None and k == 0 and t > flash:
                fa = 0.5 + 0.5 * math.sin((t - flash) * 7)
                rr(ctx, x0, yy, w0, h, 20); ctx.set_source_rgba(*RED, a * (0.45 + 0.55 * fa)); ctx.set_line_width(4); ctx.stroke()
            cur = pick(senders, t)
            if cur:
                st, nm, col, struck = cur
                sa = a * ease_out((t - st) / 0.25)
                ctx.set_source_rgba(*col, 0.85 * sa); ctx.arc(x0 + 26, yy + 28, 11, 0, 2 * math.pi); ctx.fill()
                wn = txt(ctx, nm, x0 + 48, yy + 36, 24, col, sa, "Inter SemiBold", "l")
                if struck:
                    u = ease_out((t - st - 0.15) / 0.3)
                    ctx.set_source_rgba(*RED, sa); ctx.set_line_width(4)
                    ctx.move_to(x0 + 44, yy + 28); ctx.line_to(x0 + 44 + (wn + 10) * u, yy + 28); ctx.stroke()
            txt(ctx, "now", x0 + w0 - 16, yy + 34, 18, GREY, a, "Inter Medium", "r")
            for j, ln in enumerate(lines):
                txt(ctx, ln, x0 + 18, yy + 72 + 30 * j, 23, INK, a, "Inter Medium", "l")
            y += h + 12
        for bt0, bt1, body, acc in bubbles:
            if t < bt0: continue
            lines = wrap(ctx, body, bfs, sw - 92)
            ctx.select_font_face("Inter Medium", 0, 0); ctx.set_font_size(bfs)
            bw = max(ctx.text_extents(l).x_advance for l in lines) + 34
            lh = bfs * 1.32; bh = lh * len(lines) + 22
            a = ease_out((t - bt0) / 0.25); x0 = sx + 14
            rr(ctx, x0, y, bw, bh, 18)
            ctx.set_source_rgba(*(RED if acc else INK), (0.9 if acc else 0.16) * a); ctx.fill()
            n = int(sum(len(l) for l in lines) * clamp((t - bt0) / max(0.25, bt1 - bt0)) + 0.999)
            for j, l in enumerate(lines):
                show = l[:max(0, n)]; n -= len(l)
                if show: txt(ctx, show, x0 + 17, y + 11 + lh * j + bfs, bfs, (1, 1, 1) if acc else INK, a, "Inter Medium", "l")
            y += bh + 12
        if glitch and glitch[0] <= t <= glitch[1]:
            rg = np.random.default_rng(int(t * 24))
            for _ in range(8):
                gy, gh, off = rg.uniform(sy, sy + sh), rg.uniform(4, 36), rg.uniform(-50, 50)
                ctx.set_source_rgba(*(RED if rg.random() < 0.45 else COLD), rg.uniform(0.25, 0.65))
                ctx.rectangle(sx + off, gy, sw, gh); ctx.fill()

    def d(ctx, p, t):
        k = max(ease_back(p), 1e-3) * s
        bx = sum(8 * math.sin((t - b) * 85) * (1 - clamp((t - b) / 0.5)) for b in buzz if 0 <= t - b < 0.5)
        on = 0.0 if lit is None or t < lit else ease_out((t - lit) / 0.3)
        if dim is not None: on *= 1 - 0.92 * ease_io((t - dim) / 0.9)
        ctx.save(); ctx.translate(cx + bx, cy); ctx.scale(k, k)
        if on > 0:
            g = cairo.RadialGradient(0, 0, 80, 0, 0, 560)
            g.add_color_stop_rgba(0, *COLD, 0.17 * on); g.add_color_stop_rgba(1, *COLD, 0)
            ctx.set_source(g); ctx.arc(0, 0, 560, 0, 2 * math.pi); ctx.fill()
        body = dark(0.55)
        rr(ctx, -PW / 2, -PH / 2, PW, PH, 46); ctx.set_source_rgb(*body); ctx.fill_preserve()
        ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke()
        sx, sy, sw, sh = -PW / 2 + 14, -PH / 2 + 14, PW - 28, PH - 28
        rr(ctx, sx, sy, sw, sh, 34); ctx.set_source_rgb(*[body[i] + (SCREEN[i] - body[i]) * on for i in range(3)]); ctx.fill()
        rr(ctx, -42, sy + 10, 84, 20, 10); ctx.set_source_rgb(*body); ctx.fill()
        if on > 0.01:
            ctx.save(); rr(ctx, sx, sy, sw, sh, 34); ctx.clip(); ctx.push_group()
            content(ctx, t, sx, sy, sw, sh)
            ctx.pop_group_to_source(); ctx.paint_with_alpha(on); ctx.restore()
        ctx.restore()
    return d


def eyes(x, y, t_on, gap=26, size=1.0, alpha=1.0):
    """Two red eyes in the dark that fade in and blink."""
    def d(ctx, p, t):
        a = ease_io((t - t_on) / 0.8) * alpha
        if a <= 0: return
        ph = (t - t_on) % 2.6
        open_ = 1 - 0.9 * math.sin(clamp((ph - 2.3) / 0.18) * math.pi)
        g = cairo.RadialGradient(x, y, 2, x, y, 70 * size)
        g.add_color_stop_rgba(0, *RED, 0.18 * a); g.add_color_stop_rgba(1, *RED, 0)
        ctx.set_source(g); ctx.arc(x, y, 70 * size, 0, 2 * math.pi); ctx.fill()
        for sgn in (-1, 1):
            ex = x + sgn * gap / 2 * size
            pts = [(ex + 9 * size * math.cos(u), y + 4.5 * size * open_ * math.sin(u) - sgn * 0 + 1.5 * size * math.cos(u) * sgn)
                   for u in np.linspace(0, 2 * math.pi, 24)]
            ctx.move_to(*pts[0]); [ctx.line_to(*q) for q in pts[1:]]; ctx.close_path()
            ctx.set_source_rgba(*RED, a); ctx.fill()
    return d


def stairs_side(x0, y0, x1, y1, n=8):
    """Side-view staircase from (x0, y0) to (x1, y1) as a zig-zag."""
    run, rise = (x1 - x0) / n, (y1 - y0) / n
    pts = [(x0, y0)]
    for k in range(n):
        x, y = pts[-1]
        pts += [(x, y + rise), (x + run, y + rise)] if rise > 0 else [(x + run, y), (x + run, y + rise)]
    return [pts, [(x0 - run * 0.2, y0 - 110), (x1 - run * 0.2, y1 - 110)]]


def stairs_down(cx, y_near, y_far, hw_near, hw_far, n, t0, dur=1.6):
    """Looking down a staircase: steps shrink toward the dark bottom (far = higher on screen)."""
    def d(ctx, p, t):
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for k in range(n):
            u = k / (n - 1); q = clamp((t - t0 - dur * u) / 0.25)
            if q <= 0: break
            y = y_near + (y_far - y_near) * u ** 0.85; hw = hw_near + (hw_far - hw_near) * u
            ctx.set_source_rgba(*INK, q * (1 - 0.8 * u)); ctx.set_line_width(5 - 3 * u)
            ctx.move_to(cx - hw, y); ctx.line_to(cx + hw, y); ctx.stroke()
        r = clamp((t - t0) / dur)
        for sgn in (-1, 1):
            ctx.set_source_rgba(*INK, 0.7); ctx.set_line_width(4)
            xa, xb = cx + sgn * hw_near * 1.08, cx + sgn * hw_far * 1.08
            ctx.move_to(xa, y_near + 20); ctx.line_to(xa + (xb - xa) * r, y_near + 20 + (y_far - 10 - y_near - 20) * r); ctx.stroke()
    return d


def fridge(x0, y0, w, h, t_open, t_close):
    """Fridge whose door (hinged on the right) swings open and shut, spilling cold light."""
    def d(ctx, p, t):
        k = ease_out((t - t_open) / 0.7) * (1 - ease_io((t - t_close) / 0.35))
        xr, y1 = x0 + w, y0 + h
        if k > 0:
            g = cairo.LinearGradient(xr, 0, xr + 380, 0)
            g.add_color_stop_rgba(0, *COLD, 0.2 * k); g.add_color_stop_rgba(1, *COLD, 0)
            ctx.set_source(g); ctx.move_to(xr, y0 + 40); ctx.line_to(xr + 380, y1 + 10); ctx.line_to(xr, y1); ctx.close_path(); ctx.fill()
            ctx.set_source_rgba(*COLD, 0.55 * k); ctx.rectangle(x0, y0 + h * 0.32, w, h * 0.68); ctx.fill()
        stroke_partial(ctx, [[(x0, y0), (xr, y0), (xr, y1), (x0, y1), (x0, y0)], [(x0, y0 + h * 0.32), (xr, y0 + h * 0.32)],
                             [(x0 + 18, y0 + 30), (x0 + 18, y0 + 80)]], ease_io(p), INK, 4)
        fx = x0 + k * w * 1.55
        door = [(xr, y0 + h * 0.32), (fx, y0 + h * 0.32 - 22 * k), (fx, y1 + 22 * k), (xr, y1)]
        if p >= 1:
            ctx.move_to(*door[0]); [ctx.line_to(*q) for q in door[1:]]; ctx.close_path()
            ctx.set_source_rgb(*BG); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke()
            hx = fx + 18 if fx < xr else fx - 18
            ctx.move_to(hx, y0 + h * 0.4); ctx.line_to(hx, y0 + h * 0.55); ctx.stroke()
    return d


def bed(x0, x1, y, person=True):
    yt = y - 120
    out = [[(x0, y), (x0, y - 250), (x0 + 24, y - 250), (x0 + 24, y)],
           [(x0 + 24, yt), (x1, yt), (x1, yt + 46), (x0 + 24, yt + 46)],
           [(x1 - 14, yt + 46), (x1 - 14, y)], [(x0 + 24, yt + 70), (x1 - 14, yt + 70)],
           arc(x0 + 82, yt - 15, 16, 0, 360, rx=52)]
    if person:
        out += [arc(x0 + 92, yt - 48, 25, 0, 360),
                join(bez((x0 + 118, yt - 34), (x0 + 220, yt - 80), (x1 - 130, yt - 72), (x1 - 4, yt)))]
    return out


def window(x, y, w=200, h=220):
    return [[(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2), (x - w / 2, y - h / 2)],
            [(x, y - h / 2), (x, y + h / 2)], [(x - w / 2, y), (x + w / 2, y)]]


def chair(x, y, f):
    """Side-view chair; f = 1 faces right, -1 faces left (backrest on the other side)."""
    P = lambda a, b: (x + a * f, y + b)
    return [[P(-34, 0), P(-34, -150)], [P(-34, -74), P(34, -74), P(34, 0)], [P(-34, -140), P(-20, -150)]]


def cabinet(x, y, w, h, k):
    """Upper cabinet; door hinged on the left swings open with k (0 closed, 1 open)."""
    fx = x + w - k * w * 1.45
    frame = [[(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]]
    if k > 0: frame.append([(x + 8, y + h * 0.5), (x + w - 8, y + h * 0.5)])
    return frame, [(x, y), (fx, y - 18 * k), (fx, y + h + 18 * k), (x, y + h)], fx


def kitchen_cabinets(xs, y, w, h, t_open, step=0.18):
    def d(ctx, p, t):
        for j, x in enumerate(xs):
            k = ease_back(clamp((t - t_open - step * j) / 0.45)) if t > t_open + step * j else 0.0
            frame, door, fx = cabinet(x, y, w, h, k)
            if k > 0:
                ctx.set_source_rgb(*dark(0.4)); ctx.rectangle(x, y, w, h); ctx.fill()
            stroke_partial(ctx, frame, ease_io(p), INK, 4)
            if p >= 1:
                ctx.move_to(*door[0]); [ctx.line_to(*q) for q in door[1:]]; ctx.close_path()
                ctx.set_source_rgb(*BG); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke()
                kx = fx - 16 if k < 0.69 else fx + 16
                ctx.arc(kx, y + h / 2, 4, 0, 2 * math.pi); ctx.fill()
    return d


def turning_chairs(xs, y, t_turn, step=0.25):
    def d(ctx, p, t):
        for j, x in enumerate(xs):
            u = ease_io((t - t_turn - step * j) / 0.6)
            stroke_partial(ctx, chair(x, y, 1 - 2 * u), ease_io(p), INK, 4)
    return d


def analog_clock(x, y, r, t0, t1, m0=3 * 60 + 17, m1=6 * 60):
    def d(ctx, p, t):
        stroke_partial(ctx, [arc(x, y, r, -90, 270)], ease_io(p), INK, 4)
        if p < 1: return
        ctx.set_source_rgb(*INK)
        for k in range(12):
            a = k * math.pi / 6
            ctx.set_line_width(4 if k % 3 == 0 else 2.5)
            ctx.move_to(x + r * 0.84 * math.cos(a), y + r * 0.84 * math.sin(a)); ctx.line_to(x + r * 0.95 * math.cos(a), y + r * 0.95 * math.sin(a)); ctx.stroke()
        m = m0 + (m1 - m0) * ease_io((t - t0) / max(0.3, t1 - t0))
        for ang, L, wd, col in (((m % 60) / 60 * 2 * math.pi, 0.78, 4, INK), ((m / 60 % 12) / 12 * 2 * math.pi, 0.5, 6, RED)):
            ctx.set_source_rgb(*col); ctx.set_line_width(wd); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(x, y); ctx.line_to(x + r * L * math.sin(ang), y - r * L * math.cos(ang)); ctx.stroke()
        ctx.arc(x, y, 7, 0, 2 * math.pi); ctx.fill()
    return d


def sunrise(x, y_h, t0, w=600, r=62):
    def d(ctx, p, t):
        u = ease_out((t - t0) / 1.6)
        ctx.save(); ctx.rectangle(0, 0, 1080, y_h); ctx.clip()
        ctx.set_source(glow(x, y_h - 40 * u, 260, 0.2 * u)); ctx.paint()
        cy = y_h + r - (r + 50) * u
        stroke_partial(ctx, [arc(x, cy, r, 180, 540)], 1.0, INK, 4)
        if u > 0.6:
            ra = clamp((u - 0.6) / 0.4)
            stroke_partial(ctx, rays(x, cy, r + 18, r + 18 + 34 * ra, 10, -math.pi / 2), 1.0, INK, 3.5)
        ctx.restore()
        stroke_partial(ctx, [[(x - w / 2, y_h), (x + w / 2, y_h)]], ease_io(p), INK, 4)
    return d


def say(x, y, text, t0, color=None, size=34, te=None, sfx="pop", g=0.3):
    """Speech bubble sized to its text."""
    color = color or INK
    def d(ctx, p, t):
        txt(ctx, text, x, y + size * 0.36, size, color, ease_out(p), "Inter SemiBold")
    import cairo as _c
    s = _c.ImageSurface(_c.FORMAT_ARGB32, 4, 4); c = _c.Context(s); c.select_font_face("Inter SemiBold", 0, 0); c.set_font_size(size)
    w = c.text_extents(text).x_advance + 56
    return [S(bubble(x, y, w, size + 46), t0, te=te, sfx=sfx, g=g), E_(t0 + 0.15, d, 0.3, te=te)]


def waves_left(x, y, t0, color=None):
    """Sound waves travelling left (toward a listener)."""
    def d(ctx, p, t):
        for k in range(3):
            ph = ((t - t0) * 0.8 + k / 3) % 1
            ctx.set_source_rgba(*(color or RED), 0.8 * (1 - ph)); ctx.set_line_width(4)
            ctx.new_path(); ctx.arc(x + 60 - 70 * ph, y, 30 + 30 * ph, math.pi - 0.6, math.pi + 0.6); ctx.stroke()
    return d


def figure_tall(x, y):
    """Thin, too-tall silhouette with long arms."""
    return [arc(x, y - 440, 36, 0, 360, rx=25), [(x, y - 404), (x, y - 175)],
            bez((x - 62, y - 330), (x - 30, y - 352), (x + 30, y - 352), (x + 62, y - 330)),
            join(bez((x - 62, y - 330), (x - 78, y - 240), (x - 86, y - 150), (x - 82, y - 50)), [(x - 82, y - 50), (x - 92, y - 22)]),
            join(bez((x + 62, y - 330), (x + 78, y - 240), (x + 86, y - 150), (x + 82, y - 50)), [(x + 82, y - 50), (x + 92, y - 22)]),
            [(x - 40, y), (x, y - 175), (x + 40, y)]]


def zzz(x, y, t0):
    def d(ctx, p, t):
        for k in range(3):
            ph = ((t - t0) * 0.45 + k / 3) % 1
            txt(ctx, "z", x + 40 * ph + 10 * k, y - 120 * ph, 30 + 14 * k, INK, 0.9 * math.sin(ph * math.pi))
    return d


def bang(x, y, s=1.0):
    return [[(x, y - 70 * s), (x, y + 20 * s)], arc(x, y + 48 * s, 5 * s, 0, 360, 10)]


def follow_button(fol, cx=540, cy=900):
    def btn(ctx, p, t):
        s = max(ease_back(p), 1e-3)
        if t > fol: s *= 1 - 0.07 * math.sin(clamp((t - fol) / 0.25) * math.pi)
        ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s)
        bw, r = 330, 52
        ctx.new_sub_path(); ctx.arc(-bw / 2 + r, 0, r, math.pi / 2, 3 * math.pi / 2); ctx.arc(bw / 2 - r, 0, r, -math.pi / 2, math.pi / 2)
        ctx.close_path(); ctx.set_source_rgb(*RED); ctx.fill()
        lab = "+ Follow" if t < fol + 0.5 else "✓ Following"
        txt(ctx, lab, 0, 15, 46 if t < fol + 0.5 else 40, (1, 1, 1))
        ctx.restore()
        if t > fol:
            ph = clamp((t - fol) / 0.7); ctx.set_source_rgba(*RED, 0.5 * (1 - ph)); ctx.set_line_width(4)
            ctx.arc(cx + 60, cy + 20, 20 + 90 * ph, 0, 2 * math.pi); ctx.stroke()

    def hand_tap(ctx, p, t):
        k = ease_out((t - (fol - 0.5)) / 0.5); press = math.sin(clamp((t - fol) / 0.25) * math.pi) * 8
        x, y = cx + 100 + 120 * (1 - k), cy + 60 + 140 * (1 - k) + press
        stroke_partial(ctx, [join([(x - 12, y + 70)], [(x - 12, y)], arc(x, y, 12, 180, 360), [(x + 12, y + 30)]),
                             [(x + 12, y + 30), (x + 34, y + 36), (x + 36, y + 80)]], 1.0, INK, 4)
    return btn, hand_tap


# ------------------------------------------------------------------ scenes
def build(i, w, wf):
    E = []
    if i == 0:   # If you ever get a text message from your own number at 3:17... do exactly what it says.
        ex = wf("exactly")
        E += [rings(540, 740, ex, r0=230, span=160),
              E_(0.05, phone(540, 740, 1.12, lit=wf("text") - 0.05, buzz=(wf("text"), wf("message")),
                             clock=(wf("three"), "3:17"),
                             notes=[(wf("message"), [(wf("message"), "Unknown", GREY, False), (wf("own"), "Me", RED, False)],
                                     "1 new message")],
                             flash=ex), 0.5, sfx="rumble", g=0.5),
              cue(wf("text") - 0.05, "buzz", 0.7), cue(wf("message"), "buzz", 0.5),
              cue(wf("own"), "pop", 0.45), cue(wf("three"), "tick", 0.8),
              cue(ex, "thud", 0.6)]
    elif i == 1:  # Last night, my phone lit up. Three seventeen a.m.
        lit, three = wf("lit"), wf("three")
        def ph_small(ctx, p, t):
            on = ease_out((t - lit) / 0.3) if t > lit else 0
            bx = 4 * math.sin(t * 80) * (1 - clamp((t - lit) / 0.6)) if t > lit else 0
            if on:
                g = cairo.RadialGradient(760, 840, 10, 760, 840, 320)
                g.add_color_stop_rgba(0, *COLD, 0.2 * on); g.add_color_stop_rgba(1, *COLD, 0)
                ctx.set_source(g); ctx.arc(760, 840, 320, 0, 2 * math.pi); ctx.fill()
            rr(ctx, 740 + bx, 806, 40, 66, 8); ctx.set_source_rgb(*[dark(0.55)[k] + (COLD[k] * 0.8 - dark(0.55)[k]) * on for k in range(3)])
            ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(3); ctx.stroke()
            if on:
                for sgn in (-1, 1):
                    ctx.set_source_rgba(*INK, 0.7 * on * (1 - clamp((t - lit) / 1.4))); ctx.set_line_width(3)
                    ctx.new_path(); ctx.arc(760, 838, 46, (0 if sgn > 0 else math.pi) - 0.5, (0 if sgn > 0 else math.pi) + 0.5); ctx.stroke()
        E += [S(window(330, 560), 0.05, color=GREY, sfx=None),
              S([arc(392, 512, 22, 70, 290), arc(402, 510, 18, 250, 110)], 0.3, color=INK, sfx=None),
              S(bed(130, 600, 1040), 0.15, dur=1.3, sfx="scribble", g=0.15),
              S([[(680, 1040), (680, 872), (840, 872), (840, 1040)], [(680, 950), (840, 950)]], 0.4, sfx=None),
              S([[(90, 1040), (990, 1040)]], 0.05, color=GREY, dur=0.8, sfx=None),
              E_(0.6, ph_small, 0.01),
              cue(lit, "buzz", 0.75),
              E_(three - 0.05, lambda ctx, p, t: (ctx.save(), ctx.translate(760, 700), ctx.scale(1 + 0.3 * (1 - ease_out(p)), 1 + 0.3 * (1 - ease_out(p))),
                                                   txt(ctx, "3:17", 0, 0, 110, RED, ease_out(p)), ctx.restore()), 0.35, sfx="tick", g=0.8)]
    elif i == 2:  # The sender… was me. One message: "Don't go downstairs."
        E += [E_(0.05, phone(540, 740, 1.12, lit=0.1, header=[(wf("sender") - 0.1, "Unknown", GREY), (wf("me"), "Me", RED)],
                             bubbles=[(wf("don't"), wf("downstairs") + 0.4, "Don't go downstairs.", True)],
                             buzz=(wf("message"), wf("downstairs") + 0.1)), 0.45, sfx="pop", g=0.3),
              cue(wf("me"), "thud", 0.55), cue(wf("message"), "buzz", 0.6), cue(wf("don't") - 0.05, "typing", 0.45),
              cue(wf("downstairs") + 0.1, "buzz", 0.5)]
    elif i == 3:  # I thought it was a glitch. Maybe a prank. I almost went back to sleep.
        gl, pr, al = wf("glitch"), wf("prank"), wf("almost")
        E += [E_(0.0, phone(430, 740, 1.0, lit=-1, header=[(-1, "Me", RED)], bubbles=[(-1, -0.9, "Don't go downstairs.", True)],
                            glitch=(gl - 0.05, gl + 0.7), dim=al + 0.1), 0.01),
              cue(gl - 0.05, "crack", 0.6), cue(gl + 0.2, "buzz", 0.3),
              S(qmark(840, 600, 2.0), pr - 0.1, color=INK, width=5, sfx="pop", g=0.35, te=al - 0.2,
                anim=lambda t: (0, 0, 1, 1, 0.12 * math.sin(t * 4)), pivot=(840, 600)),
              S(closed_eye(840, 820), al - 0.05, sfx=None),
              E_(al + 0.3, zzz(860, 760, al + 0.3), 0.01),
              cue(al + 0.1, "powerdown", 0.4)]
    elif i == 4:  # And I heard something. Fridge door. Downstairs. Opening… and closing.
        op, cl = wf("opening"), wf("closing")
        E += [S([[(80, 1060), (1000, 1060)], [(900, 620), (1000, 620)]], 0.05, color=GREY, dur=0.9, sfx=None),
              S(stairs_side(900, 620, 480, 1060, 8), 0.2, dur=1.4, sfx="scribble", g=0.15),
              S(man(940, 620, 0.72), 0.5, sfx=None),
              E_(wf("something"), lambda ctx, p, t: [(ctx.set_source_rgba(*RED, 0.85 * (1 - ((t * 0.8 + k / 3) % 1))), ctx.set_line_width(4),
                                                      ctx.new_path(), ctx.arc(912, 512, 26 + 40 * ((t * 0.8 + k / 3) % 1), math.pi - 0.6, math.pi + 0.6),
                                                      ctx.stroke()) for k in range(3)], 0.01, te=wf("fridge") - 0.1),
              E_(wf("fridge") - 0.25, fridge(150, 700, 160, 360, op, cl), 0.9, sfx="scribble", g=0.2),
              S(arrow(820, 520, 520, 880, 22), wf("downstairs") - 0.1, color=RED, width=5, sfx="whoosh", g=0.35, te=op - 0.1),
              cue(wf("something"), "thud", 0.35), cue(op, "squeeze", 0.35), cue(op + 0.1, "rumble", 0.3), cue(cl + 0.12, "thud", 0.85),
              S([[(330, 1000), (350, 980)], [(330, 1040), (360, 1040)], [(330, 1080), (350, 1100)]], cl + 0.12, color=RED, width=4,
                dur=0.15, sfx=None, te=cl + 0.6)]
    elif i == 5:  # My phone buzzed again: "It's in the kitchen. Stay in bed." Another message: "Don't answer when Mom calls you."
        E += [E_(0.0, phone(540, 740, 1.12, lit=-1, header=[(-1, "Me", RED)],
                            bubbles=[(-1, -0.9, "Don't go downstairs.", True),
                                     (wf("it's"), wf("kitchen") + 0.35, "It's in the kitchen.", False),
                                     (wf("stay"), wf("bed") + 0.25, "Stay in bed.", False),
                                     (wf("another"), wf("you") + 0.2, "Don't answer when Mom calls you.", True)],
                            buzz=(wf("buzzed"), wf("another"))), 0.01),
              cue(wf("buzzed"), "buzz", 0.75), cue(wf("it's") - 0.05, "typing", 0.4), cue(wf("stay") - 0.05, "typing", 0.35),
              cue(wf("another"), "buzz", 0.6), cue(wf("another") + 0.05, "typing", 0.4), cue(wf("mom"), "thud", 0.4)]
    elif i == 6:  # And right then… from the bottom of the stairs… I heard my mom's voice. "Honey? Come down here a second."
        far = 600
        E += [E_(0.05, stairs_down(540, 1080, far, 330, 70, 10, 0.05, 1.8), 0.01),
              cue(0.05, "steps", 0.25),
              E_(wf("voice") - 0.1, lambda ctx, p, t: [(ctx.set_source_rgba(*RED, 0.8 * (1 - ((t * 0.8 + k / 3) % 1))), ctx.set_line_width(4),
                                                         ctx.new_path(), ctx.arc(540, far - 20, 30 + 60 * ((t * 0.8 + k / 3) % 1), -math.pi / 2 - 0.6, -math.pi / 2 + 0.6),
                                                         ctx.stroke()) for k in range(3)], 0.01),
              *say(760, 500, "Honey?", wf("honey") - 0.05, color=RED, sfx="pop", g=0.35),
              *say(330, 470, "Come down…", wf("come") - 0.05, sfx="pop", g=0.25),
              E_(wf("second"), eyes(540, far + 8, wf("second"), gap=30, size=1.1, alpha=0.9), 0.01),
              cue(wf("second") + 0.1, "heartbeat", 0.6)]
    elif i == 7:  # I swear, I almost went. My foot was already on the floor.
        ft, fl = wf("foot"), wf("floor")
        drop = lambda t: (0, -36 * (1 - ease_in_((t - (fl - 0.35)) / 0.35)) if t < fl else 0)
        E += [S([[(70, 1040), (1010, 1040)]], 0.05, color=GREY, dur=0.8, sfx=None),
              S(bed(120, 560, 1040), 0.1, dur=1.2, sfx="scribble", g=0.15),
              E_(0.3, lambda ctx, p, t: (ctx.set_source_rgb(*dark(0.35)), ctx.rectangle(820, 680, 160, 360), ctx.fill()), 0.01),
              S(door(900, 1040, 160, 360), 0.3, sfx=None),
              E_(wf("almost"), footprints(500, 1065, 800, 1065, wf("almost"), 0.9, n=5), 0.01, te=ft - 0.2),
              cue(wf("almost"), "steps", 0.35),
              S([bez((400, 950), (420, 980), (430, 1000), (435, 1004))], ft - 0.25, width=5, sfx=None, anim=drop, pivot=(430, 1000)),
              S([[(435, 1004), (435, 1032)], [(435, 1032), (478, 1032)]], ft - 0.05, width=5, sfx=None, anim=drop, pivot=(430, 1000)),
              cue(fl, "thud", 0.9),
              S([[(400, 1012), (382, 996)], [(498, 1012), (516, 996)], [(400, 1034), (376, 1034)], [(500, 1034), (524, 1034)]],
                fl, color=RED, width=4, dur=0.15, sfx=None, te=fl + 0.7),
              E_(wf("already"), eyes(900, 760, wf("already"), gap=26, size=0.9, alpha=0.75), 0.01)]
    elif i == 8:  # Then my phone buzzed one last time. This time… the message wasn't from me. It was from Mom.
        bz = wf("buzzed")
        E += [E_(0.05, phone(540, 740, 1.12, lit=bz - 0.05, clock=(bz - 0.05, "3:19"),
                             notes=[(bz + 0.1, [(bz + 0.1, "• • •", GREY, False), (wf("me") - 0.05, "Me", GREY, True),
                                                (wf("mom") - 0.05, "Mom", RED, False)], "1 new message")],
                             buzz=(bz, wf("last"))), 0.45, sfx=None),
              cue(bz, "buzz", 0.8), cue(wf("last"), "buzz", 0.6), cue(wf("me"), "erase", 0.35), cue(wf("mom"), "thud", 0.7)]
    elif i == 9:  # "Are you awake? Don't make a sound. I'm hiding in my closet. Someone's in the kitchen."
        E += [E_(0.0, phone(540, 740, 1.12, lit=-1, header=[(-1, "Mom", RED)], bfs=23,
                            bubbles=[(wf("are") - 0.05, wf("awake") + 0.3, "Are you awake?", False),
                                     (wf("don't") - 0.05, wf("sound") + 0.3, "Don't make a sound.", False),
                                     (wf("i'm") - 0.05, wf("closet") + 0.3, "I'm hiding in my closet.", False),
                                     (wf("someone's") - 0.05, wf("kitchen") + 0.3, "Someone's in the kitchen.", True)],
                            buzz=(wf("someone's"),)), 0.01),
              cue(wf("are") - 0.05, "typing", 0.4), cue(wf("don't") - 0.05, "typing", 0.4), cue(wf("i'm") - 0.05, "typing", 0.4),
              cue(wf("someone's") - 0.05, "buzz", 0.6), cue(wf("kitchen"), "heartbeat", 0.8)]
    elif i == 10:  # I froze. I didn't move. I didn't even breathe. I stayed in that bed until sunrise.
        st, sr = wf("stayed"), wf("sunrise")
        tremble = lambda t: (1.6 * math.sin(t * 41), 1.2 * math.cos(t * 37))
        E += [S(eye(540, 720, 2.6), wf("froze") - 0.1, width=5, sfx="thud", g=0.6, te=st - 0.35, anim=tremble),
              F([(540 + 16 * math.cos(u), 720 + 16 * math.sin(u)) for u in np.linspace(0, 2 * math.pi, 30)], wf("froze") + 0.2, (540, 720),
                color=RED, sfx=None, te=st - 0.35, anim=tremble),
              cue(wf("breathe"), "heartbeat", 0.8), cue(wf("breathe") + 0.9, "heartbeat", 0.6),
              E_(st - 0.2, analog_clock(540, 640, 125, st + 0.3, sr + 0.4), 0.6, sfx="tick", g=0.6),
              cue(st + 0.5, "sand", 0.35),
              E_(sr - 0.3, sunrise(540, 1000, sr - 0.1), 0.6, sfx="chime", g=0.25)]
    elif i == 11:  # When I finally went downstairs, the kitchen was empty. Every cabinet… wide open. Every chair… turned to face the stairs.
        dn = wf("downstairs")
        walk = lambda t: (310 * ease_io((t - dn) / 1.2), 460 * ease_io((t - dn) / 1.2))
        E += [S([[(70, 1060), (1010, 1060)]], 0.05, color=GREY, dur=0.8, sfx=None),
              S(stairs_side(110, 600, 420, 1060, 7), 0.1, dur=1.2, sfx="scribble", g=0.12),
              S(man(150, 600, 0.75), 0.3, sfx=None, anim=walk),
              cue(dn, "steps", 0.4),
              E_(wf("kitchen") - 0.2, kitchen_cabinets([500, 660, 820], 470, 150, 170, wf("wide")), 0.9, sfx="scribble", g=0.2),
              cue(wf("wide"), "squeeze", 0.35), cue(wf("open"), "thud", 0.4),
              E_(wf("every", 2) - 0.2, turning_chairs([560, 720, 880], 1060, wf("turned")), 0.8, sfx="scribble", g=0.2),
              cue(wf("turned"), "rumble", 0.55), cue(wf("stairs"), "thud", 0.6),
              S(arrow(820, 830, 470, 830, 22), wf("face") - 0.1, color=RED, width=5, sfx=None)]
    elif i == 12:  # I still don't know who sent those first messages. But I know one thing.
        E += [E_(0.05, phone(420, 740, 0.98, lit=0.05, header=[(0.05, "Me", RED)], bfs=22,
                             bubbles=[(0.05, 0.1, "Don't go downstairs.", True), (0.05, 0.1, "It's in the kitchen.", False),
                                      (0.05, 0.1, "Stay in bed.", False), (0.05, 0.1, "Don't answer when Mom calls you.", True)]),
                 0.45, sfx="pop", g=0.25),
              S(qmark(830, 640, 2.2), wf("know") - 0.1, color=INK, width=5, sfx="pop", g=0.35, te=wf("but") - 0.1,
                anim=lambda t: (0, 0, 1, 1, 0.12 * math.sin(t * 4)), pivot=(830, 640)),
              S(bang(830, 640, 1.3), wf("one"), color=RED, width=7, sfx="thud", g=0.7, dur=0.25)]
    elif i == 13:  # Whatever was in that kitchen can copy any voice it hears. It just can't text.
        sway = lambda t: (0, 0, 1, 1, 0.025 * math.sin(t * 1.3))
        E += [S(figure_tall(260, 1060), 0.05, color=GREY, width=5, dur=1.6, sfx="rumble", g=0.45, anim=sway, pivot=(260, 1060)),
              E_(0.6, eyes(260, 618, 0.6, gap=20, size=0.8), 0.01, anim=sway, pivot=(260, 1060)),
              *say(560, 520, "Honey?", wf("copy") - 0.05, color=RED, g=0.3),
              *say(600, 660, "It's me.", wf("voice") - 0.1, g=0.25),
              *say(560, 800, "Come here…", wf("hears") - 0.05, g=0.25),
              E_(wf("just") - 0.1, phone(860, 900, 0.42, lit=wf("just")), 0.45, sfx="pop", g=0.3),
              S(crossx(860, 900, 95), wf("can't"), color=RED, width=8, sfx="buzz", g=0.6)]
    elif i == 14:  # So if you hear someone calling your name tonight… don't answer. Check your phone first.
        ck = wf("check")
        E += [S(ear(300, 700, 1.5), 0.05, width=5, sfx="scribble", g=0.2, te=ck - 0.25),
              *say(720, 560, "Honey?", wf("calling") - 0.1, color=RED, te=ck - 0.25, g=0.35),
              E_(wf("calling"), waves_left(470, 690, wf("calling")), 0.01, te=ck - 0.25),
              S(crossx(720, 565, 80), wf("don't"), color=RED, width=8, sfx="buzz", g=0.6, te=ck - 0.25),
              E_(ck - 0.1, phone(540, 740, 1.12, lit=wf("phone"), buzz=(wf("phone"),), clock=(wf("phone"), "3:17"),
                                notes=[(wf("first") - 0.1, [(wf("first") - 0.1, "Me", RED, False)], "Don't go downstairs.")]),
                 0.45, sfx="pop", g=0.35),
              cue(wf("phone"), "buzz", 0.7)]
    elif i == 15:  # You might be getting a warning… from someone who's already seen what's downstairs.
        mv = wf("someone")
        up = lambda t: (0, -160 * ease_io((t - mv) / 0.9), 1 - 0.3 * ease_io((t - mv) / 0.9))
        E += [E_(0.0, phone(540, 740, 1.12, lit=-1, clock=(-1, "3:17"),
                            notes=[(-1, [(-1, "Me", RED, False)], "Don't go downstairs.")], flash=wf("warning")), 0.01,
                 anim=up, pivot=(540, 740)),
              cue(wf("warning"), "thud", 0.55),
              E_(mv + 0.4, stairs_down(540, 1100, 900, 300, 70, 7, mv + 0.4, 1.0), 0.01),
              cue(mv + 0.4, "steps", 0.3),
              E_(wf("downstairs") - 0.1, eyes(540, 905, wf("downstairs") - 0.1, gap=30, size=1.1), 0.01),
              cue(wf("downstairs"), "heartbeat", 0.8)]
    elif i == 16:  # Send this to someone who sleeps with their phone next to their bed. And follow for part two.
        fol = wf("follow")
        fly = lambda t: (300 * ease_io((t - wf("bed")) / 0.9), -220 * ease_io((t - wf("bed")) / 0.9), 1, 1 - clamp((t - wf("bed") - 0.5) / 0.4))
        btn, tap = follow_button(fol, 540, 900)
        E += [S(plane(540, 640, 1.4), 0.05, color=RED, width=5, anim=fly, sfx="scribble", g=0.2),
              cue(wf("bed"), "whoosh", 0.6),
              E_(wf("and") - 0.15, btn, 0.5, sfx="pop", g=0.6), E_(fol - 0.5, tap, 0.01), cue(fol + 0.02, "click", 0.7)]
    return E
