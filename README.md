# Jarvis

Jarvis is a private, local-first voice assistant system built around a Mac operator app and a Windows PC worker node. The Mac handles the user experience, microphone, playback, keyboard or mouse push-to-talk, and the visual Jarvis shell. The PC handles the heavy work: local Ollama inference, speech transcription, Derek-only voice synthesis, and service management from `X:\Jarvis`.

The goal is simple: a conversational AI that feels present, fast, and private. Jarvis should speak like a regular assistant, call George only `Sir`, respond in English, and use the Derek voice profile only. No cloud API costs are required for the core path.

## Product Shape

- **Mac thin client**: Jarvis desktop shell, push-to-talk, UI, playback, and diagnostics.
- **PC worker**: Ollama, voice server, Derek TTS service, GPU-first model execution, and service control.
- **Network**: Tailscale connects the Mac to the PC so the assistant can run from home or away from home.
- **Storage rule**: PC-side Jarvis assets and model services are designed for `X:\Jarvis`.
- **Voice rule**: Derek is the only Jarvis voice. Generated samples, model weights, and cache files stay out of Git.

## Repository Layout

```text
fast-derek-pipeline/   Derek teacher/distillation notes and dataset tooling
pc-tts-service/        PC Derek TTS service scripts and server
pc-voice-server/       PC speech-to-text gateway and service scripts
remote_tools/          Remote diagnostics, setup, and PC control scripts
patches/               Versioned OpenJarvis Mac-app overlay snapshots
docs/                  Release notes and operational notes
```

## Version 0.3 Focus

Version `0.3` captures the first coherent remote Jarvis setup:

- Mac app talks to the PC worker over Tailscale.
- Ollama uses the remote `qwen3:8b` model instead of local Mac LLMs.
- PC services are rooted around `X:\Jarvis`.
- Derek-only TTS is enforced through the remote voice path.
- Live voice mode avoids bulky memory injection for lower latency.
- Startup cleanup reduces duplicate local backend launchers.
- Voice replies are tuned away from canned support-desk phrasing.

## What Is Not Tracked

The repo intentionally excludes generated audio, voice samples, model weights, build products, caches, virtual environments, and the upstream OpenJarvis clone. Those can be large, duplicated, or private runtime artifacts. The active Mac OpenJarvis changes are captured as a patch snapshot in `patches/`.

## License

Original Jarvis_AI_Assistant files are licensed under the [MIT License](LICENSE).

The MIT License does not relicense upstream projects or third-party artifacts. OpenJarvis patch snapshots in `patches/` may include Apache-2.0 OpenJarvis context or derived material, and referenced tools, models, checkpoints, voice samples, generated audio, and runtimes remain under their own terms. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [patches/README.md](patches/README.md).

## Current Runtime Defaults

- Mac API: `http://127.0.0.1:8000`
- PC Ollama: `http://100.117.254.71:11434`
- PC voice gateway: `http://100.117.254.71:11551`
- PC TTS: `http://100.117.254.71:11550`
- Default model: `qwen3:8b`
- Voice ID: `jarvis_online_derek`
