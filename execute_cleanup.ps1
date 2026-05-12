# Script de Limpieza Automática - Kalin Project
# Ejecutar en PowerShell desde E:\kalin

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  LIMPIEZA EXHAUSTIVA DEL PROYECTO KALIN" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

# Contadores
$deletedCount = 0
$failedCount = 0
$totalSize = 0

# Función para calcular tamaño
function Get-ItemSize {
    param($path)
    if (Test-Path $path -PathType Leaf) {
        return (Get-Item $path).Length
    } elseif (Test-Path $path -PathType Container) {
        return (Get-ChildItem $path -Recurse -File | Measure-Object -Property Length -Sum).Sum
    }
    return 0
}

# Función para formatear tamaño
function Format-Size {
    param([long]$bytes)
    if ($bytes -lt 1KB) { return "$bytes B" }
    elseif ($bytes -lt 1MB) { return "{0:N2} KB" -f ($bytes / 1KB) }
    elseif ($bytes -lt 1GB) { return "{0:N2} MB" -f ($bytes / 1MB) }
    else { return "{0:N2} GB" -f ($bytes / 1GB) }
}

Write-Host "📋 Iniciando limpieza..." -ForegroundColor Yellow
Write-Host ""

# ===== CATEGORÍA 1: DOCUMENTACIÓN REDUNDANTE =====
Write-Host "📄 Eliminando documentación redundante..." -ForegroundColor Cyan

$docPatterns = @(
    "IMPLEMENTACION_*.md",
    "FIX_*.md",
    "CORRECCION_*.md",
    "CAMBIOS_*.md",
    "RESUMEN_*.md",
    "*_SUMMARY.md",
    "*_RESUMEN.md",
    "COMO_PROBAR_CAMBIOS.md",
    "COMO_USAR_SCRIPTS_GITHUB.md",
    "CONFIGURAR_BACKUP_RAPIDO.md",
    "COPIA_LIMPIA_INSTRUCCIONES.md",
    "CHECKLIST_*.txt",
    "CHECKLIST_*.md",
    "DIAGNOSTICO_*.md",
    "SOLUCION_*.md",
    "*GITHUB*.md",
    "*GITHUB*.txt",
    "PREPARACION_*.md",
    "LISTO_PARA_GITHUB.md",
    "INDICE_ARCHIVOS_GITHUB.md",
    "EVALUACION_*.md",
    "AUDITORIA_*.md",
    "ARQUITECTURA_*.md",
    "DIAGRAMA_*.md",
    "MIGRACION_*.md",
    "FRONTEND_*.md",
    "OPTIMIZACION_*.md",
    "TEMPERATURAS_*.md",
    "ANDROID_SUPPORT.md",
    "DOCKER_DEPLOYMENT.md",
    "MULTI_PROVIDER_SUMMARY.md",
    "ESCALABILIDAD_LLMS_RESUMEN.md",
    "NUEVOS_MODELOS_*.md",
    "PROVEEDORES_LLM_GUIA.md",
    "GUIA_MULTIPLES_LLMS.md",
    "PATCH_SYSTEM.md",
    "MENUS_HERRAMIENTAS_DIFFS.md",
    "IMPLEMENTACION_PATCHES_RESUMEN.md",
    "SISTEMA_MEMORIA_CONVERSACIONAL.md",
    "IMPLEMENTACION_MEMORIA_CONVERSACIONAL.md",
    "CORRECCIONES_MEMORIA_CONTEXTUAL.md",
    "EXPERIENCE_MEMORY_GUIDE.md",
    "SISTEMA_PROMPTS_DINAMICOS.md",
    "NUEVA_ARQUITECTURA_PROMPTS.md",
    "TESTING_GUIDE.md",
    "CI_CD_TESTING_GUIDE.md",
    "CODIGO_LIMPIO_TESTING.md",
    "REPARACIONES_TESTS.md",
    "GUIA_TESTS.md",
    "RUN_TEST.md",
    "CHANGELOG_v1.1.md",
    "CHANGELOG_SIDEBAR_UPDATE.md",
    "CHANGES_TODAY.md",
    "REVIEW_SUMMARY.md",
    "EXECUTIVE_SUMMARY.md",
    "INFORME_ESTADO_PROYECTO.md",
    "INFORME_PROYECTO.pdf",
    "README.pdf",
    "README_KALIN_V3.md",
    "README_PROFESSIONAL.md",
    "README_LINUX.md",
    "README_GITHUB.md",
    "QUICK_START_SPECIALISTS.md",
    "DEPLOYMENTS.md",
    "ROADMAP_IDE_AUTONOMO.md",
    "BRANCH_PROTECTION_SETUP.md",
    "AUTO_GITHUB_INSTRUCTIONS.txt",
    "BACKUP_GITHUB_GUIA.md",
    "BACKUP_RAPIDO.md",
    "GITHUB_PREP_REPORT.txt",
    "INICIO_RAPIDO_GITHUB.txt",
    "INSTRUCCIONES_SIMPLES_GITHUB.txt",
    "INSTRUCCIONES_SUBIR_GITHUB.md",
    "SCRIPTS_AUTOMATICOS.md",
    "CAMBIO_CLIC_ELIMINAR_MODELO.md",
    "MEJORAS_VENTANA_CONTEXTO.md",
    "MEJORA_BOTON_ELIMINAR_HOVER.md",
    "FUNCIONALIDAD_MODELOS_OLLAMA.md",
    "INDICADOR_PROGRESO_DESCARGA_MODELO.md",
    "FIX_ACTUALIZACION_PREVIEW.md",
    "FIX_ANALISIS_CODIGO_PEGADO.md",
    "FIX_BOTONES_CONFIGURACION.md",
    "FIX_CAMBIO_LENGUAJE_HTML_PYTHON.md",
    "FIX_CLIC_MODELOS_INSTALADOS.md",
    "FIX_DEFINITIVO_BLOQUEO_LENGUAJE.md",
    "FIX_DETECCION_CREATE_FRASES.md",
    "FIX_FINAL_JAVA_ANTICALENDARIO.md",
    "FIX_RECHAZO_CALENDARIO.md",
    "TROUBLESHOOTING_INDICADOR_DESCARGA.md",
    "MODO_OSCURO_MENSAJES_CONFIRMACION.md",
    "CORRECCIONES_ERRORES_ARGUMENTOS.md",
    "CORRECCIONES_FINALES_EXTRACCION.md",
    "CORRECCION_EXTRACCION_ARGUMENTOS.md",
    "CORRECCION_SALUDOS_REPETITIVOS.md",
    "IMPLEMENTACION_ANALISIS_CODIGO_PEGADO.md",
    "IMPLEMENTACION_CICD_TESTS_RESUMEN.md",
    "IMPLEMENTACION_COMPLETADA.md",
    "IMPLEMENTACION_V2.md",
    "INTEGRACION_COMPLETA.md",
    "LIMPIEZA_DISCO.md",
    "RESUMEN_COMPLETO_SEGURIDAD_ESTABILIDAD.md",
    "RESUMEN_CORRECCIONES_SESIONES.md",
    "RESUMEN_EJECUTIVO_GITHUB.md",
    "RESUMEN_FINAL_COMPLETO.md",
    "GUIA_DE_USO.md",
    "GUIA_LINUX_PRINCIPIANTES.md",
    "GUIA_USUARIO.md",
    "DEBUG_GUIDE.md",
    "CHECKLIST_CLOUD.md",
    "CHECKLIST_EVALUACION.txt",
    "EVALUACION_COMPLETADA.md",
    "EVALUACION_ESPECIALISTAS_RESPUESTA.md"
)

foreach ($pattern in $docPatterns) {
    $files = Get-ChildItem -Path "." -Filter $pattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        try {
            $size = Get-ItemSize $file.FullName
            $totalSize += $size
            Remove-Item $file.FullName -Force
            Write-Host "   ✅ $($file.Name)" -ForegroundColor Green
            $deletedCount++
        } catch {
            Write-Host "   ❌ Error eliminando $($file.Name): $_" -ForegroundColor Red
            $failedCount++
        }
    }
}

Write-Host ""

# ===== CATEGORÍA 2: SCRIPTS TEMPORALES =====
Write-Host "🔧 Eliminando scripts temporales..." -ForegroundColor Cyan

$scriptFiles = @(
    "backup_github.py",
    "backup_limpio.py",
    "backup_v1.1.py",
    "auto_backup_github.py",
    "auto_github_prep.py",
    "auto_github_prep.ps1",
    "auto_prepare_github.py",
    "prepare_for_github.ps1",
    "prepare_github.bat",
    "prepare_for_review.py",
    "prepare_for_testing.py",
    "verify_before_github.py",
    "verify_github_ready.py",
    "setup_auto_backup.py",
    "commit_and_push.ps1",
    "commit_v1.1.ps1",
    "clean_copy_project.bat",
    "clean_copy_project.py",
    "clean_disk_space.py",
    "limpieza_backup_avanzado.py",
    "delete_backups.bat",
    "clean_github_trash.ps1",
    "diagnose.py",
    "diagnose_imports.py",
    "check_provider.py",
    "check_mimo_config.py",
    "verify_repairs.py",
    "fix_index.py",
    "update_names.py",
    "git_fix.py",
    "auto_fix.py",
    "test_flow_and_functionality.py",
    "test_general.py",
    "test_general_workflow.py",
    "test_quick.py",
    "run_all_tests.py",
    "crear_readme.py",
    "generar_pdf.py",
    "security_audit.py",
    "check_code_quality.py",
    "maintenance.py",
    "ejemplo_patch_system.py",
    "EJEMPLOS_PRACTICOS.py"
)

foreach ($script in $scriptFiles) {
    if (Test-Path $script) {
        try {
            $size = Get-ItemSize $script
            $totalSize += $size
            Remove-Item $script -Force
            Write-Host "   ✅ $script" -ForegroundColor Green
            $deletedCount++
        } catch {
            Write-Host "   ❌ Error eliminando $script : $_" -ForegroundColor Red
            $failedCount++
        }
    }
}

Write-Host ""

# ===== CATEGORÍA 3: DIRECTORIOS =====
Write-Host "📁 Eliminando directorios..." -ForegroundColor Cyan

$dirsToRemove = @("backups", "__pycache__", ".gradle")

foreach ($dir in $dirsToRemove) {
    if (Test-Path $dir) {
        try {
            $size = Get-ItemSize $dir
            $totalSize += $size
            Remove-Item $dir -Recurse -Force
            Write-Host "   ✅ $dir/" -ForegroundColor Green
            $deletedCount++
        } catch {
            Write-Host "   ❌ Error eliminando $dir/: $_" -ForegroundColor Red
            $failedCount++
        }
    }
}

Write-Host ""

# ===== RESUMEN FINAL =====
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  ✅ LIMPIEZA COMPLETADA" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Archivos/Directorios eliminados: $deletedCount" -ForegroundColor White
Write-Host "  Errores: $failedCount" -ForegroundColor $(if ($failedCount -eq 0) { "Green" } else { "Red" })
Write-Host "  Espacio liberado: $(Format-Size $totalSize)" -ForegroundColor White
Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Siguiente paso: Ejecuta 'git status' para ver los cambios" -ForegroundColor Yellow
Write-Host ""
