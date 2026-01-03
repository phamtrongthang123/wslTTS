# Kokoro-82M Self-Host Webapp

Local web UI for the `hexgrad/Kokoro-82M` text-to-speech model.

## Quick start

1. Create and sync the uv environment:

```bash
uv venv --seed pip
uv sync
```

If you already created the venv without pip, run `uv pip install pip` once.

2. Start the server:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 3003 --reload
```

Then open `http://localhost:3003`.

## System dependency

If you see errors about missing `espeak-ng`, install it once:

```bash
sudo apt-get update
sudo apt-get install -y espeak-ng
```

## Optional language extras

Japanese and Mandarin require extra G2P data:

```bash
uv sync --extra ja --extra zh
```

## Environment overrides

- `KOKORO_DEVICE`: `cpu` or `mps` (CUDA is always used when available)
- `KOKORO_REPO_ID`: model repo (default: `hexgrad/Kokoro-82M`)
- `KOKORO_DEFAULT_VOICE`: default voice id (default: `af_heart`)
- `KOKORO_DEFAULT_LANG`: default language code (default: `a`)
- `KOKORO_MAX_CHARS`: max input length (default: `2000`)
- `KOKORO_HF_HOME`: cache directory for HF downloads
- `KOKORO_HOST` / `KOKORO_PORT`: server bind settings (default port: 3003)

## Notes

- The model and voice packs download on first use and are cached under `.cache/huggingface`.
- The first English request may download the `en_core_web_sm` spaCy model (requires pip in the venv).
- If you add new voices upstream, update `data/voices.json` accordingly.

## systemd (user service)

Install as a user service so it starts on login:

```bash
systemctl --user daemon-reload
systemctl --user enable --now kokoro-web.service
```

Unit file location:

```
~/.config/systemd/user/kokoro-web.service
```

Service content:

```ini
[Unit]
Description=Kokoro Web TTS
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/ptthang/wslTTS
Environment=PYTHONUNBUFFERED=1
Environment=KOKORO_PORT=3003
Environment=KOKORO_HF_HOME=/home/ptthang/wslTTS/.cache/huggingface
ExecStart=/home/ptthang/wslTTS/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 3003
Restart=on-failure
RestartSec=3

[Install]
WantedBy=default.target
```

Logs:

```bash
journalctl --user -u kokoro-web.service -f
```

Auto-start even without login:

```bash
loginctl enable-linger "$USER"
```
