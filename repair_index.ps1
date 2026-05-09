# Script para reparar index.html - Elimina código corrupto después de </html>

$inputFile = "templates\index.html"
$outputFile = "templates\index_fixed.html"

# Leer todas las líneas
$lines = Get-Content $inputFile -Encoding UTF8

# Encontrar la línea con </html> (debería ser alrededor de 1102)
$htmlEndLine = $null
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i].Trim() -eq "</html>") {
        $htmlEndLine = $i
        Write-Host "[OK] Encontrado </html> en línea $($i + 1)"
        break
    }
}

if ($null -eq $htmlEndLine) {
    Write-Host "[ERROR] No se encontro </html>"
    exit 1
}

# Tomar solo hasta </html> inclusive
$cleanLines = $lines[0..$htmlEndLine]

# Escribir archivo limpio
$cleanLines | Set-Content $outputFile -Encoding UTF8

Write-Host "[OK] Archivo limpio creado: $outputFile"
Write-Host "   Lineas originales: $($lines.Count)"
Write-Host "   Lineas limpiadas: $($cleanLines.Count)"
Write-Host "   Lineas eliminadas: $($lines.Count - $cleanLines.Count)"
Write-Host ""
Write-Host "Ahora ejecuta:"
Write-Host "   Move-Item templates\index.html templates\index_old_backup.html"
Write-Host "   Move-Item templates\index_fixed.html templates\index.html"
Write-Host ""
Write-Host "Listo. Reinicia el servidor con: python run.py"
