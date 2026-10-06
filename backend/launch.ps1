Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoProfile','-File','e:\CodeBuddy\VeriCart AI\backend\run_backend.ps1') -RedirectStandardOutput 'e:\CodeBuddy\VeriCart AI\backend\backend_run3.log' -RedirectStandardError 'e:\CodeBuddy\VeriCart AI\backend\backend_run3.err' -NoNewWindow -PassThru
Write-Host "launched"
