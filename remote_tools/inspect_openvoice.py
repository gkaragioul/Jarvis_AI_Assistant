import inspect
import json
from pathlib import Path

from melo.api import TTS
from openvoice.api import ToneColorConverter

print("ToneColorConverter.convert", inspect.signature(ToneColorConverter.convert))
print("TTS.tts_to_file", inspect.signature(TTS.tts_to_file))

nb_path = Path("X:/Jarvis/tts-openvoice/demo_part3.ipynb")
if nb_path.exists():
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    for index, cell in enumerate(nb["cells"]):
        src = "".join(cell.get("source", []))
        if any(
            token in src
            for token in (
                "tone_color_converter.convert",
                "TTS(language",
                "source_se",
                "target_se",
            )
        ):
            print(f"---CELL {index}---")
            print(src.encode("ascii", "backslashreplace").decode("ascii"))
