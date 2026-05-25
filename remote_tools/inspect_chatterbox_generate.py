import inspect

from chatterbox.tts import ChatterboxTTS

print(inspect.signature(ChatterboxTTS.generate))
print(inspect.getsource(ChatterboxTTS.generate)[:4000])
