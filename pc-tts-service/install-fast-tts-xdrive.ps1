$ErrorActionPreference = "Stop"

$root = "X:\Jarvis"
$service = "$root\tts-service"
$cache = "$service\cache"
$temp = "$root\temp"

New-Item -ItemType Directory -Force $cache, "$cache\uv", "$cache\pip", "$cache\huggingface", "$cache\torch", $temp | Out-Null

$env:UV_CACHE_DIR = "$cache\uv"
$env:UV_PYTHON_INSTALL_DIR = "$root\python"
$env:UV_LINK_MODE = "copy"
$env:PIP_CACHE_DIR = "$cache\pip"
$env:HF_HOME = "$cache\huggingface"
$env:TORCH_HOME = "$cache\torch"
$env:XDG_CACHE_HOME = $cache
$env:TEMP = $temp
$env:TMP = $temp

Set-Location $service
& "$root\tools\uv.exe" pip install --python "$service\.venv\Scripts\python.exe" kokoro "misaki[en]"
& "$service\.venv\Scripts\python.exe" -c "import kokoro; print('kokoro import ok')"
