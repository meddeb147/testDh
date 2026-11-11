@echo off
REM Start Viral Studio on http://127.0.0.1:8000 (Windows)
cd /d "%~dp0"
python -m pip install -q -r requirements.txt
python -m uvicorn app:app --app-dir server --host 127.0.0.1 --port 8000
