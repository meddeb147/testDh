---
name: viral-motion-video
description: "End-to-end workflow for faceless short-form videos (TikTok, Reels, Shorts) with hand-drawn motion graphics, word-by-word captions, sound effects and music, synced to a voice-over the user records (e.g. ElevenLabs). Covers 4 steps: research a viral topic in a genre the user names (romance, relationships, horror, comedy, motivation, mystery, facts…) and write the voice-over script; receive the user's voice-over MP3; build the synced motion-graphics video and ask for approval; revise until the user is happy. Use this whenever the user wants a viral/faceless/storytelling video, a voice-over script for a short video, wants to \"make the same video in English\", sends an MP3 voice-over to turn into a video, or asks to edit/fix one of these videos — even if they don't say \"motion graphics\"."
---

# Viral motion-graphics video

A 4-step loop between you and the user. You write, they voice, you animate, they approve.
Everything renders locally with Python (cairo + numpy + ffmpeg); no paid services, no downloads beyond pip.

```
1. Topic research + script   →  user records the voice-over (ElevenLabs etc.)
2. Receive voice-over MP3    →  transcribe, verify, align every word
3. Build the video           →  scenes + animation + SFX + music → send it, ask for approval
4. Revisions                 →  fix exactly what they ask, re-render, ask again… until "yes"
```

Bundled files (paths relative to this skill's folder):
- `scripts/engine.py`: drawing engine (60+ hand-drawn icons, effects, captions, themes, renderer)
- `scripts/align.py`: offline voice-over transcription check, wording scoring, word-level alignment
- `scripts/render.py`: one command: preview frames, or the full render + SFX + music + loudness + .srt
- `scripts/sfx.py`: 29 synthesized sound effects + 4 music moods, ducked under the voice
- `references/script-writing.md`: viral research method, script formula, genre playbook. **Read for step 1.**
- `references/scene-authoring.md`: how to write a scenes file, full API, visual vocabulary per genre, QA checklist. **Read for step 3.**
- `references/examples/*.py`: two real shipped videos' scene files. Skim one before writing your first scenes file.

## Setup (once per machine/session)

```bash
pip install pycairo numpy pocketsphinx   # ffmpeg must be installed; fonts: Inter (falls back to any sans)
```

Keep each project in its own folder (e.g. `<repo>/<video-slug>/`) holding: `SCRIPT.md`, `vo.mp3`, `scenes.py`,
`timings.json`, the final `.mp4` and `.srt`. Work files go in a scratch folder.

## Step 1: research and script

Goal: one topic with real viral pull in the user's genre, plus a voice-over script they can paste straight into ElevenLabs.

1. Run 2–4 web searches (trends in that genre on TikTok/Reels/Shorts, recurring high-share themes, and the
   research or facts behind the topic). Follow `references/script-writing.md`.
2. Pick **one** topic and say in 2–3 lines why it should travel (hook, emotion, share trigger). Offer 2–3 backup
   ideas in one line each.
3. Write the script with the formula in the reference: hook in the first 3 seconds, one idea per line, a payoff,
   an actionable or chilling or funny final beat, and a share/follow call to action. **No product/book plugs.**
4. Target **60–100 seconds** spoken (≈150–240 words at a calm narrator pace of about 2.3–2.6 words/sec).
   Say the estimated length.
5. Save it as `SCRIPT.md` (script + post caption + hashtags), commit if in a repo, and paste the script in chat.
6. Tell the user: *"Paste this exact text into ElevenLabs, and when you send the MP3, send the exact text
   you pasted too, so the captions match 100%."* Voices often get edited before recording, and having the
   exact text avoids guessing words from audio.

Cite your sources at the end of the message.

## Step 2: receive the voice-over

When the MP3 arrives (it may come without the text):

1. Copy it into the project folder as `vo.mp3`.
2. **Never assume the recording matches the script.** Run
   `python3 scripts/align.py check vo.mp3` → a rough transcript of every phrase between pauses. The model is
   small and noisy ("cement" = "a man"), but it reliably shows where lines were added, removed or reworded.
3. If the user sent the exact text, use it. Otherwise rebuild the spoken text phrase by phrase: start from the
   script, change it where the rough transcript disagrees, and settle unclear phrases with
   `python3 scripts/align.py score vo.mp3 12.10-14.20 "candidate one" "candidate two" …` (higher wins).
   Close scores are a coin flip: prefer the rough transcript's reading, then the original script.
   **Keep a list of the uncertain words** to show the user in step 3.
4. Split the final text into scenes (one visual idea per scene, ~4–9 s each) and caption cards in `scenes.py`
   (see the scene-authoring reference for the `|` and `*highlight*` syntax).
5. Run `python3 scripts/align.py align vo.mp3 scenes.py timings.json`. It prints each scene's time span
   and speaking rate. A `CHECK` flag, or a failure, means the text doesn't match the audio somewhere: fix it and rerun.

## Step 3: build the video and ask for approval

1. Read `references/scene-authoring.md` (and skim an example). Choose THEME + MOOD to match the genre's vibe.
2. Write `build(i, w, wf)` for every scene, giving each scene its own visual metaphor. Animate on the spoken words
   (`wf("word")`), attach a sound to every meaningful appearance, and add a closing CTA scene (share + follow
   button tap).
3. **Preview before the full render:** `python3 scripts/render.py scenes.py timings.json out.mp4 --preview`
   → `out_preview.png` (mid and end frame of every scene). Look at it. Fix overlaps, empty scenes,
   elements off-screen or covering captions. Repeat until clean. This takes seconds, while a full render takes 1–2 minutes.
4. Full render: `python3 scripts/render.py scenes.py timings.json <slug>.mp4 --vo vo.mp3`
   → final MP4 (−14 LUFS, AAC) + `.srt`.
5. Spot-check sync: grab 4–5 frames at known word times from `timings.json`
   (`ffmpeg -ss T -i out.mp4 -frames:v 1 x.png`). The word should be just appearing.
6. Deliver: send the MP4 (and .srt) with your file-sending tool, commit and push if in a repo, then **ask for
   approval** in a short message:
   - what's in it (scene-by-scene visual highlights, sound design)
   - the uncertain words from step 2 (ask them to check those captions)
   - honest notes: you can't hear the mix, only measure it (ask for one full listen); flag if length > ~100 s
   - end with: *"Do you approve it, or what should I change?"*

## Step 4: revisions until approved

- Treat every note literally and precisely: change what was asked, keep everything else identical.
- Map the note to the place in the code: caption text and highlights → `SCENES`; timing or a visual → that
  scene's `build` branch; volume or sounds → the `g=` gains or `sfx` names (or `VOL` in `sfx.py`); colors
  and mood → `THEME` / `MOOD`; length → split or trim scenes (a shorter cut needs a shorter voice-over, or
  cutting whole sentences from the audio with ffmpeg and re-aligning).
- If they send a new MP3, go back through step 2 (check → align).
- After each fix: preview → full render → send → ask again. Keep the same output filename unless they want versions.
- When they approve, commit the final files and stop changing them.

## Things that went wrong before (so they don't again)

- Recordings drift from the script (added lines, reworded hooks). Forced alignment can "succeed" with the
  wrong text and give garbage timings, so always run `check` first.
- Quote marks after a highlight (`*nowhere.*”`) used to leak the red highlight into the next card; the parser now
  handles it, but keep closing `*` right after the word's punctuation.
- Filled shapes popping in at scale 0 crash cairo (non-invertible matrix); the engine guards it, so reuse its
  `F()` / `ease_back` helpers instead of hand-rolled scaling.
- A dark overlay (e.g. a vignette for "alone") at full strength turns the frame grey. Keep overlay alpha ≤ 0.2.
- Long videos (> 2 min) lose viewers. Say so and offer a shorter cut.
