$ErrorActionPreference = "Stop"

$root = "X:\Jarvis"
$service = "$root\voice-server"
$cache = "$service\cache"
$temp = "$root\temp"
$logs = "$service\logs"

New-Item -ItemType Directory -Force $cache, "$cache\uv", "$cache\pip", $temp, $logs | Out-Null

$env:PYTHONUNBUFFERED = "1"
$env:JARVIS_ROOT = $root
$env:JARVIS_VOICE_SERVER_ROOT = $service
$env:JARVIS_TEMP = $temp
$env:JARVIS_TOOLS = "$root\tools"
$env:JARVIS_WHISPER_ROOT = "$root\tools\whispercpp\v1.8.4"
$env:JARVIS_WHISPER_MODEL = "$service\models\ggml-small.en.bin"
$env:JARVIS_REMOTE_TTS_URL = "http://127.0.0.1:11550/synthesize"
$env:JARVIS_OLLAMA_URL = "http://127.0.0.1:11434"
$env:UV_CACHE_DIR = "$cache\uv"
$env:UV_PYTHON_INSTALL_DIR = "$root\python"
$env:UV_LINK_MODE = "copy"
$env:PIP_CACHE_DIR = "$cache\pip"
$env:TEMP = $temp
$env:TMP = $temp

$python = "$service\.venv\Scripts\python.exe"
$out = "$logs\voice-server.out.log"
$err = "$logs\voice-server.err.log"

Start-Process `
  -FilePath $python `
  -ArgumentList "-m", "uvicorn", "jarvis_voice_server:app", "--host", "0.0.0.0", "--port", "11551" `
  -WorkingDirectory $service `
  -WindowStyle Hidden `
  -RedirectStandardOutput $out `
  -RedirectStandardError $err
