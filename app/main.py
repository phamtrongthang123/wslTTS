from __future__ import annotations

import io
import wave

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import BASE_DIR, DEFAULT_VOICE, SAMPLE_RATE
from .tts import synthesize
from .voices import get_languages, get_voices, resolve_lang_code

SUPPORTED_LANG_CODES = {"a", "b", "e", "f", "h", "i", "j", "p", "z"}

app = FastAPI(title="Kokoro Web", version="0.1.0")

web_dir = BASE_DIR / "web"
app.mount("/static", StaticFiles(directory=web_dir), name="static")


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1)
    voice: str = Field(default=DEFAULT_VOICE, min_length=1)
    lang_code: str | None = None
    speed: float = Field(default=1.0, ge=0.5, le=2.0)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(web_dir / "index.html")


@app.get("/api/voices")
def voices() -> JSONResponse:
    return JSONResponse(
        {
            "default_voice": DEFAULT_VOICE,
            "voices": get_voices(),
            "languages": get_languages(),
        }
    )


@app.get("/api/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.post("/api/tts")
def tts(request: TTSRequest) -> StreamingResponse:
    lang_code = resolve_lang_code(request.voice, request.lang_code)
    if lang_code not in SUPPORTED_LANG_CODES:
        raise HTTPException(status_code=400, detail=f"Unsupported lang_code: {lang_code}")

    try:
        audio = synthesize(
            text=request.text,
            voice=request.voice,
            lang_code=lang_code,
            speed=request.speed,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        message = str(exc)
        status = 400 if "espeak-ng" in message else 500
        raise HTTPException(status_code=status, detail=message) from exc

    wav_bytes = audio_to_wav_bytes(audio, SAMPLE_RATE)
    duration = len(audio) / float(SAMPLE_RATE)
    headers = {
        "Content-Disposition": "inline; filename=kokoro.wav",
        "X-Sample-Rate": str(SAMPLE_RATE),
        "X-Duration-Seconds": f"{duration:.3f}",
    }
    return StreamingResponse(
        io.BytesIO(wav_bytes),
        media_type="audio/wav",
        headers=headers,
    )


def audio_to_wav_bytes(audio: np.ndarray, sample_rate: int) -> bytes:
    audio = np.clip(audio, -1.0, 1.0)
    pcm16 = (audio * 32767.0).astype(np.int16)
    with io.BytesIO() as buffer:
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm16.tobytes())
        return buffer.getvalue()
