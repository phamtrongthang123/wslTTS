from __future__ import annotations

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[1]

# Keep model and voice downloads inside the project by default.
if "HF_HOME" not in os.environ:
    os.environ["HF_HOME"] = os.getenv(
        "KOKORO_HF_HOME",
        str(BASE_DIR / ".cache" / "huggingface"),
    )

REPO_ID = os.getenv("KOKORO_REPO_ID", "hexgrad/Kokoro-82M")
DEVICE = os.getenv("KOKORO_DEVICE")  # "cpu", "cuda", "mps", or empty for auto
DEFAULT_VOICE = os.getenv("KOKORO_DEFAULT_VOICE", "af_heart")
DEFAULT_LANG = os.getenv("KOKORO_DEFAULT_LANG", "a")
MAX_CHARS = int(os.getenv("KOKORO_MAX_CHARS", "2000"))
SAMPLE_RATE = int(os.getenv("KOKORO_SAMPLE_RATE", "24000"))
SERVER_HOST = os.getenv("KOKORO_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("KOKORO_PORT", "3003"))
