"""Viral Studio web server.  Run from the repo root:  ./run.sh   (or: python -m uvicorn app:app --app-dir server --port 8000)"""
import os, sys, json, uuid, shutil, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pipeline, themes, scriptgen, planner

WEB = os.path.join(os.path.dirname(HERE), "web")
app = FastAPI(title="Viral Studio")
pipeline.start_worker()

MAX_AUDIO_MB = 40
MAX_AUDIO_SEC = 300


@app.get("/")
def index(): return FileResponse(os.path.join(WEB, "index.html"))


@app.get("/api/meta")
def meta():
    return dict(themes=themes.public(), genres=scriptgen.GENRES, languages=scriptgen.LANGUAGES,
                genre_theme=themes.GENRE_DEFAULT, claude=bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")))


class ScriptReq(BaseModel):
    genre: str
    language: str = "English"
    seconds: int = 75
    topic: str = ""
    tone: str = ""


@app.post("/api/script")
def script(req: ScriptReq):
    try:
        out = scriptgen.write_script(req.genre, req.language, max(30, min(180, req.seconds)), req.topic[:400], req.tone[:100])
    except RuntimeError as e:
        raise HTTPException(422, str(e))
    out["words"] = len(out["script"].split())
    out["est_seconds"] = round(out["words"] / (2.5 if req.language == "English" else 2.3))
    out["scenes_preview"] = [planner.caption_text(sc) for sc in planner.make_plan(out["script"], req.genre)]
    return out


@app.post("/api/projects")
async def create(audio: UploadFile = File(...), script: str = Form(...), genre: str = Form(""), language: str = Form("English"),
                 theme: str = Form("rose-paper"), formats: str = Form("short,long"), clips: int = Form(3),
                 label: str = Form(""), title: str = Form(""), youtube_title: str = Form("")):
    if theme not in themes.BY_ID: raise HTTPException(400, "Unknown theme")
    if len(script.split()) < 8: raise HTTPException(400, "The script is too short.")
    pid = uuid.uuid4().hex[:12]; d = pipeline.pdir(pid); os.makedirs(d)
    raw = os.path.join(d, "upload" + os.path.splitext(audio.filename or "")[1].lower()[:6])
    size = 0
    with open(raw, "wb") as f:
        while chunk := await audio.read(1 << 20):
            size += len(chunk)
            if size > MAX_AUDIO_MB << 20: shutil.rmtree(d); raise HTTPException(413, f"Audio is larger than {MAX_AUDIO_MB} MB.")
            f.write(chunk)
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-t", str(MAX_AUDIO_SEC), "-ac", "1", "-ar", "44100",
                        "-b:a", "160k", os.path.join(d, "vo.mp3")], capture_output=True, text=True)
    os.remove(raw)
    if r.returncode: shutil.rmtree(d); raise HTTPException(400, "That file doesn't look like audio we can read (MP3, WAV, M4A…).")
    fm = [x for x in formats.split(",") if x in ("short", "long")] or ["short"]
    proj = dict(id=pid, created=time.time(), script=script.strip(), genre=genre, language=language, theme=theme,
                formats=fm, clips=max(0, min(5, clips)), label=(label or title or "").upper()[:40], title=title,
                youtube_title=youtube_title or title)
    pipeline.save(pid, proj)
    pipeline.enqueue(pid)
    return dict(id=pid)


@app.get("/api/projects/{pid}")
def get(pid: str):
    if not pid.isalnum() or not os.path.isdir(pipeline.pdir(pid)): raise HTTPException(404)
    proj = pipeline.load(pid); st = pipeline.status(pid)
    renders = {t: pipeline.outputs(pid, t) for t in os.listdir(os.path.join(pipeline.pdir(pid), "out"))} \
        if os.path.isdir(os.path.join(pipeline.pdir(pid), "out")) else {}
    return dict(project={k: proj[k] for k in ("id", "theme", "formats", "clips", "label", "language", "genre")} |
                {"timing_method": proj.get("timing_method")}, status=st, renders=renders)


class Rerender(BaseModel):
    theme: str
    formats: list[str] | None = None
    clips: int | None = None


@app.post("/api/projects/{pid}/rerender")
def rerender(pid: str, req: Rerender):
    if not pid.isalnum() or not os.path.isdir(pipeline.pdir(pid)): raise HTTPException(404)
    if req.theme not in themes.BY_ID: raise HTTPException(400, "Unknown theme")
    proj = pipeline.load(pid); proj["theme"] = req.theme
    if req.formats: proj["formats"] = [x for x in req.formats if x in ("short", "long")] or proj["formats"]
    if req.clips is not None: proj["clips"] = max(0, min(5, req.clips))
    pipeline.save(pid, proj); pipeline.enqueue(pid, rerender=True)
    return dict(ok=True)


app.mount("/media", StaticFiles(directory=pipeline.DATA), name="media")
app.mount("/static", StaticFiles(directory=WEB), name="static")
