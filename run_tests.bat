@echo off
echo ========================================
echo EJECUTANDO TODOS LOS TESTS DE KALIN
echo ========================================
echo.

echo [1/7] Verificando reparaciones...
python verify_repairs.py
if errorlevel 1 (
    echo ERROR: Las verificaciones fallaron
    pause
    exit /b 1
)
echo.

echo [2/7] Diagnosticando imports...
python diagnose_imports.py
if errorlevel 1 (
    echo ERROR: Los imports fallaron
    pause
    exit /b 1
)
echo.

echo [3/7] Ejecutando test_funcional.py...
python test_funcional.py
if errorlevel 1 (
    echo ADVERTENCIA: test_funcional.py tuvo errores
)
echo.

echo [4/7] Ejecutando test_llm_providers.py...
python test_llm_providers.py
if errorlevel 1 (
    echo ADVERTENCIA: test_llm_providers.py tuvo errores
)
echo.

echo [5/7] Ejecutando test_new_architecture.py...
python test_new_architecture.py
if errorlevel 1 (
    echo ADVERTENCIA: test_new_architecture.py tuvo errores
)
echo.

echo [6/7] Ejecutando test_new_components.py...
python test_new_components.py
if errorlevel 1 (
    echo ADVERTENCIA: test_new_components.py tuvo errores
)
echo.

echo [7/7] Verificando servidor para test_endpoints.py...
python -c "import requests; requests.get('http://127.0.0.1:5000/health', timeout=2)" 2>nul
if errorlevel 1 (
    echo SERVIDOR NO DISPONIBLE: Saltando test_endpoints.py
    echo Para ejecutar test_endpoints.py, primero inicia el servidor con: python run.py
) else (
    echo SERVIDOR DETECTADO: Ejecutando test_endpoints.py...
    python test_endpoints.py
)
echo.

echo ========================================
echo RESUMEN FINAL
echo ========================================
echo Todos los tests han sido ejecutados.
echo Revisa la salida arriba para ver los resultados.
echo ========================================
pause
