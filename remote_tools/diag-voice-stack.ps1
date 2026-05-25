$ErrorActionPreference = "Continue"

Write-Host "--- processes ---"
Get-Process |
  Where-Object { $_.ProcessName -match "python|ollama|whisper|jarvis|uvicorn|piper" } |
  Select-Object Id, ProcessName, CPU, Path |
  Format-Table -AutoSize

Write-Host "--- ports ---"
netstat -ano | findstr ":11550 :11551 :11552 :11434"

Write-Host "--- tools ---"
Get-Command git, cmake, ninja, cl, msbuild, python, py, curl, winget -ErrorAction SilentlyContinue |
  Select-Object Name, Source |
  Format-Table -AutoSize

Write-Host "--- x drive ---"
Get-ChildItem X:\Jarvis -Force |
  Select-Object Mode, Length, LastWriteTime, Name |
  Format-Table -AutoSize
