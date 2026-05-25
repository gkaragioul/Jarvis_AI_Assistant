$ErrorActionPreference = "SilentlyContinue"

$uvCache = Join-Path $env:LOCALAPPDATA "uv\cache"
$uvPython = Join-Path $env:LOCALAPPDATA "uv\python"

Write-Host "Before:"
Write-Host "uv cache:" (Test-Path $uvCache)
if (Test-Path $uvCache) {
  Write-Host "uv cache MB:" ([math]::Round(((Get-ChildItem $uvCache -Recurse -Force | Measure-Object Length -Sum).Sum / 1MB), 2))
}
Write-Host "uv python:" (Test-Path $uvPython)

Remove-Item $uvCache -Recurse -Force
Remove-Item $uvPython -Recurse -Force

Write-Host "After:"
Write-Host "uv cache:" (Test-Path $uvCache)
Write-Host "uv python:" (Test-Path $uvPython)
