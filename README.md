# qwen3tts-server

OpenAI-compatible API server for [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS), enabling local text-to-speech generation via a `/v1/audio/speech` endpoint. Built with FastAPI and packaged in Docker, it integrates with any OpenAI-compatible client without code changes.

## Requirements

- **CPU**: supported (slower inference)
- **GPU**: NVIDIA RTX with CUDA 12.4+ (recommended)

## Quick start

### GPU (recommended)

```bash
# Download model weights once
pip install huggingface_hub
huggingface-cli download Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice --local-dir ./models/Qwen3-TTS-12Hz-1.7B-CustomVoice

# Start the server
docker compose up
```

### CPU

```bash
docker build -f Dockerfile.cpu -t qwen3tts-server:cpu .
docker run -p 8000:8000 \
  -v ./models:/models \
  -e MODEL_NAME_OR_PATH=/models/Qwen3-TTS-12Hz-1.7B-CustomVoice \
  -e DEVICE=cpu \
  qwen3tts-server:cpu
```

## API

### `POST /v1/audio/speech`

Compatible with the [OpenAI TTS API](https://platform.openai.com/docs/api-reference/audio/createSpeech).

**Request body**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `model` | string | yes | — | Accepted but ignored (fixed to Qwen3-TTS) |
| `input` | string | yes | — | Text to synthesize (1–4096 characters) |
| `voice` | string | yes | — | One of `alloy`, `echo`, `fable`, `nova`, `onyx`, `shimmer` |
| `response_format` | string | no | `wav` | One of `wav`, `mp3`, `opus`, `flac`, `pcm` |
| `speed` | float | no | `1.0` | Accepted for compatibility; not applied by the model |
| `instructions` | string | no | `null` | Style or tone instruction (e.g. `"speak slowly and clearly"`) |

**Example**

```bash
curl http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "Hello!", "voice": "alloy"}' \
  --output speech.wav
```

**Voice mapping**

| OpenAI voice | Qwen3-TTS speaker |
|---|---|
| `alloy` | Chelsie |
| `echo` | Ethan |
| `fable` | Cove |
| `nova` | Sora |
| `onyx` | Luca |
| `shimmer` | Aoede |

## Configuration

All settings are read from environment variables.

| Variable | Default | Description |
|---|---|---|
| `MODEL_NAME_OR_PATH` | `Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice` | HuggingFace repo or local path |
| `DEVICE` | auto-detect | `cpu`, `cuda:0`, `cuda:1`, etc. |
| `PORT` | `8000` | Listening port |
| `HOST` | `0.0.0.0` | Bind address |
| `WORKERS` | `1` | Uvicorn workers (keep at 1 for GPU) |
| `LOG_LEVEL` | `info` | Uvicorn log level |
| `HF_HOME` | — | HuggingFace cache directory |

## Development

`run.sh` creates a virtual environment, installs dependencies, and starts the server with hot-reload — no manual setup needed.

```bash
# Basic usage (creates .venv, installs deps, starts server)
./run.sh

# Include dev dependencies (pytest, httpx)
./run.sh --dev

# Force CPU, custom port, specific model
./run.sh --device cpu --port 8080 --model /models/Qwen3-TTS-12Hz-1.7B-CustomVoice

# Rebuild venv from scratch
./run.sh --reset --dev
```

**Options**

| Flag | Description |
|---|---|
| `--dev` | Install `requirements-dev.txt` (adds pytest, httpx) |
| `--device DEVICE` | Device override: `cpu`, `cuda`, `mps` |
| `--port PORT` | Port to listen on (default: `8000`) |
| `--model PATH` | Model name or local path |
| `--reset` | Delete `.venv` and reinstall from scratch |

**Running tests**

```bash
# Unit tests (no GPU or model required)
./run.sh --dev  # first run to set up venv
.venv/bin/pytest

# Integration tests (requires model downloaded)
.venv/bin/pytest -m integration
```

## Project structure

```
src/
├── main.py      # FastAPI app and startup lifespan
├── config.py    # Environment-based settings
├── model.py     # Model loading and inference
├── audio.py     # Audio encoding (WAV/MP3/OPUS/FLAC/PCM)
├── router.py    # POST /v1/audio/speech endpoint
└── tests/
```
