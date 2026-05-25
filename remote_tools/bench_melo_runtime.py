import time
from pathlib import Path

import nltk
import torch
from melo.api import TTS

out = Path("X:/Jarvis/temp/melo_test.wav")
nltk.data.path.insert(0, "X:/Jarvis/tts-gpu/nltk_data")
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"torch={torch.__version__} cuda={torch.cuda.is_available()} device={device}")

started = time.perf_counter()
model = TTS(language="EN_NEWEST", device=device)
print(f"load={time.perf_counter() - started:.3f}s")
print(f"speakers={model.hps.data.spk2id}")
speaker_id = next(iter(model.hps.data.spk2id.values()))

for text in [
    "Yes, Sir.",
    "I am good, Sir.",
    "That makes sense, Sir.",
    "I am good, just thinking through it with you.",
]:
    started = time.perf_counter()
    model.tts_to_file(text, speaker_id, str(out), speed=1.2, quiet=True)
    print(f"text={text!r} tts={time.perf_counter() - started:.3f}s size={out.stat().st_size}")
