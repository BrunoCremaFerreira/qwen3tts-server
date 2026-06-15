from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MODEL_NAME_OR_PATH: str = "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"
    DEVICE: Optional[str] = None
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    WORKERS: int = 1
    LOG_LEVEL: str = "info"
    VOICE_MAP: Optional[str] = None
    HF_HOME: Optional[str] = None
