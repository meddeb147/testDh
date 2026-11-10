"""Example scenes file: "Why Men Pull Away" (relationships genre, tender mood).
Real, shipped video. Older style: times by word index w(k); prefer wf("word") in new scenes, S/F/E_/cue elements with sfx, anim lambdas, te= exits."""
from engine import *

THEME = "relationships"
MOOD = "tender"
LABEL = "WHY MEN PULL AWAY"

SCENES = [
    "Why does a man pull *away* | from the woman he loves, | right when life gets *hardest?*",
    "From the outside, | it makes *no sense.* | If he loves her, | why would he *push her away?*",
    "But here's something | most people *don't understand.*",
    "What a man *feels* | and how he *deals* with those feelings | are two very *different* things.",
    "When everything in his life | starts *falling apart,* | when he feels lost, exhausted, | and completely *out of control,*",
    "he isn't thinking about | how to keep her close. | He's thinking about how to keep | his problems from *reaching her.*",
    "In his mind, it's simple: | If I'm on *fire,* | I need to *protect the people I love* | from getting burned.",
    "Imagine his life | as a *sinking ship.* | Instead of asking her for help, | he *pushes her away.*",
    "And he stays on board, | because it's his ship, | his responsibility. | He believes he has to *save it…* | or *sink with it.*",
    "Here's where things go *wrong.* | In trying to protect her, | he *forgets how to let her love him.* | He becomes distant. | He stops talking. | He *shuts down* emotionally.",
    "Not necessarily because | his feelings are *gone,* | because somewhere deep inside, | he believes he has to face everything | *alone.*",
    "And that's where so many men | *lose the very thing* | they're trying to protect.",
    "So many relationships | end like this. | Not because the love *disappeared,*",
    "because she sees his silence | as *rejection,* | and he sees her attempts to get closer | as more *pressure,* | instead of support.",
    "If they could only understand | what the other person was going through, | they might've made it | *through the storm together.*",
    "So if he starts pulling away, | don't *chase* him. | Don't *disappear* either.",
    "Just let him know: | *I'm not here to add to your problems.* | *I'm here because I love you.* | You don't have to go through everything *alone.*",
    "Because the right kind of closeness | doesn't make the storm *heavier…* | it makes it *easier to survive.*",
    "Send this to someone | who *needs to hear it.* | And follow for more.",
]


def build(i, w, wf):
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
