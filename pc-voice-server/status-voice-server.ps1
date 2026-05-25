Write-Host "Processes:"
Get-Process python -ErrorAction SilentlyContinue |
  Where-Object { $_.Path -like "X:\Jarvis\*" } |
  Select-Object Id, Path, StartTime

Write-Host "`nPort:"
netstat -ano | Select-String ":11551"

Write-Host "`nHealth:"
try {
  Invoke-RestMethod "http://127.0.0.1:11551/health" | ConvertTo-Json -Depth 8
} catch {
  Write-Host $_.Exception.Message
}

Write-Host "`nErrors:"
Get-Content "X:\Jarvis\voice-server\logs\voice-server.err.log" -Tail 80 -ErrorAction SilentlyContinue
