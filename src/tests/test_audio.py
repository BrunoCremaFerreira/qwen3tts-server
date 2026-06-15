"""
Tests for src.audio.encode(wav_array, sample_rate, format) -> bytes.

Uses a synthetic 1-second 440 Hz sine wave at 24 kHz to exercise each output
format without requiring a real TTS model.
"""

import numpy as np
import pytest


SAMPLE_RATE = 24000
# 1 second of 440 Hz tone at 24 kHz — a real signal so lossy codecs have
# something to compress rather than pure silence, which can produce zero bytes.
SINE_WAVE = np.sin(
    np.linspace(0, 2 * np.pi * 440, SAMPLE_RATE, dtype=np.float32)
).astype(np.float32)


def test_encode_wav_returns_nonempty_bytes():
    from src.audio import encode

    result = encode(SINE_WAVE, SAMPLE_RATE, "wav")

    assert isinstance(result, bytes)
    assert len(result) > 0


def test_encode_wav_starts_with_riff_header():
    from src.audio import encode

    result = encode(SINE_WAVE, SAMPLE_RATE, "wav")

    assert result[:4] == b"RIFF"


def test_encode_mp3_returns_nonempty_bytes():
    from src.audio import encode

    result = encode(SINE_WAVE, SAMPLE_RATE, "mp3")

    assert isinstance(result, bytes)
    assert len(result) > 0


def test_encode_opus_returns_nonempty_bytes():
    from src.audio import encode

    result = encode(SINE_WAVE, SAMPLE_RATE, "opus")

    assert isinstance(result, bytes)
    assert len(result) > 0


def test_encode_flac_returns_nonempty_bytes():
    from src.audio import encode

    result = encode(SINE_WAVE, SAMPLE_RATE, "flac")

    assert isinstance(result, bytes)
    assert len(result) > 0


def test_encode_pcm_length_equals_samples_times_4():
    """PCM is raw float32; each sample occupies 4 bytes."""
    from src.audio import encode

    result = encode(SINE_WAVE, SAMPLE_RATE, "pcm")

    assert isinstance(result, bytes)
    assert len(result) == len(SINE_WAVE) * 4


def test_encode_unknown_format_raises_value_error():
    from src.audio import encode

    with pytest.raises(ValueError):
        encode(SINE_WAVE, SAMPLE_RATE, "ogg")
