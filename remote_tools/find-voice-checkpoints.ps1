$ErrorActionPreference = "SilentlyContinue"

Get-ChildItem -Path "X:\Jarvis\tts-gpu" -Recurse -File -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -match "checkpoint|config\.json|base_speakers|ses|converter|openvoice" } |
  Select-Object -First 200 FullName,Length
