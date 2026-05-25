$ErrorActionPreference = "Stop"

$taskName = "Jarvis Remote TTS Server"
$script = "X:\Jarvis\scripts\start-jarvis-tts-hidden.ps1"
$action = New-ScheduledTaskAction `
  -Execute "powershell.exe" `
  -Argument "-WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File `"$script`""
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -ExecutionTimeLimit (New-TimeSpan -Days 30) `
  -RestartCount 3 `
  -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask `
  -TaskName $taskName `
  -Action $action `
  -Trigger $trigger `
  -Settings $settings `
  -Force | Out-Null

Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 5
Get-ScheduledTask -TaskName $taskName | Select-Object TaskName,State
