# Third-Party Notices

The original Jarvis_AI_Assistant files in this repository are licensed under
the MIT License. See [LICENSE](LICENSE).

That MIT license does not relicense upstream projects, model weights,
checkpoints, generated audio, voice samples, tools, runtimes, or other
third-party artifacts used with this project. Those items remain under their
own licenses and terms.

## OpenJarvis Patch Snapshots

The `patches/` directory contains overlay snapshots intended to be applied to
an upstream OpenJarvis checkout. These patch files may include OpenJarvis
source context and derived modifications.

OpenJarvis is distributed under the Apache License 2.0. To the extent the
patch snapshots include or derive from OpenJarvis material, that upstream
Apache-2.0 licensing and notice treatment remains applicable. The MIT License
for this repository applies only to original Jarvis_AI_Assistant material and
does not convert OpenJarvis-derived material to MIT-only licensing.

## Runtime Dependencies And Artifacts

This repository references or works with third-party projects and artifacts
that are not vendored here. Examples include:

- OpenJarvis, under the Apache License 2.0.
- Qwen/Ollama models and runtimes, under their respective model and software
  licenses.
- whisper.cpp, under the MIT License according to its upstream repository.
- Chatterbox and OpenVoice components, under the MIT License according to their
  upstream repositories.
- Voice samples, generated audio, checkpoints, model weights, and datasets,
  only when you have the necessary rights to use them.

Before distributing a build, dataset, checkpoint, installer, model bundle, or
voice asset, review the applicable upstream license files and notices for the
exact versions included.
