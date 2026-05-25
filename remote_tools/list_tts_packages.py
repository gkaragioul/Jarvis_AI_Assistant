import importlib.metadata as metadata

needles = ("piper", "onnx", "voice", "melo", "torch", "chatterbox", "kokoro", "coqui", "tts")

for dist in sorted(metadata.distributions(), key=lambda d: d.metadata.get("Name", "").lower()):
    name = dist.metadata.get("Name", "")
    if any(needle in name.lower() for needle in needles):
        print(f"{name}=={dist.version}")
