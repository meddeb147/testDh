"""Render one format of a project in its own process (the engine keeps frame size and style in module globals).

  python3 render_one.py PROJECT_DIR short|long THEME_ID [--preview]

Writes PROJECT_DIR/out/THEME_ID/{short,long}.mp4 + .srt (+ cover.jpg / thumbnail.jpg) and progress to
PROJECT_DIR/progress_<fmt>.json."""
import json, os, sys, subprocess, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "vme"))
import engine, sfx, planner, themes
import cairo

END_LEN = 8.0      # long-form end screen
TAIL = 1.8


def srt(P, path):
    def ts(s): h, r = divmod(s, 3600); m, sec = divmod(r, 60); return f"{int(h):02d}:{int(m):02d}:{int(sec):02d},{int(round((sec % 1) * 1000)) % 1000:03d}"
    out, n = [], 1
    for p in P:
        idx = 0
        for c in p["cards"]:
            a = p["abs_t"][idx]; idx += len(c)
            b = p["abs_t"][idx] - 0.05 if idx < len(p["abs_t"]) else p["end"] - 0.05
            out.append(f"{n}\n{ts(a)} --> {ts(b)}\n{' '.join(w for w, _ in c)}\n"); n += 1
    open(path, "w").write("\n".join(out))


def wrap(ctx, text, size, maxw):
    ctx.set_font_size(size); lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if cur and ctx.text_extents(t).x_advance > maxw: lines.append(cur); cur = w
        else: cur = t
    return lines + [cur]


def thumbnail(frame_png, title, out_jpg, theme):
    """1280x720: big title on the left, the most visual frame on the right."""
    pal = theme["palette"]; src = cairo.ImageSurface.create_from_png(frame_png)
    S = cairo.ImageSurface(cairo.FORMAT_RGB24, 1280, 720); c = cairo.Context(S)
    c.set_source_rgb(*pal["bg"]); c.paint()
    sw, sh = src.get_width(), src.get_height(); k = 720 / sh * 1.05
    c.save(); c.translate(1280 - sw * k * 0.62, -20); c.scale(k, k); c.set_source_surface(src, -sw * 0.18, 0); c.paint(); c.restore()
    g = cairo.LinearGradient(560, 0, 760, 0); g.add_color_stop_rgba(0, *pal["bg"], 1); g.add_color_stop_rgba(1, *pal["bg"], 0)
    c.set_source(g); c.rectangle(0, 0, 760, 720); c.fill()
    engine.set_font(c, "Inter Black"); words = title.upper()
    size = 96
    while True:
        lines = wrap(c, words, size, 620)
        if len(lines) <= 4 or size <= 56: break
        size -= 8
    y = 360 - (len(lines) - 1) * size * 0.55 + size * 0.35
    for j, ln in enumerate(lines):
        c.set_font_size(size); c.move_to(60, y + j * size * 1.08)
        c.set_source_rgb(*(pal["accent"] if j == len(lines) - 1 else pal["ink"])); c.show_text(ln)
    c.set_source_rgb(*pal["accent"]); c.rectangle(64, y + (len(lines) - 1) * size * 1.08 + 34, 260, 12); c.fill()
    tmp = out_jpg + ".png"; S.write_to_png(tmp)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-q:v", "2", out_jpg], check=True); os.remove(tmp)


def main():
    pdir, fmt, theme_id = sys.argv[1:4]; preview = "--preview" in sys.argv
    proj = json.load(open(os.path.join(pdir, "project.json")))
    plan = json.load(open(os.path.join(pdir, "plan.json")))
    tm = json.load(open(os.path.join(pdir, "timings.json")))
    theme = themes.BY_ID[theme_id]
    engine.set_theme(theme["palette"]); engine.configure(fmt, theme["style"])
    scenes = [planner.caption_text(sc) for sc in plan]
    vo_end = tm["audio_duration"]
    total = vo_end + TAIL + (END_LEN if fmt == "long" else 0)
    if fmt == "long":
        engine.END_AT = vo_end + TAIL; engine.END_TITLE = proj.get("end_title") or "Thanks for watching."
    else:
        engine.END_AT = 1e9
    build = planner.make_build(plan, slow=theme["mood"] == "dark",
                               cta_label=("Subscribe", "Subscribed") if fmt == "long" else ("Follow", "Following"))
    out = os.path.join(pdir, "out", theme_id); os.makedirs(out, exist_ok=True)
    label = proj.get("label", "")
    prog_path = os.path.join(pdir, f"progress_{fmt}.json")

    def progress(f):
        json.dump(dict(fmt=fmt, theme=theme_id, progress=round(0.9 * f, 3)), open(prog_path, "w"))

    if preview:   # one frame per scene, used by the theme picker "see it on my video" button
        P = engine.plan(scenes, tm["scenes"], total)
        frames = [int(engine.FPS * (p["start"] + p["dur"] * 0.6)) for p in P]
        engine.render(os.path.join(out, f"prev_{fmt}"), scenes, tm["scenes"], build, total, label, preview=frames)
        return
    silent, ev, wav = (os.path.join(out, f"{fmt}{x}") for x in ("_silent.mp4", "_events.json", "_mix.wav"))
    P = engine.render(silent, scenes, tm["scenes"], build, total, label, events_out=ev, progress=progress)
    progress(1.0)
    sfx.main(os.path.join(pdir, "vo.mp3"), ev, total, wav, theme["mood"])
    final = os.path.join(out, f"{fmt}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                    "-movflags", "+faststart", final], check=True)
    srt(P, os.path.join(out, f"{fmt}.srt"))
    for f in (silent, wav, ev): os.remove(f)
    # cover / thumbnail from the scene with the most visual beats
    best = max(P, key=lambda p: len(plan[p["i"]]["beats"]) + (2 if p["i"] == 0 else 0) - (9 if plan[p["i"]]["cta"] else 0))
    fr = os.path.join(out, f"{fmt}_frame.png")
    crop = ["-vf", "crop=iw:ih*0.80:0:0"] if fmt == "long" else []      # keep the captions out of the thumbnail
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{best['start'] + best['dur'] * 0.7:.2f}", "-i", final, "-frames:v", "1", *crop, fr], check=True)
    if fmt == "long":
        thumbnail(fr, proj.get("youtube_title") or proj.get("title") or label, os.path.join(out, "thumbnail.jpg"), theme)
    else:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", fr, "-vf", "scale=540:-1", "-q:v", "3", os.path.join(out, "cover.jpg")], check=True)
    os.remove(fr)
    json.dump(dict(fmt=fmt, theme=theme_id, progress=1.0, done=True), open(prog_path, "w"))


if __name__ == "__main__":
    main()
