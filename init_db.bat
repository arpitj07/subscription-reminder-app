@echo off
REM Initialize Database Script
REM Run this once to create the database

cd /d "C:\Users\ARPIT JAIN\subscription-reminder-app"

echo Creating database...
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database created successfully!')"

echo.
echo Done! You can now run the server with:
echo   - Double-click run_server.bat
echo   - Or run: python app.py
echo.
pause