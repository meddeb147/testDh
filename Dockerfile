# Viral Studio: everything (ffmpeg, cairo, fonts, Python deps) in one image.
#   docker build -t viral-studio .
#   docker run -p 8000:8000 -e ANTHROPIC_API_KEY=... -v "$PWD/data:/app/data" viral-studio
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg libcairo2-dev pkg-config build-essential fonts-inter fonts-dejavu-core fonts-jetbrains-mono \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server ./server
COPY web ./web
COPY samples ./samples
ENV HOST=0.0.0.0 PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "python -m uvicorn app:app --app-dir server --host $HOST --port $PORT"]
