import nltk

target = "X:/Jarvis/tts-gpu/cache/nltk_data"
for package in (
    "averaged_perceptron_tagger_eng",
    "averaged_perceptron_tagger",
    "cmudict",
):
    print(f"downloading {package} -> {target}")
    nltk.download(package, download_dir=target, quiet=False)
