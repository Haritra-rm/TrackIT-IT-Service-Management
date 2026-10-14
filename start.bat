@echo off
title TrackIT - Smart IT Service & Issue Management Platform
echo ======================================================================
echo Starting TrackIT Full-Stack Platform
echo ======================================================================

cd /d "%~dp0"

echo [1/3] Starting Backend Server (FastAPI + Uvicorn on http://127.0.0.1:8000)...
start "TrackIT Backend (FastAPI)" cmd /k ".\venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload"

timeout /t 2 /nobreak >nul

echo [2/3] Starting Frontend Server (Vite + React on http://127.0.0.1:5173)...
cd /d "%~dp0frontend"
start "TrackIT Frontend (Vite)" cmd /k "node node_modules\vite\bin\vite.js --host 127.0.0.1 --port 5173"

timeout /t 3 /nobreak >nul

echo [3/3] Opening TrackIT in your web browser...
start http://127.0.0.1:5173

echo.
echo ======================================================================
echo TrackIT is now running!
echo - Web Application: http://127.0.0.1:5173
echo - Backend API Docs: http://127.0.0.1:8000/docs
echo ======================================================================
echo Keep the terminal windows open while testing. Press any key to exit this launcher.
pause >nul
