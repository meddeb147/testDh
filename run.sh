#!/usr/bin/env bash
# Start Viral Studio on http://127.0.0.1:${PORT:-8000}  (Mac / Linux)
set -e
cd "$(dirname "$0")"
if [ -f .env ]; then set -a; . ./.env; set +a; fi          # optional settings, see .env.example
command -v ffmpeg >/dev/null || { echo "ffmpeg is not installed. See README.md -> Install."; exit 1; }
python3 -m pip install -q -r requirements.txt
echo "Viral Studio -> http://${HOST:-127.0.0.1}:${PORT:-8000}"
exec python3 -m uvicorn app:app --app-dir server --host "${HOST:-127.0.0.1}" --port "${PORT:-8000}"
