#!/usr/bin/env bash
# Start Viral Studio on http://localhost:${PORT:-8000}
set -e
cd "$(dirname "$0")"
python3 -m pip install -q -r requirements.txt
exec python3 -m uvicorn app:app --app-dir server --host "${HOST:-127.0.0.1}" --port "${PORT:-8000}"
