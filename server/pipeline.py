"""Project jobs: timing -> planning -> renders (one process per format) -> clips. One render at a time (CPU bound)."""
import json, os, sys, subprocess, threading, queue, time, traceback, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import planner, timing, clips, themes

DATA = os.environ.get("STUDIO_DATA", os.path.join(os.path.dirname(HERE), "data", "projects"))
os.makedirs(DATA, exist_ok=True)
Q = queue.Queue()


def pdir(pid): return os.path.join(DATA, pid)


def load(pid, name="project.json"):
    with open(os.path.join(pdir(pid), name)) as f: return json.load(f)


def save(pid, obj, name="project.json"):
    tmp = os.path.join(pdir(pid), name + ".tmp")
    with open(tmp, "w") as f: json.dump(obj, f, indent=1)
    os.replace(tmp, os.path.join(pdir(pid), name))


def set_status(pid, **kw):
    p = os.path.join(pdir(pid), "status.json")
    st = json.load(open(p)) if os.path.exists(p) else {}
    st.update(kw, updated=time.time()); save(pid, st, "status.json")


def status(pid):
    st = load(pid, "status.json")
    for fmt in ("short", "long"):
        pp = os.path.join(pdir(pid), f"progress_{fmt}.json")
        if os.path.exists(pp) and st.get("stage") == f"render_{fmt}":
            try: st["progress"] = json.load(open(pp)).get("progress", 0)
            except ValueError: pass
    return st


def outputs(pid, theme):
    out = os.path.join(pdir(pid), "out", theme); base = f"/media/{pid}/out/{theme}/"
    if not os.path.isdir(out): return {}
    files = set(os.listdir(out)); res = {}
    for k in ("short.mp4", "short.srt", "cover.jpg", "long.mp4", "long.srt", "thumbnail.jpg"):
        if k in files: res[k.replace(".", "_")] = base + k
    cl = os.path.join(out, "clips.json")
    if os.path.exists(cl):
        res["clips"] = [dict(c, url=base + f"clip_{k}.mp4") for k, c in enumerate(json.load(open(cl)), 1)
                        if f"clip_{k}.mp4" in files]
    return res


def run(pid, rerender=False):
    proj = load(pid); theme = proj["theme"]; fmts = proj["formats"]
    try:
        if not rerender or not os.path.exists(os.path.join(pdir(pid), "timings.json")):
            set_status(pid, stage="plan", progress=0.05, message="Splitting your script into scenes")
            plan = planner.make_plan(proj["script"], proj.get("genre", ""))
            save(pid, plan, "plan.json")
            set_status(pid, stage="timing", progress=0.1, message="Listening to your voice and timing every word")
            tm = timing.scene_timings(os.path.join(pdir(pid), "vo.mp3"), plan, proj.get("language", "English"))
            save(pid, tm, "timings.json")
            proj["timing_method"] = tm["method"]; save(pid, proj)
        need_short = "short" in fmts or proj.get("clips", 0) > 0
        order = (["short"] if need_short else []) + (["long"] if "long" in fmts else [])
        for fmt in order:
            pp = os.path.join(pdir(pid), f"progress_{fmt}.json")
            if os.path.exists(pp): os.remove(pp)          # don't show the previous render's 100%
            set_status(pid, stage=f"render_{fmt}", progress=0.0,
                       message="Animating the vertical video (9:16)" if fmt == "short" else "Animating the YouTube version (16:9)")
            r = subprocess.run([sys.executable, os.path.join(HERE, "render_one.py"), pdir(pid), fmt, theme],
                               capture_output=True, text=True)
            if r.returncode: raise RuntimeError(f"{fmt} render failed:\n{r.stderr[-2000:]}")
        if proj.get("clips", 0) > 0:
            set_status(pid, stage="clips", progress=0.5, message="Finding the best moments for clips")
            plan = load(pid, "plan.json"); tm = load(pid, "timings.json")
            cs = clips.pick(plan, tm, proj["clips"])
            out = os.path.join(pdir(pid), "out", theme)
            clips.cut(os.path.join(out, "short.mp4"), cs, out, themes.BY_ID[theme]["css"]["bg"])
            json.dump(cs, open(os.path.join(out, "clips.json"), "w"))
        set_status(pid, stage="done", progress=1.0, message="Ready", outputs=outputs(pid, theme), error=None)
    except Exception as e:  # noqa: BLE001 - report any failure to the UI
        traceback.print_exc()
        set_status(pid, stage="error", message=str(e)[:1500], error=True)


def worker():
    while True:
        pid, rr = Q.get()
        try: run(pid, rr)
        finally: Q.task_done()


def start_worker():
    threading.Thread(target=worker, daemon=True).start()


def enqueue(pid, rerender=False):
    set_status(pid, stage="queued", progress=0.0, message=f"In line ({Q.qsize()} ahead)", outputs={})
    Q.put((pid, rerender))
