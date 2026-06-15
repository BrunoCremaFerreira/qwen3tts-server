import numpy as np
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_synthesize(monkeypatch):
    """Replace src.model.synthesize with a stub that returns 1 second of silence."""

    def _synthesize(text, voice, speed, instructions):
        return (np.zeros(24000, dtype=np.float32), 24000)

    monkeypatch.setattr("src.model.synthesize", _synthesize)
    return _synthesize


@pytest.fixture
def client(mock_synthesize, monkeypatch):
    """
    TestClient for the FastAPI app with model loading disabled.
    The lifespan startup calls load_model; we replace it with a no-op so no
    GPU / HuggingFace download occurs during tests.
    """
    monkeypatch.setattr("src.model.load_model", lambda settings: None)

    from src.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def valid_request():
    """Minimal valid request body for POST /v1/audio/speech."""
    return {
        "model": "tts-1",
        "input": "Hello, world!",
        "voice": "alloy",
    }
