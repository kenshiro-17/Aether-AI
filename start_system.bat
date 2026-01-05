@echo off
title AETHER v1.4 - System Launcher
color 0B

echo ================================================
echo   AETHER v1.4 SYSTEM LAUNCHER
echo ================================================
echo.
echo   Press Ctrl+C or close this window to stop
echo   ALL AETHER services and free RAM/VRAM.
echo.
echo ================================================
echo.

set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend"
set "MODEL_PATH=%PROJECT_ROOT%models\Llama-3.2-3B-Instruct-Q4_K_M.gguf"

:: Store PIDs of launched processes for cleanup
set "LLM_PID="
set "BACKEND_PID="
set "VITE_PID="
set "ELECTRON_PID="

echo [1/4] Checking ports...
:: Kill anything on port 8000 (Backend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing process %%a on port 8000...
    taskkill /PID %%a /F >nul 2>&1
)
:: Kill anything on port 5173 (Frontend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    echo Killing process %%a on port 5173...
    taskkill /PID %%a /F >nul 2>&1
)

echo [1.5/4] Starting Main Brain (LLM Server)...
cd /d "%BACKEND_DIR%"
:: Context set to 16384 (16K) - Safe for Vulkan/AMD GPUs
:: Optimization: Flash Attention (-fa), Batch 2048 (-b 2048), Threads 8 (-t 8), Max GPU Layers (-ngl 999)
start "AETHER - Main Brain" /B cmd /c "bin\llama-server.exe -m "%MODEL_PATH%" -c 8192 -b 2048 --port 8081 --host 0.0.0.0 -ngl 999 -fa -t 8"
echo Started. Waiting 5 seconds...

echo.
echo [1.5/4] Vision Cortex DISABLED for Speed...
:: set "VISION_MODEL=models\llava-phi-3-mini-int4.gguf"
:: set "VISION_PROJ=models\llava-phi-3-mini-mmproj-f16.gguf"
:: start "AETHER - Vision Cortex" /B cmd /c "bin\llama-server.exe -m "%VISION_MODEL%" --mmproj "%VISION_PROJ%" -c 1024 --port 8083 --host 0.0.0.0 -ngl 30"
:: echo Started Vision Cortex.
timeout /t 1 /nobreak >nul

echo.
echo [2/4] Starting Backend API...
if exist "%BACKEND_DIR%\venv\Scripts\activate.bat" (
    start "AETHER - Backend API" cmd /c "cd /d %BACKEND_DIR% && call venv\Scripts\activate.bat && python main.py"
) else (
    start "AETHER - Backend API" cmd /c "cd /d %BACKEND_DIR% && python main.py"
)
echo Started. Waiting 5 seconds...
timeout /t 5 /nobreak >nul

echo.
echo [3/4] Starting Vite Dev Server...
cd /d "%FRONTEND_DIR%"
start "AETHER - Vite" /B cmd /c "npm run dev"
echo Started. Waiting 5 seconds...
timeout /t 5 /nobreak >nul

echo.
echo [4/4] Starting Electron GUI...
start "AETHER - Electron" /B cmd /c "cd /d %FRONTEND_DIR% && electron ."
echo Started.

echo.
echo [5/5] Starting Mobile App (Expo)...
set "MOBILE_DIR=%PROJECT_ROOT%mobile\aether-mobile"
cd /d "%MOBILE_DIR%"
:: Using Tunnel (Ngrok) for reliable access outside local network
start "AETHER - Mobile" cmd /c "npx expo start --port 8082 --tunnel"
echo Started!

echo.
echo ================================================
echo   AETHER IS NOW RUNNING
echo ================================================
echo.
echo   The Electron GUI should appear shortly.
echo.
echo   IMPORTANT: To properly shutdown AETHER and
echo   free up RAM/VRAM, press Ctrl+C in this window
echo   or simply close this window.
echo.
echo   DO NOT just close the Electron window - use
echo   this launcher window to ensure full cleanup.
echo.
echo ================================================
echo.

:: Wait for user input - when this window closes, cleanup happens
:wait_loop
echo [RUNNING] Press any key to shutdown AETHER gracefully...
pause >nul

:: Call cleanup routine
call :cleanup
exit /b 0

:cleanup
echo.
echo ================================================
echo   SHUTTING DOWN AETHER - CLEANUP IN PROGRESS
echo ================================================
echo.

:: Kill processes by window title and port usage
echo [CLEANUP] Stopping Electron...
taskkill /FI "WINDOWTITLE eq AETHER - Electron*" /F >nul 2>&1
taskkill /IM electron.exe /F >nul 2>&1

echo [CLEANUP] Stopping Vite Dev Server...
taskkill /FI "WINDOWTITLE eq AETHER - Vite*" /F >nul 2>&1
:: Kill node processes on port 5173
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo [CLEANUP] Stopping Backend API...
taskkill /FI "WINDOWTITLE eq AETHER - Backend API*" /F >nul 2>&1
:: Kill python/uvicorn on port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo [CLEANUP] Stopping Mobile App...
taskkill /FI "WINDOWTITLE eq AETHER - Mobile*" /F >nul 2>&1
:: Kill expo/node processes on port 8082
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8082 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo [CLEANUP] Stopping LLM Server (freeing VRAM)...
taskkill /FI "WINDOWTITLE eq AETHER - Main Brain*" /F >nul 2>&1
taskkill /IM llama-server.exe /F >nul 2>&1
:: Kill any process on port 8081
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8081 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

:: Additional cleanup - kill any orphaned node/python processes from AETHER
echo [CLEANUP] Cleaning up orphaned processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo ================================================
echo   CLEANUP COMPLETE - RAM/VRAM FREED
echo ================================================
echo.
echo   All AETHER services have been stopped.
echo   GPU memory has been released.
echo.
timeout /t 3
exit /b 0
