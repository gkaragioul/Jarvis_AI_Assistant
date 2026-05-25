$ErrorActionPreference = "Stop"

$root = "X:\Jarvis"
$service = "$root\tts-service"
$cache = "$service\cache"
$temp = "$root\temp"

New-Item -ItemType Directory -Force "$service\logs", $cache, "$cache\huggingface", "$cache\torch", $temp | Out-Null

$env:PYTHONUNBUFFERED = "1"
$env:UV_CACHE_DIR = "$cache\uv"
$env:UV_PYTHON_INSTALL_DIR = "$root\python"
$env:UV_LINK_MODE = "copy"
$env:PIP_CACHE_DIR = "$cache\pip"
$env:HF_HOME = "$cache\huggingface"
$env:TORCH_HOME = "$cache\torch"
$env:XDG_CACHE_HOME = $cache
$env:TEMP = $temp
$env:TMP = $temp
$env:JARVIS_VOICE_REFERENCE_ROOT = "$root\voices\chatterbox\references"

$python = "$service\.venv\Scripts\python.exe"
$out = "$service\logs\tts-server.out.log"
$err = "$service\logs\tts-server.err.log"

Start-Process `
  -FilePath $python `
  -ArgumentList "-m", "uvicorn", "jarvis_tts_server:app", "--host", "0.0.0.0", "--port", "11550" `
  -WorkingDirectory $service `
  -WindowStyle Hidden `
  -RedirectStandardOutput $out `
  -RedirectStandardError $err
