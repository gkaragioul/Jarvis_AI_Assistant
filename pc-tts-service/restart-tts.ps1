$ErrorActionPreference = "SilentlyContinue"

Get-CimInstance Win32_Process |
  Where-Object { $_.Name -like "python*.exe" -and ($_.CommandLine -like "*X:\Jarvis\tts-service\jarvis_tts_server.py*" -or $_.CommandLine -like "*jarvis_tts_server:app*") } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Stop-ScheduledTask -TaskName "Jarvis Remote TTS Server"
Start-Sleep -Seconds 2
Start-ScheduledTask -TaskName "Jarvis Remote TTS Server"
Start-Sleep -Seconds 5
Invoke-RestMethod "http://127.0.0.1:11550/health" | ConvertTo-Json -Compress
