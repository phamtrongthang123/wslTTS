from __future__ import annotations

import os
import threading

import numpy as np
import torch
from kokoro import KModel, KPipeline

from .config import DEVICE, MAX_CHARS, REPO_ID

_model_lock = threading.Lock()
_pipeline_lock = threading.Lock()
_model: KModel | None = None
_pipelines: dict[str, KPipeline] = {}


def _select_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if DEVICE:
        device = DEVICE.lower()
        if device == "mps" and not torch.backends.mps.is_available():
            raise RuntimeError("MPS requested but not available")
        if device == "mps" and os.environ.get("PYTORCH_ENABLE_MPS_FALLBACK") != "1":
            raise RuntimeError("MPS requested but fallback not enabled")
        if device == "cuda":
            return "cpu"
        return device
    if os.environ.get("PYTORCH_ENABLE_MPS_FALLBACK") == "1" and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _get_model() -> KModel:
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                model = KModel(repo_id=REPO_ID)
                model = model.to(_select_device()).eval()
                _model = model
    return _model


def _get_pipeline(lang_code: str) -> KPipeline:
    lang_code = lang_code.lower()
    if lang_code not in _pipelines:
        with _pipeline_lock:
            if lang_code not in _pipelines:
                _pipelines[lang_code] = KPipeline(
                    lang_code=lang_code,
                    repo_id=REPO_ID,
                    model=_get_model(),
                )
    return _pipelines[lang_code]


def synthesize(text: str, voice: str, lang_code: str, speed: float) -> np.ndarray:
    text = text.strip()
    if not text:
        raise ValueError("Text is required")
    if len(text) > MAX_CHARS:
        raise ValueError(f"Text exceeds MAX_CHARS ({MAX_CHARS})")

    lang_code = lang_code.lower()
    pipeline = _get_pipeline(lang_code)
    audio_chunks: list[np.ndarray] = []
    with torch.inference_mode():
        for result in pipeline(text, voice=voice, speed=speed):
            if result.audio is None:
                continue
            audio_chunks.append(result.audio.detach().cpu().numpy().reshape(-1))

    if not audio_chunks:
        raise RuntimeError("No audio produced")

    return np.concatenate(audio_chunks)
