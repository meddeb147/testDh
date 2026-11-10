# Step 3: writing `scenes.py`

## Contents
1. File shape
2. Caption syntax
3. Timing: `wf` and `w`
4. Elements: S / F / E_ / cue
5. Motion: anim, te, pivot
6. Icon and effect catalog
7. Sound names
8. Visual vocabulary per genre
9. Layout rules and QA checklist

## 1. File shape

```python
from engine import *          # render.py / align.py put scripts/ on the path

THEME = "horror"               # romance|relationships|horror|comedy|motivation|mystery|facts, or a dict
MOOD = "dark"                  # music: tender|dark|playful|uplifting
LABEL = "THE 3AM RULE"         # small caps title at the top of every frame ("" to hide)
TAIL = 1.8                     # seconds held after the voice ends (CTA button)

SCENES = [                     # one string per scene; must match the recording word-for-word
    "If you hear *knocking* | at 3am… | don't *answer.*",
    ...
]

def build(i, w, wf):
    """Return the list of elements for scene i. wf("word") = scene-local time that word is spoken."""
    E = []
    if i == 0:
        E += [S(door(540, 1000, 160, 300), 0.05),
              S(qmark(540, 560, 1.4), wf("knocking"), color=RED, sfx="thud", g=0.6),
              ...]
    elif i == 1:
        ...
    return E
```

The scene's start/end and the crossfades between scenes come from the timings automatically. Every scene also
gets a slow push-in, a subtle drift, a whoosh transition, and a punch-zoom on each highlighted phrase.

## 2. Caption syntax

- `|` splits a scene into caption cards (2–8 words each; a card replaces the previous one when its first word is spoken).
- `*word*` or `*several words*` = accent color + pop + hand-drawn underline. Highlight 1–3 key phrases per scene, not more.
- Keep punctuation as spoken; quotes `“…”` are fine. Words must match the audio (alignment is word-for-word).

## 3. Timing

- `wf("word")` → time of the first occurrence; `wf("she", 2)` → the second. It matches case- and punctuation-insensitively,
  and raises `KeyError` with the scene text if the word isn't there.
- `w(k)` → time of the k-th word (0-based). Fine for quick work, but fragile when text changes.
- Start visuals **0.1–0.3 s before** the word for drawings that take time (`wf("ship") - 0.2`). Pops and sound hits go *on* the word.

## 4. Elements

| Call | What it is |
|---|---|
| `S(polys, t0, color=INK, width=4, dur=None, sfx="scribble", g=0.16, te=None, anim=None, pivot=(540,800))` | Hand-drawn stroke that draws itself on. `polys` = list of point lists (any icon below). `dur=0.01` = appear instantly (no sound). |
| `F(poly, t0, center, color=RED, beat=False, flicker=False, sfx="pop", g=0.5, …)` | Filled shape popping in with overshoot. `beat=True` makes a heartbeat pulse; `flicker=True` is a flame flicker (anchored at the bottom). Use `heart_pts(x,y,size)` or `flame(x,y,s)` as the poly. |
| `E_(t0, draw_fn, dur, sfx=None, g=…, te=…, anim=…)` | Custom draw: `draw_fn(ctx, p, t)` with p = 0→1 reveal progress over `dur`, t = scene time. Many catalog effects are factories returning a draw_fn. |
| `cue(t, "sound", g)` | A sound with no visual. |

`sfx=None` silences an element. Gains: 0.2 subtle, 0.4–0.6 normal, 0.8 big moment.

## 5. Motion

- `te=time` makes the element fade out from that time (0.35 s), e.g. to clear the stage mid-scene.
- `anim=lambda t: (dx, dy, scale, alpha, rotation)` returns a tuple of 2–5 values; scale and rotation are about `pivot`.
- Helpers: `slide(t0, dx, dur=0.9, dy=0)`, `shake(t0, amp, dur)`, easing `ease_io`, `ease_out`, `ease_back`, `ease_in_`, `clamp`.
- Examples:
  - walk away: `anim=slide(wf("leaves"), 150)`
  - sink: `anim=lambda t: (0, 45*ease_io((t-T)/2), 1, 1, 0.14*ease_io((t-T)/2))`
  - fade to 25%: `anim=lambda t: (0, 0, 1, 1-0.75*ease_io((t-T)/1.5))`
  - fall: `lambda t: (0, 230*clamp((t-T)/0.7)**2)`
- Reuse the same `anim` on several elements to move a group together (a boat and the man on it).

## 6. Catalog (all in `engine.py`)

**People and body:** `man(x,y,s)`, `woman(x,y,s)` (y = feet), `head_profile(x,y,s)`, `eye(x,y,s)`, `closed_eye(x,y)`, `ear(x,y,s)`, `hand(x,y)` (raised palm).
**Hearts and emotion:** `heart(x,y,size)` (outline), `heart_pts` (fill), `broken_heart(x,y,size)` → (outline, crack), `heart_emptying(x,y,size,t0)`, `mask_face(cx,cy,t_reveal)` (smile mask slides off to reveal a frown + tear).
**Weather and nature:** `cloud(x,y,s)`, `bolt(x,y,s)`, `rain(x0,x1,y0,y1,t_on,t_off,n,speed,color,alpha)`, `sun(x,y,r)` + `rays(x,y,r0,r1,n)`, `moon(x,y,r)`, `waves(x,y,w,amp,n,rows,gap)`, `flame(x,y,s)`, `sparks(x0,y0,x1,y1,t_on,t_off)`.
**Objects:** `door(x,y,w,h)`, `boat(x,y,s)`, `umbrella(x,y,r)`, `anchor(x,y,s)`, `flag(x,y)`, `lifebuoy(cx,cy)`, `candle(x,y)`, `toolbox(x,y)`, `shower(x,y)`, `suitcase(x,y)`, `bulb(x,y)`, `gear(x,y,r)`, `shield(x,y,s)`, `target(x,y)`, `plane(x,y,s)` (paper plane), `pit(x,y)`, `ground(x,y,w)`.
**UI and symbols:** `bubble(x,y,w,h)`, `dots_bubble(x,y)`, `arrow(x0,y0,x1,y1,head)`, `crossx(x,y,r)`, `qmark(x,y,s)`, `warning(x,y)`, `toggle(cx,cy,t_flip)`, `phone_typing(cx,cy,msg,t_type,t_del)`, `battery(cx,cy,t_drain,t_end)`, `hourglass(cx,cy,t0,t1)`, `monitor(x0,x1,cy,t_on,t_loud,t_flat)` (voice or heart line that flatlines), `sound_waves(x,y,t0)`, `rings(x,y,t_on)` (pulsing halo), `footprints(x0,y0,x1,y1,t0,dur)`, `cal_page(ctx, dt)` (tearing calendar page; use inside an E_).
**Building blocks for new icons:** `arc(cx,cy,r,a0,a1)` (degrees, 0 = right, 90 = down), `bez(p0,p1,p2,p3)`, `join(...)`, `wobble(poly)` (S applies it automatically), `stroke_partial`, `fill_poly`, `glow(x,y,r,alpha)` (radial gradient source).

If a scene needs something missing (a knife, a house, a clock…), draw it from `arc` / `bez` / point lists right in
`scenes.py`. A recognizable 4–8-stroke silhouette is enough. Keep it in the same single-weight line style.

Colors: `INK` (lines and text), `RED` (the theme accent, whatever its hue), `GREY`, `LIGHT`, `BG`.

## 7. Sound names (`sfx=` / `cue`)

scribble, pop, heartbeat, whoosh, transition, thunder, rumble, crack, chime, tick, click, glass, crackle, fire,
shield, water, rain, buzz, squeeze, thud, tear, switch, typing, erase, powerdown, sand, steps, beeps, flatline.
Scene transitions get a whoosh automatically. New sounds can be added to `BANK`/`VOL` in `sfx.py` (numpy synthesis).

## 8. Visual vocabulary by genre

- **Relationships:** two figures and the distance between them (slide apart/together), hearts (beat, dim, crack, fly away),
  speech bubbles (crossed, growing, flipping), metaphors (sinking ship, storm and umbrella, fire and shield, door shutting, flatline).
- **Horror:** dark theme, slow draws (`dur` 1–2 s), long holds, sudden pops on the scare word (`thud`/`thunder`, shake), doors,
  windows, eyes in darkness, footprints, flickering candle, clock at 3:00, a figure appearing behind the subject at the twist.
  Use fewer elements per scene; emptiness is scary.
- **Comedy:** bright theme, fast pops (`ease_back`, `pop`/`click`), exaggerated motion (big bounces, shakes), callbacks to
  earlier drawings, an awkward-silence beat with only one tiny element and `tick`.
- **Motivation:** rising motion (things move up), sun and rays, a figure climbing steps (draw stairs from lines), battery charging (reverse of drain), uplifting chimes.
- **Mystery / facts:** maps, magnifier (circle + handle), question marks, arrows connecting clues, a reveal by `te` exits and a new big icon.

Each scene gets one main metaphor tied to that scene's key word, and nothing static: something enters, moves, or changes on almost every highlighted word.

## 9. Layout rules and QA checklist

- Canvas 1080×1920. Drawing zone y ≈ 450–1080. Captions sit at y ≈ 1210–1330 (keep drawings above ~1120). The label is at y = 200.
- People are ~170 px tall at s = 1 (feet at y); keep them ≥ 120 px from the canvas edges.
- Preview (`render.py … --preview`) and check every tile:
  - [ ] nothing overlaps captions or other drawings unintentionally
  - [ ] each scene's main visual is on screen by the mid frame
  - [ ] elements meant to leave actually left (`te`)
  - [ ] overlays are subtle (alpha ≤ 0.2)
  - [ ] the CTA scene ends on the Follow button
- After the full render, spot-check 4–5 word times for sync.
