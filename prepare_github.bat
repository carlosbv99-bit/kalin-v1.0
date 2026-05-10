@echo off
REM ============================================================================
REM Script Batch para preparar Kalin v3.0 para GitHub (Windows)
REM ============================================================================

echo.
echo ============================================================================
echo KALIN v3.0 - PREPARACION PARA GITHUB
echo ============================================================================
echo.

REM Verificar que Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en PATH
    pause
    exit /b 1
)

echo [1/5] Verificando directorio del proyecto...
if exist "main.py" (
    echo OK: Directorio del proyecto verificado
) else (
    echo ERROR: No se encontro main.py
    pause
    exit /b 1
)

echo.
echo [2/5] Verificando archivos sensibles...
if exist ".env" (
    echo ADVERTENCIA: El archivo .env existe (no debe subirse a GitHub)
) else (
    echo OK: No se encontro archivo .env
)

echo.
echo [3/5] Ejecutando limpieza automatica...
python clean_for_github.py
if errorlevel 1 (
    echo ADVERTENCIA: La limpieza encontro problemas
) else (
    echo OK: Limpieza completada
)

echo.
echo [4/5] Ejecutando verificacion avanzada...
if exist "verify_github_ready.py" (
    python verify_github_ready.py
    if errorlevel 1 (
        echo ADVERTENCIA: La verificacion encontro problemas
        echo Revisa la salida anterior para mas detalles
    ) else (
        echo OK: Verificacion completada exitosamente
    )
) else (
    echo ADVERTENCIA: No se encontro verify_github_ready.py
)

echo.
echo [5/5] Estado del repositorio Git...
git status >nul 2>&1
if errorlevel 1 (
    echo ADVERTENCIA: Git no esta instalado o no es un repositorio Git
    echo Para inicializar: git init
) else (
    echo Estado actual del repositorio:
    git status --short
)

echo.
echo ============================================================================
echo RESUMEN FINAL
echo ============================================================================
echo.
echo Tu proyecto ha sido verificado y limpiado.
echo.
echo Proximos pasos:
echo   1. Revisa el estado: git status
echo   2. Agrega archivos: git add .
echo   3. Crea commit: git commit -m "Clean project structure"
echo   4. Sube a GitHub: git push origin main
echo.
echo IMPORTANTE: Nunca subas el archivo .env a GitHub
echo.
echo ============================================================================

pause
