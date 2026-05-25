$ErrorActionPreference = "Stop"

& X:\Jarvis\tools\uv.exe --version
& X:\Jarvis\tts-service\.venv\Scripts\python.exe --version
& X:\Jarvis\tts-service\.venv\Scripts\python.exe -c @'
import importlib.util
import sys
print(sys.executable)
try:
    import torch
    print("torch", torch.__version__, "cuda", torch.cuda.is_available())
except Exception as exc:
    print("torch-error", exc)
for name in ["faster_whisper", "onnxruntime", "torch_directml", "soundfile", "fastapi", "uvicorn"]:
    print(name, importlib.util.find_spec(name) is not None)
'@
