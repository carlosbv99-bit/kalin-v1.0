@echo off
echo ========================================
echo VERIFICAR Y SUBIR CAMBIOS A GITHUB
echo ========================================
echo.

echo [1/3] Verificando URL del remoto...
git remote get-url origin
echo.

echo [2/3] Agregando cambios al repositorio...
git add .
echo.

echo [3/3] Creando commit...
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set YEAR=%datetime:~0,4%
set MONTH=%datetime:~4,2%
set DAY=%datetime:~6,2%
set HOUR=%datetime:~8,2%
set MINUTE=%datetime:~10,2%

git commit -m "📦 Scripts de backup y documentación completa - %DAY%/%MONTH%/%YEAR%

Nuevos archivos:
- backup_github.bat/ps1: Scripts de backup automático
- check_remote.ps1: Verificación de configuración remota
- BACKUP_GITHUB_GUIA.md: Guía completa de GitHub
- GUIA_TESTS.md: Guía de ejecución de tests
- REPARACIONES_TESTS.md: Documentación de reparaciones
- run_tests.bat/ps1: Scripts para ejecutar tests
- verify_repairs.py: Verificación automática
- diagnose_imports.py: Diagnóstico de imports

Reparaciones incluidas:
- requirements.txt con Flask y flask-cors
- test_funcional.py corregido
- retry_engine.py corregido
- cache.py corregido
- test_endpoints.py con validación"

if %ERRORLEVEL% EQU 0 (
    echo ✅ Commit creado
    echo.
    echo [4/4] Subiendo a GitHub...
    git push origin main --tags
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ========================================
        echo ✅ PUSH EXITOSO
        echo ========================================
        echo.
        echo Tu repositorio está actualizado en:
        echo https://github.com/carlosbv99/kalin
        echo.
    ) else (
        echo.
        echo ⚠️ Error en el push. Intenta manualmente:
        echo git push origin main --tags
        echo.
    )
) else (
    echo.
    echo ℹ️ No hay cambios nuevos para commitear
    echo O ya están subidos
    echo.
)

pause
