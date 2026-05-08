@echo off
echo ========================================
echo  REINICIANDO SERVIDOR KALIN
echo ========================================
echo.

REM Matar procesos Python existentes
echo [1/3] Deteniendo servidores existentes...
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo     ✓ Servidores detenidos
) else (
    echo     ℹ No hay servidores en ejecución
)
timeout /t 2 /nobreak >nul

echo.
echo [2/3] Limpiando cache de Python...
if exist __pycache__ rmdir /s /q __pycache__
if exist agent\__pycache__ rmdir /s /q agent\__pycache__
if exist agent\core\__pycache__ rmdir /s /q agent\core\__pycache__
if exist agent\actions\__pycache__ rmdir /s /q agent\actions\__pycache__
if exist agent\actions\tools\__pycache__ rmdir /s /q agent\actions\tools\__pycache__
echo     ✓ Cache limpiado

echo.
echo [3/3] Iniciando servidor web...
echo     → Abre tu navegador en: http://127.0.0.1:5000
echo     → Presiona Ctrl+C para detener
echo.
echo ========================================
echo  SERVIDOR INICIADO
echo ========================================
echo.

python web.py

pause
