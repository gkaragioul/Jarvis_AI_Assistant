from __future__ import annotations

import contextlib
import hashlib
import io
import os
import threading
import time
from pathlib import Path

os.environ.setdefault("HF_HOME", r"X:\Jarvis\tts-service\cache\huggingface")
os.environ.setdefault("TORCH_HOME", r"X:\Jarvis\tts-service\cache\torch")
os.environ.setdefault("XDG_CACHE_HOME", r"X:\Jarvis\tts-service\cache")
os.environ.setdefault("TEMP", r"X:\Jarvis\temp")
os.environ.setdefault("TMP", r"X:\Jarvis\temp")
os.environ.setdefault("PIP_CACHE_DIR", r"X:\Jarvis\tts-service\cache\pip")

import numpy as np
import soundfile as sf
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel


REFERENCE_ROOT = Path(os.environ.get("JARVIS_VOICE_REFERENCE_ROOT", r"X:\Jarvis\voices\chatterbox\references"))
DEFAULT_REFERENCE = REFERENCE_ROOT / "jarvis_online_derek_reference.wav"
CACHE_ROOT = Path(os.environ.get("JARVIS_TTS_CACHE_ROOT", r"X:\Jarvis\tts-service\cache\audio"))
FAST_DEREK_URL = os.environ.get("JARVIS_FAST_DEREK_URL", "").strip()

VOICE_PRESETS = {
    "jarvis_online_derek": {
        "reference": DEFAULT_REFERENCE,
        "exaggeration": 0.46,
        "cfg_weight": 0.38,
        "temperature": 0.72,
    },
}

app = FastAPI(title="Jarvis Remote TTS", version="1.0")
model_lock = threading.Lock()
synth_lock = threading.Lock()
model = None
model_device = "cpu"
model_warmed = False
model_reference_ready = False


class SynthesizeRequest(BaseModel):
    text: str
    voice_id: str = "jarvis_online_derek"
    speed: float = 1.0
    fx: str = "presence"
    mode: str = "fast"


def _resolve_device() -> str:
    forced = os.environ.get("JARVIS_TTS_DEVICE", "").strip().lower()
    if forced == "cpu":
        return "cpu"

    if forced in {"directml", "dml"}:
        try:
            import torch
            import torch_directml

            device = torch_directml.device()
            probe = torch.ones((1,), device=device)
            _ = float(probe.cpu().sum())
            return device
        except Exception:
            raise

    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
    except Exception:
        pass
    return "cpu"


def _ensure_model():
    global model, model_device, model_reference_ready
    if model is not None:
        return model
    with model_lock:
        if model is not None:
            return model
        import chatterbox.tts as chatterbox_tts

        class _NoopWatermarker:
            def apply_watermark(self, wav, sample_rate=None):
                return wav

        if getattr(chatterbox_tts.perth, "PerthImplicitWatermarker", None) is None:
            chatterbox_tts.perth.PerthImplicitWatermarker = _NoopWatermarker

        ChatterboxTTS = chatterbox_tts.ChatterboxTTS

        model_device = _resolve_device()
        model = ChatterboxTTS.from_pretrained(device=model_device)
        preset = VOICE_PRESETS["jarvis_online_derek"]
        reference = Path(preset["reference"])
        if reference.exists():
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                model.prepare_conditionals(
                    str(reference),
                    exaggeration=float(preset["exaggeration"]),
                )
            model_reference_ready = True
        return model


def _delay(x: np.ndarray, samples: int) -> np.ndarray:
    y = np.zeros_like(x)
    if samples < len(x):
        y[samples:] = x[:-samples]
    return y


def _detune(x: np.ndarray, factor: float) -> np.ndarray:
    if factor == 1.0:
        return x.copy()
    src = np.arange(len(x), dtype=np.float32) * factor
    src = np.clip(src, 0, len(x) - 1)
    return np.interp(src, np.arange(len(x)), x).astype(np.float32)


def _highpass(x: np.ndarray, sr: int, cutoff: float = 70.0) -> np.ndarray:
    rc = 1.0 / (2.0 * np.pi * cutoff)
    dt = 1.0 / sr
    alpha = rc / (rc + dt)
    y = np.zeros_like(x)
    for i in range(1, len(x)):
        y[i] = alpha * (y[i - 1] + x[i] - x[i - 1])
    return y


def _lowpass(x: np.ndarray, sr: int, cutoff: float = 180.0) -> np.ndarray:
    rc = 1.0 / (2.0 * np.pi * cutoff)
    dt = 1.0 / sr
    alpha = dt / (rc + dt)
    y = np.zeros_like(x)
    y[0] = x[0] if len(x) else 0.0
    for i in range(1, len(x)):
        y[i] = y[i - 1] + alpha * (x[i] - y[i - 1])
    return y


def _presence_fx(x: np.ndarray, sr: int) -> np.ndarray:
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x.astype(np.float32)
    dry = x / float(np.max(np.abs(x)) or 1.0)
    t = np.arange(len(dry), dtype=np.float32) / float(sr)
    bass = _lowpass(dry, sr, cutoff=155.0)
    ring = dry * np.sin(2.0 * np.pi * 68.0 * t)
    y = dry * 0.91 + bass * 0.18 + ring * 0.034
    drive = 1.22
    y = np.tanh(y * drive) / np.tanh(drive)
    y *= 0.94 / float(np.max(np.abs(y)) or 1.0)
    return y.astype(np.float32)


def _jarvis_fx(x: np.ndarray, sr: int, *, strong: bool) -> np.ndarray:
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x.astype(np.float32)
    dry = x / float(np.max(np.abs(x)) or 1.0)
    t = np.arange(len(dry), dtype=np.float32) / float(sr)
    short = _delay(dry, int(sr * 0.014))
    slap = _delay(dry, int(sr * 0.034))
    wide_a = _detune(dry, 0.996)
    wide_b = _detune(dry, 1.004)
    ring = dry * np.sin(2.0 * np.pi * 82.0 * t)
    shimmer = dry * np.sin(2.0 * np.pi * 164.0 * t)
    if strong:
        mid = _delay(dry, int(sr * 0.022))
        deep = _detune(dry, 0.985)
        high = _detune(dry, 1.015)
        bass = _lowpass(deep, sr, cutoff=210.0)
        y = (
            dry * 0.68
            + short * 0.19
            + mid * 0.14
            + slap * 0.13
            + wide_a * 0.10
            + wide_b * 0.10
            + deep * 0.12
            + bass * 0.16
            + high * 0.055
            + ring * 0.084
            + shimmer * 0.040
        )
        drive = 1.78
    else:
        y = dry * 0.78 + short * 0.16 + slap * 0.10 + wide_a * 0.08 + wide_b * 0.08 + ring * 0.055 + shimmer * 0.025
        drive = 1.45
    y = _highpass(y, sr)
    y = np.tanh(y * drive) / np.tanh(drive)
    y *= 0.96 / float(np.max(np.abs(y)) or 1.0)
    return y.astype(np.float32)


def _to_wav(audio: np.ndarray, sample_rate: int) -> bytes:
    out = io.BytesIO()
    sf.write(out, audio, sample_rate, format="WAV", subtype="PCM_16")
    return out.getvalue()


def _cache_path(req: SynthesizeRequest) -> Path:
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    payload = "\n".join([
        req.voice_id,
        req.fx.lower(),
        req.mode.lower(),
        f"{req.speed:.3f}",
        req.text.strip(),
    ])
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return CACHE_ROOT / f"{digest}.wav"


def _try_fast_derek_runtime(req: SynthesizeRequest) -> bytes | None:
    if not FAST_DEREK_URL:
        return None
    try:
        import httpx

        with httpx.Client(timeout=12.0) as client:
            remote = client.post(
                FAST_DEREK_URL,
                json={
                    "text": req.text,
                    "voice_id": req.voice_id,
                    "speed": req.speed,
                    "fx": req.fx,
                    "mode": req.mode,
                },
            )
        if remote.status_code < 400 and remote.content:
            return remote.content
    except Exception:
        return None
    return None


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "device": str(model_device),
        "reference_exists": DEFAULT_REFERENCE.exists(),
        "reference_ready": model_reference_ready,
        "fast_runtime": {
            "configured": bool(FAST_DEREK_URL),
            "url": FAST_DEREK_URL or None,
        },
    }


@app.post("/prewarm")
def prewarm():
    global model_warmed
    tts = _ensure_model()
    if not model_warmed:
        preset = VOICE_PRESETS["jarvis_online_derek"]
        reference = Path(preset["reference"])
        if reference.exists():
            with synth_lock:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    wav = tts.generate(
                        "Online, Sir.",
                        audio_prompt_path=None,
                        exaggeration=float(preset["exaggeration"]),
                        cfg_weight=float(preset["cfg_weight"]),
                        temperature=float(preset["temperature"]),
                    )
            del wav
        model_warmed = True
    return health()


@app.on_event("startup")
def startup_prewarm():
    def warm():
        try:
            prewarm()
        except Exception:
            pass

    threading.Thread(target=warm, daemon=True).start()


@app.post("/synthesize")
def synthesize(req: SynthesizeRequest):
    started = time.perf_counter()
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Missing text")
    if req.voice_id != "jarvis_online_derek":
        raise HTTPException(
            status_code=400,
            detail="Jarvis voice is locked to jarvis_online_derek",
        )

    cache_path = _cache_path(req)
    if cache_path.exists():
        return Response(
            content=cache_path.read_bytes(),
            media_type="audio/wav",
            headers={
                "X-Jarvis-Voice": req.voice_id,
                "X-Jarvis-TTS": "fast-derek-cache",
                "X-Jarvis-TTS-Device": str(model_device),
                "X-Jarvis-TTS-Cache": "hit",
                "X-Jarvis-TTS-Ms": str(round((time.perf_counter() - started) * 1000)),
            },
        )

    fast_audio = _try_fast_derek_runtime(req)
    if fast_audio:
        cache_path.write_bytes(fast_audio)
        return Response(
            content=fast_audio,
            media_type="audio/wav",
            headers={
                "X-Jarvis-Voice": req.voice_id,
                "X-Jarvis-TTS": "fast-derek-runtime",
                "X-Jarvis-TTS-Device": "pc",
                "X-Jarvis-TTS-Cache": "miss",
                "X-Jarvis-TTS-Ms": str(round((time.perf_counter() - started) * 1000)),
            },
        )

    preset = VOICE_PRESETS.get(req.voice_id, VOICE_PRESETS["jarvis_online_derek"])
    reference = Path(preset["reference"])
    if not reference.exists():
        raise HTTPException(status_code=500, detail=f"Missing reference voice: {reference}")

    with synth_lock:
        tts = _ensure_model()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            wav = tts.generate(
                text,
                audio_prompt_path=None,
                exaggeration=float(preset["exaggeration"]),
                cfg_weight=float(preset["cfg_weight"]),
                temperature=float(preset["temperature"]),
            )

    audio = wav.squeeze().detach().cpu().numpy().astype(np.float32)
    sample_rate = int(getattr(tts, "sr", 24000))

    fx = req.fx.lower()
    if fx in {"presence", "weight", "jarvis", "normal", ""}:
        audio = _presence_fx(audio, sample_rate)
    elif fx in {"strong", "jarvis_strong"}:
        audio = _jarvis_fx(audio, sample_rate, strong=True)
    elif fx not in {"none", "off"}:
        raise HTTPException(status_code=400, detail="Unknown voice FX")

    wav_bytes = _to_wav(audio, sample_rate)
    cache_path.write_bytes(wav_bytes)

    return Response(
        content=wav_bytes,
        media_type="audio/wav",
        headers={
            "X-Jarvis-Voice": req.voice_id,
            "X-Jarvis-TTS": "fast-derek-cache",
            "X-Jarvis-TTS-Device": str(model_device),
            "X-Jarvis-TTS-Cache": "miss",
            "X-Jarvis-TTS-Ms": str(round((time.perf_counter() - started) * 1000)),
        },
    )
