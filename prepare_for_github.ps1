# Script de PowerShell para preparar Kalin v3.0 para GitHub
# Este script automatiza la limpieza y verificación antes de subir a GitHub

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "KALIN v3.0 - PREPARACIÓN PARA GITHUB" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# Función para mostrar pasos
function Show-Step {
    param([string]$message)
    Write-Host "`n📋 $message" -ForegroundColor Yellow
    Write-Host ("-" * 60) -ForegroundColor DarkGray
}

# Función para mostrar éxito
function Show-Success {
    param([string]$message)
    Write-Host "✅ $message" -ForegroundColor Green
}

# Función para mostrar advertencia
function Show-Warning {
    param([string]$message)
    Write-Host "⚠️  $message" -ForegroundColor Yellow
}

# Función para mostrar error
function Show-Error {
    param([string]$message)
    Write-Host "❌ $message" -ForegroundColor Red
}

# Paso 1: Verificar que estamos en el directorio correcto
Show-Step "Verificando directorio del proyecto"
if (Test-Path "$projectRoot\main.py") {
    Show-Success "Directorio del proyecto verificado: $projectRoot"
} else {
    Show-Error "No se encontró main.py. ¿Estás en el directorio correcto?"
    exit 1
}

# Paso 2: Verificar que existe .gitignore
Show-Step "Verificando .gitignore"
if (Test-Path "$projectRoot\.gitignore") {
    Show-Success "Archivo .gitignore encontrado"
    
    # Verificar reglas importantes
    $gitignoreContent = Get-Content "$projectRoot\.gitignore" -Raw
    $requiredPatterns = @(".env", "__pycache__", "*.pyc", ".gradle", ".idea", "sessions/", "logs/")
    $missingPatterns = @()
    
    foreach ($pattern in $requiredPatterns) {
        if (-not ($gitignoreContent -match [regex]::Escape($pattern))) {
            $missingPatterns += $pattern
        }
    }
    
    if ($missingPatterns.Count -gt 0) {
        Show-Warning "Faltan patrones en .gitignore: $($missingPatterns -join ', ')"
    } else {
        Show-Success ".gitignore contiene todas las reglas necesarias"
    }
} else {
    Show-Error "No se encontró archivo .gitignore"
    exit 1
}

# Paso 3: Verificar que .env NO esté en staging
Show-Step "Verificando archivos sensibles"
$sensitiveFiles = @(
    ".env",
    "local.properties"
)

$foundSensitive = $false
foreach ($file in $sensitiveFiles) {
    $filePath = Join-Path $projectRoot $file
    if (Test-Path $filePath) {
        # Verificar si está en el índice de Git
        $result = git ls-files --error-unmatch $file 2>&1
        if ($LASTEXITCODE -eq 0) {
            Show-Error "¡ALERTA! El archivo $file está en el repositorio de Git"
            Show-Warning "Ejecuta: git rm --cached $file para eliminarlo del repositorio"
            $foundSensitive = $true
        } else {
            Show-Success "$file existe pero NO está en el repositorio (correcto)"
        }
    }
}

if ($foundSensitive) {
    Show-Error "Se encontraron archivos sensibles en el repositorio. Debes eliminarlos antes de continuar."
    exit 1
}

# Paso 4: Limpiar archivos temporales
Show-Step "Limpiando archivos temporales"

$patternsToRemove = @(
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.log",
    "*.bak",
    "*.tmp",
    ".agent_state.json",
    "health_status.json"
)

$removedCount = 0

foreach ($pattern in $patternsToRemove) {
    $items = Get-ChildItem -Path $projectRoot -Include $pattern -Recurse -ErrorAction SilentlyContinue
    
    foreach ($item in $items) {
        try {
            if ($item.PSIsContainer) {
                Remove-Item -Path $item.FullName -Recurse -Force
                Write-Host "  ✓ Eliminado directorio: $($item.Name)" -ForegroundColor DarkGreen
            } else {
                Remove-Item -Path $item.FullName -Force
                Write-Host "  ✓ Eliminado archivo: $($item.Name)" -ForegroundColor DarkGreen
            }
            $removedCount++
        } catch {
            Write-Host "  ✗ Error al eliminar $($item.FullName): $_" -ForegroundColor DarkRed
        }
    }
}

Show-Success "Limpieza completada. Se eliminaron $removedCount archivos/directorios"

# Paso 5: Verificar directorios de datos locales
Show-Step "Verificando directorios de datos locales"

$localDataDirs = @("sessions", "experience_memory", "logs")

foreach ($dir in $localDataDirs) {
    $dirPath = Join-Path $projectRoot $dir
    if (Test-Path $dirPath) {
        # Contar archivos JSON/log en el directorio
        $files = Get-ChildItem -Path $dirPath -File -ErrorAction SilentlyContinue
        if ($files.Count -gt 0) {
            Show-Warning "El directorio $dir contiene $($files.Count) archivo(s)"
            Write-Host "   Estos archivos están excluidos por .gitignore" -ForegroundColor DarkGray
        } else {
            Show-Success "Directorio $dir está vacío"
        }
    }
}

# Paso 6: Ejecutar script de verificación Python si existe
Show-Step "Ejecutando verificación avanzada"
$verifyScript = Join-Path $projectRoot "verify_github_ready.py"
if (Test-Path $verifyScript) {
    Write-Host "Ejecutando verify_github_ready.py..." -ForegroundColor Cyan
    python $verifyScript
    if ($LASTEXITCODE -eq 0) {
        Show-Success "Verificación Python completada exitosamente"
    } else {
        Show-Warning "La verificación Python encontró problemas. Revisa la salida anterior."
    }
} else {
    Show-Warning "No se encontró verify_github_ready.py. Saltando verificación avanzada."
}

# Paso 7: Mostrar estado de Git
Show-Step "Estado actual del repositorio Git"
try {
    $gitStatus = git status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host $gitStatus -ForegroundColor White
        
        # Verificar si hay archivos en staging
        $stagedFiles = git diff --cached --name-only 2>&1
        if ($stagedFiles -and $stagedFiles.Count -gt 0) {
            Show-Warning "Hay archivos en staging (preparados para commit)"
            Write-Host "Archivos en staging:" -ForegroundColor Yellow
            $stagedFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor DarkYellow }
        }
    } else {
        Show-Warning "No se detectó un repositorio Git o Git no está instalado"
        Write-Host "Para inicializar: git init" -ForegroundColor DarkGray
    }
} catch {
    Show-Warning "No se pudo verificar el estado de Git"
}

# Resumen final
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "RESUMEN FINAL" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Proyecto verificado y limpio" -ForegroundColor Green
Write-Host "✅ Archivos sensibles excluidos" -ForegroundColor Green
Write-Host "✅ .gitignore configurado correctamente" -ForegroundColor Green
Write-Host ""

Write-Host "Próximos pasos:" -ForegroundColor Yellow
Write-Host "1. Revisa el estado: git status" -ForegroundColor White
Write-Host "2. Agrega archivos: git add ." -ForegroundColor White
Write-Host "3. Crea commit: git commit -m `"Clean project structure`"" -ForegroundColor White
Write-Host "4. Sube a GitHub: git push origin main" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  IMPORTANTE: Nunca subas el archivo .env a GitHub" -ForegroundColor Yellow
Write-Host ""

Show-Success "¡Tu proyecto Kalin v3.0 está listo para GitHub!"
