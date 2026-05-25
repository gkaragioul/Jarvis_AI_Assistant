$ErrorActionPreference = "Stop"

$root = "X:\Jarvis"
$service = "$root\tts-service"
$cache = "$service\cache"
$temp = "$root\temp"

New-Item -ItemType Directory -Force `
  "$service\logs", `
  $cache, `
  "$cache\uv", `
  "$cache\pip", `
  "$cache\huggingface", `
  "$cache\torch", `
  "$cache\transformers", `
  "$cache\matplotlib", `
  "$cache\numba", `
  $temp, `
  "$root\home", `
  "$root\localappdata", `
  "$root\appdata", `
  "$root\programdata" | Out-Null

$env:JARVIS_ROOT = $root
$env:HOME = "$root\home"
$env:USERPROFILE = "$root\home"
$env:LOCALAPPDATA = "$root\localappdata"
$env:APPDATA = "$root\appdata"
$env:PROGRAMDATA = "$root\programdata"
$env:PYTHONUNBUFFERED = "1"
$env:UV_CACHE_DIR = "$cache\uv"
$env:UV_PYTHON_INSTALL_DIR = "$root\python"
$env:UV_LINK_MODE = "copy"
$env:PIP_CACHE_DIR = "$cache\pip"
$env:HF_HOME = "$cache\huggingface"
$env:HF_HUB_CACHE = "$cache\huggingface\hub"
$env:TRANSFORMERS_CACHE = "$cache\transformers"
$env:TORCH_HOME = "$cache\torch"
$env:XDG_CACHE_HOME = $cache
$env:MPLCONFIGDIR = "$cache\matplotlib"
$env:NUMBA_CACHE_DIR = "$cache\numba"
$env:TEMP = $temp
$env:TMP = $temp
$env:JARVIS_VOICE_REFERENCE_ROOT = "$root\voices\chatterbox\references"
$env:JARVIS_TTS_DEVICE = "cuda"

Get-CimInstance Win32_Process -Filter "name = 'python.exe'" |
  Where-Object { $_.CommandLine -like "*jarvis_tts_server:app*" } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

$python = "$root\tts-gpu\.venv\Scripts\python.exe"
$out = "$service\logs\tts-server.out.log"
$err = "$service\logs\tts-server.err.log"

Start-Process `
  -FilePath $python `
  -ArgumentList "-m", "uvicorn", "jarvis_tts_server:app", "--host", "0.0.0.0", "--port", "11550" `
  -WorkingDirectory $service `
  -WindowStyle Hidden `
  -RedirectStandardOutput $out `
  -RedirectStandardError $err

Start-Process `
  -FilePath "powershell.exe" `
  -ArgumentList "-WindowStyle", "Hidden", "-NoProfile", "-Command", "Start-Sleep -Seconds 4; try { Invoke-RestMethod -Method Post -Uri http://127.0.0.1:11550/prewarm | Out-Null } catch {}" `
  -WindowStyle Hidden
