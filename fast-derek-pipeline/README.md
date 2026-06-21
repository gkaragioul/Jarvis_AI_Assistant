# Fast Derek Runtime Plan

This folder is the local control copy for `X:\Jarvis\fast-derek`.

Goal: keep Derek as the only Jarvis voice, but stop doing live voice cloning for every reply. Chatterbox stays the high-quality teacher/reference voice. A lightweight trained runtime voice becomes the fast production voice once trained and validated.

Runtime target:
- Input: arbitrary English text.
- Output: Derek-style Jarvis WAV.
- Expected latency after training: sub-second to roughly 1.5 seconds for short replies.
- Storage: all datasets, models, caches, and tools live under `X:\Jarvis`.

Current stages:
1. `generate_teacher_dataset.py` uses the current Derek Chatterbox service to create a clean training dataset from neutral conversational prompts.
2. The generated dataset becomes the source for a Piper/VITS/ONNX-style runtime model.
3. Jarvis only switches to the fast runtime when a generated validation set sounds like Derek and benchmarks faster than Chatterbox.

Important:
- Do not use macOS voices.
- Do not add any non-Derek runtime voice.
- Do not wire a new TTS engine into Jarvis until it passes latency and voice checks.
- Do not redistribute voice samples, generated datasets, checkpoints, or model artifacts unless you have the rights required by the applicable licenses and voice permissions.
