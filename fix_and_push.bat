@echo off
echo ========================================
echo CORREGIR REMOTO Y SUBIR A GITHUB
echo ========================================
echo.

echo [PASO 1] Verificando remoto actual...
git remote -v
echo.

echo [PASO 2] Corrigiendo URL del remoto...
git remote set-url origin https://github.com/carlosbv99-bit/kalin-v1.0.git
echo ✅ URL corregida a: https://github.com/carlosbv99-bit/kalin-v1.0.git
echo.

echo [PASO 3] Verificando nueva URL...
git remote get-url origin
echo.

echo [PASO 4] Agregando todos los archivos...
git add .
echo ✅ Archivos agregados
echo.

echo [PASO 5] Creando commit...
git commit -m "Backup completo: tests reparados, scripts y documentacion"
echo.

if %ERRORLEVEL% EQU 0 (
    echo ✅ Commit creado exitosamente
    echo.
    
    echo [PASO 6] Subiendo a GitHub...
    git push -u origin main --tags
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ========================================
        echo ✅ EXITO - PUSH COMPLETADO
        echo ========================================
        echo.
        echo Tu repositorio esta en:
        echo https://github.com/carlosbv99-bit/kalin-v1.0
        echo.
        echo Verifica que todos los archivos esten subidos.
        echo.
    ) else (
        echo.
        echo ⚠️ Error en el push
        echo.
        echo Posibles causas:
        echo 1. No tienes acceso al repositorio
        echo 2. El repositorio no existe
        echo 3. Problemas de autenticacion
        echo.
        echo Verifica que el repositorio exista en:
        echo https://github.com/carlosbv99-bit/kalin-v1.0
        echo.
    )
) else (
    echo ℹ️ No hay cambios para commitear o error
    echo.
    echo Intentando push directo...
    git push -u origin main --tags
)

echo.
pause
