# Script PowerShell para backup versionado en GitHub
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BACKUP VERSIONADO EN GITHUB - KALIN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Git está instalado
try {
    $gitVersion = git --version 2>&1
    Write-Host "✅ Git detectado: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Git no está instalado" -ForegroundColor Red
    Write-Host "Descarga Git desde: https://git-scm.com/downloads" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host ""

# [1/7] Verificar repositorio
Write-Host "[1/7] Verificando repositorio Git..." -ForegroundColor Yellow
if (-not (Test-Path ".git")) {
    Write-Host "Inicializando repositorio Git..." -ForegroundColor Gray
    git init
    Write-Host "✅ Repositorio inicializado" -ForegroundColor Green
} else {
    Write-Host "✅ Repositorio Git existente detectado" -ForegroundColor Green
}
Write-Host ""

# [2/7] Configurar usuario
Write-Host "[2/7] Configurando usuario Git..." -ForegroundColor Yellow
git config user.name "Kalin Backup" 2>$null
git config user.email "kalin@backup.local" 2>$null
Write-Host "✅ Usuario configurado" -ForegroundColor Green
Write-Host ""

# [3/7] Verificar .gitignore
Write-Host "[3/7] Verificando archivo .gitignore..." -ForegroundColor Yellow
if (-not (Test-Path ".gitignore")) {
    Write-Host "Creando .gitignore..." -ForegroundColor Gray
    
@"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/
.venv/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Logs
logs/
*.log

# Cache
cache/

# Sessions
sessions/

# Environment variables
.env

# OS
.DS_Store
Thumbs.db

# Agent state
.agent_state.json

# Gradle (Android)
.gradle/
gradle-app.setting
!gradle-wrapper.jar

# Local properties
local.properties
"@ | Out-File -FilePath ".gitignore" -Encoding utf8
    
    Write-Host "✅ .gitignore creado" -ForegroundColor Green
} else {
    Write-Host "✅ .gitignore existente" -ForegroundColor Green
}
Write-Host ""

# [4/7] Agregar archivos
Write-Host "[4/7] Agregando archivos al staging..." -ForegroundColor Yellow
git add .
Write-Host "✅ Archivos agregados" -ForegroundColor Green
Write-Host ""

# [5/7] Crear commit
Write-Host "[5/7] Creando commit..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "dd/MM/yyyy HH:mm"
$commitMessage = @"
🔧 Reparaciones de tests y mejoras del sistema - $timestamp

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

Estado: Todos los tests reparados y listos para ejecutar
"@

git commit -m $commitMessage

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Commit creado exitosamente" -ForegroundColor Green
} else {
    Write-Host "⚠️ No hay cambios para commitear o error en commit" -ForegroundColor DarkYellow
}
Write-Host ""

# [6/7] Crear tag
Write-Host "[6/7] Creando tag de versión..." -ForegroundColor Yellow
$versionTag = "v1.0.0-tests-fixed-" + (Get-Date -Format "yyyyMMdd-HHmm")
git tag -a $versionTag -m "Versión con todos los tests reparados - $timestamp"
Write-Host "✅ Tag creado: $versionTag" -ForegroundColor Green
Write-Host ""

# [7/7] Verificar remoto
Write-Host "[7/7] Verificando remoto GitHub..." -ForegroundColor Yellow
$remotes = git remote -v 2>&1
if ($remotes -match "github.com") {
    Write-Host "✅ Remoto GitHub detectado" -ForegroundColor Green
    Write-Host ""
    
    $confirm = Read-Host "¿Deseas hacer push a GitHub? (S/N)"
    if ($confirm -eq "S" -or $confirm -eq "s") {
        Write-Host "Haciendo push a GitHub..." -ForegroundColor Gray
        git push origin main --tags
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Push exitoso" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Error en push. Verifica tu conexión y credenciales" -ForegroundColor DarkYellow
            Write-Host "Intentando con master..." -ForegroundColor Gray
            git push origin master --tags
        }
    } else {
        Write-Host "Push omitido" -ForegroundColor DarkGray
    }
} else {
    Write-Host "⚠️ No se detectó remoto GitHub configurado" -ForegroundColor DarkYellow
    Write-Host ""
    Write-Host "Para agregar un remoto GitHub:" -ForegroundColor Cyan
    Write-Host "  git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git" -ForegroundColor Gray
    Write-Host "  git push -u origin main --tags" -ForegroundColor Gray
}
Write-Host ""

# Resumen
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESUMEN DEL BACKUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📦 Últimos commits:" -ForegroundColor Yellow
git log --oneline -5
Write-Host ""

Write-Host "🏷️ Tags disponibles:" -ForegroundColor Yellow
git tag -l
Write-Host ""

Write-Host "📊 Estado actual:" -ForegroundColor Yellow
git status --short
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ BACKUP COMPLETADO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Próximos pasos:" -ForegroundColor Cyan
Write-Host "1. Si tienes un repo en GitHub, ejecuta:" -ForegroundColor White
Write-Host "   git remote add origin https://github.com/USUARIO/REPO.git" -ForegroundColor Gray
Write-Host "   git push -u origin main --tags" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Para ver el historial:" -ForegroundColor White
Write-Host "   git log --oneline" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Para ver tags:" -ForegroundColor White
Write-Host "   git tag -l" -ForegroundColor Gray
Write-Host ""

Read-Host "Presiona Enter para salir"
