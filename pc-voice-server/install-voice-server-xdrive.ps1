$ErrorActionPreference = "Stop"

$root = "X:\Jarvis"
$service = "$root\voice-server"
$tools = "$root\tools"
$whisperRoot = "$tools\whispercpp\v1.8.4"
$models = "$service\models"
$cache = "$service\cache"
$temp = "$root\temp"
$logs = "$service\logs"

New-Item -ItemType Directory -Force `
  $service, `
  $tools, `
  $whisperRoot, `
  $models, `
  $cache, `
  "$cache\uv", `
  "$cache\pip", `
  $temp, `
  $logs | Out-Null

$env:UV_CACHE_DIR = "$cache\uv"
$env:UV_PYTHON_INSTALL_DIR = "$root\python"
$env:UV_LINK_MODE = "copy"
$env:PIP_CACHE_DIR = "$cache\pip"
$env:TEMP = $temp
$env:TMP = $temp

$uv = "$tools\uv.exe"
if (-not (Test-Path $uv)) {
  $uvSource = (Get-Command uv -ErrorAction Stop).Source
  Copy-Item $uvSource $uv -Force
}

$whisperZip = "$cache\whisper-bin-x64-v1.8.4.zip"
if (-not (Test-Path "$whisperRoot\whisper-cli.exe") -and -not (Test-Path "$whisperRoot\main.exe")) {
  Invoke-WebRequest `
    -Uri "https://github.com/ggml-org/whisper.cpp/releases/download/v1.8.4/whisper-bin-x64.zip" `
    -OutFile $whisperZip
  Expand-Archive -Path $whisperZip -DestinationPath $whisperRoot -Force
}

$modelPath = "$models\ggml-small.en.bin"
if (-not (Test-Path $modelPath)) {
  Invoke-WebRequest `
    -Uri "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin?download=true" `
    -OutFile $modelPath
}

Remove-Item "$models\ggml-large-v3-turbo.bin" -Force -ErrorAction SilentlyContinue

Set-Location $service
if (-not (Test-Path "$service\.venv\Scripts\python.exe")) {
  & $uv python install 3.11
  & $uv venv --python 3.11 "$service\.venv"
}

& $uv pip install --python "$service\.venv\Scripts\python.exe" `
  fastapi `
  "uvicorn[standard]" `
  python-multipart `
  httpx `
  pydantic

& "$service\.venv\Scripts\python.exe" -m py_compile "$service\jarvis_voice_server.py"

Write-Host "Jarvis PC voice server installed at $service"
Write-Host "Whisper runtime: $whisperRoot"
Write-Host "Whisper model: $modelPath"
