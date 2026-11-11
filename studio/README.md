# Viral Studio

A website that turns an idea into finished faceless videos:

1. **Idea**: pick a genre (relationships, horror, comedy, kids story…), a language, a length, and optionally your own idea and tone.
2. **Script**: Claude writes a viral voice-over script with the hook → tension → story → twist → payoff → CTA formula, plus a caption, hashtags, a label and a YouTube title. You can edit it.
3. **Voice**: record it (ElevenLabs or your own voice) and upload the MP3 with the exact spoken text.
4. **Style**: pick one of 10 animation themes, each with live animated previews: Rose Paper, Midnight Ink, Crayon Kids, Neon Pulse, Chalkboard, Blueprint, Comic Pop, Noir Film, Sunset Calm and Mint Clean.
5. **Video**: you get back
   - a **Short** (1080×1920) for TikTok, Reels and Shorts,
   - a **Long** YouTube version (1920×1080) with lower-third captions, a Subscribe button, a 8 s end screen and a 1280×720 thumbnail,
   - **Clips**: the best 15–45 s moments, found automatically (hook, twists, questions, emotional beats, payoff),
   - `.srt` caption files for every format.

After a render, **"Same video, new vibe"** re-animates the same project in another theme in one click; the voice and timing are reused.
The site keeps players coming back with XP levels, a daily streak, a theme collection (x/10 collected), rarity tiers, a "Surprise me" dice roll and confetti.

## Run it

```bash
./studio/run.sh                 # http://127.0.0.1:8000
```

Needs Python 3.10+, `ffmpeg` on the PATH and the Python packages in `requirements.txt`.
Set `ANTHROPIC_API_KEY` to have Claude write scripts. Without it the app still works, but uses built-in sample scripts.
Rendered projects are stored in `studio/data/projects/` (override with `STUDIO_DATA`).

## How it works

| Piece | File | What it does |
|---|---|---|
| Script writer | `server/scriptgen.py` | Claude (`claude-opus-5-5`, structured JSON output, server-side refusal fallback) with the viral-script playbook; offline templates as a fallback. |
| Scene planner | `server/planner.py` | Splits any script into scenes and caption cards, picks highlight words, and maps meaning to visuals (phone, heart, night, door, storm, money, stairs, eyes in the dark…, 29 kinds) with layout templates (hero, duo, solo, list of three, big number, CTA). Negations get a red ✗, questions a "?". |
| Word timing | `server/timing.py` | English: offline forced alignment (pocketsphinx), about 0.01 s from hand-checked timings. Other languages: pauses in the audio are matched to the script's punctuation (median error about 0.1 s on a test recording). |
| Renderer | `server/render_one.py`, `server/vme/` | The hand-drawn motion-graphics engine (cairo + numpy + ffmpeg), now able to render both formats and themable (stroke weight, wobble, neon glow, paper, grid, chalk, halftone and star textures, caption font, pop and motion energy). Synthesized sound effects and a music bed matched to the theme, with loudness normalized to −14 LUFS. |
| Clips | `server/clips.py` | Scores scenes and cuts the best non-overlapping windows from the vertical video. |
| Jobs | `server/pipeline.py` | One render at a time in a background worker. Each format is rendered in its own process. |
| API + site | `server/app.py`, `web/` | FastAPI plus a framework-free single-page app. |

### API

- `GET /api/meta`: themes, genres, languages
- `POST /api/script` `{genre, language, seconds, topic, tone}` → script JSON
- `POST /api/projects` (multipart: `audio`, `script`, `theme`, `formats`, `clips`, `title`, `label`, …) → `{id}`
- `GET /api/projects/{id}` → status, progress, outputs per theme
- `POST /api/projects/{id}/rerender` `{theme, formats?, clips?}`

## Limits and next steps

- Render time is about 1–2 min per format for a 90 s video on one CPU core, and jobs run one at a time. For many users, run several workers (or a queue like Redis/RQ) on more cores.
- There are no user accounts yet: anyone with a project link can open its files. Add auth before putting it on the public internet.
- Arabic and other right-to-left or complex scripts: captions are drawn with cairo's simple text API, which doesn't shape Arabic letters. Rendering captions through Pango/HarfBuzz would fix this.
- Visuals are chosen from English keywords. Other languages still get people, numbers, questions, negations and a varied icon rotation, and a per-language keyword list would make them as rich as English.
