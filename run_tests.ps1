# Script PowerShell para ejecutar todos los tests de Kalin
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "EJECUTANDO TODOS LOS TESTS DE KALIN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorCount = 0

# [1/7] Verificar reparaciones
Write-Host "[1/7] Verificando reparaciones..." -ForegroundColor Yellow
python verify_repairs.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Las verificaciones fallaron" -ForegroundColor Red
    Read-Host "Presiona Enter para continuar"
    exit 1
}
Write-Host ""

# [2/7] Diagnosticar imports
Write-Host "[2/7] Diagnosticando imports..." -ForegroundColor Yellow
python diagnose_imports.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Los imports fallaron" -ForegroundColor Red
    Read-Host "Presiona Enter para continuar"
    exit 1
}
Write-Host ""

# [3/7] test_funcional.py
Write-Host "[3/7] Ejecutando test_funcional.py..." -ForegroundColor Yellow
python test_funcional.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ADVERTENCIA: test_funcional.py tuvo errores" -ForegroundColor DarkYellow
    $ErrorCount++
}
Write-Host ""

# [4/7] test_llm_providers.py
Write-Host "[4/7] Ejecutando test_llm_providers.py..." -ForegroundColor Yellow
python test_llm_providers.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ADVERTENCIA: test_llm_providers.py tuvo errores" -ForegroundColor DarkYellow
    $ErrorCount++
}
Write-Host ""

# [5/7] test_new_architecture.py
Write-Host "[5/7] Ejecutando test_new_architecture.py..." -ForegroundColor Yellow
python test_new_architecture.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ADVERTENCIA: test_new_architecture.py tuvo errores" -ForegroundColor DarkYellow
    $ErrorCount++
}
Write-Host ""

# [6/7] test_new_components.py
Write-Host "[6/7] Ejecutando test_new_components.py..." -ForegroundColor Yellow
python test_new_components.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ADVERTENCIA: test_new_components.py tuvo errores" -ForegroundColor DarkYellow
    $ErrorCount++
}
Write-Host ""

# [7/7] test_endpoints.py (si el servidor está disponible)
Write-Host "[7/7] Verificando servidor para test_endpoints.py..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "SERVIDOR DETECTADO: Ejecutando test_endpoints.py..." -ForegroundColor Green
    python test_endpoints.py
} catch {
    Write-Host "SERVIDOR NO DISPONIBLE: Saltando test_endpoints.py" -ForegroundColor DarkGray
    Write-Host "Para ejecutar test_endpoints.py, primero inicia el servidor con: python run.py" -ForegroundColor DarkGray
}
Write-Host ""

# Resumen final
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESUMEN FINAL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Todos los tests han sido ejecutados." -ForegroundColor White
if ($ErrorCount -eq 0) {
    Write-Host "¡Todos los tests pasaron correctamente!" -ForegroundColor Green
} else {
    Write-Host "$ErrorCount test(s) tuvieron errores. Revisa la salida arriba." -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "Presiona Enter para salir"
