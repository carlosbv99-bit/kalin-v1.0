@echo off
title Kalin AI - Iniciando...
echo ========================================
echo   KALIN AI - ASISTENTE DE PROGRAMACION
echo ========================================
echo.
echo Verificando instalacion...
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    echo.
    echo Por favor instala Python desde:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Verificar si existe el entorno virtual
if exist ".venv\Scripts\activate.bat" (
    echo [OK] Entorno virtual encontrado
    echo Activando entorno virtual...
    call .venv\Scripts\activate.bat
) else (
    echo [INFO] No se encontro entorno virtual
    echo Usando Python del sistema...
)

echo.
echo ========================================
echo   INICIANDO KALIN...
echo ========================================
echo.
echo Abre tu navegador en: http://localhost:5000
echo.
echo Presiona Ctrl+C para detener Kalin
echo.
echo ========================================
echo.

REM Iniciar Kalin
python run.py

pause
