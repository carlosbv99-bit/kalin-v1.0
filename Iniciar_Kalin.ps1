# Kalin AI - Script de inicio para Windows
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  KALIN AI - ASISTENTE DE PROGRAMACION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "Verificando instalacion..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python no esta instalado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor instala Python desde:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/" -ForegroundColor White
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""

# Verificar entorno virtual
$venvPath = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "[OK] Entorno virtual encontrado" -ForegroundColor Green
    Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
    & $venvPath
} else {
    Write-Host "[INFO] No se encontro entorno virtual" -ForegroundColor Yellow
    Write-Host "Usando Python del sistema..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INICIANDO KALIN..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Abre tu navegador en: http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Presiona Ctrl+C para detener Kalin" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Iniciar Kalin
python run.py
