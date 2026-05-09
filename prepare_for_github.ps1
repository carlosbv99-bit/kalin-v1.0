# Script de Verificación y Preparación para GitHub
# Ejecutar desde PowerShell en la carpeta E:\kalin

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PREPARANDO PARA GITHUB" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Paso 1: Verificar archivos críticos
Write-Host "[1/6] Verificando archivos criticos..." -ForegroundColor Yellow

$criticalFiles = @(
    "run.py",
    "web.py",
    "requirements.txt",
    ".env.example",
    "templates/index.html",
    "static/js/app.js",
    "static/js/config.js",
    "static/js/chat.js",
    "static/js/preview.js",
    "static/js/ui-manager.js",
    "static/js/resizable-panels.js",
    "static/js/android-utils.js",
    "static/js/legacy-compat.js"
)

$missingFiles = @()
foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] FALTA: $file" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "`n[ERROR] Faltan archivos criticos" -ForegroundColor Red
    exit 1
}

Write-Host "`n[OK] Todos los archivos criticos presentes`n" -ForegroundColor Green

# Paso 2: Limpiar archivos temporales
Write-Host "[2/6] Limpiando archivos temporales..." -ForegroundColor Yellow

# Eliminar __pycache__
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  [OK] Eliminado: $($_.FullName)" -ForegroundColor Green
}

# Eliminar archivos .pyc
Get-ChildItem -Path . -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
}

Write-Host "[OK] Limpieza completada`n" -ForegroundColor Green

# Paso 3: Verificar .gitignore
Write-Host "[3/6] Verificando .gitignore..." -ForegroundColor Yellow

if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content ".gitignore" -Raw
    
    $requiredExcludes = @(".env", "__pycache__", "*.pyc", ".venv", "*.log", "logs/", "sessions/")
    foreach ($exclude in $requiredExcludes) {
        if ($gitignoreContent -match [regex]::Escape($exclude)) {
            Write-Host "  [OK] Excluido: $exclude" -ForegroundColor Green
        } else {
            Write-Host "  [WARNING] No excluido: $exclude" -ForegroundColor Yellow
        }
    }
    
    Write-Host "[OK] .gitignore verificado`n" -ForegroundColor Green
} else {
    Write-Host "[ERROR] No existe .gitignore" -ForegroundColor Red
    exit 1
}

# Paso 4: Verificar que .env no se subirá
Write-Host "[4/6] Verificando configuracion .env..." -ForegroundColor Yellow

if (Test-Path ".env") {
    Write-Host "  [OK] Archivo .env presente (no se subira)" -ForegroundColor Green
} else {
    Write-Host "  [INFO] No existe .env (crear desde .env.example)" -ForegroundColor Cyan
}

if (Test-Path ".env.example") {
    Write-Host "  [OK] .env.example presente" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Falta .env.example" -ForegroundColor Red
}

Write-Host ""

# Paso 5: Verificar estructura HTML
Write-Host "[5/6] Verificando estructura HTML..." -ForegroundColor Yellow

$htmlContent = Get-Content "templates/index.html" -Raw -Encoding UTF8

if ($htmlContent.TrimEnd().EndsWith("</html>")) {
    Write-Host "  [OK] HTML termina correctamente" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] HTML NO termina correctamente" -ForegroundColor Red
    exit 1
}

# Verificar que no haya código después de </html>
$lines = $htmlContent -split "`n"
$htmlEndIndex = -1
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i].Trim() -eq "</html>") {
        $htmlEndIndex = $i
        break
    }
}

if ($htmlEndIndex -ge 0 -and $htmlEndIndex -lt ($lines.Count - 1)) {
    $remainingLines = $lines.Count - $htmlEndIndex - 1
    Write-Host "  [ERROR] Hay $remainingLines lineas despues de </html>" -ForegroundColor Red
    exit 1
} else {
    Write-Host "  [OK] No hay codigo despues de </html>" -ForegroundColor Green
}

Write-Host "[OK] Estructura HTML valida`n" -ForegroundColor Green

# Paso 6: Resumen de cambios
Write-Host "[6/6] Resumen de cambios del dia..." -ForegroundColor Yellow

Write-Host "`nCambios principales:" -ForegroundColor Cyan
Write-Host "  1. Paneles redimensionables implementados (1px ultra fino)" -ForegroundColor White
Write-Host "  2. Mensaje de bienvenida desactivado" -ForegroundColor White
Write-Host "  3. Arquitectura modular JavaScript completa" -ForegroundColor White
Write-Host "  4. Ruta API corregida (/chat en lugar de /send)" -ForegroundColor White
Write-Host "  5. CSS optimizado con !important para evitar cache" -ForegroundColor White
Write-Host "  6. Estilos inline en JavaScript para resizers" -ForegroundColor White

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  LISTO PARA SUBIR A GITHUB" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Comandos para subir:" -ForegroundColor Cyan
Write-Host "  git add ." -ForegroundColor White
Write-Host '  git commit -m "feat: UI improvements - ultra-thin resizable panels (1px), removed welcome message, modular architecture"' -ForegroundColor White
Write-Host "  git push origin main`n" -ForegroundColor White

Write-Host "Archivos modificados hoy:" -ForegroundColor Cyan
Write-Host "  - templates/index.html (CSS resizers, bordes eliminados)" -ForegroundColor Gray
Write-Host "  - static/js/resizable-panels.js (estilos inline 1px)" -ForegroundColor Gray
Write-Host "  - static/js/app.js (mensaje bienvenida desactivado)" -ForegroundColor Gray
Write-Host "  - static/js/config.js (ruta API corregida a /chat)" -ForegroundColor Gray
Write-Host "  - verify_before_github.py (script de verificacion)`n" -ForegroundColor Gray
