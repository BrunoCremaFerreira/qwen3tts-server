from typing import Literal, Optional

from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel, Field

import src.audio as audio
import src.model as model

router = APIRouter()

VOICE_MAP = {
    "alloy": "Chelsie",
    "echo": "Ethan",
    "fable": "Cove",
    "nova": "Sora",
    "onyx": "Luca",
    "shimmer": "Aoede",
}

CONTENT_TYPE = {
    "wav": "audio/wav",
    "mp3": "audio/mpeg",
    "opus": "audio/opus",
    "flac": "audio/flac",
    "pcm": "audio/pcm",
}


class SpeechRequest(BaseModel):
    model: str
    input: str = Field(min_length=1, max_length=4096)
    voice: Literal["alloy", "echo", "fable", "nova", "onyx", "shimmer"]
    response_format: Literal["wav", "mp3", "opus", "flac", "pcm"] = "wav"
    speed: float = Field(default=1.0, ge=0.25, le=4.0)
    instructions: Optional[str] = None


@router.post("/audio/speech")
async def speech(req: SpeechRequest):
    speaker = VOICE_MAP[req.voice]
    wav_array, sample_rate = model.synthesize(
        req.input, speaker, req.speed, req.instructions
    )
    audio_bytes = audio.encode(wav_array, sample_rate, req.response_format)
    return Response(content=audio_bytes, media_type=CONTENT_TYPE[req.response_format])
