@echo off
REM YesChef Server Quick Start
REM Double-click this file to start the server!

cd /d "D:\Mik\Downloads\Me Hungie"
echo.
echo ========================================
echo    YesChef Server Starting...
echo ========================================
echo.

REM Activate venv and start server
call venv\Scripts\activate.bat
echo Virtual environment activated!
echo.
echo Starting Flask server...
echo Server will be at: http://localhost:5000
echo Press Ctrl+C to stop
echo.

python hungie_server.py

REM Keep window open if server crashes
echo.
echo Server stopped.
pause
