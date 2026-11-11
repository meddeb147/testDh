"""Example scenes file: "When She Goes Quiet" (relationships genre, tender mood).
Real, shipped video. Read it to learn the idioms: wf("word") timing, S/F/E_/cue elements with sfx, anim lambdas, te= exits."""
from engine import *

THEME = "relationships"
MOOD = "tender"
LABEL = "WHEN SHE GOES QUIET"

SCENES = [
    "When a woman stops *fighting* with you, | it doesn't necessarily mean | she's at *peace.* | It might mean | she's slowly *giving up.*",
    "Most men make the *same mistake.* | They think silence means | everything is finally *okay.* | No more arguments. | No more complaints. | No more difficult conversations.",
    "But here's what they *don't understand:* | a woman who keeps arguing | may still be trying | to *save the relationship.* | Because behind every complaint, | there's often a simple message:",
    "*See me.* | *Hear me.* | *Make me feel like I matter.*",
    "At first, she asks gently. | Then she asks again. | She tries to explain. | Sometimes she *cries.* | Sometimes she gets *angry.* | Not because she enjoys fighting, | but because she's *hoping* | something will finally *change.*",
    "And every time, | she hears the *same things:* | “You're overreacting.” | “Not now.” | “Let's talk about it later.”",
    "Until one day, | something inside her *changes.* | She stops *expecting…* | and starts *adjusting.*",
    "She learns to do things *alone.* | To solve problems alone. | To deal with things | without asking for help. | She cries in the shower | just so nobody *hears her.*",
    "And slowly, | she stops telling him about her day. | Not because nothing happens anymore, | but because she stopped believing | you really *listen.*",
    "And that's the *dangerous* part. | On the outside, she looks calm. | Quiet. | Easy to be around. | But don't confuse her *silence* | with *happiness.*",
    "Sometimes it's emotional *exhaustion.* | Sometimes it's a *goodbye,* | happening slowly, | one silent day at a time.",
    "By the time he finally notices… | she's already *gone.* | Not necessarily with a suitcase… | with her *heart.*",
    "Then he says, | “She left out of *nowhere.*” | She didn't. | She tried to tell him, | again and again. | She was slowly walking away | for *years.* | He just never *noticed.*",
    "So if she's still complaining, | don't immediately *shut her down.* | Don't treat every conversation | like an *attack.* | Sometimes she's not fighting *against* you. | She's fighting *for the relationship.*",
    "Listen while she's still *talking.* | Pay attention while she still wants to *explain.* | Because sometimes the most heartbreaking moment | in a relationship | isn't when someone starts *shouting…* | it's when they finally *stop.*",
    "Send this to someone | who *needs to hear it.* | And follow for more.",
]


def build(i, w, wf):
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
              F(flame(560, 920, 0.45), hope + 0.4, (560, 920), flicker=True, sfx="fire", g=0.3),
              E_(wf("change"), lambda ctx, p, t: (ctx.set_source(glow(560, 900, 140, 0.25 * ease_out((t - wf("change")) / 0.6))), ctx.paint()), 0.01)]
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
              E_(wf("day"), lambda ctx, p, t: cal_page(ctx, t - wf("day")), 0.01, te=ch - 0.3),
              S(woman(330, 1050), 0.2),
              E_(ch, heart_emptying(330, 790, 36, ch), 0.4, sfx="heartbeat", g=0.35),
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
              F(flame(588, 870, 0.18), wf("nobody"), (588, 870), color=(0.35, 0.5, 0.75), sfx="pop", g=0.2,
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
              S(shield(650, 720, 0.9), wf("attack") - 0.3, te=fr - 0.5),
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
        E += [S(plane(540, 620, 1.3), 0.05, color=RED, anim=fly), cue(wf("it"), "whoosh", 0.6)]
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
