# KALIN v3.0 - Preparación y Testing (PowerShell)

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host " KALIN v3.0 - PREPARACION Y TESTING" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Paso 1: Limpiar proyecto
Write-Host "[1/3] Limpiando proyecto..." -ForegroundColor Yellow
python prepare_for_testing.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR en limpieza" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host ""

# Paso 2: Ejecutar tests
Write-Host "[2/3] Ejecutando tests..." -ForegroundColor Yellow
python test_suite_completa.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ADVERTENCIA: Algunos tests fallaron" -ForegroundColor Yellow
    Write-Host "Revisa los errores arriba antes de continuar" -ForegroundColor Yellow
    $continue = Read-Host "Deseas continuar de todas formas? (s/n)"
    if ($continue -ne "s") {
        exit 1
    }
}
Write-Host ""

# Paso 3: Iniciar servidor
Write-Host "[3/3] Iniciando servidor..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Accede a http://localhost:5000" -ForegroundColor Green
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Green
Write-Host ""
python run.py
