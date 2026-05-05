# Script para verificar y corregir URL del remoto GitHub

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VERIFICANDO REMOTO GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar remotos actuales
Write-Host "Remotos configurados:" -ForegroundColor Yellow
git remote -v
Write-Host ""

# Obtener URL actual
$currentUrl = git remote get-url origin 2>&1
Write-Host "URL actual: $currentUrl" -ForegroundColor Gray
Write-Host ""

# Verificar si la URL es correcta
if ($currentUrl -match "github.com/carlosbv99@gmail.com") {
    Write-Host "⚠️  URL incorrecta detectada (contiene email)" -ForegroundColor DarkYellow
    Write-Host ""
    
    $correctUrl = "https://github.com/carlosbv99/kalin.git"
    Write-Host "URL correcta debería ser: $correctUrl" -ForegroundColor Green
    Write-Host ""
    
    $confirm = Read-Host "¿Deseas corregir la URL? (S/N)"
    if ($confirm -eq "S" -or $confirm -eq "s") {
        git remote set-url origin $correctUrl
        Write-Host "✅ URL corregida" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "Nueva URL:" -ForegroundColor Yellow
        git remote get-url origin
    } else {
        Write-Host "URL no modificada" -ForegroundColor DarkGray
    }
} elseif ($currentUrl -match "github.com/carlosbv99/kalin") {
    Write-Host "✅ URL correcta detectada" -ForegroundColor Green
} else {
    Write-Host "⚠️  URL diferente detectada" -ForegroundColor DarkYellow
    Write-Host "Verifica que sea la correcta para tu repositorio"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VERIFICANDO ESTADO DEL REPOSITORIO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar estado
Write-Host "Estado actual:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Verificar últimos commits
Write-Host "Últimos commits:" -ForegroundColor Yellow
git log --oneline -3
Write-Host ""

# Verificar tags
Write-Host "Tags disponibles:" -ForegroundColor Yellow
git tag -l | Select-Object -Last 5
Write-Host ""

# Verificar ramas
Write-Host "Ramas:" -ForegroundColor Yellow
git branch -a
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PRÓXIMOS PASOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Si hay cambios pendientes:" -ForegroundColor White
Write-Host "  1. Agregar cambios: git add ." -ForegroundColor Gray
Write-Host "  2. Crear commit: git commit -m 'mensaje'" -ForegroundColor Gray
Write-Host "  3. Push: git push origin main --tags" -ForegroundColor Gray
Write-Host ""
Write-Host "Para ver más detalles:" -ForegroundColor White
Write-Host "  git log --oneline" -ForegroundColor Gray
Write-Host "  git tag -l" -ForegroundColor Gray
Write-Host "  git remote -v" -ForegroundColor Gray
Write-Host ""

Read-Host "Presiona Enter para salir"
