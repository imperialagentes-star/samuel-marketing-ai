@echo off
title Samuel Marketing AI
chcp 65001 >nul
cd /d D:\Samuel-Marketing-AI

echo.
echo  ==========================================
echo    Samuel Marketing AI -- Iniciando...
echo  ==========================================
echo.

echo [1/2] Instalando dependencias...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

echo [2/2] Arrancando servidor...
echo.
echo  Dashboard: http://localhost:8090
echo  Presiona Ctrl+C para detener el sistema.
echo.

timeout /t 2 /nobreak >nul
start "" "http://localhost:8090"

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8090 --reload

pause
