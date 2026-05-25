$ErrorActionPreference = "Stop"

$name = "Jarvis Remote TTS 11550"
if (-not (Get-NetFirewallRule -DisplayName $name -ErrorAction SilentlyContinue)) {
  New-NetFirewallRule `
    -DisplayName $name `
    -Direction Inbound `
    -Action Allow `
    -Protocol TCP `
    -LocalPort 11550 | Out-Null
}

netstat -ano | Select-String ":11550"
Get-NetFirewallRule -DisplayName $name | Get-NetFirewallPortFilter | Select-Object Protocol,LocalPort
