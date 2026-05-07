@echo off
echo ================================================================================
echo  KALIN v3.0 - PREPARACION Y TESTING
echo ================================================================================
echo.

echo [1/3] Limpiando proyecto...
python prepare_for_testing.py
if errorlevel 1 (
    echo ERROR en limpieza
    pause
    exit /b 1
)
echo.

echo [2/3] Ejecutando tests...
python test_suite_completa.py
if errorlevel 1 (
    echo.
    echo ADVERTENCIA: Algunos tests fallaron
    echo Revisa los errores arriba antes de continuar
    pause
    choice /M "Deseas continuar de todas formas"
    if errorlevel 2 exit /b 1
)
echo.

echo [3/3] Iniciando servidor...
echo.
echo Accede a http://localhost:5000
echo Presiona Ctrl+C para detener el servidor
echo.
python run.py
