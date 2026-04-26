@echo off
color 0A
echo ========================================================
echo    RurTech.ai CDSCO Regulatory Platform (Govt Release)
echo ========================================================
echo.
echo [1/3] Verifying and installing required AI dependencies...
pip install -r requirements.txt -q
echo.
echo [2/3] Booting RurTech.ai Intelligence Core...
start "RurTech Core Server" cmd /c "uvicorn regulatory_api.main:app --host 0.0.0.0 --port 8080"
echo.
echo [3/3] Waiting for AI engine to stabilize...
timeout /t 4 /nobreak >nul
echo.
echo ========================================================
echo   SYSTEM SECURE AND ONLINE. 
echo   Opening CDSCO Dashboard in your default browser...
echo ========================================================
start http://localhost:8080
