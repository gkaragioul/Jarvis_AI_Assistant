$ErrorActionPreference = "SilentlyContinue"

Get-Process python |
  Where-Object { $_.Path -like "X:\Jarvis\voice-server\*" } |
  Stop-Process -Force

Stop-ScheduledTask -TaskName "Jarvis PC Voice Server"
Start-Sleep -Seconds 2
Start-ScheduledTask -TaskName "Jarvis PC Voice Server"
Start-Sleep -Seconds 5

Invoke-RestMethod "http://127.0.0.1:11551/health" | ConvertTo-Json -Depth 8
Get-ChildItem "X:\Jarvis\voice-server\models" | Select-Object Name, Length | Format-Table -AutoSize
