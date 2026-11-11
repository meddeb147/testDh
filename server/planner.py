"""Turn any voice-over script into scenes + an automatic visual plan, and build() for the engine.

The plan is plain JSON (stored with the project) so a project can be re-rendered in another theme or format
without re-planning:  scene = {text, words, template, main, beats:[[word_index, kind]], neg, question, people, numbers}"""
import re, math
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vme"))
from engine import *          # noqa: F401,F403  (icons, effects, S/F/E_/cue, colors)
import engine as _eng

# ---------------------------------------------------------------- keyword -> visual kind (prefix match, any language
# keywords are English; other languages still get people/numbers/questions/negations and a rotating icon set)
LIB = {
    "heart":     "love heart care caring feel feeling romance kiss crush darling miss adore cherish amour corazon",
    "broken":    "broke broken break hurt pain heartbreak betray cheat lied lie lost tears",
    "phone":     "phone text message call notification screen scroll chat dm reply inbox ring",
    "door":      "door leave left leaving gone goodbye exit walked walk away quit",
    "eye":       "see saw look watch notice noticed eyes stare staring seen saw",
    "ear":       "hear heard listen listening voice sound whisper",
    "moon":      "night midnight dark darkness sleep asleep bed 3am dream",
    "clock":     "time hour hours minute clock late wait waiting years year days week month forever",
    "storm":     "storm rain sad sadness cry crying tears lonely alone depressed",
    "bolt":      "shock sudden suddenly angry fight fighting argue argument scream yell explode",
    "flame":     "fire burn burning passion anger rage hot desire",
    "bulb":      "idea realize realized understand learn truth secret know knew discover answer lesson",
    "qmark":     "why question wonder mystery unknown",
    "warning":   "danger dangerous careful warning red flag rule rules never",
    "battery":   "tired exhausted exhaustion energy drained drain burnout",
    "target":    "goal goals focus win success aim achieve purpose",
    "shield":    "protect protecting safe safety defend guard",
    "boat":      "ship sink sinking ocean sea drown drowning boat",
    "steps":     "walk walking steps step follow path journey run running",
    "monitor":   "heartbeat alive dead die died death flatline breathe breath",
    "money":     "money rich cash pay paid dollar dollars broke salary price",
    "mind":      "mind think thinking brain thought thoughts overthink overthinking psychology brain",
    "sun":       "morning sunrise light hope bright sunshine shine",
    "stairs":    "stairs downstairs upstairs basement attic",
    "eyes_dark": "something someone shadow creature thing ghost monster haunted watching behind",
    "house":     "home house family room kitchen",
    "star":      "star famous magic wish special shine",
    "up":        "rise grow growth better climb higher stronger level",
    "down":      "fall falling fell lower worse drop",
}
KW = {}
for kind, words in LIB.items():
    for w in words.split(): KW.setdefault(w, kind)
STOP = set("""a an the and or but so to of in on at for with from by is are was were be been being it its it's this that these those
i me my you your he him his she her we our they them their what when where who how not no do does did don't doesn't didn't
just very really then than there here as if into out up down about over again more most some any all can can't will would
should could may might must one two only also too even still yet le la les un une des et de du que qui est pas ne en el los las
y es por para con""".split())
NEG = set("not never no don't doesn't didn't stop won't can't nothing nobody isn't wasn't ne pas jamais nunca no".split())
PEOPLE_F = set("she her woman women girl girls wife girlfriend mom mother sister daughter queen elle femme".split())
PEOPLE_M = set("he him his man men boy boys husband boyfriend dad father brother son king il homme".split())
PEOPLE_N = set("they them partner couple people someone friend friends we us".split())
CTA = ("follow", "subscribe", "send this", "share this", "tag", "comment", "save this", "abonne", "suis")
ICON_ORDER = ["heart", "bulb", "clock", "eye", "storm", "door", "qmark", "phone", "sun", "mind", "target", "steps"]


def norm(w): return re.sub(r"[^\w'’]", "", w.lower()).replace("’", "'")


def kind_of(word):
    n = norm(word)
    if n in KW: return KW[n]
    for k in (n[:-1], n[:-2], n[:-3]):              # plural / -ed / -ing
        if len(k) > 3 and k in KW: return KW[k]
    return None


# ---------------------------------------------------------------- scene splitting + caption cards
def split_scenes(text, lo=9, hi=24):
    text = re.sub(r"\s+", " ", text.replace("\n", " ")).strip()
    # sentence ends: . ! ? (plus closing quote); an ellipsis only when the next word starts a new sentence
    sents = [s.strip() for s in re.split(r"(?<=[.!?][”\"'])\s+|(?<=[.!?])\s+|(?<=…)\s+(?=[A-Z“\"])", text) if s.strip()]
    pieces = []
    for s in sents:                                   # split very long sentences at commas
        if len(s.split()) > hi:
            parts, cur = re.split(r"(?<=[,;:])\s+", s), ""
            for p in parts:
                if cur and len((cur + " " + p).split()) > hi: pieces.append(cur); cur = p
                else: cur = (cur + " " + p).strip()
            if cur: pieces.append(cur)
        else: pieces.append(s)
    scenes, cur = [], ""
    for p in pieces:
        if cur and (len(cur.split()) >= lo or len((cur + " " + p).split()) > hi): scenes.append(cur); cur = p
        else: cur = (cur + " " + p).strip()
    if cur:
        if scenes and len(cur.split()) < 4: scenes[-1] += " " + cur
        else: scenes.append(cur)
    return scenes


def make_cards(words, maxw=6):
    cards, cur = [], []
    for w in words:
        cur.append(w)
        if (re.search(r"[.!?…,:;]['”\"]?$", w) and len(cur) >= 2) or len(cur) >= maxw: cards.append(cur); cur = []
    if cur:
        if cards and len(cur) == 1: cards[-1] += cur
        else: cards.append(cur)
    return cards


def plan_scene(i, text, n_scenes, genre=""):
    words = text.split()
    ns = [norm(w) for w in words]
    beats = [[k, kind_of(w)] for k, w in enumerate(words) if kind_of(w)]
    seen, uniq = set(), []
    for k, kd in beats:                               # one beat per kind, max 3
        if kd not in seen: seen.add(kd); uniq.append([k, kd])
    beats = uniq[:3]
    content = sorted([k for k, n in enumerate(ns) if n not in STOP and len(n) > 3], key=lambda k: -len(ns[k]))
    hl = sorted(set([k for k, _ in beats][:2] or content[:1]))
    if len(hl) == 2 and hl[1] - hl[0] < 2: hl = hl[:1]
    if len(hl) < 2 and content:
        extra = [k for k in content if k not in hl and abs(k - (hl[0] if hl else -9)) > 1]
        hl = sorted(hl + extra[:1])
    neg = next((k for k, n in enumerate(ns) if n in NEG), None)
    nums = [[k, re.sub(r"[^\d%:,.]", "", w).strip(".,")] for k, w in enumerate(words) if re.search(r"\d", w)]
    fem, mal = any(n in PEOPLE_F for n in ns), any(n in PEOPLE_M for n in ns)
    people = "duo" if (fem and mal) or any(n in PEOPLE_N for n in ns) else "woman" if fem else "man" if mal else None
    low = text.lower()
    is_cta = i == n_scenes - 1 and any(c in low for c in CTA)
    is_list = len(re.findall(r"[.!?]", text)) >= 3 and len(words) <= 14
    main = beats[0][1] if beats else ICON_ORDER[(i * 5 + len(words)) % len(ICON_ORDER)]
    template = "cta" if is_cta else "number" if nums else "list" if is_list else \
        "duo" if people == "duo" else "solo" if people else "hero"
    return dict(text=text, words=words, hl=hl, template=template, main=main, beats=beats, neg=neg,
                question=text.rstrip("”\"' ").endswith("?"), people=people, numbers=nums, cta=is_cta)


def caption_text(sc):
    """SCENES string with | card breaks and *highlights* (keeps the words exactly as spoken)."""
    words, hl = list(sc["words"]), set(sc["hl"])
    out, k = [], 0
    for card in make_cards(words):
        toks = []
        for w in card:
            if k in hl:
                m = re.match(r"^([“\"'(]*)(.*?)([.,!?…:;”\"')]*)$", w)
                pre, core, post = m.groups()
                w = f"*{pre}{core}{post}*" if core else w
            toks.append(w); k += 1
        out.append(" ".join(toks))
    return " | ".join(out)


def make_plan(script, genre=""):
    texts = split_scenes(script)
    return [plan_scene(i, t, len(texts), genre) for i, t in enumerate(texts)]


# ---------------------------------------------------------------- drawing helpers
def scaled(polys, cx, cy, s):
    return [[(cx + (x - cx) * s, cy + (y - cy) * s) for x, y in q] for q in polys]


def clock_face(x, y, r):
    return [arc(x, y, r, 0, 360), [(x, y), (x, y - r * 0.6)], [(x, y), (x + r * 0.45, y + r * 0.1)]]


def coin(x, y, r=60):
    return [arc(x, y, r, 0, 360), arc(x, y, r * 0.78, 0, 360),
            join(bez((x + 18, y - 22), (x + 5, y - 32), (x - 24, y - 26), (x - 16, y - 6)),
                 bez((x - 16, y - 6), (x - 8, y + 6), (x + 22, y + 2), (x + 16, y + 22)),
                 bez((x + 16, y + 22), (x + 8, y + 34), (x - 14, y + 30), (x - 20, y + 20))), [(x, y - 42), (x, y + 42)]]


def house(x, y, s=1.0):
    P = lambda a, b: (x + a * s, y + b * s)
    return [[P(-90, 0), P(-90, -110), P(0, -180), P(90, -110), P(90, 0), P(-90, 0)], [P(-25, 0), P(-25, -60), P(25, -60), P(25, 0)]]


def star(x, y, r=60):
    pts = [(x + (r if k % 2 == 0 else r * 0.45) * math.cos(-math.pi / 2 + k * math.pi / 5),
            y + (r if k % 2 == 0 else r * 0.45) * math.sin(-math.pi / 2 + k * math.pi / 5)) for k in range(11)]
    return [pts]


def stairs(x, y, n=6, run=55, rise=45):
    pts = [(x, y)]
    for _ in range(n):
        a, b = pts[-1]; pts += [(a, b - rise), (a + run, b - rise)]
    return [pts]


def phone_shape(x, y, s=1.0):
    P = lambda a, b: (x + a * s, y + b * s)
    return [join([P(-50, -90), P(50, -90), P(50, 90), P(-50, 90), P(-50, -90)]), [P(-15, -76), P(15, -76)], arc(x, y + 72 * s, 5 * s, 0, 360, 10)]


def eyes_dark(x, y, t_on, size=1.0):
    def d(ctx, p, t):
        a = ease_io((t - t_on) / 0.8)
        open_ = 1 - 0.9 * math.sin(clamp((((t - t_on) % 2.6) - 2.3) / 0.18) * math.pi)
        for sgn in (-1, 1):
            ex = x + sgn * 22 * size
            pts = [(ex + 11 * size * math.cos(u), y + 5 * size * open_ * math.sin(u)) for u in [k * math.pi / 12 for k in range(25)]]
            ctx.move_to(*pts[0]); [ctx.line_to(*q) for q in pts[1:]]; ctx.close_path()
            ctx.set_source_rgba(*RED, a); ctx.fill()
    return d


def big_text(x, y, s, t0, size=150):
    def d(ctx, p, t):
        k = max(ease_back(p), 1e-3)
        ctx.save(); ctx.translate(x, y); ctx.scale(k, k)
        set_font(ctx, _eng.STYLE["cap_font"]); ctx.set_font_size(size)
        e = ctx.text_extents(s); ctx.set_source_rgb(*RED); ctx.move_to(-e.x_advance / 2, size * 0.35); ctx.show_text(s)
        ctx.restore()
    return d


def icon(kind, x, y, s, t0, color=None, te=None, anim=None, slow=False):
    """One visual for a kind, centred at (x, y), scale s. Returns a list of elements (with their sounds).
    Elements scale and rotate about the icon's own centre."""
    els = _icon(kind, x, y, s, t0, color, te, anim, slow)
    for e in els:
        if getattr(e, "pivot", None) == (540, 800): e.pivot = (x, y)
    return els


def _icon(kind, x, y, s, t0, color=None, te=None, anim=None, slow=False):
    c = color or INK; dur = 1.4 if slow else None
    piv = dict(pivot=(x, y))
    if kind == "heart":
        return [F(heart_pts(x, y, 46 * s), t0, (x, y), beat=True, sfx="heartbeat", g=0.5, te=te, anim=anim, **piv)]
    if kind == "broken":
        out, cr = broken_heart(x, y, 46 * s)
        return [S(out, t0, color=RED, width=5, sfx="crack", g=0.5, te=te, anim=anim, dur=dur),
                S(cr, t0 + 0.35, color=RED, width=5, sfx=None, te=te, anim=anim)]
    if kind == "phone":
        return [S(phone_shape(x, y, s), t0, sfx="buzz", g=0.5, te=te, anim=anim, dur=dur), rings(x, y, t0 + 0.3, r0=50 * s, span=60 * s, t_off=te)]
    if kind == "door":
        return [S(door(x, y + 90 * s, 120 * s, 210 * s), t0, sfx="thud", g=0.5, te=te, anim=anim, dur=dur)]
    if kind == "eye":
        return [S(eye(x, y, 1.3 * s), t0, sfx="whoosh", g=0.3, te=te, anim=anim, dur=dur)]
    if kind == "ear":
        return [S(ear(x, y, 1.2 * s), t0, sfx="pop", g=0.3, te=te, anim=anim, dur=dur), E_(t0 + 0.3, sound_waves(x + 50 * s, y - 20 * s, t0), 0.01, te=te)]
    if kind == "moon":
        return [S([q for q in scaled([arc(x, y, 50, 70, 290), arc(x + 22, y - 5, 41, 250, 110)], x, y, s)], t0, sfx="whoosh", g=0.3, te=te, anim=anim, dur=dur)]
    if kind == "clock":
        return [E_(t0, hourglass(x, y, t0 + 0.3, t0 + 3.5), 0.5, sfx="sand", g=0.35, te=te, anim=anim, **piv)]
    if kind == "storm":
        return [S(cloud(x, y, 1.5 * s), t0, sfx="rain", g=0.4, te=te, anim=anim, dur=dur), rain(x - 70 * s, x + 70 * s, y + 30 * s, y + 220 * s, t0 + 0.3, te, n=16)]
    if kind == "bolt":
        return [S(cloud(x, y - 40 * s, 1.4 * s), t0, te=te, anim=anim), S(bolt(x + 10 * s, y + 40 * s, 0.8 * s), t0 + 0.3, color=RED, width=5, sfx="thunder", g=0.5, te=te, anim=anim)]
    if kind == "flame":
        return [F(flame(x, y, 0.9 * s), t0, (x, y), color=RED, flicker=True, sfx="fire", g=0.4, te=te, anim=anim)]
    if kind == "bulb":
        return [S(scaled(bulb(x, y), x, y, s), t0, sfx="chime", g=0.4, te=te, anim=anim, dur=dur),
                S(rays(x, y, 80 * s, 115 * s, 10, -math.pi / 2), t0 + 0.5, color=RED, width=4, sfx=None, te=te, anim=anim)]
    if kind == "qmark":
        return [S(qmark(x, y, 2.2 * s), t0, color=RED, width=6, sfx="pop", g=0.4, te=te,
                  anim=anim or (lambda t: (0, 0, 1, 1, 0.12 * math.sin(t * 4))), **piv)]
    if kind == "warning":
        return [S(warning(x, y), t0, color=RED, width=5, sfx="buzz", g=0.4, te=te,
                  anim=anim or (lambda t: (0, 0, s * (1 + 0.05 * math.sin(t * 10)), 1)), **piv)]
    if kind == "battery":
        return [E_(t0, battery(x, y, t0 + 0.4, t0 + 2.6), 0.5, sfx="powerdown", g=0.4, te=te, anim=anim, **piv)]
    if kind == "target":
        return [S(scaled(target(x, y), x, y, 1.4 * s), t0, sfx="pop", g=0.4, te=te, anim=anim, dur=dur),
                S(arrow(x + 150 * s, y - 120 * s, x + 8, y - 6, 18), t0 + 0.5, color=RED, width=5, sfx="whoosh", g=0.4, te=te, anim=anim)]
    if kind == "shield":
        return [S(shield(x, y, 1.6 * s), t0, sfx="shield", g=0.4, te=te, anim=anim, dur=dur)]
    if kind == "boat":
        return [S(boat(x, y, 0.9 * s), t0, sfx="water", g=0.35, te=te, anim=anim, dur=dur), S(waves(x, y + 60 * s, 320 * s, 10, 3, 2), t0 + 0.2, sfx=None, te=te)]
    if kind == "steps":
        return [E_(t0, footprints(x - 200 * s, y + 40, x + 200 * s, y - 40, t0, 1.8), 0.01, sfx="steps", g=0.4, te=te)]
    if kind == "monitor":
        return [E_(t0, monitor(x - 300 * s, x + 300 * s, y, t0, t0 + 1.0, t0 + 2.4), 0.01, sfx="beeps", g=0.3, te=te)]
    if kind == "money":
        return [S(coin(x, y, 62 * s), t0, color=RED, width=5, sfx="click", g=0.5, te=te, anim=anim, dur=dur)]
    if kind == "mind":
        return [S(head_profile(x, y, 1.2 * s), t0, sfx="scribble", g=0.25, te=te, anim=anim, dur=dur),
                S(scaled(gear(x, y - 20 * s, 24), x, y - 20 * s, s), t0 + 0.6, color=RED, width=4, sfx="switch", g=0.4, te=te,
                  anim=lambda t: (0, 0, 1, 1, (t - t0) * 1.5), pivot=(x, y - 20 * s))]
    if kind == "sun":
        return [S(sun(x, y, 50 * s), t0, color=RED, width=5, sfx="chime", g=0.35, te=te, anim=anim, dur=dur),
                S(rays(x, y, 68 * s, 100 * s, 12), t0 + 0.4, color=RED, width=4, sfx=None, te=te,
                  anim=lambda t: (0, 0, 1, 1, 0.15 * (t - t0)), pivot=(x, y))]
    if kind == "stairs":
        return [S(stairs(x - 165 * s, y + 140 * s, 6, 55 * s, 45 * s), t0, sfx="steps", g=0.4, te=te, anim=anim, dur=dur or 1.2)]
    if kind == "eyes_dark":
        return [E_(t0, eyes_dark(x, y, t0, 1.4 * s), 0.01, sfx="heartbeat", g=0.5, te=te)]
    if kind == "house":
        return [S(house(x, y + 90 * s, s), t0, sfx="scribble", g=0.25, te=te, anim=anim, dur=dur)]
    if kind == "star":
        return [S(star(x, y, 70 * s), t0, color=RED, width=5, sfx="chime", g=0.35, te=te,
                  anim=anim or (lambda t: (0, 0, 1 + 0.06 * math.sin(t * 5), 1)), **piv)]
    if kind == "up":
        return [S(arrow(x - 120 * s, y + 120 * s, x + 120 * s, y - 120 * s, 26), t0, color=RED, width=6, sfx="whoosh", g=0.45, te=te, anim=anim)]
    if kind == "down":
        return [S(arrow(x - 120 * s, y - 120 * s, x + 120 * s, y + 120 * s, 26), t0, color=RED, width=6, sfx="whoosh", g=0.45, te=te, anim=anim)]
    return [S(qmark(x, y, 2 * s), t0, color=RED, width=6, sfx="pop", g=0.4, te=te)]


def follow_cta(fol, cx=540, cy=820, label="Follow", done="Following"):
    def btn(ctx, p, t):
        s = max(ease_back(p), 1e-3)
        if t > fol: s *= 1 - 0.07 * math.sin(clamp((t - fol) / 0.25) * math.pi)
        ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s)
        bw, r = 360, 52
        ctx.new_sub_path(); ctx.arc(-bw / 2 + r, 0, r, math.pi / 2, 3 * math.pi / 2); ctx.arc(bw / 2 - r, 0, r, -math.pi / 2, math.pi / 2)
        ctx.close_path(); ctx.set_source_rgb(*RED); ctx.fill()
        set_font(ctx, _eng.STYLE["cap_font"]); lab = ("+ " + label) if t < fol + 0.5 else ("✓ " + done)
        ctx.set_font_size(44 if t < fol + 0.5 else 38); e = ctx.text_extents(lab)
        ctx.set_source_rgb(1, 1, 1); ctx.move_to(-e.x_advance / 2, 15); ctx.show_text(lab); ctx.restore()
        if t > fol:
            ph = clamp((t - fol) / 0.7); ctx.set_source_rgba(*RED, 0.5 * (1 - ph)); ctx.set_line_width(4)
            ctx.arc(cx + 60, cy + 20, 20 + 90 * ph, 0, 2 * math.pi); ctx.stroke()

    def tap(ctx, p, t):
        k = ease_out((t - (fol - 0.5)) / 0.5); press = math.sin(clamp((t - fol) / 0.25) * math.pi) * 8
        x, y = cx + 100 + 120 * (1 - k), cy + 60 + 140 * (1 - k) + press
        stroke_partial(ctx, [join([(x - 12, y + 70)], [(x - 12, y)], arc(x, y, 12, 180, 360), [(x + 12, y + 30)]),
                             [(x + 12, y + 30), (x + 34, y + 36), (x + 36, y + 80)]], 1.0, INK, 4)
    return [E_(max(0.1, fol - 1.0), btn, 0.5, sfx="pop", g=0.6), E_(fol - 0.5, tap, 0.01), cue(fol + 0.02, "click", 0.7)]


def pulse_on(t_word, amp=0.12):
    """anim: a quick scale bump when the keyword is spoken (the icon itself is already on screen)."""
    return lambda t: (0, 0, 1 + amp * math.sin(math.pi * clamp((t - t_word) / 0.35)) if t > t_word else 1, 1)


def make_build(plan, slow=False, cta_label=("Follow", "Following")):
    """build(i, w, wf) for engine.render from a plan (list of plan_scene dicts)."""
    def build(i, w, wf):
        sc = plan[i]; E = []; n = len(sc["words"])
        beats = [(w(k), kd) for k, kd in sc["beats"]]
        t_first = w(sc["hl"][0]) if sc["hl"] else 0.3
        main = sc["main"]; tpl = sc["template"]
        neg_t = w(sc["neg"]) if sc["neg"] is not None else None
        sway = lambda t: (0, 0, 1, 1, 0.02 * math.sin(t * 1.4))
        if tpl == "cta":
            fol = next((w(k) for k, x in enumerate(sc["words"]) if norm(x) in ("follow", "subscribe", "abonne", "suis")), w(n - 2))
            fly = lambda t: (300 * ease_io((t - fol + 1.2) / 0.9), -220 * ease_io((t - fol + 1.2) / 0.9), 1, 1 - clamp((t - fol + 0.7) / 0.4))
            E += [S(plane(540, 600, 1.4), 0.05, color=RED, width=5, anim=fly, sfx="scribble", g=0.2), cue(fol - 1.2, "whoosh", 0.6)]
            E += follow_cta(fol, *(540, 860), *cta_label)
            return E
        if tpl == "number":
            k, val = sc["numbers"][0]
            E += [E_(w(k) - 0.1, big_text(540, 700, val or sc["words"][k], w(k)), 0.45, sfx="thud", g=0.6)]
            if beats: E += icon(beats[0][1], 540, 930, 0.8, beats[0][0], slow=slow)
            return E
        if tpl == "list":
            starts = [0] + [k + 1 for k, x in enumerate(sc["words"][:-1]) if re.search(r"[.!?]$", x)]
            kinds = [kd for _, kd in sc["beats"]] + [ICON_ORDER[(i + j) % len(ICON_ORDER)] for j in range(3)]
            for j, k0 in enumerate(starts[:3]):
                E += icon(kinds[j], 220 + 320 * j, 760, 0.95, w(k0) - 0.05, slow=slow)
            return E
        if tpl == "duo":
            E += [S(woman(300, 1030), 0.05, sfx="scribble", g=0.15), S(man(780, 1030), 0.25, sfx=None)]
            tw = beats[0][0] if beats else t_first
            E += icon(main, 540, 640, 0.9, min(tw, 0.6), slow=slow, te=(beats[1][0] - 0.3) if len(beats) > 1 else None, anim=pulse_on(tw))
            E += [cue(tw, "pop", 0.3)] if tw > 0.8 else []
            if len(beats) > 1: E += icon(beats[1][1], 540, 640, 0.9, beats[1][0], slow=slow)
            if neg_t is not None and neg_t > 0.4:
                E += [S(arrow(380, 760, 700, 760, 18), neg_t - 0.1, color=GREY, width=4, sfx=None),
                      S(crossx(540, 760, 34), neg_t + 0.15, color=RED, width=6, sfx="buzz", g=0.4)]
        elif tpl == "solo":
            fig = woman if sc["people"] == "woman" else man
            E += [S(fig(300, 1040, 1.15), 0.05, sfx="scribble", g=0.15, anim=sway, pivot=(300, 1040)),
                  S(bubble(700, 640, 330, 270), max(0.1, t_first - 0.6), sfx="pop", g=0.25)]
            tw = beats[0][0] if beats else t_first
            E += icon(main, 700, 630, 0.85, min(tw, max(0.3, t_first - 0.3)), slow=slow, te=(beats[1][0] - 0.3) if len(beats) > 1 else None, anim=pulse_on(tw))
            if len(beats) > 1: E += icon(beats[1][1], 700, 630, 0.85, beats[1][0], slow=slow)
            if neg_t is not None: E += [S(crossx(700, 630, 120), neg_t + 0.1, color=RED, width=7, sfx="buzz", g=0.45)]
        else:   # hero: one big metaphor, then a second beat beside it
            tw = beats[0][0] if beats else t_first
            E += icon(main, 540, 790, 1.75, max(0.05, min(tw - 0.2, 0.5)), slow=slow, anim=pulse_on(tw))
            E += [cue(tw, "pop", 0.3)] if tw > 0.8 else []
            if len(beats) > 1: E += icon(beats[1][1], 540, 470, 0.7, beats[1][0], slow=slow)
            if neg_t is not None: E += [S(crossx(540, 790, 170), neg_t + 0.1, color=RED, width=8, sfx="buzz", g=0.45)]
            E += [rings(540, 790, tw, r0=190, span=120)] if not slow and main not in ("monitor", "steps") else []
        if sc["question"] and main != "qmark":
            E += icon("qmark", 900, 470 if tpl != "hero" else 560, 0.6, max(0.2, w(n - 1) - 0.3))
        return E
    return build
