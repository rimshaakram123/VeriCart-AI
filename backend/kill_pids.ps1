Stop-Process -Id 7832 -Force -ErrorAction SilentlyContinue
Stop-Process -Id 11968 -Force -ErrorAction SilentlyContinue
Write-Host "killed orphans"
