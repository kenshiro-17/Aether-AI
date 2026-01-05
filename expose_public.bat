@echo off
echo ===================================================
echo   AETHER PUBLIC UPLINK (localtunnel)
echo ===================================================
echo.
echo [1/2] Exposing Backend (Port 8000)...
start "AETHER - API Tunnel" cmd /k "lt --port 8000 --subdomain aether-api-%RANDOM%"

echo [2/2] Exposing Frontend (Port 8082)...
start "AETHER - UI Tunnel" cmd /k "lt --port 8082 --subdomain aether-ui-%RANDOM%"

echo.
echo ===================================================
echo   UPLINK ESTABLISHED
echo ===================================================
echo Check the new terminal windows for your PUBLIC URLs.
echo.
echo NOTE: You must update the Frontend to point to the new API URL!
echo (This requires rebuilding the frontend with VITE_API_URL set)
echo.
pause
