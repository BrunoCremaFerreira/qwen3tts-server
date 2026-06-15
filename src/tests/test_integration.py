"""
Integration test — loads the real Qwen3-TTS model on CPU.

Marked with @pytest.mark.integration so it is excluded from the normal test
run and only executed explicitly:

    pytest -m integration

This test does NOT use the mock fixtures from conftest.py.
It requires the model weights to be available (via HF_HOME or internet access)
and will be slow (~minutes on first run due to download).
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_real_model_cpu_returns_valid_wav():
    """
    Load the model on CPU, synthesise a short English phrase and verify that
    the response is a valid WAV file (non-empty body, RIFF header) with
    positive duration.
    """
    import os

    os.environ.setdefault("DEVICE", "cpu")

    from src.main import app

    with TestClient(app) as client:
        response = client.post(
            "/v1/audio/speech",
            json={
                "model": "tts-1",
                "input": "Hello.",
                "voice": "alloy",
            },
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"

    body = response.content
    assert len(body) > 0
    assert body[:4] == b"RIFF", "Response body is not a valid WAV file"

    # WAV data chunk size is at bytes 4-8 (little-endian uint32).
    # A non-trivial file will always be larger than the 44-byte header.
    assert len(body) > 44, "WAV body too short to contain audio data"
