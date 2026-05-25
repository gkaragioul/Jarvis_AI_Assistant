$ErrorActionPreference = "Stop"

$root = "X:\Jarvis"
$service = "$root\tts-service"
$tools = "$root\tools"
$cache = "$service\cache"
$temp = "$root\temp"

New-Item -ItemType Directory -Force `
  $service, `
  "$service\logs", `
  "$root\voices\chatterbox\references", `
  $tools, `
  $cache, `
  "$cache\uv", `
  "$cache\pip", `
  "$cache\huggingface", `
  "$cache\torch", `
  "$root\python", `
  $temp | Out-Null

$env:UV_CACHE_DIR = "$cache\uv"
$env:UV_PYTHON_INSTALL_DIR = "$root\python"
$env:UV_LINK_MODE = "copy"
$env:PIP_CACHE_DIR = "$cache\pip"
$env:HF_HOME = "$cache\huggingface"
$env:TORCH_HOME = "$cache\torch"
$env:XDG_CACHE_HOME = $cache
$env:TEMP = $temp
$env:TMP = $temp

$uvSource = (Get-Command uv).Source
Copy-Item $uvSource "$tools\uv.exe" -Force
$uv = "$tools\uv.exe"

Set-Location $service
if (Test-Path "$service\.venv") {
  Remove-Item "$service\.venv" -Recurse -Force
}

& $uv python install 3.11
& $uv venv --python 3.11 "$service\.venv"
& $uv pip install --python "$service\.venv\Scripts\python.exe" numpy setuptools wheel cython
& $uv pip install --python "$service\.venv\Scripts\python.exe" fastapi "uvicorn[standard]" soundfile chatterbox-tts --no-build-isolation

& "$service\.venv\Scripts\python.exe" -m py_compile "$service\jarvis_tts_server.py"
& "$service\.venv\Scripts\python.exe" "$service\check_import.py"

Remove-Item "$env:LOCALAPPDATA\uv\cache" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:LOCALAPPDATA\uv\python" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Jarvis TTS X-drive environment ready at $service"
