$ErrorActionPreference = "SilentlyContinue"

$taskName = "Jarvis Remote TTS Server"
$service = "X:\Jarvis\tts-service"

Stop-ScheduledTask -TaskName $taskName
Get-Process python | Where-Object { $_.Path -like "X:\Jarvis\*" } | Stop-Process -Force
Start-Sleep -Seconds 2

Set-Location $service
& "X:\Jarvis\tools\uv.exe" pip uninstall --python "$service\.venv\Scripts\python.exe" `
  kokoro misaki en-core-web-sm spacy thinc blis cymem murmurhash preshed weasel `
  cloudpathlib confection wasabi typer-slim smart-open catalogue srsly -y

Remove-Item "X:\Jarvis\tts-service\cache\huggingface\hub\models--hexgrad--Kokoro-82M" -Recurse -Force
Remove-Item "X:\Jarvis\tts-service\cache\huggingface\hub\.locks\models--hexgrad--Kokoro-82M" -Recurse -Force
Remove-Item "X:\Jarvis\tts-service\cache\audio\*" -Force

Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 5

Invoke-RestMethod "http://127.0.0.1:11550/health" | ConvertTo-Json -Compress
