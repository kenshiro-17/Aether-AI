@echo off
title AETHER - Cleanup Script
color 0C

echo ================================================
echo   AETHER EMERGENCY CLEANUP
echo ================================================
echo.
echo   This script will forcefully terminate all
echo   AETHER processes and free RAM/VRAM.
echo.
echo ================================================
echo.

echo [CLEANUP] Stopping Electron...
taskkill /IM electron.exe /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq AETHER - Electron*" /F >nul 2>&1

echo [CLEANUP] Stopping Vite Dev Server (port 5173)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo [CLEANUP] Stopping Backend API (port 8000)...
taskkill /FI "WINDOWTITLE eq AETHER - Backend API*" /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo [CLEANUP] Stopping LLM Server (port 8081 - freeing VRAM)...
taskkill /IM llama-server.exe /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq AETHER - Main Brain*" /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8081 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo [CLEANUP] Stopping Vision Cortex (port 8082 if running)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8082 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo ================================================
echo   CLEANUP COMPLETE
echo ================================================
echo.
echo   All AETHER processes have been terminated.
echo   RAM and VRAM should now be freed.
echo.
echo   You can verify by checking Task Manager.
echo.
pause
