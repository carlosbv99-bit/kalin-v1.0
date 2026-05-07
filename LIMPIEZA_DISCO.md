# 🧹 Cómo Liberar Espacio en Disco - Kalin

## Solución Rápida

### 1. Ejecutar el Script de Limpieza Automática

```bash
python clean_disk_space.py
```

Este script eliminará automáticamente:
- ✅ Logs antiguos (>7 días)
- ✅ Sesiones antiguas (>30 días)
- ✅ Cache de Python (`__pycache__`)
- ✅ Archivos de backup (`.bak`)
- ✅ Caché de Gradle (opcional)

---

## Limpieza Manual - Pasos Adicionales

### 2. Limpiar Modelos Ollama No Utilizados ⚠️ IMPORTANTE

Los modelos de IA pueden ocupar **5-15 GB** cada uno.

#### Ver modelos instalados:
```bash
ollama list
```

#### Eliminar modelos que NO necesitas:
```bash
# Si tienes estos modelos y NO los usas, elimínalos:
ollama rm qwen2.5:7b        # ~4 GB
ollama rm llama3.2          # ~2 GB
ollama rm codellama:7b      # ~3.8 GB
ollama rm llama3            # ~4.7 GB

# Mantén SOLO este modelo (el que estás usando):
ollama pull deepseek-coder:latest
```

#### Espacio que puedes liberar:
- qwen2.5:7b → **~4 GB**
- llama3.2 → **~2 GB**
- codellama:7b → **~3.8 GB**
- **Total potencial: ~10 GB**

---

### 3. Limpiar Carpeta de Descargas

```powershell
# Windows - Abrir explorador
explorer C:\Users\TU_USUARIO\Downloads

# Eliminar archivos grandes que ya no necesites
```

---

### 4. Limpiar Papelera de Reciclaje

```powershell
# Vaciar papelera de reciclaje desde el escritorio
# o usar PowerShell:
Clear-RecycleBin -Force
```

---

### 5. Limpiar Temp Files de Windows

```powershell
# Ejecutar como administrador
cleanmgr

# O manualmente:
Remove-Item $env:TEMP\* -Recurse -Force -ErrorAction SilentlyContinue
```

---

## Herramientas Recomendadas

### TreeSize Free (Windows)
Descarga: https://www.jam-software.com/treesize-free/

Te muestra visualmente qué carpetas ocupan más espacio.

### WinDirStat
Descarga: https://windirstat.net/

Análisis gráfico del uso de disco.

---

## Limpieza Específica del Proyecto Kalin

### Carpetas que puedes eliminar sin riesgo:

```bash
# Desde la raíz del proyecto E:\kalin

# 1. Cache de Python (se regenera automáticamente)
Remove-Item -Recurse -Force __pycache__

# 2. Logs antiguos (mantén solo los recientes)
Get-ChildItem logs\*.log | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Remove-Item

# 3. Sesiones antiguas
Get-ChildItem sessions\session_*.json | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item

# 4. Archivos .bak
Get-ChildItem -Recurse *.bak | Remove-Item

# 5. Carpeta .gradle (se regenera al compilar)
Remove-Item -Recurse -Force .gradle
```

---

## Espacio Típico que Puedes Liberar

| Elemento | Espacio Aproximado |
|----------|-------------------|
| Logs antiguos | 10-100 MB |
| Sesiones antiguas | 5-50 MB |
| __pycache__ | 50-200 MB |
| Archivos .bak | 10-50 MB |
| Caché Gradle | 100-500 MB |
| **Modelos Ollama no usados** | **5-15 GB** ⭐ |
| **TOTAL POTENCIAL** | **~6-16 GB** |

---

## Verificar Espacio Libre

```powershell
# Ver espacio libre en disco
Get-PSDrive C | Select-Object Used,Free

# O más detallado:
wmic logicaldisk where "DeviceID='C:'" get Size,FreeSpace
```

---

## Prevención - Mantener el Disco Limpio

### 1. Configurar Rotación de Logs

En tu aplicación, limita el tamaño de los logs:

```python
# En agent/core/logger.py
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/kalin.log',
    maxBytes=5*1024*1024,  # 5 MB máximo
    backupCount=3           # Mantener solo 3 backups
)
```

### 2. Limpiar Periódicamente

Agenda el script de limpieza semanalmente:

```powershell
# Crear tarea programada en Windows
schtasks /create /tn "Kalin Cleanup" /tr "python E:\kalin\clean_disk_space.py" /sc weekly /d SUN /st 02:00
```

### 3. Monitorear Uso de Disco

```bash
# Ejecutar análisis mensual
python clean_disk_space.py
```

---

## Solución de Emergencia - Disco 100% Lleno

Si tu disco está **completamente lleno** y no puedes hacer nada:

### Paso 1: Liberar espacio mínimo para operar
```powershell
# Eliminar archivos temporales grandes
Remove-Item $env:TEMP\* -Recurse -Force -ErrorAction SilentlyContinue

# Vaciar papelera
Clear-RecycleBin -Force
```

### Paso 2: Mover archivos grandes temporalmente
- Mover videos/fotos a disco externo
- Mover proyectos antiguos a la nube
- Comprimir carpetas grandes

### Paso 3: Ejecutar limpieza completa
```bash
python clean_disk_space.py
```

### Paso 4: Eliminar modelos Ollama
```bash
# Esto libera 5-15 GB inmediatamente
ollama rm qwen2.5:7b
ollama rm llama3.2
```

---

## Resumen de Acciones Prioritarias

### 🥇 Alta Prioridad (liberan más espacio):
1. ✅ Eliminar modelos Ollama no usados (**5-15 GB**)
2. ✅ Ejecutar `clean_disk_space.py` (**100-500 MB**)

### 🥈 Media Prioridad:
3. ✅ Limpiar carpeta Downloads (**variable**)
4. ✅ Vaciar papelera de reciclaje (**variable**)

### 🥉 Baja Prioridad:
5. ✅ Limpiar temp files de Windows (**100-500 MB**)
6. ✅ Usar TreeSize para encontrar archivos grandes

---

## Comandos Rápidos

```bash
# Todo en uno (Windows PowerShell como admin):
python E:\kalin\clean_disk_space.py && ollama list && echo "Revisa los modelos arriba y elimina los que no uses con: ollama rm <nombre>"
```

---

## ¿Necesitas Más Ayuda?

Si después de todo sigues sin espacio:

1. **Considera ampliar tu disco** (SSD externo o interno)
2. **Mueve proyectos antiguos** a almacenamiento en la nube
3. **Usa discos virtuales** en la nube (OneDrive, Google Drive)
4. **Elimina programas** que no uses desde Configuración > Aplicaciones

---

## ¡Listo!

Con estas acciones deberías poder liberar **fácilmente 5-15 GB** de espacio, principalmente eliminando modelos Ollama que no estás usando.

**¡Empieza ejecutando el script!** 🚀

```bash
python clean_disk_space.py
```
