Stop-Process -Id 19340 -Force -ErrorAction SilentlyContinue
Stop-Process -Id 19636 -Force -ErrorAction SilentlyContinue
Write-Host "killed orphans 3"
