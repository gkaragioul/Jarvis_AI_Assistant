import os
import time
from pathlib import Path

import torch
from melo.api import TTS
from openvoice.api import ToneColorConverter
import nltk

ROOT = Path("X:/Jarvis")
OPENVOICE = ROOT / "tts-openvoice"
OUT = ROOT / "tts-gpu" / "bench"
REF = ROOT / "voices" / "chatterbox" / "references" / "jarvis_online_derek_reference.wav"
FFMPEG = ROOT / "tools" / "ffmpeg"

os.chdir(OPENVOICE)
OUT.mkdir(parents=True, exist_ok=True)
os.environ["PATH"] = str(FFMPEG) + os.pathsep + os.environ.get("PATH", "")
nltk.data.path.insert(0, str(ROOT / "tts-gpu" / "nltk_data"))

device = os.environ.get("JARVIS_OPENVOICE_DEVICE")
if not device:
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"torch={torch.__version__} device={device}")
if torch.cuda.is_available():
    print(f"gpu={torch.cuda.get_device_name(0)}")

started = time.perf_counter()
converter = ToneColorConverter("checkpoints_v2/converter/config.json", device=device)
converter.watermark_model = None
converter.load_ckpt("checkpoints_v2/converter/checkpoint.pth")
print(f"converter_load={time.perf_counter() - started:.3f}s")

started = time.perf_counter()
target_se = converter.extract_se(str(REF), se_save_path=str(ROOT / "fast-derek" / "derek_openvoice_target_se.pth"))
print(f"target_extract={time.perf_counter() - started:.3f}s")

started = time.perf_counter()
model = TTS(language="EN_NEWEST", device=device)
print(f"melo_load={time.perf_counter() - started:.3f}s")
print(f"speakers={model.hps.data.spk2id}")

speaker_key, speaker_id = next(iter(model.hps.data.spk2id.items()))
source_key = speaker_key.lower().replace("_", "-")
source_se = torch.load(
    f"checkpoints_v2/base_speakers/ses/{source_key}.pth",
    map_location=device,
    weights_only=False,
)

texts = [
    "I am here, Sir.",
    "I am doing well, Sir. What are we building next?",
    "That makes sense, Sir. I can stay conversational and respond naturally.",
]

for i, text in enumerate(texts, start=1):
    src_path = OUT / f"openvoice_base_{i}.wav"
    save_path = OUT / f"openvoice_derek_{i}.wav"
    started = time.perf_counter()
    model.tts_to_file(text, speaker_id, str(src_path), speed=1.18, quiet=True)
    base_time = time.perf_counter() - started

    started = time.perf_counter()
    converter.convert(
        audio_src_path=str(src_path),
        src_se=source_se,
        tgt_se=target_se,
        output_path=str(save_path),
        message="@Jarvis",
    )
    convert_time = time.perf_counter() - started
    print(
        f"text_{i} base={base_time:.3f}s convert={convert_time:.3f}s "
        f"total={base_time + convert_time:.3f}s out={save_path}"
    )
