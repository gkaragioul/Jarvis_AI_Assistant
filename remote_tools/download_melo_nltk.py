import nltk

download_dir = "X:/Jarvis/tts-gpu/nltk_data"
for package in ("averaged_perceptron_tagger_eng", "averaged_perceptron_tagger"):
    nltk.download(package, download_dir=download_dir)
