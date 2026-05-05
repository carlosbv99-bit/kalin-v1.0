@echo off
echo ========================================
echo BACKUP VERSIONADO EN GITHUB - KALIN
echo ========================================
echo.

REM Verificar si Git está instalado
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git no está instalado o no está en PATH
    echo Descarga Git desde: https://git-scm.com/downloads
    pause
    exit /b 1
)

echo [1/7] Verificando repositorio Git...
if not exist .git (
    echo Inicializando repositorio Git...
    git init
    echo ✅ Repositorio inicializado
) else (
    echo ✅ Repositorio Git existente detectado
)
echo.

echo [2/7] Configurando usuario Git...
git config user.name "Kalin Backup" 2>nul
git config user.email "kalin@backup.local" 2>nul
echo ✅ Usuario configurado
echo.

echo [3/7] Verificando archivo .gitignore...
if not exist .gitignore (
    echo Creando .gitignore...
    (
        echo # Python
        echo __pycache__/
        echo *.py[cod]
        echo *$py.class
        echo *.so
        echo .Python
        echo build/
        echo develop-eggs/
        echo dist/
        echo downloads/
        echo eggs/
        echo .eggs/
        echo lib/
        echo lib64/
        echo parts/
        echo sdist/
        echo var/
        echo wheels/
        echo *.egg-info/
        echo .installed.cfg
        echo *.egg
        echo.
        echo # Virtual Environment
        echo venv/
        echo ENV/
        echo env/
        echo .venv/
        echo.
        echo # IDE
        echo .idea/
        echo .vscode/
        echo *.swp
        echo *.swo
        echo *~
        echo.
        echo # Logs
        echo logs/
        echo *.log
        echo.
        echo # Cache
        echo cache/
        echo.
        echo # Sessions
        echo sessions/
        echo.
        echo # Environment variables
        echo .env
        echo.
        echo # OS
        echo .DS_Store
        echo Thumbs.db
        echo.
        echo # Agent state
        echo .agent_state.json
        echo.
        echo # Gradle (Android)
        echo .gradle/
        echo gradle-app.setting
        echo !gradle-wrapper.jar
        echo.
        echo # Local properties
        echo local.properties
    ) > .gitignore
    echo ✅ .gitignore creado
) else (
    echo ✅ .gitignore existente
)
echo.

echo [4/7] Agregando archivos al staging...
git add .
echo ✅ Archivos agregados
echo.

echo [5/7] Creando commit...
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set YEAR=%datetime:~0,4%
set MONTH=%datetime:~4,2%
set DAY=%datetime:~6,2%
set HOUR=%datetime:~8,2%
set MINUTE=%datetime:~10,2%

git commit -m "🔧 Reparaciones de tests y mejoras del sistema - %DAY%/%MONTH%/%YEAR% %HOUR%:%MINUTE%

Reparaciones realizadas:
- ✅ requirements.txt: Agregadas dependencias Flask y flask-cors
- ✅ test_funcional.py: Corregido test del Orchestrator (jsonify + session_id)
- ✅ agent/core/retry_engine.py: Corregido método _heuristic
- ✅ agent/core/cache.py: Corregida llamada a load_from_disk()
- ✅ test_endpoints.py: Agregada validación de servidor

Nuevos archivos creados:
- 📝 run_all_tests.py: Script de ejecución automática de tests
- 📝 diagnose_imports.py: Diagnóstico de imports
- 📝 verify_repairs.py: Verificación de reparaciones aplicadas
- 📝 run_tests.bat: Script batch para ejecutar tests
- 📝 run_tests.ps1: Script PowerShell para ejecutar tests
- 📝 GUIA_TESTS.md: Guía completa de ejecución de tests
- 📝 REPARACIONES_TESTS.md: Documentación de reparaciones

Estado: Todos los tests reparados y listos para ejecutar"

if %ERRORLEVEL% EQU 0 (
    echo ✅ Commit creado exitosamente
) else (
    echo ⚠️ No hay cambios para commitear o error en commit
)
echo.

echo [6/7] Creando tag de versión...
set VERSION_TAG=v1.0.0-tests-fixed-%YEAR%%MONTH%%DAY%-%HOUR%%MINUTE%
git tag -a %VERSION_TAG% -m "Versión con todos los tests reparados - %DAY%/%MONTH%/%YEAR% %HOUR%:%MINUTE%"
echo ✅ Tag creado: %VERSION_TAG%
echo.

echo [7/7] Verificando remoto GitHub...
git remote -v > remotes.txt 2>&1
findstr "github.com" remotes.txt >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Remoto GitHub detectado
    echo.
    echo ¿Deseas hacer push a GitHub? (S/N)
    set /p PUSH_CONFIRM=
    if /i "%PUSH_CONFIRM%"=="S" (
        echo Haciendo push a GitHub...
        git push origin main --tags
        if %ERRORLEVEL% EQU 0 (
            echo ✅ Push exitoso
        ) else (
            echo ⚠️ Error en push. Verifica tu conexión y credenciales
        )
    ) else (
        echo Push omitido
    )
) else (
    echo ⚠️ No se detectó remoto GitHub configurado
    echo.
    echo Para agregar un remoto GitHub:
    echo   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
    echo   git push -u origin main --tags
)
del remotes.txt 2>nul
echo.

echo ========================================
echo RESUMEN DEL BACKUP
echo ========================================
echo.
echo 📦 Estado del repositorio:
git log --oneline -5
echo.
echo 🏷️  Tags disponibles:
git tag -l
echo.
echo 📊 Estadísticas:
git status
echo.
echo ========================================
echo ✅ BACKUP COMPLETADO
echo ========================================
echo.
echo Próximos pasos:
echo 1. Si tienes un repo en GitHub, ejecuta:
echo    git remote add origin https://github.com/USUARIO/REPO.git
echo    git push -u origin main --tags
echo.
echo 2. Para ver el historial:
echo    git log --oneline
echo.
echo 3. Para ver tags:
echo    git tag -l
echo.
pause
