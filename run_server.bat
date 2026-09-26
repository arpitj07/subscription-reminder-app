@echo off
REM Subscription & Bill Reminder - Auto-running Server
REM This script keeps the Flask app running and restarts it if it crashes

setlocal enabledelayedexpansion

cd /d "H:\claude-code\subscription-reminder-app"

echo ========================================
echo Subscription & Bill Reminder Service
echo ========================================
echo.
echo Starting Flask application...
echo.
echo The app will be available at:
echo   Local:  http://localhost:5000
echo   Mobile: Find your IP address with 'ipconfig' command
echo           Then use: http://YOUR_IP:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

:restart
echo [%date% %time%] Starting Flask app...
python app.py

REM If app stops, wait and restart
echo.
echo [%date% %time%] App stopped. Restarting in 5 seconds...
timeout /t 5 /nobreak
goto restart