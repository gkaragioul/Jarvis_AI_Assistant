$ErrorActionPreference = "Stop"

$name = "Jarvis PC Voice Server 11551"
if (-not (Get-NetFirewallRule -DisplayName $name -ErrorAction SilentlyContinue)) {
  New-NetFirewallRule `
    -DisplayName $name `
    -Direction Inbound `
    -Action Allow `
    -Protocol TCP `
    -LocalPort 11551 | Out-Null
}

netstat -ano | Select-String ":11551"
Get-NetFirewallRule -DisplayName $name | Get-NetFirewallPortFilter | Select-Object Protocol, LocalPort
