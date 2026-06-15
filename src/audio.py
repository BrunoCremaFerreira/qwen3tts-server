from io import BytesIO

import numpy as np
import scipy.io.wavfile as wavfile
import soundfile as sf

# soundfile format/subtype for each output format
_SF_PARAMS: dict[str, tuple[str, str | None]] = {
    "mp3": ("MP3", None),
    "opus": ("OGG", "OPUS"),
    "flac": ("FLAC", None),
}


def encode(wav_array: np.ndarray, sample_rate: int, format: str) -> bytes:
    if format == "pcm":
        return wav_array.astype(np.float32).tobytes()

    if format == "wav":
        buf = BytesIO()
        wavfile.write(buf, sample_rate, wav_array)
        return buf.getvalue()

    if format in _SF_PARAMS:
        fmt, subtype = _SF_PARAMS[format]
        buf = BytesIO()
        kwargs = {"subtype": subtype} if subtype else {}
        sf.write(buf, wav_array, sample_rate, format=fmt, **kwargs)
        return buf.getvalue()

    raise ValueError(f"Unsupported audio format: {format!r}")
