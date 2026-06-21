# Jarvis 0.3

Version `0.3` is the first tracked private snapshot of the local Jarvis system.

## Highlights

- Created the repo structure for the Jarvis Mac client plus PC worker setup.
- Captured the active OpenJarvis Mac-app modifications as a patch snapshot.
- Tracked PC-side voice server, Derek TTS service, and remote control scripts.
- Documented the product direction: Mac as operator, PC as GPU worker.
- Preserved the important constraints: Derek-only voice, `Sir` addressing, English responses, remote local inference, and `X:\Jarvis` PC storage.

## Operational Notes

- The upstream OpenJarvis clone is not vendored into this repo.
- Voice/model artifacts are intentionally ignored to avoid hoarding large or generated files.
- Original Jarvis_AI_Assistant repo files are MIT licensed, while OpenJarvis-derived patch material and third-party runtime artifacts remain under their own licenses.
- Runtime services should continue to use the PC over Tailscale for core inference and speech work.

## Tag Description

`0.3` marks the first stable tracking point for the Jarvis remote voice system: a private local-first assistant using a Mac UI, a PC worker node, remote Ollama, Derek-only TTS, and startup/process cleanup for more reliable testing.
