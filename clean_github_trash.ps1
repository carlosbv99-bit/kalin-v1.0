# Script para Limpiar Archivos Basura de GitHub
# Ejecutar desde PowerShell en E:\kalin

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  LIMPIANDO ARCHIVOS BASURA DE GITHUB" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Paso 1: Verificar qué archivos están siendo rastreados
Write-Host "[1/4] Verificando archivos rastreados..." -ForegroundColor Yellow
Write-Host "Ejecuta manualmente: git ls-files | more" -ForegroundColor Gray
Write-Host "Para ver todos los archivos en el repositorio`n" -ForegroundColor Gray

# Paso 2: Eliminar archivos que NO deberían estar en Git
Write-Host "[2/4] Identificando archivos a eliminar..." -ForegroundColor Yellow

$filesToRemove = @()

# Verificar archivos de sesión
if (Test-Path "sessions") {
    $sessionFiles = Get-ChildItem "sessions" -Filter "*.json" -ErrorAction SilentlyContinue
    if ($sessionFiles.Count -gt 0) {
        Write-Host "  [ENCONTRADO] $($sessionFiles.Count) archivos de sesión" -ForegroundColor Yellow
        $filesToRemove += "sessions/*.json"
    }
}

# Verificar archivos de log
if (Test-Path "logs") {
    $logFiles = Get-ChildItem "logs" -Filter "*.log" -ErrorAction SilentlyContinue
    if ($logFiles.Count -gt 0) {
        Write-Host "  [ENCONTRADO] $($logFiles.Count) archivos de log" -ForegroundColor Yellow
        $filesToRemove += "logs/*.log"
    }
}

# Verificar experiencia memory
if (Test-Path "experience_memory") {
    $expFiles = Get-ChildItem "experience_memory" -Filter "*.json" -ErrorAction SilentlyContinue
    if ($expFiles.Count -gt 0) {
        Write-Host "  [ENCONTRADO] $($expFiles.Count) archivos de experiencia" -ForegroundColor Yellow
        $filesToRemove += "experience_memory/*.json"
    }
}

# Verificar archivos .gradle
if (Test-Path ".gradle") {
    Write-Host "  [ENCONTRADO] Directorio .gradle" -ForegroundColor Yellow
    $filesToRemove += ".gradle/"
}

# Verificar directorio .idea
if (Test-Path ".idea") {
    Write-Host "  [ENCONTRADO] Directorio .idea" -ForegroundColor Yellow
    $filesToRemove += ".idea/"
}

# Verificar .kotlin
if (Test-Path ".kotlin") {
    Write-Host "  [ENCONTRADO] Directorio .kotlin" -ForegroundColor Yellow
    $filesToRemove += ".kotlin/"
}

# Verificar archivos Java/Dart (si existen)
$javaFiles = Get-ChildItem -Filter "*.java" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.DirectoryName -notmatch "app\\src" }
if ($javaFiles.Count -gt 0) {
    Write-Host "  [ENCONTRADO] $($javaFiles.Count) archivos Java sueltos" -ForegroundColor Yellow
}

$dartFiles = Get-ChildItem -Filter "*.dart" -Recurse -ErrorAction SilentlyContinue
if ($dartFiles.Count -gt 0) {
    Write-Host "  [ENCONTRADO] $($dartFiles.Count) archivos Dart" -ForegroundColor Yellow
}

if ($filesToRemove.Count -eq 0) {
    Write-Host "`n[OK] No se encontraron archivos problemáticos adicionales" -ForegroundColor Green
} else {
    Write-Host "`nArchivos/directorios a remover del tracking:" -ForegroundColor Yellow
    foreach ($file in $filesToRemove) {
        Write-Host "  - $file" -ForegroundColor Gray
    }
}

Write-Host ""

# Paso 3: Instrucciones para limpiar
Write-Host "[3/4] Instrucciones para limpiar GitHub:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Ejecuta estos comandos en orden:" -ForegroundColor Cyan
Write-Host ""
Write-Host "# 1. Remover archivos de sesión del tracking (pero mantenerlos localmente)" -ForegroundColor White
Write-Host "git rm -r --cached sessions/" -ForegroundColor Gray
Write-Host ""
Write-Host "# 2. Remover logs del tracking" -ForegroundColor White
Write-Host "git rm -r --cached logs/" -ForegroundColor Gray
Write-Host ""
Write-Host "# 3. Remover experience_memory del tracking" -ForegroundColor White
Write-Host "git rm -r --cached experience_memory/" -ForegroundColor Gray
Write-Host ""
Write-Host "# 4. Remover directorios IDE/build" -ForegroundColor White
Write-Host "git rm -r --cached .gradle/" -ForegroundColor Gray
Write-Host "git rm -r --cached .idea/" -ForegroundColor Gray
Write-Host "git rm -r --cached .kotlin/" -ForegroundColor Gray
Write-Host ""
Write-Host "# 5. Remover archivos Java/Dart sueltos (si existen)" -ForegroundColor White
Write-Host "git rm --cached *.java" -ForegroundColor Gray
Write-Host "git rm --cached *.dart" -ForegroundColor Gray
Write-Host "git rm --cached main.dart" -ForegroundColor Gray
Write-Host ""
Write-Host "# 6. Verificar cambios" -ForegroundColor White
Write-Host "git status" -ForegroundColor Gray
Write-Host ""
Write-Host "# 7. Commit de limpieza" -ForegroundColor White
Write-Host 'git commit -m "chore: remove tracked files that should be ignored"' -ForegroundColor Gray
Write-Host ""
Write-Host "# 8. Push a GitHub" -ForegroundColor White
Write-Host "git push origin main" -ForegroundColor Gray
Write-Host ""

# Paso 4: Verificación final
Write-Host "[4/4] Después de limpiar, verifica:" -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ sessions/ NO aparece en git status" -ForegroundColor Green
Write-Host "✅ logs/ NO aparece en git status" -ForegroundColor Green
Write-Host "✅ experience_memory/ NO aparece en git status" -ForegroundColor Green
Write-Host "✅ .gradle/, .idea/, .kotlin/ NO aparecen" -ForegroundColor Green
Write-Host "✅ .env NO está en el repositorio" -ForegroundColor Green
Write-Host "✅ Solo archivos del proyecto Kalin están trackeados" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LISTO PARA LIMPIAR" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "NOTA: Los archivos se mantendrán en tu computadora," -ForegroundColor Yellow
Write-Host "solo se eliminarán del repositorio de GitHub.`n" -ForegroundColor Yellow
