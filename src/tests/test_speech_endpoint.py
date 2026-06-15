"""
Integration tests for POST /v1/audio/speech.

All tests in this file use the `client` and `mock_synthesize` fixtures defined
in conftest.py, so no real GPU or model download ever occurs.
"""

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ENDPOINT = "/v1/audio/speech"

VOICE_TO_SPEAKER = {
    "alloy": "Chelsie",
    "echo": "Ethan",
    "fable": "Cove",
    "nova": "Sora",
    "onyx": "Luca",
    "shimmer": "Aoede",
}


# ---------------------------------------------------------------------------
# 422 — schema validation errors
# ---------------------------------------------------------------------------


def test_empty_input_returns_422(client, valid_request):
    valid_request["input"] = ""
    response = client.post(ENDPOINT, json=valid_request)
    assert response.status_code == 422


def test_input_too_long_returns_422(client, valid_request):
    valid_request["input"] = "x" * 4097
    response = client.post(ENDPOINT, json=valid_request)
    assert response.status_code == 422


def test_invalid_voice_returns_422(client, valid_request):
    valid_request["voice"] = "invalid_voice"
    response = client.post(ENDPOINT, json=valid_request)
    assert response.status_code == 422


def test_invalid_response_format_returns_422(client, valid_request):
    valid_request["response_format"] = "ogg"
    response = client.post(ENDPOINT, json=valid_request)
    assert response.status_code == 422


def test_speed_below_minimum_returns_422(client, valid_request):
    valid_request["speed"] = 0.1
    response = client.post(ENDPOINT, json=valid_request)
    assert response.status_code == 422


def test_speed_above_maximum_returns_422(client, valid_request):
    valid_request["speed"] = 5.0
    response = client.post(ENDPOINT, json=valid_request)
    assert response.status_code == 422


def test_missing_model_returns_422(client):
    response = client.post(ENDPOINT, json={"input": "Hello", "voice": "alloy"})
    assert response.status_code == 422


def test_missing_input_returns_422(client):
    response = client.post(ENDPOINT, json={"model": "tts-1", "voice": "alloy"})
    assert response.status_code == 422


def test_missing_voice_returns_422(client):
    response = client.post(ENDPOINT, json={"model": "tts-1", "input": "Hello"})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# 200 — happy path: status, Content-Type, body
# ---------------------------------------------------------------------------


def test_valid_minimal_request_returns_200_wav(client, valid_request):
    response = client.post(ENDPOINT, json=valid_request)
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert len(response.content) > 0


def test_response_format_mp3_returns_audio_mpeg(client, valid_request):
    valid_request["response_format"] = "mp3"
    response = client.post(ENDPOINT, json=valid_request)
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"


def test_response_format_opus_returns_audio_opus(client, valid_request):
    valid_request["response_format"] = "opus"
    response = client.post(ENDPOINT, json=valid_request)
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/opus"


def test_response_format_flac_returns_audio_flac(client, valid_request):
    valid_request["response_format"] = "flac"
    response = client.post(ENDPOINT, json=valid_request)
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/flac"


def test_response_format_pcm_returns_audio_pcm(client, valid_request):
    valid_request["response_format"] = "pcm"
    response = client.post(ENDPOINT, json=valid_request)
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/pcm"


def test_speed_minimum_boundary_returns_200(client, valid_request):
    valid_request["speed"] = 0.25
    response = client.post(ENDPOINT, json=valid_request)
    assert response.status_code == 200


def test_speed_maximum_boundary_returns_200(client, valid_request):
    valid_request["speed"] = 4.0
    response = client.post(ENDPOINT, json=valid_request)
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# 200 — synthesize receives correct arguments
# ---------------------------------------------------------------------------


def test_instructions_forwarded_to_synthesize(client, valid_request, monkeypatch):
    received = {}

    def capturing_synthesize(text, voice, speed, instructions):
        received["instructions"] = instructions
        return (np.zeros(24000, dtype=np.float32), 24000)

    monkeypatch.setattr("src.model.synthesize", capturing_synthesize)

    valid_request["instructions"] = "Speak slowly and clearly."
    client.post(ENDPOINT, json=valid_request)

    assert received.get("instructions") == "Speak slowly and clearly."


def test_speed_forwarded_to_synthesize(client, valid_request, monkeypatch):
    received = {}

    def capturing_synthesize(text, voice, speed, instructions):
        received["speed"] = speed
        return (np.zeros(24000, dtype=np.float32), 24000)

    monkeypatch.setattr("src.model.synthesize", capturing_synthesize)

    valid_request["speed"] = 1.5
    client.post(ENDPOINT, json=valid_request)

    assert received.get("speed") == pytest.approx(1.5)


# ---------------------------------------------------------------------------
# Voice mapping: each OpenAI voice must map to the correct Qwen3-TTS speaker
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("openai_voice,expected_speaker", VOICE_TO_SPEAKER.items())
def test_voice_mapped_to_correct_speaker(
    client, valid_request, monkeypatch, openai_voice, expected_speaker
):
    received = {}

    def capturing_synthesize(text, voice, speed, instructions):
        received["voice"] = voice
        return (np.zeros(24000, dtype=np.float32), 24000)

    monkeypatch.setattr("src.model.synthesize", capturing_synthesize)

    valid_request["voice"] = openai_voice
    response = client.post(ENDPOINT, json=valid_request)

    assert response.status_code == 200
    assert received.get("voice") == expected_speaker


# ---------------------------------------------------------------------------
# Error response envelope matches OpenAI format
# ---------------------------------------------------------------------------


def test_error_response_uses_openai_envelope(client, valid_request):
    """When the request is invalid, the body must follow the OpenAI error shape."""
    valid_request["voice"] = "not_a_voice"
    response = client.post(ENDPOINT, json=valid_request)

    assert response.status_code == 422
    body = response.json()
    # OpenAI envelope: { "error": { "message": ..., "type": ..., "code": ... } }
    assert "error" in body
    error = body["error"]
    assert "message" in error
    assert "type" in error
    assert "code" in error
