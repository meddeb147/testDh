"""Animation themes for Studio. Each theme = palette + drawing style + caption style + motion energy + music mood.

Palette entries are RGB 0-1 triples: bg, ink (lines/text), accent, grey (labels), light (disabled shapes).
`css` is used by the web app for the live animated previews, so the picker looks like the real render."""

def _hex(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def T(id, name, tagline, vibe, bg, ink, accent, grey, light, mood, style, tags, rarity="common"):
    return dict(id=id, name=name, tagline=tagline, vibe=vibe, mood=mood, tags=tags, rarity=rarity,
                palette=dict(bg=_hex(bg), ink=_hex(ink), accent=_hex(accent), grey=_hex(grey), light=_hex(light)),
                css=dict(bg=bg, ink=ink, accent=accent, grey=grey, light=light), style=style)


THEMES = [
    T("rose-paper", "Rose Paper", "Soft ink on warm paper. Made for heartbreak.", "emotional",
      "#efe9e5", "#1c1717", "#8c0d1a", "#8c8580", "#c7bfba", "tender",
      dict(stroke=1.0, wobble=1.1, texture="paper", cap_font="Inter SemiBold", cap_pop=0.18, punch=0.035),
      ["romance", "relationships"]),
    T("midnight-ink", "Midnight Ink", "Pitch-black, slow, and one red thing watching.", "serious",
      "#111113", "#dbd8d1", "#c70f14", "#73737a", "#4d4d52", "dark",
      dict(stroke=1.0, wobble=1.3, texture="grain", cap_font="Inter SemiBold", cap_pop=0.12, punch=0.045, drift=0.6),
      ["horror", "mystery"]),
    T("crayon-kids", "Crayon Kids", "Fat wobbly crayons, bouncy words, pure joy.", "childish",
      "#fff6d8", "#2b2350", "#ff5a5f", "#8a7fb5", "#d9cfee", "playful",
      dict(stroke=1.9, wobble=3.2, texture="paper", cap_font="Inter Black", cap_upper=True, cap_pop=0.34, punch=0.07,
           drift=1.8, plate=True),
      ["kids", "comedy", "story"], "rare"),
    T("neon-pulse", "Neon Pulse", "Glowing tubes on a night street. Hits like a bass drop.", "energetic",
      "#0b0820", "#7df9ff", "#ff2fd6", "#7b74b8", "#3a3566", "uplifting",
      dict(stroke=1.1, wobble=0.6, glow=1.0, texture="stars", cap_font="Inter ExtraBold", cap_upper=True, cap_pop=0.26,
           punch=0.06, drift=1.3),
      ["motivation", "facts", "gaming"], "epic"),
    T("chalkboard", "Chalkboard", "Dusty chalk lessons that actually stick.", "smart",
      "#1f3a2e", "#eef0e6", "#ffd166", "#9fb5a6", "#4f6d5d", "uplifting",
      dict(stroke=1.3, wobble=1.8, texture="chalk", cap_font="Inter Bold", cap_pop=0.16, punch=0.03),
      ["facts", "psychology", "history"]),
    T("blueprint", "Blueprint", "Engineer's grid. Every idea drawn to scale.", "serious",
      "#0e3a6b", "#e8f1ff", "#ffcf3f", "#8fb0d8", "#3f6797", "dark",
      dict(stroke=0.9, wobble=0.4, texture="grid", cap_font="JetBrains Mono SemiBold", cap_upper=True, cap_pop=0.1,
           punch=0.025, label_font="JetBrains Mono SemiBold"),
      ["mystery", "facts", "tech"]),
    T("comic-pop", "Comic Pop", "Halftone dots, thick ink, BAM on every punchline.", "funny",
      "#ffe14d", "#111111", "#e5202e", "#6b5d1a", "#d8bf3a", "playful",
      dict(stroke=1.6, wobble=1.4, texture="halftone", cap_font="Inter Black", cap_upper=True, cap_pop=0.3, punch=0.08,
           drift=1.5, plate=True),
      ["comedy", "kids", "facts"], "rare"),
    T("noir-film", "Noir Film", "Black-and-white grain, one drop of red. Very cinema.", "serious",
      "#1a1a1a", "#e9e6df", "#d6312b", "#8a8780", "#55524d", "dark",
      dict(stroke=0.9, wobble=0.7, texture="chalk", cap_font="DejaVu Serif Bold", cap_pop=0.1, punch=0.03, drift=0.5,
           label_font="DejaVu Serif"),
      ["mystery", "horror", "true crime"], "epic"),
    T("sunset-calm", "Sunset Calm", "Warm gold light for comebacks and fresh starts.", "uplifting",
      "#fdf0e3", "#2d1b14", "#e36414", "#a07a63", "#e7cbb3", "uplifting",
      dict(stroke=1.1, wobble=1.0, texture="paper", cap_font="Inter ExtraBold", cap_pop=0.2, punch=0.04),
      ["motivation", "self-growth"]),
    T("mint-clean", "Mint Clean", "Crisp, modern, explainer-video clean.", "clean",
      "#f2fbf8", "#0f2a2a", "#10a37f", "#6e8f88", "#bfe0d6", "uplifting",
      dict(stroke=0.9, wobble=0.5, texture="grain", cap_font="Inter SemiBold", cap_pop=0.14, punch=0.03, plate=True),
      ["facts", "business", "tech"]),
]
BY_ID = {t["id"]: t for t in THEMES}

GENRE_DEFAULT = {"romance": "rose-paper", "relationships": "rose-paper", "horror": "midnight-ink",
                 "mystery": "noir-film", "comedy": "comic-pop", "kids story": "crayon-kids", "motivation": "sunset-calm",
                 "facts": "chalkboard", "psychology": "chalkboard", "true crime": "noir-film", "tech": "blueprint"}


def public():
    return [{k: t[k] for k in ("id", "name", "tagline", "vibe", "mood", "tags", "rarity", "css")} | {"style": t["style"]}
            for t in THEMES]
