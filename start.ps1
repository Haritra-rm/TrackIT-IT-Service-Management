# TrackIT - PowerShell Startup Launcher
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " Starting TrackIT — Smart IT Service & Issue Management Platform" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$root = $PSScriptRoot
Set-Location $root

Write-Host "`n[1/3] Starting Backend API (FastAPI + Uvicorn on http://127.0.0.1:8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root'; .\venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload"

Start-Sleep -Seconds 2

Write-Host "[2/3] Starting Frontend Web App (Vite + React on http://127.0.0.1:5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\frontend'; node node_modules\vite\bin\vite.js --host 127.0.0.1 --port 5173"

Start-Sleep -Seconds 3

Write-Host "[3/3] Opening TrackIT in your web browser..." -ForegroundColor Green
Start-Process "http://127.0.0.1:5173"

Write-Host "`n======================================================================" -ForegroundColor Green
Write-Host " TrackIT is active and running!" -ForegroundColor Green
Write-Host " - Web Application:  http://127.0.0.1:5173" -ForegroundColor White
Write-Host " - Backend Swagger:  http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host " - Interactive ReDoc: http://127.0.0.1:8000/redoc" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Green
