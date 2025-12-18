Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Personal AI Backend Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "$PSScriptRoot\backend"

if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Path: $PWD\venv\Scripts\python.exe" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "[INFO] Starting Backend API..." -ForegroundColor Green
Write-Host "[INFO] Backend URL: http://localhost:8000" -ForegroundColor Yellow
Write-Host "[INFO] API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press CTRL+C to stop" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

& "venv\Scripts\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
