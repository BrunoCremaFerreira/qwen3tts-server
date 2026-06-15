from typing import Optional

import numpy as np

_model = None


def _detect_device(settings) -> str:
    import torch

    if settings.DEVICE:
        return settings.DEVICE
    return "cuda:0" if torch.cuda.is_available() else "cpu"


def load_model(settings) -> None:
    global _model

    import torch
    from qwen_tts import Qwen3TTSModel  # type: ignore[import]

    device = _detect_device(settings)
    dtype = torch.bfloat16 if device.startswith("cuda") else torch.float32

    _model = Qwen3TTSModel.from_pretrained(
        settings.MODEL_NAME_OR_PATH,
        dtype=dtype,
        device_map=device,
    )


def synthesize(
    text: str,
    voice: str,
    speed: float,
    instructions: Optional[str],
) -> tuple[np.ndarray, int]:
    assert _model is not None, "load_model() must be called before synthesize()"

    # speed is not supported by generate_custom_voice; accepted silently for
    # API compatibility with the OpenAI TTS contract.
    wavs, sample_rate = _model.generate_custom_voice(
        text=text,
        language="Auto",
        speaker=voice,
        instruct=instructions,
    )
    arr = np.array(wavs[0], dtype=np.float32)
    return arr, sample_rate
