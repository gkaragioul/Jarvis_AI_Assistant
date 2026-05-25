from __future__ import annotations

import asyncio
import contextlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel


ROOT = Path(os.environ.get("JARVIS_ROOT", r"X:\Jarvis"))
SERVICE_ROOT = Path(os.environ.get("JARVIS_VOICE_SERVER_ROOT", ROOT / "voice-server"))
TEMP_ROOT = Path(os.environ.get("JARVIS_TEMP", ROOT / "temp"))
TOOLS_ROOT = Path(os.environ.get("JARVIS_TOOLS", ROOT / "tools"))
WHISPER_ROOT = Path(os.environ.get("JARVIS_WHISPER_ROOT", TOOLS_ROOT / "whispercpp" / "v1.8.4"))
WHISPER_MODEL = Path(os.environ.get("JARVIS_WHISPER_MODEL", SERVICE_ROOT / "models" / "ggml-small.en.bin"))
REMOTE_TTS_URL = os.environ.get("JARVIS_REMOTE_TTS_URL", "http://127.0.0.1:11550/synthesize")
OLLAMA_URL = os.environ.get("JARVIS_OLLAMA_URL", "http://127.0.0.1:11434")
VOICE_ID = "jarvis_online_derek"

for path in (SERVICE_ROOT, TEMP_ROOT):
    path.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Jarvis PC Voice Server", version="1.0")
stt_lock = asyncio.Lock()


class SynthesizeRequest(BaseModel):
    text: str
    voice_id: str = VOICE_ID
    speed: float = 1.0
    fx: str = "none"
    mode: str = "fast"


def _find_whisper_cli() -> Optional[Path]:
    candidates = [
        WHISPER_ROOT / "whisper-cli.exe",
        WHISPER_ROOT / "main.exe",
        WHISPER_ROOT / "bin" / "whisper-cli.exe",
        WHISPER_ROOT / "bin" / "main.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    found = list(WHISPER_ROOT.rglob("whisper-cli.exe")) + list(WHISPER_ROOT.rglob("main.exe"))
    return found[0] if found else None


def _duration_hint(audio_path: Path) -> float:
    # Lightweight fallback hint used only for health/debug output; STT itself is CLI-driven.
    return max(0.0, audio_path.stat().st_size / 32000.0)


def _transcribe_with_whisper_cpp(audio: bytes, filename: str, language: Optional[str]) -> dict:
    whisper_cli = _find_whisper_cli()
    if whisper_cli is None:
        raise RuntimeError(f"whisper.cpp CLI was not found under {WHISPER_ROOT}")
    if not WHISPER_MODEL.exists():
        raise RuntimeError(f"Whisper model is missing: {WHISPER_MODEL}")

    suffix = Path(filename or "audio.wav").suffix or ".wav"
    with tempfile.TemporaryDirectory(prefix="jarvis-stt-", dir=str(TEMP_ROOT)) as tmpdir:
        tmp = Path(tmpdir)
        audio_path = tmp / f"input{suffix}"
        out_base = tmp / "transcript"
        audio_path.write_bytes(audio)

        command = [
            str(whisper_cli),
            "-m",
            str(WHISPER_MODEL),
            "-f",
            str(audio_path),
            "-l",
            language or "en",
            "-otxt",
            "-of",
            str(out_base),
            "-nt",
            "-t",
            str(max(4, (os.cpu_count() or 8) - 2)),
            "--prompt",
            (
                "Transcribe clear English speech from a Greek-accented speaker "
                "talking to an AI assistant named Jarvis. Common words include "
                "Jarvis, Sir, app, model, voice, computer, GPU, Mac, PC, Ollama, "
                "and OpenJarvis."
            ),
        ]

        started = time.perf_counter()
        completed = subprocess.run(
            command,
            cwd=str(WHISPER_ROOT),
            capture_output=True,
            text=True,
            timeout=45,
        )
        elapsed = time.perf_counter() - started

        if completed.returncode != 0:
            raise RuntimeError(
                "whisper.cpp failed: "
                + (completed.stderr or completed.stdout or f"exit {completed.returncode}")[-1500:]
            )

        transcript_path = out_base.with_suffix(".txt")
        text = transcript_path.read_text(encoding="utf-8", errors="replace").strip() if transcript_path.exists() else ""
        if not text:
            text = completed.stdout.strip()

        return {
            "text": text,
            "language": language or "en",
            "confidence": None,
            "duration_seconds": _duration_hint(audio_path),
            "engine": "whisper.cpp",
            "model": WHISPER_MODEL.name,
            "elapsed_seconds": elapsed,
        }


@app.get("/health")
async def health():
    whisper_cli = _find_whisper_cli()
    tts_ok = False
    ollama_ok = False
    with contextlib.suppress(Exception):
        async with httpx.AsyncClient(timeout=2.0) as client:
            tts_ok = (await client.get("http://127.0.0.1:11550/health")).is_success
    with contextlib.suppress(Exception):
        async with httpx.AsyncClient(timeout=2.0) as client:
            ollama_ok = (await client.get(f"{OLLAMA_URL}/api/tags")).is_success
    return {
        "status": "ok",
        "root": str(ROOT),
        "stt": {
            "backend": "whisper.cpp",
            "cli": str(whisper_cli) if whisper_cli else None,
            "cli_exists": bool(whisper_cli),
            "model": str(WHISPER_MODEL),
            "model_exists": WHISPER_MODEL.exists(),
            "runtime": "official-windows-cpu",
        },
        "tts": {
            "voice_id": VOICE_ID,
            "url": REMOTE_TTS_URL,
            "healthy": tts_ok,
        },
        "llm": {
            "url": OLLAMA_URL,
            "healthy": ollama_ok,
        },
    }


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...), language: str = Form("en")):
    audio = await file.read()
    if not audio:
        raise HTTPException(status_code=400, detail="Missing audio")
    if stt_lock.locked():
        raise HTTPException(status_code=429, detail="Jarvis is still transcribing previous audio")
    async with stt_lock:
        try:
            return await asyncio.to_thread(
                _transcribe_with_whisper_cpp,
                audio,
                file.filename or "audio.wav",
                language or "en",
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/synthesize")
async def synthesize(req: SynthesizeRequest):
    if req.voice_id != VOICE_ID:
        raise HTTPException(status_code=400, detail=f"Jarvis voice is locked to {VOICE_ID}")
    started = time.perf_counter()
    async with httpx.AsyncClient(timeout=120.0) as client:
        remote = await client.post(
            REMOTE_TTS_URL,
            json=req.model_dump(),
        )
    if remote.status_code >= 400:
        raise HTTPException(status_code=remote.status_code, detail=remote.text[:500])
    return Response(
        content=remote.content,
        media_type=remote.headers.get("content-type", "audio/wav"),
        headers={
            "X-Jarvis-Voice": remote.headers.get("X-Jarvis-Voice", VOICE_ID),
            "X-Jarvis-TTS": remote.headers.get("X-Jarvis-TTS", "derek"),
            "X-Jarvis-TTS-Device": remote.headers.get("X-Jarvis-TTS-Device", "pc"),
            "X-Jarvis-TTS-Cache": remote.headers.get("X-Jarvis-TTS-Cache", "unknown"),
            "X-Jarvis-TTS-Ms": str(round((time.perf_counter() - started) * 1000)),
            "X-Jarvis-TTS-Host": "pc-voice-server",
        },
    )


@app.post("/chat")
async def chat(payload: dict):
    async with httpx.AsyncClient(timeout=60.0) as client:
        remote = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
    if remote.status_code >= 400:
        raise HTTPException(status_code=remote.status_code, detail=remote.text[:500])
    return Response(
        content=remote.content,
        media_type=remote.headers.get("content-type", "application/json"),
    )
