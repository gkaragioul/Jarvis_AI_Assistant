$ErrorActionPreference = "SilentlyContinue"

$roots = @("X:\Jarvis", "X:\Jarvis\tts-gpu", "X:\Jarvis\tools", "X:\Jarvis\fast-derek")
$pattern = "openvoice|melo|piper|vits|kokoro|onnx|rvc|voice"

foreach ($root in $roots) {
  if (-not (Test-Path $root)) { continue }
  Get-ChildItem -Path $root -Recurse -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -match $pattern } |
    Select-Object -First 200 FullName
}
