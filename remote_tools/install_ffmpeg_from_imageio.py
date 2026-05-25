import shutil
from pathlib import Path

import imageio_ffmpeg

src = Path(imageio_ffmpeg.get_ffmpeg_exe())
dst_dir = Path("X:/Jarvis/tools/ffmpeg")
dst_dir.mkdir(parents=True, exist_ok=True)
dst = dst_dir / "ffmpeg.exe"
shutil.copy2(src, dst)
print(dst)
