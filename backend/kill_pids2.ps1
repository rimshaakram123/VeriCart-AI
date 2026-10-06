Stop-Process -Id 19708 -Force -ErrorAction SilentlyContinue
Stop-Process -Id 3152 -Force -ErrorAction SilentlyContinue
Write-Host "killed orphans 2"
