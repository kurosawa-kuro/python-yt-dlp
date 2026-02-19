# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YouTube Subtitle Extraction API — a minimal FastAPI microservice that accepts a YouTube URL and returns Japanese subtitles (manual preferred, auto-generated fallback) as text. The design spec is in `基礎設計.md`.

**Stack:** Python 3.11, FastAPI, Uvicorn, yt-dlp, ffmpeg, Docker

## Project Structure

```
app/
 ├── main.py              # FastAPI app with GET /subtitle endpoint + extract_subtitle()
 └── requirements.txt     # fastapi, uvicorn, yt-dlp
tests/
 ├── conftest.py          # TestClient fixture
 ├── test_subtitle_api.py # endpoint tests (success, 422, 404, 500)
 └── test_extract_subtitle.py  # extract_subtitle unit tests with yt-dlp mocked
Dockerfile                # python:3.11-slim, ffmpeg, uvicorn on port 10000
requirements-dev.txt      # includes test deps (pytest, httpx)
pytest.ini                # pythonpath=app, testpaths=tests
```

## Build and Run

```bash
docker build -t yt-api .
docker run -p 10000:10000 yt-api
```

Local development without Docker:

```bash
pip install -r requirements-dev.txt
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

## Tests

```bash
python3 -m pytest tests/ -v
```

Tests mock `yt_dlp.YoutubeDL` so no network access is needed.

## Architecture

Single endpoint: `GET /subtitle?url=<youtube_url>`

1. Receives YouTube URL as query parameter
2. Uses yt-dlp to download subtitles (Japanese, `lang="ja"`) into a temp directory
3. Prioritizes manual subtitles, falls back to auto-generated
4. Returns VTT subtitle text as JSON: `{"success": true, "subtitle": "..."}`

Production yt-dlp options to add: `nocheckcertificate`, `forceipv4`, `retries: 3`.

## Deployment

Target: Render.com (Docker deployment, port 10000). Known limitations on free tier:
- 15-min request timeout
- Cold starts
- YouTube may block datacenter IPs (mitigations: cookies.txt, VPS, residential proxy)
