@echo off
echo Starting CDSCO AI Regulatory Backend...
cd regulatory_api
start "CDSCO Backend" cmd /c "python main.py"

echo.
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo Starting Frontend Server...
cd ..\frontend
start "CDSCO Frontend" cmd /c "python -m http.server 3000"

echo.
echo ===================================================
echo CDSCO AI Environment is RUNNING!
echo.
echo Backend API: http://localhost:8080
echo Frontend Dashboard: http://localhost:3000
echo.
echo Opening Dashboard in your browser...
echo ===================================================

start http://localhost:3000
