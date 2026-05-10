# Script automatico para preparar Kalin v3.0 para GitHub

Write-Host "`n=== PREPARACION AUTOMATICA PARA GITHUB ===" -ForegroundColor Cyan

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# PASO 1: Verificar archivos importantes
Write-Host "`n[1/6] Verificando proyecto..." -ForegroundColor Yellow

if (Test-Path "$projectRoot\main.py") {
    Write-Host "  OK: main.py encontrado" -ForegroundColor Green
} else {
    Write-Host "  ERROR: main.py no encontrado" -ForegroundColor Red
}

# PASO 2: Verificar .env
Write-Host "`n[2/6] Verificando archivos sensibles..." -ForegroundColor Yellow

if (Test-Path "$projectRoot\.env") {
    Write-Host "  INFO: .env encontrado (protegido por .gitignore)" -ForegroundColor White
    
    # Verificar si esta en Git
    git ls-files --error-unmatch .env 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ALERTA: .env esta en Git, eliminando..." -ForegroundColor Yellow
        git rm --cached .env 2>&1 | Out-Null
        Write-Host "  OK: .env eliminado de Git" -ForegroundColor Green
    } else {
        Write-Host "  OK: .env NO esta en Git" -ForegroundColor Green
    }
} else {
    Write-Host "  OK: No hay archivo .env" -ForegroundColor Green
}

# PASO 3: Limpiar temporales
Write-Host "`n[3/6] Limpiando archivos temporales..." -ForegroundColor Yellow

$deletedCount = 0

# Eliminar directorios __pycache__
Get-ChildItem -Path $projectRoot -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    $deletedCount++
}

# Eliminar archivos .pyc
Get-ChildItem -Path $projectRoot -Recurse -File -Filter "*.pyc" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
    $deletedCount++
}

# Eliminar archivos .log
Get-ChildItem -Path $projectRoot -Recurse -File -Filter "*.log" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
    $deletedCount++
}

# Eliminar archivos de estado en raiz
if (Test-Path "$projectRoot\.agent_state.json") {
    Remove-Item "$projectRoot\.agent_state.json" -Force -ErrorAction SilentlyContinue
    $deletedCount++
}

if (Test-Path "$projectRoot\health_status.json") {
    Remove-Item "$projectRoot\health_status.json" -Force -ErrorAction SilentlyContinue
    $deletedCount++
}

Write-Host "  OK: Limpieza completada ($deletedCount archivos)" -ForegroundColor Green

# PASO 4: Verificar .gitignore
Write-Host "`n[4/6] Verificando .gitignore..." -ForegroundColor Yellow

if (Test-Path "$projectRoot\.gitignore") {
    Write-Host "  OK: .gitignore existe" -ForegroundColor Green
} else {
    Write-Host "  ERROR: .gitignore no encontrado" -ForegroundColor Red
}

# PASO 5: Verificar Git
Write-Host "`n[5/6] Verificando Git..." -ForegroundColor Yellow

git rev-parse --git-dir 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: Repositorio Git detectado" -ForegroundColor Green
    
    $status = git status --short 2>&1
    if ($status -and $status.Count -gt 0) {
        Write-Host "  INFO: Hay cambios pendientes" -ForegroundColor White
    } else {
        Write-Host "  OK: No hay cambios pendientes" -ForegroundColor Green
    }
} else {
    Write-Host "  WARNING: Git no inicializado" -ForegroundColor Yellow
}

# PASO 6: Reporte final
Write-Host "`n[6/6] Generando reporte..." -ForegroundColor Yellow

$report = @"

======================================================================
REPORTE DE PREPARACION PARA GITHUB
======================================================================

PROYECTO LISTO PARA SUBIR A GITHUB

Archivos protegidos (NO se subiran):
  - .env (credenciales)
  - sessions/ (datos personales)
  - experience_memory/ (memoria)
  - logs/ (registros)
  - __pycache__/ (cache Python)
  - backups/ (copias)

Proximos pasos:
  1. git add .
  2. git status (verifica que no haya .env)
  3. git commit -m "Clean project structure"
  4. git push origin main

======================================================================
"@

Write-Host $report -ForegroundColor White

# Guardar reporte
$report | Out-File -FilePath "$projectRoot\GITHUB_PREP_REPORT.txt" -Encoding UTF8
Write-Host "Reporte guardado en: GITHUB_PREP_REPORT.txt`n" -ForegroundColor Green

# Preguntar si quiere hacer commit
$answer = Read-Host "Quieres hacer commit automatico? (s/n)"
if ($answer -eq "s" -or $answer -eq "S") {
    Write-Host "`nHaciendo commit..." -ForegroundColor Yellow
    
    git add . 2>&1 | Out-Null
    Write-Host "  Archivos agregados" -ForegroundColor Green
    
    git commit -m "Clean project structure - ready for GitHub" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Commit creado exitosamente" -ForegroundColor Green
        
        $push = Read-Host "`nQuieres hacer push a GitHub? (s/n)"
        if ($push -eq "s" -or $push -eq "S") {
            Write-Host "`nHaciendo push..." -ForegroundColor Yellow
            git push origin main
            if ($LASTEXITCODE -eq 0) {
                Write-Host "`nOK: Push completado! Tu proyecto esta en GitHub`n" -ForegroundColor Green
            } else {
                Write-Host "`nERROR: Fallo el push. Verifica tu conexion`n" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "  ERROR: Fallo el commit" -ForegroundColor Red
    }
}

Write-Host "`n=== PROCESO COMPLETADO ===" -ForegroundColor Cyan
