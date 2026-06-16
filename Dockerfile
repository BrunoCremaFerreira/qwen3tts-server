FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 \
        python3-pip \
        libsndfile1 \
        sox \
    && rm -rf /var/lib/apt/lists/*

# Install torch with CUDA 12.4 support first so the index-url is applied only
# to torch — remaining deps use the default PyPI index.
RUN python3.11 -m pip install --no-cache-dir torch \
        --index-url https://download.pytorch.org/whl/cu124

WORKDIR /app

COPY requirements.txt .
RUN python3.11 -m pip install --no-cache-dir numpy
RUN python3.11 -m pip install --no-cache-dir \
        --constraint /dev/null \
        $(grep -v '^torch\|^numpy' requirements.txt | tr '\n' ' ')

COPY src/ src/

EXPOSE 8000

ENV MODEL_NAME_OR_PATH=Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice

CMD ["python3.11", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
