#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv"
DEV_MODE=0

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dev         Install dev dependencies (tests)"
    echo "  --device DEVICE  Device to use: cpu, cuda, mps (default: auto-detect)"
    echo "  --port PORT   Port to listen on (default: 8000)"
    echo "  --model PATH  Model name or HuggingFace path"
    echo "  --reset       Delete venv and reinstall from scratch"
    echo "  -h, --help    Show this help"
}

DEVICE=""
PORT=""
MODEL=""
RESET=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dev)     DEV_MODE=1; shift ;;
        --device)  DEVICE="$2"; shift 2 ;;
        --port)    PORT="$2"; shift 2 ;;
        --model)   MODEL="$2"; shift 2 ;;
        --reset)   RESET=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

if [[ $RESET -eq 1 && -d "$VENV_DIR" ]]; then
    echo "==> Removing existing venv..."
    rm -rf "$VENV_DIR"
fi

if [[ ! -d "$VENV_DIR" ]]; then
    echo "==> Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "==> Installing dependencies..."
pip install --quiet --upgrade pip

if [[ $DEV_MODE -eq 1 ]]; then
    pip install --quiet -r requirements-dev.txt
else
    pip install --quiet -r requirements.txt
fi

echo "==> Starting server..."

UVICORN_ARGS="src.main:app --reload"

[[ -n "$PORT" ]]   && export PORT
[[ -n "$DEVICE" ]] && export DEVICE
[[ -n "$MODEL" ]]  && export MODEL_NAME_OR_PATH="$MODEL"

exec uvicorn $UVICORN_ARGS \
    --host "${HOST:-0.0.0.0}" \
    --port "${PORT:-8000}" \
    --log-level "${LOG_LEVEL:-info}"
