from pathlib import Path

from huggingface_hub import snapshot_download

ROOT = Path("X:/Jarvis")
OPENVOICE = ROOT / "tts-openvoice"

snapshot_download(
    repo_id="myshell-ai/OpenVoiceV2",
    local_dir=str(OPENVOICE / "checkpoints_v2"),
    local_dir_use_symlinks=False,
    resume_download=True,
)

snapshot_download(
    repo_id="myshell-ai/OpenVoice",
    allow_patterns=["checkpoints/**"],
    local_dir=str(OPENVOICE),
    local_dir_use_symlinks=False,
    resume_download=True,
)

print("OpenVoice checkpoints ready:", OPENVOICE)
