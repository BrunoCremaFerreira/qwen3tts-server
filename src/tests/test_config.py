"""
Tests for src.config.Settings.

Each test verifies a single configuration field — either its default value or
its ability to be overridden via environment variable.
"""

import pytest


def test_model_name_default():
    from src.config import Settings

    s = Settings()
    assert s.MODEL_NAME_OR_PATH == "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"


def test_model_name_overridden_by_env(monkeypatch):
    monkeypatch.setenv("MODEL_NAME_OR_PATH", "local/my-model")

    from importlib import reload
    import src.config as cfg_module
    reload(cfg_module)
    from src.config import Settings

    s = Settings()
    assert s.MODEL_NAME_OR_PATH == "local/my-model"


def test_device_default_is_none():
    from src.config import Settings

    s = Settings()
    assert s.DEVICE is None


def test_device_overridden_by_env(monkeypatch):
    monkeypatch.setenv("DEVICE", "cuda")

    from src.config import Settings

    s = Settings()
    assert s.DEVICE == "cuda"


def test_port_default():
    from src.config import Settings

    s = Settings()
    assert s.PORT == 8000


def test_port_overridden_by_env_and_is_int(monkeypatch):
    monkeypatch.setenv("PORT", "9090")

    from src.config import Settings

    s = Settings()
    assert s.PORT == 9090
    assert isinstance(s.PORT, int)


def test_host_default():
    from src.config import Settings

    s = Settings()
    assert s.HOST == "0.0.0.0"


def test_workers_default():
    from src.config import Settings

    s = Settings()
    assert s.WORKERS == 1


def test_workers_overridden_by_env_and_is_int(monkeypatch):
    monkeypatch.setenv("WORKERS", "4")

    from src.config import Settings

    s = Settings()
    assert s.WORKERS == 4
    assert isinstance(s.WORKERS, int)


def test_log_level_default():
    from src.config import Settings

    s = Settings()
    assert s.LOG_LEVEL == "info"


def test_voice_map_default_is_none():
    from src.config import Settings

    s = Settings()
    assert s.VOICE_MAP is None


def test_hf_home_default_is_none():
    from src.config import Settings

    s = Settings()
    assert s.HF_HOME is None
