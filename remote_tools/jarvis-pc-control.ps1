param(
  [ValidateSet("status", "start", "stop", "restart")]
  [string]$Action = "status",
  [switch]$IncludeOllama
)

$ErrorActionPreference = "Stop"
$JarvisRoot = "X:\Jarvis"
$VoiceTask = "Jarvis PC Voice Server"
$TtsTask = "Jarvis Remote TTS Server"
$Ports = @(11434, 11550, 11551)

function Test-HttpJson {
  param([string]$Url)
  try {
    return Invoke-RestMethod -Uri $Url -TimeoutSec 3
  } catch {
    return $null
  }
}

function Stop-JarvisPython {
  $targets = @(
    "$JarvisRoot\voice-server\jarvis_voice_server.py",
    "$JarvisRoot\tts-service\jarvis_tts_server.py",
    "jarvis_voice_server:app",
    "jarvis_tts_server:app"
  )
  Get-CimInstance Win32_Process | Where-Object { $_.Name -like "python*.exe" } | ForEach-Object {
    $cmd = $_.CommandLine
    if (-not $cmd) { return }
    foreach ($target in $targets) {
      if ($cmd -like "*$target*") {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        break
      }
    }
  }
}

function Start-TaskIfPresent {
  param([string]$Name)
  $task = Get-ScheduledTask -TaskName $Name -ErrorAction SilentlyContinue
  if ($task) {
    Start-ScheduledTask -TaskName $Name
    return $true
  }
  return $false
}

function Start-JarvisServices {
  if (-not (Test-Path $JarvisRoot)) {
    throw "Jarvis root is missing. This setup is hardcoded to $JarvisRoot."
  }

  if (-not (Test-HttpJson "http://127.0.0.1:11434/api/tags")) {
    $ollama = Get-Command ollama.exe -ErrorAction SilentlyContinue
    if (-not $ollama -and (Test-Path "$JarvisRoot\ollama\ollama.exe")) {
      $ollama = Get-Item "$JarvisRoot\ollama\ollama.exe"
    }
    if ($ollama) {
      $ollamaPath = if ($ollama.Source) { $ollama.Source } else { $ollama.FullName }
      Start-Process -FilePath $ollamaPath -ArgumentList "serve" -WindowStyle Hidden -WorkingDirectory $JarvisRoot
    }
  }

  if (-not (Start-TaskIfPresent $TtsTask)) {
    & "$JarvisRoot\tts-service\start-jarvis-tts-hidden.ps1"
  }
  Start-Sleep -Seconds 2
  if (-not (Start-TaskIfPresent $VoiceTask)) {
    & "$JarvisRoot\voice-server\start-voice-server-hidden.ps1"
  }
}

function Stop-JarvisServices {
  Stop-JarvisPython
  if ($IncludeOllama) {
    Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
  }
}

function Get-JarvisStatus {
  $listening = foreach ($port in $Ports) {
    $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    [pscustomobject]@{
      port = $port
      listening = [bool]$conn
      pid = if ($conn) { $conn.OwningProcess } else { $null }
    }
  }

  [pscustomobject]@{
    root = $JarvisRoot
    tasks = @(
      Get-ScheduledTask -TaskName $TtsTask -ErrorAction SilentlyContinue | Select-Object TaskName,State
      Get-ScheduledTask -TaskName $VoiceTask -ErrorAction SilentlyContinue | Select-Object TaskName,State
    )
    ports = $listening
    ollama = Test-HttpJson "http://127.0.0.1:11434/api/tags"
    tts = Test-HttpJson "http://127.0.0.1:11550/health"
    voice = Test-HttpJson "http://127.0.0.1:11551/health"
  }
}

switch ($Action) {
  "start" { Start-JarvisServices; Start-Sleep -Seconds 2; Get-JarvisStatus | ConvertTo-Json -Depth 8 }
  "stop" { Stop-JarvisServices; Start-Sleep -Seconds 1; Get-JarvisStatus | ConvertTo-Json -Depth 8 }
  "restart" { Stop-JarvisServices; Start-Sleep -Seconds 2; Start-JarvisServices; Start-Sleep -Seconds 2; Get-JarvisStatus | ConvertTo-Json -Depth 8 }
  default { Get-JarvisStatus | ConvertTo-Json -Depth 8 }
}
